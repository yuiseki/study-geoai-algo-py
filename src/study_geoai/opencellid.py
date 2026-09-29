"""OpenCelliD cell towers for a study area, from the PMTiles on Source Cooperative.

smartmaps/opencellid holds OpenCelliD's full export of 2024-06-14 as one
PMTiles (4,835,586 points, CC BY-SA 4.0, credit OpenCelliD). It was made with
tippecanoe without dropping points, so zoom 14 has every cell. The tiles are
read by range requests with GDAL's PMTiles driver (the ogr2ogr of a separate
GDAL install, see study_geoai.gdal; the GDAL inside rasterio does not expose
vector drivers to Python), clipped to the
area and cached. Positions are OpenCelliD's estimates, not surveyed sites.
"""

import subprocess

import duckdb

from study_geoai import gdal
from study_geoai.aoi import CACHE_DIR, Area, cache_path, writing

PMTILES = "https://data.source.coop/smartmaps/opencellid/cellid.pmtiles"
VERSION = "2024-06-14"


def cells(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    """radio, mcc, net, area_code, cell, range_m, samples, created, updated, lon, lat, geometry."""
    path = cache_path("opencellid", VERSION, f"cells-{area.name}")
    if not path.exists():
        raw = CACHE_DIR / f"opencellid-{VERSION}-{area.name}.geojsonl"
        west, south, east, north = area.bbox
        subprocess.run(
            [gdal.tool("ogr2ogr"), "-f", "GeoJSONSeq", "-overwrite", str(raw), f"/vsicurl/{PMTILES}",
             "-oo", "ZOOM_LEVEL=14", "-spat", str(west), str(south), str(east), str(north),
             "-spat_srs", "EPSG:4326", "-t_srs", "EPSG:4326"],
            check=True, timeout=1800,
            env=gdal.child_env(),
        )  # fmt: skip
        with writing(path) as tmp:
            con.execute(
                f"""
                copy (
                    select radio, mcc, net, area as area_code, cell, range as range_m, samples,
                           created, updated,
                           st_x(st_centroid(geom)) as lon, st_y(st_centroid(geom)) as lat,
                           -- A plain point: st_read tags it EPSG:4326, which DuckDB refuses
                           -- to compare with Ookla's OGC:CRS84 although both are lon/lat.
                           st_point(st_x(st_centroid(geom)), st_y(st_centroid(geom))) as geometry
                    from (
                        select *, row_number() over (partition by radio, mcc, net, area, cell) as k
                        from st_read('{raw}')
                    )
                    where k = 1 and st_intersects(st_centroid(geom), st_geomfromtext(?))
                ) to '{tmp}' (format parquet)
                """,
                [area.wkt],
            )
            # Each feature is a one-point MultiPoint; ST_PointN is for lines and gave NULL,
            # which silently emptied the table once. An empty result is an error here.
            n = con.execute(f"select count(*) from read_parquet('{tmp}')").fetchone()[0]
            if n == 0:
                raise ValueError(f"no OpenCelliD cells in {area.name}; see {raw}")
        raw.unlink()
    return con.read_parquet(str(path))
