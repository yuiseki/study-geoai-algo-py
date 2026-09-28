"""Ward facility lists (Tokyo Open Data Catalog) for a study area, from the mirror."""

import pytest

from study_geoai import aoi, ckan, geocode
from study_geoai.db import connect


def test_column_detection_accepts_prefixed_names():
    header = ["全国地方公共団体コード", "ID", "投票所_名称", "投票所_緯度", "投票所_経度"]
    assert ckan.pick(header, "緯度") == "投票所_緯度"
    assert ckan.pick(header, "経度") == "投票所_経度"
    assert ckan.pick(header, "名称") == "投票所_名称"
    assert ckan.pick(["名称_カナ", "名称"], "名称") == "名称"  # an exact name wins
    assert ckan.pick(["ID"], "緯度") is None


def test_coordinates_are_checked():
    assert ckan.coord("35.724627", "139.79") == (139.79, 35.724627, "ok")
    assert ckan.coord("", "139.79") == (None, None, "no_coords")
    assert ckan.coord("abc", "139.79") == (None, None, "bad_coords")
    assert ckan.coord("139.79", "35.72") == (None, None, "bad_coords")  # swapped


@pytest.mark.network
def test_taito_evacuation_spaces():
    con = connect()
    area = aoi.load("taito", con)
    ckan.facilities(con, area, "指定緊急避難場所一覧").create_view("f")
    rows = con.sql("select status, inside, count(*) from f group by all order by all").fetchall()
    assert rows == [("ok", True, 17)]
    assert con.sql("select count(*) from f where name = '石浜小学校'").fetchone()[0] == 1


@pytest.mark.network
def test_failures_stay_visible_across_the_23_wards():
    con = connect()
    area = aoi.load("tokyo23", con)
    ckan.facilities(con, area, "投票所一覧").create_view("v")
    statuses = dict(con.sql("select status, count(*) from v group by 1").fetchall())
    # Suginami's CSV was already gone (404) when the mirror was made.
    assert statuses.get("missing_file", 0) >= 1
    assert statuses["ok"] > 100


@pytest.mark.network
def test_a_family_the_ward_does_not_publish_is_empty():
    con = connect()
    area = aoi.load("taito", con)
    assert ckan.facilities(con, area, "公衆トイレ一覧").count("*").fetchone()[0] == 0


@pytest.mark.network
def test_taito_lists_without_coordinates_keep_their_addresses():
    # Taito publishes its libraries with empty 緯度 and 経度; the address is kept.
    con = connect()
    area = aoi.load("taito", con)
    ckan.facilities(con, area, "公立図書館情報").create_view("lib")
    status, n, with_address = con.sql(
        "select any_value(status), count(*), "
        "count(*) filter (where attributes->>'所在地_連結表記' like '東京都台東区%') from lib"
    ).fetchone()
    assert (status, n, with_address) == ("no_coords", 7, 7)


@pytest.mark.network
def test_taito_libraries_are_geocoded_inside_the_ward():
    con = connect()
    area = aoi.load("taito", con)
    ckan.facilities(con, area, "公立図書館情報", geocode=True).create_view("lib")
    rows = con.sql("select status, position, inside, count(*) from lib group by all").fetchall()
    # The published coordinates stay missing; every library is placed, and inside Taito.
    assert all(status == "no_coords" and inside for status, _, inside, _ in rows)
    assert sum(n for *_, n in rows) == 7
    assert {position for _, position, _, _ in rows} <= {"name", "town"}
    assert con.sql("select position from lib where name = '中央図書館'").fetchone()[0] == "name"


@pytest.mark.network
def test_taito_care_services_are_shifted_south_east():
    # Measured 2026-09-28 against each address's town (町丁目) from Nominatim: every one of
    # Taito's 275 care services sits about 0.003 deg south and east of its town, which is
    # the error of Tokyo Datum coordinates read as WGS 84; its other lists do not. If the
    # publisher fixes the file, this test fails and the note in the docs can go.
    import statistics

    con = connect()
    area = aoi.load("taito", con)
    ckan.facilities(con, area, "介護サービス事業所一覧").create_view("k")
    offsets = []
    for lon, lat, address in con.sql(
        "select lon, lat, address from k where status = 'ok'"
    ).fetchall():
        town = geocode.town(address or "")
        for r in geocode.search(f"{town[1]} {town[0]}") if town else []:
            if r["category"] == "boundary" and r["type"] == "administrative":
                offsets.append((lat - float(r["lat"]), lon - float(r["lon"])))
                break
    dlat = statistics.median(o[0] for o in offsets)
    dlon = statistics.median(o[1] for o in offsets)
    assert len(offsets) > 250
    assert -0.0040 < dlat < -0.0020 and 0.0020 < dlon < 0.0040
