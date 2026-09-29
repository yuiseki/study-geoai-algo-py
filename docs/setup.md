# 共通の下ごしらえ

全ステップに共通する、範囲、データの読み方、分析の単位、評価と実行の決まり、共通のコード。各ステップの記録は [README](../README.md) にある。

## 2 つの範囲の役割

- A 台東区: 小さく速く回し、結果を地図で目で確かめる。ほぼすべてのステップを台東区で動かした。
- B 東京 23 区: 規模を上げ、ほかの場所でも通用するかを試す。1〜4 番、005-A〜D、006-B、008-B で使った。通信速度 (3 番) は台東区ではタイルが 62 枚しかないので、23 区が主。
- 4 番で「22 区で学習して台東区で試す」評価をし、004-C で「台東区だけ点数が大きく下がるのは範囲が小さいから」を 23 区すべてで確かめた。
- 23 区に広げると重くなるもの (7 番の Python の Dijkstra を 2 万回、10 番の都営バス) は行っていない。

## 読み方

- 切り出した結果はリポジトリに保存しない。実行時に、元の出どころから Range 要求で必要な行と列だけを読み、DuckDB (1.5.5 以上) のインメモリ DB で扱う。
- 何度も読むと遅いものは、OS の一時ディレクトリ `/tmp/study-geoai/` にキャッシュする。キャッシュの名前には出どころの版 (コミットやリリース) を入れる。書きかけのファイルは `.partial` にしておき、失敗したら残さない (`aoi.writing`)。
- Range 要求で部分読みできない出どころは、一度だけ取得して、Range で読める形に直して z.yuiseki.net/static/ に置き、そこから読む。置く前に再配布できるかを確かめ、置いた場所の README と LICENSE に出典と取得日を書く。
- 再配布できないものは置かない。国土数値情報の N13 道路データは、元資料に「複製には国土地理院長の承認が要る」とあるので置いていない (実行時に取得してキャッシュする扱い。今回は使わなかった)。同じ元データの道路中心線は、国土地理院の最適化ベクトルタイル (PMTiles、Range 可) で読める ([gsi-optimal-bvmap](datasets/gsi-optimal-bvmap/README.md))。
- 範囲は `study_geoai.aoi.load("taito")` と `load("tokyo23")` で取る。境界と人口は jp-admin-2026-09 をコミットで固定して読む。

## 使った出どころ

データの詳細は [datasets/](datasets/README.md) にある。

- 小地域の境界と人口: [estat-boundary-2020](datasets/huggingface-yuiseki/estat-boundary-2020.md)。Hugging Face、コミット固定。1, 4, 005-A, 7, 9 番
- 区の境界と人口: [jp-admin-2026-09](datasets/huggingface-yuiseki/jp-admin-2026-09.md)。Hugging Face、コミット固定。すべて
- 建物、POI: [Overture Maps](datasets/stac/overture-maps.md) 2026-09-23.1。S3 の GeoParquet、STAC でファイルを絞る。1〜5 番
- 歩行者の道路網: [osm-tokyo23-src-2026-08](datasets/huggingface-yuiseki/osm-tokyo23-src-2026-08.md) の `line` 表。形の列が 9 割で範囲では飛ばせないので、全体 (26MB) を読んで範囲ごとにキャッシュ。7〜9, 12 番
- 街路の状態: [みちよみ](datasets/michiyomi/README.md)。Hugging Face、区ごとにキャッシュ。1〜6, 11 番
- 人口グリッド: [WorldPop](datasets/stac/worldpop.md) R2025A。元のサーバーは Range が効かないので、COG にして z.yuiseki.net/static/worldpop/ にミラー。3, 005-C, 8, 12 番
- 携帯の通信速度: [Ookla Speedtest](datasets/ookla-speedtest/README.md) mobile の 3 四半期。z.yuiseki.net/static/ookla/ にミラー (CC BY-NC-SA 4.0)。3 番
- 基地局: [OpenCelliD](datasets/opencellid/README.md) (source.coop smartmaps の PMTiles)。ogr2ogr で範囲だけ読む。003-D, 003-E
- 医療機関、学校、洪水浸水想定: [国土数値情報](datasets/stac/mlit-nlftp.md) P04、P29、A31a。z.yuiseki.net/static/ksj/ にミラー (GeoParquet)。将来人口 mesh500r6 もミラーしたが、どのステップでも使っていない。7〜9, 12 番
- 避難場所: [tokyo-ckan](datasets/stac/tokyo-ckan.md) の指定緊急避難場所一覧。z.yuiseki.net/static/tokyo-ckan-files/ にミラー。7, 9 番
- バスの時刻表: [台東区めぐりん GTFS](datasets/odpt-taito-megurin/README.md)、[荒川区さくら GTFS](datasets/tokyo-gtfs/README.md)。z.yuiseki.net/static/gtfs/ にミラー。10 番

## 気をつけること (やりながら見つかったもの)

