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
| [HOTOSM OpenAerialMap](stac/hotosm-openaerialmap.md) | 航空写真、ドローン、衛星の災害画像と Copernicus DEM (5 コレクション) | OAM 21,810 件、Maxar 35,966 件など。日本は OAM 804 件、Maxar 242 件 | STAC API + COG | コレクションごと (CC-BY-4.0、CC-BY-NC-4.0、public-domain など) |
| [Maxar Open Data](stac/maxar-opendata.md) | 災害イベントごとの衛星画像 (ARD)。災害前の撮影も含む | 55 イベント、1,109 acquisition。日本は能登半島地震の 1 イベント | 静的 STAC (検索 API 無し) + COG (0.305m) | CC-BY-NC-4.0 |

fao-ferspas、mlit-nlftp、tokyo-ckan は yuiseki が作った非公式ミラーで、持っているのはメタデータだけ。

## z.yuiseki.net/static

`https://z.yuiseki.net/static/` は nginx の自動一覧で公開しているファイル置き場。
全体の構成と共通の注意は [z-yuiseki-static/README.md](z-yuiseki-static/README.md)、ディレクトリごとの中身はその下の各ファイル。

## source.coop/smartmaps

<https://source.coop/smartmaps> の 18 リポジトリ。一覧は [source-coop-smartmaps/README.md](source-coop-smartmaps/README.md)、リポジトリごとの中身はその下の各ファイル。

## Hugging Face の yuiseki のデータセット

<https://huggingface.co/yuiseki/datasets> の地理に関わる 20 個。一覧は [huggingface-yuiseki/README.md](huggingface-yuiseki/README.md)、データセットごとの中身はその下の各ファイル。
12 ステップに直接使えるのは、凍結した OSM (osm-tokyo23-src-2026-08、osm-japan-src-2026-08) と、国勢調査の小地域境界 (estat-boundary-2020)、市区町村 (jp-admin-2026-09)。

## その他

| 出どころ | 中身 | 規模 | データの形 | ライセンス |
|---|---|---|---|---|
| [Ookla Speedtest](ookla-speedtest/README.md) | 固定回線と携帯の速度・遅延を約 610m タイルで平均したもの (四半期ごと) | 2019 年第 1 四半期から 30 四半期 × 2 種別、Parquet 15.13GB | Parquet, Shapefile | CC BY-NC-SA 4.0 |
| [Mapterhorn](mapterhorn/README.md) | 全球の標高タイル。Copernicus GLO-30 を土台に各国の高精度 DEM 151 件で上書き。版 0.0.13 | planet.pmtiles (z0-12) 355.6GB と、z13 以上の地域別 458 個で合計約 9.58TB | PMTiles (Terrarium 符号化の 512px 可逆 WebP) | 元データごとに違う (約 30 種)。「© Mapterhorn」の表示が要る |
| [NASA SRTM](nasa-srtm/README.md) | 全球の標高 (北緯 60 度〜南緯 56 度)。SRTM v3 と、それを処理し直した NASADEM | 1 度四方のタイル。SRTMGL1 は 14,297 枚、1 枚 3,601 x 3,601 画素 (約 30m) で約 10MB | HGT。NASADEM は Planetary Computer に COG | CC0 (NASA の一般方針)。配布元により表記が違い、CGIAR 版は再配布不可 |
| [Geofabrik](geofabrik/README.md) | OSM の地域抽出 (大陸、国、日本は 8 地方)。毎日更新 | 555 地域。日本全体の PBF が 2.54GB | .osm.pbf、地方は .shp.zip と .gpkg.zip も | ODbL 1.0 |
| [OpenStreetMap Japan PMTiles](openstreetmap-japan-pmtiles/README.md) | 全世界のベクトルタイル (データ基準日 2026-09-21) | 1 本 84.3GB、z0-14、16 レイヤー | PMTiles、MVT、OpenMapTiles 3.16.0 スキーマ | ODbL 1.0 と OpenMapTiles (CC-BY 4.0) |
| [東京 23 区のバスの GTFS](tokyo-gtfs/README.md) | 都営バス、荒川区、葛飾区、杉並区の時刻表。どれも block_id が空 | 都営バスは 150 路線、55,846 便 | GTFS-JP | CC BY 4.0 |
| [台東区めぐりん GTFS](odpt-taito-megurin/README.md) | 台東区コミュニティバスの時刻表 (4 路線、128 停留所、290 便)。有効期間 2025-08-10〜2026-12-31 | zip 1 つ 78KB | GTFS-JP | CC BY 4.0 |
| [KartaView / GrabMaps 360 Imagery](kartaview-grabmaps-imagery/README.md) | 道路沿いの写真 (通常と 360 度)。GrabMaps 分は Yogyakarta、Langkawi、Krabi の 3 都市 | GrabMaps の公開分はサイト記載で 1,738,676 枚、30.79TiB。全体の規模は未確認 | JPEG と JSON API (位置、撮影日時、向き) | CC BY-SA 4.0 (KartaView の画像全体に一律) |
| [みちよみ](michiyomi/README.md) | 東京都の街路画像 (Mapillary) を VLM で構造化したもの。歩道、電柱、街灯、路面など | 1,914,451 シーン、一括版は Parquet 1.97GB | Parquet (Hugging Face) と API | CC BY-SA 4.0 (Mapillary のロゴ表示が要る) |
| [Google Open Buildings](google-open-buildings/README.md) | 衛星画像から推定した建物ポリゴン (v1〜v3) と、建物の有無・高さのラスタ (2.5D Temporal、2016〜2023 年)。アフリカ、南アジア、東南アジア、中南米で、日本は含まない | v3 ポリゴン約 18.5 億件、CSV.gz 333 本で 178.26GB | CSV.gz、GeoTIFF、ミラーに GeoParquet | CC BY 4.0 と ODbL 1.0 から選ぶ二重ライセンス |
| [PLATEAU](plateau/README.md) | 国土交通省の 3D 都市モデル。この学習では深追いしない (理由はリンク先) | 約 300 都市 (2025 年度末の予定) | CityGML ほか | データセットごとに確かめる (未確認) |
| [stars.optgeo.org](stars-optgeo/README.md) | Martin のタイルサーバー。空中写真、標高、Overture、OSM、国土地理院の基盤地図情報ベクトルタイル (bvmap) など 43 レイヤー | 表示用のタイル | MVT、PNG、JPEG、WebP | レイヤーごと (bvmap は未確認) |
| [OpenCelliD](opencellid/README.md) | 携帯基地局の推定位置 (直近 18 か月に観測されたもの) | 未確認 (取得に API トークンが要る) | CSV | CC BY-SA 4.0 |

