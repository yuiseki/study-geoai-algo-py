"""Step 5E: Japan's climate types by k-means, from AgERA5 monthly normals.

The same 48 features as step 6C (12 monthly normals of rain, evapotranspiration,
daily maximum and minimum temperature, 1991-2020; rain as log(1 + mm);
standardised) for every land cell of 0.1 degree.

1. k from 2 to 10: inertia and silhouette, over five seeds.
2. The chosen k: what each type is (its annual cycle), how many cells, where.
3. Types against the eight usual regions of Japan (adjusted Rand index): does a
   clustering of weather rediscover the regions, or cut across them?
4. Stability: the same k fitted on 1981-2000 and on 2006-2025, and how many
   cells change type between them.
5. Weighting: 36 of the 48 features are temperatures or evaporation, which move
   together, so on the standardised features warmth dominates the distance.
   The same k-means on the four principal components that pass step 6C's
   parallel analysis, each scaled to unit variance, gives every axis one vote.

    uv run python -u src/005-E-climate-types/run.py
"""

import importlib.util
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.optimize import linear_sum_assignment  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.metrics import adjusted_rand_score, silhouette_score  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from study_geoai import ferspas  # noqa: E402

OUT = Path(__file__).parent / "output"
KS = range(2, 11)
SEEDS = range(5)
_spec = importlib.util.spec_from_file_location(
    "step6c", Path(__file__).parents[1] / "006-C-pca-climate" / "run.py"
)
step6c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step6c)

REGIONS = [("Hokkaido", 1, 1), ("Tohoku", 2, 7), ("Kanto", 8, 14), ("Chubu", 15, 23),
           ("Kinki", 24, 30), ("Chugoku", 31, 35), ("Shikoku", 36, 39),
           ("Kyushu-Okinawa", 40, 47)]  # fmt: skip


def region_of(pref_code):
    code = int(pref_code)
    return next(name for name, lo, hi in REGIONS if lo <= code <= hi)


def kmeans(Z, k, seed=0):
    return KMeans(k, n_init=10, random_state=seed).fit(Z)


def match(a, b, k):
    """Relabel b to agree with a as far as possible (Hungarian on the contingency table)."""
    table = np.zeros((k, k))
    np.add.at(table, (a, b), 1)
    rows, cols = linear_sum_assignment(-table)
    mapping = dict(zip(cols, rows, strict=True))
    return np.array([mapping[x] for x in b])


