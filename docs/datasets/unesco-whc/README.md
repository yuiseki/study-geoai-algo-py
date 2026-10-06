# UNESCO 世界遺産センター (World Heritage List と UNESCO Sites Navigator)

2026-10-06 に読んで確かめた内容。whc.unesco.org のページは curl で直接読めた (HTTP 200、`server: cloudflare`、`cf-mitigated` は付いていなかった)。ArcGIS の情報は、ArcGIS Online の公開の REST (`www.arcgis.com/sharing/rest/` の item と search) と、公開されている FeatureServer への問い合わせで読んだ。件数は FeatureServer の `returnCountOnly=true` と、`groupByFieldsForStatistics` による集計 (属性の値ごとの件数だけを返す)。大きさは `curl -r 0-1023` の `Content-Range`。ポリゴンの中身として見たのは 1 件 (id 1430、Namib Sand Sea) だけ。一覧の XML (2,496,431 バイト) と XLSX (2,943,940 バイト) は、列と件数を数えるためにパイプで 1 回ずつ読み、保存していない。

- 入口 (GIS): <https://whc.unesco.org/en/wh-gis/> (ページ名「UNESCO Sites Navigator」)。地図ビューアは ArcGIS Experience Builder のアプリ <https://experience.arcgis.com/experience/4f1652275d1f4656964b64a20a7346d3> (item の題名「UNESCO Sites Navigator - World Heritage」)。
- 入口 (一覧): <https://whc.unesco.org/en/list/>。書き出しは <https://whc.unesco.org/en/syndication/> に並ぶ XML、RSS、GeoRSS、XLS/XLSX、KML。
- 作成: ユネスコ世界遺産センター (UNESCO World Heritage Centre)。範囲と緩衝地帯の線は締約国 (States Parties) が提出し、世界遺産センターが委員会の採択した地図と照合する。ArcGIS の item の所有者は `f_avakian` (GIS のページの連絡先 Fernando Avakian)。
- 中身: 一覧は 1,273 件 (文化 991、自然 240、複合 42、2026-10-06)。GIS は代表点が 1,271 件の遺産、資産の範囲のポリゴンが 515 件、緩衝地帯のポリゴンが 346 件。
- ライセンス: データを開いて再配布できる条件にはなっていない。ArcGIS の item に「Redistribution, bulk harvesting or commercial use is prohibited without prior written permission from UNESCO.」、syndication のページに「Any republication, online or in any other form, of any UNESCO/WHC data requires prior written authorization.」とある。CC BY-SA 3.0 IGO が付いているのは、遺産のページの説明文 (Description) と「© UNESCO」の要素で、一覧の書き出しや GIS の層には付いていない。
- 結論: 書面の許可なしに Hugging Face へ置くことはできない。

## GIS のページが提供しているもの

<https://whc.unesco.org/en/wh-gis/> の本文 (2026-10-06 に読んだ) から。

> the UNESCO Sites Navigator is the dedicated Geographic Information System (GIS) for UNESCO's key designated sites around the world. The UNESCO Sites Navigator offers a comprehensive monitoring tool that visualises verified, georeferenced boundaries of World Heritage properties, Biosphere Reserves, and UNESCO Global Geoparks, as well as properties protected under the 1954 Hague Convention and its Two Protocols. It brings together nearly 50 relevant datasets, supporting enhanced monitoring through remote sensing and providing deeper insights into the sites.

> World Heritage polygons not yet featured either await submission by the relevant State Party/Parties or remain under review by UNESCO.

- 2023 年に始まった World Heritage Online Map Platform を引き継いだもの (「Building on the World Heritage Online Map Platform (operational since 2023)」)。2025-07-29 のニュースで Sites Navigator として公開された。
- 提供の形は地図ビューアだけ。ページにダウンロードの案内、WMS/WFS、ファイルの配布は無い。ページから張られているのは Experience Builder のアプリ (PC 版、携帯版の英語・フランス語・スペイン語・ポルトガル語、1954 年ハーグ条約の表示) と、締約国向けの技術資料 (下の「締約国の提出」)。
- ビューアの裏の地物は ArcGIS Online の公開の FeatureServer にある。アプリの設定 (`items/4f1652275d1f4656964b64a20a7346d3/data`) から辿れる。
- 自然災害の警報 (地震、火災、津波、白化、植生の撹乱) を日次と週次で遺産に付ける機能がある。警報の値は下の属性の `daily_*_alert` などに入る。

