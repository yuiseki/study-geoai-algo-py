"""Step 4E: mobile speed again, with baselines, three ways to split, and where it goes wrong.

Steps 3A to 3E scored the speed models by a random split only. This step
finishes the evaluation that case study 001 asks for, on the same 2,246 tiles
of the 23 wards (2026 Q2), the same target (log download speed minus the
quarter's tests-weighted mean over the 23 wards), the same features (step 3A's
seven plus step 3D's six cell-tower features) and R2 weighted by tests.

1. Baselines: the overall mean, the mean of the tile's ward, and the tile's own
   previous quarter (2026 Q1), raw and shrunk (a line from the previous quarter
   fitted on the training rows, as step 3C did).
2. Three ways to split, the same models (linear, random forest, HistGradient-
   Boosting, XGBoost) and baselines in each:
   - random: 5-fold, pooled out-of-fold predictions
   - spatial blocks: GroupKFold over a lon/lat grid of 0.02 degree (about 2 km)
   - time, same tiles: learn 2026 Q1's speeds, predict 2026 Q2's on the same tiles
   - time + blocks: learn 2026 Q1 on some blocks, predict 2026 Q2 on the others
   Every column is scored on the tiles that have all three quarters.
3. Errors by place (ward, and how many tests the tile had) and by time (each
   quarter predicted from the one before).

    uv run python -u src/004-E-speed-evaluation/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor  # noqa: E402
from sklearn.impute import SimpleImputer  # noqa: E402
from sklearn.linear_model import LinearRegression  # noqa: E402
from sklearn.metrics import r2_score  # noqa: E402
from sklearn.model_selection import GroupKFold, KFold  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from xgboost import XGBRegressor  # noqa: E402

from study_geoai import aoi, features, ookla  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
QUARTERS = [(2025, 4), (2026, 1), (2026, 2)]
BLOCK = 0.02  # degrees, about 2 km
TEST_BINS = [(1, 1), (2, 9), (10, 29), (30, 10**9)]


def load(con):
    area = aoi.load("tokyo23", con)
    for i, (y, q) in enumerate(QUARTERS):
        ookla.tiles(con, area, "mobile", y, q).create_view(f"q{i}")
    features.tiles(con, area).create_view("t")
    features.tile_cells(con, area).create_view("tc")
    con.execute("create or replace temp table w (code5 varchar, wkt varchar)")
    con.executemany("insert into w values (?, ?)",
                    [(a.name, a.wkt) for a in aoi.wards(area, con)])  # fmt: skip
    centred = ", ".join(
        f"c{i} as (select quadkey, ln(avg_d_kbps) - (select sum(tests * ln(avg_d_kbps)) / sum(tests)"
        f" from q{i} where avg_d_kbps > 0) as y, tests from q{i} where avg_d_kbps > 0)"
        for i in range(len(QUARTERS))
    )
    rows = con.sql(f"""
        with {centred},
        ward as (
            select t.quadkey, any_value(w.code5) as code5
            from t join w on st_contains(st_geomfromtext(w.wkt), st_point(t.lon, t.lat))
            group by t.quadkey
        )
        select c2.y, c2.tests, c1.y, c1.tests, c0.y, c0.tests, t.lon, t.lat,
               coalesce(ward.code5, 'none'),
               ln(1 + t.population), t.coverage, ln(1 + t.n_buildings), ln(1 + t.n_places),
               t.undergrounded_share, t.mean_poles, t.mean_green,
               ln(1 + tc.n_cells), ln(1 + tc.n_lte), ln(1 + tc.n_nr), tc.operators,
               ln(1 + tc.nearest_m), ln(tc.mean_range_m)
        from t join c2 using (quadkey) left join c1 using (quadkey) left join c0 using (quadkey)
        left join tc using (quadkey) left join ward using (quadkey)
        order by t.quadkey
    """).fetchall()
    col = list(zip(*rows, strict=True))
    num = lambda i: np.array(col[i], dtype=float)  # noqa: E731
    return {
        "y": num(0), "w": num(1), "y_q1": num(2), "w_q1": num(3), "y_q0": num(4), "w_q0": num(5),
        "lon": num(6), "lat": num(7), "ward": np.array(col[8]),
        "ward_names": dict(con.sql(f"select code5, name from '{aoi._wards(con)}'").fetchall()),
        "X": np.column_stack([num(i) for i in range(9, len(col))]),
    }  # fmt: skip


def models():
    return {
        "linear": make_pipeline(SimpleImputer(strategy="median", add_indicator=True),
                                StandardScaler(), LinearRegression()),
        "random forest": make_pipeline(SimpleImputer(strategy="median"),
                                       RandomForestRegressor(300, min_samples_leaf=10, n_jobs=8,
                                                             random_state=0)),
        "HistGB": HistGradientBoostingRegressor(learning_rate=0.05, max_iter=400,
                                                max_leaf_nodes=15, min_samples_leaf=20,
                                                random_state=0),
        "XGBoost": XGBRegressor(n_estimators=400, learning_rate=0.05, max_depth=4, subsample=0.8,
                                colsample_bytree=0.8, n_jobs=8, random_state=0),
    }  # fmt: skip


def fit(model, X, y, w):
    if hasattr(model, "steps"):
        return model.fit(X, y, **{f"{model.steps[-1][0]}__sample_weight": w})
    return model.fit(X, y, sample_weight=w)


def evaluate(d, splits, fit_y, fit_w, fit_prev, score_prev):
    """Pooled predictions for the test rows of `splits`.

    Everything is learned from `fit_y` on the training rows: the overall and
    ward means, the models, and the shrunk previous quarter (a line fitted from
    `fit_prev` to `fit_y`). `score_prev` is the previous quarter of what is
    being predicted.
    """
    X = d["X"]
    pred = {}
    for train, test in splits:
        overall = np.average(fit_y[train], weights=fit_w[train])
        ward = {g: np.average(fit_y[train][d["ward"][train] == g],
                              weights=fit_w[train][d["ward"][train] == g])
                for g in np.unique(d["ward"][train])}  # fmt: skip
        b, a = np.polyfit(fit_prev[train], fit_y[train], 1, w=np.sqrt(fit_w[train]))
        got = {
            "overall mean": np.full(len(test), overall),
            "ward mean": np.array([ward.get(g, overall) for g in d["ward"][test]]),
            "previous quarter": score_prev[test],
            "previous quarter, shrunk": a + b * score_prev[test],
        }
        for name, m in models().items():
            got[name] = fit(m, X[train], fit_y[train], fit_w[train]).predict(X[test])
        for name, p in got.items():
            pred.setdefault(name, np.full(len(fit_y), np.nan))[test] = p
    return pred


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    con = connect()
    full = load(con)
    print(f"## 23 wards: {len(full['y']):,} tiles of 2026 Q2; wards found for "
          f"{np.mean(full['ward'] != 'none'):.1%}")  # fmt: skip
    keep = ~np.isnan(full["y_q1"]) & ~np.isnan(full["y_q0"])
    names_of = full.pop("ward_names")
    d = {k: v[keep] for k, v in full.items()}
    y, w, X = d["y"], d["w"], d["X"]
    n = len(y)
    print(f"   scored on the {n:,} tiles that have 2025 Q4, 2026 Q1 and 2026 Q2, so every column"
          " is the same tiles")  # fmt: skip
    blocks = np.floor(d["lon"] / BLOCK).astype(int) * 100_000 + np.floor(d["lat"] / BLOCK).astype(
        int
    )
    block_splits = list(GroupKFold(5, shuffle=True, random_state=0).split(X, groups=blocks))
    print(f"   spatial blocks of {BLOCK} degree: {len(np.unique(blocks))}")
    allrows = np.arange(n)
    q2 = (y, w, d["y_q1"], d["y_q1"])  # learn Q2, previous = Q1
    q1 = (d["y_q1"], d["w_q1"], d["y_q0"], d["y_q1"])  # learn Q1 (previous Q4), predict Q2
    designs = {
        "random": (list(KFold(5, shuffle=True, random_state=0).split(X)), q2),
        "spatial blocks": (block_splits, q2),
        "time, same tiles": ([(allrows, allrows)], q1),
        "time + blocks": (block_splits, q1),
    }
    scores, oof = {}, {}
    for design, (splits, (fy, fw, fp, sp)) in designs.items():
        oof[design] = evaluate(d, splits, fy, fw, fp, sp)
        scores[design] = {k: r2_score(y, p, sample_weight=w) for k, p in oof[design].items()}

    names = list(scores["random"])
    print("\n   R2 weighted by tests      " + "".join(f"{k:>18}" for k in scores))
    for k in names:
        print(f"   {k:<25}" + "".join(f"{scores[s][k]:>18.3f}" for s in scores))

    resid = oof["spatial blocks"]["HistGB"] - y
    print("\n## errors by place (spatial-block predictions of HistGB)")
    resid = oof["spatial blocks"]["HistGB"] - y
    print("   tests in the tile   tiles   weighted MAE   R2 within   shrunk previous-quarter R2")
    for lo, hi in TEST_BINS:
        m = (w >= lo) & (w <= hi)
        prev = oof["spatial blocks"]["previous quarter, shrunk"]
        print(f"   {lo:>5} to {min(hi, 9999):<6}  {m.sum():>7}   {np.average(np.abs(resid[m]), weights=w[m]):>12.3f}"
              f"   {r2_score(y[m], y[m] + resid[m], sample_weight=w[m]):>9.3f}"
              f"   {r2_score(y[m], prev[m], sample_weight=w[m]):>26.3f}")  # fmt: skip
    print("\n   ward     tiles   mean error (+ = too fast)   weighted MAE")
    rows = []
    for g in np.unique(d["ward"]):
        m = d["ward"] == g
        rows.append((np.average(resid[m], weights=w[m]), g, m.sum(),
                     np.average(np.abs(resid[m]), weights=w[m])))  # fmt: skip
    rows.sort()
    for bias, g, k, mae in rows[:4] + rows[-4:]:
        print(f"   {names_of.get(g, g):<7} {k:>6}   {bias:>+24.3f}   {mae:>12.3f}")
    spread = np.std([r[0] for r in rows])
    print(f"   spread of the ward mean errors: {spread:.3f} (log units; 0.1 is about 10% in speed)")

    print(
        "\n## errors by time: each quarter predicted from the one before (HistGB, and previous quarter)"
    )
    pairs = [("2025 Q4 -> 2026 Q1", d["y_q0"], d["w_q0"], d["y_q1"], d["w_q1"]),
             ("2026 Q1 -> 2026 Q2", d["y_q1"], d["w_q1"], y, w)]  # fmt: skip
    for label, ya, wa, yb, wb in pairs:
        p = np.full(n, np.nan)
        for train, test in block_splits:
            p[test] = fit(models()["HistGB"], X[train], ya[train], wa[train]).predict(X[test])
        print(f"   {label} (across spatial blocks): HistGB R2 {r2_score(yb, p, sample_weight=wb):.3f},"
              f" raw previous quarter R2 {r2_score(yb, ya, sample_weight=wb):.3f}")  # fmt: skip

    fig, ax = plt.subplots(figsize=(8, 7))
    lim = np.percentile(np.abs(resid), 95)
    sc = ax.scatter(d["lon"], d["lat"], c=resid, s=6, cmap="RdBu_r", vmin=-lim, vmax=lim)
    ax.set_aspect(1 / np.cos(np.radians(35.7)))
    ax.set_title("HistGB error by tile, spatial blocks (red = predicted too fast)")
    ax.set_axis_off()
    fig.colorbar(sc, ax=ax, shrink=0.6, label="log speed")
    fig.savefig(OUT / "errors-by-tile.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")


if __name__ == "__main__":
    main()
