# osm-japan-src-2026-08

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/osm-japan-src-2026-08/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/osm-japan-src-2026-08`
- 日本全国の OSM を 2026-08-31 の planet から切り出して凍結したもの。osm-tokyo23-src-2026-08 の全国版で、スキーマも手順も同じ。
- 最終更新 2026-09-25。コードは GitHub の `yuiseki/osm-japan-src-2026-08`。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| japan-260831.osm.pbf | 2,807,823,198 | 切り出した OSM。md5 ファイルの値は `2f803a54de5bdeb5ecbbb740c9b5100d` |
| japan-260831.osm.pbf.md5 | 55 | 上の md5 |
| japan_osm_boundary.geojson | 206,023 | 切り出しに使った日本の外形 (`admin_level=2` かつ `ISO3166-1=JP`) |
| parquet/planet_osm_point.parquet | 102,663,497 | 点 |
| parquet/planet_osm_line.parquet | 1,551,330,352 | 線 |
| parquet/planet_osm_polygon.parquet | 3,314,881,217 | 面 |
| parquet/planet_osm_roads.parquet | 188,747,381 | 低ズーム描画用の主要な線 |
| parquet/checksums.md5 | 330 | Parquet の md5 |
| provenance.yaml | 5,367 | 元データ、道具の版、行数、検証 |
| LICENSE | 1,550 | ODbL の表示 |

## 行数と列

フッターを DuckDB 1.5.5 で URL から読んだ (1 本 5 秒前後)。4 本とも書いた道具は `DuckDB version v1.5.5`。

| 表 | 行数 | row group |
|---|---|---|
| planet_osm_point | 3,720,141 | 31 |
| planet_osm_line | 12,259,617 | 100 |
| planet_osm_polygon | 33,281,956 | 271 |
| planet_osm_roads | 762,255 | 7 |

行数はカードと provenance.yaml の値と一致した。列は 4 表とも 70 個で、osm-tokyo23-src-2026-08 の同じ表と列名も型も完全に一致した (`way` は WKB の BLOB で EPSG:3857、`tags` は JSON 文字列)。

どれも 50MB を超えるので全体はダウンロードしていない。point だけ URL から列を絞って集計した。

- point の非 NULL 数: `name` 1,449,798、`highway` 1,016,426、`amenity` 670,563、`shop` 222,243。
- point の `amenity` 上位: restaurant 89,950、vending_machine 51,223、bench 48,885、place_of_worship 41,299、kindergarten 24,944、social_facility 24,922、cafe 24,890、pub 22,193、post_office 21,370、bicycle_rental 20,369。
- `amenity` 付きの点を経緯度に直した範囲は経度 121.49 から 145.81、緯度 24.06 から 46.62 (21 秒)。

## 元データと基準日

- planet-260831.osm.pbf (94,612,383,571 バイト、md5 `c67437924cf55de40e8708c7192f354d`) から。z.yuiseki.net の `openstreetmap/planet/` にあるものと同じ大きさと md5。
- 切り出しは 2 段階 (provenance.yaml): 広めの矩形 (経度 122.0 から 154.5、緯度 20.0 から 46.2) で切ってから、同じ planet から作った日本の外形で `complete_ways` で切る。osmium-tool 1.16.0。
- provenance.yaml の記録: nodes 318,225,406、ways 45,679,976、relations 241,943、最古の時刻 2007-07-03T14:12:14Z、最新 2026-08-30T23:59:34Z。これは読んだだけで、pbf は数えていない。
- Parquet は osm2pgsql 1.11.0 (`--hstore --cache 8000 --flat-nodes`、EPSG:3857) で PostGIS 16-3.4 に入れ、DuckDB 1.5.5 で書き出したもの。
- z.yuiseki.net の `region/japan-260423.osm.pbf` (Geofabrik 抽出、2026-04-23) とは別物。こちらは OSM 自身の国境で切っており、基準日も 4 か月新しい。
- このデータセットから作られたもの: osm-wikidata-brand-jp。

## ライセンス

- カードとタグ: `odbl` (ODbL 1.0)。

## 気づいたこと

- 座標は EPSG:3857。日本は緯度 24 度から 45 度にまたがるので、3857 の 1m が実際に何 m かは場所で変わる (カードでは沖縄 1.11、東京 1.24、稚内 1.41)。都道府県をまたいで距離や面積を比べるなら必ず変換する。
- `amenity` 付きの点に経度 121.49 (台湾の近く) や緯度 46.62 の点がある。`complete_ways` で国境をまたぐ way のノードが入ったものと思われるが、個別には確かめていない。
- polygon は 3.3GB、line は 1.5GB ある。全体を使うなら手元に落とすか、pbf から必要な範囲だけ osmium で切るほうが軽い。

## 12 ステップでの使いどころ (案)

- 1, 2, 3, 11: 都道府県や市区町村ごとに `amenity` や `shop` の件数を数えた表を作り、人口など別のデータと組み合わせて回帰。行政界は polygon の `boundary='administrative'` にある。
- 4: 市区町村の単位で、ランダム分割と都道府県ごとの分割 (空間ブロック) で CV の成績を比べる。
- 5: point の cafe や restaurant を DBSCAN にかけ、都市のまとまりを全国で切り出す。
- 6: 市区町村 x `amenity` の件数行列で PCA。
- 7, 8, 9: 全国の道路網は大きすぎるので、まず osm-tokyo23-src-2026-08 で練習してから、ここの pbf から一県を切り出して使う。
- 10, 12: 直接の材料は無い。
