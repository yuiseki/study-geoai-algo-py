"""Mirror 全国の人流オープンデータ (MLIT) as Parquet under /sata_hdd_24tb/www/html/static/mlit-1km-fromto/.

The dataset (https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto) is 94
zip files, one per prefecture and kind, each holding one zip per month that
holds one CSV. Nothing in it can be read in part. The page asks visitors to
log in before downloading, but the CKAN API lists the resources without a
login and every resource URL redirects to a signed S3 URL; the terms of use
(政府標準利用規約 2.0, compatible with CC BY 4.0) allow redistribution.

This script downloads every zip once, takes the CSVs out, and writes:

- monthly_mdp_mesh1km.parquet: stay population per 1 km mesh, all prefectures
- monthly_fromto_city.parquet: stay population per municipality by home area
- attribute_mesh1km.parquet: mesh centre and bounds (GeoParquet, a polygon
  column added from the bounds), both the 2019 and 2020 versions
- prefcode_citycode_master.parquet, regioncode_master.parquet: the UTF-8
  masters, both versions
- the terms of use and the data definition PDF, unchanged

Codes stay strings as the data definition says (prefcode "01", month "01");
only population becomes an integer. The rows and the population total of every
output are checked against the CSVs before anything is placed.

    uv run python scripts/mirror_mlit_jinryu.py
    uv run python scripts/mirror_mlit_jinryu.py --dry-run
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
import urllib.request
import zipfile
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path

import duckdb

DATASET = "mlit-1km-fromto"
API = f"https://www.geospatial.jp/ckan/api/3/action/package_show?id={DATASET}"
PAGE = f"https://www.geospatial.jp/ckan/dataset/{DATASET}"
PUBLIC_PREFIX = f"https://z.yuiseki.net/static/{DATASET}/"
DEST = Path("/sata_hdd_24tb/www/html/static") / DATASET
SCRATCH = Path(tempfile.gettempdir()) / "study-geoai-mirror-mlit-jinryu"
UA = f"study-geoai-algo-py-mirror/1 (+{PUBLIC_PREFIX})"
# Cloudflare in front of z.yuiseki.net does not cache files above 512 MB and
# then answers the first Range request with the whole body.
MAX_BYTES = 512 * 1024 * 1024
PDFS = {"利用規約": "license.pdf", "オープンデータ（人流データ）定義書": "opendatadefinition.pdf"}


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


# --- reading the nested zips -------------------------------------------------


def inner_csvs(
    path: Path, keep: Callable[[str], bool] = lambda name: True
) -> Iterator[tuple[str, bytes]]:
    """(inner zip name, CSV bytes) for every inner zip of an outer zip, by name."""
    with zipfile.ZipFile(path) as outer:
        names = sorted(n for n in outer.namelist() if n.endswith(".zip") and keep(n))
        for name in names:
            with zipfile.ZipFile(io.BytesIO(outer.read(name))) as inner:
                members = [n for n in inner.namelist() if not n.endswith("/")]
                if len(members) != 1:
                    raise ValueError(f"{path.name}:{name} holds {len(members)} files, not one file")
                yield name, inner.read(members[0])


def csv_stats(data: bytes) -> tuple[int, int]:
    """(rows, population total) of one CSV, counted without DuckDB."""
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    rows = total = 0
    for row in reader:
        rows += 1
        total += int(row["population"]) if "population" in row else 0
    return rows, total


def load_csvs(
    con: duckdb.DuckDBPyConnection,
    table: str,
    files: list[Path],
    integer_columns: Iterable[str] = (),
    version: Callable[[Path], str] | None = None,
) -> None:
    """Load CSVs into a table with every column text except integer_columns."""
    ints = list(integer_columns)
    cast = ", ".join(f"cast({c} as integer) as {c}" for c in ints)
    cols = f"* exclude ({', '.join(ints)}), {cast}" if ints else "*"

    def read(fs: list[Path]) -> str:
        lst = ", ".join(f"'{f}'" for f in fs)
        return f"read_csv([{lst}], header = true, all_varchar = true, union_by_name = true)"

    if version is None:
        con.execute(f"create or replace table {table} as select {cols} from {read(files)}")
        return
    parts = [f"select '{version(f)}' as version, {cols} from {read([f])}" for f in files]
    con.execute(f"create or replace table {table} as {' union all by name '.join(parts)}")


# --- fetching ----------------------------------------------------------------


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def resources() -> list[dict]:
    pkg = get_json(API)
    if not pkg.get("success"):
        raise RuntimeError(f"package_show failed: {pkg}")
    return pkg["result"]["resources"]


def fetch(url: str, dest: Path, size: int | None) -> dict:
    """Download url to dest unless it is already there with the listed size."""
    if dest.exists() and size and dest.stat().st_size == size:
        return {"skipped": True}
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    tmp = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f, 1 << 20)
                last_modified = r.headers.get("Last-Modified")
            break
        except OSError as e:
            if attempt == 2:
                raise
            log(f"retry {dest.name}: {e}")
            time.sleep(5 * (attempt + 1))
    if size and tmp.stat().st_size != size:
        raise RuntimeError(f"{dest.name}: got {tmp.stat().st_size} bytes, listed {size}")
    tmp.replace(dest)
    return {"last_modified": last_modified}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# --- building ----------------------------------------------------------------


def extract(zips: list[Path], out: Path, keep: Callable[[str], bool] = lambda n: True) -> dict:
    """Write every inner CSV of the zips under out; return its rows and total."""
    rows = total = n = 0
    files = []
    for z in zips:
        for name, data in inner_csvs(z, keep):
            f = out / name.removesuffix(".zip")
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
            r, t = csv_stats(data)
            rows, total, n = rows + r, total + t, n + 1
            files.append(f)
    return {"files": files, "csvs": n, "rows": rows, "population": total}


def write_parquet(con, query: str, path: Path) -> None:
    con.execute(
        f"copy ({query}) to '{path}' (format parquet, compression zstd, row_group_size 100000, write_bloom_filter false)"
    )


def check(con, path: Path, expected: dict) -> dict:
    got = con.sql(f"select count(*) from '{path}'").fetchone()[0]
    if got != expected["rows"]:
        raise RuntimeError(f"{path.name}: {got} rows, the CSVs have {expected['rows']}")
    cols = [r[0] for r in con.sql(f"select name from parquet_schema('{path}')").fetchall()]
    if "population" in cols:
        s = con.sql(f"select sum(population) from '{path}'").fetchone()[0]
        if s != expected["population"]:
            raise RuntimeError(
                f"{path.name}: population {s}, the CSVs have {expected['population']}"
            )
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise RuntimeError(f"{path.name}: {size} bytes, above the {MAX_BYTES} Cloudflare limit")
    return {"rows": got, "bytes": size, "population": expected.get("population") or None}


def build(raw: dict[str, Path], work: Path) -> dict[str, dict]:
    con = duckdb.connect()
    con.execute("set memory_limit = '6GB'; set preserve_insertion_order = false")
    con.execute("install spatial; load spatial")
    out: dict[str, dict] = {}
    csvdir = work / "csv"

    for kind, order in [
        ("monthly_mdp_mesh1km", "prefcode, year, month, dayflag, timezone, mesh1kmid"),
        ("monthly_fromto_city", "prefcode, citycode, year, month, dayflag, timezone, from_area"),
    ]:
        zips = sorted(p for name, p in raw.items() if name.startswith(kind + "_"))
        if len(zips) != 47:
            raise RuntimeError(f"{kind}: {len(zips)} prefecture zips, not 47")
        ex = extract(zips, csvdir / kind)
        log(f"{kind}: {ex['csvs']} CSVs, {ex['rows']:,} rows")
        load_csvs(con, kind, ex["files"], integer_columns=["population"])
        path = work / f"{kind}.parquet"
        write_parquet(con, f"select * from {kind} order by {order}", path)
        out[path.name] = check(con, path, ex) | {"csvs": ex["csvs"]}

    def year_of(p: Path) -> str:
        return p.stem.rsplit("_", 1)[1]

    ex = extract([raw["attribute"]], csvdir / "attribute")
    load_csvs(con, "attribute", ex["files"], version=year_of)
    path = work / "attribute_mesh1km.parquet"
    write_parquet(con, """
        select *, st_makeenvelope(lon_min::double, lat_min::double,
                                  lon_max::double, lat_max::double) as geometry
        from attribute order by version, mesh1kmid
    """, path)  # fmt: skip
    out[path.name] = check(con, path, ex) | {"csvs": ex["csvs"]}

    for name in ["prefcode_citycode_master", "regioncode_master"]:
        ex = extract([raw[name]], csvdir / name, lambda n: "_utf8_" in n)
        load_csvs(con, name, ex["files"], version=year_of)
        path = work / f"{name}.parquet"
        key = "citycode" if name.startswith("prefcode") else "prefcode"
        write_parquet(con, f"select * from {name} order by version, {key}", path)
        out[path.name] = check(con, path, ex) | {"csvs": ex["csvs"]}

    for f, info in out.items():
        log(f"{f}: {info['rows']:,} rows, {info['bytes']:,} bytes")
    return out


# --- README and LICENSE ------------------------------------------------------

CREDIT = f"「全国の人流オープンデータ」（国土交通省）（{PAGE}）を加工して作成"


def render_license(manifest: dict) -> str:
    return f"""LICENSE

