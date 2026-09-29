# study-geoai-algo-py

GeoAI のアルゴリズムを、台東区と東京 23 区の実データで一通り動かした記録。

範囲、データの読み方、分析の単位、評価と実行の決まり、共通のコードは [docs/setup.md](docs/setup.md)、データの出どころは [docs/datasets/](docs/datasets/README.md) にある。

## 動かし方

```sh
uv sync
uv run pytest
uv run python -u src/001-A-linear-regression/run.py
```

重い実験は `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0` で囲む ([docs/setup.md](docs/setup.md))。

## TODO

用語とアルゴリズムの達成度。チェックが付いているものは実験で動かしたもの (括弧の中がその実験)、付いていないものはまだ動かしていないもの。各系統の最初の行は、身につけたい感覚。52 項目のうち 40 項目が済み。

### 回帰・分類

係数、損失関数、正則化、バイアス

- [x] 線形回帰 ([001-A](src/001-A-linear-regression/README.md))
- [x] Ridge / Lasso ([001-A](src/001-A-linear-regression/README.md))
- [ ] Elastic Net
- [x] ロジスティック回帰 ([001-B](src/001-B-logistic-regression/README.md))

### 木系モデル

非線形、相互作用、過学習

- [x] 決定木 (Decision Tree) ([002-A](src/002-A-decision-tree/README.md))
- [x] ランダムフォレスト (Random Forest) ([002-B](src/002-B-random-forest/README.md))
- [x] 部分依存 (partial dependence) ([002-B](src/002-B-random-forest/README.md))

### Boosting

現実の表形式データで強い理由

- [x] Gradient Boosting (scikit-learn の HistGradientBoosting) ([003-A](src/003-A-gradient-boosting/README.md))
- [x] XGBoost (学習率、深さ、早期打ち切り) ([003-A](src/003-A-gradient-boosting/README.md), [003-B](src/003-B-xgboost/README.md))
- [x] LightGBM ([003-A](src/003-A-gradient-boosting/README.md))
- [x] CatBoost ([003-A](src/003-A-gradient-boosting/README.md), [003-E](src/003-E-pooled-target/README.md))

### 評価設計

データリークを防ぐ

- [x] K-fold / 層化 K-fold (StratifiedKFold) ([001-B](src/001-B-logistic-regression/README.md), [004-A](src/004-A-cross-validation/README.md))
- [x] Group CV / 空間ブロック CV (GroupKFold でブロックを作った) ([004-A](src/004-A-cross-validation/README.md), [004-C](src/004-C-small-areas/README.md))
- [ ] verde の BlockKFold
- [x] 時間で分ける (過去で学習、未来で試す) ([004-B](src/004-B-data-leakage/README.md))
- [ ] TimeSeriesSplit
- [x] データリーク (target encoding、答えの言い換え) ([001-B](src/001-B-logistic-regression/README.md), [004-B](src/004-B-data-leakage/README.md))
- [x] out-of-fold 予測をまとめて採点 ([004-A](src/004-A-cross-validation/README.md))
- [x] 目的変数の雑音の天井 ([003-C](src/003-C-noise-ceiling/README.md))

### クラスタリング

教師なしで構造を見つける

- [x] k-means、シルエット ([005-A](src/005-A-k-means/README.md), [005-C](src/005-C-grid-types/README.md))
- [x] DBSCAN、k 距離グラフ ([005-B](src/005-B-dbscan/README.md))
- [x] HDBSCAN ([005-B](src/005-B-dbscan/README.md))
- [x] ディリクレ過程混合 (DPMM、BayesianGaussianMixture) ([005-D](src/005-D-dpmm/README.md))
- [x] MAUP (集計単位で結果が変わる) ([005-C](src/005-C-grid-types/README.md))

### 次元削減

高次元データをどう圧縮するか

- [x] PCA ([006-A](src/006-A-pca/README.md), [006-B](src/006-B-pca-wards/README.md))
- [x] 並行分析、ブートストラップ (残す主成分の数) ([006-A](src/006-A-pca/README.md))

