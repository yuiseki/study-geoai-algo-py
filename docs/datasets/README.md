# データセットの出どころ

学習に使うデータの候補。出どころ 1 つにつき 1 ファイル。

## 取り出し方の区分

各項目に「取り出し方」の節がある。必要な範囲だけを引けるかどうかで、次の 4 つに分ける。
`cng-data-antigravity` (`https://github.com/yuiseki/cng-data-antigravity`) が実装している
仕組みの分類に合わせてある。

| 区分 | 意味 | 確かめ方 |
|---|---|---|
| range | HTTP Range で必要なバイトだけ引ける。COG、PMTiles、FlatGeobuf、行グループを持つ Parquet | `curl -r 0-1023` が 206 を返し、索引がファイルの先頭付近にあること |
| catalog | STAC などの目録で必要な資産を選んでから引ける | 目録が bbox や日時で絞れること。認証が要るならそう書く |
| split | 地域や単位ごとに事前分割されていて、必要なファイルだけ引ける | 分割の単位と個数 |
| whole | 全部落とすしかない | 最小単位の大きさ |

1 つの出典が複数に当たることがある。Geofabrik は split で、その中の PBF は whole。
Wikidata はダンプが whole で、SPARQL エンドポイントは catalog に近い使い方ができる。
その場合は主な使い方を先に書き、併記する。

区分は実測に基づく。「COG だと書いてある」ではなく「Range を投げて 206 が返った」を根拠にする。
確かめていないものは 未確認 と書く。

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

## uedayou.net

<https://uedayou.net/> の 22 プロジェクト。日本の公的データを Linked Open Data にしたものが中心。
一覧と全体の注意は [uedayou-net/README.md](uedayou-net/README.md)、SPARQL を持つ 2 つはその下の各ファイル。

| データ | 中身 | 規模 | データの形 | ライセンス |
|---|---|---|---|---|
| [鉄道駅LOD](uedayou-net/jrslod.md) `catalog` | 日本の鉄道駅。Wikidata と owl:sameAs で結べる | 1,152,137 トリプル / 駅 10,145 | SPARQL、個別 IRI は内容交渉で Turtle | CC BY-SA 4.0 |
| [住所LOD](uedayou-net/loa.md) `catalog` | 日本の住所の階層。IMI コア語彙 | 39,458,434 トリプル / 住所型 147,407 | SPARQL、個別 IRI は内容交渉で Turtle | CC BY-SA 4.0 |

## その他

