# ESA WorldCover

2026-09-30 に読んで確かめた内容。件数と大きさは AWS のバケットへの匿名の一覧要求と HEAD、ライセンスは本家のデータアクセスページの本文。

- ESA が Sentinel-1 と Sentinel-2 から作った全球 10m の土地被覆。11 区分。
- 案内: `https://esa-worldcover.org/`
- 配布: `https://esa-worldcover.s3.eu-central-1.amazonaws.com/` (AWS Open Data)
- 版は v100 (2020 年) と v200 (2021 年)。どちらもタイル 2,651 枚。

## ログイン不要で Cloud Native に読める

これがこの出典の一番の利点なので先に書く。認証もトークンも要らない。

バケットの一覧が匿名で返る。

```
https://esa-worldcover.s3.eu-central-1.amazonaws.com/?list-type=2&prefix=v200/2021/map/
```

タイルは COG で、Range 要求が効く。日本を含む N33E135 のタイルで確かめた値。

| 項目 | 値 |
|---|---|
| ファイル | `v200/2021/map/ESA_WorldCover_10m_2021_v200_N33E135_Map.tif` |
| 大きさ | 12,660,256 バイト |
| Range 要求 | 先頭 1,024 バイトを要求して 206 と 1,024 バイトが返る |
| TIFF ヘッダ | `II*\0` (リトルエンディアン)、最初の IFD がオフセット 192 |

IFD がファイルの先頭付近にあるので、全体を落とさずにヘッダだけ読んで必要な部分だけ取れる。バケットの readme も自ら COG と書いている。

> The ESA WorldCover 10 m 2020 V100 product is delivered in 3x3 degree tiles as Cloud Optimized GeoTIFFs (COGs) in EPSG:4326 projection (geographic latitude/longitude CRS). There are 2651 tiles

STAC カタログはバケットの中には無い (`v200/2021/stac/catalog.json` は 404)。代わりにタイルの格子が 2 つの形式で置いてある。

| ファイル | 中身 |
|---|---|
| `esa_worldcover_grid.geojson` | 543,674 バイト、2,651 フィーチャ、属性は `ll_tile` のみ |
| `esa_worldcover_grid.fgb` | 同じものの FlatGeobuf |

格子で空間検索してからタイルを Range で読めば、STAC を介すのと同じことができる。FlatGeobuf のほうは Range 要求で部分読みできるので、格子ファイル自体も全部落とす必要が無い。

## ライセンス

本家のデータアクセスページの本文。

> The ESA WorldCover product is provided free of charge, without restriction of use. For the full license information see the Creative Commons Attribution 4.0 International License.

CC BY 4.0。share-alike は無い。バケットの readme が求める表示文は次のとおり。

> © ESA WorldCover project 2020 / Contains modified Copernicus Sentinel data (2020) processed by ESA WorldCover consortium

出版物で使うときは論文の引用も求めている。

## 中身

- 10m 解像度、EPSG:4326、3 度四方のタイル。
- 各タイルに 2 つの層がある。`Map` が 11 区分の土地被覆、`InputQuality` が Sentinel-1 と Sentinel-2 の入力の品質指標 3 バンド。
- `Map` だけで v100 が約 117GB (readme の記載)。

## 気をつけること

`Map` と `InputQuality` はどちらも `v200/2021/map/` ではなく別のプレフィックスに分かれる。この項目で数えた 2,651 は `map/` のオブジェクト数で、`InputQuality` は含まない。

バケットの readme は v100 (2020 年) について書かれていて、v200 の説明ではない。タイル数はどちらも 2,651 で同じだが、区分の定義や精度が同じとは限らない。v200 を使うなら本家の技術資料を見る必要がある。

土地被覆は推定であって観測ではない。10m の格子ごとに 11 区分のどれかを当てたもので、境界は滑らかでなく、区分の取り違えがある。全球で同じ方法という利点と引き換えに、特定の国について地元のデータより正確だとは限らない。

2020 年と 2021 年の 2 時点しかない。時系列としては短く、変化の検出には足りない。長い時系列が要るなら [GHSL](../ghsl/README.md) は 1975 年から 2030 年まである (ただし測るものが違う)。
