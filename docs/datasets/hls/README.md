# HLS v2.0 (Harmonized Landsat Sentinel-2, Microsoft Planetary Computer)

2026-09-30 に読んで確かめた内容。数値は Planetary Computer の STAC API への無認証の要求と、SAS 署名後の HEAD による実測。ライセンスは STAC の license リンクをたどった先の本文。

- STAC API: `https://planetarycomputer.microsoft.com/api/stac/v1`、コレクション `hls2-s30` と `hls2-l30`。
- 中身は Landsat 8/9 の OLI と Sentinel-2A/2B/2C の MSI を、同じ 30m の Sentinel-2 MGRS 格子に揃えた地表反射率。1 アイテム = 1 回の撮影の MGRS タイル 1 枚。
- `hls2-s30` が Sentinel-2 由来、`hls2-l30` が Landsat 由来。どちらも temporal extent は `2020-01-01T00:00:00Z` から終わり無し、spatial extent は全球。
- 提供者は `hls2-s30` が ESA (producer)、LP DAAC (producer, licensor)、Microsoft (host)。`hls2-l30` は LP DAAC (producer, licensor) と Microsoft (host)。
- 置き場は Azure Blob の `hls2euwest`。
- planetarble (`configs/base/pipeline.yaml`) はこの 2 コレクションを `hls.collections` に指定し、`spectral_bands` を B02/B03/B04、`qa_asset_key` を Fmask、`target_zoom` を 10、`max_cloud` を 80.0 にしている。

同じ Planetary Computer の Sentinel-2 L2A は別項の [Sentinel-2 L2A (Planetary Computer)](../stac/sentinel-2-l2a-planetary-computer.md) にある。HLS は Sentinel-2 を 30m に落として Landsat と合わせたものなので、10m が要るなら向こうを見る。

## アセット (item_assets と 1 アイテムの実物)

| コレクション | item_assets の個数 | 中身 |
|---|---:|---|
| hls2-s30 | 18 | B01-B12、B8A、SAA、SZA、VAA、VZA、Fmask |
| hls2-l30 | 15 | B01-B07、B09、B10、B11、SAA、SZA、VAA、VZA、Fmask |

分光バンドの並びが 2 つのコレクションで違う。planetarble が使う B02/B03/B04 と Fmask はどちらにもある。

1 アイテム (HLS.L30.T54SVE.2026240T011542.v2.0、2026-08-28、Landsat 9) の Blob 上のアセットの大きさ。署名付き URL への HEAD の Content-Length。

| アセット | バイト数 |
|---|---:|
| B05 | 24,183,467 |
| B01 | 23,853,280 |
| B02 | 23,818,905 |
| B04 | 23,734,162 |
| B03 | 23,676,265 |
| B06 | 22,474,434 |
| B07 | 22,175,537 |
| B10 | 18,625,543 |
| B11 | 18,444,700 |
| B09 | 18,307,510 |
| VAA | 1,815,675 |
| Fmask | 1,463,407 |
| VZA | 841,770 |
| SAA | 787,819 |
| SZA | 702,035 |
| thumbnail | 175,219 |
| 合計 (Blob 上の 16 個) | 225,079,728 |

- `proj:epsg` は 32654 (UTM 54N)、`proj:shape` は 3660 x 3660、`proj:transform` の画素サイズは 30.0 m。
- `processing:software` は `{"Cloud Masking": "Fmask v5.0.1", "Atmospheric Correction": "LaSRC v3.5.1.0"}`。
- B04 の Last-Modified は 2026-09-01 20:15:18 GMT。

## 東京付近の 1 か月分 (bbox 139.56,35.52,139.92,35.82、2026-08-01 から 2026-08-31)

無認証の POST `/search` が HTTP 200 で 20 件。内訳は `hls2-l30` 11 件、`hls2-s30` 9 件。

