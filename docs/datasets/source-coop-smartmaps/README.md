# source.coop/smartmaps

<https://source.coop/smartmaps> は Source Cooperative 上の smartmaps の置き場。18 リポジトリ。
2026-09-28 に S3 互換の一覧 (`https://data.source.coop/smartmaps?list-type=2&prefix=<repo>/`) で確かめた。

## リポジトリ

ファイル数と合計の「以上」は、一覧を途中まで数えたところで止めたもの。「(マニフェスト)」は、リポジトリ内のマニフェストを数えた値 (バケットの実物との一致は未確認)。

| リポジトリ | ファイル数 | 合計 | 主な形式 | 中身 | 詳細 |
|---|---:|---:|---|---|---|
| adopt-hokkaido-lidar | 3,541 | 199.69GB | laz | 北海道庁の航空レーザを COPC 化 (LAS 1.4、平面直角 XII 系) | [adopt-hokkaido-lidar.md](adopt-hokkaido-lidar.md) |
| amx-2024-04 | 1 | 16.23GB | pmtiles | 法務省地図 XML の筆ポリゴン (2024-04)、MVT、z14-16、約 1.09 億件 | [amx-2024-04.md](amx-2024-04.md) |
| cogenerate | 158 | 427.71GB | tif | 国土地理院の災害時空中写真などの COG (RGBA, 3857, z18)。標高ではない | [cogenerate.md](cogenerate.md) |
| dem10a | 1 | 0.70GB | pmtiles | 仙台周辺の標高 PMTiles。z3-17、WebP、Terrain-RGB | [dem10a.md](dem10a.md) |
| dem1a | 2 | 2.65GB | pmtiles | 国土地理院 1m DEM の PMTiles。東北太平洋側、z3-17、Terrain-RGB | [dem1a.md](dem1a.md) |
| foil4gr1 | 7 | 25.05GB | pmtiles | 地形分類 22 区分・人口・H3 格子・タイの行政区画・ビエンチャンの土地利用などの寄せ集め | [foil4gr1.md](foil4gr1.md) |
| gel | 2 | 195.96GB | pmtiles | 全世界の標高 terrain RGB (WebP)、NASADEM と地球地図、z2-12、CC0 | [gel.md](gel.md) |
| h3ys-worldpop | 12 | 0.78GB | pmtiles | WorldPop 人口 2000〜2020 を H3 res5-9 で集計した国別ベクトル (9 か国) | [h3ys-worldpop.md](h3ys-worldpop.md) |
| japan-geotiff-dem | 784,898 (マニフェスト) | 376.69GB (マニフェスト) | tif | 国土地理院 DEM 1/5/10m の GeoTIFF (EPSG:6668, Float32) | [japan-geotiff-dem.md](japan-geotiff-dem.md) |
| japan-seamlessphoto | 4 | 1,192.53GB | pmtiles | 国土地理院シームレス空中写真 JPEG、z1-17 (512px) と z18 の 2 本 | [japan-seamlessphoto.md](japan-seamlessphoto.md) |
| mapterhorn-japan-bridge | 2 | 2.01GB | pmtiles | 北海道南西部の地形タイル。Terrarium WebP、z6-16 (暫定) | [mapterhorn-japan-bridge.md](mapterhorn-japan-bridge.md) |
| mobility-gtfs-pmtiles | 2 | 0.69GB | pmtiles | Mobility Database の全 GTFS の停留所と路線、運行頻度つき (2024-04) | [mobility-gtfs-pmtiles.md](mobility-gtfs-pmtiles.md) |
| next-ksj | 7 | 0.96GB | fgb, pmtiles | 国土数値情報のサンプル 3 種 (地価公示 2024、行政区域 2024、河川) | [next-ksj.md](next-ksj.md) |
| ngs | 81,030 以上 | 11.39GB 以上 | pnts | Open Nagasaki の LiDAR 全域を 1 つの点群 3D Tiles にしたもの (XYZ と RGB のみ) | [ngs.md](ngs.md) |
| opencellid | 1 | 0.56GB | pmtiles | OpenCelliD の基地局 約 484 万点 (2024-06-14 時点) | [opencellid.md](opencellid.md) |
| toshik | 2 | 0.16GB | pmtiles | 国交省の都市計画決定 GIS。用途地域など 21 レイヤー、全国分 | [toshik.md](toshik.md) |
| uppsala-conflict | 1 | 0.14GB | pmtiles | UCDP GED 23.1 の紛争イベント 31.7 万点 (1989〜2022) | [uppsala-conflict.md](uppsala-conflict.md) |
| xing | 58,002 以上 | 14.09GB 以上 | b3dm, json, mvt | PLATEAU の 3D Tiles (b3dm) と MVT。6,419 データセット、建物の属性付き | [xing.md](xing.md) |

