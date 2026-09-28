"""michiyomi street scenes for a study area, with chosen analysis fields."""

import pytest

from study_geoai import aoi, michiyomi
from study_geoai.db import connect


def test_every_ward_has_a_file_name():
    assert len(michiyomi.WARD_FILES) == 23
    assert set(michiyomi.WARD_FILES) == set(aoi.TOKYO23)
    # Toshima City is "toshima"; "toshima-island" is Toshima Village, not a ward.
    assert michiyomi.WARD_FILES["13116"] == "toshima"


@pytest.mark.network
def test_taito_scenes():
    con = connect()
    area = aoi.load("taito", con)
    michiyomi.scenes(con, area).create_view("s")
    n, years, poles_max, bad_width, undergrounded = con.sql(
        "select count(*), min(capture_year) || '-' || max(capture_year), max(poles_visible), "
        "count(*) filter (where roadway_width_m < 0), list(distinct undergrounded order by 1) "
        "from s"
    ).fetchone()
    # taito.parquet has 55,044 scenes; 1,096 of them lie just outside the ward
    # boundary (median 7 m, at most about 100 m), on streets along its edge.
    assert n == 53_948
    assert years == "1970-2026"
    assert 0 < poles_max < 100
    assert bad_width == 0
    assert "架空線あり" in undergrounded
