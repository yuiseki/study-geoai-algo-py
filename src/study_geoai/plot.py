"""Choropleth maps with matplotlib only, from DuckDB geometries."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PatchCollection  # noqa: E402
from matplotlib.colors import TwoSlopeNorm  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402


def _patches(geojson: str) -> list[Polygon]:
    g = json.loads(geojson)
    polygons = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return [Polygon(poly[0], closed=True) for poly in polygons]


def choropleth(
    rows: list[tuple[str, float]],
    path: Path,
    title: str,
    label: str,
    diverging: bool = False,
    outline: str | None = None,
) -> Path:
    """rows are (GeoJSON geometry, value). diverging centres the colours on 0."""
    patches, values = [], []
    for geojson, value in rows:
        for p in _patches(geojson):
            patches.append(p)
            values.append(value)
    fig, ax = plt.subplots(figsize=(8, 7))
    coll = PatchCollection(patches, edgecolor="white", linewidth=0.3)
    coll.set_array(values)
    if diverging:
        span = max(abs(min(values)), abs(max(values))) or 1
        coll.set_cmap("RdBu_r")
        coll.set_norm(TwoSlopeNorm(vcenter=0, vmin=-span, vmax=span))
    else:
        coll.set_cmap("viridis")
    ax.add_collection(coll)
    if outline:
        for p in _patches(outline):
            p.set_fill(False)
            p.set_edgecolor("black")
            p.set_linewidth(0.8)
            ax.add_patch(p)
    ax.autoscale_view()
    ax.set_aspect(1 / 0.81)  # about 1 / cos(36 deg), so Tokyo is not stretched
    ax.set_axis_off()
    ax.set_title(title)
    fig.colorbar(coll, ax=ax, label=label, shrink=0.7)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path
