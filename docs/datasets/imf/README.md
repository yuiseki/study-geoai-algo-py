# IMF Data (国際通貨基金の統計データ、SDMX API)

2026-10-04 に読んで確かめた内容。

測り方:

- `api.imf.org` の SDMX API には curl と Python 標準ライブラリで直接要求を投げた。鍵 (subscription key) なしで 200 が返った。構造 (dataflow、datastructure、availableconstraint) の応答を数え、データ本体は 1 系列の小さい応答と、系列の一覧だけを返す `detail=nodata` の応答を取った。全体の大きさは配布元が付けている系列数の注記 (`series_count`) から数えた。データ本体の一括取得はしていない。
- `www.imf.org` と `data.imf.org` は、規約、WEO のページ、ファイル (`/-/media/...`) のどれも curl に 403 を返した。応答ヘッダは `server: AkamaiGHost` で、本文は「Access Denied」。Akamai のボット対策であり、ページが無いのではない (Internet Archive には同じ URL の 200 の保存がある)。そのため Internet Archive の保存 (`web.archive.org/web/<時刻>id_/...`) で読んだ。使った保存の時刻はそれぞれの所に書く。
- 古い API `dataservices.imf.org` と古い画面 `legacydata.imf.org` は、2026-10-04 に名前解決ができなかった (`Could not resolve host`)。

## 入口

- 画面: <https://data.imf.org/> (IMF Data portal)
- API: <https://api.imf.org/external/sdmx/2.1/> (SDMX 2.1) と <https://api.imf.org/external/sdmx/3.0/> (SDMX 3.0)
- API の説明: <https://data.imf.org/en/Resource-Pages/IMF-API> (Internet Archive の 2026-09-16 の保存)。Swagger のページ <https://portal.api.imf.org/apis#tags=iData> はサインインが要る (`/signin` へ 302)。API そのものはサインインなしで使えた。
- WEO: <https://data.imf.org/en/datasets/IMF.RES:WEO>。2025 年 4 月の版までは <https://www.imf.org/en/Publications/WEO/weo-database/2025/april> の形のページ。
- 利用規約: <https://www.imf.org/en/about/copyright-and-terms> (ページ名は「Copyright and Usage」)。古い URL `https://www.imf.org/external/terms.htm` は 2024-11 から 301 で `www.imf.org/redirect/?URL=...` に回される (Internet Archive の CDX で 2024-10-07 までは 200、2024-11-08 以降は 301)。data.imf.org の画面の足元の「Copyright and Usage」は今も `terms.htm` を指している。

## 作成

- 作成者は国際通貨基金 (IMF)。データフローごとの作成部局は SDMX の `agencyID` に出る。`api.imf.org/external/sdmx/2.1/dataflow` が返した 223 件の内訳は次のとおり。

| agencyID | 件数 |
|---|---:|
| IMF.STA (統計局) | 191 |
| IMF.RES (調査局) | 10 |
| IMF.FAD (財政局) | 8 |
| IMF.WHD | 3 |
| ISORA | 3 |
| IMF.SPR | 2 |
| IMF.AFR | 2 |
| IMF.APD | 2 |
| IMF.MCD | 1 |
| IMF.MCM | 1 |

