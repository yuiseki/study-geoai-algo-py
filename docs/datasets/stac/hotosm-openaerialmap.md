# HOTOSM OpenAerialMap STAC API

2026-09-28 に読んで確かめた内容。

- `https://api.imagery.hotosm.org/stac` は STAC API (stac-fastapi、STAC 1.0.0)。`/search` は GET と POST の両方が使える。
- コレクションは 5 つ。cng-data-antigravity が使う 3 つ (`openaerialmap`, `maxar-opendata`, `noaa-emergency-response`) のほかに `vantor-opendata` と `cop-dem-glo-30` がある。
- 画像はどれも S3 上の GeoTIFF で、Range 要求に 206 を返す。GDAL の `/vsicurl/` でヘッダだけ読めた。
- 日本 (bbox `122,24,154,46`) では `openaerialmap` が 804 件、`maxar-opendata` が 242 件 (すべて 2024 年 1 月の能登半島地震)、他は 0 件。

## コレクション

件数は `/search` を `limit=10000`、`fields` で id だけにしてページを最後までたどって数えた (`numberMatched` は返らない)。

| id | 中身 | 件数 | 期間 (extent) | ライセンス |
|---|---|---:|---|---|
| openaerialmap | 利用者が投稿した航空写真、ドローン、衛星画像 | 21,810 | 0206-08-06 〜 2026-09-26 | CC-BY-4.0 (コレクション)。Item ごとに違う |
| maxar-opendata | Maxar Open Data の災害画像 (ARD) を載せ直したもの | 35,966 | 2010-06-02 〜 2025-11-04 | CC-BY-NC-4.0 |
| noaa-emergency-response | NOAA の災害後航空写真 | 163 | 2020-03-07 〜 2020-03-11 | public-domain |
| vantor-opendata | Vantor (Maxar の後継名) Open Data | 202 | 2021-10-16 〜 2026-09-18 | CC-BY-NC-4.0 |
| cop-dem-glo-30 | Copernicus DEM GLO-30 (30m 標高) | 26,450 | 2021-04-22 | other |

- `maxar-opendata` は 49 イベント。件数の多い順に Morocco-Earthquake-Sept-2023 (8,724)、Hurricane-Melissa-Oct-2025 (6,596)、Hurricane-Ian-9-26-2022 (4,207)、pakistan-flooding22 (2,549)、Kahramanmaras-turkey-earthquake-23 (2,115)。イベント名は asset の URL (`/events/<イベント>/`) から取った。
- `noaa-emergency-response` は 163 件すべて `event: Nashville Tornado`。NOAA の全データではなく 1 イベント分だけ。
- `openaerialmap` の日本 804 件の内訳は aircraft 520、uav 263、satellite 20、kite 1。年は 2020 年が 547 件で最も多い。ライセンスは CC-BY-4.0 が 790、CC-BY-NC-4.0 が 7、CC-BY-SA-4.0 が 6、null が 1。

## Item の中身 (各コレクション 1 件)

| コレクション | 見本の Item | asset | 大きさ (visual) | 画素 | CRS | 画素サイズ | 圧縮 |
|---|---|---|---:|---|---|---|---|
| openaerialmap | Jatimulya, Depok (ドローン、2026-09-26) | visual, original, mbtiles, metadata, thumbnail | 15,270,586 B (original は 139,732,499 B) | 9162 x 7340, RGBA | EPSG:32748 | 0.040 m (gsd 0.040) | WEBP (非可逆) |
| maxar-opendata | Hurricane Melissa (WV02, 2025-11-04) | visual, ms_analytic, pan_analytic, data-mask | 6,229,954 B | 17408 x 17408, RGB | EPSG:32619 | 0.305 m (gsd は 0.77) | YCbCr JPEG |
| noaa-emergency-response | Nashville Tornado (2020-03-11) | cog のみ | 9,709,431 B | 18681 x 18681, RGB | EPSG:4326 | 約 1.35e-6 度 | YCbCr JPEG |
| vantor-opendata | Nepal-Flooding-Aug-2026 (LG06) | visual, thumbnail | 334,854,058 B | 未確認 (gdalinfo は実行していない) | 未確認 | gsd 0.36 | 未確認 |

