"""Step 11C: 90% prediction intervals for a month's weather, and whether they hold.

Every AgERA5 cell of the Kanto region (study_geoai.ferspas) and every month is
one row: predict this month's rain (mm) or daily maximum temperature (C) from
the calendar month, the cell's position and the cell's own previous twelve
months. The years split in time:

    train 1980-2010    calibration 2011-2015    test 2016-2025

Three ways to give a 90% interval:

- climatology: the 5th and 95th percentiles of that cell and calendar month in
  the training years, with no model at all
- quantile GBDT: two gradient boosting models with the quantile loss, at 0.05
  and 0.95
- conformalised quantile regression (CQR): the same two models, widened (or
  narrowed) by the 90% quantile of how far the calibration years fell outside
  them. Conformal guarantees 90% on average only if the test years are
  exchangeable with the calibration years.

Scored on the test years: coverage (should be 90%), mean width, and the misses
split into above and below the interval, overall and by calendar month.

    uv run python -u src/011-C-prediction-interval/run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor  # noqa: E402

from study_geoai import ferspas  # noqa: E402

OUT = Path(__file__).parent / "output"
START, END = "1979-01-01", "2025-12-01"
ALPHA = 0.10
KANTO = ("08", "09", "10", "11", "12", "13", "14")
TRAIN, CALIB, TEST = (1980, 2010), (2011, 2015), (2016, 2025)


def table(cells, variable):
    """X, y, year, calendar month, cell index for every cell-month with 12 months of history."""
    months, values = ferspas.on_cells(variable, cells, START, END)  # month x cell
    T, N = values.shape
    cal = months.astype("datetime64[M]").astype(int) % 12
    years = months.astype("datetime64[Y]").astype(int) + 1970
    t = np.arange(12, T)
    lags = np.stack([values[t - k] for k in range(1, 13)], axis=-1)  # rows x cell x 12
    rows = len(t) * N
    X = np.column_stack([
        np.repeat(cal[t], N),
        np.tile(cells["lon"].to_numpy(), len(t)),
        np.tile(cells["lat"].to_numpy(), len(t)),
        lags.reshape(rows, 12),
    ])  # fmt: skip
    y = values[t].reshape(rows)
    ok = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
    return (X[ok], y[ok], np.repeat(years[t], N)[ok], np.repeat(cal[t], N)[ok],
            np.tile(np.arange(N), len(t))[ok])  # fmt: skip


def within(years, span):
    return (years >= span[0]) & (years <= span[1])


def quantile_model(q):
    return HistGradientBoostingRegressor(loss="quantile", quantile=q, max_iter=300,
                                         learning_rate=0.05, max_leaf_nodes=31,
                                         categorical_features=[0], random_state=0)  # fmt: skip


def score(name, lo, hi, y, cal):
    inside = (y >= lo) & (y <= hi)
    above, below = (y > hi).mean(), (y < lo).mean()
    by_month = [inside[cal == m].mean() for m in range(12)]
    print(f"   {name:<22} coverage {inside.mean():>6.1%}   width {np.mean(hi - lo):>7.1f}"
          f"   above {above:>5.1%}   below {below:>5.1%}   worst month {int(np.argmin(by_month)) + 1}"
          f" {min(by_month):.0%}")  # fmt: skip
    return by_month


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = ferspas.japan_cells()
    cells = cells[cells["pref_code"].isin(KANTO)].reset_index(drop=True)
    curves = {}
    for variable, unit in (("rain", "mm"), ("tmax", "C")):
        X, y, years, cal, cell = table(cells, variable)
        tr, ca, te = within(years, TRAIN), within(years, CALIB), within(years, TEST)
        print(f"\n## Kanto, {variable} ({unit}): {len(cells)} cells, rows train {tr.sum():,},"
              f" calibration {ca.sum():,}, test {te.sum():,}; target {1 - ALPHA:.0%}")  # fmt: skip

        # climatology: per cell and calendar month, from the training years
        lo_c, hi_c = np.empty(te.sum()), np.empty(te.sum())
        test_idx = np.where(te)[0]
        for c in range(len(cells)):
            for m in range(12):
                ref = y[tr & (cell == c) & (cal == m)]
                sel = (cell[test_idx] == c) & (cal[test_idx] == m)
                lo_c[sel], hi_c[sel] = np.quantile(ref, [ALPHA / 2, 1 - ALPHA / 2])
        curves[(variable, "climatology")] = score("climatology", lo_c, hi_c, y[te], cal[te])

        low = quantile_model(ALPHA / 2).fit(X[tr], y[tr])
        high = quantile_model(1 - ALPHA / 2).fit(X[tr], y[tr])
        lo_q, hi_q = low.predict(X[te]), high.predict(X[te])
        curves[(variable, "quantile GBDT")] = score("quantile GBDT", lo_q, hi_q, y[te], cal[te])

        # CQR: how far outside the calibration years fell, at the 90% level
        e = np.maximum(low.predict(X[ca]) - y[ca], y[ca] - high.predict(X[ca]))
        n = len(e)
        qhat = np.quantile(e, min(1.0, np.ceil((n + 1) * (1 - ALPHA)) / n))
        curves[(variable, "CQR")] = score(f"CQR (widen {qhat:+.1f})", lo_q - qhat, hi_q + qhat,
                                          y[te], cal[te])  # fmt: skip
        inside_cal = (y[ca] >= low.predict(X[ca])) & (y[ca] <= high.predict(X[ca]))
        print(f"   (quantile GBDT on the calibration years: coverage {inside_cal.mean():.1%})")

        # Year by year: does coverage drift over the test decade?
        cov = [((y[te] >= lo_q - qhat) & (y[te] <= hi_q + qhat))[years[te] == yr].mean()
               for yr in range(TEST[0], TEST[1] + 1)]  # fmt: skip
        print(f"   CQR coverage by test year: "
              f"{', '.join(f'{yr}:{c:.0%}' for yr, c in zip(range(TEST[0], TEST[1] + 1), cov, strict=True))}")  # fmt: skip

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    for ax, variable in zip(axes, ("rain", "tmax"), strict=True):
        for name in ("climatology", "quantile GBDT", "CQR"):
            ax.plot(range(12), curves[(variable, name)], marker="o", label=name)
        ax.axhline(1 - ALPHA, color="grey", ls="--", lw=0.8)
        ax.set_xticks(range(12), [str(m) for m in range(1, 13)])
        ax.set_title(f"Kanto {variable}: coverage by calendar month, 2016-2025")
    axes[0].legend()
    fig.savefig(OUT / "coverage.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nfigures: {OUT}")
    print(f"credit: {ferspas.CREDIT}")


if __name__ == "__main__":
    main()
