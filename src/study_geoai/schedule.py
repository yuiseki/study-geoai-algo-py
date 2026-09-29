"""Vehicle and crew scheduling for bus trips, with OR-Tools CP-SAT.

A trip is a timetabled run from an origin to a destination. One vehicle can do
trip b after trip a when it can get from a's destination to b's origin in time:
a layover at the terminal plus, if the terminals differ, an empty run (deadhead)
at a fixed speed. These pairs are the arcs of an acyclic graph.

- Fewest vehicles: every trip has at most one next trip and at most one previous
  trip on the same vehicle; each chain is one vehicle, so the fleet is the
  number of trips minus the number of arcs used. CP-SAT maximises the arcs; the
  same number comes from a maximum bipartite matching (minimum path cover), and
  the peak number of trips running at once is a lower bound.
- Crew: drivers take trips (not vehicles) with a break of break_len, at most
  max_piece of work on each side of it and at most max_span from first to last.
"""

from dataclasses import dataclass

import numpy as np
from ortools.sat.python import cp_model
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching


@dataclass
class Trips:
    ids: list
    start: np.ndarray  # seconds after midnight (may pass 24 h)
    end: np.ndarray
    origin: np.ndarray  # (n, 2) metres
    dest: np.ndarray


def gtfs_trips(con, feed: str, services: list[str]) -> Trips:
    """Trips of the given service_ids from a feed of study_geoai.gtfs, with the
    first departure, last arrival and the first and last stops in METRIC_CRS."""
    from study_geoai import features, gtfs

    gtfs.load(con, feed)
    svc = ", ".join(f"'{s}'" for s in services)
    rows = con.sql(f"""
        with st as (
            select trip_id, stop_id, cast(stop_sequence as integer) as seq,
                   {gtfs.seconds("departure_time")} as dep, {gtfs.seconds("arrival_time")} as arr
            from {feed}.stop_times
        ),
        ends as (
            select trip_id, arg_min(stop_id, seq) as o, arg_max(stop_id, seq) as d,
                   min(dep) as t0, max(arr) as t1
            from st group by trip_id
        )
        select e.trip_id, e.t0, e.t1, cast(so.stop_lon as double), cast(so.stop_lat as double),
               cast(sd.stop_lon as double), cast(sd.stop_lat as double)
        from ends e join {feed}.trips t using (trip_id)
        join {feed}.stops so on so.stop_id = e.o join {feed}.stops sd on sd.stop_id = e.d
        where t.service_id in ({svc})
        order by e.t0, e.trip_id
    """).fetchall()
    xy = features.to_metric(con, [r[3:5] for r in rows] + [r[5:7] for r in rows])
    n = len(rows)
    return Trips([r[0] for r in rows], np.array([r[1] for r in rows], float),
                 np.array([r[2] for r in rows], float), xy[:n], xy[n:])  # fmt: skip


def connections(t: Trips, layover: float, speed_kmh: float) -> set:
    """Pairs (a, b) that one vehicle can run in that order."""
    gap = np.hypot(*(t.dest[:, None, :] - t.origin[None, :, :]).transpose(2, 0, 1))
    deadhead = gap / (speed_kmh / 3.6)
    ok = t.start[None, :] >= t.end[:, None] + layover + deadhead
    np.fill_diagonal(ok, False)
    return {(int(a), int(b)) for a, b in zip(*np.nonzero(ok), strict=True)}


def peak(t: Trips) -> int:
    """Most trips running at the same moment (a lower bound on the fleet)."""
    events = sorted([(s, 1) for s in t.start] + [(e, -1) for e in t.end])  # ends sort first
    run = best = 0
    for _, step in events:
        run += step
        best = max(best, run)
    return best


def min_fleet_matching(n: int, arcs: set) -> int:
    """n minus a maximum matching of 'a before b' pairs: a minimum path cover."""
    if not arcs:
        return n
    a, b = zip(*arcs, strict=True)
    m = csr_matrix((np.ones(len(a)), (a, b)), shape=(n, n))
    match = maximum_bipartite_matching(m, perm_type="column")
    return n - int((match >= 0).sum())


def _blocks(n, used):
    nxt = dict(used)
    has_prev = {b for _, b in used}
    blocks = []
    for s in range(n):
        if s in has_prev:
            continue
        chain = [s]
        while chain[-1] in nxt:
            chain.append(nxt[chain[-1]])
        blocks.append(chain)
    return blocks


