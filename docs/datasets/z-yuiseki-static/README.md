# z.yuiseki.net/static

`https://z.yuiseki.net/static/` は nginx の自動一覧 (autoindex) で公開しているファイル置き場。前段に Cloudflare がいる。
構成は 2026-09-28 にディレクトリ一覧をたどって確かめた。

## ディレクトリ

| ディレクトリ | 中身 | 詳細 |
|---|---|---|
| openstreetmap/ | OSM planet 3 版、地域抽出、Layercake GeoParquet、taginfo、Wiki ダンプ、OpenMapTiles の PMTiles | [openstreetmap.md](openstreetmap.md) |
| tokyo-ckan-files/ | 東京都オープンデータカタログの 23 区の施設一覧 CSV 183 件を中身を変えずに置いたもの (2026-09-28 に作成、CC BY 4.0) | [../stac/tokyo-ckan.md](../stac/tokyo-ckan.md) |
| worldpop/ | WorldPop の日本の総人口 (100m、1km)、年齢性別 (1km)、都市化度の 2015〜2030 年を COG にしたミラー、1,024 ファイル 4.3GB (2026-09-28 に作成、CC BY 4.0) | [../stac/worldpop.md](../stac/worldpop.md) |
| gtfs/ | 東京のバスの GTFS-JP 5 つ (都営バス、台東区、杉並区、荒川区、葛飾区) を版ごとにそのまま置いたもの (2026-09-28 に作成) | [../tokyo-gtfs/README.md](../tokyo-gtfs/README.md) |
| ksj/ | 国土数値情報の東京都の P04 医療機関、P29 学校、A31a 洪水浸水想定、mesh500r6 将来推計人口を GeoParquet にしたミラー (2026-09-28 に作成、すべて CC BY 4.0) | [../stac/mlit-nlftp.md](../stac/mlit-nlftp.md) |
| mlit-1km-fromto/ | 国土交通省「全国の人流オープンデータ」の 1km メッシュ別と市区町村単位発地別の滞在人口 (2019-01〜2021-12、全国) を Parquet にしたミラー (2026-09-29 に作成、政府標準利用規約 2.0 準拠) | [../mlit-1km-fromto/README.md](../mlit-1km-fromto/README.md) |
| geonames/ | GeoNames のダンプ (地名辞書、別名、階層、5 段目の行政区分、小さい表) を、allCountries.zip の Last-Modified の日付ごとのディレクトリに元のまま残し、Parquet (地名辞書は国の境で 4 つに分けた GeoParquet) を添えたもの (2026-10-01 から、CC BY 4.0) | [../geonames/README.md](../geonames/README.md) |
| ourairports/ | OurAirports の 7 つの CSV を、上流の commit の日付ごとのディレクトリに元のまま残し、Parquet (airports と navaids は GeoParquet) を添えたもの (2026-10-01 から、public domain) | [../ourairports/README.md](../ourairports/README.md) |
| hdx-meta/ | AI for Good at Meta が HDX で配る Movement Distribution (2026-06〜、直近 90 日を超えて貯める)、Movement Range Maps (2020-03〜2022-05)、Commuting Zones、Business Activity Trends during Crisis の元のファイル 22 本 (1.25GB) と Parquet (203MB) のミラー (2026-09-29 に作成、CC BY) | [../hdx-meta-movement/README.md](../hdx-meta-movement/README.md) |
| ookla/ | Ookla Speedtest の 2026 年第 2 四半期 (mobile、fixed) を Range 要求で読める GeoParquet にしたミラー (2026-09-28 に作成) | [../ookla-speedtest/README.md](../ookla-speedtest/README.md) |
| overture/ | Overture の建物・交通・水域の全世界 PMTiles (60GB、2024-11 ビルド)。もう 1 つは 0 バイト | [overture.md](overture.md) |
| cesg/ | 東京周辺の POI 検索一式 (Overture Places 45 万件、DuckDB FTS) と Valhalla 経路タイル | [cesg.md](cesg.md) |
| planetarble/ | planetarble の出力。全球と日本の衛星画像 PMTiles 16 個と ETOPO 2022 標高 COG | [planetarble.md](planetarble.md) |
| gsi/ | 国土地理院シームレス空中写真の日本全域。z18 まで、PMTiles と MBTiles の 6 通り、合計 2.5TB 超 | [gsi.md](gsi.md) |
| mapterhorn/ | Mapterhorn 全球標高タイル (2026-01-06 版)。z0-12、512px 可逆 WebP、663GB | [mapterhorn.md](mapterhorn.md) |
| kontur/ | Kontur Population 2023-11-01 版の GeoPackage (6.7GB) と同じものの .gz、取得ログ | [kontur.md](kontur.md) |
| worldbank/ | WDI の国別年次指標 (縦持ち)。217 か国、1990〜2024 年、16 指標。うち CO2 の指標は壊れている | [worldbank.md](worldbank.md) |
| natural-earth/ | Natural Earth の国 (110m/50m) と州 (10m) の GeoParquet。列を絞り name_ja 付き | [natural-earth.md](natural-earth.md) |
| gpkg/ | Natural Earth をまとめた GeoPackage (885MB)。レイヤー一覧は読めていない | [gpkg.md](gpkg.md) |
| ucdp/ | UCDP GED の紛争イベント。25.1 (385,918 件、1989〜2024) と 26.1 (417,968 件、1989〜2025、2026-10-02 に追加) の CSV とその zip、26.1 の codebook | [ucdp.md](ucdp.md) |
| csv/ | Geo-PKO 2.3 の国連 PKO 展開地点 21,243 行 (1994〜2024、52 ミッション) | [csv.md](csv.md) |
| geojson/ | 海底ケーブル、プレート境界 PB2002、USGS の M4.5 以上の地震。ほかにスタイル JSON 1 つ | [geojson.md](geojson.md) |
| wikimedia/ | Wikipedia 記事の重要度表 (gzip した TSV、Wikidata ID 付き)。先頭だけ読んだ | [wikimedia.md](wikimedia.md) |

