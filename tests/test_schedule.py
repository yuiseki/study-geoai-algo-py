import numpy as np
import pytest

from study_geoai import schedule

H = 3600


def trips(rows):
    """rows of (start, end, from_xy, to_xy) with times in hours."""
    return schedule.Trips(
        ids=[f"t{i}" for i in range(len(rows))],
        start=np.array([r[0] * H for r in rows], dtype=float),
        end=np.array([r[1] * H for r in rows], dtype=float),
        origin=np.array([r[2] for r in rows], dtype=float),
        dest=np.array([r[3] for r in rows], dtype=float),
    )


A, B = (0.0, 0.0), (6000.0, 0.0)  # two terminals 6 km apart

# a shuttle: A to B and back, every hour, 40 minutes a leg
SHUTTLE = trips([
    (6.0, 6 + 40 / 60, A, B), (7.0, 7 + 40 / 60, B, A),
    (6.5, 6.5 + 40 / 60, B, A), (7.5, 7.5 + 40 / 60, A, B),
    (8.0, 8 + 40 / 60, A, B),
])  # fmt: skip


def test_connections_need_time_to_reach_the_next_start():
    arcs = schedule.connections(SHUTTLE, layover=300, speed_kmh=15)
    # t0 ends at B at 6:40 and t1 leaves B at 7:00: fine (5 minutes layover, no deadhead)
    assert (0, 1) in arcs
    # t2 ends at A at 7:10, t3 leaves A at 7:30: fine; t2 cannot make t1 (B at 7:00)
    assert (2, 3) in arcs and (2, 1) not in arcs
    # never backwards in time
    assert all(SHUTTLE.start[b] >= SHUTTLE.end[a] for a, b in arcs)


def test_min_fleet_three_ways_agree():
    arcs = schedule.connections(SHUTTLE, layover=300, speed_kmh=15)
    by_matching = schedule.min_fleet_matching(len(SHUTTLE.ids), arcs)
    r = schedule.min_fleet_cpsat(SHUTTLE, arcs)
    assert r["vehicles"] == by_matching
    assert schedule.peak(SHUTTLE) <= by_matching
    blocks = r["blocks"]
    assert sorted(t for b in blocks for t in b) == list(range(len(SHUTTLE.ids)))
    for b in blocks:
        assert all((u, v) in arcs for u, v in zip(b, b[1:], strict=False))


def test_second_stage_keeps_the_fleet_and_cuts_idle_time():
    arcs = schedule.connections(SHUTTLE, layover=300, speed_kmh=15)
    one = schedule.min_fleet_cpsat(SHUTTLE, arcs)
    two = schedule.min_fleet_cpsat(SHUTTLE, arcs, second_stage=True)
    assert two["vehicles"] == one["vehicles"]
    assert two["idle"] <= one["idle"] + 1e-9


def test_crew_duties_respect_the_rules():
    # eleven hourly round trips of one bus: one driver cannot do them all
    rows = []
    for h in range(6, 17):
        rows += [(h, h + 25 / 60, A, B), (h + 0.5, h + 0.5 + 25 / 60, B, A)]
    day = trips(rows)
    arcs = schedule.connections(day, layover=180, speed_kmh=15)
    rules = schedule.CrewRules(max_piece=4.5 * H, break_len=45 * 60, max_span=9.5 * H)
    r = schedule.crew_cpsat(day, arcs, rules, max_drivers=6, time_limit=20)
    assert r["status"] in ("OPTIMAL", "FEASIBLE")
    covered = sorted(t for d in r["duties"] for t in d["trips"])
    assert covered == list(range(len(day.ids)))
    for d in r["duties"]:
        ts = d["trips"]
        first, last = day.start[ts].min(), day.end[ts].max()
        assert last - first <= rules.max_span + 1e-6
        b0, b1 = d["break"]
        assert b1 - b0 >= rules.break_len - 1e-6
        # no trip overlaps the break, and each side of it is at most max_piece
        assert all(day.end[t] <= b0 or day.start[t] >= b1 for t in ts)
        before = [t for t in ts if day.end[t] <= b0]
        after = [t for t in ts if day.start[t] >= b1]
        if before:
            assert day.end[before].max() - first <= rules.max_piece + 1e-6
        if after:
            assert last - day.start[after].min() <= rules.max_piece + 1e-6
    # the day is 11 hours long, longer than one span, so at least two drivers
    assert len(r["duties"]) >= 2
    assert r["drivers"] == len(r["duties"])
    assert r["drivers"] <= 3


def test_peak_counts_overlaps():
    assert schedule.peak(SHUTTLE) == 2
    assert schedule.peak(trips([(1, 2, A, A), (2, 3, A, A)])) == 1  # touching is not overlapping
    assert np.isclose(schedule.peak(trips([(1, 3, A, A), (2, 4, A, A), (2.5, 5, A, A)])), 3)


@pytest.mark.network
def test_arakawa_weekday_trips():
    from study_geoai.db import connect

    t = schedule.gtfs_trips(connect(), "arakawa", ["毎日", "平日"])
    assert len(t.ids) == 28
    assert (t.end > t.start).all()
    assert t.origin.shape == (28, 2)


def test_break_can_fall_while_another_driver_runs_the_bus():
    # one bus shuttles at one stop from 6:00 to 14:30: 27-minute trips, 3 minutes apart.
    # Driver A drives 6:00 to 10:00, breaks while B runs 10:00 to 10:30, then
    # drives 10:30 to 14:30: two drivers. A model that also keeps B's trip out
    # of A's break finds no break inside the day and needs three.
    rows = [(6 + k / 2, 6 + k / 2 + 27 / 60, A, A) for k in range(17)]
    day = trips(rows)
    arcs = schedule.connections(day, layover=180, speed_kmh=15)
    rules = schedule.CrewRules(max_piece=4 * H, break_len=30 * 60, max_span=9 * H)
    r = schedule.crew_cpsat(day, arcs, rules, max_drivers=4, time_limit=20)
    assert r["status"] == "OPTIMAL"
    assert r["drivers"] == 2
