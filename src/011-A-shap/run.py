"""Step 11A: SHAP explanations of the undergrounded classifier in Taito City.

The XGBoost model of step 3B (street features only, AUC about 0.93) is trained
in 5 random folds; each fold's model explains its own test rows, so every
explanation comes from a model that did not see that row (out of fold).

1. Additivity: base value + SHAP values = the model's log-odds, row by row.
2. Global importance three ways: mean |SHAP|, XGBoost's gain, and permutation.
3. Dependence: SHAP against the value for the top features.
4. The map: mean SHAP of each feature per 250 m cell, next to the share undergrounded.
5. The leaky model of step 1B (poles and dense wires added): what SHAP shows.

    uv run python -u src/011-A-shap/run.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import shap  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402
from xgboost import XGBClassifier  # noqa: E402

from study_geoai import aoi, michiyomi, plot, tasks  # noqa: E402
from study_geoai.db import connect  # noqa: E402

OUT = Path(__file__).parent / "output"
TREES = 300  # about what early stopping chose in step 3B at rate 0.1, depth 6


def model():
    return XGBClassifier(n_estimators=TREES, learning_rate=0.1, max_depth=6, subsample=0.8,
                         colsample_bytree=0.8, n_jobs=8, random_state=0)  # fmt: skip


def out_of_fold(task):
    """Pooled out-of-fold probability, log-odds, SHAP values and base values."""
    n, k = task.X.shape
    prob, margin = np.empty(n), np.empty(n)
    values, base = np.empty((n, k)), np.empty(n)
    gain, perm = np.zeros(k), np.zeros(k)
    for train, test in StratifiedKFold(5, shuffle=True, random_state=0).split(task.X, task.y):
        m = model().fit(task.X[train], task.y[train])
        prob[test] = m.predict_proba(task.X[test])[:, 1]
        margin[test] = m.predict(task.X[test], output_margin=True)
        ex = shap.TreeExplainer(m)
        values[test] = ex.shap_values(task.X[test])
        base[test] = ex.expected_value
        g = m.get_booster().get_score(importance_type="gain")
        gain += np.array([g.get(f"f{j}", 0.0) for j in range(k)])
        perm += permutation_importance(m, task.X[test], task.y[test], scoring="roc_auc",
                                       n_repeats=5, random_state=0, n_jobs=8).importances_mean  # fmt: skip
    return prob, margin, values, base, gain / 5, perm / 5


def importance_table(task, values, gain, perm):
    mean_abs = np.abs(values).mean(axis=0)
    order = np.argsort(-mean_abs)
    print(
        "   feature               mean |SHAP|   rank   gain (share)   rank   permutation AUC drop   rank"
    )
    ranks = [np.argsort(np.argsort(-v)) + 1 for v in (mean_abs, gain, perm)]
    for j in order:
        print(f"   {task.features[j]:<20}  {mean_abs[j]:>11.3f}  {ranks[0][j]:>5}"
              f"  {gain[j] / gain.sum():>13.1%}  {ranks[1][j]:>5}  {perm[j]:>21.3f}  {ranks[2][j]:>5}")  # fmt: skip
    return order


def main():
    con = connect()
    OUT.mkdir(parents=True, exist_ok=True)
    task = tasks.undergrounded(con, "taito")
    print(f"## {task.name}: {len(task.y):,} scenes, {task.y.mean():.1%} undergrounded; "
          f"features {task.features}")  # fmt: skip
    prob, margin, values, base, gain, perm = out_of_fold(task)
    print(f"   pooled out-of-fold AUC {roc_auc_score(task.y, prob):.3f}")
    err = np.abs(base + values.sum(axis=1) - margin)
    print(f"   additivity: |base + sum(SHAP) - log-odds| max {err.max():.2e}, "
          f"base value (log-odds) {base.mean():.3f} = probability {1 / (1 + np.exp(-base.mean())):.3f}")  # fmt: skip
    order = importance_table(task, values, gain, perm)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, j in zip(axes, order[:3], strict=True):
        x = task.X[:, j]
        jitter = np.random.default_rng(0).normal(0, 0.05, len(x)) if len(np.unique(x)) <= 3 else 0
        ax.scatter(x + jitter, values[:, j], s=1, alpha=0.2)
        ax.axhline(0, color="grey", linewidth=0.5)
        ax.set_xlabel(task.features[j])
        ax.set_ylabel("SHAP (log-odds)")
        if task.features[j] == "roadway_width_m":
            ax.set_xlim(0, 25)
    fig.tight_layout()
    fig.savefig(OUT / "dependence-taito.png", dpi=120)
    plt.close(fig)
    top = order[0]
    x, v = task.X[:, top], values[:, top]
    for lo, hi in ((0, 4), (4, 6), (6, 8), (8, 12), (12, 99)):
        m = (x >= lo) & (x < hi)
        if m.any():
            print(f"   {task.features[top]} {lo} to {hi}: {m.sum():>6,} scenes, mean SHAP {v[m].mean():+.2f}, "
                  f"undergrounded {task.y[m].mean():.1%}")  # fmt: skip

    cells = task.groups["cell_250m"]
    uniq, inv, counts = np.unique(cells, return_inverse=True, return_counts=True)
    keep = counts >= 30
    rows_true = np.bincount(inv, weights=task.y) / counts
    maps = [("share undergrounded", rows_true, "share")]
    for j in order[:3]:
        maps.append(
            (
                f"mean SHAP of {task.features[j]}",
                np.bincount(inv, weights=values[:, j]) / counts,
                "SHAP",
            )
        )
    geo = []
    for c in uniq:
        w, s, e, n = michiyomi.cell_bounds(int(c))
        geo.append(
            json.dumps(
                {"type": "Polygon", "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]]}
            )
        )
    area = aoi.load("taito", con)
    outline = con.execute("select st_asgeojson(st_geomfromtext(?))", [area.wkt]).fetchone()[0]
    for k, (title, val, label) in enumerate(maps):
        plot.choropleth([(geo[i], float(val[i])) for i in np.flatnonzero(keep)],
                        OUT / f"map-{k}-taito.png", f"taito, 250 m cells: {title}", label,
                        diverging=label == "SHAP", outline=outline)  # fmt: skip
    r = np.corrcoef(rows_true[keep], (np.bincount(inv, weights=values.sum(axis=1)) / counts)[keep])[
        0, 1
    ]
    print(f"   {keep.sum()} cells with at least 30 scenes; correlation of the share undergrounded "
          f"with the cell's mean total SHAP: {r:.2f}")  # fmt: skip

    leaky = tasks.undergrounded(con, "taito", leaky=True)
    print(f"\n## leaky model (step 1B): features {leaky.features}")
    prob_l, _, values_l, _, gain_l, perm_l = out_of_fold(leaky)
    print(f"   pooled out-of-fold AUC {roc_auc_score(leaky.y, prob_l):.3f}")
    importance_table(leaky, values_l, gain_l, perm_l)
    print(f"\nfigures: {OUT}")


if __name__ == "__main__":
    main()
