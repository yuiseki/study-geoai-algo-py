# planetarble

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/planetarble/`
- 自作パイプライン [planetarble](https://github.com/yuiseki/planetarble) (ローカルでは `repos/__yuiseki/planetarble`) の出力置き場。衛星画像のラスタタイル (PMTiles) 16 個と、海底地形の GeoTIFF 1 個。
- planetarble の README によれば、既定は HLS v2 (NASA/USGS) を Microsoft Planetary Computer から取り、海は NOAA ETOPO 2022 で陰影を付ける。旧来の BMNG / Copernicus (Sentinel-2 WMS) の経路も残っている。
- PMTiles のメタデータは出典をほとんど書いていない (`name` と `description` だけ、または `format` と `zoom` だけ)。どの元データから作ったかはファイル名と README から読むしかない。

## ファイル

大きさは HEAD の `Content-Length`。ズームとタイル形式は PMTiles ヘッダ、タイル数はヘッダの addressed tiles。

| ファイル | バイト数 | 形式 | ズーム | タイル数 | 覆う範囲 (ディレクトリから) |
|---|---:|---|---|---:|---|
| ETOPO_2022_15s_bed.tif | 3,470,279,731 | GeoTIFF (COG) | - | - | 全球 |
| planet.pmtiles | 4,938,335,719 | jpeg | 0-10 | 1,398,101 | 全球 (z0-10 の全タイル) |
| planet_bmng.pmtiles | 4,938,335,719 | jpeg | 0-10 | 1,398,101 | 全球 (planet.pmtiles と同じ) |
| planet_2024_8z.pmtiles | 232,937,157 | jpeg | 0-7 | 21,845 | 全球 (z0-7 の全タイル) |
| planet_2024_10z.pmtiles | 2,005,602,750 | jpeg | 0-9 | 349,525 | 全球 (z0-9 の全タイル) |
| planet_2024_12z.pmtiles | 17,232,309,785 | jpeg | 0-11 | 5,592,405 | 全球 (z0-11 の全タイル) |
| world_2024_z8.pmtiles | 2,027,982 | jpeg | 0-8 | 529 | z8 で東経 122.3-147.7, 北緯 23.2-46.1 (日本周辺) |
| world_2024.pmtiles | 28,706,010 | jpeg | 0-10 | 7,729 | z10 で東経 122.3-147.7, 北緯 23.2-46.1 (日本周辺) |
| planet_copernicus.pmtiles | 68,824,453 | jpeg | 0-10 | 7,729 | z10 で東経 122.3-147.7, 北緯 23.2-46.1 (日本周辺) |
| planet_2.pmtiles | 45,613,697 | jpeg | 0-10 | 4,226 | z10 で東経 115.3-156.4, 北緯 20.0-50.1 |
| planet_3.pmtiles | 45,613,697 | jpeg | 0-10 | 4,226 | planet_2.pmtiles と同じ |
| planet_gsi.pmtiles | 7,495 | jpeg | 0-10 | 11 | 各ズーム 1 枚だけ。z10 は東京付近の 1 タイル |
| planet_japan_sentinel-2.pmtiles | 617,258,694 | webp | 0-14 | 53,198 | z0-7 は全球、z8 以上は東経 129.4-143.4, 北緯 32.0-39.9 |
| planet_tokyo23_sentinel-2.pmtiles | 197,568,096 | webp | 0-14 | 22,286 | z0-7 は全球、z8 以上は東京 23 区周辺 |
| planet_tokyo23_hls.pmtiles | 187,299,487 | webp | 0-12 | 21,890 | z0-7 は全球、z8 以上は東京 23 区周辺 |
| planet_tokyo23_seamlessphoto.pmtiles | 1,534,973,761 | jpeg | 2-18 | 87,900 | 東経 139.56-139.92, 北緯 35.53-35.82 (ヘッダの bounds) |
| planet_atami.pmtiles | 192,852,006 | webp | 0-18 | 27,349 | z0-7 は全球、z18 は東経 139.02-139.12, 北緯 35.07-35.13 (熱海) |

範囲の列は、ルートとリーフのディレクトリを読んで各ズームのタイル番号の最小と最大から出したもの。穴の有無までは見ていない。

### ETOPO_2022_15s_bed.tif

- NOAA の ETOPO 2022 の 15 秒角 bedrock (氷床下の基盤面) 標高。planetarble が海の陰影に使う元データ。
- gdalinfo の結果 (先頭 4MB を落としてローカルで読んだ):
  - 86400 x 43200 画素、EPSG:4326、画素 0.0041666... 度 (15 秒角)、原点 (-180, 90)
  - 1 バンド Float32、単位 metre、NoData -99999
  - COG、LZW 圧縮、ブロック 256x256、概観 8 段 (43200x21600 から 338x169)
- `/vsicurl/` で直接開くと「Range downloading not supported by this server!」で失敗した。curl で 206 を 3 回確かめた後でも同じ。GDAL の要求だけ 200 が返っている可能性があるが、確かめていない。先頭を curl の範囲要求で落とせば読める。

### PMTiles 共通

- どれも PMTiles v3、clustered、内部圧縮 gzip、タイル圧縮 none。
- jpeg のものはメタデータ `format: jpg`、webp のものは `format: webp`。
- `type` は jpeg の全球系が `overlay`、tokyo23_seamlessphoto だけ `baselayer`。

## 気づいたこと

- planet.pmtiles と planet_bmng.pmtiles はバイト数もヘッダも同じで、3 か所 (先頭 1MB、中ほど 1MB、末尾 約 330KB) の md5 が一致した。全体の比較はしていないが、同じファイルの可能性が高い。planet.pmtiles が BMNG 版だと読める。
- planet_2.pmtiles と planet_3.pmtiles もバイト数とヘッダが同じで、途中 1MB の md5 が一致した。
- ファイル名のズームとヘッダのズームが 1 ずれている。planet_2024_8z は z0-7、planet_2024_10z は z0-9、planet_2024_12z は z0-11。planet_2024_8z のメタデータの name は `world_8z`。
- planet.pmtiles、planet_bmng、planet_2、planet_3、planet_copernicus、planet_gsi、world_2024 のメタデータの name は全部 `world_10z`。メタデータで区別できない。
- planet_gsi.pmtiles は 7,495 バイトでタイル 11 枚 (中身の違うもの 9 枚)。z0 から z10 まで東京付近へ 1 枚ずつ降りるだけの試作と読める。データとしては使えない。
- world_2024.pmtiles と planet_copernicus.pmtiles はタイル数 (7,729) と覆う範囲が同じだが、大きさは 28.7MB と 68.8MB で違う。
- 日本や東京の地域版 (atami, japan_sentinel-2, tokyo23_hls, tokyo23_sentinel-2) は z0-7 に全球のタイルを持ち、ヘッダの bounds は全球 (-180,-85,180,85) になっている。全球の下地の上に地域を重ねたもの。bounds を範囲として信じると誤る。
- planet_tokyo23_seamlessphoto.pmtiles の center 経度が -75.008 で、bounds (東経 139.56-139.92) の外にある。gsi/seamlessphoto/z2-z17.pmtiles にも同じ種類のずれがある。
- 地域版は 2026-06 の作成、全球版は 2025-09 から 2025-10 の作成 (Last-Modified)。

## ライセンス

- planetarble の README は「NASA/USGS はパブリックドメイン、NOAA ETOPO は CC0」と書いている。原典では未確認。
- BMNG (NASA Blue Marble Next Generation) の条件: 未確認。
- Copernicus (Sentinel-2) 由来のもの: 未確認 (メタデータに記載なし)。
- planet_tokyo23_seamlessphoto はメタデータに「国土地理院 seamlessphoto (CC BY 4.0)」とある。
- planet_atami: 元データもライセンスも未確認 (メタデータに記載なし)。z18 まであるので航空写真由来と思われるが確かめていない。

## 学習ステップでの使いどころ (案)

- ETOPO は標高と水深の格子として、ほぼそのまま特徴量になる。点に標高を付けて 1 線形回帰や 2 Random Forest の説明変数に、6 PCA の入力の 1 列に。標高差を辺の重みにすれば 7 Dijkstra/A* のコスト面にもなる。
- 衛星画像タイル (Sentinel-2、HLS) は表示用の RGB で、分光バンドや反射率は残っていない。画素の色を集計した特徴量 (緑の割合など) を作って 2 から 3 の分類、5 k-means での土地被覆のクラスタリング程度に使える。
- tokyo23 の 3 種 (HLS 30m、Sentinel-2 10m、航空写真) は同じ範囲を解像度違いで持つので、解像度が特徴量の効き方をどう変えるかを 4 Cross Validation で比べる題材になる。隣接タイルが似る空間自己相関はデータリークの例にもなる。