データセットではないもの:

- `maps/` は地図の配信用素材。フォント (glyph PBF、84 書体)、スタイル JSON、スプライト、MapLibre GL JS 本体、表示テスト用 HTML。
- `tmp/` は一時置き場。発表資料 (`cng-japan-2026/`)、再現用の点群 (`github/odm/`)、中身の無いディレクトリなど。

## 読むときの注意

- DuckDB で書いた Parquet は、既定でブルームフィルタを持つ。DuckDB は、統計 (最小値と最大値) で除外できた行グループについても、絞り込みに使った列のブルームフィルタを読みにいくので、HTTP では行グループ 1 つにつき要求が 1 回増える。全国の人流オープンデータの台東区の 1 か月を引くクエリは、ブルームフィルタ付きで 1,114 回の要求になった。
  2026-10-02 に、geonames、hdx-meta、ksj、mlit-1km-fromto、ookla、ourairports の 34 ファイルを、行の並びを変えずにブルームフィルタ無しで書き直した (`scripts/rewrite_parquet_without_bloom.py`。行ごとのハッシュを順番どおりに元と比べ、一致したときだけ置き換える)。manifest と README の大きさとハッシュも書き換え、Cloudflare の該当 URL のキャッシュを消した。ミラーのスクリプトも、この日から無しで書く。
  並列に書かれたファイルは行グループの大きさが不揃いで、1 スレッドで書き直すと切れ目が変わることがある。ksj の A31a-25_83_10 の後半は 225 から 188 グループになった。台東区付近の 1,948 行は、キャッシュに載ってから 0.38〜0.45 秒で読めた (書き直す前は 0.5〜0.7 秒)。キャッシュを消した直後の最初の 1 回は 95 秒かかった。

- 前段の Cloudflare は、あるファイルへの 1 回目の Range 要求に 206 ではなく 200 (ファイル全体の送信) を返すことがある。2 回目からは 206 になる。
  巨大ファイルでこれに当たると、先頭や末尾だけ読むつもりが全体のダウンロードになる。
- なので、読む前に curl で末尾だけを要求し、206 が返るまで最大 3 回試す。`--max-filesize` を付けておくと 200 のときは本文を読まずに止まる。

  ```sh
  curl -sS -r -8 --max-filesize 1048576 --max-time 10 -o /dev/null -w "%{http_code}\n" "$URL"
  ```

- 1 ファイルの調査は 60 秒で打ち切る。読めなかったものは「60 秒以内に読めなかった」と書いて深追いしない。
- DuckDB はこのリポジトリの uv 環境の 1.5.5 を使う (`uv run python`)。1.5.5 より前は使わない。
- 一覧の大きさは nginx の丸めた表示 (`6G` など) で、正確なバイト数ではない。正確な値は HEAD の `Content-Length` で取る。
- GDAL の `/vsicurl/` は、GeoPackage 2 つ (gpkg/ と kontur/) と planetarble/ の GeoTIFF を「Range downloading not supported」で開けなかった。GDAL の詳細ログでは、Range 付きの GET に 200 が返っていた。
  curl で試すと、`Accept-Encoding: gzip` を付けた Range 要求にだけ 200 が返り、付けなければ 206 だった。ただしどちらも 1 回ずつしか試しておらず、原因はまだ仮説。
