"""Finding a GDAL command-line install without a path written into the code."""

from pathlib import Path

import pytest

from study_geoai import gdal


def _install(root: Path) -> Path:
    """A fake GDAL install: bin/ogr2ogr and its share/ data."""
    (root / "bin").mkdir(parents=True)
    (root / "bin" / "ogr2ogr").write_text("#!/bin/sh\n")
    (root / "bin" / "ogr2ogr").chmod(0o755)
    (root / "share" / "proj").mkdir(parents=True)
    (root / "share" / "gdal").mkdir(parents=True)
    return root


def test_prefix_comes_from_the_environment_variable(tmp_path, monkeypatch):
    root = _install(tmp_path / "gdal")
    monkeypatch.setenv(gdal.PREFIX_VAR, str(root))
    monkeypatch.setenv("PATH", "")
    assert gdal.prefix() == root


def test_prefix_is_found_on_path(tmp_path, monkeypatch):
    root = _install(tmp_path / "conda")
    monkeypatch.delenv(gdal.PREFIX_VAR, raising=False)
    monkeypatch.setenv("PATH", str(root / "bin"))
    assert gdal.prefix() == root


def test_missing_gdal_says_how_to_point_at_one(tmp_path, monkeypatch):
    monkeypatch.delenv(gdal.PREFIX_VAR, raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(FileNotFoundError, match=gdal.PREFIX_VAR):
        gdal.tool("ogr2ogr")


def test_tool_and_child_env_use_the_prefix(tmp_path, monkeypatch):
    root = _install(tmp_path / "gdal")
    monkeypatch.setenv(gdal.PREFIX_VAR, str(root))
    assert gdal.tool("ogr2ogr") == str(root / "bin" / "ogr2ogr")
    env = gdal.child_env()
    assert env["PROJ_DATA"] == str(root / "share" / "proj")
    assert env["GDAL_DATA"] == str(root / "share" / "gdal")
    assert env["PATH"].split(":")[0] == str(root / "bin")


def test_child_env_leaves_out_data_dirs_that_do_not_exist(tmp_path, monkeypatch):
    root = tmp_path / "bare"
    (root / "bin").mkdir(parents=True)
    monkeypatch.setenv(gdal.PREFIX_VAR, str(root))
    env = gdal.child_env()
    assert "PROJ_DATA" not in env and "GDAL_DATA" not in env
