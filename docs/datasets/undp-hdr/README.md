# UNDP Human Development Report の統計 (HDI と複合指数)

2026-10-04 に読んで確かめた内容。hdr.undp.org は Cloudflare の配下だが、curl でボット対策のチャレンジは出ず、
ページもファイルも直接読めた。配布ファイルの大きさと Last-Modified は HEAD で取った。
中身を開いたのは `HDR25_Composite_indices_complete_time_series.csv` (2,001,263 バイト) と
`HDR25_Composite_indices_metadata.xlsx` (13,731 バイト) の 2 本だけ。前の版の CSV は Range で
先頭 16KB と日本の行の前後 60KB だけを読んだ。www.undp.org のページは Akamai の `Access Denied` (HTTP 403) が
返るので、Internet Archive の保存で読んだ。

- 入口: <https://hdr.undp.org/data-center>
- 一括配布: <https://hdr.undp.org/data-center/documentation-and-downloads> (Documentation and downloads)
- API: <https://hdrdata.org> (HDRO Data API 2.0、2024-04-16 公開)。API キーが要る。
- 作成: 国連開発計画 (UNDP) の人間開発報告書室 (Human Development Report Office、HDRO)。
  一次配布元は上の hdr.undp.org。多次元貧困指数 (MPI) は HDRO とオックスフォード大学の OPHI
  (Oxford Poverty and Human Development Initiative) の共同作成 (Technical Notes の注「These global estimates are jointly produced by OPHI and HDRO」)。
- 現行の版は Human Development Report 2025 (HDR 2025、データ更新は 2025-05-06)。MPI は 2025-10-17 に別に更新された。
  2026-10-04 の時点で HDR 2026 のデータは出ていない (サイトに「Towards 2026 Human Development Report」の頁があるだけ)。

## 中身

### 複合指数と構成要素

主な配布物は全指数の時系列を 1 本にまとめた CSV
`HDR25_Composite_indices_complete_time_series.csv`。列の意味は同梱の
`HDR25_Composite_indices_metadata.xlsx` (シート `codebook` と `recommended_citation`) にある。

| 指数 | 列 (接頭辞) | 期間 |
|---|---|---|
| 人間開発指数 (HDI) | `hdi`, `le` (平均寿命), `eys` (就学予測年数), `mys` (平均就学年数), `gnipc` (1 人あたり GNI、2021 年 PPP ドル)、`hdi_rank` | 1990〜2023 (順位は 2023 のみ) |
| ジェンダー開発指数 (GDI) | `gdi`, `gdi_group`, 男女別の `hdi_f`/`hdi_m`, `le_f`/`le_m`, `eys_f`/`eys_m`, `mys_f`/`mys_m`, `gni_pc_f`/`gni_pc_m` | 1990〜2023 |
| 不平等調整済み HDI (IHDI) | `ihdi`, `coef_ineq`, `loss`, `ineq_le`, `ineq_edu`, `ineq_inc` | 2010〜2023 |
| ジェンダー不平等指数 (GII) | `gii`, `gii_rank`, `mmr` (妊産婦死亡率), `abr` (思春期出生率), `se_f`/`se_m` (中等教育以上), `pr_f`/`pr_m` (議席の割合), `lfpr_f`/`lfpr_m` (労働参加率) | 1990〜2023 |
| 地球への負荷を調整した HDI (PHDI) | `phdi`, `diff_hdi_phdi`, `rankdiff_hdi_phdi`, `co2_prod` (生産ベースの 1 人あたり CO2), `mf` (1 人あたりマテリアルフットプリント) | 1990〜2023 |
| 追加 | `pop_total` (総人口、百万人) | 1990〜2023 |

- 列は「指標_年」の横持ち。共通 4 列 (`iso3`, `country`, `hdicode`, `region`) と 1,108 の値の列で、計 1,112 列。
- 一部の指標は最新年の値を埋めている。metadata の期間の欄に `mmr` は「1990-2019, 2020-2023=2020」、
  `ineq_inc` は「2010-2021, 2022-2023=2022」とある。2020 年以降の妊産婦死亡率は 2020 年の値の繰り返しで、観測ではない。
