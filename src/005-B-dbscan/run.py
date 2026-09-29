"""Step 5B: DBSCAN and HDBSCAN on POI points, in metres.

1. Taito City, every place: how the number of clusters, the noise share and the
   largest cluster move with eps and min_samples, and the k-distance curve that
   is meant to suggest eps.
2. Taito City, food places only: can DBSCAN find the eating streets?
3. The 23 wards with the eps chosen in Taito: does one eps suit dense and sparse
   wards alike? The same question for HDBSCAN, which has no eps.

Points are Overture places projected to JGD2011 plane IX (study_geoai.features
.place_points), so eps is in metres.

    uv run python src/005-B-dbscan/run.py
"""

import time
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.cluster import DBSCAN, HDBSCAN  # noqa: E402
from sklearn.neighbors import NearestNeighbors  # noqa: E402

from study_geoai import aoi, features  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
EPS = (25, 50, 75, 100, 200)
MIN_SAMPLES = (5, 10, 20, 50)
CHOSEN = (50, 20)  # eps, min_samples carried from Taito to the 23 wards
FOOD = (40, 10)
MIN_CLUSTER_SIZE = 25


def points(con, area, kind=None):
    where = f"where kind = '{kind}'" if kind else ""
    rows = (
        features.place_points(con, area)
        .query("pp", f"select x, y, coalesce(code5, ''), coalesce(town, '') from pp {where}")
        .fetchall()
    )
    xy = np.array([r[:2] for r in rows], dtype=float)
    return xy, np.array([r[2] for r in rows]), [r[3] for r in rows]


def summary(labels):
    n = labels.max() + 1
    largest = np.bincount(labels[labels >= 0]).max() / len(labels) if n else 0.0
    return n, np.mean(labels < 0), largest


def scatter(xy, labels, path, title):
    fig, ax = plt.subplots(figsize=(8, 7))
    noise = labels < 0
    ax.scatter(xy[noise, 0], xy[noise, 1], s=0.3, c="#bbbbbb")
    # shuffle the colours so neighbouring clusters differ
    colours = np.random.default_rng(0).permutation(max(labels.max() + 1, 1))
    ax.scatter(xy[~noise, 0], xy[~noise, 1], s=0.6, c=colours[labels[~noise]] % 20,
               cmap="tab20", vmin=0, vmax=19)  # fmt: skip
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(title)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def sensitivity(xy):
    print("   eps (m)  min_samples  clusters  noise   largest")
    for eps in EPS:
        for ms in MIN_SAMPLES:
            n, noise, largest = summary(DBSCAN(eps=eps, min_samples=ms).fit_predict(xy))
            print(f"   {eps:>7}  {ms:>11}  {n:>8}  {noise:.3f}   {largest:.3f}")


