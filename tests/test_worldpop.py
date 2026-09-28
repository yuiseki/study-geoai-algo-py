"""WorldPop grids for a study area, read as COG windows from the z.yuiseki.net mirror."""

import os
import subprocess
import sys

import pytest

from study_geoai import aoi, worldpop
from study_geoai.db import connect


@pytest.mark.network
def test_url_comes_from_the_mirror_manifest():
    assert worldpop.url(2020).endswith(
        "/2020/JPN/v1/100m/constrained/jpn_pop_2020_CN_100m_R2025A_v1.tif"
    )
    assert worldpop.url(2025, "1km").endswith(
        "/2025/JPN/v1/1km_ua/constrained/jpn_pop_2025_CN_1km_R2025A_UA_v1.tif"
    )


@pytest.mark.network
def test_nodata_survives_anaconda_gdal_variables():
    # This host's shell points GDAL_DRIVER_PATH at anaconda's GDAL 3.9 plugins, which
    # made rasterio read the GeoTIFF nodata as None. Importing study_geoai must undo that.
    env = dict(os.environ, GDAL_DRIVER_PATH="/home/yuiseki/anaconda3/lib/gdalplugins")
    code = (
        "import study_geoai, rasterio\n"
        "from study_geoai import worldpop\n"
        "with rasterio.Env(**worldpop.GDAL_ENV), rasterio.open(worldpop.url(2020, '1km')) as s:\n"
        "    print(s.nodata)\n"
    )
    out = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert out.stdout.strip() == "-99999.0", out.stderr


@pytest.mark.network
def test_taito_population_grid():
    con = connect()
    area = aoi.load("taito", con)
    worldpop.grid(con, area, 2020).create_view("g")
    n, total, lowest = con.sql(
        "select count(*), sum(population), min(population) from g"
    ).fetchone()
    assert n == 1_422
    assert lowest >= 0
    # WorldPop's modelled 2020 population for the ward, against 211,444 in the census.
    assert 0.8 * 211_444 < total < 1.2 * 211_444


@pytest.mark.network
def test_taito_agesex_adds_up():
    con = connect()
    area = aoi.load("taito", con)
    worldpop.agesex(con, area, 2020).create_view("a")
    by_sex = dict(con.sql("select sex, sum(population) from a group by 1").fetchall())
    groups = con.sql("select count(distinct age_group) from a").fetchone()[0]
    assert groups == 20
    assert abs(by_sex["f"] + by_sex["m"] - by_sex["t"]) < 1
    # Against the total population grid at the same 1 km resolution.
    total = worldpop.grid(con, area, 2020, "1km").aggregate("sum(population)").fetchone()[0]
    assert abs(by_sex["t"] / total - 1) < 0.01


@pytest.mark.network
@pytest.mark.parametrize(("level", "value"), [(1, 3), (2, 30)])
def test_taito_urbanisation(level, value):
    # The grid is 1 km in Mollweide; every cell centred in Taito City has one value.
    con = connect()
    area = aoi.load("taito", con)
    n, values = (
        worldpop.urbanisation(con, area, 2020, level)
        .aggregate("count(*), list(distinct value)")
        .fetchone()
    )
    assert n == 12
    assert values == [value]
