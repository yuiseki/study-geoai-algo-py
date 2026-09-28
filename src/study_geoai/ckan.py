"""Ward facility lists from the Tokyo Open Data Catalog, for a study area.

The CSVs live on each ward's own site and links break, so they are mirrored
unchanged on z.yuiseki.net (scripts/mirror_tokyo_ckan.py; CC BY 4.0, credits in
the mirror's LICENSE). They come in UTF-8, CP932 and UTF-16, and a few named
.csv are really xlsx or zip. Every text file seen has latitude and longitude
columns, named 緯度 and 経度 or with a prefix such as 投票所_緯度.

One row per facility. Nothing is dropped quietly: rows without usable
coordinates, files that could not be read, and files that were already gone
when the mirror was made are kept, with status telling which.
"""

import csv
import io
import json
import time
import urllib.request

import duckdb

from study_geoai.aoi import Area, cache_path, writing

BASE = "https://z.yuiseki.net/static/tokyo-ckan-files"
DECODE = {"utf-8": "utf-8-sig", "cp932": "cp932", "utf-16": "utf-16"}
_manifest: dict | None = None


def manifest() -> dict:
    global _manifest
    if _manifest is None:
        req = urllib.request.Request(
            f"{BASE}/manifest.json?cb={int(time.time())}", headers={"User-Agent": "study-geoai"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            _manifest = json.load(r)
    return _manifest


def pick(header: list[str], word: str) -> str | None:
    """The column named word, else the first one ending in _word, else the first containing it."""
    names = [h.strip() for h in header]
    for test in (lambda h: h == word, lambda h: h.endswith("_" + word), lambda h: word in h):
        for original, h in zip(header, names, strict=True):
            if test(h):
                return original
    return None


def coord(lat: str | None, lon: str | None) -> tuple[float | None, float | None, str]:
    """lon, lat and a status; only points plausibly in Tokyo (islands included) are ok."""
    if not (lat or "").strip() or not (lon or "").strip():
        return None, None, "no_coords"
    try:
        y, x = float(lat), float(lon)
    except ValueError:
        return None, None, "bad_coords"
    if not (20 <= y <= 46 and 122 <= x <= 154):
        return None, None, "bad_coords"
    return x, y, "ok"


def _rows(record: dict) -> list[dict]:
    base = {
        "code5": record["collection"][1:6],
        "organization": record["organization_title"],
        "item_id": record["item_id"],
        "item_title": record["item_title"],
    }
    if not record.get("path"):
        return [{**base, "row": None, "status": "missing_file"}]
    enc = record.get("encoding")
    if enc not in DECODE:
        return [{**base, "row": None, "status": f"unsupported_{enc}"}]
    req = urllib.request.Request(f"{BASE}/{record['path']}", headers={"User-Agent": "study-geoai"})
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode(DECODE[enc])
    table = list(csv.reader(io.StringIO(text)))
    header, body = table[0], [row for row in table[1:] if any(c.strip() for c in row)]
    lat_col, lon_col, name_col = pick(header, "緯度"), pick(header, "経度"), pick(header, "名称")
    out = []
    for i, values in enumerate(body, start=1):
        attrs = dict(zip(header, values, strict=False))
        x, y, status = coord(attrs.get(lat_col), attrs.get(lon_col))
        out.append({
            **base, "row": i, "name": attrs.get(name_col), "lon": x, "lat": y,
            "status": status, "attributes": json.dumps(attrs, ensure_ascii=False),
        })  # fmt: skip
    return out


def facilities(con: duckdb.DuckDBPyConnection, area: Area, family: str) -> duckdb.DuckDBPyRelation:
    """Facilities of one family published by the wards of the area.

    Columns: code5, organization, item_id, item_title, row, name, lon, lat, status
    (ok, no_coords, bad_coords, missing_file, unsupported_xlsx, ...), attributes (JSON
    of the original row), geometry (point or NULL), inside (the point lies in the area).
    """
    path = cache_path("tokyo-ckan-files", "2026-09-28", f"{family}-{area.name}")
    if not path.exists():
        records = [
            r
            for r in manifest()["files"].values()
            if r["family"] == family and r["collection"][1:6] in area.codes
        ]
        rows = [row for r in sorted(records, key=lambda r: r["item_id"]) for row in _rows(r)]
        cols = ["code5", "organization", "item_id", "item_title", "row", "name", "lon", "lat",
                "status", "attributes"]  # fmt: skip
        types = ["varchar"] * 4 + ["integer", "varchar", "double", "double", "varchar", "json"]
        con.execute(
            "create or replace temp table _f ("
            + ", ".join(f"{c} {t}" for c, t in zip(cols, types, strict=True))
            + ")"
        )
        if rows:  # a family the area's wards do not publish gives an empty table
            con.executemany(
                f"insert into _f values ({', '.join('?' for _ in cols)})",
                [[row.get(c) for c in cols] for row in rows],
            )
        with writing(path) as tmp:
            con.execute(
                f"""
                copy (
                    select *,
                           case when lon is not null then st_point(lon, lat) end as geometry,
                           coalesce(st_intersects(st_point(lon, lat), st_geomfromtext(?)), false)
                             as inside
                    from _f
                ) to '{tmp}' (format parquet)
                """,
                [area.wkt],
            )
        con.execute("drop table _f")
    return con.read_parquet(str(path))
