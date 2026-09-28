"""The Japanese standard grid square, 3rd mesh (基準地域メッシュ, about 1 km).

Latitude is cut every 30 seconds and longitude every 45 seconds. The 8-digit
code is pq uv r s w t: the 1st mesh from lat x 1.5 and lon - 100, then 8 x 8
2nd meshes, then 10 x 10 3rd meshes.
"""

import math


def code(lon: float, lat: float) -> int:
    y, x = lat * 1.5, lon - 100
    p, u = math.floor(y), math.floor(x)
    q, v = math.floor((y - p) * 8), math.floor((x - u) * 8)
    r, w = math.floor(((y - p) * 8 - q) * 10), math.floor(((x - u) * 8 - v) * 10)
    return p * 1_000_000 + u * 10_000 + q * 1_000 + v * 100 + r * 10 + w


def bounds(c: int) -> tuple[float, float, float, float]:
    """west, south, east, north of a 3rd mesh."""
    p, u = c // 1_000_000, c // 10_000 % 100
    q, v, r, w = c // 1_000 % 10, c // 100 % 10, c // 10 % 10, c % 10
    south = (p + q / 8 + r / 80) / 1.5
    west = 100 + u + v / 8 + w / 80
    return west, south, west + 1 / 80, south + 1 / 120


def sql(lon: str, lat: str) -> str:
    """A DuckDB expression for the 3rd mesh code of the columns lon and lat."""
    y, x = f"({lat} * 1.5)", f"({lon} - 100)"
    p, u = f"floor({y})", f"floor({x})"
    q, v = f"floor(({y} - {p}) * 8)", f"floor(({x} - {u}) * 8)"
    r, w = f"floor((({y} - {p}) * 8 - {q}) * 10)", f"floor((({x} - {u}) * 8 - {v}) * 10)"
    return f"cast({p} * 1000000 + {u} * 10000 + {q} * 1000 + {v} * 100 + {r} * 10 + {w} as bigint)"
