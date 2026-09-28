# h3ys-worldpop

2026-09-28 に読んで確かめた内容。

- `https://source.coop/smartmaps/h3ys-worldpop`
- WorldPop の Population Counts (Unconstrained individual countries 2000-2020, 元は 100m 解像度) を H3 で集計し、国ごとに PMTiles にしたもの (リポジトリ内 README.md より)。
- 作り方は <https://github.com/hfu/worldpop-h3> にある (README から参照)。2026-09-28 時点の main の中身は次のとおり。配置済みファイルがこの版のスクリプトで作られたかは確かめていない。
  - `download.rb`: `https://data.worldpop.org/GIS/Population/Global_2000_2020/<年>/<ISO3>/<iso3>_ppp_<年>.tif` を 2000 年から 2020 年まで取得。
  - `filter.rb`: `gdalwarp -of XYZ` で画素を点にし、NODATA と 0 を捨て、各点を H3 解像度 5 から 9 の全セルに割り当てる。
  - `reduce.rb`: H3 セルごとに年別の人口を合計して四捨五入し、六角形ポリゴンの GeoJSON にする。解像度ごとに表示ズームを分ける (res5: z1-5, res6: z6-7, res7: z8-9, res8: z10-11, res9: z12)。
  - `Makefile`: `tippecanoe --maximum-zoom=12` で PMTiles にし、`s3://smartmaps/h3ys-worldpop/` へ同期。
- 本家 WorldPop の置き場については [../stac/worldpop.md](../stac/worldpop.md)。

## ファイル

| ファイル | 大きさ (バイト) | 実体 | 範囲 (bounds) | タイル数 | tilestats の地物数 |
|---|---:|---|---|---:|---:|
| bgd.pmtiles | 91,758,035 | PMTiles v3 | 87.92, 20.49, 92.86, 26.71 | 2,898 | 1,424,209 |
| fin.pmtiles | 110,513,351 | PMTiles v3 | 20.22, 59.72, 31.69, 70.17 | 27,341 | 4,665,788 |
| jor.pmtiles | 18,168,516 | PMTiles v3 | 34.82, 29.05, 39.40, 33.46 | 1,981 | 878,855 |
| jpn.pmtiles | 184,919,967 | PMTiles v3 | 122.80, 23.99, 154.12, 45.65 | 11,101 | 4,732,938 |
| khm.pmtiles | 50,790,530 | PMTiles v3 | 102.20, 9.84, 107.76, 14.78 | 3,036 | 1,721,458 |
| nga.pmtiles | 28,672 | 空の MBTiles (SQLite) | なし | 0 | なし |
| png.pmtiles | 84,499,298 | PMTiles v3 | 140.74, -11.80, 157.09, -0.66 | 8,795 | 4,712,171 |
| sen.pmtiles | 54,693,635 | PMTiles v3 | -17.59, 12.23, -11.20, 16.80 | 3,334 | 2,294,720 |
| tha.pmtiles | 176,811,448 | PMTiles v3 | 97.23, 5.53, 105.81, 20.59 | 8,945 | 4,876,471 |
| tls.pmtiles | 5,264,943 | PMTiles v3 | 123.92, -9.61, 127.38, -8.02 | 364 | 162,379 |
| ukr.pmtiles | 28,672 | 空の MBTiles (SQLite) | なし | 0 | なし |
| README.md | 450 | Markdown | | | |

- タイル数はヘッダの addressed tiles。10 ファイルとも addressed = entries = contents で、重複タイルは無い。
- tilestats の地物数は H3 解像度 5 から 9 のセルをすべて含む数 (上の作り方のとおりなら、同じ場所が解像度の数だけ重なって数えられる)。

## 中身 (PMTiles の 9 ファイル共通)

- ヘッダ: ズーム 0 から 12、タイル形式 MVT (tile_type 1)、タイル圧縮 gzip、内部圧縮 gzip、clustered。
- 生成: `tippecanoe v2.28.0`, `tippecanoe '--maximum-zoom=12' -f -o dst/<iso3>.pmtiles`。
- レイヤーは `pop` の 1 つ、ジオメトリは Polygon (H3 六角形)。
- 属性は `2000` から `2020` の 21 列 (Number)。その年の人口の合計を四捨五入した値。H3 セル ID は属性に無い。
- tilestats の最大値 (1 セル) の例: jpn は 2000 年 3,401,930、2020 年 4,035,768。最小値はどの国も 0。

## 気づいた異常

- `nga.pmtiles` と `ukr.pmtiles` は 28,672 バイトの SQLite (MBTiles の形) で、PMTiles ではない。metadata, map, images の 3 表とも 0 行。拡張子は .pmtiles。ナイジェリアとウクライナは作りかけで止まったものと見られる (推測)。
- ヘッダの center が国の中心ではなく端に寄っている (例: jpn は 123.79, 24.33)。表示の初期位置に使うとずれる。
- README の対象は「individual countries」だが、置かれているのは 11 か国分 (うち中身があるのは 9 か国)。

## ライセンス

- データ: 未確認 (リポジトリ内 README にも source.coop のページにも記載が見当たらない)。元の WorldPop の条件を別途確かめる必要がある。
- 作成スクリプトの GitHub リポジトリ (hfu/worldpop-h3) の LICENSE は CC0 1.0。これはコードの条件で、データの条件ではない。

## 12 ステップでの使いみち (案)

- 1 線形回帰: 2000 年から 2019 年の人口から 2020 年を予測する。セル単位の時系列回帰。
- 2, 3 決定木 / GBDT: 他のデータ (道路、土地利用) と H3 で結合した特徴量から人口や増減を予測する。
- 4 CV とデータリーク: 隣接セルや親子解像度のセルが同じ値を共有するので、空間ブロック CV の題材になる。解像度 5 と 9 を混ぜると漏れる。
- 5 k-means / DBSCAN: 年別の人口推移の形でセルをクラスタリングする。
- 6 PCA: 21 年分の列を圧縮する。第 1 成分は規模、第 2 成分は増減傾向になるかを確かめる。
- 9 facility location: 人口を需要点の重みにして施設配置を解く。
- 注意: 使うには MVT をデコードして GeoJSON や表に戻す必要がある。H3 ID は六角形の重心から復元する。
