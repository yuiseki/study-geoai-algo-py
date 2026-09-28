# osm-tag-corpus

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/osm-tag-corpus/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/osm-tag-corpus`
- OSM Wiki が説明している各タグについて、言語ごとの説明文、冒頭の文、関連語、使える要素の種類、全世界での使用回数を並べたもの。1 行 1 タグ x 1 言語。埋め込みを作るための素材で、埋め込みそのものは入っていない。
- 最終更新 2026-09-07。GitHub は `yuiseki/osm-tag-corpus`。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| data/train-00000-of-00001.parquet | 6,598,805 | 31,913 行 |
| provenance.yaml | 1,051 | 読んだ taginfo の表と読まなかった表 |
| LICENSE | 1,536 | ODbL の表示 |

## 行数と列

全体をダウンロードして DuckDB 1.5.5 で集計した。

- 31,913 行。`tag` の種類 9,803、`key` の種類 4,010、`lang` の種類 70。`lead_sentences` の文の数の合計 48,852。どれもカードと一致した。
- 列: `tag` `key` `value` `lang` `title` `description` VARCHAR、`lead_sentences` `related_terms` `on` VARCHAR[]、`implies` `status` VARCHAR、`count_all` BIGINT。
- `lang` の上位: en 9,467、de 3,301、ru 2,901、es 2,709、fr 2,047、ja 2,033、cs 1,985、pl 1,816、pt 948、uk 907。カードの表と一致した。
- `status`: approved 31,140、proposed 713、error 39、rejected_or_proposed 21。
- `value` が空の行 (キーだけのページ) は 10,022 行、タグの種類で 3,914。
- `implies` が空でない行 1,084、`related_terms` が 1 つ以上ある行 2,338。
- `on` に現れた回数: node 21,717、area 18,917、way 8,455、relation 3,843。
- タグ 1 つあたりの `count_all`: 最小 1、四分位 206 / 1,939 / 20,510、最大 673,173,299 (`building`)。同じタグの言語違いの行で `count_all` が食い違うものは無かった。
- タグの多いキー: shop 318、network 316、amenity 313、sport 201、man_made 188、building 187。

## 元データと基準日

- taginfo のダンプ 2026-01-30 分 (provenance.yaml)。wiki 側は `taginfo-wiki.db` の `wikipages` と `tag_page_related_terms`、使用回数は `taginfo-db.db` の `tags` と `keys`。データ時刻は 2026-01-29T00:59:50Z。
- z.yuiseki.net の `openstreetmap/taginfo/20260130/` と同じ回のダンプと読める (データ時刻が一致する)。同じファイルかどうかは確かめていない。

## ライセンス

- カードとタグ: `odbl` (ODbL 1.0)。provenance.yaml では taginfo が ODbL で配布しているためとしている。説明文の元は OSM Wiki (本文は CC BY-SA 2.0) だが、その扱いはカードには書かれていない。

## 気づいたこと

- カードは `status` の値を approved, proposed, rejected_or_proposed, unknown と書くが、実物に unknown は無く、代わりに error が 39 行ある (例: `man_made=lighthouse` の ar と bn、`cycleway=lane` の da)。
- `count_all` は全世界の使用回数で、日本や東京の数ではない。

## 12 ステップでの使いどころ (案)

- 1, 2, 3: 1 行 1 タグ (英語の行など) に絞り、`on` の種類、関連語の数、説明文の長さなどから `status` (approved か proposed か) を当てる分類や、`count_all` の対数を当てる回帰。地理の学習ではないが、表形式の練習にはなる。
- 6: キーとタグの有無を行列にして PCA、というより osm-tokyo23-src-2026-08 の `tags` を特徴量にするときの辞書として使うほうが自然。
- 空間の情報は入っていない。
