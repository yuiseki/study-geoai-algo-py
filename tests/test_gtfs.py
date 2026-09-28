"""The Taito City Megurin GTFS, as DuckDB views."""

import pytest

from study_geoai import gtfs
from study_geoai.db import connect


@pytest.mark.network
def test_megurin_tables():
    con = connect()
    gtfs.megurin(con)
    counts = {t: con.sql(f"select count(*) from {t}").fetchone()[0] for t in gtfs.TABLES}
    assert counts["routes"] == 4
    assert counts["stops"] == 128
    assert counts["trips"] == 290
    assert counts["stop_times"] == 8_261
    # No vehicle assignment is published: that is the scheduling problem of step 10.
    # feed_info.txt starts with a UTF-8 BOM; it must not end up in the column name.
    assert con.sql("describe feed_info").fetchall()[0][0] == "feed_publisher_name"
    trip_columns = [r[0] for r in con.sql("describe trips").fetchall()]
    assert "block_id" not in trip_columns
    # Times past midnight would need care; this feed runs 06:59 to 20:55.
    first, last = con.sql(
        "select min(departure_time), max(departure_time) from stop_times"
    ).fetchone()
    assert (first, last) == ("06:59:00", "20:55:00")
