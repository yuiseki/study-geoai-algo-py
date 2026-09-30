# 住所LOD (Linked Open Addresses Japan)

2026-09-30 に読んで確かめた内容。件数は SPARQL エンドポイントに投げた COUNT、出所とライセンスはサイトの JavaScript バンドルに埋め込まれた本文。

- `https://uedayou.net/loa/`。日本の住所を Linked Open Data にしたもの。
- エンドポイント: `https://uedayou.net/loa/sparql/query` (画面は `/sparql/` で YASGUI)
- 一覧は [README.md](README.md)。

## 規模

| 問い | 結果 |
|---|---:|
| 全トリプル | 39,458,434 |
| `a <http://imi.go.jp/ns/core/rdf#住所型>` | 147,407 |

3,945 万トリプルは、この目録にある LOD の中で最も大きい。

## 出所

画面の表より。

| 段 | 出どころ | 版 |
|---|---|---|
| 都道府県・市区町村・行政区 | 国土数値情報 N03 (行政区域データ) | 2025年版 |
| 町丁目・丁目 | e-Stat 小地域境界データ | 2020年国勢調査 |
| 番地 (代表点) | 位置参照情報 (街区レベル) | 令和6年版 |

この目録に上流の項目がある。[estat-boundary](../estat-boundary/README.md) が小地域境界、位置参照情報 (ISJ) はまだ項目が無い。

## ライセンス

サイト全体の表示が CC BY-SA 4.0。画像には CC BY-SA 3.0 のものがあるが、これは Wikimedia Commons から取った都道府県旗などで、データ本体の条件ではない。

share-alike なので、CC BY 4.0 で揃えたいデータセットには混ぜられない。

## 構造

住所が階層で繋がっている。1 件を引いた例。

```
a                ic:住所型
都道府県           長崎県
市区町村           諫早市
parentFeature    https://uedayou.net/loa/長崎県諫早市
hasPart          (下位の住所へ、多数)
```

IRI が日本語のまま使われる。`https://uedayou.net/loa/長崎県諫早市` が実在の資源で、内容交渉に応じる。

YuisekinGeoSPARQL が `abr-muni` と `abr-pref` で表している包含関係と、同じ対象を別の語彙で表したものになる。あちらは GeoSPARQL の `sfWithin` で境界から計算した関係、こちらは `parentFeature` と `hasPart` で住所の表記から辿る関係で、根拠が違う。突き合わせると、住所の階層と空間の包含が食い違う場所が出るはずである (未確認)。

## 取り出し方

catalog。SPARQL で必要な分だけ引く。一括ダンプは無い。

個別の IRI は内容交渉に応じ、`Accept: text/turtle` で 200 と `text/turtle; charset=UTF-8` が返る。

GeoJSON で切り出す道具が `https://uedayou.net/loa/geojson-downloader/` にある。

## 気をつけること

`dump.nt` のような名前を叩くと 200 が返るが、中身は SPA のフォールバックの HTML である。状態コードだけで一括ダンプがあると判断すると間違える。少し先のバイトを Range で要求すると 416 が返り、実体が短いことで分かる。

3 つの出どころは版が揃っていない。行政区域が 2025 年版、小地域境界が 2020 年国勢調査、位置参照情報が令和 6 年版である。段によって時点が違うので、市町村合併をまたぐ期間の住所は上下で食い違いうる。

住所型 147,407 件は町丁目までの数であり、番地まで展開した数ではない。番地は代表点として別の段にある。
