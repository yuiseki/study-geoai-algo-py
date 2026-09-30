# 鉄道駅LOD

2026-09-30 に読んで確かめた内容。件数は SPARQL エンドポイントに投げた COUNT、出所とライセンスはサイトの JavaScript バンドルに埋め込まれた本文。

- `https://uedayou.net/jrslod/`。日本の鉄道駅を Linked Open Data にしたもの。
- エンドポイント: `https://uedayou.net/jrslod/sparql/query` (画面は `/sparql/` で YASGUI)
- 一覧は [README.md](README.md)。

## 規模

| 問い | 結果 |
|---|---:|
| 全トリプル | 1,152,137 |
| `a <https://uedayou.net/jrslod/Class/駅>` | 10,145 |
| `geosparql:hasGeometry` を持つ主体 | 0 |

## 出所

画面の記述より。

> 国土数値情報 鉄道データ
> 国土数値情報 駅別乗降客数データ
> Wikidata
> DBpedia 日本語版

版は次のとおり。

> 2026/08/28: 2025年（令和7年）12月31日時点の国土数値情報 鉄道データ および 駅別乗降客数データ をベースに更新しました。

国土数値情報の N02 (鉄道) と S12 (駅別乗降客数) にあたる。この 2 つは、先に調べた国土数値情報 110 コレクションのうち CC BY かつ全国を網羅している数少ないものである。再配布できる部分を選んで使っている。

## ライセンス

> 国土数値情報 鉄道データ・駅別乗降客数データ: https://nlftp.mlit.go.jp/ksj/other/agreement.html#agree-01
> Wikidata: https://www.wikidata.org/wiki/Wikidata:Licensing
> DBpedia 日本語版: https://creativecommons.org/licenses/by-sa/3.0/
> 本サイトでは、上記サイトのライセンスに従い CC BY-SA によりデータを提供します。

CC BY-SA 4.0。share-alike の出どころは DBpedia 日本語版の CC BY-SA 3.0 で、Wikidata (CC0) は伝播させない。

## 語彙

既定の問い合わせがバンドルに入っており、使っている語彙が分かる。

```
rdf rdfs owl foaf skos schema dc
ic      http://imi.go.jp/ns/core/rdf#          IMI コア語彙
wdt     http://www.wikidata.org/prop/direct/   Wikidata のプロパティ
dbpediaowl / propja                            DBpedia
jrslod  https://uedayou.net/jrslod/            自前
```

Wikidata のプロパティをそのまま使っている。`wdt:P137` が運営者、`wdt:P81` が路線。

`owl:sameAs` で Wikidata のエンティティに結ばれる。既定の問い合わせがその取り方を示している。

```
OPTIONAL {
  ?station owl:sameAs ?wikidata .
  FILTER(STRSTARTS(STR(?wikidata), "http://www.wikidata.org/entity/"))
}
```

## 取り出し方

catalog。SPARQL で必要な分だけ引く。一括ダンプは無い (`dump.nt` は 404)。

個別の IRI は内容交渉に応じ、`Accept: text/turtle` で Turtle が返る。

RDF を扱わずに使うなら `https://uedayou.net/jrslod-geojson-downloader/` がある。

## 気をつけること

GeoSPARQL の語彙をバンドルに持つのに、`hasGeometry` を持つ主体が 0 件である。座標は `<https://uedayou.net/jrslod/Property/geohash>` と WGS84 の緯度経度で持っている。GeoSPARQL の空間述語 (`sfWithin` など) は使えない。語彙が読み込まれていることと、それで問い合わせられることは別である。

駅 10,145 件は、同じ「駅」でも数え方が出どころによって違いうる。国土数値情報の駅は路線ごとの区間であり、人が 1 つと思う駅が複数の主体に分かれることがある。数を他の出典と突き合わせる前に、この定義を確かめること。
