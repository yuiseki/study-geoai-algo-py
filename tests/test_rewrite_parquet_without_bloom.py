import importlib.util
import json
from pathlib import Path

import duckdb
import pytest

_spec = importlib.util.spec_from_file_location(
    "rewrite", Path(__file__).parents[1] / "scripts" / "rewrite_parquet_without_bloom.py"
)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def _con():
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    return con


def _with_bloom(path: Path, geometry: bool = False) -> None:
    geom = ", st_point(i % 180, i % 90) as geometry" if geometry else ""
    _con().execute(
        f"copy (select i, lpad((i % 47)::varchar, 2, '0') as code{geom} "
        f"from range(20000) t(i) order by code, i) "
        f"to '{path}' (format parquet, compression zstd, row_group_size 5000)"
    )


def _blooms(path: Path) -> int:
    return duckdb.sql(
        f"select count(*) filter (where bloom_filter_offset is not null) from parquet_metadata('{path}')"
    ).fetchone()[0]


def test_bloom_filters_go_and_rows_stay_in_order(tmp_path):
    p = tmp_path / "a.parquet"
    _with_bloom(p)
    before = duckdb.sql(f"select * from '{p}'").fetchall()
    rgs = m.row_group_rows(p)
    assert _blooms(p) > 0
    info = m.rewrite(p)
    assert _blooms(p) == 0
    assert duckdb.sql(f"select * from '{p}'").fetchall() == before
    assert m.row_group_rows(p) == rgs  # uniform groups come back the same
    assert info["rows"] == 20000 and info["bytes"] == p.stat().st_size


def test_geoparquet_metadata_survives(tmp_path):
    p = tmp_path / "g.parquet"
    _with_bloom(p, geometry=True)
    m.rewrite(p)
    kv = dict(
        duckdb.sql(f"select decode(key), decode(value) from parquet_kv_metadata('{p}')").fetchall()
    )
    assert json.loads(kv["geo"])["primary_column"] == "geometry"


def test_a_file_without_bloom_filters_is_left_alone(tmp_path):
    p = tmp_path / "b.parquet"
    _con().execute(f"copy (select 1 as i) to '{p}' (format parquet, write_bloom_filter false)")
    mtime = p.stat().st_mtime_ns
    assert m.rewrite(p) is None
    assert p.stat().st_mtime_ns == mtime


def test_ordered_digest_sees_a_swap(tmp_path):
    a, b = tmp_path / "a.parquet", tmp_path / "b.parquet"
    con = _con()
    con.execute(f"copy (select * from (values (1), (2)) t(i)) to '{a}' (format parquet)")
    con.execute(f"copy (select * from (values (2), (1)) t(i)) to '{b}' (format parquet)")
    assert m.ordered_digest(a) != m.ordered_digest(b)
    assert m.ordered_digest(a) == m.ordered_digest(a)


def test_a_rewrite_that_changed_rows_is_not_placed(tmp_path, monkeypatch):
    p = tmp_path / "c.parquet"
    _with_bloom(p)
    original = p.read_bytes()
    digests = iter(range(10))
    monkeypatch.setattr(m, "ordered_digest", lambda path: next(digests))
    with pytest.raises(RuntimeError, match="rows differ"):
        m.rewrite(p)
    assert p.read_bytes() == original
    assert not list(tmp_path.glob("*.part"))


def test_swap_in_docs_replaces_hashes_and_sizes(tmp_path):
    doc = tmp_path / "manifest.json"
    doc.write_text('{"a.parquet": {"bytes": 111927571, "sha256": "ab' + "0" * 62 + '"}}')
    readme = tmp_path / "README.md"
    readme.write_text("| a.parquet | 38,079,507 | 111,927,571 |\n| b | 1 | 111927571999 |\n")
    old = {"bytes": 111927571, "sha256": "ab" + "0" * 62}
    new = {"bytes": 104065028, "sha256": "cd" + "1" * 62}
    changed = m.swap_in_docs([doc, readme], old, new)
    assert changed == {doc: 2, readme: 1}
    assert doc.read_text() == '{"a.parquet": {"bytes": 104065028, "sha256": "cd' + "1" * 62 + '"}}'
    assert "| 104,065,028 |" in readme.read_text()
    assert "111927571999" in readme.read_text()  # a longer number is not touched