- `ISORA` は IMF の部局ではない。データの属性 `SHORT_SOURCE_CITATION` は「ADB, CIAT, IMF, IOTA and OECD, International Survey on Revenue Administration」で、複数機関の共同の調査。
- 一次配布元は IMF Data portal と、その裏の SDMX API。API の説明のページ: 「Our data are available through SDMX 2.1 and SDMX 3.0 APIs. You can use the APIs to import data from datasets available on http://data.imf.org into your data systems or applications.」
- 新しい portal への移行: data.imf.org の 2025-03-30 の保存の帯に「The new IMF Data Portal is LIVE. You may continue to access the retired system at legacydata.imf.org until May 31, 2025.」とある。上のとおり legacydata.imf.org は今は名前解決できない。
- IFS (International Financial Statistics) は単独のデータベースとしては廃止された。portal のお知らせ「Accessing International Financial Statistics (IFS)」(2025-03-24、Internet Archive の 2025-03-30 の保存) の表は IFS を「Discontinued as a single Dataset, Data by topic remains」とし、主題ごとに CPI、ER、EER、IL、FA、LS、PI、PPI、ITG、BOP、IIP、SPE、QGFS、NEA (年次・四半期)、MFS (中央銀行、預金取扱機関など 5 つ) の各データフローへ振り分けている。DOT (Direction of Trade) に当たる相手国別の貿易は `IMTS` (International Trade in Goods (by partner country)) にある。
- WEO は 2025 年 10 月の版から portal へ移った。www.imf.org の「World Economic Outlook Databases」のページ (Internet Archive の 2026-06-07 の保存): 「As of October 2025, the World Economic Outlook database and supporting documents will be accessible through the IMF Data portal.」
- 世界銀行の Data360 も IMF のデータベースを載せている ([../worldbank/data360.md](../worldbank/data360.md) の `IMF_BOP`、`IMF_IFS`、`IMF_GFS_SOO` など)。ライセンス欄は `License Specified Externally` で、URI は `https://www.imf.org/external/terms.htm`。条件は下の IMF の規約で、Data360 は二次配布。`IMF_IFS` の元の IFS は上のとおり IMF 側ではもう単独では無い。

## 中身

### データフローは 223 件、うち 119 件が版の写し

`https://api.imf.org/external/sdmx/2.1/dataflow` (SDMX-ML 2.1、447,879 バイト) が 223 件を返した。SDMX 3.0 の `structure/dataflow/*/*/+` も同じ 223 件だった。

- 現行のデータフローが 104 件。
- ID が `_VINTAGE` で終わる、ある時点の写しが 119 件 (下の「版」)。
- 名前は 222 件が英語だけで、`COFER` だけが 8 言語 (ar、ru、pt、ja、en、fr、es、zh) を持つ。

### 量

系列数は `https://api.imf.org/external/sdmx/2.1/availableconstraint/<agency>,<id>,<version>/all/all/all` が返す実在制約の注記 (`series_count`、`time_period_start`、`time_period_end`) から、223 件すべてについて数えた。観測数の注記は無い。

- 現行 104 件の系列数の合計は 9,067,668。版の写し 119 件の合計は 3,236,964 で、そのうち 35 件は系列数 0 だった。
- 期間は全体で 1800 年 (`HPD`、Historical Public Debt) から 2051 年 (予測を含むもの) まで。

系列数の多いものと、よく使われるもの:

| データフロー | 名前 | 系列数 | 期間 | 主な次元 |
|---|---|---:|---|---|
| IMF.STA `PIP` | Portfolio Investment Positions by Counterpart Economy (formerly CPIS) | 3,140,582 | 1997-2025 | 国 248 × 相手国 248 × 指標 60 × 部門 |
| IMF.FAD `TAXFIT` | Tax and Benefits Analysis Tool | 1,048,575 | 2022-2023 | 国 19 × 世帯の型 |
| IMF.STA `DIP` | Direct Investment Positions by Counterpart Economy (formerly CDIS) | 819,948 | 2009-2025 | 国 259 × 相手国 259 |
| IMF.STA `GFS_SOO` | GFS Statement of Operations | 715,824 | 1972-2026 | 国 195 × 指標 232 × 部門 8 |
| IMF.STA `IMTS` | International Trade in Goods (by partner country) | 473,329 | 1948-2026 | 国 237 × 相手国 245 |
| IMF.STA `BOP` | Balance of Payments | 404,758 | 1948-2026 | 国 213 × 指標 721 |
| IMF.STA `CPI` | Consumer Price Index | 28,811 | 1900-2026 | 国 202 × COICOP 13 |
| IMF.STA `ER` | Exchange Rates | 10,730 | 1924-2027 | 国 227 × 指標 10 |
| IMF.RES `WEO` | World Economic Outlook | 8,200 | 1980-2032 | 国・地域 210 × 指標 145、年次のみ |
| IMF.RES `PCPS` | Primary Commodity Price System | 1,270 | 1946-2026 | 指標 124 |
| IMF.STA `COFER` | Currency Composition of Official Foreign Exchange Reserves | 140 | 1995-2026 | 通貨 14 |

