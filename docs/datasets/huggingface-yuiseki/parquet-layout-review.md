# yuiseki の HF データセットの Parquet レイアウト点検

2026-10-06 時点の点検記録である。読み取り専用で、Parquet のフッター（ファイル末尾のメタデータ）だけを読んだ。本文のデータは読んでいない。

## 方法

- `HfApi().list_datasets(author="yuiseki")` で一覧を取り、`dataset_info(files_metadata=True)` で各ファイルの Hub 上のサイズを得た。一覧は 50 件で、うち 5 件（spartqa-train-1k, alpaca-gpt4-500, jcommonsenseqa-train-1k, math_qa-train-1k, sql-create-context-train-1k）は非公開なので対象外とした。
- 公開 45 件はすべて Parquet を持っていた。Parquet を持たないデータセットはない。ただし worldpop-jp-2026-01 の Parquet は `parquet/files.parquet`（1024 行の目録）1 本だけで、本体の Parquet はない。
- Parquet は計 360 ファイル、11.8 GB である。337 ファイルは `/sata_hdd_24tb/hf_data/` 配下にサイズが一致するローカルコピーがあったのでそちらを読んだ。残る 23 ファイル（初期の小さな QA 系、osm-tag-corpus、osm-wiki、osm-wikidata-brand-*、wikidata-gazetteer、wikipedia-geotagged、wikivoyage-geotagged）はローカルに対応物がなく、DuckDB の `hf://` で Hub のフッターだけを読んだ。
- DuckDB 1.5.6 の `parquet_file_metadata` / `parquet_metadata` / `parquet_kv_metadata` / `parquet_schema` を使った。統計は `coalesce(stats_min_value, stats_min)` で読んだ。pyarrow が書いたファイルの文字列列は新形式の `stats_min_value` にしか値がなく、旧形式の `stats_min` だけを見ると「統計なし」に見えるためである。
- 並び順の判定には、各行グループ（以下 RG）の min/max だけを使った。値 v で絞るとき、`min <= v <= max` を満たす RG は読み飛ばせない。この RG の割合を「読む RG の割合」と呼ぶ。bbox による絞り込みは、lat 列と lon 列の範囲が両方とも重なる RG を数えた。実際の該当行がなくても範囲に入れば読むので、これは上限ではなく、min/max による枝刈りでの読み取り量そのものである（bloom filter による除外は別に扱う）。
- 補助指標として、列ごとに「重なり率」（各 RG の min と max を探索値として、それを含む RG の割合の平均）と「単調率」（隣り合う RG で前の max が次の min 以下である割合）を計算した。単調率 1.00 はその列で整列済み、重なり率が 0.9 以上なら実質的に枝刈りできないことを表す。
- 典型的な絞り込みの例として、東京の bbox には lat 35.5〜35.9、lon 139.5〜140.0 を使った。

## 全体の傾向

- 書き出し元は DuckDB 1.5.6 が 260 ファイル、DuckDB 1.5.5 が 8（osm-*-src の 8 本）、pyarrow 20.0.0 が 85、pyarrow 15.x と 23.0.1 が 7 である。圧縮は 2024 年ごろの datasets ライブラリ製の 7 本が SNAPPY で、それ以外はすべて ZSTD である。
- bloom filter があるのは DuckDB 1.5.5 で書いた osm-japan-src-2026-08 と osm-tokyo23-src-2026-08 だけである。DuckDB 1.5.6 で書いたファイルにはひとつもない。書き出し時の設定差か版の差かは確かめていない。
- GeoParquet の `geo` メタデータは 1.0.0 だけで、1.1 の `covering`（bbox 列）を持つファイルはない。bbox を struct 列として持つファイルもない。Parquet 本体の GEOMETRY 論理型による RG ごとの地理統計（`geo_bbox` / `geo_types`）も、全ファイルで空である。
- ジオメトリを WKB で持つのに `geo` メタデータがないファイルがある：osm-japan-src-2026-08 と osm-tokyo23-src-2026-08 の `way`（EPSG:3857 のメートル座標）、estat-boundary-2020 の 47 本、jp-admin-2026-09 の 2 本、ne-admin0-10m の 3 本。
- `geo` メタデータがあるファイルのうち、`crs` を明示しているのは gsi-global-map-jp（JGD2000 の PROJJSON）だけで、他は省略（既定の OGC:CRS84 扱い）である。
- 並び順は二極化している。DuckDB で作った統計系（geonames、meta-*、opencellid、mlit、undata-sdmx、un-docs、npa）は主キーで整列しており、国や都道府県での絞り込みが効く。pyarrow で作った大きいテキスト系・地名系（wikipedia-geotagged、wikidata-gazetteer、osm-wiki）と OSM は主な絞り込み列で整列しておらず、国や bbox で絞っても全 RG を読む。

## データセットごとの事実

列の略記：行/RG は「最小/中央値/最大」、bloom は bloom filter を持つ列チャンク数、geo は GeoParquet メタデータの有無と内容、重複座標はジオメトリ列と別に座標列を持つか、bbox 列は bbox/covering 列の有無である。サイズは Hub 上のファイルサイズである。

