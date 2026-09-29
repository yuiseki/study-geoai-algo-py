"""Step 10B: drivers' duties for the same timetables, with CP-SAT intervals.

A driver takes trips (not a bus): consecutive trips must be reachable on foot
(relief at a stop, LAYOVER to change, walking at WALK_KMH). Each driver has one
break of BREAK_LEN that no trip of theirs overlaps (an interval in a NoOverlap
with their optional trip intervals), at most MAX_PIECE of work on each side of
it and at most MAX_SPAN from first start to last end. Minimise the drivers
(study_geoai.schedule.crew_cpsat).

Lower bounds to judge the answer: the buses of step 10A (every running trip
needs a driver), and the day's driving over the most one driver can do.

    uv run python -u src/010-B-scheduling/run.py
"""

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from study_geoai import schedule  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
H = 3600
LAYOVER = 3 * 60
WALK_KMH = 4.8
RULES = schedule.CrewRules(max_piece=4 * H, break_len=30 * 60, max_span=9 * H)
RUNS = (("arakawa", ["毎日", "平日"], 8, 60), ("megurin", ["平日"], 45, 300))


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"rules: work at most {RULES.max_piece / H:.1f} h on each side of one "
          f"{RULES.break_len / 60:.0f}-minute break, span at most {RULES.max_span / H:.1f} h; "
          f"relief on foot at {WALK_KMH} km/h with {LAYOVER // 60} minutes to change")  # fmt: skip
    for feed, services, max_drivers, limit in RUNS:
        t = schedule.gtfs_trips(con, feed, services)
        n = len(t.ids)
        bus_arcs = schedule.connections(t, layover=LAYOVER, speed_kmh=15.0)
        buses = schedule.min_fleet_matching(n, bus_arcs)
        crew_arcs = schedule.connections(t, layover=LAYOVER, speed_kmh=WALK_KMH)
        driving = float((t.end - t.start).sum())
        by_hours = math.ceil(driving / (2 * RULES.max_piece))
        print(f"\n## {feed}: {n} trips, {driving / H:.1f} h of driving; buses (10A) {buses}; "
              f"lower bound from hours {by_hours}; {len(crew_arcs):,} relief arcs; "
              f"up to {max_drivers} drivers, {limit} s")  # fmt: skip
        r = schedule.crew_cpsat(t, crew_arcs, RULES, max_drivers=max_drivers, time_limit=limit)
        if "drivers" not in r:
            print(f"   {r['status']} after {r['seconds']:.0f} s")
            continue
        print(f"   {r['status']}: {r['drivers']} drivers (CP-SAT bound {r['bound']:.0f}); "
              f"{r['seconds']:.1f} s")  # fmt: skip
        duties = sorted(r["duties"], key=lambda d: t.start[d["trips"]].min())
        spans = [(t.end[d["trips"]].max() - t.start[d["trips"]].min()) / H for d in duties]
        work = [float((t.end[d["trips"]] - t.start[d["trips"]]).sum()) / H for d in duties]
        print(f"   span per driver: median {np.median(spans):.1f} h, max {max(spans):.1f} h; "
              f"driving per driver: median {np.median(work):.1f} h, min {min(work):.1f} h")  # fmt: skip
        fig, ax = plt.subplots(figsize=(11, 0.35 * len(duties) + 1.5))
        for row, d in enumerate(duties):
            for i in d["trips"]:
                ax.barh(row, (t.end[i] - t.start[i]) / H, left=t.start[i] / H, height=0.6,
                        color="tab:blue")  # fmt: skip
            b0, b1 = d["break"]
            ax.barh(row, (b1 - b0) / H, left=b0 / H, height=0.6, color="tab:orange")
        ax.set_yticks(range(len(duties)), [f"driver {k + 1}" for k in range(len(duties))])
        ax.invert_yaxis()
        ax.set_xlabel("hour of day (orange: break)")
        ax.set_title(f"{feed}: {len(duties)} drivers")
        fig.savefig(OUT / f"duties-{feed}.png", dpi=120, bbox_inches="tight")
        plt.close(fig)
    print(f"\ncharts: {OUT}")


if __name__ == "__main__":
    main()
