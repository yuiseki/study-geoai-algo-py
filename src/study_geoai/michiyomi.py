"""michiyomi street scenes (Mapillary imagery structured by a VLM), read at runtime.

The bulk dataset on Hugging Face has one parquet file per municipality, so only
the files of the wards in the area are read, and only the listed columns. The
VLM's structured reading is one JSON string per scene (analysis); a few fields
are pulled out of it. They are model estimates, not ground truth.
"""

from pathlib import Path

import duckdb

from study_geoai.aoi import Area, cache_path, wards, writing

MICHIYOMI_REVISION = "e4966cdceff6b0a2e3cb37e6a7efcc2b07eeba44"
BASE = (
    "https://huggingface.co/datasets/finalvent/michiyomi-tokyo-streetscape/resolve/"
    f"{MICHIYOMI_REVISION}/data/scenes"
)

WARD_FILES = {
    "13101": "chiyoda", "13102": "chuo", "13103": "minato", "13104": "shinjuku",
    "13105": "bunkyo", "13106": "taito", "13107": "sumida", "13108": "koto",
    "13109": "shinagawa", "13110": "meguro", "13111": "ota", "13112": "setagaya",
    "13113": "shibuya", "13114": "nakano", "13115": "suginami", "13116": "toshima",
    "13117": "kita", "13118": "arakawa", "13119": "itabashi", "13120": "nerima",
    "13121": "adachi", "13122": "katsushika", "13123": "edogawa",
}  # fmt: skip

COLUMNS = [
    "id", "ward", "lon", "lat", "capture_year", "cell_250m", "sequence_id",
    "quarantined", "quality_score", "is_pano", "green_ratio", "colorfulness",
]  # fmt: skip

# name: JSON path inside analysis
FIELDS = {
    "roadway_width_m": "$.geometry.roadway_width_m.value",
    "roadway_width_confidence": "$.geometry.roadway_width_m.confidence",
    "sidewalk_left": "$.geometry.sidewalk.left.presence",
    "sidewalk_left_width_m": "$.geometry.sidewalk.left.width_m",
    "sidewalk_right": "$.geometry.sidewalk.right.presence",
    "sidewalk_right_width_m": "$.geometry.sidewalk.right.width_m",
    "sight_distance": "$.geometry.intersection.sight_distance",
    "surface": "$.pavement.surface",
    "undergrounded": "$.infrastructure.utilities.undergrounded",
    "poles_visible": "$.infrastructure.utilities.poles_visible",
    "wire_density": "$.infrastructure.utilities.wire_density",
    "lights_road": "$.infrastructure.lighting.lights_road",
}
NUMERIC = {"roadway_width_m", "sidewalk_left_width_m", "sidewalk_right_width_m",
           "poles_visible", "lights_road"}  # fmt: skip


def scenes(con: duckdb.DuckDBPyConnection, area: Area) -> duckdb.DuckDBPyRelation:
    """One row per scene in the area: COLUMNS, the FIELDS pulled from analysis, and geometry.

    Pulling fields out of the JSON is memory hungry, so each ward is read and
    cached on its own; the area is the union of its wards' files.
    """
    paths = [_ward_scenes(con, ward) for ward in wards(area, con)]
    return con.read_parquet([str(p) for p in paths])


def _ward_scenes(con: duckdb.DuckDBPyConnection, ward: Area) -> Path:
    (code,) = ward.codes
    path = cache_path("michiyomi", MICHIYOMI_REVISION, f"scenes-{code}")
    if not path.exists():
        fields = ", ".join(
            f"try_cast(json_extract_string(analysis, '{p}') as double) as {n}"
            if n in NUMERIC
            else f"json_extract_string(analysis, '{p}') as {n}"
            for n, p in FIELDS.items()
        )
        with writing(path) as tmp:
            con.execute(
                f"""
                copy (
                    select {", ".join(COLUMNS)}, {fields}, st_point(lon, lat) as geometry
                    from read_parquet('{BASE}/{WARD_FILES[code]}.parquet')
                    where st_intersects(st_point(lon, lat), st_geomfromtext(?))
                ) to '{tmp}' (format parquet)
                """,
                [ward.wkt],
            )
    return path
