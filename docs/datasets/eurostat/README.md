# Eurostat データベース (欧州連合統計局)

2026-10-04 (JST) に読んで確かめた内容。ページと API は curl で取得して読んだ。件数は機械可読の目録 (table of contents、inventory、metabase) を数えた値。大きさは HEAD の `Content-Length` で測った。中身は表 `tgs00003` (NUTS 2 地域の域内総生産) の TSV 1 本 (gzip で 35,173 bytes) と、同じ表の SDMX-CSV の先頭だけを見た。データベース全体は落としていない。

- 入口: <https://ec.europa.eu/eurostat/web/main/data/database> (ページ名「Database」)。表の閲覧は Data Browser (`https://ec.europa.eu/eurostat/databrowser/product/view/<コード>`)。
- 一括取得の案内: <https://ec.europa.eu/eurostat/data/bulkdownload>、画面は <https://ec.europa.eu/eurostat/databrowser/bulk?lang=en>。
- API: `https://ec.europa.eu/eurostat/api/dissemination/` 以下。SDMX 2.1 (`sdmx/2.1/`)、JSON-stat 2.0 (`statistics/1.0/`)、目録 (`catalogue/`)、ファイル置き場 (`files/`)。
- 作成: 欧州委員会の総局のひとつである Eurostat。各国統計局から送られた値を Eurostat が集めて公表する。一次配布元は ec.europa.eu の Eurostat のサイトと API。data.europa.eu (EU のオープンデータポータル) にも同じ表が `estat` カタログとして載っているが、メタデータを転載しているだけ。
- 量: 表は 7,600 (inventory の DATASET)。そのうち 7,144 に地域の次元 (`geo`) がある。gzip した TSV で全体は数 GB から 15GB 程度 (推定、下で説明)。
- ライセンス: 統計データは出典を示せば商用・非商用とも再利用できる。ただし EU、EFTA、加盟候補国以外の国のデータなどは商用利用が除外されている。GISCO の NUTS 境界は非商用に限られ、別の条件になる。
- 版: 表は上書き更新 (1 日 2 回、11:00 と 23:00 CET)。過去の版を取る手段は見つからなかった。

## 目録

### table of contents

`https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en` が TSV で返る (`table_of_contents_en.txt`、1,968,640 bytes、12,240 行)。XML 版は `catalogue/toc/xml`。認証は要らない。

列は `title`、`code`、`type`、`last update of data`、`last table structure change`、`data start`、`data end`、`values`。`type` は `folder`、`dataset`、`table` の 3 種類。同じ表が複数のフォルダに出るので、行数とコードの数は違う。

| type | 行数 | コードの数 |
|---|---:|---:|
| folder | 1,925 | 1,878 |
| dataset | 8,872 | 6,649 |
| table | 1,442 | 912 |

- `title` の先頭の空白 (4 文字ずつ) が木の深さを表す。木は「Database by themes」と「Cross cutting topics」の 2 本。
- `values` は表の値の数。dataset と table のコード 7,561 個の合計は 6,474,295,000 (約 65 億)。最大は `migr_asyrescra` (213,650,346)。
- `last update of data` の日付は 2009-03-26 から 2026-10-03。2026 年に更新された dataset は 3,719 で、2009 年のまま止まっているものが 416 ある。
- `data start` の最古は `1947-Q1`。時間の単位は年 (`2013`)、四半期 (`2026-Q1`)、月 (`1950-01`)、週と日が混ざる。

### inventory

`https://ec.europa.eu/eurostat/api/dissemination/files/inventory?type=data` (4,522,807 bytes、TSV)。1 行 1 表で、各形式のダウンロード URL が並ぶ。

- 列は `Code`、`Type`、`Source dataset`、`Last data change`、`Last structural change`、`Data download url (tsv)`、`Data download url (csv)`、`Data download url (sdmx)`、`Data structure download url`、`Open in Data Browser url`。
- 8,146 行。`DATASET` が 7,600、`EXTRACTION` が 546。`EXTRACTION` は元の表から切り出したもので、コードが `BD_9AC_L_FORM_R2$DV_343` のように `$` を含み、`Source dataset` に元の表が入る。
- `DATASET` の 7,600 は、table of contents の dataset 6,649 と table 912 をすべて含み、ほかに目録の木に出てこない 39 個 (`tag00052`、`tec00108` など) がある。
- `Last data change` と `Last structural change` は時刻付き (`2026-05-13T11:00:00+0200`)。

