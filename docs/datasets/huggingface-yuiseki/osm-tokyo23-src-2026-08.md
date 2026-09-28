# osm-tokyo23-src-2026-08

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/osm-tokyo23-src-2026-08/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/osm-tokyo23-src-2026-08`
- 東京 23 区の OSM を 2026-08-31 の planet から切り出して凍結したもの。元の .osm.pbf と、osm2pgsql のスキーマのまま Parquet にした 4 表が入っている。
- 最終更新 2026-09-15。コードは GitHub の `yuiseki/osm-tokyo23-src-2026-08`。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| tokyo23-260831.osm.pbf | 87,399,745 | 切り出した OSM。md5 ファイルの値は `44a4ba2182379c147f20a27ad1b513ef` |
| tokyo23-260831.osm.pbf.md5 | 62 | 上の md5 |
| tokyo23_osm_boundary.geojson | 85,661 | 切り出しに使った 23 区の外形 (MultiPolygon、経緯度) |
| parquet/planet_osm_point.parquet | 9,914,808 | 点 |
| parquet/planet_osm_line.parquet | 25,952,829 | 線 |
| parquet/planet_osm_polygon.parquet | 118,645,387 | 面 |
| parquet/planet_osm_roads.parquet | 4,435,958 | 低ズーム描画用の主要な線 |
| parquet/checksums.md5 | 332 | Parquet 4 本と geojson の md5 |
| provenance.yaml | 4,002 | 元データ、道具の版、除いたもの |
| LICENSE | 1,577 | ODbL の表示 |

## 行数と列

フッターを DuckDB 1.5.5 で URL から読んだ。4 本とも書いた道具は `DuckDB version v1.5.5`。

| 表 | 行数 | row group |
|---|---|---|
| planet_osm_point | 306,642 | 3 |
| planet_osm_line | 347,735 | 3 |
| planet_osm_polygon | 1,437,105 | 12 |
| planet_osm_roads | 33,113 | 1 |

行数はカードの表と一致した。

列はどの表も 70 個。osm2pgsql の default.style が昇格させたタグの列 (`amenity` `shop` `highway` `building` `name` `admin_level` など、どれも VARCHAR) と、`osm_id` BIGINT、`z_order` INTEGER、`tags` VARCHAR (hstore を JSON 文字列にしたもの)、`way` BLOB (WKB、EPSG:3857)。line と polygon と roads には `way_area` FLOAT と `tracktype` があり、point には代わりに `capital` と `ele` がある。

point と roads と line (合わせて約 40MB) は全体をダウンロードし、md5 が `checksums.md5` と一致することを確かめてから集計した。polygon は URL から列を絞って集計した。

- point: 形はすべて POINT。`osm_id` はすべて正。経緯度に直した範囲は経度 134.60 から 142.20、緯度 27.10 から 35.87。1% 点と 99% 点は経度 139.59 から 139.88、緯度 35.55 から 35.80。経度 139.55 から 139.95、緯度 35.5 から 35.84 の枠の外にある点は 71 個。
- point の非 NULL 数: `name` 127,109、`highway` 102,629、`amenity` 81,475、`shop` 29,630、`brand` 24,337、`addr:housenumber` 11,425、`railway` 10,573、`tourism` 7,984。
- point の `amenity` 上位: restaurant 14,443、vending_machine 7,641、pub 4,393、cafe 4,249、bicycle_rental 4,185、bench 4,152、fast_food 3,866。`shop` 上位: convenience 4,926、hairdresser 2,487、clothes 2,048、supermarket 1,757。
- line: 形はすべて LINESTRING。`highway` 付きが 286,144 (footway 98,855、service 77,951、residential 42,343、unclassified 21,093、steps 12,330、tertiary 9,347 ほか)。`railway` 8,483、`waterway` 1,307。`osm_id` が負 (リレーション由来) の行が 8,994。
- roads: 形はすべて LINESTRING。`highway` が NULL の行が 20,503 あり、`railway` 8,483、`boundary` 12,303 を含む。`highway` は primary 4,167、secondary 3,237、trunk 1,795、motorway 609 などの幹線だけで、residential は 47。道路網としては line を使う。
- polygon: `building` 付きが 1,361,121 (yes 932,031、house 292,426、apartments 72,626、residential 29,475)。`landuse` 17,111、`leisure` 12,890、`amenity` 34,566。
- `boundary='administrative'` かつ `admin_level='7'` で名前が「区」で終わる行は 24、名前の種類は 23。練馬区だけ 2 行 (`osm_id` -1760119)。カードのとおり、マルチポリゴンは複数行に分かれている。

## 元データと基準日

- planet-260831.osm.pbf (94,612,383,571 バイト、md5 `c67437924cf55de40e8708c7192f354d`) から osmium-tool 1.16.0 の `complete_ways` で切り出した (provenance.yaml)。z.yuiseki.net の `openstreetmap/planet/` にある planet-260831 と同じ大きさと md5。
- 基準日は 2026-08-31 の planet (複製時刻 2026-08-30T23:59:56Z)。姉妹データセットの記録では `osm_base 2026-08-30T23:50:59Z`。
- Parquet は osm2pgsql 1.11.0 (`--hstore`、投影は既定の EPSG:3857) で PostGIS 16-3.4 に入れ、DuckDB 1.5.5 で書き出したもの。
- このデータセットから作られたもの: osm-tokyo23-questions (質問)、osm-tokyo23-qa-2026-08 (答え)、osm-wikidata-brand-tokyo23 (ブランド名)。全国版は osm-japan-src-2026-08。

## ライセンス

- カードとタグ: `odbl` (ODbL 1.0)。LICENSE に OSM の帰属表示がある。

## 気づいたこと

- 座標は EPSG:3857 のまま。距離と面積をそのまま測ると東京では長さが約 1.23 倍になる (カードの説明)。学習で距離を特徴量にするなら、先に 4326 か EPSG:32654 に変換する。
- `complete_ways` なので、区の外に伸びる way も丸ごと入っている。point の最大範囲が経度 134 から 142 まで広がっているのはそのためと思われる (71 点を個別には確かめていない)。
- カードの「A question set built on this」節は、osm-tokyo23-questions を「131 questions」「90 of them were checked」と書いている。実物の osm-tokyo23-questions は 215 問、テンプレートから作ったものが 174 問で、数が古い。
- roads 表は名前に反して道路網ではない (上記)。

## 12 ステップでの使いどころ (案)

- 1, 2, 3, 11: polygon の建物で、面積 (4326 か 32654 に直して測る) や `building` の種類、`tags` の中の `building:levels` から階数を回帰・分類する。`tags` は JSON 文字列なので前処理が要る。
- 4: 同じ建物の問題で、ランダム分割と区ごとの分割 (23 区の境界は polygon に入っている) で CV の成績を比べる。
- 5: point の restaurant や cafe を DBSCAN にかけて繁華街を切り出す。k-means と比べる。
- 6: 区ごとに `amenity` や `shop` の件数を数えた 23 行の表を作って PCA。
- 7: line の `highway` からグラフを作って Dijkstra と A*。Parquet には way のノード ID が無いので、交差点を正しく作るなら pbf から (osmium や pyrosm で) 組むほうが確実。
- 8, 9: コンビニや交番 (point) を施設、建物を需要点にして facility location や割り当て。
- 10, 12: 直接の材料は無い。7 から 9 の題材を流用する。
