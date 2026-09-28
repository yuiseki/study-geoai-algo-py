# source.coop/smartmaps

<https://source.coop/smartmaps> は Source Cooperative 上の smartmaps の置き場。18 リポジトリ。
2026-09-28 に S3 互換の一覧 (`https://data.source.coop/smartmaps?list-type=2&prefix=<repo>/`) で確かめた。

## リポジトリ

ファイル数の「20,000 以上」は、一覧の取得を 20,000 件で止めたもの。「(マニフェスト)」は、リポジトリ内のマニフェストを数えた値 (バケットの実物との一致は未確認)。

| リポジトリ | ファイル数 | 合計 | 主な形式 | 中身 | 詳細 |
|---|---:|---:|---|---|---|
| adopt-hokkaido-lidar | 3,541 | 199.69GB | laz | (調査中) | [adopt-hokkaido-lidar.md](adopt-hokkaido-lidar.md) |
| amx-2024-04 | 1 | 16.23GB | pmtiles | 法務省地図 XML の筆ポリゴン (2024-04)、MVT、z14-16、約 1.09 億件 | [amx-2024-04.md](amx-2024-04.md) |
| cogenerate | 158 | 427.71GB | tif | 国土地理院の災害時空中写真などの COG (RGBA, 3857, z18)。標高ではない | [cogenerate.md](cogenerate.md) |
| dem10a | 1 | 0.70GB | pmtiles | 仙台周辺の標高 PMTiles。z3-17、WebP、Terrain-RGB | [dem10a.md](dem10a.md) |
| dem1a | 2 | 2.65GB | pmtiles | 国土地理院 1m DEM の PMTiles。東北太平洋側、z3-17、Terrain-RGB | [dem1a.md](dem1a.md) |
| foil4gr1 | 7 | 25.05GB | pmtiles | 地形分類 22 区分・人口・H3 格子・タイの行政区画・ビエンチャンの土地利用などの寄せ集め | [foil4gr1.md](foil4gr1.md) |
| gel | 2 | 195.96GB | pmtiles | 全世界の標高 terrain RGB (WebP)、NASADEM と地球地図、z2-12、CC0 | [gel.md](gel.md) |
| h3ys-worldpop | 12 | 0.78GB | pmtiles | (調査中) | [h3ys-worldpop.md](h3ys-worldpop.md) |
| japan-geotiff-dem | 784,898 (マニフェスト) | 376.69GB (マニフェスト) | tif | 国土地理院 DEM 1/5/10m の GeoTIFF (EPSG:6668, Float32) | [japan-geotiff-dem.md](japan-geotiff-dem.md) |
| japan-seamlessphoto | 4 | 1,192.53GB | pmtiles | 国土地理院シームレス空中写真 JPEG、z1-17 (512px) と z18 の 2 本 | [japan-seamlessphoto.md](japan-seamlessphoto.md) |
| mapterhorn-japan-bridge | 2 | 2.01GB | pmtiles | 北海道南西部の地形タイル。Terrarium WebP、z6-16 (暫定) | [mapterhorn-japan-bridge.md](mapterhorn-japan-bridge.md) |
| mobility-gtfs-pmtiles | 2 | 0.69GB | pmtiles | (調査中) | [mobility-gtfs-pmtiles.md](mobility-gtfs-pmtiles.md) |
| next-ksj | 7 | 0.96GB | fgb, pmtiles | (調査中) | [next-ksj.md](next-ksj.md) |
| ngs | 20,000 以上 | 2.72GB 以上 | pnts | (調査中) | [ngs.md](ngs.md) |
| opencellid | 1 | 0.56GB | pmtiles | (調査中) | [opencellid.md](opencellid.md) |
| toshik | 2 | 0.16GB | pmtiles | (調査中) | [toshik.md](toshik.md) |
| uppsala-conflict | 1 | 0.14GB | pmtiles | (調査中) | [uppsala-conflict.md](uppsala-conflict.md) |
| xing | 20,000 以上 | 9.53GB 以上 | b3dm, json | (調査中) | [xing.md](xing.md) |

## 読むときの注意

- ファイルの URL は `https://data.source.coop/smartmaps/<key>`。
- 1 ファイルの調査は 60 秒で打ち切る。巨大ファイルは Range 要求で必要な部分だけ読む。
