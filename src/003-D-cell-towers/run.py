"""Step 3D: does adding cell towers make mobile speed predictable?

Same tiles, target and scoring as step 3A (log mean download speed per Ookla
zoom-16 tile, 2026 Q2, R2 weighted by tests from pooled 5-fold predictions,
random split), with OpenCelliD cells (2024-06-14) added per tile: counts by
radio, number of operators, distance from the tile centre to the nearest
cell, and the cells' mean estimated range.

    uv run python src/003-D-cell-towers/run.py
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

from study_geoai import aoi, features, opencellid
from study_geoai.db import connect

BASE = ["log_population", "coverage", "log_buildings", "log_places", "undergrounded_share",
        "mean_poles", "mean_green"]  # fmt: skip
CELLS = ["log_cells", "log_lte", "log_nr", "operators", "log_nearest_m", "log_mean_range_m"]


def load(con, name):
    area = aoi.load(name, con)
    features.tiles(con, area).create_view("t")
    opencellid.cells(con, area).create_view("c")
    rows = con.sql("""
        with inside as (
            select t.quadkey, count(*) as n, count(*) filter (where c.radio = 'LTE') as lte,
                   count(*) filter (where c.radio = 'NR') as nr, count(distinct c.net) as nets,
                   avg(c.range_m) as mean_range
            from t join c on st_contains(t.geometry, c.geometry)
            group by t.quadkey
        ),
        nearest as (
            select t.quadkey,
                   min(st_distance_sphere(st_centroid(t.geometry), c.geometry)) as nearest_m
            from t join c on st_dwithin(st_centroid(t.geometry), c.geometry, 0.02)
            group by t.quadkey
        )
        select ln(t.avg_d_kbps), t.tests, ln(1 + t.population), t.coverage,
               ln(1 + t.n_buildings), ln(1 + t.n_places), t.undergrounded_share, t.mean_poles,
               t.mean_green,
               ln(1 + coalesce(i.n, 0)), ln(1 + coalesce(i.lte, 0)), ln(1 + coalesce(i.nr, 0)),
               coalesce(i.nets, 0), ln(1 + n.nearest_m), ln(i.mean_range)
        from t left join inside i using (quadkey) left join nearest n using (quadkey)
        where t.avg_d_kbps > 0 order by t.quadkey
    """).fetchall()
    a = np.array(rows, dtype=float)
    return a[:, 0], a[:, 1], a[:, 2:]


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


def pooled(label, X, y, tests):
    pred = np.empty_like(y)
    for train, test in KFold(5, shuffle=True, random_state=0).split(X):
        m = models()[label]
        if hasattr(m, "steps"):
            m.fit(X[train], y[train], **{f"{m.steps[-1][0]}__sample_weight": tests[train]})
        else:
            m.fit(X[train], y[train], sample_weight=tests[train])
        pred[test] = m.predict(X[test])
    return r2_score(y, pred, sample_weight=tests)


def main():
    con = connect()
    for name in ("tokyo23",):
        y, tests, X = load(con, name)
        base = X[:, : len(BASE)]
        print(f"\n## {name}: {len(y):,} tiles; R2 weighted by tests, trained with tests as weights")
        for i, f in enumerate(CELLS):
            col = X[:, len(BASE) + i]
            ok = ~np.isnan(col)
            r = np.corrcoef(col[ok], y[ok])[0, 1]
            print(f"   correlation with log speed: {f:18} {r:+.3f}  ({ok.sum():,} tiles)")
        print("   model            without cells   with cells")
        for label in models():
            print(f"   {label:15}  {pooled(label, base, y, tests):.3f}          "
                  f"{pooled(label, X, y, tests):.3f}", flush=True)  # fmt: skip


if __name__ == "__main__":
    main()
