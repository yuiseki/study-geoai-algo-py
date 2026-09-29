"""AgERA5 monthly grids from FAO FERSPAS, read by range requests.

FERSPAS publishes every month of AgERA5 (1979 on, ~10 km, one global grid of
3600 x 1800 cells of 0.1 degree, EPSG:4326) as one Cloud Optimized GeoTIFF per
variable and month, in 256 x 256 blocks. The file list comes from the
GeoParquet index at stac.yuiseki.net/fao-ferspas/; each file is on a public
Google Cloud Storage bucket, read anonymously through storage.googleapis.com
(the storage.cloud.google.com href in the index redirects to a login page).

Only the window asked for is read: Japan is a few blocks of each file, about
four seconds per month cold. A stack of months is read in parallel and kept as
one compressed array in the cache directory, so an experiment reads the files
once. Values are as published: rain and reference evapotranspiration in mm per
month, temperatures in kelvin; nodata (the sea) becomes NaN.

Licences, from the index: precipitation and reference evapotranspiration are
CC BY-SA 4.0, the two temperatures CC BY 4.0 (Copernicus Climate Change
Service, AgERA5, via FAO).
"""

from concurrent.futures import ThreadPoolExecutor

import duckdb
import numpy as np
import rasterio
from rasterio.windows import Window

from study_geoai.aoi import CACHE_DIR, JP_ADMIN_REVISION, cache_path, writing
from study_geoai.db import connect

INDEX = "https://stac.yuiseki.net/fao-ferspas/items.parquet"
JP_ADMIN_PREFECTURES = (
    "https://huggingface.co/datasets/yuiseki/jp-admin-2026-09/resolve/"
    f"{JP_ADMIN_REVISION}/prefectures.parquet"
)
_PREFIX = "fao-gismgr:C3S:raster:mapsets:AGERA5-"
VARIABLES = {
    "rain": "PF-M",  # precipitation flux, mm/month
    "et0": "ET0-M",  # reference evapotranspiration, mm/month
    "tmax": "TMAX-AVG-M",  # average daily maximum air temperature, K
    "tmin": "TMIN-AVG-M",  # average daily minimum air temperature, K
}
CREDIT = (
    "AgERA5 (Copernicus Climate Change Service), via FAO FERSPAS: precipitation and"
    " reference evapotranspiration CC BY-SA 4.0, temperatures CC BY 4.0"
)
RES = 0.1  # degrees
KELVIN = 273.15
WEST, NORTH = -180.0, 90.0
# Japan from Yonaguni to Etorofu; everything else in this box is sea or is
# dropped by the prefecture join.
JAPAN = (122.0, 24.0, 149.0, 46.0)
GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
    "GDAL_HTTP_MULTIPLEX": "YES",
    "GDAL_HTTP_VERSION": "2",
    "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
    "GDAL_HTTP_MAX_RETRY": "4",
    "GDAL_HTTP_RETRY_DELAY": "2",
}
THREADS = 12
# Any month tells land from sea: no cell over Japan is NaN in some months only.
REFERENCE_MONTH = "2020-01-01"


def https(gs_href: str) -> str:
    if not gs_href.startswith("gs://"):
        raise ValueError(f"not a gs:// href: {gs_href}")
    return "https://storage.googleapis.com/" + gs_href.removeprefix("gs://")


def collection(variable: str) -> str:
    return _PREFIX + VARIABLES[variable]