### 異常検知

「普通から外れる」とは何か

- [ ] Isolation Forest
- [ ] LOF (Local Outlier Factor)

### 時系列

時間順序、未来情報リーク

- [ ] ARIMA / ETS
- [ ] lag 特徴 + GBDT

### 確率・不確実性

「当たる」以外に「どれくらい信用できるか」

- [x] 較正 (calibration): Platt、isotonic、ECE、Brier、信頼度曲線 ([011-B](src/011-B-calibration/README.md))
- [ ] 予測区間 (prediction interval)

### 説明可能性

モデルが何を根拠にしているか

- [x] permutation importance ([011-A](src/011-A-shap/README.md))
- [x] SHAP (TreeExplainer) ([011-A](src/011-A-shap/README.md))

### 線形最適化

制約付きで最良解を選ぶ

- [x] LP、LP 緩和 ([008-A](src/008-A-lp/README.md))
- [x] 双対価格 ([008-A](src/008-A-lp/README.md))
- [x] 内点法 ([008-B](src/008-B-milp/README.md))

### 整数最適化

選ぶ/選ばない、配置、割当

- [x] MILP (最大被覆) ([008-B](src/008-B-milp/README.md))
- [x] 欲張り法と LP の上限による保証 ([008-B](src/008-B-milp/README.md))
- [x] p-median、交換法 (Teitz-Bart) ([009-B](src/009-B-facility-location/README.md))

### グラフ

経路・ネットワーク問題

- [x] Dijkstra (多始点) ([007-A](src/007-A-dijkstra/README.md))
- [x] A* ([007-B](src/007-B-a-star/README.md))
- [x] 二部グラフの最大マッチング ([010-A](src/010-A-cp-sat/README.md))
- [ ] min-cost flow (輸送問題は LP で解いた)

### 組合せ最適化

探索空間が爆発する問題

- [ ] knapsack
- [x] assignment (輸送問題、ハンガリアン法) ([009-A](src/009-A-assignment/README.md))
- [ ] TSP
- [ ] VRP

### 制約充足

勤務表、スケジューリング

- [x] CP-SAT ([010-A](src/010-A-cp-sat/README.md))
- [x] 区間変数と NoOverlap、対称性の除去 ([010-B](src/010-B-scheduling/README.md))

### 多目的意思決定

「最適」が一つではない問題

- [x] 重み付き和 (weighted sum) ([012-A](src/012-A-multi-objective-optimization/README.md))
- [x] パレートフロンティア、ε 制約法 ([012-B](src/012-B-epsilon-constraint/README.md))

## ステップごとの記録

`src/NNN-X-topic/` に、ステップ NNN の X 番目の実験を置く。A、B、C は実験の順番。各ディレクトリの `README.md` に数字と図の説明、`run.py` にコードがある。図と実行の記録は `output/` に書く (git には入れない)。

### 1. 線形回帰 / ロジスティック回帰

- 001-A 線形回帰 ([README](src/001-A-linear-regression/README.md), [run.py](src/001-A-linear-regression/run.py)): 町丁目の人口密度を建物と POI から。23 区で係数が違って見えたのは、住む人が 0 人の小地域のせいだった。
- 001-B ロジスティック回帰 ([README](src/001-B-logistic-regression/README.md), [run.py](src/001-B-logistic-regression/run.py)): 無電柱化の分類。電柱の数を入れると答えの言い換えになり、精度は偏った答えでも高く出るのであてにならない。
- 計画から変えたこと: Ridge と Lasso は 001-A の中で比べるにとどめた。

### 2. 決定木 / ランダムフォレスト

- 002-A 決定木 ([README](src/002-A-decision-tree/README.md), [run.py](src/002-A-decision-tree/run.py)): 深さを変えて過学習を見た。行の少ない台東区の人口密度では線形に負ける。
- 002-B ランダムフォレスト ([README](src/002-B-random-forest/README.md), [run.py](src/002-B-random-forest/run.py)): どの問題でも 1 本の木より良い。部分依存で、細い道では緑の効き方が違うという相互作用が見えた。
- 23 区の全 99 万行で森を作ると 16GB に達したので、20 万行の標本にした。

