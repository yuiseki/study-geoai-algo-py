# World Bank (世界銀行のオープンデータ)

2026-09-30 に読んで確かめた内容。大きさと件数はこの日に実際に要求を投げて数えたもの。

- 世界銀行が公開している国別・年別の開発指標。中心は World Development Indicators (WDI)。
- 入口: `https://data.worldbank.org/`
- 一括配布: `https://databank.worldbank.org/data/download/`
- Indicators API: `https://api.worldbank.org/v2/`
- 派生物として `https://z.yuiseki.net/static/worldbank/` に WDI の抜き出しが 2 つある
  ([z-yuiseki-static/worldbank.md](../z-yuiseki-static/worldbank.md))。この項目はその上流。
- 新しい配信基盤 Data360 は [data360.md](data360.md)。

## データベースは 71 個ある

`https://api.worldbank.org/v2/source?format=json&per_page=100` が 71 件を返す。
WDI はそのうちの 1 つ (id=2)。`lastupdated` を持つので、更新の止まっているものが見分けられる。

| id | 名前 | 最終更新 |
|---|---|---|
| 2 | World Development Indicators | 2026-07-13 |
| 3 | Worldwide Governance Indicators | 2026-09-25 |
| 14 | Gender Statistics | 2026-07-22 |
| 16 | Health Nutrition and Population Statistics | 2026-07-01 |
| 40 | Population estimates and projections | 2026-07-01 |
| 75 | Environment, Social and Governance (ESG) Data | 2026-06-24 |
| 12 | Education Statistics | 2024-06-25 |
| 1 | Doing Business | 2021-08-18 |
| 11 | Africa Development Indicators | 2013-02-22 |

更新が止まって 10 年以上のものが混ざっている。Doing Business は 2021 年に世界銀行自身が
公表を取りやめた指標で、API には残っている。名前だけで選ばず `lastupdated` を見る。

## 一括配布の大きさ

`https://databank.worldbank.org/data/download/<名前>.zip` が
`https://databankfiles.worldbank.org/public/ddpext_download/<名前>.zip` に 301 する。

| ファイル | バイト | Last-Modified |
|---|---:|---|
| WDI_CSV.zip | 282,845,220 | 2026-07-15 |
| Gender_Stats_CSV.zip | 171,317,732 | 2026-07-22 |
| HNP_Stats_CSV.zip | 120,890,865 | 2026-07-01 |
| ASPIRE_CSV.zip | 109,892,761 | 2025-08-25 |
| EdStats_CSV.zip | 38,943,514 | 2023-01-18 |
| Jobs_CSV.zip | 34,157,783 | 2025-07-01 |
| ESG_CSV.zip | 15,069,896 | 2026-06-24 |
| SDG_CSV.zip | 12,575,040 | 2023-01-18 |
| IDS_CSV.zip | 11,142,704 | 2025-12-05 |
| WGI_CSV.zip | 3,336,633 | 2026-09-25 |
| GFDD_CSV.zip | 1,687,839 | 2023-01-18 |
| SE4ALL_CSV.zip | 339,440 | 2023-01-18 |
| WDI_EXCEL.zip | 81,695,278 | 2026-07-15 |

ここに挙げた 12 個の CSV を合わせて 802,199,427 バイト、765.0MiB。71 のデータベース全部に一括配布が
あるわけではなく、`GEM_CSV.zip` や `POP_Stats_CSV.zip` は 404 だった。
一括配布の名前は API のデータベース名から機械的には導けない。

`Last-Modified` は API の `lastupdated` と概ね一致する。WDI は API が 2026-07-13、
zip が 2026-07-15 で 2 日ずれている。

## zip の索引だけを Range で読める

`accept-ranges: bytes` を申告していて、実際に効く。`curl -r 0-1023` が 206 と
`content-range: bytes 0-1023/282845220` を返した。

zip の中央ディレクトリは末尾にあるので、そこだけ Range で取れば中身の一覧が分かる。
283MB のうち 409 バイト、全体の 0.0001% を読んで次の 6 件が列挙できた。

| メンバー | 展開後 | 格納後 | 時刻 |
|---|---:|---:|---|
| WDICSV.csv | 198,481,686 | 198,511,971 | 2026-07-15 02:18 |
| WDICountry.csv | 156,476 | 156,501 | 2026-07-15 02:18 |
| WDISeries.csv | 5,961,768 | 5,962,678 | 2026-07-15 02:18 |
| WDIcountry-series.csv | 1,362,558 | 1,362,768 | 2026-07-15 02:18 |
| WDIfootnote.csv | 76,824,428 | 76,836,153 | 2026-07-15 02:18 |
| WDIseries-time.csv | 14,388 | 14,393 | 2026-07-15 02:18 |

