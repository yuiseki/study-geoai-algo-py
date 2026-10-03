# ILOSTAT (国際労働機関の労働統計データベース)

2026-10-04 に読んで確かめた内容。一括配布の一覧ページ 3 つと目次 CSV を curl で取得して数えた。
データ本体は小さいファイルを 1 本 (`INJ_WORK_SEX_MIG_NB_A`、展開後 451,326 バイト) だけ展開して中身を見た。
ほかのファイルの大きさは、取得したバイト数を `/dev/null` に捨てて測った値。
`ilostat.ilo.org` は Cloudflare のチャレンジ (`cf-mitigated: challenge`、HTTP 403) を返すため、
このサイトのページは Internet Archive の保存 (2026-07 のもの) で読んだ。

- 入口: <https://ilostat.ilo.org/> (ページ名「ILOSTAT」)。一括配布の説明は <https://ilostat.ilo.org/data/bulk/> (「Bulk download facility」)。
- 一括配布の実体: <https://rplumber.ilo.org/files/website/bulk/indicator.html>、
  <https://rplumber.ilo.org/files/website/bulk/ref_area.html>、<https://rplumber.ilo.org/files/website/bulk/dic.html>。
  ファイルは `https://rplumber.ilo.org/data/indicator?id=<ID>&format=.csv.gz` の形で、その場で生成される。
- SDMX API: <https://sdmx.ilo.org/rest/> (NSI Web Service v8.19.6.0)。
- 作成: 国際労働機関 (ILO、International Labour Organization)。一次配布元は ILO 自身の上の 3 つのホストで、
  ほかに転載元を経由していない。ただし値の多くは各国の統計機関や他の国際機関が出したもの (後述「第三者のデータ」)。
- 中身: 国別・年別 (一部は四半期別・月別) の労働統計。雇用、失業、労働時間、賃金、非公式経済、児童労働、労働災害、移民労働など。
  ILO 自身の推計 (ILO Modelled Estimates) と、各国の調査・行政記録から集めた値が同じ形で並ぶ。
- ライセンス: ILO の「Rights and permissions」によれば、2023-05-03 以降に公開されたデータベースとデータセットは CC BY 4.0。
- 一括配布は日々上書きされる。配布元は過去の版を置いていない。Internet Archive に 2024-06 以降の取得物がまとまって残っている。

## 配布ファイル

### 一覧ページ

`https://rplumber.ilo.org/files/website/bulk/` の下に 3 つの一覧ページがある。ブラウザ風の User-Agent を付けないと
200 で本文が空 (0 バイト) になる。ページが無いのではない。

| 一覧 | 単位 | ファイル数 | 列 |
|---|---|---:|---|
| indicator.html | 指標 × 頻度 | 1,964 (+ 目次 3) | file name, last.update, n.records, n.ref_area |
| ref_area.html | 地域 × 頻度 | 741 (+ 目次 3) | file name, last.update, n.records, n.indicator |
| dic.html | コード表 | 488 | file name, last.update |

- 2026-10-04 時点で、ページの末尾は「Last update: 2026-10-03」、Last-Modified は `Sat, 03 Oct 2026 21:01:05 GMT`。
- indicator の n.records の合計は 399,233,303、ref_area の合計も 399,233,303 で一致した。同じデータを 2 通りに切り分けたもの。
- 形式は 1 ファイルにつき 10 種類から選べる: `.csv.gz`、`.csv`、`.dta`、`.csv2`、`.feather`、`.rds`、`.parquet`、`.tsv`、`.json`、`.xlsx`。
  一覧のリンクは `.csv.gz`。目次とコード表のリンクは `.csv`。
- 目次: `https://rplumber.ilo.org/metadata/toc/indicator?lang=en&format=.csv` (en/fr/es)。
  ref_area 用は `https://rplumber.ilo.org/metadata/toc/ref_area?lang=en&format=.csv`。
- コード表: `https://rplumber.ilo.org/metadata/dic?var=<名前>&lang=en&format=.csv`。`cl_age`、`cl_eco`、`ref_area`、`source`、`note_source` など。

### 応答の性質

- ファイルは要求のたびに生成される。`content-disposition` の名前に生成時刻が付く
  (`INJ_WORK_SEX_MIG_NB_A-20261004T0116.csv.gz`)。`Content-Length` も `Last-Modified` も無い。`cf-cache-status: DYNAMIC`。
- HEAD は 405 (`application/json`) で、大きさを HEAD で測れない。
- `Range: bytes=0-1023` を付けても 200 で全体が返る。

測った大きさ (`.csv.gz`):

| ファイル | n.records | バイト | 1 行あたり |
|---|---:|---:|---:|
| INJ_WORK_SEX_MIG_NB_A | 4,436 | 38,913 | 8.8 |
| X91_A (ref_area) | 33,211 | 243,525 | 7.3 |
| EMP_TEMP_SEX_ECO_EDU_NB_Q (最大) | 4,766,490 | 33,150,844 | 7.0 |