## ハッカソン向けの候補

いただいた表に、調べた結果の「日本での代替」の列を足したもの。左の 5 列は元の表のまま。

| データセット | 種類 | 主な内容 | ハッカソンでの用途 | ライセンス等 | 日本での代替 |
|---|---|---|---|---|---|
| [WorldPop](stac/worldpop.md) | 人口ラスター | グリッド人口推計 | 需要・人口密度、基地局候補地の評価 | CC BY 4.0 が基本 | そのまま使える (日本も収録)。町丁目単位なら [estat-boundary-2020](huggingface-yuiseki/estat-boundary-2020.md) の人口も |
| [NASA SRTM](nasa-srtm/README.md) | DEM | 標高・地形 | 電波伝搬、見通し、3D地形 | NASA open data / 原則CC0 | [Mapterhorn](mapterhorn/README.md)。日本は国土地理院の 1m〜10m DEM で上書きされている |
| OpenStreetMap ([Geofabrik](geofabrik/README.md) ほか) | ベクタ | 道路、建物、POI、インフラ等 | 道路網、地物、候補地点 | ODbL | そのまま使える。凍結版は [osm-tokyo23-src-2026-08](huggingface-yuiseki/osm-tokyo23-src-2026-08.md)、タイルは [OpenStreetMap Japan PMTiles](openstreetmap-japan-pmtiles/README.md) |
| [Google Open Buildings](google-open-buildings/README.md) | 建物 | 建物フットプリント、派生版では高さ | 3D環境、遮蔽物、建物密度 | CC BY 4.0 または ODbL | 日本を含まないので [Overture Maps](stac/overture-maps.md) の buildings。3D なら source.coop の [smartmaps/xing](source-coop-smartmaps/xing.md) (PLATEAU の 3D Tiles) |
| [OpenCelliD](opencellid/README.md) | 通信インフラ | 基地局・セル位置 | serving cell、既存基地局配置 | CC BY-SA 4.0 | そのまま使える (取得に API トークンが要る)。source.coop の [smartmaps/opencellid](source-coop-smartmaps/opencellid.md) に 2024-06-14 時点の PMTiles もある |
| [KartaView / GrabMaps 360 Imagery](kartaview-grabmaps-imagery/README.md) | street-level imagery | 道路沿い画像、360°画像 | 電柱・街灯の物体検出 | CC BY-SA 4.0 の公開画像あり | 東京なら [みちよみ](michiyomi/README.md)。Mapillary の画像から電柱の数と道路照明の数を VLM で読み取り済み |

元の表の記載を調べて分かったこと:

- NASA SRTM の「原則CC0」は NASA 自身の一般方針の書き方と合っている。ただし配布元によって表記が違い、CGIAR の SRTM 90m 版は商用利用と再配布が禁止されている。
- Google Open Buildings の「派生版では高さ」は、Google 自身の 2.5D 版 (高さのラスタ、2016〜2023 年) のこと。実効の解像度は約 4m で、100m で頭打ちになる。「CC BY 4.0 または ODbL」は本家が 2 つから選べる二重ライセンス。
- KartaView の「CC BY-SA 4.0 の公開画像あり」は、KartaView の画像全体に一律にかかる条件。GrabMaps の画像も KartaView の中の 1 ユーザーの投稿として公開されている。公開されているのは Yogyakarta、Langkawi、Krabi の 3 都市。
- 日本で見通しを計算するなら、Mapterhorn の土台 (Copernicus GLO-30) は建物や樹木の上を測った表面 (DSM)、国土地理院の DEM は地面 (DTM) なので、場所によって遮蔽物が入っていたりいなかったりする。

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