The Parquet files in this directory are adapted from 全国の人流オープンデータ
(1km メッシュ、市区町村単位発地別), published by the Ministry of Land,
Infrastructure, Transport and Tourism (MLIT) of Japan:

  {PAGE}

They are used under 全国の人流オープンデータ利用規約 (license.pdf in this
directory, 令和3年1月27日), which follows the Government of Japan Standard Terms
of Use (Version 2.0) and is compatible with CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/legalcode.ja). The terms allow
copying, public transmission and adaptation, including commercial use.

Credit, as the terms require (出典の記載):

  出典：「全国の人流オープンデータ」（国土交通省）（{PAGE}）
  {CREDIT}

The files were changed from the originals ({manifest["built"][:10]}):

  - The CSVs inside the nested zip files were combined into one Parquet file
    per kind; for monthly_mdp_mesh1km and monthly_fromto_city, all 47
    prefectures and every month (2019-01 to 2021-12) are in one file.
  - population was turned into an integer; every other column is kept as the
    text of the CSV (codes keep their leading zeros).
  - attribute_mesh1km and the masters have both the 2019 and the 2020 file of
    the source, told apart by an added version column. Only the UTF-8 masters
    were used (the Shift_JIS ones hold the same data).
  - attribute_mesh1km has an added geometry column (the rectangle of lon_min,
    lat_min, lon_max, lat_max, WGS 84).
  - Rows were sorted; values were not changed.

