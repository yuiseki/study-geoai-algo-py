# FAOSTAT (国連食糧農業機関の食料・農業統計データベース)

2026-10-04 に読んで確かめた内容。一括配布の目録 `datasets_E.json` (109,120 バイト) を curl で取得して数えた。
ファイルの大きさは HEAD の `Content-Length`、まとめ zip の中身は末尾を `curl -r` で取って zip の中央ディレクトリを読んだ値。
データ本体は最小のファイルを 1 本 (`MDDW`、11,261 バイト) だけ取って展開した。`QCL` は先頭 32KB と末尾 16KB を Range で取り、
CSV の見出しとコード表だけを読んだ。FAO の規約のページは curl でそのまま読めた (Cloudflare 経由だがチャレンジは出なかった)。
FAOSTAT のサイト自体は JavaScript の画面で、curl では中身の無い枠 (3,752 バイト) しか返らない。
画面の裏の API は呼んでいないので、各ドメインのメタデータのページは読んでいない。

- 入口: <https://www.fao.org/faostat/en/> (ページ名「FAOSTAT」)。
- 一括配布の目録: <https://bulks-faostat.fao.org/production/datasets_E.json> (英語)。同じ内容の XML `datasets_E.xml`、
  フランス語 `datasets_F.json`、スペイン語 `datasets_S.json` もある。
- 一括配布の実体: `https://bulks-faostat.fao.org/production/<ファイル名>.zip`。AWS S3 を CloudFront で配っている
  (`server: AmazonS3`、`x-cache: Hit from cloudfront`)。
- 旧配布元 `https://fenixservices.fao.org/faostat/static/bulkdownloads/` は 301 で `bulks-faostat.fao.org/production/` に転送される。
- 作成: 国連食糧農業機関 (FAO、Food and Agriculture Organization of the United Nations)。目録の `Contact` はほぼすべて
  FAO の統計部 (Statistics Division、ESS) の各チームで、林業は Forestry Division (NFO)、食事と栄養は Food and Nutrition Division (ESN)。
  一次配布元は FAO 自身。ただし一部のドメインは他機関のデータの再掲 (後述「第三者のデータ」)。
- 中身: 国別・年別の食料と農業の統計。生産、貿易、食料需給表、価格、土地利用、肥料・農薬、農業由来の温室効果ガス排出、
  林業、人口と雇用、投資、食料安全保障、SDG 指標など。
- ライセンス: FAO の統計データベースは、メタデータやページに別の定めが無い限り CC BY 4.0 に、FAO の「Statistical Database Terms of Use」の追加条項が付く。
  再配布と商用利用は CC BY としては認められているが、追加条項に「商業的な宣伝に使わない」「FAO の推奨を示唆しない」と UNCITRAL 仲裁の条項がある。
- 一括配布は上書きされる。S3 のバケットは版管理が有効だが、過去の版は公開されていない。Internet Archive に 2018 年以降の目録と、
  2023 年以降のファイルの一部が残る。

## 配布ファイル

### 目録

`datasets_E.json` は `Datasets.Dataset` の配列で 69 件。1 件の項目:

`DatasetCode`, `DatasetName`, `Topic`, `DatasetDescription`, `Contact`, `Email`, `DateUpdate`, `CompressionFormat`, `FileType`, `FileSize`, `FileRows`, `FileLocation`

- 2026-10-04 に取得した目録の `Last-Modified` は `Fri, 02 Oct 2026 08:16:55 GMT`。
- `CompressionFormat` はすべて `zip`、`FileType` はすべて `csv`。
- `FileLocation` はすべて `..._E_All_Data_(Normalized).zip` (縦持ちの全地域版) を指す。
- `FileSize` は KB 単位の文字列 (`33127KB`)。HEAD の値と 1KB 未満の差で合う (`QCL` は目録 33127KB、HEAD 33,921,825 バイト)。
- `FileRows` の合計は 177,586,691 行、`FileSize` の合計は 1,487,483KB (約 1.42GiB、zip のまま)。

