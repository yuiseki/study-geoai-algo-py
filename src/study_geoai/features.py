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

from study_geoai import census, mesh, michiyomi, ookla, opencellid, overture, worldpop
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


def tile_cells(
    con: duckdb.DuckDBPyConnection, area: Area, year: int = 2026, quarter: int = 2
) -> duckdb.DuckDBPyRelation:
    """OpenCelliD cells per Ookla tile: n_cells, n_lte, n_nr, operators, nearest_m, mean_range_m.

    nearest_m is from the tile centre to the nearest cell in the area within about 2 km.
    """
    path = cache_path("features", f"opencellid-{opencellid.VERSION}-ookla{year}q{quarter}",
                      f"tile-cells-{area.name}")  # fmt: skip
    if not path.exists():
        ookla.tiles(con, area, "mobile", year, quarter).create_view("_t")
        opencellid.cells(con, area).create_view("_c")
        with writing(path) as tmp:
            con.sql(f"""
                copy (
                    with inside as (
                        select _t.quadkey, count(*) as n_cells,
                               count(*) filter (where _c.radio = 'LTE') as n_lte,
                               count(*) filter (where _c.radio = 'NR') as n_nr,
                               count(distinct _c.net) as operators,
                               avg(_c.range_m) as mean_range_m
                        from _t join _c on st_contains(_t.geometry, _c.geometry)
                        group by _t.quadkey
                    ),
                    nearest as (
                        select _t.quadkey,
                               min(st_distance_sphere(st_centroid(_t.geometry), _c.geometry))
                                 as nearest_m
                        from _t join _c on st_dwithin(st_centroid(_t.geometry), _c.geometry, 0.02)
                        group by _t.quadkey
                    )
                    select _t.quadkey, coalesce(i.n_cells, 0) as n_cells,
                           coalesce(i.n_lte, 0) as n_lte, coalesce(i.n_nr, 0) as n_nr,
                           coalesce(i.operators, 0) as operators, n.nearest_m, i.mean_range_m
                    from _t left join inside i using (quadkey) left join nearest n using (quadkey)
                    order by _t.quadkey
                ) to '{tmp}' (format parquet)
            """)
        con.sql("drop view _t; drop view _c")
    return con.read_parquet(str(path))


KINDS = ("food", "retail", "lodging", "culture", "other")
_RULES = [
    ("retail", ("store", "shop", "market", "mall", "boutique", "outlet")),
    ("food", ("restaurant", "bar", "cafe", "eatery", "coffee", "bakery", "pub", "izakaya",
              "food", "dessert", "tea", "diner", "bistro")),
    ("lodging", ("hotel", "hostel", "inn", "motel", "lodging", "accommodation", "guest_house",
                 "ryokan")),
    ("culture", ("worship", "historic", "museum", "gallery", "venue", "theater", "theatre",
                 "temple", "shrine", "landmark", "monument", "attraction")),
]  # fmt: skip


def place_kind(category: str | None) -> str:
    """One of KINDS for an Overture basic_category, by the words in its name.

    The first matching rule wins, so food_and_beverage_store is retail and coffee_shop,
    which also contains shop, is caught by retail first; coffee_shop is special-cased.
    """
    if not category:
        return "other"
    if category in ("coffee_shop", "tea_shop", "juice_shop", "donut_shop", "ice_cream_shop"):
        return "food"
    for kind, words in _RULES:
        if any(w in category for w in words):
            return kind
    return "other"


METRIC_CRS = "EPSG:6677"  # JGD2011 plane rectangular IX, which covers Tokyo


