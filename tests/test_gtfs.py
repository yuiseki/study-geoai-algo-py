"""Tokyo bus GTFS feeds, as DuckDB views read from the z.yuiseki.net mirror."""

import pytest

from study_geoai import gtfs
from study_geoai.db import connect


def test_seconds_handles_one_digit_hours_and_times_past_midnight():
    con = connect()
    got = con.sql(
        f"select {gtfs.seconds('t')} from (values ('6:50:00'), ('06:50:00'), ('25:01:30')) v(t)"
    ).fetchall()
    assert got == [(24_600,), (24_600,), (90_090,)]


@pytest.mark.network
@pytest.mark.parametrize(
    ("name", "routes", "stops", "trips", "stop_times"),
    [
        ("megurin", 4, 128, 290, 8_261),
        ("toei", 150, 5_365, 55_846, 1_061_831),
        ("suginami", 1, 4, 24, 120),
        ("arakawa", 4, 32, 34, 568),
        ("katsushika", 1, 11, 57, 684),
    ],
)
def test_feed_counts(name, routes, stops, trips, stop_times):
    con = connect()
    tables = gtfs.load(con, name)
    assert {"routes", "stops", "trips", "stop_times"} <= set(tables)
    count = {t: con.sql(f"select count(*) from {name}.{t}").fetchone()[0] for t in tables}
    assert (count["routes"], count["stops"], count["trips"], count["stop_times"]) == (
        routes, stops, trips, stop_times,
    )  # fmt: skip
    # No vehicle assignment is published: that is the scheduling problem of step 10.
    trip_columns = [r[0] for r in con.sql(f"describe {name}.trips").fetchall()]
    assert (
        "block_id" not in trip_columns
        or con.sql(
            f"select count(*) from {name}.trips where coalesce(trim(block_id), '') <> ''"
        ).fetchone()[0]
        == 0
    )


@pytest.mark.network
def test_megurin_service_hours():
    con = connect()
    gtfs.load(con, "megurin")
    # feed_info.txt starts with a UTF-8 BOM; it must not end up in the column name.
    assert con.sql("describe megurin.feed_info").fetchall()[0][0] == "feed_publisher_name"
    first, last = con.sql(
        f"select min({gtfs.seconds('departure_time')}), max({gtfs.seconds('departure_time')}) "
        "from megurin.stop_times"
    ).fetchone()
    assert (first, last) == (6 * 3600 + 59 * 60, 20 * 3600 + 55 * 60)
