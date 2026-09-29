"""Step 3F: TabPFN v2 against gradient boosting, from 20 rows to all 829,358.

TabPFN is a transformer pre-trained on synthetic tables: it takes the training
rows as part of its input and predicts in one forward pass, with no fitting of
its own weights. It is said to match gradient boosting with far fewer rows.
This measures that claim on the undergrounding task of the 23 wards (steps 1B
to 4A): six street features, a scene is undergrounded or not.

- Test: 3,000 rows drawn from 2 km blocks held out of training (new places),
  the same for every model and training size.
- Training: random samples of the other blocks, 20 rows to all 829,358. Three
  samples (seeds) up to 3,000 rows, one above.
- Models: logistic regression, XGBoost, LightGBM, TabPFN v2 (up to 10,000 rows).
  TabPFN runs on the CPU (the GPUs of this machine are taken by resident
  services), with TABPFN_ALLOW_CPU_LARGE_DATASET=1 above 1,000 rows.
- Scores: AUC, ECE (10 bins), and seconds to fit and predict the 3,000 rows.

TabPFN v2 is chosen explicitly: its weights are under the Prior Labs License
(Apache 2.0 plus an attribution clause); v2.5 and later are non-commercial.

    TABPFN_ALLOW_CPU_LARGE_DATASET=1 CUDA_VISIBLE_DEVICES= \\
        uv run --group tabpfn python -u src/003-F-tabpfn/run.py
"""

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from lightgbm import LGBMClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import GroupShuffleSplit  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from xgboost import XGBClassifier  # noqa: E402

from study_geoai import tasks  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
SIZES = [20, 60, 120, 300, 1000, 3000, 10000, 30000, 100000, 300000, None]  # None = all
TABPFN_MAX = 10000
SEEDS = (0, 1, 2)
N_TEST = 3000
BLOCK = 0.02  # degrees, about 2 km


def ece(y, p, bins=10):
    """Expected calibration error over equal-width probability bins."""
    idx = np.clip((p * bins).astype(int), 0, bins - 1)
    return float(sum(abs(p[idx == b].mean() - y[idx == b].mean()) * (idx == b).mean()
                     for b in range(bins) if (idx == b).any()))  # fmt: skip


def gbdt_and_linear(n):
    """The baselines; trees shallower and fewer on small samples, as a fair setting."""
    trees = 200 if n >= 1000 else 100
    return {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "XGBoost": XGBClassifier(n_estimators=trees, learning_rate=0.1,
                                 max_depth=3 if n < 1000 else (4 if n < 10000 else 6),
                                 subsample=0.8, colsample_bytree=0.8, n_jobs=16, random_state=0),
        "LightGBM": LGBMClassifier(n_estimators=trees, learning_rate=0.1, num_leaves=15,
                                   min_child_samples=min(20, max(3, n // 50)), n_jobs=16,
                                   random_state=0, verbose=-1),
    }  # fmt: skip


def tabpfn():
    from tabpfn import TabPFNClassifier
    from tabpfn.constants import ModelVersion

    return TabPFNClassifier.create_default_for_version(ModelVersion.V2, device="cpu",
                                                        n_preprocessing_jobs=8)  # fmt: skip


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t = tasks.undergrounded(connect(), "tokyo23")
    X, y = t.X, t.y
    blocks = (np.floor(t.groups["lon"] / BLOCK).astype(int) * 100_000
              + np.floor(t.groups["lat"] / BLOCK).astype(int))  # fmt: skip
    train, test = next(GroupShuffleSplit(1, test_size=0.2, random_state=0).split(X, y, blocks))
    test = np.random.default_rng(0).choice(test, N_TEST, replace=False)
    print(f"## 23 wards undergrounding: {len(y):,} rows ({y.mean():.1%} undergrounded); training"
          f" pool {len(train):,}; test {N_TEST:,} rows from held-out 2 km blocks"
          f" ({y[test].mean():.1%})", flush=True)  # fmt: skip
    print("\n   rows        model       AUC    (range)        ECE     seconds")
    curve = {}
    for n in SIZES:
        size = len(train) if n is None else n
        runs = {}
        for s in SEEDS if size <= 3000 else (0,):
            pick = (
                train
                if n is None
                else np.random.default_rng(100 + s).choice(train, size, replace=False)
            )
            if len(np.unique(y[pick])) < 2:
                print(f"   {size:<10,}  seed {s}: one class only, skipped")
                continue
            models = gbdt_and_linear(size)
            if size <= TABPFN_MAX:
                models["TabPFN v2"] = None
            for name, m in models.items():
                t0 = time.perf_counter()
                m = tabpfn() if name == "TabPFN v2" else m
                m.fit(X[pick], y[pick])
                p = m.predict_proba(X[test])[:, 1]
                runs.setdefault(name, []).append(
                    (roc_auc_score(y[test], p), ece(y[test], p), time.perf_counter() - t0)
                )
        for name, r in runs.items():
            a = np.array(r)
            curve.setdefault(name, []).append((size, a[:, 0].mean(), a[:, 0].min(), a[:, 0].max()))
            print(f"   {size:<10,}  {name:<10}  {a[:, 0].mean():.3f}  ({a[:, 0].min():.3f}-{a[:, 0].max():.3f})"
                  f"  {a[:, 1].mean():.3f}  {a[:, 2].mean():>8.1f}", flush=True)  # fmt: skip

    fig, ax = plt.subplots(figsize=(8, 5))
    for name, pts in curve.items():
        a = np.array(pts)
        ax.plot(a[:, 0], a[:, 1], marker="o", label=name)
        ax.fill_between(a[:, 0], a[:, 2], a[:, 3], alpha=0.2)
    ax.set_xscale("log")
    ax.set_xlabel("training rows")
    ax.set_ylabel("AUC on 3,000 rows of held-out blocks")
    ax.set_title("23 wards undergrounding: learning curves")
    ax.legend()
    fig.savefig(OUT / "learning-curve.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")


if __name__ == "__main__":
    main()
