import importlib.util
import json
from pathlib import Path

import duckdb
import pytest

_spec = importlib.util.spec_from_file_location(
    "mirror_ourairports", Path(__file__).parents[1] / "scripts" / "mirror_ourairports.py"
)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


@pytest.mark.parametrize(
    ("name", "sql"),
    [
        ("id", "BIGINT"),
        ("airport_ref", "BIGINT"),
        ("threadRef", "BIGINT"),
        ("elevation_ft", "INTEGER"),
        ("frequency_khz", "INTEGER"),
        ("lighted", "INTEGER"),
        ("latitude_deg", "DOUBLE"),
        ("le_heading_degT", "DOUBLE"),
        ("frequency_mhz", "DOUBLE"),
        ("local_code", "VARCHAR"),
        ("iata_code", "VARCHAR"),
        ("date", "VARCHAR"),
    ],
)
def test_column_type(name, sql):
    assert m.column_type(name) == sql


def test_csv_rows_counts_records_not_lines(tmp_path):
    f = tmp_path / "c.csv"
    f.write_text('"id","body"\n1,"two\nlines"\n2,"x"\n', encoding="utf-8")
    assert m.csv_rows(f) == 2


def test_snapshot_date_is_the_utc_day_of_the_commit():
    assert m.snapshot_date("2026-10-01T01:53:30Z") == "2026-10-01"


def _load(tmp_path, text: str, geometry: bool = False):
    f = tmp_path / "t.csv"
    f.write_text(text, encoding="utf-8")
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    return con, con.sql(m.select_sql(con, f, geometry))


def test_select_keeps_leading_zeros_and_casts_numbers(tmp_path):
    con, rel = _load(tmp_path, '"id","code","local_code","elevation_ft"\n302811,"AD-02",02,11\n')
    assert rel.fetchone() == (302811, "AD-02", "02", 11)
    assert dict(zip(rel.columns, rel.types, strict=True)) == {
        "id": "BIGINT", "code": "VARCHAR", "local_code": "VARCHAR", "elevation_ft": "INTEGER",
    }  # fmt: skip


def test_select_strips_spaces_from_header_names(tmp_path):
    _, rel = _load(tmp_path, '"id", "threadRef", "body"\n1,2,"x"\n')
    assert rel.columns == ["id", "threadRef", "body"]
    assert rel.fetchone() == (1, 2, "x")


def test_select_adds_a_point_geometry(tmp_path):
    _, rel = _load(
        tmp_path, '"id","latitude_deg","longitude_deg"\n1,35.5,139.75\n2,,\n', geometry=True
    )
    got = rel.select("id, st_astext(geometry)").order("id").fetchall()
    assert got == [(1, "POINT (139.75 35.5)"), (2, None)]


def test_select_fails_on_a_value_the_type_rule_does_not_fit(tmp_path):
    _, rel = _load(tmp_path, '"id","elevation_ft"\n1,12.5\n')
    with pytest.raises(duckdb.Error, match="elevation_ft is not an integer: 12.5"):
        rel.fetchall()


def test_snapshots_lists_dated_manifests_newest_first(tmp_path):
    for day, n in [("2026-09-30", 86153), ("2026-10-01", 86154)]:
        (tmp_path / day).mkdir()
        (tmp_path / day / "manifest.json").write_text(
            json.dumps(
                {"commit": {"sha": "abc" + day}, "outputs": {"airports.parquet": {"rows": n}}}
            )
        )
    (tmp_path / "not-a-snapshot").mkdir()
    got = m.snapshots(tmp_path)
    assert [day for day, _ in got] == ["2026-10-01", "2026-09-30"]
    assert got[0][1]["outputs"]["airports.parquet"]["rows"] == 86154
