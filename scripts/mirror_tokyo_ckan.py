"""Mirror facility CSVs of the 23 wards of Tokyo under /sata_hdd_24tb/www/html/static/tokyo-ckan-files/.

The files are listed in the Tokyo Open Data Catalog (CKAN), indexed as a static
STAC at https://stac.yuiseki.net/tokyo-ckan/, but they live on each ward's own
site, where links break (one Taito City CSV was already 404 on 2026-09-28).
This copies them unchanged, one directory per dataset, so study-geoai-algo-py can read
the same bytes later. Only CC-BY-4.0 datasets are copied.

    uv run python scripts/mirror_tokyo_ckan.py              # the default families
    uv run python scripts/mirror_tokyo_ckan.py --family 投票所一覧 AED設置箇所一覧
    uv run python scripts/mirror_tokyo_ckan.py --dry-run

Every attempt is recorded in manifest.json, including failures (HTTP status or
error), so a missing file shows up as missing. Files already placed are
fetched again and replaced only if their bytes changed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import study_geoai  # noqa: F401  (drops anaconda's GDAL variables)
from study_geoai.db import connect

ITEMS = "https://stac.yuiseki.net/tokyo-ckan/items.parquet"
ASSETS = "https://stac.yuiseki.net/tokyo-ckan/assets.parquet"
DEST = Path("/sata_hdd_24tb/www/html/static/tokyo-ckan-files")
PUBLIC = "https://z.yuiseki.net/static/tokyo-ckan-files"
UA = "study-geoai-algo-py-mirror/1 (+https://z.yuiseki.net/static/tokyo-ckan-files/)"
MAX_BYTES = 50 * 1024 * 1024
FAMILIES = [
    "指定緊急避難場所一覧", "防災行政無線設置一覧", "公衆無線LANアクセスポイント一覧",
    "AED設置箇所一覧", "公共施設一覧", "投票所一覧", "公立図書館情報", "医療機関一覧",
    "介護サービス事業所一覧", "公衆トイレ一覧", "都市公園・都立公園一覧", "スポーツ施設一覧",
    "子育て施設一覧", "観光施設一覧", "文化財一覧", "教育機関一覧", "公営駐輪場一覧",
]  # fmt: skip
# CKAN organisations of the 23 wards: t + the 6-digit local government code.
WARDS = r"^t131(0[1-9]|1[0-9]|2[0-3])[0-9]$"


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def candidates(families: list[str]) -> list[dict]:
    con = connect()
    fams = ", ".join("'" + f.replace("'", "''") + "'" for f in families)
    rows = con.sql(f"""
        select i.collection, i.organization_title, i.id as item_id, i.title as item_title,
               i.family, i.license, i.ckan_url, a.asset_key, a.title as asset_title, a.href
        from '{ITEMS}' i join '{ASSETS}' a on a.item_id = i.id
        where regexp_matches(i.collection, '{WARDS}') and a.format = 'CSV'
          and i.family in ({fams}) and i.license = 'CC-BY-4.0'
        order by i.collection, i.id, a.asset_key
    """)
    names = [d[0] for d in rows.description]
    return [dict(zip(names, r, strict=True)) for r in rows.fetchall()]


def filename(href: str, asset_key: str) -> str:
    name = urllib.parse.unquote(Path(urllib.parse.urlparse(href).path).name) or asset_key
    name = re.sub(r"[^\w.\-]", "_", name)
    return name if name.lower().endswith(".csv") else name + ".csv"


def encoding(data: bytes) -> str | None:
    """utf-8, utf-16 or cp932 for text; xlsx or zip when a spreadsheet is named .csv; None."""
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return "utf-16"
    if data[:4] == b"PK\x03\x04":
        return "xlsx" if b"[Content_Types].xml" in data[:2048] else "zip"
    for enc in ("utf-8-sig", "cp932"):
        try:
            data.decode(enc)
            return "utf-8" if enc == "utf-8-sig" else enc
        except UnicodeDecodeError:
            continue
    return None


def fetch(href: str) -> tuple[bytes | None, dict]:
    req = urllib.request.Request(href, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read(MAX_BYTES + 1)
            info = {"status": r.status, "content_type": r.headers.get("Content-Type")}
    except urllib.error.HTTPError as e:
        return None, {"status": e.code, "error": str(e)}
    except Exception as e:  # network errors, timeouts
        return None, {"status": None, "error": f"{type(e).__name__}: {e}"}
    if len(data) > MAX_BYTES:
        return None, {**info, "error": f"larger than {MAX_BYTES} bytes"}
    return data, info


def write_docs(dest: Path, manifest: dict) -> None:
    files = sorted(manifest["files"].values(), key=lambda r: (r["collection"], r["item_id"]))
    ok = [r for r in files if r.get("path")]
    bad = [r for r in files if not r.get("path")]
    lines = [
        "# 東京 23 区の施設一覧 (CSV の再配布)",
        "",
        "東京都オープンデータカタログ (CKAN) に載っている 23 区の施設一覧の CSV を、取得したときのまま (中身を変えずに) 置いたもの。",
        "元のファイルは各区のサイトにあり、リンクが切れることがあるので、study-geoai-algo-py で同じ中身を読めるように写した。",
        "CC-BY-4.0 のデータセットだけを置いている。ライセンスとクレジットは [LICENSE](LICENSE)、記録の本体は [manifest.json](manifest.json)。",
        "",
        f"置いたファイル {len(ok)}、取得できなかったもの {len(bad)}。",
        "",
        "| 区 | 共通項目 | データセット | ファイル | 大きさ | 文字コード | 取得日時 (UTC) |",
        "|---|---|---|---|---:|---|---|",
    ]
    for r in ok:
        lines.append(
            f"| {r['organization_title']} | {r['family']} | [{r['item_title']}]({r['ckan_url']}) "
            f"| [{r['path']}]({r['path']}) | {r['bytes']:,} | {r['encoding']} | {r['fetched_at']} |"
        )
    if bad:
        lines += [
            "",
            "## 取得できなかったもの",
            "",
            "| 区 | データセット | 元の URL | 結果 |",
            "|---|---|---|---|",
        ]
        for r in bad:
            lines.append(
                f"| {r['organization_title']} | {r['item_title']} | {r['href']} "
                f"| {r.get('status')} {r.get('error', '')} |"
            )
    (dest / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    lic = [
        "LICENSE",
        "",
        "Every file under this directory is an unmodified copy of a CSV published by one of",
        "the 23 wards of Tokyo through the Tokyo Open Data Catalog",
        "(https://catalog.data.metro.tokyo.lg.jp/) under the Creative Commons Attribution 4.0",
        "International licence (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/deed.ja",
        "",
        "Credit for each dataset (publisher, dataset, licence):",
        "",
    ]
    seen = set()
    for r in ok:
        key = (r["organization_title"], r["item_title"])
        if key not in seen:
            seen.add(key)
            lic.append(
                f"  {r['organization_title']}、{r['item_title']}、CC BY 4.0 ({r['ckan_url']})"
            )
    lic += [
        "",
        "Source URLs, dates and sha256 of each file are in manifest.json and README.md.",
        "These copies are provided as is, without warranty of any kind. This server is not",
        "affiliated with the Tokyo Metropolitan Government or the wards; use the catalog",
        "for current data.",
        "",
    ]
    (dest / "LICENSE").write_text("\n".join(lic), encoding="utf-8")


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--family", nargs="+", default=FAMILIES)
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--pause", type=float, default=1.0, help="seconds between requests")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    todo = candidates(args.family)
    print(f"{len(todo)} CSV assets in {len({t['collection'] for t in todo})} wards", flush=True)
    if args.dry_run:
        for t in todo:
            print(t["organization_title"], t["family"], t["href"])
        return 0

    args.dest.mkdir(parents=True, exist_ok=True)
    mpath = args.dest / "manifest.json"
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {"files": {}}
    counts = {"placed": 0, "unchanged": 0, "failed": 0}
    for t in todo:
        key = f"{t['item_id']}/{t['asset_key']}"
        data, info = fetch(t["href"])
        record = {**t, **info, "fetched_at": now_utc()}
        if data is None:
            old = manifest["files"].get(key, {})
            if old.get("path"):  # keep the copy placed earlier, note the failure
                record = {**old, "last_attempt": record["fetched_at"], "last_error": info}
            manifest["files"][key] = record
            counts["failed"] += 1
            print(f"FAIL {t['organization_title']} {t['item_title']}: {info}", flush=True)
        else:
            sha = hashlib.sha256(data).hexdigest()
            rel = f"{t['collection']}/{t['item_id']}/{filename(t['href'], t['asset_key'])}"
            final = args.dest / rel
            old = manifest["files"].get(key, {})
            if old.get("sha256") == sha and final.exists():
                counts["unchanged"] += 1
            else:
                final.parent.mkdir(parents=True, exist_ok=True)
                tmp = final.with_name(final.name + ".partial")
                tmp.write_bytes(data)
                os.replace(tmp, final)
                counts["placed"] += 1
            record.update(
                path=rel, public_url=f"{PUBLIC}/{rel}", bytes=len(data), sha256=sha,
                encoding=encoding(data),
            )  # fmt: skip
            manifest["files"][key] = record
        write_atomic(mpath, json.dumps(manifest, ensure_ascii=False, indent=1))
        time.sleep(args.pause)
    write_docs(args.dest, manifest)
    print(counts, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
