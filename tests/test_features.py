"""Tables for the study steps: one row per census small area."""

import numpy as np
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


@pytest.mark.network
def test_taito_tile_table():
    from study_geoai import worldpop

    con = connect()
    area = aoi.load("taito", con)
    features.tiles(con, area).create_view("t")
    n, keys, missing, pop, scenes = con.sql(
        "select count(*), count(distinct quadkey), count(*) filter (where avg_d_kbps is null), "
        "sum(population), sum(n_scenes) from t"
    ).fetchone()
    assert n == keys == 62  # the tiles that meet the ward
    assert missing == 0
    total = worldpop.grid(con, area, 2025).aggregate("sum(population)").fetchone()[0]
    assert 0 < pop <= total + 1  # Ookla has no tile where nobody tested
    assert scenes > 0


@pytest.mark.network
def test_taito_tile_cells():
    from study_geoai import opencellid

    con = connect()
    area = aoi.load("taito", con)
    features.tile_cells(con, area).create_view("tc")
    n, cells, missing_nearest = con.sql(
        "select count(*), sum(n_cells), count(*) filter (where nearest_m is null) from tc"
    ).fetchone()
    assert n == 62
    total = opencellid.cells(con, area).aggregate("count(*)").fetchone()[0]
    assert 0 < cells <= total  # cells outside any tested tile are not counted
    assert missing_nearest == 0


def test_place_kinds():
    assert features.place_kind("food_and_beverage_store") == "retail"
    assert features.place_kind("restaurant") == "food"
    assert features.place_kind("coffee_shop") == "food"
    assert features.place_kind("hotel") == "lodging"
    assert features.place_kind("buddhist_place_of_worship") == "culture"
    assert features.place_kind("atm") == "other"
    assert features.place_kind(None) == "other"


@pytest.mark.network
def test_taito_small_area_profiles():
    con = connect()
    area = aoi.load("taito", con)
    features.small_area_profiles(con, area).create_view("pr")
    n, bad_shares, scenes = con.sql(
        "select count(*), count(*) filter (where n_places > 0 and "
        "abs(share_food + share_retail + share_lodging + share_culture + share_other - 1) > 1e-9), "
        "sum(n_scenes) from pr"
    ).fetchone()
    assert n == 108
    assert bad_shares == 0  # the five kinds add up to all places
    assert scenes > 0


@pytest.mark.network
def test_tokyo23_grid_profiles():
    from study_geoai import worldpop

    con = connect()
    area = aoi.load("tokyo23", con)
    features.grid_profiles(con, area).create_view("g")
    n, codes, area_km2, pop = con.sql(
        "select count(*), count(distinct mesh), avg(area_km2), sum(population) from g"
    ).fetchone()
    assert n == codes
    assert 550 < n < 700  # about 627 km2 of 1.05 km2 squares
    assert 1.0 < area_km2 < 1.1
    total = worldpop.grid(con, area, 2025).aggregate("sum(population)").fetchone()[0]
    assert 0.9 * total < pop < 1.1 * total  # edge squares count their centres only


@pytest.mark.network
def test_taito_place_points_in_metres():
    con = connect()
    area = aoi.load("taito", con)
    features.place_points(con, area).create_view("pp")
    n, xmin, xmax, ymin, ymax, kinds, wards, named = con.sql("""
        select count(*), min(x), max(x), min(y), max(y), list(distinct kind), list(distinct code5),
               avg((town is not null)::int)
        from pp
    """).fetchone()
    assert n > 10_000
    # Taito is about 4 km across; plane IX puts it west and south of its origin
    assert 3_000 < xmax - xmin < 6_000 and 3_000 < ymax - ymin < 6_000
    assert -10_000 < xmin < 0 and -40_000 < ymin < -25_000
    assert set(kinds) <= set(features.KINDS) and "food" in kinds
    assert set(wards) <= {"13106", None}
    assert named > 0.95


@pytest.mark.network
def test_taito_street_cells():
    con = connect()
    features.street_cells(con, aoi.load("taito", con)).create_view("sc")
    n, cells, least, shares = con.sql("""
        select count(*), count(distinct cell_250m), min(n_scenes),
               list_value(min(undergrounded_share), max(undergrounded_share),
                          min(block_paving_share), max(wires_high_share))
        from sc
    """).fetchone()
    assert n == cells and 100 < n < 205  # Taito has 205 cells, some with few scenes
    assert least >= features.MIN_SCENES
    assert all(0 <= s <= 1 for s in shares)
    wards = con.sql("select list(distinct ward) from sc").fetchone()[0]
    assert wards == ["台東区"]  # the ward most of a cell's scenes lie in
    area = con.sql("select avg(st_area_spheroid(st_flipcoordinates(geometry))) from sc").fetchone()[
        0
    ]
    assert 55_000 < area < 70_000  # 0.00275 by 0.00225 degrees near 35.7 N is about 62,000 m2


def test_to_metric_keeps_distances():
    con = connect()
    # Ueno Station and Asakusa Station: 0.0202 deg east and 0.0034 deg south, about 1.9 km
    xy = features.to_metric(con, [(139.7774, 35.7141), (139.7976, 35.7107)])
    assert xy.shape == (2, 2)
    assert 1_700 < np.hypot(*(xy[0] - xy[1])) < 2_000
