# UNHCR Refugee Population Statistics Database (Refugee Data Finder)

2026-10-04 に読んで確かめた内容。www.unhcr.org のページは curl で取ると Cloudflare のチャレンジ (HTTP 403、`cf-mitigated: challenge`) が返り、本文が読めない。ページが無いのではなく、ボット対策で止められている。そのため www.unhcr.org のページは Internet Archive の保存 (時刻は各所に書いた) で読んだ。API (`api.unhcr.org`) と HDX (`data.humdata.org`) はチャレンジ無しで直接読めた。件数は API の `limit=1` の応答の `maxPages` (1 ページ 1 行なので行数になる)、大きさは `curl -r` の `Content-Range` の値。データ本体は落としていない。中身として見たのは、HDX の CSV と API の CSV の先頭 1KB から 4KB だけ。

- 入口: <https://www.unhcr.org/refugee-statistics/> (ページ名「Refugee Data Finder - Key Indicators」)。データの抽出画面は <https://www.unhcr.org/refugee-statistics/download/>、説明は <https://www.unhcr.org/refugee-statistics/methodology/>。
- API: <https://api.unhcr.org/population/v1/>。説明は <https://api.unhcr.org/docs/refugee-statistics.html> (「Refugee Statistics API」Version 1.0.0)。認証は要らなかった。
- 作成: 国連難民高等弁務官事務所 (UNHCR)。データは主に各国政府から集め、UNHCR の現地事務所のデータも使う (methodology の「The data is sourced primarily from governments and also from UNHCR operations.」)。
- 一次配布元は UNHCR の Refugee Data Finder とその API。HDX の UNHCR のデータセットは、同じデータベースから UNHCR 自身 (HDX の組織「UNHCR - The UN Refugee Agency」) が書き出して載せている写し。
- 中身: 年、出身国、庇護国 (受け入れ国) の組み合わせごとの人数。難民、庇護申請者、国内避難民、無国籍者、帰還、第三国定住、帰化、庇護申請、庇護の決定、年齢性別の内訳。出身国と庇護国の組み合わせ (国の間の移動元と移動先) を持つ。最古は 1951 年。
- 年 2 回公表 (6 月に前年末の値、12 月ごろにその年の 1 月から 6 月の値)。公表のたびに過去の値も直る。データベースそのものの過去の版は UNHCR からは取れない。UNHCR の職員が保守する CRAN の R パッケージ `refugees` に、2022 年末の版からの写しが版ごとに残っている。

## 三つのデータ源

Refugee Data Finder の冒頭 (Wayback の 20260906165942 の保存) の原文:

> This website is based on three data sources:
> UNHCR data collected through its annual statistical activities with some data going back as far as 1951, the year UNHCR was created.
> Data provided by the United Nations Relief and Works Agency for Palestine Refugees in the Near East ( UNRWA). Information is limited to registered Palestine refugees under UNRWA's mandate.
> Data provided by the Internal Displacement Monitoring Centre ( IDMC). Information is limited to people displaced within their country due to conflict or violence.

- UNHCR 自身の値と、UNRWA (パレスチナ難民) と IDMC (紛争による国内避難民) の値が同じサイトに並ぶ。API でも `unrwa` と `idmc` は別のエンドポイントになっている。
- 国内避難民の数は 2 種類ある。UNHCR の `idps` (UNHCR が保護や支援をしている紛争による国内避難民だけ) と、IDMC の値。トップページの「68.7 MILLION are internally displaced people (Source: IDMC, as of end-2025)」は IDMC の値。methodology には「UNHCR statistics do not provide a complete overview of global internal displacement.」とある。
- 第三者のデータは下のライセンスの節の第 6 項に当たる可能性がある (未確認)。

## 中身

### 指標と期間

methodology のページ (Wayback の 20260730195054) の「Year first available」の表:

| 区分 | 項目 | 最初の年 |
|---|---|---:|
| 人数 (年末の値) | 難民 (Refugees) | 1951 |
| | 庇護申請者 (Asylum-seekers) | 2000 |
| | UNHCR が関わる国内避難民 | 1993 |
| | その他の国際的保護を要する人 (Other people in need of international protection) | 2018 |
| | 無国籍者 (Stateless people) | 2004 |
| 解決 (その年の流れ) | 難民の帰還 (Refugee returnees) | 1965 |
| | 国内避難民の帰還 (IDP returnees) | 1997 |
| | 第三国定住 (Resettlement arrivals) | 1959 |
| | 帰化 (Naturalisation) | 1990 |
| 内訳 | 年齢、性別 | 2001 |
| その他 | Others of concern to UNHCR | 1997 |
| | 受け入れ地域の住民 (Host community) | 2021 |

- 国ごとに始まりの年が違う。国と項目ごとの始まりの年は UNHCR の表 (<https://unhcr-web.github.io/refugee-statistics/0000-Data-Availability/UNHCR_Refugee_Statistics_DataAvailabilityMatrix.xlsx>) にある、と methodology に書かれている。この表は開いていない。
- 年末の人数は stock、解決は flow (data-content のページ、Wayback の 20250830082055)。
- 解決のデータでは「庇護国」の意味が変わる。第三国定住では到着した国、帰還では出発した国 (data-content のページ)。
- 庇護申請と決定には、手続きの段階 (新規、再申請、不服申し立てなど)、決定した主体 (政府、合同、UNHCR)、数え方 (人か件か) の符号が付く。
- 「その他の国際的保護を要する人」は 2022 年半ばの報告で新設され、それまでの「Venezuelans displaced abroad」を 2018 年まで遡って置き換えた (methodology)。項目の定義が途中で変わっている。
- 無国籍で難民でもある人は、2017 年より前は避難の区分でしか数えず、2017 年からミャンマーのロヒンギャ、2020 年からすべての国で両方の区分に数える (methodology)。年をまたいで足すと二重に数える年がある。

### API のエンドポイントと行数

2026-10-04 に `yearFrom=1951&yearTo=2026&coo_all=true&coa_all=true&limit=1` で数えた。`coo_all` と `coa_all` を付けると、出身国と庇護国の組み合わせ 1 つごとに 1 行になる。付けないと、その軸は足し合わされて 1 行にまとまる (API の説明の「If not specified, data for this dimension will be summed and aggregated to one row.」)。

| エンドポイント | 行数 | 列 (`year`、`coo_id`、`coo_name`、`coo`、`coo_iso`、`coa_id`、`coa_name`、`coa`、`coa_iso` のあと) |
|---|---:|---|
| `population` | 138,893 | `refugees`、`asylum_seekers`、`returned_refugees`、`idps`、`returned_idps`、`stateless`、`ooc`、`oip`、`hst` |
| `asylum-applications` | 120,597 | `procedure_type`、`app_type`、`dec_level`、`app_pc`、`applied` |
| `asylum-decisions` | 113,929 | `procedure_type`、`dec_level`、`dec_pc`、`dec_recognized`、`dec_other`、`dec_rejected`、`dec_closed`、`dec_total` |
| `solutions` | 21,258 | `returned_refugees`、`resettlement`、`naturalisation`、`returned_idps` |
| `demographics` | 116,781 | `f_0_4`、`f_5_11`、`f_12_17`、`f_18_59`、`f_60`、`f_other`、`f_total`、`m_0_4` から `m_total` まで同じ並び、`total` |
| `idmc` | 934 | `total` |
| `unrwa` | 296 | `total` |

- ほかに `countries`、`regions`、`years`、`footnotes` (値の注記)、`nowcasting` (まだ公表されていない年の推計) がある。
- `population` の 2025 年は 6,290 行。2026 年は 0 行。`years` は 1951 から 2027 までの 77 年を返したが、2026 年と 2027 年に人数の行は無かった (年の一覧が何を基準にしているかは未確認)。
- 国の符号は UNHCR 独自の 3 文字 (`coo`、`coa`) と ISO3 (`coo_iso`、`coa_iso`) の両方が付く。不明は `UKN` ("Various / unknown")、無国籍は `STA` (data-content)。API の CSV では不明が `UNK` だった。
- JSON の値は数値と文字列が混ざる (`"refugees":"0"` と `"refugees":5`)。値が無いことを `"-"` で表す列もある (`oip`)。
- 国の間の移動元と移動先は、`population`、`asylum-applications`、`asylum-decisions`、`solutions`、`demographics` の 5 つで取れる。組み合わせは国の単位で、地点や州は持たない。`demographics` には場所の説明 (キャンプや都市の名前) の列があると data-content のページに書かれているが、API の応答の列には出てこなかった (パラメータで出るかは未確認)。

### HDX の CSV

HDX の `unhcr-population-data-for-world` (題名「Data on forcibly displaced populations and stateless persons (Global)」、2026-10-04 に `package_show` で読んだ)。

| リソース | 大きさ (バイト) | last_modified |
|---|---:|---|
| `end_year_population_totals_residing_world.csv` | 7,281,295 | 2026-08-20 |
| `demographics_residing_world.csv` | 29,504,789 | 2026-08-20 |
| `asylum_applications_residing_world.csv` | 8,669,567 | 2026-08-20 |
| `asylum_decisions_residing_world.csv` | 8,833,586 | 2026-08-20 |
| `solutions_residing_world.csv` | 1,016,821 | 2026-06-11 |

- 合計約 55MB の CSV 5 本。`dataset_date` は 1951-01-01 から 2025-12-31、`data_update_frequency` は 365。
- 人数の CSV の見出し: `Year,Country of Origin Code,Country of Asylum Code,Country of Origin Name,Country of Asylum Name,Refugees,Asylum seekers,Other people in need of international protection,Internally displaced persons,Stateless Persons,Others of concern to UNHCR,Host community`。2 行目からデータ (`1951,UKN,AUS,Various / unknown,Australia,180000,0,0,0,0,0,0`)。API の `population` にある帰還の 2 列はここには無い (解決の CSV にある)。
- 世界全体のほかに、国ごとのデータセット (`unhcr-population-data-for-<国>`) が並ぶ。名前で引くと 219 件。中身が世界全体の CSV を国で切ったものかは確かめていない (未確認)。
- HDX の UNHCR の組織には 1,196 件のデータセットがある。多くは調査の個票 (`hdx-other` が 925 件) で、Refugee Data Finder とは別物。

### 小さい数の丸め

data-content のページの原文:

> Before publishing any statistics on the refugee statistics website, UNHCR applies safeguards to protect confidentiality. Small numbers less than five are rounded to the nearest multiple of five. Additionally data relating to asylum decisions is rounded between five and ten.
> Data between tables remains additive therefore the totals should be considered approximations.

- 5 未満の値は 5 の倍数に丸めてある。合計は近似値として扱う。

## 取り出し方

区分は catalog。主な使い方は API で、年、出身国、庇護国で絞って引ける。目録 (`countries`、`years`) もある。ファイルとしては HDX の CSV が whole。2026-10-04 に実測した。

| 要求した URL | 応答 | 全体の大きさ (バイト) |
|---|---|---:|
| API `population/?yearFrom=1951&yearTo=2026&coo_all=true&coa_all=true&download=true` | `-r 0-1023` に 206、`application/zip`、`filename=query_data.zip` | 1,080,972 |
| HDX `end_year_population_totals_residing_world.csv` | 302 で S3 の署名付き URL へ。`-r 0-1023` に 206、`Accept-Ranges: bytes` | 7,281,295 |

- API は `limit` と `page` でページを送る JSON か、`download=true` で zip を返す。`coo` と `coa` は国の符号をカンマで並べて絞れ、`yearFrom`、`yearTo`、`year` で年を絞れる。`cf_type=ISO` で ISO3 の符号で引ける。
- `download=true` の zip は要求のたびに作られる (`Last-Modified` が要求した時刻だった)。全期間の `population` の zip の中身は `population.csv` (展開後 7,735,696 バイト) と `footnotes.csv` (230,155 バイト)。
- API の CSV の見出しは HDX と違う: `Year,"Country of origin","Country of origin (ISO)","Country of asylum","Country of asylum (ISO)","Refugees under UNHCR's mandate",Asylum-seekers,"Returned refugees","IDPs of concern to UNHCR","Returned IDPss","Stateless persons","Others of concern","Other people in need of international protection","Host Community"`。原文のまま `Returned IDPss` と綴られている。
- HDX の CSV は Range が通るが、索引の無い CSV 1 本なので、必要な行だけを選ぶ手段にならない。小さいので丸ごと落とせばよい。最小の単位は解決の CSV の約 1MB。
- API の利用回数の上限は説明に書かれていない (未確認)。1.5 秒おきの要求では止められなかった。

## ライセンス

### データセットの利用条件

methodology のページ (<https://www.unhcr.org/refugee-statistics/methodology/>、Wayback の 20260730195054 で 2026-10-04 に読んだ) の「Data terms and conditions of usage」:

> Creative Commons Attribution 4.0 International Public License
> Except where otherwise indicated, the datasets made available by UNHCR on UNHCR Refugee Population Statistics Database are licensed under the Creative Commons Attribution 4.0 International Public License.
> Please refer to the Terms of Use for Datasets

「Terms of Use for Datasets」(<https://www.unhcr.org/what-we-do/data-and-publications/data-and-statistics/terms-use-datasets>、Wayback の 20260921095347 で 2026-10-04 に読んだ。リンク元の `https://www.unhcr.org/terms-and-conditions-data.html` からは 301 で転送される) から、関係する項:

> 1. Except where otherwise provided, the datasets made available by UNHCR on the UNHCR Refugee Population Statistics Database (the "Datasets") are licensed under a Creative Commons Attribution International License 4.0 (the "CC BY License") and the provision thereof is subject to the supplemental terms contained below in these Terms of Use for Datasets.

> 2. Access to and use of the Datasets are subject to the UNHCR Website Terms of Use that apply to use of the UNHCR's website. See https://www.unhcr.org/terms-and-conditions.html. In case of conflict between any provisions of the UNHCR Website Terms of Use conflict with these Terms of Use for Dataset, these Terms of Use for Datasets shall prevail.

> 3. You shall provide attribution to UNHCR and its data providers in the following format:"UNHCR Refugee Population Statistics Database".

> 4. When sharing or facilitating access to the Datasets, the URI or hyperlink to the Datasets shall also provide the uniform resource locator (URL) of these Terms of Use for Datasets.

> 5. You may not publicly represent or otherwise assert or imply that UNHCR, in the past, currently or in the future, participates, sponsors, approves or endorsed the manner or purpose of your use or reproduction of the Datasets.

> 6. Some datasets and indicators are provided by third parties, and may not be shared, redistributed or reused without the consent of the original data provider, or may be subject to terms and conditions that are different from those described herein. Where applicable, these conditions are included in the dataset or indicator metadata.

> 8. You may use UNHCR application programming interfaces ("APIs") to facilitate access to the Datasets, whether through a separate Web site or through another type of software application.

> 14. UNHCR may, at any time and from time to time, amend these Terms of Use for Datasets at any time.

- 残りの項は、名前と徽章の使用禁止 (7)、提供の変更と停止 (9、10)、無保証 (11)、特権免除 (12)、紛争の調停と仲裁 (13、ジュネーブ、UNCITRAL の規則)。
- 2023-03-14 の保存 (旧 URL) の第 1 項から第 4 項は、上と同じ文だった。

### ウェブサイトの利用条件

Terms and conditions of use (<https://www.unhcr.org/contact-us/terms-and-conditions-use>、Wayback の 20260922015717 で 2026-10-04 に読んだ) の第 1 項:

> The UNHCR website is made available by UNHCR for personal use and educational purposes only. Extracts of the information on this website may be reviewed, reproduced or translated for research or private study but not for sale or for use in conjunction with commercial purposes. Any use of Content from the UNHCR website shall be accompanied by an acknowledgment of the source, citing the uniform resource locator (URL) of the text.

> Any use other than for personal or educational purposes, including reproduction, scraping by artificial intelligence (AI), or translation of substantial portions of the Content of the UNHCR website, requires the express prior written permission of UNHCR.

Copyright (<https://www.unhcr.org/contact-us/copyright>、同じ保存) も、AI によるスクレイピングや電子媒体への編集を含む利用には書面の許可が要る、ただし Terms of use の定めを除く、と書く。

### 読み取れること

- データセットは CC BY 4.0。ShareAlike も NonCommercial も付いていない。再配布、加工したものの再配布、商用利用は CC BY 4.0 の範囲で認められる。
- ウェブサイトの利用条件 (個人と教育の目的に限る、商用は不可、AI によるスクレイピングは許可制) はデータセットにも及ぶと第 2 項は書くが、食い違うときはデータセットの利用条件が優先する、とも書く。データセットの利用条件の第 1 項が CC BY 4.0 を明示しているので、商用不可の条項はデータセットには効かないと読める。ただし UNHCR がそう解釈しているかは確かめていない (未確認)。画面をスクレイピングせず、API か HDX の CSV で取るほうが条件に沿う (第 8 項が API の利用を認めている)。
- 表示の要件: 「UNHCR Refugee Population Statistics Database」の表記 (第 3 項)。再配布するときは Terms of Use for Datasets の URL も添える (第 4 項)。CC BY 4.0 の表示 (ライセンス名と URL、改変の有無) も要る。UNHCR が後援しているように見せない (第 5 項)。UNHCR の名前と徽章は使わない (第 7 項)。
- 第 6 項の第三者のデータ。UNRWA と IDMC の値 (API の `unrwa`、`idmc`、`population` 以外の IDMC 由来の値) が当たる可能性がある。「Where applicable, these conditions are included in the dataset or indicator metadata」とあるが、API の応答にも HDX の CSV の先頭にもそうした記載は見当たらなかった。UNHCR 自身の値 (`population`、`asylum-applications`、`asylum-decisions`、`solutions`、`demographics`) に絞るのが安全。
- 条件は予告なく変わりうる (第 14 項)。置いた時点の条件の写しと日付を残すとよい。

### HDX と CRAN の表示

- HDX の `unhcr-population-data-for-world` の `license_id` は `cc-by-igo` (題名「Creative Commons Attribution for Intergovernmental Organisations (CC BY-IGO)」)。UNHCR のサイトは CC BY 4.0 と書いており、食い違う。HDX の UNHCR の組織全体では `hdx-other` 925、`cc-by-igo` 231、`cc-by` 33、`other-pd-nr` 4、`cc-by-sa` 1。
- CRAN の `refugees` パッケージの License は CC BY 4.0 (<https://cran.r-project.org/package=refugees>、2026-10-04 に読んだ)。
- 一次配布元の UNHCR のサイトの表示 (CC BY 4.0 と Terms of Use for Datasets) に従うのがよい。CC BY-IGO 3.0 は紛争解決の条項などが違う。HDX から取ったなら、HDX の表示と食い違うことを書いておく。

## 版

### 公表の時期

methodology の原文:

> UNHCR publishes population statistics every six months:
> End-year statistics for the previous year are published in June, typically on World Refugee Data.
> Mid-year statistics covering January to June for the current year are typically published in December.
> Demographic data is only collected within the end-year statistics.

- 年末の値は Global Trends、年央の値は Mid-Year Trends の報告と一緒に出る。トップページの「Last update: 11 June 2026」は「UNHCR Global Trends 2025」。
- IDMC の値は年 1 回、UNRWA の値は四半期ごと (methodology)。

### 過去の値の改訂

methodology の「Version history」に、版ごとの改訂が書かれている。抜粋:

| 公表日 | 内容 | 過去の値の改訂 (原文の要約) |
|---|---|---|
| 2026-06-11 | 2025 年の年末の値 | 記載なし |
| 2025-11-03 | 2025 年の年央の値 | 記載なし |
| 2025-06-12 | 2024 年の年末の値 | 2022 年と 2023 年のウクライナ難民の帰還、1975 年から 1981 年の米国への第三国定住の推計、2009 年から 2023 年の IDMC の値 |
| 2023-10-24 | 2023 年の年央の値 | ベルギー、コートジボワール、日本、オランダ、北マケドニア、スペイン、南アフリカの 2022 年の値 |
| 2022-10-27 | 2022 年の年央の値 | 「その他の国際的保護を要する人」の新設 (2018 年まで遡る) |
| 2022-06-16 | 2021 年の年末の値 | 受け入れ地域の住民を分離、2001 年から 2005 年の年齢内訳、2020 年のヨルダンとオランダの訂正 |
| 2021-11-10 | 2021 年の年央の値 | 2020 年のオランダ、モロッコ、ブラジルの値、丸めの改善 |
| 2020-06-18 | 2019 年の年末の値 | 「Venezuelans displaced abroad」の新設 |

- 一覧は 2020-06-18 の版から。2024-10-08 の行は「Mid-year statistics for 2023」と書かれているが、日付から見て 2024 年の年央の値の誤記と思われる (未確認)。
- 改訂は直近の年に限らず数十年前に及ぶ (米国の 1975 年から 1981 年)。同じ年の値が版によって違う。

### 過去の版が取れるか

- API には版を選ぶパラメータが無い (説明を検索した)。いつも最新の版を返す。
- HDX のリソースは同じ URL のまま上書きされている。世界全体のデータセットの作成は 2020-08-27、人数の CSV の最終更新は 2026-08-20。HDX は更新の履歴 (`package_activity_list`) を返すが、古い CSV の中身が取れるかは確かめていない (未確認)。
- CRAN の `refugees` パッケージ (保守は UNHCR の Janis Kreuder、著作権者 UNHCR) がデータの写しを版ごとに持つ。版番号は公表の年月に合わせてある。CRAN の Archive (<https://cran.r-project.org/src/contrib/Archive/refugees/>) にある版:

| 版 | CRAN の日時 | 大きさ |
|---|---|---:|
| 2022.12.0 | 2023-07-08 | 3.1M |
| 2022.12.1 | 2023-08-16 | 3.2M |
| 2023.6.0 | 2023-10-26 | 3.2M |
| 2023.12.0 | 2024-06-17 | 3.4M |
| 2024.6.0 | 2024-10-19 | 3.4M |
| 2024.12.0 | 2025-06-15 | 3.6M |
| 2025.06.0 | 2025-11-19 | 3.7M |
| 2025.06.1 | 2026-03-30 | 3.7M |
| 2025.12.0 | 2026-06-15 | 3.9M |
| 2025.12.1 | 2026-06-25 | 1.9M |

  - 現行は 2025.12.2 (2026-08-19 公開)。中身を開いていないので、どの表が入っているか、2025.12.1 で大きさが半分になった理由は確かめていない (未確認)。版の名前の年月と、データの年末と年央の対応も未確認。
- HDX の `unhcr-statistical-yearbooks` (UNHCR Statistical Yearbook Data) に古い年鑑のデータがある。中身は確かめていない (未確認)。

## 気をつけること

- 国内避難民は UNHCR の値と IDMC の値で意味が違う。UNHCR の `idps` は UNHCR が関わる人だけ。
- 項目の定義が年で変わる (「その他の国際的保護を要する人」、無国籍者の二重計上、受け入れ地域の住民の分離)。長い時系列を作るときは methodology の注記を先に読む。
- 庇護国の意味が解決のデータでは変わる (定住は到着国、帰還は出発国)。
- 5 未満は丸めてある。庇護の決定は 5 から 10 の丸め。
- 庇護申請と決定は「人」と「件」が混ざる (`app_pc`、`dec_pc`)。足す前に分ける。
- 不明の国の符号は HDX と API の JSON で `UKN`、API の CSV で `UNK`。

## 未確認の点

- ウェブサイトの利用条件の商用不可と AI のスクレイピングの許可制が、API や HDX で取ったデータセットに及ばないと UNHCR が解釈しているか。
- UNRWA と IDMC の値が第 6 項の第三者のデータに当たるか、その条件はどこに書かれているか。
- HDX が CC BY-IGO と表示している理由。
- CRAN の `refugees` の各版の中身と、公表の版との対応。HDX の古い CSV が取れるか。
- `demographics` の場所の列を API で出す方法。
- API の利用回数の上限。
- www.unhcr.org の現在のページ。Cloudflare のチャレンジのため、Internet Archive の 2026-07-30 から 2026-09-22 の保存で読んだ。