### ArcGIS のサービス

`https://services6.arcgis.com/eMd5K6XXEvJETxfQ/arcgis/rest/services/prd_whc_sites_dossiers_elements_v2_view/FeatureServer`

- item `0eb76eed88bf40a3bb76018fbd5f1fce`、題名「prd_dossiers_elements_v2 view」、種類は Feature Service の View (`View Service`)。説明は「View of production service_v2」。`access` は `public`。
- 作成 2025-01-30、item の更新 2026-09-23。
- `capabilities` は `Query,Extract`、`maxRecordCount` はサービスが 1000、各層が 2000。`supportedQueryFormats` は `JSON` と書かれているが、`f=geojson` も返った。
- 空間参照は Web メルカトル (`wkid` 102100、`latestWkid` 3857)。`outSR=4326` を付ければ経緯度で返る。
- 応答ヘッダに `x-esri-org-request-units-per-min: usage=303;max=6000` が付く。組織全体で 1 分あたりの要求量に上限がある。

| 層 | 名前 | 形 | 地物の数 | 遺産の数 (`property_id` の種類) | データの最終更新 (`dataLastEditDate`) |
|---|---|---|---:|---:|---|
| 0 | `whc_sites_dossiers_elements_core_points` | 点 | 6,311 | 1,271 | 2026-10-06 00:05 UTC |
| 1 | `whc_sites_dossiers_elements_core_poly` | ポリゴン | 2,184 | 515 | 2026-10-06 00:05 UTC |
| 2 | `whc_sites_dossiers_elements_core_buffer_poly` | ポリゴン | 1,117 | 346 | 2026-10-06 00:05 UTC |

- 1 地物は遺産の構成資産 (component part、`element_*`) 1 つ。連続する遺産 (serial) は構成資産の数だけ地物を持つ。例: 1133quinquies (Ancient and Primeval Beech Forests of the Carpathians and Other Regions of Europe) は範囲 93、緩衝地帯 72。
- `table_source` は `elements` と `nominations` の 2 値。点で elements 485 件、nominations 786 件の遺産。構成資産の表を持つ遺産と、推薦書の単位で 1 つにまとめた遺産の違いに見えるが、定義は書かれていない (未確認)。
- 点の 1,271 件と一覧の 1,273 件の差は 2 件。点が無いのは 868 (Routes of Santiago de Compostela in France) と 1567 (Funerary and memory sites of the First World War (Western Front))。ポリゴンと緩衝地帯の層に、一覧に無い `property_id` は無かった。
- 範囲のポリゴンがある遺産は一覧の 40.5% (515 / 1,273)。種類別では文化 379、自然 112、複合 24。登録年では 2026 年登録 25 件のうち 9 件、2025 年 26 件のうち 18 件。
- 緩衝地帯のポリゴンがある遺産は 346 件 (文化 288、自然 47、複合 11)。緩衝地帯は範囲の部分を抜いた穴あきの形で作る、と技術資料にある。
- 危機遺産 (`property_danger` = 1) は点で 58 件。一覧の「58 In Danger」と合う。

同じ所有者の公開の item には、ほかに `harmonized_sites_v2` (`https://services6.arcgis.com/eMd5K6XXEvJETxfQ/arcgis/rest/services/harmonized_sites_v2/FeatureServer/1`) がある。6,216 地物のポリゴンで、`geometry_source` が `polygon` 1,660、`polygon_hidden` 386、`point` 4,170。点しか無い構成資産を面にしたもので、警報の計算に使う層に見える (未確認)。同じ名前の Service Definition (`e71b6f800a7a41ad92fdd12acf81039a`、5,856,198 バイト) も公開になっている。どちらも `accessInformation` と `licenseInfo` は空。