def window(bbox: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    """(row0, col0, rows, cols) of the global grid cells inside bbox."""
    west, south, east, north = bbox
    col0, col1 = round((west - WEST) / RES), round((east - WEST) / RES)
    row0, row1 = round((NORTH - north) / RES), round((NORTH - south) / RES)
    return row0, col0, row1 - row0, col1 - col0


def centres(bbox: tuple[float, float, float, float]) -> tuple[np.ndarray, np.ndarray]:
    """Cell-centre longitudes (west to east) and latitudes (north to south)."""
    row0, col0, rows, cols = window(bbox)
    lon = WEST + (col0 + np.arange(cols) + 0.5) * RES
    lat = NORTH - (row0 + np.arange(rows) + 0.5) * RES
    return lon, lat


def files(variable: str, start: str, end: str) -> list[tuple[np.datetime64, str]]:
    """(month, https url) of every file of one variable from start to end, inclusive."""
    con = duckdb.connect()
    con.execute("load httpfs")
    rows = con.execute(
        f"""select start_datetime::date, data_gs_href from '{INDEX}'
            where collection = ? and start_datetime between ?::date and ?::date
            order by 1""",
        [collection(variable), start, end],
    ).fetchall()
    return [(np.datetime64(d, "D"), https(h)) for d, h in rows]


def _read(url: str, win: tuple[int, int, int, int]) -> np.ndarray:
    row0, col0, rows, cols = win
    with rasterio.Env(**GDAL_ENV), rasterio.open(url) as src:
        a = src.read(1, window=Window(col0, row0, cols, rows), masked=True)
    return a.astype("float32").filled(np.nan)


def stack(
    variable: str, bbox: tuple[float, float, float, float], start: str, end: str
) -> tuple[np.ndarray, np.ndarray]:
    """(months, values[month, row, col]) for one variable, cached after the first read."""
    tag = "_".join(f"{v:g}" for v in bbox)
    path = CACHE_DIR / f"ferspas-{VARIABLES[variable]}-{tag}-{start}-{end}.npz"
    if path.exists():
        with np.load(path) as z:
            return z["months"], z["values"]
    listed = files(variable, start, end)
    if not listed:
        raise LookupError(f"no {variable} files from {start} to {end}")
    win = window(bbox)
    with ThreadPoolExecutor(THREADS) as pool:
        grids = list(pool.map(lambda f: _read(f[1], win), listed))
    months = np.array([m for m, _ in listed], dtype="datetime64[D]")
    values = np.stack(grids)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".partial.npz")
    np.savez_compressed(tmp, months=months, values=values)
    tmp.rename(path)
    return months, values


def on_cells(
    variable: str, cells, start: str, end: str, bbox: tuple[float, float, float, float] = JAPAN
) -> tuple[np.ndarray, np.ndarray]:
    """(months, values[month, cell]) at the rows and cols of cells; temperatures in Celsius."""
    months, grid = stack(variable, bbox, start, end)
    values = grid[:, cells["row"].to_numpy(), cells["col"].to_numpy()]
    if variable in ("tmax", "tmin"):
        values = values - KELVIN
    return months, values


def normals(values: np.ndarray, months: np.ndarray) -> np.ndarray:
    """Mean of each calendar month: values[month, ...] -> [12, ...]."""
    cal = months.astype("datetime64[M]").astype(int) % 12
    return np.stack([np.nanmean(values[cal == m], axis=0) for m in range(12)])


def _prefecture_cells(bbox, con):
    """Grid cells whose centre lies in a prefecture, cached: row, col, lon, lat, pref_code, pref."""
    tag = "_".join(f"{v:g}" for v in bbox)
    path = cache_path("ferspas-cells", JP_ADMIN_REVISION, tag)
    if not path.exists():
        lon, lat = centres(bbox)
        rr, cc = np.meshgrid(np.arange(len(lat)), np.arange(len(lon)), indexing="ij")
        con.register("cells_in", {
            "row": rr.ravel(), "col": cc.ravel(),
            "lon": np.broadcast_to(lon, rr.shape).ravel(),
            "lat": np.broadcast_to(lat[:, None], rr.shape).ravel(),
        })  # fmt: skip
        with writing(path) as tmp:
            con.sql(f"""
                copy (
                    with p as (
                        select pref_code, pref, st_geomfromwkb(geometry) as g
                        from read_parquet('{JP_ADMIN_PREFECTURES}')
                    )
                    select c.row, c.col, c.lon, c.lat, p.pref_code, p.pref
                    from cells_in c join p on st_contains(p.g, st_point(c.lon, c.lat))
                    order by c.row, c.col
                ) to '{tmp}' (format parquet)
            """)
    return con.sql(f"select * from '{path}' order by row, col").df()


def japan_cells(
    bbox: tuple[float, float, float, float] = JAPAN, con: duckdb.DuckDBPyConnection | None = None
):
    """Land cells of the grid inside a Japanese prefecture: row, col, lon, lat, pref_code, pref.

    A cell belongs to the prefecture its centre falls in; cells whose centre is
    at sea (coastal cells, small islands) are dropped, and so are the few whose
    centre is on land but that AgERA5 has as sea (NaN in every month; 5 of
    3,850 over Japan, checked on all four variables from 1979 to 2025).
    """
    cells = _prefecture_cells(bbox, con or connect())
    _, grid = stack("tmax", bbox, REFERENCE_MONTH, REFERENCE_MONTH)
    land = np.isfinite(grid[0, cells["row"].to_numpy(), cells["col"].to_numpy()])
    return cells[land].reset_index(drop=True)