大きいもの:

| コード | 名前 | zip | 行数 |
|---|---|---:|---:|
| TM | Trade: Detailed trade matrix | 410,792KB | 52,410,630 |
| TCL | Trade: Crops and livestock products | 267,104KB | 17,143,873 |
| EA | Investment: Development Flows to Agriculture | 121,781KB | 17,042,560 |
| SCL | Food Balances: Supply Utilization Accounts (2010-) | 87,389KB | 12,955,325 |
| FBSH | Food Balances: Food Balances (-2013, old methodology and population) | 70,769KB | 11,479,903 |
| TI | Trade: Trade Indices | 66,519KB | 10,406,391 |

最小は `MDDW` (Food and Diet: Diversity (MDD-W)、12KB、1,223 行)。

### 目録に載らない形

目録が指すのは縦持ち (Normalized) の全地域版だけだが、同じ場所に別の形もある。`QCL` (Production_Crops_Livestock) で HEAD を投げた結果:

| ファイル | バイト |
|---|---:|
| `Production_Crops_Livestock_E_All_Data_(Normalized).zip` | 33,921,825 |
| `Production_Crops_Livestock_E_All_Data.zip` (横持ち、年が列) | 25,138,572 |
| `Production_Crops_Livestock_E_Africa.zip` | 4,319,333 |
| `Production_Crops_Livestock_E_Americas.zip` | 3,599,599 |
| `Production_Crops_Livestock_E_Asia.zip` | 4,708,076 |
| `Production_Crops_Livestock_E_Europe.zip` | 3,882,548 |
| `Production_Crops_Livestock_E_Oceania.zip` | 794,030 |
| `Production_Crops_Livestock_E_All_Area_Groups.zip` | 7,655,099 |

- 地域別は横持ちだけで、`_E_Africa_(Normalized).zip` は 403 だった。
- 無いファイルは 404 でなく 403 (`AccessDenied`) が返る。S3 が一覧の権限を持たない利用者に返す形で、ボット対策ではない。
- 地域別のファイル名はここでは推測で組んだもの。Internet Archive に `Production_Crops_Livestock_E_All_Area_Groups.zip` や
  `Food_Security_Data_E_Latin_America_and_the_Caribbean.zip` の取得物があり、同じ命名が使われてきたことは確かめた。
  ドメインごとに地域別の版がどこまであるかは確かめていない。

### まとめ zip

全ドメインを 2 つにまとめた zip がある。目録には載っていない。

| ファイル | バイト | Last-Modified | 中のファイル |
|---|---:|---|---:|
| `FAOSTAT_A-S_E.zip` | 738,662,691 | 2026-10-02 08:25:20 GMT | 72 |
| `FAOSTAT_T-Z_E.zip` | 777,321,957 | 2026-07-24 09:12:15 GMT | 7 |

- 中身はドメインごとの `..._E_All_Data_(Normalized).zip` を zip に入れたもの (zip の入れ子)。中のファイルの合計は 1,531,619,505 バイト。
- 目録の 69 本はすべて入っている。ほかに目録に無い 10 本が残っている:
  `ASTI_Expenditures_archive`、`ASTI_Researchers_archive`、`CommodityBalances_(non-food)`、`Environment_Emissions_by_Sector`、
  `Environment_Food_Waste_Disposal`、`Environment_LandUse`、`Environment_Pesticides`、`Environment_Soil_nutrient_budget`、
  `Food_and_Diet_Individual_Quantitative_Dietary_Data`、`Investment_CountryInvestmentStatisticsProfile`。
  終了したか名前が変わったドメインの古いファイルと見えるが、確かめていない。
- 中の `Trade_DetailedTradeMatrix_E_All_Data_(Normalized).zip` は 403,095,115 バイトで、単独で配っている同名ファイル (420,650,070 バイト) と大きさが違う。
  まとめ zip と単独のファイルは同じ時点のものとは限らない。
