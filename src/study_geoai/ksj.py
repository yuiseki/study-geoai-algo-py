"""国土数値情報 (MLIT's National Land Numerical Information) for a study area.

MLIT publishes only zip files, which cannot be read in part. The Tokyo files of
four datasets, all CC BY 4.0 for their latest year, were converted once to
GeoParquet (bbox column, Hilbert order, 10,240-row groups) and mirrored on
z.yuiseki.net under /static/ksj/; see README.md and LICENSE there for sources
and the required credit. Coordinates are JGD2011 (EPSG:6668), as published;
at this scale the difference from WGS 84 is well under a metre, so they are
compared with the ward polygons directly.

The flood file of the Kanto Regional Development Bureau is split into two
halves: at 677 MB, Cloudflare would not cache it and the first range request
sent the whole file (67 to 97 s); each half reads in under a second.
"""

import duckdb

from study_geoai.aoi import Area, cache_path, writing

MIRROR = "https://z.yuiseki.net/static/ksj"
VERSION = "2026-09-28"
DATASETS = {
    "P04": [f"{MIRROR}/P04/P04-20_13_GML.parquet"],
    "P29": [f"{MIRROR}/P29/P29-23_13_GML.parquet"],
    "A31a": [
        f"{MIRROR}/A31a/A31a-25_13_10_GEOJSON.parquet",
        f"{MIRROR}/A31a/A31a-25_13_20_GEOJSON.parquet",
        f"{MIRROR}/A31a/A31a-25_83_10_GEOJSON-part0.parquet",
        f"{MIRROR}/A31a/A31a-25_83_10_GEOJSON-part1.parquet",
    ],
    "mesh500r6": [f"{MIRROR}/mesh500r6/500m_mesh_2024_13_GEOJSON.parquet"],
}


def read(con: duckdb.DuckDBPyConnection, area: Area, dataset: str) -> duckdb.DuckDBPyRelation:
    """Rows of the dataset that meet the area, with every column (files unioned by name)."""
    path = cache_path("ksj", VERSION, f"{dataset}-{area.name}")
    if not path.exists():
        sources = ", ".join(f"'{u}'" for u in DATASETS[dataset])
        west, south, east, north = area.bbox
        with writing(path) as tmp:
            con.execute(
                f"""
                copy (
                    select * exclude (bbox)
                    from read_parquet([{sources}], union_by_name = true)
                    where bbox.xmin < {east} and bbox.xmax > {west}
                      and bbox.ymin < {north} and bbox.ymax > {south}
                      and st_intersects(geometry, st_geomfromtext(?))
                ) to '{tmp}' (format parquet)
                """,
                [area.wkt],
            )
    return con.read_parquet(str(path))
