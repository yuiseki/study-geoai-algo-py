# Google Open Buildings

2026-09-28 に読んで確かめた内容。数字は断りがない限りこの日に実測したもの。本家ページに書かれている数字は「本家の記載」と書き分ける。

- 本家: <https://sites.research.google/gr/open-buildings/> (旧 URL `https://sites.research.google/open-buildings/` はここへ転送される)
- 2.5D 版: <https://sites.research.google/gr/open-buildings/temporal/>
- 中身は 2 つある。高解像度衛星画像から推定した建物のポリゴン (v1, v2, v3) と、Sentinel-2 から推定した建物の有無・件数・高さのラスタ (2.5D Temporal, 2016〜2023 年の毎年)。
- どちらも Google Cloud Storage の公開バケットにあり、ログイン無しで一覧も取得もできる。Range 要求にも 206 を返す。
- 日本は含まれない。ポリゴンも 2.5D 版も、対象はアフリカ、南アジア、東南アジア、中南米・カリブ。

## ライセンス

本家の FAQ は、ポリゴン版も 2.5D 版も「CC BY 4.0 と ODbL 1.0 の二重ライセンスで、利用者がどちらか好きな方を選べる」と書いている。理由は、OpenStreetMap (ODbL) に取り込めるようにしつつ、ODbL を使わない人は CC BY 4.0 で使えるようにするため。2.5D 版には加えて Copernicus Sentinel データ (2016〜2023) を使った旨の表記がある。

つまり「CC BY 4.0 または ODbL」は本家そのものの二重ライセンスで、派生物のライセンスではない。派生物は条件が変わる。

| 配布元 | ライセンス (各 README の記載) |
|---|---|
| 本家 (ポリゴン、2.5D) | CC BY 4.0 または ODbL 1.0 (選択) |
| source.coop/cholmes/google-open-buildings | 本家と同じ二重ライセンス |
| source.coop/vida/google-microsoft-open-buildings | ODbL 1.0 のみ |
| source.coop/vida/google-microsoft-osm-open-buildings | ODbL 1.0 のみ |
| Overture Maps buildings | Google 由来の部分は attribution ページで CC BY 4.0。テーマ全体は ODbL-1.0 ([overture-maps.md](../stac/overture-maps.md)) |

VIDA 版は Microsoft (ODbL) や OSM (ODbL) と混ぜているので ODbL だけになっている。

## ポリゴン版 (v1, v2, v3)

### 本家の記載

- v3 は 2023 年 5 月に推論。対象面積 5,800 万 km2、18 億件。
- v2 は 2022 年 8 月 (3,910 万 km2、アフリカ、南アジア、東南アジア)、v1 は 2021 年 4 月 (1,940 万 km2、アフリカ)。旧版も同じバケットに残っている。
- 属性は幾何形状だけ。建物の種類、住所、高さは無い。
- 列: `latitude`, `longitude` (ポリゴンの重心), `area_in_meters`, `confidence` (0.65〜1.0), `geometry` (WKT の POLYGON または MULTIPOLYGON。ポリゴン版のみ), `full_plus_code` (重心の Plus Code)
- 1 ファイル = S2 セル レベル 4 の 1 個。ポリゴンは合計 178GB、1 ファイル最大 7.8GB。点は合計 48GB、最大 2.1GB。
- 紛争地などの危険な地域は意図的に除いてある。
- 高層建物は屋根を検出しているので、衛星の見る角度によって位置がずれる。

### バケットの中身 (実測)

`gs://open-buildings-data/` を JSON API (`https://storage.googleapis.com/storage/v1/b/open-buildings-data/o`) で匿名で一覧した。

| 置き場所 | ファイル数 | 合計 | 最大の 1 ファイル |
|---|---:|---:|---:|
| v3/polygons_s2_level_4_gzip/ (CSV.gz) | 333 | 178.26GB | 8.42GB (39f) |
| v3/polygons_s2_level_4/ (CSV 非圧縮) | 333 | 466.30GB | 21.78GB (39f) |
| v3/polygons_s2_level_6_gzip_no_header/ | 3,330 | 175.53GB | 1.73GB |
| v3/polygons_single_csv/ (全件 1 本の CSV) | 1 | 466.30GB | 466.30GB |
| v3/points_s2_level_4_gzip/ | 333 | 48.12GB | 2.31GB |
| v3/points_s2_level_6_gzip_no_header/ | 3,330 | 46.19GB | 0.45GB |
| v2/polygons_s2_level_4_gzip/ | 205 | 78.27GB | 5.82GB |
| v1/polygons_s2_level_4_gzip/ | 135 | 49.80GB | 2.40GB |