- 2024 年にはスペイン語版のまとめ (`FAOSTAT_A-C_S.zip`、`FAOSTAT_D-Z_S.zip`) が Internet Archive に残っている。現行にあるかは確かめていない。

## 中身

### ドメイン

目録の `DatasetName` は「グループ: 名前」の形。グループは 20、ドメインは 69。

| グループ | ドメイン数 | 例 (コード) |
|---|---:|---|
| Land, Inputs and Sustainability | 12 | 土地利用 RL、土地被覆 LC、肥料 RFN / RFB / RFM、農薬 RP / RT、家畜の糞尿 EMN、地表気温の変化 ET |
| Climate Change | 10 | 農業食料システムの排出: 作物 GCE、家畜 GLE、森林 GF、火災 GI、合計 GT、排出原単位 EI |
| Discontinued archives and data series | 7 | 旧生産者価格 PA、食糧援助 FA、林産物の貿易フロー FT、旧肥料 RA、農業機械 RM / RY |
| Food Balances | 5 | 食料需給表 FBS (2010-)、旧方式 FBSH (-2013)、供給利用勘定 SCL |
| Prices | 4 | 生産者価格 PP、消費者物価指数 CP、為替 PE、デフレーター PD |
| Investment | 4 | 開発資金 EA、政府支出 IG、農業向け信用 IC、海外直接投資 FDI |
| Food and Diet | 4 | FDIQ、HCES、MDDW、SUA |
| Trade | 4 | 作物と畜産物 TCL、詳細な貿易行列 TM、貿易指数 TI |
| Population and Employment | 3 | 人口 OA、農業の雇用 OEA、農村の雇用 OER |
| Production | 3 | 作物と畜産物 QCL、生産指数 QI、生産額 QV |
| そのほか (各 1〜2) | 13 | 農業研究 AE / AF、マクロ指標 MK / CS、林業 FO / FOP、健康的な食事の費用 CAHD、食料安全保障 FS、食品バリューチェーン GFDI、農村の暮らし RLIS、SDG 指標 SDGB、ジェンダー SXS、世界農業センサス WCAD |

`QCL` の説明には 278 品目とある。品目のコード表 (`ItemCodes.csv`) は 311 行。

### ファイルの中

zip 1 本にデータ本体と、そのドメインのコード表が入る。`QCL` の場合:

| ファイル | 展開後のバイト |
|---|---:|
| `Production_Crops_Livestock_E_All_Data_(Normalized).csv` | 545,005,770 |
| `Production_Crops_Livestock_E_AreaCodes.csv` | 5,391 |
| `Production_Crops_Livestock_E_Elements.csv` | 404 |
| `Production_Crops_Livestock_E_Flags.csv` | 169 |
| `Production_Crops_Livestock_E_ItemCodes.csv` | 10,838 |

`QCL` の CSV の先頭 (UTF-8、BOM なし、カンマ区切り、すべて引用符つき):

```
Area Code,Area Code (M49),Area,Item Code,Item Code (CPC),Item,Element Code,Element,Year Code,Year,Unit,Value,Flag,Note
"2","'004","Afghanistan","221","'01371","Almonds, in shell","5312","Area harvested","1961","1961","ha","0.000000","A",
```

- M49 と CPC のコードの頭に `'` が付く (表計算ソフトで先頭の 0 が消えないようにするためと見える)。読むときに外す必要がある。
- `Flag` は値の素性。`QCL` のコード表は A (Official figure)、E (Estimated value)、I (Value imputed by a receiving agency)、
  M (Missing value; data cannot exist)、X (Figure from external organization)。
- 列はドメインで違う。`MDDW` は `Survey Code, Survey, Food Group Code, Food Group, Indicator Code, Indicator, Geographic Level Code, Geographic Level, Element Code, Element, Unit, Value, Flag`
  で、国ではなく調査 (「Brazil - 2014」) が単位になり、全国・都市・農村の別を持つ。
