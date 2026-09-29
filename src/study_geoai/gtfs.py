"""Bus GTFS-JP feeds for Tokyo, as DuckDB views, read from a mirror.

The feeds are mirrored unchanged on z.yuiseki.net under /static/gtfs/, one
directory per version, so the same path always returns the same bytes. Toei
Bus in particular replaces its feed daily at a URL with no date in it. All
five are CC BY 4.0; sources, sha256 and credits are in the mirror's README.md
and LICENSE.

Each feed becomes a schema (megurin.trips, toei.stop_times, ...). Every column
is read as text: IDs contain Japanese, GTFS times can pass 24:00, and two
feeds write one-digit hours (6:50:00), so nothing is left to type inference.
"""

import io
import urllib.request
import zipfile

import duckdb

from study_geoai.aoi import CACHE_DIR

MIRROR = "https://z.yuiseki.net/static/gtfs"
FEEDS = {
    "megurin": "odpt/TokyoTaitoCity/megurinCCBY40/20251028/megurinCCBY40.zip",
    "toei": "odpt/Toei/ToeiBus-GTFS/20260928_030815/ToeiBus-GTFS.zip",
    "suginami": "odpt/TokyoSuginamiCity/GreenSlowMobility/20260601/GreenSlowMobility.zip",
    "arakawa": "gtfs-data.jp/arakawacity/sakura/f42df805-0434-4196-af64-c9641b284388/feed.zip",
    "katsushika": "gtfs-data.jp/katsushikacity/sakura/1f3a5571-ce79-492a-9751-5c2031d96cde/feed.zip",
}


def load(con: duckdb.DuckDBPyConnection, name: str) -> list[str]:
    """Create a schema named after the feed with one view per GTFS file; return the table names."""
    path = FEEDS[name]
    folder = CACHE_DIR / "gtfs" / path.removesuffix(".zip")
    if not (folder / "trips.txt").exists():
        req = urllib.request.Request(
            f"{MIRROR}/{path}", headers={"User-Agent": "study-geoai-algo-py"}
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        tmp = folder.with_suffix(".partial")
        tmp.mkdir(parents=True, exist_ok=True)
        zipfile.ZipFile(io.BytesIO(data)).extractall(tmp)
        tmp.rename(folder)
    con.sql(f"create schema if not exists {name}")
    tables = sorted(p.stem for p in folder.glob("*.txt"))
    for table in tables:
        con.sql(
            f"create or replace view {name}.{table} as select * from read_csv("
            f"'{folder / table}.txt', header = true, all_varchar = true)"
        )
    return tables


def seconds(column: str) -> str:
    """SQL expression turning a GTFS time (H:MM:SS or HH:MM:SS, may pass 24:00) into seconds."""
    parts = f"string_split({column}, ':')"
    return (
        f"(cast({parts}[1] as integer) * 3600 + cast({parts}[2] as integer) * 60"
        f" + cast({parts}[3] as integer))"
    )
