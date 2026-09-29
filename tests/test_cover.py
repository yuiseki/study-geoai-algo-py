import numpy as np
import pytest

from study_geoai import cover, graph

# Six demand points and three candidates. A covers 1 to 4, B covers 1, 2 and 5,
# C covers 3, 4 and 6. Greedy takes A first (4) and then B or C (+1.5) for 5.5;
# the best pair is B and C, covering everything for 7.
POP = np.array([1.0, 1.0, 1.0, 1.0, 1.5, 1.5])
SETS = [np.array([0, 1, 2, 3]), np.array([0, 1, 4]), np.array([2, 3, 5])]


def test_greedy_falls_into_the_trap():
    chosen, covered = cover.greedy(SETS, POP, 2)
    assert chosen[0] == 0 and covered == pytest.approx(5.5)


def test_milp_finds_the_best_pair():
    r = cover.solve(SETS, POP, 2, integer=True)
    assert r["objective"] == pytest.approx(7.0)
    assert sorted(np.flatnonzero(r["x"] > 0.5).tolist()) == [1, 2]


def test_lp_bounds_the_milp():
    lp = cover.solve(SETS, POP, 1, integer=False)
    ip = cover.solve(SETS, POP, 1, integer=True)
    assert lp["objective"] >= ip["objective"] - 1e-9
    assert ip["objective"] == pytest.approx(4.0)


def test_dual_of_k_is_the_slope_of_the_lp_optimum():
    # the LP optimum is a concave, piecewise linear function of k; away from a
    # break its slope is the dual price of the constraint sum(x) = k
    k, h = 1.5, 0.01
    lp = cover.solve(SETS, POP, k, integer=False)
    slope = (cover.solve(SETS, POP, k + h, integer=False)["objective"]
             - cover.solve(SETS, POP, k - h, integer=False)["objective"]) / (2 * h)  # fmt: skip
    assert lp["dual_k"] == pytest.approx(slope, abs=1e-6)


def test_ortools_agrees_with_highs():
    for integer in (False, True):
        a = cover.solve(SETS, POP, 2, integer=integer)
        b = cover.solve_ortools(SETS, POP, 2, integer=integer)
        assert a["objective"] == pytest.approx(b["objective"])


def test_coverage_by_walking_distance():
    # a path of five nodes 100 m apart; demand sits on every node
    g = graph.build([(i * 100.0, 0.0, (i + 1) * 100.0, 0.0, 100.0) for i in range(4)])
    nodes = [g.node((i * 100.0, 0.0)) for i in range(5)]
    sets = cover.coverage(g, [nodes[0], nodes[2]], np.array(nodes), 150.0)
    assert sets[0].tolist() == [0, 1]
    assert sets[1].tolist() == [1, 2, 3]


def test_dijkstra_limit_stops_early():
    g = graph.build([(i * 100.0, 0.0, (i + 1) * 100.0, 0.0, 100.0) for i in range(9)])
    dist, _, settled = graph.dijkstra(g, [g.node((0.0, 0.0))], limit=250.0)
    assert settled == 3
    assert np.isfinite(dist[:3]).all() and dist[3] == pytest.approx(300.0)


def test_merging_identical_rows_keeps_the_optimum():
    # cells 0 and 1 are covered by A and B only, cells 2 and 3 by A and C only
    sets, pop = cover.merge_identical(SETS, POP)
    assert len(pop) == 4 and pop.sum() == pytest.approx(POP.sum())
    for integer in (False, True):
        a = cover.solve(sets, pop, 2, integer=integer)
        b = cover.solve(SETS, POP, 2, integer=integer)
        assert a["objective"] == pytest.approx(b["objective"])


def test_interior_point_gives_the_same_lp():
    a = cover.solve(SETS, POP, 1.5, integer=False, lp_solver="ipm")
    b = cover.solve(SETS, POP, 1.5, integer=False, lp_solver="simplex")
    assert a["objective"] == pytest.approx(b["objective"], rel=1e-6)
