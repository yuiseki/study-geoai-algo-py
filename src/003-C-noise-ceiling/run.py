"""Step 3C: how much of mobile speed per tile is repeatable at all?

A tile's speed is a mean over a handful of tests, so part of it is noise that
no feature can predict. Taking another quarter's speed of the same tile as
the prediction gives a rough ceiling: what "the place itself" explains.
Tiles of the 23 wards measured in both quarters, log mean download speed,
R2 weighted by the current quarter's tests.

    uv run python src/003-C-noise-ceiling/run.py
"""

import numpy as np
from sklearn.metrics import r2_score

from study_geoai import aoi, ookla
from study_geoai.db import connect

CURRENT = (2026, 2)
EARLIER = [(2026, 1), (2025, 4)]


def pairs(con, area, earlier):
    ookla.tiles(con, area, "mobile", *CURRENT).create_view("a")
    ookla.tiles(con, area, "mobile", *earlier).create_view("b")
    rows = con.sql("""
        select ln(a.avg_d_kbps), ln(b.avg_d_kbps), a.tests, b.tests
        from a join b using (quadkey)
        where a.avg_d_kbps > 0 and b.avg_d_kbps > 0
    """).fetchall()
    return np.array(rows, dtype=float).T


def main():
    con = connect()
    area = aoi.load("tokyo23", con)
    n_now = ookla.tiles(con, area, "mobile", *CURRENT).aggregate("count(*)").fetchone()[0]
    print(f"23 wards: {n_now:,} tiles in {CURRENT[0]} Q{CURRENT[1]}")
    for earlier in EARLIER:
        now, then, t_now, t_then = pairs(con, area, earlier)
        print(f"\n## {CURRENT[0]} Q{CURRENT[1]} against {earlier[0]} Q{earlier[1]}: "
              f"{len(now):,} tiles in both")  # fmt: skip
        print("   minimum tests in both   tiles   correlation   R2 (weighted)   R2 of a linear fit")
        for k in (1, 10, 30, 100):
            m = (t_now >= k) & (t_then >= k)
            if m.sum() < 30:
                continue
            r = np.corrcoef(now[m], then[m])[0, 1]
            r2_raw = r2_score(now[m], then[m], sample_weight=t_now[m])
            # A linear fit of now on then removes any overall shift between quarters.
            slope, icpt = np.polyfit(then[m], now[m], 1, w=np.sqrt(t_now[m]))
            r2_fit = r2_score(now[m], icpt + slope * then[m], sample_weight=t_now[m])
            print(f"   {k:>3}                     {m.sum():>5,}   {r:+.3f}        "
                  f"{r2_raw:+.3f}          {r2_fit:+.3f}")  # fmt: skip


if __name__ == "__main__":
    main()
