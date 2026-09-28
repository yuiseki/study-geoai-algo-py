"""The shared DuckDB connection is capped, because this host has no swap."""

from study_geoai import db


def test_connection_is_capped(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "SPILL_DIR", tmp_path / "spill")
    con = db.connect()
    settings = dict(
        con.sql(
            "select name, value from duckdb_settings() "
            "where name in ('memory_limit', 'threads', 'max_temp_directory_size', 'temp_directory')"
        ).fetchall()
    )
    assert settings["memory_limit"] == "3.7 GiB"
    assert settings["threads"] == "8"
    assert settings["max_temp_directory_size"] == "7.4 GiB"
    assert settings["temp_directory"] == str(tmp_path / "spill")
