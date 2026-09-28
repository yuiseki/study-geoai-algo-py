# xing

2026-09-28 に読んで確かめた内容。

- `https://source.coop/smartmaps/xing` (Web ページの題は「Vector Tiles and 3D Tiles from Project PLATEAU」)
- データの URL は `https://data.source.coop/smartmaps/xing/<データセット名>/...`
- 直下に `README.md` (270 バイト) と `index.html` (3,202 バイト、CesiumJS のビューア) がある

## 何のデータか

国土交通省 Project PLATEAU の 3D 都市モデルを、3D Tiles (b3dm) とベクトルタイル (mvt) にしたものを置いた場所。

- README の出典は「3D都市モデル（Project PLATEAU）ポータルサイト」(`https://www.geospatial.jp/ckan/dataset/plateau`)。方針として「標準製品仕様書V3に対応したデータのみを収録することにします」とある。
- index.html は `?cid=<データセット名>` で `xing/<cid>/tileset.json` を CesiumJS に読み込む。クレジット表示は「国土交通省 with UN Smart Maps」。
- Web ページの作成日は 2024-11-21、最終更新は 2025-08-21。数えた範囲のファイルの更新日時はすべて 2024-11-21。

## 形式と大きさ

`delimiter=/` の一覧で、直下のデータセット (ディレクトリ) は 6,419 個、直下のファイルは 2 個 (README.md、index.html) だった。

ファイルの件数は continuation-token をたどって 58.7 秒で 58,000 個 (14,093,206,313 バイト) まで数えて打ち切った。進んだのは 6,419 データセットのうち先頭 37 個 (札幌市のもの) で、37 個目 (`..._toyohiragawa_3dtiles_l2`) は途中。

- 合計は 58,002 ファイル以上、14.09GB 以上。全体の件数は 60 秒では数えきれなかった。
- 数えた 58,000 個の内訳は b3dm 57,964、json (tileset.json) 36。b3dm は最小 2,604 バイト、中央値 49,712 バイト、最大 62,168,856 バイト。0 バイトは無かった。
- mvt は数えた範囲に入っていないが、mvt のデータセットの中を別に見て存在を確かめた。

### データセット名の規則

多くは PLATEAU の配布名の形 `<市区町村コード 5 桁>_<名前>_<city|pref>_<年度>_citygml_<版>_op_<地物>_<形式>_<LOD など>`。例 `01100_sapporo-shi_city_2020_citygml_6_op_bldg_3dtiles_01101_chuo-ku_lod2`。

6,419 個の名前から数えたこと:

- 市区町村コードの先頭 5 桁は 200 種類、都道府県コードの先頭 2 桁は 37 種類。
- 年度は 2023: 4,150、2022: 1,396、2020: 865、2021: 2、読み取れないもの 6。
- 形式は 3dtiles を含む名前 4,699、mvt を含む名前 1,719 (両方を含む `3dtiles-mvt` 6 個を両方に数えた)、どちらも含まないもの 7。
- 地物の種類 (`_op_` の後) は fld (洪水浸水想定) 2,812、urf (都市計画) 1,042、bldg (建物) 748、tran (道路) 280、luse (土地利用) 181、tnm (津波) 156、lsld (土砂災害) 120、veg (植生) 98、htd (高潮) 86 など。`_op_` を含まない名前が 533 個ある。
- `_no_texture` で終わるもの 1,965 個 (テクスチャ付きと無しの 2 組で置かれている)。

### 中の並び

- 3D Tiles: `<データセット>/tileset.json` と `<データセット>/data/data<番号>.b3dm`、または `data/<階層>/data<番号>.b3dm`。
- 2022 年度の `..._3dtiles-mvt_1_op` は 1 段深く、`01205_muroran-shi_2022_3dtiles-mvt_1_op/bldg_lod1/data/data0.b3dm` のように地物ごとのサブディレクトリがある。
- mvt: `<データセット>/<z>/<x>/<y>.mvt`。例 `01100_sapporo-shi_city_2020_citygml_6_op_urf_UseDistrict_mvt_lod1/10/913/375.mvt`。1 個読んだ mvt は gzip されておらず、レイヤ名は `UseDistrict`、Content-Type は application/octet-stream。

## 中身

### tileset.json

`01100_sapporo-shi_city_2020_citygml_6_op_bldg_3dtiles_01101_chuo-ku_lod2/tileset.json` (107,646 バイト) を読んだ。

- `asset.version` 1.0、`geometricError` 365.34、`refine` REPLACE。境界は `region`。
- ノード 176 個 (深さ 0 から 4)。region の合計範囲は 東経 141.2483 から 141.3884、北緯 43.0133 から 43.0845、高さ 39.87m から 510.85m (札幌市中央区)。
- `properties` に属性の最小と最大がある。例 `bldg:yearOfConstruction` 1878 から 2019、`bldg:measuredHeight` 2 から 173.9、`bldg:storeysAboveGround` 1 から 38、`uro:BuildingDetailAttribute_uro:totalFloorArea` 1 から 275,840。

