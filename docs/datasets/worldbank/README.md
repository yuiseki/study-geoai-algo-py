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

## z.yuiseki.net の WDI の抜き出しのライセンス

2026-10-02 に調べた内容。対象は `https://z.yuiseki.net/static/worldbank/` の 2 ファイル
([z-yuiseki-static/worldbank.md](../z-yuiseki-static/worldbank.md))。
既定のライセンスと調停・仲裁の追加条項は上の「ライセンス」の節のとおりで、ここでは繰り返さない。

### どう作られたか

- 作成者は yuiseki。リポジトリは `repos/__yuiseki/_hf_data/wdi-to-parquet` で、コミットは 4 件、
  すべて 2026-05-31 16:38〜16:51 JST。リモートに公開されているか、スクリプト自体のライセンスは未確認。
- 取得元は指標ごとの zip。`https://api.worldbank.org/v2/en/indicator/<コード>?downloadformat=csv`
  から 2026-05-31 に取得し、`~/.cache/wdi-to-parquet/` に置いてある (zip の mtime は 16:42〜16:51)。
- 変換は zip 内の `API_*.csv` を読み、`Metadata_Country_*.csv` の Region が空の行 (集計地域) を落とし、
  指定した年を縦持ちにして値の無い行を捨てるだけ。単位変換や補完はしていない。
- 版。15 指標は zip 内 CSV の見出しが `"Data Source","World Development Indicators"`,
  `"Last Updated Date","2026-04-08"` で、2026-04-08 更新の WDI。
  EN.ATM.CO2E.PC だけは `"WDI Database Archives"` (source 57), `"Last Updated Date","2025-10-29"`。
- より新しい WDI がある。API の `https://api.worldbank.org/v2/source/2?format=json` は
  lastupdated 2026-07-13、データカタログの WDI ページは 2026-07-15 版。抜き出しは 1 世代古い。
- キャッシュの zip から同じ関数で作り直すと値が再現した。
  wdi_basic_annual.parquet は 16 指標 × 1990〜2024 年で完全一致。
  wdi_indicators.parquet は初回コミットの既定値 (6 指標 × 8 時点) で作り直して全 10,205 行のキーと値が一致した。
  ただし md5 は再生成物と一致せず、その理由は未確認。

### 16 指標のライセンス

`https://api.worldbank.org/v2/sources/{2|57}/series/<コード>/metadata?format=json` の
`License_Type` を 2026-10-02 に引いた。source 2 と 57 で同じ値だった。
出典組織は zip 内 Metadata_Indicator の SOURCE_ORGANIZATION の要約。
収録の min は wdi_indicators.parquet にも入っている 6 指標。

| コード | 名前 | ライセンス | 出典組織 | 収録 |
|---|---|---|---|---|
| SP.POP.TOTL | Population, total | CC BY 4.0 | UN Population Division (WPP), 各国統計局, Eurostat, UN Statistics Division | min, basic |
| SP.POP.GROW | Population growth (annual %) | CC BY 4.0 | 同上から導出 | min, basic |
| NY.GDP.MKTP.CD | GDP (current US$) | CC BY 4.0 | 各国公式統計, OECD, World Bank staff estimates | min, basic |
| NY.GDP.PCAP.CD | GDP per capita (current US$) | CC BY 4.0 | 同上 | min, basic |
| AG.SRF.TOTL.K2 | Surface area (sq. km) | CC BY 4.0 | FAO | min, basic |
| SP.URB.TOTL.IN.ZS | Urban population (% of total population) | CC BY 4.0 | UN Population Division (World Urbanization Prospects) | min, basic |
| SP.DYN.LE00.IN | Life expectancy at birth, total (years) | CC BY 4.0 | UN WPP, 各国統計局, Eurostat | basic |
| SP.DYN.TFRT.IN | Fertility rate, total (births per woman) | CC BY 4.0 | UN WPP, 各国統計局, Eurostat | basic |
| SH.DYN.MORT | Mortality rate, under-5 (per 1,000 live births) | CC BY 4.0 | UN IGME (UNICEF, WHO, World Bank, UN Population Division) | basic |
| SE.ADT.LITR.ZS | Literacy rate, adult total (% of people ages 15 and above) | CC BY 4.0 | UNESCO Institute for Statistics | basic |
| NY.GNP.PCAP.CD | GNI per capita, Atlas method (current US$) | CC BY 4.0 | 各国公式統計, OECD, World Bank staff estimates | basic |
| SI.POV.GINI | Gini index | CC BY 4.0 | World Bank Poverty and Inequality Platform (高所得国は主に Luxembourg Income Study) | basic |
| SL.UEM.TOTL.ZS | Unemployment, total (% of total labor force) (modeled ILO estimate) | CC BY 4.0 | ILO Modelled Estimates (ILOEST) | basic |
| EN.ATM.CO2E.PC | CO2 emissions (metric tons per capita) | CC BY-NC 4.0 | Climate Watch Historical GHG Emissions (1990-2020), World Resources Institute | basic |
| AG.LND.FRST.ZS | Forest area (% of land area) | CC BY 4.0 | FAOSTAT (FAO) | basic |
| IT.NET.USER.ZS | Individuals using the Internet (% of population) | CC BY 4.0 | ITU World Telecommunication/ICT Indicators Database | basic |

