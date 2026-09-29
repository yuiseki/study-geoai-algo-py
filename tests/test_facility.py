import numpy as np
import pytest

from study_geoai import facility

# three areas on a line at 0, 10 and 20; two shelters at 0 and 20
DIST = np.array([[0.0, 20.0], [10.0, 10.0], [20.0, 0.0]])


def test_nearest_ignores_capacity():
    load = facility.nearest_load(DIST, np.array([5, 5, 5]), n_sites=2)
    assert load.sum() == 15 and load.max() >= 7  # the middle area goes wholly to one site


def test_transport_respects_capacity_and_is_integral():
    demand, cap = np.array([5, 4, 5]), np.array([6, 9])
    r = facility.transport(DIST, demand, cap)
    flow = r["flow"]
    assert np.allclose(flow.sum(axis=1), demand)
    assert np.all(flow.sum(axis=0) <= cap + 1e-9)
    assert np.allclose(flow, np.round(flow))  # integer data, so the LP vertex is integral
    # the end areas sit on their sites; the middle area pays 10 a head either way
    assert r["cost"] == pytest.approx(0 * 5 + 10 * 1 + 10 * 3 + 0 * 5)


def test_single_source_costs_at_least_the_transport():
    demand, cap = np.array([5, 4, 5]), np.array([6, 9])
    split = facility.transport(DIST, demand, cap)
    single = facility.transport(DIST, demand, cap, single_source=True)
    assert single["cost"] >= split["cost"] - 1e-9
    assert np.all((single["flow"] == 0) | np.isclose(single["flow"], demand[:, None]))


def test_hungarian_on_seats_equals_transport():
    demand, cap = np.array([5, 4, 5]), np.array([6, 9])
    assert facility.hungarian_seats(DIST, demand, cap) == pytest.approx(
        facility.transport(DIST, demand, cap)["cost"]
    )


def test_transport_reports_infeasible():
    r = facility.transport(DIST, np.array([5, 5, 5]), np.array([3, 3]))
    assert r["status"] != "Optimal"


def test_p_median_exact_and_heuristics():
    rng = np.random.default_rng(0)
    pts, sites = rng.uniform(0, 100, (40, 2)), rng.uniform(0, 100, (15, 2))
    dist = np.hypot(*(pts[:, None, :] - sites[None, :, :]).transpose(2, 0, 1))
    w = rng.integers(1, 10, 40).astype(float)
    exact = facility.p_median(dist, w, 3)
    lp = facility.p_median(dist, w, 3, integer=False)
    chosen, cost = facility.greedy_median(dist, w, 3)
    swapped, cost2 = facility.interchange(dist, w, chosen)
    assert lp["cost"] <= exact["cost"] + 1e-6
    assert exact["cost"] <= cost2 + 1e-6 <= cost + 1e-6
    assert len(exact["open"]) == 3
    assert facility.median_cost(dist, w, exact["open"]) == pytest.approx(exact["cost"])
