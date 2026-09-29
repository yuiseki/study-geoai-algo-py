"""Maximal covering location: choose k sites to cover as much demand as possible.

A demand point i (weight p_i) is covered when a chosen site lies within the
radius. With x_j = 1 for a chosen site and y_i = 1 for a covered point:

    maximise    sum_i p_i y_i
    subject to  y_i <= sum_{j covers i} x_j     for every i
                sum_j x_j = k
                0 <= x, y <= 1, and x integer for the MILP

y may stay continuous even in the MILP: with x integer, y_i = 1 exactly when
some chosen site covers i. Relaxing x as well gives the LP, an upper bound.
"""

import time

import highspy
import numpy as np
from ortools.linear_solver import pywraplp
from scipy.sparse import csc_matrix

from study_geoai import graph


def coverage(g: graph.Graph, candidates, demand_nodes: np.ndarray, radius: float) -> list:
    """For each candidate node, the indices of demand points within radius along g."""
    by_node: dict[int, list[int]] = {}
    for i, n in enumerate(demand_nodes.tolist()):
        by_node.setdefault(n, []).append(i)
    sets = []
    for c in candidates:
        trace: list[int] = []
        graph.dijkstra(g, [c], trace=trace, limit=radius)
        sets.append(np.array(sorted(i for n in trace for i in by_node.get(n, [])), dtype=np.int64))
    return sets


def greedy(sets, pop: np.ndarray, k: int):
    """Take, k times, the site adding the most uncovered demand. Returns (chosen, covered)."""
    covered = np.zeros(len(pop), dtype=bool)
    chosen = []
    for _ in range(k):
        gains = [pop[s[~covered[s]]].sum() if j not in chosen else -1.0
                 for j, s in enumerate(sets)]  # fmt: skip
        j = int(np.argmax(gains))
        chosen.append(j)
        covered[sets[j]] = True
    return chosen, float(pop[covered].sum())


def merge_identical(sets, pop: np.ndarray):
    """Merge demand points covered by exactly the same candidates into one row with
    their summed weight, and drop points no candidate covers. The optimum is
    unchanged; the model shrinks. Returns (sets, pop) over the merged rows."""
    cand_of: list[list[int]] = [[] for _ in pop]
    for j, st in enumerate(sets):
        for i in st.tolist():
            cand_of[i].append(j)
    groups: dict[tuple, list[int]] = {}
    for i, js in enumerate(cand_of):
        if js:
            groups.setdefault(tuple(js), []).append(i)
    keys = list(groups)
    merged: list[list[int]] = [[] for _ in sets]
    for r, key in enumerate(keys):
        for j in key:
            merged[j].append(r)
    weights = np.array([pop[groups[key]].sum() for key in keys], dtype=float)
    return [np.array(m, dtype=np.int64) for m in merged], weights


def _matrix(sets, n_demand):
    """Constraint rows: y_i - sum x_j <= 0 for each demand, then sum x_j = k.
    Columns: x_0..x_{m-1}, then y_0..y_{n-1}."""
    m = len(sets)
    rows, cols, vals = [], [], []
    for j, s in enumerate(sets):
        rows += s.tolist()
        cols += [j] * len(s)
        vals += [-1.0] * len(s)
    rows += list(range(n_demand))
    cols += list(range(m, m + n_demand))
    vals += [1.0] * n_demand
    rows += [n_demand] * m
    cols += list(range(m))
    vals += [1.0] * m
    return csc_matrix((vals, (rows, cols)), shape=(n_demand + 1, m + n_demand))


def solve(sets, pop: np.ndarray, k: float, integer: bool, time_limit: float = 60.0,
          lp_solver: str = "choose") -> dict:  # fmt: skip
    """Solve with HiGHS. Returns objective, x, y, seconds, status, and dual_k (LP only:
    the extra covered demand per extra site) or mip_gap and nodes (MILP only).

    lp_solver is HiGHS's solver option for the LP: "choose" (simplex here),
    "simplex" or "ipm" (interior point, much faster on the large covering LPs)."""
    m, n = len(sets), len(pop)
    a = _matrix(sets, n)
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = m + n, n + 1
    lp.col_cost_ = np.concatenate([np.zeros(m), -pop]).astype(float)  # HiGHS minimises
    lp.col_lower_ = np.zeros(m + n)
    lp.col_upper_ = np.ones(m + n)
    lp.row_lower_ = np.concatenate([np.full(n, -highspy.kHighsInf), [k]])
    lp.row_upper_ = np.concatenate([np.zeros(n), [k]])
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = a.indptr
    lp.a_matrix_.index_ = a.indices
    lp.a_matrix_.value_ = a.data
    if integer:
        lp.integrality_ = [highspy.HighsVarType.kInteger] * m + [
            highspy.HighsVarType.kContinuous
        ] * n
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", float(time_limit))
    if not integer:
        h.setOptionValue("solver", lp_solver)
    h.passModel(lp)
    t = time.perf_counter()
    h.run()
    seconds = time.perf_counter() - t
    sol, info = h.getSolution(), h.getInfo()
    col = np.array(sol.col_value)
    out = {"objective": -info.objective_function_value, "x": col[:m], "y": col[m:],
           "seconds": seconds, "status": h.modelStatusToString(h.getModelStatus())}  # fmt: skip
    if integer:
        out["mip_gap"] = info.mip_gap
        out["nodes"] = info.mip_node_count
    else:
        out["dual_k"] = -np.array(sol.row_dual)[-1]  # sign flips with the minimisation
    return out


def solve_ortools(sets, pop: np.ndarray, k: float, integer: bool) -> dict:
    """The same model through OR-Tools: SCIP for the MILP, GLOP for the LP."""
    s = pywraplp.Solver.CreateSolver("SCIP" if integer else "GLOP")
    x = [s.IntVar(0, 1, f"x{j}") if integer else s.NumVar(0, 1, f"x{j}") for j in range(len(sets))]
    y = [s.NumVar(0, 1, f"y{i}") for i in range(len(pop))]
    covers: list[list[int]] = [[] for _ in pop]
    for j, st in enumerate(sets):
        for i in st.tolist():
            covers[i].append(j)
    for i, js in enumerate(covers):
        s.Add(y[i] <= sum(x[j] for j in js))
    s.Add(sum(x) == k)
    s.Maximize(sum(float(p) * yi for p, yi in zip(pop, y, strict=True)))
    t = time.perf_counter()
    s.Solve()
    return {"objective": s.Objective().Value(), "seconds": time.perf_counter() - t,
            "x": np.array([v.solution_value() for v in x])}  # fmt: skip
