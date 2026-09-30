# Wikidata

2026-09-30 に読んで確かめた内容。大きさはダンプの索引が返したバイト数、件数は MediaWiki API と Query Service。

- `https://www.wikidata.org/`。Wikimedia の構造化データ。項目 (Q) とプロパティ (P) の集まり。
- ダンプ: `https://dumps.wikimedia.org/wikidatawiki/entities/`。
- 問い合わせ: `https://query.wikidata.org/sparql` (SPARQL、User-Agent が要る)。1 項目だけなら `https://www.wikidata.org/wiki/Special:EntityData/Q42.json`。
- 既に `yuiseki/wikidata-gazetteer` の出典として使っている ([huggingface-yuiseki/wikidata-gazetteer.md](../huggingface-yuiseki/wikidata-gazetteer.md))。この項目はその上流。

## ライセンス

API (`action=query&meta=siteinfo&siprop=rightsinfo`) が返した本文。

> All structured data from the main and property namespace is available under the Creative Commons CC0 License; text in the other namespaces is available under the Creative Commons Attribution-ShareAlike License; additional terms may apply.

構造化データは CC0。地理データとしてはこれ以上緩いものがほとんど無い。ただし main と property の名前空間だけ で、それ以外 (Wikidata:、Help: など) の文章は CC BY-SA。取り込むのが項目のステートメントなら CC0、解説文を混ぜると share-alike が付いてくる。

## 規模

- ページ 129,291,984、うち項目 123,512,974。編集回数は 2,550,629,614。
- 座標 (P625) を持つ項目は 12,437,128 (Query Service で数えた)。

## ダンプ

索引には 20 版が並び、2〜3 日おきに作られている (2026-08-17 から 2026-09-30 まで)。`latest-*` はそのうち最新へのリンク。

| ファイル | バイト数 | 作られた日 |
|---|---:|---|
| latest-all.json.bz2 | 103,272,886,026 | 2026-09-29 |
| latest-all.json.gz | 156,315,459,742 | 2026-09-29 |
| latest-all.ttl.bz2 | 125,670,694,752 | 2026-09-28 |
| latest-all.nt.bz2 | 588,138,969,914 | 2026-09-29 |
| latest-truthy.nt.bz2 | 43,489,023,865 | 2026-09-27 |

`truthy` は「最良ランクのステートメントだけ」を落としたもの。全体の 1/13 で済むので、出典や順位が要らない用途はこちらで足りる。

`latest-*` のファイルごとに作られた日が 1〜2 日ずれている。同じ日の状態を揃えたいなら日付入りのディレクトリ (`20260930/`) を使う。

## 気をつけること

`yuiseki/wikidata-gazetteer` を作るときに踏んだ罠は [huggingface-yuiseki/wikidata-gazetteer.md](../huggingface-yuiseki/wikidata-gazetteer.md) 側に書いてある。上流の性質として繰り返しておく。

ラベルと別名が混ざる。 `names` には `kind` が `label` と `alias` の両方あり、絞らないと大阪府の日本語名が「おおさかふ」(読み仮名) になる。

`instance_of` は時制を持たない。 `Q50337` (都道府県) で引くと 47 でなく 50 件返る。余分は堺県 (1881 年廃止)、樺太庁、東京府。廃止 (P576) を除くか、件数を既知の値と突き合わせる。

数値は出典付きでも間違っている。 富士山 (Q39231) の標高は 3777.24m (normal rank、出典 1 件) だが、国土地理院は 3776m。CC0 で機械可読という利点の裏側。

点しか無い。 P625 は代表点で、境界は持たない。「富士山は山梨県と静岡県にまたがる」は点と境界からは計算できない (実測: 富士山の点は静岡県の内側 278m、山梨県から 379m)。境界が要るなら [geoBoundaries](../geoboundaries/README.md) か国土数値情報。
