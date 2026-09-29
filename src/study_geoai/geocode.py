"""Geocode ward facilities with nominatim.yuiseki.net, keeping how each was found.

Tried on 2026-09-28: full Japanese addresses with block and building numbers
return nothing; a town (西浅草三丁目) returns its administrative boundary, but
also traffic signals and bus stops named after it at place_rank 30; a facility
name often finds the building, and sometimes a same-named place elsewhere in
Japan (中央図書館 found a bus stop in Yokohama). So:

1. name: search the facility name in three forms; among amenities, buildings
   and the like inside the area whose name contains the facility's, prefer an
   exact name, then the shortest (a main library over its branch).
2. town: search the town taken from the address; accept only an
   administrative boundary inside the area. Coarser, about a town block.
3. otherwise nothing, reported as such.

Answers are cached per query in the OS temp directory.
"""

import hashlib
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request

import duckdb

from study_geoai.aoi import CACHE_DIR, Area

NOMINATIM = "https://nominatim.yuiseki.net/search"
PAUSE = 0.2  # seconds between requests to the server
CACHE = CACHE_DIR / "nominatim"
POINTLIKE = {"highway", "railway", "public_transport", "place"}  # never a facility itself
DIGITS = "〇一二三四五六七八九"


def kanji(n: int) -> str:
    """1 to 99 in kanji numerals, as town names write chome (三丁目, 十二丁目)."""
    tens, ones = divmod(n, 10)
    return ("" if tens == 0 else ("十" if tens == 1 else DIGITS[tens] + "十")) + (
        DIGITS[ones] if ones else ""
    )


def town(address: str) -> tuple[str, str] | None:
    """(ward, town) from an address: 東京都台東区西浅草3-25-16 -> (台東区, 西浅草三丁目)."""
    a = unicodedata.normalize("NFKC", address).replace("ー", "-").replace("－", "-")
    m = re.match(r"^(?:東京都)?\s*(\S+?区)(.*)$", a)
    if not m:
        return None
    ward, rest = m.group(1), m.group(2).strip()
    if written := re.match(r"^(\D+?[一二三四五六七八九十]+丁目)", rest):
        return ward, written.group(1)
    if numbered := re.match(r"^([^\d\s-]+?)(\d+)(?:丁目|-|$)", rest):
        return ward, f"{numbered.group(1)}{kanji(int(numbered.group(2)))}丁目"
    if plain := re.match(r"^([^\d\s-]+)", rest):
        return ward, plain.group(1)
    return None


def core(name: str) -> str:
    """A facility name without the ward and 区立/都立 prefixes, NFKC-normalised."""
    n = unicodedata.normalize("NFKC", name)
    n = re.sub(r"\s+", "", n)  # OSM writes 台東区立 平成小学校 with a space
    n = n[len("東京都立") :] if n.startswith("東京都立") else n.removeprefix("東京都")
    return re.sub(r"^(?:\S{1,4}?区立|区立|都立)", "", n).strip()


def same_name(found: str, wanted: str) -> bool:
    a, b = core(found), core(wanted)
    return bool(a and b) and (b in a or a in b)


def search(query: str) -> list[dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha256(query.encode()).hexdigest()[:32] + ".json")
    if path.exists():
        return json.loads(path.read_text())
    params = {"q": query, "format": "jsonv2", "limit": 10, "countrycodes": "jp"}
    req = urllib.request.Request(
        f"{NOMINATIM}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "study-geoai-algo-py"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        results = json.load(r)
    time.sleep(PAUSE)
    path.write_text(json.dumps(results, ensure_ascii=False))
    return results


def _inside(con: duckdb.DuckDBPyConnection, area: Area, lon: float, lat: float) -> bool:
    return con.execute(
        "select st_contains(st_geomfromtext(?), st_point(?, ?))", [area.wkt, lon, lat]
    ).fetchone()[0]


def locate(
    con: duckdb.DuckDBPyConnection,
    area: Area,
    name: str | None,
    address: str | None,
    ward: str | None = None,
) -> tuple[float | None, float | None, str | None]:
    """lon, lat and how they were found ("name" or "town"), or (None, None, None).

    ward (such as 台東区) is used when the address does not give one; some lists, such
    as polling stations, have no address column at all.
    """
    parts = town(address) if address else None
    ward = parts[0] if parts else (ward or "")
    if name:
        # Nominatim does not narrow "台東区 中央図書館" to the ward (it found a bus stop in
        # Yokohama), but "台東区立中央図書館" and "中央図書館 台東区 東京都" work; the latter
        # also finds 中央図書館浅草橋分室. So try several forms, keep candidates in the area,
        # and prefer an exact name, then the shortest name containing it.
        queries = [f"{name} 東京都"]
        if ward:
            queries = [f"{ward}立{core(name)}", f"{name} {ward} 東京都", f"{ward} {name}"]
        best = None
        for q in dict.fromkeys(q.strip() for q in queries if q.strip()):
            for r in search(q):
                found = r["name"] or r["display_name"].split(",")[0]
                if r["category"] in POINTLIKE or not same_name(found, name):
                    continue
                lon, lat = float(r["lon"]), float(r["lat"])
                if not _inside(con, area, lon, lat):
                    continue
                rank = (core(found) != core(name), len(core(found)))
                if best is None or rank < best[0]:
                    best = (rank, lon, lat)
        if best:
            return best[1], best[2], "name"
    if parts:
        for r in search(f"{parts[1]} {ward}"):
            if r["category"] == "boundary" and r["type"] == "administrative":
                lon, lat = float(r["lon"]), float(r["lat"])
                if _inside(con, area, lon, lat):
                    return lon, lat, "town"
    return None, None, None
