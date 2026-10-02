# wikimedia

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/wikimedia/`
- ファイルは 1 つ。Wikipedia の記事ごとの重要度 (importance) の表。列の形 (`language`, `type`, `title`, `importance`, `wikidata_id`) は Nominatim が検索順位に使う `wikimedia-importance.csv.gz` と同じ形だが、出どころはファイルの中に書かれておらず未確認。
- 版や基準日はファイル名からはわからない。Last-Modified は 2025-10-11。

## ファイル

| ファイル | 形式 | 大きさ (Content-Length) | Last-Modified |
|---|---|---|---|
| `wikimedia-importance.csv.gz` | gzip 圧縮の TSV (区切りはタブ) | 276,336,642 バイト | 2025-10-11 |

## 中身 (先頭 2MiB だけを範囲要求で読んだ)

- 丸ごとは落としていない。末尾 8 バイトの要求で 206 が返ることを確かめたあと (本文は時間切れで届かなかった)、先頭 2,097,152 バイトだけを取って展開した。先頭の要求は 206 で 2,097,152 バイト届いた。
- 拡張子は `.csv` だが区切りはタブ。
- 見出し行は `language	type	title	importance	wikidata_id`。
  - `language`: 言語コード (先頭部分は全部 `en`)
  - `type`: `a` と `r` の 2 値 (記事とリダイレクトと思われる。未確認)
  - `title`: 記事名 (空白は `_`)
  - `importance`: 0 から 1 の実数と見える (例 `0.8586751425079319`)
  - `wikidata_id`: `Q884` のような Wikidata の ID
- 先頭 2MiB を展開すると 151,838 行 (見出しと、途中で切れた最後の行を含む)。その中は全部 `en` で、`type` は `r` が 99,093、`a` が 52,745。
- 先頭の数十行は英語版なのに `군`, `동`, `광주`, `남한` のような韓国語の記事名が並ぶ (英語版にあるハングルのリダイレクトと思われる)。その後はアルファベット順らしく、2MiB の終わりは `Archdiocese_of_Gu...` のあたり。
- 全体の行数、言語の種類と分布、`importance` の分布は読めていない。gzip の末尾 8 バイト (展開後の大きさ) も 2 回要求して 2 回とも時間切れで読めなかった。

## 気をつけること

- 264MB あるので、丸ごと落とすかは用途で決める。行数を数えるだけでも全体の展開が要る。
- 同じ `wikidata_id` が複数の `title` (記事とそのリダイレクト) に出てくる (例: `고공` と `고대` はどちらも `Q39997`、`importance` も同じ値)。Wikidata ID で結合すると行が増える。
- `importance` がどう計算されたかはファイルにない。未確認。
- ライセンス: データのライセンスは配布元のどこにも明記が無い。入力は Wikipedia (CC BY-SA 4.0) と Wikidata (CC0) (2026-10-02 に調べた)。この写しは nominatim.org が配っていた 2024-08 版と同じもの。詳しくは [../nominatim-wikimedia-importance/README.md](../nominatim-wikimedia-importance/README.md)。

## 12 ステップでの使い道 (案)

- 他のデータに Wikidata ID で結合する補助の特徴量として使う (例: `ucdp/` や `natural-earth/` の地名の知名度)。単体で学習の題材になるものではない。
- 1, 3 回帰 / Gradient Boosting: 地物の属性から `importance` を当てる目的変数として使う。
- 4 データリーク: 同じ Wikidata ID の記事とリダイレクトが学習と検証に割れると、同じ値を覚えるだけで当たってしまう。重複を先に畳む練習になる。
