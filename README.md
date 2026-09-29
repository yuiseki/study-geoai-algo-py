# study-geoai

Study environment for classical machine learning and mathematical optimisation, managed with uv.

12 ステップのアルゴリズムを、台東区と東京 23 区の実データで一通り動かした記録。最初に立てた計画から、やりながら変えたところが多いので、このページは「実際に行ったこと」を正として書き直した (2026-09-29)。各ステップの数字と図は `src/NNN-X-*/README.md` にある。データは [docs/datasets/](docs/datasets/README.md) で確かめたもの。

目的はアルゴリズムを一通り押さえることで、題材を掘り下げることではない。各ステップは、そのアルゴリズムの要点が見える 2 つほどの実験で終え、広げる案は「行わなかったこと」に残した。

| Library | Use |
| --- | --- |
| scikit-learn | General ML |
| xgboost | Gradient boosting |
| lightgbm | Gradient boosting |
| catboost | Gradient boosting |
| statsmodels | Time series (ARIMA/ETS) and statistics |
| shap | Model explanation |
| verde | Spatial block cross-validation (BlockKFold) |
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

## 2 つの範囲の役割

| | A 台東区 | B 東京 23 区 |
|---|---|---|
| 目的 | 小さく速く回し、結果を地図で目で確かめる | 規模を上げ、ほかの場所でも通用するかを試す |
| 実際 | ほぼすべてのステップを台東区で動かした | 1〜4 番、5-A〜D、6-B、8-B で使った。通信速度 (3 番) は台東区ではタイルが 62 枚しかないので、23 区が主 |

- 4 番で「22 区で学習して台東区で試す」評価をし、4-C で「台東区だけ点数が大きく下がるのは範囲が小さいから」を 23 区すべてで確かめた。
- 23 区に広げると重くなるもの (7 番の Python の Dijkstra を 2 万回、10 番の都営バス) は行っていない。

## 0. 共通の下ごしらえ

### 読み方

- 切り出した結果はリポジトリに保存しない。実行時に、元の出どころから Range 要求で必要な行と列だけを読み、DuckDB (1.5.5 以上) のインメモリ DB で扱う。
- 何度も読むと遅いものは、OS の一時ディレクトリ `/tmp/study-geoai/` にキャッシュする。キャッシュの名前には出どころの版 (コミットやリリース) を入れる。書きかけのファイルは `.partial` にしておき、失敗したら残さない (`aoi.writing`)。
- Range 要求で部分読みできない出どころは、一度だけ取得して、Range で読める形に直して z.yuiseki.net/static/ に置き、そこから読む。置く前に再配布できるかを確かめ、置いた場所の README と LICENSE に出典と取得日を書く。
- 再配布できないものは置かない。国土数値情報の N13 道路データは、元資料に「複製には国土地理院長の承認が要る」とあるので置いていない (実行時に取得してキャッシュする扱い。今回は使わなかった)。同じ元データの道路中心線は、国土地理院の最適化ベクトルタイル (PMTiles、Range 可) で読める ([gsi-optimal-bvmap](docs/datasets/gsi-optimal-bvmap/README.md))。
- 範囲は `study_geoai.aoi.load("taito")` と `load("tokyo23")` で取る。境界と人口は jp-admin-2026-09 をコミットで固定して読む。

### 使った出どころ

