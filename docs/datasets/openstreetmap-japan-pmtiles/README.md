# openstreetmap-japan-pmtiles

2026-09-28 に読んで確かめた内容。大きさは HEAD の `Content-Length` (バイト)、時刻は UTC。

- `https://tile.openstreetmap.jp/static/planet.pmtiles`
- OpenStreetMap Japan のタイルサーバー `https://tile.openstreetmap.jp/` (TileServer GL) が置いている、全世界のベクタータイル 1 本。OSM を Planetiler で OpenMapTiles スキーマのタイルにしたもの。
- cng-data-antigravity は組み込みの出どころ `osm-jp-pmtiles` にこれを使う (origin/main の `sources/osm_jp_pmtiles.py`)。`adapters/pmtiles.py` は HTTP の範囲要求でヘッダとディレクトリを読み、指定した bbox とズームのタイルだけを取り出して新しい PMTiles を書く。全体はダウンロードしない。

## ファイル

| 項目 | 値 |
|---|---|
| 大きさ | 84,276,503,187 |
| Last-Modified | 2026-09-25T03:30:59Z |
| ETag | `"6ab5eaf3-139f456293"` |
| Accept-Ranges | bytes (1 回目の範囲要求から 206 が返った) |
| サーバー | nginx/1.24.0 (Ubuntu)、CORS の許可ヘッダ付き |

- `https://tile.openstreetmap.jp/static/` のディレクトリ一覧に `planet-20260921.pmtiles` と `planet.pmtiles` が並んでいる。2 本は大きさ、Last-Modified、ETag がすべて同じで、同じファイルと読める (リンクかどうかは確かめていない)。
- 同じ一覧には `lka.pmtiles` (8M)、`wan-R04.pmtiles` (647K)、`plateau/`、`README.txt` もある。README.txt (113 バイト) は「overture.pmtiles は削除し、`https://dev.smellman.org/static/overture-latest/` を使うようになった」という 1 行。
- 古い日付の planet は一覧に無い。更新の頻度はサイトに書かれておらず、未確認。z.yuiseki.net の複製 (後述) のデータが 2025-11-24 なので、少なくとも一度は作り直されている。

## ヘッダ

先頭 127 バイトを範囲要求で読み、Python 標準ライブラリで解いた。

| 項目 | 値 |
|---|---|
| 版 | PMTiles v3 |
| タイル形式 | MVT (pbf) |
| タイル圧縮 / 内部圧縮 | gzip / gzip |
| clustered | 1 |
| ズーム | 0 から 14 |
| bounds | 経度 -180 から 180、緯度 -85.05113 から 85.05113 |
| center | 0, 0 (ズーム 0) |
| ルートディレクトリ | 127 から 16,200 バイト |
| メタデータ | 16,327 から 1,533 バイト (gzip) |
| リーフディレクトリ | 17,860 から 95,950,006 バイト |
| タイルデータ | 95,967,866 から 84,180,535,321 バイト |
| アドレスされたタイル数 | 276,014,552 |
| ディレクトリ項目 | 51,606,334 |
| 中身の異なるタイル | 45,539,210 |

## メタデータ

| キー | 値 |
|---|---|
| name | OpenMapTiles |
| version | 3.16.0 |
| description | A tileset showcasing all layers in OpenMapTiles. https://openmaptiles.org |
| type | baselayer |
| format / compression | pbf / gzip |
| planetiler:version | 0.10.2 |
| planetiler:githash | 0e5588c4a6e8c29a270a33afe8df62027d889604 |
| planetiler:buildtime | 2026-03-28T14:40:55.764Z |
| planetiler:osm:osmosisreplicationtime | 2026-09-21T00:00:03Z |
| planetiler:osm:osmosisreplicationseq | 0 |
| planetiler:osm:osmosisreplicationurl | (空) |
| attribution | `© OpenMapTiles` (openmaptiles.org へのリンク) と `© OpenStreetMap contributors` (openstreetmap.org/copyright へのリンク) |

- スキーマは OpenMapTiles 3.16.0。Shortbread ではない。
- 元データの基準日は 2026-09-21T00:00:03Z (ファイル名の 20260921 と一致)。replication の URL が空で番号が 0 なので、差分で追いかけたものではなく planet ファイル 1 本から作ったと読める。
- `planetiler:buildtime` (2026-03-28) はデータの基準日より半年前。これはタイルを作った時刻ではなく Planetiler 本体を組み立てた時刻と読める (確かめていない)。

### レイヤー (16)

括弧内はズーム範囲と属性の数。

