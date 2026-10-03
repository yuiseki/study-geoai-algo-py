# EDGAR (Emissions Database for Global Atmospheric Research)

2026-10-04 に読んで確かめた内容。ページは curl で取得して読んだ。大きさは配布サーバのディレクトリ一覧 (Apache の自動索引) と
HEAD の `Content-Length`、zip の中身は末尾の中央ディレクトリだけを Range で読んで数えた。中身を開いたのは国別の表
`IEA_EDGAR_CO2_1970_2025.zip` (4,657,858 bytes) 1 本だけで、格子のファイルは落としていない。

- 入口: <https://edgar.jrc.ec.europa.eu/>。データセットの一覧は <https://edgar.jrc.ec.europa.eu/emissions_data_and_maps>、
  古い版の一覧は <https://edgar.jrc.ec.europa.eu/archived_datasets>。
- 最新の温室効果ガス版: <https://edgar.jrc.ec.europa.eu/dataset_ghg2026> (EDGAR_2026_GHG、1970〜2025 年、2026 年 9 月公開)。
- 配布サーバ: <https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/>。データセットのページの Download はすべてここを指す。
  認証なしで一覧が見え、HTTP Range が効く。
- 目録: JRC Data Catalogue (<https://data.jrc.ec.europa.eu/>) と、それを取り込んだ data.europa.eu。
- 作成: 欧州委員会 共同研究センター (European Commission, Joint Research Centre, JRC) の EDGAR チーム。化石燃料燃焼の CO2 は
  国際エネルギー機関 (IEA) との協定にもとづく共同の値 (IEA-EDGAR CO2)。
- 中身: 国別・部門別の排出量の時系列 (xlsx) と、0.1 度格子の排出量 (NetCDF とテキスト)。
- ライセンス: 欧州連合の著作物は CC BY 4.0。ただし化石 CO2 (IEA-EDGAR CO2) は CC BY-NC-ND 4.0 と明記されている。

## データセットの種類

<https://edgar.jrc.ec.europa.eu/emissions_data_and_maps> に並んでいたもの (2026-10-04)。

| 系統 | 最新 | 期間 | 物質 |
|---|---|---|---|
| 温室効果ガス | EDGAR_2026_GHG | 1970〜2025 | CO2 (化石、バイオ)、CH4、N2O、F ガス |
| 温室効果ガスの地域別 (NUTS2) | dataset_ghg2026_nuts2 | 1990〜2025 | 温室効果ガス |
| 大気汚染物質 | v8.1_AP | 1970〜2022 | SO2、NOx、CO、NMVOC、NH3、PM10、PM2.5、BC、OC |
| NMVOC の成分別 | v8.1_VOC_spec | 1970〜2022 | 25 成分 |
| 水銀 | v8.1 | | 水銀 |
| 非意図的生成 POPs | v8.1 UPOPs | 1970〜2024 | |
| 都市・居住地の種類別 | EDGAR Cities、EDGAR by Settlement type | | CO2、GHG、NOx、PM2.5 (1km) |
| HTAP | HTAP_V3.2 ほか | 2000〜2020 | 大気汚染物質 |

ここでは主に温室効果ガス (EDGAR_2026_GHG) を扱う。

- EDGAR_2025_GHG のページには、温室効果ガスとは別に `EDGAR_NOx_1970_2024.zip` と `EDGAR_PM2.5_1970_2024.zip` が載っている。
  配布サーバでの時刻は 2026-02-18 で、本体 (2025-09-15) より 5 か月遅れて足されている。大気汚染物質の 1970〜2024 年は
  この 2 物質だけで、ほかは v8.1_AP の 2022 年まで。

## 中身 (EDGAR_2026_GHG)

ページの説明 (Introduction) による。

- 物質: CO2 は化石 (IEA-EDGAR CO2) とバイオ (EDGAR CO2bio) に分かれる。ほかに CH4、N2O、F ガス (HFCs、PFCs、SF6、NF3)。
  CO2 換算の合計 (GWP_100_AR5_GHG、IPCC 第 5 次評価報告書の GWP100) と F ガスの合計 (GWP_100_AR5_F-gases) もある。
- 化石 CO2 には化石燃料の燃焼、セメントなどの非金属鉱物、金属の製造、尿素の製造、農地の石灰施用、溶剤が入る。
  燃焼の部分は IEA の Greenhouse Gas Emissions from Energy (2025b) の値を取り込んでいる。
- 大規模なバイオマス燃焼 (サバンナ火災、森林火災) と土地利用・土地利用変化・林業 (LULUCF) は含まない。
  その速報値は <https://edgar.jrc.ec.europa.eu/report_2026> にある、とページにある。
- 期間は 1970〜2025 年。F ガスは 1990〜2025 年。最新の数年は Fast Track という外挿で延ばしている (Guizzardi et al.)。
- 活動量は、エネルギー部門が IEA の World Energy Balances、農業が FAOSTAT。ほかに USGS、IFA、GFMR/NOAA、UNFCCC、worldsteel。
- 部門は IPCC 1996 と 2006 の区分コードで表す。EDGAR 独自の部門記号 (ENE 発電、TRO 道路交通、ENF 消化管内発酵など) は
  readme (<https://edgar.jrc.ec.europa.eu/readme/edgar_2026_ghg_readme.txt>) に 28 個の対応表がある。

### 国別の表

`IEA_EDGAR_CO2_1970_2025.zip` を開いて確かめた。zip の中身は `IEA_EDGAR_CO2_1970_2025.xlsx` と `_readme.html`
(readme の txt へ転送するだけの HTML)。

- シートは 4 枚: `Citations and references`、`IPCC 2006`、`IPCC 1996`、`TOTALS BY COUNTRY`。
- 各シートの先頭 8 行は説明 (`Compound: CO2`、`Start year: 1970`、`End year: 2025`、`Unit: Gg`)。9 行目が見出し。
- `IPCC 2006` の列は `IPCC_annex`、`C_group_IM24_sh`、`Country_code_A3`、`Name`、`ipcc_code_2006_for_standard_report`、
  `ipcc_code_2006_for_standard_report_name`、`Substance`、`fossil_bio`、`Y_1970`〜`Y_2025`。国と部門の組で 3,563 行、部門コードは 23 種。
  `IPCC 1996` は同じ形で 4,263 行。
- `TOTALS BY COUNTRY` は国ごとの合計で 224 行。そのうち 2 行は国でなく `AIR` (Int. Aviation) と `SEA` (Int. Shipping)。
  国・地域は 222。国コードは ISO 3166 の 3 文字。
- 単位は Gg (= kt)。ページは「kton substance / year」と書く。
- 1 枚目のシートに、ページと同じ利用条件と引用の文面が入っている (下の「ライセンス」)。

### 格子

- 解像度は 0.1 度 × 0.1 度、全球。
- 年別の格子: 1970〜2025 年。部門別と合計 (TOTALS)。単位は排出量が ton / セル / 年 (txt と nc)、フラックスが kg / m2 / s (nc)。
- 月別の格子: 2000〜2025 年。部門を 8 つにまとめたもの (Agriculture、Buildings、Fuel exploitation、Industrial combustion、
  Industrial processes、Power industry、Transport、Waste)。1 年 1 ファイルに 12 か月が入る。単位は Mg / 月 と kg / m2 / s。
- readme の注記: txt の座標はセルの左下隅、NetCDF の座標はセルの中心。
- 年別 NetCDF 1 本の展開後の大きさは 25,972,785 bytes (CO2 の TOTALS、どの年も同じ)。3600 × 1800 × 4 bytes
  (= 25,920,000) にヘッダを足した大きさで、float32 の非圧縮 NetCDF に見える (中身を開いていないので推測)。

### 月別の国別表

物質ごとに `*_m_1970_2025.zip` (xlsx)。1970〜2025 年の月別の国・部門別の値。F ガスには月別の値が無く、ページは年の値を
12 で割ることを勧めている。

## 配布ファイル (EDGAR_2026_GHG)

配布サーバの `EDGAR_2026_GHG/` の構成。

```
EDGAR_2026_GHG/
  IEA_EDGAR_CO2_1970_2025.zip ほか 11 本   国別の表 (年別 7 本、月別 4 本)
  CO2/ CO2bio/ CH4/ N2O/ GWP_100_AR5_GHG/  物質ごと
    <部門>/
      <部門>_emi_nc.zip  <部門>_emi_txt.zip  <部門>_flx_nc.zip   全年をまとめた zip
      emi_nc/ emi_txt/ flx_nc/                                    1 年 1 zip に分けたもの
  Fgases/HFCs/ PFCs/ SF6/ NF3/                   F ガス (部門は PRU_SOL と TOTALS)
  monthly/<物質>/bkl_<部門>/bkl_<部門>_{emi,flx}_nc.zip           月別の格子
  copyright.txt                                  各階層に同じものがある
```

国別の表 (ディレクトリ一覧と HEAD。時刻はすべて 2026-09-18):

| ファイル | 中身 | bytes / 一覧の表示 |
|---|---|---:|
| IEA_EDGAR_CO2_1970_2025.zip | 化石 CO2、年別 | 4,657,858 |
| EDGAR_CO2bio_1970_2025.zip | バイオ CO2、年別 | 1.4M |
| EDGAR_CH4_1970_2025.zip | CH4、年別 | 5.5M |
| EDGAR_N2O_1970_2025.zip | N2O、年別 | 6.0M |
| EDGAR_F-gases_1990_2025.zip | F ガス、年別 | 1.4M |
| EDGAR_AR5g_F-gases_1990_2025.zip | F ガス合計 (CO2 換算)、年別 | 460K |
| EDGAR_AR5_GHG_1970_2025.zip | 温室効果ガス合計 (CO2 換算)、年別 | 9,595,704 |
| IEA_EDGAR_CO2_m_1970_2025.zip | 化石 CO2、月別 | 70,972,540 |
| EDGAR_CO2bio_m_1970_2025.zip | バイオ CO2、月別 | 21M |
| EDGAR_CH4_m_1970_2025.zip | CH4、月別 | 73M |
| EDGAR_N2O_m_1970_2025.zip | N2O、月別 | 73M |

国別の表は 11 本で合計約 260MB (一覧の表示の和で 0.26GiB)。年別だけなら 7 本で約 29MB。

格子 (ディレクトリ一覧の表示の和。一覧の大きさは丸められているので概数):

| 物質 | 部門のディレクトリ | 全年まとめの zip の合計 |
|---|---:|---:|
| CO2 | 21 | 12.9 GiB |
| CO2bio | 15 | 4.1 GiB |
| CH4 | 25 | 18.6 GiB |
| N2O | 23 | 19.4 GiB |
| GWP_100_AR5_GHG | 28 | 24.1 GiB |
| F ガス (4 種) | 2 ずつ | 3.1 GiB |

- 年別の格子を全年まとめの zip で揃えると約 82.5 GiB。形式別では emi_nc 17.7 GiB、emi_txt 45.8 GiB、flx_nc 18.7 GiB。
  NetCDF の排出量 (emi_nc) だけなら約 18 GiB。
- 1 年 1 zip のディレクトリ (`emi_nc/` など) は同じ中身を分けたもの。サーバ上の総量はまとめの zip の約 2 倍になる。
- 月別の格子はページに 80 本 (5 物質 × 8 部門 × emi/flx)。ページの表示の和で 101,233 MiB (約 98.9 GiB)。
  最大は `monthly/CO2/bkl_TRANSPORT/bkl_TRANSPORT_emi_nc.zip` で、HEAD の `Content-Length` は 4,858,606,820 bytes。
  ページの表示 4633.53 Mb と一致するので、ページの「Mb」は MiB。
- まとめの zip の例。`CO2/TOTALS/TOTALS_emi_nc.zip` は 881,337,303 bytes で、中身は 1970〜2025 年の nc 56 本と `_readme.html`。
  展開後の合計は 1,454,476,430 bytes。nc は deflate で約 60% に縮んでいる。

## 取り出し方

区分は split。物質 × 部門 × 形式 × 年で事前に分かれていて、必要なファイルだけ引ける。各ファイルの中は whole。

| 区分 | 手段 | 実測 |
|---|---|---|
| split | 物質 × 部門 × 年の格子 zip | CO2 の TOTALS の 2025 年 NetCDF が 15,898,101 bytes (`CO2/TOTALS/emi_nc/EDGAR_2026_GHG_CO2_2025_TOTALS_emi_nc.zip`) |
| split | 物質ごとの国別表 | 年別の化石 CO2 で 4,657,858 bytes |
| range | zip の中央ディレクトリ | 一覧を 227〜4,792 bytes の読み出しで得られた。メンバーは deflate なので、1 メンバーだけ抜くには圧縮後の大きさ分を読む |
| catalog | ディレクトリ一覧 | Apache の自動索引で全階層を列挙できる。bbox や時刻で絞る目録は無い |
| whole | 年別の格子を全部 | 約 82.5 GiB。月別を足すと約 180 GiB |

- `curl -r 0-1023` を `CO2/TOTALS/TOTALS_emi_nc.zip` に投げると 206 と `content-range: bytes 0-1023/881337303` が返った。
  HEAD は `accept-ranges: bytes`、`Last-Modified`、`ETag` を返す。
- 格子は zip の中の NetCDF で、メンバーは deflate 圧縮されている。NetCDF の中の一部の領域だけを Range で読むことはできない
  (zip を展開してから読む)。最小単位は 1 物質 1 部門 1 年の zip で、CO2 の TOTALS で約 15MB。
- 認証、利用規約への同意画面、トークンは無かった。
- JRC Data Catalogue (`data.jrc.ec.europa.eu`) は、curl の既定に近い要求ヘッダだと「Request Rejected」という 245 bytes の
  ページを 200 で返した。ブラウザに近い `User-Agent` と `Accept` を付けると本来のページが返った。
  ページが無いのではなく WAF の拒否。

## ライセンス

### データセットのページ

<https://edgar.jrc.ec.europa.eu/dataset_ghg2026> の「Conditions of use」(2026-10-04 に読んだ)。

> ©European Union 2026, European Commission, Joint Research Centre (JRC), EDGAR (Emissions Database for Global
> Atmospheric Research) Community GHG database, comprising IEA-EDGAR CO 2 , EDGAR CH 4 , EDGAR N 2 O and EDGAR F-gases
> version EDGAR_2026_GHG (2026). Unless otherwise noted, all material owned by the European Union is licensed under the
> Creative Commons Attribution 4.0 International (CC BY 4.0) licence. This means that reuse is allowed, provided that
> appropriate credit is given and any changes are indicated.

> All emissions, except for CO 2 emissions from fuel combustion, are from the EDGAR (Emissions Database for Global
> Atmospheric Research) Community GHG database comprising IEA-EDGAR CO 2 , EDGAR CH 4 , EDGAR N 2 O and EDGAR F-gases
> version EDGAR_2026_GHG (2026).

> IEA-EDGAR CO 2 (v5) data are based on data from IEA (2025) Greenhouse Gas Emissions from Energy,
> www.iea.org/data-and-statistics, as modified by the Joint Research Centre, licensed under CC BY-NC-ND 4.0. Users of the
> IEA-EDGAR CO 2 data should contact the IEA at compliance@iea.org if they wish to use such data outside the terms of the
> CC-BY-NC-ND 4.0 licence.

- 欧州連合が持つもの (CH4、N2O、F ガス、バイオ CO2) は CC BY 4.0。複製、改変、再配布、商用利用ができる。
  要るのは出典の表示と、変更したならその旨。
- 化石 CO2 (IEA-EDGAR CO2) は CC BY-NC-ND 4.0。非商用に限り、改変したものは配れない。
  それ以外の使い方は IEA (compliance@iea.org) に問い合わせよ、とある。
- xlsx の 1 枚目のシートにも同じ趣旨の文面が入っている。こちらの書き方は
  「licensed under CC BY-NC-ND 4.0. Users of IEA-EDGAR CO2 data should contact the IEA at compliance@iea.org for permission to use.」
- 温室効果ガス合計 (EDGAR_AR5_GHG、格子の GWP_100_AR5_GHG) は化石 CO2 を足し込んだ値だが、どちらの条件に従うかは
  ページに書かれていない (未確認)。
- 免責 (<https://edgar.jrc.ec.europa.eu/disclaimer>) は、欧州連合と IEA がともに一切の保証と責任を否認する、という文面。

同じ CC BY-NC-ND 4.0 の記載は EDGAR_2025_GHG (IEA-EDGAR CO2 v4)、EDGAR_2024_GHG、v8.0、v7.0 のページにもある。
v6.0 のページには無い (下の「版」)。

### 配布サーバの copyright.txt

配布サーバの各階層に同じ `copyright.txt` (540 bytes、2026-03-05) が置かれている。全文:

> (c) European Union, 1995-2026
>
> The Commission's reuse policy is implemented by the Commission Decision of 12 December 2011
> on the reuse of Commission documents [1]. Any copyright and/or sui generis right on the dataset
> is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence [2].
> Reuse is allowed provided appropriate credit is given and any changes are indicated.

IEA-EDGAR CO2 のディレクトリ (`EDGAR_2026_GHG/CO2/`) にも同じものが置かれていて、CC BY-NC-ND の記載は無い。
データセットのページと xlsx は化石 CO2 を CC BY-NC-ND 4.0 としているので、食い違う。
ページは「Unless otherwise noted」と書いたうえで化石 CO2 を例外としているので、ページの記載を優先して読むのが安全。

### JRC Data Catalogue

data.europa.eu の検索 API (`https://data.europa.eu/api/hub/search/search?q=EDGAR%20GHG&filter=dataset`) で引いた。

- 温室効果ガスの記録は v5.0、v6.0、v7.0、v8.0、2024、2025 の 6 件。どれも配布物のライセンスは
  「European Commission reuse notice」。
- 2026 年版の記録は 2026-10-04 時点で無かった。
- JRC Data Catalogue の記録の画面での説明:

> According to the European Commission reuse notice, reuse is authorised, provided the source is acknowledged. ...
> Reuse is not applicable to documents subject to intellectual property rights of third parties.

  第三者の権利のあるものには再利用の許可が及ばない、と書いている。化石 CO2 の IEA の部分はこれに当たる。

### 出典の表示

ページの「How to cite」。データの引用:

> EDGAR (Emissions Database for Global Atmospheric Research) Community GHG Database, a collaboration between the
> European Commission, Joint Research Centre (JRC), the International Energy Agency (IEA), and comprising IEA-EDGAR CO 2 ,
> EDGAR CH 4 , EDGAR N 2 O, EDGAR F-GASES version EDGAR_2026_GHG (2026) European Commission, JRC (Datasets).

化石 CO2 を使うときはさらに:

> IEA-EDGAR CO 2 , a component of the EDGAR (Emissions Database for Global Atmospheric Research) Community GHG database
> version EDGAR_2026_GHG (2026) including or based on data from IEA (2025) Greenhouse Gas Emissions from Energy,
> www.iea.org/data-and-statistics, as modified by the Joint Research Centre.

> Users of the data are obliged to acknowledge the source of the data also with reference to the EDGAR_2026_GHG (2026)
> website (link) and/or relevant reports.

報告書の引用は Crippa, M. et al., GHG emissions of all world countries - 2026 Report, Publications Office of the
European Union, 2026, doi:10.2760/7717504, JRC147815。格子の作り方は Crippa et al. (2024),
Earth Syst. Sci. Data, 16, 2811–2830, doi:10.5194/essd-16-2811-2024。

JRC Data Catalogue の記録には版ごとの DOI がある。

| 版 | DOI | 記録 |
|---|---|---|
| EDGAR 2025 GHG | 10.2905/JRC.1K6V990 | <https://data.jrc.ec.europa.eu/dataset/d8e966b3-ff36-4b40-a365-f1776cf603d4> |
| EDGAR v8.0 GHG | 10.2905/JRC.023EKYG | <https://data.jrc.ec.europa.eu/dataset/b54d8149-2864-4fb9-96b9-5fd3a020c224> |
| EDGAR v6.0 GHG | 10.2905/JRC.787T5VR | <https://data.jrc.ec.europa.eu/dataset/97a67d67-c62e-4826-b873-9d972c4f670b> |

v7.0 は `fdb5aff4-66e5-4938-92a5-159ff872afd3`、2024 は `88c4dde4-05e0-40cd-a5b9-19d536f1791a`、
v5.0 は `488dc3de-f072-4810-ab83-47185158ce2a` (DOI は読んでいない)。

### Hugging Face に置けるか

- CH4、N2O、F ガス、バイオ CO2 の国別の表と格子は、CC BY 4.0 として出典を書けば置ける。
- 化石 CO2 (IEA-EDGAR CO2) は CC BY-NC-ND 4.0。そのままの形 (改変なし) で非商用として置くことは条件の範囲に入るが、
  Parquet への変換や縦持ちへの組み替えが「改変」に当たるかは、ライセンスの文言からは決めきれない。
  商用可の CC BY のデータセットに混ぜることはできない。
- 合計の GWP_100_AR5_GHG は化石 CO2 を含むので、同じ扱いにするのが安全 (条件は未確認)。
- 大気汚染物質 (v8.1_AP) のページには CC BY の明記が無く、「Users of the data are obliged to acknowledge the source of the data
  with a reference to the EDGARv8.1 air pollutant website」とだけある。配布サーバの copyright.txt (CC BY 4.0) と
  目録の European Commission reuse notice が根拠になる。

## WDI の CO2 指標の代わりになるか

[worldbank/README.md](../worldbank/README.md) と [worldbank/wdi-archives.md](../worldbank/wdi-archives.md) では、
WDI の `EN.ATM.CO2E.PC` などが Climate Watch (WRI) 由来の CC BY-NC 4.0 で、除外した。

- CO2 (化石) の代わりにはならない。EDGAR の化石 CO2 は CC BY-NC-ND 4.0 で、Climate Watch の CC BY-NC 4.0 より条件が狭い
  (改変も禁止)。
- CH4、N2O、F ガスの代わりにはなる。除外した `EN.ATM.METH.*`、`EN.ATM.NOXE.*` に当たる値が、CC BY 4.0 で国別・部門別にある。
- 温室効果ガス合計 (`EN.ATM.GHGT.KT.CE` に当たる) は化石 CO2 を含むので、CO2 と同じ問題が残る。
- 現行の WDI (source 2) には EDGAR 由来の指標がある。`https://api.worldbank.org/v2/sources/2/series/<コード>/metadata?format=json`
  (2026-10-04 に引いた) で、`EN.GHG.CO2.PC.CE.AR5` (Carbon dioxide (CO2) emissions excluding LULUCF per capita)、
  `EN.GHG.ALL.MT.CE.AR5`、`EN.GHG.CH4.MT.CE.AR5` の `License_Type` はどれも `CC BY-4.0`。`Source` は
  「EDGAR ... Community GHG Database, Joint Research Centre (JRC) - European Commission, uri: https://edgar.jrc.ec.europa.eu/dataset_ghg2024
  ...; International Energy Agency (IEA), ...」。
  EDGAR 側は化石 CO2 を CC BY-NC-ND 4.0 としているので、WDI の `EN.GHG.CO2.*` の CC BY-4.0 という表示は配布元の条件と食い違う。
  CH4 と N2O の指標は、配布元の条件と合っている。

## 版

- 版の名前は v4.x、v5.0、v6.0、v7.0、v8.0 のあと、2024 年から年の名前 (EDGAR_2024_GHG、EDGAR_2025_GHG、EDGAR_2026_GHG) に変わった。
  毎年 9 月から 11 月ごろに新しい版が出て、期間が 1 年延びる。
- 過去の版は消えない。<https://edgar.jrc.ec.europa.eu/archived_datasets> に 2025、2024、v8.0、v7.0、v6.0、v5.0、v4.3.2、v4.2、v4.1、v4.0 の
  ページがあり、配布サーバにも版ごとのディレクトリが残っている。HEAD で 200 を確かめたもの:

| 版 | ディレクトリ | 確かめたファイル | Last-Modified |
|---|---|---|---|
| 2026 | EDGAR_2026_GHG/ | IEA_EDGAR_CO2_1970_2025.zip | 2026-09-18 |
| 2025 | EDGAR_2025_GHG/ | IEA_EDGAR_CO2_1970_2024.zip (4,398,973 bytes) | 2025-09-15 |
| 2024 | EDGAR_2024_GHG/ | IEA_EDGAR_CO2_1970_2023.zip (4,878,996 bytes) | 2024-11-04 |
| v8.0 | v80_FT2022_GHG/ | EDGAR_CH4_1970_2022.zip (6,021,159 bytes) | 2023-10-23 |
| v7.0 | v70_FT2021_GHG/ | EDGAR_CH4_1970-2021.zip (5,541,629 bytes) | 2023-01-09 |
| v6.0 | v60_GHG/ | v60_GHG_CH4_1970_2018.zip (4,292,713 bytes) | 2021-08-10 |

  ほかに v50_GHG、v432、v42、v41、v40 などのディレクトリもある。
- 版のディレクトリの中身はあとから足されることがある。EDGAR_2025_GHG/ には公開から 5 か月後の 2026-02-18 に
  NOx と PM2.5 の表が加わった。既存のファイルが置き換わったかは確かめていない。
- `LATEST/` というディレクトリは最新版ではない。中身は CH4 と N2O で、時刻は 2021-03-04。
- 版ごとに期間が違い、過去の年の値も作り直される (ページの「Compared to previous EDGAR data releases」に排出係数や方法の更新が並ぶ)。
  版をまたいで値をつなぐことはできない。
- 化石 CO2 の扱いは版で違う。v7.0 から IEA-EDGAR CO2 になり、ページに CC BY-NC-ND 4.0 の記載が出る。
  v6.0 の CO2 は `CO2_excl_short-cycle_org_C` (1970〜2018 年) で、ページの条件は「Users of the data are obliged to acknowledge the
  source of the data with a reference to the EDGARv6.0 website ..., to Crippa et al. (2021) and to the DOI」だけ。
  ただし v6.0 も活動量に「IEA (2019) World Energy Balances ..., All rights reserved, as modified by Joint Research Centre」を使っている。

## 未確認の点

- 温室効果ガス合計 (EDGAR_AR5_GHG、GWP_100_AR5_GHG) に適用される条件。化石 CO2 の CC BY-NC-ND 4.0 が及ぶか。
- 化石 CO2 を Parquet などに変換して置くことが、CC BY-NC-ND 4.0 の改変禁止に当たるか。IEA の側の利用規約は読んでいない。
- v6.0 以前の化石 CO2 を CC BY として扱えるか。ページに NC の記載は無いが、活動量は IEA の「All rights reserved」のデータ。
- 格子の NetCDF の中身 (変数名、属性、圧縮の有無)。zip の中央ディレクトリの大きさから推測しただけで、開いていない。
- 月別の国別表 (xlsx) と、格子のテキスト形式の中身。
- 2026 年版の JRC Data Catalogue の記録と DOI。2026-10-04 時点で data.europa.eu の検索に出なかった。
- EDGAR_2025_GHG のように、公開後に版のファイルが差し替えられることがあるか。
