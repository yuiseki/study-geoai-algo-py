"""Step 9A: assigning Taito City's residents to evacuation sites with capacities.

The ward's 17 designated emergency evacuation sites publish an expected
capacity (想定収容人数), 2,244 people in all against 209,000 residents. As a
teaching setting, 1 % of each small area's residents (SHARE) go to a site,
about 2,090 people: it fits the total capacity with little room to spare.
Distances are walks on the network of step 7 (one Dijkstra per site).

1. Nearest site for everyone, ignoring capacity: which sites overflow.
2. The transportation LP with capacities (an area may be split between sites):
   integral without asking, because integer data meets a totally unimodular matrix.
3. Without splitting areas (single source): a MILP, and what it costs.
4. The same problem as a one-to-one assignment of people to seats (Hungarian).

    uv run python src/009-A-assignment/run.py
"""

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from study_geoai import aoi, census, ckan, facility, features, graph, osm  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
SHARE = 0.01


def network(con, area):
    """The walking graph, and a nearest-node lookup restricted to its largest component."""
    g = graph.build(osm.walk_edges(con, area))
    labels = graph.component_labels(g)
    main_nodes = np.flatnonzero(labels == np.argmax(np.bincount(labels)))
    snap = graph.Graph(g.xy[main_nodes], g.indptr, g.indices, g.weights, {})

    def nearest(xy):
        idx, gap = graph.nearest(snap, xy)
        return main_nodes[idx], gap

    return g, nearest


def small_areas(con, area):
    census.small_areas(con, area).create_view("sa")
    rows = con.sql("""select name, population, st_x(st_centroid(geometry)),
                             st_y(st_centroid(geometry))
                      from sa where population > 0 order by key11""").fetchall()
    return [r[0] for r in rows], np.array([r[1] for r in rows], dtype=float), \
        features.to_metric(con, [r[2:] for r in rows])  # fmt: skip


def distances(g, from_nodes, from_gap, to_nodes, to_gap):
    """dist[to, from]: one full Dijkstra per 'from' node, plus the steps onto the network."""
    out = np.empty((len(to_nodes), len(from_nodes)))
    for j, (n, gap) in enumerate(zip(from_nodes, from_gap, strict=True)):
        d, _, _ = graph.dijkstra(g, [int(n)])
        out[:, j] = d[to_nodes] + to_gap + gap
    return out


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    area = aoi.load("taito", con)
    g, nearest = network(con, area)
    names, pop, area_xy = small_areas(con, area)
    a_nodes, a_gap = nearest(area_xy)
    rows = ckan.facilities(con, area, "指定緊急避難場所一覧").query("f", """
        select name, lon, lat, cast(attributes->>'$.想定収容人数' as integer),
               attributes->>'$.備考'
        from f where status = 'ok' order by row""").fetchall()  # fmt: skip
    sites = [r[0] for r in rows]
    cap = np.array([r[3] for r in rows], dtype=float)
    arakawa_closed = np.array(["荒川が氾濫" in (r[4] or "") for r in rows])
    site_xy = features.to_metric(con, [r[1:3] for r in rows])
    s_nodes, s_gap = nearest(site_xy)
    t = time.perf_counter()
    dist = distances(g, s_nodes, s_gap, a_nodes, a_gap)
    demand = np.round(pop * SHARE)
    print(f"## taito: {len(names)} small areas, {pop.sum():,.0f} residents; demand {SHARE:.0%} "
          f"of residents = {demand.sum():,.0f} people; {len(sites)} sites, capacity "
          f"{cap.sum():,.0f}; distances in {time.perf_counter() - t:.1f} s")  # fmt: skip

    load = facility.nearest_load(dist, demand, len(sites))
    over = load > cap
    near_cost = float((dist.min(axis=1) * demand).sum())
    print(f"\n1. nearest site, capacity ignored: mean walk {near_cost / demand.sum():.0f} m; "
          f"{over.sum()} of {len(sites)} sites overflow, by {(load - cap)[over].sum():,.0f} people "
          f"in all; the fullest gets {load.max():,.0f} for {cap[np.argmax(load)]:,.0f} seats "
          f"({sites[int(np.argmax(load))]})")  # fmt: skip

    tr = facility.transport(dist, demand, cap)
    flow = tr["flow"]
    split = int(((flow > 1e-6).sum(axis=1) > 1).sum())
    integral = bool(np.allclose(flow, np.round(flow)))
    per_person = np.repeat(dist.ravel(), np.round(flow.ravel()).astype(int))
    print(f"\n2. transportation LP: mean walk {tr['cost'] / demand.sum():.0f} m "
          f"(+{tr['cost'] / near_cost - 1:.0%} over nearest), longest {per_person.max():.0f} m; "
          f"{split} areas split between sites; flows integral: {integral}; "
          f"{tr['seconds']:.2f} s; sites full: {(flow.sum(axis=0) >= cap - 1e-6).sum()}")  # fmt: skip

    ss = facility.transport(dist, demand, cap, single_source=True)
    print(f"\n3. single source (MILP): mean walk {ss['cost'] / demand.sum():.0f} m, "
          f"+{ss['cost'] / tr['cost'] - 1:.2%} over the LP; {ss['seconds']:.2f} s; {ss['status']}")  # fmt: skip

    t = time.perf_counter()
    h = facility.hungarian_seats(dist, demand, cap)
    print(f"\n4. Hungarian on {demand.sum():,.0f} people x {cap.sum():,.0f} seats: total "
          f"{h:,.0f} m against the LP's {tr['cost']:,.0f} m; {time.perf_counter() - t:.2f} s")  # fmt: skip

    open_cap = cap[~arakawa_closed].sum()
    r = facility.transport(dist[:, ~arakawa_closed], demand, cap[~arakawa_closed])
    print(f"\n5. if the Arakawa may flood, {arakawa_closed.sum()} sites stay shut: "
          f"{(~arakawa_closed).sum()} open with {open_cap:,.0f} seats for {demand.sum():,.0f} "
          f"people; the LP says: {r['status']}")  # fmt: skip

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    for ax, (title, f) in zip(axes, (
        ("nearest site (capacity ignored)", np.eye(len(sites))[dist.argmin(axis=1)] * demand[:, None]),
        ("transportation LP (capacity kept)", flow),
    ), strict=True):  # fmt: skip
        for i, j in zip(*np.nonzero(f > 1e-6), strict=True):
            ax.plot(*np.array([area_xy[i], site_xy[j]]).T, color="tab:blue",
                    linewidth=0.3 + f[i, j] / 20, alpha=0.6)  # fmt: skip
        used = f.sum(axis=0)
        ax.scatter(area_xy[:, 0], area_xy[:, 1], s=demand, c="tab:blue")
        ax.scatter(site_xy[:, 0], site_xy[:, 1], s=cap, c=np.where(used > cap + 1e-6, "red", "black"),
                   marker="s", alpha=0.5)  # fmt: skip
        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.set_title(f"taito: {title}\n(squares: sites sized by capacity, red when over)")
    fig.savefig(OUT / "assignment-taito.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