- 3 つ (openaerialmap, maxar-opendata, noaa) は gdalinfo `/vsicurl/` で 512x512 のタイルとオーバービューを確かめた。`LAYOUT=COG` の表示が出たのは openaerialmap と maxar-opendata。noaa は表示が無いが、タイル分割とオーバービューがあるので部分読みはできる形。
- `maxar-opendata` の `gsd` (0.77) は撮影時の地上分解能で、ファイルの画素サイズ (0.305 m) とは違う。ARD は 0.305 m の格子に揃えて配っている。
- `openaerialmap` の visual は元画像から作った表示用の非可逆 COG (`processing:lineage` に明記)。解析で色の値を使うなら `original` を見る。

## 検索の使い方

```bash
# 日本の OAM 画像を新しい順に 3 件
curl -X POST https://api.imagery.hotosm.org/stac/search -H 'Content-Type: application/json' -d '{
  "collections": ["openaerialmap"],
  "bbox": [122, 24, 154, 46],
  "datetime": "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z",
  "sortby": [{"field": "properties.datetime", "direction": "desc"}],
  "limit": 3
}'
```

- `bbox`、`datetime`、`sortby` (asc / desc) はどれも効いた。GET の `sortby=-properties.datetime` も効いた。
- `openaerialmap` の Item は `properties.datetime` が null で、`start_datetime` と `end_datetime` だけを持つ。それでも `datetime` での絞り込みと `properties.datetime` での並べ替えは期間で効いた。
- 何も指定しないときも新しい順に返ってきた。
- `limit=10000` まで 1 ページで返る。`openaerialmap` の 1 万件 (id だけ) で約 12 秒。
- conformance には item-search の filter (CQL2)、fields、sort、query がある。

## 気をつけること

- `openaerialmap` の期間の始まりが 0206 年になっている。日付を誤入力した Item があると思われる (該当 Item は探していない)。
- `openaerialmap` の gsd は日本の範囲だけでも 0.0023 m から 1180.7 m まで広がる。1180 m は航空写真としてありえないので、値を信じる前に確かめる。
- `openaerialmap` の Item の properties に、投稿者のメールアドレス (`oam:uploader_email`) がそのまま入っている。データを再配布するときはこの列を落とす。
- `noaa-emergency-response` の asset は `cog` という名前で、`visual` が無い。cng-data-antigravity の `hotosm-noaa` は `asset: visual` を指定していて、`stac_cog.py` は `item.assets[source["asset"]]` と引くので、コードを読む限り KeyError になるはず (実行しては確かめていない)。
- `maxar-opendata` は Maxar 本家の静的 STAC と同じファイルを指している (asset の URL が `maxar-opendata.s3.amazonaws.com/events/...` で同じ)。ただし本家にある 6 イベント (2025 年 11 月以降の 5 つと Hurricane-Maria-PuertoRico-Oct-2017) が無く、2025-11-04 で止まっている。詳しくは [maxar-opendata.md](maxar-opendata.md)。
- `openaerialmap` はコレクションのライセンスが CC-BY-4.0 でも、Item ごとに CC-BY-NC-4.0 や CC-BY-SA-4.0 がある。Item の `license` を見る。

## 12 ステップで使えそうなところ (案)

- 5 k-means / DBSCAN: 画像 1 枚の画素の色を k-means で分ける (教師なしの土地被覆)。Item の中心点を DBSCAN にかけ、`maxar-opendata` の 49 イベントが塊として出てくるか見る。
- 6 PCA: `maxar-opendata` の `ms_analytic` (多バンド) を PCA で縮める。
- 1, 2 ロジスティック回帰 / Random Forest: `openaerialmap` の Item の表 (gsd、面積、機材、年) から `oam:platform_type` (uav / aircraft / satellite) を当てる。ラベルは Item に入っている。画素の分類はラベルが無いので自分で作る必要がある。
- 4 Cross Validation とデータリーク: 隣り合うタイルや同じ撮影 (catalog_id) の画像を学習と検証に分けるとリークになる。quadkey や catalog_id でグループ分けする練習になる。
- 災害前後の比較: 能登半島地震の 242 件は 2023-08 から 2023-12-30 の撮影 (前) と 2024-01-02 の撮影 (後) を含む。同じ quadkey の前後を並べて差分を取れる。
