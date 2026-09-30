# OpenStreetMap Wiki (wiki.openstreetmap.org)

2026-09-30 に読んで確かめた内容。数値は当日 `https://wiki.openstreetmap.org/w/api.php` と `https://wiki.openstreetmap.org/dump/` を curl で叩いて得たもの。

- `https://wiki.openstreetmap.org/`
- OSM のタグの意味、提案、各地のマッピング方針を書いた MediaWiki。地図データではなく文章。
- API が返した `sitename` は `OpenStreetMap Wiki`、`generator` は `MediaWiki 1.46.0`。応答の `time` は 2026-09-30T08:03:27Z。
- `yuiseki/osm-wiki` の上流 ([huggingface-yuiseki/osm-wiki.md](../huggingface-yuiseki/osm-wiki.md))。`yuiseki/osm-tag-corpus` の説明文も、taginfo を経由してここから来ている。

## ライセンス

OSM の地図データ (ODbL) とは別のライセンスである。API の `meta=siteinfo&siprop=rightsinfo` が返した値。

```json
{"url":"https://wiki.openstreetmap.org/wiki/Wiki_content_license",
 "text":"Creative Commons Attribution-ShareAlike 2.0 license"}
```

`Wiki_content_license` の本文 (`?action=raw` で取得) はこう書いている。

> The text of this wiki is licensed under Creative Commons Attribution-ShareAlike 2.0 (CC BY-SA 2.0).

同じページが地図データとの違いを明示している。

> This only applies to the content of this documentation site. The (much more important!) license of the OpenStreetMap map data itself, is described at www.openstreetmap.org/copyright

さらに、全部が CC BY-SA 2.0 とは限らないと断っている。

> Some wiki pages may contain content which is licensed differently. In these cases the page should be clearly labelled with copyright information.

> Images which have been uploaded to this wiki are often also licensed under CC BY-SA 2.0, but certainly not always!

つまり本文を再利用するなら表示と継承 (share-alike) が要る。画像は 1 枚ずつ画像説明ページを見ないと条件が決まらない。

## 規模 (siteinfo statistics)

| 項目 | 値 |
|---|---:|
| pages | 304,486 |
| articles | 86,510 |
| edits | 3,101,980 |
| images | 53,861 |
| users | 173,831 |
| activeusers | 779 |
| admins | 21 |
| max-page-id | 345,829 |

`pages` はリダイレクトや全名前空間を含む総数、`articles` は本文のあるページ数で、両者は 3.5 倍違う。

## 名前空間

`siprop=namespaces` が返した構成。言語別の名前空間があるのがこの wiki の特徴で、`osm-wiki` データセットが `namespace` 200 から 212 として持っているのはこれ。

| id | 名前空間 | 備考 |
|---|---|---|
| 0 | (メイン) | 英語の本文と `Key:` `Tag:` ページ |
| 12 | Help | |
| 120 / 122 | Item / Property | Wikibase。`wikibase-conceptbaseuri` は `https://wiki.openstreetmap.org/entity/` |
| 200/202/204/206/208/210/212 | DE / FR / ES / IT / NL / RU / JA | 言語別 |
| 3000 | Proposal | タグの提案 |

言語別名前空間は 7 言語分しかない。それ以外の言語 (日本語以外のアジア言語など) はメイン名前空間の `Ja:` のような接頭辞ではなく、各ページのサブページや別の題名で書かれている場合があり、名前空間だけでは言語を数え切れない。

## Key: と Tag: のページ数 (当日 allpages で数えた)

`action=query&list=allpages` をページングして数えた実数。リダイレクトを含む。

| 名前空間 | 接頭辞 | ページ数 |
|---|---|---:|
| 0 (メイン) | `Key:` | 6,720 |
| 0 (メイン) | `Tag:` | 8,538 |
| 3000 (Proposal) | (全部) | 2,678 |
| 212 (JA) | `Key:` | 849 |
| 212 (JA) | `Tag:` | 2,030 |
| 212 (JA) | (全部) | 4,592 |

