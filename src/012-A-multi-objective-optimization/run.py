"""Step 12A: three objectives for siting in Taito City, by weighted sums.

The covering problem of step 8A (WorldPop 100 m cells, 566 candidate sites,
400 m on foot) gets two more objectives: open few sites (cost), and avoid
flood-prone places. Each candidate's flood rank is the deepest of the
maximum-scale flood depth ranks (KSJ A31a, 想定最大規模) of the Arakawa,
Sumida and Kanda rivers at the site: 0 when outside, 1 under 0.5 m, 2 up to
3 m, 3 up to 5 m, 4 up to 10 m. The third objective is the sum over opened sites.

Weighted sum: maximise covered - W_SITE * sites - W_FLOOD * flood, with the
number of sites free, for a grid of weights; keep the solutions that no other
solution beats on all three objectives (Pareto).

    uv run python -u src/012-A-multi-objective-optimization/run.py
"""

import importlib.util
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from study_geoai import aoi, cover, ksj  # noqa: E402
from study_geoai.db import connect  # noqa: E402
from study_geoai.features import METRIC_CRS  # noqa: E402

OUT = Path(__file__).parent / "output"
W_SITE = (1000, 2000, 3000, 5000, 8000)  # people a site must add to be worth opening
W_FLOOD = (0, 500, 1000, 2000, 4000, 8000, 16000)  # people traded for one flood rank
_spec = importlib.util.spec_from_file_location(
    "step8a", Path(__file__).parents[1] / "008-A-lp" / "run.py"
)
step8a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step8a)


def instance(con):
    """(pop, sets, flood rank per candidate, candidate xy, names) for Taito."""
    _, _, pop, names, site_xy, sets = step8a.instance(con, "taito")
    area = aoi.load("taito", con)
    ksj.read(con, area, "A31a").create_view("_flood")
    con.execute("create or replace temp table _sites (i integer, x double, y double)")
    con.executemany("insert into _sites values (?, ?, ?)",
                    [(i, float(x), float(y)) for i, (x, y) in enumerate(site_xy)])  # fmt: skip
    rows = con.sql(f"""
        with f as (
            select cast(A31a_205 as integer) as rank,
                   st_transform(geometry, 'EPSG:6668', '{METRIC_CRS}', always_xy := true) as g
            from _flood where source_file like 'A31a-20-%'
        )
        select s.i, coalesce(max(f.rank), 0)
        from _sites s left join f on st_contains(f.g, st_point(s.x, s.y))
        group by s.i order by s.i
    """).fetchall()
    flood = np.array([r[1] for r in rows], dtype=float)
    return pop, sets, flood, site_xy, names


def pareto(points):
    """Indices of points not dominated: more covered, fewer sites, less flood."""
    keep = []
    for i, (c, s, f) in enumerate(points):
        beaten = any(c2 >= c and s2 <= s and f2 <= f and (c2, s2, f2) != (c, s, f)
                     for c2, s2, f2 in points)  # fmt: skip
        if not beaten:
            keep.append(i)
    return keep


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    pop, sets, flood, site_xy, _ = instance(con)
    counts = np.bincount(flood.astype(int), minlength=5)
    print(f"## taito: {len(pop):,} cells, {pop.sum():,.0f} people; {len(sets)} candidates by "
          f"flood rank 0 to 4: {counts.tolist()}")  # fmt: skip
    for r in range(5):
        m = flood == r
        if m.any():
            reach = np.zeros(len(pop), dtype=bool)
            for j in np.flatnonzero(m):
                reach[sets[j]] = True
            print(f"   rank {r}: {m.sum()} candidates, together within 400 m of "
                  f"{pop[reach].sum() / pop.sum():.1%} of people")  # fmt: skip

    print("\n   w_site  w_flood   sites     covered   share   flood   seconds")
    sols = {}
    for ws in W_SITE:
        for wf in W_FLOOD:
            r = cover.solve_multi(sets, pop, flood, w_site=ws, w_flood=wf)
            key = (round(r["covered"]), r["sites"], round(r["flood"]))
            sols.setdefault(key, []).append((ws, wf))
            print(f"   {ws:>6}  {wf:>7}  {r['sites']:>6}  {r['covered']:>10,.0f}  "
                  f"{r['covered'] / pop.sum():>6.1%}  {r['flood']:>6.0f}  {r['seconds']:>8.1f}", flush=True)  # fmt: skip
    points = list(sols)
    front = [points[i] for i in pareto(points)]
    print(f"\n   {len(W_SITE) * len(W_FLOOD)} weightings gave {len(points)} different solutions, "
          f"{len(front)} of them Pareto optimal among these")  # fmt: skip
    for c, s, f in sorted(front, key=lambda p: (p[1], p[2])):
        print(f"      {s:>3} sites, {c:>8,} people ({c / pop.sum():.1%}), flood {f:>3}  "
              f"from weights {sols[(c, s, f)][:3]}")  # fmt: skip

    fig, ax = plt.subplots(figsize=(7, 5))
    arr = np.array(points, dtype=float)
    sc = ax.scatter(arr[:, 1], arr[:, 0] / pop.sum(), c=arr[:, 2], cmap="viridis_r", s=60)
    fa = np.array(front, dtype=float)
    ax.scatter(fa[:, 1], fa[:, 0] / pop.sum(), facecolors="none", edgecolors="red", s=140,
               label="Pareto optimal")  # fmt: skip
    ax.set_xlabel("sites opened")
    ax.set_ylabel("share of people within 400 m")
    ax.legend()
    fig.colorbar(sc, ax=ax, label="flood rank summed over sites")
    fig.savefig(OUT / "weighted-sum-taito.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 6))
    sc = ax.scatter(site_xy[:, 0], site_xy[:, 1], c=flood, cmap="Blues", vmin=-0.5, vmax=4,
                    edgecolors="grey", linewidths=0.3, s=25)  # fmt: skip
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_title("taito: candidate sites by maximum-scale flood depth rank (A31a)")
    fig.colorbar(sc, ax=ax, label="rank (0 outside)", shrink=0.6)
    fig.savefig(OUT / "flood-rank-taito.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")


if __name__ == "__main__":
    main()
