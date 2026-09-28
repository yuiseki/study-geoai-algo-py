# osm-tokyo23-questions

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/osm-tokyo23-questions/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/osm-tokyo23-questions`
- 東京 23 区について人が書いた英語の質問 215 問。答えは入っていない (答えは osm-tokyo23-qa-2026-08 にある)。
- 最終更新 2026-09-23。GitHub は `yuiseki/osm-tokyo23-questions`。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| data/train-00000-of-00001.parquet | 26,498 | 質問 215 行 |
| tag_hints.jsonl | 24,310 | 質問ごとの OSM タグの手がかり (215 行) |
| provenance.yaml | 3,177 | 質問の出どころと確かめた相手 |
| LICENSE | 2,978 | ODbL の表示 |

## 行数と列

全体をダウンロードして DuckDB 1.5.5 で集計した。

- 215 行、`id` は 215 種類で重複なし。
- 列は 30 個、すべて VARCHAR: `id` `origin` `region` `question` `template` `type` `level` `source` `template_file` `checked` と、スロットの値 (`place` `place_1` `place_2` `target` `category` `neighbour` `neighbour_1` `neighbour_2` `brand` `brand_1` `brand_2` `operator` `radius` `radius_1` `radius_2` `outer_radius` `inner_radius` `area` `count` `name`)。スロットは、その質問のテンプレートが使うものだけに値が入る。
- `origin`: filled 174、written 41。
- `type` は 20 種類: nearest_neighbor 16、distance 14、range_count 14、attribute_lookup 14、multi_criteria_filter 13、bearing 12、multi_criteria_rank 12、nearest_brand_compare 12、radius_sensitivity 12、area_compare 11、area_rank 11、containment_count 11、containment_rank 11、existence 11、radius_sensitivity_compare 11、neighbour_count_rank 11、length_total 9、name_count 7、distance_definition_sensitivity 2、anchor_sensitivity 1。カードの表と一致した。
- `level` が入っているのは 34 行 (1: 5、2: 12、3: 6、4: 5、5: 6)。カードの「最初の 34 問」と合う。
- filled の質問が使うテンプレートは、`template` の文字列でも `template_file` でも 18 種類。
- `checked` は値が 1 種類で `tokyo23-260831.osm.pbf md5 44a4ba2182379c147f20a27ad1b513ef, osm_base 2026-08-30T23:50:59Z`、残りは NULL。

## 元データと基準日

- 質問を確かめた相手は osm-tokyo23-src-2026-08 の `tokyo23-260831.osm.pbf` (2026-08-31 の planet から切り出したもの)。provenance.yaml によると、確かめたのは filled の 174 問で、written の 41 問は確かめていない。
- 地名、ブランド名、事業者名は OSM から読んだもの。
- osm-tokyo23-qa-2026-08 の 215 行と `id` も `question` の文も 215 行すべて一致した。

## ライセンス

- カードとタグ: `odbl` (ODbL 1.0)。

## 気づいたこと

- カードの「Where the questions come from」節は「174 were filled from 38 templates」と書いているが、実物の filled 174 問が使うテンプレートは 18 種類。provenance.yaml は「the eighteen types that have a template」と書いており、こちらと合う。38 がリポジトリ側の別の数え方なのかは確かめていない。
- osm-tokyo23-src-2026-08 のカードはこのデータセットを 131 問と書いているが、実物は 215 問。

## 12 ステップでの使いどころ (案)

- 答えも数値も入っていない英語の質問文なので、12 ステップの学習データには使えない。
- 使うとすれば、osm-tokyo23-src-2026-08 で分析を組むときの問いの例として。例えば `nearest_neighbor` や `distance` は 7 (Dijkstra/A*) の練習問題の種になる。
