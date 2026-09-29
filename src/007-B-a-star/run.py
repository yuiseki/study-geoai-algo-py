"""Step 7B: A* against Dijkstra on Taito City's walking network.

1. Random pairs of small-area centres: nodes settled, time and path length for
   Dijkstra stopped at the target, A*, and A* with the heuristic inflated.
2. How the number of settled nodes grows with the distance.
3. A map of the nodes each search settles for one long pair.
4. The largest detours of step 7A, drawn, to see what the walk goes around.

    uv run python src/007-B-a-star/run.py
"""

import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

from study_geoai import aoi, census, ckan, features, graph, ksj, osm  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
PAIRS = 300
INFLATIONS = (1.0, 1.2, 1.5, 2.0, 3.0)
DETOURS = [  # from step 7A: small area, destination kind, destination name
    ("池之端二丁目", "hospital", "東京大学医学部附属病院"),
    ("根岸一丁目", "shelter", "上野中学校"),
    ("駒形二丁目", "hospital", "医療法人　相生会　墨田病院"),
]


def background(ax, g, box, colour="#dddddd"):
    x0, y0, x1, y1 = box
    inside = ((g.xy[:, 0] >= x0) & (g.xy[:, 0] <= x1)
              & (g.xy[:, 1] >= y0) & (g.xy[:, 1] <= y1))  # fmt: skip
    lines = [[g.xy[u], g.xy[v]] for u in np.flatnonzero(inside)
             for v, _ in g.neighbours(u) if u < v]  # fmt: skip
    ax.add_collection(LineCollection(lines, colors=colour, linewidths=0.4))