- `MDDW` の CSV は 1,224 行 (見出し込み) で、目録の `FileRows` 1,223 と合う。

### 地域の単位と期間

- `QCL` の地域コード表は 244 行。うち 34 がコード 5000 以上の集計 (World 5000、Africa 5100、Western Europe 5404 など)、
  残り 210 が国と地域。ソ連 (228)、ユーゴスラビア (248)、チェコスロバキア (51) など消滅した国も残る。
- 国は FAO 独自の数値コードと M49 の両方を持つ。ISO 3166 の 3 文字コードは `QCL` の CSV には無い。
- 国の下の単位 (州・県) は無い。例外は調査が単位の `MDDW` などで、それでも全国・都市・農村の区別まで。
- 期間はドメインで違う。`QCL` は 1961 年から。目録の `RT` (農薬の貿易) の説明には、1961〜1990 年は各国の貿易テープから取ったとある。
  ドメインごとの終わりの年は確かめていない。

### 第三者のデータ

目録の説明に、他機関のデータを使うと書かれているドメインがある。

| コード | 説明に出てくる出典 |
|---|---|
| EA | 「republishes the OECD Creditor Reporting System (CRS) Aid Activity database」 (OECD のデータの再掲) |
| OA | 国連人口部の World Population Prospects 2024 と World Urbanization Prospects 2018 |
| OEA, OER | ILO のデータベース |
| CP | IMF、UNSD、OECD、BCEAO、ECCB、UNdata、UNCTAD など |
| CS, MK, PD | UNSD の国民経済計算 (AMA)、OECD の国民経済計算 |
| TCL, TI, TM | UNSD (UN Comtrade)、Eurostat、各国 |
| CAHD | 世界銀行の Food Prices for Nutrition との共同 |
| MDDW | DHS、MICS、世界銀行 LSMS、FAO/WHO GIFT |

これらの説明は出典を書いているだけで、FAO と別の利用条件が付くとは書いていない。
規約では、第三者の条件は「metadata of the database」に書くことになっている (下記)。各ドメインのメタデータのページは読んでいない。

## 取り出し方

区分は split。ドメイン (69) ごとの zip を選んで取る。横持ちの一部は大陸別にも分かれている。
各 zip は Range が効くので、中央ディレクトリを読んで中のファイルを 1 本ずつ取れる。ただし中のデータ本体は CSV 1 本で、
その中は whole。

| 区分 | 手段 | 実測 |
|---|---|---|
| split | `bulks-faostat.fao.org/production/<名前>_E_All_Data_(Normalized).zip` | 1 本 11,261 バイト (`MDDW`) から 420,650,070 バイト (`TM`) |
| catalog | `datasets_E.json` | 69 件。名前、説明、更新日、行数、大きさ、URL。bbox や期間では絞れない |
| range | zip の中のファイル単位 | `curl -r 0-1023` が 206 (`content-range: bytes 0-1023/738662691`)。末尾 16KB で中央ディレクトリとコード表が読めた |
| whole | 各 CSV | 圧縮は deflate。データ本体の CSV は 1 本なので、行や国で絞ることはできない |

まとめ zip (`FAOSTAT_A-S_E.zip` と `FAOSTAT_T-Z_E.zip`、計 1,515,984,648 バイト) は whole で取ることもできるし、
中のファイルは 1 本ずつ別に圧縮されて並ぶので、中央ディレクトリを読めば Range で 1 本ずつ抜くこともできる。

## ライセンス

### Statistical Database Terms of Use

<https://www.fao.org/contact-us/terms/db-terms-of-use/en/> (ページ名「FAO Statistical Database Terms of Use」、2026-10-04 取得)。