日本語の `Tag:` ページは英語の 4 分の 1 弱ある。タグの辞書として日本語で引く用途にはそれなりに使える。

## ダンプ

- 置き場は `https://wiki.openstreetmap.org/dump/`。索引に 2 ファイルだけある。
- `dump.xml.gz`: 6,887,110,913 バイト、`Last-Modified` 2026-09-01 06:23:39 GMT、`Content-Type` は `application/x-gzip`。全履歴 (`dumpBackup.php --full`) の XML。
- `wikibase-rdf.ttl.gz`: 索引の表示で 11M、最終更新 2026-09-30 04:01。Wikibase 部分の RDF。
- wiki の `Wiki` ページ (`?action=raw`) はこう書いている。

> Daily full history exports of this wiki are available here:
> * https://wiki.openstreetmap.org/dump/ (5.9 GB as of 24 February 2025)
> This is configured to run dumpBackup.php with --full (All revisions) each morning.

## API の使い方

- エンドポイントは `https://wiki.openstreetmap.org/w/api.php`。認証なしで読める。
- `api.php` の自動生成ヘルプが書いている上限。

> Most API modules can accept up to 50 inputs in multivalue parameters, and can return up to 500 results per query (50 results for slow queries). For users with the apihighlimits right (Bots and Administrators), the limits are increased to 500 inputs and 5,000 results (500 results for slow queries).

- 1 秒あたりの要求数のような数値の制限は、当日読んだ範囲 (`api.php` のヘルプ、`robots.txt`) には書かれていなかった。未確認。
- `robots.txt` は `Disallow: /w/` と `Disallow: /api/` を含む。API は人間が使う想定で、巡回ロボットには開けていない。大量に取るならダンプを使うのが筋。

## 気をつけること

ライセンスを OSM 本体と取り違えないこと。 wiki 本文は CC BY-SA 2.0 で、継承 (share-alike) がある。地図データの ODbL とは別物で、条件も違う。`yuiseki/osm-tag-corpus` は taginfo 経由なので ODbL を名乗っているが、その説明文の元は CC BY-SA 2.0 の wiki 本文である。この二重性はどちらのデータセットカードにも書かれていない。

「毎朝」と書いてあっても実際は止まっている。 `Wiki` ページは `each morning` と書くのに、当日の `dump.xml.gz` の `Last-Modified` は 2026-09-01 06:23:39 GMT で約 1 か月前だった。同じ索引の `wikibase-rdf.ttl.gz` は 2026-09-30 04:01 で当日更新されている。片方だけ止まっている。ダンプを使うときは説明文でなく `Last-Modified` を見て、それを基準日として記録する。

ダンプは全履歴なので大きい。 6.9 GB の gzip で、中身は全リビジョン。最新版だけが欲しくても全部を通す必要がある。`yuiseki/osm-wiki` はこの処理を済ませたもの ([huggingface-yuiseki/osm-wiki.md](../huggingface-yuiseki/osm-wiki.md) によると 2026-01-30 のダンプ 6,676,932,113 バイト由来)。今のダンプはそれより大きくなっている。

`articles` と `pages` を混同しない。 86,510 と 304,486 で 3.5 倍違う。リダイレクト、トークページ、テンプレートが後者に入っている。

wikitext は平文ではない。 テンプレート展開、表、言語間リンクが本文に混ざる。そのまま埋め込みに入れると記号が支配的になる。

## 学習ステップでの使いどころ (案)

- 地物の特徴量にはならない。座標が本文に無い。
- タグの意味を引く辞書として使う。`Key:` 6,720 と `Tag:` 8,538 のページが対象。日本語が要るなら JA 名前空間の 2,879 ページ。
- 数値が欲しいなら wiki を直接読むより taginfo ([../taginfo/README.md](../taginfo/README.md)) を使う。wiki は説明文、taginfo は使用回数という分担になっている。