`TAXFIT` の 1,048,575 は Excel の行数の上限 (2^20 - 1) と同じ値で、切り詰められている可能性がある。確かめていない。

GFS (政府財政統計) は `GFS_SOO`、`GFS_BS`、`GFS_COFOG`、`GFS_SFCP`、`GFS_SOEF`、`GFS_SSUC` の 6 つに分かれ、合わせて 1,668,700 系列。

### WEO の中身

- `IMF.RES:WEO` 9.0.0 の系列を `detail=nodata` で一覧にした (5,808,471 バイト) ところ、8,200 系列、国・地域 210 (ISO 3 文字の国 197 と、`G001` 世界などの集計 13)、指標 145、頻度は年次だけだった。
- 日本の実質 GDP 成長率 (`JPN.NGDP_RPCH.A`) は 1980 年から 2031 年までの 52 観測。2032 年までの中期予測を持つ系列もある (制約の終わりが 2032)。
- データセットの属性は `PUBLICATION_DATE="2026-04-14T13:00:00Z"`、`UPDATE_DATE="2026-04-15T13:00:00Z"`。今の WEO は 2026 年 4 月の版。
- 2025 年 10 月の版から国の識別子が IFS の 3 桁の数字から ISO の 3 文字に変わった。集計は `1` が `G001` (World) のように頭に `G` か `GX` が付いた。WEO Database Transition Guide (as of April 1, 2026、Internet Archive の 2026-05-17 の保存) の表による。

### 地域の単位

国が単位で、国より細かい地域は無い。座標や境界の形状は含まれない。

### 形式

- API: SDMX-ML 2.1 (structure-specific)、SDMX-JSON、SDMX-CSV 2.0 (`Accept: application/vnd.sdmx.data+csv;version=2.0.0` で 1 行目が `STRUCTURE[;],STRUCTURE_ID,ACTION,COUNTRY,...` の CSV が返った)。
- WEO の静的ファイル (portal の WEO のページ、Internet Archive の 2026-09-23 の保存): 「April 2026 WEO Entire Dataset in Excel」(`WEOApr2026all.xlsx`、Countries、Country Groups、Commodity Prices などのシート)、「April 2026 WEO Database Appendix」(PDF)、「WEO Historical Forecasts Database」(`WEOhistorical.xlsx`)。Internet Archive の CDX の記録では `WEOApr2026all.xlsx` が 5,494,799 バイト、`WEOhistorical.xlsx` が 9,415,451 バイト (2026-04-15 の保存)。
- 2025 年 4 月までの www.imf.org の WEO のページは、「By Countries」(`weoapr2025all.xls`、19 MB と表示)、「By Country Groups」(`weoapr2025alla.xls`、1 MB)、「SDMX Data」(`weoapr2025-sdmxdata.zip`、28 MB と表示) の 3 つを配っていた (Internet Archive の 2026-05-12 の保存)。Transition Guide によると、2 つの Excel は 1 つの「(Vintage) WEO Entire Dataset in Excel」にまとめられ、SDMX のファイルは API に置き換えられた。
- 項目の数: Transition Guide によると、portal の「Download」ボタンの一括ダウンロードは項目が 68 個 (旧来の一括ファイルは 10 個)。

## 配布

- 一括配布の静的ファイルは WEO などごく一部 (上の Excel)。それ以外のデータフローの一括取得は API か画面の「Download」ボタン。Transition Guide は portal の機能として「bulk downloads, application programming interfaces (APIs)」を挙げている。
- 静的ファイルは data.imf.org の `/-/media/iData/External-Storage/Documents/<32 桁の ID>/en/<名前>` に置かれる。ファイル名から URL を組み立てることはできない (ID が版ごとに違う)。curl からは Akamai の 403 で、HEAD でも大きさは取れなかった。
- API の応答には `cache-control: no-cache, no-store` が付き、`server: istio-envoy`。回数制限を示すヘッダは無く、今回の数百回の要求 (1 秒以上あけた) では 429 は出なかった。重い要求は遅く、`detail=nodata` の 1 回に数十秒かかるものがあった。
- 古い DataMapper API (`https://www.imf.org/external/datamapper/api/v1/`) は Internet Archive に 2026-08 の 200 の保存があり、今も動いていると考えられるが、ここからは Akamai の 403 で確かめられなかった。