### 初期の小さな QA・テキスト系（Hub から読んだ）

| データセット / ファイル | 行数 | サイズ | RG（行/RG） | 圧縮 | bloom | 列 | geo | 並び順の判定 |
|---|---|---|---|---|---|---|---|---|
| onomatopoeia-ja `data/train-*.parquet` | 5,060 | 0.3 MB | 6（60/1000/1000） | SNAPPY | 0 | 4 | なし | 小さく判定不要 |
| onomatopoeia-ja-flat `data/train-*.parquet` | 10,346 | 0.2 MB | 11（346/1000/1000） | SNAPPY | 0 | 3 | なし | 小さく判定不要 |
| sake_qa `data/train-*.parquet` | 5,176 | 0.1 MB | 6（1000） | SNAPPY | 0 | 3 | なし | 小さく判定不要 |
| scp-jp-plain `data/train-*.parquet` | 999 | 5.3 MB | 1 | SNAPPY | 0 | 2 | なし | 1 RG |
| g-uc `data/train-*.parquet` | 3,344 | 0.3 MB | 4（1000） | SNAPPY | 0 | 6 | なし | episode で整列（単調率 1.00） |
| open2ch-livejupiter-qa `data/train-*.parquet` | 663,546 | 47.3 MB | 664（1000） | SNAPPY | 0 | 2 | なし | 絞り込み列なし。RG が約 70 KB と小さく数が多い |
| text2geoql `data/train-*.parquet` | 4,897 | 0.2 MB | 1 | SNAPPY | 0 | 4 | なし | 1 RG |
| osm-tokyo23-questions `data/train-*.parquet` | 215 | 0.03 MB | 1 | SNAPPY | 0 | 30 | なし | 1 RG |
| osm-tokyo23-qa-2026-08 `data/train-*.parquet` | 215 | 0.4 MB | 1 | SNAPPY | 0 | 18 | なし | 1 RG |

### OSM 由来のコーパス（Hub から読んだ）

| データセット / ファイル | 行数 | サイズ | RG（行/RG） | 圧縮 | bloom | 列 | geo | 並び順の判定 |
|---|---|---|---|---|---|---|---|---|
| osm-tag-corpus `data/train-*.parquet` | 31,913 | 6.6 MB | 32（913/1000/1000） | SNAPPY | 0 | 12 | なし | title（言語接頭辞つき）でほぼ整列。lang='ja' は 7/32 RG、key='amenity' は 21/32 RG |
| osm-wiki `data/train-*.parquet` | 78,178 | 159.2 MB | 79（178/1000/1000） | SNAPPY | 0 | 8 | なし | 未整列。lang='ja' は 79/79 RG |
| osm-wikidata-brand-tokyo23 `data/train-*.parquet` | 892 | 0.6 MB | 1 | SNAPPY | 0 | 9 | なし | 1 RG |
| osm-wikidata-brand-jp `data/train-*.parquet` | 1,859 | 2.2 MB | 2（859/1000） | SNAPPY | 0 | 9 | なし | 小さく判定不要 |

### osm-tokyo23-src-2026-08 と osm-japan-src-2026-08（ローカルを読んだ）

両者とも osm2pgsql の 4 表を DuckDB 1.5.5 で書いたもので、列は 70、ジオメトリは `way` 列の WKB（座標値は約 1.55e7 で EPSG:3857 のメートル）である。`geo` メタデータも bbox 列もない。`way` の統計は WKB のバイト列なので空間の絞り込みには使えない。

| ファイル | 行数 | サイズ | RG（行/RG） | 最大 RG | 圧縮 | bloom | way 列の割合 | 並び順の判定 |
|---|---|---|---|---|---|---|---|---|
| tokyo23 `planet_osm_line` | 347,735 | 26.0 MB | 3（101,975/122,880/122,880） | 9.3 MB | ZSTD | 151 | 89% | 小さい |
| tokyo23 `planet_osm_point` | 306,642 | 9.9 MB | 3 | 3.9 MB | ZSTD | 140 | 37% | 小さい |
| tokyo23 `planet_osm_polygon` | 1,437,105 | 118.6 MB | 12（85,425/122,880/122,880） | 11.3 MB | ZSTD | 558 | 90% | amenity='cafe' は 12/12 RG |
| tokyo23 `planet_osm_roads` | 33,113 | 4.4 MB | 1 | 4.4 MB | ZSTD | 36 | 87% | 1 RG |
| japan `planet_osm_line` | 12,259,617 | 1,551.3 MB | 100（94,497/122,880/122,880） | 37.1 MB | ZSTD | 4,752 | 96% | highway='motorway' は 100/100 RG |
| japan `planet_osm_point` | 3,720,141 | 102.7 MB | 31（33,741/122,880/122,880） | 4.3 MB | ZSTD | 1,574 | 46% | amenity='cafe' は 31/31 RG |
| japan `planet_osm_polygon` | 33,281,956 | 3,314.9 MB | 271（104,356/122,880/122,880） | 25.7 MB | ZSTD | 12,223 | 93% | 下記 |
| japan `planet_osm_roads` | 762,255 | 188.7 MB | 7（24,975/122,880/122,880） | 38.5 MB | ZSTD | 275 | 95% | 小さい |

