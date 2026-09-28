"""Step 2A: decision trees on the two problems of step 1, and how they overfit.

For each problem and area, the tree depth goes from 1 to 15 and the score on
the training data is set against 5-fold cross-validation (random split, as in
step 1; step 4 revisits the split). A shallow tree is printed as rules.

    uv run python src/002-A-decision-tree/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.linear_model import LinearRegression, LogisticRegression  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import KFold, StratifiedKFold, cross_validate  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text  # noqa: E402

from study_geoai import tasks  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
DEPTHS = list(range(1, 16))


def sweep(task, regression):
    if regression:
        cv, scoring = KFold(5, shuffle=True, random_state=0), "r2"
        make = lambda d: DecisionTreeRegressor(max_depth=d, random_state=0)  # noqa: E731
        linear = make_pipeline(StandardScaler(), LinearRegression())
    else:
        cv, scoring = StratifiedKFold(5, shuffle=True, random_state=0), "roc_auc"
        make = lambda d: DecisionTreeClassifier(max_depth=d, random_state=0)  # noqa: E731
        linear = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    train, test = [], []
    for d in DEPTHS:
        r = cross_validate(make(d), task.X, task.y, cv=cv, scoring=scoring,
                           return_train_score=True, n_jobs=5)  # fmt: skip
        train.append(r["train_score"].mean())
        test.append(r["test_score"].mean())
    lin = cross_validate(linear, task.X, task.y, cv=cv, scoring=scoring)["test_score"].mean()
    return train, test, lin, scoring, make


def main():
    con = connect()
    problems = [
        (tasks.density(con, "taito"), True),
        (tasks.density(con, "tokyo23"), True),
        (tasks.undergrounded(con, "taito"), False),
        (tasks.undergrounded(con, "tokyo23"), False),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    for ax, (task, regression) in zip(axes.ravel(), problems, strict=True):
        train, test, lin, scoring, make = sweep(task, regression)
        best = int(np.argmax(test))
        print(f"\n## {task.name}: {len(task.y):,} rows, {scoring}")
        print(f"   linear model (step 1), 5-fold: {lin:.3f}")
        print(
            f"   best tree depth {DEPTHS[best]}: 5-fold {test[best]:.3f}, train {train[best]:.3f}"
        )
        print(f"   depth 15: 5-fold {test[-1]:.3f}, train {train[-1]:.3f}")
        tree = make(2).fit(task.X, task.y)
        print("   depth-2 tree:")
        for line in export_text(tree, feature_names=task.features, decimals=3).splitlines():
            print("     " + line)
        if not regression:
            p = tree.predict_proba(task.X)[:, 1]
            print(f"   depth-2 tree AUC on training data: {roc_auc_score(task.y, p):.3f}")
        ax.plot(DEPTHS, train, marker="o", label="train")
        ax.plot(DEPTHS, test, marker="o", label="5-fold CV")
        ax.axhline(lin, color="grey", linestyle="--", label="linear, 5-fold CV")
        ax.set_title(f"{task.name} ({len(task.y):,} rows)")
        ax.set_ylabel(scoring)
        ax.legend(fontsize=8)
    for ax in axes[-1]:
        ax.set_xlabel("max_depth")
    OUT.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT / "depth.png", dpi=120)
    print(f"\nplot: {OUT / 'depth.png'}")


if __name__ == "__main__":
    main()
