# OECD Data Explorer (OECD の統計データ、SDMX API)

2026-10-04 に読んで確かめた内容。

測り方:

- `sdmx.oecd.org` の API には curl で直接要求を投げた。構造 (dataflow、datastructure、contentconstraint、availableconstraint) の応答を数え、データ本体は 1 系列から数十行の小さい応答を数本だけ取った。全体の大きさは配布元が付けている観測数の注記 (`obs_count`) から数えた。データ本体の一括取得はしていない。
- `www.oecd.org` のページ (利用規約、API の説明、FAQ) は curl に 403 を返した。応答ヘッダは `server: cloudflare` と `cf-mitigated: challenge` で、Cloudflare のボット対策のチャレンジであり、ページが無いのではない。そのため Internet Archive の保存 (`web.archive.org/web/<時刻>id_/...`) で読んだ。使った保存の時刻はそれぞれの引用の所に書く。
- `data-explorer.oecd.org` と `sdmx.oecd.org` はチャレンジ無しで 200 を返した。

## 入口

- 画面: <https://data-explorer.oecd.org/> (OECD Data Explorer)
- API: <https://sdmx.oecd.org/public/rest/> (SDMX REST。v1 の構文がこの下、v2 の構文が `/public/rest/v2/` の下)
- API の説明書: <https://gitlab.algobank.oecd.org/public-documentation/dotstat-migration/-/raw/main/OECD_Data_API_documentation.pdf> (PDF 9 ページ、「Last updated: 17 September 2026」)
- 利用規約: <https://www.oecd.org/en/about/terms-conditions.html>。古い URL `https://www.oecd.org/termsandconditions/` は `termsandconditions.html` を経てここへ 301 する (Internet Archive の 2026-10-01 の保存で確かめた)。
- API の運用の説明: <https://www.oecd.org/en/data/insights/data-explainers/2024/11/Api-best-practices-and-recommendations.html>、FAQ: <https://www.oecd.org/en/data/insights/data-explainers/2024/09/OECD-DE-FAQ.html>

## 作成

- 作成者は経済協力開発機構 (OECD)。データフローごとの作成部局は SDMX の `agencyID` に出る (`OECD.SDD.NAD` は統計データ局の国民経済計算、`OECD.CFE.EDS` は起業・中小企業・地域・都市センターなど)。
- 一次配布元は OECD Data Explorer と、その裏の SDMX API (`sdmx.oecd.org`)。説明書に「The OECD Data Explorer powered by the .Stat Suite is sourced by this API.」とあり、画面は API の上に乗っている。
- 前の配布基盤 OECD.Stat (`stats.oecd.org`) は 2024-07-01 に止まった。FAQ の文:

> On July 1st, 2024, the OECD.Stat servers (the former OECD data dissemination platform) were taken offline, meaning queries to http://stats.oecd.org no longer work.

- 世界銀行の Data360 も OECD のデータベースを載せている。[../worldbank/data360.md](../worldbank/data360.md) では `OECD_IDD` (所得分配データベース) のライセンス欄が `License Specified Externally` で、URI は `https://www.oecd.org/termsandconditions/` だった。つまり条件は上の OECD の利用規約で、Data360 は二次配布。同じデータベースは OECD 側では `OECD.WISE.INE` の `DSD_WISE_IDD@DF_IDD` (Income distribution database) にある。

## 中身

### 配信空間は 4 つ

Data Explorer の画面の設定 (`data-explorer.oecd.org` のページに埋め込まれた JSON) に、外部から引ける配信空間が 4 つ書かれている。

| 空間 | API の根 | 画面の設定での名前 | データフロー数 (latest) |
|---|---|---|---:|
| public | `https://sdmx.oecd.org/public/rest` | Disseminate - Final (external access) | 1,548 |
| archive | `https://sdmx.oecd.org/archive/rest` | Disseminate - Archive (external access) | 1,388 |
| sti-public | `https://sdmx.oecd.org/sti-public/rest` | STI - Disseminate - Final (external access) | 20 |
| dcd-public | `https://sdmx.oecd.org/dcd-public/rest` | DCD - Disseminate - Final (external access) | 12 |

数は `<根>/dataflow/all/all/latest` の応答で数えた。sti-public は付加価値貿易 (TiVA) や二国間商品貿易 (BIMTS) の大きいもの、dcd-public は開発援助の CRS。archive の 1,388 件のうち 1,375 件は `agencyID` が部局を持たない `OECD` で、ID も `DF_` で始まる旧形式 (`DF_FFS_USA`、`DF_QASA_TABLE720`、`DF_AEO2012_CH5_FIG1` など)。OECD.Stat 時代のデータと刊行物の図表のデータが置かれている。

