# foil4gr1

2026-09-28 に読んで確かめた内容。数字はすべてこの日の実測。

- `https://source.coop/smartmaps/foil4gr1` (Web ページの名前は "FOIL4G Data Pack Release 1")
- Web ページの説明は "FOIL4G (Free and Open Information Library for Geospatial) Data Pack Release 1" の 1 行だけ。README.md は無い。
- 中身は互いに関係の薄い 7 つのベクトル PMTiles の寄せ集め。各ファイルの出典はどこにも書かれていない。

## ファイル

すべて PMTiles v3、ベクトルタイル (MVT)、タイルは gzip、生成は tippecanoe v2.28.0。

| key | 大きさ (バイト) | 更新 | ズーム | レイヤー (件数、形) | 属性 |
|---|---:|---|---|---|---|
| `44.pmtiles` | 864,758,710 | 2024-07-04 | 8-14 | terrain22 (778,982、Polygon) | terrain22 (1 から 22) |
| `fabdem-fiji.pmtiles` | 57,890,231 | 2024-07-20 | 9-14 | contour (139,075、LineString) | ID, h (0 から 1310) |
| `kpop.pmtiles` | 475,263,703 | 2024-08-19 | 0-9 | kpop (44,467,536、Polygon) | pop (1 から 1,141,305,573) |
| `reusable-h3-pmtiles/h3.pmtiles` | 337,919,649 | 2025-02-23 | 0-7 (ヘッダ) | h3 (16,525,525、Polygon) | h3, res (1 から 6) |
| `terrain22.pmtiles` | 23,169,587,933 | 2024-08-06 | 9-12 | terrain22 (43,965,174、Polygon) | terrain22 (1 から 22) |
| `tha-adm/a.pmtiles` | 127,340,020 | 2025-03-31 | 0-14 | adm0 から adm3, bndl, bndp | code, name, admLevel |
| `vientiane-landuse.pmtiles` | 14,436,715 | 2024-07-01 | 0-14 | landuse (24,491、Polygon) | l1, l2, 英名とラオ語名, area_ha など 9 つ |

件数は tilestats の値。bounds は次のとおり。

- 44: 91.147, 1.114, 109.470, 33.825 (東南アジア大陸部から中国南部あたり)
- fabdem-fiji: 170.186, -19.549, 179.999, -10.787 (フィジー)
- kpop, h3: ほぼ全世界
- terrain22: -180, -59.46, 180, 83.68
- tha-adm: 97.343, 5.613, 105.637, 20.465 (タイ)
- vientiane-landuse: 102.012, 17.804, 103.153, 18.439 (ラオスのビエンチャン)

## 各ファイルについて

- terrain22 と 44: 22 クラスの地形分類ポリゴン。値の意味 (どの分類体系か) は書かれていない。22 クラスの全球地形分類としては岩橋らの分類が知られているが、それかどうかは未確認。44 は terrain22 と同じレイヤー名と属性で、範囲だけ東南アジアに絞った版に見える (名前の 44 の意味は不明)。
- fabdem-fiji: 名前から FABDEM 由来の等高線と見られる (未確認)。h は 10 刻み。
- kpop: 人口 (pop) を持つポリゴン。出典も単位も書かれていない。最大値 1,141,305,573 は 1 つのポリゴンとしては大きすぎるので、階層的に集計した値が混ざっていると見られる (推測)。
- h3: H3 セルのポリゴン。解像度 (res) は 1 から 6。名前 (reusable) から、他のデータを載せるための空の格子と見られる。
- tha-adm: タイの行政区画。adm1 は 77 件 (TH10 など)、adm2 は 928 件、adm3 は 7,425 件、境界線 bndl 22,425 件、点 bndp 7,425 件。
- vientiane-landuse: ビエンチャンの土地利用。大分類 l1 が 8 種 (A, B, C, D, F, I, R, W)、小分類 l2 が 27 種。

## 気づいたこと

- h3.pmtiles: ヘッダの maxzoom は 7 だが、メタデータの maxzoom は 11、name は `9.mbtiles`。center_zoom も 11。作り直した跡が食い違っている。
- terrain22.pmtiles の antimeridian_adjusted_bounds が 0 から 360 になっている。
- vientiane-landuse の l1_name_e に `DEFEND  LAND` (空白 2 つ) と `DEFEND LAND` が並び、l1 が 8 種なのに l1_name_e は 9 種になっている。
- 44, tha-adm などでメタデータの name と description が `dst/44.pmtiles` や `docs/a.pmtiles` のような作者の手元のパスのまま。
- どのファイルにも出典の記述が無い。

## ライセンス

リポジトリ、Web ページ、メタデータのどれにもライセンスの記述は無かった。未確認。元データごとに条件が違うはずなので、使うならファイルごとに出典を特定する必要がある。

## 学習での使い道 (案)

- 2, 3: vientiane-landuse の l1 (8 クラス) を、面積や形状から分類する。小さく (14MB) 全体を取れるので最初の題材に向く。
- 4 データリーク: tha-adm の adm1 (77 県) をグループにした GroupKFold の題材。
- 9 facility location: kpop の人口を需要として、施設の置き場所を選ぶ。h3 の格子に人口を載せ替えると問題を作りやすい。
- 8 LP/MILP: 同じく人口と格子で、容量制約付きの割り当て。
- 7 Dijkstra/A*: fabdem-fiji の等高線から標高を補間し、傾斜をコストにした経路探索。
- 5 k-means: terrain22 のクラスと別の地形量を比べ、教師なしで似た区分が出るかを見る。
