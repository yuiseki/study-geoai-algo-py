# Landsat Collection 2 Level-2 (Microsoft Planetary Computer)

2026-09-30 に読んで確かめた内容。数値は Planetary Computer の STAC API への無認証の要求と、SAS 署名後の HEAD による実測。ライセンスは USGS の該当ページの本文。

- STAC API: `https://planetarycomputer.microsoft.com/api/stac/v1`、コレクション `landsat-c2-l2`。
- 中身は Landsat 4/5 の TM、Landsat 7 の ETM+、Landsat 8/9 の OLI と TIRS を大気補正した地表反射率と地表温度。1 アイテム = 1 シーン (WRS-2 の path/row 1 つ分)。
- temporal extent は `1982-08-22T00:00:00Z` から終わり無し、spatial extent は全球。40 年を超える時系列がある点が、2020 年からしかない [HLS](../hls/README.md) との一番の違い。
- 提供者は NASA (producer, licensor)、USGS (producer, processor, licensor)、Microsoft (host)。置き場は Azure Blob の `landsateuwest`。
- DOI は 3 つに分かれている。`10.5066/P9IAXOVV` (Landsat 4-5 TM)、`10.5066/P9C7I13B` (Landsat 7 ETM+)、`10.5066/P9OGBGM6` (Landsat 8-9 OLI/TIRS)。
- planetarble (`configs/base/pipeline.yaml`) はこれを `hls.fallback_collections` に 1 つだけ入れている。HLS で雲が抜けないときの穴埋め用で、`fallback_max_cloud` は 90.0。

同じ Planetary Computer の Sentinel-2 L2A は [別項](../stac/sentinel-2-l2a-planetary-computer.md) にある。SAS トークンの署名が必須という点はこのコレクションも同じで、下の実測で確かめた。

## アセット

`item_assets` は 26 個。実際の 1 アイテム (LC09_L2SP_107036_20260828_02_T1) では Blob 上に 23 個あった。署名付き URL への HEAD の Content-Length。

| アセット | 中身 | バイト数 |
|---|---|---:|
| blue | 青 (SR_B2) | 98,721,593 |
| green | 緑 (SR_B3) | 98,721,671 |
| coastal | 沿岸エアロゾル (SR_B1) | 98,650,535 |
| nir08 | 近赤外 (SR_B5) | 98,715,038 |
| red | 赤 (SR_B4) | 98,579,728 |
| swir16 | 短波赤外 1.6µm | 95,107,275 |
| swir22 | 短波赤外 2.2µm | 94,353,783 |
| trad | 熱放射 | 77,735,462 |
| lwir11 | 地表温度 (gsd 100) | 64,051,111 |
| qa | 品質 | 43,568,271 |
| atran | 大気透過率 | 12,916,224 |
| urad | 上向き放射 | 12,490,976 |
| drad | 下向き放射 | 9,342,159 |
| emis | 射出率 | 7,085,638 |
| qa_aerosol | エアロゾル品質 | 4,408,653 |
| cdist | 雲からの距離 | 4,357,844 |
| emsd | 射出率の標準偏差 | 3,990,153 |
| qa_pixel | 画素品質 (雲マスク) | 3,513,508 |
| qa_radsat | 飽和品質 | 230,663 |
| ang | 角度係数 | 117,391 |
| mtl.xml / mtl.txt / mtl.json | メタデータ | 22,517 / 15,292 / 14,423 |
| 合計 (Blob 上の 23 個) | | 926,709,908 |

- `proj:epsg` は 32654 (UTM 54N)、`proj:shape` は 7881 x 7751。`red` の TIFF ヘッダを読むと 7751 x 7881 の 16bit、Deflate 圧縮、256 x 256 のタイル (TileOffsets の要素数 961)。IFD はオフセット 8、つまりファイル先頭にある。
- `lwir11` だけ gsd が 100 m。他の反射率バンドは 30 m。

## 東京付近の 1 か月分 (bbox 139.56,35.52,139.92,35.82、2026-08-01 から 2026-08-31)

無認証の POST `/search` が HTTP 200 で 12 件。

- WRS-2 の path/row は 107/035、107/036、108/035 の 3 通り。東京の bbox が 3 つのシーンの重なりにかかる。
- 衛星は landsat-8 が 5 件、landsat-9 が 7 件。`landsat:correction` はすべて L2SP、`landsat:collection_number` はすべて 02。
- `eo:cloud_cover` は 20.72 から 99.92。50 未満は 3 件 (8/20 の 107/036 が 20.72、8/19 の 108/035 が 43.62、8/12 の 107/036 が 45.46)。
- 同じ期間の [HLS](../hls/README.md) は 20 件で雲量 50 未満が 2 件。Landsat 単独のほうが件数は少ないが、雲の少ないシーンの数はむしろ多かった。

## 取り出し方

catalog。副次的に range。