### public のデータフロー

`https://sdmx.oecd.org/public/rest/dataflow/all/all/latest` が 1,548 件を返した (SDMX-ML 2.1、8,908,464 バイト)。部局 (`agencyID` の上 3 段) ごとの上位:

| agencyID | 件数 | 主題 |
|---|---:|---|
| OECD.CTP.TPS | 212 | 税 |
| OECD.SDD.NAD | 197 | 国民経済計算 |
| OECD.CFE.EDS | 133 | 地域・都市 |
| OECD.EDU.IMEP | 127 | 教育 |
| OECD.SDD.TPS | 117 | 貿易・物価など |
| OECD.ELS.HD | 86 | 保健 |
| OECD.GOV.GIP | 57 | ガバナンス |
| OECD.TAD.ADM | 54 | 農業 |
| OECD.ENV.EPI | 51 | 環境 |
| OECD.STI.STP | 50 | 科学技術 |

`agencyID` の種類は 50。OECD 以外の機関のものが 3 件ある (`ESTAT` の `SEEA_AEA_A` Air Emissions Accounts、`IAEG-SDGs` の SDG のデータフロー 2 件)。名前に英語と仏語の両方があるのが 1,475 件、英語だけが 72 件、仏語だけが 1 件。

### 量

全体の観測数は、`https://sdmx.oecd.org/public/rest/contentconstraint/all/all/latest?detail=allcompletestubs` (120,393 バイト) が返す実在制約 (`CR_A_<データフロー>`、`type="Actual"`) に付いた注記 `obs_count` から数えた。

| 空間 | 観測数の注記があるデータフロー | 観測数の合計 |
|---|---:|---:|
| public | 1,510 | 2,064,486,952 |
| archive | 1,378 | 3,137,503,489 |

public の合計は重複を含む上限である。同じデータ構造 (DSD) を共有するデータフローは同じデータを別の切り口で見せていることがあり、たとえば `DSD_REG_DEMO@DF_DEMO` (16,452,318、「for 'Developer API'」と名前にある総まとめ) と `DSD_REG_DEMO@DF_POP_5Y` (8,102,495) などの個別のものが両方数えられている。

public の観測数の中央値は 30,131。大きいもの:

| データフロー | 観測数 |
|---|---:|
| OECD.STI.PIE `DSD_TIM_2025@DF_TIM_2025` | 120,261,120 |
| OECD.SDD.TPS `DSD_BATIS@DF_BATIS` | 100,951,234 |
| OECD.ENV.EPI `DSD_ECH@EXT_TEMP_P` | 95,164,608 |
| OECD.STI.PIE `DSD_TIM_2023@DF_TIM_2023` | 87,966,060 |
| OECD.SDD.STES `DSD_STES_REVISIONS@DF_STES_REVISIONS` | 78,344,373 |

SDMX-CSV v1 で 1 観測がおよそ 100 バイトだった (`DF_POP_5Y` の 88 行が 8,674 バイト)。この比で public の上限は非圧縮の CSV でおよそ 200GB になる。見積もりであり、全体を落として測ったものではない。

### 地域の単位

国が基本で、地域・都市は `OECD.CFE.EDS` の 133 件にまとまっている。名前の接頭辞で 3 系統に分かれる。

- `DSD_REG_*`: 地域 (Regions)。OECD の地域区分 TL2 (大地域) と TL3 (小地域)。
- `DSD_FUA_*`: 都市と機能的都市圏 (Cities and FUAs)。
- `DSD_LA_*`: 基礎自治体などの小地域 (Local areas)。

例として `DSD_REG_DEMO@DF_POP_5Y` (Population by 5-year age groups - Regions) の `availableconstraint` は次を返した。

| 次元 | 値の数 | 値の例 |
|---|---:|---|
| TERRITORIAL_LEVEL | 3 | CTRY、TL2、TL3 |
| REF_AREA | 3,375 | AL01、AL011、... (国コードと地域コード) |
| MEASURE | 2 | POP、DEPEND_RATIO |
| AGE | 28 | _T、Y_LT5、Y_GE80 など |
| SEX | 3 | _T、F、M |

期間は 1990 年から 2026 年まで (制約の StartPeriod と EndPeriod)。地域のデータに座標や境界の形状は含まれない。境界は別に配られているかもしれないが、この調べでは確かめていない。

データの説明文には他機関の名前が出る。地域人口は EU 諸国について Eurostat (`reg_dem`) から集めていると書かれている (Eurostat の名を説明文に含むデータフローは 102 件)。都市圏の温室効果ガスは EC JRC と IEA の EDGAR 8.0、公共交通の到達性は GTFS と OpenStreetMap を使っている。

