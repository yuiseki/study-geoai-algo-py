"""Step 7A: walking distance from every small area of Taito City to the nearest
hospital and the nearest designated emergency evacuation site, by Dijkstra.

The walking network is built from OSM ways (study_geoai.osm.walk_edges), joined
where they share a vertex. One Dijkstra started from all destinations at once
(multi-source) gives every node its distance to the nearest one; it is checked
against one run per destination and against networkx.

The detour ratio is the walking distance over the straight-line distance to
the same destination: where is the walk much longer than the crow flies?

    uv run python src/007-A-dijkstra/run.py
"""

import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

from study_geoai import aoi, census, ckan, graph, ksj, osm, plot  # noqa: E402
from study_geoai.db import connect  # noqa: E402
from study_geoai.features import METRIC_CRS  # noqa: E402

OUT = Path(__file__).parent / "output"
BUFFER_DEG = osm.BUFFER_DEG
MIN_STRAIGHT = 300  # below this the snapping steps (up to about 50 m) dominate the ratio


def metric(con, lonlat):
    """lon/lat pairs to METRIC_CRS metres."""
    con.execute("create or replace temp table _ll (lon double, lat double)")
    con.executemany("insert into _ll values (?, ?)", [tuple(p) for p in lonlat])
    rows = con.sql(f"""
        select st_x(m), st_y(m) from (
            select st_transform(st_point(lon, lat), 'EPSG:4326', '{METRIC_CRS}',
                                always_xy := true) as m from _ll)
    """).fetchall()
    return np.array(rows, dtype=float)


def hospitals(con, area):
    """Hospitals (P04_001 = 1, not clinics) within the area's bbox plus the buffer,
    so that a hospital just over the ward border counts."""
    xmin, ymin, xmax, ymax = area.bbox
    rows = ksj.read(con, aoi.load("tokyo23", con), "P04").query("p", f"""
        select P04_002, st_x(geometry), st_y(geometry) from p
        where P04_001 = 1
          and st_x(geometry) between {xmin - BUFFER_DEG} and {xmax + BUFFER_DEG}
          and st_y(geometry) between {ymin - BUFFER_DEG} and {ymax + BUFFER_DEG}
        order by 1
    """).fetchall()  # fmt: skip
    return [r[0] for r in rows], np.array([r[1:] for r in rows], dtype=float)


def shelters(con, area):
    """Designated emergency evacuation sites published by the ward (the ward's own list)."""
    rows = (
        ckan.facilities(con, area, "指定緊急避難場所一覧")
        .query("f", "select name, lon, lat from f where status = 'ok' order by row")
        .fetchall()
    )
    return [r[0] for r in rows], np.array([r[1:] for r in rows], dtype=float)


def check_against_others(g, sources):
    """The multi-source run against one run per source, and against networkx."""
    t = time.perf_counter()
    multi, owner, _ = graph.dijkstra(g, sources, return_owner=True)
    t_multi = time.perf_counter() - t
    t = time.perf_counter()
    each = np.min([graph.dijkstra(g, [s])[0] for s in sources], axis=0)
    t_each = time.perf_counter() - t
    ref = nx.Graph()
    for u in range(g.n_nodes):
        for v, w in g.neighbours(u):
            if u < v:
                ref.add_edge(u, v, weight=w)
    t = time.perf_counter()
    nxd = nx.multi_source_dijkstra_path_length(ref, set(sources))
    t_nx = time.perf_counter() - t
    reach = np.isfinite(multi)
    same_each = np.allclose(multi[reach], each[reach])
    same_nx = all(abs(nxd[u] - multi[u]) < 1e-6 for u in nxd)
    print(f"   multi-source: {t_multi:.2f} s; one run per destination ({len(sources)} runs): "
          f"{t_each:.2f} s; networkx: {t_nx:.2f} s")  # fmt: skip
    print(f"   same distances as one run per destination: {same_each}; as networkx: {same_nx}")
    return multi, owner