> FAO encourages you to use datasets contained in FAO corporate statistical databases for research, statistical, scientific
> and evidence-based decision-making purposes. You may access, download, create copies, adapt and re-disseminate datasets
> subject to these Database terms.

> Unless specified otherwise in their metadata or webpage, all datasets disseminated through FAO corporate statistical databases
> (see examples in Annex 1) are licensed under the Creative Commons Attribution-4.0 International licence (CC BY 4.0) available here
> as complemented by the Terms of Use outlined below.

Annex 1 の例に FAOSTAT が入っている。CC BY 4.0 のリンク先は `https://creativecommons.org/licenses/by/4.0/legalcode.en`。

追加条項 (ADDITIONAL TERMS OF USE) は 7 項。

> 1. Prohibited uses
> You will not use the datasets contained in FAO corporate statistical databases for any other purposes and/or in any other manner
> than as expressly provided herein, nor attempt to de-anonymize the datasets. Datasets shall not be used for or in conjunction with
> the promotion of a commercial enterprise and/or its product(s) or services (s), and/or in any way that suggests that FAO endorses
> any specific company, products or services. Furthermore, you shall not use FAO datasets in a manner that falsifies or misrepresents
> their content.

> 2. Third party exceptions
> FAO corporate statistical databases may include data provided by third parties which may not be redistributed or reused without
> the consent of the original data provider, or that may be subject to terms and conditions which are different than those of FAO.
> In such cases, these conditions are included in the dataset metadata or webpage. It is your responsibility to determine if
> a particular dataset is fully or partially owned by third parties and/or whether additional restrictions may apply.

> 3. Attribution
> The CC BY 4.0 licence specifies that you must give appropriate attribution and credit to FAO for any work produced using an FAO
> dataset or when FAO data is re-disseminated. The citation must follow the following format:
> "FAO. [YYYY (year of last update)]. [Name of database: Name of dataset OR Name of database]. [Accessed on [DD Month YYYY]]. [URL] Licence: CC-BY-4.0."

> 6. Dispute resolution
> Any dispute, controversy or claim arising out of or in relation to this licence that cannot be settled amicably shall be submitted
> to arbitration in accordance with the Arbitration Rules of the United Nations Commission on International Trade Law (UNCITRAL).

> 7. Amending FAO Statistical Database Terms of Use and associated Terms and Conditions regarding the Reuse of Web content
> (略) Both the Terms and Conditions regarding the Reuse of Web content and these Database terms may be amended from time to time.
> It is your responsibility to check for updates and amended versions as your continued use of any dataset or database guarantees
> your consent to any amendments.

ほかに 4 (No endorsement、FAO が関与・承認したと示さない) と 5 (Exclusion of liability、無保証。FAO はデータベースをいつでも変更・中止できる) がある。
ページに改訂日の記載は無かった。

### Open Data Licensing for Statistical Databases Policy

