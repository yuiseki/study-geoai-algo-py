"""Mirror WorldPop rasters as Cloud Optimized GeoTIFFs under /www/html/static/worldpop/.

data.worldpop.org advertises Accept-Ranges but ignores Range and always sends
the whole file with 200, slowly, so GDAL's /vsicurl/ cannot open it. This
script downloads the files once, converts them to COG without changing any
value, checks the result against the original, and places it where
z.yuiseki.net/static/worldpop/ serves it with Range support.

Items are chosen from the WorldPop STAC API by country, project, year and
resolution. STAC datetime is the release date, not the data year, so the year
filter uses properties.year. Files already placed with the same source size
as recorded are skipped, so the command can be rerun with more years:

    uv run python scripts/mirror_worldpop.py --year 2020 2025
    uv run python scripts/mirror_worldpop.py --year 2015 2016 2017
    uv run python scripts/mirror_worldpop.py --year 2020 --resolution 1km --dry-run

manifest.json in the destination is the record of what is placed; README.md
and LICENSE are rebuilt from it on every run. The GDAL command-line tools and
the Python bindings (for the pixel comparison) come from --gdal-bin and
--gdal-python, since the uv environment has neither.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

STAC_SEARCH = "https://api.stac.worldpop.org/search"
SOURCE_PREFIX = "https://data.worldpop.org/"
PUBLIC_PREFIX = "https://z.yuiseki.net/static/worldpop/"
DEST = Path("/www/html/static/worldpop")
SCRATCH = Path(tempfile.gettempdir()) / "study-geoai-mirror-worldpop"
GDAL_BIN = Path("/home/yuiseki/anaconda3/bin")
GDAL_PYTHON = Path("/home/yuiseki/anaconda3/bin/python")
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


def select(items: list[dict], project: str, years: list[int], resolutions: list[str]) -> list[dict]:
    chosen = []
    for f in items:
        p = f["properties"]
        if p.get("project") != project or p.get("year") not in years:
            continue
        if p.get("resolution") not in resolutions:
            continue
        if "data" not in f.get("assets", {}):
            raise RuntimeError(f"{f['id']} has no data asset")
        chosen.append(f)
    missing = {(y, r) for y in years for r in resolutions} - {
        (f["properties"]["year"], f["properties"]["resolution"]) for f in chosen
    }
    if missing:
        log(f"WARNING: no STAC item for (year, resolution) {sorted(missing)}")
    dup = len(chosen) - len(
        {(f["properties"]["year"], f["properties"]["resolution"]) for f in chosen}
    )
    if dup:
        log(f"WARNING: {dup} extra items share a (year, resolution); all are mirrored")
    return sorted(chosen, key=lambda f: (f["properties"]["year"], f["properties"]["resolution"]))


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


def load_manifest(dest: Path) -> dict:
    path = dest / "manifest.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"files": {}}


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(text)
    os.replace(tmp, path)


def save_manifest(dest: Path, manifest: dict) -> None:
    manifest["files"] = dict(sorted(manifest["files"].items()))
    write_atomic(dest / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def fmt_int(n: int) -> str:
    return f"{n:,}"


def render_readme(manifest: dict) -> str:
    files = manifest["files"]
    lines = [
        "# WorldPop の人口グリッド (COG)",
        "",
        "WorldPop (https://www.worldpop.org/) が配布する人口グリッドの GeoTIFF を、HTTP Range 要求で必要な部分だけを読めるように Cloud Optimized GeoTIFF (COG) に変換したもの。",
        "配布元の data.worldpop.org は Range 要求に応えず毎回ファイル全体を返すため、GDAL の /vsicurl/ などで直接読めない。そのための非公式のコピーで、WorldPop とは関係がない。",
        "",
        "パスは元の URL の `GIS/` 以降をそのまま写している。たとえば",
        "`https://data.worldpop.org/GIS/Population/...` は `https://z.yuiseki.net/static/worldpop/GIS/Population/...` にある。ファイル名も元のまま。",
        "",
        "## 変換",
        "",
        "GDAL 3.9 の `gdal_translate "
        + " ".join(COG_OPTIONS)
        + "` で COG に変換しただけで、値は変えていない (再投影、再標本化、データ型や nodata の変更はしていない)。",
        "変換のあと、元のファイルと比べて、幅と高さ、座標系、geotransform、nodata、データ型が一致すること、全画素の値が一致すること (nodata を除いた合計も一致すること) を確かめた。",
        "",
        "ライセンスと引用のしかたは [LICENSE](LICENSE) を見ること (CC BY 4.0)。",
        "",
        "## 置いてあるファイル",
        "",
        "| ファイル | 年 | 解像度 | 大きさ (bytes) | 幅 x 高さ | nodata を除いた合計 |",
        "|---|---|---|---|---|---|",
    ]
    for rel, r in files.items():
        lines.append(
            f"| [{Path(rel).name}]({rel}) | {r['year']} | {r['resolution']} | {fmt_int(r['cog_bytes'])} "
            f"| {r['width']} x {r['height']} | {r['sum']:,.1f} |"
        )
    lines += [
        "",
        "## 元データ",
        "",
        "元の大きさは HTTP の Content-Length、STAC の size の両方と一致することを確かめた。sha256 は元のファイルと COG の両方を載せる。data.worldpop.org の HTTPS は遅く Range にも応えないため、多くは同じファイルを ftp.worldpop.org から分割して取得し、先頭 256 KiB が HTTPS のものと一致することを確かめている。どちらから取ったかは「取得経路」の列にある。",
        "",
        "| ファイル | 元の URL | 取得経路 | 取得日時 (UTC) | 元の大きさ (bytes) | 元の sha256 | COG の sha256 | STAC の item id | DOI |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for rel, r in files.items():
        lines.append(
            f"| {rel} | {r['source_url']} | {'FTP' if r.get('fetched_via', '').startswith('ftp:') else 'HTTPS'} | {r['fetched_at']} | {fmt_int(r['source_bytes'])} "
            f"| {r['source_sha256']} | {r['cog_sha256']} | {r['stac_id']} "
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
        "coordinate_reference_system:citation property of each STAC item):",
        "",
    ]
    for _doi, e in sorted(by_doi.items()):
        cit = " ".join(e["citation"].split())
        lines.append(f"  {cit}")
        lines.append("")
        lines.append("    Files under this citation:")
        lines += [f"      {f}" for f in e["files"]]
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
        "    source URLs, dates, sizes and sha256 sums.",
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


def process(item: dict, args: argparse.Namespace, manifest: dict) -> str:
    p = item["properties"]
    href = item["assets"]["data"]["href"]
    rel = relpath(href)
    h = head(href)
    if h.get("status") != "200" or "content-length" not in h:
        raise RuntimeError(f"{href}: HEAD returned {h}")
    source_bytes = int(h["content-length"])
    lo, hi = stac_size_bytes(p["size"])
    if not lo <= source_bytes <= hi:
        raise RuntimeError(f"{item['id']}: Content-Length {source_bytes} vs STAC size {p['size']}")
    with _lock:
        record = manifest["files"].get(rel)
    if up_to_date(args.dest, rel, record, source_bytes):
        log(f"skip {rel} (already placed, source {fmt_int(source_bytes)} bytes)")
        return "skipped"
    if source_bytes > MAX_BYTES:
        raise RuntimeError(f"{rel}: source is {source_bytes} bytes, above {MAX_BYTES}; stopping")
    if args.dry_run:
        log(f"would fetch {rel} ({fmt_int(source_bytes)} bytes)")
        return "dry-run"

    work = Path(tempfile.mkdtemp(prefix=item["id"] + ".", dir=args.scratch))
    try:
        src = work / Path(rel).name
        log(f"fetch {href} ({fmt_int(source_bytes)} bytes)")
        fetched_at = now_utc()
        if args.via == "ftp":
            took = download_ftp(href, src, source_bytes, args.attempts, args.connections)
            # The FTP copy must be the file that the HTTPS URL serves.
            prefix = https_prefix(href, 256 * 1024)
            with src.open("rb") as f:
                if f.read(len(prefix)) != prefix:
                    raise RuntimeError(f"{rel}: FTP copy differs from HTTPS in the first bytes")
        else:
            took = download(href, src, source_bytes, args.attempts)
        log(f"  fetched {src.name} in {took:.0f} s ({source_bytes / took / 1e6:.2f} MB/s)")
        src_sha = sha256(src)

        cog = work / (src.stem + ".cog.tif")
        t0 = time.monotonic()
        subprocess.run(
            [str(args.gdal_bin / "gdal_translate"), "-q", *COG_OPTIONS, str(src), str(cog)],
            check=True, timeout=3600,
        )  # fmt: skip
        log(f"  converted in {time.monotonic() - t0:.0f} s: {fmt_int(cog.stat().st_size)} bytes")
        cog_bytes = cog.stat().st_size
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
            f"  verified in {time.monotonic() - t0:.0f} s: shape, CRS, geotransform, nodata, "
            f"type and all pixels equal; sum {bands[0]['sum_src']:,.1f} "
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

        record = {
            "stac_id": item["id"],
            "collection": item.get("collection"),
            "project": p["project"],
            "year": p["year"],
            "resolution": p["resolution"],
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
            "fetched_via": ftp_url(href) if args.via == "ftp" else href,
            "source_bytes": source_bytes,
            "stac_size": p["size"],
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
            "gdal_translate_options": COG_OPTIONS,
        }
        with _lock:
            manifest["files"][rel] = record
            save_manifest(args.dest, manifest)
        log(f"  placed {final}")
        return "placed"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--country", default="JPN", help="STAC collection (ISO alpha-3), default JPN")
    ap.add_argument("--year", type=int, nargs="+", required=True, help="data years, e.g. 2020 2025")
    ap.add_argument(
        "--project", default="Population", help="properties.project, default Population"
    )
    ap.add_argument("--resolution", nargs="+", default=["100m", "1km"], help="default 100m 1km")
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--gdal-bin", type=Path, default=GDAL_BIN)
    ap.add_argument("--gdal-python", type=Path, default=GDAL_PYTHON)
    ap.add_argument("--attempts", type=int, default=3, help="download attempts per file")
    ap.add_argument(
        "--via",
        choices=["ftp", "https"],
        default="ftp",
        help="ftp: aria2c split over ftp.worldpop.org (default); https: curl, one stream",
    )
    ap.add_argument("--connections", type=int, default=6, help="aria2c connections per file (ftp)")
    ap.add_argument("--jobs", type=int, default=2, help="files fetched at the same time")
    ap.add_argument("--dry-run", action="store_true", help="list what would be fetched")
    args = ap.parse_args()

    log(f"STAC search {args.country}")
    items = select(stac_items(args.country), args.project, args.year, args.resolution)
    log(f"{len(items)} items: {', '.join(f['id'] for f in items)}")
    args.dest.mkdir(parents=True, exist_ok=True)
    args.scratch.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(args.dest)

    failures = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {pool.submit(process, f, args, manifest): f["id"] for f in items}
        for fut, item_id in futures.items():
            try:
                fut.result()
            except Exception as e:  # report every item, then fail
                failures.append(item_id)
                log(f"ERROR {item_id}: {e}")

    if not args.dry_run and manifest["files"]:
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
