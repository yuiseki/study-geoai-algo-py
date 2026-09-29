"""OSM roads of the 23 wards, from the frozen osm-tokyo23-src-2026-08 on Hugging Face.

The line table (osm2pgsql schema, EPSG:3857) has no node IDs, only the shape
of each way. Ways meet at shared nodes, so their shapes share those vertices
exactly; walk_edges relies on that to rebuild the junctions.

The table has no bbox column and is not sorted in space, so reading shapes
reads nearly the whole file (26 MB); each area's roads are cached.
"""

import duckdb
import numpy as np

from study_geoai.aoi import Area, cache_path, writing
from study_geoai.features import METRIC_CRS

OSM_REVISION = "e60e017f6a77fa81014b11ca953ae0b2b177edaf"
LINE = (
    "https://huggingface.co/datasets/yuiseki/osm-tokyo23-src-2026-08/resolve/"
    f"{OSM_REVISION}/parquet/planet_osm_line.parquet"
)
BUFFER_DEG = 0.01  # about 1 km: routes may leave the area and come back

WALK = {"footway", "path", "pedestrian", "steps", "corridor", "elevator", "living_street",
        "residential", "service", "unclassified", "track", "cycleway", "bridleway",
        "tertiary", "tertiary_link", "secondary", "secondary_link", "primary",
        "primary_link", "trunk", "trunk_link"}  # fmt: skip
NO_ENTRY = {"private", "no"}
FOOT_OK = {"yes", "designated", "permissive"}


def walkable(highway: str | None, access: str | None, foot: str | None) -> bool:
    """Can a pedestrian use this way? Motorways and unbuilt roads are left out;
    access=private or no shuts it unless foot says otherwise; foot=no shuts it."""
    if highway not in WALK or foot == "no":
        return False
    return access not in NO_ENTRY or foot in FOOT_OK


def roads(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    """Ways with a highway tag within the area's bbox plus BUFFER_DEG, in METRIC_CRS."""
    path = cache_path("osm-tokyo23", OSM_REVISION[:12], f"roads-6677-{area.name}")
    if not path.exists():
        xmin, ymin, xmax, ymax = area.bbox
        with writing(path) as tmp:
            con.sql(f"""
                copy (
                    with l as (
                        select osm_id, highway, name, oneway, access, foot, bridge, tunnel,
                               layer, st_transform(st_geomfromwkb(way), 'EPSG:3857', 'EPSG:4326',
                                                   always_xy := true) as g
                        from '{LINE}' where highway is not null
                    )
                    select * exclude (g),
                           st_setcrs(st_transform(g, 'EPSG:4326', '{METRIC_CRS}',
                                                  always_xy := true), '{METRIC_CRS}') as geometry
                    from l
                    where st_intersects(g, st_makeenvelope({xmin - BUFFER_DEG}, {ymin - BUFFER_DEG},
                                                           {xmax + BUFFER_DEG}, {ymax + BUFFER_DEG}))
                ) to '{tmp}' (format parquet)
            """)
    return con.read_parquet(str(path))


def walk_edges(con: duckdb.DuckDBPyConnection, area: Area) -> np.ndarray:
    """(x1, y1, x2, y2, length) in metres, one row per pair of consecutive vertices
    of every walkable way. Coordinates are rounded to 1 mm so shared vertices match."""
    r = roads(con, area)
    combos = r.aggregate("highway, access, foot").fetchall()
    con.execute(
        "create or replace temp table _walk (highway varchar, access varchar, foot varchar)"
    )
    keep = [c for c in combos if walkable(*c)]
    if keep:
        con.executemany("insert into _walk values (?, ?, ?)", keep)
    r.create_view("_roads")
    rows = con.sql("""
        with w as (
            select g.geometry from _roads g
            join _walk k on k.highway = g.highway
                        and k.access is not distinct from g.access
                        and k.foot is not distinct from g.foot
        ),
        v as (
            select geometry, unnest(generate_series(1, st_npoints(geometry)::integer - 1)) as i from w
        ),
        e as (
            select round(st_x(st_pointn(geometry, i::integer)), 3) as x1,
                   round(st_y(st_pointn(geometry, i::integer)), 3) as y1,
                   round(st_x(st_pointn(geometry, (i + 1)::integer)), 3) as x2,
                   round(st_y(st_pointn(geometry, (i + 1)::integer)), 3) as y2
            from v
        )
        select x1, y1, x2, y2, sqrt((x2 - x1) ^ 2 + (y2 - y1) ^ 2) from e
        where x1 != x2 or y1 != y2
    """).fetchnumpy()
    con.sql("drop view _roads")
    return np.column_stack([rows[k] for k in rows]).astype(float)