def draw_path(ax, g, nodes, colour, label):
    xy = g.xy[nodes]
    ax.plot(xy[:, 0], xy[:, 1], color=colour, linewidth=2, label=label)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    area = aoi.load("taito", con)
    g = graph.build(osm.walk_edges(con, area))
    labels = graph.component_labels(g)
    main_nodes = np.flatnonzero(labels == np.argmax(np.bincount(labels)))
    tree_xy = g.xy[main_nodes]

    census.small_areas(con, area).create_view("sa")
    sa = con.sql("""select name, st_x(st_centroid(geometry)), st_y(st_centroid(geometry))
                    from sa where population > 0 order by key11""").fetchall()
    names = [r[0] for r in sa]
    centres = features.to_metric(con, [r[1:] for r in sa])
    snap = graph.Graph(tree_xy, g.indptr, g.indices, g.weights, {})
    nodes = main_nodes[graph.nearest(snap, centres)[0]]

    rng = np.random.default_rng(0)
    pairs = set()
    while len(pairs) < PAIRS:
        a, b = rng.choice(len(nodes), 2, replace=False)
        if nodes[a] != nodes[b]:
            pairs.add((int(nodes[a]), int(nodes[b])))
    pairs = sorted(pairs)

    rows = []  # (straight, optimum, dijkstra settled, time, then per inflation settled, time, length)
    for s, t in pairs:
        t0 = time.perf_counter()
        dist, _, n_dij = graph.dijkstra(g, [s], target=t)
        t_dij = time.perf_counter() - t0
        row = [float(np.hypot(*(g.xy[s] - g.xy[t]))), dist[t], n_dij, t_dij]
        for inf in INFLATIONS:
            t0 = time.perf_counter()
            length, _, n = graph.astar(g, s, t, inflation=inf)
            row += [n, time.perf_counter() - t0, length]
        rows.append(row)
    R = np.array(rows)
    straight, optimum, n_dij, t_dij = R[:, 0], R[:, 1], R[:, 2], R[:, 3]
    exact = np.allclose(R[:, 4 + 2], optimum)  # A* with inflation 1
    print(f"## taito: {g.n_nodes:,} nodes; {PAIRS} pairs of small-area centres; "
          f"straight line median {np.median(straight):.0f} m, max {straight.max():.0f} m")  # fmt: skip
    print(f"   A* (inflation 1) finds the same length as Dijkstra for every pair: {exact}")
    print(
        "   search            settled nodes (median)  vs Dijkstra  time (median ms)  vs Dijkstra"
        "  length over shortest (median, max)"
    )
    print(f"   Dijkstra          {np.median(n_dij):>22,.0f}  {1:>10.2f}  {np.median(t_dij) * 1e3:>16.1f}"
          f"  {1:>11.2f}  1.000, 1.000")  # fmt: skip
    for k, inf in enumerate(INFLATIONS):
        n, t, length = R[:, 4 + 3 * k], R[:, 5 + 3 * k], R[:, 6 + 3 * k]
        over = length / optimum
        print(f"   A* x {inf:<4}        {np.median(n):>22,.0f}  {np.median(n / n_dij):>10.2f}"
              f"  {np.median(t) * 1e3:>16.1f}  {np.median(t / t_dij):>11.2f}"
              f"  {np.median(over):.3f}, {over.max():.3f}")  # fmt: skip

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.scatter(optimum, n_dij, s=6, label="Dijkstra")
    for inf in INFLATIONS[:1] + INFLATIONS[3:4]:
        col = 4 + 3 * INFLATIONS.index(inf)
        ax.scatter(optimum, R[:, col], s=6, label=f"A* x {inf}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("shortest walk (m)")
    ax.set_ylabel("nodes settled")
    ax.legend()
    fig.savefig(OUT / "settled-by-distance.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    far = optimum > 500
    for label, col in (("Dijkstra", 2), ("A* x 1", 4), ("A* x 2", 4 + 3 * 3)):
        slope = np.polyfit(np.log(optimum[far]), np.log(R[far, col]), 1)[0]
        print(f"   {label}: settled nodes grow as distance ^ {slope:.2f} (pairs over 500 m)")

    s, t = pairs[int(np.argmax(optimum))]
    traces = {}
    for label, inf in (("Dijkstra", None), ("A*", 1.0), ("A* x 2", 2.0)):
        trace = []
        if inf is None:
            dist, pred, _ = graph.dijkstra(g, [s], target=t, trace=trace)
            route = graph.path(pred, t)
        else:
            _, route, _ = graph.astar(g, s, t, inflation=inf, trace=trace)
        traces[label] = (trace, route)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    box = (*g.xy[main_nodes].min(axis=0), *g.xy[main_nodes].max(axis=0))
    for ax, (label, (trace, route)) in zip(axes, traces.items(), strict=True):
        background(ax, g, box)
        ax.scatter(g.xy[trace, 0], g.xy[trace, 1], s=0.3, c="tab:orange")
        draw_path(ax, g, route, "tab:blue", "path")
        ax.set_title(f"{label}: {len(trace):,} nodes settled")
        ax.set_aspect("equal")
        ax.set_axis_off()
    fig.savefig(OUT / "settled-map.png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"   map of the longest pair ({optimum.max():.0f} m): "
          + ", ".join(f"{k} {len(v[0]):,}" for k, v in traces.items()))  # fmt: skip

    print("\n## the largest detours of 7A, drawn")
    hosp = (
        ksj.read(con, aoi.load("tokyo23", con), "P04")
        .query("p", "select P04_002, st_x(geometry), st_y(geometry) from p where P04_001 = 1")
        .fetchall()
    )
    shel = (
        ckan.facilities(con, area, "指定緊急避難場所一覧")
        .query("f", "select name, lon, lat from f where status = 'ok'")
        .fetchall()
    )
    places = {("hospital", r[0]): r[1:] for r in hosp} | {("shelter", r[0]): r[1:] for r in shel}
    for town, kind, dest in DETOURS:
        o = names.index(town)
        d_xy = features.to_metric(con, [places[(kind, dest)]])[0]
        d_node = int(main_nodes[graph.nearest(snap, d_xy[None, :])[0][0]])
        dist, pred, _ = graph.dijkstra(g, [nodes[o]], target=d_node)
        route = graph.path(pred, d_node)
        straight_line = np.hypot(*(g.xy[nodes[o]] - g.xy[d_node]))
        print(f"   {town} to {dest}: walk {dist[d_node]:.0f} m along {len(route)} nodes, "
              f"straight {straight_line:.0f} m (node to node)")  # fmt: skip
        xy = g.xy[[nodes[o], d_node]]
        pad = 250
        box = (
            xy[:, 0].min() - pad,
            xy[:, 1].min() - pad,
            xy[:, 0].max() + pad,
            xy[:, 1].max() + pad,
        )
        route_xy = g.xy[route]
        box = (min(box[0], route_xy[:, 0].min() - 50), min(box[1], route_xy[:, 1].min() - 50),
               max(box[2], route_xy[:, 0].max() + 50), max(box[3], route_xy[:, 1].max() + 50))  # fmt: skip
        fig, ax = plt.subplots(figsize=(7, 7))
        background(ax, g, box, colour="#bbbbbb")
        ax.plot(xy[:, 0], xy[:, 1], "--", color="black", linewidth=1, label="straight line")
        draw_path(ax, g, route, "tab:red", "shortest walk")
        ax.scatter(*xy.T, c=["tab:blue", "tab:red"], s=40, zorder=3)
        ax.set_xlim(box[0], box[2])
        ax.set_ylim(box[1], box[3])
        ax.set_aspect("equal")
        ax.set_axis_off()
        ax.legend(loc="lower right")
        ax.set_title(f"{town} to {dest}: {dist[d_node]:.0f} m on foot, {straight_line:.0f} m straight",
                     fontfamily="Noto Sans CJK JP")  # fmt: skip
        fig.savefig(OUT / f"detour-{town}.png", dpi=130, bbox_inches="tight")
        plt.close(fig)
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
