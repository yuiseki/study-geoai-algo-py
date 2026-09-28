"""Step 4A: the same model, scored with different ways of splitting the data.

Steps 1 to 3 used random 5-fold splits. Street scenes of the same place in
other years, scenes of the same capture run, and neighbouring small areas all
look alike, so a random split puts near copies of a test row in training.
Here only the split changes:

- random: shuffled 5-fold (as before)
- sequence: GroupKFold by michiyomi's capture run (sequence_id)
- cell 250 m: GroupKFold by michiyomi's 250 m cell (the same place, all years)
- block 1 km / 2 km: GroupKFold by a lon/lat grid of about 0.9 / 1.8 km
- ward: leave one ward out (23 wards only)

Models: XGBoost (learning rate 0.1, depth 6, 100 trees, as step 3B found) for
undergrounded, random forest for density. Scores are pooled over folds.

    uv run python src/004-A-cross-validation/run.py
"""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import GroupKFold, KFold, LeaveOneGroupOut
from xgboost import XGBClassifier

from study_geoai import tasks
from study_geoai.db import connect


def block(task, size):
    return (np.floor(task.groups["lon"] / size).astype(int) * 100_000
            + np.floor(task.groups["lat"] / size).astype(int))  # fmt: skip


def splits(task, ward_key):
    out = {"random": KFold(5, shuffle=True, random_state=0).split(task.X)}
    for label, groups in (
        ("sequence", task.groups.get("sequence_id")),
        ("cell 250 m", task.groups.get("cell_250m")),
        ("block 1 km", block(task, 0.01)),
        ("block 2 km", block(task, 0.02)),
    ):
        if groups is not None and len(np.unique(groups)) >= 5:
            out[label] = GroupKFold(5, shuffle=True, random_state=0).split(task.X, groups=groups)
    wards = task.groups.get(ward_key)
    if wards is not None and len(np.unique(wards)) > 1:
        out["ward"] = LeaveOneGroupOut().split(task.X, groups=wards)
    return out


def score(task, make, folds, classification):
    pred = np.full(len(task.y), np.nan)
    for train, test in folds:
        m = make().fit(task.X[train], task.y[train])
        pred[test] = (
            m.predict_proba(task.X[test])[:, 1] if classification else m.predict(task.X[test])
        )
    if classification:
        return roc_auc_score(task.y, pred), pred
    return r2_score(task.y, pred), pred


def sample(task, n):
    rng = np.random.default_rng(0)
    rows = np.sort(np.concatenate([
        rng.choice(np.flatnonzero(task.y == c), round(n * (task.y == c).mean()), replace=False)
        for c in (0, 1)
    ]))  # fmt: skip
    groups = {k: v[rows] for k, v in task.groups.items()}
    return tasks.Task(f"{task.name}-sample", task.features, task.X[rows], task.y[rows], groups)


def xgb():
    return XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, subsample=0.8,
                         colsample_bytree=0.8, n_jobs=8, random_state=0)  # fmt: skip


def forest():
    return RandomForestRegressor(300, min_samples_leaf=5, n_jobs=8, random_state=0)


def main():
    con = connect()
    runs = [
        (tasks.undergrounded(con, "taito"), xgb, True, "ward"),
        (sample(tasks.undergrounded(con, "tokyo23"), 200_000), xgb, True, "ward"),
        (tasks.density(con, "taito"), forest, False, "code5"),
        (tasks.density(con, "tokyo23"), forest, False, "code5"),
    ]
    for task, make, classification, ward_key in runs:
        metric = "AUC" if classification else "R2"
        print(f"\n## {task.name}: {len(task.y):,} rows, pooled {metric}")
        for label, folds in splits(task, ward_key).items():
            s, pred = score(task, make, folds, classification)
            print(f"   {label:12} {s:.3f}", flush=True)
            if label == "ward":
                wards = task.groups[ward_key]
                taito = wards == ("台東区" if classification else "13106")
                if taito.any():
                    if classification:
                        t = roc_auc_score(task.y[taito], pred[taito])
                    else:
                        t = r2_score(task.y[taito], pred[taito])
                    print(f"   {'':12} Taito City scored by a model of the other 22 wards: {t:.3f}")


if __name__ == "__main__":
    main()