- GB は 10 の 9 乗バイト。v3 の最終更新は 2023-06-23 (single_csv は 2023-06-24) で、その後の更新は無い。
- v3 の S2 レベル 4 のファイルは中央値 145MB。50MB 未満は 122 本。
- `level_6_gzip_no_header` はヘッダー行が無い。列の順は本家の説明を見る。
- タイルの一覧 `https://openbuildings-public-dot-gweb-research.uw.r.appspot.com/public/tiles.geojson` (250KB) は 333 地物で、各地物に `tile_id`, `tile_url`, `size_mb` がある。
- 日本の確認: tiles.geojson の 333 タイルの外接矩形に、東京 (139.7, 35.7)、大阪 (135.5, 34.7)、那覇 (127.7, 26.2) を含むものは無かった。外接矩形の北端は最大でも北緯 39.98 度。本家の国一覧にも JPN は無い。

### 1 ファイルを読んだ結果

小さい `v3/polygons_s2_level_4_gzip/32b_buildings.csv.gz` (12,230 バイト) を丸ごと取得し、DuckDB 1.5.5 の `read_csv_auto` で読んだ。

- 列: `latitude` DOUBLE, `longitude` DOUBLE, `area_in_meters` DOUBLE, `confidence` DOUBLE, `geometry` VARCHAR (WKT), `full_plus_code` VARCHAR
- 134 行。confidence 0.6506〜0.9367、面積 8.1〜225.6 m2 (中央値 33.7 m2)。経度 130.0〜131.3、緯度 0.0〜1.1 (インドネシア東部の海域のセル)。
- 同じセルの点版 (`points_s2_level_4_gzip/32b_buildings.csv.gz`, 3,264 バイト) は geometry 列が無いだけで、他の列は同じ。

### 閾値表 (実測)

`v3/score_thresholds_s2_level_4.csv` (75,976 バイト) を丸ごと読んだ。列は `s2_token`, `geometry`, `confidence_threshold_{80,85,90}%_precision`, `building_count_{80,85,90}%_precision`, `building_count`, `num_samples`。

- 312 行。`building_count` の合計は 1,848,201,804 (本家の「18 億件」と合う)。
- 精度 90% の閾値を超える建物は合計 524,531,299 件で、全体の 28.4%。
- 精度 90% の閾値はセルによって 0.65〜1.0 と大きく違う。1 つの閾値で全域を切ると、場所によって精度が変わる。

## 2.5D Temporal 版 (建物の有無と高さのラスタ)

### 本家の記載

- 2016〜2023 年の毎年 (6 月 30 日を中心に前後 16 枚ずつ、計 32 枚の Sentinel-2 画像から推論)。対象面積は約 5,800 万 km2 で、ポリゴン v3 と同じ地域。
- 3 バンド: 建物の有無 (confidence)、建物の件数 (fractional count)、建物の高さ (地面からの相対高さ、m)。
- ファイルの画素は 50cm だが、実効解像度は約 4m。
- 高さの平均絶対誤差は 1.5m。ただし評価したのは北米、欧州、日本だけで、対象地域 (Global South) では定性的な評価しかしていない。高さは 100m で打ち切り。
- confidence は較正されていない。0.8 は「80% の確率で建物」という意味ではない。高さは建物の有無と組み合わせて、有無の confidence が低い画素を隠して使う。
- 年ごとの位置ずれ、タイル境界の継ぎ目、太陽光パネルや農業用ハウスの誤検出がある。
- Earth Engine の ImageCollection `GOOGLE/Research/open-buildings-temporal/v1` と、GCS の GeoTIFF の 2 経路。

### バケットの中身 (実測)

`gs://open-buildings-temporal-data/v1/` は `geotiffs/` と `manifests/` の 2 つ。

- `geotiffs/` の直下は `{S2 トークン}_{年}_06_30/` のフォルダが 110,826 個。S2 トークンは 14,013 種類。
- 年ごとのフォルダ数は 13,693 (2016, 2017) から 13,988 (2023) まで違う。全セルに 8 年分そろっているわけではない。
- フォルダの中は `tile_{ID}.tif`。1 フォルダで見た 10 本は 10.3〜37.3MB。全体のファイル数と合計の大きさは数えていない。
- `manifests/` は Earth Engine に取り込むための JSON (1 本 0.6〜1MB 程度)。各タイルの URI とアフィン変換が入っている。1 本 (`01_EPSG_32723_2023_06_30.json`) を読むと、タイルは 2,583 本だった。

