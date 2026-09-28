# osm-wiki

2026-09-28 に読んで確かめた内容。大きさは Hugging Face の API (`/api/datasets/yuiseki/osm-wiki/tree/main?recursive=true`) が返したバイト数。

- `https://huggingface.co/datasets/yuiseki/osm-wiki`
- OSM Wiki の各ページの最新版の本文を、wikitext から平文にしたもの。1 行 1 ページ、8 言語。
- 最終更新 2026-09-17。

## ファイル

| ファイル | 大きさ | 中身 |
|---|---|---|
| data/train-00000-of-00001.parquet | 159,245,929 | 78,178 行 |
| provenance.yaml | 2,470 | 元のダンプ、除いた名前空間 |
| LICENSE | 969 | CC BY-SA 2.0 の表示 |

## 行数と列

50MB を超えるので全体はダウンロードしていない。フッターを DuckDB 1.5.5 で URL から読み、`text` 以外の列を絞って集計した (全体で 28 秒)。

- 78,178 行、row group 79。書いた道具は `parquet-cpp-arrow version 20.0.0`。
- 列: `id` `title` `lang` `kind` `licence` `text` VARCHAR、`namespace` `n_chars` BIGINT。
- `lang` ごとのページ数と文字数 (`n_chars` の合計): en 55,360 / 218,113,129、de 5,195 / 17,775,433、es 4,781 / 15,466,962、ru 4,368 / 12,400,972、fr 3,759 / 13,872,883、ja 2,835 / 6,238,181、it 1,373 / 4,400,046、nl 507 / 2,011,402。
- `kind` と `namespace`: main 0 が 52,895、help 12 が 9、lang 200 から 212 が合わせて 22,818、proposal 3000 が 2,456。
- `n_chars` の合計 290,279,008、中央値 1,237、最小 1、最大 995,068。30 文字未満 814 ページ、300,000 文字超 20 ページ。
- `title` の種類 60,835。`id` が `Key:` か `Tag:` で始まるページ 9,613。
- `licence` の値は 1 種類。
- ここまでの数はすべてカードと一致した。

## 元データと基準日

- OSM Wiki の全履歴 XML ダンプ `dump.xml.gz` (6,676,932,113 バイト、ダンプ日 2026-01-30) から、各ページの最新版だけを取ったもの (provenance.yaml)。z.yuiseki.net の `openstreetmap/wiki/dump.xml.gz` と大きさが一致する。
- 抽出日 2026-09-17。本文の基準日は 2026-01-30。
- リダイレクト 32,656 と、Talk や User などの名前空間 179,173 ページは除いてある。
- OSM の地図データ (planet) は入っていない。

## ライセンス

- Hugging Face のメタデータ (カードの YAML) に `license` が無く、タグも `region:us` だけ。
- カード本文、LICENSE、`licence` 列では CC BY-SA 2.0 (OSM Wiki の著者)。

## 気づいたこと

- カードの本文は「`pages.jsonl` holds the text」と書き、provenance.yaml も `data/pages.jsonl` を指すが、リポジトリにあるのは `data/train-00000-of-00001.parquet` だけで pages.jsonl は無い。
- ライセンスのタグが付いていないので、Hub の一覧や検索ではライセンス不明に見える。

## 12 ステップでの使いどころ (案)

- 文章のコーパスなので、12 ステップの学習データには使えない。
- 学習中に OSM のタグの意味を調べる辞書としては使える (`Key:` と `Tag:` のページ 9,613)。
