"""Step 4D: forecasting Tokyo's monthly weather, and splitting a time series honestly.

The series are the monthly means over the AgERA5 cells of the 23 wards
(study_geoai.ferspas): daily maximum temperature (C) and rain (mm/month),
1979-01 to 2025-12, 564 months.

Forecasts are made one month ahead and twelve months ahead, and scored over the
last ten years with TimeSeriesSplit: each fold trains on everything before a
twelve-month block and forecasts that block. Models:

- climatology: the training mean of the calendar month
- seasonal naive: the same month a year (or, one month ahead, also a year) before
- ETS: Holt-Winters, additive trend and seasonality (statsmodels ETSModel)
- SARIMA (1,0,1)(0,1,1,12) (statsmodels SARIMAX)
- GBDT on lag features: calendar month, a time index and the values h to h+11
  months before (h is the horizon), so nothing it sees is later than the
  forecast origin

Then the same GBDT scored by a shuffled K-fold: rows from the future train a
model that is asked about the past, and the score says so.

    uv run python -u src/004-D-time-series/run.py
"""

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor  # noqa: E402
from sklearn.model_selection import KFold, TimeSeriesSplit  # noqa: E402
from statsmodels.tools.sm_exceptions import ConvergenceWarning  # noqa: E402
from statsmodels.tsa.exponential_smoothing.ets import ETSModel  # noqa: E402
from statsmodels.tsa.statespace.sarimax import SARIMAX  # noqa: E402

from study_geoai import ferspas  # noqa: E402

OUT = Path(__file__).parent / "output"
START, END = "1979-01-01", "2025-12-01"
WARDS_BOX = (139.55, 35.5, 139.95, 35.85)  # the 23 wards, roughly
FOLDS, BLOCK = 10, 12
HORIZONS = (1, 12)


def tokyo(cells, variable):
    lon, lat = cells["lon"].to_numpy(), cells["lat"].to_numpy()
    w, s, e, n = WARDS_BOX
    m = (cells["pref"] == "東京都").to_numpy() & (lon >= w) & (lon <= e) & (lat >= s) & (lat <= n)
    months, values = ferspas.on_cells(variable, cells[m], START, END)
    return months, np.nanmean(values, axis=1), int(m.sum())


def lag_table(y, months, h):
    """Rows t with calendar month, time index and y[t-h] .. y[t-h-11]."""
    cal = months.astype("datetime64[M]").astype(int) % 12
    lags = [np.r_[np.full(k, np.nan), y[:-k]] for k in range(h, h + 12)]
    return np.column_stack([cal, np.arange(len(y)), *lags])


def gbdt():
    return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_depth=3,
                                         categorical_features=[0], random_state=0)  # fmt: skip