### 属性

3 つの層でほぼ同じ列を持つ。主なもの:

| 列 | 意味 |
|---|---|
| `property_id` | 一覧の id_no (例: 1430) |
| `dossier` | 推薦書の番号。改訂の接尾辞が付く (`1133quinquies`、`1018rev`、`100bis`) |
| `property_rev_bis` | 改訂の区分 |
| `property_name_en`、`property_name_fr` | 遺産の名前 (英、仏) |
| `property_short_description_en`、`_fr` | 短い説明 |
| `element_id`、`element_serial_number`、`element_name_en`、`_fr` | 構成資産の番号と名前 |
| `element_iso2`、`element_state_name_en` | 構成資産のある国 |
| `element_longitude`、`element_latitude` | 構成資産の代表点 |
| `element_CoreArea`、`element_BufferArea` | 構成資産の範囲と緩衝地帯の面積 |
| `property_core_area`、`property_buffer_area` | 遺産全体の面積 |
| `element_precision_publish` | 位置の精度の区分 (値の意味は書かれていない) |
| `property_inscribed`、`property_inscribed_sec_dates` | 登録年、拡張などの年 |
| `property_criteria_txt`、`C1`〜`C6`、`N7`〜`N10` | 登録基準 (文字列と 0/1 の列) |
| `property_category` | Cultural / Natural / Mixed |
| `property_danger` | 危機遺産なら 1 |
| `property_serial`、`property_transboundary` | 連続資産、国境をまたぐ資産 |
| `property_states_name_en`、`property_iso2`、`property_iso3` | 締約国 |
| `region_en`、`whc_region`、`date_adhesion`、`ratification` | 地域、条約の締結 |
| `daily_quake_alert`、`daily_fire_alert`、`daily_tsunami_alert`、`daily_bleaching_alert`、`weekly_vegetation_disturbance_alert` | 警報 |
| `land_cover`、`cover_loss_tree`、`ghg_flux`、`desig`、`sids` | 付加の指標 |
| `Shape__Area`、`Shape__Length` | 図形の面積と周長 (Web メルカトルの値。ポリゴンの層だけ) |

