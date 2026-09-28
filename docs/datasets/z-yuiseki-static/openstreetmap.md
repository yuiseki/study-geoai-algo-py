# openstreetmap/

2026-09-28 に読んで確かめた内容。大きさは HEAD の `Content-Length` (バイト)。

- `https://z.yuiseki.net/static/openstreetmap/`
- 下位は `planet/` `region/` `layercake/` `layercake-gpio/` `taginfo/` `wiki/` `names/` の 7 つ。直下にファイルは無い。
- どれも OpenStreetMap (OSM) かその周辺 (OSM Wiki、taginfo、Wikidata の名前) から作られたもの。

## planet/

OSM 本家の planet ファイル 3 版と、それを元にしたベクタータイル 1 本。

| ファイル | 大きさ | 中身 |
|---|---|---|
| planet-260803.osm.pbf | 94,197,298,196 | OSM planet。複製時刻 2026-08-03T00:00:02Z |
| planet-260817.osm.pbf | 94,393,027,107 | 同 2026-08-17T00:00:02Z |
| planet-260831.osm.pbf | 94,612,383,571 | 同 2026-08-30T23:59:56Z |
| planet-*.osm.pbf.md5 | 各 56 | md5 と元のファイル名 1 行 |
| planet-*.osm.pbf.torrent | 450,699 / 451,639 / 452,679 | mktorrent 1.1 で作った本家配布の torrent |
| planet.pmtiles | 82,984,871,716 | OpenMapTiles スキーマのベクタータイル |

.osm.pbf は先頭 64KB の範囲要求で HeaderBlock を読んだ。

- writingprogram は `planet-dump-ng 1.2.4`、source は `http://www.openstreetmap.org/api/0.6`。
- features は `OsmSchema-V0.6` `DenseNodes`、optional は `Has_Metadata` `Sort.Type_then_ID`。メタデータ (版、変更セット、利用者) 付き。
- bbox は全球。
- md5 の値: 260803 `156085691b8f5cce296e36c35a6ba57b`、260817 `efb6bb214fa6829aa706b69e90cf1d51`、260831 `c67437924cf55de40e8708c7192f354d`。ファイル本体の md5 は計算していない (全体を読む必要があるため)。
- torrent の `info.length` は 3 本とも `Content-Length` と一致した。piece 長は 4,194,304。`url-list` の先頭は `https://planet.openstreetmap.org/pbf/planet-260831.osm.pbf` で、本家の配布物そのもの。
- ノード数や way 数は数えていない (全体を読む必要がある)。

planet.pmtiles はヘッダ (先頭 127 バイト) とメタデータ JSON (1,536 バイト、gzip) を範囲要求で読んだ。

- PMTiles v3、タイル形式 MVT (pbf)、タイル圧縮 gzip、clustered。
- ズーム 0 から 14。範囲は経度 -180 から 180、緯度 -85.05113 から 85.05113。
- アドレスされたタイル数 275,142,148、ディレクトリ項目 50,651,567、中身の異なるタイル 44,626,561。
- メタデータ: name `OpenMapTiles`、version `3.15.0`、`planetiler:version` `0.9.2-SNAPSHOT`、`planetiler:osm:osmosisreplicationtime` `2025-11-24T00:59:59Z`。データの基準日は 2025-11-24 で、同じディレクトリの planet .osm.pbf より古い。
- レイヤー (16): aerodrome_label, aeroway, boundary, building (z13 から), housenumber (z14 のみ), landcover, landuse, mountain_peak, park, place, poi (z11 から), transportation, transportation_name, water, water_name, waterway。名前の付くレイヤーには `name:ja` などの多言語名がある。

## region/

Geofabrik の地域抽出。ヘッダの `osmosis_replication_base_url` が `https://download.geofabrik.de/...-updates` を指している。ファイル名の数字は YYMMDD。

小さいもの (4MB 未満) は全体をダウンロードして `osmium fileinfo -e` で数えた。大きいもの (japan, kanto) は先頭 64KB のヘッダだけ読んだ。