japan `planet_osm_polygon` の詳細：osm_id は RG ごとに約 -2.1e7〜1.55e9 の全域にまたがり、整列していない（単調率 0.00）。タグ列の min/max はどれも全域にまたがり、amenity='cafe' も name='東京駅' も min/max では 271/271 RG を読む。bloom filter を引くと（`parquet_bloom_probe`）、name='東京駅' は 3/271 RG まで絞れるが、amenity='cafe' は 269/271、amenity='townhall' は 263/271、shop='convenience' は 271/271 で、頻出値にはほとんど効かない。point では name の bloom filter が 31 RG のうち 1 RG にしかなく、name='東京駅' でも 30/31 RG を読む。bbox で絞る手段はない。

### wikidata-gazetteer、wikipedia-geotagged、wikivoyage-geotagged（Hub から読んだ）

| データセット / ファイル | 行数 | サイズ | RG（行/RG） | 最大 RG | 圧縮 | bloom | 列 | geo | 重複座標 | 並び順の判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| wikidata-gazetteer `names.parquet` | 62,506,107 | 508.4 MB | 126（4,401/500,003/500,168） | 5.9 MB | ZSTD | 0 | 4 | なし | なし | qid は部分的に整列（単調率 0.27）。qid='Q1490' は 63/126 RG、lang='ja' は 126/126 RG |
| wikidata-gazetteer `places.parquet` | 12,205,328 | 355.0 MB | 25（205,328/500,000/500,000） | 16.2 MB | ZSTD | 0 | 16 | なし | lat/lon のみ（ジオメトリ列なし） | 未整列。country='Q17' も東京 bbox も 25/25 RG |
| wikipedia-geotagged `20260901.en/*`（5 本） | 1,374,056 | 1,750.1 MB | 275（5,000） | 60.5 MB | ZSTD | 0 | 23 | なし | lat/lon のみ | id でほぼ整列（単調率 0.82）。gt_country='JP' は 275/275 RG、東京 bbox は 274/275 RG |
| wikipedia-geotagged `20260901.ja/*`（2 本） | 218,496 | 454.1 MB | 44（5,000） | 39.2 MB | ZSTD | 0 | 23 | なし | lat/lon のみ | gt_country='JP' も東京 bbox も 44/44 RG |
| wikivoyage-geotagged `20260901.en/*` | 29,505 | 101.6 MB | 6（4,505/5,000/5,000） | 20.7 MB | ZSTD | 0 | 23 | なし | lat/lon のみ | 東京 bbox は 6/6 RG |

places.parquet では lat と lon の列が合わせて 184 MB あり、ファイルの 52% を占める。値の並びがばらばらで、倍精度がほとんど圧縮されていないと見られる。lat の最大値は 351.37、lon は -360〜360 の範囲に値がある。wikipedia-geotagged の lon も -330〜359.91 の値を含む（gt_globe には地球以外の天体もあるが、その分かどうかは確かめていない）。

### 地理トリプル系（ローカルを読んだ）

| データセット / ファイル | 行数 | サイズ | RG（行/RG） | 圧縮 | bloom | 列 | geo | 並び順の判定 |
|---|---|---|---|---|---|---|---|---|
| geo-triples-tokyo23 `cpt` / `probe` / `triples` | 483,922 / 8,854 / 510,616 | 5.4 / 0.3 / 2.2 MB | 各 1 | ZSTD | 0 | 11 / 12 / 25 | なし | 1 RG（小さい） |
| geo-triples-japan `cpt` | 4,678,910 | 62.5 MB | 5（484,606/1,048,576/1,048,576） | ZSTD | 0 | 14 | なし | form で整列。form='en' は 1/5 RG |
| geo-triples-japan `probe` | 68,025 | 2.1 MB | 1 | ZSTD | 0 | 15 | なし | 1 RG |
| geo-triples-japan `triples` | 3,286,232 | 21.6 MB | 4（140,504/1,048,576/1,048,576） | ZSTD | 0 | 25 | なし | subject_id で整列。subject_layer='jp-pref' は 1/4 RG（行の 4%） |
| geo-triples-jp-gov `cpt` / `probe` / `triples` | 165,670 / 1,807 / 162,810 | 1.5 / 0.05 / 0.8 MB | 各 1 | ZSTD | 0 | 15 / 15 / 29 | なし | 1 RG（小さい） |

### 日本の行政区域・住所・境界（ローカルを読んだ）

