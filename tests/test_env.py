"""Smoke tests: each library imports and solves a tiny problem."""

import numpy as np


def _xy():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(200, 4))
    y = (x[:, 0] + x[:, 1] > 0).astype(int)
    return x, y


def test_sklearn():
    from sklearn.linear_model import LogisticRegression

    x, y = _xy()
    assert LogisticRegression().fit(x, y).score(x, y) > 0.9


def test_xgboost():
    import xgboost as xgb

    x, y = _xy()
    assert xgb.XGBClassifier(n_estimators=20).fit(x, y).score(x, y) > 0.9


def test_lightgbm():
    import lightgbm as lgb

    x, y = _xy()
    model = lgb.LGBMClassifier(n_estimators=20, verbose=-1).fit(x, y)
    assert model.score(x, y) > 0.9


def test_catboost():
    from catboost import CatBoostClassifier

    x, y = _xy()
    model = CatBoostClassifier(iterations=20, verbose=0, allow_writing_files=False).fit(x, y)
    assert model.score(x, y) > 0.9


def test_statsmodels_arima():
    from statsmodels.tsa.arima.model import ARIMA

    rng = np.random.default_rng(0)
    series = np.zeros(300)
    for t in range(1, 300):
        series[t] = 0.7 * series[t - 1] + rng.normal()
    fit = ARIMA(series, order=(1, 0, 0), trend="n").fit()
    assert abs(fit.params[0] - 0.7) < 0.1


def test_shap():
    import shap
    import xgboost as xgb

    x, y = _xy()
    model = xgb.XGBClassifier(n_estimators=20).fit(x, y)
    values = shap.TreeExplainer(model).shap_values(x)
    importance = np.abs(values).mean(axis=0)
    # y depends only on features 0 and 1
    assert set(np.argsort(importance)[-2:]) == {0, 1}


def test_scipy_optimize():
    from scipy.optimize import minimize

    res = minimize(lambda v: (v[0] - 3) ** 2 + (v[1] + 1) ** 2, [0, 0])
    assert np.allclose(res.x, [3, -1], atol=1e-4)


def test_networkx():
    import networkx as nx

    g = nx.Graph()
    g.add_weighted_edges_from([("a", "b", 1), ("b", "c", 1), ("a", "c", 5)])
    assert nx.shortest_path(g, "a", "c", weight="weight") == ["a", "b", "c"]


def test_ortools():
    from ortools.linear_solver import pywraplp

    s = pywraplp.Solver.CreateSolver("GLOP")
    x, y = s.NumVar(0, 10, "x"), s.NumVar(0, 10, "y")
    s.Add(x + y <= 4)
    s.Maximize(3 * x + 2 * y)
    assert s.Solve() == pywraplp.Solver.OPTIMAL
    assert abs(s.Objective().Value() - 12) < 1e-6


def test_highspy():
    import highspy

    h = highspy.Highs()
    h.silent()
    x, y = h.addVariable(0, 10), h.addVariable(0, 10)
    h.addConstr(x + y <= 4)
    h.maximize(3 * x + 2 * y)
    assert h.getModelStatus() == highspy.HighsModelStatus.kOptimal
    assert abs(h.getInfo().objective_function_value - 12) < 1e-6


def test_ortools_and_highspy_share_one_process():
    # ortools bundles its own libhighs.so.1 with the same soname as highspy's,
    # so whichever is imported first wins. Both orders must work.
    import subprocess
    import sys

    probe = "import {0}; import {1}; import highspy; highspy.Highs().run()"
    for first, second in [
        ("ortools.linear_solver.pywraplp", "highspy"),
        ("highspy", "ortools.linear_solver.pywraplp"),
    ]:
        subprocess.run([sys.executable, "-c", probe.format(first, second)], check=True)
