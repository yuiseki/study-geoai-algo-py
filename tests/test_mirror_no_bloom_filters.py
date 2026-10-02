"""Every Parquet a mirror script writes for z.yuiseki.net goes without bloom filters.

DuckDB writes bloom filters by default and reads a column's filter in every
row group a query's filter touches, even the row groups the min/max
statistics have already ruled out. Over HTTP that is one request per row
group per filtered column: a query on one ward and month of the MLIT mesh
data made 1,114 requests from the Hugging Face Hub and took 32 s, against 12
requests and 7 s without them. The mirrors are read over HTTP, so none of
them may carry bloom filters.
"""

import re
from pathlib import Path

import pytest

SCRIPTS = sorted((Path(__file__).parents[1] / "scripts").glob("mirror_*.py"))


def parquet_options(source: str) -> list[str]:
    """The option lists that follow 'format parquet' in a script's source."""
    return re.findall(r"\(format parquet[^)]*\)", source)


def test_the_check_sees_the_options():
    src = "copy (select 1) to 'x' (format parquet, compression zstd, write_bloom_filter false)"
    assert parquet_options(src) == ["(format parquet, compression zstd, write_bloom_filter false)"]


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_mirror_writes_without_bloom_filters(script):
    options = parquet_options(script.read_text())
    for opt in options:
        assert "write_bloom_filter false" in opt, f"{script.name}: {opt}"