| データセット / ファイル | 行数 | サイズ | RG | 圧縮 | 列 | geo | 重複座標 | 備考 |
|---|---|---|---|---|---|---|---|---|
| abr-src-2026-09 `mt_city_all` / `mt_pref_all` | 1,918 / 47 | 0.1 / 0.01 MB | 各 1 | ZSTD | 16 / 7 | なし | なし | 小さい |
| abr-src-2026-09 `mt_city_pos_all` / `mt_pref_pos_all` | 1,918 / 47 | 0.04 / 0.01 MB | 各 1 | ZSTD | 10 | なし | rep_lat/rep_lon（ジオメトリ列なし） | 小さい |
| abr-src-2026-09 `mt_town_all` / `mt_town_fullset_all` | 727,429 | 9.3 MB | 1 | ZSTD | 38 / 52 | なし | なし | 72 万行が 1 RG |
| abr-src-2026-09 `mt_town_pos_all` | 337,641 | 3.8 MB | 1 | ZSTD | 18 | なし | rep_lat/rep_lon（ジオメトリ列なし） | 1 RG |
| estat-boundary-2020 `parquet/r2ka01〜47`（47 本） | 1,010〜22,967 | 2.7〜18.1 MB（計 372 MB） | 各 1 | ZSTD | 30 | なし（WKB の geometry 列あり） | なし（X_CODE/Y_CODE は文字列の代表点） | 都道府県ごとのファイル分割が実質的な分割になっている |
| jp-admin-2026-09 `municipalities` | 1,918 | 149.1 MB | 1（1 RG で 149 MB） | ZSTD | 25 | なし（WKB の geometry 列あり） | rep_lat/rep_lon は代表点で重複ではない | geometry 列が 148.9 MB |
| jp-admin-2026-09 `prefectures` | 47 | 79.7 MB | 1（1 RG で 80 MB） | ZSTD | 10 | なし（WKB の geometry 列あり） | 同上 | geometry 列が 79.7 MB |

### 世界の境界・空港・駅・GSI（ローカルを読んだ）

| データセット / ファイル | 行数 | サイズ | RG | 圧縮 | 列 | geo | 重複座標 | 備考 |
|---|---|---|---|---|---|---|---|---|
| ne-admin0-10m `ne_10m_admin_0_countries` | 258 | 6.1 MB | 1 | ZSTD | 173 | なし（WKB あり） | LABEL_X/Y は代表点 | |
| ne-admin0-10m `ne_10m_admin_1_states_provinces` | 4,596 | 16.8 MB | 1 | ZSTD | 126 | なし（WKB あり） | latitude/longitude は代表点 | 1 RG で 16.8 MB |
| ne-admin0-10m `ne_10m_admin_2_counties` | 3,224 | 2.0 MB | 1 | ZSTD | 66 | なし（WKB あり） | 同上 | |
| ourairports-2026-08 `airports` | 86,002 | 5.0 MB | 1 | ZSTD | 20 | 1.0.0、Point、bbox あり、crs 省略、covering なし | latitude_deg/longitude_deg（1.0 MB）＋geometry（1.1 MB） | |
| ourairports-2026-08 `navaids` | 11,008 | 0.5 MB | 1 | ZSTD | 21 | 1.0.0、Point、bbox あり、crs 省略 | latitude_deg/longitude_deg＋geometry | |
| ourairports-2026-08 `runways` | 48,203 | 1.0 MB | 1 | ZSTD | 20 | なし | 両端の緯度経度 4 列（ジオメトリ列なし） | |
| ourairports-2026-08 その他 4 本 | 249〜30,343 | 0.01〜1.7 MB | 各 1 | ZSTD | 6〜8 | なし | なし | |
| ekidata-jp `station.*`（6 本） | 10,941〜10,962 | 各 0.6 MB | 各 1 | ZSTD | 16 | 1.0.0、Point、bbox あり、crs 省略 | lon/lat＋geometry | |
| ekidata-jp `line.*`（5 本） | 622〜624 | 0.03 MB | 各 1 | ZSTD | 13 | なし | lon/lat（中心点） | |
| ekidata-jp `company.*` / `join.*` / `pref`（12 本） | 48〜10,189 | 0.1 MB 以下 | 各 1 | ZSTD | 2〜10 | なし | なし | |
| gsi-global-map-jp `vector-2.0〜2.2/*`（45 本） | 29〜31,642 | 3.1 MB 以下 | 各 1 | ZSTD | 4〜11 | 1.0.0、型あり、bbox あり、crs は JGD2000 を明示 | なし | 規約上もっとも整っている |

### 点データ・メッシュ・事故（ローカルを読んだ）

