"""Step 4B: two kinds of leakage, made on purpose, on Taito's undergrounded problem.

1. Target encoding: add "share of undergrounded scenes in the same 250 m cell".
   Computed on all rows, each test row's own answer is inside its feature.
   Computed from the training fold only, it is an honest feature.
2. Time: train on scenes up to 2020 and test on 2021 onwards, against a random
   split of the same rows, which lets later scenes of a place teach the model
   about earlier ones.

Model: XGBoost as in step 4A. Scores are pooled AUC.

    uv run python src/004-B-data-leakage/run.py
"""

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, KFold
from xgboost import XGBClassifier

from study_geoai import tasks
from study_geoai.db import connect


def xgb():
    return XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, subsample=0.8,
                         colsample_bytree=0.8, n_jobs=8, random_state=0)  # fmt: skip


def cell_share(cells, y, fit_rows, apply_rows, smoothing=10):
    """Share of positives per cell, learnt on fit_rows, smoothed towards the overall share."""
    prior = y[fit_rows].mean()
    uniq, inv = np.unique(cells[fit_rows], return_inverse=True)
    pos = np.bincount(inv, weights=y[fit_rows])
    n = np.bincount(inv)
    share = dict(zip(uniq, (pos + smoothing * prior) / (n + smoothing), strict=True))
    return np.array([share.get(c, prior) for c in cells[apply_rows]])


def target_encoding(task):
    cells, y = task.groups["cell_250m"], task.y
    everything = np.arange(len(y))
    leaky = np.column_stack([task.X, cell_share(cells, y, everything, everything)])
    block = (np.floor(task.groups["lon"] / 0.01).astype(int) * 100_000
             + np.floor(task.groups["lat"] / 0.01).astype(int))  # fmt: skip
    print("\n## target encoding: share of undergrounded scenes in the same 250 m cell")
    print("   split        without    computed on all rows    computed in the training fold")
    for label, folds in (
        ("random", lambda: KFold(5, shuffle=True, random_state=0).split(task.X)),
        (
            "block 1 km",
            lambda: GroupKFold(5, shuffle=True, random_state=0).split(task.X, groups=block),
        ),
    ):
        base = np.empty(len(y))
        bad = np.empty(len(y))
        good = np.empty(len(y))
        for train, test in folds():
            base[test] = xgb().fit(task.X[train], y[train]).predict_proba(task.X[test])[:, 1]
            bad[test] = xgb().fit(leaky[train], y[train]).predict_proba(leaky[test])[:, 1]
            # Honest: the training rows' own feature is computed out of fold inside the
            # training set, so the model never learns from a feature containing its label.
            inner = np.empty(len(train))
            for itr, ite in KFold(5, shuffle=True, random_state=1).split(train):
                inner[ite] = cell_share(cells, y, train[itr], train[ite])
            Xtr = np.column_stack([task.X[train], inner])
            Xte = np.column_stack([task.X[test], cell_share(cells, y, train, test)])
            good[test] = xgb().fit(Xtr, y[train]).predict_proba(Xte)[:, 1]
        print(f"   {label:10}   {roc_auc_score(y, base):.3f}      {roc_auc_score(y, bad):.3f}"
              f"                   {roc_auc_score(y, good):.3f}")  # fmt: skip


def time_split(task):
    year, y = task.groups["capture_year"], task.y
    past, future = year <= 2020, year >= 2021
    print(f"\n## time: {past.sum():,} scenes up to 2020, {future.sum():,} from 2021")
    print(
        f"   undergrounded share: up to 2020 {y[past].mean():.3f}, from 2021 {y[future].mean():.3f}"
    )
    m = xgb().fit(task.X[past], y[past])
    print(
        f"   train up to 2020, test from 2021:       {roc_auc_score(y[future], m.predict_proba(task.X[future])[:, 1]):.3f}"
    )
    m = xgb().fit(task.X[future], y[future])
    print(
        f"   train from 2021, test up to 2020:       {roc_auc_score(y[past], m.predict_proba(task.X[past])[:, 1]):.3f}"
    )
    pred = np.empty(len(y))
    for train, test in KFold(5, shuffle=True, random_state=0).split(task.X):
        pred[test] = xgb().fit(task.X[train], y[train]).predict_proba(task.X[test])[:, 1]
    print(
        f"   random split, scored on the 2021 rows:   {roc_auc_score(y[future], pred[future]):.3f}"
    )
    # Same size of training data as the time split, drawn at random from all years.
    rng = np.random.default_rng(0)
    train = rng.choice(len(y), past.sum(), replace=False)
    test = np.setdiff1d(np.flatnonzero(future), train)
    m = xgb().fit(task.X[train], y[train])
    print(f"   random {past.sum():,} rows of any year, test on unseen 2021 rows: "
          f"{roc_auc_score(y[test], m.predict_proba(task.X[test])[:, 1]):.3f}")  # fmt: skip


def main():
    task = tasks.undergrounded(connect(), "taito")
    print(f"{task.name}: {len(task.y):,} scenes")
    target_encoding(task)
    time_split(task)


if __name__ == "__main__":
    main()