- 巨大な Parquet は、DuckDB の httpfs で直接読むとフッターだけでも 60 秒以内に返らないことがある。
  そのときは、curl の範囲要求でフッターだけ取り、空のファイルの末尾に書いてからローカルで読む (openstreetmap/ の 4 本はこれで読めた)。
- Range で読ませるファイルは 512MB 未満にする。前段の Cloudflare は 512MB を超えるファイルをキャッシュせず (cf-cache-status が MISS のまま)、Range 要求の最初の 1 回でファイル全体を送ろうとする。677MB の GeoParquet は台東区付近の読み出しに 67〜97 秒かかり、半分に分けたら 0.5〜0.7 秒になった (キャッシュに載る最初の 1 回だけ約 23 秒)。

## 取り出し方

区分は range。Range 要求が本当に 206 で返り、PMTiles や GeoParquet のように先頭や末尾に索引を持つファイルを置いてあるので、必要なところだけ読める。ただし一覧は機械可読ではないので、catalog としては使えない。

2026-09-30 に、置いてある中で最も大きいファイルで測った。

| 要求 | 応答 |
|---|---|
| `curl -sI https://z.yuiseki.net/static/openstreetmap/planet/planet.pmtiles` | 200、`content-length: 82984871716`、`accept-ranges: bytes`、`cf-cache-status: BYPASS` |
| `curl -r 0-1023 --max-filesize 1048576` 同じ URL、1 回目 | 206、`content-range: bytes 0-1023/82984871716`、1,024 バイト |
| 同じ要求、2 回目 | 206、1,024 バイト |
| 同じ要求、3 回目 | 206、1,024 バイト |

取れた先頭 7 バイトは `PMTiles` で、PMTiles のヘッダそのものだった。索引はファイルの先頭にあるので、82,984,871,716 バイト (約 77GiB) のうち先頭の数 KB を読むだけでタイルの引き方が分かる。

上の「読むときの注意」に書いた「1 回目の Range に 200 が返ることがある」現象は、今日この 1 本では 3 回とも再現しなかった。`cf-cache-status` は 3 回とも BYPASS のままで、そもそもキャッシュに載せていない。この注意が不要になったとは考えていない。同じ注意の後半にある「512MB を超えるファイルはキャッシュに載らない」とも整合していて、載らないファイルはオリジンに素通しされ、オリジンの nginx は素直に 206 を返す、と読める。キャッシュに載る大きさのファイルで 1 回目に当たったときが危ないのだと思われる (仮説であって、今日確かめてはいない)。いずれにせよ `--max-filesize` を付けておく手当ては続ける。

一覧は機械可読ではない。

| 要求 | 応答 |
|---|---|
| `curl -sI https://z.yuiseki.net/static/` | 200、`content-type: text/html` |
| `Accept: application/json` を付けて同じ要求 | 同じ HTML が返る。内容交渉はしていない |

返るのは nginx の autoindex の既定の HTML で、`<pre>` の中に `<a href="...">` と日付と大きさが桁揃えで並んでいるだけである。`autoindex_format json` にはなっていない。大きさは `88G` `77G` `440K` のように丸めた表示で、正確なバイト数は入っていない。

```
<a href="planet-260803.osm.pbf">planet-260803.osm.pbf</a>                              12-Aug-2026 22:42     88G
<a href="planet.pmtiles">planet.pmtiles</a>                                     30-Nov-2025 18:54     77G
```

したがって、どのファイルがあるかを知るには HTML を自分で解き、正確な大きさが要るなら 1 本ずつ HEAD を投げる。bbox や日時で絞れる目録は無いので catalog ではない。ディレクトリで種類ごとに分かれてはいるが、地域や単位で事前分割したものではないので split でもない。

まとめると、この置き場の価値は目録ではなく Range にある。planet.pmtiles や Ookla の GeoParquet のように索引を持つ形式に変換したものを置いてあるから、77GiB のファイルから東京のぶんだけを秒で読める。どのファイルを読むかは、この README とその下の各ファイルを人が読んで決める。
