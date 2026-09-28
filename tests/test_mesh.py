"""The Japanese standard grid square (3rd mesh, about 1 km)."""

import pytest

from study_geoai import mesh
from study_geoai.db import connect


def test_tokyo_station_is_in_53394611():
    assert mesh.code(139.767125, 35.681236) == 53394611


def test_bounds_contain_the_point_and_have_the_mesh_size():
    west, south, east, north = mesh.bounds(53394611)
    assert west <= 139.767125 < east and south <= 35.681236 < north
    assert abs((east - west) - 45 / 3600) < 1e-12  # 45 seconds of longitude
    assert abs((north - south) - 30 / 3600) < 1e-12  # 30 seconds of latitude


def test_sql_matches_python():
    con = connect()
    points = [(139.767125, 35.681236), (139.7745, 35.7138), (139.5, 35.6), (139.99, 35.51)]
    for lon, lat in points:
        got = con.execute(
            f"select {mesh.sql('lon', 'lat')} from (select ?::double as lon, ?::double as lat)",
            [lon, lat],
        ).fetchone()[0]
        assert got == mesh.code(lon, lat)


@pytest.mark.parametrize("code", [53394611, 53394683, 53395700])
def test_code_of_the_centre_round_trips(code):
    west, south, east, north = mesh.bounds(code)
    assert mesh.code((west + east) / 2, (south + north) / 2) == code