| ファイル | 大きさ | 複製時刻 | nodes | ways | relations |
|---|---|---|---|---|---|
| andorra-251101.osm.pbf | 3,321,139 | 2025-11-01T21:21:02Z | 488,632 | 25,541 | 695 |
| andorra-251231.osm.pbf | 3,327,770 | 2025-12-31T21:20:53Z | 489,175 | 25,624 | 701 |
| andorra-260423.osm.pbf | 3,348,267 | 2026-04-23T20:21:08Z | 490,081 | 25,712 | 723 |
| monaco.osm.pbf | 651,336 | 2025-07-11T20:20:56Z | 40,620 | 5,932 | 308 |
| monaco-251101.osm.pbf | 661,687 | 2025-11-01T21:21:02Z | 40,975 | 6,023 | 309 |
| monaco-251231.osm.pbf | 673,489 | 2025-12-31T21:20:53Z | 41,316 | 6,168 | 347 |
| monaco-260423.osm.pbf | 678,660 | 2026-04-23T20:21:08Z | 41,351 | 6,186 | 348 |
| niue-251101.osm.pbf | 413,977 | 2025-11-01T21:21:02Z | 46,917 | 3,286 | 134 |
| niue-251231.osm.pbf | 419,313 | 2025-12-31T21:20:53Z | 47,528 | 3,398 | 134 |
| japan-251231.osm.pbf | 2,341,984,378 | 2025-12-31T21:20:53Z | (数えていない) | | |
| japan-260423.osm.pbf | 2,407,046,008 | 2026-04-23T20:21:08Z | (数えていない) | | |
| kanto-260423.osm.pbf | 463,775,701 | 2026-04-23T20:21:08Z | (数えていない) | | |

- 地域抽出はメタデータ (Has_Metadata) を持たない。writingprogram は japan-251231 が osmium/1.14.0、260423 の 2 本が osmium/1.16.0。
- japan のヘッダ bbox は経度 122.5607 から 154.4709、緯度 20.08228 から 45.815403。kanto は経度 134.045154 から 155.605818、緯度 18.625054 から 37.15988 (東京都の島しょ部を含むためと思われるが確かめていない)。
- 同じ地域の複数の日付がそろっているので、版の違いによる差分を見る練習に使える。

## layercake/ と layercake-gpio/

OpenStreetMap US の Layercake (OSM を主題別に切り出した GeoParquet、配布元は `https://data.openstreetmap.us/layercake/`) と、その建物を並べ替えたもの。フッターを curl の範囲要求で取り、同じ大きさの疎ファイルの末尾に書いてから DuckDB 1.5.5 で読んだ (DuckDB から URL を直接読むと 60 秒以内に終わらなかったため)。

| ファイル | 大きさ | 行数 | row group | 書いた道具 |
|---|---|---|---|---|
| layercake/boundaries.parquet | 1,982,641,406 | 814,633 | 7 | DuckDB v1.5.1 |
| layercake/buildings.parquet | 43,837,981,826 | 689,237,307 | 5,610 | DuckDB v1.5.1 |
| layercake-gpio/layercake-buildings.parquet | 43,837,981,826 | 689,237,307 | 5,610 | DuckDB v1.5.1 |
| layercake-gpio/buildings-hilbert.parquet | 59,714,651,302 | 689,237,307 | 22,437 | DuckDB v1.5.0 |

boundaries.parquet の列:

`type` VARCHAR, `id` BIGINT, `boundary` VARCHAR, `admin_level` VARCHAR, `name` VARCHAR[], `names` MAP(VARCHAR, VARCHAR[]), `official_name` VARCHAR[], `official_names` MAP(VARCHAR, VARCHAR[]), `int_name` VARCHAR[], `alt_name` VARCHAR[], `alt_names` MAP(VARCHAR, VARCHAR[]), `place` VARCHAR, `border_type` VARCHAR, `ISO3166-2` VARCHAR, `ISO3166-1:alpha2` VARCHAR, `ISO3166-1:alpha3` VARCHAR, `wikidata` VARCHAR, `wikipedia` VARCHAR, `disputed_by` VARCHAR[], `claimed_by` VARCHAR[], `controlled_by` VARCHAR[], `recognized_by` VARCHAR[], `bbox` STRUCT(xmin, ymin, xmax, ymax FLOAT), `geometry` GEOMETRY('OGC:CRS84')

- GeoParquet 1.0.0、WKB、Polygon と MultiPolygon。bbox は経度 -180 から 180、緯度 -59.858 から 84.145777。