- MPI はこの CSV に入っていない。`2025_gMPI_Table1and2.xlsx` (139,761 バイト) で別に配られる。
  MPI のページによれば 109 か国の値と、101 か国 1,359 地域の地方別の推計がある。xlsx の中身は開いていない。
- 日本 (JPN) の 2023 年は `hdi` 0.925 (順位 23)、`le` 84.712、`gii` 0.059、`phdi` 0.785。1990 年の `hdi` は 0.853。

### 地域の単位

206 行。国が 195、集計が 11。

- 国の行は ISO3 の `iso3` を持つ。`hdicode` は Very High 74、High 50、Medium 43、Low 26、
  「Other Countries or Territories」2 (北朝鮮 PRK、モナコ MCO。HDI の値が無い)。
- `region` は開発途上地域の区分 (SSA 46、LAC 33、EAP 26、AS 20、ECA 17、SA 9) で、先進国は空。
- 集計の行は `iso3` が `ZZA.VHHD` から `ZZK.WORLD` の 11 行 (HDI の 4 区分、6 地域、世界)。
  国だけを使うなら `ZZ` で始まる行を落とす。
- 2023 年の値がある国の数: `hdi` 193、`gdi` 184、`gii` 172、`ihdi` 169、`phdi` 156。1990 年の `hdi` は 141 か国。
- 国の中の地方の HDI (subnational HDI) は HDRO の配布物に無い。地方別は MPI の推計だけ。
  地方の HDI はラドバウド大学の Global Data Lab が「Subnational HDI Database」(<https://globaldatalab.org/shdi/>) として
  別に作っている。HDRO の配布物ではないので、ここでは扱わない。

### 形式

- CSV はカンマ区切り、改行は CRLF、BOM は無い。文字コードは UTF-8 ではなく Windows-1252
  (`Côte d'Ivoire` と `Türkiye` の 2 行だけが ASCII 外で、UTF-8 として読むと 0xF4 で失敗する)。
- 値の欠けは空文字。1,108 列 × 206 行の 228,248 セルのうち 28,244 が空。
- 統計付録 (Statistical Annex) の表は XLSX で、報告書の表の体裁 (見出しや注が入った行) になっている。機械で読むなら CSV のほうが楽。

### 元になったデータ

HDRO が自分で測った値ではなく、他機関の値を集めて計算している。HDR 2025 の Technical Notes
(<https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Technical_Notes.pdf>) の「Data sources」:

| 構成要素 | 出典 |
|---|---|
| 平均寿命、思春期出生率 | UNDESA (World Population Prospects 2024) |
| 就学予測年数 | UNESCO 統計研究所 (UIS)、DHS、UNICEF の MICS |
| 平均就学年数、中等教育以上の割合 | Barro and Lee (2018)、Eurostat、DHS、UIS、MICS |
| 1 人あたり GNI | IMF、国連統計部、World Bank (WDI) |
| 妊産婦死亡率 | WHO、UNICEF、UNFPA、World Bank Group、UNDESA の共同推計 |
| 議席の割合 | IPU (Parline) |
| 労働参加率 | ILO (ILOSTAT) |
| CO2、マテリアルフットプリント | Global Carbon Project、UNEP (International Resource Panel) |
| MPI | DHS、MICS と各国の世帯調査 (個票) |

## 配布ファイル

Documentation and downloads に載っている HDR 2025 のファイル。URL は
`https://hdr.undp.org/sites/default/files/2025_HDR/<名前>`。

| ファイル | 大きさ (バイト) | Last-Modified |
|---|---:|---|
| `HDR25_Composite_indices_complete_time_series.csv` | 2,001,263 | 2025-05-05 |
| `HDR25_Composite_indices_metadata.xlsx` | 13,731 | 2025-05-05 |
| `HDR25_Statistical_Annex_HDI_Table.xlsx` (表 1) | 44,086 | 2025-05-06 |
| `HDR25_Statistical_Annex_HDI_Trends_Table.xlsx` (表 2、1990〜2023) | 49,378 | 2025-05-06 |
| `HDR25_Statistical_Annex_IHDI_Table.xlsx` (表 3) | 59,710 | 2025-05-06 |
| `HDR25_Statistical_Annex_GDI_Table.xlsx` (表 4) | 61,878 | 2025-05-06 |
| `HDR25_Statistical_Annex_GII_Table.xlsx` (表 5) | 46,364 | 2025-05-06 |
| `HDR25_Statistical_Annex_PHDI_Table.xlsx` (表 7) | 47,439 | 2025-05-06 |
| `HDR25_Statistical_Annex_Tables_1-7.xlsx` (全表) | 217,358 | 2025-05-06 |
| `HDR25_calculating_indices.xlsx` (計算例) | 54,929 | 2025-05-07 |
| `HDR25_Technical_Notes.pdf` | 393,826 | 2025-05-15 |

MPI は `https://hdr.undp.org/sites/default/files/publications/additional-files/2025-10/2025_gMPI_Table1and2.xlsx`
(139,761 バイト、2025-10-16)。MPI の計算用の Stata の do ファイルは <https://hdr.undp.org/mpi-statistical-programmes> にある。

全部合わせても 3MB ほど。データとしては時系列 CSV の 2MB 1 本でほぼ足りる。

Documentation and downloads の頁の冒頭には「Explore and download data」の埋め込みアプリ
(curl で取ると「Application loading...」だけ) がある。画面の裏の API は調べていない。

### Humanitarian Data Exchange (HDX)

HDX の組織 `undp-human-development-reports-office` が 228 件のデータセットを載せている
(2026-10-04 に `package_search` で数えた)。多くは国ごとの `hdro-data-for-<国>` で、
例えばエチオピアは縦持ちの CSV `hdro_indicators_eth.csv` (96,093 バイト) と集計の CSV の 2 本。
HDRO 自身が載せている写しで、一次配布元は hdr.undp.org。

## 取り出し方

区分は whole。最新の全指数・全期間・全か国が 2MB の CSV 1 本なので、丸ごと取る。

| 区分 | 手段 | 実測 |
|---|---|---|
| whole | 時系列 CSV | 2,001,263 バイト。これが最小の単位 |
| split | HDX の国別 CSV | 国ごとのデータセット。エチオピアで 96,093 バイト |
| catalog | HDRO Data API | 国、年、指標で絞れる。API キーが要る |

- サーバーは Range を受け付ける。CSV に `curl -r 0-1023` を投げると 206 と `content-range: bytes 0-1023/2001263` が返った。
  ただし索引の無い CSV なので、必要な行だけを選ぶ手段にはならない。
- API の使い方は <https://hdr.undp.org/sites/default/files/2023-24_HDR/HDRO_data_api_manual.pdf> にある。
  hdrdata.org で登録し、メールの確認のあと別のメールで API キーが届く。
  `https://hdrdata.org/api/CompositeIndices/query?apikey=...&countryOrAggregation=AFG&year=2022&indicator=ABR` の形で、
  国 (ISO3 か地域・区分の符号)、年、指標をカンマ区切りで複数指定できる。目録は `api/Metadata/{Dimensions,Indices,Indicators,Countries,HDRegions,HDGroups}`。
- キーなしで `https://hdrdata.org/api/Metadata/Indices` を引くと HTTP 400 と `Please provide API key.` が返った。目録もキーが要る。
- API が過去の版の値を返すかは、キーが無いので確かめていない。

## ライセンス

### hdr.undp.org の利用条件

Terms of use (<https://hdr.undp.org/terms-use>、2026-10-04 に読んだ):

> Creative Commons Attribution 3.0 IGO
> All materials provided on this website are copyrighted under the Creative Commons Attribution 3.0 IGO license. This International Governmental Organizations license was developed under the auspices of the World Intellectual Property Organization (WIPO) and has been adopted by a number of other international organizations, such as CERN, ILO, OECD, WHO, UNESCO and the UN.

> You are free to:
> Share - copy and redistribute the material in any medium or format
> Adapt - remix, transform, and build upon the material for any purpose, even commercially.

> Appropriate Credit
> You must give appropriate credit, provide a link to the license, and indicate where changes were made. You may do so in any reasonable manner, but in no way that suggests the licensor endorses you or your use.

(原文の区切りの記号はダッシュ。ここでは `-` に置き換えた。)

同じ頁に、ライセンスの要約のほかに次の項がある。

> Principles
> The use of these materials should comply with the principles outlined in the United Nation Charter . By way of example and not as a limitation, when using these materials, you shall not do any of the following:
> Defame, abuse, harass, stalk, threaten or otherwise violate the legal rights (such as rights of privacy and publicity) of others;
> Publish, post, distribute or disseminate any defamatory, infringing, obscene, indecent or unlawful material or information;

> Latest available Data
> When requesting the data to be incorporated in internal servers, you must ensure you are providing the latest available data and comply with updates. The entire series of Human Development Index (HDI) values and rankings are recalculated every year using the same methodology, the most recent data. and updated time series.

> We also strongly recommend the following text to accompany the publication of the HDI dataset, particularly in print publications:
> "The entire series of Human Development Index (HDI) values and rankings are recalculated every year using the same the most recent (revised) data and functional forms. The HDI rankings and values in the 2014 Human Development Report cannot therefore be compared directly to indices published in previous Reports. Please see hdr.undp.org for more information. ..."

- 同じ CC BY 3.0 IGO の表示は、旧サイトの頁 (`http://hdr.undp.org/en/content/copyright-and-terms-use`) の
  Wayback の 2014-06-14 と 2020-06-11 の保存にもある。少なくとも 2014 年から変わっていない。
- 推奨の引用文は metadata の `recommended_citation` シートにある:
  「Source: UNDP (United Nations Development Programme). 2025. Human Development Report 2025 - A matter of choice: People and possibilities in the age of AI. New York.」
  (原文の区切りもハイフン。)
- 時系列 CSV と metadata の xlsx の中に、ライセンスや著作権の表示は無い。

### CC BY 3.0 IGO の要点

条文は <https://creativecommons.org/licenses/by/3.0/igo/legalcode>。un-wpp の README で読んだものと同じライセンス。

- 複製、再配布、改変、商用利用ができる。非商用の制限も share-alike も無い。
- 帰属の表示、ライセンスの URI、改変したことの表示が要る。
- 国連機関が推奨・関与していると示唆してはいけない。
- 紛争は調停と UNCITRAL 仲裁規則による仲裁。国連機関の特権と免除は放棄されない。

### UNDP 全体の利用規約と、報告書の PDF

- www.undp.org の Copyright and terms of use (<https://www.undp.org/copyright-terms-use>、直接は 403。
  Wayback の 20260917154342 の保存で 2026-10-04 に読んだ) は、サブドメインを含む全サイトに及ぶ。

> Unless otherwise specified in any Special Terms, UNDP grants permission to Users to visit the Sites and to download and copy information, documents and materials (collectively, "Materials") from the Sites for the User's personal, non-commercial use, without any right to resell or redistribute them or to compile or create derivative works therefrom, subject to these Terms of Use, and also subject to more specific restrictions that may apply to specific Material within the Sites.

> Third party content displayed in the Sites may only be used subject to its owner's consent or as otherwise permitted by applicable law, as the case may be.

  一般規約は非商用・再配布不可だが、「Unless otherwise specified in any Special Terms」と書いてあり、
  hdr.undp.org の Terms of use が CC BY 3.0 IGO を明示している。WPP の場合 (一般規約は「more specific restrictions」しか予定していない) と違い、
  UNDP の規約は個別の条件が優先すると文言で書いている。
- 報告書本体の PDF (`hdr2025reporten.pdf`) の奥付は「Copyright @ 2025 By the United Nations Development Programme」
  「All rights reserved. No part of this publication may be reproduced, stored in a retrieval system or transmitted, in any form or by means, electronic, mechanical, photocopying, recording or otherwise, without prior permission.」で、CC BY 3.0 IGO ではない。
  サイトの Terms of use の「All materials provided on this website」と食い違う。データのファイルには奥付が無く、
  サイトの表示しか掛かっていないので、データは CC BY 3.0 IGO と読める。報告書の本文や図をそのまま写すのは避ける。
- HDX の HDRO の 228 件は `license_id` が `cc-by-igo` 225 件、`cc-by` 3 件。

### 他機関のデータから作った値

- Terms of use の頁にも CSV にも、指標ごとに別のライセンスが付くという記載は無い。World Bank の WDI のような指標単位の除外は示されていない。
- ただし構成要素の多くは他機関の値をそのまま (あるいは補完して) 載せたもの (平均寿命は UNDESA、GNI は World Bank と IMF、
  労働参加率は ILO、議席は IPU など)。UNDP の一般規約の「Third party content」の文は、第三者の内容は持ち主の同意か法の許す範囲でのみ使える、と書く。
- 合成した指数 (HDI、GDI、IHDI、GII、PHDI) は HDRO の計算結果で、HDRO のサイトが CC BY 3.0 IGO で出している。
  構成要素の列を再配布することについて、元の機関の条件が及ぶかを HDRO は書いていない。元の機関の多くは CC BY 系
  (UNDESA の WPP、ILO、World Bank の WDI は CC BY 3.0 IGO か CC BY 4.0) だが、
  Barro and Lee、IPU、Global Carbon Project の条件は確かめていない。

### Hugging Face に置くこと

- 一次配布元の表示 (CC BY 3.0 IGO) のもとで、再配布も商用利用も CSV から Parquet への変換などの改変もできる。
- 置くときに要るもの: ライセンスの URI (`http://creativecommons.org/licenses/by/3.0/igo/`)、
  推奨の引用文、形式を変えたことの記載、UNDP が関与しているように見せないこと。
- Terms of use の「Latest available Data」の項は「internal servers」に取り込む場合に最新の値を使い更新に従うよう求めている。
  公開のミラーに当たるかは文言からは分からないが、版の名前 (HDR 2025 など) をデータセットに明記し、
  最新ではない版であることが分かるようにしておくのが筋。
- 推奨の注記 (HDI は毎年全系列を計算し直すので、別の報告書の値と比べられない) を README に入れる。
- Hugging Face のライセンス選択肢に CC BY 3.0 IGO があるかは確かめていない。無ければ `license: other` にして本文で明記する。

## 版

### 毎年の計算し直し

Terms of use の原文 (上に引用) のとおり、HDI の全系列と順位は毎年、最新のデータで計算し直される。
実際に、HDR 2023/24 の CSV と HDR 2025 の CSV で日本の値を比べると、同じ年の値が違う。

| 列 | HDR 2023/24 | HDR 2025 |
|---|---:|---:|
| `hdi_1990` | 0.846 | 0.853 |
| `hdi_2000` | 0.883 | 0.889 |
| `hdi_2010` | 0.903 | 0.907 |
| `hdi_2020` | 0.917 | 0.922 |
| `hdi_2022` | 0.920 | 0.921 |
| `le_2010` | 82.919 | 82.916 |
| `gnipc_2010` | 39,084.57 | 42,697.71 |

- GNI の大きな変化は PPP の基準年の違いと考えられる (HDR 2025 の Technical Notes は 2021 年 PPP で計算すると書く)。
  HDR 2023/24 の基準年は確かめていない。
- 版ごとに別のデータセットとして持つ必要がある。1 つの年の値を版をまたいで混ぜると系列が壊れる。

### 過去の版の取得

配布元の頁には現行の HDR 2025 しか載っていないが、過去の版のファイルは同じサーバーに残っていて HEAD で 200 が返った。

| 版 | 時系列 | 大きさ (バイト) | Last-Modified | 期間 |
|---|---|---:|---|---|
| HDR 2025 | `2025_HDR/HDR25_Composite_indices_complete_time_series.csv` | 2,001,263 | 2025-05-05 | 1990〜2023 |
| HDR 2023/24 | `2023-24_HDR/HDR23-24_Composite_indices_complete_time_series.csv` | 1,919,243 | 2024-03-13 | 1990〜2022 (1,076 列) |
| HDR 2021/22 | `2021-22_HDR/HDR21-22_Composite_indices_complete_time_series.csv` | 1,781,357 | 2022-09-07 | 未確認 |
| HDR 2020 | `data/2020/{HDI,GDI,GII,IHDI,PHDI}_HDR2020_040722.csv` の 5 本 | 262,671 / 218,207 / 181,078 / 93,402 / 14,513 | 2022-06-08 | 未確認 |

- 前に `https://hdr.undp.org/sites/default/files/` を付ける。metadata の xlsx も 2023/24 (19,405 バイト) と 2021/22 (13,635 バイト) が残っている。
- HDR 2020 は版ごとの 1 本の CSV ではなく指数ごとの 5 本で、列の構成は 2021/22 以降と違うと考えられる (中身は開いていない)。
- 統計付録の XLSX も、2021/22 と 2023/24 は残っている。HDR 2020 の `data/2020/2020_statistical_annex_all.xlsx` (1,465,288 バイト) と
  2018 年の `composite_tables/2018_Statistical_Annex_Table_*.xlsx` も 200。
  一方 `2018_statistical_annex_all.xlsx` は 404、2015 年の `2015_statistical_annex_tables_all.xls` は
  `private/documents/` へ 301 で転送されたうえで 403 になる。この 403 には Cloudflare のチャレンジの印 (`cf-mitigated`) が無く、
  Pantheon の配信元が返している。Wayback も 2024-10 以降この転送先では 403 しか保存していない。古い版はサイトの作り直しで非公開の置き場に移されたと見られる。
- Internet Archive の CDX には、3 つの時系列 CSV と HDR 2020 の 5 本の CSV がすべて 200 で保存されている。
  HDR 2025 の CSV の保存 (20250523112831) の digest は、いま取れるファイルの SHA-1 (base32) と一致した。公表後に差し替えられていない。
  HDR 2021/22 の CSV も 2022-09 と 2023-03 の保存で digest が同じ。
- Wayback には 2015、2016、2018、2020 年の統計付録の XLS/XLSX も残っている (`hdr.undp.org/sites/default/files/composite_tables/` など)。
- 過去の版も Terms of use の CC BY 3.0 IGO の下にある (2014 年の保存から同じ表示)。

### MPI の版

MPI は HDR とは別の日程で更新される (2025 年版は 2025-10-17)。調査の年が国ごとに違い、
毎年すべての国の値が新しくなるわけではない。過去の MPI の版のファイルは調べていない。

## 未確認の点

- HDR 2021/22 の時系列 CSV の期間と列、HDR 2020 の 5 本の CSV の列の構成。
- HDR 2023/24 の GNI の PPP 基準年。
- `2025_gMPI_Table1and2.xlsx` の中身と、地方別 (1,359 地域) の推計が入っているか。地方別の MPI を OPHI 側でどう配っているか。
- HDRO Data API が過去の版の値を返すか。利用回数の上限。API キーを取っていない。
- Documentation and downloads の頁の埋め込みアプリが使うデータの出どころ。
- 構成要素の列 (他機関の値) の再配布に、元の機関の条件が及ぶかについての HDRO の見解。Barro and Lee、IPU、Global Carbon Project の条件。
- Terms of use の「Latest available Data」の項が、過去の版の公開ミラーに適用されるか。
- 報告書の PDF の「All rights reserved」とサイトの CC BY 3.0 IGO の関係についての HDRO の見解。
- Hugging Face のライセンス一覧に CC BY 3.0 IGO があるか。