- 撮影日は 8/3、8/4 (3 件)、8/9 (2)、8/11 (2)、8/12 (2)、8/14 (2)、8/19 (3)、8/20 (2)、8/28 (2)。
- 衛星は landsat-8、landsat-9、sentinel-2a、sentinel-2b、sentinel-2c の 5 機。
- `eo:cloud_cover` は 36.0 から 100.0。50 未満は 2 件だけ (8/20 の L30 が 36.0、8/19 の S30 が 45.0)。
- レスポンスに `numberMatched` も `context` も無い。件数はページを数えるしかない。

## 取り出し方

catalog。副次的に range。

- STAC 検索は認証なしで通る。`POST https://planetarycomputer.microsoft.com/api/stac/v1/search` に上記の bbox と datetime を投げて HTTP 200、20 件が返った。トークンもヘッダも付けていない。
- `collections/hls2-s30/queryables` は 5 項目 (`datetime`、`end_datetime`、`geometry`、`id`、`start_datetime`) しか宣言しない。それでも `query` に `{"eo:cloud_cover": {"lt": 50}}` を入れた検索は HTTP 200 で 1 件を返した。queryables の宣言は実際に効く絞り込みより狭い。
- アセットの読み出しには SAS トークンの署名が要る。署名無しで `https://hls2euwest.blob.core.windows.net/hls2/L30/54/S/VE/2026/08/28/HLS.L30.T54SVE.2026240T011542.v2.0/HLS.L30.T54SVE.2026240T011542.v2.0.B04.tif` に `Range: bytes=0-1023` を投げると HTTP 409、本文は 248 バイトの XML で `PublicAccessNotPermitted` (`Public access is not permitted on this storage account.`)。Sentinel-2 L2A と同じ挙動で、署名を飛ばすと 1 バイトも読めない。
- トークンは `GET https://planetarycomputer.microsoft.com/api/sas/v1/token/hls2-l30` が認証無しで HTTP 200 を返す。08:37 UTC に取った応答の `msft:expiry` は 2026-09-30T09:22:04Z で、有効期間は約 45 分。
- 署名後は同じ URL に `?` + token を付けて Range 要求が HTTP 206、1,024 バイトが返る。先頭は `II*\0` でオフセット 192 に IFD、その前に COG のゴーストヘッダ `GDAL_STRUCTURAL_METADATA_SIZE=000140 bytes` / `LAYOUT=IFDS_BEFORE_DATA` / `BLOCK_ORDER=ROW_MAJOR` が入っている。索引がファイル先頭にあるので窓読みができる。
- コレクション自体に `geoparquet-items` というアセットがあり、href は `abfs://items/hls2-s30.parquet`、`msft:partition_info` は `{"is_partitioned": true, "partition_frequency": "W-MON"}`。アイテムのメタデータを週単位の Parquet でまとめて引く経路。今回は abfs の読み出しは試していない (未確認)。

## ライセンス

STAC のコレクションの `license` は `proprietary`。license リンクは `https://lpdaac.usgs.gov/data/data-citation-and-policies/` で、今日たどると `https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance` に 200 でリダイレクトされる。CMR (`https://cmr.earthdata.nasa.gov/search/collections.umm_json?short_name=HLSS30&version=2.0`) の `UseConstraints` も `https://earthdata.nasa.gov/earth-observation-data/data-use-policy` を指していて、同じページに行き着く。HLSS30 も HLSL30 も `AccessConstraints` は null。

そのページの本文。

> ESDIS content that is subject to usage restrictions, such as a license agreement, shall be labeled as such and the use of that data shall be in accordance with the designated license. Unless the content is marked with a use restriction or license, data provided from a NASA-led mission are licensed as Creative Commons Zero (CC0). While there are no restrictions on the use of these data, data users are very strongly urged to cite the data used in their work products.

同じページに、NASA 以外が出した部分は別だと書いてある。

