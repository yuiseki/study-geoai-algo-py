"""Mirror a dated snapshot of OurAirports under /www/html/static/ourairports/YYYY-MM-DD/.

OurAirports (https://ourairports.com/data/) rebuilds its 7 CSVs every night in
the GitHub repository davidmegginson/ourairports-data, at the same URLs. The
rows carry no update date, so an analysis can only be reproduced if the day's
files are kept. The data is in the public domain.

This script pins the latest commit of the repository, downloads the 7 CSVs at
that commit, checks each against the git blob it came from, and writes, in a
directory named after the commit's UTC day:

- csv/: the 7 CSVs, unchanged
- one Parquet per CSV, airports and navaids with a point geometry (GeoParquet)
- manifest.json: the commit, and the size, sha256 and rows of every file

Columns are text unless their name says otherwise (id and *ref integers, *_ft
and *_khz integers, *_deg and *_mhz floats); a value that does not fit stops
the run. The row count of every Parquet is checked against the CSV.

    uv run python scripts/mirror_ourairports.py
    uv run python scripts/mirror_ourairports.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path

import duckdb

REPO = "davidmegginson/ourairports-data"
PAGE = "https://ourairports.com/data/"
PUBLIC_PREFIX = "https://z.yuiseki.net/static/ourairports/"
DEST = Path("/www/html/static/ourairports")
SCRATCH = Path(tempfile.gettempdir()) / "study-geoai-mirror-ourairports"
UA = f"study-geoai-algo-py-mirror/1 (+{PUBLIC_PREFIX})"
FILES = [
    "airports", "runways", "navaids", "countries", "regions",
    "airport-frequencies", "airport-comments",
]  # fmt: skip
GEOMETRY = {"airports", "navaids"}
ORDER = {"countries": "code", "regions": "code"}


def log(msg: str) -> None:
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


# --- types -------------------------------------------------------------------


def column_type(name: str) -> str:
    """The SQL type of an OurAirports column, from its name alone."""
    low = name.lower()
    if low == "id" or low.endswith("ref"):
        return "BIGINT"
    if low.endswith(("_ft", "_khz")) or low in ("lighted", "closed"):
        return "INTEGER"
    if low.endswith(("_deg", "_degt", "_mhz")):
        return "DOUBLE"
    return "VARCHAR"


def csv_rows(path: Path) -> int:
    """Records in a CSV, counted without DuckDB (quoted fields may span lines)."""
    with open(path, newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def snapshot_date(committed: str) -> str:
    return (
        dt.datetime.fromisoformat(committed.replace("Z", "+00:00"))
        .astimezone(dt.UTC)
        .date()
        .isoformat()
    )


def select_sql(con: duckdb.DuckDBPyConnection, path: Path, geometry: bool = False) -> str:
    """A query reading one CSV with the types of column_type and trimmed names."""
    src = f"read_csv('{path}', header = true, all_varchar = true, strict_mode = true)"
    names = con.sql(f"select * from {src} limit 0").columns
    cols = []
    for n in names:
        t = column_type(n.strip())
        expr = f'"{n}"' if t == "VARCHAR" else f'cast("{n}" as {t})'
        if t in ("BIGINT", "INTEGER"):
            # a plain cast rounds '12.5' to 13 instead of failing
            expr = (
                f"""case when "{n}" is null or regexp_full_match("{n}", '-?[0-9]+') then {expr} """
                f"""else error('{path.name}: {n.strip()} is not an integer: ' || "{n}") end"""
            )
        cols.append(f'{expr} as "{n.strip()}"')
    if geometry:
        cols.append(
            "st_point(cast(longitude_deg as double), cast(latitude_deg as double)) as geometry"
        )
    return f"select {', '.join(cols)} from {src}"


# --- fetching ----------------------------------------------------------------


def get_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    tmp.replace(dest)


# --- README and LICENSE ------------------------------------------------------


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

The files in this directory are snapshots of OurAirports ({PAGE}), taken from
the GitHub repository {REPO} at the commit named in each manifest.json.

OurAirports releases its data to the public domain. The terms of use on the
download page say:

  All data is released to the Public Domain, and comes with no guarantee of
  accuracy or fitness for use.

and credit is asked for but not required:

  We'd love you to give us credit, like we give credit to our sources, but
  you're not required to.

The repository's own LICENSE file is The Unlicense, which speaks only of
software; the public domain statement for the data is the one on the site.

Credit, if you give it: Data from OurAirports (https://ourairports.com/).

In every snapshot, csv/ holds the source files unchanged. The Parquet files
were made from them: the header names were trimmed of spaces, columns were
typed by name (id and *ref as integers, *_ft and *_khz as integers, *_deg and
*_mhz as floats, the rest as the text of the CSV), and airports and navaids got
a point geometry from longitude_deg and latitude_deg (WGS 84). Values were not
changed.
"""


