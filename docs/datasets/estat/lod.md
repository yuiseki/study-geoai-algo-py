# e-Stat 統計 LOD (日本の政府統計 LOD)

2026-09-30 に読んで確かめた内容。トリプル数と件数はこの日に SPARQL を投げて数えたもの。

- 総務省統計局が政府統計を RDF Data Cube で公開しているもの。運用は e-Stat。
- 入口: `https://data.e-stat.go.jp/lod/`
- SPARQL: `https://data.e-stat.go.jp/lod/sparql/alldata/query`
- 親項目は [README.md](README.md)。

認証は要らない。`SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }` がそのまま通り、
2,086,445,173 トリプルと返ってきた。20 億トリプルが公開のエンドポイントで引ける。

## グラフ

名前付きグラフごとのトリプル数。

| グラフ | トリプル |
|---|---:|
| gridCode | 1,103,554,640 |
| g00200521 (国勢調査) | 361,591,423 |
| smallArea | 334,489,853 |
| g00200502 (社会・人口統計体系) | 164,368,649 |
| g00200552 (経済センサス－基礎調査) | 70,815,804 |
| g00200561 | 49,338,847 |
| g00200523 | 659,898 |
| g00200573 | 645,250 |
| crossDomain | 504,281 |
| g00200564 | 232,498 |
| g00200524 | 161,526 |
| g00200531 | 15,458 |

全体の 53% が `gridCode`、つまり地域メッシュの定義そのもの。統計の値ではなく、
メッシュ番号と位置の対応が半分以上を占めている。

## メッシュは GeoSPARQL で置かれている

`gridCode` の 1 件を引くと次の形だった。

```
<http://data.e-stat.go.jp/lod/gridCode/G206445228914>
  a                     gridCode:GridCode5 ;
  dcterms:identifier    "206445228914" ;
  rdfs:label            "206445228914" ;
  gridCode:worldGridCode "206445228914" ;
  gridCode:japanGridCode "6445228914" ;
  gridCode:lat-NW       "42.9041667" ;
  gridCode:lat-SE       "42.9020834" ;
  gridCode:long-NW      "145.3656250" ;
  gridCode:long-SE      "145.3687500" ;
  geo:hasGeometry       <.../G206445228914/polygon> .
```

`geo:hasGeometry` の先に `geo:asWKT` がある。GeoSPARQL の関数も動く。

```sparql
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
SELECT (geof:sfWithin(
  'POINT(139.7 35.6)'^^geo:wktLiteral,
  'POLYGON((139 35,140 35,140 36,139 36,139 35))'^^geo:wktLiteral) AS ?r) WHERE {}
```

これが `true` を返した。語彙を借りているだけでなく、空間述語が実装されている。

## WKT リテラルの接頭辞が標準でない

ここが罠。`geo:asWKT` の値はこうなっている。

```
<http://xmlns.oracle.com/rdf/geo/srid/4612> POLYGON((145.3656250 42.9020834, ...))
```

GeoSPARQL は座標参照系を IRI で前置できると定めているが、そこに置かれているのが
OGC の `http://www.opengis.net/def/crs/EPSG/0/4612` ではなく Oracle の
`http://xmlns.oracle.com/rdf/geo/srid/4612` になっている。実装が Oracle なのだろう。

この文字列をそのまま shapely に渡すと落ちる。

```
GEOSException: ParseException: Unknown type: '<HTTP://XMLNS.ORACLE.COM/RDF/GEO/SRID/4612>'
```

接頭辞を切り落とせば普通に読める。SRID 4612 は EPSG:4612、JGD2000 の地理座標系。
つまり座標系そのものは e-Stat の他の配布物 ([estat-boundary](../estat-boundary/README.md) の
`.prj` が `GCS_JGD_2000`) と揃っている。食い違っているのは表記だけ。

読む側は `> ` で分割してから WKT として解釈し、座標系は 4612 だと自分で覚えておく。

## データセットは 87 件で、2015 年で止まっている