| レイヤー | ズーム | 属性数 | 名前以外の属性 |
|---|---|---|---|
| aerodrome_label | 8-14 | 88 | class, ele, ele_ft, iata, icao |
| aeroway | 10-14 | 2 | class, ref |
| boundary | 0-14 | 29 | adm0_l, adm0_r, admin_level, claimed_by, class, disputed, disputed_name, maritime |
| building | 13-14 | 4 | colour, hide_3d, render_height, render_min_height |
| housenumber | 14 | 1 | housenumber |
| landcover | 0-14 | 2 | class, subclass |
| landuse | 4-14 | 1 | class |
| mountain_peak | 7-14 | 88 | class, customary_ft, ele, ele_ft, rank |
| park | 4-14 | 85 | class, rank |
| place | 0-14 | 88 | capital, class, iso_a2, rank |
| poi | 11-14 | 91 | agg_stop, class, indoor, layer, level, rank, subclass |
| transportation | 4-14 | 19 | access, bicycle, brunnel, class, expressway, foot, horse, indoor, layer, level, mtb_scale, network, official, oneway, ramp, service, subclass, surface, toll |
| transportation_name | 6-14 | 167 | class, indoor, layer, level, network, ref, ref_length, route_1 から route_21 の name/network/ref/colour, subclass |
| water | 0-14 | 4 | brunnel, class, id, intermittent |
| water_name | 0-14 | 85 | class, intermittent |
| waterway | 3-14 | 86 | brunnel, class, intermittent |

- 名前の属性は `name`, `name_en`, `name_de`, `name_int`, `name:latin`, `name:nonlatin` と `name:<言語>` (place では 78 言語)。日本語は `name:ja`, `name:ja-Hira`, `name:ja-Latn`。
- 数値の属性 (ele, rank, render_height など) は型が Number と宣言されている。

## タイルサーバーとの関係

- `https://tile.openstreetmap.jp/data/planet.json` (TileJSON 3.0.0) は `basename` が `planet.mbtiles` で、XYZ で `https://tile.openstreetmap.jp/data/planet/{z}/{x}/{y}.pbf` を配っている。version、planetiler の各キー、基準日 2026-09-21T00:00:03Z は PMTiles のメタデータと同じ。配信は MBTiles から、静的配布は PMTiles から、と読める (同じ Planetiler の出力かは確かめていない)。
- タイルサーバーには planet のほかに overlay が 2 つある。`hoppo` (北方領土の島のポリゴン、tippecanoe v1.36.0、レイヤー `island`、901 地物、ズーム 5-14) と `takeshima` (竹島、レイヤー `island` 284 地物と `island_poi` 10 地物、ズーム 6-14)。スタイル (maptiler-basic-ja など) はこれらを planet に重ねて使うと思われるが、スタイルの中身は読んでいない。静的配布の planet.pmtiles にはこの 2 つは入っていない。

## z.yuiseki.net の複製との比較

`https://z.yuiseki.net/static/openstreetmap/planet/planet.pmtiles` とヘッダとメタデータで比べた。z 側は 1 回目の範囲要求に 200 を返し、2 回目で 206 になった。ヘッダとメタデータの要求は 1 回目から 206 だった。

| 項目 | OSMJ (tile.openstreetmap.jp) | z.yuiseki.net |
|---|---|---|
| 大きさ | 84,276,503,187 | 82,984,871,716 |
| Last-Modified | 2026-09-25T03:30:59Z | 2025-11-30T09:54:41Z |
| ETag | `"6ab5eaf3-139f456293"` | `"692c1461-135248a724"` |
| OpenMapTiles version | 3.16.0 | 3.15.0 |
| planetiler:version | 0.10.2 | 0.9.2-SNAPSHOT |
| planetiler:buildtime | 2026-03-28T14:40:55.764Z | 2025-07-02T08:41:04.159Z |
| 基準日 (osmosisreplicationtime) | 2026-09-21T00:00:03Z | 2025-11-24T00:59:59Z |
| アドレスされたタイル数 | 276,014,552 | 275,142,148 |
| ディレクトリ項目 | 51,606,334 | 50,651,567 |
| 中身の異なるタイル | 45,539,210 | 44,626,561 |
| メタデータ (gzip) | 1,533 | 1,536 |

- 別物。z 側は約 10 か月前のデータで作った、スキーマ 1 版前のもの。ヘッダの形式 (v3、MVT、gzip、z0-14、全球) とメタデータのキーの並びは同じ。
- レイヤーは 16 本とも同じ名前、同じズーム範囲。属性の違い:
  - OSMJ だけにある: `name:af` (名前を持つ 8 レイヤー)、`name:tok` (place, poi)、`transportation` の `official`。
  - z だけにある: `name:ja_kana` と `name:ja_rm` (名前を持つ 8 レイヤー)。
  - `boundary` は z が 78 属性、OSMJ が 29 属性。z にある `name:ar` から `name:ur` まで 49 言語の名前が OSMJ には無い。
- z の複製を使っていたコードを OSMJ に切り替えると、`name:ja_kana` / `name:ja_rm` を参照するスタイルや、`boundary` の多言語名を使う処理が黙って空になる。

## 気をつけること

