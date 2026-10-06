# UNdata (国連統計部のデータ集約サイト)

2026-10-06 に読んで確かめた内容。

測り方:

- ページ、SDMX API、配布ファイルに curl で直接要求を投げた。User-Agent を付けなくても 403 や 429 は返らなかった。要求の間は 1 秒以上空けた。
- 一覧と規約はページの HTML から読んだ。更新予定表 (Update Calendar) はページに埋め込まれた JSON (`var data = {"updateData": [...]}`) を読んだ。
- データ本体は小さい問い合わせだけを取った。SDMX は国と年を絞った問い合わせ、統計年鑑の CSV は大きさを HEAD で測り、1 本 (Internet Usage、288,287 バイト) だけ中身を見た。
- 1 件だけ、絞り方を誤って SDG のデータフローに全世界・2023 年以降の問い合わせを投げ、60 秒の上限で切れるまでに 29,763,327 バイトを受け取った。中身は使わずに消した。
- 画面の「Download」ボタンが使う `Handlers/DownloadHandler.ashx` と、Explorer が使う `Handlers/DataMartHandler.ashx` は、ページの JavaScript が組み立てる内部の URL で、文書化された配布方法ではないので呼んでいない。
- データベースごとの記録数は Explorer の XHR でしか出ないため、ほとんど不明のまま。

## 入口と現状

- 旧来の UNdata: <https://data.un.org/Default.aspx> (ページ名「UNdata」)。見出しに「32 databases - 60 million records」とある。
- <https://data.un.org/> (ルート) は 2026-10-06 時点で UNdata ではなく、「UN - Welcome to UN System Data Commons」という別の JavaScript アプリ (Google の Data Commons の部品を `unsd-datacommons.gcp.un-icc.cloud` から読む) になっている。旧来の UNdata は `Default.aspx` 以下にそのまま残っている。
- SDMX REST の `https://data.un.org/ws/rest/...` は `https://data.un.org/legacy/ws/rest/...` へ 302 (http からは 301) で回される。API にも「legacy」の扱いが付き始めている。
- 更新予定表: <http://data.un.org/UpdateCalendar.aspx>
- API の説明: <https://data.un.org/Host.aspx?Content=API>
- 利用規約: <https://data.un.org/Host.aspx?Content=UNdataUse>
- 運営: 国連経済社会局 (UN DESA) 統計部 (UNSD) の Development Data Section (About のページ)。同じ課が Statistical Yearbook、World Statistics Pocketbook、MBS、SDG 指標データベースも担当している。

### UNdata とは何か

About のページ (2026-10-06 に読んだ) の説明:

> UNdata is a web-based data service for the global user community. It brings international statistical databases within easy reach of users through a single-entry point. Users can search and download a variety of statistical resources compiled by the United Nations (UN) statistical system and other international agencies. The numerous databases or tables collectively known as "datamarts" contain over 60 million data points ...

国連と他の国際機関のデータベース (datamart) を、1 つの検索画面と 1 つの表示形式にまとめた集約サイトである。2005 年の「Statistics as a Public Good」計画で作られた。各データベースの値は元の機関のものをそのまま載せたもので、規約の Disclaimers も「supplied as contained in the source database without any addition, subtraction, amendment, or modification」と書く。

ほかに、UNdata 自身の成果物として次の 2 つがある。

- Popular statistical tables: 国連統計年鑑 (Statistical Yearbook、SYB) の表を CSV と PDF で配るもの。年鑑より早く更新される「live」の表とされる。
- 国と地域の統計プロファイル (World Statistics Pocketbook の HTML 版)。

## データベースの一覧

更新予定表の JSON にある 32 件。ホームの一覧と同じ 32 件で、Explorer の `d=` の識別子はホームのリンクから対応させた。最終更新と次回予定は更新予定表の値そのまま。記録数は表示されていない (ホームの合計 6,000 万件だけ)。

