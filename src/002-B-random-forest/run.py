"""Step 2B: random forests against one tree and the linear models.

Scores are 5-fold cross-validated predictions pooled and scored once (step 2A
showed that per-fold means can be dragged by one low-variance fold), random
split as before. A 2-D partial dependence shows the interaction a linear
model cannot represent.

    uv run python src/002-B-random-forest/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor  # noqa: E402
from sklearn.inspection import partial_dependence  # noqa: E402
from sklearn.linear_model import LinearRegression, LogisticRegression  # noqa: E402
from sklearn.metrics import r2_score, roc_auc_score  # noqa: E402
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor  # noqa: E402

from study_geoai import tasks  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"


def pooled(model, task, regression, cv):
    if regression:
        return r2_score(task.y, cross_val_predict(model, task.X, task.y, cv=cv))
    p = cross_val_predict(model, task.X, task.y, cv=cv, method="predict_proba")[:, 1]
    return roc_auc_score(task.y, p)


def models(regression, big):
    # Big data: each tree sees 10 % of the rows, and leaves hold at least 20, to bound memory.
    rf = dict(n_estimators=100 if big else 200, n_jobs=8, random_state=0,
              max_samples=0.1 if big else None)  # fmt: skip
    if regression:
        return {
            "linear": make_pipeline(StandardScaler(), LinearRegression()),
            "tree (depth 5)": DecisionTreeRegressor(max_depth=5, random_state=0),
            "forest, leaf >= 1": RandomForestRegressor(min_samples_leaf=1, **rf),
            "forest, leaf >= 5": RandomForestRegressor(min_samples_leaf=5, **rf),
        }
    small_leaf, large_leaf = (20, 100) if big else (5, 20)
    return {
        "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "tree (best depth)": DecisionTreeClassifier(max_depth=11 if big else 7, random_state=0),
        f"forest, leaf >= {small_leaf}": RandomForestClassifier(min_samples_leaf=small_leaf, **rf),
        f"forest, leaf >= {large_leaf}": RandomForestClassifier(min_samples_leaf=large_leaf, **rf),
    }


def interaction(task, forest, path):
    i, j = task.features.index("roadway_width_m"), task.features.index("green_ratio")
    # 5,000 rows are plenty for an average over the grid, and bound memory.
    rows = np.random.default_rng(0).choice(len(task.y), min(5_000, len(task.y)), replace=False)
    pd = partial_dependence(forest, task.X[rows], [(i, j)], grid_resolution=25, kind="average")
    widths, greens = pd["grid_values"]
    fig, ax = plt.subplots(figsize=(6, 5))
    mesh = ax.pcolormesh(widths, greens, pd["average"][0].T, shading="auto", cmap="viridis")
    ax.set_xlabel("roadway_width_m")
    ax.set_ylabel("green_ratio")
    ax.set_title(f"{task.name}: partial dependence of P(undergrounded)")
    fig.colorbar(mesh, ax=ax, label="average predicted probability")
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


def subsample(task, n):
    rng = np.random.default_rng(0)
    rows = np.concatenate([
        rng.choice(np.flatnonzero(task.y == c), round(n * (task.y == c).mean()), replace=False)
        for c in np.unique(task.y)
    ])  # fmt: skip
    rows.sort()
    groups = {k: v[rows] for k, v in task.groups.items()}
    return tasks.Task(f"{task.name}-sample", task.features, task.X[rows], task.y[rows], groups)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    for task, regression in (
        (tasks.density(con, "taito"), True),
        (tasks.density(con, "tokyo23"), True),
        (tasks.undergrounded(con, "taito"), False),
        (tasks.undergrounded(con, "tokyo23"), False),
    ):
        big = len(task.y) > 100_000
        if big:
            # A forest over 988,619 rows peaked at 16 GB RSS; a stratified 200,000 is enough here.
            task = subsample(task, 200_000)
        cv = (KFold if regression else StratifiedKFold)(
            3 if big else 5, shuffle=True, random_state=0
        )
        metric = "R2" if regression else "AUC"
        print(f"\n## {task.name}: {len(task.y):,} rows, pooled {cv.get_n_splits()}-fold {metric}")
        for label, model in models(regression, big).items():
            print(f"   {label:20} {pooled(model, task, regression, cv):.3f}", flush=True)
        forest = list(models(regression, big).values())[2].fit(task.X, task.y)
        imp = sorted(
            zip(task.features, forest.feature_importances_, strict=True), key=lambda x: -x[1]
        )
        print("   impurity importance: " + ", ".join(f"{f} {v:.2f}" for f, v in imp))
        if not regression:
            print(
                f"   partial dependence: {interaction(task, forest, OUT / f'pd-{task.name}.png')}"
            )


if __name__ == "__main__":
    main()
