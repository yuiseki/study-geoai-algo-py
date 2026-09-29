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


def test_cell_bounds_from_the_id():
    # row 6976, column 7187: south-west corner 20 + 6976 * 0.00225, 120 + 7187 * 0.00275
    west, south, east, north = michiyomi.cell_bounds(697607187)
    assert west == pytest.approx(139.76425) and south == pytest.approx(35.696)
    assert east - west == pytest.approx(0.00275) and north - south == pytest.approx(0.00225)


@pytest.mark.network
def test_taito_scenes_lie_in_their_cells():
    con = connect()
    michiyomi.scenes(con, aoi.load("taito", con)).create_view("s")
    rows = con.sql("select cell_250m, lon, lat from s using sample 2000 rows (reservoir, 0)")
    for cell, lon, lat in rows.fetchall():
        west, south, east, north = michiyomi.cell_bounds(cell)
        assert west - 1e-9 <= lon < east + 1e-9 and south - 1e-9 <= lat < north + 1e-9