> Non-NASA data available through the ESDIS project is subject to the license arrangements of the sponsoring organization. Users are encouraged to validate the source and associated use permissions.

読み取れること。NASA が主導した観測については CC0 で、引用は強く勧められるが義務ではない。ただし「印が無ければ」という条件付きの既定値であって、データセットごとに CC0 と明記されているわけではない。

合成物としての注意。`hls2-s30` は ESA の Sentinel-2 MSI が元で、STAC の providers も ESA を producer に挙げている。NASA が作ったのは調和処理の部分で、入力は NASA-led mission ではない。上の一文をそのまま当てると、S30 の側には Copernicus 側の条件が付いて回ると読める。Copernicus の条件そのものは今回読めていない (未確認。[Sentinel-2 L2A の項](../stac/sentinel-2-l2a-planetary-computer.md) にも同じ未確認が記録されている)。`hls2-l30` の側は Landsat が元で、そちらは [landsat-c2-l2 の項](../landsat-c2-l2/README.md) にある USGS の「制限なし」に当たる。

Planetary Computer 自体の利用規約 (`https://planetarycomputer.microsoft.com/terms`) は JavaScript で描くページで、curl では本文が取れなかった (未確認)。

## 気をつけること

planetarble の README は「NASA/USGS public domain」でひとまとめにするが、HLS の半分は ESA の Sentinel-2 が入力で、NASA の文言はそこを明示的に除外している。全体を public domain と言い切るなら S30 を外すか、Copernicus の条件を確かめる必要がある。

STAC の `license` が `proprietary` のままなのも、ライセンスを機械的に読む処理では引っかかる。`proprietary` は「SPDX の識別子に当てはまらない」の意味で使われていて、CC0 という結論とは食い違う。

署名を飛ばすと 409 で止まる。planetarble の process 段階が「SAS-signed HLS scene manifest」を作るのはこのため。トークンの寿命は約 45 分なので、1.6 TB から 2.0 TB を流す長い処理 (planetarble の README の見積り) の途中で必ず切れる。取り直しの経路を持たない実装は途中で落ちる。

`queryables` が 5 項目しか宣言しないのに `eo:cloud_cover` の絞り込みは通る。queryables を見て「雲量では絞れない」と判断すると、全件取ってから手元で捨てる無駄な実装になる。逆に、宣言に無い項目に頼るので、将来黙って効かなくなる可能性もある。

東京の 2026 年 8 月は 20 件中 18 件が雲量 50 以上だった。`max_cloud: 80.0` という既定は、この地域この季節では緩すぎて雲を通す。

30m という実効解像度は Web Mercator の z11 相当で、planetarble の README も同じことを書いている。z12 以上は z11 の引き伸ばしであって新しい情報ではない。

`hls2-l30` には B08 も B12 も B8A も無い。S30 と L30 をまたいで同じバンド番号で処理を書くと、L30 で欠ける。バンド番号は衛星をまたいで調和されているが、揃っているのは共通部分だけ。

## 学習ステップでの使いどころ (案)

- 1 ロジスティック回帰、2 Random Forest、3 XGBoost: B02/B03/B04 と NDVI などを特徴量にした土地被覆分類。Fmask を雲の教師ラベルにする練習もできる。
- 4 Cross Validation: 同じ MGRS タイルの別の日を訓練と検証に分けると、空間的にほぼ同じ画素なのでリークする。日付分割と空間ブロック分割の差を見る題材。
- 6 PCA: S30 の 13 バンドは強く相関する。主成分いくつで説明できるかを見る。
- 12 多目的最適化: 雲量の少なさ、撮影日の新しさ、季節の窓 (planetarble は北半球 4 月から 10 月、南半球 10 月から 4 月) の 3 つを天秤にかけてシーンを選ぶ。
- 1 アイテムは全アセットで約 225MB。COG の窓読みで必要な範囲だけを引く。トークンは約 45 分で切れるので長い処理では取り直す。
