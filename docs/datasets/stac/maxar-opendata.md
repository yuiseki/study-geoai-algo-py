# Maxar Open Data (静的 STAC カタログ)

2026-09-28 に読んで確かめた内容。

- `https://maxar-opendata.s3.amazonaws.com/events/catalog.json` が入口の Catalog (STAC 1.0.0、`license: CC-BY-NC-4.0`)。検索 API (`/search`) は無い。ただの JSON ファイルの木。
- 構造は `catalog.json` → イベントごとの `{イベント}/collection.json` → 撮影 (acquisition) ごとの `{イベント}/ard/acquisition_collections/{catalog_id}_collection.json` → Item → asset。
- イベントは 55、acquisition は全部で 1,109 (55 個の `collection.json` の child リンクを数えた)。
- Item の総数は数えていない (1,109 個の acquisition を全部読む必要があり、60 秒に収まらない)。HOTOSM 側の載せ直し ([hotosm-openaerialmap.md](hotosm-openaerialmap.md)) は 49 イベントで 35,966 件だった。
- 画像は GeoTIFF で、Range 要求に 206 を返す。GDAL の `/vsicurl/` で部分読みできた。
- 日本は Japan-Earthquake-Jan-2024 (能登半島地震) の 1 イベントだけ。11 acquisition、242 Item。

## 1 件の Item (能登半島地震)

`Japan-Earthquake-Jan-2024/ard/53/120022031302/2024-01-02/10200100E6723900.json`

- Item の id は `53/120022031302/10200100E6723900` (UTM ゾーン / quadkey / catalog_id)。1 Item = 1 つの地上タイル (quadkey) の 1 回の撮影。
- properties: platform WV01、gsd 0.7、`view:off_nadir` 34.1、`tile:clouds_percent` 0、`proj:epsg` 32653 など。
- asset は visual、pan_analytic、data-mask (GeoPackage)。WorldView-2 など多バンドの衛星では ms_analytic もある。
- visual は 12,573,295 B、17408 x 17408 画素、EPSG:32653、画素サイズ 0.305 m、512x512 タイル、オーバービュー 6 段、JPEG 圧縮。
- `gdal_translate -srcwin 0 0 512 512` で 512x512 を切り出すのに約 1.4 秒だった。

## イベントの一覧

acquisition は各イベントの `collection.json` の child リンクの数。期間はその `extent.temporal` (災害前の撮影も含むので、イベント名の年月より前から始まる)。

