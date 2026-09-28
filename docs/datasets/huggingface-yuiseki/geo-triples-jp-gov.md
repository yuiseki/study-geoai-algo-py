# geo-triples-jp-gov

2026-09-28 に読んで確かめた内容。

- <https://huggingface.co/datasets/yuiseki/geo-triples-jp-gov>
- 47 都道府県と 1,909 市区町村のポリゴンどうしの空間関係 (GeoSPARQL の Simple Features 8 述語、DE-9IM、RCC8) を 1 行 1 三つ組にした表と、それをテンプレートで文にしたもの。言語モデルの事前学習 (CPT) と評価用に作られている。
- 入力は jp-admin-2026-09 (コミット c86cbe9) の abr-pref 47 件と abr-muni 1,909 件 (jp-admin の 1,918 からジオメトリの無い 9 件を除いた数)。計算は YuisekinGeoSPARQL (Apache Jena Fuseki 6.2.0、shapely/GEOS)、証明は LeanGeospatial と manifest.json に書かれている。
- 最終更新 2026-09-26。schema_version 6。

## ファイル

どれも小さいので全体をダウンロードして DuckDB 1.5.5 で読んだ。

| ファイル | 大きさ (バイト) | 行数 |
|---|---|---|
| data/triples.parquet | 763,924 | 162,810 |
| data/cpt.parquet | 1,490,728 | 165,670 |
| data/probe.parquet | 47,587 | 1,807 |
| data/manifest.json | 4,987 | 件数と sha256 |
| vendor/de9im_sf_verdicts.tsv | 8,320 | DE-9IM から述語への判定表 |
| ATTRIBUTION.md, LICENSE, README.md | | |

行数は 3 つともカードと一致した。

## 列

- triples (29 列): subject_id / _iri / _name / _source / _layer / _kind、predicate、object_ 同じ 6 列、truth (BOOLEAN)、de9im、rcc8、rcc8_observed、reading、norm_method、norm_tolerance、certification、certificate、derivation、via_id、via_iri、outside_ratio (DOUBLE)、source_dataset、engine_version、schema_version。
- cpt (15 列): text、form (ntriples / ja / en)、subject_id、predicate、object_id、derivation、via_id、de9im、rcc8、reading、certification、certificate、holdout (BOOLEAN)、topic、pair。
- probe (15 列): child_id / _iri / _en / _ja、parent_ 同じ 4 列、level、child_layer、parent_layer、rcc8、answer_in_child_ja、answer_in_child_en、split。
- ジオメトリの列は無い。ID は abr-muni-011002 の形で、後ろの 6 桁が lg_code。

## 中身

- triples は observed (ジオメトリから測った) 129,104 行 = 16,138 組 × 8 述語と、composition (RCC8 の合成表から導いた) 33,706 行 (1 組 1 行)。true は 65,982。
- true の内訳: sfDisjoint 33,574、sfIntersects 16,138、sfTouches 11,984、sfWithin 2,143、sfContains 2,143。sfEquals、sfOverlaps、sfCrosses の true は 0。
- sfTouches (true) を層で分けると、市区町村どうし 10,152 (向き付きなので無向の辺にすると 5,076)、都道府県どうし 176、市区町村と都道府県 828 ずつ。向きを逆にした相手はすべてそろっている。隣接を 1 つ以上持つ市区町村は 1,861。
- observed の組を RCC8 で数えると EC 8,590、PO→EC に読み替え 3,394、TPP/TPPi 1,316 ずつ、NTPP/NTPPi 761 ずつ。
- certification: certified 135,658、uncertified 27,152 (manifest と一致)。
- cpt の holdout は True 27,782、False 137,888。probe の split は train 1,632、eval 175。

## 気をつけること

- 全組ではない。1,956 地物の順序付きの組は 3,823,980 (1,956 × 1,955 の計算値) あるが、triples に出てくる組は 49,712 だけ。測った組 (16,138) に無い組は「離れている」と「比べていない」の区別が付かない。隣接グラフとして使うなら sfTouches の true だけを辺にすればよい。
- 国勢調査の境界どうしが境目でわずかに重なっているため、測ったままだと隣接の 3,394 組が PO (部分的に重なる) になる。rcc8 列はこれを EC (接する) に読み替えた値、rcc8_observed が測ったままの値。隣接グラフを作るときは rcc8 (または sfTouches) を使う。
- カードは reading が normalised の行を「2 つが違う 59,712 行」と書いているが、rcc8 と rcc8_observed が違うのは observed の 27,152 行だけ。残りの 32,560 行は composition の行で、rcc8 と rcc8_observed は同じ (読み替えた前提から導かれた行に normalised が付いているように見える)。
- outside_ratio の最大が 1.00000000753 と 1 をわずかに超える (浮動小数の誤差と思われる)。

## ライセンス

- Hugging Face のタグは cc-by-4.0。データと文は CC BY 4.0、コードは MIT とカードに書かれている。
- 元データはアドレス・ベース・レジストリ (デジタル庁) と令和2年国勢調査小地域境界 (総務省統計局) で、どちらも CC BY 4.0 互換。ATTRIBUTION.md は読んでいない。

## 12 ステップで使えそうな場面 (案)

- LLM 向けの文と評価問題が主で、表形式の機械学習の目的変数としては使いにくい。
- 7 Dijkstra/A*: sfTouches の true (市区町村どうし 5,076 辺) をそのまま隣接グラフにできる。辺の重みは jp-admin-2026-09 の代表点どうしの距離を使う。ポリゴンから隣接を計算する手間が省ける。
- 10 CP-SAT: 都道府県 (176 の向き付き辺 = 88 辺) や市区町村の隣接グラフで地図の塗り分けを解く。4 色で塗れるかの確認は小さな練習問題になる。
- 5 クラスタリング: 隣接グラフの上でのクラスタリング (グラフ分割) の入力にできる。
- 4 データリーク: 空間ブロック CV で「隣接する市区町村を同じ fold に入れる」ときの隣接情報として使える。