## 取り出し方

区分は catalog。主な使い方は、構造の問い合わせで目録を読んでから、データフローと次元の値で絞ったデータを引くこと。WEO の Excel は whole (1 ファイル、約 5.5MB)。range には当たらない。

- 目録: `dataflow` (一覧)、`datastructure` (次元と属性)、`availableconstraint` (今あるコードの組、系列数、期間)。
- 絞り方: 次元の値を `.` で区切ったキー (`JPN.NGDP_RPCH.A`)、空欄で全部。SDMX 2.1 は `data/<agency>,<id>[,<version>]/<key>`、SDMX 3.0 は `data/dataflow/<agency>/<id>/<version>/<key>` (最新は `+` を `%2B` にして渡す)。
- HTTP Range: `curl -r 0-1023` は 206 ではなく 200 で全体 (6,533 バイト) を返した。`accept-ranges` ヘッダは無かった。
- 系列の一覧だけなら `detail=nodata` で取れる (WEO で 5.8MB)。

## ライセンス

### 規約の本文

<https://www.imf.org/en/about/copyright-and-terms> を、Internet Archive の 2026-06-25 06:18 の保存 (`https://web.archive.org/web/20260625061819id_/https://www.imf.org/en/about/copyright-and-terms`) で 2026-10-04 に読んだ。本体は curl に Akamai の 403 を返したので直接は読めていない。改定日の記載は無い。

一般の条項 (General Terms and Conditions of Usage) は「All Rights Reserved」が前提で、個人の非商用の利用だけを許す。

> Unless stated otherwise, the Content presented on the IMF Sites are the intellectual property of the IMF and are published "All Rights Reserved."

> The IMF allows free non-systematic downloading and/or printing of Content from its Sites by Users for personal, noncommercial usage only without any right to resell, redistribute, compile, or create derivative works.

> Permission is required to copy or download IMF Content in any systematic way or to re-use, publish, and disseminate a substantial amount beyond "Fair Use," whether for commercial or noncommercial purposes.

> The IMF prohibits the bulk download of information by automated technology without explicit permission and reserves the right to terminate access to its Sites or Content.

> The IMF does not permit use of its Content or Sites for the training of large language models (LLMs) without explicit permission.

統計データには特別の条項 (The Use of IMF Data) があり、一般の条項より緩い。

> Notwithstanding the general prohibition on the commercial use of IMF Content, with respect to published statistical data made available on IMF Sites, the following special terms shall govern.

> For the purposes of these special terms, the term "Data" refers to any published statistical data produced or curated by the IMF. In particular, "Data" refers to the following:
> IMF Statistical Data, including but not limited to, International Financial Statistics (IFS), Balance of Payments (BOP), Direction of Trade (DOT), and Government Finance Statistics (GFS);
> World Economic Outlook database;
> Primary Commodity Prices;
> IMF Financial Data;
> Exchange Rate Data; and
> Most statistical data available on www.IMF.org, www.data.IMF.org, or the iData Portal that explicitly identify the International Monetary Fund as the source.
> Note:
> Some statistical products may incorporate information from third parties and may have separate terms and conditions for usage.

> You may download, extract, copy, create derivative works, publish, distribute, and use Data obtained from IMF Sites, subject to the following conditions:
> Whether obtained directly from the IMF or another party, when Data is distributed or reproduced in any manner, it must appear accurately with attribution to the IMF as the source, e.g. "Source: International Monetary Fund, Database Name, <<link to the dataset>>."
> Users shall not infringe upon the integrity of the Data and in particular shall refrain from any act of alteration of the Data that intentionally affects its nature or accuracy. If the Data is materially transformed by the User, this must be stated explicitly along with the required source citation.
> Users who make IMF Data available to other Users through any type of distribution or download environment agree to take reasonable efforts to communicate and promote compliance by their users with these terms.
> If IMF Data is sold by Users as a standalone product, sellers must inform purchasers that the Data is available free of charge from the IMF.