| 切り出すもの | 出どころ | 読み方 | 使ったステップ |
|---|---|---|---|
| 小地域の境界と人口 | [estat-boundary-2020](docs/datasets/huggingface-yuiseki/estat-boundary-2020.md) | Hugging Face、コミット固定 | 1, 4, 5-A, 7, 9 |
| 区の境界と人口 | [jp-admin-2026-09](docs/datasets/huggingface-yuiseki/jp-admin-2026-09.md) | Hugging Face、コミット固定 | すべて |
| 建物、POI | [Overture Maps](docs/datasets/stac/overture-maps.md) 2026-09-23.1 | S3 の GeoParquet、STAC でファイルを絞る | 1〜5 |
| 歩行者の道路網 | [osm-tokyo23-src-2026-08](docs/datasets/huggingface-yuiseki/osm-tokyo23-src-2026-08.md) の `line` 表 | Hugging Face。形の列が 9 割で範囲では飛ばせないので、全体 (26MB) を読んで範囲ごとにキャッシュ | 7〜9, 12 |
| 街路の状態 | [みちよみ](docs/datasets/michiyomi/README.md) | Hugging Face、区ごとにキャッシュ | 1〜6, 11 |
| 人口グリッド | [WorldPop](docs/datasets/stac/worldpop.md) R2025A | 元のサーバーは Range が効かないので、COG にして z.yuiseki.net/static/worldpop/ にミラー | 3, 5-C, 8, 12 |
| 携帯の通信速度 | [Ookla Speedtest](docs/datasets/ookla-speedtest/README.md) mobile の 3 四半期 | z.yuiseki.net/static/ookla/ にミラー (CC BY-NC-SA 4.0) | 3 |
| 基地局 | [OpenCelliD](docs/datasets/opencellid/README.md) (source.coop smartmaps の PMTiles) | ogr2ogr で範囲だけ読む | 3-D, 3-E |
| 医療機関、学校、洪水浸水想定 | [国土数値情報](docs/datasets/stac/mlit-nlftp.md) P04、P29、A31a | z.yuiseki.net/static/ksj/ にミラー (GeoParquet)。将来人口 mesh500r6 もミラーしたが、どのステップでも使っていない | 7〜9, 12 |
| 避難場所 | [tokyo-ckan](docs/datasets/stac/tokyo-ckan.md) の指定緊急避難場所一覧 | z.yuiseki.net/static/tokyo-ckan-files/ にミラー | 7, 9 |
| バスの時刻表 | [台東区めぐりん GTFS](docs/datasets/odpt-taito-megurin/README.md)、[荒川区さくら GTFS](docs/datasets/tokyo-gtfs/README.md) | z.yuiseki.net/static/gtfs/ にミラー | 10 |

### 下ごしらえで気をつけること (やりながら見つかったもの)

- estat-boundary-2020 の `KEY_CODE` は一意ではない。PREF + CITY + S_AREA で 11 桁のキーを作り直す。
- osm-tokyo23-src の `roads` 表は道路網ではない。`line` 表の highway がある行を使う。`line` 表には交差点の ID が無いので、道どうしが共有する頂点を交差点としてつなぎ直した (99% のノードが 1 つにつながった)。
- みちよみの `analysis` は VLM の推定。`confidence` では絞らず、隔離 (quarantined) されたシーンだけを除いて使った。目的変数 (無電柱化) も同じ VLM の読みなので、「当たる」は「VLM の読みと合う」という意味。
- みちよみの `cell_250m` の ID の作り方は説明に無い。「行 x 100000 + 列、南西の角が北緯 20 + 行 x 0.00225 度、東経 120 + 列 x 0.00275 度」と読み取った ([michiyomi.cell_bounds](src/study_geoai/michiyomi.py))。
- anaconda の `GDAL_DATA` などの環境変数が rasterio の GDAL を壊す。[study_geoai/__init__.py](src/study_geoai/__init__.py) で外している。
- DuckDB は座標系の名前が違うジオメトリ (EPSG:4326 と OGC:CRS84) を比べられない。点は座標系なしで作る。
- z.yuiseki.net の Cloudflare は、初回の Range 要求に 200 を返すことがあり、512MB を超えるファイルをキャッシュせず、Python-urllib の User-Agent を拒む。大きなファイルは 512MB 未満に分け、User-Agent を付ける。
- ライセンスはデータごとに違う。Ookla は CC BY-NC-SA 4.0 (非営利)、みちよみは CC BY-SA 4.0 (Mapillary、国土数値情報、東京都建設局の出典が要る)、OSM と Overture の一部は ODbL。各ステップの README の末尾に出典を書いた。

### 分析の単位

