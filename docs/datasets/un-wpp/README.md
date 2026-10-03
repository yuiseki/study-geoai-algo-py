# UN World Population Prospects (WPP、国連の世界人口推計)

2026-10-04 に読んで確かめた内容。ファイルの一覧はサイトが読み込む目録 `assets/downloads.json` から取り、
載っている 351 本すべてに HEAD を 1.1 秒間隔で投げて大きさと Last-Modified を数えた。
zip の中身は末尾の中央ディレクトリだけを Range で読んで列挙した。
中身を開いたのは `WPP2024_Demographic_Indicators_Medium.csv.gz` (16,557,272 バイト) の 1 本だけで、
保存せずにパイプで数えた。ほかの CSV は先頭 1,024 バイトだけ見た。

- 入口: <https://population.un.org/wpp/>
- 一括配布の目録: <https://population.un.org/wpp/assets/downloads.json> (248,768 バイト)。
  サイトは Angular の SPA で、Downloads の画面はこの JSON から組み立てられている。
- Data Portal: <https://population.un.org/dataportal/>
- Data Portal API: <https://population.un.org/dataportalapi/index.html> (Swagger)。データの取得には token が要る。
- 作成: 国連経済社会局 人口部 (United Nations, Department of Economic and Social Affairs, Population Division)。
  一次配布元は上の population.un.org。
- 現行の版は WPP 2024 (2024-07-11 公表)。次の版は 2026 年の予定が 2027-07-11 に延期された (後述)。

## 作成と公表の経緯

Downloads の Interim Update の節 (Release date: 19 January 2026) にこうある。

> The World Population Prospects 2024 was released on 11 July 2024. The next revision, originally planned for 2026, has been postponed for public release until 11 July 2027.

同じ節が、トーゴ (Togo、LocID 768) だけを直した暫定更新を出している。2010 年と 2022 年の国勢調査の
数字を、各国側が補正済みだったのに人口部がもう一度補正していた (二重補正) ためで、2022 年の人口が
公式の 8.2 百万に対し WPP 2024 では 9.1 百万になっていた。

> Results for all other locations are unchanged, and global/regional aggregates have not been revised in this interim update.

直したのは推計 (1950〜2023) と中位推計 (2024〜2100) の人口と出生・死亡数で、出生率と死亡率、
中位以外のシナリオ、地域集計は直していない。

## 中身

### 指標

`Demographic_Indicators` の CSV は 67 列。共通の 13 列 (SortOrder, LocID, Notes, ISO3_code,
ISO2_code, SDMX_code, LocTypeID, LocTypeName, ParentID, Location, VarID, Variant, Time) に続いて
54 の指標が並ぶ。

| 分野 | 列 |
|---|---|
| 人口 | TPopulation1Jan, TPopulation1July, TPopulationMale1July, TPopulationFemale1July, PopDensity, PopSexRatio, MedianAgePop, PopChange, PopGrowthRate, DoublingTime, NatChange, NatChangeRT |
| 出生 | Births, Births1519, CBR, TFR, NRR, MAC, SRB |
| 死亡 | Deaths, DeathsMale, DeathsFemale, CDR, LEx, LExMale, LExFemale, LE15/LE65/LE80 (各男女), InfantDeaths, IMR, LBsurvivingAge1, Under5Deaths, Q5, Q0040, Q0060, Q1550, Q1560 (各男女) |
| 移動 | NetMigrations, CNMR |

ほかのファイルは年齢を軸にした表で、AgeGrp, AgeGrpStart, AgeGrpSpan の 3 列が加わる。
人口 (5 歳階級と各歳、7 月 1 日と 1 月 1 日、実数と割合、曝露人口)、年齢別出生率 (5 歳と各歳)、
年齢別死亡数、生命表 (簡易と完全、男女別) がある。人の移動は純移動数と純移動率だけで、
出発地と到着地の組 (OD) は無い。

単位は千人が多い。日本 (JPN) の 2024 年は TPopulation1July 123,753.041、TFR 1.2168、LEx 84.852、
Births 750.57、Deaths 1,540.205、NetMigrations 153.357 だった。

### 地域の単位

