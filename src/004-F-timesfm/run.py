"""Step 4F: TimesFM 2.5, zero-shot, against the forecasts of step 4D.

TimesFM is a time series foundation model from Google Research, pre-trained on
a large corpus of real and synthetic series. It forecasts a series it has
never seen from its history alone: no fitting to this series at all. Here it
gets step 4D's problem unchanged: Tokyo's monthly daily maximum temperature
and rain (AgERA5 cells of the 23 wards, 1979-2025), the last ten years in
twelve-month blocks by TimeSeriesSplit, one month and twelve months ahead.

- One month ahead: the history up to each month is the context, and the next
  month is forecast (a separate context for each of the 120 months).
- Twelve months ahead: the history up to each block's start is the context,
  and the whole block is forecast.
- The same baselines and models as step 4D, recomputed on the same folds.
- TimesFM's quantile head gives the 10% to 90% points (checked on a sine wave:
  index 0 is the mean, 1 to 9 the deciles, the point forecast is the median):
  how often does the 80% interval hold the actual month (step 11C's question)?

TimesFM 2.5 (200M, PyTorch) is pinned by revision: its weights are Apache 2.0.
TimesFM 3.0 weights are non-commercial and are not used.

    CUDA_VISIBLE_DEVICES= uv run --group timesfm python -u src/004-F-timesfm/run.py
"""

import importlib.util
import time
from pathlib import Path

import numpy as np
from sklearn.model_selection import TimeSeriesSplit

from study_geoai import ferspas

OUT = Path(__file__).parent / "output"
REPO, REVISION = "google/timesfm-2.5-200m-pytorch", "1d952420fba87f3c6dee4f240de0f1a0fbc790e3"
_spec = importlib.util.spec_from_file_location(
    "step4d", Path(__file__).parents[1] / "004-D-time-series" / "run.py"
)
step4d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(step4d)


def load_timesfm():
    import timesfm

    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(REPO, revision=REVISION)
    model.compile(timesfm.ForecastConfig(
        max_context=1024, max_horizon=128, normalize_inputs=True,
        use_continuous_quantile_head=True, force_flip_invariance=True,
        infer_is_positive=False, fix_quantile_crossing=True,
    ))  # fmt: skip
    return model


def quantile(qs, q):
    """TimesFM returns [mean, 0.1, ..., 0.9]; 0.05 and 0.95 are not among them."""
    return qs[..., {0.1: 1, 0.5: 5, 0.9: 9}[q]]


def timesfm_forecasts(model, y, test, h):
    """Point forecasts and the 10% and 90% points for `test`, h months ahead."""
    if h == 1:
        contexts = [y[:t].astype(np.float32) for t in test]
        point, qs = model.forecast(horizon=1, inputs=contexts)
        return point[:, 0], quantile(qs, 0.1)[:, 0], quantile(qs, 0.9)[:, 0]
    point, qs = model.forecast(horizon=len(test), inputs=[y[: test[0]].astype(np.float32)])
    return point[0], quantile(qs, 0.1)[0], quantile(qs, 0.9)[0]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    model = load_timesfm()
    print(
        f"## TimesFM 2.5 200M loaded in {time.perf_counter() - t0:.1f} s ({REPO}@{REVISION[:12]})"
    )
    cells = ferspas.japan_cells()
    split = TimeSeriesSplit(n_splits=step4d.FOLDS, test_size=step4d.BLOCK)
    for variable, unit in (("tmax", "C"), ("rain", "mm")):
        months, y, n = step4d.tokyo(cells, variable)
        print(f"\n## Tokyo 23 wards ({n} cells), {variable}: {len(y)} months")
        for h in step4d.HORIZONS:
            errors, inside, seconds = {}, [], 0.0
            for train, test in split.split(y):
                for name, pred in step4d.forecasts(y, months, train, test, h).items():
                    errors.setdefault(name, []).append(pred - y[test])
                t1 = time.perf_counter()
                point, lo, hi = timesfm_forecasts(model, y, test, h)
                seconds += time.perf_counter() - t1
                errors.setdefault("TimesFM 2.5", []).append(point - y[test])
                inside.append((y[test] >= lo) & (y[test] <= hi))
            base = np.abs(np.concatenate(errors["climatology"])).mean()
            print(f"   {h:>2} month ahead, last {step4d.FOLDS * step4d.BLOCK} months "
                  f"(MAE {unit}, against climatology, mean error: + forecasts too high)")  # fmt: skip
            for name, e in errors.items():
                e = np.concatenate(e)
                mae = np.abs(e).mean()
                print(f"      {name:<16} {mae:>7.2f}   {mae / base - 1:+.1%}   {e.mean():+.2f}")
            inside = np.concatenate(inside)
            print(f"      TimesFM 80% interval (10% to 90% points) holds {inside.mean():.1%} of the"
                  f" months; TimesFM took {seconds:.1f} s for these forecasts")  # fmt: skip
    print(f"\ncredit: {ferspas.CREDIT}")


if __name__ == "__main__":
    main()
