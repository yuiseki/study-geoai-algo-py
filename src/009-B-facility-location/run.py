"""Step 9B: p-median facility location in Taito City, against maximal covering.

Open p of the 566 candidate sites of step 8 (medical facilities P04 and schools
P29) so that residents walk as little as possible in total, each to the nearest
open site. Demand is the 108 small areas with residents (2020 census), and
distances are walks on the network of step 7 (one Dijkstra per small area).

1. The exact MILP against its LP, greedy, and greedy followed by interchange.
2. The same p with maximal covering (step 8, 400 m): mean walk against the share
   of residents within 400 m. The two objectives pick different sites.

    uv run python src/009-B-facility-location/run.py
"""

import importlib.util
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from study_geoai import aoi, cover, facility, features, ksj  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
RADIUS = 400.0
PS = (1, 2, 3, 5, 8, 10, 15, 20)
_spec = importlib.util.spec_from_file_location(
    "step9a", Path(__file__).parents[1] / "009-A-assignment" / "run.py"
)
step9a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step9a)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    area = aoi.load("taito", con)
    g, nearest = step9a.network(con, area)
    names, pop, area_xy = step9a.small_areas(con, area)
    a_nodes, a_gap = nearest(area_xy)
    sites = []
    for dataset, label in (("P04", "P04_002"), ("P29", "P29_004")):
        sites += (
            ksj.read(con, area, dataset)
            .query("s", f"select {label}, st_x(geometry), st_y(geometry) from s")
            .fetchall()
        )
    site_names = [s[0] for s in sites]
    site_xy = features.to_metric(con, [s[1:] for s in sites])
    s_nodes, s_gap = nearest(site_xy)
    t = time.perf_counter()
    # one Dijkstra per small area, read at the sites: dist[area, site]
    dist = step9a.distances(g, a_nodes, a_gap, s_nodes, s_gap).T
    print(f"## taito: {len(names)} small areas, {pop.sum():,.0f} residents; {len(sites)} "
          f"candidate sites; distances in {time.perf_counter() - t:.1f} s")  # fmt: skip
    sets = [np.flatnonzero(dist[:, j] <= RADIUS) for j in range(len(sites))]

    print(
        "\n    p   MILP mean walk   (s)    LP/MILP   greedy/MILP   interchange/MILP"
        "   p-median within 400 m   max-cover within 400 m   max-cover mean walk"
    )
    chosen_at = {}
    for p in PS:
        ex = facility.p_median(dist, pop, p)
        lp = facility.p_median(dist, pop, p, integer=False)
        gre, gcost = facility.greedy_median(dist, pop, p)
        swp, scost = facility.interchange(dist, pop, gre)
        mc = cover.solve(sets, pop, p, integer=True)
        mc_open = np.flatnonzero(mc["x"] > 0.5).tolist()
        within = lambda open_: pop[dist[:, open_].min(axis=1) <= RADIUS].sum() / pop.sum()  # noqa: E731
        lp_frac = int(((lp["y"] > 1e-6) & (lp["y"] < 1 - 1e-6)).sum())
        chosen_at[p] = (ex["open"], mc_open)
        print(f"   {p:>2}  {ex['cost'] / pop.sum():>14.0f}  {ex['seconds']:>5.1f}"
              f"  {lp['cost'] / ex['cost']:>9.4f}  {gcost / ex['cost']:>12.4f}"
              f"  {scost / ex['cost']:>17.4f}  {within(ex['open']):>22.1%}"
              f"  {within(mc_open):>23.1%}"
              f"  {facility.median_cost(dist, pop, mc_open) / pop.sum():>20.0f}"
              f"   (LP fractional sites {lp_frac})")  # fmt: skip

    p = 5
    med, mc = chosen_at[p]
    print(f"\n   p = {p}: p-median opens " + ", ".join(site_names[j] for j in med))
    print(f"   p = {p}: max cover opens " + ", ".join(site_names[j] for j in mc))
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    for ax, (title, open_) in zip(axes, (("p-median", med), ("maximal covering", mc)), strict=True):
        near = np.array(open_)[dist[:, open_].argmin(axis=1)]
        walk = dist[np.arange(len(names)), near]
        for i in range(len(names)):
            ax.plot(*np.array([area_xy[i], site_xy[near[i]]]).T, color="#aaaaaa", linewidth=0.5)
        sc = ax.scatter(area_xy[:, 0], area_xy[:, 1], s=pop / 60, c=walk, cmap="viridis_r",
                        vmin=0, vmax=1500)  # fmt: skip
        ax.scatter(site_xy[open_, 0], site_xy[open_, 1], marker="*", s=250, c="red")
        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.set_title(f"taito, p = {p}: {title}\nmean walk {(walk * pop).sum() / pop.sum():.0f} m, "
                     f"within {RADIUS:.0f} m {pop[walk <= RADIUS].sum() / pop.sum():.0%}")  # fmt: skip
        fig.colorbar(sc, ax=ax, label="walk to the nearest open site (m)", shrink=0.6)
    fig.savefig(OUT / f"p{p}-taito.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