| 出どころ | 中身 | 規模 | データの形 | ライセンス |
|---|---|---|---|---|
| [Ookla Speedtest](ookla-speedtest/README.md)  `range` | 固定回線と携帯の速度・遅延を約 610m タイルで平均したもの (四半期ごと) | 2019 年第 1 四半期から 30 四半期 × 2 種別、Parquet 15.13GB | Parquet, Shapefile | CC BY-NC-SA 4.0 |
| [Mapterhorn](mapterhorn/README.md)  `range` | 全球の標高タイル。Copernicus GLO-30 を土台に各国の高精度 DEM 151 件で上書き。版 0.0.13 | planet.pmtiles (z0-12) 355.6GB と、z13 以上の地域別 458 個で合計約 9.58TB | PMTiles (Terrarium 符号化の 512px 可逆 WebP) | 元データごとに違う (約 30 種)。「© Mapterhorn」の表示が要る |
| [NASA SRTM](nasa-srtm/README.md)  `split` | 全球の標高 (北緯 60 度〜南緯 56 度)。SRTM v3 と、それを処理し直した NASADEM | 1 度四方のタイル。SRTMGL1 は 14,297 枚、1 枚 3,601 x 3,601 画素 (約 30m) で約 10MB | HGT。NASADEM は Planetary Computer に COG | CC0 (NASA の一般方針)。配布元により表記が違い、CGIAR 版は再配布不可 |
| [e-Stat 小地域境界](estat-boundary/README.md)  `split` | 国勢調査の町丁・字等別の境界と人口・世帯数。`yuiseki/estat-boundary-2020` の上流 | 47 都道府県で 322,733,398 バイト、全国 232,019 フィーチャ | Shapefile (zip、cp932、JGD2000) | 政府標準利用規約2.0。CC BY に従う利用も可 |
| [GeoNames](geonames/README.md)  `split` | 全世界の地名と別名。Wikidata の Q id と結べる | 13,465,076 件 / 252 国。allCountries.zip 422,001,054 バイト | タブ区切りテキスト (zip)、API。z.yuiseki.net に日付ごとのスナップショット (元の zip と GeoParquet) あり | CC BY 4.0。表示が要る。商用可、share-alike 無し |
| [OSM Wiki](osm-wiki/README.md)  `catalog` | OSM のタグの説明。`yuiseki/osm-wiki` の上流 | 記事 86,510、Key: 6,720、Tag: 8,538 | MediaWiki API、全履歴ダンプ 6.89GB | CC BY-SA 2.0。地図データのライセンスとは別 |
| [taginfo](taginfo/README.md)  `catalog` | OSM のタグの実使用回数。`yuiseki/osm-tag-corpus` の上流 | キー 115,209。DB の bz2 で 2.62GB | JSON API、SQLite ほか | ODbL。ただし wiki 由来の説明文の扱いは未確認 |
| [OurAirports](ourairports/README.md)  `whole` | 全世界の空港と滑走路。IATA/ICAO コードつき | 86,153 行、19 列。7 ファイルで 24.7MB | CSV。z.yuiseki.net に日付ごとのスナップショット (元の CSV と GeoParquet) あり | public domain と明記。ただし LICENSE は The Unlicense で software としか書かない |
| [Wikipedia](wikipedia/README.md)  `range` | 座標つき記事。`yuiseki/wikipedia-geotagged` の上流 | ja 1,520,723 記事 / en 7,245,970 記事 | XML ダンプ、SQL ダンプ、API | CC BY-SA 4.0。share-alike |
| [Wikivoyage](wikivoyage/README.md)  `range` | 旅行先の記事。`yuiseki/wikivoyage-geotagged` の上流 | en 34,710 記事 / ja 1,808 記事 | XML ダンプ、SQL ダンプ、API | CC BY-SA 4.0。share-alike |
| [国連文書 (ODS)](un-docs-source/README.md)  `split` | 総会と安保理の公式文書。`yuiseki/un-docs` の上流 | 未確認 (派生側で 39,363 件) | PDF (API 経由)、一部はスキャン | 許諾の文言が無い。1987 年の内部方針とサイト規約が矛盾する |
| [ESA WorldCover](esa-worldcover/README.md)  `range` | 全球 10m の土地被覆 11 区分。2020 年版と 2021 年版 | タイル 2,651 枚、Map だけで約 117GB | COG (EPSG:4326)。認証不要で Range が効く。格子は GeoJSON と FlatGeobuf | CC BY 4.0。表示文が指定されている |
| [GHSL](ghsl/README.md)  `split` | 全球の人口・建物・都市化度の格子。1975 年から 2030 年まで 5 年刻みで、2025 と 2030 は推計 | GHS-POP 1km で 1 エポック約 320MB、12 エポック | GeoTIFF (zip)、モルワイデ図法 | CC BY 4.0 (欧州委員会の法的通知による)。EU 所有でない部分は別 |
| [アドレス・ベース・レジストリ](abr/README.md)  `split` | 日本の住所の基本台帳。都道府県・市区町村・町字のマスターと代表点。`yuiseki/abr-src-2026-09` の上流 | 町字 727,429 行、座標 337,641 行 | CSV (zip)。直接配布と ArcGIS Hub の 2 経路 | PDL1.0。原文が CC BY に従う利用を許諾。出典と加工の明示が要る |
| [Wikidata](wikidata/README.md)  `catalog` | 全世界の構造化データ。座標を持つ項目が 1,243 万件。`yuiseki/wikidata-gazetteer` の上流 | 項目 1 億 2,351 万件。truthy ダンプで 43.5GB | JSON / TTL / NT のダンプ、SPARQL | 構造化データは CC0。main と property 以外の名前空間の文章は CC BY-SA |
| [Natural Earth](natural-earth/README.md)  `split` | 全世界の行政区域、地名、自然地物を 3 縮尺で。`yuiseki/ne-admin0-10m` の上流 | 実データ 215 レイヤー。10m の国 4.93MB、州 14.91MB | Shapefile (zip)、GitHub に版管理された本体 | public domain。帰属表示も不要と明記 |
| [geoBoundaries](geoboundaries/README.md)  `split` | 全世界の行政区域 ADM0〜ADM5。Natural Earth に無い ADM2 が 180 の国と地域にある | 715 件 / 232 の ISO コード。ADM2 だけで 49,363 単位 | GeoJSON, TopoJSON, Shapefile | 国ごと・階層ごとに違う (25 種類)。ADM2 の 135 件は share-alike でない |
| [Geofabrik](geofabrik/README.md)  `split` | OSM の地域抽出 (大陸、国、日本は 8 地方)。毎日更新 | 555 地域。日本全体の PBF が 2.54GB | .osm.pbf、地方は .shp.zip と .gpkg.zip も | ODbL 1.0 |
| [OpenStreetMap Japan PMTiles](openstreetmap-japan-pmtiles/README.md)  `range` | 全世界のベクトルタイル (データ基準日 2026-09-21) | 1 本 84.3GB、z0-14、16 レイヤー | PMTiles、MVT、OpenMapTiles 3.16.0 スキーマ | ODbL 1.0 と OpenMapTiles (CC-BY 4.0) |
| [東京 23 区のバスの GTFS](tokyo-gtfs/README.md)  `split` | 都営バス、荒川区、葛飾区、杉並区の時刻表。どれも block_id が空 | 都営バスは 150 路線、55,846 便 | GTFS-JP | CC BY 4.0 |
| [台東区めぐりん GTFS](odpt-taito-megurin/README.md)  `whole` | 台東区コミュニティバスの時刻表 (4 路線、128 停留所、290 便)。有効期間 2025-08-10〜2026-12-31 | zip 1 つ 78KB | GTFS-JP | CC BY 4.0 |
| [KartaView / GrabMaps 360 Imagery](kartaview-grabmaps-imagery/README.md)  `catalog` | 道路沿いの写真 (通常と 360 度)。GrabMaps 分は Yogyakarta、Langkawi、Krabi の 3 都市 | GrabMaps の公開分はサイト記載で 1,738,676 枚、30.79TiB。全体の規模は未確認 | JPEG と JSON API (位置、撮影日時、向き) | CC BY-SA 4.0 (KartaView の画像全体に一律) |
| [みちよみ](michiyomi/README.md)  `range` | 東京都の街路画像 (Mapillary) を VLM で構造化したもの。歩道、電柱、街灯、路面など | 1,914,451 シーン、一括版は Parquet 1.97GB | Parquet (Hugging Face) と API | CC BY-SA 4.0 (Mapillary のロゴ表示が要る) |
| [Google Open Buildings](google-open-buildings/README.md)  `split` | 衛星画像から推定した建物ポリゴン (v1〜v3) と、建物の有無・高さのラスタ (2.5D Temporal、2016〜2023 年)。アフリカ、南アジア、東南アジア、中南米で、日本は含まない | v3 ポリゴン約 18.5 億件、CSV.gz 333 本で 178.26GB | CSV.gz、GeoTIFF、ミラーに GeoParquet | CC BY 4.0 と ODbL 1.0 から選ぶ二重ライセンス |
| [PLATEAU](plateau/README.md)  `catalog` | 国土交通省の 3D 都市モデル。この学習では深追いしない (理由はリンク先) | 約 300 都市 (2025 年度末の予定) | CityGML ほか | データセットごとに確かめる (未確認) |
| [stars.optgeo.org](stars-optgeo/README.md)  `split` | Martin のタイルサーバー。空中写真、標高、Overture、OSM、国土地理院の最適化ベクトルタイル (bvmap) など 43 レイヤー | 表示用のタイル | MVT、PNG、JPEG、WebP | レイヤーごと (bvmap は国土地理院コンテンツ利用規約) |
| [国土地理院 最適化ベクトルタイル](gsi-optimal-bvmap/README.md)  `range` | 数値地図 (国土基本情報) の道路中心線、建物、等高線など 24 レイヤー。全国、2026-07-01 時点 | 地物 (MVT、タイル境界で切られる) | PMTiles 16.9GB (Range 可) | 国土地理院コンテンツ利用規約 (出典の明示) |
| [OpenCelliD](opencellid/README.md)  `未確認` | 携帯基地局の推定位置 (直近 18 か月に観測されたもの) | 未確認 (取得に API トークンが要る) | CSV | CC BY-SA 4.0 |
| [NYC TLC Trip Record Data](nyc-tlc/README.md)  `range` | ニューヨーク市のタクシーと配車の乗車記録 (乗降のゾーン ID と時刻、料金) と、263 のゾーン境界 | 2009 年から毎月。2026-07 は yellow 353 万行 61.7MB、fhvhv 2,092 万行 511MB | Parquet (CloudFront、Range 可)、境界は Shapefile の zip | 記載無し (NYC.gov の利用規約を指す)。再配布の許可は不明 |
| [Meta の移動データ (HDX)](hdx-meta-movement/README.md)  `whole` | Facebook の位置情報から出した行政区域ごとの 1 日の移動。Movement Range Maps (2020-03〜2022-05、終了) と Movement Distribution (家からの距離 4 区分、直近 90 日のみ) | Range Maps は 2021〜2022 年分で 695 万行、日本 679 区域。Distribution は 4 日分で 62 万行、日本 1,802 区域 | TSV の zip、CSV (署名付き S3、Range 可だが部分読みは不可)。z.yuiseki.net に元のファイルと Parquet のミラーあり (Commuting Zones、Business Activity Trends も) | CC BY |
| [全国の人流オープンデータ](mlit-1km-fromto/README.md)  `range` | 国土交通省の 1km メッシュ別と市区町村単位発地別の滞在人口 (平日/休日 × 昼/深夜/終日)。元は Agoop の GPS | 2019-01〜2021-12 の月別、47 都道府県で zip 191.7MB。東京都のメッシュ別は 49 万行 | 入れ子の zip の CSV (署名付き S3)。ページはログインを求めるが API からは不要。z.yuiseki.net に Parquet のミラーあり | 政府標準利用規約 2.0 準拠 (CC BY 4.0 互換) |
| [警察庁 交通事故統計オープンデータ](npa-traffic-accidents/README.md)  `split` | 人身事故 1 件 1 行の全国の記録。発生日時、緯度経度、道路と天候、当事者、死傷者数 | 2019〜2025 年、年に本票 29 万行前後。21 本で約 450MB | CSV (cp932)。緯度経度は度分秒の整数、都道府県コードは警察の単位 | PDL1.0 (CC BY 4.0 互換) |
| [食品営業許可・届出のオープンデータ](food-business-permits/README.md)  `split` | 食品の営業許可と届出 1 件 1 行。施設名、業種、所在地、緯度経度、許可日。厚生労働省 i2fas は電子申請で掲載に賛同した分だけ | i2fas は保健所設置主体ごとに 157 本、合計約 382MB。毎月 15 日に上書き | CSV (UTF-8 BOM)。Range は効かない | PDL1.0 だが同じ規約に営利目的の複製・頒布を禁じる一文がある (未確認)。自治体は個別 |
| [住居表示住所 (電子国土基本図の地名情報)](gsi-jukyo-jusho/README.md)  `split` | 住居表示地区の街区の区間ごとの点。住所と緯度経度 (JGD2024) | 市区町村ごとの ZIP 674 本、約 1.25GB。2026-03-26 更新 | CSV (見出しなし、UTF-8) と Shapefile | PDL1.0 (サイト規約)。座標ごとの再配布は測量法の複製承認が要るか未確認 |
| [歩行空間ネットワークデータ](mlit-walkspace-network/README.md)  `split` | 歩道のノードとリンク。ノードに緯度経度、住所は無い | hokoukukan 51 地区 約 335MB (2018 年仕様)、hokonavi 28 地区 約 79MB (2024 年仕様) | CSV、Shapefile、GML | hokonavi は PDL1.0。hokoukukan はファイルごとにばらばら (CC BY-SA を含む) |
| [国土調査 土地分類・水調査の GIS](mlit-land-classification/README.md)  `split` | 表層地質、土壌、地形分類、土地履歴、土地保全、利水現況図、地下水資料台帳 | ZIP 398 本、約 3.55GB | Shapefile。50 万分の 1 だけ日本測地系 | PDL1.0 だがダウンロードページに「そのまま複製して配布することは禁止」。背景図は測量法の承認対象 |
| [地球地図日本](gsi-global-map-japan/README.md)  `split` | 100 万分の 1 の行政界、交通、水系、人口集中地区、ラスタ。地名はローマ字 | 18 本、約 51MB。ベクタ第 2〜2.2 版、ラスタ第 1.0、1.1 版 | Shapefile、GeoTIFF | 国土地理院コンテンツ利用規約 (PDL1.0)。ZIP 内のメタデータに古い条件が残る |
| [全国警察施設名称位置等](npa-police-facilities/README.md)  `split` | 警察本部、警察署、交番・駐在所の名称と住所。緯度経度は無い | 3 本で約 2.0MB、13,041 件 (令和 8 年版) | CSV (cp932) と XLSX | PDL1.0 (警察庁サイト) |
| [東北地方太平洋沿岸地域 自然環境調査](env-tohoku-coastal-survey/README.md)  `split` | 震災後の植生図、藻場、海岸、重要湿地、生態系監視 (平成 24〜26 年度) | GIS 456 本 約 283MB、報告書 PDF 約 690MB | KMZ、Shapefile (JGD2000、cp932) | PDL1.0 (生物多様性センター)。個人名と「取扱い注意」のレイヤを含む |
| [環境省レッドリスト](env-redlist/README.md)  `split` | 初版から第 5 次までの種の一覧と、維管束植物の 2 次メッシュの分布情報 | CSV 130 本と zip 1 本、約 4.3MB | CSV (cp932 と UTF-8 が混在) | 第 5 次は CC BY 4.0。それより前は配布元に記載なし (未確認) |
| [気象庁 予報区等のコードと GIS](jma-forecast-area-codes/README.md)  `split` | 府県予報区、一次細分区域、市町村等、地震・津波の区域のコード表と区域の形 | コード表 1.7MB、GIS 19 本 約 2.8GB | xlsx、Shapefile (JGD2011) | PDL1.0 (気象庁サイト)。GIS に測量法の承認番号の注記。過去版は 3 年分だけ |
| [医療情報ネットのオープンデータ](mhlw-iryou-net/README.md)  `split` | 病院、診療所、歯科、助産所、薬局の施設票と診療科・診療時間票。住所と緯度経度 (0,0 の行あり) | 1 時点 ZIP 8 本 約 28MB、展開 376MB。2024-08 から 2026-06 の 5 時点 | CSV (UTF-8 BOM) | PDL1.0 (厚生労働省) |
| [法人番号公表サイトの法人情報](nta-houjin-bangou/README.md)  `split` | 法人の名称、所在地 (都道府県、市区町村、丁目番地、郵便番号)、法人番号。緯度経度は無い | 全国 CSV 約 256MB (UTF-8)、公表 572 万件。全件は月末に作り直し、差分は 40 日分 | CSV (見出しなし)、XML。POST でしか取れない | PDL1.0 (国税庁) |
| [金融庁 免許・許可・登録等を受けている業者一覧](fsa-licensed-firms/README.md)  `split` | 業態ごとの業者一覧。本店所在地、郵便番号、法人番号。個人の業者を含む | xlsx 76 本、約 8MB。上書き更新 | xlsx と PDF | PDL1.0 (金融庁) |
| [国際観光ホテル整備法の登録ホテル・旅館](mlit-registered-hotels/README.md)  `split` | 登録ホテル 926、旅館 1,359 の名称と住所。旧サイトの CSV (2018 年末) は緯度経度つき | PDF 約 1MB、CSV 4 本 約 0.8MB | PDF (観光庁)、CSV (hokoukukan、cp932) | PDL1.0 |
| [信書便事業者一覧](soumu-shinshobin/README.md)  `whole` | 特定信書便事業者 656 者の住所、役務、提供区域 | xlsx 1 本 約 140KB。年 3、4 回の更新で旧版は消える | xlsx と PDF | PDL1.0 (総務省) |
| [住民基本台帳人口移動報告](estat-jumin-idou/README.md)  `catalog` | 転入・転出・転入超過。都道府県間の移動元と移動先、市区町村間は 2012 年から参考表 (小さい流れは「その他」) | e-Stat の DB に 471 表、約 2.1 億件。1999〜2025 年 (ファイルの長期表は 1954 年から) | e-Stat API、Excel/CSV | e-Stat 利用規約 (政府標準利用規約 2.0、CC BY 4.0 互換) |
| [国勢調査の移動人口](estat-census-migration/README.md)  `catalog` | 5 年前の常住地別の人口。市区町村から市区町村への移動元と移動先 | 1990、2000、2010、2015、2020 年。表 ID で 529 表 | e-Stat API、Excel/CSV | e-Stat 利用規約 (CC BY 4.0 互換) |
| [国勢調査 人口等基本集計](estat-census-basic/README.md)  `catalog` | 男女・年齢・配偶関係、世帯、住宅、外国人。原数値と不詳補完値 | 2025 年は 444 表 (2026-09-29 公表)、全 1,072 表で約 9.5 億セル | e-Stat API、Excel/CSV | e-Stat 利用規約 (CC BY 4.0 互換) |
| [World Population Prospects](un-wpp/README.md)  `split` | 国別・年齢別の人口、出生、死亡、移動の推計と予測 | 555 地域、1950〜2101 年。現行 CSV 3.8GB、過去の版を含め 27GB | csv.gz、xlsx | CC BY 3.0 IGO |
| [ILOSTAT](ilostat/README.md)  `split` | 雇用、賃金、労働の指標 1,213 | 約 4 億行、csv.gz で約 3GB (推定) | csv.gz、parquet ほか、SDMX | CC BY 4.0 (2023-05-03 以降のデータセット) |
| [OECD Data Explorer](oecd/README.md)  `catalog` | 先進国の経済・社会、OECD 地域 (TL2/TL3) | データフロー 1,548、約 20 億観測 | SDMX API (1 時間 60 回) | OECD の利用条件 (CC BY ではない。出典表示を下流に引き継ぐ義務) |
| [Eurostat](eurostat/README.md)  `split` | 欧州の統計 7,600 表、NUTS 地域まで | 約 65 億値、gzip TSV で数〜15GB (推定) | TSV、SDMX、JSON-stat | 欧州委員会の再利用ポリシー。EU 外の国のデータは商用不可 |
| [UNHCR 難民統計](unhcr/README.md)  `catalog` | 難民、庇護申請、庇護の決定。出身国と庇護国の組み合わせ | 1951〜2025 年、約 50 万行、CSV 約 55MB | API、HDX の CSV | CC BY 4.0 (第三者の値とウェブサイト規約に注意) |
| [EDGAR](edgar/README.md)  `split` | 温室効果ガスと大気汚染物質の国別表と 0.1 度格子 | 国別 xlsx 約 29MB、格子は年別で約 83GiB | xlsx、NetCDF | CH4・N2O・F ガスは CC BY 4.0、化石 CO2 は CC BY-NC-ND 4.0 |
| [国土数値情報 鉄道 (N02)](ksj-n02-railway/README.md)  `split` | 全国の鉄道区間と駅 (線)。路線名、運営会社、事業者種別、駅名、駅コード | 2005〜2025 年度 (2009、2010 年度は無し)、全国 1 本の zip。2025 年度は区間 21,933、駅 10,234 | GML、GeoJSON、Shapefile (JGD2011。2014 年度以前は JGD2000) | 2020 年度以降オープンデータ (PDL1.0)、以前は商用可 (旧約款)。2005〜2014 年度は測量法の複製承認の下 |
| [国土数値情報 地価公示 (L01)](ksj-l01-land-price/README.md)  `split` | 標準地の公示価格と属性。2014 年版から 1983 年以来の価格の履歴を同じ行に | 1983〜2026 年 (44 年)、2026 年は 26,000 地点。全年で約 330MB (全ファイル 2,120 本で 659MB) | GML、Shapefile、GeoJSON (2018 年から) | 2019 年以降オープンデータ (PDL1.0)、以前は商用可 (旧約款)。測量法の注記なし。修正は同名で上書き |
| [不動産情報ライブラリ](mlit-reinfolib/README.md)  `split` | 不動産の取引価格 (アンケート) と成約価格 (レインズ)。所在地は町・大字まで | 取引約 592 万件 (2005 年第 3 四半期から)、成約約 67 万件 (2021 年第 1 四半期から) | CSV (画面から)、API (キーの申請が必要) | PDL1.0。レインズ側の著作権表示との関係は未確認 |
| [登記所備付地図データ](moj-chizu/README.md)  `split` | 法務省の地図 XML。筆ごとの地番と形状 (所有者・地目・地積は無し) | 2022〜2026 年の 5 年。1 年約 102GB (地図 XML の zip)、変換版 GeoJSON 約 110GB | 地図 XML (ログインと同意が必要)、変換版は公開 S3 | 法務省の独自規約。再配布・改変・商用は可、取消と用途制限 (個人の識別の禁止など) あり |
| [e-Stat](estat/README.md)  `catalog` | 日本の政府統計の窓口。統計 GIS の機械可読目録、統計データ API 3.0、統計 LOD の三経路 | 境界データ 54 件で全国およそ 10.8GiB。LOD は 20.9 億トリプル | Shapefile / KML / GML の zip、JSON API、SPARQL | e-Stat 利用規約 (政府標準利用規約2.0 準拠)。LOD だけは別扱い |
| [e-Stat 統計 LOD](estat/lod.md)  `catalog` | 政府統計を RDF Data Cube で。メッシュは GeoSPARQL のポリゴンつき | 2,086,445,173 トリプル / データセット 87 件。2010〜2019 年で止まっている | SPARQL (ダンプ無し) | CC BY 4.0 (VoID で機械可読に宣言) |
| [World Bank](worldbank/README.md)  `range` | 世界銀行の開発指標 (WDI ほか)。`z.yuiseki.net/static/worldbank/` の上流 | データベース 71、指標 29,544。WDI_CSV.zip 282,845,220 バイト | CSV の zip (Range 可、中身は非圧縮)、JSON API | CC BY 4.0 に紛争解決の追加条項。一部は ODbL や再配布不可 |
| [World Bank Data360](worldbank/data360.md)  `catalog` | 世界銀行が IMF、OECD、FAO、V-Dem などの指標をまとめて配信する基盤 | 指標 12,510 / データベース 170 | JSON API (SDMX に近い形)。一括配布は無い | データベースごとに違う。上位 30 で CC BY 13、外部指定 12 |
| [Kontur Population](kontur/README.md)  `whole` | 全世界の人口を H3 の六角形 (解像度 8、約 400m) で。2023-11-01 版 | 32,957,699 六角形、合計 8,031,924,024 人。gzip で 2,436,991,241 バイト | GeoPackage (gzip)、EPSG:3857。HDX に国別の版もある | CC BY (HDX の license_id。版番号の明記なし) |
| [UCDP GED](ucdp-ged/README.md)  `whole` | 組織的暴力の出来事 1 件 1 行。場所、日付、死者数。25.1 は 1989〜2024 年 | 25.1 は 385,918 件、26.1 は 417,968 件 (1989〜2025)。zip で 29,307,888 と 39,122,522 バイト | CSV (zip)。最新は 26.1 | CC BY 4.0 (ダウンロードのページ)。論文の引用が要る |
| [Geo-PKO](geo-pko/README.md)  `whole` | 国連 PKO の展開地点。2.3 版、1994〜2024 年 | 21,243 行、114 列。12,500,418 バイト | CSV | 明記なし。作成者は論文の引用を求める |
| [TeleGeography 海底ケーブル](telegeography-submarine-cables/README.md)  `whole` | 海底通信ケーブルの経路 | z の写しは 681 地物、2026-09-30 の現行版は 733 | GeoJSON (API) | 再配布を許す記述なし。元データは有料の購読者向け |
| [PB2002 プレート境界](pb2002-plates/README.md)  `whole` | Bird (2003) のプレート境界モデルを GeoJSON にしたもの | 241 地物、226,378 バイト | GeoJSON (GitHub) | 変換したものは ODC-By 1.0。元のモデルは明記なし |
| [USGS の地震](usgs-earthquakes/README.md)  `whole` `catalog` | 地震の位置、時刻、マグニチュード。リアルタイムのフィードと ComCat | z の写しは M4.5 以上の 1 か月 (2025-08-23〜09-22) で 601 件 | GeoJSON のフィード、ComCat の API | USGS が作ったものはパブリックドメイン。他の観測網の分は未確認 |
| [Nominatim の Wikipedia 重要度](nominatim-wikimedia-importance/README.md)  `whole` | Wikipedia の記事ごとの重要度 (リンクの数から)。Wikidata の ID つき | 17,846,821 行、39 言語。2024-08 版で 276,336,642 バイト | TSV (gzip) | データのライセンスは明記なし。入力は Wikipedia (CC BY-SA 4.0) と Wikidata (CC0) |

## 新しい出どころを足すとき

- 1 出どころ 1 ファイル。STAC なら `stac/`、それ以外は出どころの名前でディレクトリを作り、入口を `README.md` にする。中身が多ければその下を 1 ディレクトリ (またはリポジトリ) 1 ファイルに分ける。
- 数字は実際に読んで確かめた値を書き、確かめた日付を添える。
- 上の表に 1 行足す。

## 学習ステップとの対応

実際にどのステップでどのデータを使ったかは [../setup.md](../setup.md) の「使った出どころ」にある。各出どころのファイルの末尾にある「学習ステップとの対応 (案)」は、調べた時点の案。