| データセット / ファイル | 行数 | サイズ | RG（行/RG） | 最大 RG | 圧縮 | bloom | 列 | geo | 重複座標 | 並び順の判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| geonames `geoname/part-00〜03`（4 本） | 13,472,217 | 580.4 MB | 136（22,387/100,352/100,352） | 7.2 MB | ZSTD | 0 | 20 | 1.0.0、Point、bbox あり、crs 省略 | latitude/longitude（計 108 MB）＋geometry（計 137 MB） | country_code で整列。country_code='JP' は 2/136 RG、東京 bbox は 27/136 RG |
| geonames `alternate_names` | 19,219,062 | 170.5 MB | 192（51,830/100,352/100,352） | | ZSTD | 0 | 10 | なし | なし | geonameid で整列。geonameid=1850147 は 1/192 RG、isolanguage='ja' は 192/192 RG |
| geonames `hierarchy` | 519,183 | 1.5 MB | 6 | | ZSTD | 0 | 3 | なし | なし | parent_id で整列 |
| geonames `admin_code5` | 78,514 | 0.2 MB | 1 | | ZSTD | 0 | 2 | なし | なし | 1 RG |
| opencellid `cell_towers` | 5,502,843 | 126.5 MB | 45（96,123/122,880/122,880） | 3.1 MB | ZSTD | 0 | 15 | 1.0.0、Point、bbox あり、crs 省略 | lon/lat（33.5 MB）＋geometry（39.4 MB） | mcc で整列。mcc=440 は 7/45 RG、東京 bbox は 10/45 RG |
| mlit-1km-fromto-2022-01 `monthly_mdp_mesh1km` | 38,079,507 | 104.1 MB | 380（46,099/100,352/100,352） | 0.4 MB | ZSTD | 0 | 8 | なし | なし | prefcode で整列。prefcode='13' は 6/380 RG、mesh1kmid='53394611' は 65/380 RG、2020 年 4 月は 180/380 RG |
| mlit-1km-fromto-2022-01 `monthly_fromto_city` | 2,340,980 | 5.5 MB | 24 | 0.3 MB | ZSTD | 0 | 8 | なし | なし | prefcode で整列 |
| mlit-1km-fromto-2022-01 `attribute_mesh1km` | 775,000 | 7.0 MB | 8 | 1.1 MB | ZSTD | 0 | 11 | 1.0.0、Polygon、bbox あり、crs 省略 | 中心と四隅の緯度経度 6 列（文字列型）＋geometry（5.4 MB） | version, mesh1kmid の順。prefcode='13' は 7/8 RG |
| mlit-1km-fromto-2022-01 マスタ 2 本 | 94 / 3,792 | 0.01 MB | 各 1 | | ZSTD | 0 | 5〜6 | なし | なし | |
| npa-traffic-accidents `20xx/honhyo`（7 本） | 287,023〜381,237 | 14.6〜18.1 MB | 3〜4 | 5.2 MB | ZSTD | 0 | 61〜71 | 1.0.0、Point、bbox あり、crs 省略 | 元の「地点 緯度/経度」文字列＋latitude/longitude＋geometry（2025 年で計 9.8 MB / 14.8 MB） | 都道府県コードで整列。2025 年で都道府県コード='30' は 1/3 RG、東京 bbox は 2/3 RG |
| npa-traffic-accidents `20xx/hojuhyo`, `kosokuhyo`（14 本） | 4,649〜88,961 | 0.3 MB 以下 | 各 1 | | ZSTD | 0 | 15〜17 | なし | なし | 小さい |
| worldpop-jp-2026-01 `files.parquet` | 1,024 | 0.1 MB | 1 | | ZSTD | 0 | 23 | なし | なし | 目録のみ |

### 移動・紛争（ローカルを読んだ）

| データセット / ファイル | 行数 | サイズ | RG（行/RG） | 最大 RG | 圧縮 | bloom | 列 | geo | 重複座標 | 並び順の判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| meta-move-dist `movement_distribution_2026` | 11,735,260 | 89.1 MB | 117（94,428/100,352/100,352） | | ZSTD | 0 | 8 | なし | なし | country, gadm_id で整列。country='JPN' は 6/117 RG |
| meta-range-maps-2022-05 `movement_range_2020/2021/2022` | 5,229,342 / 5,287,242 / 1,662,956 | 38.7 / 38.3 / 12.1 MB | 53 / 53 / 17 | 0.8 MB | ZSTD | 0 | 10 | なし | なし | country で整列。2020 年版で country='JPN' は 3/53 RG |
| ucdp-ged `19.1〜26.1/ged`（8 本、代表は 26.1） | 417,968 | 35.6 MB | 9（8,368/51,200/51,200） | 5.8 MB | ZSTD | 0 | 50 | 1.0.0、Point、bbox あり、crs 省略 | latitude/longitude＋geom_wkt（WKT 文字列）＋geometry、さらに where_coordinates（計 6.0 MB / 35.6 MB） | country_id で整列（単調率 1.00）。ただし国名の country では Syria が 9/9 RG、year=2024 も 9/9 RG、ウクライナ東部 bbox は 2/9 RG |

### 国別統計（ローカルを読んだ）

