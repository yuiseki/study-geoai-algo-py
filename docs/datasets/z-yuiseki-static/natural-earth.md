# natural-earth/

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/natural-earth/`
- Natural Earth の国境と一次行政区画を GeoParquet にしたものが 3 つ。どれも 50MB 以下なので全体をダウンロードして DuckDB 1.5.5 で読んだ。

## ファイル

| ファイル | Content-Length (バイト) | Last-Modified | 行数 | 形 |
|---|---|---|---|---|
| ne_110m_admin_0_countries.parquet | 209,382 | 2026-05-31 06:00:20 GMT | 177 | POLYGON 148 / MULTIPOLYGON 29 |
| ne_50m_admin_0_countries.parquet | 1,047,807 | 2026-05-31 06:28:32 GMT | 242 | POLYGON 123 / MULTIPOLYGON 119 |
| ne_10m_admin_1_states_provinces.parquet | 19,153,045 | 2026-05-31 06:28:36 GMT | 4,596 | POLYGON 3,945 / MULTIPOLYGON 651 |

- 3 つとも GeoParquet 1.0.0 (メタデータ `geo`)、geometry は WKB、CRS は WGS 84 (EPSG:4326)。書き出しは pandas 2.3.3 と parquet-cpp-arrow 20.0.0、行グループは 1 つ。
- geometry の NULL は無い。
- Natural Earth の版 (5.1.x など) はファイルに記録が無く、未確認。

## 列

admin_0 の 2 つ (110m と 50m) は同じ 21 列。110m だけ geometry が先頭に来ている (書き出し方が少し違う)。

| 列 | 型 |
|---|---|
| name, name_en, name_ja, admin | VARCHAR |
| iso_a3, iso_a2 | VARCHAR |
| continent, region_un, subregion, region_wb | VARCHAR |
| pop_est | DOUBLE |
| pop_rank, pop_year, gdp_md, gdp_year | INTEGER |
| economy, income_grp, sovereignt, type, formal_en | VARCHAR |
| geometry | GEOMETRY |

ne_10m_admin_1_states_provinces は 17 列。

| 列 | 型 |
|---|---|
| name, name_en, name_ja, name_alt, name_local, admin | VARCHAR |
| iso_a2, iso_3166_2, adm0_a3 | VARCHAR |
| type, type_en, region, region_sub | VARCHAR |
| latitude, longitude, area_sqkm | DOUBLE |
| geometry | GEOMETRY |

- 名前 (日本語の name_ja を含む) と分類と人口・GDP を残して列を絞った抜き出しに見える。元の配布物の列とは突き合わせていない。

## 中身

- admin_0 の pop_year は 110m で 2014〜2020、50m で 2011〜2020。gdp_year は 110m で 2007〜2019、50m で 2003〜2019。人口と GDP は国ごとに年がばらばらなので、そのまま横並びで比べない。
- continent は 8 種、income_grp は 5 種。
- type の内訳 (110m): Sovereign country 156, Country 10, Disputed 3, Dependency 3, Indeterminate 3, Sovereignty 2。50m では Dependency が 28 に増える。
- iso_a3 が `-99` の行が 110m で 5 (Norway, France, N. Cyprus, Somaliland, Kosovo)、50m で 8 (前の 5 に Indian Ocean Ter., Ashmore and Cartier Is., Siachen Glacier)。France と Norway が ISO3 で引けないのは Natural Earth 側の既知の癖と思われる (未確認)。WDI (worldbank/) と iso3 で結ぶと、WDI 217 のうち 50m で 212、110m で 167 が一致した。
- admin_1 は adm0_a3 で 251 の国と地域、type_en は 101 種。日本は 47 行 (都道府県、name_ja に「鹿児島県」など)。name_ja が NULL の行が 7。

## gpkg/ との重なり

- gpkg/natural_earth_vector.gpkg も Natural Earth だが、レイヤー一覧を 60 秒以内に読めなかったので、ここの 3 レイヤーが入っているかは確かめていない ([gpkg.md](gpkg.md))。
- ここの 3 つは列を絞った GeoParquet なので、仮に同じレイヤーが gpkg にあっても列の数と形式は違う。

## ライセンス

- Natural Earth の Terms of Use に「All versions of Natural Earth raster + vector map data found on this website are in the public domain.」とある。

## 12 ステップで使えそうな場面 (案)

- 1〜3 回帰と木: pop_est、gdp_md、income_grp、continent を使った小さな表の練習。worldbank/ と iso_a3 で結べば特徴量が増える。
- 4 データリーク: 大陸や地域で GroupKFold すると、近い国どうしが訓練とテストにまたがる効果が見える。
- 5 k-means/DBSCAN: admin_1 の latitude, longitude を点にして空間クラスタリングする。
- 7 Dijkstra/A*: 国や州の隣接 (境界の接触) からグラフを作り、最短経路を解く。
- 9 facility location: admin_1 の代表点を需要点や候補地にする。
- 地図の下絵としては 110m は粗く、50m か 10m が向く。
