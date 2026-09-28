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

## Study map

| 系統 | まず触る定番 | 身につけたい感覚 |
|---|---|---|
| 回帰・分類 | 線形回帰、ロジスティック回帰 | 係数、損失関数、正則化、バイアス |
| 木系モデル | Decision Tree、Random Forest | 非線形、相互作用、過学習 |
| Boosting | Gradient Boosting、XGBoost、LightGBM、CatBoost | 現実の表形式データで強い理由 |
| 次元削減 | PCA | 高次元データをどう圧縮するか |
| クラスタリング | k-means、DBSCAN、HDBSCAN | 教師なしで構造を見つける |
| 異常検知 | Isolation Forest、LOF | 「普通から外れる」とは何か |
| 時系列 | ARIMA/ETS、lag特徴＋GBDT | 時間順序、未来情報リーク |
| 確率・不確実性 | calibration、prediction interval | 「当たる」以外に「どれくらい信用できるか」 |
| 説明可能性 | permutation importance、SHAP | モデルが何を根拠にしているか |
| 線形最適化 | LP | 制約付きで最良解を選ぶ |
| 整数最適化 | MILP | 選ぶ/選ばない、配置、割当 |
| グラフ | Dijkstra、A*、min-cost flow | 経路・ネットワーク問題 |
| 組合せ最適化 | knapsack、assignment、TSP、VRP | 探索空間が爆発する問題 |
| 制約充足 | CP-SAT | 勤務表、スケジューリング |
| 多目的意思決定 | weighted sum、Pareto frontier | 「最適」が一つではない問題 |
| 評価設計 | K-fold、Group CV、TimeSeriesSplit、Spatial CV | データリークを防ぐ |

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