| データセット / ファイル | 行数 | サイズ | RG（行/RG） | 圧縮 | bloom | 列 | 並び順の判定 |
|---|---|---|---|---|---|---|---|
| worldbank-wdi `20xx/data`（7 版、代表は 2026-10-01） | 8,790,085 | 50.4 MB | 88（59,461/100,352/100,352） | ZSTD | 0 | 4 | indicator_code で整列。indicator_code='NY.GDP.MKTP.CD' は 2/88 RG だが、country_code='JPN' は 88/88 RG、year=2020 も 88/88 RG |
| worldbank-wdi `20xx/footnotes`（7 本） | 744,775〜821,921 | 3.0〜4.0 MB | 8〜9 | ZSTD | 0 | 5 | 未整列（CountryCode の重なり率 0.56） |
| worldbank-wdi `countries` / `country_series` / `series` / `series_time`（28 本） | 133〜7,643 | 0.5 MB 以下 | 各 1 | ZSTD | 0 | 3〜31 | 小さい |
| undp-hdr `composite_indices` | 206 | 1.5 MB | 1 | ZSTD | 0 | 1,112 | 1 RG（横長） |
| undp-hdr `composite_indices_long` | 200,004 | 1.0 MB | 2（77,124/122,880） | ZSTD | 0 | 6 | indicator で整列。iso3='JPN' は 2/2 RG |
| unhcr-refugee-stats `population` | 138,893 | 0.6 MB | 2（16,013/122,880） | ZSTD | 0 | 14 | Year で整列。Year=2024 は 1/2 RG |
| unhcr-refugee-stats その他 6 本 | 232〜120,597 | 1.0 MB 以下 | 各 1 | ZSTD | 0 | 5〜20 | 1 RG |
| maddison-project `2023/full_data` | 131,144 | 0.2 MB | 2 | ZSTD | 0 | 6 | countrycode で整列 |
| maddison-project その他 5 本 | 147〜21,682 | 0.1 MB 以下 | 各 1 | ZSTD | 0 | 3〜8 | 1 RG |
| pwt `8.0〜11.0/*`（41 本） | 8,059〜393,970 | 2.1 MB 以下 | 1（10.0, 10.01, 11.0 の esh_bilateral_cor の 3 本だけ 3〜4） | ZSTD | 0 | 3〜52 | 小さい |
| un-statistical-yearbook `syb61`, `syb68/*`, `sources`, `tables`（24 本） | 33〜8,700 | 0.05 MB 以下 | 各 1 | ZSTD | 0 | 7〜16 | 小さい |
| undata-sdmx `NA_MAIN` | 1,161,845 | 5.9 MB | 10 | ZSTD | 0 | 40 | REF_AREA で整列。REF_AREA='JP' は 1/10 RG、TIME_PERIOD='2020' は 10/10 RG |
| undata-sdmx `DF_UNDATA_ENERGY` | 1,919,234 | 4.7 MB | 16 | ZSTD | 0 | 11 | REF_AREA で整列。REF_AREA='392' は 1/16 RG |
| undata-sdmx `DF_UNData_EnergyBalance` / `DF_SEEA_ENERGY` / `DF_SEEA_AEA` | 1,045,891 / 1,134,569 / 134,248 | 4.3 / 0.9 / 0.1 MB | 9 / 10 / 2 | ZSTD | 0 | 10〜32 | REF_AREA で整列 |
| undata-sdmx `codelists` / `compilers` / `components` | 9,907 / 726 / 120 | 0.1 MB 以下 | 各 1 | ZSTD | 0 | 7〜11 | 小さい |
| env-redlist-jp `5th/*`（8 本） | 63〜2,222 | 0.1 MB 以下 | 各 1 | ZSTD | 0 | 4〜178 | 小さい |

### 文書（ローカルを読んだ）

| データセット / ファイル | 行数 | サイズ | RG（行/RG） | 圧縮 | bloom | 列 | 並び順の判定 |
|---|---|---|---|---|---|---|---|
| un-docs `documents.parquet` | 39,363 | 409.4 MB | 20（1,363/2,000/2,000） | ZSTD | 0 | 15 | id で整列。id='S/RES/2532(2020)' は 1/20 RG、date_adopted が 2020 年のものは 6/20 RG |

## 典型的な絞り込みで読む RG の割合（まとめ）

| データセット / 対象 | 絞り込み | 読む RG |
|---|---|---|
| osm-japan-src-2026-08 polygon（3.3 GB） | 東京 bbox | 絞れない（271/271、統計がない） |
| osm-japan-src-2026-08 polygon | amenity='cafe'（bloom 込み） | 269/271 |
| osm-japan-src-2026-08 polygon | name='東京駅'（bloom 込み） | 3/271 |
| wikipedia-geotagged en（1.75 GB） | gt_country='JP' / 東京 bbox | 275/275 / 274/275 |
| wikipedia-geotagged ja（454 MB） | gt_country='JP' / 東京 bbox | 44/44 / 44/44 |
| wikidata-gazetteer places（355 MB） | country='Q17' / 東京 bbox | 25/25 / 25/25 |
| wikidata-gazetteer names（508 MB） | qid='Q1490' / lang='ja' | 63/126 / 126/126 |
| geonames geoname（580 MB） | country_code='JP' / 東京 bbox | 2/136 / 27/136 |
| geonames alternate_names（171 MB） | geonameid=1850147 | 1/192 |
| opencellid（127 MB） | mcc=440 / 東京 bbox | 7/45 / 10/45 |
| mlit monthly_mdp_mesh1km（104 MB） | prefcode='13' / メッシュ 1 つ / 年月 1 つ | 6/380 / 65/380 / 180/380 |
| meta-move-dist（89 MB） | country='JPN' | 6/117 |
| worldbank-wdi data（50 MB × 7 版） | 指標 1 つ / country_code='JPN' / year=2020 | 2/88 / 88/88 / 88/88 |
| ucdp-ged 26.1（36 MB） | country='Syria' / year=2024 / 小 bbox | 9/9 / 9/9 / 2/9 |
| npa honhyo 2025（15 MB） | 都道府県コード='30' / 東京 bbox | 1/3 / 2/3 |
| un-docs（409 MB） | 文書 id 1 つ / 2020 年採択 | 1/20 / 6/20 |
| undata-sdmx NA_MAIN（6 MB） | REF_AREA='JP' / TIME_PERIOD='2020' | 1/10 / 10/10 |
| osm-wiki（159 MB） | lang='ja' | 79/79 |
| jp-admin-2026-09 municipalities（149 MB） | 市区町村 1 つ | 1/1（1 RG なので 149 MB の geometry 列全体） |