- estat-boundary-2020 の `KEY_CODE` は一意ではない。PREF + CITY + S_AREA で 11 桁のキーを作り直す。
- osm-tokyo23-src の `roads` 表は道路網ではない。`line` 表の highway がある行を使う。`line` 表には交差点の ID が無いので、道どうしが共有する頂点を交差点としてつなぎ直した (99% のノードが 1 つにつながった)。
- みちよみの `analysis` は VLM の推定。`confidence` では絞らず、隔離 (quarantined) されたシーンだけを除いて使った。目的変数 (無電柱化) も同じ VLM の読みなので、「当たる」は「VLM の読みと合う」という意味。
- みちよみの `cell_250m` の ID の作り方は説明に無い。「行 x 100000 + 列、南西の角が北緯 20 + 行 x 0.00225 度、東経 120 + 列 x 0.00275 度」と読み取った ([michiyomi.cell_bounds](../src/study_geoai/michiyomi.py))。
- anaconda の `GDAL_DATA` などの環境変数が rasterio の GDAL を壊す。[study_geoai/\_\_init\_\_.py](../src/study_geoai/__init__.py) で外している。
- DuckDB は座標系の名前が違うジオメトリ (EPSG:4326 と OGC:CRS84) を比べられない。点は座標系なしで作る。
- z.yuiseki.net の Cloudflare は、初回の Range 要求に 200 を返すことがあり、512MB を超えるファイルをキャッシュせず、Python-urllib の User-Agent を拒む。大きなファイルは 512MB 未満に分け、User-Agent を付ける。
- ライセンスはデータごとに違う。Ookla は CC BY-NC-SA 4.0 (非営利)、みちよみは CC BY-SA 4.0 (Mapillary、国土数値情報、東京都建設局の出典が要る)、OSM と Overture の一部は ODbL。各ステップの README の末尾に出典を書いた。

## 分析の単位

- 小地域 (町丁目): 人口がそのまま付いている。面積がばらばら。1, 4, 005-A, 7, 9 番
- みちよみのシーン: 写真 1 枚。1, 2, 003-B, 4, 11 番
- 250m 格子 (`cell_250m`): みちよみと揃う。面積が一定。4 番の groups、6, 11 番の地図
- 1km (3 次メッシュ): 日本の標準地域メッシュ (`study_geoai.mesh`)。005-C, 005-D
- Ookla のタイル: ズーム 16、約 610m 四方。3 番
- WorldPop の 100m 格子: 需要の点。8, 12 番
- POI の点、道路網のノード: メートル座標 (平面直角座標系 IX 系、EPSG:6677)。005-B, 7〜9, 12 番

## 評価と実行の決まり (やりながら決めたもの)

- 交差検証の点数は、分割ごとの点数を平均せず、分割の外の予測 (out of fold) をまとめて 1 回で測る。分割ごとの平均は、ばらつきの小さい 1 つの分割に振り回された (002-A)。
- 通信速度のタイルは、測定回数で重み付けして採点する。分割の切り方 (乱数の種) を変えて、点数のばらつきも見る。モデルの間の差と同じくらい動く (003-E)。
- 目的変数そのものの雑音の天井 (同じタイルの別の四半期との一致) を先に測る (003-C)。
- 重い処理は `systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0` で囲む (母艦には swap が無く、メモリが尽きると機械ごと止まる)。DuckDB の上限 (4GB) は scikit-learn には効かない。
- 数分以上かかる処理は `python -u` で裏で流し、Monitor で進み具合と終わりを確かめる。
- ソルバーが「最適」と答えても、手で組める解や下限と突き合わせる (010-B でモデルの誤りを見つけた)。

## 共通のコード ([src/study_geoai/](../src/study_geoai/))

- [aoi](../src/study_geoai/aoi.py), [db](../src/study_geoai/db.py): 範囲、キャッシュ、DuckDB の接続 (上限つき)
- [census](../src/study_geoai/census.py), [overture](../src/study_geoai/overture.py), [michiyomi](../src/study_geoai/michiyomi.py), [worldpop](../src/study_geoai/worldpop.py), [ookla](../src/study_geoai/ookla.py), [opencellid](../src/study_geoai/opencellid.py), [ksj](../src/study_geoai/ksj.py), [ckan](../src/study_geoai/ckan.py), [geocode](../src/study_geoai/geocode.py), [gtfs](../src/study_geoai/gtfs.py), [osm](../src/study_geoai/osm.py): 出どころごとの読み込み
- [features](../src/study_geoai/features.py), [mesh](../src/study_geoai/mesh.py), [tasks](../src/study_geoai/tasks.py): 特徴量 (小地域、タイル、1km メッシュ、250m 格子、POI の点)、3 次メッシュ、1〜4 番の課題
- [graph](../src/study_geoai/graph.py): 自前の Dijkstra と A* (確定したノードを数える、打ち切り、多始点)
- [cover](../src/study_geoai/cover.py): 最大被覆 (LP、MILP、欲張り法、需要の行をまとめる、多目的)
- [facility](../src/study_geoai/facility.py): 輸送問題、ハンガリアン法、p-median、交換法
- [schedule](../src/study_geoai/schedule.py): GTFS の便、車両の最少台数、乗務員の勤務 (CP-SAT)
- [plot](../src/study_geoai/plot.py): matplotlib だけで塗り分け地図

z.yuiseki.net へのミラーを作るスクリプトは [scripts/](../scripts/) にある。

## highspy は ortools の中の HiGHS に合わせて固定する

ortools は自前の `libhighs.so.1` を同梱していて、highspy のものと soname が同じ。先に import されたほうが両方で使われるので、版が合わないともう一方が `undefined symbol` で落ちる。ortools 9.15 は HiGHS 1.12.0 を同梱しているので、highspy は `>=1.12,<1.13` に固定している。ortools を上げるときは、同梱の版を確かめて highspy も合わせる。

```sh
strings .venv/lib/python3.12/site-packages/ortools/.libs/libhighs.so.1 | grep -xE '1\.[0-9]+\.[0-9]+'
```

[tests/test_env.py](../tests/test_env.py) の `test_ortools_and_highspy_share_one_process` が、両方の import の順を確かめている。
