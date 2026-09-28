"""2020 census small areas (e-Stat) for a study area, read at runtime.

The estat-boundary-2020 dataset on Hugging Face has one parquet file per
prefecture; Tokyo is r2ka13.parquet (6.3 MB). Its KEY_CODE is not unique: one
small area can be split into several polygons, and KEY_CODE is sometimes only a
prefix. So the key is rebuilt as PREF + CITY + S_AREA (11 digits) and the parts
are merged, adding up their population and households.
"""

import duckdb

from study_geoai.aoi import Area, cache_path, writing

ESTAT_REVISION = "823195c40e1055e2c1b3c0a635369f8c82b6c3fb"
TOKYO = (
    "https://huggingface.co/datasets/yuiseki/estat-boundary-2020/resolve/"
    f"{ESTAT_REVISION}/parquet/r2ka13.parquet"
)


def small_areas(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    """key11, code5, name, population, households and geometry of each small area."""
    path = cache_path("estat-boundary", ESTAT_REVISION, f"small-areas-{area.name}")
    if not path.exists():
        codes = ", ".join(f"'{c}'" for c in area.codes)
        with writing(path) as tmp:
            con.sql(f"""
                copy (
                    select PREF || CITY || S_AREA as key11,
                           PREF || CITY as code5,
                           any_value(CITY_NAME) as city_name,
                           any_value(S_NAME) as name,
                           sum(cast(JINKO as bigint)) as population,
                           sum(cast(SETAI as bigint)) as households,
                           st_union_agg(st_geomfromwkb(geometry)) as geometry
                    from read_parquet('{TOKYO}')
                    where PREF || CITY in ({codes})
                    group by all
                ) to '{tmp}' (format parquet)
            """)
    return con.read_parquet(str(path))
