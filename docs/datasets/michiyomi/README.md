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

## 取り出し方

区分は range。分割の単位としては split (区市町村ごとに 63 ファイル) を、
座標での絞り込みには catalog に近い API を併せ持つ。2026-09-30 に実測した。

### Hugging Face の Parquet は range で、転送先でも Range が生きる

`https://huggingface.co/datasets/finalvent/michiyomi-tokyo-streetscape/resolve/main/data/scenes/taito.parquet` で確かめた。

この URL は 302 で `https://us.aws.cdn.hf.co/xet-bridge-us/...` (署名付きの CDN) へ飛ぶ。
飛ぶ前の応答には `x-linked-size: 59739579` が付いていて、飛んだ先は 200、Content-Length 59,739,579、`Accept-Ranges: bytes`。

| 確かめたこと | 結果 |
|---|---|
| `curl -L -r 0-1023` | 206、1,024 バイト |
| `curl -L -r -8` | 206、8 バイト |
| 末尾 8 バイト | `5b 79 00 00 50 41 52 31` |
| 末尾 4 バイト | `PAR1` |
| フッターの長さ | 31,067 バイト |
| フッター本体 `bytes=59708504-59739570` | 206、31,067 バイト |

転送をまたいでも Range は生きている。`resolve` の URL に Range を付けたまま `curl -L` を投げれば、CDN 側が 206 を返す。

Parquet のフッターはファイルの末尾にあるので、先頭を読んでも索引は得られない。
末尾を引いて長さを知り、そこから戻ってフッターを読む、という 2 段の往復が要る。

pyarrow 20.0.0 に Range 要求だけを出す読み取り器を渡して、要求の回数を数えた。
台東区のファイルから `lat`、`lon`、`capture_year` の 3 列を最初の行グループ分だけ読んだ結果:

- 要求は合計 4 回。1 回目が末尾 65,536 バイト (フッター 31,067 バイトがこの中に収まる)、残り 3 回が 3 つの列の塊。
- 流れたのは 413,268 バイト、5.4 秒。ファイル全体 59,739,579 バイトの 0.7%。
- 3 行グループ、1 つ 20,000 行。55,044 行のうち最初の 20,000 行が読めた。

列の数だけ要求が増える。49 列のうち重いのは `analysis` (VLM の解釈を入れた JSON 文字列) なので、
そこを読まない限り、台東区の位置と撮影年だけなら 0.4MB で足りる。

### split の面

`https://huggingface.co/api/datasets/finalvent/michiyomi-tokyo-streetscape/tree/main/data/scenes` は
ログイン無しで 200 を返し、63 個のファイルが並ぶ。区市町村ごとに 1 本で、大きさは足立区 45,012,941 バイト、
あきる野市 6,976,906 バイト、昭島市 9,795,692 バイトなど。
台東区だけが欲しければ `taito.parquet` の 1 本を選べばよく、他の 62 本には触らない。

### API は catalog に近い

`https://michiyomi.dev/v1/meta` はログイン無しで 200、4,381 バイト。
版 `2026-09-13-r1`、`released_total` 1,914,451、ライセンスと表示の要件、`sharding` (4 シャード、経度帯で振り分け) が返る。

`https://michiyomi.dev/v1/` の `endpoints` によると、座標で絞れるのは次のもの。

- `GET /v1/scenes/nearby`: lat と lon が必須。radius_m、limit、quality、generation、撮影年で絞れる。実際に
  `?lat=35.7148&lon=139.7967&limit=2` を投げると 200 と 3,085 バイトが返った。
- `GET /v1/amenities/nearby` と `POST /amenities/search`: 自販機、トイレ、ベンチの観測。
- `GET /v1/scenes/{id}`: 1 シーンの詳細。`include=` でメタデータ、決定論計算の特徴量、VLM の解釈を選べる。

bbox での絞り込みは無く、`?bbox=...` は `unknown endpoint` の 404 を返した。中心と半径で引く形になる。
STAC のような資産の目録ではないので catalog そのものではないが、「必要なものを選んでから引く」使い方はできる。

### まとめ

| 経路 | 区分 | 根拠 |
|---|---|---|
| Hugging Face の Parquet | range | 末尾 4 バイトが `PAR1`、3 列 1 行グループを 4 回の要求、413,268 バイトで読めた。転送先の CDN も 206 を返す |
| Hugging Face のリポジトリ | split (63 ファイル) | tree API が匿名で 200。区市町村ごとに 1 本 |
| `michiyomi.dev` の API | catalog に近い | `/v1/scenes/nearby` が lat/lon と半径で絞れる。bbox は無い |
| 画像そのもの | 対象外 | 配っておらず、`id` が Mapillary の画像 ID を指すだけ。Mapillary 側の取り出し方は 未確認 |
