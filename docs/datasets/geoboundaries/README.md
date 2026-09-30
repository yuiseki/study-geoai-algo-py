# geoBoundaries

2026-09-30 に読んで確かめた内容。件数と大きさは API (`https://www.geoboundaries.org/api/current/gbOpen/ALL/ALL/`) が返した 715 件のメタデータと、配布ファイルへの HEAD から。

- `https://www.geoboundaries.org/`。William & Mary の geoLab が作っている、全世界の行政区域。
- 配布は GitHub の `wmgeolab/geoBoundaries` の `releaseData/` 以下。API は各ファイルへの直リンクを返す。
- 系統が 3 つある。`gbOpen` が開いたライセンスのものだけを集めたもの、`gbHumanitarian` が OCHA 由来、`gbAuthoritative` が UN 由来。ここで見たのは `gbOpen`。

## 規模

| 階層 | 国・地域の数 | 単位の合計 |
|---|---:|---:|
| ADM0 | 230 | 230 |
| ADM1 | 199 | 3,281 |
| ADM2 | 180 | 49,363 |
| ADM3 | 81 | 105,170 |
| ADM4 | 21 | 94,251 |
| ADM5 | 4 | 699,798 |

715 件、232 の ISO コード。

Natural Earth と補い合う。Natural Earth の admin-2 は米国だけで 3,224 件 ([stac/](../stac/) ではなく `yuiseki/ne-admin0-10m` に入っている) だが、こちらは 180 の国と地域に ADM2 がある。逆に Natural Earth は 1 ファイルに全世界が入っていて版が固定されているのに対し、こちらは国ごとにファイルが分かれ、出どころも年も国ごとに違う。

## ライセンスは国ごと、しかも階層ごとに違う

`gbOpen` は「開いたライセンスのものだけ」という意味で、ライセンスが 1 つという意味ではない。715 件に 25 種類ある。

| ライセンス | 件数 |
|---|---:|
| ODbL 1.0 | 225 |
| Public Domain | 102 |
| CC BY 4.0 International | 102 |
| CC BY 3.0 IGO | 98 |
| CC BY 4.0 | 46 |
| CC BY-SA 2.0 | 33 |
| CC0 1.0 | 22 |
| (以下 18 種類) | 87 |

同じ国の中でも階層ごとに違う。日本の 3 階層はこうなっていた。

| 階層 | 単位 | canonical | 出どころ | ライセンス | 年 |
|---|---:|---|---|---|---|
| ADM0 | 1 | Japan | 国土数値情報 (国土交通省) | CC BY 4.0 | 2022 |
| ADM1 | 47 | Prefectures | OpenStreetMap, Wambacher | ODbL 1.0 | 2017 |
| ADM2 | 1,745 | Subprefectures | OpenStreetMap, Wambacher | CC BY-SA 2.0 | 2017 |

share-alike (ODbL か CC BY-SA) は 715 件中 270 件。ADM2 に限ると 180 件中 45 件が share-alike で、残り 135 件・36,925 単位は share-alike でない。取り込む先の方針によっては、この 135 件だけを使うことになる。

## 気をつけること

日本の ADM2 の canonical が Subprefectures なのに件数は 1,745。 支庁は北海道の 14 だけなので、名前と中身が合っていない。市区町村 (1,741、`yuiseki/jp-admin-2026-09`) に近い。`boundaryCanonical` は出どころが自称した呼び名で、階層の意味は国ごとに違う。ADM2 を「同じ粒度」として国をまたいで比べてはいけない。

年が揃っていない。 `boundaryYearRepresented` は 1995 から 2022 まで散らばり、`09-09-2017 to 24-08-2020` のような期間を書いた行もある。日本は ADM0 が 2022 で ADM1/ADM2 が 2017。同じ国の中でも階層によって時点が違う。

出どころがデータでないものが混じっている。 台湾の ADM0 は `boundarySource` が `geoBoundaries, Pixabay`、`licenseSource` が `pixabay.com/vectors/taiwan-map-roc-republic-of-china-33713/`。ストックのクリップアートから起こした国境。ポーランドの ADM0 は `Wiki Commons Media`。国境が政治的に難しい地域では、測量ではなく絵が入っていることがある。

日本に ADM3 は無い。 API は 404 を返す。町丁・字の粒度が要るなら国勢調査の小地域境界 (`yuiseki/estat-boundary-2020`) を使う。

## ファイルの形

API の 1 件が返す配布先は 5 つ。日本の ADM2 の例。

| 種類 | URL の末尾 | 大きさ |
|---|---|---:|
| 一式 (Shapefile 他) | `geoBoundaries-JPN-ADM2-all.zip` | 11,540,370 |
| GeoJSON | `geoBoundaries-JPN-ADM2.geojson` | 10,897,321 |
| GeoJSON (簡略化) | `geoBoundaries-JPN-ADM2_simplified.geojson` | 未計測 |
| TopoJSON | `geoBoundaries-JPN-ADM2.topojson` | 未計測 |
| 画像 | `geoBoundaries-JPN-ADM2-PREVIEW.png` | 未計測 |

URL には commit hash が入る (日本の ADM2 は `9469f09`)。版を固定して引ける。

メタデータには形の統計も入っていて、そのまま使える。日本の ADM2 なら頂点数の平均 218、最小 5、最大 1,553。面積の平均 213.59 km2、最小 0.0012 km2、最大 2,177.56 km2。
