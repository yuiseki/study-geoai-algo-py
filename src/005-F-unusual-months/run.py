"""Step 5F: unusual months in Japan's weather, by Isolation Forest and LOF.

Every month from 1979 to 2025 (564) is one row. Its features are anomalies:
for each of the eight regions and each of the four AgERA5 variables, the
regional mean for that month minus the 1991-2020 normal of the same calendar
month, divided by that calendar month's spread over the years (a z-score), so
a wet June and a wet December count the same. 32 features per month.

1. Isolation Forest and LOF each rank the 564 months; the top of both lists.
2. Do they agree? Rank correlation, and the overlap of their top 20.
3. Months that anyone in Japan would call unusual, and where the two methods
   put them: the cool summer of 1993, the heat of 2010, 2018 and 2023, the
   west Japan rain of July 2018, the warm winter of 2019-20.
4. What the methods see and a plain threshold does not: the months that are
   extreme in no single feature but odd in their combination.

    uv run python -u src/005-F-unusual-months/run.py
"""

import importlib.util
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.ensemble import IsolationForest  # noqa: E402
from sklearn.neighbors import LocalOutlierFactor  # noqa: E402

from study_geoai import ferspas  # noqa: E402

OUT = Path(__file__).parent / "output"
START, END = "1979-01-01", "2025-12-01"
VARS = ("rain", "et0", "tmax", "tmin")
TOP = 20
NEIGHBOURS = 20
KNOWN = {
    "1993-07": "cool summer of 1993",
    "1993-08": "cool summer of 1993",
    "2010-08": "heat of 2010",
    "2018-07": "west Japan rain and heat of July 2018",
    "2023-08": "heat of 2023",
    "2020-01": "warm winter of 2019-20",
    "2024-07": "heat of 2024",
}
_spec = importlib.util.spec_from_file_location(
    "step5e", Path(__file__).parents[1] / "005-E-climate-types" / "run.py"
)
step5e = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step5e)


def anomalies(cells):
    """(months, X[month, region x variable], names): z-scores against 1991-2020."""
    regions = cells["pref_code"].map(step5e.region_of).to_numpy()
    names, cols = [], []
    for v in VARS:
        months, values = ferspas.on_cells(v, cells, START, END)
        cal = months.astype("datetime64[M]").astype(int) % 12
        years = months.astype("datetime64[Y]").astype(int) + 1970
        base = (years >= 1991) & (years <= 2020)
        for r, _, _ in step5e.REGIONS:
            series = np.nanmean(values[:, regions == r], axis=1)
            z = np.empty_like(series)
            for m in range(12):
                ref = series[base & (cal == m)]
                z[cal == m] = (series[cal == m] - ref.mean()) / ref.std()
            cols.append(z)
            names.append(f"{v}:{r}")
    return months, np.column_stack(cols), names


def label(month):
    return str(month.astype("datetime64[M]"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = ferspas.japan_cells()
    months, X, names = anomalies(cells)
    print(f"## {len(months)} months ({label(months[0])} to {label(months[-1])}), "
          f"{X.shape[1]} features (8 regions x 4 variables, z-scores against 1991-2020)")  # fmt: skip

    iso = IsolationForest(n_estimators=500, random_state=0).fit(X)
    iso_score = -iso.score_samples(X)  # higher = more unusual
    lof = LocalOutlierFactor(n_neighbors=NEIGHBOURS).fit(X)
    lof_score = -lof.negative_outlier_factor_
    iso_rank = (-iso_score).argsort().argsort() + 1
    lof_rank = (-lof_score).argsort().argsort() + 1
    maxabs = np.abs(X).max(axis=1)
    max_rank = (-maxabs).argsort().argsort() + 1

    print(f"\n   top {TOP} by Isolation Forest, with the LOF rank and the rank by the single"
          " largest |z|")  # fmt: skip
    print("   rank  month     IF rank  LOF rank  max|z| rank  largest anomalies")
    for i in np.argsort(-iso_score)[:TOP]:
        big = np.argsort(-np.abs(X[i]))[:3]
        what = ", ".join(f"{names[j]} {X[i, j]:+.1f}" for j in big)
        print(f"   {iso_rank[i]:>4}  {label(months[i])}  {iso_rank[i]:>7}  {lof_rank[i]:>8}"
              f"  {max_rank[i]:>11}  {what}")  # fmt: skip

    rho = spearmanr(iso_score, lof_score).statistic
    top_iso, top_lof = set(np.argsort(-iso_score)[:TOP]), set(np.argsort(-lof_score)[:TOP])
    top_max = set(np.argsort(-maxabs)[:TOP])
    print(f"\n   Spearman between the two scores: {rho:.2f}; top {TOP} in common: "
          f"{len(top_iso & top_lof)}; IF and max|z| in common: {len(top_iso & top_max)}")  # fmt: skip

    print("\n   months people remember")
    index = {label(m): i for i, m in enumerate(months)}
    for m, what in KNOWN.items():
        i = index[m]
        print(f"   {m}  IF rank {iso_rank[i]:>3}  LOF rank {lof_rank[i]:>3}  max|z| rank"
              f" {max_rank[i]:>3}  {what}")  # fmt: skip

    combo = [i for i in np.argsort(-iso_score)[:TOP] if maxabs[i] < 2.5]
    print(f"\n   in the IF top {TOP} with no feature beyond |z| 2.5: "
          f"{', '.join(label(months[i]) for i in combo) or 'none'}")  # fmt: skip
    years = months.astype("datetime64[Y]").astype(int) + 1970
    for lo, hi in ((1979, 2000), (2001, 2025)):
        m = (years >= lo) & (years <= hi)
        print(f"   months {lo}-{hi} in the IF top 50: "
              f"{np.isin(np.where(m)[0], np.argsort(-iso_score)[:50]).sum()} of {m.sum()}")  # fmt: skip

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(months, iso_score, lw=0.8, label="Isolation Forest")
    ax2 = ax.twinx()
    ax2.plot(months, lof_score, lw=0.8, color="tab:orange", alpha=0.7, label="LOF")
    ax.set_ylabel("Isolation Forest score")
    ax2.set_ylabel("LOF score")
    ax.set_title("how unusual each month was over Japan")
    fig.savefig(OUT / "scores.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")
    print(f"credit: {ferspas.CREDIT}")


if __name__ == "__main__":
    main()
