"""An in-memory DuckDB that reads remote GeoParquet with range requests."""

import duckdb


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.sql("install spatial; load spatial; install httpfs; load httpfs")
    # Overture's buckets are in us-west-2 and allow anonymous reads.
    con.sql("set s3_region = 'us-west-2'")
    con.sql("set http_timeout = 20000")
    con.sql("set enable_progress_bar = false")
    return con