### metabase

`https://ec.europa.eu/eurostat/api/dissemination/catalogue/metabase.txt.gz` (4,063,443 bytes、展開すると 1,344,313 行)。表、次元、コードの 3 列で、どの表にどのコードが出てくるかが分かる。HEAD では `Content-Length` が返らなかった。

## 中身

### 主題

table of contents の「Database by themes」の下の 10 の主題と、表の数 (重複を除いたコード):

| コード | 主題 | 表の数 |
|---|---|---:|
| general | General and regional statistics | 898 |
| economy | Economy and finance | 395 |
| popul | Population and social conditions | 3,685 |
| icts | Industry, trade and services | 524 |
| agric | Agriculture, forestry and fisheries | 508 |
| external | International trade | 63 |
| transp | Transport | 659 |
| envir | Environment and energy | 275 |
| science | Science, technology, digital society | 679 |
| tb_eu / cc | EU policies / Cross cutting topics (再掲の木) | 685 / 1,150 |

`general` の下に「Regional statistics by NUTS classification」(`reg`、354 表)、「Regional statistics by typology」(`reg_typ`、82)、「Degree of urbanisation」(`degurb`、173)、「City statistics」(`urb`、21)、「Non EU countries」(`noneu`、176) がある。ほかの主題の中にも地域別の表が散っている (`tran_r` など)。表題に「NUTS」を含む dataset は 488 行。

### 地域の単位

metabase の `geo` 次元のコードを、GISCO の NUTS 2021 と NUTS 2024 のコード一覧 (下の「NUTS と GISCO の境界」) と突き合わせ、表ごとに一番細かい NUTS の階層を数えた。

| 一番細かい単位 | 表の数 |
|---|---:|
| NUTS 3 | 124 |
| NUTS 2 | 412 |
| NUTS 1 | 79 |
| 国 (NUTS 0) | 6,267 |
| `geo` はあるが NUTS のコードが無い (EU27_2020 などの集計や EU 外の国だけ) | 262 |
| `geo` 次元が無い | 456 |

- 古い版 (NUTS 2016 以前) にしか無いコードは数えていないので、NUTS 1/2/3 の表の数は下限。
- 国のコードはギリシャが `EL`、英国が `UK` (ISO 3166 の `GR`、`GB` ではない)。
- 集計地域のコードが国と並んで入る (`EU27_2020`、`EA20` など)。
- 地域の値には国外の領域や所在不明の分を表す `ZZ` 付きのコード (`ATZZ`、`FRZZ` など、Extra-Regio) が混ざる。`tgs00003` では 10 個以上あった。
- 加盟候補国は NUTS ではなく統計地域のコードで入る (`tgs00003` のアルバニア `AL01`〜`AL03`)。

`tgs00003` (2026-02-10 更新) の 4 文字の地域コード 309 個のうち 293 個が NUTS 2024 にあり、NUTS 2021 には無い `NL35`、`NL36`、`PT19`〜`PT1D` を含んでいた。この表は NUTS 2024 で出ている。表によってどの版の NUTS を使っているかは違いうるが、全表は調べていない (未確認)。

### 形式

同じ表を 3 形式で取れる。

- TSV (gzip)。1 列目に次元のコードをカンマでつないだもの (`freq,unit,geo\TIME_PERIOD`)、2 列目以降が時点。値の後ろに空白とフラグが付く (`4887.89 ` や `2939.04 p`)。欠測は `:`。`tgs00003` は 619 行 (見出しを含む)、フラグは `p` (暫定) 724 個と `e` (推計) 66 個。
- SDMX-CSV。1 観測 1 行の縦持ち。列は `DATAFLOW,LAST UPDATE,freq,unit,geo,TIME_PERIOD,OBS_VALUE,OBS_FLAG,CONF_STATUS`。`DATAFLOW` は `ESTAT:TGS00003(1.0)` で、表の構造の版 (1.0) が付く。`LAST UPDATE` は `10/02/26 11:00:00`。
- SDMX 2.1 (XML)。構造定義 (DSD、コードリスト) は inventory の `Data structure download url` で取れる。

### 大きさ

TSV gzip の URL (`sdmx/2.1/data/<コード>/?format=TSV&compressed=true`) に HEAD を投げると `Content-Length` が返る。

