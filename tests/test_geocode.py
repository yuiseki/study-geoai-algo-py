"""Geocoding facility addresses with nominatim.yuiseki.net."""

import pytest

from study_geoai import aoi, geocode
from study_geoai.db import connect


@pytest.mark.parametrize(
    ("address", "ward", "town"),
    [
        ("東京都台東区西浅草3丁目25-16", "台東区", "西浅草三丁目"),
        ("東京都台東区西浅草3-25-16台東区生涯学習センター内", "台東区", "西浅草三丁目"),
        ("東京都台東区清川１－１４－２１", "台東区", "清川一丁目"),
        ("台東区台東1丁目", "台東区", "台東一丁目"),
        ("東京都台東区上野公園", "台東区", "上野公園"),
        ("東京都千代田区丸の内二丁目", "千代田区", "丸の内二丁目"),
    ],
)
def test_town_is_taken_from_the_address(address, ward, town):
    assert geocode.town(address) == (ward, town)


def test_kanji_numbers():
    assert [geocode.kanji(n) for n in (1, 3, 10, 12, 20, 25)] == [
        "一", "三", "十", "十二", "二十", "二十五",
    ]  # fmt: skip


def test_names_match_without_the_ward_prefix():
    assert geocode.same_name("台東区立中央図書館", "中央図書館")
    assert geocode.same_name("台東区立石浜小学校", "石浜小学校")
    assert geocode.same_name("台東区立 平成小学校", "平成小学校")
    assert not geocode.same_name("相互台公民館", "台東一丁目区民館")
    assert geocode.core("東京都立上野高等学校") == "上野高等学校"
    assert geocode.core("台東一丁目区民館") == "台東一丁目区民館"
    assert geocode.core("立花台") == "立花台"  # a name that starts with 立 is left alone
    assert (
        geocode.core("東京都台東区立りゅうせん高齢者在宅サービスセンター")
        == "りゅうせん高齢者在宅サービスセンター"
    )


@pytest.mark.network
def test_taito_library_by_name():
    con = connect()
    area = aoi.load("taito", con)
    lon, lat, how = geocode.locate(con, area, "中央図書館", "東京都台東区西浅草3丁目25-16")
    assert how == "name"
    assert abs(lon - 139.7899) < 0.001 and abs(lat - 35.7173) < 0.001


@pytest.mark.network
def test_a_name_found_elsewhere_in_japan_is_not_taken():
    # "台東区 台東一丁目区民館" alone returns community centres in Hiroshima and Toride;
    # the other query forms find the real one in Taito.
    con = connect()
    area = aoi.load("taito", con)
    lon, lat, how = geocode.locate(con, area, "台東一丁目区民館", "東京都台東区台東1丁目")
    assert how == "name"
    assert area.contains(lon, lat)


@pytest.mark.network
def test_an_unknown_name_falls_back_to_the_town():
    con = connect()
    area = aoi.load("taito", con)
    lon, lat, how = geocode.locate(con, area, "存在しない施設ゼロゼロ", "東京都台東区台東1丁目2-3")
    assert how == "town"
    assert area.contains(lon, lat)
    assert geocode.locate(con, area, "存在しない施設ゼロゼロ", "") == (None, None, None)


@pytest.mark.network
def test_the_ward_can_come_from_the_publisher_when_there_is_no_address():
    con = connect()
    area = aoi.load("taito", con)
    lon, lat, how = geocode.locate(con, area, "平成小学校", None, ward="台東区")
    assert how == "name"
    assert area.contains(lon, lat)