def min_fleet_cpsat(t: Trips, arcs: set, second_stage=False, time_limit=60.0) -> dict:
    """Fewest vehicles; with second_stage, then least idle time between trips
    (the time from one trip's end to the next trip's start) at that fleet."""
    n = len(t.ids)
    arcs = sorted(arcs)
    model = cp_model.CpModel()
    x = {a: model.NewBoolVar(f"x{a}") for a in arcs}
    for i in range(n):
        model.AddAtMostOne(x[a] for a in arcs if a[0] == i)
        model.AddAtMostOne(x[a] for a in arcs if a[1] == i)
    model.Maximize(sum(x.values()))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8
    status = solver.Solve(model)
    used_n = int(round(solver.ObjectiveValue()))
    seconds = solver.WallTime()
    if second_stage:
        model.Add(sum(x.values()) == used_n)
        idle = {a: int(t.start[a[1]] - t.end[a[0]]) for a in arcs}
        model.Minimize(sum(idle[a] * x[a] for a in arcs))
        status = solver.Solve(model)
        seconds += solver.WallTime()
    used = [a for a in arcs if solver.Value(x[a])]
    return {"vehicles": n - len(used), "blocks": _blocks(n, used), "status": solver.StatusName(status),
            "idle": float(sum(t.start[b] - t.end[a] for a, b in used)), "seconds": seconds}  # fmt: skip


@dataclass
class CrewRules:
    max_piece: float  # longest stretch of work without a break (s)
    break_len: float  # the one break each driver takes (s)
    max_span: float  # first start to last end (s)


def crew_cpsat(t: Trips, arcs: set, rules: CrewRules, max_drivers: int, time_limit=60.0) -> dict:
    """Fewest drivers. Each driver d has trips assign[i, d] that are pairwise
    runnable in time order (the arcs, taken transitively as pairs), one break
    interval that no trip of theirs overlaps, and limits on span and pieces."""
    n = len(t.ids)
    compatible = set(arcs) | {(b, a) for a, b in arcs}
    horizon = int(t.end.max() + rules.break_len + 1)
    model = cp_model.CpModel()
    assign = {(i, d): model.NewBoolVar(f"a{i}_{d}") for i in range(n) for d in range(max_drivers)}
    used = [model.NewBoolVar(f"u{d}") for d in range(max_drivers)]
    for i in range(n):
        model.AddExactlyOne(assign[i, d] for d in range(max_drivers))
    duties = []
    for d in range(max_drivers):
        for i in range(n):
            model.AddImplication(assign[i, d], used[d])
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) not in compatible:
                    model.AddBoolOr([assign[i, d].Not(), assign[j, d].Not()])
        first = model.NewIntVar(0, horizon, f"f{d}")
        last = model.NewIntVar(0, horizon, f"l{d}")
        bstart = model.NewIntVar(0, horizon, f"b{d}")
        brk = model.NewFixedSizeIntervalVar(bstart, int(rules.break_len), f"br{d}")
        work = []
        for i in range(n):
            s, e = int(t.start[i]), int(t.end[i])
            model.Add(first <= s).OnlyEnforceIf(assign[i, d])
            model.Add(last >= e).OnlyEnforceIf(assign[i, d])
            work.append(model.NewOptionalFixedSizeIntervalVar(s, e - s, assign[i, d], f"w{i}_{d}"))
            # a trip before the break ends within max_piece of the first start;
            # a trip after it starts within max_piece of the last end
            # only the driver's own trips have to keep clear of the break: another
            # driver may run the bus while this one rests
            before = model.NewBoolVar(f"bf{i}_{d}")
            model.Add(e <= bstart).OnlyEnforceIf([assign[i, d], before])
            model.Add(s >= bstart + int(rules.break_len)).OnlyEnforceIf(
                [assign[i, d], before.Not()]
            )
            model.Add(e - first <= int(rules.max_piece)).OnlyEnforceIf([assign[i, d], before])
            model.Add(last - s <= int(rules.max_piece)).OnlyEnforceIf([assign[i, d], before.Not()])
        model.AddNoOverlap([*work, brk])
        model.Add(last - first <= int(rules.max_span))
        duties.append((first, last, bstart))
    # drivers are interchangeable, so number them by their first trip: the trip
    # that is k-th by start time can only go to drivers 0..k. This removes
    # relabelled copies of the same solution and keeps the optimum.
    rank = np.empty(n, dtype=int)
    rank[np.argsort(t.start, kind="stable")] = np.arange(n)
    for i in range(n):
        for d in range(rank[i] + 1, max_drivers):
            model.Add(assign[i, d] == 0)
    for d in range(max_drivers - 1):
        model.AddImplication(used[d + 1], used[d])
    model.Minimize(sum(used))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8
    status = solver.Solve(model)
    out = {"status": solver.StatusName(status), "seconds": solver.WallTime(), "duties": []}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for d in range(max_drivers):
            ts = [i for i in range(n) if solver.Value(assign[i, d])]
            if ts:
                b = solver.Value(duties[d][2])
                out["duties"].append({"trips": ts, "break": (b, b + rules.break_len)})
        out["drivers"] = len(out["duties"])
        out["bound"] = solver.BestObjectiveBound()
    return out