## 改善候補（効果の大きい順。決定はしない）

1. osm-japan-src-2026-08（5.16 GB、4 表）と osm-tokyo23-src-2026-08（159 MB）
   - 現状：`way` が EPSG:3857 の WKB なのに `geo` メタデータがなく、CRS がどこにも書かれていない。bbox 列も RG ごとの地理統計もなく、osm_id もタグ列も整列していないので、空間の絞り込みでは常に全 RG（polygon なら 3.3 GB）を読む。bloom filter は稀な name には効くが、amenity などの頻出値には効かない。
   - 案：ジオメトリの bbox 中心の Hilbert 値（DuckDB spatial の `ST_Hilbert` など）で並べ替え、`bbox` struct 列（xmin, ymin, xmax, ymax）を加え、GeoParquet 1.1 の `geo` メタデータに `covering` と EPSG:3857 の PROJJSON `crs` を書く。EPSG:4326 へ変換した版を別に用意するかどうかも選択肢になる。RG の行数は現状の 122,880 のままでよい。
   - 期待効果：東京都区部程度の bbox で読む RG は、日本全体のうち該当地域が占める割合の程度（数%〜十数%）まで減る見込みである。並べ替えでジオメトリの局所性が上がり、ZSTD の圧縮率も上がる可能性がある。CRS が明示されることで、GeoPandas や QGIS がそのまま正しく読める。
2. wikipedia-geotagged（en 1.75 GB、ja 454 MB）
   - 現状：id でほぼ整列しており、gt_country でも lat/lon でも全 RG を読む。RG は 5,000 行固定で、本文の長さ次第で最大 60.5 MB になる。
   - 案：言語ごとに gt_country、次に lat/lon の Hilbert 値で並べ替える。RG は行数ではなくバイト数（例えば 32〜64 MB）を目安にそろえる。点ジオメトリと GeoParquet メタデータを加えるかは別の判断になる。
   - 期待効果：gt_country='JP' は en で全体の数% の RG に、東京 bbox はさらに少なくなる。Hub 越しに国単位で取る用途で、転送量が 1 桁以上減る見込みである。
3. wikidata-gazetteer（places 355 MB、names 508 MB）
   - 現状：places は country も lat/lon も未整列で、country='Q17' も東京 bbox も 25/25 RG を読む。lat と lon の列だけで 184 MB（52%）あり、ほとんど圧縮されていない。names は lang='ja' が 126/126 RG、qid 1 件でも 63/126 RG を読む。
   - 案：places を country、次に lat/lon の Hilbert 値で並べ替える。names は qid（places との結合キー）で並べ替える。lang で引く用途が主なら lang、qid の順にする。
   - 期待効果：places の国単位の取得は 1〜数 RG になる。lat/lon が空間的に近い順に並ぶので、2 列の 184 MB はかなり縮む見込みである（どこまで縮むかは実測が要る）。names の qid 引きは 1 RG になる。
4. jp-admin-2026-09（municipalities 149 MB、prefectures 80 MB）
   - 現状：どちらも 1 RG で、geometry 列が 1 つの列チャンクに入っている。市区町村 1 つのポリゴンを Hub から取るにも 149 MB を読む。`geo` メタデータもない。
   - 案：lg_code 順のまま、RG を都道府県ごと程度（数十行、数 MB）に切る。`geo` メタデータと bbox 列を加える。CRS は元の境界 Shapefile の .prj が 47 本とも JGD2000 で、EPSG:4612 だった (2026-10-06 に確かめた。当初この欄に書いた EPSG:6668 は誤り)。
   - 期待効果：市区町村 1 つ、または都道府県 1 つの取得が全体の約 1/47 の読み取りで済む。GIS ツールがジオメトリを自動認識する。
