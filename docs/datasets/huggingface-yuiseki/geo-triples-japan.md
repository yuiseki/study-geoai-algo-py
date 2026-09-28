# geo-triples-japan

2026-09-28 に読んで確かめた内容。

- <https://huggingface.co/datasets/yuiseki/geo-triples-japan>
- 日本全国の OpenStreetMap から、国 1、都道府県 47、市区町村 1,740、Wikidata id を持つ場所 (POI) 80,748 の空間関係を三つ組にした表と、その文 (日本語・英語・N-Triples) と評価問題。geo-triples-jp-gov の ODbL 版にあたり、POI の層がある。
- 入力は osm-japan-src-2026-08 (コミット b51be03、2026-08-31 の planet から切り出し) の 4 層 (manifest.json の sources)。
- 最終更新 2026-09-26。schema_version 5。

## ファイル

| ファイル | 大きさ (バイト) | 行数 | 読み方 |
|---|---|---|---|
| data/triples.parquet | 21,566,951 | 3,286,232 | ダウンロードして全体を集計 |
| data/cpt.parquet | 62,516,508 | 4,678,910 | 50MB を超えるのでフッターだけ (行グループ 5) |
| data/probe.parquet | 2,068,267 | 68,025 | ダウンロードして集計 |
| data/manifest.json | 5,715 | | 件数と sha256 |
| vendor/de9im_sf_verdicts.tsv | 8,320 | | |

## 列

- triples (25 列): geo-triples-jp-gov と同じ形から rcc8_observed、reading、norm_method、norm_tolerance を除いたもの。subject_kind / object_kind が area か point。
- cpt (14 列): text、form、subject_id、predicate、object_id、derivation、via_id、de9im、rcc8、certification、certificate、holdout、topic、pair。
- probe: child / parent の id・iri・名前、level、split、answer_in_child_ja / _en など。

## 中身

- triples: true 2,053,684、false 1,232,548。observed 1,643,408 行 (= 205,426 組 × 8)、composition 1,642,824 行。
- 主語に出る地物: 国 1、都道府県 47、市区町村 1,740、POI 80,684 (area 43,670、point 37,014)。
- observed の組の RCC8: NTPP 50,736、NTPPi 50,736、EC 16,080、PO 7,014、TPP 3,350、TPPi 3,350、EQ 4、点を含むので空 74,156。カードの表と一致する。
- de9im が空の行 762,114 (比べていない組について合成表で導いた行。カードと一致)。
- 市区町村どうしの sfTouches (observed、true) は 9,844 (向き付き)。隣接を持つ市区町村は 1,735。
- probe: place-in-municipality 66,541 (train 59,885、eval 6,656)、municipality-in-prefecture 1,484 (全部 train)。
- cpt の form 別の行数 (manifest): ntriples 2,053,684、ja 1,848,010、en 777,216。held_out_features 8,121、held_out_rows 408,356。

## 気をつけること (カードと実物の食い違い)

- カードの冒頭の段落は「510,616 spatial triples, 483,922 text rows and 8,890 evaluation questions」と書いているが、これは geo-triples-tokyo23 の数。実物と本文の数は 3,286,232 / 4,678,910 / 68,025。
- カードの YAML の pretty_name が「Geo Triples Tokyo 23」のまま。
- タグに natural-earth があるが、manifest の入力は OpenStreetMap だけ。
- カードの「True triples, by predicate」の表で、observed と composed の割り振りが実物と違う。sfContains と sfWithin は カード 105,076 / 271,470、実物 91,044 / 285,502。sfTouches は カード 16,080 / 276、実物 16,328 / 28。合計 (376,546 と 16,356) はどちらも一致する。カードの observed 側は RCC8 で数えた値 (EC 16,080) のように見える。

## ライセンス

- Hugging Face のタグは odbl。入力がすべて OpenStreetMap なので、表も文も ODbL-1.0 (継承あり)。コードは MIT。
- 出典表示「(c) OpenStreetMap contributors」が必要。CC BY の geo-triples-jp-gov と混ぜると、混ぜたものは ODbL になる。

## 12 ステップで使えそうな場面 (案)

- LLM 向けの文と評価問題が主。表形式の機械学習の目的変数としては使いにくい。
- 7 Dijkstra/A*: OSM の市区町村 (1,740) の隣接グラフが sfTouches から取れる。国勢調査版 (geo-triples-jp-gov) と辺を比べると、境界データの違いが見える。
- 10 CP-SAT: 同じ隣接グラフで地図の塗り分け。
- 分類の練習: POI がどの市区町村にあるか (probe の place-in-municipality) は、座標があれば point-in-polygon で答えが出るので、機械学習ではなく空間結合の検算に使うほうが向く。
