"""Step 6B: the street PCA of step 6A across the 23 wards.

Same street measures per 250 m cell (study_geoai.features.street_cells), without
the scene count, which 6A showed is not a property of the street.

1. PCA of the 23 wards: loadings, parallel analysis, bootstrap.
2. Do Taito's axes hold? Cosine between Taito's and the 23 wards' components,
   and each ward's own PC1 and PC2 against the 23 wards' plane.
3. How the wards differ: the 23-ward scores per ward, and the share of the score
   variance that lies between wards (eta squared).
4. Maps of PC1 and PC2 over the 23 wards.

    uv run python src/006-B-pca-wards/run.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from study_geoai import aoi, features, plot  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
COLS = ["roadway_width_m", "sidewalk_width_m", "sidewalk_share", "poles", "lights", "green",
        "colorfulness", "undergrounded_share", "wires_high_share", "block_paving_share",
        "poor_sight_share"]  # fmt: skip
SHOWN = 4
BOOTSTRAPS = 200


def load(con, area):
    features.street_cells(con, area).create_view("sc")
    rows = con.sql(f"""
        select ward, {", ".join(COLS)}, st_asgeojson(geometry) from sc order by cell_250m
    """).fetchall()
    X = np.array([r[1:-1] for r in rows], dtype=float)
    missing = np.isnan(X).sum(axis=0)
    X = np.where(np.isnan(X), np.nanmedian(X, axis=0), X)
    return np.array([r[0] for r in rows]), X, [r[-1] for r in rows], missing


def aligned(a, b):
    """|cos| between two unit vectors; a component's sign is arbitrary."""
    return abs(float(a @ b))


def in_plane(v, plane):
    """Length of v's projection onto the plane spanned by the rows of plane (1 = inside)."""
    return float(np.linalg.norm(plane @ v))


def parallel_analysis(Z, rounds=50):
    rng = np.random.default_rng(0)
    real = PCA().fit(Z).explained_variance_
    null = np.array([
        PCA().fit(np.column_stack([rng.permutation(col) for col in Z.T])).explained_variance_
        for _ in range(rounds)
    ])  # fmt: skip
    limit = np.percentile(null, 95, axis=0)
    above = real > limit
    keep = int(np.argmin(above)) if not above.all() else len(real)
    print("   parallel analysis: " + ", ".join(
        f"PC{i + 1} {real[i]:.2f}/{limit[i]:.2f}" for i in range(6)) + f"; keep {keep}")  # fmt: skip


