# NYC TLC Trip Record Data と taxi zones

2026-09-29 に読んで確かめた内容。ニューヨーク市のタクシーと配車サービスの乗車記録で、台東区と 23 区の外の題材になる。

- 配布ページ: <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>
- 公開者: ニューヨーク市タクシー・リムジン委員会 (TLC)。問い合わせ先は research@tlc.nyc.gov
- 同じデータの AWS Open Data Registry の登録: <https://registry.opendata.aws/nyc-tlc-trip-records-pds/>
- ゾーン境界の GeoParquet 版: <https://source.coop/cholmes/nyc-taxi-zones>

## 乗車記録

URL は `https://d37ci6vzurychx.cloudfront.net/trip-data/{種類}_tripdata_YYYY-MM.parquet`。1 か月 1 ファイルで、2009 年から続いている。約 2 か月遅れで足される。

| 種類 | 中身 | 2026-07 の行数 | 大きさ | 行グループ |
|---|---|---:|---:|---:|
| yellow | イエローキャブ | 3,530,109 | 61.7MB | 4 |
| green | 流し営業が区域限定のタクシー | 41,252 | 1.0MB | 1 |
| fhv | 配車の車両 (大手以外) | 未公開 (403)。2026-06 までは読める | | |
| fhvhv | 大手の配車 (Uber、Lyft など)。2019 年から | 20,921,249 | 511.2MB | 20 |

- CloudFront (元は S3) で、初回の要求から 206 を返す。DuckDB 1.5.5 の httpfs でそのまま読める。
- 列を絞って読むのはよく効く。yellow の 2026-07 で PULocationID の列は 2.8MB (全体の 5%) で、乗車ゾーン別の件数は 0.3 秒で出た。いちばん重いのは乗車と降車の時刻の列 (各 16MB)。
- 行を絞って読むのは効きにくい。行グループが約 105 万行ずつと粗く、2009-01 と 2011-01 は 1 ファイルが 1 行グループ (1,400 万行、1,300 万行)。
- 未公開の月は 404 ではなく 403 が返る。

### 列

- 2011 年以降の yellow と green は、位置をゾーン ID (PULocationID、DOLocationID) でしか持たない。座標は無い。
- 2009 年の yellow は列名が違い (Trip_Pickup_DateTime など)、座標 (Start_Lon、Start_Lat、End_Lon、End_Lat) を持つ。
- 2025 年から cbd_congestion_fee (マンハッタン中心部の渋滞税)、2026 年の yellow と green には request_source が増えた。列は年で増えるので、年をまたいで読むときは `union_by_name` が要る。
- 列の意味は配布ページの Data Dictionary (種類ごとの PDF) と Trip Record User Guide にある。

## ゾーン境界

乗車記録のゾーン ID は、TLC が決めた 263 のゾーンを指す。

| ファイル | 中身 | 更新 | Range |
|---|---|---|---|
| `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv` | ID、区 (Borough)、名前、サービス区分。265 行 | 2024-02-22 | 206 |
| `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip` | Shapefile、EPSG:2263 (NAD83 ロングアイランド州平面、フィート単位)。263 行 | 2026-02-19 | 206 (ただし zip なので部分読みは無理。1MB) |
| `https://data.source.coop/cholmes/nyc-taxi-zones/taxi_zones.parquet` | 上の Shapefile を ogr2ogr で GeoParquet にしたもの (EPSG:2263) | 2023-08-17 | 206 |
| `https://data.source.coop/cholmes/nyc-taxi-zones/taxi_zones_4326.parquet` | 同じものを EPSG:4326 に。GeoParquet 1.0.0-beta.1、bbox 付き。1.5MB | 2023-08-17 | 206 |
| `https://data.source.coop/cholmes/nyc-taxi-zones/taxi_zones.pmtiles` | 表示用のタイル。0.5MB | 2023-08-17 | 206 |

- lookup の 264 は Unknown、265 は Outside of NYC で、境界は無い。
- 配布ページには「Taxi Zone Shapefile (PARQUET)」とあるが、`misc/` に Parquet は見つからなかった (推測した 2 つの名前はどちらも 403)。実体は zip。
- source.coop 版は古い。2023 年版は ID 56 (Corona) が 2 行、103 (Governor's Island/Ellis Island/Liberty Island) が 3 行あり、ID は 260 種類しかない。2026 年の TLC 版では、それぞれ 57 と、104、105 に振り直されて 263 種類になっている。残る 258 ゾーンの形は完全に一致した。
- 乗車記録には 57、104、105 が出てくるので、source.coop 版に ID で結合すると、この 3 ゾーンが落ちる。使うなら TLC の zip を `/tmp/study-geoai/` に落として読む (1MB なので例外として扱う)。

## ライセンス

- TLC の配布ページにあるのは「データは TLC が作ったものではなく、正確さを保証しない」という断り書きだけで、ライセンスの記載は無い。
- AWS の登録 (`awslabs/open-data-registry` の `nyc-tlc-trip-records-pds.yaml`) の License は NYC.gov の利用規約 (<https://www.nyc.gov/home/terms-of-use.page>) を指している。その規約は NYC.gov の内容を市の所有物とし、複製や再配布を明示的には認めていない。オープンデータについての別の定めも無い。
- NYC Open Data の FAQ は「利用に制約は無い」とし、根拠の Local Law 11 of 2012 は、公開するデータに登録、ライセンス、利用制限を課さないと定める。ただし、この乗車記録がその対象として扱われるのかは、確かめていない。
- AWS の登録は引用の書き方を示している: 「New York City Taxi and Limousine Commission (TLC) Trip Record Data was accessed on [DATE] from https://registry.opendata.aws/nyc-tlc-trip-records-pds」
- source.coop 版にはライセンスの記載が無い。
- ここでの扱い: 分析して結果を出典付きで出すのは問題ないと考える。再配布の許可ははっきりしないので、ミラーはしない。CloudFront が Range を受けるので、ミラーする理由も無い。

## AWS の S3 (s3://nyc-tlc)

- 登録上は us-east-1 のバケット `nyc-tlc` で、`AccountRequired: True`。
- 匿名では、一覧 (`aws s3 ls --no-sign-request`) も、オブジェクトの取得も 403 だった。AWS のアカウントで署名すれば読めるはずだが、試していない。
- 登録文も、匿名なら配布ページから落とすよう案内している。使うのは CloudFront のほう。

## 学習ステップとの対応 (案)

- 1〜3 回帰・分類: ゾーンと時刻から乗車数、チップの割合、料金を予測する。
- 4 Cross Validation: 月で分ける時系列の分割と、区でまとめる空間の分割を比べる。
- 5 クラスタリング: ゾーンを、時刻別の乗車数の形で型に分ける。
- 7 最短経路: 乗車と降車のゾーンの組の所要時間から、ゾーン間の時間の表を作る。
- 9〜10 割当とスケジューリング: 需要のゾーンに車両を割り当てる。乗車記録は時刻付きなので、車両の最少台数も試せる。
