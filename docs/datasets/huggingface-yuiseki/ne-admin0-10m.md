# ne-admin0-10m

2026-09-28 に読んで確かめた内容。

- <https://huggingface.co/datasets/yuiseki/ne-admin0-10m>
- Natural Earth 5.1.1 の 1:10m の国 (admin-0)、一次行政区画 (admin-1)、米国の郡 (admin-2) を、配布 zip と Parquet の両方で固めたもの。名前は admin0 だが 3 つの層が入っている。
- 最終更新 2026-09-26、コミット a891044。geo-triples-tokyo23 はこのデータセットの以前のコミット d1d37a1 を入力にしている。

## ファイル

Parquet は 3 つとも 50MB 以下なので全体をダウンロードして DuckDB 1.5.5 で読んだ。

| ファイル | 大きさ (バイト) | 行数 | 列 (geometry を含む) | 形 |
|---|---|---|---|---|
| v5.1.1/parquet/ne_10m_admin_0_countries.parquet | 6,120,439 | 258 | 173 | POLYGON 107 / MULTIPOLYGON 151 |
| v5.1.1/parquet/ne_10m_admin_1_states_provinces.parquet | 16,795,713 | 4,596 | 126 | POLYGON 3,945 / MULTIPOLYGON 651 |
| v5.1.1/parquet/ne_10m_admin_2_counties.parquet | 2,036,647 | 3,224 | 66 | POLYGON 3,112 / MULTIPOLYGON 112 |

- ほかに配布元の zip 3 つ (4,930,492 / 14,909,524 / 1,919,144 バイト、カードの md5 表と大きさが一致)、その .md5、VERSION.txt (中身は「5.1.1」)、manifest.json、provenance.yaml、LICENSE。
- 行グループは 1 つ、書き出しは parquet-cpp-arrow 20.0.0。GeoParquet の geo メタデータは無い (キー値メタデータが空)。geometry は WKB。
- CRS はファイルに記録が無い。zip の中に .prj がある (manifest.json に一覧) が中身は読んでいない。座標の範囲は admin-0 で経度 −180〜180、緯度 −90〜83.63 なので経緯度であることは確か。

## 列

- 列の数はカードの属性数 (168 / 121 / 61) に geometry と 4 つの由来の列 (geometrySource, datasetVersion, boundaryView, adminLevel) を足したものと合う。4 つの列は各層で定数 (Natural Earth、5.1.1、default/de-facto、admin-0 または admin-1)。
- admin-0 の主な列: ADM0_A3, ISO_A3, ISO_A3_EH, NAME, NAME_JA, TYPE, CONTINENT, POP_EST (DOUBLE), POP_YEAR, GDP_MD (BIGINT), GDP_YEAR, INCOME_GRP, WIKIDATAID ほか。
- admin-1 は列名が小文字 (adm0_a3, iso_3166_2, name_ja, wikidataid など)。admin-0 は大文字で、層によって綴りが違う (カードの注意どおり)。
- admin-2 には REGION, ISO_3166_2, TYPE_EN, NAME_JA, WIKIDATAID などがある。

## 中身

- admin-0: TYPE は Sovereign country 185、Dependency 33、Country 19、Indeterminate 12、Disputed 5、Sovereignty 2、Lease 2。CONTINENT 8 種。NAME_JA と WIKIDATAID は 258 行すべてにある。ISO_A3 が -99 の行が 22 (France、Norway、Kosovo、N. Cyprus、Somaliland、各種の係争地や基地など)、ISO_A3_EH が -99 の行は 14。POP_YEAR は 2009〜2020、GDP_YEAR は 1999〜2019 で国ごとにばらばら。
- admin-1: adm0_a3 で 251 の国と地域。どれも admin-0 の ADM0_A3 にある (孤立する行は 0)。日本は 47 行。wikidataid がある行 4,332 (カードと一致)、name_ja が空の行 7。
- admin-2: ADMIN はすべて United States of America。TYPE_EN は County 3,008、Municipio 77、Parish 64、City 41、Borough 13、Census Area 11、City and Borough 4 など。NAME_JA がある行 3,212 (カードと一致)。

## z.yuiseki.net/static/natural-earth/ との比べ

[../z-yuiseki-static/natural-earth.md](../z-yuiseki-static/natural-earth.md) の 3 ファイルと比べると次のとおり。

| | z.yuiseki.net | ここ |
|---|---|---|
| admin-0 | 110m (177 行) と 50m (242 行)、21 列 | 10m (258 行)、173 列 |
| admin-1 | 10m、4,596 行、17 列 | 10m、4,596 行、126 列 |
| admin-2 | 無し | 米国の郡 3,224 行 |
| 形式 | GeoParquet 1.0.0 | 素の Parquet (geo メタデータ無し) |
| 版 | ファイルに記録無し | 5.1.1 (VERSION.txt と datasetVersion 列) |

- admin-1 の 10m は行数と POLYGON/MULTIPOLYGON の内訳 (3,945 / 651) が z.yuiseki.net のものと同じで、name_ja が空の行も同じく 7。同じ元データを列を絞ったかどうかの違いと思われる (行ごとの突き合わせはしていない)。
- 版が分かる、列が全部ある、の 2 点でこちらが扱いやすい。GeoParquet として読みたいなら z.yuiseki.net のほうが楽。

## 気をつけること

- カードの「What is here」のファイル一覧に admin-2 の zip と Parquet が載っていないが、実物にはある (YAML の configs には v5.1.1.admin2 がある)。
- カードは admin-2 の内訳で Puerto Rico の municipios を 77 と書き、別の段落では「Puerto Rico's 78」と書いている。TYPE_EN が Municipio の行は 77 だった。
- admin-1 の iso_3166_2 (US-WA) と admin-2 の ISO_3166_2 (US-53) は同じ名前で値の形式が違う。結ぶなら admin-2 の REGION を使う (カードの注意どおり)。
- 国境は Natural Earth の既定の de facto の見方。

## ライセンス

- Hugging Face のタグは other (license_name: public-domain、リンクは Natural Earth の Terms of Use)。
- Natural Earth はパブリックドメインで、出典表示は求められていない (歓迎はされる)。

## 12 ステップで使えそうな場面 (案)

- 1〜3 回帰と木: admin-0 の POP_EST、GDP_MD、INCOME_GRP、CONTINENT などで小さな表の練習。列が 168 あるので、使える特徴量を選ぶ練習にもなる。年がばらばらな点に注意。
- 4 データリーク: CONTINENT や地域の列で GroupKFold。admin-2 なら州 (REGION) で GroupKFold して郡を行にする。
- 5 k-means/DBSCAN: admin-1 や admin-2 の代表点で空間クラスタリング。
- 6 PCA: admin-0 の数値列を並べて主成分を見る (欠損と -99 の扱いを先に決める)。
- 7 Dijkstra/A*: 国や州の隣接からグラフを作る。admin-2 の米国の郡は隣接グラフの練習に程よい大きさ。
- 10 CP-SAT: 米国の州や郡の地図の塗り分け。