同じ `INJ_WORK_SEX_MIG_NB_A` の `.parquet` は 44,482 バイト。

全体の大きさは測っていない。1 行 7.0〜8.8 バイトを 399,233,303 行に掛けると、indicator の側だけで
`.csv.gz` 約 2.8〜3.5GB になる。これは 3 本からの推定。

## 中身

### 指標

目次 (indicator, en) は 1,964 行、20 列。

- 列: `id`, `indicator`, `indicator.label`, `freq`, `freq.label`, `rep_var`, `rep_var.label`, `classification`,
  `classif.labels`, `data.start`, `data.end`, `last.update`, `n.records`, `n.records.all`, `n.ref_area`, `with.region`,
  `subject`, `subject.label`, `database`, `database.label`。
- `indicator` の異なり数は 1,213。これを頻度で分けたものが 1,964 ファイル。年次 1,204、四半期 590、月次 170。
- 期間: `data.start` の最小は 1914、`data.end` の最大は 2030。`data.end` が 2026 年より後のものは推計・予測を含む。
- `n.records` の合計は 399,233,303、`n.records.all` の合計は 429,502,365。2 つの差の意味は確かめていない。
- 地域の集計 (`with.region` = Y) を含む指標は 106。

主題 (`subject.label`) の上位:

| 主題 | ファイル数 |
|---|---:|
| Unemployment and labour underutilization | 457 |
| Informal economy | 450 |
| Employment | 245 |
| Hours of work | 146 |
| Earnings and income | 129 |
| Employees | 102 |
| Labour force | 93 |
| Population | 67 |
| International migrant stock | 46 |
| Child labour | 38 |

ほかに 17 の主題 (技能、ケア労働者、STEM、観光、公務員、労働災害、物価、労使関係、労働生産性、労働監督、社会保障など)。

データベース (`database.label`) は 17: Labour Force Statistics (LFS) 405、Wages and Working Time Statistics (COND) 262、
Education and Mismatch Indicators (EMI) 253、Rural and Urban Labour Markets (RURBAN) 215、
Disability Labour Market Indicators (DLMI) 191、Gender Equality and Non-Discrimination Indicators (GEND) 182、
Worker and Sector Profiles 96、International Labour Migration Statistics 71、YouthSTATS 68、Work Statistics (19th ICLS) 56、
ILO Modelled Estimates (ILOEST) 47、Child Labour Statistics 35、ILOSDG 25、OSH 19、ILOSECTOR 18、PRICES 15、IRdata 6。

最大のファイルは四半期の `EMP_TEMP_SEX_ECO_EDU_NB_Q` (4,766,490 行、100 地域)、最小は月次の `EIP_WDIS_SEX_AGE_NB_M` (209 行、3 地域)。

### 地域の単位

ref_area の一覧は 327 地域。年次 327、四半期 207、月次 207 で 741 ファイル。

- 国・地域は ISO 3166 の 3 文字コード (AFG、JPN など)。消滅したもの (ANT、オランダ領アンティル) も残る。
- `X` で始まる 93 コード (X01〜X99、XA1) は世界、地域、所得グループなどの集計。国と同じ列に並ぶので、国別の分析ではこれを除く必要がある。
- 国の下 (州・県など) の単位は無い。都市・農村の別 (`cl_geo`) は分類として持つ。

### 列

`INJ_WORK_SEX_MIG_NB_A` の CSV (UTF-8、見出しあり、カンマ区切り) は 4,436 行で、目次の n.records と一致した。

```
ref_area, source, indicator, sex, classif1, time, obs_value, note_indicator, note_source
"ANT","FA:854","INJ_WORK_SEX_MIG_NB","SEX_T","MIG_STATUS_TOTAL","1999",55.268,"T13:149","S9:259"
```

値はコードで入っていて、名前はコード表で引く。列は指標によって増減する (`classif2`、`obs_status`、`note_classif` など)。

### 第三者のデータ

`source` 列は出典のコード。コード表 `source` (3,805 行) の接頭辞で種類が分かる。

| 接頭辞 | 種類 | 例 |
|---|---|---|
| BA, BB, BC, BE | 各国の世帯調査 | LFS - Labour Force Survey |
| AA | 人口センサス | PC - Population and Housing Census |
| DA, CA | 事業所調査・センサス | ES - Labour-related Establishment Survey |
| EA, EB | 公式推計・その他の公式資料 | OE - Official Estimates |
| FA〜FN, FX | 各国の行政記録 | ADM - Other Administrative records |
| GA | 消費者物価調査 | CPS - Consumer Price Survey |
| JA | 国民経済計算 | SNA - National Accounts |
| BX | 他機関の世帯調査 | UNICEF の MICS (53)、Demographic and Health Survey (13) |
| XX | その他 | World Bank ICP (195)、International Monetary Fund (194) |
| XA | ILO 自身 | ILO - Modelled Estimates (282) など |

