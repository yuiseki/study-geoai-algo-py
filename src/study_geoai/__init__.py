"""Shared helpers for the study steps under src/.

The shell on this host exports GDAL_DRIVER_PATH, GDAL_DATA and PROJ_DATA for
anaconda's GDAL 3.9 and PROJ. rasterio's wheel bundles its own GDAL and PROJ,
and with those variables set it loads anaconda's GDAL plugins (GeoTIFF nodata
then reads as None, so -99999 is counted as population) and anaconda's
proj.db (EPSG codes fail). They are dropped here, before anything imports
rasterio, so the bundled libraries use their own data.
"""

import os

for _name in ("GDAL_DRIVER_PATH", "GDAL_DATA", "PROJ_DATA", "PROJ_LIB"):
    os.environ.pop(_name, None)
