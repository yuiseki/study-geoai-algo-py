"""Tables for the study steps: one row per census small area (町丁目).

Built from the other readers at runtime, for either study area:

- population, households: 2020 census (census.small_areas)
- area_km2: the small area on the ellipsoid, density = population / area_km2
- n_buildings, footprint_km2, coverage: Overture buildings whose centroid lies in
  the small area; coverage = footprint_km2 / area_km2 (like a building coverage ratio)
- mean_floors, floors_known: Overture num_floors, known for about 15 % of Taito's
  buildings, so mean_floors is over those only and floors_known is their share
- n_places, place_density: Overture places (POIs) in the small area

tiles: one row per Ookla zoom-16 tile that meets the area (about 610 m), with
mobile speeds of 2026 Q2 and, inside the tile, WorldPop 2025 population
(100 m pixels by centre), Overture buildings (by centroid) and places, and
michiyomi scenes (share undergrounded, mean visible poles, mean green).
"""

import duckdb

from study_geoai import census, michiyomi, ookla, overture, worldpop
from study_geoai.aoi import Area, cache_path, writing

AREA_KM2 = "st_area_spheroid(st_flipcoordinates({g})) / 1e6"


def small_areas(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    path = cache_path("features", overture.RELEASE, f"small-areas-{area.name}")
    if not path.exists():
        census.small_areas(con, area).create_view("_sa")
        overture.read(
            con, area, "buildings", "building", ["id", "height", "num_floors"]
        ).create_view("_b")
        overture.read(con, area, "places", "place", ["id", "basic_category"]).create_view("_p")
        with writing(path) as tmp:
            con.sql(f"""
                copy (
                    with sa as (
                        select key11, code5, city_name, name, population, households, geometry,
                               {AREA_KM2.format(g="geometry")} as area_km2
                        from _sa
                    ),
                    b as (
                        select sa.key11, count(*) as n_buildings,
                               sum({AREA_KM2.format(g="_b.geometry")}) as footprint_km2,
                               avg(_b.num_floors) as mean_floors,
                               count(_b.num_floors) / count(*) as floors_known
                        from sa join _b on st_contains(sa.geometry, st_centroid(_b.geometry))
                        group by sa.key11
                    ),
                    p as (
                        select sa.key11, count(*) as n_places
                        from sa join _p on st_contains(sa.geometry, _p.geometry)
                        group by sa.key11
                    )
                    select sa.key11, sa.code5, sa.city_name, sa.name, sa.population,
                           sa.households, sa.area_km2,
                           sa.population / sa.area_km2 as density,
                           coalesce(b.n_buildings, 0) as n_buildings,
                           coalesce(b.footprint_km2, 0) as footprint_km2,
                           coalesce(b.footprint_km2, 0) / sa.area_km2 as coverage,
                           b.mean_floors, coalesce(b.floors_known, 0) as floors_known,
                           coalesce(p.n_places, 0) as n_places,
                           coalesce(p.n_places, 0) / sa.area_km2 as place_density,
                           sa.geometry
                    from sa left join b using (key11) left join p using (key11)
                    order by sa.key11
                ) to '{tmp}' (format parquet)
            """)
        for view in ("_sa", "_b", "_p"):
            con.sql(f"drop view {view}")
    return con.read_parquet(str(path))


def tiles(
    con: duckdb.DuckDBPyConnection, area: Area, year: int = 2026, quarter: int = 2
) -> duckdb.DuckDBPyRelation:
    path = cache_path("features", f"{overture.RELEASE}-ookla{year}q{quarter}", f"tiles-{area.name}")
    if not path.exists():
        ookla.tiles(con, area, "mobile", year, quarter).create_view("_t")
        worldpop.grid(con, area, 2025).create_view("_w")
        overture.read(
            con, area, "buildings", "building", ["id", "height", "num_floors"]
        ).create_view("_b")
        overture.read(con, area, "places", "place", ["id", "basic_category"]).create_view("_p")
        michiyomi.scenes(con, area).create_view("_s")
        with writing(path) as tmp:
            con.sql(f"""
                copy (
                    with t as (
                        select *, {AREA_KM2.format(g="geometry")} as area_km2 from _t
                    ),
                    w as (
                        select t.quadkey, sum(_w.population) as population
                        from t join _w on st_contains(t.geometry, st_point(_w.lon, _w.lat))
                        group by t.quadkey
                    ),
                    b as (
                        select t.quadkey, count(*) as n_buildings,
                               sum({AREA_KM2.format(g="_b.geometry")}) as footprint_km2
                        from t join _b on st_contains(t.geometry, st_centroid(_b.geometry))
                        group by t.quadkey
                    ),
                    p as (
                        select t.quadkey, count(*) as n_places
                        from t join _p on st_contains(t.geometry, _p.geometry)
                        group by t.quadkey
                    ),
                    s as (
                        select t.quadkey, count(*) as n_scenes,
                               avg((_s.undergrounded = '無電柱化済')::int)
                                 filter (where _s.undergrounded in ('無電柱化済', '架空線あり'))
                                 as undergrounded_share,
                               avg(_s.poles_visible) as mean_poles,
                               avg(_s.green_ratio) as mean_green
                        from t join _s on st_contains(t.geometry, _s.geometry)
                        where _s.quarantined = 0
                        group by t.quadkey
                    )
                    select t.quadkey, t.avg_d_kbps, t.avg_u_kbps, t.avg_lat_ms, t.tests, t.devices,
                           t.area_km2,
                           coalesce(w.population, 0) as population,
                           coalesce(b.n_buildings, 0) as n_buildings,
                           coalesce(b.footprint_km2, 0) / t.area_km2 as coverage,
                           coalesce(p.n_places, 0) as n_places,
                           coalesce(s.n_scenes, 0) as n_scenes,
                           s.undergrounded_share, s.mean_poles, s.mean_green,
                           st_x(st_centroid(t.geometry)) as lon, st_y(st_centroid(t.geometry)) as lat,
                           t.geometry
                    from t left join w using (quadkey) left join b using (quadkey)
                    left join p using (quadkey) left join s using (quadkey)
                    order by t.quadkey
                ) to '{tmp}' (format parquet)
            """)
        for view in ("_t", "_w", "_b", "_p", "_s"):
            con.sql(f"drop view {view}")
    return con.read_parquet(str(path))