- STAC 検索は認証なしで通る。`POST https://planetarycomputer.microsoft.com/api/stac/v1/search` に上記の bbox と datetime を投げて HTTP 200、12 件。
- `collections/landsat-c2-l2/queryables` は 27 項目。`eo:cloud_cover`、`landsat:wrs_path`、`landsat:wrs_row`、`landsat:collection_category`、`landsat:cloud_cover_land`、`platform`、`view:sun_elevation` などが宣言されている。HLS の 5 項目と比べて格段に絞り込みやすい。
- `query` に `{"eo:cloud_cover": {"lt": 50}}` を入れた検索は HTTP 200 で 3 件を返した。
- アセットの読み出しには SAS トークンの署名が要る。署名無しで `https://landsateuwest.blob.core.windows.net/landsat-c2/level-2/standard/oli-tirs/2026/107/036/LC09_L2SP_107036_20260828_20260829_02_T1/LC09_L2SP_107036_20260828_20260829_02_T1_SR_B4.TIF` に `Range: bytes=0-1023` を投げると HTTP 409、本文は 248 バイトの `PublicAccessNotPermitted` (`Public access is not permitted on this storage account.`)。署名を飛ばすと 1 バイトも読めない。
- トークンは `GET https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2` が認証無しで HTTP 200。08:38 UTC に取った応答の `msft:expiry` は 2026-09-30T09:23:20Z で、有効期間は約 45 分。1 URL ずつ署名する `GET https://planetarycomputer.microsoft.com/api/sas/v1/sign?href=...` も HTTP 200 を返した。
- 署名後は Range 要求が HTTP 206、1,024 バイト。先頭は `II*\0` で IFD はオフセット 8。256 x 256 のタイル TIFF なので窓読みができる。ただし HLS の COG と違い `GDAL_STRUCTURAL_METADATA` のゴーストヘッダは無く、オーバービューの有無は先頭 1KB からは確かめていない (未確認)。
- コレクションに `geoparquet-items` アセットがある。href は `abfs://items/landsat-c2-l2.parquet`、`msft:partition_info` は `{"is_partitioned": true, "partition_frequency": "MS"}` で月単位の分割。今回 abfs の読み出しは試していない (未確認)。

## ライセンス

STAC のコレクションの `license` は `proprietary`。license リンクは `https://www.usgs.gov/core-science-systems/hdds/data-policy` で、タイトルは「Public Domain」。今日たどると `https://www.usgs.gov/emergency-operations-portal/data-policy` に 200 でリダイレクトされる。

このリンク先は Landsat 専用の文書ではなく、災害対応ポータル (HDDS) が扱う雑多な画像の方針を述べたページで、public domain のものと制限付きのものを区別している。public domain の側の本文。

> All public domain imagery may be used, shared, transferred, or redistributed without restriction. However, there should be acknowledgement of the image source within any derived maps, products, or publications.

同じページに、Landsat が public domain の側だと明示されている。

> Most of the satellite images supplied by U.S. Federal civil agencies are public domain (such as Landsat or ASTER).

Landsat Collection 2 Level-2 の製品ページ (`https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products`) の本文はもっと直接的。

> There are no restrictions on the use of Landsat products. Please cite the appropriate Landsat Level-2 datasets in the following manner:

同じページのクレジットについての一文。

> It is not a requirement, but the following credit may be used in publication or presentation materials to acknowledge the USGS:

USGS 全体の方針 (`https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits`) も同じ向き。

> When using information from USGS information products, publications, or websites, we ask that proper credit be given.

読み取れること。Landsat Collection 2 Level-2 は「制限なし」で、表示は要請であって義務ではない。製品ページははっきり「not a requirement」と書いている。HDDS のページの「there should be acknowledgement」という言い方はもう少し強いが、こちらも「must」ではない。CC0 のような明示的な権利放棄の宣言文ではなく、米国政府の著作物は米国内で著作権の対象にならないという前提に立った「制限なし + 表示は任意」である。

Planetary Computer 自体の利用規約 (`https://planetarycomputer.microsoft.com/terms`) は JavaScript で描くページで、curl では本文が取れなかった (未確認)。

## 気をつけること

コレクションの license リンクが指す先が Landsat の方針を書いた文書ではない。災害対応ポータルの、権利の混ざった画像群についてのページで、Landsat は例示として 1 回出てくるだけ。ライセンスを自動で辿る処理はここで誤読する。根拠として使うなら Landsat Collection 2 の製品ページのほうを見る。

`license` フィールドの値は `proprietary`。「制限なし」という結論と食い違うので、機械的に読むと使えないデータに分類される。

planetarble の README は「NASA/USGS public domain」と書く。Landsat についてはこの表現で大きく外れてはいない。ただし表示は義務ではないというところまで含めて言うなら、GEBCO や ETOPO を同じ一文でまとめるのは正しくない ([GEBCO](../gebco/README.md) は表示が義務)。

署名を飛ばすと 409。トークンの寿命は約 45 分で、コレクションごとに別のトークンが要る。HLS 用のトークンで Landsat の Blob は読めない (別のストレージアカウント)。

1 シーンは全アセットで約 927MB あり、[HLS](../hls/README.md) の 1 アイテム (約 225MB) の 4 倍。穴埋めのつもりで全部落とすと転送量が主役を追い越す。

`landsat:collection_category` は T1 と T2 を区別する。T2 は幾何精度が落ちる。今回の 12 件のうち 1 件 (LC08_L2SP_108035_20260827) が T2 で、雲量も 99.92 だった。並べて使うときはカテゴリで絞る。

Collection 2 Level-2 の反射率は DN で、スケールとオフセットが掛かる。今回 `raster:bands` の有無は確かめていない (未確認)。物理量にするなら `mtl.json` を読む必要がある。

## 学習ステップでの使いどころ (案)

- 1 から 3 の分類器: 反射率 7 バンドに地表温度 (lwir11) を足せる。Sentinel-2 系には無い熱赤外が使えるのがこのデータの利点。
- 4 Cross Validation: 1982 年からあるので、年で分けた分割と空間で分けた分割の差を大きく取れる。
- 8 時系列: 同じ path/row を数十年並べて、都市化や植生の変化を追う。`landsat:wrs_path` と `landsat:wrs_row` で絞れる。
- 11 SHAP: 熱赤外が分類にどれだけ効くかを、反射率だけのモデルと比べる。
- 12 多目的最適化: 雲量、撮影日、T1/T2 のカテゴリを天秤にかけてシーンを選ぶ。
