"""FAO FERSPAS AgERA5 monthly grids over Japan."""

import numpy as np
import pytest

from study_geoai import ferspas


def test_gs_href_becomes_the_anonymous_https_url():
    gs = "gs://fao-gismgr-c3s-data/DATA/C3S/MAPSET/AGERA5-PF-M/C3S.AGERA5-PF-M.1979-01.tif"
    assert ferspas.https(gs) == (
        "https://storage.googleapis.com/fao-gismgr-c3s-data/DATA/C3S/MAPSET/"
        "AGERA5-PF-M/C3S.AGERA5-PF-M.1979-01.tif"
    )


def test_https_refuses_anything_else():
    with pytest.raises(ValueError):
        ferspas.https("https://storage.cloud.google.com/x.tif")


def test_collection_ids_for_the_four_variables():
    assert ferspas.collection("rain") == "fao-gismgr:C3S:raster:mapsets:AGERA5-PF-M"
    assert ferspas.collection("tmin") == "fao-gismgr:C3S:raster:mapsets:AGERA5-TMIN-AVG-M"
    with pytest.raises(KeyError):
        ferspas.collection("wind")


def test_window_is_whole_pixels_of_the_global_grid():
    # The grid starts at 180 W, 90 N with 0.1 degree cells.
    row0, col0, rows, cols = ferspas.window((139.0, 35.0, 140.0, 36.0))
    assert (row0, col0, rows, cols) == (540, 3190, 10, 10)


def test_pixel_centres_of_a_window():
    lon, lat = ferspas.centres((139.0, 35.0, 140.0, 36.0))
    assert lon.shape == (10,) and lat.shape == (10,)
    assert np.isclose(lon[0], 139.05) and np.isclose(lat[0], 35.95)  # north first
    assert np.isclose(lat[-1], 35.05)


def test_monthly_normals_average_each_calendar_month():
    # Two years of a 1x1 grid: January is 1 then 3, every other month is 10.
    months = np.array([f"{y}-{m:02d}-01" for y in (2000, 2001) for m in range(1, 13)],
                      dtype="datetime64[D]")  # fmt: skip
    values = np.full((24, 1, 1), 10.0)
    values[0], values[12] = 1.0, 3.0
    normals = ferspas.normals(values, months)
    assert normals.shape == (12, 1, 1)
    assert normals[0, 0, 0] == 2.0 and normals[5, 0, 0] == 10.0


@pytest.mark.network
def test_one_month_over_tokyo():
    months, grid = ferspas.stack("tmax", (139.5, 35.5, 140.0, 36.0), "2020-08-01", "2020-08-01")
    assert list(months) == [np.datetime64("2020-08-01")]
    assert grid.shape == (1, 5, 5)
    celsius = grid - 273.15
    assert 25 < np.nanmean(celsius) < 35  # an August afternoon in Tokyo


def test_on_cells_keeps_land_cells_and_turns_kelvin_into_celsius(monkeypatch):
    import pandas as pd

    months = np.array(["2000-01-01", "2000-02-01"], dtype="datetime64[D]")
    grid = np.arange(2 * 2 * 3, dtype="float32").reshape(2, 2, 3) + 273.15
    monkeypatch.setattr(ferspas, "stack", lambda *a: (months, grid))
    cells = pd.DataFrame({"row": [0, 1], "col": [2, 0]})
    got_months, values = ferspas.on_cells("tmax", cells, "2000-01-01", "2000-02-01")
    assert list(got_months) == list(months)
    assert values.shape == (2, 2)  # month x cell
    assert np.allclose(values[:, 0], [2.0, 8.0]) and np.allclose(values[:, 1], [3.0, 9.0])
    _, rain = ferspas.on_cells("rain", cells, "2000-01-01", "2000-02-01")
    assert np.isclose(rain[0, 0], 275.15)  # rain is not converted


def test_japan_cells_drops_cells_agera5_has_as_sea(monkeypatch):
    import pandas as pd

    joined = pd.DataFrame({"row": [0, 0, 1], "col": [0, 1, 1], "pref_code": ["13"] * 3})
    monkeypatch.setattr(ferspas, "_prefecture_cells", lambda bbox, con: joined)
    grid = np.array([[[1.0, np.nan], [5.0, 2.0]]], dtype="float32")
    monkeypatch.setattr(
        ferspas, "stack", lambda *a: (np.array(["2020-01-01"], "datetime64[D]"), grid)
    )
    got = ferspas.japan_cells(con=object())
    assert list(zip(got["row"], got["col"], strict=True)) == [(0, 0), (1, 1)]
