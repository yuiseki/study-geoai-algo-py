"""The two study areas: Taito City (A) and the 23 wards of Tokyo (B).

Boundaries and 2020 census populations come from the jp-admin-2026-09 dataset on
Hugging Face, pinned to one revision. Its municipality table is a single 149 MB
row group, so the 23 wards are read once and kept as a parquet file in the OS
temp directory; later runs read that instead.
"""

import tempfile
from dataclasses import dataclass
from pathlib import Path

import duckdb

from study_geoai.db import connect

JP_ADMIN_REVISION = "c86cbe9f2200dadb441f5bde7a1e4b068aeaa7f0"
JP_ADMIN_MUNICIPALITIES = (
    "https://huggingface.co/datasets/yuiseki/jp-admin-2026-09/resolve/"
    f"{JP_ADMIN_REVISION}/municipalities.parquet"
)
CACHE_DIR = Path(tempfile.gettempdir()) / "study-geoai"

# code5 of the 23 special wards of Tokyo: 13101 Chiyoda to 13123 Edogawa.
TOKYO23 = tuple(f"131{n:02d}" for n in range(1, 24))
AREAS = {"taito": ("13106",), "tokyo23": TOKYO23}


@dataclass(frozen=True)
class Area:
    name: str
    codes: tuple[str, ...]
    population: int
    bbox: tuple[float, float, float, float]  # west, south, east, north
    wkt: str

    def contains(self, lon: float, lat: float) -> bool:
        con = duckdb.connect()
        con.sql("install spatial; load spatial")
        return con.execute(
            "select st_contains(st_geomfromtext(?), st_point(?, ?))", [self.wkt, lon, lat]
        ).fetchone()[0]


def cache_path(dataset: str, revision: str, part: str) -> Path:
    return CACHE_DIR / f"{dataset}-{revision[:12]}-{part}.parquet"


def _wards(con: duckdb.DuckDBPyConnection) -> Path:
    path = cache_path("jp-admin", JP_ADMIN_REVISION, "tokyo23")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        codes = ", ".join(f"'{c}'" for c in TOKYO23)
        tmp = path.with_suffix(".partial")
        con.sql(f"""
            copy (
                select code5, name, population, st_geomfromwkb(geometry) as geometry
                from read_parquet('{JP_ADMIN_MUNICIPALITIES}')
                where code5 in ({codes})
            ) to '{tmp}' (format parquet)
        """)
        tmp.rename(path)
    return path


def load(name: str, con: duckdb.DuckDBPyConnection | None = None) -> Area:
    codes = AREAS[name]
    con = con or connect()
    path = _wards(con)
    placeholders = ", ".join("?" for _ in codes)
    population, found, xmin, ymin, xmax, ymax, wkt = con.execute(
        f"""
        with g as (
            select sum(population) as population, count(*) as found,
                   st_union_agg(geometry) as geom
            from read_parquet(?) where code5 in ({placeholders})
        )
        select population, found, st_xmin(geom), st_ymin(geom), st_xmax(geom), st_ymax(geom),
               st_astext(geom)
        from g
        """,
        [str(path), *codes],
    ).fetchone()
    if found != len(codes):
        raise ValueError(f"{name}: expected {len(codes)} wards, found {found} in {path}")
    return Area(name, codes, int(population), (xmin, ymin, xmax, ymax), wkt)
