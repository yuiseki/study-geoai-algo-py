import networkx as nx
import numpy as np
import pytest

from study_geoai import graph


def grid(n=15, seed=0):
    """An n by n grid of points 10 m apart, with random extra length on each edge."""
    rng = np.random.default_rng(seed)
    edges = []
    for i in range(n):
        for j in range(n):
            for di, dj in ((1, 0), (0, 1)):
                if i + di < n and j + dj < n:
                    a, b = (i * 10.0, j * 10.0), ((i + di) * 10.0, (j + dj) * 10.0)
                    edges.append((*a, *b, 10.0 + rng.uniform(0, 5)))
    return edges


def test_nodes_are_shared_by_coordinates():
    g = graph.build([(0, 0, 1, 0, 1.0), (1, 0, 1, 1, 1.0), (5, 5, 6, 5, 1.0)])
    assert g.n_nodes == 5
    assert graph.component_sizes(g).tolist() == [3, 2]


def test_dijkstra_matches_networkx():
    edges = grid()
    g = graph.build(edges)
    ref = nx.Graph()
    for x1, y1, x2, y2, w in edges:
        ref.add_edge((x1, y1), (x2, y2), weight=w)
    source = g.node((0.0, 0.0))
    dist, _, settled = graph.dijkstra(g, [source])
    expected = nx.single_source_dijkstra_path_length(ref, (0.0, 0.0))
    for (x, y), d in expected.items():
        assert dist[g.node((x, y))] == pytest.approx(d)
    assert settled == g.n_nodes


def test_multi_source_gives_the_nearest_source():
    g = graph.build(grid())
    a, b = g.node((0.0, 0.0)), g.node((140.0, 140.0))
    both, owner, _ = graph.dijkstra(g, [a, b], return_owner=True)
    da, _, _ = graph.dijkstra(g, [a])
    db, _, _ = graph.dijkstra(g, [b])
    assert np.allclose(both, np.minimum(da, db))
    assert np.all(owner[da < db] == a) and np.all(owner[db < da] == b)
    assert set(owner[da == db].tolist()) <= {a, b}


def test_path_follows_predecessors():
    g = graph.build(grid())
    s, t = g.node((0.0, 0.0)), g.node((140.0, 70.0))
    dist, pred, _ = graph.dijkstra(g, [s])
    path = graph.path(pred, t)
    assert path[0] == s and path[-1] == t
    length = sum(g.weight(u, v) for u, v in zip(path, path[1:], strict=False))
    assert length == pytest.approx(dist[t])


def test_astar_is_exact_and_expands_fewer_nodes():
    g = graph.build(grid())
    s, t = g.node((0.0, 0.0)), g.node((140.0, 70.0))
    dist, _, _ = graph.dijkstra(g, [s])
    d_dij, _, n_dij = graph.dijkstra(g, [s], target=t)
    d_star, path, n_star = graph.astar(g, s, t)
    assert d_dij[t] == pytest.approx(dist[t])
    assert d_star == pytest.approx(dist[t])
    assert path[0] == s and path[-1] == t
    assert n_star < n_dij


def test_inflated_heuristic_is_never_shorter():
    g = graph.build(grid())
    s, t = g.node((0.0, 0.0)), g.node((140.0, 140.0))
    best, _, n_best = graph.astar(g, s, t)
    fast, _, n_fast = graph.astar(g, s, t, inflation=2.0)
    assert fast >= best - 1e-9
    assert fast <= 2.0 * best  # the bound weighted A* guarantees
    assert n_fast <= n_best


def test_nearest_node():
    g = graph.build(grid())
    idx, gap = graph.nearest(g, np.array([[1.0, 2.0], [139.0, 141.0]]))
    assert idx.tolist() == [g.node((0.0, 0.0)), g.node((140.0, 140.0))]
    assert gap == pytest.approx([np.hypot(1, 2), np.hypot(1, 1)])
