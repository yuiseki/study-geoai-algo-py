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

- [x] 線形回帰 (既知のデータをもとに変数同士の直線的な関係を数式で表し、未知の値を予測する。 [001-A](src/001-A-linear-regression/README.md))
- [x] Ridge / Lasso (通常の線形回帰で、過学習を防ぐためのペナルティ項を加えた、回帰分析の手法。 [001-A](src/001-A-linear-regression/README.md))
- [ ] Elastic Net (Ridge と Lasso のペナルティを混ぜて使う線形回帰。)
- [x] ロジスティック回帰 (特徴量の重み付き和をシグモイド関数に通し、あるクラスに入る確率を予測する分類の手法。 [001-B](src/001-B-logistic-regression/README.md))

### 木系モデル

非線形、相互作用、過学習

- [x] 決定木 (Decision Tree) (特徴量のしきい値で「はい/いいえ」の分岐を繰り返し、データを分けて予測する木構造のモデル。 [002-A](src/002-A-decision-tree/README.md))
- [x] ランダムフォレスト (Random Forest) (行と特徴量を無作為に選んで作った多数の決定木の予測を平均 (多数決) する手法。 [002-B](src/002-B-random-forest/README.md))
- [x] 部分依存 (partial dependence) (ほかの特徴量を固定したまま 1 つの特徴量だけを動かしたとき、予測が平均してどう変わるかを描く方法。 [002-B](src/002-B-random-forest/README.md))

### Boosting

現実の表形式データで強い理由

- [x] Gradient Boosting (scikit-learn の HistGradientBoosting) (前の木の残差 (誤差) を次の木が学ぶように、浅い木を順に足していく手法。 [003-A](src/003-A-gradient-boosting/README.md))
- [x] XGBoost (学習率、深さ、早期打ち切り) (正則化と高速化の工夫を入れた勾配ブースティングの実装。 [003-A](src/003-A-gradient-boosting/README.md), [003-B](src/003-B-xgboost/README.md))
- [x] LightGBM (特徴量をヒストグラムにまとめ、葉ごとに木を伸ばして速く学習する勾配ブースティングの実装。 [003-A](src/003-A-gradient-boosting/README.md))
- [x] CatBoost (カテゴリ変数をそのまま扱え、左右対称な木を使う勾配ブースティングの実装。 [003-A](src/003-A-gradient-boosting/README.md), [003-E](src/003-E-pooled-target/README.md))

### 評価設計

データリークを防ぐ

- [x] K-fold / 層化 K-fold (StratifiedKFold) (データを K 個に分け、1 つを試験、残りを学習に使うことを K 回繰り返して評価する方法。層化はクラスの割合を各分割で揃える。 [001-B](src/001-B-logistic-regression/README.md), [004-A](src/004-A-cross-validation/README.md))
- [x] Group CV / 空間ブロック CV (GroupKFold でブロックを作った) (同じグループ (近い場所) の行が学習と試験の両方に入らないように、グループ単位で分けて評価する方法。 [004-A](src/004-A-cross-validation/README.md), [004-C](src/004-C-small-areas/README.md))
- [ ] verde の BlockKFold (座標を四角いブロックに区切り、ブロック単位で分ける空間交差検証の実装。)
- [x] 時間で分ける (過去で学習、未来で試す) (過去のデータで学習して未来のデータで試し、実際に使うときと同じ条件で評価する方法。 [004-B](src/004-B-data-leakage/README.md))
- [ ] TimeSeriesSplit (学習の期間を少しずつ延ばしながら、その直後の期間で試すことを繰り返す時系列の交差検証。)
- [x] データリーク (target encoding、答えの言い換え) (本番では使えない答えの情報が特徴量や学習に紛れ込み、評価が実力より良く見えること。 [001-B](src/001-B-logistic-regression/README.md), [004-B](src/004-B-data-leakage/README.md))
- [x] out-of-fold 予測をまとめて採点 (各行を、その行を学習に使わなかったモデルで予測し、全行の予測をまとめて 1 回で採点する方法。 [004-A](src/004-A-cross-validation/README.md))
- [x] 目的変数の雑音の天井 (目的変数そのものに含まれる雑音のために、どんなモデルでも超えられない点数の上限。 [003-C](src/003-C-noise-ceiling/README.md))

### クラスタリング

教師なしで構造を見つける