| 単位 | 中身 | 使ったステップ |
|---|---|---|
| 小地域 (町丁目) | 人口がそのまま付いている。面積がばらばら | 1, 4, 5-A, 7, 9 |
| みちよみのシーン | 写真 1 枚 | 1, 2, 3-B, 4, 11 |
| 250m 格子 (`cell_250m`) | みちよみと揃う。面積が一定 | 4 の groups、6, 11 の地図 |
| 1km (3 次メッシュ) | 日本の標準地域メッシュ (`study_geoai.mesh`) | 5-C, 5-D |
| Ookla のタイル | ズーム 16、約 610m 四方 | 3 |
| WorldPop の 100m 格子 | 需要の点 | 8, 12 |
| POI の点、道路網のノード | メートル座標 (平面直角座標系 IX 系、EPSG:6677) | 5-B, 7〜9, 12 |

### 評価と実行の決まり (やりながら決めたもの)

- 交差検証の点数は、分割ごとの点数を平均せず、分割の外の予測 (out of fold) をまとめて 1 回で測る。分割ごとの平均は、ばらつきの小さい 1 つの分割に振り回された (2-A)。
- 通信速度のタイルは、測定回数で重み付けして採点する。分割の切り方 (乱数の種) を変えて、点数のばらつきも見る。モデルの間の差と同じくらい動く (3-E)。
- 目的変数そのものの雑音の天井 (同じタイルの別の四半期との一致) を先に測る (3-C)。
- 重い処理は `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0` で囲む (母艦には swap が無く、メモリが尽きると機械ごと止まる)。DuckDB の上限 (4GB) は scikit-learn には効かない。
- 数分以上かかる処理は `python -u` で裏で流し、Monitor で進み具合と終わりを確かめる。
- ソルバーが「最適」と答えても、手で組める解や下限と突き合わせる (10-B でモデルの誤りを見つけた)。

### 共通のコード ([src/study_geoai/](src/study_geoai/))

| モジュール | 中身 |
|---|---|
| [aoi](src/study_geoai/aoi.py), [db](src/study_geoai/db.py) | 範囲、キャッシュ、DuckDB の接続 (上限つき) |
| [census](src/study_geoai/census.py), [overture](src/study_geoai/overture.py), [michiyomi](src/study_geoai/michiyomi.py), [worldpop](src/study_geoai/worldpop.py), [ookla](src/study_geoai/ookla.py), [opencellid](src/study_geoai/opencellid.py), [ksj](src/study_geoai/ksj.py), [ckan](src/study_geoai/ckan.py), [geocode](src/study_geoai/geocode.py), [gtfs](src/study_geoai/gtfs.py), [osm](src/study_geoai/osm.py) | 出どころごとの読み込み |
| [features](src/study_geoai/features.py), [mesh](src/study_geoai/mesh.py), [tasks](src/study_geoai/tasks.py) | 特徴量 (小地域、タイル、1km メッシュ、250m 格子、POI の点)、3 次メッシュ、1〜4 番の課題 |
| [graph](src/study_geoai/graph.py) | 自前の Dijkstra と A* (確定したノードを数える、打ち切り、多始点) |
| [cover](src/study_geoai/cover.py) | 最大被覆 (LP、MILP、欲張り法、需要の行をまとめる、多目的) |
| [facility](src/study_geoai/facility.py) | 輸送問題、ハンガリアン法、p-median、交換法 |
| [schedule](src/study_geoai/schedule.py) | GTFS の便、車両の最少台数、乗務員の勤務 (CP-SAT) |
| [plot](src/study_geoai/plot.py) | matplotlib だけで塗り分け地図 |

## ステップごとの記録

### 1. 線形回帰 / ロジスティック回帰

- [1-A](src/001-A-linear-regression/README.md) 線形回帰: 町丁目の人口密度 (対数) を、建物の面積の割合と POI の密度から。台東区で R² 0.36。23 区では係数が大きく違って見えたが、住む人が 0 人の小地域 (78) を除くと、建物の係数は台東区とほぼ同じ (0.450 と 0.438) になった。
- [1-B](src/001-B-logistic-regression/README.md) ロジスティック回帰: みちよみのシーンが無電柱化されているか。道の特徴だけで台東区 AUC 0.849。電柱の数を入れると 0.988 に跳ねる (答えの言い換えという漏れ)。精度は、全部「架空線あり」と答えるだけで 0.884 になるので、あてにならない。
- 計画から変えたこと: Ridge と Lasso は 1-A の中で比べるにとどめた。