### 期間と形式

- 期間はデータフローごとに違う。`DF_STES_REVISIONS` の制約は 1914-04 から 2026-08 まで。全データフローを通した最古と最新は数えていない。
- 応答の形式は SDMX-ML 2.1 (generic と structure-specific)、SDMX-ML 3.0 (実験的)、SDMX-JSON v1 と v2、SDMX-CSV v1 と v2。`Accept` ヘッダか、`format=csvfile` や `format=csvfilewithlabels` などの URL 引数で選ぶ (説明書による)。
- `format=csvfile` の応答は `Content-Disposition: attachment; filename="OECD.CFE.EDS,DSD_REG_DEMO@DF_POP_5Y,,filtered,2026-10-04 01-21-25.csv"` のように取得時刻入りの名前で返る。1 行目はデータフローと版 (`OECD.CFE.EDS:DSD_REG_DEMO@DF_POP_5Y(2.4)`) を持つ。
- 例: 日本の総人口の最新値は `A.CTRY.JPN._Z.POP._T._T.PS` で 2024 年 123,802,000。

## 配布

- ファイルとしての一括配布は見つからなかった。Data Explorer の画面の CSV ダウンロードも API の呼び出しで、同じ回数制限に数えられる (下の運用の説明の文)。
- 1 回の要求でデータフロー 1 つを丸ごと取れる (`<データフロー>/all`)。
- 前に Cloudflare が付いていて、データの応答に `cache-control: public,max-age=7200` と `cf-cache-status` が付く。データフロー一覧の応答は `cf-cache-status: HIT` だった。

## 取り出し方

区分は catalog。主な使い方は、構造の問い合わせで目録を読んでから、データフローと次元の値で絞ったデータを引くこと。データフロー単位で見ると whole (分割済みのファイルは無く、そのデータフローの `all` を取る)。range には当たらない。

- 目録: `dataflow` (一覧)、`datastructure` (次元)、`availableconstraint` (今あるコードの組と期間)、`contentconstraint` (最終更新時刻 `validFrom` と観測数 `obs_count`)。運用の説明は `contentconstraint` を更新の確認に使うよう勧めている。
- 絞り方: 次元の値を `.` で区切ったキー (`A.CTRY.JPN._Z.POP._T._T.PS`)、`+` で複数値、空欄で全部。期間は `startPeriod`、`endPeriod`。差分は `updatedAfter` (説明書は「frequent database synchronisations」でこれを使うよう強く勧めている)。`updatedAfter=2026-01-01T00:00:00` を付けた日本の総人口の要求は、ヘッダ行だけの CSV を返した。
- HTTP Range: `curl -r 0-1023` は 206 ではなく 200 で全体を返した。応答には `accept-ranges: values` があり、.Stat Suite の行範囲の指定 (`Range: values=0-4`) を受ける素振りを見せるが、SDMX-CSV で試すと 200 で 35 行全部が返った。バイト単位でも行単位でも部分取得は効かなかった。
- 説明書が保証するのは書いてある構文だけ (「only the syntax listed in this document is guaranteed to be supported」)。標準の `includeHistory=true` と `asOf=` は 500 (Internal server error) を返した。

### 回数制限

運用の説明 (Internet Archive の 2026-09-27 の保存、ページの日付は 18 March 2026):

> API access is currently restricted to a maximum of
> 60 data downloads per hour.
> Any requests exceeding this limit will be temporarily blocked. This restriction also applies to
> CSV file downloads
> from the
> data-explorer.oecd.org
> interface. Additionally,
> traffic originating from VPNs or anonymized sources is not allowed

