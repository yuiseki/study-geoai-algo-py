"""Mirror WorldPop rasters as Cloud Optimized GeoTIFFs under /www/html/static/worldpop/.

data.worldpop.org advertises Accept-Ranges but ignores Range and always sends
the whole file with 200, slowly, so GDAL's /vsicurl/ cannot open it. This
script downloads the files once, converts them to COG without changing any
value, checks the result against the original, and places it where
z.yuiseki.net/static/worldpop/ serves it with Range support.

Items are chosen from the WorldPop STAC API by country, project, year and
resolution. STAC datetime is the release date, not the data year, so the year
filter uses properties.year. Every GeoTIFF asset of a chosen item is mirrored
(the data asset of Population, both grids of Degree of Urbanisation, the 60
age and sex rasters of Age and Sex Structures); thumbnails and zip files are
not. Files already placed with the same source size as recorded are skipped,
so the command can be rerun with more years:

    uv run python scripts/mirror_worldpop.py --year 2020 2025
    uv run python scripts/mirror_worldpop.py --year 2015-2019 2021
    uv run python scripts/mirror_worldpop.py --year 2020 --resolution 1km --dry-run
    uv run python scripts/mirror_worldpop.py --project dug --year 2015-2030
    uv run python scripts/mirror_worldpop.py --project agesex --resolution 1km --year 2015-2030

--project takes the STAC properties.project or a short name (pop, dug,
agesex). --resolution takes 100m, 1km, none (items without one, such as
Degree of Urbanisation) or any (the default).

When an item has an archive asset (Age and Sex Structures) and several of its
GeoTIFFs are to be fetched, the archive is fetched once over FTP instead and
the GeoTIFFs are taken out of it: one file per GeoTIFF over FTP costs about a
minute of connection setup each. Every member must have the size that
data.worldpop.org gives for the GeoTIFF's own URL and the same first 256 KiB,
and pass the zip CRC. The archive itself is not placed.

manifest.json in the destination is the record of what is placed; README.md
and LICENSE are rebuilt from it on every run. The GDAL command-line tools and
the Python bindings (for the pixel comparison) come from --gdal-bin and
--gdal-python, since the uv environment has neither; both default to the GDAL
install that study_geoai.gdal finds (STUDY_GEOAI_GDAL_PREFIX, or ogr2ogr on PATH).

ftp.worldpop.org refuses connections beyond a limit per address (421 There
are too many connections). On 2026-09-28 it refused some of the 12 that
2 jobs x 6 connections opened; the exact limit was not measured. The default
is 1 job x 4 connections to stay under it.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from study_geoai import gdal

STAC_SEARCH = "https://api.stac.worldpop.org/search"
SOURCE_PREFIX = "https://data.worldpop.org/"
PUBLIC_PREFIX = "https://z.yuiseki.net/static/worldpop/"
DEST = Path("/www/html/static/worldpop")
SCRATCH = Path(tempfile.gettempdir()) / "study-geoai-mirror-worldpop"
# Cloudflare in front of z.yuiseki.net does not cache files above 512 MB and
# then answers the first Range request with the whole body.
MAX_BYTES = 512 * 1024 * 1024
COG_OPTIONS = [
    "-of", "COG",
    "-co", "COMPRESS=DEFLATE",
    "-co", "PREDICTOR=YES",
    "-co", "BLOCKSIZE=512",
    "-co", "OVERVIEWS=AUTO",
    "-co", "BIGTIFF=IF_SAFER",
]  # fmt: skip
# Class grids (Degree of Urbanisation) must not have interpolated overviews:
# the default resampling made codes 3 and 30 into 7 to 26 at low zoom.
CATEGORICAL = {"Degree of Urbanisation"}


def cog_options(project: str) -> list[str]:
    return COG_OPTIONS + (["-co", "RESAMPLING=NEAREST"] if project in CATEGORICAL else [])


UA = "study-geoai-mirror/1 (+https://z.yuiseki.net/static/worldpop/)"

_lock = threading.Lock()


def log(msg: str) -> None:
    stamp = dt.datetime.now().strftime("%H:%M:%S")
    with _lock:
        print(f"[{stamp}] {msg}", flush=True)


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# --- STAC ------------------------------------------------------------------


def get_json(url: str, timeout: float = 120) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def stac_items(country: str) -> list[dict]:
    """All items of one country collection, following rel=next links."""
    url = f"{STAC_SEARCH}?collections={country}&limit=100"
    items: list[dict] = []
    seen: set[str] = set()
    while url:
        page = get_json(url)
        for f in page.get("features", []):
            if f["id"] not in seen:
                seen.add(f["id"])
                items.append(f)
        nxt = [link for link in page.get("links", []) if link.get("rel") == "next"]
        url = nxt[0]["href"] if nxt and nxt[0].get("method", "GET") == "GET" else None
        if nxt and url is None:
            raise RuntimeError(f"unsupported next link: {nxt[0]}")
    return items


PROJECTS = {
    "pop": "Population",
    "dug": "Degree of Urbanisation",
    "agesex": "Age and Sex Structures",
}


def project_name(name: str) -> str:
    return PROJECTS.get(name.lower(), name)


def parse_years(values: list[str]) -> list[int]:
    """Years given as 2020 or as an inclusive range 2015-2030."""
    years: set[int] = set()
    for v in values:
        lo, sep, hi = v.partition("-")
        if sep:
            if int(hi) < int(lo):
                raise argparse.ArgumentTypeError(f"empty year range {v}")
            years.update(range(int(lo), int(hi) + 1))
        else:
            years.add(int(v))
    return sorted(years)


def resolution_key(item: dict) -> str:
    return item["properties"].get("resolution") or "none"


def select(
    items: list[dict], projects: list[str], years: list[int], resolutions: list[str]
) -> list[dict]:
    """Items of the projects and years; resolutions may hold 'none' and 'any'."""
    chosen = []
    for f in items:
        p = f["properties"]
        if p.get("project") not in projects or p.get("year") not in years:
            continue
        if "any" not in resolutions and resolution_key(f) not in resolutions:
            continue
        if not geotiff_assets(f):
            raise RuntimeError(f"{f['id']} has no GeoTIFF asset")
        chosen.append(f)

    def key(f: dict) -> tuple:
        return (f["properties"]["project"], f["properties"]["year"], resolution_key(f))

    found = {key(f) for f in chosen}
    present = {(k[0], k[2]) for k in found}
    missing = {(pr, y, r) for pr, r in present for y in years} - found
    for pr in projects:
        if not any(k[0] == pr for k in found):
            log(f"WARNING: no STAC item for project {pr!r} with {resolutions}")
    if missing:
        log(f"WARNING: no STAC item for (project, year, resolution) {sorted(missing)}")
    dup = len(chosen) - len(found)
    if dup:
        log(f"WARNING: {dup} extra items share a (project, year, resolution); all are mirrored")
    return sorted(chosen, key=lambda f: (*key(f), f["id"]))


def is_geotiff(asset: dict) -> bool:
    roles = asset.get("roles") or []
    return (asset.get("type") or "").startswith("image/tiff") and "overview" not in roles


def geotiff_assets(item: dict) -> list[tuple[str, dict]]:
    """(key, asset) of every GeoTIFF asset, one per href, in the item's order."""
    out, seen = [], set()
    for k, a in item.get("assets", {}).items():
        if is_geotiff(a) and a["href"] not in seen:
            seen.add(a["href"])
            out.append((k, a))
    return out


