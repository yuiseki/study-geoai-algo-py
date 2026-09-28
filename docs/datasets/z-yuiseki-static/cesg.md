# z.yuiseki.net/static/cesg/

実測日 2026-09-28。`https://z.yuiseki.net/static/cesg/` の下は `tokyo/` だけで、7 ファイルある。HEAD、範囲要求、DuckDB 1.5.5 で読んで確かめた内容。

## 何のための一式か

CESG は、yuiseki の 2 つの PoC がクラウドでもエッジでも同じ形で動かすために置いている、配布用のデータ一式。ビルド元のリポジトリ (手元の `repos/__yuiseki/_poc/` にある) の README に、起動時にここからダウンロードすると書かれている。

- POI 検索: [poc-cesg-poi-search](https://github.com/yuiseki/poc-cesg-poi-search)。Overture Places から検索用の文書と DuckDB の全文検索索引を作り、FastAPI で返す。
- 経路検索: [poc-cesg-route-search](https://github.com/yuiseki/poc-cesg-route-search)。Valhalla の経路タイルを tar で配り、Knative の起動時に取得する。

CESG の略は README によって違う。poi-search は Cloud-Edge Symmetric Geospatial、route-search は Cloud-Native Geospatial と書いている。

ファイル同士の関係:

```
overture-places.parquet (Overture Places 2026-04-15.0 の切り出し, 450,302 行)
  -> poi-documents.parquet (検索用に整形, 450,295 行)
    -> poi-search.duckdb (同じ表 + FTS 索引)
  poi-search-manifest.json (上の 2 つを説明する)

valhalla_tiles.tar (Valhalla 経路タイル, 関東の OSM から)
  valhalla.json (それを読む Valhalla の設定)

input.parquet (5 行の手書きの見本。上のどれとも直接はつながっていない)
```

| ファイル | 大きさ (Content-Length) | Last-Modified | 中身 |
|---|---:|---|---|
| input.parquet | 4,403 | 2026-05-09 03:48:38 GMT | 5 行の見本 POI |
| overture-places.parquet | 84,729,012 | 2026-05-09 03:48:38 GMT | Overture Places の bbox 切り出し |
| poi-documents.parquet | 135,748,496 | 2026-05-09 03:48:38 GMT | 検索用に整形した POI 文書 |
| poi-search-manifest.json | 589 | 2026-05-09 03:48:38 GMT | 一式の説明 |
| poi-search.duckdb | 426,782,720 | 2026-05-09 03:48:38 GMT | POI 文書 + DuckDB FTS 索引 |
| valhalla.json | 9,131 | 2026-05-10 08:24:04 GMT | Valhalla の設定 |
| valhalla_tiles.tar | 858,224,640 | 2026-05-10 08:23:55 GMT | Valhalla 経路タイル 272 枚 |

範囲要求は、どのファイルも 1 回目の末尾要求で 206 が返った。

## poi-search-manifest.json

全体を取得した (589 バイト)。

- `profile`: cesg-poi-search/0.1、`runtime`: duckdb+fts
- `source`: overture-places、`source_release`: 2026-04-15.0
- `bbox`: 139.56000518798828, 35.520002365112305, 139.91997528076172, 35.81999969482422
- `count`: 450,295
- `created_at`: 2026-05-09T03:48:25.638668+00:00
- トークン化: NFKC 正規化と小文字化、形態素解析は lindera、文字 2-gram と 3-gram、1-gram は無し
- `assets`: documents は poi-documents.parquet、duckdb は poi-search.duckdb

bbox は東京 23 区より広く、川崎と横浜の北部、埼玉の南部、千葉の西部 (市川、浦安) を含む。「tokyo」は東京都の範囲ではない。

## overture-places.parquet

DuckDB でフッターと一部の列だけ読んだ。

- 行数 450,302、行グループ 29、作成は parquet-cpp-arrow 20.0.0
- GeoParquet 1.1.0 のメタデータ付き。geometry は WKB の Point、bbox 列を covering に指定している
- bbox 列の統計: xmin 139.5599822998047 から 139.9199981689453、ymin 35.519996643066406 から 35.81999969482422。manifest の bbox と一致する
- 列は Overture places/place の列そのもの

| 列 | 型 |
|---|---|
| id | VARCHAR |
| geometry | GEOMETRY('OGC:CRS84') |
| categories | STRUCT(primary VARCHAR, alternate VARCHAR[]) |
| confidence | DOUBLE |
| websites, emails, socials, phones | VARCHAR[] |
| brand | STRUCT(wikidata, names STRUCT(...)) |
| addresses | STRUCT(freeform, locality, postcode, region, country)[] |
| names | STRUCT(primary VARCHAR, common MAP(VARCHAR, VARCHAR), rules STRUCT(...)[]) |
| sources | STRUCT(property, dataset, license, record_id, update_time, confidence, between)[] |
| operating_status | VARCHAR |
| basic_category | VARCHAR |
| taxonomy | STRUCT(primary VARCHAR, hierarchy VARCHAR[], alternates VARCHAR[]) |
| version | INTEGER (1 から 10) |
| bbox | STRUCT(xmin, xmax, ymin, ymax DOUBLE) |

集計した値:

- id の重複は無し (distinct 450,302)
- operating_status: open 450,299、closed 3
- addresses の先頭要素の region: 空 331,301、東京都 96,584、神奈川県 7,500、埼玉県 3,891、Tōkyō 3,628、Tokyo 2,328、千葉県 2,171、Tōkyō-to 867 (上位 8)。表記が揃っていない
- sources の update_time は 2020-06-22 から 2026-04-07

sources 列に書かれた元データとライセンス (1 行に複数の出典があるので合計は行数を超える):

| dataset | license | 件数 |
|---|---|---:|
| Overture | CDLA-Permissive-2.0 | 450,302 |
| meta | CDLA-Permissive-2.0 | 307,649 |
| Foursquare | Apache-2.0 | 101,431 |
| AllThePlaces | CC0-1.0 | 24,602 |
| Microsoft | CDLA-Permissive-2.0 | 16,564 |
| PinMeTo | CDLA-Permissive-2.0 | 35 |
| DAC | CDLA-Permissive-2.0 | 21 |

ライセンスは上のとおり行ごとに違う。一覧の条件は <https://docs.overturemaps.org/attribution/> を見る。

## poi-documents.parquet

- 行数 450,295、行グループ 1、作成は parquet-cpp-arrow 20.0.0 (pandas から書いたもの)
- source はすべて overture-places、source_release はすべて 2026-04-15.0

| 列 | 型 | 中身 (見本の行から) |
|---|---|---|
| poi_id | VARCHAR | `overture-places:` + Overture の id |
| source, source_release | VARCHAR | overture-places, 2026-04-15.0 |
| source_feature_id | VARCHAR | Overture の id |
| lon, lat | DOUBLE | 座標 |
| quadkey_z12 | VARCHAR | z12 の quadkey (12 桁) |
| name_primary, name_normalized, names_all | VARCHAR | 名前と正規化した名前 |
| category_primary, category_path | VARCHAR | 例 `obstetrician_and_gynecologist > prenatal_perinatal_care > hospital` |
| address_text | VARCHAR | 住所を 1 文字列にしたもの |
| exact_tokens, category_tokens, morph_tokens, name_bigram_tokens, name_trigram_tokens | VARCHAR | 空白区切りのトークン列 |
| display_json | VARCHAR | 表示用の name, category, address |

overture-places.parquet との差は 7 行。その 7 行は id で突き合わせて特定した。どれも座標が bbox の縁 (x が 139.5599822998047 または 139.9199981689453、y が 35.519996643066406 または 35.81999969482422) にある。bbox 列の単精度の丸めで切り出しでは内側に入り、文書化のときの座標の判定で外に出た、と説明できる (推測)。

## poi-search.duckdb

- 先頭 4 KiB の範囲要求で見たヘッダ: 保存形式の番号 64、書いた DuckDB は v1.3.2 (0b83e5d2f6)
- DuckDB 1.5.5 から HTTP 越しに `ATTACH ... (read_only)` で読めた。丸ごとは落としていない
- 表:

| スキーマ.表 | 行数 (推定値) | 列 |
|---|---:|---|
| main.poi_documents | 450,295 | poi-documents.parquet と同じ 19 列。display_json だけ JSON 型 |
| fts_main_poi_documents.docs | 450,295 | docid, name, len |
| fts_main_poi_documents.terms | 10,149,090 | docid, fieldid, termid |
| fts_main_poi_documents.dict | 1,109,689 | termid, term, df |
| fts_main_poi_documents.fields | 5 | exact_tokens, category_tokens, morph_tokens, name_bigram_tokens, name_trigram_tokens |
| fts_main_poi_documents.stats | 1 | num_docs 450,295、avgdl 22.53875792536004 |
| fts_main_poi_documents.stopwords | 0 | sw |

- マクロ `match_bm25` と `tokenize` がある。`USE` でこの DB を既定にしないと、マクロの中の表が見つからずエラーになる
- 試しに `match_bm25(poi_id, '都庁')` を HTTP 越しに投げると 24.4 秒で返り、上位は 都庁前駅、都庁弓道部、東京都庁 だった
- 中身は poi-documents.parquet の複製と索引。行数も一致する

## input.parquet

全体を取得した (4,403 バイト)。

- 5 行、列は id, names, categories, geometry, addresses で、すべて VARCHAR (JSON を文字列で入れている)
- 中身は スターバックス渋谷店、ファミリーマート新宿店、東京都庁、寿司さか井、上野公園カフェ。id は 001 から 005、座標は小数 4 桁
- Overture の本物の行ではなく、手で書いたテスト用の見本と見える (推測)。2 つの PoC のリポジトリで、このファイル名を使っている箇所は見つけられなかった

## valhalla_tiles.tar

先頭 64 KiB だけを範囲要求で読んだ。

- 普通の ustar。最初の要素は `index.bin` (4,352 バイト、mtime 2026-05-10 07:56:03 UTC)。その後に `0/002/690.gph` のような Valhalla のタイルが続く
- index.bin を 16 バイトずつ読むと 272 エントリ。階層別に level 0 が 8 枚、level 1 が 14 枚、level 2 が 250 枚。タイルの合計は 857,738,264 バイト
- タイルのヘッダにある版は 3.5.1 (Valhalla の版と見える)
- タイルの外接範囲: level 2 は経度 130.75 から 142.25、緯度 24.5 から 42.75。level 1 は経度 138 から 143、緯度 24 から 38。POI の bbox よりずっと広い。関東の抽出データにはフェリー航路や伊豆・小笠原諸島が入るので、それで広がっていると説明できる (推測、タイルの中身は見ていない)

元データ: ビルド元リポジトリの docs (findings.md, tokyo-valhalla-pipeline.md) によると、元は `kanto-260423.osm.pbf` (443 MB、2026-04-23 付けの関東の OSM 抽出)。タイル枚数 272 もその記述と一致する。ファイル自体に元の PBF の名前や日付は書かれていない。

ライセンス: 未確認。元が OSM なら ODbL-1.0 になる。

## valhalla.json

全体を取得した (9,131 バイト)。Valhalla の標準の設定ファイル。

- `mjolnir.tile_extract` は `/custom_files/valhalla_tiles.tar`、`tile_dir` は `/custom_files/valhalla_tiles`
- `admin` (admins.sqlite)、`timezone` (timezones.sqlite)、`additional_data.elevation`、`traffic_extract`、`transit_dir`、`landmarks` も指しているが、それらのファイルはここに置かれていない
- `loki.actions` に route, sources_to_targets, optimized_route, isochrone, trace_route などが有効になっている
- httpd の待ち受けは 8002 番

## 12 ステップでの使いどころ (案)

- 1 ロジスティック回帰 / 2 Random Forest / 3 XGBoost: overture-places.parquet の confidence、sources の数、websites や phones の有無、カテゴリから、operating_status や「確からしい POI か」を当てる。ただし closed は 3 件しかないので、目的変数は別に作る必要がある
- 4 Cross Validation とデータリーク: POI は空間的に固まるので、ランダム分割と quadkey_z12 単位の空間分割で成績を比べる。poi-documents.parquet の quadkey_z12 列がそのまま分割キーに使える
- 5 k-means / DBSCAN: lon, lat でカテゴリ別 (コンビニ、駅など) にクラスタリングする。45 万件あるので DBSCAN は範囲を絞る
- 6 PCA: quadkey_z12 ごとのカテゴリ件数の表を作り、次元を落として街の性格を見る
- 7 Dijkstra / A*: valhalla_tiles.tar をローカルの Valhalla で読ませると、自前実装の最短経路と答え合わせができる。自前のグラフそのものは OSM から作る
- 8 LP/MILP / 9 facility location: POI を需要点や候補地にして、店舗配置や施設配置を解く。距離を Valhalla の sources_to_targets (距離行列) で出すと道路距離で解ける
- 10 CP-SAT / scheduling: 複数の POI を時間枠つきで巡る訪問計画。移動時間は Valhalla から
- 11 SHAP / calibration: 上の分類モデルに対して、confidence 列の較正を確かめる
- 12 多目的最適化: 施設配置で距離と件数と費用の釣り合いを見る

poi-search.duckdb は全文検索の索引で、機械学習の入力にはあまり向かない。表として使うなら poi-documents.parquet か overture-places.parquet を直接読む。