- 面積の単位は書かれていない。id 1430 で `element_CoreArea` = 3,077,700、`element_BufferArea` = 899,500。遺産のページ (<https://whc.unesco.org/en/list/1430/maps/>) の表は 3,077,700 ha と 899,500 ha なので、ヘクタールと読める。
- id 1430 の範囲のポリゴンは単一の Polygon、1,031 頂点、GeoJSON で 38,506 バイト。応答ヘッダに `x-esri-query-max-vertex-count: 1031` が付いた。

## 一覧 (World Heritage List) の書き出し

<https://whc.unesco.org/en/list/> の冒頭 (2026-10-06):

> The World Heritage List includes 1273 properties forming part of the cultural and natural heritage which the World Heritage Committee considers as having outstanding universal value. These include 991 cultural, 240 natural and 42 mixed properties in 173 States Parties.

同じページの数え: 51 Transboundary / Transnational、3 Delisted、58 In Danger。抹消された 3 件 (654 Arabian Oryx Sanctuary、1150 Liverpool、1156 Dresden Elbe Valley) はページには載るが、XLSX の 1,273 行と GIS の層には入っていない。

| 書き出し | URL | 形 | 大きさ (バイト) | Range |
|---|---|---|---:|---|
| XML | <https://whc.unesco.org/en/list/xml/> (ar、fr、es、ru、zh もある) | `whc-en.xml` | 2,496,431 | 効かない (200 で全体) |
| XLSX | <https://whc.unesco.org/en/list/xlsx/?2026> (`/en/list/xls/?2026` も同じ xlsx を返す) | `whc-sites.xlsx` | 2,943,940 | 206 |
| KML | <https://whc.unesco.org/en/list/kml/> | 386 バイトの NetworkLink。実体は `/en/list/kmz` | 874,537 (kmz) | 206 (kmz) |
| GeoRSS | <https://whc.unesco.org/en/list/georss/> | `whcgeorss-en.xml` | 未確認 | 効かない |
| RSS | <https://whc.unesco.org/en/list/rss/> | `whcrss-en.xml` | 未確認 | 効かない |

- XML は `<query columns="216" rows="1273">` の下に `<row>` が 1,273 個。要素は `http_url`、`dossier`、`id_number`、`unique_number`、`image_url`、`iso_code`、`justification`、`geolocations` (構成資産ごとの `<poi>` に `latitude`、`longitude`、`iso2`)、`site`、`short_description`、`date_inscribed`、`secondary_dates`、`danger`、`extension`、`criteria_txt`、`category`、`states`、`regions`、`location`、`transnational`。面積は無い。`<poi>` の無い行が 3 つある。
- XLSX は 1 シート、見出し 1 行と 1,273 行。列は `unique_number`、`id_no`、`rev_bis`、`name_en`/`fr`/`es`/`ru`/`ar`/`zh`、`short_description_*` (6 言語、HTML の断片)、`justification_en`/`fr`、`date_inscribed`、`secondary_dates`、`danger`、`date_end`、`danger_list`、`longitude`、`latitude`、`area_hectares`、`C1`〜`C6`、`N7`〜`N10`、`criteria_txt`、`category`、`category_short`、`states_name_*` (6 言語)、`region_en`/`fr`、`iso_code`、`udnp_code`、`transboundary`。`date_end` は危機遺産一覧から外れた年 (例: Angkor 2004)。`area_hectares` の空は 18 行。点は遺産ごとに 1 つ。
- RSS の `<copyright>` は「Copyright 2026 UNESCO World Heritage Centre」、`<lastBuildDate>` は Mon, 05 Oct 2026。
- KMZ の中身は開いていない。点だけか範囲を含むかは未確認。
- syndication のページには、UNEP-WCMC の「Natural and mixed World Heritage sites」の KML (2017 年 8 月時点) へのリンクもある。自然遺産と複合遺産の範囲は WDPA にも世界遺産の指定として入っている (`../protected-planet/README.md`、`DESIG_TYPE` が `Not Applicable`)。WDPA の条件は同じ README にある。

## 締約国の提出

GIS のページの「Guidelines on the provision of geospatial World Heritage data」(<https://whc.unesco.org/document/208934>、`activity-1142-33.pdf`、9,536,588 バイト、題名「UNESCO SITES NAVIGATOR Technical note on the provision of geospatial data」) の「Guiding principles」から:

> When submitting data of the World Heritage sites, your State Party is consenting to their display on the UNESCO Sites Navigator, hosted on the website of UNESCO and the World Heritage Convention.

> The layers must be developed in collaboration with and in full agreement with all relevant rightsholders of the property.

> The publication of the World Heritage boundaries and buffer zones does not imply the expression of any opinion whatsoever of the World Heritage Committee or UNESCO concerning the legal status of any country, territory, city or area or of its boundaries.

- 締約国が UNESCO に与えるのは、Sites Navigator での表示への同意として書かれている。第三者への再配布の許諾には触れていない。
- 形式は Shapefile (zip) が望ましく、GML や GeoJSON も受ける。1 遺産 1 層、名前は `Property_<ISO2>_<id>.zip` と `Buffer_Zone_<ISO2>_<id>.zip`。座標系は属性でなくメタデータに書く (例として WGS 84、EPSG:4326)。
- 境界の変更が委員会で承認されると、世界遺産センターが締約国に連絡して層を更新する。

## 取り出し方

区分は catalog。主な使い方は ArcGIS の FeatureServer への問い合わせで、`where` (id、国、登録年など) と空間の条件で必要な地物だけを引ける。一覧の XLSX は whole (2,943,940 バイトの 1 本)。2026-10-06 に実測した。

| 要求 | 応答 |
|---|---|
| FeatureServer `.../1/query?where=1=1&returnCountOnly=true` | `{"count":2184}` |
| FeatureServer `.../1/query?where=property_id=1430&outSR=4326&f=geojson` | 200、38,506 バイト、`accept-ranges: bytes`、`cache-control: public, max-age=3600` |
| XLSX `-r 0-1023` | 206、`content-range: bytes 0-1023/2943940` |
| XML `-r 0-1023` | 200 (Range を無視して全体) |

- FeatureServer は 1 回に最大 2,000 地物。全件を引くには `resultOffset` で送る必要がある。
- `supportedExportFormats` に csv、shapefile、geoPackage、filegdb、geojson、kml などが並ぶが、書き出し (Extract) を匿名で使えるかは試していない (未確認)。
- 範囲と緩衝地帯の全体の大きさは測っていない (未確認)。全件を引かないと分からない。
- 下のライセンスの節のとおり、FeatureServer からの一括取得 (bulk harvesting) は item の条件で禁じられている。区分は技術的にできることを書いたもの。

## ライセンス

### ArcGIS の item

item `0eb76eed88bf40a3bb76018fbd5f1fce` の `accessInformation` (<https://www.arcgis.com/sharing/rest/content/items/0eb76eed88bf40a3bb76018fbd5f1fce?f=json>、2026-10-06 に読んだ) の全文:

> UNESCO dataset for public consultation and map display on its Sites Navigator. Redistribution, bulk harvesting or commercial use is prohibited without prior written permission from UNESCO.

- `licenseInfo` は空 (null)。サービスの `copyrightText` も空。
- Experience Builder のアプリの item (`4f1652275d1f4656964b64a20a7346d3`) は `accessInformation` も `licenseInfo` も空。

### syndication のページ

<https://whc.unesco.org/en/syndication/> の「Terms and Conditions of Use」(2026-10-06 に読んだ) から:

> UNESCO/WHC makes some of its web content available via syndication (XML/RSS/KML/XLS/GEORSS). An RSS icon appears on the syndication page, indicating those sections available for syndication. Whether you register as a subscriber or not, you must observe the following rules
> This website and its content is protected by international law. Any republication, online or in any other form, of any UNESCO/WHC data requires prior written authorization.
> Individuals or organizations may ask for written permission to syndicate the content of the sections that are specifically made available (as indicated by the availability of the RSS icons mentioned above) for personal, non-commercial use, without fee. For more information, or to obtain an authorization, contact us.
> No modifications may be made to the content of any material that is syndicated. Changes you may make are limited to display typeface, typeface size, typeface color, and linebreaks.
> You may not sell, license, or otherwise assign the use of any of the material contained in UNESCO/WHC website. Each syndication use must include a link back to the UNESCO/WHC home page: https://whc.unesco.org as well as the specific item's page.

> Each syndication use must include the following copyright notice: "Copyright © 1992 - [current year] UNESCO/World Heritage Centre. All rights reserved."

> Individuals or organizations who wish to syndicate specific material must obtain a specific XML subscription and licence from UNESCO/WHC. This will imply a fee. UNESCO/WHC reserves the right to deny syndication licences at its sole discretion.

### Terms / Policies のページ

<https://whc.unesco.org/en/disclaimer/> (2026-10-06 に読んだ) の「Intellectual Property」の表。

| License source | License / Read Usage Terms |
|---|---|
| © UNESCO | Creative Commons Attribution-ShareAlike 3.0 IGO |
| non © UNESCO (Nomination File) | Operational Guidelines の定める非独占的な権利の譲渡 (下の引用) |
| non © UNESCO | 第三者の所有。利用には権利者への個別の許可が要る |
| Creative Commons Licenses | creativecommons.org/licenses/ |
| Public Domain | No copyrights |

推薦書 (Nomination File) の行の文:

> States Parties are encouraged to grant to UNESCO, in written form and free of charge, the non exclusive cession of rights to diffuse, to communicate to the public, to publish, to reproduce, to exploit, in any form and on any support, including digital, all or part of the images provided and license these rights to third parties.

同じページの「Images Policy」:

> All photographs and other elements of the UNESCO World Heritage Centre website are protected by international treaties on intellectual property and other applicable laws. The elements it displays may not be copied or retransmitted by any means without explicit authorisation from the World Heritage Centre or the copyright holders.

「Linking Policy」:

> Do not incorporate any content from this site into your site (e.g., by in-lining, framing or creating other browser or border environments around UNESCO/WHC content). You may only link to, not replicate content.

> You may not sell, license, or otherwise assign the use of any material from UNESCO's or the World Heritage Centre's web site.

### 遺産のページの説明文と地図

遺産のページ (例: <https://whc.unesco.org/en/list/1430/>、2026-10-06 に読んだ) の説明文の下には、言語ごとに次の表示がある。

> Description is available under license CC-BY-SA IGO 3.0

リンク先は <https://whc.unesco.org/en/licenses/6> (Creative Commons Attribution-ShareAlike 3.0 IGO の要約)。スペイン語の説明には「source: UNESCO/CPE」も付く。この表示は説明文に付いたもので、同じページの座標、面積、地図には付いていない。一覧の書き出しの `short_description_*` が同じ文なら CC BY-SA 3.0 IGO で扱える可能性があるが、書き出しの側にその表示は無い (未確認)。

同じ遺産の地図のタブ (<https://whc.unesco.org/en/list/1430/maps/>) は、締約国が推薦書で出した地図 (「Namib Sand Sea - map of inscribed property」、2013) を並べ、次の断り書きを付ける。

> The Nomination files produced by the States Parties are published by the World Heritage Centre at its website and/or in working documents in order to ensure transparency, access to information and to facilitate the preparations of comparative analysis by other nominating States Parties.
> The sole responsibility for the content of each Nomination file lies with the State Party concerned.

- 範囲の地図は締約国の推薦書の一部として、透明性と比較分析のために公開されている、という位置づけ。許諾の条件は書かれていない。

### Terms / Policies の表の読み方

- Terms / Policies の表は個々の要素 (写真、文書など) に付く出典の区分と、その区分ごとの条件を並べたもの。「© UNESCO」と表示された要素は CC BY-SA 3.0 IGO になる。一覧の XML、XLSX、GIS の層に「© UNESCO」や CC BY-SA 3.0 IGO の表示は付いていなかった。
- 推薦書の行の「cession of rights」は締約国が提出する画像 (images) について書かれている。範囲の地図や GIS の層を第三者に許諾できる権利を UNESCO が得ているかは、どこにも書かれていない (未確認)。

### UNESCO の利用規約

whc.unesco.org の足元の「Terms of use」のリンクは <https://www.unesco.org/en> を指している。UNESCO の Terms of Use (<https://www.unesco.org/en/terms-use>、「Last update: 15 September 2026」、2026-10-06 に読んだ) は、「Site」を「any current or future website, platform, database, portal, mobile application, subdomain, associated site, social media account, or other online service operated by or on behalf of UNESCO」と定義する。関係する項:

> Independently of the rights in individual Materials, UNESCO holds or may assert, as applicable, copyright and other rights in the selection, verification, coordination, arrangement and presentation of its databases and online collections and in their contents.

> Except as expressly permitted under these Terms, under an applicable license, or specific authorization by UNESCO, the extraction or reutilization of all or a Substantial Part of the contents of a UNESCO database, or the repeated or systematic extraction or reutilization of insubstantial parts of its contents, is prohibited without prior written authorization, whether or not UNESCO holds rights in the/each individual Material of the database, including where individual Materials are in the public domain.

> Where a Material is made available under an Intergovernmental Organization (IGO) Creative Commons license or other specific license, the User may use that Material in accordance with the terms of that license. Not all Materials are made available under such a license: some Sites may provide Materials for viewing only and grant no license, and Contributed and Third-Party Materials may require the permission of their respective right holders.

第 7 項 (Prohibited Use) から:

> (a) use the Sites or Materials for commercial purposes; (b) extract or reutilize all or a Substantial Part of the contents of a database, or repeatedly or systematically extract or reutilize insubstantial parts of its contents; (c) access, scrape, crawl, harvest or bulk-download Materials by any Automated System, except for ordinary indexing by general-purpose search engines and real-time retrieval by Artificial Intelligence Systems as expressly permitted under Section 5; (d) use any Materials for AI training, including the training, pre-training, fine-tuning or calibration of Artificial Intelligence Systems or the creation of, or contribution to AI-training datasets incorporating Materials, except under a formal authorization granted pursuant to Section 9;

- 第 8 項で、テキストとデータのマイニング、自動の抽出、AI の学習に関する権利をすべて留保している。
- 引用の書式は「UNESCO (year), Title, URL」(第 5 項)。

### 読み取れること

- 一覧の書き出し (XML、XLSX、KML、RSS) も GIS の層も、開いたライセンスは付いていない。syndication の条件は、再掲載に書面の許可を求め、許可の対象も個人の非商用に限り、改変を認めない。
- GIS の層は item の条件で再配布、一括取得、商用利用を禁じている。表示の目的 (public consultation and map display) に限った公開。
- UNESCO の Terms of Use は、データベースの全体または実質的な部分の抽出と再利用、自動の一括取得、AI の学習用データセットへの組み込みを、書面の許可なしには禁じている。
- 範囲と緩衝地帯の線は締約国が作って提出したもの。締約国が同意したのは Sites Navigator での表示で、再配布の権利がどこにあるかは書かれていない。
- よって Hugging Face にオープンデータとして置くことは、書面の許可なしにはできない。手元の解析に使い、成果物は図や集計にとどめるのが条件に沿う。許可を求める窓口は wh-gis@unesco.org (GIS のページと技術資料に書かれている)。
- 説明文は CC BY-SA 3.0 IGO と表示されているので、遺産のページから取った説明文だけは表示と継承の条件で配れる。ただし UNESCO の Terms of Use の第 7 項は自動の一括取得とデータベースの実質的な部分の再利用を別に禁じているので、全遺産の説明文を集めて配ることまで許されるかは確かめていない (未確認)。
- 遺産の id_no、名前、登録年、基準、国といった事実は Wikidata にも別の出典として入っている。どれだけ揃っているかは確かめていない (未確認)。

## 版

- 一覧は毎年の世界遺産委員会の登録、拡張、抹消、危機遺産の出入りで変わる。XLSX の 2026 年登録は 25 件で、2026 年の第 48 回委員会の結果が入っている。RSS の `lastBuildDate` は 2026-10-05。
- 書き出しの URL は 1 つで、版の区別が無い。XLSX の `?2026` は年を付けているだけで、XLS の URL では `?2013` から `?2024` などの例が Internet Archive に残っている。年を変えて過去の一覧が出るかは試していない (未確認)。
- 過去の一覧は Internet Archive にある。CDX で数えた 200 応答の保存: `/en/list/xml` は 2005-11-25 から 2025-01-27 までに年 1 回間隔で 17 件、`/en/list/xls` の系統は 2011-06-04 から 2026-05-05 まで、`/en/list/xlsx` は 2024-12-02 から 2026-03-15 までに 5 件。
- GIS の層は随時編集される。`dataLastEditDate` は 3 層とも 2026-10-06 00:05 UTC で、警報の列が日次で書き換わる。範囲のポリゴンは締約国の提出と審査のたびに足される。サービスに過去の版を選ぶ手段は無い。
- GIS のページの 2021 年の保存 (Wayback の 20211029155119) では、欧州と北米の遺産を対象にした Online Map Platform の計画として書かれている。

## 未確認の点

- `table_source` の `elements` と `nominations` の違い。
- `element_precision_publish` の値の意味。
- `harmonized_sites_v2` の `polygon_hidden` 386 件が何か (審査中で表示しない範囲か)。
- 範囲と緩衝地帯の全件の大きさ。
- FeatureServer の書き出し (Extract) が匿名で使えるか。
- KMZ の中身 (点だけか)。GeoRSS と RSS の大きさ。
- 締約国が提出した範囲の地図について、UNESCO が第三者に許諾する権利を持つか。
- 一覧の書き出しの年の引数で過去の一覧が出るか。
- 一覧の書き出しの説明文 (`short_description_*`) が CC BY-SA 3.0 IGO の説明文と同じものか。
