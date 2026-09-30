# taginfo (taginfo.openstreetmap.org)

2026-09-30 に読んで確かめた内容。数値は当日 `https://taginfo.openstreetmap.org/api/4/...` を curl で叩いて得たもの。過去の数との比較は `yuiseki/osm-tag-corpus` の `provenance.yaml` (当日取得) と同リポジトリの項目による。

- `https://taginfo.openstreetmap.org/`
- OSM で実際に使われているタグの統計。キーと値ごとの使用回数、値の分布、どのプログラムが使っているか、wiki に説明があるか、時系列をまとめている。
- `/api/4/site/info` が返した説明: `This is the main taginfo site. It contains OSM data for the whole planet and is updated daily.`。`area` は `World`、`contact` は `Jochen Topf <jochen@remote.org>`。
- about ページによると運営は OSMF、保守は Jochen Topf と Sysadmin team。地域別の taginfo サイトを別の人が運用している。
- `yuiseki/osm-tag-corpus` の上流 ([huggingface-yuiseki/osm-tag-corpus.md](../huggingface-yuiseki/osm-tag-corpus.md))。説明文の元をたどるとさらに OSM Wiki ([../osm-wiki/README.md](../osm-wiki/README.md))。

## ライセンス

about ページ (`https://taginfo.openstreetmap.org/about`) の License 節。

> The data available through taginfo is licenced under ODbL, the same license as the OpenStreetMap data.

全ページのフッターにも `Data © OSM contributors (ODbL)` と出る。`yuiseki/osm-tag-corpus` の `provenance.yaml` も同じ根拠を書いている。

> taginfo distributes its data under ODbL, and this repository's derivative inherits it: attribute the source, and share alike if you redistribute a modified version.

ただし taginfo が配っているものには、OSM データ由来の使用回数と、OSM Wiki 由来の説明文の両方が入っている。wiki 本文は CC BY-SA 2.0 で ODbL ではない。about ページはこの区別に触れていない。未確認のまま扱うなら、使用回数は ODbL、説明文は CC BY-SA 2.0 として両方の表示をしておくのが安全。

## 使い方の方針 (本家が書いていること)

数値の上限は書かれていない。書かれているのは方針だけである。API については about ページにこうある。

> The servers running the taginfo API do not have unlimited resources. Please use the API responsibly. If in doubt contact the maintainers of the site you are using or talk to us on the mailing list.

ダウンロードについても同じ調子。

> Note that some of these files can get quite large. If you want to download them regularly, contact the maintainers of the site you are using or talk to us on the mailing list.

1 秒あたりの要求数、1 日あたりの上限、必要な User-Agent の形といった具体的な制限は、当日読んだ about ページ、API ドキュメント (`/taginfo/apidoc`)、download ページのどこにも書かれていなかった。未確認。`robots.txt` は `Disallow: /api` と `Disallow: /download` を含むので、巡回ロボットには開けていない。まとめて取るならダンプを落として手元で処理するのが本家の想定と読める。

## 当日の実数 (API)

`data_until` は API が自分で返す基準時刻。db 系は 2026-09-29T00:59:51Z。

| 問い合わせ | total |
|---|---:|
| `/api/4/keys/all` | 115,209 |
| `/api/4/tags/popular` | 14,467 |
| `/api/4/keys/wiki_pages` (wiki に説明があるキー) | 6,811 |
| `/api/4/keys/without_wiki_page` | 509 |
| `/api/4/wiki/languages` | 80 |
| `/api/4/projects/all` | 304 |
| `/api/4/relations/all` (リレーションの type) | 825 |

使われているキーは 115,209 あるのに、wiki に説明があるのは 6,811。全体の 6% 弱しか文書化されていない。`without_wiki_page` の 509 は 115,209 から 6,811 を引いた数ではない。API ドキュメントによるとこれは `Return frequently used tag keys that have no associated wiki page.` で、既定の `min_count` は 10000。つまり「1 万回以上使われているのに説明が無いキー」が 509 個あるという意味。

個別の例 (当日、`data_until` 2026-09-29T00:59:51Z)。

| 問い合わせ | count (all) |
|---|---:|
| `key/overview?key=building` | 709,892,745 (値の種類 9,247) |
| `tag/overview?key=building&value=yes` | 562,269,780 |

## 更新のしくみ (`/api/4/site/sources`)

源ごとに更新の時刻が違う。1 つの `data_until` で全部を語れない。

| id | 名前 | data_until | 更新の開始 | 終了 |
|---|---|---|---|---|
| db | Database | 2026-09-29 00:59:51 | 03:43:17 | 06:48:04 |
| wiki | Wiki | 2026-09-29 07:01:39 | 07:01:39 | 07:09:37 |
| languages | Languages | 2026-09-29 06:48:05 | 06:48:05 | 06:48:20 |
| projects | Projects | 2026-09-29 06:48:20 | 06:48:20 | 07:01:39 |
| chronology | Chronology | 2026-09-29 00:59:51 | 07:09:37 | 07:54:04 |
| sw | Software | 2026-09-29 07:54:04 | 07:54:04 | 07:54:07 |

OSM データの取り込み (db) は 00:59 時点のもので、wiki の取り込みはその 6 時間後。同じ回のダンプでも、使用回数と説明文で 6 時間ずれている。

