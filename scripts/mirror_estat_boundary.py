"""Mirror the e-Stat boundary data as GeoParquet under /www/html/static/estat-boundary/.

e-Stat's statistical GIS (https://www.e-stat.go.jp/gis/statmap-search?type=2)
serves 54 boundary datasets (docs/datasets/estat/boundary-catalog.tsv) as one
Shapefile zip per prefecture: names in cp932 without a .cpg, no Range, no
Last-Modified. The terms (政府標準利用規約 2.0, usable under CC BY 4.0) allow
redistribution with credit.

This script downloads the 47 prefecture zips of every dataset, and writes one
directory per distinct dataset:

- raw/: the zips, unchanged, under the names the server gave them
- <dir>.parquet (or part-NN.parquet below 512 MB each): all prefectures in one
  GeoParquet, names decoded from cp932, the geometry carrying its CRS
  (EPSG:4612 for JGD2000, EPSG:6668 for JGD2011), a prefcode column added
- manifest.json

Two things the catalogue hides are handled on purpose. Some dataset ids
answer with a 404 HTML page instead of a zip; those prefectures are recorded
as missing, not written. Some datasets are the same files under another id
(the zips are rebuilt on every request, so only their members can be
compared); those are placed once and the others are listed as aliases.

    uv run python scripts/mirror_estat_boundary.py
    uv run python scripts/mirror_estat_boundary.py --only A002005212020
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import shutil
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import duckdb
import pyarrow as pa

ROOT = Path(__file__).parents[1]
CATALOG = ROOT / "docs" / "datasets" / "estat" / "boundary-catalog.tsv"
SEARCH = "https://www.e-stat.go.jp/gis/statmap-search?type=2"
DATA = "https://www.e-stat.go.jp/gis/statmap-search/data"
PUBLIC_PREFIX = "https://z.yuiseki.net/static/estat-boundary/"
DEST = Path("/www/html/static/estat-boundary")
SCRATCH = Path(tempfile.gettempdir()) / "study-geoai-mirror-estat-boundary"
UA = f"study-geoai-algo-py-mirror/1 (+{PUBLIC_PREFIX})"
# Cloudflare in front of z.yuiseki.net does not cache files above 512 MB and
# then answers the first Range request with the whole body.
MAX_BYTES = 512 * 1024 * 1024
PREFS = [f"{i:02d}" for i in range(1, 48)]
CRS = {"2000": "EPSG:4612", "2011": "EPSG:6668"}


class NotAShapefile(ValueError):
    pass


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


# --- catalogue and URLs ------------------------------------------------------


def catalog(path: Path = CATALOG) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def dataset_dir(servey_id: str, datum: str) -> str:
    return f"{servey_id}-jgd{datum}"


def download_url(servey_id: str, code: str, datum: str) -> str:
    q = {
        "dlserveyId": servey_id, "code": code, "coordSys": "1", "format": "shape",
        "downloadType": "5", "datum": datum,
    }  # fmt: skip
    return f"{DATA}?{urllib.parse.urlencode(q)}"


def disposition_filename(header: str) -> str:
    for part in header.split(";"):
        part = part.strip()
        if part.startswith("filename*=UTF-8''"):
            return urllib.parse.unquote(part.removeprefix("filename*=UTF-8''"))
        if part.startswith("filename="):
            return part.removeprefix("filename=").strip('"')
    raise ValueError(f"no filename in {header!r}")


# --- checking the zips -------------------------------------------------------


def check_zip(data: bytes) -> str:
    """The stem of the one shapefile in a zip; NotAShapefile for anything else."""
    if data[:4] != b"PK\x03\x04":
        kind = "empty" if data[:4] == b"PK\x05\x06" else "html" if b"<html" in data[:2000] else "?"
        raise NotAShapefile(f"{kind}: not a zip with files ({len(data)} bytes)")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
    stems = {Path(n).stem for n in names if n.lower().endswith(".shp")}
    if len(stems) != 1:
        raise NotAShapefile(f"{len(stems)} shapefiles in {names}")
    stem = stems.pop()
    have = {Path(n).suffix.lower() for n in names if Path(n).stem == stem}
    for ext in (".shp", ".shx", ".dbf", ".prj"):
        if ext not in have:
            raise NotAShapefile(f"{stem} has no {ext[1:]} in {names}")
    return stem


def content_key(data: bytes) -> str:
    """A hash of the members' names and bytes, blind to the times in the zip."""
    h = hashlib.sha256()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in sorted(z.namelist()):
            h.update(name.encode() + b"\0" + hashlib.sha256(z.read(name)).digest())
    return h.hexdigest()