def archive_asset(item: dict) -> dict | None:
    for a in item.get("assets", {}).values():
        if "archive" in (a.get("roles") or []) and a["href"].endswith(".zip"):
            return a
    return None


def source_assets(item: dict) -> list[dict]:
    """The files on data.worldpop.org that STAC properties.size adds up.

    Checked on JPN 2026-09-28: Population's size is its one GeoTIFF, Degree
    of Urbanisation's is its 2 GeoTIFFs and 2 zips together, and Age and Sex
    Structures' is its GeoTIFFs without the archive.
    """
    out, seen = [], set()
    for a in item.get("assets", {}).values():
        roles = a.get("roles") or []
        if not a["href"].startswith(SOURCE_PREFIX) or "archive" in roles:
            continue
        if a["href"] not in seen:
            seen.add(a["href"])
            out.append(a)
    return out


def relpath(href: str) -> str:
    """Path under DEST: the source URL from GIS/ on."""
    if not href.startswith(SOURCE_PREFIX + "GIS/"):
        raise RuntimeError(f"unexpected data URL {href}")
    return href[len(SOURCE_PREFIX) :]


def stac_size_bytes(size: str) -> tuple[float, float]:
    """Range of byte counts that a STAC size such as '104.04 MB' can stand for.

    WorldPop writes MiB with two decimals (109,097,531 bytes is '104.04 MB').
    Accept rounding and truncation alike.
    """
    value, unit = size.split()
    scale = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}[unit.upper()]
    step = 10 ** -(len(value.split(".")[1]) if "." in value else 0)
    return ((float(value) - step) * scale, (float(value) + step) * scale)


# --- download ----------------------------------------------------------------


def head(url: str) -> dict[str, str]:
    out = subprocess.run(
        ["curl", "-sSIL", "--max-time", "60", "-A", UA, url],
        capture_output=True, text=True, timeout=90, check=True,
    )  # fmt: skip
    headers: dict[str, str] = {}
    for line in out.stdout.splitlines():
        if line.upper().startswith("HTTP/"):
            headers = {"status": line.split()[1]}
        elif ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return headers


def ftp_url(url: str) -> str:
    """The same file on WorldPop's FTP server, which honours REST (byte offsets)."""
    return "ftp://ftp.worldpop.org/" + url[len(SOURCE_PREFIX) :]


def download_ftp(url: str, out: Path, expected: int, attempts: int, connections: int) -> float:
    """Split download over FTP with aria2c; resumes from its control file on retry.

    Measured 2026-09-28: HTTPS gave 50 kB/s on one connection and ignores
    Range; FTP gave about 1.7 MB/s with 6 connections.
    """
    for n in range(1, attempts + 1):
        t0 = time.monotonic()
        cmd = [
            "aria2c", "-q", "--allow-overwrite=false", "--auto-file-renaming=false",
            "-x", str(connections), "-s", str(connections), "-k", "1M",
            "--file-allocation=none", "--connect-timeout=30", "--timeout=120",
            "--max-tries=5", "--retry-wait=10",
            "-d", str(out.parent), "-o", out.name, ftp_url(url),
        ]  # fmt: skip
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        took = time.monotonic() - t0
        size = out.stat().st_size if out.exists() else 0
        control = out.with_name(out.name + ".aria2")
        if r.returncode == 0 and size == expected and not control.exists():
            return took
        log(
            f"  attempt {n}/{attempts} failed for {out.name}: aria2c={r.returncode} "
            f"bytes={size}/{expected} {(r.stdout + r.stderr).strip()[:200]}"
        )
        time.sleep(min(60, 10 * n))
    raise RuntimeError(f"{url}: FTP download failed after {attempts} attempts")