### 2. 決定木 / ランダムフォレスト

- [2-A](src/002-A-decision-tree/README.md) 決定木: 深さを変えて過学習を見た。無電柱化では線形より良い (台東区 0.894)。台東区の人口密度 (108 行) では木は線形に負ける。
- [2-B](src/002-B-random-forest/README.md) ランダムフォレスト: どの問題でも 1 本の木より良く、台東区の人口密度でも線形を超えた (R² 0.455)。無電柱化 AUC 0.926。部分依存で、細い道では緑の効き方が違う、という相互作用が見えた。
- 23 区の全 99 万行で森を作ると 16GB に達したので、20 万行の標本にした。

### 3. 勾配ブースティング / XGBoost

- [3-A](src/003-A-gradient-boosting/README.md): 携帯の下り速度 (Ookla、23 区) は、人口、建物、POI、街路の様子からほとんど予測できない (R² 0.1 未満)。ブースティングの 4 つの差も意味がない。
- [3-B](src/003-B-xgboost/README.md) XGBoost: 信号のある無電柱化で、学習率、深さ、早期打ち切りを見た。台東区 AUC 0.930。
- [3-C](src/003-C-noise-ceiling/README.md): 雑音の天井。同じタイルの前の四半期の速度ですら R² 0.15 しか説明できない。目的変数がほとんど雑音。
- [3-D](src/003-D-cell-towers/README.md): 基地局 (OpenCelliD) を足しても、ほとんど良くならない。
- [3-E](src/003-E-pooled-target/README.md): 3 つの四半期を測定回数で重み付けしてまとめた目的変数では、CatBoost が 0.099 から 0.175 に上がった。乱数の種を変えると、点数はモデルの間の差と同じくらい動く。
- 計画から変えたこと: 速度には信号が無かったので、XGBoost の性質は無電柱化で見た。3-C から 3-E は計画に無く、足した実験。

### 4. 交差検証とデータリーク

- [4-A](src/004-A-cross-validation/README.md): 分け方だけを変えた。台東区では空間ブロックで点数がはっきり下がる (無電柱化 0.931 → 0.870、人口密度 0.456 → 0.139)。23 区ではほとんど下がらない。22 区で学習して台東区で試すと、台東区の中だけの空間 CV より良い。
- [4-B](src/004-B-data-leakage/README.md): 近所の答えの平均 (target encoding) をわざと漏らすと、ランダム分割では見抜けず、空間で分けて正直に作ったときだけ役に立たないと分かる。時間 (撮影年) の漏れは小さい。
- [4-C](src/004-C-small-areas/README.md): 台東区だけ大きく下がるのは範囲が小さいからか、を 23 区すべてで確かめた。どの区でも下がり、ブロックの少ない区ほど大きい (スピアマン −0.54、p 0.008)。
- 計画から変えたこと: 4-C は計画に無く、4-A の仮説を確かめるために足した。

### 5. k-means / DBSCAN (と DPMM)

- [5-A](src/005-A-k-means/README.md) k-means: 町丁目を 9 つの特徴量で「街の型」に分けた。台東区は 4 型 (飲食・商業、住宅、宿泊の日本堤・清川、文化・緑の上野公園・谷中)。シルエットは低く、塊ははっきりしない。
- [5-B](src/005-B-dbscan/README.md) DBSCAN と HDBSCAN: Overture の POI の点 (メートル座標)。台東区は eps 50m で区全体が連鎖し、k 距離グラフに折れ目が無い。飲食店だけにすると飲食街が塊になる。23 区で eps を固定すると、塊に入る割合が区の密度でほぼ決まる (スピアマン +0.89)。HDBSCAN は差を縮めるが、中心部を細かく割り、250 倍遅い。
- [5-C](src/005-C-grid-types/README.md): 1km メッシュで「街の型」。23 区の大きな構造は見えるが、台東区の小さな地区の型は 1km の中で混ざって消える (MAUP)。
- [5-D](src/005-D-dpmm/README.md) ディリクレ過程混合 (DPMM): k を決めなくてよくはならない。既定では型の数が上限に比例し、集中度 γ はほとんど効かず、共分散の事前分布が型の数を決めていた。データが増えると型も増える。
- 計画から変えたこと: 5-A は電柱と街灯の点のクラスタリングの予定だったが、町丁目の型に変えた。5-C と 5-D は計画に無く、足した実験。

