# geo-triples-tokyo23

2026-09-28 に読んで確かめた内容。

- <https://huggingface.co/datasets/yuiseki/geo-triples-tokyo23>
- 東京 23 区と区内の場所 (POI 7,265) を、Natural Earth の国 (admin-0) と一次行政区画 (admin-1) と一緒に比べた空間関係の三つ組、その文、評価問題。geo-triples 系で最初に作られたもの (schema_version 4)。
- 入力は manifest.json の sources で、osm-tokyo23-src-2026-08 (コミット e60e017) の tokyo23 23 件と tokyo23-poi 7,265 件、ne-admin0-10m (コミット d1d37a1) の ne-admin0 258 件と ne-admin1 4,596 件。
- 最終更新 2026-09-25。

## ファイル

どれも小さいので全体をダウンロードして DuckDB 1.5.5 で読んだ。

| ファイル | 大きさ (バイト) | 行数 |
|---|---|---|
| data/triples.parquet | 2,243,598 | 510,616 |
| data/cpt.parquet | 5,426,032 | 483,922 |
| data/probe.parquet | 282,967 | 8,854 |
| data/manifest.json | 4,209 | |
| vendor/de9im_sf_verdicts.tsv | 7,374 | |

## 列

- triples: geo-triples-japan と同じ 25 列 (subject_* / object_*、predicate、truth、de9im、rcc8、derivation、via_*、outside_ratio、certification など)。
- cpt: text、form (ntriples / ja / en) ほか。
- probe (12 列): child / parent の id・iri・en・ja、level、child_layer、parent_layer、rcc8。geo-triples-japan や jp-gov と違い split と answer_in_child_* の列は無い。

## 中身

- triples: true 202,116。observed 411,488 行 (= 51,436 組 × 8)、composition 99,128 行。
- 主語に出る地物: tokyo23 23、tokyo23-poi 7,252、ne-admin1 4,596、ne-admin0 255。
- observed の組を層で分けると、ne-admin1 どうし 21,946 組、ne-admin0 と ne-admin1 6,920 組ずつ、区と POI 7,371 組ずつ、ne-admin0 どうし 688 組、区どうし 114 組など。
- 23 区どうしの sfTouches (true) は 114 (向き付き)、無向の辺にすると 57。
- cpt の form 別: ntriples 202,116、ja 150,666、en 131,140。
- probe の level: place-in-ward 6,157、state-in-country 2,680、ward-in-state 17。

## 気をつけること (カードと実物の食い違い)

- カードの本文は triples を「346,256 rows: 126,208 true and 220,048 false」「eight rows per pair, 293,552 in all」と書いているが、実物は 510,616 行 (true 202,116、false 308,500)、observed 411,488 行。冒頭の段落の 510,616 と manifest は実物と一致するので、本文の数が古いと思われる。
- probe の件数はカード冒頭が 8,890、本文と実物が 8,854。
- ward-in-state は表と実物で 17 問だが、本文には「16 questions」とある。
- カードの YAML の件数区分は 100K-1M、Hugging Face のタグは 1M-10M。
- カードによると、Natural Earth の admin-0 と admin-1 は海岸線の頂点が食い違うため、日本の 47 都道府県のうち幾何的に日本の内側 (within) になるのは 21 だけ。state-in-country の答えは幾何ではなく属性から決めている。幾何の関係を真値として使うなら、この層の組は疑ってかかる。

## ライセンス

- Hugging Face のタグは odbl。OpenStreetMap 由来の層があるので全体が ODbL-1.0。Natural Earth の層はパブリックドメインだが、混ぜたものは ODbL になる。

## 12 ステップで使えそうな場面 (案)

- LLM 向けの文と評価問題が主。表形式の機械学習には向かない。
- 7 Dijkstra/A*: 23 区の隣接 (57 辺) は手で確かめられる大きさの最短経路の練習グラフになる。
- 10 CP-SAT: 23 区の地図の塗り分けを解く最小の例にちょうどよい。
- 9 assignment: POI (区ごとの所属が分かる) を区の中の施設に割り当てる練習の下敷きには使えるが、POI の座標はこの表に無いので osm-tokyo23-src-2026-08 から取る。