- [x] k-means、シルエット (データを k 個の塊に分け、各点を最も近い塊の中心に割り当てることを繰り返す手法。シルエットは塊の分かれ具合の指標。 [005-A](src/005-A-k-means/README.md), [005-C](src/005-C-grid-types/README.md))
- [x] DBSCAN、k 距離グラフ (半径 eps の中に点が十分ある所を密な塊としてつなぎ、どこにも入らない点を外れ値とする手法。k 距離グラフは eps の目安を探す図。 [005-B](src/005-B-dbscan/README.md))
- [x] HDBSCAN (eps を 1 つに決めず、密度の階層から安定して残る塊を選ぶ DBSCAN の拡張。 [005-B](src/005-B-dbscan/README.md))
- [x] ディリクレ過程混合 (DPMM、BayesianGaussianMixture) (塊の数を事前に固定せず、データに合わせて必要な数だけ正規分布を使う混合モデル。 [005-D](src/005-D-dpmm/README.md))
- [x] MAUP (集計単位で結果が変わる) (同じデータでも、集計する区画の大きさや区切り方を変えると分析の結果が変わる問題。 [005-C](src/005-C-grid-types/README.md))

### 次元削減

高次元データをどう圧縮するか

- [x] PCA (データのばらつきが最も大きい向きから順に新しい軸 (主成分) を取り、少ない軸で要約する次元削減の手法。 [006-A](src/006-A-pca/README.md), [006-B](src/006-B-pca-wards/README.md))
- [x] 並行分析、ブートストラップ (残す主成分の数) (乱数のデータの固有値と比べたり、データを復元抽出し直して軸の安定性を見たりして、残す主成分の数を決める方法。 [006-A](src/006-A-pca/README.md))

### 異常検知

「普通から外れる」とは何か

- [ ] Isolation Forest (無作為な分割を繰り返し、少ない回数で孤立する点ほど異常とみなす異常検知の手法。)
- [ ] LOF (Local Outlier Factor) (近所の点と比べて周りの密度が低い点ほど異常とみなす異常検知の手法。)

### 時系列

時間順序、未来情報リーク

- [ ] ARIMA / ETS (過去の値と誤差の自己相関 (ARIMA) や、水準、傾向、季節の指数平滑 (ETS) で、時系列の先を予測する統計モデル。)
- [ ] lag 特徴 + GBDT (過去の時点の値 (ラグ) を特徴量にして、時系列の予測を勾配ブースティングの回帰として解く方法。)

### 確率・不確実性

「当たる」以外に「どれくらい信用できるか」

- [x] 較正 (calibration): Platt、isotonic、ECE、Brier、信頼度曲線 (予測した確率が、実際にその割合で当たるように合わせること。Platt はシグモイド、isotonic は単調な階段で合わせ、ECE、Brier、信頼度曲線で合い具合を測る。 [011-B](src/011-B-calibration/README.md))
- [ ] 予測区間 (prediction interval) (1 つの値ではなく、本当の値が一定の確率で入る範囲を予測すること。)

### 説明可能性

モデルが何を根拠にしているか

- [x] permutation importance (1 つの特徴量の値をシャッフルしたとき、点数がどれだけ下がるかで、その特徴量の重要度を測る方法。 [011-A](src/011-A-shap/README.md))
- [x] SHAP (TreeExplainer) (1 件ごとの予測を、各特徴量の寄与の足し算に分ける説明の手法 (協力ゲームのシャープレイ値に基づく)。 [011-A](src/011-A-shap/README.md))

### 線形最適化

制約付きで最良解を選ぶ

- [x] LP、LP 緩和 (線形の制約のもとで線形の目的を最大 (最小) にする最適化。LP 緩和は、整数の変数を連続値に緩めて LP として解くこと。 [008-A](src/008-A-lp/README.md))
- [x] 双対価格 (制約を 1 単位緩めたとき、目的の値がどれだけ良くなるかを表す値。 [008-A](src/008-A-lp/README.md))
- [x] 内点法 (制約の境界ではなく実行可能な領域の内側を通って、LP の最適解に近づく解法。 [008-B](src/008-B-milp/README.md))

### 整数最適化

選ぶ/選ばない、配置、割当

- [x] MILP (最大被覆) (一部の変数を整数 (0 か 1 など) に限った線形最適化。最大被覆は、k か所を選んで覆う人の数を最大にする問題。 [008-B](src/008-B-milp/README.md))
- [x] 欲張り法と LP の上限による保証 (その時点で最も得な選択を順に取る近似解法と、LP 緩和の値 (最適値の上限) を比べて、最適からどれだけ離れうるかを示すこと。 [008-B](src/008-B-milp/README.md))
- [x] p-median、交換法 (Teitz-Bart) (p か所の施設を選び、需要から最寄りの施設までの距離の合計を最小にする問題。交換法は、選んだ施設を 1 つずつ入れ替えて改善していく近似解法。 [009-B](src/009-B-facility-location/README.md))

