"""2020 census small areas, one row per 11-digit key."""

import pytest

from study_geoai import aoi, census
from study_geoai.db import connect


@pytest.mark.network
@pytest.mark.parametrize(("name", "population"), [("taito", 211_444), ("tokyo23", 9_733_276)])
def test_small_areas_add_up_to_the_area_population(name, population):
    con = connect()
    area = aoi.load(name, con)
    census.small_areas(con, area).create_view("sa")
    n, keys, total, key_lengths = con.sql(
        "select count(*), count(distinct key11), sum(population), list(distinct length(key11)) "
        "from sa"
    ).fetchone()
    assert n == keys  # one row per key
    assert key_lengths == [11]
    assert total == population