def https_prefix(url: str, n: int) -> bytes:
    """The first n bytes over HTTPS (the connection is closed after them)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(n)


def download(url: str, out: Path, expected: int, attempts: int) -> float:
    """Whole-file download over HTTPS with retries (the server ignores Range, so no resume)."""
    hdr = out.with_suffix(".headers")
    for n in range(1, attempts + 1):
        out.unlink(missing_ok=True)
        t0 = time.monotonic()
        cmd = [
            "curl", "-sS", "-f", "-L", "-A", UA,
            "--connect-timeout", "30",
            # Abort a stalled transfer: under 10 kB/s for 120 s.
            "--speed-limit", "10000", "--speed-time", "120",
            "--max-time", "3600",
            "-D", str(hdr), "-o", str(out),
            "-w", "%{http_code} %{size_download}",
            url,
        ]  # fmt: skip
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3700)
        took = time.monotonic() - t0
        code, _, got = r.stdout.partition(" ")
        size = out.stat().st_size if out.exists() else 0
        if r.returncode == 0 and code == "200" and size == expected:
            cl = [
                line.split(":", 1)[1].strip()
                for line in hdr.read_text().splitlines()
                if line.lower().startswith("content-length:")
            ]
            if cl and int(cl[-1]) != size:
                raise RuntimeError(f"{url}: Content-Length {cl[-1]} != downloaded {size}")
            hdr.unlink(missing_ok=True)
            return took
        log(
            f"  attempt {n}/{attempts} failed for {out.name}: curl={r.returncode} "
            f"http={code} bytes={size}/{expected} {r.stderr.strip()[:200]}"
        )
        time.sleep(min(60, 10 * n))
    raise RuntimeError(f"{url}: download failed after {attempts} attempts")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --- GDAL --------------------------------------------------------------------


def gdalinfo(gdal_bin: Path, path: Path) -> dict:
    out = subprocess.run(
        [str(gdal_bin / "gdalinfo"), "-json", "-nomd", str(path)],
        capture_output=True, text=True, timeout=300, check=True,
    )  # fmt: skip
    return json.loads(out.stdout)


def gdalinfo_layout(gdal_bin: Path, path: Path) -> str | None:
    out = subprocess.run(
        [str(gdal_bin / "gdalinfo"), "-json", str(path)],
        capture_output=True, text=True, timeout=300, check=True,
    )  # fmt: skip
    md = json.loads(out.stdout).get("metadata", {}).get("IMAGE_STRUCTURE", {})
    return md.get("LAYOUT")


def shape_of(info: dict) -> dict:
    """The properties that must not change between the original and the COG."""
    return {
        "size": info["size"],
        "crs_wkt": info["coordinateSystem"]["wkt"],
        "geotransform": info["geoTransform"],
        "bands": [{"type": b["type"], "noDataValue": b.get("noDataValue")} for b in info["bands"]],
    }


PIXEL_COMPARE = r"""
import json, math, sys
import numpy as np
from osgeo import gdal
gdal.UseExceptions()
a = gdal.Open(sys.argv[1]); b = gdal.Open(sys.argv[2])
out = []
for i in range(1, a.RasterCount + 1):
    ba, bb = a.GetRasterBand(i), b.GetRasterBand(i)
    nd = ba.GetNoDataValue()
    w, h = a.RasterXSize, a.RasterYSize
    rows = 512
    sa = sb = 0.0
    valid = 0
    equal = True
    for y in range(0, h, rows):
        n = min(rows, h - y)
        xa = ba.ReadAsArray(0, y, w, n); xb = bb.ReadAsArray(0, y, w, n)
        if xa.dtype.kind == "f":
            same = np.array_equal(xa, xb, equal_nan=True)
        else:
            same = np.array_equal(xa, xb)
        equal = equal and same
        ma = np.ones(xa.shape, bool) if nd is None else (xa != nd)
        if xa.dtype.kind == "f":
            ma &= ~np.isnan(xa)
        mb = np.ones(xb.shape, bool) if nd is None else (xb != nd)
        if xb.dtype.kind == "f":
            mb &= ~np.isnan(xb)
        valid += int(ma.sum())
        sa = math.fsum([sa, float(xa[ma].astype(np.float64).sum())])
        sb = math.fsum([sb, float(xb[mb].astype(np.float64).sum())])
    out.append({"band": i, "equal": bool(equal), "valid_pixels": valid, "sum_src": sa, "sum_cog": sb})
