"""Step 3B: XGBoost where there is signal, on the undergrounded problem.

Step 3A found almost no signal in mobile speed, so XGBoost is studied on the
undergrounded problem of steps 1B and 2 (random forest AUC 0.926 in Taito,
0.888 on the 23-ward sample). Learning rate and depth vary; the number of
trees is chosen by early stopping on a validation set carved out of each
training fold, never the test fold. Scores are pooled 5-fold AUC (random).

    uv run python src/003-B-xgboost/run.py
"""

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedKFold, train_test_split  # noqa: E402
from xgboost import XGBClassifier  # noqa: E402

from study_geoai import tasks  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
RATES = [0.3, 0.1, 0.03]
DEPTHS = [3, 6, 9]


def sample(task, n):
    """A stratified sample of n rows, as in step 2B (the full 23 wards peaked at 16 GB)."""
    rng = np.random.default_rng(0)
    rows = np.sort(np.concatenate([
        rng.choice(np.flatnonzero(task.y == c), round(n * (task.y == c).mean()), replace=False)
        for c in (0, 1)
    ]))  # fmt: skip
    return tasks.Task(f"{task.name}-sample", task.features, task.X[rows], task.y[rows], {})


def model(rate, depth):
    return XGBClassifier(
        n_estimators=3000, learning_rate=rate, max_depth=depth, subsample=0.8,
        colsample_bytree=0.8, eval_metric="auc", early_stopping_rounds=50,
        n_jobs=8, random_state=0,
    )  # fmt: skip


def evaluate(task, rate, depth):
    pred, rounds = np.empty(len(task.y)), []
    for train, test in StratifiedKFold(5, shuffle=True, random_state=0).split(task.X, task.y):
        Xtr, Xva, ytr, yva = train_test_split(
            task.X[train], task.y[train], test_size=0.2, stratify=task.y[train], random_state=0
        )
        m = model(rate, depth).fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
        pred[test] = m.predict_proba(task.X[test])[:, 1]
        rounds.append(m.best_iteration + 1)
    return roc_auc_score(task.y, pred), rounds


def curve(task, path):
    """Train and validation AUC by number of trees, without early stopping."""
    Xtr, Xva, ytr, yva = train_test_split(
        task.X, task.y, test_size=0.2, stratify=task.y, random_state=0
    )
    fig, axes = plt.subplots(1, len(RATES), figsize=(13, 4), sharey=True)
    for ax, rate in zip(axes, RATES, strict=True):
        m = XGBClassifier(n_estimators=1500, learning_rate=rate, max_depth=6, subsample=0.8,
                          colsample_bytree=0.8, eval_metric="auc", n_jobs=8, random_state=0)  # fmt: skip
        m.fit(Xtr, ytr, eval_set=[(Xtr, ytr), (Xva, yva)], verbose=False)
        r = m.evals_result()
        ax.plot(r["validation_0"]["auc"], label="train")
        ax.plot(r["validation_1"]["auc"], label="validation")
        best = int(np.argmax(r["validation_1"]["auc"]))
        ax.axvline(best, color="grey", linestyle="--")
        ax.set_title(f"learning_rate {rate}, depth 6 (best at {best + 1})")
        ax.set_xlabel("trees")
        ax.set_xscale("log")
    axes[0].set_ylabel("AUC")
    axes[0].legend()
    fig.suptitle(task.name)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    for task in (
        tasks.undergrounded(con, "taito"),
        sample(tasks.undergrounded(con, "tokyo23"), 200_000),
    ):
        print(f"\n## {task.name}: {len(task.y):,} rows, pooled 5-fold AUC")
        print("   rate   depth   AUC     trees chosen by early stopping (per fold)   time")
        for rate in RATES:
            for depth in DEPTHS:
                t0 = time.monotonic()
                auc, rounds = evaluate(task, rate, depth)
                print(f"   {rate:<5}  {depth:<5}   {auc:.3f}   {rounds}   {time.monotonic() - t0:.0f} s",
                      flush=True)  # fmt: skip
        print(f"   curves: {curve(task, OUT / f'curve-{task.name}.png')}")


if __name__ == "__main__":
    main()
