import importlib.util
import io
import zipfile
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "mirror_estat_boundary", Path(__file__).parents[1] / "scripts" / "mirror_estat_boundary.py"
)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

PRJ_2000 = (
    b'GEOGCS["GCS_JGD_2000",DATUM["D_JGD_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]]]'
)


def _zip(members: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in members.items():
            z.writestr(name, data)
    return buf.getvalue()


def test_catalog_reads_the_committed_tsv():
    rows = m.catalog()
    assert len(rows) == 54
    first = rows[0]
    assert (first["serveyId"], first["datum"], first["year"]) == ("A002005512001", "2000", "2001")
    assert {r["datum"] for r in rows} == {"2000", "2011"}


def test_download_url_names_the_datum():
    url = m.download_url("A002005212020", "13", "2011")
    assert url == (
        "https://www.e-stat.go.jp/gis/statmap-search/data?dlserveyId=A002005212020"
        "&code=13&coordSys=1&format=shape&downloadType=5&datum=2011"
    )


def test_filename_from_content_disposition():
    h = "attachment; filename*=UTF-8''A002005212020DDSWC13-JGD2011.zip"
    assert m.disposition_filename(h) == "A002005212020DDSWC13-JGD2011.zip"


@pytest.mark.parametrize(
    ("data", "kind"),
    [
        (b"<!DOCTYPE html><html lang='ja'>", "html"),
        (b"PK\x05\x06" + b"\0" * 18, "empty"),
    ],
)
def test_check_zip_rejects_what_is_not_a_shapefile_zip(data, kind):
    with pytest.raises(m.NotAShapefile, match=kind):
        m.check_zip(data)


def test_check_zip_wants_all_four_parts():
    data = _zip({"r2ka13.shp": b"x", "r2ka13.dbf": b"x", "r2ka13.prj": PRJ_2000})
    with pytest.raises(m.NotAShapefile, match="shx"):
        m.check_zip(data)


def test_check_zip_returns_the_stem():
    data = _zip({f"r2ka13.{e}": b"x" for e in ("shp", "shx", "dbf")} | {"r2ka13.prj": PRJ_2000})
    assert m.check_zip(data) == "r2ka13"


def test_content_key_ignores_member_times():
    a = io.BytesIO()
    b = io.BytesIO()
    for buf, t in [(a, (2026, 10, 1, 19, 0, 0)), (b, (2026, 10, 1, 19, 5, 0))]:
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr(zipfile.ZipInfo("agri202013.shp", t), b"same")
    assert a.getvalue() != b.getvalue()
    assert m.content_key(a.getvalue()) == m.content_key(b.getvalue())
    with zipfile.ZipFile(c := io.BytesIO(), "w") as z:
        z.writestr("agri202013.shp", b"other")
    assert m.content_key(c.getvalue()) != m.content_key(a.getvalue())


@pytest.mark.parametrize(
    ("prj", "datum", "ok"),
    [(PRJ_2000, "2000", True), (PRJ_2000, "2011", False), (b"GCS_JGD_2011", "2011", True)],
)
def test_prj_must_match_the_requested_datum(prj, datum, ok):
    if ok:
        m.check_datum(prj, datum)
    else:
        with pytest.raises(ValueError, match="JGD"):
            m.check_datum(prj, datum)


def test_decode_turns_cp932_blobs_into_text():
    import pyarrow as pa

    t = pa.table({"PREF_NAME": [b"\x93\x8c\x8b\x9e\x93s", None], "JINKO": [10, 0]})
    got = m.decode_cp932(t)
    assert got.column("PREF_NAME").to_pylist() == ["東京都", None]
    assert got.column("JINKO").to_pylist() == [10, 0]
    assert got.schema.field("PREF_NAME").type == pa.string()


def test_decode_fails_on_bytes_that_are_not_cp932():
    import pyarrow as pa

    with pytest.raises(UnicodeDecodeError):
        m.decode_cp932(pa.table({"S_NAME": [b"\x82"]}))


def test_shx_records_counts_the_index_entries():
    assert m.shx_records(b"\0" * 100 + b"\0" * 8 * 6021) == 6021


def test_decode_leaves_the_wkb_geometry_alone():
    import pyarrow as pa

    wkb = bytes.fromhex("0101000000000000000000f03f0000000000000040")
    got = m.decode_cp932(pa.table({"S_NAME": [b"\x93\x8c"], "geometry": [wkb]}))
    assert got.column("geometry").to_pylist() == [wkb]
    assert got.column("S_NAME").to_pylist() == ["東"]


def _shapefile_zip(tmp_path, code: str, n: int) -> Path:
    """A zip of a small polygon shapefile, written by GDAL, with a JGD2000 .prj."""
    import duckdb

    d = tmp_path / f"shp{code}"
    d.mkdir()
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    con.execute(
        f"copy (select 'K' || i::varchar as KEY_CODE, i as JINKO, "
        f"st_buffer(st_point(139 + i * 0.01, 35), 0.004, 4) as geom from range({n}) t(i)) "
        f"to '{d}/b{code}.shp' (format gdal, driver 'ESRI Shapefile')"
    )
    (d / f"b{code}.prj").write_bytes(PRJ_2000)
    z = tmp_path / f"B{code}.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for f in sorted(d.iterdir()):
            if f.suffix in (".shp", ".shx", ".dbf", ".prj"):
                zf.write(f, f.name)
    return z


def test_build_splits_between_prefectures_when_one_file_is_too_big(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    metas = {c: {"missing": "html"} for c in m.PREFS}
    for code, n in [("01", 300), ("13", 300), ("47", 300)]:
        z = _shapefile_zip(tmp_path, code, n)
        z.rename(raw / z.name)
        metas[code] = {"file": z.name}
    work = tmp_path / "X-jgd2000"
    work.mkdir()
    one = m.build(raw, metas, "2000", work)
    assert list(one) == ["X-jgd2000.parquet"] and one["X-jgd2000.parquet"]["rows"] == 900

    size = one["X-jgd2000.parquet"]["bytes"]
    monkeypatch.setattr(m, "MAX_BYTES", size * 2 // 3)
    (work / "X-jgd2000.parquet").unlink()
    parts = m.build(raw, metas, "2000", work)
    assert len(parts) >= 2 and all(k.startswith("part-") for k in parts)
    assert sum(v["rows"] for v in parts.values()) == 900
    assert all(v["bytes"] <= size * 2 // 3 for v in parts.values())
    firsts = [v["prefcodes"][0] for v in parts.values()]
    assert firsts == sorted(firsts) and firsts[0] == "01"
