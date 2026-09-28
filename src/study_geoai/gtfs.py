"""The Taito City community bus (Megurin) GTFS-JP feed, as DuckDB views.

The feed is a single 78 KB zip from the ODPT public API (no registration),
licensed CC BY 4.0. It is unpacked once into the OS temp directory. Every
column is read as text: stop and trip IDs contain Japanese, and GTFS times
can pass 24:00, so nothing is left to type inference.
"""

import io
import urllib.request
import zipfile

import duckdb

from study_geoai.aoi import CACHE_DIR

MEGURIN_DATE = "20251028"
MEGURIN_URL = (
    "https://api-public.odpt.org/api/v4/files/odpt/TokyoTaitoCity/megurinCCBY40.zip"
    f"?date={MEGURIN_DATE}"
)
TABLES = [
    "agency", "agency_jp", "calendar", "calendar_dates", "fare_attributes", "feed_info",
    "office_jp", "routes", "shapes", "stop_times", "stops", "transfers", "trips",
]  # fmt: skip


def megurin(con: duckdb.DuckDBPyConnection) -> None:
    """Create one view per GTFS table (routes, stops, trips, stop_times, ...)."""
    folder = CACHE_DIR / f"megurin-{MEGURIN_DATE}"
    if not (folder / "trips.txt").exists():
        req = urllib.request.Request(MEGURIN_URL, headers={"User-Agent": "study-geoai"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        tmp = folder.with_suffix(".partial")
        tmp.mkdir(parents=True, exist_ok=True)
        zipfile.ZipFile(io.BytesIO(data)).extractall(tmp)
        tmp.rename(folder)
    for table in TABLES:
        con.sql(
            f"create or replace view {table} as select * from read_csv("
            f"'{folder / table}.txt', header = true, all_varchar = true)"
        )
