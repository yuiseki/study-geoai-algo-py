import numpy as np
import pytest

from study_geoai import aoi, graph, osm
from study_geoai.db import connect


def test_walkable():
    assert osm.walkable("footway", None, None)
    assert osm.walkable("residential", None, None)
    assert not osm.walkable("motorway", None, None)
    assert not osm.walkable("construction", None, None)
    assert not osm.walkable("footway", "private", None)
    assert osm.walkable("service", "private", "yes")  # foot=yes overrides access
    assert not osm.walkable("primary", None, "no")


@pytest.mark.network
def test_taito_walk_edges():
    con = connect()
    area = aoi.load("taito", con)
    edges = osm.walk_edges(con, area)
    assert len(edges) > 50_000
    lengths = edges[:, 4]
    assert (lengths > 0).all() and lengths.max() < 2_000
    # each edge joins two consecutive vertices, so its length is the straight gap
    gap = np.hypot(edges[:, 2] - edges[:, 0], edges[:, 3] - edges[:, 1])
    assert np.allclose(gap, lengths)
    # the ward is about 4 km across and the buffer adds about 1 km on each side;
    # ways crossing the buffered bbox are kept whole, so a few reach further
    span = edges[:, [0, 2]].max() - edges[:, [0, 2]].min()
    assert 5_000 < span < 12_000
    g = graph.build(edges)
    sizes = graph.component_sizes(g)
    assert sizes[0] / sizes.sum() > 0.9