ILO が自分で推計した値は XA の一部で、大半は各国の統計機関の値を ILO が集めたもの。IMF、世界銀行 ICP、UNICEF の値も入っている。

## 取り出し方

区分は split。指標 × 頻度 (1,964) か、地域 × 頻度 (741) で分割されたファイルを選んで取る。
各ファイルは Range が効かないので、その中では whole。

| 区分 | 手段 | 実測 |
|---|---|---|
| split | `data/indicator?id=<ID>` / `data/ref_area?id=<ID>` | 1 ファイル 38,913 バイトから 33,150,844 バイト (`.csv.gz`) |
| catalog | 目次 CSV と SDMX の dataflow 一覧 | 目次 1,964 行。SDMX の dataflow は 1,215 個、すべて version 1.0 |
| whole | 各ファイル | Range 不可。`curl -r 0-1023` が 200 で 33,150,844 バイト全部を返した |
| range | なし | 未対応 |

### 絞り込み

`data/indicator` は問い合わせで絞れる。`SDG_0111_SEX_AGE_RT_A` (全 42,030 行) で試した。

- `ref_area=IND` で 218 行 (1 地域)。
- `timefrom=2020` で 7,290 行。
- `region=AFRICA` と `region=ASIA` は効かず 42,030 行のまま。Internet Archive にはこの引数つきの取得物が多数あり、
  そちらでは行が減っているので、効く値は別にあるのかもしれない (未確認)。

### SDMX API

- `https://sdmx.ilo.org/rest/dataflow/ILO` が 1,215 個の dataflow (`DF_<指標>`) を返す。7,276,669 バイトの XML。
- データは `https://sdmx.ilo.org/rest/data/ILO,DF_<指標>,1.0/<キー>?format=csv`。キーで地域を、`startPeriod` / `endPeriod` で期間を絞れる。
  `DF_SDG_0111_SEX_AGE_RT` に `IND.A....` で、インドだけが返った。
- SDMX の CSV は出典を名前で持つ (`ILO - Modelled Estimates`)。一括配布の CSV はコード (`XA:2010`)。
- dataflow の注記に `LAST_UPDATE` があるが、ライセンスの記載は無い。

## ライセンス

### ILO の Rights and permissions

ILOSTAT のフッターの「Copyright & permissions」は ILO 全体のページにつながる。
旧 URL `http://www.ilo.org/global/copyright/lang--en/index.htm` が 301 で
<https://www.ilo.org/rights-and-permissions> (2026-10-04 取得) に転送される。

> All ILO knowledge products published on or after 3 May 2023 by the ILO or on its behalf will be available
> for use or reuse without needing to request permission – as long as the ILO is cited as the source of material.
> The policy also covers all materials published or made available by the ILO ranging from reports and publications
> to videos and datasets.

データの節。

> As of 3 May 2023, databases and datasets together with the accompanying referential metadata are covered by the
> Creative Commons CC BY 4.0 licence. This licence does not apply to microdata submitted by or obtained from
> constituents and partner institutions that is restricted solely to the ILO's use. To explore ILO data and
> statistical tools, please visit ILOSTAT .

> Databases and datasets together with the accompanying referential metadata produced prior to 3 May 2023 do not
> automatically benefit from a Creative Commons licence. It is essential that users check the copyright page of
> each work for exact licence information.

第三者の権利。

> ILO publications and documents may contain components (e.g. text, graphics, tables, illustrations) where the ILO
> does not hold copyright. Users wishing to reuse third-party material contained in an ILO publication are responsible
> for determining whether permission is needed for its reuse and for obtaining permission from the original copyright
> holder.

読み取れること。

- 再配布と商用利用はできる (CC BY 4.0)。share-alike は無い。
- 必要なのは ILO を出典として示すこと。CC BY 4.0 の表示要件 (ライセンスへのリンク、変更の有無) も付く。
- ILO の名前と紋章 (ロゴ) は同じページで、書面の許可なしに使えないとされている。データの再配布で ILO のロゴを使わない。
- 対象外はマイクロデータ (加盟国や協力機関から ILO 専用として受け取ったもの)。一括配布は集計値で、マイクロデータは入っていない。
- 2023-05-03 より前に「produced」されたデータセットは自動では CC BY にならない。一括配布は毎日作り直されるので、
  現行の配布物はこの日付より後に公開されたものと読める。ただし目次の `last.update` が 2023-05-03 より前のファイルが 1 つある
  (2022-05)。過去の取得物 (Internet Archive の 2023 年以前の旧一括配布) は CC BY の対象かどうかがこの文言では決まらない。
