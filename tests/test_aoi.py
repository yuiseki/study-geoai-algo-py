"""The two study areas: Taito City (A) and the 23 wards of Tokyo (B)."""

import pytest

from study_geoai import aoi


def test_cache_path_is_under_the_temp_dir_and_keyed_by_revision(tmp_path, monkeypatch):
    monkeypatch.setattr(aoi, "CACHE_DIR", tmp_path)
    path = aoi.cache_path("jp-admin", "abc123", "tokyo23")
    assert path.parent == tmp_path
    assert "abc123" in path.name and path.suffix == ".parquet"


def test_unknown_area_is_rejected():
    with pytest.raises(KeyError):
        aoi.load("osaka")


@pytest.mark.network
def test_taito():
    area = aoi.load("taito")
    assert area.codes == ("13106",)
    assert area.population == 211_444
    west, south, east, north = area.bbox
    assert 139.76 < west < 139.77 and 139.80 < east < 139.81
    assert 35.69 < south < 35.70 and 35.73 < north < 35.74
    assert area.contains(139.7745, 35.7138)  # Ueno
    assert not area.contains(139.7671, 35.6812)  # Tokyo Station, in Chiyoda


@pytest.mark.network
def test_tokyo23():
    area = aoi.load("tokyo23")
    assert len(area.codes) == 23
    # 2020 census population of the 23 wards
    assert area.population == 9_733_276
    assert area.contains(139.7745, 35.7138)
    assert area.contains(139.7671, 35.6812)
    assert not area.contains(139.4800, 35.6600)  # Fuchu, outside the wards