def render_readme(dest: Path) -> str:
    rows = []
    for day, man in snapshots(dest):
        a = man["outputs"]["airports.parquet"]["rows"]
        sha = man["commit"]["sha"]
        rows.append(
            f"| [{day}/]({day}/) | {a:,} | [{sha[:8]}](https://github.com/{REPO}/tree/{sha}) |"
        )
    return f"""# OurAirports のスナップショット

[OurAirports]({PAGE}) の 7 つの CSV を、日付ごとにそのまま残し、Parquet も添えたもの。
上流は毎晩同じ URL の中身を差し替え、行に更新日の列が無いので、その日のファイルを残しておかないと分析を再現できない。

## 出典とライセンス

public domain。表示は求められているが義務ではない。表示するなら「Data from OurAirports (https://ourairports.com/)」。詳しくは [LICENSE](LICENSE)。

## スナップショット

ディレクトリ名は、取った commit の UTC の日付。

| 日付 | airports の行数 | commit |
|---|---:|---|
{chr(10).join(rows)}

各ディレクトリの中身:

- `csv/`: 上流の 7 ファイルをそのまま。git の blob の SHA-1 と照合してから置いている。
- `airports.parquet`、`navaids.parquet`: `geometry` 列 (点、WGS 84) を足した GeoParquet。
- `runways.parquet`、`countries.parquet`、`regions.parquet`、`airport-frequencies.parquet`、`airport-comments.parquet`。
- `manifest.json`: commit、各ファイルの大きさ、sha256、行数。

列の型は名前で決めている。`id` と `*ref` は BIGINT、`*_ft` と `*_khz` と `lighted`、`closed` は INTEGER、`*_deg` と `*_mhz` は DOUBLE、それ以外は CSV のとおりの文字列 (`regions.local_code` の `02` のような先頭のゼロは残る)。

この README と LICENSE は、取得スクリプト (study-geoai-algo-py の scripts/mirror_ourairports.py) を流すたびに作り直される。
"""


# --- main --------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--dry-run", action="store_true", help="show the commit that would be taken")
    args = ap.parse_args()

    commit = get_json(f"https://api.github.com/repos/{REPO}/commits/main")
    sha, committed = commit["sha"], commit["commit"]["committer"]["date"]
    day = snapshot_date(committed)
    log(f"commit {sha} of {committed}, snapshot {day}")
    if args.dry_run:
        return
    out = args.dest / day
    if (out / "manifest.json").exists():
        log(f"{out} is already there")
        return

    tree = {
        e["path"]: e
        for e in get_json(f"https://api.github.com/repos/{REPO}/git/trees/{sha}")["tree"]
    }
    work = args.scratch / f"{day}-{sha[:8]}"
    (work / "csv").mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    sources, outputs = {}, {}
    for name in FILES:
        f = work / "csv" / f"{name}.csv"
        fetch(f"https://raw.githubusercontent.com/{REPO}/{sha}/{name}.csv", f)
        blob = tree[f"{name}.csv"]
        if git_blob_sha(f) != blob["sha"] or f.stat().st_size != blob["size"]:
            raise RuntimeError(f"{f.name} does not match blob {blob['sha']} of commit {sha}")
        rows = csv_rows(f)
        sources[f.name] = {
            "bytes": f.stat().st_size,
            "sha256": sha256(f),
            "git_blob": blob["sha"],
            "rows": rows,
        }

        p = work / f"{name}.parquet"
        query = select_sql(con, f, name in GEOMETRY)
        con.execute(
            f"copy ({query} order by {ORDER.get(name, 'id')}) to '{p}' (format parquet, compression zstd, write_bloom_filter false)"
        )
        got = con.sql(f"select count(*) from '{p}'").fetchone()[0]
        if got != rows:
            raise RuntimeError(f"{p.name}: {got} rows, {f.name} has {rows}")
        outputs[p.name] = {"bytes": p.stat().st_size, "sha256": sha256(p), "rows": got}
        log(f"{name}: {rows:,} rows")

    manifest = {
        "source": PAGE,
        "commit": {"repository": REPO, "sha": sha, "committed": committed},
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