license.pdf and opendatadefinition.pdf are the source's own files, unchanged.
"""


def render_readme(manifest: dict) -> str:
    rows = "\n".join(
        f"| [{f}]({f}) | {info['rows']:,} | {info['bytes']:,} | {info['csvs']} |"
        for f, info in manifest["outputs"].items()
    )
    src = "\n".join(
        f"| {s['name']} | {s['bytes']:,} | {s.get('last_modified') or ''} |"
        for s in manifest["sources"]
    )
    return f"""# 全国の人流オープンデータ (国土交通省) の Parquet

[全国の人流オープンデータ（1kmメッシュ、市区町村単位発地別）]({PAGE}) の入れ子の zip の CSV を、HTTP Range 要求で必要な列と行だけ読めるように Parquet にまとめたもの。
2019-01〜2021-12 の月ごとの滞在人口 (1 日あたりの平均、10 人未満は出力しない)。列の意味は [opendatadefinition.pdf](opendatadefinition.pdf) を見ること。

## 出典の表示

[license.pdf](license.pdf) (全国の人流オープンデータ利用規約、政府標準利用規約 2.0 準拠、CC BY 4.0 互換) に従い、利用する際は次のように表示すること。

- {CREDIT}

加工の中身は [LICENSE](LICENSE) にある。

