"""Mirror a dated snapshot of the GeoNames dump under /www/html/static/geonames/YYYY-MM-DD/.

GeoNames (https://download.geonames.org/export/dump/) rebuilds its dump every
night at the same URLs, with no version number or checksum; past versions are
only kept for paying subscribers. The data is under CC BY 4.0, so a day's dump
can be kept and passed on with credit.

This script downloads the gazetteer (allCountries.zip), the alternate names
(alternateNamesV2.zip), the hierarchy, the fifth admin level and the small
code tables, checks that the server's Last-Modified did not move while it was
downloading, and writes, in a directory named after the UTC day of
allCountries.zip's Last-Modified:

- raw/: the downloaded files, unchanged
- geoname/part-NN.parquet: the gazetteer with a point geometry (GeoParquet),
  sorted by country and cut between countries to stay under 512 MB a file
- alternate_names.parquet, hierarchy.parquet, admin_code5.parquet
- manifest.json: Last-Modified, size and sha256 of every download, rows and
  size of every output

Every output's row count is checked against the line count of its text file.
A value that does not fit its column's type stops the run.

    uv run python scripts/mirror_geonames.py
    uv run python scripts/mirror_geonames.py --dry-run
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import hashlib
import json
import os
import shutil
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import duckdb

BASE = "https://download.geonames.org/export/dump/"
PAGE = "https://www.geonames.org/"
PUBLIC_PREFIX = "https://z.yuiseki.net/static/geonames/"
DEST = Path("/www/html/static/geonames")
SCRATCH = Path(tempfile.gettempdir()) / "study-geoai-mirror-geonames"
UA = f"study-geoai-algo-py-mirror/1 (+{PUBLIC_PREFIX})"
# Cloudflare in front of z.yuiseki.net does not cache files above 512 MB and
# then answers the first Range request with the whole body.
MAX_BYTES = 512 * 1024 * 1024
FILES = [
    "allCountries.zip", "alternateNamesV2.zip", "hierarchy.zip", "adminCode5.zip",
    "admin1CodesASCII.txt", "admin2Codes.txt", "countryInfo.txt", "featureCodes_en.txt",
    "iso-languagecodes.txt", "timeZones.txt", "readme.txt",
]  # fmt: skip

# columns as readme.txt lists them, in snake case
GEONAME = [
    ("geonameid", "BIGINT"), ("name", "VARCHAR"), ("asciiname", "VARCHAR"),
    ("alternatenames", "VARCHAR"), ("latitude", "DOUBLE"), ("longitude", "DOUBLE"),
    ("feature_class", "VARCHAR"), ("feature_code", "VARCHAR"), ("country_code", "VARCHAR"),
    ("cc2", "VARCHAR"), ("admin1_code", "VARCHAR"), ("admin2_code", "VARCHAR"),
    ("admin3_code", "VARCHAR"), ("admin4_code", "VARCHAR"), ("population", "BIGINT"),
    ("elevation", "INTEGER"), ("dem", "INTEGER"), ("timezone", "VARCHAR"),
    ("modification_date", "DATE"),
]  # fmt: skip
ALTERNATE_NAMES = [
    ("alternate_name_id", "BIGINT"), ("geonameid", "BIGINT"), ("isolanguage", "VARCHAR"),
    ("alternate_name", "VARCHAR"), ("is_preferred_name", "FLAG"), ("is_short_name", "FLAG"),
    ("is_colloquial", "FLAG"), ("is_historic", "FLAG"), ("from", "VARCHAR"), ("to", "VARCHAR"),
]  # fmt: skip
HIERARCHY = [("parent_id", "BIGINT"), ("child_id", "BIGINT"), ("type", "VARCHAR")]
ADMIN_CODE5 = [("geonameid", "BIGINT"), ("adm5code", "VARCHAR")]
# a part of geoname/ holds whole countries up to this many rows (about 300 MB)
GEONAME_PART_ROWS = 4_000_000


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


# --- reading -----------------------------------------------------------------


def lines(path: Path) -> int:
    """Records in a GeoNames text file: one per line, a last line may lack its newline."""
    n, last = 0, b"\n"
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            n += block.count(b"\n")
            last = block[-1:]
    return n + (last != b"\n")


def snapshot_date(last_modified: str) -> str:
    return email.utils.parsedate_to_datetime(last_modified).astimezone(dt.UTC).date().isoformat()


def select_sql(path: Path, columns: list[tuple[str, str]], geometry: bool = False) -> str:
    """A query reading one tab separated GeoNames file with the given column types.

    The files have no header and no quoting. FLAG columns hold '1' or nothing
    and become booleans; integers are checked before the cast, which would
    round '12.5' to 13 instead of failing.
    """
    raw = ", ".join(f"'c{i}': 'VARCHAR'" for i in range(len(columns)))
    src = (
        f"read_csv('{path}', delim = '\\t', header = false, quote = '', escape = '', "
        f"strict_mode = true, columns = {{{raw}}})"
    )
    exprs = []
    for i, (name, t) in enumerate(columns):
        c = f"c{i}"
        if t == "VARCHAR":
            e = c
        elif t == "FLAG":
            e = (
                f"case when {c} is null then false when {c} = '1' then true "
                f"else error('{path.name}: {name} is not ''1'' or empty: ' || {c}) end"
            )
        elif t in ("BIGINT", "INTEGER"):
            e = (
                f"case when {c} is null or regexp_full_match({c}, '-?[0-9]+') then cast({c} as {t}) "
                f"else error('{path.name}: {name} is not an integer: ' || {c}) end"
            )
        else:
            e = f"cast({c} as {t})"
        exprs.append(f'{e} as "{name}"')
    if geometry:
        exprs.append("st_point(cast(c5 as double), cast(c4 as double)) as geometry")
    return f"select {', '.join(exprs)} from {src}"


def split_points(counts: list[tuple[str, int]], max_rows: int) -> list[list[str]]:
    """Group sorted keys into parts of at most max_rows rows, never splitting a key."""
    parts: list[list[str]] = []
    size = 0
    for key, n in counts:
        if parts and size + n <= max_rows:
            parts[-1].append(key)
            size += n
        else:
            parts.append([key])
            size = n
    return parts


# --- fetching ----------------------------------------------------------------


def head(url: str) -> dict:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return {
            "last_modified": r.headers["Last-Modified"],
            "bytes": int(r.headers["Content-Length"]),
        }


def fetch(url: str, dest: Path, meta: dict) -> None:
    """Download url to dest, resuming a partial file only while it is the same version.

    The server is slow (about 70 KB/s on 2026-10-01), so a cut connection is
    resumed with If-Range: a changed file comes back whole with 200.
    """
    if dest.exists() and dest.stat().st_size == meta["bytes"]:
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(20):
        have = tmp.stat().st_size if tmp.exists() else 0
        headers = {"User-Agent": UA}
        if have:
            headers |= {"Range": f"bytes={have}-", "If-Range": meta["last_modified"]}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=300) as r:
                mode = "ab" if r.status == 206 else "wb"
                with open(tmp, mode) as f:
                    shutil.copyfileobj(r, f, 1 << 20)
            break
        except (OSError, urllib.error.URLError) as e:
            log(f"retry {dest.name} at {have:,} bytes: {e}")
            time.sleep(min(60, 5 * (attempt + 1)))
    else:
        raise RuntimeError(f"{dest.name}: gave up")
    if tmp.stat().st_size != meta["bytes"]:
        raise RuntimeError(f"{dest.name}: got {tmp.stat().st_size} bytes, listed {meta['bytes']}")
    tmp.replace(dest)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def unzip_one(path: Path, out: Path) -> Path:
    """Extract the one data file of a GeoNames zip (beside its readme)."""
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n != "readme.txt"]
        if len(names) != 1:
            raise ValueError(f"{path.name} holds {names}, not one data file")
        return Path(z.extract(names[0], out))


# --- building ----------------------------------------------------------------


def write_parquet(con, query: str, path: Path) -> dict:
    con.execute(
        f"copy ({query}) to '{path}' (format parquet, compression zstd, row_group_size 100000)"
    )
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise RuntimeError(f"{path.name}: {size} bytes, above the {MAX_BYTES} Cloudflare limit")
    rows = con.sql(f"select count(*) from '{path}'").fetchone()[0]
    return {"rows": rows, "bytes": size, "sha256": sha256(path)}


def build(raw: Path, work: Path) -> dict[str, dict]:
    con = duckdb.connect()
    con.execute("set memory_limit = '8GB'; set temp_directory = '" + str(work / "tmp") + "'")
    con.execute("install spatial; load spatial")
    text = work / "text"
    out: dict[str, dict] = {}

    f = unzip_one(raw / "allCountries.zip", text)
    expected = lines(f)
    con.execute(f"create table geoname as {select_sql(f, GEONAME, geometry=True)}")
    got = con.sql("select count(*) from geoname").fetchone()[0]
    if got != expected:
        raise RuntimeError(f"{f.name}: {got} rows read, the file has {expected} lines")
    counts = con.sql(
        "select coalesce(country_code, ''), count(*) from geoname group by 1 order by 1"
    ).fetchall()
    (work / "geoname").mkdir()
    total = 0
    for i, keys in enumerate(split_points(counts, GEONAME_PART_ROWS)):
        inlist = ", ".join(f"'{k}'" for k in keys)
        p = work / "geoname" / f"part-{i:02d}.parquet"
        info = write_parquet(
            con,
            f"select * from geoname where coalesce(country_code, '') in ({inlist}) "
            "order by country_code nulls first, geonameid",
            p,
        )
        out[f"geoname/{p.name}"] = info | {"countries": [keys[0], keys[-1]]}
        total += info["rows"]
        log(f"geoname/{p.name}: {info['rows']:,} rows, {keys[0] or '(none)'}..{keys[-1]}")
    if total != expected:
        raise RuntimeError(f"geoname parts hold {total} rows, {f.name} has {expected}")
    con.execute("drop table geoname")

    for zname, cols, order in [
        ("alternateNamesV2.zip", ALTERNATE_NAMES, "geonameid, alternate_name_id"),
        ("hierarchy.zip", HIERARCHY, "parent_id, child_id"),
        ("adminCode5.zip", ADMIN_CODE5, "geonameid"),
    ]:
        f = unzip_one(raw / zname, text)
        expected = lines(f)
        name = {"alternateNamesV2.zip": "alternate_names", "hierarchy.zip": "hierarchy",
                "adminCode5.zip": "admin_code5"}[zname]  # fmt: skip
        p = work / f"{name}.parquet"
        info = write_parquet(con, f"{select_sql(f, cols)} order by {order}", p)
        if info["rows"] != expected:
            raise RuntimeError(f"{p.name}: {info['rows']} rows, {f.name} has {expected} lines")
        out[p.name] = info
        log(f"{p.name}: {info['rows']:,} rows")
    return out


# --- README and LICENSE ------------------------------------------------------

CREDIT = "GeoNames (https://www.geonames.org/), CC BY 4.0"


def snapshots(dest: Path) -> list[tuple[str, dict]]:
    """(day, manifest) of every dated snapshot under dest, newest first."""
    out = []
    for d in dest.iterdir() if dest.exists() else []:
        try:
            dt.date.fromisoformat(d.name)
        except ValueError:
            continue
        if (d / "manifest.json").exists():
            out.append((d.name, json.loads((d / "manifest.json").read_text())))
    return sorted(out, reverse=True)


LICENSE = f"""LICENSE