buildings.parquet の列 (3 本とも同じ):

`type` VARCHAR, `id` BIGINT, `building`, `building:levels`, `building:flats`, `building:material`, `building:colour`, `building:part`, `building:use`, `name`, `addr:housenumber`, `addr:street`, `addr:city`, `addr:postcode`, `website`, `wikipedia`, `wikidata`, `height`, `roof:shape`, `roof:levels`, `roof:colour`, `roof:material`, `roof:orientation`, `roof:height`, `start_date`, `access`, `wheelchair` (ここまで id 以外はすべて VARCHAR), `bbox` STRUCT(xmin, ymin, xmax, ymax FLOAT), `geometry` GEOMETRY('OGC:CRS84')

- `building:levels` や `height` も文字列のまま。数値として使うには自分で変換と外れ値の処理が要る。
- layercake の 2 本は GeoParquet 1.0.0。buildings-hilbert.parquet は GeoParquet 2.0.0 で、`covering` に bbox 列を登録している。row group が 4 倍に細かい。名前からヒルベルト曲線順に並べ替えたものと思われるが、並び順そのものは確かめていない。
- 基準日: ファイルの更新時刻は 2026-05-03。中の OSM データの時点はフッターからはわからなかった。

## taginfo/

taginfo (OSM のタグ利用統計) の SQLite データベースを bzip2 で圧縮したもの。3 回分ある。基準日は master の `sources` 表に記録されたデータ時刻。

| ディレクトリ | db の データ時刻 | 入っているファイル |
|---|---|---|
| 20250803/ | 2025-08-02 00:59:28 | db, master, wiki, wikidata |
| 20260111/ | 2026-01-10 00:59:50 | db, master, wiki, wikidata |
| 20260130/ | 2026-01-29 00:59:50 | db, master, wiki, wikidata, history, languages, projects, sw |

圧縮時の大きさ:

| ファイル | 20250803 | 20260111 | 20260130 |
|---|---|---|---|
| taginfo-db.db.bz2 | 2,351,433,128 | 2,450,755,952 | 2,464,286,975 |
| taginfo-master.db.bz2 | 5,062,059 | 5,235,427 | 5,244,663 |
| taginfo-wiki.db.bz2 | 22,710,953 | 24,049,419 | 24,220,678 |
| taginfo-wikidata.db.bz2 | 3,472,336 | 3,518,815 | 3,517,615 |
| taginfo-history.db.bz2 | | | 3,372,743 |
| taginfo-languages.db.bz2 | | | 736,103 |
| taginfo-projects.db.bz2 | | | 15,803,631 |
| taginfo-sw.db.bz2 | | | 17,085 |

20260130 の小さい 7 本は全体をダウンロードして伸張し、表と行数を数えた。

- master (伸張後 19,660,800): languages 78, master_stats 124, popular_keys 6,885, project_unique_keys 7,784, project_unique_tags 226,130, sources 7, suggestions 14,179, top_tags 13,723 ほか
- wiki (122,576,896): wikipages 40,552, wikipages_keys 6,421, wikipages_tags 8,042, redirects 7,155, tag_page_wikipedia_links 18,226, wiki_images 7,485, words 9,638 ほか
- wikidata (9,756,672): wikidata_labels 173,503, wikidata_tags 3,740, wikidata_keys 828 ほか
- history (19,127,296): history_stats 434,731
- languages (2,777,088): subtags 8,767, unicode_data 40,575, wikipedia_sites 359 ほか
- projects (283,398,144): project_tags 440,572, projects 274
- sw (73,728): deprecated_tags_id 527, discardable_tags 112 ほか

taginfo-db.db.bz2 (20260130) は先頭 8MB を伸張した。SQLite 3 で、ヘッダ上はページサイズ 4,096、ページ数 3,271,533。スキーマ (表の定義) は先頭に無く、60 秒以内に読めなかった。

## wiki/

| ファイル | 大きさ | 中身 |
|---|---|---|
| dump.xml.gz | 6,676,932,113 | OSM Wiki の MediaWiki XML ダンプ |
| wikibase-rdf.ttl.gz | 10,403,305 | OSM Wiki の Wikibase (データ項目) の RDF (Turtle) |