## 置いたもの

| ファイル | 行数 | 大きさ (bytes) | 元の CSV の数 |
|---|---:|---:|---:|
{rows}

- コードの列 (mesh1kmid、prefcode、citycode、year、month、dayflag、timezone、from_area) は CSV のとおりの文字列。population だけ整数。
- dayflag は 0 休日、1 平日、2 全日。timezone は 0 昼 (11〜14 時台)、1 深夜 (1〜4 時台)、2 終日。from_area は 0 同じ市区町村、1 同じ都道府県の別の市区町村、2 同じ地方ブロックの別の都道府県、3 別の地方ブロック。
- monthly_mdp_mesh1km は prefcode、year、month、dayflag、timezone、mesh1kmid の順に並べてあるので、都道府県と月で絞ると読む行グループが少なくて済む。
- attribute_mesh1km と 2 つのマスタは、元にある 2019 年版と 2020 年版の両方を version 列で分けて持つ。2019 年の福岡県那珂川市は旧那珂川町のコード (40305)。

## 元データ

取得は {manifest["built"]}。行数と population の合計が元の CSV と一致することを確かめてから置いている。

| ファイル | 大きさ (bytes) | サーバーの Last-Modified |
|---|---:|---|
{src}

記録の本体は [manifest.json](manifest.json)。この README と LICENSE は、取得スクリプト (study-geoai-algo-py の scripts/mirror_mlit_jinryu.py) を流すたびに作り直される。
"""


# --- main --------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--dry-run", action="store_true", help="list what would be fetched")
    args = ap.parse_args()

    res = resources()
    wanted = [
        r for r in res
        if r["name"].startswith(("monthly_mdp_mesh1km_", "monthly_fromto_city_"))
        or r["name"] in ("attribute", "prefcode_citycode_master", "regioncode_master", *PDFS)
    ]  # fmt: skip
    log(f"{len(res)} resources, {len(wanted)} to mirror")
    if args.dry_run:
        for r in wanted:
            print(r["name"], r.get("size"), r["url"])
        return

    rawdir = args.scratch / "raw"
    rawdir.mkdir(parents=True, exist_ok=True)
    raw: dict[str, Path] = {}
    sources = []
    for r in wanted:
        fname = r["url"].rsplit("/", 1)[1]
        key = fname.removesuffix(".zip")
        key = {"prefcodecitycodemaster": "prefcode_citycode_master",
               "regioncodemaster": "regioncode_master"}.get(key, key)  # fmt: skip
        size = int(r["size"]) if r.get("size") else None
        info = fetch(r["url"], rawdir / fname, size)
        raw[key] = rawdir / fname
        sources.append({
            "name": r["name"], "url": r["url"], "file": fname,
            "bytes": (rawdir / fname).stat().st_size, "sha256": sha256(rawdir / fname),
            "last_modified": info.get("last_modified") or r.get("last_modified"),
        })  # fmt: skip
        log(f"{'have' if info.get('skipped') else 'got '} {fname}")

    # a new build directory per run: nothing under the scratch path is deleted
    work = args.scratch / f"build-{dt.datetime.now():%Y%m%dT%H%M%S}"
    work.mkdir(parents=True)
    outputs = build(raw, work)

    manifest = {
        "dataset": PAGE,
        "built": dt.datetime.now(dt.UTC).astimezone().replace(microsecond=0).isoformat(),
        "outputs": outputs,
        "sources": sources,
    }
    args.dest.mkdir(parents=True, exist_ok=True)
    for f in outputs:
        tmp = args.dest / (f + ".part")
        shutil.copyfile(work / f, tmp)
        os.replace(tmp, args.dest / f)
    for pdf in PDFS.values():
        shutil.copyfile(rawdir / pdf, args.dest / pdf)
    (args.dest / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    (args.dest / "LICENSE").write_text(render_license(manifest))
    (args.dest / "README.md").write_text(render_readme(manifest))
    log(f"placed in {args.dest}")


if __name__ == "__main__":
    main()
