# osm-tokyo23-qa-2026-08

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/osm-tokyo23-qa-2026-08/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/osm-tokyo23-qa-2026-08`
- osm-tokyo23-questions の 215 問に、osm-tokyo23-src-2026-08 から計算した答えと、それを出したクエリ (PostGIS の SQL、Overpass QL、DuckDB の SQL) を付けたもの。質問が曖昧なときに聞き返すべきかどうか (`response`) も入っている。
- 最終更新 2026-09-23。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| data/train-00000-of-00001.parquet | 400,699 | 答え 215 行 |
| provenance.yaml | 8,273 | 誰が何を書いたか、訂正の記録 |
| LICENSE | 1,546 | ODbL の表示 |

## 行数と列

全体をダウンロードして DuckDB 1.5.5 と Python の `json` で集計した。

- 215 行、`id` は 215 種類で重複なし。
- 列は 18 個、すべて VARCHAR: `id` `type` `question` `answer_kind` `response` `said` `unit` `ask` `agreement` `checked` と、JSON 文字列の `answer` `interpretations` `ambiguity` `engines` `osm` `on_the_edge` `queries` `record`。
- `response`: answer 190、ask 18、tie 6、out of scope 1。
- `answer_kind` と `response` の組: value/answer 179、ambiguous/answer 11、ambiguous/ask 18、ambiguous/tie 6、unanswerable/out of scope 1。カードの表と一致した。
- `agreement`: agree 182、agree within 0.1% 11、agree within 0.5% 9、one engine only 8、disagree only on what osm2pgsql loads 2、disagree only at the radius 2、disagree only at a boundary 1。
- `unit`: NULL 99、metres 25、features 25、yes or no 23、a list of features 13、compass point, of eight 12、square metres 11、stations 7。
- `answer` を JSON として読んだ型: 文字列 94、整数 25、null 24、小数 21、真偽値 21、リスト 19、辞書 11。
- `engines` のキーに現れた回数: postgis 210、overpass 175、duckdb 46。
- `record` (レコード全体の JSON) に現れるキーは 48 種類。
- `checked` は 1 種類: `tokyo23-260831.osm.pbf md5 44a4ba2182379c147f20a27ad1b513ef, osm_base 2026-08-30T23:50:59Z`。

## 元データと基準日

- 答えは osm-tokyo23-src-2026-08 の `tokyo23-260831.osm.pbf` (2026-08-31 の planet) から計算したもの。
- 質問は osm-tokyo23-questions。`id` と `question` の文は 215 行すべて一致した。
- provenance.yaml によると、答えは 2026-09-15 に計算し、09-16 に拡張、09-23 に訂正 (name_count の 7 問のうち 6 問を answer から ask に変更)。クエリと計測の決まりは Claude Code (claude-opus-5) が書いたとカードにある。

## ライセンス

- カードとタグ: `odbl` (ODbL 1.0)。カードの本文では、`queries` 列の SQL と Overpass QL はコードなので MIT としている。

## 気づいたこと

- カードは「forty-four fields appear across the set」と書いているが、`record` に現れるキーを数えると 48 種類だった。
- カードは「Three engines, asked separately」と書くが、`engines` に duckdb が入っているのは 46 行だけ。postgis は 210 行、overpass は 175 行。
- `answer` は同じ列に整数、小数、文字列、リスト、辞書が混ざる。表として使うには `type` ごとに分けて読む必要がある。

## 12 ステップでの使いどころ (案)

- 215 行の QA で、ほとんどは LLM の評価用。12 ステップの学習データとしては小さすぎ、形もばらばらなので使えない。
- 使うとすれば、osm-tokyo23-src-2026-08 で距離や近傍探索を自分で実装したときの答え合わせ。`type` が distance や nearest_neighbor の行には、答えとそれを出した SQL が付いている。ただしカードの決まりでは距離は 2 つの物の最も近い点どうしの測地線距離で、道路網上の距離ではない。7 (Dijkstra/A*) の答え合わせには直接は使えない。