## ダンプ (download ページ)

`https://taginfo.openstreetmap.org/download/` に SQLite を bzip2 で固めたものが置いてある。download ページの表 (丸めた値) と、当日 HEAD で見た実バイト数。

| ファイル | 表の Packed | 表の Unpacked | HEAD の Content-Length | HEAD の Last-Modified | 中身 |
|---|---|---|---:|---|---|
| taginfo-db.db.bz2 | 2501 MB | 40441 MB | 2,623,225,085 | 2026-09-29 07:55:51 GMT | キーとタグごとの統計 |
| taginfo-wiki.db.bz2 | 24 MB | 126 MB | 25,852,280 | 2026-09-29 07:54:11 GMT | wiki のタグ/キーページ |
| taginfo-projects.db.bz2 | 21 MB | 312 MB | 22,224,912 | 2026-09-29 07:54:15 GMT | 外部プロジェクトと使うタグ |
| taginfo-master.db.bz2 | 6 MB | 25 MB | 7,083,941 | 2026-09-29 08:39:59 GMT | 集計と UI 用 |
| taginfo-history.db.bz2 | 3 MB | 19 MB | (未取得) | (未取得) | 時系列の集計 |
| taginfo-languages.db.bz2 | 728 kB | 2 MB | (未取得) | (未取得) | 言語名と符号 |
| taginfo-chronology.db.bz2 | 269 MB | 1521 MB | (未取得) | (未取得) | 履歴データからの推移 |
| taginfo-sw.db.bz2 | 16 kB | 72 kB | (未取得) | (未取得) | エディタ等の設定 |

download ページの脚注。

> Some indexes are not in the databases available for download here. The 'Packed' size is the size without those indexes, the 'Unpacked' size includes the indexes you probably want to build after downloading.

`taginfo-db.db` は展開して索引を張ると 40 GB になる。落とす前にディスクを確認すること。

## `yuiseki/osm-tag-corpus` が何を読み、何を読まなかったか

`provenance.yaml` (当日取得) による。

| ファイル | 使った表 | 何に使ったか |
|---|---|---|
| taginfo-wiki.db (ダンプ日 2026-01-30、data_until 2026-01-29T00:59:50Z) | `wikipages`, `tag_page_related_terms` | description, 冒頭段落, related_terms, status, on_* |
| taginfo-db.db (ダンプ日 2026-01-30) | `tags`, `keys` | count_all (全世界の使用回数) |

読まなかった表と、その理由 (原文)。

- `words`: `Body text stemmed across every language. Asking it for tourism=hotel returns hundreds of terms like acho, allas, americain. Mixing them into a passage makes retrieval worse.`
- `redirects`: `A plausible source of aliases, not evaluated here.`

つまり別名 (リダイレクト) は corpus に入っていない。タグの表記ゆれを吸収したいなら `redirects` を自分で読む必要がある。

## 気をつけること

使用回数は全世界の値で、しかも毎日動く。 版番号は無い。`data_until` を記録しない限り、taginfo から作ったコーパスは「いつの」スナップショットか分からなくなる。実際に確かめた差は次のとおり。`building` キーの `count_all` は `yuiseki/osm-tag-corpus` (data_until 2026-01-29T00:59:50Z) で 673,173,299、当日の API (data_until 2026-09-29T00:59:51Z) で 709,892,745。8 か月で 36,719,446 増えており、約 5.5% の差。回数を特徴量や閾値に使うなら、必ず `data_until` を一緒に保存する。

日本や東京の数ではない。 このサイトは `area: World`。地域別の taginfo サイトは別の人が別に運用している。日本国内のタグ分布が欲しいなら、この数値は使えない。

キーとタグの total は別物。 `keys/all` は 115,209 だが `tags/popular` は 14,467。後者は「よく使われているタグ」に絞った一覧で、存在するタグの総数ではない。名前が似ているので取り違えやすい。

キーに空白が入っていることがある。 `keys/all?page=1&rp=1` を既定の並びで引くと、先頭に返ってくるのは ` temporary:closed:reason` で、先頭に半角空白が付いている (count_all 2)。キー名を trim して扱うコードは、この行を別のキーと衝突させる。

`data_until` は源ごとに違う。 上の表のとおり db と wiki で 6 時間ずれる。1 つの値で「この回のデータ」と言い切れない。

wiki 由来の部分は ODbL だけで説明できない。 説明文の元は CC BY-SA 2.0 の OSM Wiki。taginfo は全体を ODbL と書いているが、二次利用するなら両方の表示を付けておくほうが安全。

## 学習ステップでの使いどころ (案)

- 空間の情報は無い。地物の位置を扱う課題には直接使えない。
- OSM のタグを特徴量にするとき、`count_all` で希少タグを切る閾値の根拠として使える。四分位は `yuiseki/osm-tag-corpus` 側に集計がある。
- `keys/wiki_pages` (6,811) と `keys/all` (115,209) の差は、そのまま「文書化されているか」というラベルになる。説明の有無を当てる分類の題材。
- 1 件ずつ API を叩くのではなく、`taginfo-db.db.bz2` と `taginfo-wiki.db.bz2` を落として SQLite で引くほうが速く、本家の方針にも合う。
