"""Step 3E: a less noisy target by pooling three quarters of mobile speed.

Step 3C found the per-tile speed of one quarter mostly noise (the previous
quarter explains R2 0.15). Here each tile's target pools 2025 Q4, 2026 Q1
and 2026 Q2: log speed minus that quarter's tests-weighted mean over the 23
wards (quarters shift as a whole), averaged with the quarters' tests as
weights. Features, models and scoring as in steps 3A and 3D, on the same
2,246 tiles of 2026 Q2, with the pooled test count as the weight.

    uv run python src/003-E-pooled-target/run.py
"""

import numpy as np
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from study_geoai import aoi, features, ookla
from study_geoai.db import connect

QUARTERS = [(2025, 4), (2026, 1), (2026, 2)]
BASE = 7  # the first 7 features are step 3A's; the rest are step 3D's cell features


def load(con, name):
    area = aoi.load(name, con)
    for i, (y, q) in enumerate(QUARTERS):
        ookla.tiles(con, area, "mobile", y, q).create_view(f"q{i}")
    features.tiles(con, area).create_view("t")
    features.tile_cells(con, area).create_view("tc")
    union = " union all ".join(
        f"select quadkey, ln(avg_d_kbps) - (select sum(tests * ln(avg_d_kbps)) / sum(tests) "
        f"from q{i} where avg_d_kbps > 0) as centred, tests, {i} as quarter "
        f"from q{i} where avg_d_kbps > 0"
        for i in range(len(QUARTERS))
    )
    rows = con.sql(f"""
        with all_quarters as ({union}),
        pooled as (
            select quadkey, sum(tests * centred) / sum(tests) as target, sum(tests) as tests,
                   count(*) as quarters
            from all_quarters group by quadkey
        ),
        current as (
            select quadkey, centred as target, tests from all_quarters where quarter = 2
        )
        select p.target, p.tests, c.target, c.tests, p.quarters,
               ln(1 + t.population), t.coverage, ln(1 + t.n_buildings), ln(1 + t.n_places),
               t.undergrounded_share, t.mean_poles, t.mean_green,
               ln(1 + tc.n_cells), ln(1 + tc.n_lte), ln(1 + tc.n_nr), tc.operators,
               ln(1 + tc.nearest_m), ln(tc.mean_range_m)
        from t join pooled p using (quadkey) join current c using (quadkey)
        left join tc using (quadkey)
        order by t.quadkey
    """).fetchall()
    a = np.array(rows, dtype=float)
    return a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5:]


def models():
    return {
        "linear": make_pipeline(SimpleImputer(strategy="median", add_indicator=True),
                                StandardScaler(), LinearRegression()),
        "sklearn HistGB": HistGradientBoostingRegressor(
            learning_rate=0.05, max_iter=400, max_leaf_nodes=15, min_samples_leaf=20,
            random_state=0),
        "XGBoost": XGBRegressor(n_estimators=400, learning_rate=0.05, max_depth=4, subsample=0.8,
                                colsample_bytree=0.8, n_jobs=8, random_state=0),
        "LightGBM": LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=15,
                                  min_child_samples=20, subsample=0.8, subsample_freq=1,
                                  colsample_bytree=0.8, n_jobs=8, random_state=0, verbose=-1),
        "CatBoost": CatBoostRegressor(iterations=400, learning_rate=0.05, depth=4, random_seed=0,
                                      verbose=0, thread_count=8, allow_writing_files=False),
    }  # fmt: skip


def pooled_r2(label, X, y, w, seed=0):
    pred = np.empty_like(y)
    for train, test in KFold(5, shuffle=True, random_state=seed).split(X):
        m = models()[label]
        if hasattr(m, "steps"):
            m.fit(X[train], y[train], **{f"{m.steps[-1][0]}__sample_weight": w[train]})
        else:
            m.fit(X[train], y[train], sample_weight=w[train])
        pred[test] = m.predict(X[test])
    return r2_score(y, pred, sample_weight=w)


def main():
    con = connect()
    y_pool, w_pool, y_now, w_now, nq, X = load(con, "tokyo23")
    print(f"23 wards: {len(y_pool):,} tiles of 2026 Q2")
    print(f"   quarters per tile: 1 {np.mean(nq == 1):.0%}, 2 {np.mean(nq == 2):.0%}, "
          f"3 {np.mean(nq == 3):.0%}")  # fmt: skip
    print(
        f"   tests per tile, median: one quarter {np.median(w_now):.0f}, pooled {np.median(w_pool):.0f}"
    )
    print("\nR2 weighted by tests, pooled 5-fold predictions (random split)")
    print("   model            one quarter          pooled target")
    print("                    base    + cells      base    + cells")
    for label in models():
        r = [
            pooled_r2(label, X[:, :BASE], y_now, w_now),
            pooled_r2(label, X, y_now, w_now),
            pooled_r2(label, X[:, :BASE], y_pool, w_pool),
            pooled_r2(label, X, y_pool, w_pool),
        ]
        print(f"   {label:15}  {r[0]:+.3f}  {r[1]:+.3f}       {r[2]:+.3f}  {r[3]:+.3f}", flush=True)

    # With R2 around 0.1, are the differences between models more than the luck of the split?
    print("\nsame scores over 5 different random splits (seeds 0 to 4): mean, standard deviation")
    print("   model            one quarter, base      pooled, + cells")
    for label in models():
        a = [pooled_r2(label, X[:, :BASE], y_now, w_now, s) for s in range(5)]
        b = [pooled_r2(label, X, y_pool, w_pool, s) for s in range(5)]
        print(f"   {label:15}  {np.mean(a):+.3f} ({np.std(a):.3f})      "
              f"{np.mean(b):+.3f} ({np.std(b):.3f})", flush=True)  # fmt: skip


if __name__ == "__main__":
    main()
