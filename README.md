# study-geoai

Study environment for classical machine learning and mathematical optimisation, managed with uv.

| Library | Use |
| --- | --- |
| scikit-learn | General ML |
| xgboost | Gradient boosting |
| lightgbm | Gradient boosting |
| scipy (scipy.optimize) | Continuous optimisation |
| networkx | Graphs and networks |
| ortools | LP/MIP, CP-SAT, routing |
| highspy | HiGHS LP/MIP solver |

## Setup

```sh
uv sync
uv run pytest
```

## Note: highspy is pinned to the HiGHS inside ortools

ortools bundles its own `libhighs.so.1`, with the same soname as the one in highspy.
Whichever is imported first is used by both, so with mismatched versions the other fails with `undefined symbol`.
ortools 9.15 ships HiGHS 1.12.0, so highspy is pinned to `>=1.12,<1.13`.
When upgrading ortools, check the bundled version and move highspy with it:

```sh
strings .venv/lib/python3.12/site-packages/ortools/.libs/libhighs.so.1 | grep -xE '1\.[0-9]+\.[0-9]+'
```

`tests/test_env.py::test_ortools_and_highspy_share_one_process` checks both import orders.
