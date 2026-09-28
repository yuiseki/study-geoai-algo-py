"""An in-memory DuckDB that reads remote GeoParquet with range requests.

The host this runs on has no swap: running out of memory hangs the machine
instead of killing the process. So memory, threads and spill-to-disk are
capped here, for every step.
"""

import tempfile
from pathlib import Path

import duckdb

MEMORY_LIMIT = "4GB"
THREADS = 8
SPILL_DIR = Path(tempfile.gettempdir()) / "study-geoai" / "duckdb-tmp"
SPILL_LIMIT = "8GB"


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.sql(f"set memory_limit = '{MEMORY_LIMIT}'")
    con.sql(f"set threads = {THREADS}")
    con.sql(f"set temp_directory = '{SPILL_DIR}'")
    con.sql(f"set max_temp_directory_size = '{SPILL_LIMIT}'")
    # Row order is never relied on; dropping it lets COPY stream instead of buffering.
    con.sql("set preserve_insertion_order = false")
    con.sql("install spatial; load spatial; install httpfs; load httpfs")
    # Overture's buckets are in us-west-2 and allow anonymous reads.
    con.sql("set s3_region = 'us-west-2'")
    con.sql("set http_timeout = 20000")
    con.sql("set enable_progress_bar = false")
    return con