`?ds a qb:DataSet` を数えると 87 件。1 件はこういう記述を持っている。

```
dcterms:description  "年齢（5歳階級）別、男女別人口－小地域別"
rdfs:label           "年齢別、男女別人口－小地域別"
dcat:theme           <.../dataset/theme/field/field-0201>
dcterms:spatial      <.../terms/smallArea/SmallAreaCode>
dcterms:temporal     <.../ds012015003/PeriodOfTime>
cc:license           <http://creativecommons.org/licenses/by/4.0/>
cc:attributionName   "国勢調査" , "Population census"
cc:attributionURL    <http://www.stat.go.jp/data/kokusei/2015/index.htm>
qb:structure         <.../ds012015003/dsd>
```

`dcterms:temporal` の先に `schema:startDate` と `schema:endDate` がある。
これで調査ごとの収録年を数えた。

| 政府統計 | データセット | 期間 |
|---|---:|---|
| 国勢調査 | 52 | 2010 年 8 件、2015 年 44 件 |
| 社会・人口統計体系 | 24 | 1995 〜 2016 |
| 経済センサス－基礎調査 | 4 | 2014 |
| 消費者物価指数 | 2 | 2012-01 〜 2016-12 |
| 人口推計 | 1 | 2014 〜 2017 |
| 住民基本台帳人口移動報告 | 1 | 2014 〜 2017 |
| 全国消費実態調査 | 1 | 2014 |
| 労働力調査 | 1 | 2012-01 〜 2019-01 |
| 家計調査 | 1 | 2000-01 〜 2018-11 |

最新は労働力調査の 2019 年 1 月。VoID は `dcterms:created "2016-03-03"` を持つが
`dcterms:modified` を持たない。

これが効いてくる場面がある。[estat-boundary](../estat-boundary/README.md) が扱う
小地域境界は 2020 年国勢調査のものだが、統計 LOD には 2020 年国勢調査が入っていない。
境界を LOD 側の統計値と結ぼうとすると、同じ版では結べない。

## ライセンス

VoID の中で機械可読に宣言されている。

```
dcterms:license  <http://creativecommons.org/licenses/by/4.0/> ;
cc:license       <http://creativecommons.org/licenses/by/4.0/> ;
cc:attributionName  "政府統計の総合窓口(e-Stat)"@ja ;
cc:attributionURL   <http://www.e-stat.go.jp/> ;
```

データセット 1 件ごとにも `cc:license` が付いている。e-Stat の利用規約ページの
「CC BY に従うことでも利用することができます」という間接的な言い方ではなく、
CC BY 4.0 そのものを指している。SPDX でいえば CC-BY-4.0。

## ダンプは無い

`http://data.e-stat.go.jp/lod/page/download/` は 404。トップページから辿れる
リンクにもダンプは無い。VoID は `void:sparqlEndpoint` を宣言しているが
`void:dataDump` は宣言していない。20 億トリプルを手元に置く手段は用意されていない。

したがって、手元に持ちたい部分があるなら SPARQL で切り出して自分で貯める。

## 取り出し方

区分は catalog。SPARQL で必要な部分だけを引く。ダンプが無いので whole の選択肢は無い。

| 手段 | 実測 |
|---|---|
| SPARQL (GET、`query` を URL エンコード) | 認証不要。`application/sparql-results+json` を Accept で指定できる |
| 全数の COUNT | 2,086,445,173 を数え切って返した |
| 内容交渉 | 個別 IRI に `Accept: text/turtle` で Turtle が返る |
| ダンプ | 無い |

エンドポイントの URL は `/lod/sparql/alldata/query`。GET でも POST でも 200 が返る。
トップページが `void:sparqlEndpoint` として宣言している `/lod/sparql/` も、
`query` を渡せば 200 で答える。

HEAD だけは 405 を返す。生死確認に `curl -I` を使うと、動いているエンドポイントが
落ちているように見える。確かめるなら実際に短いクエリを投げる。