### 6. PCA

- [6-A](src/006-A-pca/README.md): 台東区の 250m 格子 (173) ごとに、みちよみの 12 の数値を PCA。PC1 (41%) は「電柱と電線」と「無電柱化・ブロック舗装・緑」、PC2 (21%) は「広い通り」と「見通しの悪い細い道」。並行分析とブートストラップで、残すのは 2 つ。標準化しないと撮影の枚数が PC1 を独占する。
- [6-B](src/006-B-pca-wards/README.md): 23 区 (7,152 格子)。PC1 は台東区と同じ向きで、幹線道路が地図に線で出る。台東区の軸は 23 区の PC1-PC2 平面の中で約 45 度回っていた。主成分は 1 本ずつでなく平面で比べる。区の違いは PC1 の分散の 23% だけ。
- 行わなかったこと: WorldPop の年齢構成の PCA。

### 7. Dijkstra / A*

- [7-A](src/007-A-dijkstra/README.md) Dijkstra: OSM の歩行者の道路網 (台東区と周り 1km) で、町丁目から最寄りの病院と避難場所まで。多始点の Dijkstra 1 回で、行き先ごとに回すより 38 倍速い。迂回率の中央値 1.3。
- [7-B](src/007-B-a-star/README.md) A*: 確定するノードは Dijkstra の 1/10 だが、距離の 2 乗で増えるのは同じ。目安を水増しすると探索は経路の近くだけになり、最短から外れる。7-A の遠回りを描くと、直線が道の無い帯 (大学の区画、線路、隅田川) を横切っていた。
- 行わなかったこと: 23 区への拡大、一方通行、道路網どうしの比較 (N13 または最適化ベクトルタイル、OSM、Overture)、道の快適さや浸水を重みにする経路、めぐりんの時刻表つきのグラフ。

### 8. LP / MILP

- [8-A](src/008-A-lp/README.md) LP: 台東区の最大被覆 (WorldPop 100m 格子、医療機関と学校の候補地 566、歩いて 400m) を LP に緩めた。k ≤ 7 では LP の解がそのまま整数、それより上で x = 0.5 の解が出る。双対価格が「拠点 1 つの価値」を人数で表す。LP を丸めるより欲張り法のほうがずっと良い。
- [8-B](src/008-B-milp/README.md) MILP: 台東区は全 k で分枝なしに解け、LP との差は 0.43% 以下。23 区 (直線 400m、候補地 22,693) では LP が先に詰まった。同じ覆われ方の需要をまとめ、LP を内点法で解くと 1 万か所まで解けた。全候補地では、欲張り法と LP の上限で 1% 前後の保証を出した。
- 計画から変えたこと: 23 区の覆う条件は、歩く距離でなく直線距離にした (Python の Dijkstra を 2 万回回すと数十分かかるため)。

### 9. 割当 / 施設配置

- [9-A](src/009-A-assignment/README.md) 割当: 台東区の住民の 1% を、容量のある避難場所 17 か所に。最寄りだと 8 か所が超過。輸送問題の LP で容量を守ると平均 14% 遠くなる。LP の解は自動的に整数 (完全単模)。ハンガリアン法 (人 x 席) と完全に一致。町丁目を分けない MILP は +3.2%。荒川の氾濫時は 3 か所しか開かず、実行不可能。
- [9-B](src/009-B-facility-location/README.md) p-median: LP はどの p でも整数。欲張り法は 3〜7% 悪く、交換法でほぼ最適。同じ 5 か所でも、p-median (平均 666m、400m 以内 15%) と最大被覆 (32%、平均 791m) で選ぶ場所がまったく違う。
- 計画から変えたこと: 需要は人口だけにした (通信の遅さを掛けるのはやめた)。
- 行わなかったこと: 基地局の候補地の評価、23 区で区の境界をまたぐ割当。

