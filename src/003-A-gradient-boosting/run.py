"""Step 3: gradient boosting on mobile download speed, 23 wards of Tokyo.

One row per Ookla zoom-16 tile (about 610 m) with mobile tests in 2026 Q2.
Target: log of the mean download speed. Features from WorldPop, Overture and
michiyomi (study_geoai.features.tiles). Tiles with a speed of 0 are dropped.

Each tile's speed is a mean over tests, so tiles with few tests are noisy.
Scores are R2 weighted by the number of tests, from 5-fold predictions pooled
(random split). Models are trained without and with tests as sample weights.

    uv run python src/003-A-gradient-boosting/run.py
"""

import time
from pathlib import Path

import numpy as np
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from study_geoai import aoi, features
from study_geoai.db import connect

OUT = Path(__file__).parent / "output"
FEATURES = ["log_population", "coverage", "log_buildings", "log_places", "undergrounded_share",
            "mean_poles", "mean_green"]  # fmt: skip


def load(con, name):
    area = aoi.load(name, con)
    features.tiles(con, area).create_view("t")
    rows = con.sql("""
        select ln(avg_d_kbps), tests, ln(1 + population), coverage, ln(1 + n_buildings),
               ln(1 + n_places), undergrounded_share, mean_poles, mean_green
        from t where avg_d_kbps > 0 order by quadkey
    """).fetchall()
    dropped = con.sql("select count(*) from t where avg_d_kbps <= 0").fetchone()[0]
    a = np.array(rows, dtype=float)
    return a[:, 0], a[:, 1], a[:, 2:], dropped


def models():
    impute = SimpleImputer(strategy="median", add_indicator=True)
    return {
        "linear": make_pipeline(impute, StandardScaler(), LinearRegression()),
        "random forest": make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True),
            RandomForestRegressor(200, min_samples_leaf=5, n_jobs=8, random_state=0),
        ),
        "sklearn HistGB": HistGradientBoostingRegressor(
            learning_rate=0.05, max_iter=400, max_leaf_nodes=15, min_samples_leaf=20,
            random_state=0,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=400, learning_rate=0.05, max_depth=4, subsample=0.8,
            colsample_bytree=0.8, n_jobs=8, random_state=0,
        ),
        "LightGBM": LGBMRegressor(
            n_estimators=400, learning_rate=0.05, num_leaves=15, min_child_samples=20,
            subsample=0.8, subsample_freq=1, colsample_bytree=0.8, n_jobs=8, random_state=0,
            verbose=-1,
        ),
        "CatBoost": CatBoostRegressor(
            iterations=400, learning_rate=0.05, depth=4, random_seed=0, verbose=0,
            thread_count=8, allow_writing_files=False,
        ),
    }  # fmt: skip


def fit_step(model, X, y, w):
    """Fit with sample weights, passing them to the last step of a pipeline."""
    if hasattr(model, "steps"):
        model.fit(X, y, **{f"{model.steps[-1][0]}__sample_weight": w})
    else:
        model.fit(X, y, sample_weight=w)
    return model


def pooled(make, X, y, tests, weighted):
    pred = np.empty_like(y)
    for train, test in KFold(5, shuffle=True, random_state=0).split(X):
        w = tests[train] if weighted else np.ones(len(train))
        pred[test] = fit_step(make(), X[train], y[train], w).predict(X[test])
    return r2_score(y, pred, sample_weight=tests), r2_score(y, pred)


def main():
    con = connect()
    for name in ("tokyo23", "taito"):
        y, tests, X, dropped = load(con, name)
        print(f"\n## {name}: {len(y):,} tiles ({dropped} with speed 0 dropped), "
              f"{int(tests.sum()):,} tests, median {np.exp(np.median(y)) / 1000:.0f} Mbps")  # fmt: skip
        print(
            f"   tiles with 1 test: {(tests == 1).mean():.0%}, with 10 or more: {(tests >= 10).mean():.0%}"
        )
        print(
            "   model            R2 weighted by tests (unweighted)   trained unweighted | weighted"
        )
        for label in models():
            t0 = time.monotonic()
            make = lambda label=label: models()[label]  # noqa: E731
            u = pooled(make, X, y, tests, weighted=False)
            w = pooled(make, X, y, tests, weighted=True)
            print(f"   {label:15}  {u[0]:.3f} ({u[1]:.3f})  |  {w[0]:.3f} ({w[1]:.3f})"
                  f"   {time.monotonic() - t0:.1f} s", flush=True)  # fmt: skip
        if name == "tokyo23":
            model = LGBMRegressor(**models()["LightGBM"].get_params()).fit(
                X, y, sample_weight=tests
            )
            gain = model.booster_.feature_importance("gain")
            order = np.argsort(-gain)
            print("   LightGBM gain importance (weighted fit): "
                  + ", ".join(f"{FEATURES[i]} {gain[i] / gain.sum():.2f}" for i in order))  # fmt: skip


if __name__ == "__main__":
    main()
