"""Tables for the study steps: one row per census small area."""

import pytest

from study_geoai import aoi, features, overture
from study_geoai.db import connect


@pytest.mark.network
def test_taito_small_area_table_adds_up():
    con = connect()
    area = aoi.load("taito", con)
    features.small_areas(con, area).create_view("t")
    n, population, area_km2, buildings = con.sql(
        "select count(*), sum(population), sum(area_km2), sum(n_buildings) from t"
    ).fetchone()
    assert n == 108
    assert population == 211_444
    assert 9.8 < area_km2 < 10.3  # the ward is about 10.1 km2
    overture.read(con, area, "buildings", "building", ["id", "height", "num_floors"]).create_view(
        "b"
    )
    centred = con.execute(
        "select count(*) from b where st_contains(st_geomfromtext(?), st_centroid(geometry))",
        [area.wkt],
    ).fetchone()[0]
    assert buildings == centred  # every building centred in the ward lands in one small area


@pytest.mark.network
def test_taito_small_area_values_are_sane():
    con = connect()
    area = aoi.load("taito", con)
    features.small_areas(con, area).create_view("t")
    lo, hi, bad_cover, negative = con.sql(
        "select min(density), max(density), count(*) filter (where coverage > 1), "
        "count(*) filter (where n_places < 0 or n_buildings < 0) from t"
    ).fetchone()
    assert lo >= 0 and hi < 100_000  # people per km2
    assert bad_cover == 0
    assert negative == 0
