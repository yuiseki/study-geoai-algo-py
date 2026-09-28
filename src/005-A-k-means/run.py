"""Step 5A: k-means types of place, from small-area profiles.

Each census small area is described by density, building coverage, POI density,
the shares of food, retail, lodging and culture places, the share of streets
with wires underground, and street greenery (study_geoai.features
.small_area_profiles). Standardised, then k-means for k = 2 to 10; the chosen
k is mapped and each cluster described by its medians. For contrast, k-means
on the raw lon/lat of POIs, which only cuts space into pieces.

    uv run python src/005-A-k-means/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402
from sklearn.metrics import silhouette_score  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from study_geoai import aoi, features, overture, plot  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
COLS = ["log_density", "coverage", "log_place_density", "share_food", "share_retail",
        "share_lodging", "share_culture", "undergrounded_share", "mean_green"]  # fmt: skip


def load(con, area):
    features.small_area_profiles(con, area).create_view("pr")
    rows = con.sql("""
        select name, ln(1 + density), coverage, ln(1 + place_density), share_food, share_retail,
               share_lodging, share_culture, undergrounded_share, mean_green,
               st_asgeojson(geometry)
        from pr where population > 0 or n_places > 0 order by key11
    """).fetchall()
    names = [r[0] for r in rows]
    X = np.array([r[1:10] for r in rows], dtype=float)
    missing = np.isnan(X).sum(axis=0)
    X = np.where(np.isnan(X), np.nanmedian(X, axis=0), X)
    return names, X, [r[10] for r in rows], missing


def choose_k(Z, name):
    ks, inertia, sil = range(2, 11), [], []
    for k in ks:
        km = KMeans(k, n_init=20, random_state=0).fit(Z)
        inertia.append(km.inertia_)
        sil.append(silhouette_score(Z, km.labels_))
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.5))
    a.plot(ks, inertia, marker="o")
    a.set_title(f"{name}: within-cluster sum of squares")
    b.plot(ks, sil, marker="o")
    b.set_title(f"{name}: silhouette")
    for ax in (a, b):
        ax.set_xlabel("k")
    fig.tight_layout()
    fig.savefig(OUT / f"k-{name}.png", dpi=120)
    plt.close(fig)
    return dict(zip(ks, sil, strict=True))


def raw_lonlat(con, area):
    rows = (
        overture.read(con, area, "places", "place", ["id"])
        .query("p", "select st_x(geometry), st_y(geometry) from p")
        .fetchall()
    )
    xy = np.array(rows, dtype=float)
    labels = KMeans(8, n_init=10, random_state=0).fit_predict(xy)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(xy[:, 0], xy[:, 1], c=labels, cmap="tab10", s=2)
    ax.set_aspect(1 / 0.81)
    ax.set_title(f"{area.name}: k-means (k = 8) on POI lon/lat only")
    ax.set_axis_off()
    fig.savefig(OUT / f"lonlat-{area.name}.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, k in (("taito", 4), ("tokyo23", 6)):
        area = aoi.load(name, con)
        names, X, geojson, missing = load(con, area)
        print(f"\n## {name}: {len(names):,} small areas; filled with the median: "
              + ", ".join(f"{c} {m}" for c, m in zip(COLS, missing, strict=True) if m))  # fmt: skip
        Z = StandardScaler().fit_transform(X)
        sil = choose_k(Z, name)
        print("   silhouette by k: " + ", ".join(f"{kk} {v:.3f}" for kk, v in sil.items()))
        labels = KMeans(k, n_init=20, random_state=0).fit_predict(Z)
        print(f"   k = {k}: medians per cluster")
        print("   cluster  size  " + "  ".join(f"{c[:12]:>12}" for c in COLS))
        for c in range(k):
            m = labels == c
            med = np.median(X[m], axis=0)
            print(f"   {c:>7}  {m.sum():>4}  " + "  ".join(f"{v:>12.3f}" for v in med))
            examples = [n for n, keep in zip(names, m, strict=True) if keep][:6]
            print(f"            e.g. {', '.join(examples)}")
        plot.choropleth(list(zip(geojson, labels.tolist(), strict=True)),
                        OUT / f"clusters-{name}.png", f"{name}: k-means types of place (k = {k})",
                        "cluster", categorical=True)  # fmt: skip
        if name == "taito":
            raw_lonlat(con, area)
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
