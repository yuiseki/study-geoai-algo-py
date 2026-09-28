# Sentinel-2 L2A (Microsoft Planetary Computer)

2026-09-28 に読んで確かめた内容。

- STAC API: `https://planetarycomputer.microsoft.com/api/stac/v1`、コレクション `sentinel-2-l2a`。
- 中身は Sentinel-2 の全球アーカイブを L2A (大気補正後の地表反射率、Sen2Cor で処理) にして COG に変換したもの。1 アイテム = 1 回の撮影の MGRS タイル 1 枚 (約 110 km 四方、UTM)。
- 提供者: ESA (producer, licensor)、Esri (processor)、Microsoft (host, processor)。置き場は Azure Blob の `sentinel2l2a01` / `sentinel2-l2` (westeurope)。
- 期間: コレクションの temporal extent は `2015-06-27T10:25:31Z` から終わり無し (更新中)。東京の bbox で一番古いアイテムは 2015-08-07、一番新しいのは 2026-09-23 (5 日前)。
- 解像度: gsd は 10、20、60 m。

## アセット (item_assets と 1 アイテムの実物)

| アセット | 中身 | gsd (m) | 画素数 (1 アイテム) |
|---|---|---:|---|
| B02, B03, B04, B08 | 青、緑、赤、近赤外 | 10 | 10980 x 10980 |
| B05, B06, B07, B8A | レッドエッジ 1-4 | 20 | 5490 x 5490 |
| B11, B12 | 短波赤外 1.6 / 2.2 µm | 20 | 5490 x 5490 |
| B01, B09 | 沿岸エアロゾル、水蒸気 | 60 | 1830 x 1830 |
| AOT, WVP | エアロゾル光学的厚さ、水蒸気量 | 10 | 10980 x 10980 |
| SCL | シーン分類 (雲、影、植生、水など) | 20 | 5490 x 5490 |
| visual | トゥルーカラー (TCI) | 10 | 10980 x 10980 |
| safe-manifest ほか XML 4 つ | メタデータ | | |
| tilejson, rendered_preview | Planetary Computer のタイル API | | |

- 分光バンドは 12 個 (B10 は L2A に無い)。

## クエリ可能な項目 (queryables)

`/collections/sentinel-2-l2a/queryables` で 36 項目。学習でよく使いそうなもの:

- `datetime`、`eo:cloud_cover`、`s2:mgrs_tile`、`sat:relative_orbit`、`sat:orbit_state`、`platform` は properties にある。
- 画素の割合: `s2:vegetation_percentage`、`s2:water_percentage`、`s2:snow_ice_percentage`、`s2:cloud_shadow_percentage`、`s2:thin_cirrus_percentage`、`s2:high_proba_clouds_percentage`、`s2:medium_proba_clouds_percentage`、`s2:nodata_pixel_percentage` ほか。
- 太陽の角度: `s2:mean_solar_zenith`、`s2:mean_solar_azimuth`。処理版: `s2:processing_baseline`。

## 東京付近の 1 か月分 (bbox 139.56,35.52,139.92,35.82、2026-08-01 から 2026-08-31)

- 16 件。8 回の撮影 x 2 つの MGRS タイル (54SUE と 54SVE)。bbox がタイルの境目にかかるので、同じ日に 2 件ずつ出る。
- 撮影日: 8/4、8/9、8/11、8/14、8/19、8/24、8/29、8/31。衛星は Sentinel-2A、2B、2C の 3 機。相対軌道はすべて 74、処理版はすべて 05.12。
- 雲量 (`eo:cloud_cover`) は 10.24 % から 99.96 %。30 % 以下は 8/24 の 2 件 (54SUE 10.24 %、54SVE 18.73 %) だけ。
- レスポンスに `numberMatched` も `context` も無く、件数はページを数えるしかない (limit 500 で 1 ページに収まった)。

### 1 件の中身 (S2B_MSIL2A_20260824T012649_R074_T54SUE_20260824T043331)

- EPSG 32654 (UTM 54N)。bbox 138.778,35.135 から 140.010,36.141。
- アセットの大きさ (署名付き URL への HEAD の Content-Length):

| アセット | バイト数 |
|---|---:|
| visual | 363,581,758 |
| B08 | 286,382,937 |
| B03 | 276,678,687 |
| B02 | 272,150,898 |
| B04 | 271,442,386 |
| WVP | 111,292,089 |
| B05, B06, B07, B8A, B11, B12 | 各 70,294,925 から 72,120,788 |
| datastrip-metadata | 13,116,265 |
| B09 / B01 | 8,058,930 / 7,704,220 |
| AOT | 5,367,232 |
| SCL | 3,368,331 |
| XML 4 つ | 18,648 から 626,493 |
| 合計 (Blob 上の 21 個) | 2,048,035,260 |