### グラフ

経路・ネットワーク問題

- [x] Dijkstra (多始点) (始点から近い順にノードの最短距離を確定していく最短経路の手法。多始点は、複数の始点をまとめて 1 回で探す。 [007-A](src/007-A-dijkstra/README.md))
- [x] A* (ゴールまでの距離の見積もりを足して有望な方向から探し、Dijkstra より少ない探索で最短経路を見つける手法。 [007-B](src/007-B-a-star/README.md))
- [x] 二部グラフの最大マッチング (2 つのグループの間で、同じ点を 2 度使わずに結べる組の数を最大にする問題。 [010-A](src/010-A-cp-sat/README.md))
- [ ] min-cost flow (容量と費用のあるネットワークで、必要な量を最小の費用で流す問題。輸送問題は LP で解いた。)

### 組合せ最適化

探索空間が爆発する問題

- [ ] knapsack (重さの上限の中で、価値の合計が最大になるように品物を選ぶ問題。)
- [x] assignment (輸送問題、ハンガリアン法) (人と仕事のように 2 つの集まりを組み合わせ、費用の合計を最小にする割当の問題。ハンガリアン法はその厳密な解法。 [009-A](src/009-A-assignment/README.md))
- [ ] TSP (すべての地点を 1 回ずつ回って出発点に戻る、最短の巡回路を求める問題 (巡回セールスマン問題)。)
- [ ] VRP (複数の車両で、容量や時間の制約を守りながら、すべての客を回る最短の経路を求める問題 (配送計画問題)。)

### 制約充足

勤務表、スケジューリング

- [x] CP-SAT (変数の取りうる値と制約を書くと、制約伝播と SAT ソルバーの探索で解を見つける OR-Tools の制約ソルバー。 [010-A](src/010-A-cp-sat/README.md))
- [x] 区間変数と NoOverlap、対称性の除去 (開始と長さを持つ区間を変数にし、NoOverlap で同じ資源の区間が重ならないようにする。対称性の除去は、入れ替えても同じになる解を 1 つに絞って探索を減らすこと。 [010-B](src/010-B-scheduling/README.md))

### 多目的意思決定

「最適」が一つではない問題

- [x] 重み付き和 (weighted sum) (複数の目的に重みを掛けて足し、1 つの目的にして解く多目的最適化の方法。 [012-A](src/012-A-multi-objective-optimization/README.md))
- [x] パレートフロンティア、ε 制約法 (どの目的も同時には改善できない解 (パレート解) の集まり。ε 制約法は、1 つの目的だけを残し、ほかを上限の制約にして解くことを繰り返して、パレート解を並べる方法。 [012-B](src/012-B-epsilon-constraint/README.md))

## ステップごとの記録

`src/NNN-X-topic/` に、ステップ NNN の X 番目の実験を置く。A、B、C は実験の順番。各ディレクトリの `README.md` に数字と図の説明、`run.py` にコードがある。図と実行の記録は `output/` に書く (git には入れない)。

### 1. 線形回帰 / ロジスティック回帰

- 001-A 線形回帰 ([README](src/001-A-linear-regression/README.md), [run.py](src/001-A-linear-regression/run.py)): 町丁目の人口密度を建物と POI から。23 区で係数が違って見えたのは、住む人が 0 人の小地域のせいだった。
- 001-B ロジスティック回帰 ([README](src/001-B-logistic-regression/README.md), [run.py](src/001-B-logistic-regression/run.py)): 無電柱化の分類。電柱の数を入れると答えの言い換えになり、精度は偏った答えでも高く出るのであてにならない。

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

### 4. 交差検証とデータリーク

- 004-A 分け方 ([README](src/004-A-cross-validation/README.md), [run.py](src/004-A-cross-validation/run.py)): 台東区では空間ブロックで点数がはっきり下がり、23 区ではほとんど下がらない。
- 004-B データリーク ([README](src/004-B-data-leakage/README.md), [run.py](src/004-B-data-leakage/run.py)): target encoding の漏れはランダム分割では見抜けない。撮影年の漏れは小さい。
- 004-C 範囲の小ささ ([README](src/004-C-small-areas/README.md), [run.py](src/004-C-small-areas/run.py)): 空間 CV で点数が下がるのはどの区でも同じで、ブロックの少ない区ほど大きい。

### 5. k-means / DBSCAN (と DPMM)

