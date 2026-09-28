# osm-wikidata-brand-tokyo23

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/osm-wikidata-brand-tokyo23/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/osm-wikidata-brand-tokyo23`
- 東京 23 区の OSM で `brand:wikidata` が付いた地物を Wikidata の Q 番号ごとにまとめ、OSM 側の名前の書き方とその件数、Wikidata 側のラベル・説明・別名を並べたもの。1 行 1 ブランド。
- 最終更新 2026-09-17。カードでは第 2 版 (第 1 版は PostGIS 経由で `name` と `brand` が抜けていた)。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| data/train-00000-of-00001.parquet | 609,302 | 892 行 |
| provenance.yaml | 7,168 | コマンド、道具の版、件数 |
| LICENSE | 1,268 | ODbL と CC0 の表示 |

## 行数と列

全体をダウンロードして DuckDB 1.5.5 と Python の `json` で集計した。

- 892 行、`qid` は 892 種類で重複なし。
- 列: `qid` VARCHAR、`features` BIGINT、`label_en` `label_ja` `description_en` `description_ja` VARCHAR、`osm` VARCHAR (JSON。`{キー: {値: 件数}}`)、`aliases` VARCHAR (JSON)、`record` VARCHAR (レコード全体の JSON)。
- `features` の合計 25,407、最小 1、最大 2,334。`features` が 1 のブランドは 256、10 以上は 298。
- `osm` に現れるキーは 82 種類。1 行が持つ値の数は 1 から 4,850。キーと値の組の種類は 15,192、値の文字列だけの種類は 7,853。
- キーが現れるブランド数の上位: name 887、brand 881、name:en 697、name:ja 646、brand:en 590、brand:ja 586、name:ja_rm 221、name:ja-Latn 183。
- Wikidata 側の非空: ラベル en 887、ja 828。説明 en 862、ja 655。別名 en 498、ja 532。`found` が false (Wikidata のダンプに無い Q 番号) は 3 行。
- `features` の上位: Hello Cycling 2,334、7-Eleven 1,944、Docomo Bike Share 1,779、FamilyMart 1,252、Lawson 825、Times Parking 618、Coca-Cola 531、Mitsui Repark 499。店だけでなく、シェアサイクルのポート、駐車場、自動販売機のブランドも入っている。

## 元データと基準日

- OSM: osm-tokyo23-src-2026-08 の `tokyo23-260831.osm.pbf` (md5 `44a4ba2182379c147f20a27ad1b513ef`、2026-08-31 の planet) を osmium で読んだもの (カードと provenance.yaml)。
- Wikidata: `wikidata-20260831-all.json.bz2` (md5 `f99e3ee0778ffe1c3b54fa5dbc6ce395`)。OSM と同じ日のダンプ。
- 全国版は osm-wikidata-brand-jp。

## ライセンス

- カードとタグ: `odbl`。カードの本文では、`qid` `features` `osm` が OSM 由来で ODbL 1.0、`wikidata` の中身が CC0 1.0 と分けて書いている。

## 気づいたこと

カードの数字が実物と合わないところが多い。第 1 版の数字が残っているように見える。

| 項目 | カード | 実測 |
|---|---|---|
| キーの種類 | 冒頭は 82、表は「80 keys occur」 | 82 |
| distinct values | 15,730 | キーと値の組で 15,192、値だけで 7,853 |
| 1 行の値の数の最大 | 2,515 | 4,850 |
| features が 1 のブランド | 表は 143、後の節は 256 | 256 |
| label en / ja | 726 / 701 | 887 / 828 |
| description en / ja | 709 / 575 | 862 / 655 |
| aliases ja / en | 466 / 398 | 532 / 498 |
| found が false | 表は 1、後の節は 3 | 3 |
| 7-Eleven の features | 1942 | 1,944 |

- カードの例のレコードでは 7-Eleven の `brand:en` に `7-ELEVEN` 1513 と `7-Eleven` 428 とあり、これは実物と一致した。
- `osm-wikidata-brand-jp` のカードは、この東京版の `7-ELEVEN` を「1,512」と書く。実物の `brand` キーの `7-ELEVEN` が 1,512、`brand:en` キーが 1,513 で、キーによって違う。

## 12 ステップでの使いどころ (案)

- 位置も座標も入っていない名前の表なので、空間の学習データとしては使えない。
- 使うとすれば、osm-tokyo23-src-2026-08 の point や polygon の `brand` を正規化する対応表として。例えば 9 (facility location) でコンビニのチェーンごとに施設を分けるとき、`brand:wikidata` で束ねる根拠になる。
- 2 や 1 の分類 (ある名前の値がブランド名か支店名かノイズかを件数の比から当てる) の練習にはなるが、地理とは関係が薄い。