`Demographic_Indicators_Medium` の 84,360 行は 555 地域 × 152 年 (1950〜2101) で、どの地域も 152 行ずつ。

| LocTypeName | 数 |
|---|---:|
| Country/Area | 237 |
| (空) | 234 |
| Ad Hoc groups | 23 |
| Subregion | 21 |
| SDG region | 9 |
| Income group | 9 |
| Development group | 7 |
| Special other | 7 |
| Geographic region | 7 |
| World | 1 |

- ISO3_code を持つのは 237 の Country/Area だけ。LocID は国と地域については ISO 3166-1 の数字コード
  (CSV の説明より)。
- LocTypeName が空の 234 件は「特別集計」(ADB の地域区分、AUKUS、African Union など) で、
  LocTypeID と ParentID も空。LocID は 986 から 98509。
- 国別に使うなら ISO3_code のある行に絞る。集計地域を落とさないと、World Bank の `country/all` と
  同じく上位集計が 1 行の観測として混ざる。
- 2101 年の行は TPopulation1Jan だけが値を持つ (2100 年末の人口を 2101 年 1 月 1 日として持っている)。

Data Portal API の `locations` は 300 件、`locationsWithAggregates` は 317 件で、
CSV の 555 とは数え方が違う。

### 期間とシナリオ

- 推計は 1950〜2023、予測は 2024〜2100。
- 決定論的な予測のシナリオ (Variant) は Medium のほか、Low, High, Constant fertility,
  Instant replacement, Instant replacement zero migration, Constant mortality, No change, Momentum,
  Zero migration など。ファイル名の `_Medium` と `_OtherVariants` で分かれている。
- 確率的予測 (Probabilistic Projections、PPP) は Excel だけで配られている。

### 形式

- CSV は UTF-8 で、先頭に BOM (EF BB BF) が付く。区切りはカンマ。
- CSV は gzip (`.csv.gz`) で 1 ファイル 1 表。
- Excel は XLSX。

## 配布ファイル

目録 `downloads.json` の 5 つのフォルダにある 351 本。349 本が 200、2 本が 404 だった。
404 の 2 本は Special Aggregates の Political groups の XLSX で、応答は Azure の
`The requested content does not exist.` (ボット対策の画面ではない)。

| フォルダ / 群 | 本数 | 大きさ |
|---|---:|---:|
| Standard Projections / Most used (XLSX) | 2 | 161.9 MiB |
| Standard Projections / Population (XLSX) | 17 | 2,490.0 MiB |
| Standard Projections / Fertility (XLSX) | 7 | 219.3 MiB |
| Standard Projections / Mortality (XLSX) | 24 | 2,431.0 MiB |
| Standard Projections / CSV format | 42 | 3,852.8 MiB |
| Standard Projections / Interim Update (zip) | 2 | 2.9 MiB |
| Probabilistic Projections (XLSX) | 40 | 472.3 MiB |
| Special Aggregates (XLSX) | 184 | 3,404.9 MiB (2 本 404 を除く) |
| Documentation | 3 | 6.2 MiB |
| Archive / Standard Projections (Excel の zip) | 14 | 9,778.1 MiB |
| Archive / Probabilistic Projections (zip) | 4 | 812.0 MiB |
| Archive / CSV files (zip) | 12 | 4,261.2 MiB |

合計 29,247,325,608 バイト (27.24 GiB)。うち現行 (WPP 2024) が約 12.7 GiB、過去の版の zip が 14.50 GiB。

### CSV (WPP 2024)

`https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/<名前>`

- `.csv.gz` が 40 本、注記の `.csv` が 2 本 (`WPP2024_Locations_notes.csv` 6,170 バイト、
  `WPP2024_Demographic_Indicators_notes.csv` 4,370 バイト)。合計 4,039,910,774 バイト (3.76 GiB、gzip のまま)。
- 小さいのは `WPP2024_Demographic_Indicators_Medium.csv.gz` (16,557,272)、`WPP2024_TotalPopulationBySex.csv.gz`
  (16,980,593)。大きいのは `WPP2024_Fertility_by_Age1.csv.gz` (301,907,467)、
  `WPP2024_PopulationByAge5GroupSex_OtherVariants.csv.gz` (231,139,177)、生命表の完全版 6 本 (各約 200MB)。