### 1 ファイルを読んだ結果

`v1/geotiffs/00824_2023_06_30/tile_3R_Zv1Dd-Gc.tif` のヘッダーだけを GDAL 3.9.2 の `/vsicurl/` で読んだ (Range 要求)。

- 25,000 × 25,000 画素、画素 0.5m (1 タイル 12.5km 四方)。座標系は UTM (この 1 本は EPSG:32723)。
- 3 バンドとも Float32、NoData は -99。バンド名は `building_fractional_count`, `building_height`, `building_presence`。
- 512 × 512 のブロック、DEFLATE 圧縮、オーバービュー 14 段。Range 要求で必要な部分だけ読める形になっている。
- このタイルと隣のタイル (tile_CFFGIJ0Q5W0.tif) の低解像度オーバービューの統計は、3 バンドとも全部 0 だった。どちらもブラジル沿岸の海を多く含むタイルで、建物の値の中身はまだ確かめていない。

## 入手経路

| 経路 | ログイン | 形式 | 確かめたこと |
|---|---|---|---|
| GCS `open-buildings-data` (ポリゴン、点、閾値) | 不要 | CSV.gz、CSV | 匿名で一覧、取得、Range 206 |
| GCS `open-buildings-temporal-data` (2.5D) | 不要 | GeoTIFF (タイル化、オーバービュー付き) | 匿名で一覧、Range 206、ヘッダー読み取り |
| Earth Engine (`GOOGLE/Research/open-buildings/v3/polygons`, `GOOGLE/Research/open-buildings-temporal/v1`) | 要ログイン | FeatureCollection、ImageCollection | 使っていない |
| 本家の地図からタイル単位でダウンロード、Colab ノートブック | 不要 (Colab は Google アカウント) | CSV.gz、GeoTIFF | 使っていない |
| HDX (20 か国分) | 未確認 | 未確認 | 本家に案内があるだけ |
| source.coop/cholmes/google-open-buildings | 不要 | GeoParquet (国別、S2 別)、FlatGeobuf、PMTiles | 下記 |
| source.coop/vida/google-microsoft-open-buildings | 不要 | GeoParquet 1.1.0、FlatGeobuf、PMTiles | 下記 |
| source.coop/vida/google-microsoft-osm-open-buildings | 不要 | GeoParquet 1.1.0、FlatGeobuf、PMTiles | README だけ読んだ |
| Overture Maps buildings | 不要 | GeoParquet | 下記 |

### source.coop のミラー (実測)

`https://data.source.coop/{アカウント}?list-type=2&prefix=...` の S3 互換 API で一覧した。

- cholmes 版 (Chris Holmes による v3 の変換): 更新は 2023-09-28 から 2023-10-13。PMTiles 1 本 130.58GB。`geoparquet-by-country/country_iso={2 文字}/` に国別の Parquet。
  - 変更点 (README の記載): MULTIPOLYGON を POLYGON に分けて面積を計算し直した。latitude と longitude を削った。`country_iso` と `quadkey` (レベル 12) を足した。
  - `country_iso=SG/SG.parquet` (39.5MB) のフッターを DuckDB で読んだ: 列は `area_in_meters`, `confidence`, `full_plus_code`, `geometry` (WKB), `quadkey`, `country_iso`。378,254 行、13 行グループ。GeoParquet は `1.0.0-beta.1`。
- VIDA 版 (Google v3 + Microsoft): README の記載では 2,579,035,323 件、185 区画、版 2.0 (2024-09-04)。`bf_source` 列で出どころを区別する。Google の `full_plus_code`, `latitude`, `longitude` は削ってある。
  - `country_iso=SGP/SGP.parquet` のフッター: 列は `boundary_id`, `bf_source`, `confidence`, `area_in_meters`, `s2_id`, `country_iso`, `geohash`, `geometry` (WKB), `bbox` (xmin, ymin, xmax, ymax)。394,403 行、79 行グループ。GeoParquet `1.1.0`。`bf_source` は google と microsoft の両方。
  - `country_iso=JPN/JPN.parquet` (5.06GB) のフッター: 40,719,754 行、8,144 行グループ。全行グループで `bf_source` の最小も最大も microsoft、`confidence` は全行 null。日本の分は全部 Microsoft 由来で、Google の建物は 1 件も入っていない。
- VIDA + OSM 版: README の記載では 2,705,459,584 件、200 区画 (本文の別の箇所では 182 区画)。Google の元データは 2023-10-02 時点。
- どのミラーにも高さの列は無い。