| d= | データベース | 元の機関 | UNdata での最終更新 | 次回予定 |
|---|---|---|---|---|
| POP | Demographic Statistics Database | UNSD | 2026/08/10 | 2027/02/15 |
| SNAAMA | National Accounts Estimates of Main Aggregates | UNSD | 2026/03/04 | 2027/03/05 |
| WDI | World Development Indicators | World Bank | 2026/02/25 | 2027/02/25 |
| EDATA | Energy Statistics Database | UNSD | 2025/12/15 | 2027/01/15 |
| SNA | National Accounts Official Country Data | UNSD | 2025/10/14 | 2026/10/01 |
| UNHCR | UNHCR Statistical Database | UNHCR | 2025/08/29 | 2026/07/31 |
| 32 | Human Development Indices: A statistical update 2025 | UNDP | 2025/07/18 | 2026/12/01 |
| ComTrade | Commodity Trade Statistics Database | UNSD (UN Comtrade) | 2025/07/10 | 2025/10/01 |
| 33 | Homicide Statistics | UNODC | 2025/05/15 | 2026/05/15 |
| PopDiv | World Population Prospects: The 2024 Revision | UNPD | 2024/10/16 | 2025/10/16 |
| ITU | World Telecommunication/ICT Indicators Database | ITU | 2024/04/04 | 2025/04/01 |
| FAO | FAOSTAT | FAO | 2024/01/22 | 2024/12/20 |
| GHG | Greenhouse Gas Inventory Data | UNFCCC | 2023/11/22 | 2024/12/01 |
| ENV | Environment Statistics Database | UNSD | 2023/06/20 | 2025/06/20 |
| 19 | World Tourism Data | UNWTO (UN Tourism) | 2022/12/12 | 2023/12/01 |
| ICS | Industrial Commodity Statistics Database | UNSD | 2019/01/28 | To be confirmed |
| UNESCO | UIS Data Centre | UNESCO UIS | 2016/10/24 | To be confirmed |
| 31 | World Telecommunication/ICT Indicators Table | ITU | 2016/01/14 | To be confirmed |
| UNAIDS | UNAIDS Data | UNAIDS | 2015/10/21 | To be confirmed |
| WHO | WHO Data | WHO | 2014/07/31 | To be confirmed |
| 29 | World Contraceptive Use | UNPD | 2014/07/30 | To be confirmed |
| UNIDO | INDSTAT | UNIDO | 2014/07/23 | To be confirmed |
| 16 | Indicators on Women and Men | UNSD | 2013/07/11 | Not applicable |
| SOWC | The State of the World's Children | UNICEF | 2013/06/19 | To be confirmed |
| 25 | World Marriage Data | UNPD | 2013/03/31 | To be confirmed |
| 22 | World Fertility Data | UNPD | 2013/03/31 | To be confirmed |
| 30 | Key Indicators of the Labour Market, 7th Edition | ILO | 2011/10/25 | Not applicable |
| CLINO | World Meteorological Organization Standard Normals | WMO | 2010/07/14 | To be confirmed |
| IFS | International Financial Statistics | IMF | 2010/05/14 | To be confirmed |
| LABORSTA | LABORSTA | ILO | 2010/01/27 | Not applicable |
| 18 | OECD Data | OECD | 2009/10/20 | To be confirmed |
| GenderStat | Gender Info | UNSD | 2008/03/21 | Not applicable |

読み取れること:

- 32 件のうち、2025 年以降に更新されたのは 9 件だけ。17 件は 2016 年以前で止まり、次回予定は「To be confirmed」か「Not applicable」。止まった datamart は元の機関の古い版の写しである。
- 次回予定を過ぎて更新されていないものがある (2026-10-06 時点): National Accounts Official Country Data (予定 2026/10/01)、UNHCR (2026/07/31)、Commodity Trade (2025/10/01)、Homicide (2026/05/15)、WPP (2025/10/16。中身は 2024 年版のまま)、ITU (2025/04/01)、FAOSTAT (2024/12/20)、GHG (2024/12/01)、ENV (2025/06/20)、World Tourism (2023/12/01)。
- 記録数は一部だけ分かった。FAQ に Commodity Trade は「around 40 million trade records only in 2 digit HS 1992 classification」とある。Demographic Statistics の表 1 (Population by sex and urban/rural residence) は Data.aspx のページに 75,644 件と出た。

## 利用規約