- 大きさは 84GB。丸ごとのダウンロードは避け、範囲要求で必要なところだけ読む (cng-data-antigravity の pmtiles アダプタもそうしている)。
- `planet.pmtiles` は差し替えられる名前。再現性が要るなら日付付きの `planet-20260921.pmtiles` を指すか、ETag を記録しておく。
- `planetiler:buildtime` をデータの時点と読み違えない。データの時点は `planetiler:osm:osmosisreplicationtime`。
- 北方領土と竹島の overlay はタイルサーバーの側にだけある。静的の planet.pmtiles だけで日本の地図を描くと、OSMJ のサイトで見える地図と一致しない可能性がある (描き比べていない)。

## ライセンス

- メタデータと TileJSON の attribution は「© OpenMapTiles © OpenStreetMap contributors」。
- OSM のデータとしては ODbL 1.0 (OSM 本家の copyright ページの条件)。OSMJ のサイト (tile.openstreetmap.jp のトップページ) にはライセンスの記載が見当たらず、OSMJ 独自の条件は未確認。
- OpenMapTiles の GitHub の LICENSE.md (master) によると、スキーマのコードは BSD 3-Clause、地図のデザイン (look and feel) は CC-BY 4.0 で、OpenMapTiles スキーマ由来の地図には「OpenMapTiles」への帰属表示が要る。表示例は `© OpenMapTiles © OpenStreetMap contributors`。

## 12 ステップでの使いどころ (案)

- 学習データというより、結果を地図に重ねる背景として使うのが主。範囲要求で必要な地域とズームだけ切り出せる。
- 7: z14 の `transportation` (class, oneway, toll, expressway など) から道路網を作れる。ただしタイル境界で線が切れ、形状も簡略化されているので、経路探索の正解データには Geofabrik の PBF のほうが向く。タイルから作った網と PBF から作った網で最短経路を比べるのは練習になる。
- 1, 2, 3, 11: z14 の `building` の `render_height` を、面積や周りの `poi` `landuse` から回帰する。SHAP で効いた特徴を見る。
- 5: `poi` の点 (class, subclass) を DBSCAN にかけて繁華街を切り出す。
- 4: タイル (z, x, y) の単位は空間ブロック分割のブロックにそのまま使える。
- 6: タイルごとにレイヤー別の地物数や `poi.class` の件数を数えて行列にし、PCA で地域の型を見る。

## 取り出し方

range。2026-09-30 に実測した。

`https://tile.openstreetmap.jp/static/planet.pmtiles` の HEAD は 200 で、`Content-Length` 84,276,503,187、`Accept-Ranges: bytes`、`Last-Modified` Fri, 25 Sep 2026 03:30:59 GMT、`ETag` `"6ab5eaf3-139f456293"`。サーバーは nginx/1.24.0 (Ubuntu) で、`Access-Control-Allow-Headers` に `Range` が入っている。

`curl -s -r 0-1023` は 1 回目から 206 と 1,024 バイトを返した。ヘッダが宣言しているだけでなく、要求が実際に通る。

先頭 127 バイトの Range 要求も 206 と 127 バイトで、中身は次のとおり。

| 項目 | 値 | 読み方 |
|---|---|---|
| 先頭 7 バイト | `PMTiles` | そのままの文字列 |
| 8 バイト目 | 3 | spec version |
| ルートディレクトリ | 位置 127、長さ 16,200 | 9 バイト目からの uint64 2 つ |
| メタデータ | 位置 16,327、長さ 1,533 | 25 バイト目からの uint64 2 つ |
| 葉ディレクトリ | 位置 17,860、長さ 95,950,006 | 41 バイト目からの uint64 2 つ |
| タイルデータ | 位置 95,967,866 | 57 バイト目からの uint64 |
| アドレスされたタイル数 | 276,014,552 | 73 バイト目からの uint64 |
| ズーム | 0 から 14 | 101 バイト目と 102 バイト目の 1 バイトずつ |
| bounds | 経度 -180 から 180、緯度 -85.05113 から 85.05113 | 103 バイト目からの int32 4 つ (1e-7 度単位) |

84GB のファイルに対して、索引の入口 (ルートディレクトリ) は先頭から 16,327 バイトまでに収まっている。葉ディレクトリは 95,950,006 バイトあるが、これも必要な部分だけ Range で引ける位置に置かれている。

XYZ の配信 `https://tile.openstreetmap.jp/data/planet/{z}/{x}/{y}.pbf` もあり、こちらは Range ではなくタイル 1 枚につき 1 要求になる。TileJSON `https://tile.openstreetmap.jp/data/planet.json` は 200 で 18,542 バイトを返し、bounds、minzoom、maxzoom、vector_layers を持つので、範囲もレイヤー構成も推測せずに分かる。ただし配信側は MBTiles が元なので、静的配布の PMTiles と同じ中身とは限らない (上の「タイルサーバーとの関係」を見る)。