- 例: `nama_10r_3gdp` (NUTS 3 の域内総生産) 743,572 bytes、`tgs00003` 35,173 bytes、最大の `migr_asyrescra` 121,204,846 bytes。
- 全表に HEAD は投げていない。table of contents の値の数から無作為に 40 表を選んで HEAD を投げると、1 値あたり 2.27 bytes (合計の比)。表ごとの比の中央値は 3.70、`migr_asyrescra` は 0.57。大きい表ほど 1 値あたりが小さい。全体の 65 億値に掛けると、0.57 なら 3.7GB、2.27 なら 14.7GB。gzip の TSV で全体は数 GB から 15GB 程度と見ている (推定)。
- 国際貿易の詳細データ (Comext) は別の置き場にある (`files/?sort=1&dir=comext`)。`COMEXT_DATA/PRODUCTS` だけで 7z が 392 本、画面の表示の合計で約 12.7GB。上の推定には入っていない。

## 取り出し方

区分は split。表ごとに 1 本のファイルになっていて、必要な表だけ取れる。各ファイルの中は whole。目録 (table of contents、inventory、metabase) が機械可読で取れるので、表を選ぶところは catalog に近い。API で次元を絞って一部だけ取ることもできる。

| 区分 | 手段 | 実測 |
|---|---|---|
| split | 表ごとの TSV gzip / SDMX-CSV / SDMX 2.1 | 7,600 表。`tgs00003` で 35,173 bytes |
| catalog | table of contents、inventory、metabase。SDMX と JSON-stat の API で次元を指定 | 認証なしで全表を列挙できた |
| range | 不可 | `Range: bytes=0-1023` に 206 ではなく 200 (chunked) が返った |
| whole | Data Browser の bulk 画面で複数の表を選んで 1 つの圧縮ファイルにまとめる | 試していない |

- 表の URL は `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/<コード>/?format=TSV&compressed=true`。応答は `Content-Disposition: attachment; filename="estat_nama_10r_3gdp.tsv.gz"`。`format=SDMX-CSV` で SDMX-CSV、`format=sdmx_2.1_generic` で XML。
- 応答に `Last-Modified` と `ETag` は無かった。更新の有無は inventory の `Last data change` で見る。
- 次元で絞る例。SDMX のキー `sdmx/2.1/data/TGS00003/A.MIO_EUR.DE11?format=SDMX-CSV&startPeriod=2022` は 3 行を返した。JSON-stat の `statistics/1.0/data/tgs00003?geo=DE11&time=2020` は値 1 つの JSON-stat 2.0 を返し、`updated` (2026-02-10) と DOI が付いていた。
- bulk の案内ページの原文: 「information updated twice a day, at 11:00 and 23:00 CET」「datasets available in tsv (tab separated values) and sdmx format」「an inventory / table of contents that each include the list of the datasets available」。
- 以前の一括取得の画面 `https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing` は 2026-10-04 に 404。Internet Archive では 2024-01-07 までは 200 で保存されていて、2026 年の保存は 301 と 404。今の `api/dissemination/files/` に移ったものと見ている。

## ライセンス

### Eurostat の copyright notice

<https://ec.europa.eu/eurostat/help/copyright-notice> (ページ名「Copyright notice and free re-use of data」、2026-10-04 に読んだ)。データベースのページのフッターからリンクされている。`https://ec.europa.eu/eurostat/about-us/policies/copyright` は 404 で、こちらは正しい URL ではない。

一般原則:

> The copyright for the editorial content of this website, which is owned by the EU, is licensed under the Creative Commons Attribution 4.0 International licence.
> This means that you can re-use the content provided you acknowledge the source and indicate any changes you have made.

> Reuse of statistical data, metadata, publications, and other dissemination tools published on this website for commercial or non-commercial purposes is authorised provided the source is acknowledged. The reuse policy of the European Commission is implemented by the Decision of 12 December 2011.

除外 (第三者の権利とロゴ):

> The permission granted above does not extend to any material whose copyright is identified as belonging to a third-party, such as photos or illustrations from copyright holders other than the European Union.

> Logos and trademarks are excluded from the above mentioned general permission, except if they are redistributed as an integral part of a Eurostat publication and if the publication is redistributed unchanged.

加工したとき:

> When reuse involves translations of publications or modifications to the data or text, this must be stated clearly to the end user of the information. A disclaimer regarding the non-responsibility of Eurostat shall be included.

商用利用の除外 (非商用は自由):

> The following Eurostat data and documents may not be reused for commercial purposes, but non-commercial reuse is possible without restriction:

挙げられているのは次の 5 つ。

- Eurostat 以外の出典のものと明示されたデータ。「All data published on Eurostat's website can be regarded as belonging to Eurostat for the purpose of their reuse, with the exceptions stated below, or if it is explicitly stated otherwise.」
- 権利の一部または全部が他の組織にある出版物 (共同出版など)。
- EU 加盟国、EFTA 加盟国、正式な EU 加盟候補国以外の国のデータ。原文は「Examples are data for the United States of America, Japan or China. In such cases, the user will need to eliminate these data from the tables before reusing them commercially.」
- リヒテンシュタインとスイスが申告国の 1995 年以降の貿易データ (HS、SITC、BEC、NSTR と各国の品目分類)。
- オーストリアが申告国の CN 8 桁の貿易データ。

商用利用の手続:

> There is no special procedure or requirement for a written licence. Just download the material and use it, unless the material is listed in the exceptions above.

出典の書き方 (表の場合):

> Source: [digital object identifier (DOI) number of the Eurostat dataset], [access date]

> Customised versions of a dataset must be cited as following:
> Source: [Eurostat dataset datacode link], [access date]

表の DOI は `10.2908/<コード>` (`https://doi.org/10.2908/TGS00003` は `https://ec.europa.eu/eurostat/product?code=TGS00003` へ 302)。

### 欧州委員会の再利用ポリシー

