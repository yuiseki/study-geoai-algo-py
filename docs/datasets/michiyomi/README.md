# みちよみ (michiyomi) 東京都 街路言語化オープンデータ

2026-09-28 に読んで確かめた内容。

- API の説明: <https://michiyomi.dev/docs/> (認証不要、read-only)
- 一括版: <https://huggingface.co/datasets/finalvent/michiyomi-tokyo-streetscape>
- 版: `2026-09-13-r1` (データ基準日 2026-09-13)

## 中身

Mapillary の公開街路画像を視覚言語モデル (VLM) で読み取り、写っている道の状態を構造化したもの。画像そのものは配っておらず、`id` が Mapillary の画像 ID になっている。

- 東京都全域で 1,914,451 シーン (API の `/v1/meta` の `released_total`)。23 区は複数年、多摩と島しょは最新年が中心。
- 1 シーンは「格子 × 撮影方向 × 年」の代表画像 1 枚。
- ほかに、同じ地点の経年変化 2,522 件と、小学校の位置 1,323 件がある。

一括版は Hugging Face に Parquet で 70 ファイル、合計 1.97GB。シーンは区市町村ごとに 1 ファイル (`data/scenes/taito.parquet` など)。

台東区のファイルは 55,044 行、撮影年は 1970〜2026。列は 49 あり、学習に使いやすいのは次のもの:

| 列 | 中身 | 性質 |
|---|---|---|
| lat, lon (raw_ と computed_ も) | 位置。computed は Mapillary の SfM 補正 | 観測 |
| capture_year, month, hour, season | 撮影時期 | 観測 |
| cell_250m | 250m 格子の ID | 観測 |
| sequence_id | 撮影の連続列の ID | 観測 |
| green_ratio, colorfulness, warm_ratio | 画像の緑の割合や色 | 決定論計算 |
| abs_objects | 絶対方位つきの物体 | 決定論計算 |
| analysis | VLM の解釈 (JSON 文字列) | 推定を含む |

`analysis` の中には、例えば次の値がある (1 件で確かめた):

- `geometry.roadway_width_m.value` (車道の幅、m) と `confidence`
- `geometry.sidewalk.left.presence` / `width_m` (歩道の有無と幅)
- `geometry.intersection.sight_distance` (交差点の見通し)
- `infrastructure.utilities.poles_visible` (見える電柱の数)、`undergrounded` (架空線か地中化か)、`wire_density`
- `infrastructure.lighting.lights_road` (道路照明の数)
- `pavement.surface`、`markings_wear` (標示の摩耗 %)

## 気をつけること

- ライセンスは CC BY-SA 4.0。表示には「© Mapillary contributors (CC BY-SA 4.0) を加工」と、国土数値情報 (A29、P29) と東京都建設局の緊急輸送道路の出典が要る。
  データを表示する UI には、Mapillary のロゴと <https://www.mapillary.com> へのリンクを見える形で出す必要がある (`/v1/meta` の `ui_requirements`)。
- `analysis` は VLM の推定で、正解ではない。値ごとに `confidence` や `evidence` が付くので、使うときは確からしさで絞る。どの層 (観測、計算、解釈) の値かを分けて扱う。
- 被覆は Mapillary の撮影がある場所に偏る。レコードが無いのは「収録が無い」だけで、「その地物が無い」ではない。
- 同じ地点に複数年のシーンがある (23 区)。ランダムに分けると同じ場所が train と test の両方に入る。

## 学習ステップとの対応 (案)

- 1〜3: `analysis` の値 (歩道の幅、電柱の数など) を目的変数にして、位置や人口、Overture の建物から予測する。逆に、これらを特徴量にもできる。
- 4: `cell_250m` や `sequence_id` を groups にした GroupKFold と、ランダム分割を比べる。同じ地点の複数年が漏れる典型例になる。
- 5: 電柱や街灯の多い地点を DBSCAN でまとめる。
- 9: 基地局の候補地として、電柱や街灯の位置を使う。KartaView の画像から物体検出する代わりになる。
- 11: VLM の `confidence` と実際の当たり方の関係を calibration として見る。
