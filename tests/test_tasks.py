"""The two learning problems shared by the steps."""

import numpy as np
import pytest

from study_geoai import tasks
from study_geoai.db import connect


@pytest.mark.network
def test_density_problem():
    con = connect()
    t = tasks.density(con, "taito")
    assert t.X.shape == (108, len(t.features))
    assert not np.isnan(t.X).any()
    assert len(t.y) == len(t.groups["key11"]) == 108
    # 23 wards: the 78 small areas without residents are left out.
    assert len(tasks.density(con, "tokyo23").y) == 3_072


@pytest.mark.network
def test_undergrounded_problem():
    con = connect()
    t = tasks.undergrounded(con, "taito")
    assert t.X.shape == (32_593, len(t.features))
    assert not np.isnan(t.X).any()
    assert set(np.unique(t.y)) == {0, 1}
    assert abs(t.y.mean() - 0.116) < 0.001
    assert "poles_visible" not in t.features  # leaky ones are opt-in
    assert "poles_visible" in tasks.undergrounded(con, "taito", leaky=True).features
