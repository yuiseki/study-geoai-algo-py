"""Overture Maps read at runtime, for one study area.

The STAC collection for each type lists one bbox per GeoParquet file, in item
order after a collection-wide bbox. Picking the overlapping files there first
means reading one file for Taito City instead of the footers of all 512
building files (18 s instead of 159 s). Within those files, the bbox column
lets DuckDB skip row groups. The rows clipped to the area are cached as a
parquet file in the OS temp directory.
"""

import json
import urllib.request

import duckdb

from study_geoai.aoi import Area, cache_path, writing

RELEASE = "2026-09-23.1"
STAC = "https://stac.overturemaps.org"


def overlapping(bboxes: list[list[float]], bbox: tuple[float, float, float, float]) -> list[int]:
    """Item positions whose bbox overlaps, given extent.spatial.bbox of a collection."""
    west, south, east, north = bbox
    return [
        i
        for i, (xmin, ymin, xmax, ymax) in enumerate(bboxes[1:])
        if xmin < east and xmax > west and ymin < north and ymax > south
    ]


def _json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "study-geoai"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def files(theme: str, type_: str, bbox: tuple[float, float, float, float]) -> list[str]:
    collection = _json(f"{STAC}/{RELEASE}/{theme}/{type_}/collection.json")
    bboxes = collection["extent"]["spatial"]["bbox"]
    items = [link["href"] for link in collection["links"] if link["rel"] == "item"]
    if len(bboxes) != len(items) + 1:
        raise ValueError(f"{theme}/{type_}: {len(bboxes)} bboxes for {len(items)} items")
    return [_json(items[i])["assets"]["aws"]["href"] for i in overlapping(bboxes, bbox)]


def read(
    con: duckdb.DuckDBPyConnection,
    area: Area,
    theme: str,
    type_: str,
    columns: list[str],
) -> duckdb.DuckDBPyRelation:
    """Rows of one Overture type that intersect the area, with the listed columns and geometry."""
    path = cache_path("overture", RELEASE, f"{theme}-{type_}-{area.name}-{'-'.join(columns)}")
    if not path.exists():
        urls = files(theme, type_, area.bbox)
        if not urls:
            raise ValueError(f"{theme}/{type_}: no file overlaps {area.name}")
        west, south, east, north = area.bbox
        sources = ", ".join(f"'{u}'" for u in urls)
        with writing(path) as tmp:
            con.execute(
                f"""
                copy (
                    select {", ".join(columns)}, geometry
                    from read_parquet([{sources}])
                    where bbox.xmin < {east} and bbox.xmax > {west}
                      and bbox.ymin < {north} and bbox.ymax > {south}
                      and st_intersects(geometry, st_geomfromtext(?))
                ) to '{tmp}' (format parquet)
                """,
                [area.wkt],
            )
    return con.read_parquet(str(path))