### 10. CP-SAT / スケジューリング

- [10-A](src/010-A-cp-sat/README.md): GTFS の便から最少台数を CP-SAT で。二部グラフの最大マッチングと一致。荒川区 2 台、めぐりんは折り返し 3 分で 17 台、0 分で 14 台 (同時に走る便の最大と同じ)。
- [10-B](src/010-B-scheduling/README.md): 乗務員の勤務を、区間変数と NoOverlap で (休憩 30 分、前後 4 時間以内、拘束 9 時間以内)。荒川区 4 人 (最適)、めぐりん 35 人 (下限 33)。最初のモデルは休憩の制約をほかの乗務員の便にもかけていて、荒川区を 5 人と誤って「最適」と答えた。手で組んだ 4 人の解で気づき、回帰テストを足した。
- 行わなかったこと: 都営バス (55,846 便)、葛飾区と杉並区。

### 11. SHAP / 較正

- [11-A](src/011-A-shap/README.md) SHAP: 無電柱化の XGBoost を、分割の外で説明した。足し算で予測に戻り (差 10⁻⁵ 以下)、格子の平均は実際の割合とよく合う (相関 0.88)。上位 3 つ (車道の幅、街灯、緑) は 3 つの重要度で一致。細い道 (公園) と 15m の道が無電柱化の側に効く。街灯の数には電柱の代わりという漏れの疑い。
- [11-B](src/011-B-calibration/README.md) 較正: ロジスティック、ランダムフォレスト、XGBoost。ランダムフォレストはそのままで最もよく較正されていた (ECE 0.004)。XGBoost は同じ AUC で ECE が 3 倍。isotonic はどれも改善し、Platt は木のモデルを悪くした。格子を丸ごと試験に回しても順位は同じ。
- 計画から変えたこと: SHAP の題材を通信速度から無電柱化に変えた (速度はほとんど予測できず、説明するものが無い)。
- 行わなかったこと: みちよみの `confidence` の較正。

### 12. 多目的最適化

- [12-A](src/012-A-multi-objective-optimization/README.md) 重み付き和: 8 番の問題に「拠点の数」と「浸水 (A31a の想定最大規模の浸水深ランク)」を足した。候補地の 89% が浸水区域にあり、浸水しない 63 か所では 22.5% の人しか覆えない。重みを振ると解が飛び、中間の解がほとんど出ない。
- [12-B](src/012-B-epsilon-constraint/README.md) ε 制約法: 拠点 13 か所で、34 のパレート解を出した。重み付き和 (77 通り) はそのうち 11 しか出さない (凸包の上だけ)。重みを 0 にすると、パレート最適でない解も返る。
- 行わなかったこと: 23 区で区ごとのパレートフロンティアを比べること。

## src/ との対応

`src/NNN-X-topic/` に、ステップ NNN の X 番目の実験を置く。A、B、C は実験の順番で、このページの A (台東区)、B (23 区) とは別物。各ディレクトリに `run.py` と、結果を書いた `README.md` がある。図と実行の記録は `output/` に書く (git には入れない)。