- 第三者の権利の節は「publications and documents」についての記述で、データセットに混ざる他機関 (IMF、世界銀行、UNICEF、各国統計機関) の値をどう扱うかは書かれていない。
  データの節は、マイクロデータ以外に除外を設けていない。

### 免責

<https://www.ilo.org/disclaimer> (2026-10-04 取得) は、国名・地域の表示が領土の法的地位についての意見を表すものではないこと、
ILO の特権と免除を放棄しないことを書く。

> Nothing herein shall constitute or be considered to be a limitation upon or a waiver of the privileges and
> immunities of the International Labour Organization.

### ILOSTAT 自身の表示

Internet Archive の `https://ilostat.ilo.org/data/bulk/` (2026-07-09 保存) と `https://ilostat.ilo.org/` (2026-07-03 保存)、
`https://ilostat.ilo.org/about/` (2026-06-02 保存) には、ライセンス名の記載が無かった。フッターの
「© 1996-2026 International Labour Organization | Copyright & permissions」だけ。

## 版

- 一括配布は上書きされる。一覧ページは 2026-10-03 21:01 GMT 更新で、ファイルの `last.update` は 1,964 のうち
  1,359 が 2026-10、448 が 2026-09。指標ごとに随時更新され、決まった公開日はない。
- ファイル名に版は無い。ダウンロード名の時刻は生成した時刻で、データの版ではない。版を示せるのは目次の `last.update` だけ。
- 配布元に過去の版の置き場は見当たらない。SDMX の dataflow もすべて version 1.0 のまま。
- 旧一括配布 `https://www.ilo.org/ilostat-files/WEB_bulk_download/` は 301 で `https://webapps.ilo.org/ilostat-files/WEB_bulk_download/` に移り、そこは 404 (2026-10-04)。

### Internet Archive

`rplumber.ilo.org/data/indicator` を前方一致で引くと、状態 200 の取得物が 72,915 件ある (2024 年 37,312、2025 年 33,878、2026 年 1,725)。
形式は `.csv` 23,170、`.xlsx` 18,259、`.csv.gz` 18,076、`.dta` 13,341。

- `.csv.gz` の指標は 1,750 種類。日付ごとに数えると、ほぼ全体を一度に取ったように見える日がある:
  2025-10-15 (1,688)、2024-08-16 (1,664)、2024-06-14 (1,622)、2025-02-21 (1,572)。
- URL は一定しない。ILOSTAT のサイトのボタンから来たらしく、`type=code`、`channel=ilostat`、`title=...`、`region=...` などの引数が付く。
  同じ指標でも地域で絞った取得物が混ざるので、全体の版として使うには `region` の無いものを選ぶ必要がある。
- 2025-02-21 保存の `SDG_0111_SEX_AGE_RT_A` (`id` と `format` だけの URL) を取り出すと gzip の CSV で、38,473 行だった。
  2026-10-04 の現行は 42,030 行。列も違い、2025-02-21 版には `obs_status` がある。
- 同じ指標の取得物の `title` が、2026-01-16 保存では「below US$3 PPP」、それより前は「below US$2.15 PPP」。
  指標 ID が同じまま定義 (貧困線) が変わっている。
- 旧一括配布 `www.ilo.org/ilostat-files/WEB_bulk_download` の状態 200 の取得物は 2018〜2024 年に 763 件 (2022 年が 636 件)、
  `webapps.ilo.org/ilostat-files/WEB_bulk_download` は状態 200 が 2024〜2025 年に 1,935 件ある。中身は確かめていない。

## 未確認の点

- 一括配布全体の大きさ。3 本からの推定で indicator 側 `.csv.gz` 約 2.8〜3.5GB。全ファイルは取っていない。
- 目次の `n.records` と `n.records.all` の差 (30,269,062 行) の意味。
- ILOSTAT 自身のページ (`ilostat.ilo.org`) に、ILO 全体と別のライセンス表示や引用の書式があるか。Cloudflare のチャレンジで現行のページは読めず、
  Internet Archive の 3 ページだけを見た。
- データセットに混ざる他機関・各国の値に、ILO の CC BY 4.0 と別の条件が付くか。ILO の文言はデータについてマイクロデータ以外の除外を設けていないが、
  IMF や世界銀行 ICP、UNICEF MICS 側の条件は確かめていない。
- `last.update` が 2023-05-03 より前のファイル (1 つ) に CC BY 4.0 が及ぶか。
- `data/indicator` の `region` 引数で効く値。
- Internet Archive の旧一括配布 (`ilostat-files`) の中身と、2024 年以前の版がどこまで揃うか。
- 更新の頻度についての配布元の公式な記述。上の頻度は `last.update` の分布から読んだもの。