def place_points(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    """Overture places as metres in METRIC_CRS, for distance-based clustering.

    Columns: id, name, kind (one of KINDS), x, y, code5 and town (the census small
    area's name; NULL for the few places outside every small area), lon, lat.
    """
    census.small_areas(con, area).create_view("_sa")
    places = overture.read(con, area, "places", "place", ["id", "names", "basic_category"])
    cats = places.aggregate("basic_category").fetchall()
    con.execute("create or replace temp table _kind (basic_category varchar, kind varchar)")
    con.executemany("insert into _kind values (?, ?)", [(c, place_kind(c)) for (c,) in cats])
    places.create_view("_pp")
    return con.sql(f"""
        select p.id, p.names.primary as name, coalesce(k.kind, 'other') as kind,
               st_x(m) as x, st_y(m) as y, sa.code5, sa.name as town,
               st_x(p.geometry) as lon, st_y(p.geometry) as lat
        from (select *, st_transform(geometry, 'EPSG:4326', '{METRIC_CRS}', always_xy := true) as m
              from _pp) p
        left join _kind k on k.basic_category is not distinct from p.basic_category
        left join _sa sa on st_contains(sa.geometry, p.geometry)
        order by p.id
    """)


MIN_SCENES = 30  # fewer street scenes than this make a cell's averages too noisy


def street_cells(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    """michiyomi street measures averaged per 250 m cell (cell_250m), for cells with at
    least MIN_SCENES scenes (quarantined scenes left out).

    Shares are taken among the scenes where the answer is known (不明 and 該当なし
    left out): undergrounded_share, wires_high_share (wire_density 高),
    block_paving_share (surface ブロック) and poor_sight_share (sight_distance 不良).
    sidewalk_share is the share of scenes with a sidewalk seen on either side.
    """
    michiyomi.scenes(con, area).create_view("_sc")

    def share(column, hit, known):
        known = ", ".join(f"'{k}'" for k in known)
        return f"avg(({column} = '{hit}')::int) filter (where {column} in ({known}))"

    return con.sql(f"""
        select cell_250m, count(*) as n_scenes,
               avg(roadway_width_m) as roadway_width_m,
               avg((coalesce(sidewalk_left_width_m, 0) + coalesce(sidewalk_right_width_m, 0))
                   / nullif((sidewalk_left_width_m is not null)::int
                            + (sidewalk_right_width_m is not null)::int, 0))
                 as sidewalk_width_m,
               avg((sidewalk_left = 'あり' or sidewalk_right = 'あり')::int) as sidewalk_share,
               avg(poles_visible) as poles, avg(lights_road) as lights,
               avg(green_ratio) as green, avg(colorfulness) as colorfulness,
               {share("undergrounded", "無電柱化済", ["無電柱化済", "架空線あり"])}
                 as undergrounded_share,
               {share("wire_density", "高", ["なし", "低", "中", "高"])} as wires_high_share,
               {
        share(
            "surface",
            "ブロック",
            ["アスファルト", "ブロック", "コンクリート", "混在", "砂利", "土・苔"],
        )
    } as block_paving_share,
               {share("sight_distance", "不良", ["良", "不良"])} as poor_sight_share,
               {michiyomi.cell_sql()} as geometry
        from _sc where quarantined = 0
        group by cell_250m having count(*) >= {MIN_SCENES}
        order by cell_250m
    """)


def small_area_profiles(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    """small_areas plus POI kind shares and michiyomi street averages per small area.

    share_<kind>: share of the small area's places of each kind (NULL without places).
    n_scenes, undergrounded_share, mean_green, mean_poles, mean_roadway_m: michiyomi
    scenes inside the small area (quarantined scenes left out).
    """
    path = cache_path("features", f"{overture.RELEASE}-{michiyomi.MICHIYOMI_REVISION[:12]}",
                      f"profiles-{area.name}")  # fmt: skip
    if not path.exists():
        small_areas(con, area).create_view("_sa")
        places = overture.read(con, area, "places", "place", ["id", "basic_category"])
        cats = places.aggregate("basic_category").fetchall()
        con.execute("create or replace temp table _kind (basic_category varchar, kind varchar)")
        con.executemany("insert into _kind values (?, ?)", [(c, place_kind(c)) for (c,) in cats])
        places.create_view("_p")
        michiyomi.scenes(con, area).create_view("_s")
        shares = ", ".join(
            f"avg((coalesce(k.kind, 'other') = '{k}')::int) as share_{k}" for k in KINDS
        )
        with writing(path) as tmp:
            con.sql(f"""
                copy (
                    with p as (
                        select sa.key11, {shares}
                        from _sa sa join _p on st_contains(sa.geometry, _p.geometry)
                        left join _kind k on k.basic_category is not distinct from _p.basic_category
                        group by sa.key11
                    ),
                    s as (
                        select sa.key11, count(*) as n_scenes,
                               avg((_s.undergrounded = '無電柱化済')::int)
                                 filter (where _s.undergrounded in ('無電柱化済', '架空線あり'))
                                 as undergrounded_share,
                               avg(_s.green_ratio) as mean_green,
                               avg(_s.poles_visible) as mean_poles,
                               avg(_s.roadway_width_m) as mean_roadway_m
                        from _sa sa join _s on st_contains(sa.geometry, _s.geometry)
                        where _s.quarantined = 0
                        group by sa.key11
                    )
                    select sa.* exclude (geometry), p.* exclude (key11),
                           coalesce(s.n_scenes, 0) as n_scenes,
                           s.* exclude (key11, n_scenes), sa.geometry
                    from _sa sa left join p using (key11) left join s using (key11)
                    order by sa.key11
                ) to '{tmp}' (format parquet)
            """)
        for view in ("_sa", "_p", "_s"):
            con.sql(f"drop view {view}")
        con.sql("drop table _kind")
    return con.read_parquet(str(path))


def grid_profiles(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    """One row per 3rd mesh (about 1 km) whose centre lies in the area.

    Everything is counted where its point falls: WorldPop 2025 100 m pixel centres
    (population), Overture building centroids (n_buildings, coverage) and places
    (place_density, share_<kind>), michiyomi scenes (undergrounded_share, mean_green,
    mean_poles) and OpenCelliD cells (cell_density).
    """
    path = cache_path("features", f"{overture.RELEASE}-mesh3", f"grid-{area.name}")
    if not path.exists():
        worldpop.grid(con, area, 2025).create_view("_w")
        overture.read(
            con, area, "buildings", "building", ["id", "height", "num_floors"]
        ).create_view("_b")
        places = overture.read(con, area, "places", "place", ["id", "basic_category"])
        cats = places.aggregate("basic_category").fetchall()
        con.execute("create or replace temp table _kind (basic_category varchar, kind varchar)")
        con.executemany("insert into _kind values (?, ?)", [(c, place_kind(c)) for (c,) in cats])
        places.create_view("_p")
        michiyomi.scenes(con, area).create_view("_s")
        opencellid.cells(con, area).create_view("_c")
        code = mesh.sql("lon", "lat")
        shares = ", ".join(
            f"avg((coalesce(k.kind, 'other') = '{k}')::int) as share_{k}" for k in KINDS
        )
        codes = con.sql(f"select distinct {code} as mesh from _w").fetchall()
        con.execute("create or replace temp table _m (mesh bigint, geometry geometry)")
        con.executemany(
            "insert into _m values (?, st_makeenvelope(?, ?, ?, ?))",
            [(c, *mesh.bounds(c)) for (c,) in codes],
        )
        with writing(path) as tmp:
            con.execute(
                f"""
                copy (
                    with m as (
                        select mesh, geometry, {AREA_KM2.format(g="geometry")} as area_km2
                        from _m where st_contains(st_geomfromtext(?), st_centroid(geometry))
                    ),
                    w as (select {code} as mesh, sum(population) as population from _w group by 1),
                    b as (
                        select {code} as mesh, count(*) as n_buildings,
                               sum({AREA_KM2.format(g="geometry")}) as footprint_km2
                        from (select *, st_x(st_centroid(geometry)) as lon,
                                     st_y(st_centroid(geometry)) as lat from _b)
                        group by 1
                    ),
                    p as (
                        select {code} as mesh, count(*) as n_places, {shares}
                        from (select _p.*, st_x(geometry) as lon, st_y(geometry) as lat from _p) _p
                        left join _kind k on k.basic_category is not distinct from _p.basic_category
                        group by 1
                    ),
                    s as (
                        select {code} as mesh, count(*) as n_scenes,
                               avg((undergrounded = '無電柱化済')::int)
                                 filter (where undergrounded in ('無電柱化済', '架空線あり'))
                                 as undergrounded_share,
                               avg(green_ratio) as mean_green, avg(poles_visible) as mean_poles
                        from _s where quarantined = 0 group by 1
                    ),
                    c as (select {code} as mesh, count(*) as n_cells from _c group by 1)
                    select m.mesh, m.area_km2,
                           coalesce(w.population, 0) as population,
                           coalesce(w.population, 0) / m.area_km2 as density,
                           coalesce(b.n_buildings, 0) as n_buildings,
                           coalesce(b.footprint_km2, 0) / m.area_km2 as coverage,
                           coalesce(p.n_places, 0) as n_places,
                           coalesce(p.n_places, 0) / m.area_km2 as place_density,
                           p.* exclude (mesh, n_places),
                           coalesce(s.n_scenes, 0) as n_scenes, s.* exclude (mesh, n_scenes),
                           coalesce(c.n_cells, 0) / m.area_km2 as cell_density,
                           m.geometry
                    from m left join w using (mesh) left join b using (mesh)
                    left join p using (mesh) left join s using (mesh) left join c using (mesh)
                    order by m.mesh
                ) to '{tmp}' (format parquet)
                """,
                [area.wkt],
            )
        for view in ("_w", "_b", "_p", "_s", "_c"):
            con.sql(f"drop view {view}")
        con.sql("drop table _kind; drop table _m")
    return con.read_parquet(str(path))