- 欧州委員会のサイトの Legal notice (<https://commission.europa.eu/legal-notice_en>、2026-10-04 に読んだ):

> Unless otherwise indicated (e.g. in individual copyright notices), content owned by the EU on this website is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence. This means that reuse is allowed, provided appropriate credit is given and changes are indicated.

> Software or documents covered by industrial property rights, such as patents, trade marks, registered designs, logos and names, are excluded from the Commission's reuse policy and are not licensed to you.

- 根拠は Commission Decision 2011/833/EU (<https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32011D0833>、2026-10-04 に読んだ)。第 6 条:

> Documents shall be made available for reuse without application unless otherwise specified and without restrictions or, where appropriate, an open licence or disclaimer setting out conditions explaining the rights of reusers.

  条件として挙げられるのは出典の表示、元の意味を歪めないこと、委員会の免責の 3 つ。第 2 条 2 項で、第三者の知的財産権のあるもの、ロゴや名称など産業財産権のあるもの、Regulation (EC) No 223/2009 の秘匿データは対象外。

- data.europa.eu の `estat` カタログでは、`tgs00003` の配布 (HTML、CSV、XML) の `license` が `http://spdx.org/licenses/CC-BY-4.0` だった (API `https://data.europa.eu/api/hub/search/search?q=tgs00003&filter=dataset`)。

### Hugging Face に置くときの読み

- 再配布と商用利用は、出典 (DOI と取得日) を書き、加工したならその旨と Eurostat の免責を書けばできる。識別子は `CC-BY-4.0` が配布元とデータポータルの表記に合う。
- ただし素の CC BY 4.0 ではない。EU、EFTA、加盟候補国以外の国の行は商用利用できないと copyright notice が書いている。「Non EU countries」(`noneu`) の表のほか、国の次元に `US`、`JP`、`CN` などが入る表は多い。全行を CC BY 4.0 とだけ表示して置くと、この除外と食い違う。対象外の国の行を除くか、その行が非商用であることを併記する必要がある。
- スイス、リヒテンシュタイン、オーストリアの貿易データの除外は、主に Comext の詳細データに関わる。
- 個々の表のメタデータに別の権利表示があるかは、全表は見ていない (未確認)。

## NUTS と GISCO の境界

### 関係

- NUTS (Nomenclature of territorial units for statistics) は EU の地域区分。規則で定められ、数年ごとに改正される。GISCO の説明: 「NUTS 1: major socio-economic regions」「NUTS 2: basic regions for the application of regional policies」「NUTS 3: small regions for specific diagnoses」「Also, there is a NUTS 0 level, which usually corresponds to the national boundaries.」
- Eurostat の表は `geo` の列に NUTS のコード (`DE11` など) だけを持ち、形は持たない。地図に置くには、GISCO (Eurostat の地理情報の部署) が配る NUTS の境界とコードで結ぶ。
- 結ぶときは NUTS の版を合わせる。`tgs00003` は NUTS 2024 のコードだった。境界の版を間違えると、変わった地域 (オランダ、ポルトガルなど) が黙って落ちる。
- GISCO の配布 API: <https://gisco-services.ec.europa.eu/distribution/v2/nuts/>。`datasets.json` に版が 7 つ (NUTS 2003、2006、2010、2013、2016、2021、2024)。形式は CSV、GeoJSON、GeoPackage、Parquet、PBF、SHP、SVG、TopoJSON。縮尺は 01M から 60M、座標系は EPSG:3035、4326、3857。GISCO のサーバーは `accept-ranges: bytes` を返す (`nuts-2024-units.json` 1,670,146 bytes、`last-modified: Thu, 01 Oct 2026`)。
- コード一覧 `csv/NUTS_AT_2024.csv` (92,282 bytes) は 1,971 コード (国 39、NUTS 1 が 123、NUTS 2 が 326、NUTS 3 が 1,483)。`NUTS_AT_2021.csv` は 2,010 コード (NUTS 2 が 334)。どちらにも `ZZ` のコードは無い。

### 境界のライセンスは統計と別

GISCO の統計単位のページ <https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units> (2026-10-04 に読んだ)。NUTS、LAU、census、coastal、cities and functional urban areas に適用される。

> The Commission agrees to grant the non-exclusive and non-transferable right to use and process the Eurostat/GISCO geographical data downloaded from this page (the ‘data’).
> The permission to use the data is granted on condition that:
> the data will not be used for commercial purposes
> the source will be acknowledged.

表示の文言:

> EN: © EuroGeographics for the administrative boundaries

> If you intend to use the data commercially, please contact EuroGeographics for information about their licence agreements.

行政単位 (communes、countries、postal codes) のページ <https://ec.europa.eu/eurostat/web/gisco/geodata/administrative-units> も同じ条件。

- NUTS の境界は非商用で、譲渡できない (non-transferable) 利用権。統計データの CC BY 4.0 相当とは違い、Hugging Face にオープンデータとして置く条件を満たさない。置くなら統計の表とコードだけにして、境界は GISCO から取ってもらう形になる。
- コード一覧の CSV (名前と属性だけで形の無いもの) がこの条件に入るかは、ページの文言からは決められない (未確認)。

## 版

- 表は上書き更新。bulk は 1 日 2 回 (11:00 と 23:00 CET) 更新される。2026-10-04 の table of contents では、`last update of data` が 2026 年の dataset が 3,719 あった。
- 過去の版を取る手段は見つからなかった。表の URL に版の指定は無く、DOI (`10.2908/<コード>`) も最新の表を指すだけ。SDMX-CSV の `ESTAT:TGS00003(1.0)` の `1.0` は表の構造の版で、データの時点の版ではない。
- 値は改訂される。データ改訂方針のページ (<https://ec.europa.eu/eurostat/data/data-revision-policy>) は、定例の改訂 (各国からの新しい送信)、大きな改訂 (国民経済計算の 5 年ごとの基準改定、分類の変更など、事前告知あり)、誤りの訂正による予定外の改訂の 3 つを挙げる。改訂の情報は各領域のメタデータの「Data revision - policy」「Data revision - practice」に書かれる。
- NUTS が改正されると、地域の表のコードも新しい版に置き換わる (`tgs00003` は NUTS 2024)。
- 版として残すなら、取った日と inventory の `Last data change` を自分で記録するしかない。

## 未確認の点

- 全表の gzip TSV の合計の大きさ (40 表の標本からの推定だけ)。Comext の全体の大きさ。
- Data Browser の bulk 画面で全表をまとめて取る操作と、その大きさ。
- 過去の版を取る手段が API や別の置き場にあるか (速報値の改訂を追う real-time database の有無。推測で組んだ URL 2 つが 404 だっただけで、無いとは確かめていない)。Internet Archive に表の TSV の保存があるか。
- 表ごとに使っている NUTS の版。
- 個々の表のメタデータに copyright notice と別の権利表示があるか。
- GISCO の NUTS コード一覧 (形の無い CSV) に非商用の条件がかかるか。