### Overture Maps との関係 (実測)

Overture の attribution ページは、buildings の出どころの 1 つに Google Open Buildings (CC BY 4.0) を挙げている。

2026-09-23.1 リリースの `theme=buildings/type=building/` の Parquet から 13 本を選び、フッターの `sources.dataset` の統計を読んだ。メキシコ、西アフリカ、東アフリカ、南部アフリカ、インド、東南アジア、フィリピンにかかるファイルでは最小値が `Google Open Buildings` で、Google 由来の建物が入っている。北米、欧州、イラン、日本 (経度 136〜139、緯度 33.8〜35.2) のファイルでは最小値が `Microsoft ML Buildings` 以降で、Google 由来は入っていない。統計は行グループの最小と最大なので、件数はわからない。

## ユーザーの表との違い

- 「派生版では高さ」: 高さを持つのは第三者の派生物ではなく、Google 自身の 2.5D Temporal 版 (ラスタ)。source.coop の cholmes 版と VIDA 版はポリゴンを変換、統合しただけで、高さは無い。ポリゴン版そのものにも高さは無い。
- 「CC BY 4.0 または ODbL」: 本家 (ポリゴン、2.5D とも) の二重ライセンスのこと。VIDA の統合版は ODbL だけになる。
- 携帯基地局の配置で「3D 環境、遮蔽物、建物密度」に使うなら、対象地域が Global South だけなのが最大の制約。日本の建物は入っていない。2.5D 版の高さは実効 4m 解像度の推定値で、1 棟ごとの遮蔽の計算には粗い。建物密度 (件数ラスタ、ポリゴンの集計) には使える。

## 気づいた異常

- 本家の「1 ファイル最大 7.8GB」は実測 8.42GB、「点は最大 2.1GB」は実測 2.31GB。どちらも 2 の 30 乗を 1GB とすると本家の値に合う。一方で「合計 178GB」は 10 の 9 乗で合う。単位が混ざっている。
- 閾値表は 312 行なのに、ファイル (タイル) は 333 本ある。21 本 (013, 025, 05b, 063, 0e1, 225, 23d, 249, 2cd, 307, 32b, 347, 39d, 3b9, 3d1, 69d, 83f, 855, 8d5, 971, 973) には閾値が無い。どれも 1.9MB 以下の小さいタイル。上で読んだ 32b もその 1 本。
- 国一覧が 2 つのページで違う。2.5D 版の一覧には MLI (マリ) と TCD (チャド) があるが、ポリゴン v3 の一覧には無い。本家は「ポリゴン v3 と同じ範囲」と書いている。
- 2.5D 版は年によってフォルダ数が最大 295 違う。
- 2.5D 版の高さの誤差は、対象地域の外 (北米、欧州、日本) でしか測られていない。
- VIDA + OSM 版の README は区画数を 200 と 182 の 2 通りに書いている。
- v3 は 2023 年 6 月から更新されていない。画像の撮影時期は場所ごとに違い、数年前の画像のこともあると本家が書いている。

## 学習ステップとの対応 (案)

| ステップ | 使い方 |
|---|---|
| 1〜3 回帰・分類、木、Boosting | 格子やセルごとに建物件数、面積の合計、平均面積を集計して、WorldPop の人口を予測する特徴量にする |
| 4 Cross Validation とデータリーク | S2 セル (ファイルの単位) をそのまま空間ブロックにして GroupKFold する。2.5D 版の年を使えば時間方向の分割も試せる |
| 5 k-means / DBSCAN | 点版 (重心) を DBSCAN にかけて集落を切り出す |
| 6 PCA | 2.5D 版の 8 年分の件数や高さを画素ごとの時系列として並べ、次元を圧縮して変化の型を見る |
| 8〜9 LP / MILP、facility location | 建物の点を需要点にして、基地局や施設の配置と割当を解く (Global South の国で) |
| 11 SHAP / calibration | confidence は較正されていない (本家の記載)。閾値表のセルごとの精度 80/85/90% の閾値を使って、較正曲線を考える題材になる |
| 12 多目的最適化 | 8〜9 の配置に、覆う建物数と設置数やコストを同時に目的として与える |

## 取り出し方

区分は split。本家の配布物 1 本の中は whole で、2.5D の GeoTIFF と source.coop のミラーだけが range。
2026-09-30 に実測した。

### 本家のポリゴン (CSV.gz) は split で、中は whole

