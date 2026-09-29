"""WorldPop grids for a study area, read as COG windows at runtime.

data.worldpop.org ignores Range requests, so the rasters are mirrored as COGs
on z.yuiseki.net (scripts/mirror_worldpop.py; CC BY 4.0, credits in the
mirror's LICENSE). The mirror's manifest.json lists what is there; files are
looked up in it rather than by guessing paths. Only the window over the
area's bounding box is read, and pixels whose centre lies in the area are
kept, one row per pixel, with the centre and the cell in lon/lat.

- grid: total population (Population), 100 m or 1 km.
- agesex: population by sex and age group (Age and Sex Structures), long form.
- urbanisation: Degree of Urbanisation grids (level 1 or 2), 1 km in
  Mollweide (ESRI:54009). Values are kept as published; their class codes
  are not decoded here.
"""

import json
import time
import urllib.request

import duckdb
import numpy as np
import rasterio
from rasterio.warp import transform as warp_points
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

from study_geoai.aoi import Area, cache_path, writing

BASE = "https://z.yuiseki.net/static/worldpop"
GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
    "GDAL_HTTP_TIMEOUT": "30",
    # Cloudflare sometimes stalls the first range request of a file.
    "GDAL_HTTP_MAX_RETRY": "3",
    "GDAL_HTTP_RETRY_DELAY": "1",
}
POPULATION = "Population"
AGESEX = "Age and Sex Structures"
URBANISATION = "Degree of Urbanisation"

_manifest: dict | None = None


def manifest() -> dict:
    """The mirror's manifest.json, fetched once per process past any stale CDN copy."""
    global _manifest
    if _manifest is None:
        req = urllib.request.Request(
            f"{BASE}/manifest.json?cb={int(time.time())}",
            headers={"User-Agent": "study-geoai-algo-py"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            _manifest = json.load(r)
    return _manifest


def records(project: str, year: int, resolution: str | None = None) -> list[dict]:
    found = [
        r
        for r in manifest()["files"].values()
        if r["project"] == project and r["year"] == year and r.get("resolution") == resolution
    ]
    if not found:
        raise KeyError(f"{project} {year} {resolution} is not in the mirror yet")
    return found


def url(year: int, resolution: str = "100m") -> str:
    (record,) = records(POPULATION, year, resolution)
    return record["public_url"]


def _pixels(url_: str, area: Area) -> tuple[np.ndarray, ...]:
    """lon, lat of pixel centres, the four corners in lon/lat, and values, for valid pixels."""
    with rasterio.Env(**GDAL_ENV), rasterio.open(url_) as src:
        crs = src.crs
        bounds = (
            area.bbox if crs.to_epsg() == 4326 else transform_bounds("EPSG:4326", crs, *area.bbox)
        )
        window = from_bounds(*bounds, transform=src.transform).round_offsets().round_lengths()
        values = src.read(1, window=window)
        t = src.window_transform(window)
        nodata = src.nodata
    rows, cols = np.nonzero(values != nodata)
    x0, y0 = t.c + cols * t.a, t.f + rows * t.e
    corners = [(x0, y0), (x0 + t.a, y0), (x0 + t.a, y0 + t.e), (x0, y0 + t.e)]
    centre = (x0 + t.a / 2, y0 + t.e / 2)
    if crs.to_epsg() != 4326:
        centre = warp_points(crs, "EPSG:4326", *centre)
        corners = [warp_points(crs, "EPSG:4326", xs, ys) for xs, ys in corners]
    return np.asarray(centre[0]), np.asarray(centre[1]), corners, values[rows, cols]


def _write(con, area: Area, path, columns: dict[str, list], lon, lat, corners) -> None:
    """Keep pixels centred in the area and write them with their cell polygon."""
    names = list(columns)
    rings = [
        "POLYGON(("
        + ", ".join(f"{corners[k][0][i]} {corners[k][1][i]}" for k in (0, 1, 2, 3, 0))
        + "))"
        for i in range(len(lon))
    ]
    con.execute(
        "create or replace temp table _px ("
        + ", ".join(
            f"{n} {'varchar' if isinstance(columns[n][0], str) else 'double'}" for n in names
        )
        + ", lon double, lat double, cell varchar)"
    )
    con.executemany(
        f"insert into _px values ({', '.join('?' for _ in names)}, ?, ?, ?)",
        list(zip(*(columns[n] for n in names), lon.tolist(), lat.tolist(), rings, strict=True)),
    )
    with writing(path) as tmp:
        con.execute(
            f"""
            copy (
                select {", ".join(names)}, lon, lat, st_geomfromtext(cell) as geometry
                from _px
                where st_intersects(st_point(lon, lat), st_geomfromtext(?))
            ) to '{tmp}' (format parquet)
            """,
            [area.wkt],
        )
    con.execute("drop table _px")


def grid(
    con: duckdb.DuckDBPyConnection, area: Area, year: int, resolution: str = "100m"
) -> duckdb.DuckDBPyRelation:
    """Total population: population, lon, lat (centre), geometry (cell)."""
    path = cache_path("worldpop", f"R2025A-{year}", f"{resolution}-{area.name}")
    if not path.exists():
        lon, lat, corners, values = _pixels(url(year, resolution), area)
        _write(con, area, path, {"population": values.astype(float).tolist()}, lon, lat, corners)
    return con.read_parquet(str(path))


def agesex(
    con: duckdb.DuckDBPyConnection, area: Area, year: int, resolution: str = "1km"
) -> duckdb.DuckDBPyRelation:
    """Population by sex (f, m, t) and age group: sex, age_group, age_label, population, lon, lat, geometry."""
    path = cache_path("worldpop", f"R2025A-{year}", f"agesex-{resolution}-{area.name}")
    if not path.exists():
        cols = {"sex": [], "age_group": [], "age_label": [], "population": []}
        lons, lats, corners_all = [], [], [[[], []] for _ in range(4)]
        for r in records(AGESEX, year, resolution):
            props = r["asset_properties"]
            lon, lat, corners, values = _pixels(r["public_url"], area)
            n = len(values)
            cols["sex"] += [props["agesex:sex"]] * n
            cols["age_group"] += [props["agesex:age_group"]] * n
            cols["age_label"] += [props["agesex:age_label"]] * n
            cols["population"] += values.astype(float).tolist()
            lons.append(lon)
            lats.append(lat)
            for k in range(4):
                corners_all[k][0].append(np.asarray(corners[k][0]))
                corners_all[k][1].append(np.asarray(corners[k][1]))
        corners = [(np.concatenate(xs), np.concatenate(ys)) for xs, ys in corners_all]
        _write(con, area, path, cols, np.concatenate(lons), np.concatenate(lats), corners)
    return con.read_parquet(str(path))


def urbanisation(
    con: duckdb.DuckDBPyConnection, area: Area, year: int, level: int = 1
) -> duckdb.DuckDBPyRelation:
    """Degree of Urbanisation grid level 1 or 2: value (as published), lon, lat, geometry."""
    path = cache_path("worldpop", f"R2025A-{year}", f"urbanisation-l{level}-{area.name}")
    if not path.exists():
        (record,) = [r for r in records(URBANISATION, year) if r["asset"] == f"grid_l{level}"]
        lon, lat, corners, values = _pixels(record["public_url"], area)
        _write(con, area, path, {"value": values.astype(float).tolist()}, lon, lat, corners)
    return con.read_parquet(str(path))