> Except as stated in this Section on Data Usage, all other terms set forth in the general terms and conditions shall continue to apply to use of IMF Data.
> For any potential commercial reuse of IMF Data, please email copyright@imf.org to request permission.

### 2024 年 11 月の改定で商用の許可が消えた

`https://www.imf.org/external/terms.htm` の Internet Archive の 2024-10-07 09:05 の保存 (`https://web.archive.org/web/20241007090557id_/https://www.imf.org/external/terms.htm`) の「SPECIAL TERMS AND CONDITIONS PERTAINING TO THE USE OF DATA」は、商用を明示的に許していた。

> Users may download, extract, copy, create derivative works, publish, distribute, and sell Data obtained from IMF Sites, including for commercial purposes, subject to the following conditions:

今の版ではこの文の「and sell」と「including for commercial purposes」が消え、末尾に「For any potential commercial reuse of IMF Data, please email copyright@imf.org to request permission.」が加わった。一般の条項も変わった。2024-10-07 の版の自動化された取得の条項は「The IMF reserves the right to terminate access to its Sites or Content by automated technology (including but not limited to bots, spiders and crawlers) for the purposes of bulk downloading IMF publication files.」で、出版物のファイルについて利用を止める権利を留保するだけだった。今の版は情報一般の自動化された一括ダウンロードを許可制にし、LLM の学習の条項 (2024-10-07 の版には無い) を加えている。copyright-and-terms のページの保存を順に調べると、2024-11-19、2025-04-05、2025-07-14、2025-09-27、2025-10-23、2026-01-06、2026-06-25 のどれも今の文面 (商用は要問い合わせ、一括ダウンロードと LLM の学習は要許可) だった。改定は 2024-10-07 から 2024-11-19 の間で、`terms.htm` が 301 に変わった時期 (2024-11-08) と重なる。

「IMF は商用の再配布に許可を求める」は今の文面については当たっている。ただし 2024 年 10 月までは逆に商用を明示的に許していた。

### データに付いたライセンスの属性

API のデータの応答には、データセットの属性として `LICENSE` と `SUGGESTED_CITATION` が付く。WEO の値:

- `LICENSE="© International Monetary Fund Copyright. All Rights Reserved. https://www.imf.org/external/terms.htm"`
- `SUGGESTED_CITATION="International Monetary Fund. World Economic Outlook (WEO), https://data.imf.org/en/datasets/IMF.RES:WEO. Accessed on [current date]."`

現行 104 件のうち WEO を含む 21 件で `detail=nodata` を取って `LICENSE` を見た。

| LICENSE の値 | 件数 | データフロー |
|---|---:|---|
| © International Monetary Fund Copyright. All Rights Reserved. https://www.imf.org/external/terms.htm | 13 | WEO、BOP、BOP_AGG、COFER、CPI、CTOT、FFS、GFS_SOO、HPD、IIPCC、INFORMRISK、NDGAIN、PCPS |
| 属性なし | 7 | AEA、FM、GS_LGRGHTS、NA_MAIN、QGDP_WCA、SRD、UNFCCC |
| https://data.imf.org/en/Datasets/RAFIT-Consolidated/Terms-and-Conditions | 1 | ISORA_LATEST_DATA_PUB |

BOP と IIPCC は `©` が UTF-8 として不正なバイトになっていて、文字化けした。

- 属性が無いデータフローがあり、API の応答だけでは条件が分からないものがある。
- `NDGAIN` (IMF-Adapted ND-GAIN Index) と `INFORMRISK` (Climate-Driven INFORM Risk Indicator) は名前から外部の指標 (ノートルダム大学の ND-GAIN、INFORM) を加工したものと読めるが、`LICENSE` は IMF の著作権表示で、外部の条件は書かれていない。規約の「Some statistical products may incorporate information from third parties」に当たるかどうかは、API からは機械的に決められない。
- ISORA の条件は別のページ「ISORA Data Portal - Terms and Conditions of Data Access and Use」(Internet Archive の 2026-05-17 の保存) で、IMF の規約とは違う。「A. Users may publish ISORA data, provided that the publication source is appropriately acknowledged.」とし、利用者に ADB、CIAT、IMF、IOTA、OECD への補償 (indemnify) を求める。

