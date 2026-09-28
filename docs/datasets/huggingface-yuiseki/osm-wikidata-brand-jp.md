# osm-wikidata-brand-jp

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/osm-wikidata-brand-jp/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/osm-wikidata-brand-jp`
- osm-wikidata-brand-tokyo23 の全国版。日本全国の OSM で `brand:wikidata` が付いた地物を Q 番号ごとにまとめ、OSM 側の名前の書き方と件数、Wikidata 側のラベル・説明・別名を並べたもの。1 行 1 ブランド。
- 最終更新 2026-09-17。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| data/train-00000-of-00001.parquet | 2,176,983 | 1,859 行 |
| provenance.yaml | 8,480 | コマンド、道具の版、件数 |
| LICENSE | 1,268 | ODbL と CC0 の表示 |

## 行数と列

全体をダウンロードして DuckDB 1.5.5 と Python の `json` で集計した。

- 1,859 行、`qid` は 1,859 種類で重複なし。
- 列は東京版と同じ 9 個: `qid` VARCHAR、`features` BIGINT、`label_en` `label_ja` `description_en` `description_ja` VARCHAR、`osm` `aliases` `record` (JSON 文字列)。
- `features` の合計 172,852、最小 1、最大 14,752。`features` が 1 のブランドは 621、10 以上は 725。カードと一致した。
- `osm` に現れるキーは 221 種類 (カードと一致)。1 行が持つ値の数は 1 から 29,411。キーと値の組の種類は 62,919、値の文字列だけの種類は 36,461。
- キーが現れるブランド数の上位: name 1,839、brand 1,469、name:en 1,151、name:ja 1,102、brand:en 849、brand:ja 837、name:ja-Hira 440、name:ja-Latn 419。カードの表と一致した。
- Wikidata 側の非空: ラベル en 1,733、ja 1,746。説明 en 1,413、ja 1,310。別名 en 824、ja 1,033。`found` が false は 12 行 (カードと一致)。
- `features` の上位: 7-Eleven 14,752、Hello Cycling 13,992、Lawson 8,777、Docomo Bike Share 5,798、FamilyMart (Q11247682) 5,621、FamilyMart (Q1191685) 5,401、ENEOS 4,449、Coca-Cola 4,292。FamilyMart は Q 番号が 2 つあり、別々の行になっている (カードの「One chain has two Wikidata items」のとおり)。

## 元データと基準日

- OSM: osm-japan-src-2026-08 の `japan-260831.osm.pbf` (md5 `2f803a54de5bdeb5ecbbb740c9b5100d`、2026-08-31 の planet) を osmium で読んだもの。
- Wikidata: `wikidata-20260831-all.json.bz2` (md5 `f99e3ee0778ffe1c3b54fa5dbc6ce395`)。

## ライセンス

- カードとタグ: `odbl`。カードの本文では、OSM 由来の部分が ODbL 1.0、`wikidata` の中身が CC0 1.0。

## 気づいたこと

- カードの「65,026 distinct values」は、キーと値の組で数えても (62,919)、値の文字列だけで数えても (36,461) 一致しなかった。数え方が違うのかは確かめていない。ほかの数 (行数、features 合計、キー数、1 件だけのブランド数、found が false の数) は一致した。
- 7-Eleven の `brand` に `Agu hairグループ` (1 件) や `disused:セブン-イレブン` (1 件) のような、OSM 側の誤りや古い値がそのまま入っている。カードは何も除いていないと明言している。

## 12 ステップでの使いどころ (案)

- 位置が入っていない名前の表なので、空間の学習データとしては使えない。
- osm-japan-src-2026-08 の点をチェーンごとに束ねる対応表として使える。例えば 5 (DBSCAN) でコンビニの分布をチェーン別に比べる、9 (facility location) で既存店をチェーン別に固定するなど。
- 東京版と同じく、名前の値が「チェーン名」「支店名」「誤り」のどれかを件数の比から当てる分類 (1, 2) の練習にはなる。