print(json.dumps(out))
"""


def compare_pixels(gdal_python: Path, src: Path, cog: Path) -> list[dict]:
    out = subprocess.run(
        [str(gdal_python), "-c", PIXEL_COMPARE, str(src), str(cog)],
        capture_output=True, text=True, timeout=3600, check=True,
    )  # fmt: skip
    return json.loads(out.stdout)


# --- manifest, README, LICENSE -------------------------------------------------

MANIFEST_VERSION = 2


def load_manifest(dest: Path) -> dict:
    """The record of what is placed, with version 1 records read as version 2.

    Version 1 (until 2026-09-28) mirrored only the data asset of Population
    items; its records have no asset key, and stac_size is the item's size,
    which was that one file.
    """
    path = dest / "manifest.json"
    manifest = json.loads(path.read_text()) if path.exists() else {"files": {}}
    for r in manifest["files"].values():
        r.setdefault("asset", "data")
        r.setdefault("item_stac_size", r.get("stac_size"))
    manifest["manifest_version"] = MANIFEST_VERSION
    return manifest


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(text)
    os.replace(tmp, path)


def save_manifest(dest: Path, manifest: dict) -> None:
    manifest["files"] = dict(sorted(manifest["files"].items()))
    write_atomic(dest / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def fmt_int(n: int) -> str:
    return f"{n:,}"


# Items with more files than this are summarised per item in README.md and
# per directory in LICENSE; the per-file details stay in manifest.json.
PER_FILE_ROWS = 8

PROJECT_JA = {
    "Population": "総人口 (Population)",
    "Degree of Urbanisation": "都市化度 (Degree of Urbanisation)",
    "Age and Sex Structures": "年齢階級と性別ごとの人口 (Age and Sex Structures)",
}


def by_item(files: dict) -> dict[str, list[tuple[str, dict]]]:
    items: dict[str, list[tuple[str, dict]]] = {}
    for rel, r in files.items():
        items.setdefault(r["stac_id"], []).append((rel, r))
    return items


def via_label(r: dict) -> str:
    via = r.get("fetched_via", "")
    if r.get("archive_url"):
        return "FTP (zip)"
    return "FTP" if via.startswith("ftp:") else "HTTPS"


def sums_by_sex(fs: list[tuple[str, dict]]) -> str:
    """Sums per agesex:sex (f, m, and t for both); t already holds f and m."""
    groups: dict[str, list[float]] = {}
    for _, r in fs:
        sex = (r.get("asset_properties") or {}).get("agesex:sex", "all")
        groups.setdefault(sex, []).append(r["sum"])
    return ", ".join(f"{k} {math.fsum(v):,.1f}" for k, v in sorted(groups.items()))


def render_readme(manifest: dict) -> str:
    files = manifest["files"]
    items = by_item(files)
    projects = sorted({r["project"] for r in files.values()}, key=list(PROJECT_JA).index)
    lines = [
        "# WorldPop のグリッドデータ (COG)",
        "",
        "WorldPop (https://www.worldpop.org/) が配布するグリッドデータの GeoTIFF を、HTTP Range 要求で必要な部分だけを読めるように Cloud Optimized GeoTIFF (COG) に変換したもの。",
        "配布元の data.worldpop.org は Range 要求に応えず毎回ファイル全体を返すため、GDAL の /vsicurl/ などで直接読めない。そのための非公式のコピーで、WorldPop とは関係がない。",
        "",
        "置いてあるのは " + "、".join(PROJECT_JA[p] for p in projects) + "。",
        "STAC の item にある GeoTIFF の asset をすべて置いている。サムネイルと zip (年齢性別の個別の GeoTIFF をまとめた archive、都市化度の entities と statistics) は置いていない。",
        "",
        "パスは元の URL の `GIS/` 以降をそのまま写している。たとえば",
        "`https://data.worldpop.org/GIS/Population/...` は `https://z.yuiseki.net/static/worldpop/GIS/Population/...` にある。ファイル名も元のまま。",
        "",
        "## 変換",
        "",
        "GDAL 3.9 の `gdal_translate "
        + " ".join(COG_OPTIONS)
        + "` で COG に変換しただけで、値は変えていない (再投影、再標本化、データ型や nodata の変更はしていない)。",
        "都市化度 (区分のコードの格子) だけは `-co RESAMPLING=NEAREST` を足し、縮小版 (overview) でも元にあるコードだけが出るようにしている。ほかは既定の補間で縮小版を作っている。元の解像度の値はどれも元と同じ。",
        "変換のあと、どのファイルも元のファイルと比べて、幅と高さ、座標系、geotransform、nodata、データ型が一致すること、全画素の値が一致すること (nodata を除いた合計も一致すること) を確かめた。",
        "",
        "ライセンスと引用のしかたは [LICENSE](LICENSE) を見ること (CC BY 4.0)。どのファイルがどの DOI の引用に当たるかも LICENSE にある。",
        "",
        "## 置いてあるファイル",
        "",
        f"ファイルが {PER_FILE_ROWS} 個を超える item (年齢性別) は item ごとに 1 行にまとめた。ファイルごとの記録は [manifest.json](manifest.json) にある。",
        "年齢性別のファイル名の m は男性、f は女性、t は男女の計 (2020 年で合計が m と f の和に一致することを確かめた)。数字は年齢階級で、STAC の agesex:age_label では 00 が 0-1 years、01 が 1-5 years、05 が 5-10 years、以下 5 歳ごとで、90 が 90+ years。",
    ]
    for proj in projects:
        lines += ["", f"### {PROJECT_JA[proj]}", ""]
        rows = [(sid, fs) for sid, fs in items.items() if fs[0][1]["project"] == proj]
        if all(len(fs) <= PER_FILE_ROWS for _, fs in rows):
            lines += [
                "| ファイル | 年 | 解像度 | asset | 大きさ (bytes) | 幅 x 高さ | 型 | nodata を除いた合計 |",
                "|---|---|---|---|---|---|---|---|",
            ]
            for _, fs in rows:
                for rel, r in fs:
                    lines.append(
                        f"| [{Path(rel).name}]({rel}) | {r['year']} | {r['resolution'] or '-'} "
                        f"| {r['asset']} | {fmt_int(r['cog_bytes'])} | {r['width']} x {r['height']} "
                        f"| {r['data_type']} | {r['sum']:,.1f} |"
                    )
        else:
            lines += [
                "| ディレクトリ | 年 | 解像度 | ファイル数 | 大きさの合計 (bytes) | 幅 x 高さ | 型 | nodata を除いた合計 (性別ごと) |",
                "|---|---|---|---|---|---|---|---|",
            ]
            for _, fs in rows:
                r = fs[0][1]
                dirs = sorted({str(Path(rel).parent) for rel, _ in fs})
                lines.append(
                    f"| {', '.join(f'[{d}/]({d}/)' for d in dirs)} | {r['year']} | {r['resolution'] or '-'} "
                    f"| {len(fs)} | {fmt_int(sum(x['cog_bytes'] for _, x in fs))} "
                    f"| {r['width']} x {r['height']} | {r['data_type']} "
                    f"| {sums_by_sex(fs)} |"
                )
    lines += [
        "",
        "## 元データ",
        "",
        "元の大きさは HTTP の Content-Length、STAC の size の両方と一致することを確かめた。sha256 は元のファイルと COG の両方を載せる。data.worldpop.org の HTTPS は遅く Range にも応えないため、多くは同じファイルを ftp.worldpop.org から分割して取得し、先頭 256 KiB が HTTPS のものと一致することを確かめている。どちらから取ったかは「取得経路」の列にある。",
        "年齢性別の GeoTIFF は、1 ファイルずつ FTP で取ると接続のたびに 1 分ほどかかるため、同じ item の archive (zip) を FTP で 1 度だけ取り、その中から取り出した (取得経路 FTP (zip))。取り出したファイルは zip の CRC を通り、大きさと先頭 256 KiB が個別の URL の HTTPS のものと一致することを確かめている。",
        "",
        "| ファイル | 元の URL | 取得経路 | 取得日時 (UTC) | 元の大きさ (bytes) | 元の sha256 | COG の sha256 | STAC の item id | DOI |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    grouped = []
    for sid, fs in items.items():
        if len(fs) > PER_FILE_ROWS:
            grouped.append((sid, fs))
            continue
        for rel, r in fs:
            lines.append(
                f"| {rel} | {r['source_url']} | {via_label(r)} | {r['fetched_at']} | {fmt_int(r['source_bytes'])} "
                f"| {r['source_sha256']} | {r['cog_sha256']} | {r['stac_id']} "
                f"| [{r['doi']}](https://doi.org/{r['doi']}) |"
            )
    if grouped:
        lines += [
            "",
            "item ごとにまとめたもの (ファイルごとの URL と sha256 は manifest.json):",
            "",
            "| STAC の item id | ファイル数 | 取得経路 | archive の URL | 取得日時 (UTC) | 元の大きさの合計 (bytes) | DOI |",
            "|---|---|---|---|---|---|---|",
        ]
        for sid, fs in grouped:
            r = fs[0][1]
            archives = sorted({x.get("archive_url") or "-" for _, x in fs})
            vias = sorted({via_label(x) for _, x in fs})
            lines.append(
                f"| {sid} | {len(fs)} | {', '.join(vias)} | {', '.join(archives)} "
                f"| {min(x['fetched_at'] for _, x in fs)} | {fmt_int(sum(x['source_bytes'] for _, x in fs))} "
                f"| [{r['doi']}](https://doi.org/{r['doi']}) |"
            )
    lines += [
        "",
        "STAC の item は `https://api.stac.worldpop.org/collections/<国>/items/<item id>` にある。",
        "記録の本体は [manifest.json](manifest.json)。この README と LICENSE は、取得スクリプト (study-geoai の scripts/mirror_worldpop.py) を流すたびに作り直される。",
        "",
    ]
    return "\n".join(lines)


def render_license(manifest: dict) -> str:
    by_doi: dict[str, dict] = {}
    for rel, r in manifest["files"].items():
        e = by_doi.setdefault(r["doi"], {"citation": r["citation"], "files": []})
        e["files"].append(rel)
    lines = [
        "LICENSE",
        "",
        "All data files in this directory (the .tif files under GIS/) are adapted from",
        "WorldPop datasets published by WorldPop, School of Geography and Environmental",
        "Science, University of Southampton, under the Creative Commons Attribution 4.0",
        "International licence (CC BY 4.0).",
        "",
        "  Licence: https://creativecommons.org/licenses/by/4.0/",
        "  Legal code: https://creativecommons.org/licenses/by/4.0/legalcode",
        "  Original data: https://www.worldpop.org/ (files from https://data.worldpop.org/)",
        "",
        "Credit: cite the original datasets as WorldPop gives them (the",
        "coordinate_reference_system:citation property of each STAC item). Each",
        "dataset has its own DOI:",
        "",
    ]
    for _doi, e in sorted(by_doi.items()):
        cit = " ".join(e["citation"].split())
        lines.append(f"  {cit}")
        lines.append("")
        lines.append("    Files under this citation:")
        dirs: dict[str, list[str]] = {}
        for f in e["files"]:
            dirs.setdefault(str(Path(f).parent), []).append(f)
        for d, fs in dirs.items():
            if len(fs) > PER_FILE_ROWS:
                lines.append(f"      {d}/ ({len(fs)} .tif files)")
            else:
                lines += [f"      {f}" for f in fs]
        lines.append("")
    lines += [
        "These files were changed from the originals:",
        "",
        "  - Converted from GeoTIFF to Cloud Optimized GeoTIFF with GDAL 3.9",
        "    (DEFLATE compression with a predictor, 512 x 512 tiles, overviews).",
        "    The overviews are new, averaged or resampled images added for display;",
        "    they are not part of the original data.",
        "  - No pixel value of the full-resolution image was changed. The size,",
        "    coordinate reference system, geotransform, data type and nodata value",
        "    are the same as in the originals. See README.md for the checks, the",
        "    source URLs, dates, sizes and sha256 sums (manifest.json has them for",
        "    every file).",
        "",
        "These files are provided as is, without warranty of any kind. The copy on",
        "this server is unofficial and not affiliated with or endorsed by WorldPop",
        "or the University of Southampton. For the current data, use the original",
        "sources.",
        "",
    ]
    return "\n".join(lines)


# --- one item --------------------------------------------------------------------


def up_to_date(dest: Path, rel: str, record: dict | None, source_bytes: int) -> bool:
    path = dest / rel
    return (
        record is not None
        and path.exists()
        and record.get("source_bytes") == source_bytes
        and path.stat().st_size == record.get("cog_bytes")
    )


def head_ok(url: str) -> dict[str, str]:
    h = head(url)
    if h.get("status") != "200" or "content-length" not in h:
        raise RuntimeError(f"{url}: HEAD returned {h}")
    return h


def check_prefix(rel: str, path: Path, prefix: bytes) -> None:
    """The copy must be the file that the HTTPS URL serves (as far as prefix goes)."""
    with path.open("rb") as f:
        if f.read(len(prefix)) != prefix:
            raise RuntimeError(f"{rel}: copy differs from HTTPS in the first {len(prefix)} bytes")


PREFIX_BYTES = 256 * 1024


def process_item(item: dict, args: argparse.Namespace, manifest: dict) -> dict[str, int]:
    p = item["properties"]
    tifs = geotiff_assets(item)
    sources = source_assets(item)
    with ThreadPoolExecutor(max_workers=args.meta_jobs) as pool:
        heads = dict(
            zip(
                [a["href"] for a in sources],
                pool.map(lambda a: head_ok(a["href"]), sources),
                strict=True,
            )
        )
    sizes = {href: int(h["content-length"]) for href, h in heads.items()}
    lo, hi = stac_size_bytes(p["size"])
    total = sum(sizes.values())
    if not lo <= total <= hi:
        raise RuntimeError(
            f"{item['id']}: Content-Length {total} of {len(sizes)} files vs STAC size {p['size']}"
        )
    for _k, a in tifs:
        if "file:size" in a:
            flo, fhi = stac_size_bytes(a["file:size"])
            if not flo <= sizes[a["href"]] <= fhi:
                raise RuntimeError(
                    f"{a['href']}: Content-Length {sizes[a['href']]} vs STAC {a['file:size']}"
                )

    counts = {"skipped": 0, "placed": 0, "dry-run": 0}
    todo = []
    for k, a in tifs:
        rel = relpath(a["href"])
        with _lock:
            record = manifest["files"].get(rel)
        if not args.rebuild and up_to_date(args.dest, rel, record, sizes[a["href"]]):
            counts["skipped"] += 1
            continue
        if sizes[a["href"]] > MAX_BYTES:
            raise RuntimeError(
                f"{rel}: source is {sizes[a['href']]} bytes, above {MAX_BYTES}; stopping"
            )
        todo.append((k, a))
    if counts["skipped"]:
        log(f"skip {counts['skipped']} of {len(tifs)} files of {item['id']} (already placed)")
    if not todo:
        return counts
    arch = archive_asset(item)
    use_arch = (
        arch is not None and args.via == "ftp" and args.archive and len(todo) >= args.archive_min
    )
    if args.dry_run:
        if len(todo) > PER_FILE_ROWS:
            dirs = sorted({str(Path(relpath(a["href"])).parent) for _, a in todo})
            log(
                f"would fetch {len(todo)} files of {item['id']} into {', '.join(dirs)} "
                f"({fmt_int(sum(sizes[a['href']] for _, a in todo))} bytes)"
            )
        else:
            for _k, a in todo:
                log(f"would fetch {relpath(a['href'])} ({fmt_int(sizes[a['href']])} bytes)")
        if use_arch:
            log(f"  (taken out of {arch['href']})")
        counts["dry-run"] = len(todo)
        return counts

    work = Path(tempfile.mkdtemp(prefix=item["id"] + ".", dir=args.scratch))
    try:
        if use_arch:
            counts["placed"] += fetch_from_archive(item, arch, todo, heads, args, manifest, work)
        else:
            for k, a in todo:
                href = a["href"]
                rel = relpath(href)
                src = work / Path(rel).name
                log(f"fetch {href} ({fmt_int(sizes[href])} bytes)")
                fetched_at = now_utc()
                if args.via == "ftp":
                    took = download_ftp(href, src, sizes[href], args.attempts, args.connections)
                    check_prefix(rel, src, https_prefix(href, PREFIX_BYTES))
                    via = {"fetched_via": ftp_url(href)}
                else:
                    took = download(href, src, sizes[href], args.attempts)
                    via = {"fetched_via": href}
                log(f"  fetched {src.name} in {took:.0f} s ({sizes[href] / took / 1e6:.2f} MB/s)")
                place(item, k, a, src, heads[href], fetched_at, took, via, args, manifest, work)
                counts["placed"] += 1
        return counts
    finally:
        shutil.rmtree(work, ignore_errors=True)


def fetch_from_archive(
    item: dict,
    arch: dict,
    todo: list[tuple[str, dict]],
    heads: dict[str, dict[str, str]],
    args: argparse.Namespace,
    manifest: dict,
    work: Path,
) -> int:
    """Fetch the item's zip once and place the wanted GeoTIFFs out of it."""
    ah = head_ok(arch["href"])
    arch_bytes = int(ah["content-length"])
    if "file:size" in arch:
        lo, hi = stac_size_bytes(arch["file:size"])
        if not lo <= arch_bytes <= hi:
            raise RuntimeError(
                f"{arch['href']}: Content-Length {arch_bytes} vs STAC {arch['file:size']}"
            )
    zpath = work / Path(arch["href"]).name
    log(f"fetch {arch['href']} ({fmt_int(arch_bytes)} bytes) for {len(todo)} GeoTIFFs")
    with ThreadPoolExecutor(max_workers=args.meta_jobs) as pool:
        # The HTTPS prefixes are slow (about 50 kB/s each); fetch them meanwhile.
        prefixes = {a["href"]: pool.submit(https_prefix, a["href"], PREFIX_BYTES) for _, a in todo}
        fetched_at = now_utc()
        took = download_ftp(arch["href"], zpath, arch_bytes, args.attempts, args.connections)
        log(f"  fetched {zpath.name} in {took:.0f} s ({arch_bytes / took / 1e6:.2f} MB/s)")
        arch_sha = sha256(zpath)
        with zipfile.ZipFile(zpath) as zf:
            members = {Path(i.filename).name: i for i in zf.infolist() if not i.is_dir()}
            wanted = {Path(a["href"]).name for _, a in geotiff_assets(item)}
            extra = sorted(set(members) - wanted)
            lacking = sorted(wanted - set(members))
            log(
                f"  {zpath.name}: {len(members)} members, {len(wanted & set(members))} are "
                f"GeoTIFF assets of the item; not assets: {extra or 'none'}; "
                f"assets not in it: {lacking or 'none'}"
            )
            placed = 0
            for k, a in todo:
                href = a["href"]
                rel = relpath(href)
                name = Path(rel).name
                if name not in members:
                    raise RuntimeError(f"{rel}: not in {arch['href']}")
                src = work / name
                with zf.open(members[name]) as fin, src.open("wb") as fout:
                    shutil.copyfileobj(fin, fout, 1 << 20)  # raises on a bad CRC
                expected = int(heads[href]["content-length"])
                if src.stat().st_size != expected:
                    raise RuntimeError(
                        f"{rel}: zip member is {src.stat().st_size} bytes, URL {expected}"
                    )
                check_prefix(rel, src, prefixes[href].result())
                via = {
                    "fetched_via": ftp_url(arch["href"]) + "#" + members[name].filename,
                    "archive_url": arch["href"],
                    "archive_member": members[name].filename,
                    "archive_bytes": arch_bytes,
                    "archive_sha256": arch_sha,
                    "archive_last_modified": ah.get("last-modified"),
                }
                place(item, k, a, src, heads[href], fetched_at, took, via, args, manifest, work)
                src.unlink()
                placed += 1
    return placed