## 読むときの注意

- ファイルの URL は `https://data.source.coop/smartmaps/<key>`。
- 1 ファイルの調査は 60 秒で打ち切る。巨大ファイルは Range 要求で必要な部分だけ読む。
- 一覧を数えるときは `continuation-token` だけでたどる。`start-after` は当てにならず、あるはずの件数が 0 件で返ったり、サブディレクトリを飛ばしたりした。

## 取り出し方

range。ファイルを選ぶところは catalog に近い。2026-09-30 に実測した。

ファイルの選び方は S3 互換の一覧。`https://data.source.coop/smartmaps?list-type=2&prefix=amx-2024-04/` は 200 で 485 バイトを返し、`<Key>amx-2024-04/MojMap_amx_2024.pmtiles</Key>` と `<Size>16225577433</Size>` が入っている。認証は要らない。bbox や日時での絞り込みはできないので STAC のような目録ではないが、prefix で repo ごとに引けて、キーと大きさが分かる。

引いたファイルは Range が効く。`https://data.source.coop/smartmaps/amx-2024-04/MojMap_amx_2024.pmtiles` の HEAD は 200 で `Content-Length` 16,225,577,433、`Accept-Ranges: bytes`、`Last-Modified` Thu, 18 Apr 2024 10:34:15 GMT、`Server: cloudflare`。`curl -s -r 0-1023` は 206 と 1,024 バイトを返した。

先頭 127 バイトの Range 要求も 206 と 127 バイト。先頭 7 バイトは `PMTiles`、8 バイト目 (spec version) は 3。

| 項目 | MojMap_amx_2024.pmtiles | opencellid/cellid.pmtiles |
|---|---:|---:|
| 大きさ | 16,225,577,433 | 559,569,057 |
| ルートディレクトリの位置 / 長さ | 127 / 1,301 | 127 / 1,616 |
| メタデータの位置 / 長さ | 1,428 / 2,337 | 1,743 / 2,377 |
| 葉ディレクトリの位置 / 長さ | 3,765 / 2,737,278 | 4,120 / 2,519,411 |
| タイルデータの位置 | 2,741,043 | 2,523,531 |
| アドレスされたタイル数 | 1,217,008 | 1,364,455 |
| ズーム | 14 から 16 | 0 から 14 |

ズームはヘッダの 101 バイト目と 102 バイト目、bounds は 103 バイト目からの int32 4 つ (1e-7 度単位) を読んだ値。amx は経度 122.934191 から 145.816789、緯度 24.045645 から 46.051342。cellid は経度 -175.3443 から 179.3287999、緯度 -54.8428999 から 78.2295 で、全世界に散っている。

PMTiles 以外も同じ。`cogenerate/19480000dol.tif` は HEAD が 200 で `Content-Length` 354,029,890、`Accept-Ranges: bytes`、`curl -s -r 0-1023` が 206 と 1,024 バイト。先頭 4 バイトは `II+\0` で、版番号 43、オフセット幅 8 の BigTIFF。9 バイト目からの uint64 を読むと最初の IFD が 200 バイト目にある。索引がファイルの先頭付近にあるので、COG として必要なタイルだけ引ける。

例外になりうるのは、そもそも 1 ファイルが小さくて分割で足りる repo (ngs の pnts、xing の b3dm、japan-geotiff-dem の tif は数万から数十万ファイル) で、こちらは split として扱うほうが自然になる。この節で Range を確かめたのは amx-2024-04、opencellid、cogenerate の 3 つで、残りの 15 repo は未確認。同じ `data.source.coop` の配信なので同じ結果になると考えられるが、確かめてはいない。
