# NOAA ETOPO 2022

2026-09-30 に読んで確かめた内容。件数と大きさは NOAA NCEI の配布ディレクトリの一覧と HEAD による実測。ライセンスは NCEI が公開している ISO メタデータの本文。

- 配布元: `https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/`
- 案内: `https://www.ncei.noaa.gov/products/etopo-global-relief-model`
- 中身は全球の地形と水深を 1 つに繋いだ標高格子。陸の標高、海の水深、湖底、氷床の表面と氷の下の岩盤を含む。
- DOI は `10.25921/fd45-gt74`。
- 解像度は 15 秒、30 秒、60 秒の 3 段。垂直基準は EGM2008 (GeoTIFF の ImageDescription タグが `Topography-Bathymetry; EGM2008 height`)。
- planetarble (`configs/base/pipeline.yaml`) は `ocean.source_id: etopo_2022_15arcsec_geotiff` でこれを海の描画に使い、深さの色分けと lambertian ヒルシェードを掛ける。

## 配布の形 (実測した一覧)

15 秒は 15 度四方のタイルに分かれる。surface (氷の表面を含む地表) と bed (氷の下の岩盤) で枚数が違う。

| ディレクトリ | ファイル数 | 備考 |
|---|---:|---|
| `data/15s/15s_surface_elev_gtif/` | 288 | 緯度 12 帯 x 経度 24 列。全球を覆う |
| `data/15s/15s_bed_elev_gtif/` | 62 | N90/N75/N60 と S60/S75 の帯だけ。極地方のみ |
| `data/15s/15s_surface_sid_gtif/` | 未確認 | 元データの種別を示す格子 |
| `data/15s/15s_bed_sid_gtif/` | 未確認 | |
| `data/15s/15s_geoid_gtif/` | 未確認 | |

bed が 62 枚しかないのは、氷床の下でしか surface と bed が違わないため。15 秒の岩盤標高は全球 1 枚の GeoTIFF としては配布されていない。

30 秒と 60 秒は全球 1 枚。

| ファイル | バイト数 | 画素数 |
|---|---:|---|
| `data/30s/30s_bed_elev_gtif/ETOPO_2022_v1_30s_N90W180_bed.tif` | 1,624,895,430 | 43200 x 21600 |
| `data/30s/30s_surface_elev_gtif/ETOPO_2022_v1_30s_N90W180_surface.tif` | 1,585,813,987 | 未確認 |
| `data/60s/60s_bed_elev_gtif/ETOPO_2022_v1_60s_N90W180_bed.tif` | 478,386,633 | 未確認 |

15 秒タイルの大きさの例 (HEAD の Content-Length)。

| タイル | バイト数 |
|---|---:|
| `ETOPO_2022_v1_15s_N45E120_surface.tif` | 20,965,352 |
| `ETOPO_2022_v1_15s_S45W075_surface.tif` | 18,054,730 |
| `ETOPO_2022_v1_15s_N45E135_surface.tif` (日本を含む) | 17,959,004 |
| `ETOPO_2022_v1_15s_N30E135_surface.tif` | 13,867,975 |
| `ETOPO_2022_v1_15s_S75E135_bed.tif` | 26,183,613 |

## 取り出し方

split。1 枚の中は range。

- 15 秒は 15 度四方の 288 枚 (surface) に事前分割されている。必要な範囲のタイルだけを名前で指定して引ける。名前は北西の角の緯度経度で、日本は `N45E135`。
- `https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/ETOPO_2022_v1_15s_N45E135_surface.tif` に `Range: bytes=0-1023` を投げて HTTP 206、1,024 バイトが返る。HEAD は HTTP 200、`accept-ranges: bytes`、`content-length: 17959004`、`last-modified: Tue, 04 Oct 2022 21:51:01 GMT`。
- 先頭 1,024 バイトを読むと `II*\0` でリトルエンディアン、IFD はオフセット 8、つまりファイルの先頭。タグは ImageWidth 3600、ImageLength 3600、BitsPerSample 32、SampleFormat 3 (浮動小数)、Compression 8 (Deflate)、TileWidth 256、TileLength 256、TileOffsets の要素数 225 (15 x 15 のタイル格子)。NODATA は `-99999`。
- タイル化されていて索引が先頭にあるので、1 枚の中でも窓読みができる。オーバービューがあるかどうかは先頭 1KB からは確かめていない (未確認)。
- 30 秒の全球 1 枚も同じ構造で range が効く。`ETOPO_2022_v1_30s_N90W180_bed.tif` に `Range: bytes=0-1023` を投げて HTTP 206、IFD はオフセット 8、43200 x 21600 の float32、Deflate、256 x 256 のタイル (TileOffsets の要素数 14365)。全球を 1.6GB で 1 枚に収めつつ部分読みできるので、実用上はこちらが扱いやすい。
- COG の証拠であるゴーストヘッダ (`GDAL_STRUCTURAL_METADATA`) は入っていない。タイル TIFF ではあるが COG とは名乗っていない。

## ライセンス

NCEI が公開している ISO メタデータ (`https://www.ngdc.noaa.gov/metadata/published/NOAA/NESDIS/NGDC/MGG/DEM/iso/xml/etopo_2022.xml`、今日は `https://data.noaa.gov/waf/...` に 200 でリダイレクトされる) の `gmd:otherConstraints` に、権利放棄がはっきり書いてある。

