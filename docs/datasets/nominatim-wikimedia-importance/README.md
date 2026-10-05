# Nominatim の Wikipedia 重要度表 (wikimedia-importance.csv.gz)

2026-10-02 に読んで確かめた内容。行数、言語、値の分布は z.yuiseki.net に置いた写し (`/sata_hdd_24tb/www/html/static/wikimedia/wikimedia-importance.csv.gz`) を zcat で全体ストリーム展開し、awk で数えた値 (ディスクには何も書いていない。1 回の走査は約 19 秒)。配布元の大きさは HEAD とディレクトリ一覧、写しの同定は Wayback Machine の記録から。

- Wikipedia 39 言語版の記事名とリダイレクト名ごとに、0 から 1 の重要度 (importance) と Wikidata ID を並べた表。OpenStreetMap のジオコーダ Nominatim が、同じ名前の地名の順位付けに使う。
- 作成のコードは GitHub の osm-search/wikipedia-wikidata (<https://github.com/osm-search/wikipedia-wikidata>)。Nominatim の開発者コミュニティのもので、README には 2019 年の Google Summer of Code で tchaddad 氏が書き直した経緯がある。配布は nominatim.org。文書のフッタは "Copyright © Nominatim developer community"。
- Nominatim の文書 (<https://nominatim.org/release-docs/latest/customize/Importance/>) は「nominatim.org has preprocessed importance tables for the primary Wikipedia rankings ... The source code for creating these files is available in the Github projects osm-search/wikipedia-wikidata and osm-search/secondary-importance.」と書いている。
- importance の計算 (README の "How importance is computed" の要約)。
  1. 各言語版の `pagelinks` ダンプから、同じ言語の記事から張られたリンクを数える (`langcount`)。
  2. `langlinks` ダンプから、他の言語版からの言語間リンクを、その言語版のリンク数で重み付けして足す (`othercount`)。
  3. `totalcount = langcount + othercount`。最大値 (README の執筆時は United States) を基準に対数で正規化する。式は `importance = GREATEST(LOG(totalcount) / LOG(MAX(totalcount)), 0.0000000001)`。
  4. リダイレクト (`type = r`) には、転送先の記事 (`type = a`) と同じ値と Wikidata ID が付く。
- 入力は、各言語の `page`, `pagelinks`, `langlinks`, `linktarget`, `redirect` の SQL ダンプと、Wikidata の `geo_tags`, `page`, `wb_items_per_site` の SQL ダンプ (2024-08-01 時点のコミット c2e21bdf のスクリプトで確認)。取得元の既定は Wikimedia ダンプのミラー `mirror.clarkson.edu/wikimedia`。記事の本文は入力に含まれない。

## ライセンス

データのライセンスは、配布元のどこにも書かれていない。2026-10-02 に次の場所を見た。

- Nominatim 文書の Import ページ (<https://nominatim.org/release-docs/latest/admin/Import/>) の "Wikipedia/Wikidata rankings" 節。取得の手順と「This data is available as a binary download.」だけで、ライセンスの記載は無い。
- Nominatim 文書の Importance ページ (上の引用の箇所)。ライセンスの記載は無い。
- `https://nominatim.org/data/` の一覧。LICENSE や README のファイルは無い。
- nominatim.org のトップページ。licence も copyright の語も無い。
- osm-search/wikipedia-wikidata の issue を license と licence で検索。データのライセンスを論じたものは無い。

コードのライセンスは書いてある。osm-search/wikipedia-wikidata の README (master、コミット 92b3024e、2026-07-23) の末尾の節は、次の一文だけ。

> License
> The source code is available under a GPLv2 license.

同じリポジトリの LICENSE は GNU General Public License Version 2 (June 1991) の全文で、GitHub API の判定も `GPL-2.0`。この一文は source code についてしか言っていない。

入力側の条件。

Wikimedia ダンプの案内 (<https://dumps.wikimedia.org/legal.html>、2026-10-02 取得)。

> Except as discussed below, all original textual content is licensed under the GNU Free Documentation License (GFDL) and the Creative Commons Attribution-Share-Alike 4.0 License.

> Copyrights of structured data in the main, Property, Lexeme, and EntitySchema namespaces are waived using the Creative Commons Zero (CC0) public domain dedication. All unstructured content in other namespaces is licensed under the Creative Commons Attribution-Share-Alike 4.0 License.

Wikipedia:Copyrights (英語版、<https://en.wikipedia.org/w/index.php?title=Wikipedia:Copyrights&action=raw>、2026-10-02 取得)。

> Permission is granted to copy, distribute and/or modify Wikipedia's text under the terms of the Creative Commons Attribution-ShareAlike 4.0 International License and, unless otherwise noted, the GNU Free Documentation License, unversioned, with no invariant sections, front-cover texts, or back-cover texts.

Wikidata:Copyright (<https://www.wikidata.org/w/index.php?title=Wikidata:Copyright&action=raw>、2026-10-02 取得)。

> All structured data from the main, Property, Lexeme, and EntitySchema namespaces is available under the [[Wikidata:Text of the Creative Commons Public Domain Dedication|Creative Commons CC0 License]]; text in the other namespaces is available under the [[...]|Creative Commons Attribution-ShareAlike License]]; additional terms may apply.

読み取れること。

- 配布元は「データは GPLv2」とも「CC0」とも「CC BY-SA」とも言っていない。データのライセンス名と版は未確認 (明示なし)。
- 表に入っているのは、記事名とリダイレクト名、リンク数から計算した数値、Wikidata の Q ID と記事の対応の 3 つ。Q ID の対応は Wikidata の main 名前空間の構造化データ (sitelinks) 由来で、こちらは CC0。
- 記事名とリンク数は Wikipedia の `page`/`pagelinks`/`langlinks`/`redirect` という本文ではない表から来ている。legal.html が CC BY-SA と GFDL の対象とするのは "original textual content" で、題名やリンク数がそれに当たるかは配布元も Wikimedia も書いていない。未確認。
- GPL の FAQ はプログラムの出力に GPL は原則として及ばないと説明しているが、この表について配布元がそう述べた記述は無い。未確認。
- EU のデータベース権がこの表に及ぶかも未確認。
- 変更なしの再配布、変換した形 (Parquet など) の再配布、商用利用、share-alike の要否、必要な表記は、どれも明示が無い。入力側 (Wikipedia の CC BY-SA と GFDL、Wikidata の CC0) はどちらも商用可。Wikipedia 由来の部分に CC BY-SA が及ぶとみなすなら、派生物も CC BY-SA 4.0 で出し、Wikipedia の寄稿者への帰属を書くことになる。

[wikipedia](../wikipedia/README.md) (CC BY-SA 4.0) や [wikidata](../wikidata/README.md) (CC0) と違い、許諾の文言そのものが無いのがこの表の特徴。

## 中身

| 項目 | 値 |
|---|---|
| 形式 | gzip 圧縮のタブ区切り。拡張子は `.csv` だが区切りはタブで、引用符は使わない |
| 圧縮後の大きさ | 276,336,642 バイト (z.yuiseki.net の写し) |
| 展開後の大きさ | 1,002,214,893 バイト |
| データ行 | 17,846,821 行 (見出し 1 行は別) |
| 記事 (`a`) | 9,779,403 行 |
| リダイレクト (`r`) | 8,067,418 行 |
| 言語 | 39 種 |
| 異なる Wikidata ID | 3,364,133 |

見出し行は `language	type	title	importance	wikidata_id`。

| 列 | 内容 |
|---|---|
| `language` | Wikipedia の言語コード (`en`, `ja` など) |
| `type` | `a` が記事、`r` がリダイレクト |
| `title` | 記事名。空白は `_` |
| `importance` | 0 から 1 の実数。最小値は式の下限の `1e-10` |
| `wikidata_id` | `Q34600` のような Wikidata の ID。全行で空欄は無かった |

例: `ja	a	京都市	0.6994910287722182	Q34600`。

言語ごとの行数。ファイルの中もこの順に言語ごとのかたまりで並んでいて、同じ言語が離れて 2 か所に出てくることは無かった。

| 言語 | 行数 | 言語 | 行数 | 言語 | 行数 |
|---|---:|---|---:|---|---:|
| en | 3,311,990 | ja | 467,800 | tr | 199,135 |
| de | 989,524 | pt | 393,550 | eu | 167,257 |
| fr | 947,663 | ar | 351,280 | fi | 150,776 |
| uk | 922,254 | id | 335,400 | war | 113,879 |
| sv | 917,064 | ca | 294,158 | lt | 101,372 |
| es | 826,644 | ko | 260,027 | sk | 98,570 |
| fa | 804,784 | vi | 232,491 | da | 90,981 |
| ru | 789,716 | eo | 213,219 | bg | 88,887 |
| sr | 718,042 | cs | 204,630 | kk | 77,238 |
| zh | 645,834 | no | 203,740 | he | 75,640 |
| pl | 597,222 | ms | 200,152 | hi | 61,987 |
| nl | 585,834 | hu | 200,118 | hr | 47,757 |
| it | 575,678 | | | sl | 45,747 |
| ro | 538,781 | | | | |

値の両端。

- importance が 1 の行は 969 行で、すべて `Q30` (アメリカ合衆国) とそのリダイレクト。ja では `アメリカ合衆国` (a) のほかに `アメリカ`、`USA`、`アメリカ合衆国の文化` などのリダイレクトが 1 を持つ。
- 下限の `1e-10` に張り付いた行は 110,824 行。式の上では totalcount が 1 以下だと LOG が 0 以下になり下限で置き換わるので、リンクがほとんど無い記事とそのリダイレクトと読める。個々の行のリンク数までは確かめておらず未確認。

## 気をつけること

同じ Wikidata ID が何度も出てくる。 リダイレクトは転送先と同じ ID と同じ値を持ち、言語が違えば同じ ID が言語の数だけ出てくる。3,364,133 の ID のうち 1,989,044 は 2 行以上に出てくる。ただし同じ言語で同じ ID を持つ記事 (`a`) は 2 行以上無かった。Wikidata ID で 1 件にしたいなら、言語と `type = a` で絞ってから結ぶ。絞らずに結ぶと行が増える。

リダイレクトの名前は転送先の言い換えとは限らない。 `アメリカ合衆国の文化` が `Q30` と値 1 を持つように、節や下位の話題へのリダイレクトも転送先の値をそのまま受け継ぐ。名前の重要度として使うと、下位の話題が親と同じ重さに見える。en の先頭にある `군`、`동` のように、別の文字のリダイレクトも入る。

言語間で値は比べられる形だが、言語ごとには計算していない。 正規化の基準は全体の最大 (United States) 1 つ。ある言語の中での順位が欲しければ自分で並べ直す。

拡張子は `.csv` だがタブ区切りで、引用符の処理が無い。 README には `"Alford	_Massachusetts"` のような崩れた行の例がある。今回の写しでは 17,846,821 行すべてがちょうど 5 列だった。

座標は入っていない。 入力には Wikidata の `geo_tags` があるが、出力の列は 5 つだけ。地図に置くには [wikidata](../wikidata/README.md) などと Q ID で結ぶ。

版がファイルに書かれていない。 版の手がかりは配布元のファイル名と gzip ヘッダの時刻だけ。元にした Wikipedia と Wikidata のダンプの日付 (YYYYMMDD) は、ファイルにも配布元にも無い。未確認。

2024-08 版は配布元から消えている。 2026-10-02 の nominatim.org にあるのは次の版で、2024-08 版は `/data/wikipedia/` に残っていない (2025-08 版に置き換えられた)。Wayback Machine には取得物と当時の一覧が残っている。配布元はチェックサムを出していない (`/data/` の一覧に .md5 も .sha256 も無い)。

| URL | Content-Length | Last-Modified |
|---|---:|---|
| `https://nominatim.org/data/wikimedia-importance.csv.gz` | 321,855,821 | 2025-11-27 08:22:57 GMT |
| `https://nominatim.org/data/wikipedia/wikimedia-importance-2025-11.csv.gz` | 321,855,821 | 2025-11-27 |
| `https://nominatim.org/data/wikipedia/wikimedia-importance-2025-08.csv.gz` | 282,870,555 | 2025-08-10 |
| `https://nominatim.org/data/wikipedia/wikimedia-importance-2019-11.sql.gz` | 393,574,858 | 2019-11-17 |

`https://nominatim.org/data/wikimedia-importance.csv.gz` は固定の URL で中身が差し替わる。同じ URL から取っても、時期によって別の版になる。

nominatim.org は curl の既定の User-Agent に 403 を返す。ブラウザ風の User-Agent を付けると 200 (206) が返る。

## 取り出し方

whole。gzip 1 本で、言語や行を選ぶ索引が無い。2026-10-02 に実測した。

| 要求した URL | Range 要求 (`-r 0-1023`) | 全体の大きさ |
|---|---|---:|
| `https://z.yuiseki.net/static/wikimedia/wikimedia-importance.csv.gz` | 206、1,024 バイト、`cf-cache-status: HIT` | 276,336,642 |
| `https://nominatim.org/data/wikimedia-importance.csv.gz` | 206、1,024 バイト (ブラウザ風の User-Agent で) | 321,855,821 |

- Range は通るが、中身は先頭から順に展開するしかない gzip のストリームで、途中のバイトから読み始めることはできない。言語ごとのかたまりに並んでいても、その境目がどのバイトにあるかは分からない。
- 2026-09-28 の [z.yuiseki.net の記録](../z-yuiseki-static/wikimedia.md) では、先頭 2,097,152 バイトを範囲要求で取って展開すると 151,838 行が読め、全部 `en` だった。先頭から読み切れる範囲で en の一部が見られるだけで、他の言語は全体を流さないと届かない。
- 最小単位は 1 本の 276,336,642 バイト (2024-08 版) か 321,855,821 バイト (2025-11 版)。手元で全体を流して数えるのに約 19 秒だった。

## z.yuiseki.net の写し

`https://z.yuiseki.net/static/wikimedia/wikimedia-importance.csv.gz` (yuisekin-z の `/sata_hdd_24tb/www/html/static/wikimedia/`) に 1 本だけ置いてある。nominatim.org が 2024-08-07 から 2025-08 頃まで配布していた `wikimedia-importance-2024-08.csv.gz` と、バイト単位で同じもの。

| 項目 | 値 | 根拠 |
|---|---|---|
| 大きさ | 276,336,642 バイト | `ls`、公開 URL の Content-Range も同じ |
| Last-Modified | 2025-10-11 07:14:10 GMT | z に置いた日時。作成日ではない |
| gzip ヘッダの時刻 | 2024-06-28 20:24:33 UTC、"max compression"、OS=Unix | `file` と `xxd`。出力スクリプトは `pigz -9` |
| SHA-1 | 1571e79a43ce6f8dcc3e55bff5ae4cfc8ff3f2de (base32 で CVY6PGSDZZXY3TB6KW77LLSM7SH7H4W6) | 手元で計算 |
| MD5 | df4aaadd7d774e4dc7d00e03ca964a9c | 手元で計算 |
| SHA-256 | f68c241e2a873c47ab85d4ef637a8db727f620ebc10344e83dedb7b14cb26256 | 手元で計算 |

2024-08 版と同じだと言える根拠。

- Wayback Machine の nominatim.org/data/ の一覧 (2024-08-08、2024-12-02、2025-07-09 の各スナップショット) に `wikimedia-importance.csv.gz  07-Aug-2024 07:55  276336642` がある。
- 2024-09-18 のスナップショットの `/data/wikipedia/` の一覧に `wikimedia-importance-2024-08.csv.gz  07-Aug-2024 07:55  276336642` がある。
- Wayback の CDX が記録した `https://nominatim.org/data/wikimedia-importance.csv.gz` の 2024-11-14 と 2025-01-16 の取得物の digest が `CVY6PGSDZZXY3TB6KW77LLSM7SH7H4W6` で、手元の SHA-1 と一致する。

版の呼び名は配布元に合わせて「2024-08」。gzip の時刻からはファイル自体は 2024-06-28 に作られたと読める。ビルドに使ったコードのコミットは未確認 (2024-05-15 の #81 から 2024-07-08 の #82 の間と推測できるだけ)。元のダンプの日付も未確認。

## 学習ステップとの対応 (案)

- 他のデータに Wikidata ID で結ぶ補助の特徴量 (地名の知名度) として使う。[geonames](../geonames/README.md) の `wkdt` の別名や [wikidata](../wikidata/README.md) の座標と結べる。単体で学習の題材になるものではない。
- 1, 3 回帰 / Gradient Boosting: 地物の属性 (人口、行政の階層など) から `importance` を当てる目的変数。下限に張り付いた 110,824 行の扱いが問題になる。
- 4 データリーク: 同じ Wikidata ID の記事とリダイレクト、別の言語の同じ ID が学習と検証に割れると、同じ値を覚えるだけで当たる。ID で先に畳む練習になる。