### 読み取れること

- 再配布: 統計データ (Data) については規約が「distribute」を認める。出典の表示と、受け取る側への条件の周知が条件。ただし一般の条項の「bulk download ... by automated technology without explicit permission」の禁止は、データの節が「all other terms ... shall continue to apply」としているので、データにも及ぶと読める。API で全データフローを機械的に取ることは、この文面では許可が要る。
- 商用利用: 2024 年 11 月以降の文面では copyright@imf.org への許可の依頼が要る。
- 改変: 「create derivative works」は認められる。大きく変えたときはその旨を出典と一緒に明記する。値の正確さを損なう改変は禁止。
- 出典表示: 必須。形の例は「Source: International Monetary Fund, Database Name, <<link to the dataset>>.」。データには `SUGGESTED_CITATION` が付いている。
- LLM の学習: 一般の条項で明示的な許可が要る。データの節はこれを外していない。
- データベースごとの違い: 規約の上では WEO、IFS、BOP、DOT、GFS、Primary Commodity Prices、為替レートは同じ Data の条項に入る。ISORA は別の条件。外部の情報を含むものは別の条件があり得る。

### Hugging Face に置くことについて

- 文面上、再配布そのものは許されるが、CC BY のような無条件の公開ライセンスではない。ライセンス名は「other」として IMF の規約を指すことになる。
- 非商用に限っても、自動化された一括取得は明示的な許可が要る (一般の条項)。Hugging Face のデータセットは利用者に商用利用や LLM の学習を想定させやすく、IMF の規約は商用と LLM の学習の両方を許可制にしている。置く場合は、IMF の許可 (copyright@imf.org) を先に取るのが文面に沿った手順になる。
- 置くときに要るもの: 出典の表示 (`SUGGESTED_CITATION`)、取得日、データフローの ID と版、加工の明記、受け取る側への IMF の条件の周知。
- IMF の紋章、名前、略称は商標で、使うには許可が要る (規約の「The IMF Seal, Name, and Initials」)。

## 版

### WEO

- WEO は年 2 回 (4 月と 10 月) の版。WEO の説明: 「The World Economic Outlook (WEO) database is created during the biannual WEO exercise, which begins in January and June of each year and results in the April and September/October WEO publication.」1 月と 7 月の WEO Update には database は出ない (Transition Guide)。
- 現行の `IMF.RES:WEO` は版ごとに上書きされる。Transition Guide: 「IMF.RES:WEO represents the publicly released WEO database and is updated only at the time of the April and October WEO publications.」
- 過去の版は API で 3 通りに取れた。日本の 2023 年の実質 GDP 成長率で確かめた。

| 取り方 | 版 | 2023 年の値 |
|---|---|---:|
| `IMF.RES,WEO` (9.0.0、現行) | 2026 年 4 月 (`PUBLICATION_DATE` 2026-04-14) | 0.720785 |
| `IMF.RES,WEO_2025_OCT_VINTAGE` | 2025 年 10 月 (2025-10-14) | 1.245 |
| SDMX 3.0 の `asOf=2025-12-01T00:00:00Z` | 2025 年 10 月 | 1.245 |
| `IMF.RES,WEO,6.0.0` (古い構造の版) | 2025 年 4 月 (2025-04-22) | 1.486 |

  1. `_VINTAGE` のデータフロー。WEO は `WEO_2025_OCT_VINTAGE` の 1 件だけで、注記に「Vintage for 2025-10-14」とある。
  2. SDMX 3.0 の `asOf`。データフローの注記が `historySettingType: FULL_HISTORY`。WEO では `asOf` が 2025-11-01 と 2025-11-25 で 2025 年 10 月の版を返し、2025-10-01、2025-06-01、2024-12-01、2023-01-01 では空だった。
  3. データフローの古い版。`dataflow/all/all/all` は 407 件を返し、WEO は 9.0.0 と 6.0.0 の 2 つ。6.0.0 は 2025 年 4 月の版の値を返した。