- dump.xml.gz は先頭 4MB を伸張して 59,174,666 バイトの XML を読んだ。sitename `OpenStreetMap Wiki`、generator `MediaWiki 1.43.6`。先頭の 60 ページに 6,612 版が入っており、最新版だけでなく全履歴のダンプと読める。最初の版は 2005-04-24。全体は読んでいない。
- wikibase-rdf.ttl.gz は全体を読んだ。1,762,975 行。`schema:dateModified "2026-01-30T04:00:04Z"`。`wikibase:Item` が 23,255 件、`wikibase:Property` が 47 件。OSM のキーやタグに対応する項目 (例: Q2 は Tags のページ)。

## names/

| ファイル | 大きさ | 中身 |
|---|---|---|
| wikidata_names.json | 482,194,311 | Wikidata の Q 番号ごとの多言語名 |

- 先頭 4KB と末尾 600 バイトを読んだ。1 行 1 件の JSON 配列で、`["Q 番号の数字", {"言語コード": "名前", ...}, 取得時刻 (ミリ秒)]`。先頭と末尾の取得時刻は 2025-07-24 00:16 と 00:43 (UTC)。
- Planetiler が Wikidata の翻訳を取ってきて保存する形式と同じに見えるが、確かめていない。
- 行数は数えていない (全体を読む必要がある)。

## 気をつけること

- `layercake/buildings.parquet` と `layercake-gpio/layercake-buildings.parquet` は同じもの。大きさ、更新時刻、ETag (`69f6ab84-a34f28482`) が一致し、フッター 16,575,896 バイトもバイト単位で一致した。
- `region/monaco.osm.pbf` は名前に日付が無いが、中身は 2025-07-11 時点。
- monaco の 260423 以外の 3 本は、実データの範囲の南端が緯度 37.268984 で、モナコから離れた点を含んでいる。260423 では 43.3026367。
- niue だけ 260423 版が無い。
- taginfo の 20250803 と 20260111 には history, languages, projects, sw が無い。
- planet.pmtiles のデータ (2025-11-24) は planet .osm.pbf (2026-08) より 9 か月ほど古い。
- DuckDB の httpfs でこのサーバーの巨大 Parquet の URL を直接読むと、フッターだけでも 60 秒以内に返らなかった。curl の範囲要求でフッターを取るほうが速かった (16MB で数秒)。
- 小さい地域 (monaco, andorra, niue) は全体を読んでも 3.4MB 以下なので、まず手元で試すのに向いている。

## ライセンス

- planet .osm.pbf: torrent の comment に「licensed under https://opendatacommons.org/licenses/odbl/ by OpenStreetMap contributors」とある。ODbL 1.0。
- region/ (Geofabrik 抽出)、layercake、planet.pmtiles: OSM 由来だが、それぞれの配布物のライセンス表記はここでは確かめていない (未確認)。planet.pmtiles の attribution は「© OpenMapTiles © OpenStreetMap contributors」。OpenMapTiles スキーマ側の条件は未確認。
- wikibase-rdf.ttl.gz: ファイル内の `cc:license` が CC0 1.0。
- dump.xml.gz (OSM Wiki の本文)、taginfo、wikidata_names.json: 未確認。

## 12 ステップでの使いどころ (案)

- 1, 2, 3, 11: layercake の建物で、形状の面積や `building` の種類から `building:levels` や `height` を回帰・分類する。欠損が多く文字列なので、前処理の練習にもなる。SHAP で何が効いたかを見る。
- 4: 建物は近いもの同士が似ているので、ランダム分割と空間ブロック分割で CV の成績がどれだけ違うかを見るのに向く。boundaries の行政界をブロックに使える。
- 5: 建物の重心を DBSCAN にかけて集落を切り出す。k-means と比べる。
- 6: taginfo の master (top_tags, popular_keys) や建物のタグの有無を行列にして PCA。
- 7: region/ の小さい地域 (monaco, andorra) から道路網を作って Dijkstra と A*。慣れたら kanto。
- 8, 9: 同じく道路網と POI から、施設配置 (facility location) や割り当ての MILP を小さい地域で解く。
- 10, 12: 直接の材料は無い。7 から 9 で作った道路網と施設を題材に流用する形になる。
- planet.pmtiles は学習データというより、結果を地図に重ねるときの背景に使える。