5. worldbank-wdi `data.parquet`（7 版 × 約 50 MB）
   - 現状：indicator_code で整列しているので指標 1 つなら 2/88 RG だが、国 1 つや年 1 つでは 88/88 RG を読む。
   - 案：主な用途が「指標を選ぶ」なら現状が正しい。国で引く用途が主なら country_code、indicator_code の順に並べ替える。両方が要るなら、国順の写しを別ファイルで持つ方法もある。
   - 期待効果：国で引く場合は 1〜2 RG になる。ファイルが 50 MB と小さいので、効果はローカル利用より Hub 越しの利用で目立つ。
6. 重複する座標列（容量の削減）
   - npa-traffic-accidents honhyo（7 本）：元の「地点 緯度/経度」の文字列、latitude/longitude、geometry の 3 通りで同じ位置を持ち、2025 年版では計 9.8 MB と 14.8 MB の 66% を占める。
   - ucdp-ged（8 本）：latitude/longitude、geom_wkt、geometry、where_coordinates で、26.1 版では計 6.0 MB（17%）。
   - geonames geoname（4 本）：latitude/longitude 計 108 MB と geometry 計 137 MB で、580 MB の 42%。
   - opencellid：lon/lat 33.5 MB と geometry 39.4 MB で、126.5 MB の 58%。
   - mlit attribute_mesh1km：中心と四隅の緯度経度 6 列を文字列で持ち、さらにポリゴンを持つ。メッシュコードから計算できる。
   - ourairports airports/navaids、ekidata station：小さいので影響は小さい。
   - 注意：点データでは lon/lat 列が実質的な bbox になっていて、WKB の geometry 列には統計がない。lon/lat を消すと、東京 bbox で 10/45 RG まで絞れている opencellid などの枝刈りが効かなくなる。消すなら GeoParquet 1.1 の covering（bbox struct 列）か native の点エンコーディング（x, y の 2 列に統計がつく）へ置き換える必要がある。DuckDB 1.5.6 がどちらを書けるかは確かめていない。重複を残す選択も合理的で、その場合は README に「lat/lon は絞り込み用」と書くと誤解が減る。
   - 期待効果：npa と geonames と opencellid で計 200 MB 前後が減る見込みである（置き換え先の列の分は差し引く）。
7. ジオメトリがあるのに `geo` メタデータがないファイル（estat-boundary-2020 の 47 本、ne-admin0-10m の 3 本）
   - 現状：WKB の geometry 列はあるが、GeoParquet として認識されない。CRS も書かれていない。どれも 1 RG で、最大 18.1 MB（estat r2ka01）と 16.8 MB（ne admin_1）である。
   - 案：`geo` メタデータ（ジオメトリ型、bbox、CRS）を書き足す。estat は都道府県ごとのファイル分割が既に効いているので、並べ替えの必要は小さい。
   - 期待効果：主に相互運用性である。枝刈りの効果は小さい。
8. CRS の省略
   - 現状：`geo` メタデータを持つファイルのうち gsi-global-map-jp 以外は `crs` を省略しており、既定の OGC:CRS84 として扱われる。npa の座標が JGD2011 由来なら、厳密には CRS84 ではない。
   - 案：元データの測地系を確かめ、CRS84 でないものは PROJJSON を書く。
   - 期待効果：正確さの担保。差はメートル単位以下であり、実用上の影響は小さい。
9. 小さすぎる RG（初期の datasets ライブラリ製）
   - 現状：open2ch-livejupiter-qa は 47 MB を 664 RG（各 1,000 行、約 70 KB）に分けており、SNAPPY 圧縮である。osm-wiki も 1,000 行ずつ 79 RG である。
   - 案：再出力の機会があれば、ZSTD で 10〜50 万行程度の RG にする。
   - 期待効果：フッターが小さくなり、Hub 越しの読み取りでリクエスト数が減る。絞り込み列がないので、枝刈りの効果はない。
10. 大きすぎる単一 RG（小規模）
    - abr-src-2026-09 の mt_town_all / mt_town_fullset_all（72 万行で 1 RG）、geo-triples-tokyo23 の cpt / triples（48〜51 万行で 1 RG）。都道府県コードや subject で並べたうえで、RG を 10 万行程度に切ると、部分取得ができるようになる。どれも 10 MB 未満なので、優先度は低い。

## 並べ替えるときの注意：DuckDB 1.5.6 の -0.0

DuckDB 1.5.6 では、DOUBLE 列で直接 `ORDER BY` すると -0.0 が 0.0 として返ってくる。符号を保つには `::varchar` を通して並べる必要がある。したがって、上の候補で並べ替えて書き直すときは、必ず元のファイルと突き合わせて値が変わっていないことを確かめる必要がある（例えば、各 DOUBLE 列で `x::varchar = '-0.0'` の行数を書き直しの前後で比べる）。

今回の統計を見た範囲では、RG の min か max に -0.0 が現れている列が次のとおりある。統計の端に出ないだけで -0.0 を含む列は、これ以外にもありうる。

- wikidata-gazetteer `places.parquet` の population と area（上記の改善候補 3 の対象）
- ne-admin0-10m `ne_10m_admin_0_countries` の MIN_ZOOM と POP_EST
- geo-triples-tokyo23 / geo-triples-japan / geo-triples-jp-gov の `triples.parquet` の outside_ratio