- 展開後の大きさは測っていない。WPP 2022 の同じ構成の CSV 42 本は展開後に 10,919,358,622 バイト (約 10.9GB) あった (後述)。

### 暫定更新 (トーゴ)

- `WPP2024_CSV_files_update.zip` (943,827 バイト、Last-Modified 2026-01-22)。中身は `_Medium_Update.csv` が 11 本で、
  展開後 7,363,859 バイト。
- `WPP2024_Excel_files_update.zip` (2,047,378 バイト、Last-Modified 2026-02-10)。
- 本体の `.csv.gz` 40 本はすべて Last-Modified が 2024-12-13 のままで、暫定更新は反映されていない。
  トーゴの最新値が要るなら、本体に更新分の CSV を上書きする必要がある。

## 取り出し方

区分は split。指標 × シナリオ × 期間ごとに事前に分かれた `.csv.gz` を、要るものだけ取る。
各ファイルの中は whole。

| 区分 | 手段 | 実測 |
|---|---|---|
| split | 指標ごとの `.csv.gz` | 40 本、最小 16,557,272 バイト |
| whole | 1 本の `.csv.gz` の中 | 単一の gzip ストリームなので途中から読めない |
| range | 過去の版の zip のメンバー | `WPP2022-CSV-data.zip` (3.5GB) の中央ディレクトリ 8,957 バイトを Range で読んで 82 メンバーを列挙できた |
| catalog | Data Portal API | 目録 (指標、地域、出典) は認証なしで引ける。データは token が要る |

- サーバー (`server: Windows-Azure-Web/1.0`) は Range を受け付ける。`curl -r 0-1023` が 206 と
  `content-range: bytes 0-1023/16980593` を返した。ただし末尾からの Range (`bytes=-65536`) は効かず、
  全体が 200 で返った。zip の末尾を読むときは HEAD で大きさを取ってから明示の範囲で要求する。
- zip のメンバーは deflate で圧縮されている。1 メンバーだけ Range で抜いて展開できる。

### Data Portal API

- Swagger の仕様は `https://population.un.org/dataportalapi/swagger/DataPortalOpenAPISpecificationv1.0/swagger.json`
  (v1.0 と v2.0 がある。2026-09-25 のビルド)。v1.0 のパスは 23。
- 目録系 (`/api/v1/indicators`, `/api/v1/locations`, `/api/v1/sources` など) は token なしで 200。
  `indicators` は 86 件で、WPP 2024 のものが 46、World Urbanization Prospects 2025 が 22、家族計画が 18。
- データ (`/api/v1/data/indicators/{indicators}/locations/{locations}/...`) は token なしだと
  `401` と `www-authenticate: Bearer`。仕様の説明にこうある。

> IMPORTANT: Please note that our data endpoints require an authorization token for access.

- token は `https://population.un.org/dataportalapi/token/index.html` のフォームで、メールアドレス、氏名、所属、
  利用目的を出して申請し、メールで受け取る。
- `sources` は 31 件で、WPP は 2018 (id 2)、2019 (id 13)、2022 (id 25)、2024 (id 27) がある。
  過去の版のデータを API で引けるかは token が無いので確かめていない。
- 一括取得なら CSV のほうが手間が少ない。API は認証と頁送りが要る。

## ライセンス

### WPP の配布物に付いている表示

Downloads の各群の脚注 (`downloads.json` の `Footer`、2026-10-04 に読んだ)。

> Copyright © 2024 by United Nations, made available under a Creative Commons license CC BY 3.0 IGO: http://creativecommons.org/licenses/by/3.0/igo/
> Suggested citation: United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024, Online Edition.

- Special Aggregates の群は引用名が `World Population Prospects 2024 - Special Aggregates, Online Edition`。
- Archive の群は「Copyright © 1992-2024 by United Nations, made available under a Creative Commons license CC BY 3.0 IGO」で、
  引用は `World Population Prospects [revision year], archive` と版の年を入れる。
