"""Step 8B: maximal covering as a MILP, against its LP and greedy, and at scale.

1. Taito City, the instance of step 8A (walking distance): the integer optimum
   for k = 1 to 20, the integrality gap to the LP, how far greedy falls short,
   branch-and-bound nodes and time; HiGHS checked against SCIP.
2. The 23 wards, with straight-line coverage (a walking Dijkstra from each of
   some 20,000 candidates in Python would take tens of minutes, and the point
   here is the solver): solve time as the number of candidates and k grow.
   Demand cells covered by the same candidates are merged, and the LP is solved
   by interior point; where the MILP cannot finish, greedy against the LP bound
   still bounds how far greedy is from the optimum.

    uv run python src/008-B-milp/run.py
"""

import importlib.util
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from study_geoai import aoi, cover, features, ksj, worldpop
from study_geoai.db import connect

OUT = Path(__file__).parent / "output"
RADIUS = 400.0
TIME_LIMIT = 120.0
_spec = importlib.util.spec_from_file_location(
    "step8a", Path(__file__).parents[1] / "008-A-lp" / "run.py"
)
step8a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step8a)


def taito(con):
    _, _, pop, _, _, sets = step8a.instance(con, "taito")
    print(f"## taito (walking {RADIUS:.0f} m): {len(pop):,} cells, {len(sets)} candidates")
    print("    k        LP       MILP   greedy   LP/MILP-1   MILP/greedy-1   nodes   seconds")
    for k in range(1, 21):
        lp = cover.solve(sets, pop, k, integer=False)
        ip = cover.solve(sets, pop, k, integer=True, time_limit=TIME_LIMIT)
        _, gre = cover.greedy(sets, pop, k)
        print(f"   {k:>2}  {lp['objective']:>8,.0f}  {ip['objective']:>9,.0f}  {gre:>7,.0f}"
              f"  {lp['objective'] / ip['objective'] - 1:>10.4f}  {ip['objective'] / gre - 1:>14.4f}"
              f"  {ip['nodes']:>6}  {ip['seconds']:>8.2f}   {ip['status']}")  # fmt: skip
    for k in (10, 20):
        a = cover.solve(sets, pop, k, integer=True)
        b = cover.solve_ortools(sets, pop, k, integer=True)
        print(f"   k = {k}: HiGHS {a['objective']:,.1f} in {a['seconds']:.2f} s; "
              f"SCIP {b['objective']:,.1f} in {b['seconds']:.2f} s")  # fmt: skip


def tokyo23(con):
    area = aoi.load("tokyo23", con)
    cells = worldpop.grid(con, area, step8a.YEAR).query(
        "w", f"""select lon, lat, population from w
                 where population > 0 and st_intersects(geometry, st_geomfromtext('{area.wkt}'))"""
    ).fetchall()  # fmt: skip
    demand = features.to_metric(con, [c[:2] for c in cells])
    pop = np.array([c[2] for c in cells])
    sites = []
    for dataset in ("P04", "P29"):
        sites += (
            ksj.read(con, area, dataset)
            .query("s", "select st_x(geometry), st_y(geometry) from s")
            .fetchall()
        )
    site_xy = features.to_metric(con, sites)
    tree = cKDTree(demand)
    all_sets = [np.array(sorted(s), dtype=np.int64)
                for s in tree.query_ball_point(site_xy, RADIUS)]  # fmt: skip
    print(f"\n## tokyo23 (straight line {RADIUS:.0f} m): {len(pop):,} cells, "
          f"{pop.sum():,.0f} people, {len(all_sets):,} candidates")  # fmt: skip
    print(f"   time limit {TIME_LIMIT:.0f} s per solve; demand cells covered by the same "
          "candidates are merged into one row; the LP is solved by interior point")  # fmt: skip
    print(
        "   candidates     k     rows       LP (s)          MILP (s, nodes)       greedy"
        "   MILP/greedy-1   LP/greedy-1"
    )
    rng = np.random.default_rng(0)
    runs = [(n, 50) for n in (500, 1000, 2000, 5000, 10000)] + [
        (len(all_sets), k) for k in (10, 50, 200)
    ]
    for n, k in runs:
        pick = np.sort(rng.choice(len(all_sets), n, replace=False)) if n < len(all_sets) else None
        sets = [all_sets[j] for j in pick] if pick is not None else all_sets
        sets, p = cover.merge_identical(sets, pop)
        lp = cover.solve(sets, p, k, integer=False, time_limit=TIME_LIMIT, lp_solver="ipm")
        ip = cover.solve(sets, p, k, integer=True, time_limit=TIME_LIMIT)
        _, gre = cover.greedy(sets, p, k)
        lp_ok, ip_ok = lp["status"] == "Optimal", ip["status"] == "Optimal"
        lp_txt = (
            f"{lp['objective']:>9,.0f} ({lp['seconds']:>5.1f})"
            if lp_ok
            else f"{'-':>9} ({lp['status']})"
        )
        ip_txt = (
            f"{ip['objective']:>9,.0f} ({ip['seconds']:>5.1f}, {ip['nodes']})"
            if ip_ok
            else f"{'-':>9} ({ip['status']}, {ip['seconds']:.0f} s)"
        )
        print(f"   {n:>10,}  {k:>4}  {len(p):>7,}  {lp_txt}  {ip_txt:>22}  {gre:>11,.0f}"
              f"  {(ip['objective'] / gre - 1) if ip_ok else float('nan'):>14.4f}"
              f"  {(lp['objective'] / gre - 1) if lp_ok else float('nan'):>12.4f}")  # fmt: skip


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    taito(con)
    tokyo23(con)


if __name__ == "__main__":
    main()