| イベント | acquisition | 期間 |
|---|---:|---|
| BayofBengal-Cyclone-Mocha-May-23 | 5 | 2023-01-03 〜 2023-05-22 |
| Belize-Wildfires-June24 | 7 | 2019-08-29 〜 2024-06-03 |
| Brazil-Flooding-May24 | 38 | 2018-12-17 〜 2024-05-17 |
| Cyclone-Chido-Dec15 | 29 | 2024-05-23 〜 2025-01-01 |
| Cyclone-Ditwah-Sri-Lanka-Nov-2025 | 8 | 2025-01-17 〜 2025-12-05 |
| Cyclone-Senyar-Indonesia-Nov-2025 | 1 | 2025-11-30 〜 2025-11-30 |
| Cyclone-Senyar-Thailand-Nov-2025 | 4 | 2025-12-01 〜 2025-12-01 |
| Earthquake-Myanmar-March-2025 | 29 | 2025-02-02 〜 2025-04-04 |
| Emilia-Romagna-Italy-flooding-may23 | 11 | 2015-05-28 〜 2023-05-23 |
| Floods-Spain-Oct24 | 12 | 2024-03-14 〜 2024-11-10 |
| Gambia-flooding-8-11-2022 | 6 | 2022-03-15 〜 2022-08-13 |
| Hurricane-Fiona-9-19-2022 | 16 | 2022-02-07 〜 2022-09-29 |
| Hurricane-Ian-9-26-2022 | 89 | 2021-04-29 〜 2022-10-08 |
| Hurricane-Idalia-Florida-Aug23 | 14 | 2017-10-20 〜 2023-08-30 |
| Hurricane-Maria-PuertoRico-Oct-2017 | 2 | 2017-08-29 〜 2017-10-12 |
| Hurricane-Melissa-Oct-2025 | 134 | 2022-10-13 〜 2025-11-09 |
| HurricaneHelene-Oct24 | 42 | 2019-11-09 〜 2024-10-06 |
| HurricaneMilton-Oct24 | 15 | 2023-11-04 〜 2024-10-10 |
| Iceland-Volcano_Eruption-Dec-2023 | 1 | 2023-07-08 〜 2023-07-08 |
| India-Floods-Oct-2023 | 6 | 2022-03-07 〜 2023-10-06 |
| Indonesia-Earthquake22 | 8 | 2021-07-04 〜 2022-11-28 |
| Japan-Earthquake-Jan-2024 | 11 | 2023-08-29 〜 2024-01-02 |
| Kahramanmaras-turkey-earthquake-23 | 76 | 2021-02-28 〜 2023-03-11 |
| Kalehe-DRC-Flooding-5-8-23 | 2 | 2023-04-10 〜 2023-05-12 |
| Kenya-Flooding-May24 | 2 | 2023-11-30 〜 2024-05-11 |
| Libya-Floods-Sept-2023 | 15 | 2023-01-22 〜 2023-09-22 |
| Marshall-Fire-21-Update | 1 | 2021-12-30 〜 2021-12-30 |
| Maui-Hawaii-fires-Aug-23 | 5 | 2023-08-09 〜 2023-08-12 |
| McDougallCreekWildfire-BC-Canada-Aug-23 | 2 | 2022-05-18 〜 2022-07-14 |
| Morocco-Earthquake-Sept-2023 | 238 | 2010-06-02 〜 2023-09-11 |
| Morocco-Flooding-Dec-2025 | 2 | 2025-11-11 〜 2025-12-18 |
| NWT-Canada-Aug-23 | 4 | 2023-08-08 〜 2023-08-21 |
| Nepal-Earthquake-Apr-2015 | 1 | 2023-10-25 〜 2023-10-25 |
| Nepal-Earthquake-Nov-2023 | 8 | 2014-12-04 〜 2023-11-09 |
| Nepal-Floods-Sept-2024 | 17 | 2022-03-26 〜 2024-10-06 |
| New-Zealand-Flooding23 | 3 | 2022-11-01 〜 2023-02-08 |
| Nigeria-Flooding-May-2025 | 2 | 2023-10-09 〜 2025-06-02 |
| Nigeria-Floods-Sept-2024 | 2 | 2024-01-12 〜 2024-03-25 |
| PNG-Landslide-June24 | 2 | 2023-06-27 〜 2024-05-27 |
| SmokeHouseCreek-Wildfires-Texas-Mar24 | 16 | 2021-07-31 〜 2024-03-04 |
| Sudan-flooding-8-22-2022 | 7 | 2022-03-23 〜 2022-09-07 |
| Texas-Flooding-July-2025 | 4 | 2025-07-08 〜 2025-07-09 |
| Typhoon-Kalmaegi-Nov-2025 | 31 | 2025-03-04 〜 2025-11-14 |
| Vanuatu-Earthquake-Dec17 | 6 | 2024-09-21 〜 2024-12-02 |
| WildFires-LosAngeles-Jan-2025 | 40 | 2024-12-14 〜 2025-01-20 |
| afghanistan-earthquake22 | 15 | 2021-06-09 〜 2022-06-27 |
| cyclone-emnati22 | 6 | 2020-08-11 〜 2022-02-28 |
| ghana-explosion22 | 3 | 2020-01-06 〜 2022-01-22 |
| kentucky-flooding-7-29-2022 | 10 | 2021-07-03 〜 2022-08-07 |
| pakistan-flooding22 | 63 | 2019-11-29 〜 2022-10-11 |
| shovi-georgia-landslide-8Aug23 | 3 | 2011-09-19 〜 2023-08-08 |
| southafrica-flooding22 | 13 | 2022-04-12 〜 2022-04-21 |
| tonga-volcano21 | 10 | 2021-03-27 〜 2022-01-18 |
| volcano-indonesia21 | 7 | 2019-05-18 〜 2021-12-11 |
| yellowstone-flooding22 | 5 | 2022-06-15 〜 2022-06-18 |

## 検索 API が無いことの影響