def network_map(g, dist, dest_xy, outline_xy, path, title, cap=1500):
    lines, colours = [], []
    for u in range(g.n_nodes):
        for v, _ in g.neighbours(u):
            if u < v and np.isfinite(dist[u]) and np.isfinite(dist[v]):
                lines.append([g.xy[u], g.xy[v]])
                colours.append(min((dist[u] + dist[v]) / 2, cap))
    fig, ax = plt.subplots(figsize=(8, 8))
    coll = LineCollection(lines, array=np.array(colours), cmap="viridis_r", linewidths=0.4)
    ax.add_collection(coll)
    for ring in outline_xy:
        ax.plot(ring[:, 0], ring[:, 1], color="black", linewidth=0.8)
    ax.scatter(dest_xy[:, 0], dest_xy[:, 1], marker="+", c="red", s=60, linewidths=1.5)
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title(title)
    fig.colorbar(coll, ax=ax, label=f"walking distance (m, capped at {cap})", shrink=0.6)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    area = aoi.load("taito", con)
    t = time.perf_counter()
    edges = osm.walk_edges(con, area)
    g = graph.build(edges)
    labels = graph.component_labels(g)
    sizes = np.bincount(labels)
    main_c = int(np.argmax(sizes))
    print(f"## taito walking network: {len(edges):,} edges, {g.n_nodes:,} nodes "
          f"({time.perf_counter() - t:.1f} s)")  # fmt: skip
    print(f"   components: {len(sizes):,}; the largest holds {sizes[main_c] / g.n_nodes:.1%} "
          f"of nodes; the next: {sorted(sizes, reverse=True)[1:6]}")  # fmt: skip
    keep = labels == main_c
    lengths = edges[:, 4]
    print(f"   total length {lengths.sum() / 1000:.0f} km; "
          f"degree-2 nodes {np.mean(np.diff(g.indptr) == 2):.0%}")  # fmt: skip

    census.small_areas(con, area).create_view("sa")
    sa = con.sql("""
        select key11, name, population, st_x(st_centroid(geometry)), st_y(st_centroid(geometry)),
               st_asgeojson(geometry)
        from sa where population > 0 order by key11
    """).fetchall()
    origins = metric(con, [r[3:5] for r in sa])
    # snap only to the largest component, so every origin can reach somewhere
    main_nodes = np.flatnonzero(keep)
    sub = graph.Graph(g.xy[main_nodes], g.indptr, g.indices, g.weights, {})
    o_idx, o_gap = graph.nearest(sub, origins)
    o_node = main_nodes[o_idx]
    print(f"   {len(sa)} small areas with residents; centroid to network: median "
          f"{np.median(o_gap):.0f} m, max {o_gap.max():.0f} m")  # fmt: skip
    outline = json.loads(con.execute("select st_asgeojson(st_transform(st_geomfromtext(?), "
                                     f"'EPSG:4326', '{METRIC_CRS}', always_xy := true))",
                                     [area.wkt]).fetchone()[0])  # fmt: skip
    rings = (
        outline["coordinates"] if outline["type"] == "MultiPolygon" else [outline["coordinates"]]
    )
    outline_xy = [np.array(p[0]) for p in rings]

    for kind, (names, lonlat) in (("hospital", hospitals(con, area)),
                                  ("shelter", shelters(con, area))):  # fmt: skip
        dest = metric(con, lonlat)
        d_idx, d_gap = graph.nearest(sub, dest)
        d_node = main_nodes[d_idx]
        print(f"\n## nearest {kind}: {len(names)} destinations; snapping gap median "
              f"{np.median(d_gap):.0f} m, max {d_gap.max():.0f} m")  # fmt: skip
        dist, owner = check_against_others(g, list(dict.fromkeys(d_node.tolist())))
        walk = dist[o_node] + o_gap  # add the step from the centroid onto the network
        reached = {int(n): i for i, n in enumerate(d_node)}
        target = np.array([reached[int(owner[n])] for n in o_node])
        crow_same = np.hypot(*(origins - dest[target]).T)
        crow_min = np.hypot(origins[:, None, 0] - dest[None, :, 0],
                            origins[:, None, 1] - dest[None, :, 1])  # fmt: skip
        nearest_by_crow = crow_min.argmin(axis=1)
        far = crow_same >= MIN_STRAIGHT
        ratio = np.where(far, walk / np.maximum(crow_same, 1.0), np.nan)
        differs = np.mean(nearest_by_crow != target)
        pop = np.array([r[2] for r in sa], dtype=float)
        print(f"   walking distance: median {np.median(walk):.0f} m, 90th percentile "
              f"{np.percentile(walk, 90):.0f} m, max {walk.max():.0f} m; "
              f"residents over 1 km: {pop[walk > 1000].sum() / pop.sum():.1%}")  # fmt: skip
        print(f"   detour ratio (walk / straight line to the same {kind}), {far.sum()} small "
              f"areas at least {MIN_STRAIGHT} m away: median {np.nanmedian(ratio):.2f}, "
              f"90th percentile {np.nanpercentile(ratio, 90):.2f}")  # fmt: skip
        print(f"   the nearest {kind} by straight line is not the nearest on foot for "
              f"{differs:.0%} of small areas")  # fmt: skip
        order = np.argsort(-np.nan_to_num(ratio))
        for k in order[:6]:
            print(f"      {sa[k][1]}: walk {walk[k]:.0f} m, straight {crow_same[k]:.0f} m, "
                  f"ratio {ratio[k]:.2f}, to {names[target[k]]}")  # fmt: skip
        geo = [r[5] for r in sa]
        plot.choropleth(list(zip(geo, walk.tolist(), strict=True)),
                        OUT / f"walk-{kind}-taito.png",
                        f"taito: walking distance to the nearest {kind} (m)", "m")  # fmt: skip
        plot.choropleth([(gj, r) for gj, r, f in zip(geo, ratio.tolist(), far, strict=True) if f],
                        OUT / f"detour-{kind}-taito.png",
                        f"taito: detour ratio to the nearest {kind}", "walk / straight line")  # fmt: skip
        network_map(g, dist, dest, outline_xy, OUT / f"network-{kind}-taito.png",
                    f"taito: walking distance to the nearest {kind} (+)")  # fmt: skip
    print(f"\nmaps: {OUT}")


if __name__ == "__main__":
    main()
