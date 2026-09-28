"""WorldPop population grids for a study area, read as COG windows at runtime.

data.worldpop.org ignores Range requests, so the rasters are mirrored as COGs
on z.yuiseki.net (scripts/mirror_worldpop.py; CC BY 4.0, credits in the
mirror's LICENSE). Only the window over the area's bounding box is read;
pixels whose centre lies in the area are kept, one row per pixel. So far the
mirror holds Japan's total population for 2020 and 2025 at 100 m and 1 km.
"""

import duckdb
import numpy as np
import rasterio
from rasterio.windows import from_bounds

from study_geoai.aoi import Area, cache_path, writing

MIRROR = "https://z.yuiseki.net/static/worldpop/GIS/Population/Global_2015_2030/R2025A"
GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
    "GDAL_HTTP_TIMEOUT": "30",
    # Cloudflare sometimes stalls the first range request of a file.
    "GDAL_HTTP_MAX_RETRY": "3",
    "GDAL_HTTP_RETRY_DELAY": "1",
}


def url(year: int, resolution: str = "100m", country: str = "JPN") -> str:
    c = country.lower()
    if resolution == "100m":
        return f"{MIRROR}/{year}/{country}/v1/100m/constrained/{c}_pop_{year}_CN_100m_R2025A_v1.tif"
    if resolution == "1km":
        return (
            f"{MIRROR}/{year}/{country}/v1/1km_ua/constrained/"
            f"{c}_pop_{year}_CN_1km_R2025A_UA_v1.tif"
        )
    raise ValueError(f"resolution must be 100m or 1km, not {resolution}")


def grid(
    con: duckdb.DuckDBPyConnection, area: Area, year: int, resolution: str = "100m"
) -> duckdb.DuckDBPyRelation:
    """One row per pixel centred in the area: lon, lat (centre), population, geometry (cell)."""
    path = cache_path("worldpop", f"R2025A-{year}", f"{resolution}-{area.name}")
    if not path.exists():
        with rasterio.Env(**GDAL_ENV), rasterio.open(url(year, resolution)) as src:
            window = (
                from_bounds(*area.bbox, transform=src.transform).round_offsets().round_lengths()
            )
            values = src.read(1, window=window)
            transform = src.window_transform(window)
            nodata = src.nodata
        rows, cols = np.nonzero(values != nodata)
        # Pixel corners in lon/lat: x = c + col * a, y = f + row * e (e is negative).
        west = transform.c + cols * transform.a
        north = transform.f + rows * transform.e
        con.execute("create or replace temp table _pixels (west double, north double, pop double)")
        con.executemany("insert into _pixels values (?, ?, ?)", list(zip(
            west.tolist(), north.tolist(), values[rows, cols].astype(float).tolist(), strict=True
        )))  # fmt: skip
        dx, dy = transform.a, transform.e
        with writing(path) as tmp:
            con.execute(
                f"""
                copy (
                    select west + {dx / 2} as lon, north + {dy / 2} as lat, pop as population,
                           st_makeenvelope(west, north + {dy}, west + {dx}, north) as geometry
                    from _pixels
                    where st_intersects(st_point(west + {dx / 2}, north + {dy / 2}),
                                        st_geomfromtext(?))
                ) to '{tmp}' (format parquet)
                """,
                [area.wkt],
            )
        con.execute("drop table _pixels")
    return con.read_parquet(str(path))