- Interim Update の群は脚注が空。
- Data Portal API の Swagger 仕様の `info.license` も `Creative Commons license CC BY 3.0 IGO`。
- 2020-12-28 の Wayback の保存 (<https://web.archive.org/web/20201228114654/https://population.un.org/wpp/Download/Standard/CSV/>) でも
  WPP 2019 に同じ CC BY 3.0 IGO の表示がある。過去の版でも同じライセンスが掲げられていた。

CC BY 3.0 IGO であることは確かめられた。

### CC BY 3.0 IGO の条文

<https://creativecommons.org/licenses/by/3.0/igo/legalcode> (2026-10-04 に読んだ)。

> Licensor hereby grants You a worldwide, royalty-free, non-exclusive license to exercise the rights in the Work as follows: to Reproduce, Distribute and Publicly Perform the Work, to incorporate the Work into one or more Collections, ... to create, Reproduce, Distribute and Publicly Perform Adaptations, provided that You clearly label, demarcate or otherwise identify that changes were made to the original Work.

> You must include a copy of, or the Uniform Resource Identifier (URI) for, this License with every copy of the Work You Distribute or Publicly Perform.

- できること: 複製、再配布、改変、商用利用。非商用の制限も share-alike も無い。
- 必要なこと: 著作権表示を残す、ライセンスの URI を付ける、指定された帰属 (上の Suggested citation) と題名を示す、
  改変したらその旨を示す。
- してはいけないこと: 国連が推奨・関与していると示唆すること (4(b))。ライセンスより狭い条件を課すこと。
- 紛争は調停、45 日で解決しなければ UNCITRAL 仲裁規則による仲裁 (8(h))。国連の特権と免除は放棄されない (8(g))。
  World Bank の CC BY 4.0 に付いていた追加条項と同じ趣旨が、IGO 版では条文に最初から入っている。

### un.org の一般の利用規約との関係

サイトのフッターの Terms of Use は <https://www.un.org/en/about-us/terms-of-use>
(`https://www.un.org/en/aboutun/terms/` から転送、2026-10-04 に読んだ)。

> The United Nations grants permission to Users to visit the Site and to download and copy the information, documents and materials (collectively, "Materials") from the Site for the User's personal, non-commercial use, without any right to resell or redistribute them or to compile or create derivative works therefrom, subject to the terms and conditions outlined below, and also subject to more specific restrictions that may apply to specific Material within this Site.

Copyright のページ (<https://www.un.org/en/about-us/copyright>) も「All rights reserved.」で、
Terms and Conditions に定めるもの以外は書面の許可が要ると書く。

この一般規約だけを読むと、非商用・再配布不可になる。WPP のデータには配布画面と API 仕様で個別に
CC BY 3.0 IGO が明示されており、個別の資料に付いた明示のライセンスが一般規約より優先すると読むのが自然。
ただし一般規約の文言は「more specific restrictions」(より狭い制限) を予定しているだけで、
より広い許諾が優先すると書いてあるわけではない。これは文言からの解釈で、人口部に確かめてはいない。

### Hugging Face に置くこと

- CC BY 3.0 IGO のもとで、再配布も商用利用も改変 (Parquet への変換など) もできる。
- 置くときに要るもの: ライセンスの URI (`http://creativecommons.org/licenses/by/3.0/igo/`)、
  「Copyright © 2024 by United Nations」の表示、Suggested citation、形式を変えたことの記載。
  過去の版を置くなら版ごとの年の引用。
- Hugging Face のライセンス選択肢に CC BY 3.0 IGO があるかは確かめていない。無ければ `license: other` にして本文で明記する。
- 指標ごとに別のライセンスが付いている、という記載は WPP の配布物には見当たらなかった。
  World Bank の WDI のような指標単位の例外は無い。

## 版

- 改訂は 1992 年から概ね 2〜3 年ごと (1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012,
  2015, 2017, 2019, 2022, 2024)。次は 2027-07-11 の予定。
- 改訂しても過去の版は消えていない。配布元の Archive に、Excel の zip が 14 版 (1992〜2022、1998 は無い)、
  確率的予測の zip が 4 版 (2015〜2022)、CSV の zip が 12 版 (1998〜2022) ある。Last-Modified はすべて 2024-12-13。

| 版 | CSV の zip | Excel の zip |
|---|---:|---:|
| 2022 | 3,522,206,105 | 6,953,853,765 |
| 2019 | 271,236,186 | 723,314,988 |
| 2017 | 133,674,262 | 690,465,710 |
| 2015 | 124,512,315 | 452,011,077 |
| 2012 | 125,176,227 | 412,048,613 |
| 2010 | 106,068,723 | 402,022,316 |
| 2008 | 49,217,340 | 216,476,036 |
| 2006 | 49,402,353 | 136,838,654 |
| 2004 | 48,998,338 | 156,616,569 |
| 2002 | 13,456,679 | 63,757,833 |
| 2000 | 14,056,801 | 32,063,935 |
| 1998 | 10,179,012 | 無し |
| 1996 | 無し | 6,681,834 |
| 1994 | 無し | 2,777,984 |
| 1992 | 無し | 4,153,420 |

- 中身の作り方は版で違う。`WPP2022-CSV-data.zip` は 82 メンバーで、同じ表を `.csv` と `.zip` の両方で
  二重に持つ (展開後の合計 12,660,350,132 バイト。`.csv` 42 本だけで 10,919,358,622 バイト)。
  `WPP2019-CSV-data.zip` は 10 メンバー (展開後 1,183,630,993)、`WPP1998-CSV-data.zip` は 7 メンバー
  (展開後 60,131,192)。2019 以前はファイル名も列も 2022 以降と違い (`Period_Indicators`, `PopulationByAgeSex` など)、
  そのままでは縦に積めない。
- 同じ版の中でも、ファイル名を変えずに中身が差し替わる。WPP 2024 では、2025-03 から 2026-02 にかけて
  確率的予測の XLSX 6 本、出生のコーホート系 XLSX 3 本、Demographic Indicators の XLSX 2 本、
  メタデータの XLSX と注記の CSV が差し替わっている (Last-Modified で判別)。
  WPP 2019 も 2019-08-28 に「minor technical correction」で Excel と CSV を差し替えた記録がある (上の 2020 年の Wayback)。
  ファイル名だけでは版の中の更新を区別できないので、Last-Modified か内容のハッシュを記録する必要がある。

### URL の変更と Internet Archive

- サイトの作り直しで URL が変わった。2024 年までは
  `https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/...` で、
  いまは `https://population.un.org/wpp/assets/Excel%20Files/...`。
- 旧 URL に HEAD を投げると 404 が返る。GET では SPA の HTML (タイトル「World Population Prospects」) が 200 のような顔で返るが、
  これは 404 のときに表示される画面で、ファイルは無い。ボット対策ではない (応答は Azure の静的サイト)。
- Internet Archive の CDX では、旧 URL の WPP 2022 の CSV zip がほぼすべて 2022-12-01 に 200 で保存されている
  (`WPP2022_TotalPopulationBySex.zip` は id_ の取得で 11,028,063 バイト)。WPP 2019 の CSV、WPP 2024 の旧 URL の
  `.csv.gz` も一部が保存されている。
- 新 URL では、WPP 2024 の `.csv.gz` の多くが 2025 年に、Archive の Excel の zip (2012, 2015, 2017, 2022) が 2026-01 に保存されている。
  Archive の CSV の zip は CDX で見つからなかった。
- `downloads.json` は 2025-01-16 から保存があり、digest は 5 種類あり、内容が 4 回変わっている。

## 未確認の点

- WPP 2024 の `.csv.gz` 40 本の展開後の大きさと行数。開いたのは Demographic_Indicators_Medium の 1 本だけ。
- Data Portal API で過去の版 (source 13, 25) のデータを引けるか。token を申請していない。
- un.org の一般の利用規約と CC BY 3.0 IGO の優先関係についての人口部の見解。
- Hugging Face のライセンス一覧に CC BY 3.0 IGO があるか。
- WPP 2024 の本体ファイルの Last-Modified が公表 (2024-07-11) より後の 2024-12-13 である理由。
  サイトの作り直しで置き直しただけか、中身が変わったか。2024-11-09 に Wayback が旧 URL で保存したものと比べれば分かる。
- 2 本の 404 (Political groups の XLSX) が配布元の誤りか、一時的なものか。
