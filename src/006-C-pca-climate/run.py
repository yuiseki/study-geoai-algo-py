"""Step 6C: PCA of Japan's climate, and whether its axes survive a change of sample.

Each land cell of AgERA5 over Japan (0.1 degree, study_geoai.ferspas) is
described by its monthly normals: 12 months of four variables (rain, reference
evapotranspiration, daily maximum and minimum temperature), 48 numbers. Rain is
taken as log(1 + mm) because it is skewed; everything is standardised.

1. PCA over 1991-2020: explained variance, parallel analysis, what each
   component loads on (as a variable x month table).
2. Do the axes hold? Fitted on 1981-2000 and on 2006-2025, and on the east and
   the west of Japan separately: |cos| between matching components, and how
   much of each component lies in the other fit's PC1-PC2 plane (the check of
   step 6B).
3. Moving the later period onto the earlier axes: which component carries
   the warming.
4. Maps of PC1 to PC3.

    uv run python -u src/006-C-pca-climate/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from study_geoai import ferspas  # noqa: E402

OUT = Path(__file__).parent / "output"
START, END = "1979-01-01", "2025-12-01"
VARS = ("rain", "et0", "tmax", "tmin")
MONTHS = "JFMAMJJASOND"
SHOWN = 3


def features(cells, period):
    """cells x 48: the normals of `period` (start year, end year), rain on a log scale."""
    cols, names = [], []
    for v in VARS:
        months, values = ferspas.on_cells(v, cells, START, END)
        years = months.astype("datetime64[Y]").astype(int) + 1970
        keep = (years >= period[0]) & (years <= period[1])
        norm = ferspas.normals(values[keep], months[keep])  # 12 x cells
        if v == "rain":
            norm = np.log1p(norm)
        cols.append(norm.T)
        names += [f"{v}-{m}" for m in range(1, 13)]
    return np.hstack(cols), names


def parallel_analysis(Z, rounds=50):
    """Eigenvalues a component must beat: the 95th percentile of shuffled columns."""
    rng = np.random.default_rng(0)
    top = []
    for _ in range(rounds):
        shuffled = np.column_stack([rng.permutation(c) for c in Z.T])
        top.append(PCA().fit(shuffled).explained_variance_)
    return np.percentile(top, 95, axis=0)


def fit(X):
    scaler = StandardScaler().fit(X)
    return scaler, PCA().fit(scaler.transform(X))


def loading_table(pca, k):
    print(f"\n   component {k + 1} ({pca.explained_variance_ratio_[k]:.1%}): loading by month")
    print("            " + "  ".join(f"{m:>4}" for m in MONTHS))
    comp = pca.components_[k].reshape(len(VARS), 12)
    for v, row in zip(VARS, comp, strict=True):
        print(f"   {v:>6}   " + "  ".join(f"{x:+.2f}" for x in row))


def compare(a, b, label):
    """|cos| of matching components and the share of a's first three in b's PC1-PC2 plane."""
    cos = [abs(float(a.components_[k] @ b.components_[k])) for k in range(SHOWN)]
    plane = b.components_[:2]
    inside = [float(np.linalg.norm(plane @ a.components_[k])) for k in range(SHOWN)]
    print(f"   {label:<34} |cos| PC1-3: {', '.join(f'{c:.3f}' for c in cos)};"
          f" in the other PC1-PC2 plane: {', '.join(f'{x:.3f}' for x in inside)}")  # fmt: skip


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = ferspas.japan_cells()
    X, names = features(cells, (1991, 2020))
    print(f"## Japan: {len(cells):,} land cells of 0.1 degree, {X.shape[1]} features "
          f"(4 variables x 12 monthly normals, 1991-2020)")  # fmt: skip
    scaler, pca = fit(X)
    Z = scaler.transform(X)
    ev = pca.explained_variance_
    bar = parallel_analysis(Z)
    print("\n   component   variance   cumulative   eigenvalue   parallel-analysis bar")
    for k in range(6):
        print(f"   {k + 1:>9}   {pca.explained_variance_ratio_[k]:>8.1%}"
              f"   {pca.explained_variance_ratio_[:k + 1].sum():>10.1%}   {ev[k]:>10.2f}   {bar[k]:>10.2f}")  # fmt: skip
    print(f"   components above the bar: {int((ev > bar).sum())}")
    for k in range(SHOWN):
        loading_table(pca, k)

    print("\n## do the axes hold?")
    early, late = features(cells, (1981, 2000))[0], features(cells, (2006, 2025))[0]
    _, p_early = fit(early)
    _, p_late = fit(late)
    compare(p_early, p_late, "1981-2000 against 2006-2025")
    east = cells["lon"].to_numpy() >= 137.5
    _, p_east = fit(X[east])
    _, p_west = fit(X[~east])
    compare(p_east, p_west, f"east ({east.sum()}) against west ({(~east).sum()})")
    compare(p_east, pca, "east against all of Japan")

    print("\n## the later period on the earlier axes (mean score shift, in standard deviations)")
    s_early, _ = fit(early)
    a = p_early.transform(s_early.transform(early))
    b = p_early.transform(s_early.transform(late))
    for k in range(SHOWN):
        shift = (b[:, k].mean() - a[:, k].mean()) / a[:, k].std()
        print(f"   PC{k + 1}: {shift:+.2f}  (cells moving up: {(b[:, k] > a[:, k]).mean():.0%})")
    t_early = np.mean([early[:, names.index(f"tmax-{m}")] for m in range(1, 13)])
    t_late = np.mean([late[:, names.index(f"tmax-{m}")] for m in range(1, 13)])
    print(f"   for scale: the mean daily maximum over Japan went from {t_early:.2f} to "
          f"{t_late:.2f} C ({t_late - t_early:+.2f})")  # fmt: skip

    scores = pca.transform(Z)
    fig, axes = plt.subplots(1, SHOWN, figsize=(5 * SHOWN, 6))
    for k, ax in enumerate(axes):
        lim = np.percentile(np.abs(scores[:, k]), 98)
        sc = ax.scatter(cells["lon"], cells["lat"], c=scores[:, k], s=3, cmap="RdBu_r",
                        vmin=-lim, vmax=lim)  # fmt: skip
        ax.set_aspect(1 / np.cos(np.radians(36)))
        ax.set_title(f"PC{k + 1} ({pca.explained_variance_ratio_[k]:.0%})")
        ax.set_axis_off()
        fig.colorbar(sc, ax=ax, shrink=0.5)
    fig.savefig(OUT / "pc-maps.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")
    print(f"credit: {ferspas.CREDIT}")


if __name__ == "__main__":
    main()