- 場所で絞るには木をたどるしかない。全イベントの範囲を知るだけで `catalog.json` 1 件 + `collection.json` 55 件 = 56 要求。逐次で約 28 秒だった (1 件あたり約 0.45 秒)。
- Item まで届くには、さらに acquisition の `collection.json` を最大 1,109 件読み、その先の Item の JSON を 1 件ずつ読む。範囲の重ならないイベントを外せば減らせる (cng-data-antigravity の `stac-static-cog` はこれをやっている)。
- 能登半島地震 1 イベントなら、acquisition 11 件の読み込みが 6.4 秒で済んだ。イベント名がわかっているなら `collection` を指定するのがよい。
- 時刻でも絞れない。Item を開くまで撮影日時がわからない (acquisition の `extent.temporal` で大まかには絞れる)。
- バケットは一覧 (`?list-type=2&prefix=events/&delimiter=/`) を公開している。`events/` の下に 56 フォルダあり、カタログに載っていない `bangladesh-flooding22` が 1 つある。

## HOTOSM の maxar-opendata との関係

- 同じ画像を別の経路で出している。能登半島地震の Item `53/120022031302/10200100E6723900` は、HOTOSM では id `53-120022031302-10200100E6723900` (区切りが `-`) で、visual の URL は同じ `maxar-opendata.s3.amazonaws.com/events/...-visual.tif` だった。
- 能登半島地震の Item 数は、本家の木をたどっても HOTOSM で bbox 検索しても 242 件で一致した。
- HOTOSM に無いイベントが 6 つある: Cyclone-Ditwah-Sri-Lanka-Nov-2025、Cyclone-Senyar-Indonesia-Nov-2025、Cyclone-Senyar-Thailand-Nov-2025、Morocco-Flooding-Dec-2025、Typhoon-Kalmaegi-Nov-2025、Hurricane-Maria-PuertoRico-Oct-2017。HOTOSM の期間は 2025-11-04 で終わっているので、その頃に取り込みが止まったように見える (理由は未確認)。Maria は古いイベントだが HOTOSM に無い。
- 検索したいなら HOTOSM、最新のイベントや全部が欲しいなら本家、という使い分けになる。

## ライセンス

- `catalog.json` と各イベントの `collection.json` は 55 件すべて `CC-BY-NC-4.0`。
- AWS Open Data Registry の `maxar-open-data.yaml` も Creative Commons Attribution Non Commercial 4.0。非商用のみ。
- バケットに README は無かった (`events/README.md` は 404)。

## 気をつけること

- Item の `datetime` が `2024-01-02 04:34:38Z` のように T の代わりに空白で書かれている。RFC 3339 の厳密なパーサーは読めない。
- WV01 (白黒の衛星) の visual は 1 バンド (Gray) で、RGB ではない。「visual = RGB」と決め打ちしない。
- `gsd` (撮影時の分解能、0.7 など) とファイルの画素サイズ (0.305 m) は違う。
- イベント名の年月と中身が合わないものがある。Nepal-Earthquake-Apr-2015 は撮影が 2023-10-25 の 1 回だけ。Nigeria-Floods-Sept-2024 は 2024-03-25 まで、McDougallCreekWildfire-BC-Canada-Aug-23 は 2022-07-14 までで、イベント後の撮影が無いように見える。
- イベント名の書き方が揃っていない (`pakistan-flooding22`、`Hurricane-Ian-9-26-2022`、`HurricaneMilton-Oct24` など)。名前から年月を機械的に取り出せない。
- 2025 年以降は Vantor という名前で別のバケット (`vantor-opendata`) にも出ている。HOTOSM の `vantor-opendata` コレクションに 202 件あった。

## 12 ステップで使えそうなところ (案)

- 災害前後の比較: 同じ quadkey の前後の撮影を並べられる。能登半島地震なら 2023-08-29 から 2023-12-30 の撮影と 2024-01-02 の撮影がある。
- 5 k-means / DBSCAN: 前後の差分画像の画素を k-means で分け、変化した場所を取り出す。
- 6 PCA: ms_analytic の多バンドを PCA で縮める。前後を重ねたバンドに PCA をかける変化検出もある。
- 4 Cross Validation とデータリーク: 同じ catalog_id や隣の quadkey を学習と検証に分けるとリークになる。グループ分けの題材になる。
- 1, 2 ロジスティック回帰 / Random Forest: 被害ラベルは入っていないので、分類をするならラベルを自分で作るか、別の出どころ (被害判読データなど) と組み合わせる必要がある。
