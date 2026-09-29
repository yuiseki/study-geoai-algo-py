"""Step 6A: PCA of street measures on Taito City's 250 m cells.

michiyomi street scenes are averaged per 250 m cell (study_geoai.features
.street_cells): roadway and sidewalk width, poles, lights, greenery,
colourfulness and the shares of undergrounded wires, dense wires, block paving
and poor sight lines. PCA squeezes the 12 measures; the maps of the component
scores show what the first components stand for.

1. Standardised PCA: explained variance, loadings.
2. Without standardising: the measure with the largest units takes over.
3. How many components: parallel analysis (eigenvalues of column-shuffled data).
4. Are the loadings stable: bootstrap over cells.
5. Maps of PC1 and PC2 scores, and a biplot.

    uv run python src/006-A-pca/run.py
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
        "poor_sight_share", "n_scenes"]  # fmt: skip
SHOWN = 4  # components printed
BOOTSTRAPS = 500


def loadings_table(pca, title):
    print(f"\n   {title}: loadings (weight of each measure in each component)")
    print("   " + " " * 20 + "".join(f"{f'PC{i + 1}':>8}" for i in range(SHOWN)))
    for j, c in enumerate(COLS):
        print(f"   {c:<20}" + "".join(f"{pca.components_[i, j]:>8.2f}" for i in range(SHOWN)))
    print(
        "   explained      " + "".join(f"{v:>8.3f}" for v in pca.explained_variance_ratio_[:SHOWN])
    )


def parallel_analysis(Z, rounds=200):
    """Eigenvalues of the data against the 95th percentile of eigenvalues of data whose
    columns were shuffled independently (same marginals, no correlation)."""
    rng = np.random.default_rng(0)
    real = PCA().fit(Z).explained_variance_
    null = np.array([
        PCA().fit(np.column_stack([rng.permutation(col) for col in Z.T])).explained_variance_
        for _ in range(rounds)
    ])  # fmt: skip
    limit = np.percentile(null, 95, axis=0)
    keep = int(np.argmax(real < limit)) if (real < limit).any() else len(real)
    print("\n   parallel analysis: eigenvalue of the data against shuffled data (95th percentile)")
    for i in range(6):
        print(f"   PC{i + 1}: {real[i]:.2f} against {limit[i]:.2f}"
              + ("   <- above" if real[i] > limit[i] else ""))  # fmt: skip
    print(f"   components worth keeping: {keep}")
    return real, limit


def bootstrap(Z, reference):
    """Absolute cosine between each bootstrap component and the full-data one."""
    rng = np.random.default_rng(0)
    cos = np.zeros((BOOTSTRAPS, SHOWN))
    for b in range(BOOTSTRAPS):
        sample = Z[rng.integers(0, len(Z), len(Z))]
        comp = PCA(SHOWN).fit(sample).components_
        cos[b] = np.abs(np.sum(comp * reference.components_[:SHOWN], axis=1))
    print(f"\n   bootstrap ({BOOTSTRAPS} resamples of cells): |cos| with the full-data component")
    for i in range(SHOWN):
        print(f"   PC{i + 1}: median {np.median(cos[:, i]):.2f}, "
              f"5th percentile {np.percentile(cos[:, i], 5):.2f}")  # fmt: skip


def biplot(scores, pca, path):
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(scores[:, 0], scores[:, 1], s=8, c="#999999")
    scale = np.abs(scores[:, :2]).max() * 0.9
    for j, c in enumerate(COLS):
        x, y = pca.components_[0, j] * scale, pca.components_[1, j] * scale
        ax.arrow(0, 0, x, y, color="tab:red", width=0.01, head_width=0.08)
        ax.annotate(c, (x, y), fontsize=8, color="tab:red")
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.0%})")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.0%})")
    ax.set_title("taito, 250 m cells: biplot")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    area = aoi.load("taito", con)
    features.street_cells(con, area).create_view("sc")
    rows = con.sql(f"""
        select cell_250m, {", ".join(COLS)}, st_asgeojson(geometry) from sc order by cell_250m
    """).fetchall()
    cells = [r[0] for r in rows]
    X = np.array([r[1:-1] for r in rows], dtype=float)
    geojson = [r[-1] for r in rows]
    missing = np.isnan(X).sum(axis=0)
    X = np.where(np.isnan(X), np.nanmedian(X, axis=0), X)
    print(f"## taito: {len(cells)} cells with at least {features.MIN_SCENES} scenes; "
          f"filled with the median: "
          + (", ".join(f"{c} {m}" for c, m in zip(COLS, missing, strict=True) if m) or "none"))  # fmt: skip
    print("   " + ", ".join(f"{c} sd {s:.3g}" for c, s in zip(COLS, X.std(axis=0), strict=True)))

    Z = StandardScaler().fit_transform(X)
    pca = PCA().fit(Z)
    loadings_table(pca, "standardised")
    cum = np.cumsum(pca.explained_variance_ratio_)
    print("   cumulative: " + ", ".join(f"PC{i + 1} {v:.2f}" for i, v in enumerate(cum[:6])))

    raw = PCA().fit(X - X.mean(axis=0))
    loadings_table(raw, "not standardised")

    real, limit = parallel_analysis(Z)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    ax.plot(range(1, len(real) + 1), real, marker="o", label="data")
    ax.plot(range(1, len(limit) + 1), limit, marker="x", label="shuffled, 95th percentile")
    ax.set_xlabel("component")
    ax.set_ylabel("eigenvalue")
    ax.legend()
    fig.savefig(OUT / "scree-taito.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    bootstrap(Z, pca)

    scores = pca.transform(Z)
    for i in range(2):
        order = np.argsort(scores[:, i])
        print(f"\n   PC{i + 1} lowest cells: " + ", ".join(str(cells[k]) for k in order[:3])
              + "; highest: " + ", ".join(str(cells[k]) for k in order[-3:]))  # fmt: skip
        for k in (*order[:2], *order[-2:]):
            lon, lat = json.loads(geojson[k])["coordinates"][0][0]
            print(f"      {cells[k]} (south-west {lat:.5f}, {lon:.5f}): score {scores[k, i]:+.2f}, "
                  + ", ".join(f"{c} {X[k, j]:.2f}" for j, c in enumerate(COLS)))  # fmt: skip
    outline = json.dumps(json.loads(con.execute(
        "select st_asgeojson(st_geomfromtext(?))", [area.wkt]).fetchone()[0]))  # fmt: skip
    for i in range(2):
        plot.choropleth(list(zip(geojson, scores[:, i].tolist(), strict=True)),
                        OUT / f"pc{i + 1}-taito.png",
                        f"taito, 250 m cells: PC{i + 1} score "
                        f"({pca.explained_variance_ratio_[i]:.0%} of variance)",
                        f"PC{i + 1}", diverging=True, outline=outline)  # fmt: skip
    biplot(scores, pca, OUT / "biplot-taito.png")
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
