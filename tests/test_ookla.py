"""Ookla Speedtest tiles for a study area, read from the z.yuiseki.net mirror."""

import pytest

from study_geoai import aoi, ookla
from study_geoai.db import connect


def test_url_follows_ookla_layout():
    assert ookla.url("mobile", 2026, 2).endswith(
        "/type=mobile/year=2026/quarter=2/2026-04-01_performance_mobile_tiles.parquet"
    )
    assert "/2025-10-01_performance_fixed_tiles.parquet" in ookla.url("fixed", 2025, 4)


@pytest.mark.network
@pytest.mark.parametrize("type_", ["mobile", "fixed"])
def test_taito_tiles(type_):
    con = connect()
    area = aoi.load("taito", con)
    ookla.tiles(con, area, type_, 2026, 2).create_view("t")
    n, outside, keylen, tests = con.execute(
        "select count(*), count(*) filter (where not st_intersects(geometry, st_geomfromtext(?))), "
        "list(distinct length(quadkey)), min(tests) from t",
        [area.wkt],
    ).fetchone()
    # 89 mobile and 90 fixed tiles meet the ward's bounding box; 62 of each meet the ward.
    assert n == 62
    assert outside == 0
    assert keylen == [16]
    assert tests >= 1