## 読むには SAS トークンの署名が要る

- 署名無しで asset の URL を Range 要求すると 409 `PublicAccessNotPermitted` (「Public access is not permitted on this storage account.」)。
- トークン: `GET https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a` が `{"msft:expiry": ..., "token": "st=...&se=...&sp=rl&...&sig=..."}` を返した (認証無し、200)。取得から有効期限まで約 45 分 (07:58 に取って expiry 08:43 UTC)。asset の URL の後ろに `?` + token を付ける。
- 1 URL ずつの署名: `GET https://planetarycomputer.microsoft.com/api/sas/v1/sign?href=<URL エンコードした href>` も 200 で `{"msft:expiry", "href"}` を返した。cng-data-antigravity の `adapters/stac_cog.py` はこちらを使っている。
- 署名後の B04 を `gdalinfo /vsicurl/...` で開けた (1.3 秒): `LAYOUT=COG`、DEFLATE、ブロック 512x512、UInt16 (NBITS=15)、オーバービュー 4 段 (5490 から 687)。
- `gdal_translate -srcwin 9000 5000 512 512` で 512x512 の窓だけを 3.8 秒で読めた。値は 1,194 から 17,729、平均 2,083.8。

## ライセンス

- コレクションの `license` は `proprietary`。license リンクは「Copernicus Sentinel data terms」(`https://scihub.copernicus.eu/twiki/pub/SciHubWebPortal/TermsConditions/Sentinel_Data_Terms_and_Conditions.pdf`)。
- アイテムには `https://sentinel.esa.int/documents/247904/690755/Sentinel_Data_Legal_Notice` へのリンクがある。
- どちらの文書も今回は読めなかった (scihub.copernicus.eu は接続できず、sentinel.esa.int は名前解決できなかった)。条件の中身は未確認。
- Planetary Computer 自体の利用規約も今回は読んでいない。

## 気づいた異常

- コレクションの license リンク先 (scihub.copernicus.eu) に接続できなかった。Sci Hub は Copernicus Data Space Ecosystem に移ったサービスで、リンクが古いままと読める (確かめていない)。
- 説明文は「from 2016 to the present」「thirteen spectral bands」と書くが、東京の bbox で 2015-08-07 のアイテムがあり (生成日 2021-04-11 の再処理版)、L2A のアセットに分光バンドは 12 個しか無い (B10 が無い)。
- `item_assets` には `preview` があるが、実際のアイテムには無く、代わりに `tilejson` と `rendered_preview` がある。
- 反射率の値にスケールやオフセットの情報 (`raster:bands`) がアセットに無い。処理版 04.00 以降の L2A は DN に +1000 のオフセットが入る、というのが ESA の仕様として知られているが、この item にはそれが書かれていない。窓の最小値 1,194 はオフセットがあると考えると説明できる (確かめていない)。処理版が混ざる期間をまたいで使うときは `s2:processing_baseline` を見て揃える必要がある。
- cng-data-antigravity の組み込み (`sources/sentinel_2_pc.py`) は `visual` (8bit のトゥルーカラー) を切り出す。見た目の確認には良いが、NDVI などの計算や学習の特徴量には B04/B08 などの反射率バンドを別に指定する必要がある。

## 学習ステップでの使いどころ (案)

- 1 ロジスティック回帰、2 Random Forest、3 XGBoost: 画素または区画ごとに B02 から B12 と NDVI、NDWI などを特徴量にして土地被覆を分類する。SCL をそのまま (粗い) 教師ラベルにする練習もできる。
- 4 Cross Validation とデータリーク: 隣り合う画素はほぼ同じ値なので、ランダム分割だと精度が高く出すぎる。空間ブロック分割や、日付で分けた場合との差を見る好題材。
- 5 k-means/DBSCAN: 12 バンドの画素を教師無しでまとめ、土地被覆らしい群が出るかを見る。
- 6 PCA: 12 バンドは互いに強く相関するので、主成分 2、3 個で大半が説明できるかを見る。
- 11 SHAP/calibration: どのバンドが分類に効いたか、雲量で確率がどうずれるかを見る。
- 12 多目的最適化: 雲量の少なさと撮影日の新しさ (と取得量) を天秤にかけて、使うシーンを選ぶ。
- 1 シーンは全バンドで約 2GB あるので、COG の窓読み (gdal_translate -srcwin や -projwin) で必要な範囲だけを引く。トークンは約 45 分で切れるので、長い処理では取り直す。