### 3. 勾配ブースティング / XGBoost

- 003-A 5 つのブースティング ([README](src/003-A-gradient-boosting/README.md), [run.py](src/003-A-gradient-boosting/run.py)): 携帯の下り速度はほとんど予測できず、モデルの差にも意味が無い。
- 003-B XGBoost ([README](src/003-B-xgboost/README.md), [run.py](src/003-B-xgboost/run.py)): 信号のある無電柱化で、学習率、深さ、早期打ち切りを見た。
- 003-C 雑音の天井 ([README](src/003-C-noise-ceiling/README.md), [run.py](src/003-C-noise-ceiling/run.py)): 同じタイルの前の四半期ですら速度をほとんど説明できない。目的変数がほとんど雑音。
- 003-D 基地局 ([README](src/003-D-cell-towers/README.md), [run.py](src/003-D-cell-towers/run.py)): OpenCelliD の基地局を足しても、ほとんど良くならない。
- 003-E まとめた目的変数 ([README](src/003-E-pooled-target/README.md), [run.py](src/003-E-pooled-target/run.py)): 3 四半期を測定回数で重み付けすると少し上がるが、乱数の種による揺れがモデルの差と同じくらいある。
- 計画から変えたこと: 速度には信号が無かったので、XGBoost の性質は無電柱化で見た。003-C から 003-E は足した実験。

### 4. 交差検証とデータリーク

- 004-A 分け方 ([README](src/004-A-cross-validation/README.md), [run.py](src/004-A-cross-validation/run.py)): 台東区では空間ブロックで点数がはっきり下がり、23 区ではほとんど下がらない。
- 004-B データリーク ([README](src/004-B-data-leakage/README.md), [run.py](src/004-B-data-leakage/run.py)): target encoding の漏れはランダム分割では見抜けない。撮影年の漏れは小さい。
- 004-C 範囲の小ささ ([README](src/004-C-small-areas/README.md), [run.py](src/004-C-small-areas/run.py)): 空間 CV で点数が下がるのはどの区でも同じで、ブロックの少ない区ほど大きい。
- 計画から変えたこと: 004-C は 004-A の仮説を確かめるために足した。

### 5. k-means / DBSCAN (と DPMM)

- 005-A k-means ([README](src/005-A-k-means/README.md), [run.py](src/005-A-k-means/run.py)): 町丁目を「街の型」に分けると、台東区は 4 型。ただし塊ははっきりしない。
- 005-B DBSCAN と HDBSCAN ([README](src/005-B-dbscan/README.md), [run.py](src/005-B-dbscan/run.py)): POI の点は台東区では区全体が連鎖する。eps を固定すると、塊に入る割合は区の密度でほぼ決まる。
- 005-C 1km メッシュの型 ([README](src/005-C-grid-types/README.md), [run.py](src/005-C-grid-types/run.py)): 23 区の大きな構造は見えるが、台東区の小さな地区の型は消える (MAUP)。
- 005-D ディリクレ過程混合 ([README](src/005-D-dpmm/README.md), [run.py](src/005-D-dpmm/run.py)): k を決めなくてよくはならない。型の数を決めていたのは共分散の事前分布だった。
- 計画から変えたこと: 005-A は電柱と街灯の点の予定だったが、町丁目の型に変えた。005-C と 005-D は足した実験。

### 6. PCA

- 006-A 台東区 ([README](src/006-A-pca/README.md), [run.py](src/006-A-pca/run.py)): みちよみの 12 の数値から、PC1 は電柱と無電柱化、PC2 は道の広さと細さ。残すのは 2 つ。
- 006-B 23 区 ([README](src/006-B-pca-wards/README.md), [run.py](src/006-B-pca-wards/run.py)): PC1 は台東区と同じ向き。台東区の軸は平面の中で約 45 度回っていたので、主成分は平面で比べる。
- 行わなかったこと: WorldPop の年齢構成の PCA。