<https://data.un.org/Host.aspx?Content=UNdataUse> (ページ名「Terms and Conditions of use」、2026-10-06 に読んだ)。全ページの足元の「Conditions of Use」もここを指す。

> Terms of Use
>
> All data and metadata provided on UNdata's website are available free of charge and may be copied freely, duplicated and further distributed provided that UNdata is cited as the reference.

> Disclaimers
>
> The data and metadata presented on UNdata are supplied as contained in the source database without any addition, subtraction, amendment, or modification by the United Nations Statistics Division.

> Information about the quality or limitations of the data and metadata should be obtained from the organization responsible for the source database.

API のページも「The API is governed by UNdata Terms of Use」と書く。

読み方:

- 再配布: 「copied freely, duplicated and further distributed」と明示的に認める。条件は UNdata を出典として示すことだけ。
- 商用利用: 規約に「commercial」の語は無い。禁止も許可も書いていない。再配布に目的の限定が付いていないので商用も含むと読めるが、明文ではない。
- ライセンス名 (CC BY など) は書かれていない。改変や派生物についての記述も無い。
- 元の機関の権利への言及が無い。「All data and metadata provided on UNdata's website」が UNdata の写しすべてを覆うように書かれているが、UNSD が他機関のデータについてこの許諾を出せる立場にあるかは書かれていない。元の機関の規約が UNdata の規約より厳しい場合 (下の Comtrade、ITU、WHO) は食い違いになる。
- 国連の一般の利用規約 (<https://www.un.org/en/about-us/terms-of-use>) は「for the User's personal, non-commercial use, without any right to resell or redistribute them or to compile or create derivative works therefrom」で、UNdata の規約とは逆に近い。UNdata のサイトは自分の規約を掲げているので、data.un.org の上のデータには UNdata の規約が当たると読む。UNODC のサイト (unodc.org/unodc/legal.html) は国連の一般規約と同じ文面だった。

## 取得の方法

### 1. SDMX API (REST と SOAP)

API のページ (2026-10-06 に読んだ) の説明:

- REST: `http://data.un.org/ws/rest/{artifact}/{artifactId}/{parameters}`。実際は `https://data.un.org/legacy/ws/rest/` に回される。応答の XML のコメントは `NSI Web Service v8.15.1.0` (Eurostat の SDMX-RI)。
- 形式: 既定は SDMX-ML Generic (2.1)。`Accept: application/vnd.sdmx.structurespecificdata+xml;version=2.1`、`Accept: text/json`、`Accept: text/csv` (データのみ)。
- SOAP: `http://data.un.org/ws/NSIStdV20Service.asmx` (`GetCompactData`、`GetGenericData`、`QueryStructure`)。CORS 対応とされる。
- 認証は不要。
- API の FAQ: 「To be exposed through SDMX API, each datamart requires an SDMX Data Structure Definition (DSD) ... API support will be gradually extended」。つまり 32 の datamart の一部しか API に無い。

`/ws/rest/dataflow/` の応答 (6,402 バイト) にあるデータフローは 15 件:

| データフロー | 機関 (SDMX) | 名前 | 小さい問い合わせの結果 |
|---|---|---|---|
| DF_UNDATA_ENERGY | UNSD 1.2 | UNSD Energy Statistics | `A.392..?startPeriod=2020` が 200、3,530 行、264,296 バイト (CSV) |
| DF_UNData_EnergyBalance | UNSD 1.0 | Energy Balance DataFlow | `392...?startPeriod=2022` が 200、627 行、52,087 バイト |
| DF_UNData_UNFCC | UNSD 1.0 | SDMX_GHG_UNDATA | API のページの見本の問い合わせ 3 つを含め、すべて 500「Error executing generated SQL and populating SDMX model」 |
| DF_UNDATA_WDI | WB 1.0 | WB World Development Indicators | 500 (同上) |
| DF_UNData_UIS | UIS 1.1 | SDMX_UIS_UNData | 500 (同上) |
| DF_UNDATA_MDG | IAEG 1.2 | SDMX-MDGs | 500 (同上) |
| DF_UNDATA_COUNTRYDATA | UNSD 1.4 | SDMX-CountryData | `startPeriod=2022` で 404「NoRecordsFound」 |
| DF_SDG_GLH | IAEG-SDGs 1.26 | SDG Harmonized Global Dataflow | 200。全世界・2023 年以降で 60 秒に 29.8MB を超えた (上記) |
| NA_MAIN | ESTAT 1.9 | NA Main Aggregates | `A.N.JP...........?startPeriod=2022` が 200、165 行、18,592 バイト |
| NASEC_IDCFINA_A / _Q | ESTAT 1.9 | Annual / Quarterly financial accounts | 試していない |
| NASEC_IDCNFSA_A / _Q | ESTAT 1.9 | Annual / Quarterly non-financial accounts | 試していない |
| DF_SEEA_AEA | ESTAT 1.3 | Air emission accounts | 全世界・2021 年以降が 200、6,916 行、653,175 バイト。国はインドネシアとウクライナだけ |
| DF_SEEA_ENERGY | ESTAT 1.3 | Physical energy flow accounts | 試していない |

- 機関が ESTAT のものは構造 (DSD) が Eurostat の定義というだけで、中身は UNSD が各国から SDMX で集めた国民経済計算と環境経済勘定 (SEEA) と見られる。NA_MAIN に日本、SEEA にインドネシアがあり、Eurostat の配布とは別物。
- datastructure の一覧には `DSD_WPP_UNDATA` (UNSD 2.0) もあるが、対応するデータフローは無い。
- 2026-10-06 時点で、API から安定して取れたのは Energy、Energy Balance、NA_MAIN、SEEA、SDG だった。API のページ自身の見本 (GHG) が動かない。
- データの版の指定 (過去の時点の取得) の仕組みは見当たらない。

### 2. 画面からのダウンロード (Data.aspx)

- 表示: `https://data.un.org/Data.aspx?d=<datamart>&f=<フィルタ>` (例 `Data.aspx?d=POP&f=tableCode%3a1`)。Explorer (`Explorer.aspx?d=<datamart>`) は中身を JavaScript で読み込むので、HTML には一覧が無い。
- 「Download」ボタンは XML、カンマ区切り、セミコロン区切り、パイプ区切りの 4 形式。ページの文言は「Only the first 100000 records may be downloaded using this facility.」、FAQ も「100,000 is the maximum number of records that are downloadable at any one time」。
- ボタンの URL は `SeriesActions.js` が `Handlers/DownloadHandler.ashx?DataFilter=...&DataMartId=...&Format=csv` の形で組み立てる。文書化された URL の型ではないので、ここでは呼んでいない。使うなら 1 回 10 万件までに区切って何度も呼ぶことになり、再現できる取得としては弱い。
- datamart 全体を 1 つのファイルで配る一括ダウンロードは見当たらない。

### 3. 統計年鑑の表 (Popular statistical tables)

ホームから直接リンクされた静的ファイル。HEAD に `Content-Length` と `Last-Modified` が返る。

- URL の型: `https://data.un.org/_Docs/SYB/CSV/SYB<版>_<表番号>_<年月>_<表名>.csv` (PDF は `_Docs/SYB/PDFs/`)。
- 2026-10-06 時点でリンクされているのは 33 本、合計 34,549,870 バイト (約 34.5MB)。うち 32 本が SYB68 (`202511`)、1 本 (Population Growth Rates in Urban areas and Capital cities) は SYB61 のまま (2018-08-31)。
- 大きいもの: Population, Fertility and Mortality 2,137,820、Population, Surface Area and Density 2,124,540、Education 2,042,991 バイト。小さいもの: ODA from Donors 205,703 バイト。
- Last-Modified は 2026-02-02 と 2026-02-24。ホームの「Updated」の表示 (2025-12-22、2026-03-02) とは合わない。
- 中身 (Internet Usage を見た): 1 行目が表番号と表名 (`T30,Internet Usage`)、2 行目が見出し `Region/Country/Area,,Year,Series,Value,Footnotes,Source`。行ごとに元の出典が入る。Internet Usage の 1,520 行はすべて「International Telecommunication Union (ITU), Geneva, the ITU database, last accessed March 2025.」だった。つまり年鑑の表は、他機関の値を UNSD が切り出して並べたもの。
- 前の版のファイルも残っている。`SYB67_314_202411_Internet%20Usage.csv` は 200 だった (推測した URL で、確かめたのはこの 1 本だけ)。

### 4. 更新予定表

上の一覧表のとおり、datamart ごとに「最終更新」と「次回予定」を 1 組だけ載せる。履歴は無い。頻度は書かれていないが、予定の間隔から読むと、更新が続いているものは年 1 回 (Demographic は約半年) である。

## データベースごとの条件と重複

ライセンスは元の機関のもの。UNdata の規約は上のとおり一律に再配布を認めるが、元の機関の条件と食い違うものに印を付けた。「収集済み」は利用者がすでに集めているもの (UN WPP、FAOSTAT、ILOSTAT、UNHCR、UNDP HDR、World Bank WDI、OECD、Eurostat、EDGAR、PWT、Maddison)。大きさはほとんど不明。

| データベース | 元の機関の条件 (2026-10-06 時点) | 印 | 重複 |
|---|---|---|---|
| Demographic Statistics (POP) | UNSD 自身。UNdata の規約がそのまま当たる | 再配布可 (商用は明文なし) | 無し。WPP は推計、こちらは各国の届出値 (人口動態、センサス、移民) |
| National Accounts Main Aggregates (SNAAMA) | UNSD 自身 | 同上 | 無し (PWT、WDI と一部重なるが別系列)。UNSD の国民経済計算のサイトでも配っているとされる (未確認) |
| National Accounts Official Country Data (SNA) | UNSD 自身 | 同上 | 無し |
| Energy Statistics (EDATA) | UNSD 自身 | 同上 | 無し (EDGAR は排出量で別物) |
| Environment Statistics (ENV) | UNSD 自身 | 同上 | 無し |
| Industrial Commodity Statistics (ICS) | UNSD 自身。2019 年で停止 | 同上 | 無し |
| Indicators on Women and Men、Gender Info | UNSD 自身。停止 | 同上 | 無し。中身は他機関からの再録が多いと見られる (未確認) |
| Commodity Trade (ComTrade) | UN Comtrade の「Policy on Comtrade Data Use」: 「UN Comtrade data are provided for internal use only and may not be re-disseminated in any form without UNSD's permission.」 | 要許可。UNdata の規約と食い違う | 無し |
| World Development Indicators | 世界銀行 CC BY 4.0 (追加条項あり。../worldbank/) | 再配布可 | 収集済み (WDI) |
| UNHCR Statistical Database | CC BY 4.0 (../unhcr/) | 再配布可 | 収集済み (UNHCR) |
| Human Development Indices | CC BY 3.0 IGO (../undp-hdr/) | 再配布可 | 収集済み (HDR) |
| World Population Prospects 2024 | CC BY 3.0 IGO (../un-wpp/) | 再配布可 | 収集済み (WPP) |
| FAOSTAT | CC BY 4.0 + FAO の追加条項 (../faostat/) | 再配布可 | 収集済み (FAOSTAT)。UNdata の写しは 2024-01 で古い |
| KILM 7th、LABORSTA | ILO。後継は ILOSTAT (CC BY 4.0、../ilostat/)。この古い版の条件は未確認 | 不明 | 実質的に収集済み (ILOSTAT が後継) |
| OECD Data | OECD の規約 (../oecd/)。2009 年の写し | 不明 (古い写し) | 収集済み (OECD) |
| International Financial Statistics | IMF。今の規約は商用に許可が要る (../imf/)。2010 年の写し | 商用は要許可 | 収集済みの一覧には無い |
| Homicide Statistics | UNODC。data.unodc.org の利用条件は見つけられなかった。unodc.org の legal は国連の一般規約 (個人・非商用) | 不明 | 無し |
| World Telecommunication/ICT Indicators (Database、Table) | ITU のサイト規約: 「ITU grants you permission to download, copy and use content for personal, educational, or non-commercial purposes ... You may not modify, reproduce, distribute, sell, transmit, create derivative works or use the content for any commercial purpose without obtaining prior written permission from ITU.」 データ専用の条件は未確認 | 非商用 / 要許可。UNdata の規約と食い違う | 無し |
| WHO Data | WHO の Datasets の条件: 「for public health purposes」に限った利用許諾。「Any other alteration or modification of the Datasets ... may be made only with the prior written authorization of WHO」、商業的な宣伝への利用の禁止。2014 年の写し | 目的限定、改変は要許可 | 無し |
| Greenhouse Gas Inventory Data | UNFCCC。利用条件のページは取得できなかった (unfccc.int は 212 バイトや 957 バイトの JavaScript の応答だけ) | 不明 | 無し (EDGAR はモデル推計、こちらは各国の届出インベントリ) |
| World Tourism Data | UNWTO (UN Tourism)。未確認 | 不明 | 無し |
| UIS Data Centre | UNESCO UIS。未確認 (uis.unesco.org の推測した規約 URL は 404) | 不明 | 無し |
| UNAIDS Data | UNAIDS。未確認 | 不明 | 無し |
| The State of the World's Children | UNICEF。未確認 | 不明 | 無し |
| INDSTAT | UNIDO。未確認 | 不明 | 無し |
| WMO Standard Normals (CLINO) | WMO。未確認 | 不明 | 無し |
| World Contraceptive Use、World Marriage Data、World Fertility Data | UNPD。WPP と同じ CC BY 3.0 IGO かは未確認 | 不明 | 無し (WPP とは別のデータベース) |

### 大きさの手がかり

- 全体: ホームに 60 million records、About に「over 60 million data points」。
- Commodity Trade: 約 4,000 万件 (FAQ)。全体の 3 分の 2 を占める。
- Demographic Statistics: 表 1 だけで 75,644 件。表の数は数えていない。
- Energy (SDMX): 日本の 2020〜2024 年で 3,530 行、264,296 バイト (CSV、1 行約 75 バイト)。日本は品目が多い国なので、これを 240 の国と地域、35 年に掛けた約 440MB は上限の目安にすぎない。実際の大きさは不明。
- 統計年鑑の CSV: 33 本で 34.5MB (HEAD で確かめた値)。

## 更新の仕方と版

- datamart と SDMX は上書き型。規約が「The United Nations Statistics Division periodically incorporates, without notice, revisions, updates and improvements to UNdata's content」と書く。更新予定表は最終更新日を 1 つだけ載せ、過去の版を取る手段は画面にも API にも無い。
- datamart の名前に版が付くものがある (World Population Prospects: The 2024 Revision、Human Development Indices 2025、KILM 7th Edition)。新しい版が出ると名前ごと置き換わると見られるが、古い版の datamart が残るかは確かめていない。
- 統計年鑑の CSV はファイル名に版 (SYB68) と年月 (202511) が入り、少なくとも SYB67 は同じ場所に残っていた。こちらは版が分かれて残る。
- Data.aspx のページには datamart ごとに「Last update in UNdata: 2026/08/10」「Next update in UNdata: 2027/02/15」の表示がある (Demographic で確認)。

## UNdata にしか無いもの

元の機関から直接取れるもの、すでに集めているもの、条件が不明か厳しいものを除くと、残る候補は UNSD 自身のデータベースだけになる。UNdata の規約がそのまま当たり、他機関の権利と食い違わない。

| 候補 | 元の機関から直接取れるか | 取り方 | 大きさ |
|---|---|---|---|
| Demographic Statistics Database | UNSD の人口統計のページは主に年鑑 (DYB) の PDF と表。機械可読の網羅的な配布は UNdata が主と見られる (未確認) | 画面のダウンロードだけ (10 万件ずつ、文書化されない URL)。SDMX に無い | 不明 (表 1 だけで 75,644 件) |
| Energy Statistics Database (+ Energy Balance) | UNSD の Energy Statistics のサイトにも年報やデータがある (未確認) | SDMX の DF_UNDATA_ENERGY と DF_UNData_EnergyBalance が動く | 不明 (日本の 5 年で 264KB。上限の目安で数百 MB) |
| National Accounts (Main Aggregates、Official Country Data) | UNSD の国民経済計算のサイトにもあるとされる (未確認) | 画面のダウンロード。SDMX の NA_MAIN が一部を返す | 不明 |
| Environment Statistics Database | UNSD の環境統計のサイトに表がある (未確認) | 画面のダウンロード | 不明 |
| Industrial Commodity Statistics、Gender Info、Indicators on Women and Men | 停止した古い版 | 画面のダウンロード | 不明 |
| 統計年鑑の表 (SYB68 の CSV 33 本) | UNSD の年鑑のページと同じものと見られる | 静的ファイル。HEAD で大きさが取れ、版名で残る | 34.5MB |

注意:

- 統計年鑑の表は UNSD の編集物だが、値の出典は各行の Source 列のとおり他機関 (ITU など) である。UNdata の規約は再配布を認めるが、ITU の行を ITU の規約で読むと非商用になる。表ごとに Source 列を数えてから判断する必要がある。
- Commodity Trade は UNdata にしか無い形 (HS 1992 の 2 桁) だが、Comtrade の方針は再配布に許可を求めるので候補から外した。
- GHG、Homicide、UIS、UNICEF などは UNdata の写しが古いか、元の機関に新しい版がある。取るなら元の機関から取るのが筋である。

## 選択肢 (決めていない)

1. 統計年鑑の CSV 33 本だけを取る。34.5MB。静的ファイルで HEAD が使え、版名でファイルが残るので、再現できる取得としては一番素直。ただし行ごとの出典の条件 (ITU、WHO など) を表ごとに確かめる手間がある。
2. SDMX で動く UNSD 自身のデータフローだけを取る (DF_UNDATA_ENERGY、DF_UNData_EnergyBalance、NA_MAIN、SEEA)。文書化された API で、UNSD 自身のデータなので条件は UNdata の規約で足りる。大きさは不明で、Energy は国ごとに区切って取ることになる。上限の目安で数百 MB。
3. 2 に加えて Demographic、SNA、ENV を画面のダウンロードで取る。UNdata にしか無い度合いは一番高いが、文書化されていない URL を 10 万件ずつ叩くことになり、この調査の線引きの外になる。大きさも不明。
4. 取らない。更新が続いている 9 件のうち 5 件 (WDI、UNHCR、HDR、WPP、FAOSTAT) はすでに元の機関から集めている。残りの 17 件は 2016 年以前で止まった写し。UNSD 自身のデータは UNSD の個別のサイトから取れる可能性があり (未確認)、そちらを先に調べる手もある。

どの案でも、UNdata の規約は商用について明文で書いていないことと、ルートの data.un.org がすでに Data Commons に置き換わり API が `legacy` の下に移されていることは、続くかどうかの不確かさとして残る。

## 判断 (2026-10-06)

上の案 1 と案 2 を両方採った。収集リポジトリは un-statistical-yearbook (統計年鑑の CSV) と undata-sdmx (SDMX の UNSD のデータフロー) の 2 つ。

統計年鑑は、行ごとの Source 列が示す元の機関の規約を優先し、その規約が再配布を認める行だけを公開する。UNdata の規約は「出典を示せば再配布してよい」と書くが、サイト全体への一文で、表や機関ごとの表示ではなく、元の機関の権利にも触れていない。世界銀行 WDI では配布元が指標ごとに付けたライセンスの表示に従ったが (EDGAR の CO2 指標を残した判断)、UNdata にはそれに当たる個別の表示が無いので、元の機関の規約で読む。

除く行と理由 (2026-10-06 に各機関の規約を読んだ):

| 機関 | 表 | 理由 | 規約 |
|---|---|---|---|
| ITU | 314 | 「ITU grants you permission to download, copy and use content for personal, educational, or non-commercial purposes ... You may not modify, reproduce, distribute, sell, transmit, create derivative works or use the content for any commercial purpose without obtaining prior written permission from ITU.」 | <https://www.itu.int/en/about/Pages/terms-of-use.aspx> |
| WHO | 154、315 (WHO/UNICEF JMP)、325、246 のうち妊産婦死亡の 657 行 | データセットの利用許諾は「for public health purposes」に限られ、「Any other alteration or modification of the Datasets ... may be made only with the prior written authorization of WHO」 | <https://www.who.int/about/policies/publishing/data-policy/terms-and-conditions> |
| IMF | 125、130 | 2024-11 の改定で、データの商用の再利用と、相当量の再掲に許可が要る ([../imf/](../imf/)) | <https://www.imf.org/en/about/copyright-and-terms> |
| UN Tourism (旧 UNWTO) | 176 | 「personal, non-commercial use, without any right to resell or redistribute ... or create derivative works」 | <https://www.untourism.int/copyright> |
| WIPO | 264 | 統計データの条件が「not to republish or commercially re-sell WIPO's statistical datasets」。全体の規約の CC BY 4.0 より、サービス固有の条件が優先する | <https://www.wipo.int/en/web/ip-statistics/about> |
| IPU | 317 | Parline は CC BY-NC-SA 4.0 (非商用) | <https://www.ipu.org/terms-use> |
| UNODC | 328 | データポータルが国連の一般規約 (個人・非商用、再配布不可) を指し、データ固有のライセンスが無い | <https://www.un.org/en/about-us/copyright> |
| IUCN | 313 | 商用利用と再掲載・再配布を、派生物も含めて事前の書面許可制にしている | <https://www.iucnredlist.org/terms/terms-of-use> |
| UNEP-WCMC、IUCN、BirdLife | 145 のうち保護区と KBA の 1,014 行 | WDPA も KBA も派生物の商用利用を禁じ、KBA は派生物の再配布にも書面許可を求める | <https://www.protectedplanet.net/en/legal>、<https://www.keybiodiversityareas.org/termsofservice> |

UIS (245、285、309、319、323) は公開する。データ閲覧サイトの規約と API の説明が CC BY-SA 4.0 を明示している (<https://databrowser.uis.unesco.org/terms-and-conditions>)。CC BY ではないので、これらの表には継承の条件が掛かる。7 機関の規約の原文は [yearbook-source-terms.md](yearbook-source-terms.md)。

仕組み: 収集リポジトリの scripts/03_export_parquet.py の SOURCES が Source の文字列を機関に対応づけ、公開するかと理由を決める。どれにも当たらない Source は公開しない (新しい版で知らない機関が現れても、黙って公開されない)。公開する行が無い表は Parquet を作らず、行を一部でも除いた表は元の CSV も上げない。sources.parquet に出典ごとの機関、公開の可否、理由が入る。

UN Comtrade (123、330) は公開する。上の「データベースごとの条件と重複」の表で引いた「internal use only and may not be re-disseminated in any form without UNSD's permission」は古い方針の文面で、今の FAQ (<https://uncomtrade.org/docs/faqs-on-use-and-re-dissemination/>、2026-10-06 に読んだ) は次のとおり書く。

> You may re-disseminate a limited amount of UN Comtrade data for commercial purposes without obtaining an additional distribution license. A "limited amount" is defined as a database containing fewer than 100,000 records in total. This threshold applies to the total number of records stored in your database or product, not to individual queries, API calls, or downloads.

年鑑の 123 と 330 は合わせて 8,536 行で、この範囲に収まる。FAQ は地理や部門の集計 (「Producing geographic, sectoral, or other aggregations」) も「transformed」の例に挙げている。上限は製品全体の件数に掛かるので、書き出しは公開する Comtrade の行が全版の合計で 100,000 に達したら止まる。

SDMX の 5 本 (undata-sdmx) も同じ考え方で扱う。NA_MAIN は行ごとに作成機関 (`COMPILING_ORG`) を持つので、その機関の規約で読む。Eurostat (EU、EFTA、正式な加盟候補国の行)、OECD、国連機関の行は公開する。IMF の行 (58 地域、58,040 行) は IMF の規約が商用の再利用と相当量の再掲に許可を求めるので除き、Eurostat の Kosovo の行 (3,881 行) は Eurostat の copyright notice が EU、EFTA、正式な加盟候補国以外の国のデータを商用の再利用から除いており、Kosovo は潜在的な候補にとどまるので除く。エネルギーの 2 本と SEEA の 2 本には作成機関の記載が無く、UNSD のデータとして公開する。決定と理由は収集リポジトリの compilers.parquet に、行の範囲ごとに残る。
