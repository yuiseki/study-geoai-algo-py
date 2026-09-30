# uedayou.net

2026-09-30 に読んで確かめた内容。件数は各 SPARQL エンドポイントに投げた COUNT、出所とライセンスは各サイトの JavaScript バンドルに埋め込まれた本文。

- `https://uedayou.net/`。@uedayou が作った 22 のプロジェクトを並べたページ。
- 日本の公的データを Linked Open Data に変換したものが中心で、ほかに可視化アプリや実験がある。
- どのページも JavaScript で描くので、HTML を取っても本文が出てこない。出所とライセンスの記述はバンドル (`/assets/index-*.js`) の中にあり、この項目の引用はそこから取った。

## SPARQL エンドポイントを持つのは 2 つ

22 のうち、問い合わせられるのは次の 2 つだけ。ほかの 20 は `/sparql/` が 404 を返す。

| | [鉄道駅LOD](jrslod.md) | [住所LOD](loa.md) |
|---|---|---|
| URL | `https://uedayou.net/jrslod/` | `https://uedayou.net/loa/` |
| エンドポイント | `.../jrslod/sparql/query` | `.../loa/sparql/query` |
| トリプル | 1,152,137 | 39,458,434 |
| 主体 | 駅 10,145 | 住所型 147,407 |
| ライセンス | CC BY-SA 4.0 | CC BY-SA 4.0 |

画面の `/sparql/` は YASGUI で、実際の口はその下の `/query`。YASGUI のページの JavaScript に `endpoint: url + "/query"` と書いてある。

## 残りの 20

バンドルから拾ったパスの一覧。SPARQL は持たないので、この目録の対象としては道具か作品にあたる。

```
automaker  expo25view  jrslod-geojson-downloader  kyotobooks  ldapinavi
ld/library  loa/geojson-downloader  loa/puzzle  osakabridge  osakacrimemap
sagabridge  SPARQLTimeliner  SPARQLTimeliner/apps  SPARQLTimeliner/ukiyoe
SPARQLTimeliner/view  TimeMapper2RDF  trainview  yanevent2013  zannen9x
```

このうち 2 つは、ほかの LOD を使う側の道具なので性格が違う。

- `ldapinavi` は「Linked Data API Navi」。SPARQL エンドポイントを探すための検索サイト。
- `SPARQLTimeliner` は SPARQL の結果を年表として描くビューア。

`jrslod-geojson-downloader` と `loa/geojson-downloader` は、それぞれの LOD から GeoJSON を切り出す道具。RDF を扱わずに使いたい場合の入口になる。

## 取り出し方

catalog。SPARQL で必要な範囲だけ問い合わせるのが本筋で、一括ダウンロードは無い。

- 個別の IRI は内容交渉に応じる。`https://uedayou.net/loa/長崎県諫早市` に `Accept: text/turtle` を付けると 200 と `text/turtle; charset=UTF-8` が返る。IRI が日本語のまま使われている。
- 一括ダンプは無い。`dump.nt` のような名前を叩くと 200 が返るが、中身は SPA のフォールバックの HTML である。状態コードだけを見て存在すると判断すると間違える。実際に一度間違えた。ファイルの先頭を読めば `<!DOCTYPE html>` で分かる。
- 少し先のバイトを Range で要求すると 416 が返り、そこで実体の短さが分かる。

## ライセンスの組み立て方が読める

どちらのサイトも、上流のライセンスを並べたうえで自分のライセンスを導いている。結論だけでなく導出が書いてあるのが珍しい。

鉄道駅LOD の記述。

> 国土数値情報 鉄道データ・駅別乗降客数データ: https://nlftp.mlit.go.jp/ksj/other/agreement.html#agree-01
> Wikidata: https://www.wikidata.org/wiki/Wikidata:Licensing
> DBpedia 日本語版: https://creativecommons.org/licenses/by-sa/3.0/
> 本サイトでは、上記サイトのライセンスに従い CC BY-SA によりデータを提供します。

share-alike を持ち込んでいるのは DBpedia 日本語版の CC BY-SA 3.0 で、それが全体に伝播して CC BY-SA 4.0 になる。Wikidata は CC0 なので伝播させない。国土数値情報は独自約款。混ぜた結果いちばん強い条件が残る、という当たり前の計算を明示している。

この目録に取り込む側から見ると、CC BY-SA は share-alike なので、CC BY 4.0 で揃えたいデータセットには混ぜられない。

## 気をつけること

ページが JavaScript で描かれるので、出所もライセンスも HTML には無い。バンドルを読むか、画面を人が見るかのどちらかになる。機械で条件を確かめる用途には向かない。

`jrslod` は GeoSPARQL の語彙 (`http://www.opengis.net/ont/geosparql`) をバンドルに持つが、`hasGeometry` を持つ主体は 0 件だった。座標は geohash と WGS84 の緯度経度で持っている。GeoSPARQL の空間述語は使えない。

更新は続いている。鉄道駅LOD は 2026-08-28 に、令和 7 年 12 月 31 日時点の国土数値情報 N02 と S12 で更新されたと画面に書いてある。
