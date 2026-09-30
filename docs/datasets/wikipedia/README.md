# Wikipedia

2026-09-30 に読んで確かめた内容。件数とライセンスは各言語版の MediaWiki API (`action=query&meta=siteinfo`)、ダンプの大きさと日付は `https://dumps.wikimedia.org/` の索引と `dumpstatus.json` が返した値。

- 百科事典の本文と、その記事に編集者が書いた座標。`https://ja.wikipedia.org/` と `https://en.wikipedia.org/`。
- ダンプ: `https://dumps.wikimedia.org/jawiki/` と `https://dumps.wikimedia.org/enwiki/`。言語版ごとにディレクトリが分かれる。
- 座標は MediaWiki の GeoData 拡張が持つ。`siprop=extensions` を引くと ja でも en でも `GeoData` が入っている (version は返らない)。
- 地理データとして使うときの上流は [Wikidata](../wikidata/README.md) と近い。Wikidata が構造化された値を持つのに対し、Wikipedia は本文と、その記事 1 件に付いた座標を持つ。
- 派生データ: [huggingface-yuiseki/wikipedia-geotagged.md](../huggingface-yuiseki/wikipedia-geotagged.md)。この項目はその上流。

## ライセンス

`https://ja.wikipedia.org/w/api.php?action=query&meta=siteinfo&siprop=rightsinfo&format=json` が返した本文。en も同じ文字列で、`url` の末尾だけ `deed.ja` と `deed.en` で違う。

> Creative Commons Attribution-Share Alike 4.0

`url` は `https://creativecommons.org/licenses/by-sa/4.0/deed.ja`。

表示 (attribution) と継承 (share-alike) の両方が要る。継承が付くので、本文を取り込んだデータセットは同じ CC BY-SA 4.0 で配るしかない。CC0 の [Wikidata](../wikidata/README.md) と混ぜると、全体が share-alike 側に引きずられる。座標だけを取り出した場合にどこまで share-alike が及ぶかは、API の rightsinfo だけでは決まらない (未確認)。著者を辿る先は記事の履歴なので、1 行 1 記事にするなら記事の URL を残す必要がある。

## 規模 (API が 2026-09-30T08:03Z に返した値)

| | ja | en |
|---|---:|---:|
| 記事 (articles) | 1,520,723 | 7,245,970 |
| ページ (pages、記事以外も含む) | 4,459,783 | 66,341,668 |
| 編集回数 | 111,008,021 | 1,372,869,965 |
| 利用者 | 2,763,765 | 54,739,296 |
| 直近に活動した利用者 | 24,995 | 266,550 |
| 本文の語数 (cirrussearch-article-words) | 1,671,360,209 | 5,291,610,850 |

`pages` は記事以外 (ノート、テンプレート、利用者ページ、リダイレクト) を全部数えた値で、`articles` の 3 倍から 9 倍ある。記事数として使うのは `articles` のほう。

言語版は全部で 348 (meta の `action=sitematrix` で、閉鎖されていないものを数えた)。

## ダンプ

索引 (`https://dumps.wikimedia.org/jawiki/`, `.../enwiki/`) に並んでいるディレクトリ。

- ja: 20260201, 20260301, 20260401, 20260501, 20260601, 20260701, 20260801, 20260901 の 8 版と `latest/`。
- en: 20260301 から 20260901 までの 7 版と `latest/`。
- どれも月初 (毎月 1 日) 始まり。2026-09-30 の時点で 20260901 より新しい版は無い。

古い版のファイルは消えていない。`jawiki/20260201/jawiki-20260201-geo_tags.sql.gz` (5,965,554 バイト、Last-Modified 2026-02-01) も `enwiki/20260301/enwiki-20260301-geo_tags.sql.gz` (52,266,122 バイト、Last-Modified 2026-03-05) も Range 要求に 206 を返した。半年から 7 か月前まで遡れる。`latest/` は最新版への別名で、`enwiki-latest-geo_tags.sql.gz` の Content-Length は 53,391,772 で 20260901 のものと一致した。

### 20260901 版のファイル (地理で使うもの)

| ファイル | バイト数 | 作り終わった時刻 (UTC) |
|---|---:|---|
| jawiki-20260901-pages-articles.xml.bz2 | 4,730,918,124 | 2026-09-02 13:57:37 |
| jawiki-20260901-pages-articles-multistream.xml.bz2 | 4,852,895,748 | 2026-09-02 13:57:37 |
| jawiki-20260901-geo_tags.sql.gz | 6,113,811 | 2026-09-02 13:25:51 |
| jawiki-20260901-page.sql.gz | 171,061,922 | |
| jawiki-20260901-page_props.sql.gz | 60,096,094 | |
| enwiki-20260901-pages-articles.xml.bz2 | 25,680,955,982 | 2026-09-03 20:49:41 |
| enwiki-20260901-pages-articles-multistream.xml.bz2 | 26,797,495,184 | 2026-09-03 20:49:41 |
| enwiki-20260901-geo_tags.sql.gz | 53,391,772 | 2026-09-03 18:00:33 |
| enwiki-20260901-page.sql.gz | 2,393,769,310 | |
| enwiki-20260901-page_props.sql.gz | 470,958,111 | |

`pages-articles.xml.bz2` は記事本文。`dumpstatus.json` には md5 も入っている (例: jawiki の pages-articles は `8beb2eb9b1e9c70826d0b05d19eea999`)。

`pages-articles` は分割版も同時に置かれる。ja は 7 本、en は 72 本。丸ごと 1 本で落とすと en は 25 GB になるので、途中で切れる環境では分割版のほうが扱いやすい。`multistream` は 100 ページごとに独立した bz2 ストリームになっていて、索引 (`-multistream-index.txt.bz2`) と組めば 1 記事だけを展開できる。連結版より 2% から 4% 大きい。