- 1 時間 60 回だと、public の 1,510 データフローを 1 回ずつ取るだけで 26 時間かかる。運用の説明は 1,000 万件を超えるデータフローは分けて取るよう勧めているので、実際はそれより多い。
- 大きいデータフローでは `lastNObservations` と `firstNObservations` が止められている。「API query parameter restrictions」のページ (<https://www.oecd.org/en/data/insights/data-explainers/2026/03/Restricted-API-parameter.html>、Internet Archive の 2026-04-14 の保存) によると、sti-public (TiVA) と dcd-public (CRS) の空間では全部、public では `DSD_BATIS@DF_BATIS`、`DSD_ECH@EXT_TEMP_P`、`DSD_TIM_2023@DF_TIM_2023`、`DSD_STES_REVISIONS@DF_STES_REVISIONS` などの挙げられたものだけ。
- FAQ は緩和を予告している: 「the OECD is working towards relaxing these restrictions」。
- 利用規約も、1 回の量と回数を OECD が任意に変えられること、負荷をかける IP を予告なく止められることを定めている (下の Availability of Data と APIs の節)。
- 今回の 15 本ほどのデータ要求では 429 は出ず、応答に残り回数を示すヘッダも無かった。

## ライセンス

### 利用規約の Data の節

<https://www.oecd.org/en/about/terms-conditions.html> を、Internet Archive の 2026-10-03 06:45 の保存 (`https://web.archive.org/web/20261003064505id_/https://www.oecd.org/en/about/terms-conditions.html`) で 2026-10-04 に読んだ。末尾は「Last updated on 1 July 2024」。本体は curl に Cloudflare のチャレンジ (403、`cf-mitigated: challenge`) を返したので直接は読めていない。

規約は内容の種類ごとに節が分かれる (OECD Written Content、OECD Legal Instruments、Data、Multimedia content、OECD Logo、Links、Press Releases)。統計データに当たるのは「3. Data」。

> The OECD makes data (the "Data") available for use and consultation by the public. Data may be subject to restrictions beyond the scope of these Terms and Conditions, either because specific terms apply to those Data or because third parties may have ownership interests. It is the user's responsibility to verify, either directly in the metadata or, if available, by clicking on the icon and then referring to the "source" tab, whether the Data is fully or partially owned by third parties and/or whether additional restrictions may apply, and to contact the owner of the Data before incorporating it in your work in order to secure the necessary permissions. The OECD in no way represents or warrants that it owns or controls all rights in all Data, and the OECD will not be liable to any user for any claims brought against the user by third parties in connection with the use of any Data.

> Permitted Use
> Except where additional restrictions apply as stated above, you can extract from, download, copy, adapt, print, distribute, share and embed Data for any purpose, even for commercial use. You must give appropriate credit to the OECD by using the citation associated with the relevant Data, or, if no specific citation is available, you must cite the source information using the following format: OECD (year), (dataset name),(data source) DOI or URL (accessed on (date)). When sharing or licensing work created using the Data, you agree to include the same acknowledgment requirement in any sub-licenses that you grant, along with the requirement that any further sub-licensees do the same.

> Availability of Data
> The availability of the Data is contingent upon the availability of the OECD's corresponding resources, whose capacity is subject to change at any time. The OECD may monitor your use of the Data and reserves the right, at its sole discretion and without limitation, to modify the amount of Data you may request in a single query, to modify the number of queries you may make over a specified time, to remove certain Data and to alter the file formats in which Data are available.

API については:

> You agree not to modify, distribute, decompile, disassemble, reverse engineer or perform any similar action on the APIs or any of their portions or components.

これは API のソフトウェアについての条項で、取得したデータの再配布を禁じるものではない (データは上の Permitted Use が「distribute」を認めている)。

API の説明書の冒頭も「OECD data and the API service are offered subject to your acceptance of OECD Terms and Conditions.」としている。

### 読み取れること

- 再配布: できる (「distribute, share」)。
- 商用利用: できる (「for any purpose, even for commercial use」)。
- 改変: できる (「adapt」)。
- 出典表示: 必須。データに付いた引用があればそれを、無ければ「OECD (year), (dataset name),(data source) DOI or URL (accessed on (date))」の形。
- 出典表示の引き継ぎ: 派生物を共有やライセンスするときは、同じ出典表示の要件を下位のライセンスに入れ、さらにその先にも入れさせることに同意する。CC BY 4.0 には無い条項で、Hugging Face に置くならデータセットカードにこの要件を書き写す必要がある。
- 第三者のデータ: 規約の範囲外。OECD は全データの権利を持つとは保証せず、第三者の権利の有無を確かめて許諾を取るのは利用者の責任とされる。確かめる場所はメタデータか画面の「source」タブとされているが、API の構造の応答 (データフロー 1,548 件の名前と説明) にライセンスや権利の欄は無かった (「licen」に当たったのは仏語の学位名「licence」だけ)。データフローごとに、他機関由来かどうかを説明文から読むしかない。

### CC BY 4.0 になったのは書かれたものだけ

「2024 年ごろに CC BY 4.0 へ変わった」は、統計データについては当たらない。2024-07-01 から CC BY 4.0 になったのは刊行物などの書かれたもので、規約の「1. OECD Written Content」の節:

> 1.1 Content published as of 1 July 2024
> Following implementation of the OECD Open Access Policy, most OECD written content published as of 1 July 2024 is licensed under a Creative Commons Attribution BY 4.0 licence (CC BY 4.0).

Open Access Policy のページ (<https://www.oecd.org/en/about/oecd-open-by-default-policy.html>、Internet Archive の 2026-09-26 の保存) も範囲を書かれたものに限っている:

> The OECD Open Access Policy applies to most written content published by the Organisation, including OECD publications, working papers, journal articles, policy papers, policy briefs, case studies and country notes.

Data の節は 2024-07-01 の改定の前後で同じである。旧 URL の Internet Archive の 2024-02-01 の保存 (`https://web.archive.org/web/20240201005244id_/https://www.oecd.org/termsandconditions/`、「Last updated on 16/08/2018」) の「(c) Data」の Permitted Use の段落は、新しい規約の段落と、`You` の大文字小文字を除いて一字一句同じだった。統計データの利用条件は少なくとも 2018-08-16 の版から、CC BY 4.0 ではなく OECD 独自の規約 (帰属表示付きで商用・再配布可) のままである。

### Hugging Face に置くことについて

- 規約の文面上は、出典表示を付ければ再配布も商用利用もできる。ライセンス名としては CC BY 4.0 ではなく「OECD Terms and Conditions」(other) と書くのが正しい。
- 置くときに要るもの: OECD の引用形式での出典、取得日、データフローの ID と版、出典表示を引き継ぐ要件の明記。
- 他機関由来の系列 (Eurostat、IEA など) を含むデータフローは、OECD の規約の外の条件がかかりうる。除くかどうかを機械的に決める欄は API に無い。
- OECD のロゴは使えない (規約の「5. OECD Logo」)。

## 版

- データは上書き更新。データフローの問い合わせで版を省くと最新の構造の版のデータが返り、同じキーの値は更新で置き換わる。FAQ も、最新の値を見るにはブックマークした URL から版の引数 (`df[vs]`) を外せと書いている。
- データフローの「版」は構造 (DSD) の版で、データのヴィンテージではない。`dataflow/all/all/all` は 2,689 件を返し、latest の 1,548 件のうち 732 件が複数の版を持つ (`DSD_REG_DEMO@DF_POP_5Y` は 1.0、2.0、2.4)。古い版の構造と制約は残っている (`DF_POP_5Y` 1.0 の制約は 1995 年から 2025 年、観測数 12,473,341 と応答した) が、1.0 を指定したデータの要求は日本の国レベルでも `NoResultsFound` (404) だった。古い版でデータが取れるとは限らない。
- 過去の時点の値を取る標準の引数 (`includeHistory`、`asOf`) は 500 を返し、使えなかった。
- 例外として、過去の公表値そのものをデータにしたものがある。`DSD_STES_REVISIONS@DF_STES_REVISIONS` (Short-term economic statistics revisions) は `EDITION` 次元に 1999-02 から 2026-09 までの 332 の月次の版を持ち、60 の国・地域、22 の指標 (GDP、失業率、物価など)、観測数 78,344,373。説明文は「Access monthly data snapshots of published short term economic statistics and observe the revisions made to key economic variables.」。
- 更新の時刻は `contentconstraint` の `validFrom` で分かる。public の 1,510 件の年の内訳は 2026 年が 1,090、2025 年が 290、2024 年が 120、2023 年が 10。運用の説明は「most OECD datasets are updated infrequently (with revisions occurring primarily once or twice a year)」と書く。データの応答の `last-modified` (`DF_POP_5Y` で 2023-11-14) は `validFrom` (2026-07-17) と合わず、更新の目印には使えない。
- 版を残したいなら、取った側で取得日ごとに保存するしかない。archive の空間は OECD.Stat 時代のデータを凍結したもので、`validFrom` は 1,261 件が 2024 年、110 件が 2023 年。これは過去の版というより、移行で新しい基盤に移らなかったデータの置き場である。

## 未確認の点

- `www.oecd.org` の規約ページを本体から直接は読めていない (Cloudflare のチャレンジ)。読んだのは Internet Archive の 2026-10-03 の保存。
- データフローごとの第三者の権利の有無を、API や画面の「source」タブから機械的に取る方法。
- 引用の形式が個別に決まっているデータ (「the citation associated with the relevant Data」) が、API のどこに出るか。参照メタデータ (v2 の `attributes=msd`) は試していない。
- 回数制限の数え方 (構造の問い合わせも数えるか、IP 単位か)。今回の要求では 429 は出なかった。
- public の観測数の重複を除いた実数と、全体を CSV にしたときの実際の大きさ。
- 地域 (TL2、TL3) や都市圏 (FUA) の境界の形状がどこで、どの条件で配られているか。
- 全データフローを通した期間の最古と最新。
- archive の空間のデータの利用条件が public と同じか (同じ規約が当たると考えられるが、個別の記載は確かめていない)。
