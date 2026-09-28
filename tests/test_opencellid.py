"""OpenCelliD cell towers for a study area."""

import pytest

from study_geoai import aoi, opencellid
from study_geoai.db import connect


@pytest.mark.network
def test_taito_cells():
    con = connect()
    area = aoi.load("taito", con)
    opencellid.cells(con, area).create_view("c")
    n, keys, outside, radios, mcc = con.execute(
        "select count(*), count(distinct (radio, mcc, net, area_code, cell)), "
        "count(*) filter (where not st_intersects(geometry, st_geomfromtext(?))), "
        "list(distinct radio order by radio), list(distinct mcc) from c",
        [area.wkt],
    ).fetchone()
    assert n == keys  # one row per cell
    assert outside == 0
    assert n == 3_445  # of 7,143 cells over the ward's bounding box
    assert radios == ["LTE", "NR", "UMTS"]
    assert mcc == [440]
