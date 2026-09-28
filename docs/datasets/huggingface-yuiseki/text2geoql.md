# text2geoql

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/text2geoql/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/text2geoql`
- TRIDENT の中間言語 (`AreaWithConcern: 地名, 上位の地名; 関心`) を Overpass QL に訳すための合成データ。小さな言語モデルの fine-tune 用。
- 最終更新 2026-08-29。GitHub は `yuiseki/text2geoql-dataset`。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| data/train-00000-of-00001.parquet | 160,533 | 4,897 行 |
| README.md | 1,870 | カード |

LICENSE と provenance.yaml は無い。

## 行数と列

全体をダウンロードして DuckDB 1.5.5 で集計した。

- 4,897 行。列は `input` `input_type` `output` `output_type` の 4 つで、すべて VARCHAR。
- `input_type` はすべて `trident`、`output_type` はすべて `overpassql`。
- `input` の先頭: `AreaWithConcern:` 4,591、`Area:` 271、`SubArea:` 32、空文字列 3。
- `AreaWithConcern` の行の関心 (`;` の後ろ) は 110 種類。上位は Cafes 262、Convenience stores 256、Hotels 241、Museums 231、Hospitals 193、Parks 184、Train Stations 183。
- `AreaWithConcern` の行の国 (地名の最後の要素) は 49 種類。全行で数えると Japan 2,649、South Korea 1,236、China 438、Kosovo 46、Italy 25。日本と韓国で 7 割を超える。
- `input` の重複 7 行、`output` の重複 26 行。

## 元データと基準日

- カードによると、地名は Nominatim、タグは taginfo で確かめ、どの Overpass QL も公開の Overpass API で 1 件以上返ることを確かめた、とある。どの時点のデータで確かめたかは書かれていない (未確認)。
- この一覧のほかのデータセット (2026-08-31 の凍結) とは関係が無い。

## ライセンス

- カードとタグ: `odbl` (ODbL 1.0)。LICENSE ファイルは無い。

## 気づいたこと

- カードは「148 POI categories, global geographic coverage」と書くが、`AreaWithConcern` の関心は 110 種類、国は 49 種類で、行の 7 割以上が日本と韓国。
- `input` が空文字列の行が 3 行ある。

## 12 ステップでの使いどころ (案)

- 言語モデル向けの入出力の対で、表の数値も位置も入っていないので、12 ステップには使えない。
