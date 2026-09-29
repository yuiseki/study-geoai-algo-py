"""Step 5D: a Dirichlet process mixture instead of k-means. Does it choose k?

scikit-learn's BayesianGaussianMixture with a dirichlet_process weight prior is
a truncated, variational DPMM: n_components is an upper bound, and components
the data do not need should get weights near zero. The number of components in
use (weight over MIN_WEIGHT) is the "effective k".

1. Blobs with 4 known centres: does it find 4?
2. The 1 km grid of step 5C: effective k against the concentration prior
   (gamma), the upper bound, the covariance prior and reg_covar.
3. Small areas of step 5A: effective k against the number of rows.
4. One chosen fit on the grid: medians per component, agreement with k-means
   (k = 6) and a map.

    uv run python src/005-D-dpmm/run.py
"""

import json
import warnings
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import adjusted_rand_score
from sklearn.mixture import BayesianGaussianMixture
from sklearn.preprocessing import StandardScaler

from study_geoai import aoi, features, plot
from study_geoai.db import connect

OUT = Path(__file__).parent / "output"
COLS = ["log_density", "coverage", "log_place_density", "share_food", "share_retail",
        "share_lodging", "share_culture", "undergrounded_share", "mean_green",
        "log_cell_density"]  # fmt: skip
SEEDS = range(5)
MIN_WEIGHT = 0.01
GAMMAS = (1e-3, 1e-1, 1.0, 10.0, 1e3)
CHOSEN = {"n_components": 20, "covariance_prior": 10.0}


def dpmm(Z, seed, n_components=20, gamma=1.0, covariance_prior=None, reg_covar=1e-6):
    prior = None if covariance_prior is None else covariance_prior * np.eye(Z.shape[1])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        return BayesianGaussianMixture(
            n_components=n_components,
            weight_concentration_prior_type="dirichlet_process",
            weight_concentration_prior=gamma,
            covariance_prior=prior,
            reg_covar=reg_covar,
            max_iter=2000,
            random_state=seed,
        ).fit(Z)


def effective_k(Z, **kw):
    return [int((dpmm(Z, seed, **kw).weights_ > MIN_WEIGHT).sum()) for seed in SEEDS]


def show(label, ks):
    print(f"   {label:<34} {' '.join(f'{k:>2}' for k in ks)}   (median {int(np.median(ks))})")


