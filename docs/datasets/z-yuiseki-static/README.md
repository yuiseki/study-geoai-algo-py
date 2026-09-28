# z.yuiseki.net/static

`https://z.yuiseki.net/static/` は nginx の自動一覧 (autoindex) で公開しているファイル置き場。前段に Cloudflare がいる。
構成は 2026-09-28 にディレクトリ一覧をたどって確かめた。

## ディレクトリ

| ディレクトリ | 中身 | 詳細 |
|---|---|---|
| openstreetmap/ | OSM planet 3 版、地域抽出、Layercake GeoParquet、taginfo、Wiki ダンプ、OpenMapTiles の PMTiles | [openstreetmap.md](openstreetmap.md) |
| worldpop/ | WorldPop の日本の総人口 (100m、1km)、年齢性別 (1km)、都市化度の 2015〜2030 年を COG にしたミラー、1,024 ファイル 4.3GB (2026-09-28 に作成、CC BY 4.0) | [../stac/worldpop.md](../stac/worldpop.md) |
| gtfs/ | 東京のバスの GTFS-JP 5 つ (都営バス、台東区、杉並区、荒川区、葛飾区) を版ごとにそのまま置いたもの (2026-09-28 に作成) | [../tokyo-gtfs/README.md](../tokyo-gtfs/README.md) |
| ksj/ | 国土数値情報の東京都の P04 医療機関、P29 学校、A31a 洪水浸水想定、mesh500r6 将来推計人口を GeoParquet にしたミラー (2026-09-28 に作成、すべて CC BY 4.0) | [../stac/mlit-nlftp.md](../stac/mlit-nlftp.md) |
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
| ucdp/ | UCDP GED 25.1 の紛争イベント 385,918 件 (1989〜2024)。CSV とその zip | [ucdp.md](ucdp.md) |
| csv/ | Geo-PKO 2.3 の国連 PKO 展開地点 21,243 行 (1994〜2024、52 ミッション) | [csv.md](csv.md) |
| geojson/ | 海底ケーブル、プレート境界 PB2002、USGS の M4.5 以上の地震。ほかにスタイル JSON 1 つ | [geojson.md](geojson.md) |
| wikimedia/ | Wikipedia 記事の重要度表 (gzip した TSV、Wikidata ID 付き)。先頭だけ読んだ | [wikimedia.md](wikimedia.md) |

データセットではないもの:

- `maps/` は地図の配信用素材。フォント (glyph PBF、84 書体)、スタイル JSON、スプライト、MapLibre GL JS 本体、表示テスト用 HTML。
- `tmp/` は一時置き場。発表資料 (`cng-japan-2026/`)、再現用の点群 (`github/odm/`)、中身の無いディレクトリなど。

## 読むときの注意

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
