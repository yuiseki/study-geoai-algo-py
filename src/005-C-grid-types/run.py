"""Step 5C: k-means types of place on a 1 km grid instead of small areas.

Small areas (step 5A) differ a lot in size and shape; the Japanese standard
3rd mesh (about 1.05 km2 here) gives equal units. Same kind of features as 5A,
per mesh (study_geoai.features.grid_profiles), plus cell tower density.
23 wards; Taito City's squares are listed from the same clustering.

    uv run python src/005-C-grid-types/run.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402
from sklearn.metrics import silhouette_score  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from study_geoai import aoi, features, plot  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
COLS = ["log_density", "coverage", "log_place_density", "share_food", "share_retail",
        "share_lodging", "share_culture", "undergrounded_share", "mean_green",
        "log_cell_density"]  # fmt: skip
K = 6


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    area = aoi.load("tokyo23", con)
    taito = aoi.load("taito", con)
    features.grid_profiles(con, area).create_view("g")
    rows = con.execute(
        """
        select mesh, ln(1 + density), coverage, ln(1 + place_density), share_food, share_retail,
               share_lodging, share_culture, undergrounded_share, mean_green,
               ln(1 + cell_density), st_asgeojson(geometry),
               st_intersects(geometry, st_geomfromtext(?))
        from g order by mesh
        """,
        [taito.wkt],
    ).fetchall()
    meshes = [r[0] for r in rows]
    X = np.array([r[1:11] for r in rows], dtype=float)
    missing = np.isnan(X).sum(axis=0)
    X = np.where(np.isnan(X), np.nanmedian(X, axis=0), X)
    in_taito = np.array([r[12] for r in rows])
    print(f"23 wards: {len(meshes)} squares; filled with the median: "
          + ", ".join(f"{c} {m}" for c, m in zip(COLS, missing, strict=True) if m))  # fmt: skip
    Z = StandardScaler().fit_transform(X)
    sil = {k: silhouette_score(Z, KMeans(k, n_init=20, random_state=0).fit_predict(Z))
           for k in range(2, 11)}  # fmt: skip
    print("silhouette by k: " + ", ".join(f"{k} {v:.3f}" for k, v in sil.items()))
    labels = KMeans(K, n_init=20, random_state=0).fit_predict(Z)
    print(f"\nk = {K}: medians per cluster")
    print("cluster  size  " + "  ".join(f"{c[:12]:>12}" for c in COLS))
    for c in range(K):
        m = labels == c
        med = np.median(X[m], axis=0)
        print(f"{c:>7}  {m.sum():>4}  " + "  ".join(f"{v:>12.3f}" for v in med))
    counts = {c: int(((labels == c) & in_taito).sum()) for c in range(K)}
    print(f"\nTaito City: {int(in_taito.sum())} squares touch the ward; by cluster {counts}")
    outline = json.dumps(json.loads(con.execute(
        "select st_asgeojson(st_geomfromtext(?))", [area.wkt]).fetchone()[0]))  # fmt: skip
    path = plot.choropleth(list(zip([r[11] for r in rows], labels.tolist(), strict=True)),
                           OUT / "clusters-tokyo23-1km.png",
                           f"23 wards: k-means types of place on the 1 km grid (k = {K})",
                           "cluster", categorical=True, outline=outline)  # fmt: skip
    print(f"map: {path}")
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.plot(list(sil), list(sil.values()), marker="o")
    ax.set_xlabel("k")
    ax.set_title("silhouette, 1 km grid")
    fig.tight_layout()
    fig.savefig(OUT / "k-tokyo23-1km.png", dpi=120)


if __name__ == "__main__":
    main()
