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
| [e-Stat](estat/README.md)  `catalog` | 日本の政府統計の窓口。統計 GIS の機械可読目録、統計データ API 3.0、統計 LOD の三経路 | 境界データ 54 件で全国およそ 10.8GiB。LOD は 20.9 億トリプル | Shapefile / KML / GML の zip、JSON API、SPARQL | e-Stat 利用規約 (政府標準利用規約2.0 準拠)。LOD だけは別扱い |
| [e-Stat 統計 LOD](estat/lod.md)  `catalog` | 政府統計を RDF Data Cube で。メッシュは GeoSPARQL のポリゴンつき | 2,086,445,173 トリプル / データセット 87 件。2010〜2019 年で止まっている | SPARQL (ダンプ無し) | CC BY 4.0 (VoID で機械可読に宣言) |
| [World Bank](worldbank/README.md)  `range` | 世界銀行の開発指標 (WDI ほか)。`z.yuiseki.net/static/worldbank/` の上流 | データベース 71、指標 29,544。WDI_CSV.zip 282,845,220 バイト | CSV の zip (Range 可、中身は非圧縮)、JSON API | CC BY 4.0 に紛争解決の追加条項。一部は ODbL や再配布不可 |
| [World Bank Data360](worldbank/data360.md)  `catalog` | 世界銀行が IMF、OECD、FAO、V-Dem などの指標をまとめて配信する基盤 | 指標 12,510 / データベース 170 | JSON API (SDMX に近い形)。一括配布は無い | データベースごとに違う。上位 30 で CC BY 13、外部指定 12 |

## 新しい出どころを足すとき

- 1 出どころ 1 ファイル。STAC なら `stac/`、それ以外は出どころの名前でディレクトリを作り、入口を `README.md` にする。中身が多ければその下を 1 ディレクトリ (またはリポジトリ) 1 ファイルに分ける。
- 数字は実際に読んで確かめた値を書き、確かめた日付を添える。
- 上の表に 1 行足す。

## 学習ステップとの対応

実際にどのステップでどのデータを使ったかは [../setup.md](../setup.md) の「使った出どころ」にある。各出どころのファイルの末尾にある「学習ステップとの対応 (案)」は、調べた時点の案。