def place(
    item: dict,
    key: str,
    asset: dict,
    src: Path,
    h: dict[str, str],
    fetched_at: str,
    took: float,
    via: dict,
    args: argparse.Namespace,
    manifest: dict,
    work: Path,
) -> None:
    """Convert one fetched GeoTIFF to COG, verify it against the original and place it."""
    p = item["properties"]
    href = asset["href"]
    rel = relpath(href)
    source_bytes = src.stat().st_size
    src_sha = sha256(src)

    cog = work / (src.stem + ".cog.tif")
    t0 = time.monotonic()
    subprocess.run(
        [str(args.gdal_bin / "gdal_translate"), "-q", *cog_options(p["project"]), str(src), str(cog)],
        check=True, timeout=3600,
    )  # fmt: skip
    cog_bytes = cog.stat().st_size
    log(f"  {src.name}: converted in {time.monotonic() - t0:.0f} s: {fmt_int(cog_bytes)} bytes")
    if cog_bytes > MAX_BYTES:
        raise RuntimeError(f"{rel}: COG is {cog_bytes} bytes, above {MAX_BYTES}; stopping")

    a, b = shape_of(gdalinfo(args.gdal_bin, src)), shape_of(gdalinfo(args.gdal_bin, cog))
    if a != b:
        raise RuntimeError(f"{rel}: raster properties changed:\n{a}\n{b}")
    if (a["size"][0], a["size"][1]) != (p.get("data:width"), p.get("data:height")):
        raise RuntimeError(f"{rel}: size {a['size']} differs from STAC")
    layout = gdalinfo_layout(args.gdal_bin, cog)
    if layout != "COG":
        raise RuntimeError(f"{rel}: LAYOUT is {layout}, not COG")
    t0 = time.monotonic()
    bands = compare_pixels(args.gdal_python, src, cog)
    for bd in bands:
        if not bd["equal"] or bd["sum_src"] != bd["sum_cog"]:
            raise RuntimeError(f"{rel}: pixel values differ: {bd}")
    log(
        f"  {src.name}: verified in {time.monotonic() - t0:.0f} s: shape, CRS, geotransform, "
        f"nodata, type and all pixels equal; sum {bands[0]['sum_src']:,.1f} "
        f"over {fmt_int(bands[0]['valid_pixels'])} pixels"
    )
    cog_sha = sha256(cog)

    final = args.dest / rel
    final.parent.mkdir(parents=True, exist_ok=True)
    partial = final.with_name(final.name + ".partial")
    shutil.copyfile(cog, partial)
    if sha256(partial) != cog_sha:
        partial.unlink()
        raise RuntimeError(f"{rel}: copy to {partial} does not match")
    os.chmod(partial, 0o644)
    os.replace(partial, final)
    cog.unlink()

    only_file = len(source_assets(item)) == 1
    record = {
        "stac_id": item["id"],
        "collection": item.get("collection"),
        "project": p["project"],
        "year": p["year"],
        "resolution": p.get("resolution"),
        "asset": key,
        "asset_title": asset.get("title"),
        "title": p.get("title"),
        "release": p.get("Release"),
        "version": p.get("Version"),
        "doi": p.get("Digital Object Identifier (DOI)"),
        "citation": p.get("coordinate_reference_system:citation"),
        "source_url": href,
        "source_last_modified": h.get("last-modified"),
        "source_etag": h.get("etag"),
        "fetched_at": fetched_at,
        "download_seconds": round(took, 1),
        **via,
        "source_bytes": source_bytes,
        # The STAC size this file was checked against: its asset's file:size,
        # or the item's size when the item has this one file only.
        "stac_size": asset.get("file:size") or (p["size"] if only_file else None),
        "item_stac_size": p["size"],
        "source_sha256": src_sha,
        "cog_bytes": cog_bytes,
        "cog_sha256": cog_sha,
        "public_url": PUBLIC_PREFIX + rel,
        "width": a["size"][0],
        "height": a["size"][1],
        "data_type": a["bands"][0]["type"],
        "nodata": a["bands"][0]["noDataValue"],
        "valid_pixels": bands[0]["valid_pixels"],
        "sum": bands[0]["sum_src"],
        "gdal_translate_options": cog_options(p["project"]),
    }
    extra = {k: v for k, v in asset.items() if ":" in k and k != "file:size"}
    if extra:
        record["asset_properties"] = extra
    if len(a["bands"]) > 1:
        record["bands"] = len(a["bands"])
    with _lock:
        manifest["files"][rel] = record
        save_manifest(args.dest, manifest)
    log(f"  placed {final}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--country", default="JPN", help="STAC collection (ISO alpha-3), default JPN")
    ap.add_argument(
        "--year", nargs="+", required=True, help="data years, e.g. 2020 2025 or 2015-2030"
    )
    ap.add_argument(
        "--project",
        nargs="+",
        default=["Population"],
        help="properties.project or pop, dug, agesex; default Population",
    )
    ap.add_argument(
        "--resolution",
        nargs="+",
        default=["any"],
        help="100m, 1km, none (items without a resolution) or any (default)",
    )
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    gdal_root = gdal.prefix()
    ap.add_argument("--gdal-bin", type=Path, default=gdal_root / "bin" if gdal_root else None)
    ap.add_argument(
        "--gdal-python", type=Path, default=gdal_root / "bin" / "python" if gdal_root else None
    )
    ap.add_argument("--attempts", type=int, default=3, help="download attempts per file")
    ap.add_argument(
        "--via",
        choices=["ftp", "https"],
        default="ftp",
        help="ftp: aria2c split over ftp.worldpop.org (default); https: curl, one stream",
    )
    ap.add_argument("--connections", type=int, default=4, help="aria2c connections per file (ftp)")
    ap.add_argument("--jobs", type=int, default=1, help="items fetched at the same time")
    ap.add_argument(
        "--meta-jobs",
        type=int,
        default=4,
        help="HEAD and prefix requests at the same time per item",
    )
    ap.add_argument(
        "--no-archive",
        dest="archive",
        action="store_false",
        help="fetch each GeoTIFF on its own even when the item has an archive",
    )
    ap.add_argument(
        "--archive-min",
        type=int,
        default=5,
        help="use the item's archive when at least this many of its GeoTIFFs are wanted",
    )
    ap.add_argument("--dry-run", action="store_true", help="list what would be fetched")
    ap.add_argument(
        "--rebuild", action="store_true", help="fetch and place again even if already placed"
    )
    args = ap.parse_args()
    if args.gdal_bin is None or args.gdal_python is None:
        ap.error(
            f"no GDAL install found; pass --gdal-bin and --gdal-python or set {gdal.PREFIX_VAR}"
        )
    years = parse_years(args.year)
    projects = [project_name(x) for x in args.project]
    resolutions = [x.lower() for x in args.resolution]

    log(f"STAC search {args.country}")
    items = select(stac_items(args.country), projects, years, resolutions)
    log(f"{len(items)} items: {', '.join(f['id'] for f in items)}")
    args.dest.mkdir(parents=True, exist_ok=True)
    args.scratch.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(args.dest)

    failures = []
    totals = {"skipped": 0, "placed": 0, "dry-run": 0}
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(process_item, f, args, manifest): f["id"] for f in items}
        for fut, item_id in futures.items():
            try:
                for k, v in fut.result().items():
                    totals[k] += v
            except Exception as e:  # report every item, then fail
                failures.append(item_id)
                log(f"ERROR {item_id}: {e}")

    log(f"files: {totals}")
    if not args.dry_run and manifest["files"]:
        save_manifest(args.dest, manifest)
        write_atomic(args.dest / "README.md", render_readme(manifest))
        write_atomic(args.dest / "LICENSE", render_license(manifest))
        log("README.md and LICENSE rebuilt")
    with contextlib.suppress(OSError):
        args.scratch.rmdir()  # only if empty
    if failures:
        log(f"FAILED: {failures}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