| ディレクトリ | 中身 | コード |
|---|---|---|
| [001-A-linear-regression](src/001-A-linear-regression/README.md) | 町丁目の人口密度の線形回帰 | [run.py](src/001-A-linear-regression/run.py) |
| [001-B-logistic-regression](src/001-B-logistic-regression/README.md) | 無電柱化のロジスティック回帰 | [run.py](src/001-B-logistic-regression/run.py) |
| [002-A-decision-tree](src/002-A-decision-tree/README.md) | 決定木の深さと過学習 | [run.py](src/002-A-decision-tree/run.py) |
| [002-B-random-forest](src/002-B-random-forest/README.md) | ランダムフォレストと部分依存 | [run.py](src/002-B-random-forest/run.py) |
| [003-A-gradient-boosting](src/003-A-gradient-boosting/README.md) | 携帯の速度を 5 つのブースティングで | [run.py](src/003-A-gradient-boosting/run.py) |
| [003-B-xgboost](src/003-B-xgboost/README.md) | XGBoost の学習率、深さ、早期打ち切り | [run.py](src/003-B-xgboost/run.py) |
| [003-C-noise-ceiling](src/003-C-noise-ceiling/README.md) | 速度の雑音の天井 | [run.py](src/003-C-noise-ceiling/run.py) |
| [003-D-cell-towers](src/003-D-cell-towers/README.md) | 基地局を特徴量に足す | [run.py](src/003-D-cell-towers/run.py) |
| [003-E-pooled-target](src/003-E-pooled-target/README.md) | 3 四半期をまとめた目的変数 | [run.py](src/003-E-pooled-target/run.py) |
| [004-A-cross-validation](src/004-A-cross-validation/README.md) | 分け方を変えた交差検証 | [run.py](src/004-A-cross-validation/run.py) |
| [004-B-data-leakage](src/004-B-data-leakage/README.md) | target encoding と時間の漏れ | [run.py](src/004-B-data-leakage/run.py) |
| [004-C-small-areas](src/004-C-small-areas/README.md) | 範囲の小ささと空間 CV の下がり方 | [run.py](src/004-C-small-areas/run.py) |
| [005-A-k-means](src/005-A-k-means/README.md) | 町丁目の「街の型」 | [run.py](src/005-A-k-means/run.py) |
| [005-B-dbscan](src/005-B-dbscan/README.md) | POI の DBSCAN と HDBSCAN | [run.py](src/005-B-dbscan/run.py) |
| [005-C-grid-types](src/005-C-grid-types/README.md) | 1km メッシュの「街の型」 | [run.py](src/005-C-grid-types/run.py) |
| [005-D-dpmm](src/005-D-dpmm/README.md) | ディリクレ過程混合 | [run.py](src/005-D-dpmm/run.py) |
| [006-A-pca](src/006-A-pca/README.md) | 台東区の道の PCA | [run.py](src/006-A-pca/run.py) |
| [006-B-pca-wards](src/006-B-pca-wards/README.md) | 23 区の道の PCA | [run.py](src/006-B-pca-wards/run.py) |
| [007-A-dijkstra](src/007-A-dijkstra/README.md) | 病院と避難場所までの歩く距離 | [run.py](src/007-A-dijkstra/run.py) |
| [007-B-a-star](src/007-B-a-star/README.md) | A* と Dijkstra | [run.py](src/007-B-a-star/run.py) |
| [008-A-lp](src/008-A-lp/README.md) | 最大被覆の LP 緩和と双対価格 | [run.py](src/008-A-lp/run.py) |
| [008-B-milp](src/008-B-milp/README.md) | 最大被覆の MILP と 23 区 | [run.py](src/008-B-milp/run.py) |
| [009-A-assignment](src/009-A-assignment/README.md) | 容量つきの避難場所への割当 | [run.py](src/009-A-assignment/run.py) |
| [009-B-facility-location](src/009-B-facility-location/README.md) | p-median と最大被覆 | [run.py](src/009-B-facility-location/run.py) |
| [010-A-cp-sat](src/010-A-cp-sat/README.md) | バスの最少台数 | [run.py](src/010-A-cp-sat/run.py) |
| [010-B-scheduling](src/010-B-scheduling/README.md) | 乗務員の勤務 | [run.py](src/010-B-scheduling/run.py) |
| [011-A-shap](src/011-A-shap/README.md) | 無電柱化の分類器の SHAP | [run.py](src/011-A-shap/run.py) |
| [011-B-calibration](src/011-B-calibration/README.md) | 3 つの分類器の較正 | [run.py](src/011-B-calibration/run.py) |
| [012-A-multi-objective-optimization](src/012-A-multi-objective-optimization/README.md) | 3 つの目的の重み付き和 | [run.py](src/012-A-multi-objective-optimization/run.py) |
| [012-B-epsilon-constraint](src/012-B-epsilon-constraint/README.md) | ε 制約法と重み付き和 | [run.py](src/012-B-epsilon-constraint/run.py) |

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

[tests/test_env.py](tests/test_env.py) の `test_ortools_and_highspy_share_one_process` checks both import orders.
