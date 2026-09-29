"""Step 11B: are the undergrounded classifier's probabilities to be trusted?

Three models of steps 1B to 3B on Taito City's street scenes (the same six
street features as 11A): logistic regression, a random forest and XGBoost.
Out-of-fold probabilities, pooled, are scored for ranking (AUC) and as
probabilities (Brier score, log loss, expected calibration error).

1. Random 5 folds: each model raw, then calibrated inside each training fold
   with Platt scaling (sigmoid) or isotonic regression (CalibratedClassifierCV).
2. The same with 250 m cells held out (GroupKFold): calibrated on some places,
   is it still calibrated in others?

    uv run python -u src/011-B-calibration/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.calibration import CalibratedClassifierCV, calibration_curve  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score  # noqa: E402
from sklearn.model_selection import GroupKFold, StratifiedKFold  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from xgboost import XGBClassifier  # noqa: E402

from study_geoai import tasks  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
BINS = 10

MODELS = {
    "logistic": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    "random forest": lambda: RandomForestClassifier(
        n_estimators=300, min_samples_leaf=5, n_jobs=8, random_state=0
    ),  # fmt: skip
    "XGBoost": lambda: XGBClassifier(
        n_estimators=300,
        learning_rate=0.1,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=8,
        random_state=0,
    ),  # fmt: skip
}


def ece(y, p, bins=BINS):
    """Expected calibration error with equal-width bins: the mean gap between the
    predicted probability and the observed share, weighted by the rows in each bin."""
    idx = np.minimum((p * bins).astype(int), bins - 1)
    total = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            total += m.sum() * abs(p[m].mean() - y[m].mean())
    return total / len(y)


def out_of_fold(task, make, method, splits):
    p = np.empty(len(task.y))
    for train, test in splits:
        model = make()
        if method != "raw":
            model = CalibratedClassifierCV(model, method=method, cv=3)
        model.fit(task.X[train], task.y[train])
        p[test] = model.predict_proba(task.X[test])[:, 1]
    return p


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    task = tasks.undergrounded(connect(), "taito")
    y = task.y
    print(f"## {task.name}: {len(y):,} scenes, {y.mean():.1%} undergrounded; "
          f"{len(np.unique(task.groups['cell_250m']))} cells of 250 m")  # fmt: skip
    schemes = {
        "random 5 folds": list(StratifiedKFold(5, shuffle=True, random_state=0).split(task.X, y)),
        "250 m cells held out": list(GroupKFold(5).split(task.X, y, task.groups["cell_250m"])),
    }
    curves = {}
    for scheme, splits in schemes.items():
        print(f"\n### {scheme}")
        print("   model           calibration    AUC    Brier   log loss    ECE   mean p")
        for name, make in MODELS.items():
            for method in ("raw", "sigmoid", "isotonic"):
                p = out_of_fold(task, make, method, splits)
                curves[(scheme, name, method)] = p
                print(f"   {name:<15} {method:<12} {roc_auc_score(y, p):.3f}  {brier_score_loss(y, p):.4f}"
                      f"  {log_loss(y, np.clip(p, 1e-6, 1 - 1e-6)):>8.4f}  {ece(y, p):.4f}"
                      f"  {p.mean():.3f}", flush=True)  # fmt: skip

    for scheme in schemes:
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
        for ax, method in zip(axes, ("raw", "sigmoid", "isotonic"), strict=True):
            ax.plot([0, 1], [0, 1], color="grey", linestyle="--", linewidth=0.8)
            for name in MODELS:
                p = curves[(scheme, name, method)]
                frac, mean = calibration_curve(y, p, n_bins=BINS, strategy="quantile")
                ax.plot(mean, frac, marker="o", label=f"{name} (ECE {ece(y, p):.3f})")
            ax.set_title(f"{scheme}: {method}")
            ax.set_xlabel("predicted probability")
            ax.legend(fontsize=8)
        axes[0].set_ylabel("observed share undergrounded")
        fig.tight_layout()
        fig.savefig(OUT / f"reliability-{scheme.split()[0]}.png", dpi=120)
        plt.close(fig)
    print(f"\nfigures: {OUT}")


if __name__ == "__main__":
    main()
