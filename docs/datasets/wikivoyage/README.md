# Wikivoyage

2026-09-30 に読んで確かめた内容。件数とライセンスは各言語版の MediaWiki API (`action=query&meta=siteinfo`)、ダンプの大きさと日付は `https://dumps.wikimedia.org/` の索引と `dumpstatus.json` が返した値。

- Wikimedia の旅行ガイド。`https://en.wikivoyage.org/` と `https://ja.wikivoyage.org/`。記事のほとんどが行き先 (都市、地区、公園) そのもので、座標が付いている。
- ダンプ: `https://dumps.wikimedia.org/enwikivoyage/` と `https://dumps.wikimedia.org/jawikivoyage/`。
- [Wikipedia](../wikipedia/README.md) と同じ MediaWiki で、同じ GeoData 拡張が座標を持つ。`siprop=extensions` を引くと en 版には `GeoData` のほかに `GeoCrumbs` 2.0.1 が入っている (地域の階層を辿るための拡張)。
- 派生データ: [huggingface-yuiseki/wikivoyage-geotagged.md](../huggingface-yuiseki/wikivoyage-geotagged.md)。この項目はその上流。

## ライセンス

`https://en.wikivoyage.org/w/api.php?action=query&meta=siteinfo&siprop=rightsinfo&format=json` が返した本文。ja 版も同じ文字列。

> Creative Commons Attribution-Share Alike 4.0

`url` は `https://creativecommons.org/licenses/by-sa/4.0/deed.en` (ja 版は `deed.ja`)。

Wikipedia と同じで、表示 (attribution) と継承 (share-alike) の両方が要る。本文を取り込んだデータセットは同じ CC BY-SA 4.0 で配るしかなく、CC0 の [Wikidata](../wikidata/README.md) と混ぜれば全体が share-alike 側になる。著者は記事の履歴にいるので、行に記事の URL を残す必要がある。

## 規模 (API が 2026-09-30T08:03Z に返した値)

| | en | ja |
|---|---:|---:|
| 記事 (articles) | 34,710 | 1,808 |
| ページ (pages) | 183,266 | 6,541 |
| 編集回数 | 5,370,304 | 59,119 |
| 直近に活動した利用者 | 1,082 | 77 |
| 本文の語数 (cirrussearch-article-words) | 49,939,142 | 1,391,527 |

en 版でも 34,710 記事しかない。同じ en の [Wikipedia](../wikipedia/README.md) (7,245,970) の 0.5% で、語数では 0.9%。ja 版は 1,808 記事で、実用的な網羅性は無い。言語版は全部で 27 (meta の `action=sitematrix` で、閉鎖されていないものを数えた)。

## ダンプ

索引に並んでいるディレクトリは en, ja とも 20251220, 20260101, 20260201, 20260301, 20260401, 20260501, 20260601, 20260701, 20260801, 20260901 の 10 版と `latest/`。20251220 だけが月の途中で、それ以降は月初 (1 日) だけ。2026-09-30 の時点で 20260901 より新しい版は無い。

古い版も残っている。`enwikivoyage/20251220/enwikivoyage-20251220-geo_tags.sql.gz` (469,137 バイト、Last-Modified 2025-12-21) は Range 要求に 206 を返した。9 か月前まで遡れる。

### 20260901 版のファイル

| ファイル | バイト数 | 作り終わった時刻 (UTC) |
|---|---:|---|
| enwikivoyage-20260901-pages-articles.xml.bz2 | 130,838,743 | 2026-09-01 11:06:21 |
| enwikivoyage-20260901-pages-articles-multistream.xml.bz2 | 134,029,357 | |
| enwikivoyage-20260901-geo_tags.sql.gz | 474,945 | 2026-09-01 11:03:17 |
| enwikivoyage-20260901-page.sql.gz | 5,522,585 | |
| enwikivoyage-20260901-page_props.sql.gz | 1,644,455 | |
| jawikivoyage-20260901-pages-articles.xml.bz2 | 6,149,672 | 2026-09-01 18:26:03 |
| jawikivoyage-20260901-pages-articles-multistream.xml.bz2 | 6,357,035 | |
| jawikivoyage-20260901-geo_tags.sql.gz | 18,342 | 2026-09-01 17:11:01 |
| jawikivoyage-20260901-page.sql.gz | 223,736 | |
| jawikivoyage-20260901-page_props.sql.gz | 190,206 | |

Wikipedia と違って分割版が無く、`pages-articles.xml.bz2` は 1 本だけ。en で 131 MB、ja で 6 MB なので手元に丸ごと置ける。`geo_tags` は en で 475 KB しかない。`latest/` の `jawikivoyage-latest-pages-articles.xml.bz2` は 6,149,672 バイトで 20260901 のものと一致した。

`dumpstatus.json` には md5 も入っている (例: enwikivoyage の pages-articles は `f54ef82a` で始まる)。

### 増え方

`enwikivoyage-geo_tags.sql.gz` は 2025-12-20 版で 469,137、2026-09-01 版で 474,945 バイト。9 か月で 1.2% しか増えていない。座標付きの記事はほぼ頭打ちと読める。

## 座標の取り出し方

- API で試せる。`https://en.wikivoyage.org/w/api.php?action=query&list=geosearch&gscoord=35.6812|139.7671&gsradius=10000&gslimit=5&format=json` は東京駅から 10 km 以内を返し、`Tokyo (prefecture)`, `Tokyo/Chuo`, `Tokyo/Ginza`, `Tokyo/Shinbashi`, `Tokyo/Chiyoda` の 5 件だった。
- 大量に要るならダンプの `geo_tags`。ページ ID しか持たないので、記事名には `page.sql.gz`、Wikidata の ID には `page_props.sql.gz` が要る。

## 気をつけること

`geo_tags` の属性の列が空。 派生データ側の実測では `gt_type`, `gt_country`, `gt_region`, `gt_name` が全 29,505 行で NULL、`gt_dim` が全行 1000。上で引いた geosearch も、返すのは `lat`, `lon`, `primary` だけで種類や国を返さない。Wikivoyage の側で書き込まれていないのが理由と読める。国別に集計したいなら `qid` で [Wikidata](../wikidata/README.md) を引くか、座標から判定する。

1 つの行き先が複数の記事に割れる。 上の geosearch が返した 5 件のうち 4 件が `Tokyo/Chuo` のような下位ページ。東京は 1 点ではなく、区ごとに座標を持つ十数点として入っている。都市を 1 点として数えると重複する。

en 版と ja 版で規模が 19 倍違う。 en が 34,710 記事に対し ja は 1,808。ja 版の geosearch を東京駅から 10 km で引くと東京駅、東京都、中央区、千代田区、港区、台東区、文京区、墨田区、新宿区、新宿駅の 10 件で、区の単位で止まっている。日本国内でも ja 版より en 版のほうが密度が高い。

行き先でない記事が混ざる。 派生データの記録では旅程 (航海)、旅の話題、会話帳にも座標が付き、3.3% が Wikidata の gazetteer に無い。座標が (0, 0) の記事も 2 件あり、どちらも航海の記事だった。

新しい版は月初にしか出ない。 2026-09-30 に見て最新は 20260901。最新の座標が要るなら API を使う。

Wikipedia 用に書いた本文抽出の処理をそのまま当てない。 Wikivoyage の記事は listing テンプレートに店名や住所を入れる。テンプレートを削る処理だと中身ごと消える。派生データではテンプレートを展開する側に倒している。