def describe(X, names, labels, k, cells):
    col = {n: i for i, n in enumerate(names)}
    print("\n   type  cells   Jan tmax  Aug tmax  Jan rain  Jul rain  year rain  "
          "main regions")  # fmt: skip
    for t in range(k):
        m = labels == t
        jan_t, aug_t = X[m, col["tmax-1"]].mean(), X[m, col["tmax-8"]].mean()
        jan_r, jul_r = np.expm1(X[m, col["rain-1"]]).mean(), np.expm1(X[m, col["rain-7"]]).mean()
        year = sum(np.expm1(X[m, col[f"rain-{i}"]]).mean() for i in range(1, 13))
        regions = cells.loc[m, "region"].value_counts(normalize=True).head(3)
        where = ", ".join(f"{r} {s:.0%}" for r, s in regions.items())
        print(f"   {t:>4}  {m.sum():>5}   {jan_t:>7.1f}C  {aug_t:>7.1f}C  {jan_r:>6.0f}mm"
              f"  {jul_r:>6.0f}mm  {year:>7.0f}mm  {where}")  # fmt: skip


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = ferspas.japan_cells()
    cells["region"] = cells["pref_code"].map(region_of)
    X, names = step6c.features(cells, (1991, 2020))
    Z = StandardScaler().fit_transform(X)
    print(f"## Japan: {len(cells):,} cells, {X.shape[1]} features (1991-2020 normals)")

    print("\n   k   inertia   silhouette (mean of 5 seeds)   range")
    sil = {}
    for k in KS:
        runs = [kmeans(Z, k, s) for s in SEEDS]
        scores = [silhouette_score(Z, r.labels_) for r in runs]
        sil[k] = np.mean(scores)
        print(f"   {k:>2}  {np.mean([r.inertia_ for r in runs]):>9.0f}   {sil[k]:>10.3f}"
              f"   {min(scores):.3f}-{max(scores):.3f}")  # fmt: skip
    best = max(sil, key=sil.get)
    k = best if best > 2 else max((kk for kk in KS if kk > 2), key=sil.get)
    print(f"   best silhouette at k = {best}; described below: k = 2 and k = {k}")
    describe(X, names, kmeans(Z, 2).labels_, 2, cells)

    model = kmeans(Z, k)
    labels = model.labels_
    describe(X, names, labels, k, cells)
    regions = cells["region"].to_numpy()
    print(f"\n   adjusted Rand index against the 8 regions: {adjusted_rand_score(regions, labels):.3f}"
          f" (k = 8: {adjusted_rand_score(regions, kmeans(Z, 8).labels_):.3f})")  # fmt: skip
    seeds = [kmeans(Z, k, s).labels_ for s in SEEDS]
    print(f"   agreement between seeds (ARI to seed 0): "
          f"{', '.join(f'{adjusted_rand_score(labels, s):.3f}' for s in seeds[1:])}")  # fmt: skip

    print("\n## the same k on two periods")
    early = StandardScaler().fit_transform(step6c.features(cells, (1981, 2000))[0])
    late = StandardScaler().fit_transform(step6c.features(cells, (2006, 2025))[0])
    le, ll = kmeans(early, k).labels_, kmeans(late, k).labels_
    ll = match(le, ll, k)
    print(f"   ARI 1981-2000 against 2006-2025, each fitted on its own: "
          f"{adjusted_rand_score(le, ll):.3f}; cells that change type: {(le != ll).mean():.1%}")  # fmt: skip
    # The later normals on the earlier scaling and centres: where the old types moved.
    scaler = StandardScaler().fit(step6c.features(cells, (1981, 2000))[0])
    old = KMeans(k, n_init=10, random_state=0).fit(
        scaler.transform(step6c.features(cells, (1981, 2000))[0])
    )
    moved = old.predict(scaler.transform(step6c.features(cells, (2006, 2025))[0]))
    changed = moved != old.labels_
    print(f"   the later normals on the earlier centres: {changed.mean():.1%} of cells fall in "
          f"another type")  # fmt: skip
    if changed.any():
        pairs = {}
        for a, b in zip(old.labels_[changed], moved[changed], strict=True):
            pairs[(a, b)] = pairs.get((a, b), 0) + 1
        for (a, b), n in sorted(pairs.items(), key=lambda p: -p[1])[:5]:
            print(f"      type {a} -> {b}: {n} cells")

    print("\n## the same on four whitened principal components")
    W = PCA(4, whiten=True).fit_transform(Z)
    wsil = {}
    for kk in KS:
        wsil[kk] = np.mean([silhouette_score(W, kmeans(W, kk, s).labels_) for s in SEEDS])
    print("   silhouette by k: " + ", ".join(f"{kk}: {v:.3f}" for kk, v in wsil.items()))
    wk = max((kk for kk in KS if kk > 2), key=wsil.get)
    wlabels = kmeans(W, wk).labels_
    print(
        f"   k = {wk} (best above 2); ARI against the 8 regions {adjusted_rand_score(regions, wlabels):.3f},"
        f" against the k = {wk} types on the 48 features {adjusted_rand_score(kmeans(Z, wk).labels_, wlabels):.3f}"
    )
    describe(X, names, wlabels, wk, cells)

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    for ax, lab, title in ((axes[0], labels, f"k-means, k = {k}, 48 standardised features"),
                           (axes[1], wlabels, f"k-means, k = {wk}, 4 whitened components"),
                           (axes[2], regions, "the eight regions")):  # fmt: skip
        values = np.unique(lab, return_inverse=True)[1]
        ax.scatter(cells["lon"], cells["lat"], c=values, s=3, cmap="tab10")
        ax.set_aspect(1 / np.cos(np.radians(36)))
        ax.set_title(title)
        ax.set_axis_off()
    fig.savefig(OUT / "types.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")
    print(f"credit: {ferspas.CREDIT}")


if __name__ == "__main__":
    main()
