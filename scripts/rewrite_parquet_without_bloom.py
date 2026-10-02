"""Rewrite Parquet files without bloom filters, keeping every row where it was.

DuckDB writes bloom filters by default, and reads a column's filter in every
row group a query's filter touches, even those the min/max statistics rule
out. For a file read over HTTP that is a request per row group per filtered
column. The mirror scripts now write without them; this fixes files already
placed.

A file is rewritten only if it has bloom filters. The new file keeps the row
order and the GeoParquet metadata, and is placed only if its rows, read one by
one in order, hash the same as the original's. The row groups keep their
target size but not always their exact boundaries: a file written in parallel
has a few short groups, and a rewrite on one thread does not reproduce them.
The rows are in the same order, so the statistics skip the same way.

    uv run python scripts/rewrite_parquet_without_bloom.py /www/html/static/ksj/*/*.parquet
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import duckdb


def _con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    # one thread: the scan, the write and the digest all see the file's order
    con.execute("set threads = 1; set preserve_insertion_order = true; set memory_limit = '8GB'")
    con.execute("install spatial; load spatial")
    return con


def has_bloom_filters(path: Path) -> bool:
    return (
        duckdb.sql(
            f"select count(*) filter (where bloom_filter_offset is not null) "
            f"from parquet_metadata('{path}')"
        ).fetchone()[0]
        > 0
    )


def row_group_rows(path: Path) -> list[int]:
    return [
        r[1]
        for r in duckdb.sql(
            f"select distinct row_group_id, row_group_num_rows from parquet_metadata('{path}') "
            "order by row_group_id"
        ).fetchall()
    ]


def ordered_digest(path: Path) -> str:
    """A hash of every row in file order: the same rows in another order differ."""
    h = hashlib.sha256()
    con = _con()
    rel = con.sql(f"select hash(t) from read_parquet('{path}') t")
    while batch := rel.fetchmany(100_000):
        h.update(b"".join(v.to_bytes(8, "little") for (v,) in batch))
    return h.hexdigest()


def rewrite(path: Path) -> dict | None:
    """Rewrite one file in place without bloom filters; None if it had none."""
    if not has_bloom_filters(path):
        return None
    rgs = row_group_rows(path)
    tmp = path.with_name(path.name + ".part")
    con = _con()
    try:
        con.execute(
            f"copy (select * from read_parquet('{path}')) to '{tmp}' "
            f"(format parquet, compression zstd, row_group_size {max(rgs)}, "
            "write_bloom_filter false)"
        )
        if sum(row_group_rows(tmp)) != sum(rgs):
            raise RuntimeError(f"{path.name}: {sum(row_group_rows(tmp))} rows, not {sum(rgs)}")
        if ordered_digest(tmp) != ordered_digest(path):
            raise RuntimeError(f"{path.name}: rows differ after the rewrite")
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    after = row_group_rows(tmp)
    os.replace(tmp, path)
    return {
        "row_groups": [len(rgs), len(after)],
        "rows": sum(rgs),
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def main(argv: list[str]) -> int:
    for arg in argv:
        p = Path(arg)
        before = p.stat().st_size
        info = rewrite(p)
        if info is None:
            print(f"skip   {p}  (no bloom filters)")
        else:
            g = info["row_groups"]
            print(
                f"done   {p}  {before:,} -> {info['bytes']:,} bytes, "
                f"{info['rows']:,} rows, row groups {g[0]} -> {g[1]}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