### b3dm

同じデータセットの `data/data175.b3dm` (169,924 バイト) を全体ダウンロードして読んだ。

- magic `b3dm`、version 1。feature table JSON 20 バイト、feature table バイナリ 0、batch table JSON 71,208 バイト、batch table バイナリ 1,432 バイト。その後に glTF (`glTF` の magic を確認)。
- feature table は `{"BATCH_LENGTH": 19}` (建物 19 棟)。
- batch table に建物ごとの属性がある。主なもの: `gml_id`, `meshcode`, `city_code`, `city_name`, `bldg:class` (例 堅ろう建物), `bldg:usage` (例 共同住宅、商業施設), `bldg:yearOfConstruction`, `bldg:measuredHeight`, `bldg:storeysAboveGround`, `bldg:storeysBelowGround`, 敷地面積、延床面積、建築面積、構造種別、耐火構造種別、用途地域、指定建ぺい率、指定容積率、調査年、不動産 ID とその照合スコア、洪水浸水想定のランク。
- `attributes` 列には CityGML 由来の入れ子の属性が丸ごと入っている (洪水の想定浸水深 `uro:depth` など)。
- 値が欠けている建物がある (19 棟の先頭 3 棟のうち 1 棟は用途、建築年、階数が null)。

## 気づいた異常

- 札幌市中央区の `..._lod2` と `..._lod3` は中身が同じに見える。tileset.json はバイト単位で一致、b3dm は 177 個すべてで大きさが一致し、`data/data175.b3dm` は md5 も一致した。`_no_texture` の組も 177 個の大きさが一致した。
- 同じ市区町村コード 15222 に `joestu-shi` と `joetsu-shi` の 2 つの綴りがある (`15222_joestu-shi_city_2023_citygml_1_lsld_mvt` と `15222_joetsu-shi_city_2023_citygml_1_op_bldg_3dtiles_lod1`)。上流の配布名がそうなっているのかは確かめていない。
- 名前の揺れ: `lod3.0` で終わるもの (`13999_tokyo_mlit_2023_...`) が 7 個、`_op_` を含まないもの (`11243_yoshikawa-shi_pref_2023_citygml_1_fld_...`、`..._lsld_mvt` など) が 533 個。
- `07205_shirakawa-shi_2020_citygml_5_op/` はタイルではなく、CityGML の配布物 (`codelists/*.xml`、`07205_indexmap_op.pdf` 2,034,630 バイト) がそのまま置かれているように見える (先頭 8 件を見た)。
- `..._dm_geometric_attributes` (つくば市、長岡市) の 6 個は名前に形式を含まない。そのうち `08220_tsukuba-shi_city_2023_citygml_1_op_brid_dm_geometric_attributes` の先頭 8 件は mvt だった。
- README は「標準製品仕様書V3 対応のみ」とするが、2020 年度や 2021 年度のデータセットが V3 に対応しているかは確かめていない。
- 札幌市北区は lod1 が 164 ファイル、lod2 が 531 ファイルで、同じ区でも LOD によってタイル分割が違う。
- S3 一覧の `start-after` は当てにならない。数えた範囲の末尾から 11 件手前のキーを `start-after` に渡すと 0 件が返った。件数は continuation-token だけでたどること。

## ライセンス

未確認。README と source.coop の Web ページにはライセンスの記載が無かった。PLATEAU 側の利用条件は今回読んでいない。

## 12 ステップでの使い道 (案)

建物の b3dm の batch table は、そのまま表形式の特徴量になる。glTF の形状を読まなくても使える。

- 1 線形回帰: 地上階数から `bldg:measuredHeight` を予測する。延床面積と建築面積から階数を推定する。
- 2 Random Forest、3 XGBoost: 高さ、面積、建築年、用途地域から建物用途 (`bldg:usage`) を分類する。
- 4 Cross Validation とデータリーク: 同じ敷地や同じタイルの建物は似るので、区やタイル単位で分ける。lod2 と lod3 のように中身が同じデータセットがあるので、別のデータセットを評価用にしても実は同じ建物、ということが起こる。
- 11 SHAP/calibration: 洪水浸水ランクの分類モデルで、効いている属性を SHAP で見る。確率の較正も試せる。
- 9 facility location: 建物の位置と延床面積を需要点にして、避難所や店舗の配置を解く。洪水浸水深で制約を付けられる。
- 12 多目的最適化: 浸水リスクと移動距離の両方を目的にした配置。
- mvt の都市計画 (用途地域など) は、建物の属性と空間結合して特徴量を増やすのに使える。