def standardise(rows):
    X = np.array(rows, dtype=float)
    X = np.where(np.isnan(X), np.nanmedian(X, axis=0), X)
    return X, StandardScaler().fit_transform(X)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"effective k = components with weight over {MIN_WEIGHT}; one number per seed")

    print("\n## 1. blobs: 631 points, 10 dimensions, 4 centres")
    Zb = StandardScaler().fit_transform(make_blobs(631, n_features=10, centers=4,
                                                   random_state=0)[0])  # fmt: skip
    for g in GAMMAS:
        show(f"gamma {g:g}", effective_k(Zb, gamma=g))

    area = aoi.load("tokyo23", con)
    taito = aoi.load("taito", con)
    features.grid_profiles(con, area).create_view("g")
    rows = con.execute(
        """
        select ln(1 + density), coverage, ln(1 + place_density), share_food, share_retail,
               share_lodging, share_culture, undergrounded_share, mean_green,
               ln(1 + cell_density), st_asgeojson(geometry),
               st_intersects(geometry, st_geomfromtext(?))
        from g order by mesh
        """,
        [taito.wkt],
    ).fetchall()
    X, Z = standardise([r[:10] for r in rows])
    print(f"\n## 2. 1 km grid, 23 wards: {len(Z)} squares")
    for g in GAMMAS:
        show(f"gamma {g:g}", effective_k(Z, gamma=g))
    for n in (10, 20, 30, 40):
        show(f"upper bound {n}", effective_k(Z, n_components=n))
    for s in (1.0, 3.0, 10.0, 30.0):
        show(f"covariance_prior {s:g}", effective_k(Z, covariance_prior=s))
    for n in (10, 20, 40):
        show(f"covariance_prior 10, upper bound {n}",
             effective_k(Z, n_components=n, covariance_prior=10.0))  # fmt: skip
    for g in (1e-3, 1e3):
        show(f"covariance_prior 10, gamma {g:g}",
             effective_k(Z, gamma=g, covariance_prior=10.0))  # fmt: skip
    for rc in (1e-2, 0.1, 0.3, 1.0):
        show(f"reg_covar {rc:g}", effective_k(Z, reg_covar=rc))
    show("without share_lodging", effective_k(np.delete(Z, 5, axis=1)))
    show("without the four shares", effective_k(np.delete(Z, [3, 4, 5, 6], axis=1)))

    features.small_area_profiles(con, area).create_view("pr")
    _, Zs = standardise(
        con.sql("""
        select ln(1 + density), coverage, ln(1 + place_density), share_food, share_retail,
               share_lodging, share_culture, undergrounded_share, mean_green
        from pr where population > 0 or n_places > 0 order by key11
    """).fetchall()
    )
    print(f"\n## 3. small areas, 23 wards: {len(Zs):,}; random subsets of n rows")
    rng = np.random.default_rng(0)
    for n in (300, 1000, 2000, len(Zs)):
        sub = Zs[rng.choice(len(Zs), n, replace=False)]
        show(f"n {n:,}, default priors", effective_k(sub))
        show(f"n {n:,}, covariance_prior 10", effective_k(sub, covariance_prior=10.0))

    print("\n## 4. chosen fit on the grid: " + ", ".join(f"{k} {v}" for k, v in CHOSEN.items()))
    fits = [dpmm(Z, seed, **CHOSEN) for seed in SEEDS]
    labels_by_seed = [f.predict(Z) for f in fits]
    ari = [adjusted_rand_score(labels_by_seed[0], other) for other in labels_by_seed[1:]]
    print("   ARI of seed 0 against seeds 1 to 4: " + ", ".join(f"{a:.2f}" for a in ari))
    best = max(range(len(fits)), key=lambda i: fits[i].lower_bound_)
    labels = labels_by_seed[best]
    # renumber by size so the map legend is stable
    used = [c for c, _ in sorted(((c, (labels == c).sum()) for c in set(labels)),
                                 key=lambda t: -t[1])]  # fmt: skip
    labels = np.array([used.index(c) for c in labels])
    km = KMeans(6, n_init=20, random_state=0).fit_predict(Z)
    print(f"   best lower bound: seed {best}; {len(used)} components used; "
          f"ARI against k-means (k = 6) {adjusted_rand_score(labels, km):.2f}")  # fmt: skip
    print("   comp   size  " + "  ".join(f"{c[:12]:>12}" for c in COLS))
    for c in range(len(used)):
        m = labels == c
        med = np.median(X[m], axis=0)
        print(f"   {c:>4}  {m.sum():>5}  " + "  ".join(f"{v:>12.3f}" for v in med))
    in_taito = np.array([r[11] for r in rows])
    counts = {c: int(((labels == c) & in_taito).sum()) for c in range(len(used))}
    print(f"   Taito City: {int(in_taito.sum())} squares; by component {counts}")
    crosstab = np.zeros((len(used), 6), dtype=int)
    for a, b in zip(labels, km, strict=True):
        crosstab[a, b] += 1
    print("   components (rows) against k-means clusters 0 to 5 (columns)")
    for c, row in enumerate(crosstab):
        print(f"   {c:>4}  " + " ".join(f"{v:>4}" for v in row))
    outline = json.dumps(json.loads(con.execute(
        "select st_asgeojson(st_geomfromtext(?))", [area.wkt]).fetchone()[0]))  # fmt: skip
    path = plot.choropleth(list(zip([r[10] for r in rows], labels.tolist(), strict=True)),
                           OUT / "dpmm-tokyo23-1km.png",
                           f"23 wards, 1 km grid: DPMM ({len(used)} components used)",
                           "component", categorical=True, outline=outline)  # fmt: skip
    print(f"   map: {path}")


if __name__ == "__main__":
    main()
