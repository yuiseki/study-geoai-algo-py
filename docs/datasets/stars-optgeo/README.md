# stars.optgeo.org (Martin のタイルサーバー)

2026-09-28 にカタログ (`https://stars.optgeo.org/catalog`) と bvmap の TileJSON を読んで確かめた内容。

- タイルサーバー: <https://stars.optgeo.org/> (Martin)。管理のリポジトリは <https://github.com/hfu/stars>
- 見つけた経緯: dwg7 の知識ベース <https://github.com/dwg7/cafebabe> の PROJECTS.md (コミット 2f4c0f2、2026-09-24)。cafebabe はデータではなく、dwg7 と hfu のプロジェクトの一覧と作業の知見をまとめたリポジトリで、プロジェクトの多くは北海道のもの。

## 中身

タイル 43、スタイル 8、スプライト 3、フォント 12。表示用のタイルなので、分析には元データを使う。

| まとまり | レイヤー | このリポジトリでの扱い |
|---|---|---|
| 国土地理院のシームレス空中写真 | japan-seamless-aerial-z18、seamlessphoto512、kitaphoto、kitaphoto17 | 元の PMTiles は [z.yuiseki.net の gsi](../z-yuiseki-static/gsi.md) と [smartmaps/japan-seamlessphoto](../source-coop-smartmaps/japan-seamlessphoto.md) |
| 標高 | mapterhorn-japan-bridge、mapterhorn-japan-bridge-lineage | [smartmaps/mapterhorn-japan-bridge](../source-coop-smartmaps/mapterhorn-japan-bridge.md) |
| Overture | overture_addresses、_base、_buildings、_divisions、_places、_transportation | [Overture Maps](../stac/overture-maps.md) |
| OSM | openstreetmap_jp_planet | [OpenStreetMap Japan PMTiles](../openstreetmap-japan-pmtiles/README.md) |
| 国土地理院の最適化ベクトルタイル | bvmap | 下を見る |
| 北海道 | vbm、vlcm (火山基本図など)、pmtiles_ksj_n03_hkd (行政区域 N03 2023)、pmtiles_jma_1saibun_hkd (気象庁の一次細分区域)、tokachi20260911-ortho | 台東区と 23 区には関係しない |
| FAO Hand-in-Hand | hih-* の 19 個 (コンゴ民主共和国、コートジボワールなどの適地スコア)、gaez-aez33、gaez-aez57 | 日本には関係しない。GAEZ は [fao-ferspas](../stac/fao-ferspas.md) にもある |
| そのほか | freetown-mapterhorn (フリータウンのドローン写真)、glup2030_zoning (ヴィエンチャンのゾーニング) | 日本には関係しない |

## bvmap

国土地理院の最適化ベクトルタイル (元は数値地図 (国土基本情報)) を配信しているもの。日本全国で、台東区と 23 区も入る。(2026-09-28 には「基盤地図情報」と書いていたが、2026-09-29 に国土地理院のリポジトリで確かめて直した)

- ズーム 4〜16、bounds は経度 122.0〜154.77、緯度 17.03〜46.0
- 縮尺ごとの 4 つの MBTiles (5000k、1000k、200k、25k) をまとめて配信している
- レイヤー 24: 建物 (BldA)、道路中心線 (RdCL)、道路縁 (RdEdg)、鉄道中心線 (RailCL)、送電線 (PwrTrnsmL)、等高線 (Cntr)、水涯線 (WL)、行政界 (AdmBdry)、注記 (Anno) など
- TileJSON の attribution は空。出典の表示の仕方は未確認 (国土地理院の条件に従う必要がある)
- スタイルは bvmap-dark、bvmap-starlight などがあり、元は <https://github.com/dwg7/bvmap>
- タイルそのものの出どころは、国土地理院の最適化ベクトルタイル (<https://github.com/gsi-cyberjapan/optimal_bvmap>) と考えられる (縮尺ごとの 4 つの MBTiles という構成が同じ)。国土地理院が PMTiles を Range で読める形で配っているので、分析にはそちらを使う。詳しくは [gsi-optimal-bvmap](../gsi-optimal-bvmap/README.md)

使い道の案: A (台東区) の結果を地図で目で確かめるときの下地。建物や道路を分析に使うなら、国土地理院の最適化ベクトルタイルの PMTiles を直接読む ([gsi-optimal-bvmap](../gsi-optimal-bvmap/README.md))。
