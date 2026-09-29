"""Assignment and facility location on a distance matrix dist[area, site].

- transport: send each area's demand to sites without exceeding their capacity,
  at least total distance. With integer demand and capacity the LP's optimum is
  already integral (the constraint matrix is totally unimodular), so no MILP is
  needed; single_source=True forbids splitting an area and does need one.
- hungarian_seats: the same problem as a classic one-to-one assignment, one
  row per person and one column per seat, solved by scipy's linear_sum_assignment.
- p_median: open p sites, send every area to an open site, least weighted distance.

The LPs and MILPs go through scipy.optimize.milp, which calls HiGHS.
"""

import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linear_sum_assignment, milp
from scipy.sparse import coo_matrix, hstack


def nearest_load(dist: np.ndarray, demand: np.ndarray, n_sites: int) -> np.ndarray:
    """Demand each site gets when every area goes to its nearest site."""
    return np.bincount(dist.argmin(axis=1), weights=demand, minlength=n_sites)


def _solve(c, constraints, integrality, ub=None):
    t = time.perf_counter()
    r = milp(c, constraints=constraints, integrality=integrality,
             bounds=Bounds(0, np.inf if ub is None else ub))  # fmt: skip
    status = "Optimal" if r.status == 0 else r.message
    return r, status, time.perf_counter() - t


def transport(dist, demand, cap, single_source=False) -> dict:
    """Variables f[i, j] (people of area i at site j), flattened row by row."""
    n, m = dist.shape
    rows = np.repeat(np.arange(n), m)
    cols = np.arange(n * m)
    each_area = coo_matrix((np.ones(n * m), (rows, cols)), shape=(n, n * m))
    each_site = coo_matrix((np.ones(n * m), (np.tile(np.arange(m), n), cols)), shape=(m, n * m))
    if not single_source:
        cons = [LinearConstraint(each_area, demand, demand), LinearConstraint(each_site, 0, cap)]
        r, status, sec = _solve(dist.ravel(), cons, np.zeros(n * m))
        flow = r.x.reshape(n, m) if r.x is not None else None
    else:
        # z[i, j] = 1 when area i goes wholly to site j; flow = demand_i z[i, j]
        weighted = coo_matrix((np.repeat(demand, m).astype(float), (np.tile(np.arange(m), n), cols)),
                              shape=(m, n * m))  # fmt: skip
        cons = [LinearConstraint(each_area, 1, 1), LinearConstraint(weighted, 0, cap)]
        cost = (dist * demand[:, None]).ravel()
        r, status, sec = _solve(cost, cons, np.ones(n * m), ub=1)
        flow = (r.x.reshape(n, m) * demand[:, None]) if r.x is not None else None
    cost = float((dist * flow).sum()) if flow is not None else np.inf
    return {"flow": flow, "cost": cost, "status": status, "seconds": sec}


def hungarian_seats(dist, demand, cap) -> float:
    """One row per person, one column per seat; returns the least total distance."""
    people = np.repeat(np.arange(len(demand)), demand.astype(int))
    seats = np.repeat(np.arange(len(cap)), cap.astype(int))
    rows, cols = linear_sum_assignment(dist[people][:, seats])
    return float(dist[people[rows], seats[cols]].sum())


def median_cost(dist, w, open_sites) -> float:
    return float((w * dist[:, list(open_sites)].min(axis=1)).sum())


def p_median(dist, w, p, integer=True) -> dict:
    """x[i, j] (area i served by site j) flattened, then y[j] (site j open)."""
    n, m = dist.shape
    nm = n * m
    cols = np.arange(nm)
    assign = coo_matrix((np.ones(nm), (np.repeat(np.arange(n), m), cols)), shape=(n, nm + m))
    # x[i, j] - y[j] <= 0
    link = hstack([coo_matrix((np.ones(nm), (cols, cols)), shape=(nm, nm)),
                   coo_matrix((-np.ones(nm), (cols, np.tile(np.arange(m), n))), shape=(nm, m))])  # fmt: skip
    count = coo_matrix((np.ones(m), (np.zeros(m), np.arange(nm, nm + m))), shape=(1, nm + m))
    cons = [LinearConstraint(assign, 1, 1), LinearConstraint(link, -np.inf, 0),
            LinearConstraint(count, p, p)]  # fmt: skip
    c = np.concatenate([(dist * w[:, None]).ravel(), np.zeros(m)])
    integrality = np.concatenate([np.zeros(nm), np.full(m, 1 if integer else 0)])
    r, status, sec = _solve(c, cons, integrality, ub=1)
    y = r.x[nm:] if r.x is not None else np.zeros(m)
    return {"cost": float(r.fun) if r.x is not None else np.inf, "y": y,
            "open": np.flatnonzero(y > 0.5).tolist(), "status": status, "seconds": sec}  # fmt: skip


def greedy_median(dist, w, p):
    """Open, p times, the site that lowers the weighted distance the most."""
    chosen: list[int] = []
    best = np.full(len(w), np.inf)
    for _ in range(p):
        costs = (w[:, None] * np.minimum(best[:, None], dist)).sum(axis=0)
        costs[chosen] = np.inf
        j = int(np.argmin(costs))
        chosen.append(j)
        best = np.minimum(best, dist[:, j])
    return chosen, float((w * best).sum())


def interchange(dist, w, chosen):
    """Teitz and Bart: swap an open site for a closed one while that lowers the cost."""
    chosen = list(chosen)
    cost = median_cost(dist, w, chosen)
    improved = True
    while improved:
        improved = False
        for a in range(len(chosen)):
            for j in range(dist.shape[1]):
                if j in chosen:
                    continue
                trial = chosen[:a] + [j] + chosen[a + 1 :]
                c = median_cost(dist, w, trial)
                if c < cost - 1e-9:
                    chosen, cost, improved = trial, c, True
    return chosen, cost