def bootstrap(Z, reference):
    rng = np.random.default_rng(0)
    cos = np.array([
        np.abs(np.sum(PCA(SHOWN).fit(Z[rng.integers(0, len(Z), len(Z))]).components_
                      * reference.components_[:SHOWN], axis=1))
        for _ in range(BOOTSTRAPS)
    ])  # fmt: skip
    print(f"   bootstrap ({BOOTSTRAPS}): 5th percentile of |cos| "
          + ", ".join(f"PC{i + 1} {np.percentile(cos[:, i], 5):.2f}" for i in range(SHOWN)))  # fmt: skip


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    tokyo23 = aoi.load("tokyo23", con)
    wards, X, geojson, missing = load(con, tokyo23)
    print(f"## tokyo23: {len(X):,} cells with at least {features.MIN_SCENES} scenes; "
          "filled with the median: "
          + (", ".join(f"{c} {m}" for c, m in zip(COLS, missing, strict=True) if m) or "none"))  # fmt: skip
    scaler = StandardScaler().fit(X)
    Z = scaler.transform(X)
    pca = PCA().fit(Z)
    print("   " + " " * 20 + "".join(f"{f'PC{i + 1}':>8}" for i in range(SHOWN)))
    for j, c in enumerate(COLS):
        print(f"   {c:<20}" + "".join(f"{pca.components_[i, j]:>8.2f}" for i in range(SHOWN)))
    print(
        "   explained      " + "".join(f"{v:>8.3f}" for v in pca.explained_variance_ratio_[:SHOWN])
    )
    parallel_analysis(Z)
    bootstrap(Z, pca)

    _, Xt, _, _ = load(con, aoi.load("taito", con))
    taito = PCA().fit(StandardScaler().fit_transform(Xt))
    print(f"\n## taito on its own ({len(Xt)} cells) against the 23 wards")
    for i in range(3):
        cos = [aligned(taito.components_[i], pca.components_[k]) for k in range(3)]
        print(f"   taito PC{i + 1}: |cos| with 23-ward PC1 {cos[0]:.2f}, PC2 {cos[1]:.2f}, "
              f"PC3 {cos[2]:.2f}; in the 23-ward PC1-PC2 plane "
              f"{in_plane(taito.components_[i], pca.components_[:2]):.2f}")  # fmt: skip

    print("\n## each ward on its own: PCA of its cells (standardised within the ward)")
    print(
        "   ward        cells  PC1 |cos| with 23-ward PC1  PC2  PC1 in plane  PC2 in plane"
        "  explained PC1 PC2"
    )
    names = sorted(set(wards))
    for w in names:
        m = wards == w
        own = PCA(2).fit(StandardScaler().fit_transform(X[m]))
        c1, c2 = own.components_
        print(f"   {w:<8}  {m.sum():>5}  {aligned(c1, pca.components_[0]):>26.2f}"
              f"  {aligned(c2, pca.components_[1]):>3.2f}"
              f"  {in_plane(c1, pca.components_[:2]):>12.2f}  {in_plane(c2, pca.components_[:2]):>12.2f}"
              f"  {own.explained_variance_ratio_[0]:>13.2f} {own.explained_variance_ratio_[1]:.2f}")  # fmt: skip

    scores = pca.transform(Z)[:, :2]
    print("\n## 23-ward scores per ward (median, and 10th to 90th percentile)")
    print("   ward        cells   PC1 median  (10th, 90th)   PC2 median  (10th, 90th)")
    medians = {}
    for w in names:
        s = scores[wards == w]
        medians[w] = np.median(s, axis=0)
        p1, p2 = np.percentile(s[:, 0], [10, 90]), np.percentile(s[:, 1], [10, 90])
        print(f"   {w:<8}  {len(s):>5}  {medians[w][0]:>+10.2f}  ({p1[0]:+.2f}, {p1[1]:+.2f})"
              f"  {medians[w][1]:>+10.2f}  ({p2[0]:+.2f}, {p2[1]:+.2f})")  # fmt: skip
    for i in range(2):
        s = scores[:, i]
        between = sum((wards == w).sum() * (s[wards == w].mean() - s.mean()) ** 2 for w in names)
        print(f"   PC{i + 1}: share of variance between wards (eta squared) "
              f"{between / ((s - s.mean()) ** 2).sum():.2f}")  # fmt: skip

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(scores[:, 0], scores[:, 1], s=1, c="#cccccc")
    for w, (x, y) in medians.items():
        ax.scatter(x, y, c="tab:red", s=12)
        ax.annotate(w, (x, y), fontsize=8, fontfamily="Noto Sans CJK JP")
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.0%})")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.0%})")
    ax.set_title("23 wards: cells (grey) and ward medians (red)")
    fig.savefig(OUT / "ward-medians.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    outline = json.dumps(json.loads(con.execute(
        "select st_asgeojson(st_geomfromtext(?))", [tokyo23.wkt]).fetchone()[0]))  # fmt: skip
    for i in range(2):
        clipped = np.clip(scores[:, i], -5, 5)  # a few extreme cells would wash out the colours
        plot.choropleth(list(zip(geojson, clipped.tolist(), strict=True)),
                        OUT / f"pc{i + 1}-tokyo23.png",
                        f"23 wards, 250 m cells: PC{i + 1} score "
                        f"({pca.explained_variance_ratio_[i]:.0%}), clipped to +-5",
                        f"PC{i + 1}", diverging=True, outline=outline)  # fmt: skip
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