圧縮方式は deflate (compress_type=8) だが、格納後のほうが大きい。6 件すべてで
展開後より格納後が多く、圧縮が全く効いていない。283MB を落として得られるのは 282MB の CSV。
CSV は本来よく縮むので、配布側が非圧縮のブロックとして詰めていることになる。

そのおかげで、1 メンバーだけを Range で抜き出せる。`WDICountry.csv` を取り出すのに
実際に読んだのは 156,954 バイト、全体の 0.0555% だった。指標の定義表 `WDISeries.csv` も
同じ要領で 6MB だけ読めば足りる。

## 指標を 1 つだけ引く

指標ごとの CSV も配られている。

```
https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv
```

これが `application/zip` で 89,654 バイト。全人口 1 指標ならこれで済む。

## Indicators API

```
https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=32500
```

応答の 1 番目の要素がページ情報 (`page`, `pages`, `total`, `sourceid`, `lastupdated`)、
2 番目が値の配列。`SP.POP.TOTL` の全数は 17,490 行だった。

`per_page` の上限は 32,500 と 50,000 の間にある。32,501 は通り、50,000 は HTML の
エラーページが返った。JSON を期待して parse すると、そこで初めて失敗する。

指標の総数は 29,544。`https://api.worldbank.org/v2/indicator?format=json&per_page=1` の
`total` で分かる。

## country/all には集計地域が混ざる

`https://api.worldbank.org/v2/country?format=json&per_page=400` が 295 件を返す。
そのうち `region.id` が `NA` のものが 78 件あり、これが集計地域 (アフリカ東部、
アラブ世界、高所得国など)。差し引き 217 件が国と地域。

`country/all` はこの 295 件すべてを対象にする。国別の平均や回帰にそのまま入れると、
WLD (世界) や AFE (アフリカ東部) といった上位集計が 1 行の観測として混ざる。
除くには `region.id != 'NA'` で絞る。

217 という数は `z.yuiseki.net/static/worldbank/` の抜き出しが持っている国の数と一致する
([z-yuiseki-static/worldbank.md](../z-yuiseki-static/worldbank.md))。あちらは集計地域を
既に除いてある。

## ライセンス

`https://datacatalog.worldbank.org/public-licenses` の本文。

> The World Bank Group makes data publicly available according to open data standards
> and licenses datasets under the Creative Commons Attribution 4.0 International
> license (CC-BY 4.0). Many datasets are available under other licenses.

既定は CC BY 4.0。ただし素の CC BY 4.0 ではない。同じページが続けてこう書く。

> All users of these Datasets under the CC-BY 4.0 License also agree to the following
> mandatory terms:

その追加条項は紛争解決の手続きで、調停に応じること、45 日で解決しなければ仲裁に
移せること、仲裁地はライセンサーの本部であることを定めている。Data360 の API が
返すメタデータは同じ条項をもう少し具体的に書いており、調停は WIPO 調停規則、
仲裁は UNCITRAL 仲裁規則、場所はワシントン DC の世界銀行本部としている。

> This work is provided under a Creative Commons 4.0 Attribution International License,
> with the following mandatory and binding addition: i. Any and all disputes arising
> under this License that cannot be settled amicably shall be submitted to mediation
> in accordance with the WIPO Mediation Rules ...

できること。複製、改変、再配布、商用利用。share-alike は無い。

必要なこと。出典の表示と、変更したならその旨。

注意すること。SPDX でいえば CC-BY-4.0 に見えるが、追加条項がある以上 CC-BY-4.0 と
同一ではない。目録の上では `CC-BY-4.0` と書き、追加条項があることを併記するのが正確。
PLATEAU のサイトポリシーが CC BY を「許諾します」と書きながら他のライセンスを
「妨げるものではありません」と書き分けていたのと同じで、識別子だけでは落ちないものが残る。

既定でないものもある。同じページが ODbL、Microdata Research License、
License Specified Externally、Custom License、Data Not Available を挙げている。
Microdata Research License は再配布を禁じ、統計・科学研究目的に限り、
個人の再識別を試みないことを求める。世界銀行のものだから開いている、とは言えない。

実際にどれだけ混ざっているかは [data360.md](data360.md) に測った結果がある。

## 取り出し方

区分は range。一括 zip が Range を受け付け、中身が非圧縮なので、必要なメンバーだけ引ける。
split と catalog の性質も併せ持つ。

| 区分 | 手段 | 実測 |
|---|---|---|
| range | WDI_CSV.zip に Range | 索引 409 バイト (0.0001%)、1 メンバー 156,954 バイト (0.0555%) |
| split | 指標ごとの CSV zip | `SP.POP.TOTL` で 89,654 バイト |
| catalog | Indicators API | データベース 71、指標 29,544 を認証なしで列挙できる |
| whole | データベースごとの一括 zip | 最大の WDI_CSV.zip で 282,845,220 バイト |

全部を手元に置く場合。上に挙げた 12 のデータベースの CSV で 765.0MiB。
71 全部ではないので、これは下限。