> These data were produced by NOAA and are not subject to copyright protection in the United States. NOAA waives any potential copyright and related rights in these data worldwide through the Creative Commons Zero 1.0 Universal Public Domain Dedication (CC0-1.0).

同じ文書の `gmd:useLimitation`。

> Produced by the NOAA National Centers for Environmental Information. Not subject to copyright protection within the United States.

引用の依頼も同じ `otherConstraints` に入っている。

> Cite as:NOAA National Centers for Environmental Information. 2022: ETOPO 2022 15 Arc-Second Global Relief Model. NOAA National Centers for Environmental Information. https://doi.org/10.25921/fd45-gt74 . Accessed [date].

用途の制限が 1 つだけある。

> Not to be used for navigation. Although these data are of high quality and useful for planning and modeling purposes, they are not suitable for navigation. For navigation, please refer to the NOS nautical chart series.

読み取れること。ETOPO 2022 は CC0 1.0 である。米国内で著作権の対象にならないというだけでなく、世界に対して明示的に権利を放棄している。表示は義務ではなく「Cite as」の依頼。航海に使うなという但し書きは著作権の条件ではなく、安全上の注意。この 4 つのうち、CC0 と明記されている点で ETOPO は [Landsat](../landsat-c2-l2/README.md) の「制限なし」や [GEBCO](../gebco/README.md) の「public domain だが表示は義務」より強い。

合成物としての注意。ETOPO 2022 は独自に測ったものではなく、既存のデータを重ねたもの。ユーザーガイド (`https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/docs/1.2%20ETOPO%202022%20User%20Guide.pdf`、852,374 バイト) の出典表 (Source Name / layer source id / Creator) の 1 行目と 2 行目がこれ。

- layer source id 1: 「GEBCO 2022」、Creator「GEBCO Compilation Group (2022)」、用途「Sea bathymetry base layer, large lake bathy」
- layer source id 2: 「GEBCO 2022 MSL sub-ice」、Creator「GEBCO Compilation Group (2022)」、用途「Sea bathymetry (sub-ice, polar regions)」
- layer source id 12: 「GEBCO Lake Depths」、用途「surveyed lake depths (very large lakes)」

つまり ETOPO 2022 の海の部分は GEBCO 2022 である。GEBCO の条件は「public domain だが出典の表示は義務」なので、その義務は ETOPO 経由でも付いて回ると読むのが素直。NOAA の CC0 宣言は NOAA が持ちうる権利についての放棄であって、GEBCO が課す表示義務を消すものではない。ETOPO の ISO メタデータには GEBCO の文字は 1 度も出てこないので、この対応はメタデータからは辿れない (ユーザーガイドを読んで初めて分かる)。

## 気をつけること

planetarble の `configs/base/assets.yaml` が ETOPO の取得先にしている `https://storage.googleapis.com/natcap-data-cache/global/etopo-noaa-ngdc/noaa-ngdc-etopo-bedrock-bathymetry.tif` は、今日 HEAD も Range も HTTP 403 を返す (本文 432 バイトの XML)。NOAA ではなく natcap の複製で、しかも今は読めない。README が書く「≈9 GB compressed」の元もこの URL なので、その数字は今日は確かめられない (未確認)。NOAA から直接取るなら 30 秒の全球 1 枚 (1,624,895,430 バイト) か、15 秒の 288 タイルになる。

planetarble は保存先を `data/etopo/ETOPO_2022_15s_bed.tif` と名付けて「global 15 arc-second bedrock GeoTIFF」と書くが、NOAA が配る 15 秒の bed GeoTIFF は極地方の 62 枚だけで、全球 1 枚のものは存在しない。名前と実物が一致しない。海の描画が目的なら bed (氷の下の岩盤) ではなく surface のほうが素直で、そちらは 288 枚で全球を覆う。

assets.yaml の license 欄は NOAA National Centers for Environmental Information (2022) の CC0 1.0 としている。これは ISO メタデータの記述と一致していて、正しい。ただし上に書いたとおり、海の部分の GEBCO 由来の表示義務はこの一文では拾えない。

NODATA が `-99999` で、float32。整数として読むと海面下の値と NODATA を取り違える。

垂直基準は EGM2008 のジオイド高。楕円体高を前提にした標高データと重ねるとずれる。

15 秒タイルの名前は北西の角。`N45E135` は北緯 30 度から 45 度、東経 135 度から 150 度を覆う。名前の緯度が下端だと思い込むと 1 枚ずれる。

## 学習ステップでの使いどころ (案)

- 標高と水深を同じ格子で扱えるので、海岸線をまたぐ特徴量を作れる。1 から 3 の回帰と分類で「海からの深さ」「海抜」を同じ列として持てる。
- 7 Dijkstra/A*: 陸の標高差を辺のコストにする。海を通れない制約も同じ格子で表せる。
- 9 facility location: 標高を浸水しにくさの代理にする。
- 陸だけの高精度な標高が要るなら [Mapterhorn](../mapterhorn/README.md) (Copernicus GLO-30 と各国の高精度 DEM) か [NASA SRTM](../nasa-srtm/README.md)。海の水深の原本は [GEBCO](../gebco/README.md)。ETOPO はその両方を 1 つの格子に繋いだものなので、繋ぎ目の扱いを学ぶ題材にもなる。
- 必要な範囲だけなら 15 秒の 1 タイル (約 18MB) で足りる。全球の概観なら 60 秒の 478MB。