- 005-A k-means ([README](src/005-A-k-means/README.md), [run.py](src/005-A-k-means/run.py)): 町丁目を「街の型」に分けると、台東区は 4 型。ただし塊ははっきりしない。
- 005-B DBSCAN と HDBSCAN ([README](src/005-B-dbscan/README.md), [run.py](src/005-B-dbscan/run.py)): POI の点は台東区では区全体が連鎖する。eps を固定すると、塊に入る割合は区の密度でほぼ決まる。
- 005-C 1km メッシュの型 ([README](src/005-C-grid-types/README.md), [run.py](src/005-C-grid-types/run.py)): 23 区の大きな構造は見えるが、台東区の小さな地区の型は消える (MAUP)。
- 005-D ディリクレ過程混合 ([README](src/005-D-dpmm/README.md), [run.py](src/005-D-dpmm/run.py)): k を決めなくてよくはならない。型の数を決めていたのは共分散の事前分布だった。

### 6. PCA

- 006-A 台東区 ([README](src/006-A-pca/README.md), [run.py](src/006-A-pca/run.py)): みちよみの 12 の数値から、PC1 は電柱と無電柱化、PC2 は道の広さと細さ。残すのは 2 つ。
- 006-B 23 区 ([README](src/006-B-pca-wards/README.md), [run.py](src/006-B-pca-wards/run.py)): PC1 は台東区と同じ向き。台東区の軸は平面の中で約 45 度回っていたので、主成分は平面で比べる。

### 7. Dijkstra / A*

- 007-A Dijkstra ([README](src/007-A-dijkstra/README.md), [run.py](src/007-A-dijkstra/run.py)): 町丁目から最寄りの病院と避難場所まで歩く距離。多始点にすると 1 回で済み、38 倍速い。
- 007-B A* ([README](src/007-B-a-star/README.md), [run.py](src/007-B-a-star/run.py)): 確定するノードは Dijkstra の 1/10 だが、増え方は同じ。遠回りの原因は道の無い帯 (大学の区画、線路、隅田川)。

### 8. LP / MILP

- 008-A LP ([README](src/008-A-lp/README.md), [run.py](src/008-A-lp/run.py)): 最大被覆の LP 緩和。拠点が少ないうちは LP の解がそのまま整数。双対価格が拠点 1 つの価値を人数で表す。
- 008-B MILP ([README](src/008-B-milp/README.md), [run.py](src/008-B-milp/run.py)): 台東区は分枝なしで解ける。23 区では需要をまとめて内点法で解き、全候補地では欲張り法と LP の上限で約 1% の保証を出した。

### 9. 割当 / 施設配置

- 009-A 割当 ([README](src/009-A-assignment/README.md), [run.py](src/009-A-assignment/run.py)): 容量のある避難場所への割当。輸送問題の LP は自動的に整数で、ハンガリアン法と一致する。荒川の氾濫時は実行不可能。
- 009-B p-median ([README](src/009-B-facility-location/README.md), [run.py](src/009-B-facility-location/run.py)): 交換法でほぼ最適。同じ数の拠点でも、p-median と最大被覆では選ぶ場所がまったく違う。

### 10. CP-SAT / スケジューリング

- 010-A 車両の最少台数 ([README](src/010-A-cp-sat/README.md), [run.py](src/010-A-cp-sat/run.py)): GTFS の便から CP-SAT で。二部グラフの最大マッチングと一致する。
- 010-B 乗務員の勤務 ([README](src/010-B-scheduling/README.md), [run.py](src/010-B-scheduling/run.py)): 区間変数と NoOverlap で。最初のモデルは誤って「最適」と答え、手で組んだ解で気づいた。

### 11. SHAP / 較正

- 011-A SHAP ([README](src/011-A-shap/README.md), [run.py](src/011-A-shap/run.py)): 無電柱化の XGBoost を説明した。上位 3 つは 3 つの重要度で一致。街灯の数には電柱の代わりという漏れの疑い。
- 011-B 較正 ([README](src/011-B-calibration/README.md), [run.py](src/011-B-calibration/run.py)): ランダムフォレストはそのままでよく較正されていた。isotonic はどれも改善し、Platt は木のモデルを悪くした。

### 12. 多目的最適化

- 012-A 重み付き和 ([README](src/012-A-multi-objective-optimization/README.md), [run.py](src/012-A-multi-objective-optimization/run.py)): 最大被覆に拠点の数と浸水を足した。候補地の 89% が浸水区域にあり、重みを振っても中間の解がほとんど出ない。
- 012-B ε 制約法 ([README](src/012-B-epsilon-constraint/README.md), [run.py](src/012-B-epsilon-constraint/run.py)): 34 のパレート解を出した。重み付き和はそのうち 11 しか出さない (凸包の上だけ)。