def check_datum(prj: bytes, datum: str) -> None:
    want = f"JGD_{datum}"
    if want.encode() not in prj:
        raise ValueError(f"asked for JGD{datum}, the .prj says {prj[:80]!r}")


def shx_records(shx: bytes) -> int:
    """Records in a shapefile, from its index: a 100-byte header, 8 bytes each."""
    return (len(shx) - 100) // 8


def decode_cp932(t: pa.Table) -> pa.Table:
    """Every binary column of a table but the WKB geometry as text, decoded strictly from cp932."""
    cols = []
    for name, col in zip(t.column_names, t.columns, strict=True):
        if name != "geometry" and (
            pa.types.is_binary(col.type) or pa.types.is_large_binary(col.type)
        ):
            col = pa.array(
                [None if v is None else v.decode("cp932") for v in col.to_pylist()], pa.string()
            )
        cols.append(col)
    return pa.table(cols, names=t.column_names)


# --- fetching ----------------------------------------------------------------


def fetch(servey_id: str, datum: str, code: str, rawdir: Path) -> dict:
    """Download one prefecture once; the outcome is kept beside the zip."""
    meta_path = rawdir / f"{code}.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text())
    url = download_url(servey_id, code, datum)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                status, data = r.status, r.read()
                header = r.headers.get("Content-Disposition") or ""
            break
        except urllib.error.HTTPError as e:
            status, data, header = e.code, e.read(), ""
            break
        except OSError as e:
            if attempt == 4:
                raise
            log(f"retry {servey_id} {code}: {e}")
            time.sleep(10 * (attempt + 1))
    meta = {"url": url, "status": status, "bytes": len(data),
            "fetched": dt.datetime.now().astimezone().replace(microsecond=0).isoformat()}  # fmt: skip
    try:
        meta["stem"] = check_zip(data)
        meta["file"] = disposition_filename(header)
        meta["sha256"] = hashlib.sha256(data).hexdigest()
        meta["content"] = content_key(data)
        (rawdir / meta["file"]).write_bytes(data)
    except NotAShapefile as e:
        meta["missing"] = str(e)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False))
    time.sleep(0.3)
    return meta


# --- building ----------------------------------------------------------------


def read_prefecture(con, zpath: Path, datum: str, code: str, tmp: Path) -> pa.Table:
    with zipfile.ZipFile(zpath) as z:
        z.extractall(tmp)
    stem = check_zip(zpath.read_bytes())
    check_datum((tmp / f"{stem}.prj").read_bytes(), datum)
    expected = shx_records((tmp / f"{stem}.shx").read_bytes())
    t = con.sql(
        f"select * exclude (geom), st_aswkb(geom) as geometry "
        f"from st_readshp('{tmp / stem}.shp', encoding := 'blob')"
    ).arrow()
    t = t.read_all() if hasattr(t, "read_all") else t
    if t.num_rows != expected:
        raise RuntimeError(f"{zpath.name}: {t.num_rows} rows read, the .shx has {expected}")
    t = decode_cp932(t)
    return t.add_column(0, "prefcode", pa.array([code] * t.num_rows, pa.string()))


