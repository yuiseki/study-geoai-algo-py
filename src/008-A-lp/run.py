"""Step 8A: the LP relaxation of maximal covering in Taito City.

Demand is WorldPop 2025 population on 100 m cells; candidate sites are the
ward's medical facilities (P04) and schools (P29); a cell is covered when a
chosen site is within RADIUS on foot (the walking network of step 7). The
model is in study_geoai.cover.

With x relaxed to [0, 1] the problem is an LP. For k = 1 to K_MAX:
- the LP optimum, an upper bound on any choice of k sites;
- how many sites take a fractional value;
- the dual price of sum(x) = k against the LP's actual gain from one more site;
- rounding the LP (the k largest x) and greedy, both real choices of k sites.

    uv run python src/008-A-lp/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from study_geoai import aoi, cover, features, graph, ksj, osm, worldpop  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
RADIUS = 400.0
K_MAX = 20
YEAR = 2025


def covered_by(sets, pop, chosen):
    hit = np.zeros(len(pop), dtype=bool)
    for j in chosen:
        hit[sets[j]] = True
    return float(pop[hit].sum())


def instance(con, name):
    """(graph, main-component nodes, demand xy, pop, candidate names, candidate xy, sets)."""
    area = aoi.load(name, con)
    g = graph.build(osm.walk_edges(con, area))
    labels = graph.component_labels(g)
    main_nodes = np.flatnonzero(labels == np.argmax(np.bincount(labels)))
    snap = graph.Graph(g.xy[main_nodes], g.indptr, g.indices, g.weights, {})

    cells = worldpop.grid(con, area, YEAR).query(
        "w", f"""select lon, lat, population from w
                 where population > 0 and st_intersects(geometry, st_geomfromtext('{area.wkt}'))"""
    ).fetchall()  # fmt: skip
    demand_xy = features.to_metric(con, [c[:2] for c in cells])
    pop = np.array([c[2] for c in cells])
    demand_nodes = main_nodes[graph.nearest(snap, demand_xy)[0]]

    sites = []
    for dataset, label in (("P04", "P04_002"), ("P29", "P29_004")):
        rel = ksj.read(con, area, dataset)
        sites += rel.query("s", f"select {label}, st_x(geometry), st_y(geometry) from s").fetchall()
    names = [s[0] for s in sites]
    site_xy = features.to_metric(con, [s[1:] for s in sites])
    site_nodes = main_nodes[graph.nearest(snap, site_xy)[0]]
    sets = cover.coverage(g, site_nodes.tolist(), demand_nodes, RADIUS)
    return g, demand_xy, pop, names, site_xy, sets


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    g, demand_xy, pop, names, site_xy, sets = instance(con, "taito")
    reach = np.zeros(len(pop), dtype=bool)
    for s in sets:
        reach[s] = True
    print(f"## taito: {len(pop):,} populated 100 m cells, {pop.sum():,.0f} people; "
          f"{len(sets)} candidate sites (P04 and P29); radius {RADIUS:.0f} m on foot")  # fmt: skip
    print(f"   people within reach of some candidate: {pop[reach].sum() / pop.sum():.1%}; "
          f"cells per site: median {np.median([len(s) for s in sets]):.0f}")  # fmt: skip

    print(
        "\n    k   LP bound  fractional   dual   LP(k+1)-LP(k)   LP rounded   greedy"
        "   rounded/LP  greedy/LP"
    )
    rows = []
    lps = [cover.solve(sets, pop, k, integer=False) for k in range(1, K_MAX + 2)]
    for k in range(1, K_MAX + 1):
        lp = lps[k - 1]
        frac = int(((lp["x"] > 1e-6) & (lp["x"] < 1 - 1e-6)).sum())
        rounded = covered_by(sets, pop, np.argsort(-lp["x"])[:k])
        _, gre = cover.greedy(sets, pop, k)
        gain = lps[k]["objective"] - lp["objective"]
        rows.append((k, lp["objective"], frac, lp["dual_k"], gain, rounded, gre))
        print(f"   {k:>2}  {lp['objective']:>9,.0f}  {frac:>10}  {lp['dual_k']:>5,.0f}"
              f"  {gain:>14,.0f}  {rounded:>11,.0f}  {gre:>7,.0f}"
              f"  {rounded / lp['objective']:>11.3f}  {gre / lp['objective']:>9.3f}")  # fmt: skip
    R = np.array(rows)
    b = cover.solve_ortools(sets, pop, 10, integer=False)
    print(f"\n   k = 10: HiGHS {lps[9]['objective']:,.1f} in {lps[9]['seconds']:.2f} s, "
          f"OR-Tools GLOP {b['objective']:,.1f} in {b['seconds']:.2f} s")  # fmt: skip

    fig, ax = plt.subplots(figsize=(6, 4))
    total = pop.sum()
    ax.plot(R[:, 0], R[:, 1] / total, marker="o", label="LP bound")
    ax.plot(R[:, 0], R[:, 5] / total, marker="x", label="LP rounded")
    ax.plot(R[:, 0], R[:, 6] / total, marker=".", label="greedy")
    ax.set_xlabel("k (sites)")
    ax.set_ylabel(f"share of residents within {RADIUS:.0f} m")
    ax.legend()
    fig.savefig(OUT / "coverage-by-k.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    k = 10
    lp = lps[k - 1]
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(demand_xy[:, 0], demand_xy[:, 1], s=4, c=lp["y"], cmap="Greys", vmin=0, vmax=1)
    used = lp["x"] > 1e-6
    ax.scatter(site_xy[~used, 0], site_xy[~used, 1], s=6, c="#9ecae1")
    sc = ax.scatter(site_xy[used, 0], site_xy[used, 1], s=60, c=lp["x"][used], cmap="autumn_r",
                    vmin=0, vmax=1, edgecolors="black")  # fmt: skip
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(f"taito, k = {k}: LP solution (sites by x, cells by covered share y)")
    fig.colorbar(sc, ax=ax, label="x", shrink=0.6)
    fig.savefig(OUT / "lp-k10.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"   k = {k}: sites with x > 0: "
          + ", ".join(f"{names[j]} {lp['x'][j]:.2f}" for j in np.flatnonzero(used)))  # fmt: skip
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
