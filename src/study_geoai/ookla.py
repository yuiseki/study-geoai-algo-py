"""Ookla Speedtest performance tiles for a study area, read at runtime.

Read from a mirror on z.yuiseki.net, not from Ookla's bucket. The originals
cover the world in one parquet file per quarter and type with only four row
groups, and the bucket served 39 KB/s to 1 MB/s on 2026-09-28, so even a
count for Taito City did not finish in 60 s. The mirror keeps every row and
column and the same path layout, adds geometry and a bbox struct, and uses
row groups of 20,480 rows in quadkey order: Taito City reads about 1 MB in
0.5 s. Only 2026 Q2 is mirrored so far; see /static/ookla/README.md there.

quarter, type and year are not columns in the files; they come from the path.
Licensed CC BY-NC-SA 4.0 (non-commercial, attribution, share-alike).
"""

import duckdb

from study_geoai.aoi import Area, cache_path, writing

MIRROR = "https://z.yuiseki.net/static/ookla/parquet/performance"
COLUMNS = [
    "quadkey", "avg_d_kbps", "avg_u_kbps", "avg_lat_ms",
    "avg_lat_down_ms", "avg_lat_up_ms", "tests", "devices",
]  # fmt: skip


def url(type_: str, year: int, quarter: int) -> str:
    month = 3 * (quarter - 1) + 1
    return (
        f"{MIRROR}/type={type_}/year={year}/quarter={quarter}/"
        f"{year}-{month:02d}-01_performance_{type_}_tiles.parquet"
    )


def tiles(
    con: duckdb.DuckDBPyConnection, area: Area, type_: str, year: int, quarter: int
) -> duckdb.DuckDBPyRelation:
    """Zoom-16 tiles of one quarter that meet the area: COLUMNS and the tile polygon."""
    path = cache_path("ookla", f"{year}q{quarter}", f"{type_}-{area.name}")
    if not path.exists():
        west, south, east, north = area.bbox
        with writing(path) as tmp:
            con.execute(
                f"""
                copy (
                    select {", ".join(COLUMNS)}, geometry
                    from read_parquet('{url(type_, year, quarter)}')
                    where bbox.xmin < {east} and bbox.xmax > {west}
                      and bbox.ymin < {north} and bbox.ymax > {south}
                      and st_intersects(geometry, st_geomfromtext(?))
                ) to '{tmp}' (format parquet)
                """,
                [area.wkt],
            )
    return con.read_parquet(str(path))
