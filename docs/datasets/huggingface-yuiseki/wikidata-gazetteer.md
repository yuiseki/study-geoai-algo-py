# wikidata-gazetteer

2026-09-28 に読んで確かめた内容。

- `https://huggingface.co/datasets/yuiseki/wikidata-gazetteer`
- 位置を持つ Wikidata の項目 (P625 座標 か P1566 GeoNames ID を持つもの) を、場所の表 `places` と名前の表 `names` の 2 つにしたもの。集落だけでなく山、通り、川、建物、学校なども入る。
- 作ったコード: `https://github.com/yuiseki/wikidata-gazetteer` (Apache-2.0)。

## 元データと基準日

- Wikidata の JSON ダンプ `wikidata-20260831-all.json.bz2` (102,943,257,005 バイト、`provenance.yaml` による)。基準日 2026-08-31。
- `provenance.yaml` の `built` は 2026-09-17。Hugging Face の最終更新は 2026-09-21。

## ファイル (API の tree で確認)

| パス | 大きさ (バイト) | 行数 (フッター) | 行グループ |
|---|---|---|---|
| `places.parquet` | 354,951,517 | 12,205,328 | 25 |
| `names.parquet` | 508,418,581 | 62,506,107 | 126 |
| `LICENSE`, `README.md`, `provenance.yaml` | 593 / 8,158 / 3,183 | | |

- 行数はカードの 12,205,328 と 62,506,107 に一致する。
- どちらも 50MB を超えるので丸ごとは落としていない。DuckDB 1.5.5 で必要な列だけを読んだ。

## 列

`places` (1 場所 1 行):

| 列 | 型 | 中身 (カードの説明) |
|---|---|---|
| `qid` | VARCHAR | Wikidata の ID |
| `lat`, `lon` | DOUBLE | P625 |
| `country` | VARCHAR | P17 の最初の値 (Q ID) |
| `parent` | VARCHAR | P131 の最初の値 |
| `instance_of` | LIST(VARCHAR) | P31 の全部 |
| `located_in` | LIST(VARCHAR) | P131 の全部 |
| `geonames_id` | VARCHAR | P1566 |
| `osm_relation` | VARCHAR | P402 |
| `capital` | VARCHAR | P36 |
| `iso_3166_2` | VARCHAR | P300 |
| `contains` | LIST(VARCHAR) | P150 の全部 |
| `population` | DOUBLE | P1082 |
| `area` | DOUBLE | P2046 |
| `sitelinks` | INTEGER | Wikipedia の記事数 |
| `n_names` | INTEGER | `names` の行数 |

`names` (1 名前 1 行): `qid`, `lang`, `name`, `kind` (すべて VARCHAR。`kind` は `label` か `alias`)。

国、親、種類はどれも Q ID のままで、名前は `names` を引かないとわからない。

## 実測 (2026-09-28)

`places`:

- 座標が NULL の行 71,552 (フッターの統計)。座標ありは 12,133,776 で、カードと一致する。
- 緯度の範囲 -90 から 351.368411、経度の範囲 -360 から 360。経度が ±180 を超える行 3,677、緯度が ±90 を超える行 4、`(0, 0)` の行 32。
- ±180 を超える例は `Q24227` (-14.47, 351.83)、`Q219269` (65.9, -236.4) など。どれも `country` が空で、`instance_of` の先頭が `Q55818` (衝突クレーター) などの天体上の地形と見える (Q ID の意味は未確認)。
- `country` の上位 (Q ID): Q30 1,320,385, Q183 962,729, Q145 824,177, Q142 700,572, Q16 423,196, Q159 417,769, Q668 417,448, Q29 415,503, Q252 399,183, Q20 384,000。
- `sitelinks`: 最大 428、中央値 1、1 以上は 7,374,883 (カードの 60.4% と一致)。
- `population`: 値あり 827,694 (カードと一致)、最大 8,117,059,282、負の値 0。
- `area`: 最大 25,000,000,000,000、0 以下 1,106。
- `n_names`: 最大 1,115、0 の行 2,669。
- `geonames_id` が数字だけでない行 14、`osm_relation` が数字だけでない行 34。例: `geonames_id` に `Reit   Schöllnach` や `27.525872,41.674833`、`osm_relation` に `node 12724375082`、`Q7570048`、`八条用水`、`30.9838`。

`names`:

- `lang` の種類 553。`kind` は `label` 54,121,136、`alias` 8,384,971。
- `lang` の上位: en 11,220,242, ceb 3,514,525, nl 3,210,573, fr 3,186,376, de 3,077,615, sv 2,207,820, es 1,831,360, tr 1,244,593, id 1,141,000, ru 1,097,255。

## ライセンス

- カードとタグは `cc0-1.0`。`LICENSE` は Wikidata の CC0 1.0 を引き継ぐと書き、選択と配列に生じうる権利も CC0 で放棄するとする。

## 気づいた異常

- 地球の座標としてあり得ない値がある (緯度 351.37、経度 -360 から 360)。天体上の地形らしい項目が混ざっていて、P625 の globe (どの天体か) の列が無いので区別できない。地球だけにするなら `abs(lat) <= 90 and abs(lon) <= 180` で落とすか、`instance_of` で除く。ただし 0 から 360 の範囲に収まる天体の座標はこの条件では落ちない。
- `geonames_id` と `osm_relation` に ID でない値が混ざる (上記 14 行と 34 行)。Wikidata 側の入力の誤りをそのまま持ってきたと見える。
- `area` の最大 2.5e13 はどの単位でも地球上の場所として大きすぎる。単位の揃え方はカードに書かれていない (未確認)。
- `n_names` が 0 の場所 2,669。
- `lang` の種類が実測 553 で、カードと `provenance.yaml` の 552 と 1 つずれる。
- カードが書くとおり、言語 (729 件) と組織 (約 36,000 件) が場所として入っている。除くための `instance_of` の一覧がカードにある。

## 他のデータとの関係

- `wikipedia-geotagged` と `wikivoyage-geotagged` の `qid` を結合する先。場所かどうかの判定、国、人口を足すのに使う。
- `z-yuiseki-static/wikimedia.md` の重要度表とも Wikidata ID で結合できる見込み (未確認)。`sitelinks` は知名度の別の指標になる。
- `osm_relation` と `geonames_id` で OSM と GeoNames に繋がる (ただし上記の汚れた値がある)。

## 12 ステップでの使い道 (案)

- 5 k-means / DBSCAN: 1,200 万点は大きいので、国か種類 (山、湖など) で絞って点をクラスタリングする。
- 1 回帰, 3 Gradient Boosting: `population` (値ありは 82 万件) を `sitelinks`, `n_names`, `area`, 種類から当てる。裾が重いので対数を取る練習になる。`sitelinks` を目的変数にしてもよい。
- 2 Random Forest: 座標と名前の数から `instance_of` の大分類 (山、川、集落など) を当てる分類。
- 4 データリーク: 親 (都市) と子 (区) が別の行として入っているので、ランダムに分けると `located_in` の親子が学習と検証に割れる。親で分割する練習になる。
- 6 PCA: 国ごとに種類の件数を並べた表を作って次元を減らす。
- 7 Dijkstra: `located_in` を辺にしたグラフで階層を辿る (距離ではなく木の探索)。
- 9 facility location: 候補地 (学校、病院など) と需要点 (集落と人口) を一つの表から取り出せる。
