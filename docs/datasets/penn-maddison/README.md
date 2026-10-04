# Penn World Table (PWT) と Maddison Project Database (MPD)

2026-10-04 に読んで確かめた内容。どちらもフローニンゲン大学の Groningen Growth and Development Centre (GGDC) が公開している。
配布ページ (www.rug.nl) は curl でそのまま読めた (ボット対策の画面は出なかった)。
ファイルの一覧、大きさ、ハッシュ、版の履歴は DataverseNL の公開 API
(`/api/datasets/:persistentId/`、`/api/datasets/:persistentId/versions`、`/api/search`、`/api/dataverses/GGDC/contents`) から取った。
rug.nl に置かれた過去の版のファイルは HEAD を 1.2 秒間隔で投げて大きさと Last-Modified を取った。
中身を開いたのは `pwt110.xlsx` (5,839,841 バイト) と `mpd2023_web.xlsx` (4,903,804 バイト) の 2 本だけで、
どちらも DataverseNL が示す SHA-1 と一致した。ほかのファイルは開いていない。

- 運営: Groningen Growth and Development Centre, Faculty of Economics and Business, University of Groningen。
- いまの一次配布元は DataverseNL (<https://dataverse.nl/dataverse/GGDC>)。rug.nl の配布ページの
  「Excel」「Stata」のリンクは `https://dataverse.nl/api/access/datafile/<id>` を指している。
  ファイルの実体は SURF のオブジェクトストア (`objectstore.surf.nl`) に置かれ、`/api/access/datafile/<id>` は 303 でそこへ転送する。
- 2021 年以前の版 (PWT 10.0 まで、MPD 2020 まで) は DataverseNL に無く、rug.nl の静的ファイルとして配られている。
- ライセンスは、PWT 8.0 以降と MPD 2018 以降の配布ページに CC BY 4.0 と明記されている。
  PWT 7.1 以前と MPD 2013、Maddison Database 2010 のページにはライセンスの記載が無い。

| | PWT | MPD |
|---|---|---|
| 現行の版 | 11.0 (2025-10-07) | 2023 (DataverseNL 公開 2024-04-26) |
| DOI | 10.34894/FABVLR | 10.34894/INZBF2 |
| 範囲 | 185 か国、1950〜2023 年 | 169 か国、西暦 1 年〜2022 年 |
| 主な変数 | 実質 GDP、人口、就業者、労働時間、人的資本、資本ストック、TFP、為替、物価水準、支出構成 | 1 人あたり実質 GDP (2011 年ドル)、人口 |
| 配布ファイル | 12 本、40,728,519 バイト | 2 本、15,796,193 バイト |
| 形式 | xlsx、dta (Stata 14)、zip、pdf | xlsx、dta (Stata 14) |
| ライセンス | CC BY 4.0 | CC BY 4.0 |

## Penn World Table

### 作成と配布元

- 入口: <https://www.rug.nl/ggdc/productivity/pwt/> (ページ名「PWT 11.0 | Penn World Table」、Last modified 2026-03-19)。
  `www.ggdc.net/pwt` もここを指す名前として使われている。
- DataverseNL: <https://doi.org/10.34894/FABVLR> (データセット名「Penn World Table version 11.0」)。
  著者の欄は「Groningen Growth and Development Centre」、所属は University of Groningen (ROR 012p63287)。
- ライセンスの表示上の作成者は Robert C. Feenstra、Robert Inklaar、Marcel P. Timmer の 3 人。
- 配布ページの説明 (原文):

> PWT version 11.0 is a database with information on relative levels of income, output, input and productivity, covering 185 countries between 1950 and 2023.

> Published on October 7, 2025, PWT 11.0 constitutes a major update from PWT 10.01.

- PWT 11.0 は英国 FCDO の資金による STEG プロジェクトの支援を受けている (配布ページの「License and funding」)。
  PWT 10.01 以前は National Science Foundation、Sloan Foundation などの支援と書かれている。
- 一部の変数はウェブの「Online data access tool」(<https://pwt-data-tool.streamlit.app>) でも引ける。
  一括取得には使えないので、ここでは扱わない。

### 中身

`pwt110.xlsx` のシートは Info、Legend、Data の 3 つ。Data は 51 列 × 13,690 行で、
185 か国 × 74 年 (1950〜2023) の全組み合わせが 1 行ずつ並ぶ (どの国も 74 行)。値の無い年も行はある。

| 群 | 列 |
|---|---|
| 識別 | countrycode (ISO 3166-1 alpha-3)、country、currency_unit、year |
| 実質 GDP、雇用、人口 | rgdpe、rgdpo (連鎖 PPP、百万 2021 年米ドル)、pop (百万人)、emp (就業者、百万人)、avh (年間労働時間)、hc (人的資本指数) |
| 当年 PPP の GDP、資本、TFP | ccon、cda、cgdpe、cgdpo、cn (資本ストック)、ck、ctfp、cwtfp |
| 国民経済計算ベース | rgdpna、rconna、rdana、rnna、rkna、rtfpna、rwtfpna (2021 年の自国価格)、labsh (労働分配率)、irr、delta (減価償却率) |
| 為替と物価水準 | xr (対米ドル為替)、pl_con、pl_da、pl_gdpo |
| データの由来 | i_cig、i_xm、i_xr、i_outlier、i_irr、cor_exp |
| CGDPo に占める割合 | csh_c、csh_i、csh_g、csh_x、csh_m、csh_r |
| 支出項目別の物価水準 | pl_c、pl_i、pl_g、pl_x、pl_m、pl_n、pl_k |

- PWT 11.0 の基準年は 2021 年 (Legend の単位が「mil. 2021US$」「2021=1」)。PWT 10.x までの基準年とは違うので、
  版をまたいで値を並べると水準がずれる。
- 値のある行数: rgdpe / rgdpo / pop / rgdpna / xr / pl_gdpo / csh_c が 11,201、emp 10,307、hc 9,217、labsh 8,215、
  ctfp / rtfpna 6,988、avh 5,015。rgdpe のある国は 1950 年 55、1960 年 111、1970 年 158、2000 年 182、2023 年 185。
- 日本 (JPN) の 2023 年は rgdpo 5,505,348、pop 124.370947、emp 67.93、hc 3.657、ctfp 0.640、xr 140.49。
- 各国内の地域区分は無い。国の単位だけ。

### 配布ファイル (PWT 11.0、DataverseNL)

| ファイル | 大きさ (バイト) | 中身 |
|---|---:|---|
| `pwt110.xlsx` | 5,839,841 | 本体 |
| `pwt110.dta` | 3,739,965 | 本体 (Stata) |
| `pwt110_na_data.xlsx` / `.dta` | 2,732,538 / 2,092,044 | 自国価格の国民経済計算、為替、人口 |
| `pwt110_capital_detail.xlsx` / `.dta` | 3,948,645 / 1,793,875 | 資産別の投資、資本ストック、資本減耗 |
| `pwt110_labor_detail.dta` | 2,723,875 | 雇用、学歴、労働分配率の出典と方法 |
| `pwt110_trade_detail.dta` | 1,817,863 | 広義経済分類 (BEC) 別の輸出入 |
| `pwt110_sh_bilateral_cor_data.dta` | 10,642,598 | ベンチマーク年の支出構成の 2 国間相関 |
| `program_package_pwt_110.zip` | 4,883,267 | PWT を再現する Stata のデータと do ファイル |
| `pwt110_user_guide_to_data_files.pdf` | 119,363 | 利用者向けの説明 |
| `pwt110_whatsnew.pdf` | 394,645 | 10.01 からの変更点 |

- 合計 12 本、40,728,519 バイト (約 38.8 MiB)。どれも制限 (restricted) は付いていない。
- CSV は無い。dta は DataverseNL の表形式への取り込み (ingest) がされておらず、元の Stata ファイルのまま配られている。
- 配布ページの「NA vintages」(2009、2010、2011、2014、2017、2019 年までの国民経済計算) と
  「ICP benchmark data」(1970、1975、1980、1985、1996) のリンクは、PWT 11.0 のデータセットではなく
  PWT 10.01 のデータセット (10.34894/QT5BCC) のファイルを指している。

### 取り出し方

区分は whole。本体は xlsx か dta の 1 本 (最小 3,739,965 バイト) を丸ごと取れば足りる。
補助の表は用途別に分かれたファイルなので、その意味では split でもある。

| 区分 | 手段 | 実測 |
|---|---|---|
| whole | 本体 `pwt110.xlsx` か `pwt110.dta` | 5.8MB / 3.7MB |
| split | 用途別の補助ファイル | 本体を含め 12 本 |
| range | オブジェクトストア上のファイル | `curl -L -r 0-1023` が 206 と `content-range: bytes 0-1023/5839841` を返した。ただし xlsx は zip で、行を選んで読める索引は無い。大きさから見ても Range で絞る意味は薄い |
| catalog | DataverseNL の API | ファイルの一覧、大きさ、SHA-1、版の履歴は認証なしで引ける。中の行は選べない |

## Maddison Project Database

### 作成と配布元

- 入口: <https://www.rug.nl/ggdc/historicaldevelopment/maddison/> (ページ名「Maddison Historical Statistics」)。
  版の一覧は <https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/>。
- 現行版のページ: <https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023>
  (Last modified 2024-09-24)。
- DataverseNL: <https://doi.org/10.34894/INZBF2> (データセット名「Maddison Project Database 2023」、公開 2024-04-26)。
  著者は Jutta Bolt (University of Groningen) と Jan Luiten van Zanden (Utrecht University)。
- Internet Archive が 2023 版のページを最初に保存したのは 2024-04-29 で、DataverseNL の公開日と合う。
- 背景 (入口のページの原文):

> The Maddison Project has been initiated in March 2010 by a group of close colleagues of Angus Maddison, with the aim to support an effective way of cooperation between scholars to continue Maddison's work on measuring economic performance for different regions, time periods and subtopics.

> The original estimates are kept intact, and only revised or adjusted when there is more and better information available.

- 2023 版のページの説明 (原文):

> The 2023 version of this database covers 169 countries and the period up to 2022.

### 中身

`mpd2023_web.xlsx` のシートは Notes、Sources、GDPpc、Population、Full data、Regional data、Maddison original sources の 7 つ。

- Notes の定義: GDPpc は「Real GDP per capita in 2011$」、Population は「Population, mid-year (thousands)」。
- Full data は縦持ちで、列は countrycode、country、region、year、gdppc、pop の 6 つ。131,144 行。
  169 か国 × 776 の年 (どの国も 776 行)。年は 1、730、1000、1090、1150、1252 から 2022 まで飛び飛びに始まり、途中から毎年になる。
- 行の大半は空。gdppc のある行は 21,366、pop のある行は 17,875、両方あるのは 15,961。
- gdppc のある国は、西暦 1 年が 14 か国 (BEL、CHE、EGY、ESP、FRA、GRC、IRN、IRQ、ISR、ITA、JOR、PRT、TUN、TUR)、
  1820 年 55、1950 年 146、2022 年 169。
- GDPpc と Population のシートは同じ値の横持ち (行が年、列が国、上の 3 行が国名、地域、ISO コード)。
- Regional data は 8 地域 (East Asia、Eastern Europe、Latin America、Middle East and North Africa、
  South and South East Asia、Sub Saharan Africa、Western Europe、Western Offshoots) と世界の 1 人あたり GDP と人口。1820 年から。
- countrycode は ISO 3166-1 alpha-3 に近いが、CSK (Czechoslovakia) のような消滅した国を含む。
- 日本 (JPN) は 1 年に人口 3,000 (千人)、1600 年に gdppc 1,061 と人口 18,500、2022 年に gdppc 38,268.79 と人口 124,762.11。
- Sources シートは国ごとの出典の一覧 (202 行)。冒頭に「GDP pc: 2008 - 2022: Total Economy Database the Conference Board for all countries included in TED. Otherwise UN national accounts statistics」とある。
  近年の値は Conference Board の Total Economy Database と国連の国民経済計算から来ている。

### 配布ファイル (MPD 2023、DataverseNL)

| ファイル | 大きさ (バイト) | SHA-1 |
|---|---:|---|
| `mpd2023_web.xlsx` | 4,903,804 | 1480521f602fbd5df64e108867ac971caa00ed1a |
| `maddison2023_web.dta` | 10,892,389 | 264862c8a188d4bc770b607663211ec1c4eb0d5d |

合計 2 本、15,796,193 バイト。CSV は無い。

### 取り出し方

区分は whole。1 本 (xlsx 4.9MB) を丸ごと取れば全部入っている。
Range はオブジェクトストアでは効くが (PWT と同じ配信)、行を選ぶ索引は無い。

## ライセンス

### 配布ページの表示

PWT 11.0 の配布ページ (<https://www.rug.nl/ggdc/productivity/pwt/>、2026-10-04 に読んだ):

> Penn World Table 11.0 by Robert C. Feenstra, Robert Inklaar and Marcel P. Timmer is licensed under a Creative Commons Attribution 4.0 International License.

リンク先は `http://creativecommons.org/licenses/by/4.0/`。

MPD 2023 の配布ページ (<https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023>、2026-10-04 に読んだ):

> Maddison Project Database, version 2023 by Jutta Bolt and Jan Luiten van Zanden is licensed under a Creative Commons Attribution 4.0 International License.

- DataverseNL のメタデータでも、PWT 11.0、PWT 10.01、MPD 2023 の全版で `license.name` が `CC-BY-4.0`
  (`uri` は `http://creativecommons.org/licenses/by/4.0`)。`termsOfUse` と `termsOfAccess` は空。
- 過去の版のページのライセンス表示 (2026-10-04 に読んだ):

| 版 | 表示 |
|---|---|
| PWT 10.01、10.0、9.1、9.0、8.1、8.0 | 各版の題名と Feenstra、Inklaar、Timmer の名で CC BY 4.0 |
| PWT 7.1、7.0、6.3、6.2、6.1、5.6 | ライセンスの記載なし。帰属の指定 (Heston、Summers、Aten) と NSF の助成の注記だけ |
| MPD 2020 | Bolt と van Zanden の名で CC BY 4.0 |
| MPD 2018 | Bolt、Inklaar、de Jong、van Zanden の名で CC BY 4.0 |
| MPD 2013 | ライセンスの記載なし。引用の指定だけ |
| Maddison Database 2010 | ライセンスの記載なし |

CC BY 4.0 と言われているのは確かめられた。ただし PWT 8.0 以降と MPD 2018 以降に限る。

### CC BY 4.0 の条文

<https://creativecommons.org/licenses/by/4.0/legalcode.en> (2026-10-04 に読んだ)。

> the Licensor hereby grants You a worldwide, royalty-free, non-sublicensable, non-exclusive, irrevocable license to exercise the Licensed Rights in the Licensed Material to: reproduce and Share the Licensed Material, in whole or in part; and produce, reproduce, and Share Adapted Material.

> retain the following if it is supplied by the Licensor with the Licensed Material: identification of the creator(s) of the Licensed Material and any others designated to receive attribution, in any reasonable manner requested by the Licensor

- 再配布、改変 (Parquet への変換など)、商用利用ができる。非商用の制限も share-alike も無い。
- 要るのは、作成者の表示、ライセンスへの参照、元の資料への URI、改変したことの表示。

### 引用の指定

PWT (配布ページの「Attribution requirement」、全版共通で 8.0 以降):

> When using these data (for whatever purpose), please make the following reference:
> Feenstra, Robert C., Robert Inklaar and Marcel P. Timmer (2015), "The Next Generation of the Penn World Table" American Economic Review, 105(10), 3150-3182, available for download at www.ggdc.net/pwt

DataverseNL の説明には DOI 10.1257/aer.20130954 が添えられている。

MPD 2023 (配布ページと xlsx の Notes シート):

> All original papers must be cited when:
> the data is shown in any graphical form
> subsets of the full dataset that include less than a dozen (12) countries are used for statistical analysis or any other purposes
> A list of original papers can be found in the source sheet of the database. When neither a) or b) apply, then the MPD as a whole should be cited.
> MPD version 2023: Bolt, Jutta and Jan Luiten van Zanden (2024), "Maddison style estimates of the evolution of the world economy: A new 2023 update", Journal of Economic Surveys, 1–41. DOI: 10.1111/joes.12618

- MPD は、図にするときと 12 か国未満の部分集合を使うときに、元の論文 (Sources シートの出典) をすべて引用せよと求めている。
  これはライセンス条文の外側の、作成者からの「要請」として書かれている。CC BY 4.0 の帰属条件
  (「in any reasonable manner requested by the Licensor」) との関係は、作成者に確かめていない。
- 版ごとに引用すべき論文が違う。2020 版は Bolt and van Zanden (2020) の working paper (wp15)、
  2018 版は Bolt, Inklaar, de Jong and van Zanden (2018) の Maddison Project Working paper 10、
  2013 版は Bolt and van Zanden (2014) The Economic History Review 67(3)。

### 大学のサイトの一般規約との関係

rug.nl の Disclaimer & Copyright (<https://www.rug.nl/info/disclaimer-copyright>、2026-10-04 に読んだ):

> The texts, images, logos, audio and video on the website, as well as its design, may not be copied, modified or otherwise used without the prior and explicit consent of the University of Groningen.

対象はウェブサイトの文章、画像、ロゴ、音声、動画、デザインで、データファイルは挙がっていない。
データにはデータセットごとに CC BY 4.0 が明記され、DataverseNL のメタデータも同じなので、データには CC BY 4.0 が適用されると読める。
これは文言からの解釈で、GGDC に確かめてはいない。

### Hugging Face に置くこと

- PWT 8.0〜11.0 と MPD 2018、2020、2023 は CC BY 4.0 のもとで再配布、改変、商用利用ができる。
  Hugging Face の `license: cc-by-4.0` に当てはまる。
- 置くときに要るもの: 版ごとの作成者の表示 (PWT は Feenstra、Inklaar、Timmer。MPD は版ごとの著者)、
  ライセンスの URI、元の DOI (10.34894/FABVLR、10.34894/INZBF2 など)、指定された論文の引用、
  形式を変えた (xlsx から Parquet など) ことの記載。MPD は上の「元の論文をすべて引用」の要請もカードに書いておく。
- PWT 7.1 以前、MPD 2013、Maddison Database 2010 はライセンスが示されていないので、そのままでは再配布の根拠が無い。
- 中身には第三者の統計が入っている (PWT は各国の国民経済計算と ICP、MPD 2023 は Conference Board の
  Total Economy Database と国連の統計)。作成者は加工後の表全体を CC BY 4.0 で出しているが、
  元の統計の条件がどう効くかは確かめていない。

## 版

### PWT

rug.nl の Earlier Releases (<https://www.rug.nl/ggdc/productivity/pwt/earlier-releases>) に 12 版が並ぶ。

| 版 | 公表 | 範囲 | 配布元 | DOI | 本体の大きさ (バイト) |
|---|---|---|---|---|---|
| 11.0 | 2025-10-07 | 185 か国、1950〜2023 | DataverseNL | 10.34894/FABVLR | xlsx 5,839,841 / dta 3,739,965 |
| 10.01 | 2023-01-23 | 183 か国、1950〜2019 | DataverseNL | 10.34894/QT5BCC | xlsx 6,551,843 / dta 3,452,645 |
| 10.0 | 2021-06-18 更新 | 183 か国、1950〜2019 | rug.nl | 10.15141/S5Q94M | xlsx 6,561,820 / dta 3,452,645 |
| 9.1 | (Last-Modified 2019-04-09) | 182 か国、1950〜2017 | rug.nl | 10.15141/S50T0R | xlsx 6,267,402 / dta 3,071,612 |
| 9.0 | (Last-Modified 2016-09-08) | 182 か国、1950〜2014 | rug.nl | 10.15141/S5J01T | xlsx 4,784,339 / dta 3,131,446 |
| 8.1 | 2015-04-13 | 8.0 と同じ | rug.nl | 10.15141/S5NP4S | xlsx 4,168,966 / Stata zip 1,608,751 |
| 8.0 | 2013-07-02 | 167 か国、1950〜2011 | rug.nl | 10.15141/S5159X | xlsx 3,595,338 / Stata zip 1,588,858 |
| 7.1 | 2012-11-03 | 189 か国と地域、1950〜2010 | rug.nl | なし | zip 1,582,077 |
| 7.0 | 2011-06-03 | 189、1950〜2009 | rug.nl | なし | zip 1,546,392 |
| 6.3 | 2009-08 | 189、1950〜2007 | rug.nl | なし | zip 2,762,758 |
| 6.2 | 2006-09 | 188、1950〜2004 | rug.nl | なし | xlsx 3,021,688 |
| 6.1 | 2002-10 | 168、1950〜2000 | rug.nl | なし | xlsx 2,251,711 |
| 5.6 | 不明 | 152、1950〜1992 | rug.nl | なし | xls 1,349,120 |

- rug.nl のファイルは `https://www.rug.nl/ggdc/docs/<名前>` (例 `pwt100.xlsx`、`pwt91.dta`、`pwt71_11302012version.zip`)。
  すべて HEAD で大きさが返った。Last-Modified は 9.0 以前が 2016-09-08〜09 (サイトの移設時に置き直したもの)。
- 10.15141 の DOI は doi.org から rug.nl の各版のページへ 302 で転送される。DataverseNL のデータセットではない。
- DataverseNL にあるのは 10.01 と 11.0 だけ (検索 API で「penn world table」を引いて確かめた)。
- 7.1 以前はペンシルベニア大学の Center for International Comparisons (Heston、Summers、Aten) の作で、
  8.0 から GGDC (Feenstra、Inklaar、Timmer) の「Next Generation」に変わった。変数の体系も違う
  (8.0 のページに PWT 7.1 との変数対応表がある)。
- 10.0 の dta と 10.01 の dta (DataverseNL) は同じ 3,452,645 バイト。中身が同じかは確かめていない。

#### DataverseNL の版の中の更新

- PWT 11.0 のデータセットには 2 つの版がある。1.0 (2025-10-07) と 2.0 (2025-10-10)。
  違いは `pwt110.xlsx` だけで、1.0 のもの (datafile 554027、5,841,216 バイト) が 2.0 で 554105 (5,839,841 バイト) に差し替わった。
  ほかの 11 本は SHA-1 が同じ。版の説明 (versionNote) は空で、差し替えの理由は書かれていない。
- 差し替え前の 554027 も `/api/access/datafile/554027` で 303 が返り、いまも取れる。
- PWT 10.01 は 1.0 と 1.1 (どちらも 2023-01-26) で、ファイルの SHA-1 は全部同じ (メタデータだけの更新)。
- ファイル名は版の中で変わらないので、取り込むときは DataverseNL の版番号と SHA-1 を記録する必要がある。

### MPD

rug.nl の Releases (<https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/>) の原文:

> To date there have been four releases of the Maddison Project Database, the 2013, 2018, 2020, and 2023 releases. Additionally we present the last version of the original Maddison database from 2010.

| 版 | 範囲 | 配布元 | ファイル (バイト) | ライセンス |
|---|---|---|---|---|
| MPD 2023 | 169 か国、〜2022 | DataverseNL (10.34894/INZBF2) | xlsx 4,903,804 / dta 10,892,389 | CC BY 4.0 |
| MPD 2020 | 169 か国、〜2018 | rug.nl | `mpd2020.xlsx` 1,764,793 / `mpd2020.dta` 1,196,265 | CC BY 4.0 |
| MPD 2018 | 169 か国、〜2016 | rug.nl | `mpd2018.xlsx` 1,955,430 / `mpd2018.dta` 1,378,770、地域 `mpd2018_region_data.xlsx` 61,702、1990 年基準 `mpd2018_1990bm.xlsx` 700,128 | CC BY 4.0 |
| MPD 2013 | 西暦 1〜2010 | rug.nl | `mpd_2013-01.xlsx` 354,233 | 記載なし |
| Maddison Database 2010 | 西暦 1〜2008 | rug.nl | `md2010_vertical.xlsx` 757,968 / `md2010_horizontal.xlsx` 1,433,284 | 記載なし |

- rug.nl のファイルは `https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/<名前>`。すべて HEAD で大きさが返った。
- rug.nl の静的ファイルは Range を受け付けない。`curl -r 0-1023` に 200 と全体 (`mpd2020.xlsx` で 1,764,793 バイト) が返った。
- 2018 版と 2020 版は方法が違う。2020 版のページの原文:

> We now offer a new 2020 update of the Maddison Project database, which uses a different methodology compared to the 2018 update. The approach of the 2018 update is identical to that of Penn World Tables, ... The 2020 update has to some extent gone back to the original Maddison approach to remedy for this

  2018 版は 2 種類の 1 人あたり実質 GDP の系列を持つ (ページは利用者ガイドを読むよう強く勧めている)。
  2023 版の単位は 2011 年ドル。版をまたいで値を縦に積むことはできない。
- Angus Maddison 自身の最終版 (2010) の解説は、Internet Archive に保存された元のサイト
  (<https://web.archive.org/web/20211102093357/http://www.ggdc.net/maddison/oriindex.htm>) を見るよう案内されている。
- DataverseNL で「maddison」を検索すると 3 件で、MPD は 2023 版だけ。ほかに Bolt と van Zanden の
  「The long view on economic growth: New estimates of GDP」(10.34894/I7YZIV、2026-01-08 公開、CC0 1.0、
  xlsx 2 本と docx 2 本、合わせて約 0.56MB) がある。説明に「This paper is a first product of the project.」とある論文の付属データで、MPD 本体ではない。

## 未確認の点

- MPD の「元の論文をすべて引用」の要請が、CC BY 4.0 の帰属条件として拘束力を持つのか、お願いにとどまるのか。GGDC に確かめていない。
- PWT 7.1 以前、MPD 2013、Maddison Database 2010 の再配布の可否。ページにライセンスの記載が無く、作成者 (ペンシルベニア大学側を含む) に確かめていない。
- 元になった第三者の統計 (Conference Board の Total Economy Database、ICP、各国の国民経済計算) の条件が、加工後の表の再配布に影響するか。
- PWT 11.0 の `pwt110.xlsx` が公表 3 日後に差し替わった理由と、差し替え前後の中身の違い。差し替え前のファイルは開いていない。
- PWT 10.0 と 10.01 の dta が同じ大きさである理由 (同じ中身か)。
- dta、補助ファイル、過去の版の中身と行数。開いたのは PWT 11.0 と MPD 2023 の xlsx 2 本だけ。
- PWT 5.6 の公表日。ページに記載が無い。
- DataverseNL のデータセット一括 zip の取得 (`/api/access/dataset/...`) が使えるか。試していない。
