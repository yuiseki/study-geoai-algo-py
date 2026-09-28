"""Overture read at runtime: STAC picks the files, the bbox column picks the rows."""

import pytest

from study_geoai import aoi, overture
from study_geoai.db import connect


def test_overlapping_positions_skip_the_collection_wide_bbox():
    # extent.spatial.bbox[0] covers the whole collection; the rest follow item order.
    bboxes = [[-180, -90, 180, 90], [0, 0, 1, 1], [139, 35, 140, 36], [139.5, 35.5, 141, 37]]
    assert overture.overlapping(bboxes, (139.76, 35.69, 139.81, 35.74)) == [1, 2]
    assert overture.overlapping(bboxes, (10, 10, 11, 11)) == []


@pytest.mark.network
def test_taito_buildings_come_from_one_file():
    area = aoi.load("taito")
    assert len(overture.files("buildings", "building", area.bbox)) == 1


@pytest.mark.network
def test_taito_buildings():
    con = connect()
    area = aoi.load("taito", con)
    overture.read(con, area, "buildings", "building", ["id", "height", "num_floors"]).create_view(
        "buildings"
    )
    n, with_height, outside = con.execute(
        "select count(*), count(height), "
        "count(*) filter (where not st_intersects(geometry, st_geomfromtext(?))) from buildings",
        [area.wkt],
    ).fetchone()
    assert n == 40_502
    assert 0 < with_height < n
    assert outside == 0