GCS は Range を受ける。小さい `v3/polygons_s2_level_4_gzip/32b_buildings.csv.gz` (12,230 バイト) も、
最大の `39f_buildings.csv.gz` (8,423,792,523 バイト) も、`curl -sI` が 200 と `Accept-Ranges: bytes` を返し、
`curl -r 0-1023` に 206 と 1,024 バイト、`curl -r -8` に 206 と 8 バイトが返る。

ただし 206 が返ることと、必要な範囲だけ取れることは別だった。`39f_buildings.csv.gz` で確かめた。

- 先頭 65,536 バイトを引いて gzip として展開すると 167,388 バイトになり、1 行目が
  `latitude,longitude,area_in_meters,confidence,geometry,full_plus_code` と読めた。先頭からなら途中まで展開できる。
- 同じファイルの `bytes=4000000000-4000065535` を引いて展開しようとすると
  `Error -3 while decompressing data: incorrect header check` で失敗する。gzip は 1 本の連続した流れなので、途中から展開できない。

つまり、ある建物を探すには、その建物が現れるところまで先頭から順に流すしかない。
索引の役目を果たすのは分割のほうで、S2 レベル 4 で 333 本、レベル 6 で 3,330 本に切ってある。
どのセルを引くかは `tiles.geojson` (250KB、333 地物) で決められる。これが split の実体。

### 2.5D Temporal の GeoTIFF は range

`https://storage.googleapis.com/open-buildings-temporal-data/v1/geotiffs/00824_2023_06_30/tile_3R_Zv1Dd-Gc.tif`
は 25,409,708 バイトで `Accept-Ranges: bytes`。`curl -r 0-3` が 206 と 4 バイトを返し、中身は `49 49 2a 00` (`II*\0`)。
TIFF のヘッダが先頭にあるので、上の「1 ファイルを読んだ結果」で GDAL が読めたとおり、
512 x 512 のブロックとオーバービューを部分読みできる。ESA WorldCover と同じ形。

### source.coop のミラー (GeoParquet) は range

Parquet のフッターはファイルの末尾にあるので、末尾を引いて長さを知り、そこから戻ってフッターを読む往復が要る。

| ファイル | 大きさ | `curl -r -8` の 8 バイト | フッターの長さ | フッター本体の Range |
|---|---:|---|---:|---|
| `https://data.source.coop/cholmes/google-open-buildings/geoparquet-by-country/country_iso=SG/SG.parquet` | 39,533,047 | `b6 89 00 00 50 41 52 31` | 35,254 | `bytes=39497785-39533038` に 206、35,254 バイト |
| `https://data.source.coop/vida/google-microsoft-open-buildings/geoparquet/by_country/country_iso=SGP/SGP.parquet` | 55,605,555 | `65 1a 03 00 50 41 52 31` | 203,365 | `bytes=55402182-55605546` に 206、203,365 バイト |

どちらも末尾 4 バイトは `PAR1`。

pyarrow 20.0.0 に Range 要求だけを出す読み取り器を渡して、要求の回数を数えた。
cholmes 版の SG から `area_in_meters` と `confidence` の 2 列を最初の行グループ分だけ読むと、
要求は合計 3 回 (末尾 65,536 バイトが 1 回、列の塊が 2 回)、流れたのは 383,685 バイト、2.2 秒だった。
ファイル全体の 1.0% で済む。13 行グループのうちの 1 つで 30,000 行。

本家の CSV.gz と比べると、同じ建物を国単位で引くのに桁が 2 つ違う。
本家で国を絞るには S2 セルのファイルを丸ごと流す必要があり、ミラーなら列と行グループで刻める。

### まとめ

| 経路 | 区分 | 根拠 |
|---|---|---|
| GCS のポリゴン、点 (CSV.gz) | split (333 / 3,330 本)、1 本は whole | Range は 206 だが、途中からの gzip 展開が失敗する |
| GCS の閾値表 `v3/score_thresholds_s2_level_4.csv` (75,976 バイト) | whole | 非圧縮の CSV で索引が無い。小さいので問題にならない |
| GCS の 2.5D GeoTIFF | range | 先頭 4 バイトが `II*\0`、タイル化とオーバービューあり |
| source.coop の GeoParquet | range | 末尾 4 バイトが `PAR1`、2 列 1 行グループを 3 回の要求、383,685 バイトで読めた |
| Earth Engine | 未確認 | ログインが要る。確かめるには Google アカウントと EE の登録が要る |
| HDX の 20 か国分 | 未確認 | 本家に案内があるだけで、URL を追っていない |
