"""国土数値情報 (National Land Numerical Information) for a study area, from the mirror."""

import pytest

from study_geoai import aoi, ksj
from study_geoai.db import connect


def test_every_dataset_points_at_the_mirror():
    assert set(ksj.DATASETS) == {"P04", "P29", "A31a", "mesh500r6"}
    for files in ksj.DATASETS.values():
        assert all(f.startswith(f"{ksj.MIRROR}/") and f.endswith(".parquet") for f in files)
    # The Kanto bureau flood file is split in two to stay under Cloudflare's 512 MB cache limit.
    assert sum("A31a-25_83_10_GEOJSON-part" in f for f in ksj.DATASETS["A31a"]) == 2


@pytest.mark.network
@pytest.mark.parametrize("dataset", ["P04", "P29", "A31a", "mesh500r6"])
def test_taito_rows_lie_in_the_ward(dataset):
    con = connect()
    area = aoi.load("taito", con)
    ksj.read(con, area, dataset).create_view("k")
    n, outside = con.execute(
        "select count(*), count(*) filter (where not st_intersects(geometry, st_geomfromtext(?))) "
        "from k",
        [area.wkt],
    ).fetchone()
    assert n > 0
    assert outside == 0
