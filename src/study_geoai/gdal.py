"""A GDAL command-line install for the tools that rasterio's wheel lacks.

rasterio bundles its own GDAL but no command-line tools and no vector drivers,
so a few steps run ogr2ogr, gdal_translate and gdalinfo from a separate GDAL
install (conda, a system package, ...). Its prefix is taken from the
STUDY_GEOAI_GDAL_PREFIX environment variable, or else from where ogr2ogr is
found on PATH. Such a GDAL needs its own PROJ and GDAL data, the variables
that importing study_geoai drops for rasterio; child_env gives them to the
child process only.
"""

import os
import shutil
from pathlib import Path

PREFIX_VAR = "STUDY_GEOAI_GDAL_PREFIX"


def prefix() -> Path | None:
    """The GDAL install prefix (the directory holding bin/), or None."""
    if os.environ.get(PREFIX_VAR):
        return Path(os.environ[PREFIX_VAR])
    found = shutil.which("ogr2ogr")
    return Path(found).resolve().parent.parent if found else None


def tool(name: str) -> str:
    """Path of one GDAL command-line tool, such as ogr2ogr."""
    root = prefix()
    if root is None or not (root / "bin" / name).exists():
        raise FileNotFoundError(
            f"GDAL's {name} was not found; install GDAL or set {PREFIX_VAR} to its prefix"
        )
    return str(root / "bin" / name)


def child_env() -> dict[str, str]:
    """Environment for a child process running the GDAL tools of prefix()."""
    root = prefix()
    env = {"PATH": "/usr/bin:/bin", "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR"}
    if root is None:
        return env
    env["PATH"] = f"{root / 'bin'}:{env['PATH']}"
    for var, sub in (("PROJ_DATA", "share/proj"), ("GDAL_DATA", "share/gdal")):
        if (root / sub).is_dir():
            env[var] = str(root / sub)
    return env
