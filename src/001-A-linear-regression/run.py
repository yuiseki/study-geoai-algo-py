"""Step 1A: linear regression of population density on buildings and POIs.

One row per 2020 census small area (町丁目). Taito City first, then the 23 wards
with the same code, to see how far the coefficients move.

    uv run python src/001-A-linear-regression/run.py            # both areas
    uv run python src/001-A-linear-regression/run.py --area taito

Writes a residual map per area to output/ next to this file.
"""

import argparse
from pathlib import Path

import numpy as np
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from study_geoai import aoi, features, plot
from study_geoai.db import connect

OUT = Path(__file__).parent / "output"
# Floors are known for only about 15 to 20 % of buildings, so they are left out.
FEATURES = ["coverage", "log_place_density"]


def load(con, name):
    area = aoi.load(name, con)
    features.small_areas(con, area).create_view("t")
    rows = con.sql("""
        select key11, name, population, density, coverage,
               ln(1 + place_density) as log_place_density,
               st_asgeojson(geometry) as geojson
        from t where area_km2 > 0.001
        order by key11
    """).fetchall()
    cols = ["key11", "name", "population", "density", *FEATURES, "geojson"]
    data = {c: [r[i] for r in rows] for i, c in enumerate(cols)}
    X = np.array([data[f] for f in FEATURES], dtype=float).T
    return area, data, X


def fit(name, con, residents_only=False):
    area, data, X = load(con, name)
    if residents_only:
        # Offices, parks and reclaimed land have no residents; log(1 + 0) = 0 then gives
        # residuals of -10 and more that swamp the fit. Keep areas with residents.
        keep = np.array(data["population"]) > 0
        if keep.all():
            return None
        print(f"\n(dropping {int((~keep).sum())} small areas with no residents)")
        data = {k: [v for v, m in zip(vs, keep, strict=True) if m] for k, vs in data.items()}
        X = X[keep]
        name = f"{name}-residents"
    y = np.array(data["density"], dtype=float)
    ylog = np.log1p(y)
    cv = KFold(5, shuffle=True, random_state=0)
    print(f"\n## {name}: {len(y)} small areas, density median {np.median(y):,.0f} /km2")

    results = {}
    for label, target in (("density", y), ("log density", ylog)):
        model = make_pipeline(StandardScaler(), LinearRegression()).fit(X, target)
        r2_train = model.score(X, target)
        r2_cv = cross_val_score(model, X, target, cv=cv, scoring="r2").mean()
        coef = model[-1].coef_
        results[label] = (model, coef)
        print(
            f"OLS on {label:11}: R2 train {r2_train:.3f}, 5-fold {r2_cv:.3f}; standardised coefficients "
            + ", ".join(f"{f} {c:+.3f}" for f, c in zip(FEATURES, coef, strict=True))
        )

    for label, reg in (
        ("Ridge", RidgeCV(alphas=np.logspace(-3, 3, 50))),
        ("Lasso", LassoCV(alphas=np.logspace(-4, 0, 50), cv=cv, max_iter=100_000)),
    ):
        model = make_pipeline(StandardScaler(), reg).fit(X, ylog)
        print(
            f"{label} on log density: alpha {model[-1].alpha_:.4g}; coefficients "
            + ", ".join(f"{f} {c:+.3f}" for f, c in zip(FEATURES, model[-1].coef_, strict=True))
        )

    model, _ = results["log density"]
    residual = ylog - model.predict(X)
    order = np.argsort(residual)
    print("most over-predicted (fewer residents than buildings and POIs suggest):")
    for i in order[:5]:
        print(f"   {data['name'][i]}: density {y[i]:,.0f}, residual {residual[i]:+.2f}")
    print("most under-predicted:")
    for i in order[-3:][::-1]:
        print(f"   {data['name'][i]}: density {y[i]:,.0f}, residual {residual[i]:+.2f}")

    path = plot.choropleth(
        list(zip(data["geojson"], residual.tolist(), strict=True)),
        OUT / f"residual-{name}.png",
        f"{name}: residual of log density (OLS on {', '.join(FEATURES)})",
        "log(1 + density) observed - predicted",
        diverging=True,
    )
    print(f"map: {path}")
    return dict(zip(FEATURES, results["log density"][1], strict=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--area", choices=["taito", "tokyo23", "both"], default="both")
    args = ap.parse_args()
    con = connect()
    names = ["taito", "tokyo23"] if args.area == "both" else [args.area]
    coefs = {}
    for name in names:
        coefs[name] = fit(name, con)
        if (c := fit(name, con, residents_only=True)) is not None:
            coefs[f"{name}-residents"] = c
    print("\n## standardised OLS coefficients on log density")
    for key, c in coefs.items():
        print(f"   {key:18}: " + ", ".join(f"{f} {c[f]:+.3f}" for f in FEATURES))


if __name__ == "__main__":
    main()