座標だけが要るなら `geo_tags.sql.gz` だけで足りる。ja で 6 MB、en で 53 MB しかない。ただし `geo_tags` はページ ID しか持たないので、記事名と名前空間には `page.sql.gz`、Wikidata の ID には `page_props.sql.gz` が要る。

### 増え方

同じファイルを版違いで比べると、7 か月で ja の `geo_tags` は 5,965,554 から 6,113,811 バイト (2.5% 増)、半年で en は 52,266,122 から 53,391,772 バイト (2.2% 増)。座標付き記事の伸びは年 4% から 5% ほどと読める。

## 座標の取り出し方

- ダンプ全体を落とさずに試すなら API。`https://ja.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord=35.6812|139.7671&gsradius=500&gslimit=10&format=json` は東京駅から 500 m 以内の記事を距離順に返した。1 件ずつは `prop=coordinates`。
- 大量に要るならダンプの `geo_tags` 表。派生データ ([wikipedia-geotagged](../huggingface-yuiseki/wikipedia-geotagged.md)) はこの経路で作られている。

## 気をつけること

座標がある記事が場所とは限らない。 東京駅から 500 m の geosearch を ja で引くと、5 件目までに「原敬暗殺事件」が入る。出来事や人物にも、起きた場所や生まれた場所として座標が付く。派生データの `provenance.yaml` は英語版の 6.1% が場所でないと書いている。場所だけが要るなら Wikidata の `instance_of` で絞るのが確実。

`pages` と `articles` を取り違えない。 en の `pages` は 66,341,668 で `articles` の 9 倍ある。ノートもテンプレートもリダイレクトも入っている。ダンプから作るなら名前空間 0 かつリダイレクトでないもの、と明示する。

ダンプの SQL 表はエスケープされたまま入っている。 派生データ側で、`geo_tags` の名前欄に `St John\'s College` のようなバックスラッシュが残る不具合が実際に出ている ([wikipedia-geotagged.md](../huggingface-yuiseki/wikipedia-geotagged.md))。XML ダンプ (本文と記事名) 側には出ない。SQL 表から読むなら unescape が要る。

版の日付とファイルの作成日は別。 20260901 の版でも、ja の `geo_tags` は 09-02、en の `pages-articles` は 09-03 に作られている。en は表とページ本文で 2 時間以上ずれる。厳密に同じ瞬間の状態ではない。

新しい版は月初にしか出ない。 2026-09-30 に見て最新は 20260901 で、ほぼ 1 か月前。最新の座標が要るなら API を使う。

本文の抽出は自明ではない。 wikitext からテンプレートと表と画像を落とす処理は、書き方を間違えると本文まで削る。派生データでは自己閉じの `<ref />` の扱いを誤って英語版の本文が 3,843,346,999 文字から 4,331,110,851 文字に増えた (削れていた分が戻った) 記録がある。自前で書くなら、抽出前後の文字数を必ず数える。

## 取り出し方

区分は range と catalog。2026-09-30 に curl で確かめた。

multistream のダンプは、この一覧の中で唯一「圧縮ダンプに対する Range が本当に役に立つ」例である。索引と本体の 2 本が対になっていて、両方が Range を受ける。

| ファイル | 大きさ (バイト) | Accept-Ranges | `-r 0-1023` |
|---|---:|---|---|
| `https://dumps.wikimedia.org/jawiki/20260901/jawiki-20260901-pages-articles-multistream.xml.bz2` | 4,852,895,748 | bytes | 206 / 1,024 バイト |
| `https://dumps.wikimedia.org/jawiki/20260901/jawiki-20260901-pages-articles-multistream-index.txt.bz2` | 31,357,252 | bytes | 206 / 1,024 バイト |
| `https://dumps.wikimedia.org/enwiki/20260901/enwiki-20260901-pages-articles-multistream-index.txt.bz2` | 284,375,992 | bytes | (索引の大きさの確認のみ) |

使い方は 2 段である。まず索引 (数十 MB) だけを落として展開する。中身は `オフセット:ページID:記事名` の 1 行 1 記事で、オフセットは本体の中でその記事を含む独立 bz2 ストリームが始まるバイト位置を指す。次に目当ての記事のオフセットから、索引で次に現れるオフセットの直前までを `Range` で取り、その断片だけを bzip2 で展開すると 100 ページ分の XML が出てくる。本体を 1 バイトも余計に読まずに 1 記事に届く。

実際に通した例は [Wikivoyage](../wikivoyage/README.md) の同じ節にある。ja の本体 6,357,035 バイトのうち 126,293 バイトだけを 206 で取って、目当ての記事を含む 100 ページを展開できた。jawiki でも構造は同一で、本体が 4.85 GB と大きいぶん効きが強い。

対照として、multistream でない `jawiki-20260901-pages-articles.xml.bz2` (4,730,918,124 バイト) も Accept-Ranges: bytes を返し `-r 0-1023` は 206 を返すが、これは意味が無い。1 本の連続した bz2 ストリームなので、途中のバイト列だけでは展開できない。Range が効くことと部分的に読めることは別である。

API は catalog として使える。`https://ja.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord=35.6812|139.7671&gsradius=500&gslimit=10&format=json` は 200 で 1,538 バイトを返し、東京駅から 500 m 以内の記事を距離つきで列挙した。範囲と件数を指定して選べるので、目録として使ってから本文を 1 件ずつ取る流れが組める。

SQL 表は split に近い。`jawiki-20260901-geo_tags.sql.gz` は 6,113,811 バイトで、座標だけが要るならこの 1 本を丸ごと落とせば済む。本文のダンプ全体は要らない。
