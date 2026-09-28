"""The two learning problems the steps share, as arrays.

density: log(1 + population density) of census small areas, from building
coverage and POI density (step 1A). Small areas without residents are left
out: log(1 + 0) = 0 made residuals of -10 and more.

undergrounded: whether a michiyomi street scene has its wires underground
(無電柱化済 = 1, 架空線あり = 0), from the road and the picture (step 1B).
leaky=True adds visible poles and wire density, which restate the answer.

groups carries columns for grouped or spatial splits in step 4.
"""

from dataclasses import dataclass

import numpy as np

from study_geoai import aoi, features, michiyomi


@dataclass
class Task:
    name: str
    features: list[str]
    X: np.ndarray
    y: np.ndarray
    groups: dict[str, np.ndarray]


DENSITY = ["coverage", "log_place_density"]
STREET = ["roadway_width_m", "sidewalk_left", "sidewalk_right", "green_ratio", "colorfulness",
          "lights_road"]  # fmt: skip
LEAKY = ["poles_visible", "wire_high"]


def density(con, area_name: str) -> Task:
    area = aoi.load(area_name, con)
    rel = features.small_areas(con, area)
    rows = rel.query(
        "t",
        """
        select key11, code5, coverage, ln(1 + place_density), ln(1 + density),
               st_x(st_centroid(geometry)), st_y(st_centroid(geometry))
        from t where population > 0 and area_km2 > 0.001 order by key11
        """,
    ).fetchall()
    X = np.array([r[2:4] for r in rows], dtype=float)
    y = np.array([r[4] for r in rows], dtype=float)
    groups = {
        "key11": np.array([r[0] for r in rows]),
        "code5": np.array([r[1] for r in rows]),
        "lon": np.array([r[5] for r in rows], dtype=float),
        "lat": np.array([r[6] for r in rows], dtype=float),
    }
    return Task(f"density-{area_name}", DENSITY, X, y, groups)


def undergrounded(con, area_name: str, leaky: bool = False) -> Task:
    area = aoi.load(area_name, con)
    rel = michiyomi.scenes(con, area)
    rows = rel.query(
        "s",
        """
        select (undergrounded = '無電柱化済')::int, roadway_width_m,
               (sidewalk_left = 'あり')::int, (sidewalk_right = 'あり')::int,
               green_ratio, colorfulness, lights_road, poles_visible,
               (wire_density = '高')::int,
               cell_250m, sequence_id, capture_year, lon, lat, ward
        from s
        where undergrounded in ('無電柱化済', '架空線あり')
          and roadway_width_m is not null and lights_road is not null
          and poles_visible is not null and wire_density is not null
          and green_ratio is not null and colorfulness is not null and quarantined = 0
        order by id
        """,
    ).fetchall()
    feats = STREET + (LEAKY if leaky else [])
    cols = 6 + (2 if leaky else 0)
    X = np.array([r[1 : 1 + cols] for r in rows], dtype=float)
    y = np.array([r[0] for r in rows], dtype=int)
    groups = {
        "cell_250m": np.array([r[9] for r in rows]),
        "sequence_id": np.array([r[10] for r in rows]),
        "capture_year": np.array([r[11] for r in rows]),
        "lon": np.array([r[12] for r in rows], dtype=float),
        "lat": np.array([r[13] for r in rows], dtype=float),
        "ward": np.array([r[14] for r in rows]),
    }
    return Task(f"undergrounded-{area_name}", feats, X, y, groups)
