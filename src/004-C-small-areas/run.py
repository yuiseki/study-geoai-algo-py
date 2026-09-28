"""Step 4C: is the large drop in Taito City's spatial CV about small areas in general?

Step 4A found that spatial blocks cut Taito's scores a lot, but hardly the
23 wards'. Hypothesis: a small area has few blocks, so a held-out block's kind
of place is rarely learnt elsewhere. If so, every ward, cross-validated within
itself, should drop too, and small wards (few blocks) more. The alternative is
something particular to Taito, such as undergrounding clustered in tourist
districts; then the other wards should drop little.

For each ward: AUC of random and 2 km block 5-fold CV inside the ward, the
number of 2 km blocks, and the AUC of a model trained on the other 22 wards.

    uv run python src/004-C-small-areas/run.py
"""

import numpy as np
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import GroupKFold, KFold
from xgboost import XGBClassifier

from study_geoai import tasks
from study_geoai.db import connect


def xgb():
    return XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, subsample=0.8,
                         colsample_bytree=0.8, n_jobs=8, random_state=0)  # fmt: skip


def forest():
    return RandomForestRegressor(300, min_samples_leaf=5, n_jobs=8, random_state=0)


def blocks(g, size=0.02):
    return np.floor(g["lon"] / size).astype(int) * 100_000 + np.floor(g["lat"] / size).astype(int)


def cv(X, y, folds, make, classification):
    pred = np.empty(len(y))
    for train, test in folds:
        m = make().fit(X[train], y[train])
        pred[test] = m.predict_proba(X[test])[:, 1] if classification else m.predict(X[test])
    return roc_auc_score(y, pred) if classification else r2_score(y, pred)


def per_ward(task, ward_key, make, classification, min_rows):
    wards = task.groups[ward_key]
    b = blocks(task.groups)
    metric = "AUC" if classification else "R2"
    print(
        f"\n## {task.name}: {len(task.y):,} rows; {metric} inside each ward, and from the other 22"
    )
    print("   ward        rows     2 km blocks   random   block 2 km   drop    other 22 wards")
    drops, sizes = [], []
    for w in sorted(set(wards.tolist())):
        m = wards == w
        X, y, g = task.X[m], task.y[m], b[m]
        n_blocks = len(np.unique(g))
        if len(y) < min_rows or n_blocks < 5 or (classification and len(np.unique(y)) < 2):
            print(f"   {w:10}  {len(y):>7,}   {n_blocks:>3}   (skipped: too few rows or blocks)")
            continue
        rnd = cv(X, y, KFold(5, shuffle=True, random_state=0).split(X), make, classification)
        blk = cv(X, y, GroupKFold(5, shuffle=True, random_state=0).split(X, groups=g), make,
                 classification)  # fmt: skip
        other = make().fit(task.X[~m], task.y[~m])
        p = other.predict_proba(X)[:, 1] if classification else other.predict(X)
        out = roc_auc_score(y, p) if classification else r2_score(y, p)
        drops.append(rnd - blk)
        sizes.append(n_blocks)
        print(f"   {w:10}  {len(y):>7,}   {n_blocks:>3}           {rnd:.3f}    {blk:.3f}       "
              f"{rnd - blk:+.3f}   {out:.3f}", flush=True)  # fmt: skip
    rho, p = spearmanr(sizes, drops)
    print(f"   drop against number of blocks: Spearman {rho:+.2f} (p {p:.3f}, {len(drops)} wards); "
          f"median drop {np.median(drops):+.3f}")  # fmt: skip


def main():
    con = connect()
    per_ward(tasks.undergrounded(con, "tokyo23"), "ward", xgb, True, min_rows=2_000)
    per_ward(tasks.density(con, "tokyo23"), "code5", forest, False, min_rows=50)


if __name__ == "__main__":
    main()
