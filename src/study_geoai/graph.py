"""A small undirected road graph with hand-written Dijkstra and A*.

Written by hand, not taken from networkx, so the search can be counted: every
function returns how many nodes it settled (took off the heap for good). The
tests check the answers against networkx.

Edges are (x1, y1, x2, y2, length) in metres; two edges meet where they share
an end point exactly, which is how OSM ways meet at a shared node.
"""

import heapq
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree


@dataclass
class Graph:
    xy: np.ndarray  # (n, 2) node coordinates in metres
    indptr: np.ndarray  # CSR adjacency: neighbours of u are indices[indptr[u]:indptr[u + 1]]
    indices: np.ndarray
    weights: np.ndarray
    _index: dict

    @property
    def n_nodes(self) -> int:
        return len(self.xy)

    def node(self, xy: tuple[float, float]) -> int:
        return self._index[(float(xy[0]), float(xy[1]))]

    def neighbours(self, u: int):
        lo, hi = self.indptr[u], self.indptr[u + 1]
        return zip(self.indices[lo:hi].tolist(), self.weights[lo:hi].tolist(), strict=True)

    def weight(self, u: int, v: int) -> float:
        return min(w for x, w in self.neighbours(u) if x == v)


def build(edges) -> Graph:
    index: dict = {}

    def node(x, y):
        key = (float(x), float(y))
        if key not in index:
            index[key] = len(index)
        return index[key]

    src, dst, w = [], [], []
    for x1, y1, x2, y2, length in edges:
        a, b = node(x1, y1), node(x2, y2)
        if a == b:
            continue
        src += [a, b]
        dst += [b, a]
        w += [float(length), float(length)]
    n = len(index)
    # built by hand rather than with csr_matrix, which would sum parallel edges
    order = np.lexsort((np.array(dst), np.array(src)))
    src, dst, w = np.array(src)[order], np.array(dst)[order], np.array(w)[order]
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.add.at(indptr, src + 1, 1)
    indptr = np.cumsum(indptr)
    xy = np.array(list(index), dtype=float).reshape(-1, 2)
    return Graph(xy, indptr, dst.astype(np.int64), w, index)


def component_sizes(g: Graph) -> np.ndarray:
    """Sizes of the connected components, largest first."""
    return np.sort(np.bincount(component_labels(g)))[::-1]


def component_labels(g: Graph) -> np.ndarray:
    m = csr_matrix((np.ones(len(g.indices)), g.indices, g.indptr), shape=(g.n_nodes, g.n_nodes))
    return connected_components(m, directed=False)[1]


def dijkstra(g: Graph, sources, target=None, return_owner=False):
    """Distances from the nearest of sources; stops once target is settled.

    Returns (dist, pred, settled), or (dist, owner, settled) with return_owner,
    where owner is the source each node's distance comes from.
    """
    dist = np.full(g.n_nodes, np.inf)
    pred = np.full(g.n_nodes, -1, dtype=np.int64)
    owner = np.full(g.n_nodes, -1, dtype=np.int64)
    done = np.zeros(g.n_nodes, dtype=bool)
    heap = []
    for s in sources:
        dist[s], owner[s] = 0.0, s
        heap.append((0.0, int(s)))
    heapq.heapify(heap)
    settled = 0
    while heap:
        d, u = heapq.heappop(heap)
        if done[u]:
            continue
        done[u] = True
        settled += 1
        if u == target:
            break
        for v, w in g.neighbours(u):
            nd = d + w
            if nd < dist[v]:
                dist[v], pred[v], owner[v] = nd, u, owner[u]
                heapq.heappush(heap, (nd, v))
    return (dist, owner if return_owner else pred, settled)


def astar(g: Graph, source: int, target: int, inflation: float = 1.0):
    """A* with the straight-line distance to target as the heuristic.

    Straight-line distance never overestimates a path along edges whose length
    is at least the distance between their ends, so with inflation 1 the answer
    is exact. inflation > 1 searches less but may return a path up to
    inflation times the shortest. Returns (length, path, settled).
    """
    goal = g.xy[target]

    def h(u):
        return inflation * float(np.hypot(*(g.xy[u] - goal)))

    dist = {source: 0.0}
    pred = {source: -1}
    done = set()
    heap = [(h(source), source)]
    while heap:
        _, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        if u == target:
            break
        for v, w in g.neighbours(u):
            nd = dist[u] + w
            if nd < dist.get(v, np.inf):
                dist[v], pred[v] = nd, u
                heapq.heappush(heap, (nd + h(v), v))
    if target not in done:
        return np.inf, [], len(done)
    return dist[target], path(pred, target), len(done)


def path(pred, target: int) -> list[int]:
    """Nodes from the source to target, following predecessors (-1 ends)."""
    out = [target]
    while pred[out[-1]] != -1:
        out.append(int(pred[out[-1]]))
    return out[::-1]


def nearest(g: Graph, xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The nearest node to each point, and the straight-line gap to it in metres."""
    gap, idx = cKDTree(g.xy).query(xy)
    return idx, gap