- 2025 年 4 月より前の版は API では見つからなかった。Transition Guide: 「Earlier WEO databases remain accessible through the legacy archive on imf.org until vintages are fully incorporated into the IMF Data Portal under Vintage icon in Resources section.」www.imf.org の `weo-database/<年>/<月>` のページと `/-/media/files/publications/weo/weo-database/...` のファイルは Internet Archive に 1999 年 (指標ごとの CSV) から 2025 年 4 月の版まで保存がある。www.imf.org 本体は curl に 403 で、ここからは取れなかった。
- 2025 年 10 月と 2026 年 4 月の版の旧形式のファイル (`weoapr2026all.xls`、`weoapr2026-sdmxdata.zip`) は Internet Archive の記録で 404 (2026-07〜08)。新しい版は portal の Excel だけ。
- 過去の予測値そのものを集めたファイルとして「WEO Historical Forecasts Database」(`WEOhistorical.xlsx`) がある。FAQ (Internet Archive の 2026-09-18 の保存): 「historical forecasts from the April 1990 WEO for select key indicators are compiled into one Excel file. For all other indicators, they may be found in the archived WEO databases web pages」。
- portal の版のページ <https://data.imf.org/en/Datasets/WEO/Dataset-Vintages> は画面の裏で一覧を読み込むので、保存からは中身が読めなかった。

### 他のデータベース

- 現行のデータフローは上書き更新。`detail=nodata` の応答で `UPDATE_DATE` と `PUBLICATION_DATE` が分かる。
- 統計局 (IMF.STA) の主要なデータフローには月ごとの `_VINTAGE` がある。元になるデータフローは 36 種類 (BOP、IIP、CPI、ER、EER、IL、MFS の 7 つ、QNEA、ANEA、QGFS、ITG、IMTS、PPI、PI、LS、FA、SPE など) で、版の月は 2025-10 (6 件)、2025-12 (1 件)、2026-01 (27 件)、2026-02 (28 件)、2026-04 (29 件)、2026-05 (28 件)。2026-03 と 2026-06 以降の版は無かった。119 件のうち 35 件は系列数 0 (中身が空) だった。
- SDMX 3.0 の `asOf` は統計局のデータでも効いた。日本の CPI (`JPN.CPI._T.IX.M`) は `asOf` を 2025-10-01、2025-12-01、2026-01-15、2026-03-01 にすると観測数が 1,507、1,509、1,511、1,513 と時点に応じて減り、2025-06-01 では空だった。遡れるのは 2025 年秋ごろまでで、それより前は API に無い。
- SDMX 2.1 の `includeHistory=true` はエラーにならなかったが、現行の値を 1 つ返すだけだった。
- データフローの構造の版は多いもので 12 (MFS_CBS)。WEO のように古い構造の版で古い値が取れるかは、WEO 以外では確かめていない。
- 版を残したいなら、取った側で取得日ごとに保存するか、`asOf` で遡れる範囲 (2025 年秋以降) を取るしかない。

## 未確認の点

- www.imf.org と data.imf.org の本体を直接は読めていない (Akamai の 403)。規約は Internet Archive の 2026-06-25 の保存で読んだ。
- 規約の改定日。ページに日付の記載が無い。
- 現行 104 件のうち `LICENSE` を見たのは 21 件。残り 83 件の属性。
- 外部の指標を加工したデータフロー (NDGAIN、INFORMRISK、UNFCCC、AEA など) の元の機関の条件。
- 観測数と、全体を CSV にしたときの大きさ。API に観測数の注記が無い。
- `TAXFIT` の系列数 1,048,575 が実数か、上限で切られた値か。
- API の回数制限の有無と値。説明のページにも記載が無かった。
- portal の画面の「Download」ボタンの一括ダウンロードの中身と大きさ (画面の裏の要求になるので試していない)。
- 統計局の `_VINTAGE` が 2026-06 以降に作られていない理由と、系列数 0 の版の意味。
- DataMapper API の今の状態と条件。