### 7. Dijkstra / A*

- 007-A Dijkstra ([README](src/007-A-dijkstra/README.md), [run.py](src/007-A-dijkstra/run.py)): 町丁目から最寄りの病院と避難場所まで歩く距離。多始点にすると 1 回で済み、38 倍速い。
- 007-B A* ([README](src/007-B-a-star/README.md), [run.py](src/007-B-a-star/run.py)): 確定するノードは Dijkstra の 1/10 だが、増え方は同じ。遠回りの原因は道の無い帯 (大学の区画、線路、隅田川)。
- 行わなかったこと: 23 区への拡大、一方通行、道路網どうしの比較、快適さや浸水を重みにする経路、時刻表つきのグラフ。

### 8. LP / MILP

- 008-A LP ([README](src/008-A-lp/README.md), [run.py](src/008-A-lp/run.py)): 最大被覆の LP 緩和。拠点が少ないうちは LP の解がそのまま整数。双対価格が拠点 1 つの価値を人数で表す。
- 008-B MILP ([README](src/008-B-milp/README.md), [run.py](src/008-B-milp/run.py)): 台東区は分枝なしで解ける。23 区では需要をまとめて内点法で解き、全候補地では欲張り法と LP の上限で約 1% の保証を出した。
- 計画から変えたこと: 23 区の覆う条件は、歩く距離でなく直線距離にした。

### 9. 割当 / 施設配置

- 009-A 割当 ([README](src/009-A-assignment/README.md), [run.py](src/009-A-assignment/run.py)): 容量のある避難場所への割当。輸送問題の LP は自動的に整数で、ハンガリアン法と一致する。荒川の氾濫時は実行不可能。
- 009-B p-median ([README](src/009-B-facility-location/README.md), [run.py](src/009-B-facility-location/run.py)): 交換法でほぼ最適。同じ数の拠点でも、p-median と最大被覆では選ぶ場所がまったく違う。
- 計画から変えたこと: 需要は人口だけにした。
- 行わなかったこと: 基地局の候補地の評価、区の境界をまたぐ割当。

### 10. CP-SAT / スケジューリング

- 010-A 車両の最少台数 ([README](src/010-A-cp-sat/README.md), [run.py](src/010-A-cp-sat/run.py)): GTFS の便から CP-SAT で。二部グラフの最大マッチングと一致する。
- 010-B 乗務員の勤務 ([README](src/010-B-scheduling/README.md), [run.py](src/010-B-scheduling/run.py)): 区間変数と NoOverlap で。最初のモデルは誤って「最適」と答え、手で組んだ解で気づいた。
- 行わなかったこと: 都営バス、葛飾区と杉並区。

### 11. SHAP / 較正

- 011-A SHAP ([README](src/011-A-shap/README.md), [run.py](src/011-A-shap/run.py)): 無電柱化の XGBoost を説明した。上位 3 つは 3 つの重要度で一致。街灯の数には電柱の代わりという漏れの疑い。
- 011-B 較正 ([README](src/011-B-calibration/README.md), [run.py](src/011-B-calibration/run.py)): ランダムフォレストはそのままでよく較正されていた。isotonic はどれも改善し、Platt は木のモデルを悪くした。
- 計画から変えたこと: SHAP の題材を通信速度から無電柱化に変えた。
- 行わなかったこと: みちよみの `confidence` の較正。

### 12. 多目的最適化

- 012-A 重み付き和 ([README](src/012-A-multi-objective-optimization/README.md), [run.py](src/012-A-multi-objective-optimization/run.py)): 最大被覆に拠点の数と浸水を足した。候補地の 89% が浸水区域にあり、重みを振っても中間の解がほとんど出ない。
- 012-B ε 制約法 ([README](src/012-B-epsilon-constraint/README.md), [run.py](src/012-B-epsilon-constraint/run.py)): 34 のパレート解を出した。重み付き和はそのうち 11 しか出さない (凸包の上だけ)。
- 行わなかったこと: 23 区で区ごとのパレートフロンティアを比べること。