def build(rawdir: Path, metas: dict[str, dict], datum: str, work: Path) -> dict[str, dict]:
    con = duckdb.connect()
    con.execute("set memory_limit = '8GB'; install spatial; load spatial")
    tables = []
    for code in PREFS:
        if "missing" in metas[code]:
            continue
        with tempfile.TemporaryDirectory(dir=work) as tmp:
            tables.append(
                read_prefecture(con, rawdir / metas[code]["file"], datum, code, Path(tmp))
            )
    whole = pa.concat_tables(tables, promote_options="permissive")
    con.register("whole", whole)
    total = whole.num_rows
    crs = CRS[datum]
    cols = [f'"{c}"' for c in whole.column_names if c != "geometry"]
    query = (
        f"select {', '.join(cols)}, st_geomfromwkb(geometry)::geometry('{crs}') as geometry "
        "from whole"
    )
    out: dict[str, dict] = {}
    name = work.name
    single = work / f"{name}.parquet"
    write = "(format parquet, compression zstd, row_group_size 10000)"
    con.execute(f"copy ({query}) to '{single}' {write}")
    if single.stat().st_size <= MAX_BYTES:
        out[single.name] = {"rows": total, "bytes": single.stat().st_size}
    else:
        # aim below the limit: prefectures differ in how well they compress
        parts = -(-single.stat().st_size // (MAX_BYTES * 3 // 4))
        single.unlink()
        counts = con.sql("select prefcode, count(*) from whole group by 1 order by 1").fetchall()
        limit = -(-total // parts)
        groups, size = [[]], 0
        for code, n in counts:
            if groups[-1] and size + n > limit:
                groups.append([])
                size = 0
            groups[-1].append(code)
            size += n
        for i, g in enumerate(groups):
            p = work / f"part-{i:02d}.parquet"
            inlist = ", ".join(f"'{c}'" for c in g)
            con.execute(f"copy ({query} where prefcode in ({inlist})) to '{p}' {write}")
            if p.stat().st_size > MAX_BYTES:
                raise RuntimeError(f"{p.name}: {p.stat().st_size} bytes, above {MAX_BYTES}")
            rows = con.sql(f"select count(*) from '{p}'").fetchone()[0]
            out[p.name] = {"rows": rows, "bytes": p.stat().st_size, "prefcodes": [g[0], g[-1]]}
    got = sum(v["rows"] for v in out.values())
    if got != total:
        raise RuntimeError(f"{name}: wrote {got} rows, read {total}")
    for f, info in out.items():
        info["sha256"] = hashlib.sha256((work / f).read_bytes()).hexdigest()
    return out


# --- README and LICENSE ------------------------------------------------------

CREDIT = "出典：政府統計の総合窓口(e-Stat)（https://www.e-stat.go.jp/）"

LICENSE = f"""LICENSE

The files in this directory are the boundary data of the statistical GIS of
e-Stat, the portal site for official statistics of Japan
({SEARCH}), and GeoParquet made from them.

They are used under the e-Stat terms of use (https://www.e-stat.go.jp/terms-of-use),
which follow the Government of Japan Standard Terms of Use (Version 2.0) and
say the content may also be used under CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/legalcode.ja). Copying, public
transmission and adaptation, including commercial use, are allowed.

Credit, as the terms require (出典の記載):

  {CREDIT}
  e-Stat の境界データを加工して作成

The Parquet files were changed from the zips in raw/: the 47 prefectures were
put in one file (or a few, below 512 MB each), the text columns were decoded
from cp932, a prefcode column was added from the request, and the geometry got
the CRS of the requested datum (EPSG:4612 for JGD2000, EPSG:6668 for JGD2011).
Values were not changed. This is not data published by the Government of
Japan; it is a copy made by a third party.
"""


def render_readme(entries: list[dict]) -> str:
    rows = []
    for e in entries:
        d = e["dir"]
        if e.get("alias_of"):
            where = f"[{e['alias_of']}/]({e['alias_of']}/) と同じ中身"
        elif e.get("unavailable"):
            where = "配布元が zip を返さない (下の注)"
        else:
            where = f"[{d}/]({d}/)"
        n = f"{e['rows']:,}" if e.get("rows") else ""
        miss = ", ".join(e.get("missing") or [])
        rows.append(
            f"| {e['survey']} | {e['year']} | {e['label']} | `{e['serveyId']}` | {where} | {n} | {miss} |"
        )
    return f"""# e-Stat 統計 GIS の境界データの GeoParquet

[e-Stat の統計 GIS]({SEARCH}) が都道府県ごとの Shapefile の zip で配っている境界データを、元の zip のまま残し、全国を 1 つ (512MB を超えるものは数個) の GeoParquet にまとめたもの。

## 出典の表示

e-Stat の利用規約 (政府標準利用規約 2.0 準拠、CC BY 4.0 に従う利用も可) に従い、利用する際は次のように表示すること。

- {CREDIT}
- e-Stat の境界データを加工して作成

国 (又は府省等) が作成したかのような態様で公表・利用してはいけない、と規約にある。加工の中身は [LICENSE](LICENSE)。

## データセット

| 統計 | 年 | 種類 | 調査 ID | 置き場 | 行数 | zip が返らなかった都道府県 |
|---|---|---|---|---|---:|---|
{chr(10).join(rows)}

- ディレクトリ名は `<調査 ID>-jgd<測地系>`。
- 各ディレクトリに `raw/` (47 都道府県の zip をそのまま)、GeoParquet、`manifest.json` (要求した URL、大きさ、sha256、取得日時、行数)。
- 文字の列は cp932 から解いた文字列、数値の列は dbf の型のまま。コードの列 (PREF、CITY など) は dbf でも文字なので先頭のゼロは残る。`prefcode` 列は要求した都道府県コードで、こちらが足したもの。
- `geometry` は要求した測地系の CRS を持つ (JGD2000 は EPSG:4612、JGD2011 は EPSG:6668)。.prj がそれと一致することを確かめている。
- 行数は都道府県ごとに .shx の件数と照合している。
- 同じ中身: 配布元は要求のたびに zip を作り直すので、zip 自体の sha256 は毎回変わる。中のファイルの名前と中身が 47 都道府県すべてで一致するものは 1 か所にだけ置いた。
- zip が返らない: 配布元が zip の代わりに HTML のページ (多くは 404) を返したもの。その都道府県は Parquet に入っていない。

この README と LICENSE は、取得スクリプト (study-geoai-algo-py の scripts/mirror_estat_boundary.py) を流すたびに作り直される。
"""


# --- main --------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--only", action="append", help="a dataset id to take (repeatable)")
    ap.add_argument("--fetch-only", action="store_true", help="download, do not build")
    args = ap.parse_args()

    entries = [e for e in catalog() if not args.only or e["serveyId"] in args.only]
    log(f"{len(entries)} datasets")

    metas: dict[str, dict[str, dict]] = {}
    for e in entries:
        d = dataset_dir(e["serveyId"], e["datum"])
        rawdir = args.scratch / "raw" / d
        rawdir.mkdir(parents=True, exist_ok=True)
        metas[d] = {code: fetch(e["serveyId"], e["datum"], code, rawdir) for code in PREFS}
        miss = [c for c, mt in metas[d].items() if "missing" in mt]
        got = sum(mt["bytes"] for mt in metas[d].values() if "missing" not in mt)
        log(f"{d}: {47 - len(miss)} zips, {got:,} bytes, missing {miss or 'none'}")
    if args.fetch_only:
        return

    first_of: dict[tuple, str] = {}
    for e in entries:
        d = dataset_dir(e["serveyId"], e["datum"])
        e["dir"] = d
        e["missing"] = [c for c, mt in metas[d].items() if "missing" in mt]
        if len(e["missing"]) == len(PREFS):
            e["unavailable"] = True
            continue
        key = tuple(metas[d][c].get("content") for c in PREFS)
        if key in first_of:
            e["alias_of"] = first_of[key]
            continue
        first_of[key] = d

        work = args.scratch / "build" / d
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        outputs = build(args.scratch / "raw" / d, metas[d], e["datum"], work)
        e["rows"] = sum(v["rows"] for v in outputs.values())
        aliases = []  # filled after the loop
        manifest = {
            "dataset": {k: e[k] for k in ("survey", "year", "serveyId", "datum", "label")},
            "crs": CRS[e["datum"]],
            "built": dt.datetime.now(dt.UTC).astimezone().replace(microsecond=0).isoformat(),
            "outputs": outputs,
            "sources": metas[d],
            "aliases": aliases,
        }
        (work / "raw").mkdir()
        for mt in metas[d].values():
            if "file" in mt:
                shutil.copyfile(args.scratch / "raw" / d / mt["file"], work / "raw" / mt["file"])
        (work / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
        log(f"{d}: {e['rows']:,} rows in {list(outputs)}")

    for e in entries:
        if e.get("alias_of"):
            p = args.scratch / "build" / e["alias_of"] / "manifest.json"
            man = json.loads(p.read_text())
            man["aliases"].append(
                {k: e[k] for k in ("survey", "year", "serveyId", "datum", "label")}
            )
            p.write_text(json.dumps(man, ensure_ascii=False, indent=1))
            e["rows"] = next(x["rows"] for x in entries if x["dir"] == e["alias_of"])

    args.dest.mkdir(parents=True, exist_ok=True)
    for e in entries:
        if e.get("alias_of") or e.get("unavailable"):
            continue
        work = args.scratch / "build" / e["dir"]
        tmp = args.dest / f".{e['dir']}.part"
        if tmp.exists():
            shutil.rmtree(tmp)
        shutil.copytree(work, tmp)
        old = args.dest / e["dir"]
        if old.exists():
            shutil.rmtree(old)
        os.replace(tmp, old)
        log(f"placed {old}")
    (args.dest / "LICENSE").write_text(LICENSE)
    (args.dest / "README.md").write_text(render_readme(entries))
    (args.dest / "catalog.json").write_text(json.dumps(entries, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