def forecasts(y, months, train, test, h):
    """Each model's forecasts for `test` (a block right after `train`), h months ahead.

    One month ahead, the statistical models keep their fitted parameters and are
    fed the observations up to each forecast origin (a one-step prediction);
    twelve months ahead, they forecast the whole block from its origin.
    """
    cal = months.astype("datetime64[M]").astype(int) % 12
    out = {}
    out["climatology"] = np.array([y[train][cal[train] == cal[t]].mean() for t in test])
    out["seasonal naive"] = y[test - 12]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        warnings.simplefilter("ignore", UserWarning)
        warnings.simplefilter("ignore", RuntimeWarning)
        models = {
            "ETS": lambda s: ETSModel(s, error="add", trend="add", seasonal="add",
                                      seasonal_periods=12, damped_trend=True),
            "SARIMA": lambda s: SARIMAX(s, order=(1, 0, 1), seasonal_order=(0, 1, 1, 12)),
        }  # fmt: skip
        for name, make in models.items():
            fit = make(y[train]).fit(disp=False)
            if h == 1:
                full = fit.apply(y[: test[-1] + 1]) if name == "SARIMA" else None
                if full is not None:
                    out[name] = full.predict(start=test[0], end=test[-1])
                else:
                    # ETSModel has no apply(); refit-free one-step is its smoothing of the
                    # full series with the training parameters.
                    smoothed = make(y[: test[-1] + 1]).smooth(fit.params)
                    out[name] = smoothed.fittedvalues[test]
            else:
                out[name] = np.asarray(fit.forecast(len(test)))
    X = lag_table(y, months, h)
    ok = ~np.isnan(X[train]).any(axis=1)
    model = gbdt().fit(X[train][ok], y[train][ok])
    out["GBDT on lags"] = model.predict(X[test])
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = ferspas.japan_cells()
    plot_data = {}
    for variable, unit in (("tmax", "C"), ("rain", "mm")):
        months, y, n = tokyo(cells, variable)
        print(f"\n## Tokyo 23 wards ({n} cells), {variable}: {len(y)} months, "
              f"mean {y.mean():.1f} {unit}")  # fmt: skip
        split = TimeSeriesSplit(n_splits=FOLDS, test_size=BLOCK)
        for h in HORIZONS:
            errors = {}
            for train, test in split.split(y):
                for name, pred in forecasts(y, months, train, test, h).items():
                    errors.setdefault(name, []).append(pred - y[test])
            base = np.abs(np.concatenate(errors["climatology"])).mean()
            print(f"   {h:>2} month ahead, last {FOLDS * BLOCK} months "
                  f"(MAE {unit}, against climatology, and the mean error: + forecasts too high)")  # fmt: skip
            for name, e in errors.items():
                mae = np.abs(np.concatenate(e)).mean()
                bias = np.concatenate(e).mean()
                print(f"      {name:<16} {mae:>7.2f}   {mae / base - 1:+.1%}   {bias:+.2f}")
            if h == 1:
                plot_data[variable] = (months, y, errors)

        # The leak: the same one-month-ahead GBDT, scored by a shuffled K-fold over all years.
        X = lag_table(y, months, 1)
        ok = ~np.isnan(X).any(axis=1)
        Xo, yo = X[ok], y[ok]
        shuffled = []
        for train, test in KFold(FOLDS, shuffle=True, random_state=0).split(Xo):
            shuffled.append(np.abs(gbdt().fit(Xo[train], yo[train]).predict(Xo[test]) - yo[test]))
        honest = []
        for train, test in TimeSeriesSplit(n_splits=FOLDS, test_size=BLOCK).split(Xo):
            honest.append(np.abs(gbdt().fit(Xo[train], yo[train]).predict(Xo[test]) - yo[test]))
        # And the same shuffled K-fold scored only on the last ten years, like the honest split.
        last = np.zeros(len(yo), bool)
        last[-FOLDS * BLOCK :] = True
        pred = np.empty(len(yo))
        for train, test in KFold(FOLDS, shuffle=True, random_state=0).split(Xo):
            pred[test] = gbdt().fit(Xo[train], yo[train]).predict(Xo[test])
        print(f"   GBDT one month ahead: shuffled K-fold MAE {np.concatenate(shuffled).mean():.2f}"
              f" (last ten years only {np.abs(pred - yo)[last].mean():.2f}); TimeSeriesSplit"
              f" {np.concatenate(honest).mean():.2f}")  # fmt: skip

    fig, axes = plt.subplots(2, 1, figsize=(12, 6))
    for ax, (variable, (months, y, _)) in zip(axes, plot_data.items(), strict=True):
        ax.plot(months[-FOLDS * BLOCK - 36 :], y[-FOLDS * BLOCK - 36 :], color="black", lw=1)
        ax.set_title(f"Tokyo {variable}, the last {FOLDS * BLOCK} months are forecast")
    fig.tight_layout()
    fig.savefig(OUT / "series.png", dpi=130)
    plt.close(fig)
    print(f"\nfigures: {OUT}")
    print(f"credit: {ferspas.CREDIT}")


if __name__ == "__main__":
    main()