def k_distance(xy, ks=(5, 10, 20, 50)):
    """Sorted distance to the k-th neighbour; its knee is the usual hint for eps."""
    d, _ = NearestNeighbors(n_neighbors=max(ks)).fit(xy).kneighbors(xy)
    fig, ax = plt.subplots(figsize=(6, 4))
    for k in ks:
        kth = np.sort(d[:, k - 1])  # the point itself is its own first neighbour
        ax.plot(np.linspace(0, 1, len(kth)), kth, label=f"k = {k}")
        print(f"   k = {k:>2}: distance to the k-th neighbour, median {np.median(kth):.0f} m, "
              f"90th percentile {np.percentile(kth, 90):.0f} m")  # fmt: skip
    ax.set_ylim(0, 300)
    ax.set_xlabel("share of points (sorted)")
    ax.set_ylabel("distance to k-th neighbour (m)")
    ax.legend()
    fig.savefig(OUT / "k-distance-taito.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def describe(labels, towns, top=12):
    """The largest clusters, each named by the small areas most of its points lie in."""
    sizes = Counter(labels[labels >= 0].tolist())
    for c, size in sizes.most_common(top):
        where = Counter(t for t, lab in zip(towns, labels, strict=True) if lab == c)
        names = ", ".join(f"{t} {k}" for t, k in where.most_common(3))
        print(f"   cluster {c:>3}: {size:>5} places; {names}")


def by_ward(con, area, codes, labels, name):
    """Per ward: POIs per km2 and the share of POIs put in some cluster."""
    rows = []
    for w in aoi.wards(area, con):
        km2 = con.sql(f"""select st_area(st_transform(st_geomfromtext('{w.wkt}'), 'EPSG:4326',
                                 '{features.METRIC_CRS}', always_xy := true)) / 1e6""").fetchone()[
            0
        ]
        m = codes == w.name
        rows.append((w.name, m.sum() / km2, np.mean(labels[m] >= 0), len(set(labels[m]) - {-1})))
    rho, p = spearmanr([r[1] for r in rows], [r[2] for r in rows])
    print(f"\n   {name}: per ward, POIs per km2 against the share put in a cluster")
    print("   ward    POIs/km2  clustered  clusters")
    for code, density, share, n in sorted(rows, key=lambda r: -r[1]):
        print(f"   {code}  {density:>8.0f}  {share:>9.3f}  {n:>8}")
    print(f"   Spearman {rho:+.2f} (p {p:.3g}); clustered share ranges "
          f"{min(r[2] for r in rows):.3f} to {max(r[2] for r in rows):.3f}")  # fmt: skip
    return rows


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)

    taito = aoi.load("taito", con)
    xy, _, towns = points(con, taito)
    print(f"## taito: {len(xy):,} places")
    sensitivity(xy)
    k_distance(xy)
    for eps, ms in ((25, 10), CHOSEN, (100, 5)):
        labels = DBSCAN(eps=eps, min_samples=ms).fit_predict(xy)
        n, noise, largest = summary(labels)
        scatter(xy, labels, OUT / f"dbscan-taito-{eps}m-{ms}.png",
                f"taito: DBSCAN eps {eps} m, min_samples {ms}: {n} clusters, "
                f"noise {noise:.0%}")  # fmt: skip
    labels = DBSCAN(eps=CHOSEN[0], min_samples=CHOSEN[1]).fit_predict(xy)
    print(f"\n   eps {CHOSEN[0]} m, min_samples {CHOSEN[1]}: largest clusters")
    describe(labels, towns)
    t = time.time()
    labels = HDBSCAN(min_cluster_size=MIN_CLUSTER_SIZE, copy=True).fit_predict(xy)
    n, noise, largest = summary(labels)
    print(f"\n   HDBSCAN min_cluster_size {MIN_CLUSTER_SIZE}: {n} clusters, noise {noise:.3f}, "
          f"largest {largest:.3f} ({time.time() - t:.1f} s)")  # fmt: skip
    describe(labels, towns)
    scatter(xy, labels, OUT / "hdbscan-taito.png",
            f"taito: HDBSCAN min_cluster_size {MIN_CLUSTER_SIZE}: {n} clusters, noise {noise:.0%}")  # fmt: skip

    xy, _, towns = points(con, taito, "food")
    eps, ms = FOOD
    labels = DBSCAN(eps=eps, min_samples=ms).fit_predict(xy)
    n, noise, largest = summary(labels)
    print(f"\n## taito, food only: {len(xy):,} places; eps {eps} m, min_samples {ms}: "
          f"{n} clusters, noise {noise:.3f}, largest {largest:.3f}")  # fmt: skip
    describe(labels, towns)
    scatter(
        xy,
        labels,
        OUT / "dbscan-taito-food.png",
        f"taito, food: DBSCAN eps {eps} m, min_samples {ms}: {n} clusters",
    )

    tokyo23 = aoi.load("tokyo23", con)
    xy, codes, _ = points(con, tokyo23)
    print(f"\n## tokyo23: {len(xy):,} places")
    eps, ms = CHOSEN
    t = time.time()
    labels = DBSCAN(eps=eps, min_samples=ms).fit_predict(xy)
    n, noise, largest = summary(labels)
    print(f"   DBSCAN eps {eps} m, min_samples {ms}: {n} clusters, noise {noise:.3f}, "
          f"largest {largest:.3f} ({time.time() - t:.1f} s)")  # fmt: skip
    scatter(
        xy,
        labels,
        OUT / "dbscan-tokyo23.png",
        f"tokyo23: DBSCAN eps {eps} m, min_samples {ms}: noise {noise:.0%}",
    )
    by_ward(con, tokyo23, codes, labels, "DBSCAN")
    t = time.time()
    labels = HDBSCAN(min_cluster_size=MIN_CLUSTER_SIZE, copy=True).fit_predict(xy)
    n, noise, largest = summary(labels)
    print(f"\n   HDBSCAN min_cluster_size {MIN_CLUSTER_SIZE}: {n} clusters, noise {noise:.3f}, "
          f"largest {largest:.3f} ({time.time() - t:.1f} s)")  # fmt: skip
    scatter(
        xy,
        labels,
        OUT / "hdbscan-tokyo23.png",
        f"tokyo23: HDBSCAN min_cluster_size {MIN_CLUSTER_SIZE}: noise {noise:.0%}",
    )
    by_ward(con, tokyo23, codes, labels, "HDBSCAN")
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
