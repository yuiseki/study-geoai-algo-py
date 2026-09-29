"""Step 10A: the fewest buses to run a community bus timetable, with CP-SAT.

GTFS feeds of the community buses leave block_id empty: they do not say which
bus runs which trip. From the weekday trips' first and last stops and times,
find the fewest vehicles that can run them all (study_geoai.schedule):

- arcs: a bus can run trip b after trip a when it reaches b's first stop in
  time: LAYOVER at the terminal, plus an empty run at DEADHEAD_KMH over the
  straight-line gap when the terminals differ;
- CP-SAT: every trip has at most one next and one previous trip on its bus;
  maximise the arcs used (fleet = trips - arcs);
- checked against a maximum bipartite matching (the same minimum, exactly) and
  the peak number of trips running at once (a lower bound);
- a second stage keeps that fleet and minimises the time buses stand idle.

The small Arakawa City feed (28 weekday trips) comes first, then Megurin (171).

    uv run python src/010-A-cp-sat/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from study_geoai import schedule  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
LAYOVER = 3 * 60
DEADHEAD_KMH = 15.0
FEEDS = (("arakawa", ["毎日", "平日"]), ("megurin", ["平日"]))


def hhmm(s):
    return f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}"


def gantt(t, blocks, path, title):
    fig, ax = plt.subplots(figsize=(11, 0.35 * len(blocks) + 1.5))
    for row, b in enumerate(blocks):
        for i in b:
            ax.barh(row, (t.end[i] - t.start[i]) / 3600, left=t.start[i] / 3600, height=0.6,
                    color="tab:blue", edgecolor="white")  # fmt: skip
    ax.set_yticks(range(len(blocks)), [f"bus {k + 1}" for k in range(len(blocks))])
    ax.invert_yaxis()
    ax.set_xlabel("hour of day")
    ax.set_title(title)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    for feed, services in FEEDS:
        t = schedule.gtfs_trips(con, feed, services)
        n = len(t.ids)
        for layover in (LAYOVER, 0):
            arcs = schedule.connections(t, layover=layover, speed_kmh=DEADHEAD_KMH)
            same = sum(1 for a, b in arcs if np.hypot(*(t.dest[a] - t.origin[b])) < 1)
            match = schedule.min_fleet_matching(n, arcs)
            one = schedule.min_fleet_cpsat(t, arcs)
            two = schedule.min_fleet_cpsat(t, arcs, second_stage=True)
            if layover == LAYOVER:
                print(f"\n## {feed} ({', '.join(services)}): {n} trips, "
                      f"{hhmm(t.start.min())} to {hhmm(t.end.max())}; peak running at once "
                      f"{schedule.peak(t)}")  # fmt: skip
            print(f"   layover {layover // 60} min, deadhead {DEADHEAD_KMH:.0f} km/h: {len(arcs):,} arcs "
                  f"({same:,} at the same stop); fewest buses: CP-SAT {one['vehicles']} "
                  f"({one['status']}, {one['seconds']:.2f} s), matching {match}; "
                  f"idle time {one['idle'] / 3600:.1f} h -> {two['idle'] / 3600:.1f} h after "
                  f"the second stage ({two['seconds']:.2f} s)")  # fmt: skip
            if layover == LAYOVER:
                blocks = sorted(two["blocks"], key=lambda b: t.start[b[0]])
                for k, b in enumerate(blocks[:4]):
                    print(f"      bus {k + 1}: {len(b)} trips, {hhmm(t.start[b[0]])} to "
                          f"{hhmm(t.end[b[-1]])}")  # fmt: skip
                gantt(t, blocks, OUT / f"blocks-{feed}.png",
                      f"{feed}: {two['vehicles']} buses (layover {layover // 60} min)")  # fmt: skip
    print(f"\ncharts: {OUT}")


if __name__ == "__main__":
    main()