FAO の Terms and Conditions (<https://www.fao.org/contact-us/terms/en/>、2026-10-04 取得) は「Specific statistical databases are covered by
the Open Data Licensing Policy, and governed by the Statistical Databases Terms of Use.」と書き、
<https://openknowledge.fao.org/handle/20.500.14283/cd7464en> にリンクする。題名「Open Data Licensing for Statistical Databases Policy」、
FAO Statistics Division (ESS)、2025 年 (リポジトリの公開は 2025-11-24)。本文は同じ記録のテキスト版 (13,658 バイト) で読んだ (2026-10-04)。

> Since 30 November 2019, and unless otherwise specified, FAO has applied a Creative Commons licence to all statistical databases
> it creates or maintains, including those listed in Annex 1 and available at www.FAO.org.
> As of 1 July 2024, all FAO statistical databases, except for some databases made available under more restrictive terms, are made
> available under an Attribution 4.0 International Creative Commons licence (CC BY 4.0), available here. This licence and the FAO
> Statistical Database Terms of Use set out the terms and conditions under which FAO datasets may be accessed, downloaded, adapted
> and redistributed.
> FAO statistical databases published before 30 November 2019 are not licensed under a Creative Commons licence unless the Creative
> Commons icon, as shown in Annex 2, is present in the database's metadata or webpage.

> 3. THIRD PARTY EXCEPTIONS
> FAO statistical databases may include data provided by a third party that may not be redistributed or reused without the consent
> of the original data provider, or that may be subject to terms and conditions which are different from those of FAO. In such cases,
> this is noted in the metadata of the database.

適用範囲から公開用マイクロデータは外れる (「Public use microdata files published by the Organization (e.g. through the Food and Agriculture Microdata Catalogue) are not included in the scope of this policy.」)。
FAOSTAT は Annex 1 に「FAOSTAT Statistics Division (ESS) faostat@fao.org」として載る。

### ウェブ全体の Terms and Conditions

同じ <https://www.fao.org/contact-us/terms/en/> の、統計データベース以外のウェブの内容についての条件は非商用に限っている。

> All other content on the FAO website (except where otherwise indicated), may be copied, printed and downloaded for private study,
> research and teaching purposes, and for use in non-commercial products or services, provided that appropriate acknowledgement of
> FAO as the source and copyright holder is given

統計データベースは上の 2 つで扱われるので、この非商用の条件は FAOSTAT のデータには当たらないと読める。
ただし Database terms の 7 項は、この Terms and Conditions を「incorporated verbatim herein」としている。
ロゴは書面の許可なしに使えない (「Its use is highly restricted and is prohibited without prior permission.」)。

### 読み取れること

- 再配布と改変はできる。Database terms に「access, download, create copies, adapt and re-disseminate」と明記されている。
- 商用利用は CC BY 4.0 としては制限されない。ただし追加条項 1 で「商業企業や製品・サービスの宣伝に使う」ことと、
  FAO の推奨を示唆することが禁じられている。CC BY 4.0 にこの種の制限は無く、FAO 側の追加条件になる。
- 出典表示は書式が決まっている: 「FAO. [最終更新年]. [データベース名: データセット名]. [Accessed on 日付]. [URL] Licence: CC-BY-4.0.」
- 紛争は UNCITRAL の仲裁による。世界銀行のライセンスの追加条項も UNCITRAL 仲裁を定めている ([../worldbank/README.md](../worldbank/README.md) のライセンスの節を参照)。
- 規約は予告なく改訂されうるもので、使い続けることが改訂への同意とされている。
- 2019-11-30 より前に公開されたデータベースは、CC のアイコンが無い限り CC ライセンスではない。FAOSTAT の現行の一括配布は
  ほとんどが 2025〜2026 年の更新だが、目録の `DateUpdate` が 2019-11-30 より前のものが 3 件ある (`PA` 1991-12-31、`HS` 2014-07-31、`FA` 2016-12-22。いずれも終了したデータ系列)。
  「データベース」の公開日がドメイン単位か FAOSTAT 全体かは文言から決まらない。
- 第三者のデータは、条件が違う場合にメタデータに書くとされる。`EA` は OECD CRS の再掲と目録に書かれているが、目録にライセンスの記載は無い。
  各ドメインのメタデータのページは確かめていない。
- [../worldbank/data360.md](../worldbank/data360.md) によれば、世界銀行 Data360 が再配布している FAO_AS (106 指標) のライセンス欄は CC BY 4.0
  (URI `https://creativecommons.org/licenses/by/4.0/`) で、紛争解決の `note` は無い。FAO 自身の規約には仲裁の条項がある。

## 版

### 更新

- 一括配布は同じファイル名のまま上書きされる。ファイル名に版や日付は無い。版を示すのは目録の `DateUpdate` と HTTP の `Last-Modified` だけ。
- ドメインごとに更新日が違う。目録の `DateUpdate` は 2026 年 34 件、2025 年 25 件。月別に見ると 2025-10 に 15 件、2026-07 に 12 件が集まる。
  ほかは随時。2026-10-04 時点で最新は `RL` (Land Use、2026-10-02)、`SDGB` (2026-09-29)。
- 終了したデータ系列 (Discontinued archives) は古い日付のまま残る (`PA` 1991-12-31 など)。
- ドメインの構成とコードは変わってきた。2018-07 の目録 (Internet Archive) は 78 件で、`QC` (作物)、`QL` (畜産)、`TP` (作物・畜産の貿易) などがあった。
  現行は `QCL`、`TCL` に統合されている。

### 配布元の過去の版

- バケットは S3 の版管理が有効で、`datasets_E.json` や `FAOSTAT_A-S_E.zip` の HEAD に `x-amz-version-id` が付く
  (ドメインの zip の多くは `null`)。
- しかし `?versionId=<今の版の ID>` を付けると 403 (`AccessDenied`)、バケットの一覧も 403、`?versions` は 400。
  過去の版を利用者が取る手段は見当たらない。
- 配布元に過去の版の置き場は見当たらない。

### Internet Archive

2026-10-04 に CDX で数えた状態 200 の取得物:

| 前方一致 | 件数 | 年 |
|---|---:|---|
| `bulks-faostat.fao.org/production/` | 580 (zip 551、異なり 113 本) | 2024 年 55、2025 年 164、2026 年 361 |
| `fenixservices.fao.org/faostat/static/bulkdownloads/` | 115 (zip 45、異なり 34 本) | 2017〜2024 年 |

- 目録 `datasets_E.json` は 2018-07 から 2023-12 まで旧ホストで 32 回、2024-09 から 2026-09 まで新ホストで 8 回取られている。
  ドメインごとの `DateUpdate` の移り変わりはこれで追える。
- まとめ zip: `FAOSTAT_A-S_E.zip` が 2023-11-27 (旧ホスト、609,387,002 バイト)、2024-05-20、2025-03-28、2026-04-21。
  `FAOSTAT_T-Z_E.zip` が 2023-11-27 (866,176,651 バイト)、2025-03-28 (1,433,311,027 バイト)、2026-04-21。全ドメインを揃えた版はこの数時点だけ。
- ドメイン単位では取られ方に偏りがある。多いのは `FoodBalanceSheets` の縦持ち 55 回、`FoodBalanceSheetsHistoric` 45 回、`Production_Crops_Livestock` の縦持ち 31 回 (2024-08 から 2026-09)。
- 2025-06-13 保存の `Production_Crops_Livestock_E_All_Data_(Normalized).zip` は `id_` 付きの URL に Range を投げると 206 が返り、
  先頭は zip の署名 (`PK\x03\x04`) だった。元の `Last-Modified` は 2025-06-11、大きさ 33,109,510 バイト (現行は 33,921,825 バイト)。

## 未確認の点

- 各ドメインのメタデータのページ (FAOSTAT の画面の「Metadata」) に、CC BY 4.0 と別の条件や第三者の条件が書かれているか。
  とくに OECD CRS を再掲する `EA`、UN Comtrade を元にする貿易のドメイン、国連人口部の `OA`。
- 2019-11-30 より前の日付を持つ 3 ドメイン (`PA`、`HS`、`FA`) に CC BY 4.0 が及ぶか。
- ドメインごとの終わりの年と、全ドメインの国・地域の数。地域コード表は `QCL` の 1 本だけ見た。
- 地域別 (大陸別) の zip がどのドメインにあるか。目録に載らないので、名前を推測して HEAD を投げるしかない。
- まとめ zip に残る目録外の 10 本が何で、まとめ zip と単独のファイルの中身がどれだけ違うか (`TM` は大きさが違った)。
- 更新の予定 (公開カレンダー) についての配布元の記述。上の頻度は `DateUpdate` の分布から読んだもの。
- 現行のスペイン語・フランス語のまとめ zip の有無。
