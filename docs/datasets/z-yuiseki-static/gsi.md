# gsi

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/gsi/`
- 中身は `seamlessphoto/` の 1 ディレクトリだけ。国土地理院の「シームレス空中写真」(全国最新写真、タイル名 seamlessphoto) を日本全域でタイルごと集めて、PMTiles と MBTiles に詰め直したもの。
- 同じ写真が、ズームの切り方とタイルの大きさと形式を変えて 6 通りある。合計 2.5TB を超えるので、選んで使う。
- 基準日: 元の写真の撮影時期はメタデータに書いていない。ファイルの作成は 2026-06-07 から 2026-06-10 (Last-Modified)。

## ファイル

大きさは HEAD の `Content-Length`。ズームと範囲はヘッダ、タイルの画素数は最初のタイル 1 枚の JPEG から。

| ファイル | バイト数 | 形式 | ズーム | タイル | タイル数 |
|---|---:|---|---|---|---:|
| z18.pmtiles | 424,950,358,986 | PMTiles, jpeg | 18 のみ | 256px | 28,162,630 |
| z2-z17.pmtiles | 146,942,991,995 | PMTiles, jpeg | 2-17 | 256px | 10,769,985 |
| seamlessphoto512.pmtiles | 767,579,254,057 | PMTiles, jpeg | 1-17 | 512px | 9,772,357 |
| z18.mbtiles | 447,497,322,496 | MBTiles (SQLite) | 未確認 | 未確認 | 未確認 |
| z2-z17.mbtiles | 155,759,443,968 | MBTiles (SQLite) | 未確認 | 未確認 | 未確認 |
| z2-z18.mbtiles | 603,278,450,688 | MBTiles (SQLite) | 未確認 | 未確認 | 未確認 |
| z18.pmtiles.torrent | 253,806 | BitTorrent | - | - | - |
| z18.pmtiles.3webseeds.torrent | 253,883 | BitTorrent | - | - | - |
| SHA256SUMS | 159 | テキスト | - | - | - |
| z18.pmtiles.sha256 | 78 | テキスト | - | - | - |
| seamlessphoto512.pmtiles.sha256 | 91 | テキスト | - | - | - |
| compare.html | (HEAD に Content-Length なし) | HTML | - | - | - |

タイル数はヘッダの addressed tiles。

### PMTiles 3 つ

- PMTiles v3、clustered、内部圧縮 gzip、タイル圧縮 none、タイル形式 jpeg。
- 範囲 (bounds):
  - z18 と seamlessphoto512: 東経 122.920532-153.989868, 北緯 20.40642-45.541946
  - z2-z17: 東経 122.0-154.0, 北緯 20.0-46.0 (丸めた値)
- メタデータの attribution はどれも「国土地理院 シームレス空中写真 (GSI seamlessphoto) CC BY 4.0」。
- seamlessphoto512 の description は「GSI seamlessphoto re-tiled to 512px tiles, zoom 1-17 (from 256px z2-z18)」。256px の z2-z18 を 512px に組み直したもので、z が 1 つずつ下がる。最初のタイルは実際に 512x512 だった。
- z18 と z2-z17 の最初のタイルは 256x256。

### MBTiles 3 つ

- 丸ごとは落とせないので、先頭 64KB だけを範囲要求で読んだ。
- どれも SQLite 3、ページ 4096 バイト。ページ数 x ページサイズが Content-Length と一致した (途中で切れたファイルではない)。
- スキーマは標準的な MBTiles: `tiles (zoom_level, tile_column, tile_row, tile_data)`、一意索引 `tile_index`、`metadata (name, value)`。
- metadata 表の中身とズーム範囲は読めていない (表のページを探す必要があり、今回は見送った)。名前から z18.mbtiles と z2-z17.mbtiles は同名の PMTiles の元、z2-z18.mbtiles はその 2 つを合わせたものと読めるが、確かめていない。

### torrent 2 つ

- どちらも z18.pmtiles (424,950,358,986 バイト、ピース 32MiB) の torrent。作成は mktorrent 1.1。
- z18.pmtiles.torrent (作成 2026-06-16) の webseed は 2 つ: `z.yuiseki.net` と `depot.optgeo.org`。
- z18.pmtiles.3webseeds.torrent (作成 2026-06-18) はそれに `data.source.coop/smartmaps/japan-seamlessphoto/pmtiles/z18.pmtiles` を足した 3 つ。
- 同じものが Source Cooperative にもあると読める (向こう側は確かめていない)。

### ハッシュ

- `z18.pmtiles`: c839630f56ae41736268befea2fc499fa8d84c06f92ae41d02c704a1569cdaea
- `seamlessphoto512.pmtiles`: 404c2965dbd108715b8d54675425fd39d64ef8dddfe37e9167710f363e22ed78
- ファイルそのものを落としての照合はしていない。

## 気づいたこと

- SHA256SUMS は `z1-z17.pmtiles` という名前のハッシュを載せているが、そのファイルは無い (404)。ハッシュが seamlessphoto512.pmtiles.sha256 と同じなので、改名前の名前が残っている。
- SHA256SUMS に z2-z17.pmtiles と MBTiles 3 つのハッシュは無い。
- compare.html (256px と 512px の見え方を並べる確認ページ) は `z2-z16.pmtiles` を読みに行くが、そのファイルは無い (404)。ページは今は地図を出せないはず。
- z2-z17.pmtiles のヘッダの center 経度が -76.748 で、bounds の外にある。planetarble/planet_tokyo23_seamlessphoto.pmtiles も同じ種類のずれ (-75.008)。表示に使う値なので実害は小さいが、center を読むコードは誤る。
- ヘッダの center zoom が z18 と seamlessphoto512 では 18。seamlessphoto512 の最大ズーム 17 を超えている。
- 東京 23 区だけを切り出した版が planetarble/planet_tokyo23_seamlessphoto.pmtiles (1.5GB) にある。試すならそちらが軽い。

## ライセンス

- メタデータには CC BY 4.0 と書いてある。国土地理院のコンテンツ利用規約 (出典の明示で利用可、CC BY 4.0 互換) の対象と思われるが、seamlessphoto の個別条件は原典で未確認。
- 使うときは「国土地理院 シームレス空中写真」などの出典を明示する。

## 学習ステップでの使いどころ (案)

- z18 の 256px タイルは緯度 35 度で約 0.49m/px (Web メルカトルの式からの計算値で、元写真の解像度ではない) の航空写真なので、建物や道路、緑地が見分けられる。画素の色や質感を集計して特徴量にし、2 Random Forest や 3 XGBoost で土地利用を分類する。ラベルは OSM などの別データから付ける。
- 5 k-means で画素やタイルを色でクラスタリングすると、植生、水面、市街地がどこまで分かれるかを試せる。6 PCA でタイルの色統計を縮約するのもよい。
- 隣り合うタイルは似ているので、ランダム分割と空間ブロック分割で 4 Cross Validation の結果が変わる例になる。
- 数百 GB あるので丸ごと扱わず、PMTiles の範囲要求で必要なタイルだけ引く。まずは planet_tokyo23_seamlessphoto.pmtiles で試すのが現実的。