The files in this directory are dated snapshots of the GeoNames data dump
({BASE}), made by GeoNames ({PAGE}).

They are licensed under the Creative Commons Attribution 4.0 License
(https://creativecommons.org/licenses/by/4.0/), as the dump's readme.txt says:

  This work is licensed under a Creative Commons Attribution 4.0 License,
  see https://creativecommons.org/licenses/by/4.0/
  The Data is provided "as is" without warranty or any representation of
  accuracy, timeliness or completeness.

Credit: {CREDIT}

In every snapshot, raw/ holds the downloaded files unchanged. The Parquet files
were made from them:

  - The columns were named after readme.txt in snake case and typed:
    ids, population, elevation and dem as integers, latitude and longitude as
    floats, modification_date as a date, the rest as the text of the file
    (codes keep their leading zeros).
  - The four is_* columns of the alternate names ('1' or empty in the source)
    became booleans.
  - The gazetteer got a point geometry from longitude and latitude (WGS 84)
    and was cut, between countries, into several files.
  - Rows were sorted; values were not changed otherwise.
"""


def render_readme(dest: Path) -> str:
    rows = []
    for day, man in snapshots(dest):
        g = sum(v["rows"] for k, v in man["outputs"].items() if k.startswith("geoname/"))
        a = man["outputs"]["alternate_names.parquet"]["rows"]
        lm = man["sources"]["allCountries.zip"]["last_modified"]
        rows.append(f"| [{day}/]({day}/) | {g:,} | {a:,} | {lm} |")
    return f"""# GeoNames のスナップショット

[GeoNames]({PAGE}) のダンプ ({BASE}) を日付ごとに元のまま残し、Parquet も添えたもの。
上流は毎晩同じ URL の中身を差し替え、版番号もチェックサムも無く、過去の版は有料の購読でしか残らない。

## 出典とライセンス

CC BY 4.0。表示が必要。表示は「{CREDIT}」。詳しくは [LICENSE](LICENSE)。

## スナップショット

ディレクトリ名は、allCountries.zip の Last-Modified の UTC の日付。

| 日付 | geoname の行数 | alternate_names の行数 | allCountries.zip の Last-Modified |
|---|---:|---:|---|
{chr(10).join(rows)}

各ディレクトリの中身:

- `raw/`: 落としたファイルをそのまま。allCountries.zip、alternateNamesV2.zip、hierarchy.zip、adminCode5.zip と、小さい表 (admin1CodesASCII.txt、admin2Codes.txt、countryInfo.txt、featureCodes_en.txt、iso-languagecodes.txt、timeZones.txt) と readme.txt。
- `geoname/part-NN.parquet`: allCountries の地名辞書。`geometry` 列 (点、WGS 84) を足した GeoParquet。country_code、geonameid の順に並べ、国の途中では切らずに 512MB 未満の複数ファイルに分けてある。どの国がどのファイルにあるかは manifest.json の `countries` (最初と最後の国コード)。
- `alternate_names.parquet` (alternateNamesV2)、`hierarchy.parquet`、`admin_code5.parquet`。
- `manifest.json`: 各ファイルの Last-Modified、大きさ、sha256 と、出力の行数。

列の名前は readme.txt の列を snake case にしたもの。is_preferred_name などの 4 つの旗は、元の '1' か空を真偽値にしてある。行数は元のテキストの行数と照合してから置いている。

この README と LICENSE は、取得スクリプト (study-geoai-algo-py の scripts/mirror_geonames.py) を流すたびに作り直される。
"""


# --- main --------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--dry-run", action="store_true", help="show what would be taken")
    args = ap.parse_args()

    before = {f: head(BASE + f) for f in FILES}
    day = snapshot_date(before["allCountries.zip"]["last_modified"])
    for f, meta in before.items():
        log(f"{f}: {meta['bytes']:,} bytes, {meta['last_modified']}")
    log(f"snapshot {day}")
    if args.dry_run:
        return
    out = args.dest / day
    if (out / "manifest.json").exists():
        log(f"{out} is already there")
        return

    raw = args.scratch / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        fetch(BASE + f, raw / f, before[f])
        log(f"have {f}")
    after = {f: head(BASE + f) for f in FILES}
    moved = [f for f in FILES if after[f] != before[f]]
    if moved:
        raise RuntimeError(f"changed upstream while downloading: {moved}; run again")

    work = args.scratch / f"build-{day}"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    outputs = build(raw, work)
    shutil.rmtree(work / "text")
    shutil.rmtree(work / "tmp", ignore_errors=True)
    (work / "raw").mkdir()
    sources = {}
    for f in FILES:
        shutil.copyfile(raw / f, work / "raw" / f)
        sources[f] = before[f] | {"url": BASE + f, "sha256": sha256(raw / f)}

    manifest = {
        "source": BASE,
        "built": dt.datetime.now(dt.UTC).astimezone().replace(microsecond=0).isoformat(),
        "sources": sources,
        "outputs": outputs,
    }
    (work / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))

    # place the snapshot whole: a half-copied day never shows up under its name
    args.dest.mkdir(parents=True, exist_ok=True)
    tmp = args.dest / f".{day}.part"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(work, tmp)
    os.replace(tmp, out)
    (args.dest / "LICENSE").write_text(LICENSE)
    (args.dest / "README.md").write_text(render_readme(args.dest))
    log(f"placed in {out}")


if __name__ == "__main__":
    main()