API の表記は CC BY 4.0 の行が `CC BY-4.0`、EN.ATM.CO2E.PC が
`Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)`。

- wdi_indicators.parquet の 6 指標はすべて CC BY 4.0 (追加条項つき)。
- wdi_basic_annual.parquet は 15 指標が CC BY 4.0、EN.ATM.CO2E.PC だけが CC BY-NC 4.0 (非商用)。
  出典は WRI の Climate Watch で、現行の WDI 本体ではなく WDI Database Archives から来ている。
  wdi_basic_annual.parquet の 102,623 行のうち 6,437 行 (約 6.3%) がこの指標。
  このファイルを CC BY 4.0 とだけ表示して配ると、指標のメタデータと食い違う。
- 既存ノートが報告した EN.ATM.CO2E.PC の重複と桁違いの値は、取得した上流の CSV にそのまま入っている。
  アーカイブ CSV は 292 行で、AND, COD, IMN, XKX, PSE, ROU, TLS が 2 行ずつ。
  ROU の 1990 年は 6.85 と 810.49、JPN は 1 行で 1990 年 1018.62。変換スクリプトの不具合ではない。

### Terms of Use for Datasets と表示の書式

本来の URL `https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets` は 2026-10-02 時点で
301 により一般の Terms and Conditions (`https://www.worldbank.org/ext/en/legal/terms-conditions`) へ
転送され、本文はそこに無い。本文は Wayback Machine の 2026-06-08 保存のコピー
`http://web.archive.org/web/20260608124135/https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets`
(末尾に「Last Updated: Mar 23, 2018」) で読んだ。

> You agree to provide attribution to The World Bank and its data providers in the following
> format: The World Bank: Dataset name: Data source (if known).

同じ書式は `https://data.worldbank.org/summary-terms-of-use` (2026-10-02 取得) にもある。
WDI ならたとえば「The World Bank: World Development Indicators: <指標の出典組織>」。
再配布するときは同じ表示要件をサブライセンスに含める必要があり、利用規約の URL を示せば足りると書かれている。
World Bank が推奨・関与していると示唆しないことも求められる。
第三者のデータについては「Where applicable, these conditions are included in the dataset or indicator metadata」とある。

### 未確認

- Terms of Use for Datasets の現行の本文。読めたのは Wayback の 2018 年版だけで、改訂や統合があったかは未確認。
- EN.ATM.CO2E.PC の上流である Climate Watch (WRI) 自身のライセンス。climatewatchdata.org の 2 つの URL を試したが 404 だった。
- 第三者出典 (ILO, ITU, UNESCO, FAO, UN 系, OECD, Eurostat, LIS) の側の条件。
  WDI のメタデータに制限の記載が無いことだけを確かめた。記載が無いことを制限が無いと読むのは規約の文言に依った解釈。

## Hugging Face の worldbank-wdi

2026-10-04 に <https://huggingface.co/datasets/yuiseki/worldbank-wdi> へ置いた。コードは
<https://github.com/yuiseki/wdi-to-parquet>。過去の版の取り方は [wdi-archives.md](wdi-archives.md)。

- 版は世界銀行の一括 zip ごと。現行の `WDI_CSV.zip` は更新のたびに上書きされるので Last-Modified の日付で、
  データカタログが残す `WDI_CSV_YYYY_MM_DD.zip` は名前の日付で呼ぶ。2026-10-04 時点で 7 版 (2024-05-30〜2026-10-01)。
  カタログの 2026_10_01 は現行の zip と sha256 が同じだった。
- 指標ごとのライセンス (WDISeries.csv の License Type) は版によって変わる。SIPRI の軍事支出は 2024-05-30 と
  2026-10-01 では SIPRI の条件、その間の版では `CC BY-4.0`。IEA のエネルギーと WDPA の保護区は 2024-05-30 だけ
  提供元の条件で、以後は `CC BY-4.0`。出典は変わっていない。そこで、どれかの版で CC BY 以外か空の 74 指標を全版から除いた。
- 2026-02-25 の CSV は数値を有効数字 11 桁まで (多くは 10 桁) で書いている。ほかの版は 17 桁まで。
- 2026-07-15 と 2026-10-01 は値が同じで、指標の説明だけが違う。
- 脚注の Year は末尾に空白の付いたもの (2026-10-01 で 27,992 行) と小文字の yr2005 (92 行) が混ざる。
