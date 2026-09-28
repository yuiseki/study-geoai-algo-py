# データセットの出どころ

学習に使うデータの候補。出どころ 1 つにつき 1 ファイル。

## STAC カタログ

| カタログ | 中身 | 規模 | データの形 | ライセンス |
|---|---|---|---|---|
| [fao-ferspas](stac/fao-ferspas.md) | FAO の農業・食料系ラスタ (干ばつ指数、作物、土壌、降水など) | 1,921 コレクション / 639,947 ファイル / 約 21TB | COG | コレクションごと |
| [mlit-nlftp](stac/mlit-nlftp.md) | 国土数値情報 (鉄道、バス停、浸水想定、将来推計人口メッシュなど) | 110 データセット / 21,603 ファイル / 228.2GB | zip (Shapefile / GeoJSON / GML) | 年ごとに違う |
| [tokyo-ckan](stac/tokyo-ckan.md) | 東京都オープンデータカタログ (施設一覧、統計表など) | 9,698 データセット / 83,821 ファイル | CSV, XLSX, PDF, GeoJSON など | ほぼ CC-BY-4.0 |
| [Overture Maps](stac/overture-maps.md) | 全世界の建物、道路、POI、行政区域、住所、土地被覆 | 建物だけで 25 億件 | GeoParquet | テーマごと |
| [WorldPop](stac/worldpop.md) | 全世界の人口グリッド (総人口、年齢性別、都市化度) | 248 か国 / 2015〜2030 年 | GeoTIFF (100m と 1km) | CC-BY-4.0 |
| [Sentinel-2 L2A (Planetary Computer)](stac/sentinel-2-l2a-planetary-computer.md) | 地表反射率。分光 12 バンド (10/20/60m) と SCL、visual。2015 年から更新中 | 東京の bbox で 1 か月 16 件、1 件は全アセットで約 2.05GB | STAC API + COG。SAS トークンの署名が必須 | Copernicus Sentinel data terms (本文は未確認) |

fao-ferspas、mlit-nlftp、tokyo-ckan は yuiseki が作った非公式ミラーで、持っているのはメタデータだけ。

## z.yuiseki.net/static

`https://z.yuiseki.net/static/` は nginx の自動一覧で公開しているファイル置き場。
全体の構成と共通の注意は [z-yuiseki-static/README.md](z-yuiseki-static/README.md)、ディレクトリごとの中身はその下の各ファイル。

## source.coop/smartmaps

<https://source.coop/smartmaps> の 18 リポジトリ。一覧は [source-coop-smartmaps/README.md](source-coop-smartmaps/README.md)、リポジトリごとの中身はその下の各ファイル。

## その他

| 出どころ | 中身 | 規模 | データの形 | ライセンス |
|---|---|---|---|---|
| [Ookla Speedtest](ookla-speedtest/README.md) | 固定回線と携帯の速度・遅延を約 610m タイルで平均したもの (四半期ごと) | 2019 年第 1 四半期から 30 四半期 × 2 種別、Parquet 15.13GB | Parquet, Shapefile | CC BY-NC-SA 4.0 |
| [Mapterhorn](mapterhorn/README.md) | 全球の標高タイル。Copernicus GLO-30 を土台に各国の高精度 DEM 151 件で上書き。版 0.0.13 | planet.pmtiles (z0-12) 355.6GB と、z13 以上の地域別 458 個で合計約 9.58TB | PMTiles (Terrarium 符号化の 512px 可逆 WebP) | 元データごとに違う (約 30 種)。「© Mapterhorn」の表示が要る |
| [Geofabrik](geofabrik/README.md) | OSM の地域抽出 (大陸、国、日本は 8 地方)。毎日更新 | 555 地域。日本全体の PBF が 2.54GB | .osm.pbf、地方は .shp.zip と .gpkg.zip も | ODbL 1.0 |
| [OpenStreetMap Japan PMTiles](openstreetmap-japan-pmtiles/README.md) | 全世界のベクトルタイル (データ基準日 2026-09-21) | 1 本 84.3GB、z0-14、16 レイヤー | PMTiles、MVT、OpenMapTiles 3.16.0 スキーマ | ODbL 1.0 と OpenMapTiles (CC-BY 4.0) |
| [OpenCelliD](opencellid/README.md) | 携帯基地局の推定位置 (直近 18 か月に観測されたもの) | 未確認 (取得に API トークンが要る) | CSV | CC BY-SA 4.0 |

## 新しい出どころを足すとき

- 1 出どころ 1 ファイル。STAC なら `stac/`、それ以外は出どころの名前でディレクトリを作り、入口を `README.md` にする。中身が多ければその下を 1 ディレクトリ (またはリポジトリ) 1 ファイルに分ける。
- 数字は実際に読んで確かめた値を書き、確かめた日付を添える。
- 上の表に 1 行足す。

## 学習ステップとの対応 (案)

| ステップ | 使えそうなデータ |
|---|---|
| 1〜3 回帰・分類、木、Boosting | WorldPop の人口と Overture の建物・POI をメッシュで集計して、人口を予測する |
| 4 Cross Validation とデータリーク | 同じメッシュ表を、ランダム分割と空間ブロック分割 (GroupKFold / verde) で比べる |
| 5 k-means / DBSCAN | Overture の places や tokyo-ckan の施設一覧の点をクラスタリングする |
| 6 PCA | FAO の多数のラスタを同じ格子で読んで、次元を圧縮する |
| 7 Dijkstra / A* | Overture の transportation (segment と connector) で道路グラフを作る |
| 8〜9 LP / MILP、assignment / facility location | mlit-nlftp の将来推計人口メッシュと施設 (医療機関、学校、避難施設) で配置と割当を解く |
| 10 CP-SAT / scheduling | 未定 |
| 11 SHAP / calibration | 1〜3 で作ったモデルを説明・較正する |
| 12 多目的最適化 | 8〜9 の配置問題に、距離とコストなど複数の目的を与える |
