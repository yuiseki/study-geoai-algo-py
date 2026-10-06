# Risk Data Library (RDL)

2026-10-06 に読んで確かめた内容。ページは curl で取得して読み、目録は GitHub の公開リポジトリのファイル一覧 (GitHub API の
git tree) と、そこから一様無作為に選んだ 400 件の JSON で数えた。データ本体は落としていない。大きさは HEAD と
`Range: bytes=0-0` の応答、および HDX の CKAN API (`package_show`) が返す resource の `size` から取った。
実測と推定は節ごとに分けて書く。

- 入口: <https://riskdatalibrary.org/>。データの案内は <https://riskdatalibrary.org/data/>。
- 目録 (カタログ): <https://catalog.riskdatalibrary.org/> (表題は "Risk Data Library catalog (beta)")。
- 目録の実体: GitHub の [GFDRR/rdl-jkan](https://github.com/GFDRR/rdl-jkan)、既定ブランチ `rdl-1.0` の `_datasets/json/`。
- 標準の文書: <https://docs.riskdatalibrary.org/en/latest/> (RDLS 1.0.0)。リポジトリは [GFDRR/rdl-standard](https://github.com/GFDRR/rdl-standard)。
- 運営: 世界銀行が事務局を務める防災基金 GFDRR (Global Facility for Disaster Reduction and Recovery)。
  サイトのフッタは "An initiative of the GFDRR"、目録のフッタには Swiss Re Foundation と Gates Foundation のロゴがある。
- 結論を先に書くと、RDL はデータの置き場ではなく、他所のデータを RDLS という形式で記述したメタデータの目録である。
  記録 9,665 件のうち約 86% は HDX (Humanitarian Data Exchange) から自動で抜き出したもので、ファイルはすべて元の配布元にある。

## 1. Risk Data Library とは

- GFDRR が 2016 年ごろから進めてきた計画で、当初は災害リスク評価のためのデータベース構造 (hazard は BGS、exposure の
  GED4ALL と loss は GEM 財団、vulnerability の MOVER は UCL EPICentre が担当) だった。2021 年からこれを公開の
  メタデータ標準に作り替え、同時に JKAN (Jekyll で動く静的なデータカタログ) の試作カタログを作った
  (<https://riskdatalibrary.org/project/> の記述)。
- 2022 年に Swiss Re Foundation の助成を得て、世界銀行の Data Catalog (Development Data Hub) に "Risk Data Library
  Collection" (<https://datacatalog.worldbank.org/search/collections/RDL>) を作った。
- RDLS (Risk Data Library Standard) は、リスク評価で使う・作るデータを hazard (ハザード)、exposure (曝露)、
  vulnerability (脆弱性)、loss (損失・被害) の 4 要素で記述する JSON のメタデータ標準である。データの中身の形式は
  標準化しない (案内だけ)。
  - 1.0 が 2026-06-10 に出た (changelog <https://docs.riskdatalibrary.org/en/latest/about/changelog/>)。
    レビュー期間は 2026-05-13〜05-30 だった (ブログ 2026-05-18)。スキーマは
    <https://docs.riskdatalibrary.org/en/1__0__0/rdls_schema.json>。
  - 文書のライセンスは CC BY-SA 4.0 (<https://docs.riskdatalibrary.org/en/latest/about/license/>)。rdl-standard リポジトリも CC-BY-SA-4.0。
  - RDLS の resource には大きさ (バイト数) の項目がない。大きさは目録からは分からない。
- サイトの /data/ ページが挙げる「RDLS を使っているカタログ」は 3 つ。
  1. Risk Data Library catalog (JKAN、GFDRR の自前)。本書の主な対象。
  2. 世界銀行 Data Catalog の RDL コレクション。
  3. 欧州委員会 JRC の DRMKC Risk Data Hub (<https://drmkc.jrc.ec.europa.eu/risk-data-hub#/atlas/>)。
- JKAN カタログは README で、World Bank Data Catalog、HDX、Copernicus Climate Data Store、FAO、GAR PreventionWeb などを
  まとめて検索できると書く。実際の記録の取り込み元は「2. 目録の数え方」の表のとおりで、HDX が圧倒的に多い。
- 目録の免責 (<https://catalog.riskdatalibrary.org/legal/>) は "proof-of-concept implementation" と書いている。

## 2. 目録の数え方

### 文書化された API について

- JKAN カタログの画面は Netlify Function (`https://rdl-jkan.netlify.app`) に検索を投げる。これは文書化された API ではない
  (サイトの JS の内部呼び出し) ので使っていない。
- JKAN が本来出す `/data.json` と `/rdl-datasets.json` はリポジトリに雛形があるが、公開サイトでは 404 だった
  (ブラウザの User-Agent でも同じ。GitHub Pages の応答)。
- CKAN の API はない。STAC もカタログとしては出ていない ([GFDRR/rdl-stac](https://github.com/GFDRR/rdl-stac) は STAC 拡張の定義だけ)。

### 使える列挙の方法: GitHub リポジトリ

- 公開リポジトリ [GFDRR/rdl-jkan](https://github.com/GFDRR/rdl-jkan) (ブランチ `rdl-1.0`) の `_datasets/json/` に、
  1 データセット 1 ファイルの RDLS JSON (`{"datasets":[{...}]}`) が置かれている。カタログのページ (`_datasets/*.md`) は
  これから CI (`python/main.py --markdown`) が生成する。
- 一覧の取り方: `https://api.github.com/repos/GFDRR/rdl-jkan/git/trees/rdl-1.0?recursive=1` (truncated=false で 19,632 項目)。
  個々のファイルは `https://raw.githubusercontent.com/GFDRR/rdl-jkan/rdl-1.0/_datasets/json/<id>.json`。
- 件数 (2026-10-06 の tree): JSON 9,665 件、合計 108,148,192 bytes (約 108 MB)。生成された .md も 9,665 件 (約 114 MB)。
  リポジトリ全体は約 249 MB (国境 GeoJSON などを含む)。
- リポジトリのライセンスは MIT だが、これは JKAN のソフトウェアの LICENSE (著作者 Tim Wisniewski) で、メタデータの記録の
  ライセンスはどこにも書かれていない。記録の説明文の多くは HDX の説明文の写しである。

### 取り込みの内訳 (コミットの記録から)

2026-06-15 に「再取り込みのため削除」したうえで、23 回に分けて入れ直している。

| batch | 中身 | 件数 |
|---|---|---|
| 1 | 旧 JKAN の記録を v1.0 に変換 | 44 |
| 2 | DesInventar、Google、India GOBS、JRC-DRMKC | 38 |
| 3 | NISMOD (ICRA、SDK) | 256 |
| 4 | Tomorrow Cities、vulnerability、WBG-UFRA | 29 |
| 5 | GeoNode (各国の GeoNode) と MDG | 762 |
| 6 | STAC (climate-risk、CoCliCo) | 239 |
| 7〜23 | HDX (17 回) | 残り約 8,297 |

HDX 以外は合計 1,368 件、HDX 由来は約 8,297 件 (85.8%) になる。無作為標本 400 件では publisher が
"Humanitarian Data Exchange (HDX)" のものが 335 件 (83.8%) で、整合する。

### 世界銀行 Data Catalog の RDL コレクション

- 世界銀行の Data Catalog API は文書化されている (<https://datahelpdesk.worldbank.org/knowledgebase/articles/1886698-data-catalog-api>
  が案内する暫定文書 <https://gist.github.com/tgherzog/e6090f9b2ba74f49f75b228f5c7169b9>)。`/ddhxext/DatasetList`、
  `/ddhxext/Search` (OData の `$filter`)、`/ddhxext/DatasetView` (版の `version_id` 指定可)、`/ddhxext/ResourceDownload` がある。
- ただし今回は `datacatalogapi.worldbank.org` が 4 回続けて 429 (Rate limit is exceeded) を返したので打ち切った。
  RDL コレクションの件数と、コレクションで絞り込む `$filter` の書き方は未確認 (unknown)。
- JKAN 側の記録のうち世界銀行のものは少ない。ID に `gfdrr` を含むものは 9 件 (アフガニスタンと南スーダンのハザード)、
  標本 400 件で配布 URL が `datacatalogfiles.worldbank.org` のものは 1 件だった。

## 3. ファイルの置き場所

RDL 自身はファイルを持たない (旧来の RDL の AWS バケットは鍵が要る内部用で、[GFDRR/rdl-bucket](https://github.com/GFDRR/rdl-bucket) は
その管理ツール)。`resources[].download_url` か `access_url` が元の配布元を指す。

標本 400 件の resource は 4,060 個 (1 データセット平均 10.15 個)、うち http の `download_url` を持つものが 3,759 個。
ホスト別の resource 数は次のとおり。

| ホスト | resource 数 | 備考 |
|---|---|---|
| data.worldpop.org | 2,530 (67%) | WorldPop の GeoTIFF と zip。HEAD で Content-Length、Accept-Ranges: bytes |
| data.humdata.org | 635 (17%) | HDX。S3 (`s3.*.amazonaws.com`) に転送され、Range が効く (206) |
| fdw.fews.net | 220 | FEWS NET の API で GeoJSON を生成。1 件は応答が返らず止まった |
| unosat.org、unosat-maps.web.cern.ch | 79 | UNOSAT の被害判読 (shp、gdb の zip) |
| geonode.pacificdata.org | 46 | GeoServer の WMS GetMap と WFS。403 が多い |
| maps.eurac.edu | 32 | GeoServer。到達不能 (No route to host) |
| export.hotosm.org ほか HOT の S3 | 20 前後 | 期限切れで 404 のものがある |
| Kontur の S3、HeiGIT のストレージ、Zenodo、Google Cloud Storage、Azure ほか | 少数 | |

- Range: HEAD または Range で成功した 219 件のうち 203 件が 206 応答か `Accept-Ranges: bytes` を示した。
- 失敗: 250 件中 36 件。http の URL がない 11、404 が 9 (WorldPop の PCN、HOT export、HDX)、403 が 7
  (Pacific Community の GeoNode、Zenodo、IOM。ブラウザの User-Agent でも 403)、到達不能 3、応答なし 1。
  リンク切れが目に見える割合で混じっている。
- WMS GetMap の URL を「ダウンロード」として載せている記録がある。この応答は描画した PNG で、データではない。

## 4. 内訳

### リスク要素 (全 9,665 件、実測)

ID の接頭辞 (`rdls_<要素>-...`) から数えた。`hzd` `exp` `vln` `lss` は単独、`he` `hel` `el` などは組み合わせ
(h=hazard、e=exposure、v=vulnerability、l=loss)。

| 接頭辞 | 件数 |
|---|---|
| exp | 4,290 |
| lss | 2,059 |
| hzd | 1,516 |
| he | 591 |
| hel | 508 |
| el | 333 |
| hl | 275 |
| vln | 65 |
| hevl | 14 |
| ev | 7 |
| hev | 7 |

要素ごとに重複を許して数えると exposure 5,750、loss 3,189、hazard 2,911、vulnerability 93。
vulnerability (被害関数など) は 1% に満たない。

### 作成者 (全 9,665 件、ID からの近似)

ID の `<国>_<組織>_<名前>` の組織部分から数えた。国コードのない ID もあるので近似である。

| 組織 | 件数 |
|---|---|
| unosat | 1,393 |
| worldpop | 1,175 |
| hotosm | 723 |
| fewsnet | 638 |
| copernicus (HDX 上の GHSL など) | 472 |
| idmc | 418 |
| heigit | 350 |
| kontur | 328 |
| hdx | 307 |
| pacificdata | 294 |
| wfp | 292 |
| nismod | 248 |
| undrr | 213 |
| metad4g (Meta Data for Good) | 203 |
| iom | 200 |
| icpac | 193 |
| cred (EM-DAT) | 134 |
| hdxapi (HDX HAPI) | 122 |

標本 400 件の `publisher.name` は HDX が 335、Zenodo 15、Pacific Community 10、ICPAC 5 などで、
HDX 由来の記録では publisher が HDX、creator が元の組織になっている。

### ライセンス (標本 400 件、推定)

RDL の `license` 欄をそのまま数えたもの。全体件数は 9,665/400 倍した推定。

| license 欄 | 標本 | 割合 | 全体の推定 |
|---|---|---|---|
| CC-BY-4.0 | 291 | 72.8% | 約 7,030 |
| CC-BY-SA-4.0 | 51 | 12.8% | 約 1,230 |
| ODbL-1.0 (値は `ODbL-1.0/` と末尾に / が付く) | 44 | 11.0% | 約 1,060 |
| CC0-1.0 | 10 | 2.5% | 約 240 |
| CC-BY-NC-SA-4.0 (非商用) | 3 | 0.8% | 約 70 |
| `https://example.org/license/unknown` (不明) | 1 | 0.3% | 約 25 |

ただし RDL の license 欄は元の配布元のライセンスと一致しない。HDX 由来の標本から 150 件を無作為に選び、HDX の
CKAN API (`https://data.humdata.org/api/3/action/package_show?id=<name>`、HDX が公開している API) で元の
`license_id` を引いて突き合わせた (146 件取得、4 件は HDX 側で 404)。

| RDL の欄 | HDX の元のライセンス | 件数 |
|---|---|---|
| CC-BY-4.0 | cc-by | 50 |
| CC-BY-4.0 | hdx-other (自由記述) | 47 |
| CC-BY-4.0 | cc-by-igo | 17 |
| ODbL-1.0/ | hdx-odc-odbl、odc-odbl | 16 |
| CC-BY-SA-4.0 | cc-by-sa | 11 |
| CC0-1.0 | other-pd-nr (パブリックドメイン) | 5 |
| CC-BY-4.0 | なし | 4 |

HDX で "Other" (自由記述) の 47 件はすべて RDL で CC-BY-4.0 にされている。自由記述の中身は次のとおりで、
非商用や再配布不可のものが混じる。

| 作成者 | 件数 | 自由記述の中身 | 判定 |
|---|---|---|---|
| WorldPop | 22 | WorldPop licence (hub.worldpop.org/data/licence.txt) | CC BY 4.0 相当 |
| HeiGIT | 6 | "Non-commercial use only. Contains derivatives of PlanetScope imagery." | 非商用・再配布は Planet の条件 |
| UNDRR (GAR 2015) | 5 | 非商用目的に限り無償 | 非商用 |
| HDX HAPI | 4 | resource ごとに複数のライセンス | 不明 |
| UNOSAT | 2 | CC BY-NC-SA 3.0 | 非商用 |
| IOM | 2 | Copyright IOM 2018、所有権を留保 | 再配布不可 |
| CRED (EM-DAT) と HDX 上の EM-DAT | 2 | EM-DAT の独自規約 (非営利の研究機関向け) | 再配布不可 |
| UNHCR | 1 | Scientific Use License | 再配布不可 |
| OCHA (Liberia、Iraq、Nigeria) | 3 | HDX の旧規約 (legacy hrinfo) を参照 | 不明 |

まとめると HDX 由来 146 件のうち、自由に再配布できる (CC BY、CC BY-SA、ODbL、PD、WorldPop) ものが約 104 件 (71%)、
CC BY-IGO が 17 件 (12%、帰属表示のみだが国際機関向けの紛争条項付き)、非商用・再配布不可が 18 件 (12%)、
不明が 11 件 (8%)。RDL の license 欄が非商用を示したのは標本 400 件中 3 件だけなので、欄を信じると非商用を
約 4 倍見落とす。

### 形式 (標本 400 件の resource 4,060 個、実測)

| media_type | 件数 |
|---|---|
| image/tiff;application=geotiff | 2,096 |
| application/zip | 1,006 |
| text/csv | 180 |
| application/geo+json | 168 |
| (なし) | 149 |
| xlsx | 125 |
| KML | 105 |
| application/vnd.shp | 90 |
| GeoPackage | 47 |
| image/png (多くは WMS GetMap) | 32 |
| GML、JSON、PDF、Parquet、NetCDF、GRIB2 ほか | 60 未満 |

GeoTIFF の大半は WorldPop である。

### 大きさ

目録に大きさがないので 2 通りで測った。どちらも推定で、誤差は大きい。

1. HEAD と Range (実測は resource 単位)。標本 400 件の resource 4,060 個から一様無作為に 250 個を選んで問い合わせ、
   214 個の大きさが取れた。平均 510 MB、中央値 5.3 MB、最大 45.4 GB、平均の標準誤差 294 MB。
   取れた 214 個の合計 109 GB のうち 108.6 GB が WorldPop (169 個) で、インドの 100m 年齢性別 zip 2 本
   (`ind_agesex_structures_2025_CN_100m_R2025A_v1.zip` 45.35 GB、同 2018 年 43.74 GB) だけで 89 GB を占める。
   全体の download_url 付き resource は約 9,665 × 9.40 = 約 90,800 個なので、単純に掛けると約 46 TB。
   ただし標準誤差から見て 95% 区間はほぼ 0〜100 TB で、数値としては「数十 TB、WorldPop が大半」以上のことは言えない。
2. HDX のメタデータの `size` (HDX が記録している大きさ)。HDX 由来 146 件のうち全 resource に size があるもので、
   WorldPop 22 件の 1 データセットあたり平均 12.1 GB (0〜164 GB)、WorldPop 以外 108 件の平均 51.6 MB、
   中央値 3.2 MB、最大 0.82 GB。
   - WorldPop は全体の約 13% (標本 52/400、全件では約 1,175〜1,256 件) なので約 15 TB。
   - WorldPop 以外の HDX 由来 (約 6,800 件) は約 0.35 TB。
   - HDX 以外の 1,368 件 (NISMOD、STAC、各国 GeoNode など) は測っていない (unknown)。GeoNode の多くは WMS/WFS で、
     ファイルとしての大きさがない。

まとめると、全体は 15〜50 TB の桁で 95% 以上が WorldPop の再掲。WorldPop を除くと HDX 由来で約 0.35 TB と見積もる。

## 5. 再配布できる部分

- RDL のメタデータそのもの (9,665 件、108 MB): ライセンス表示がない。RDLS の文書は CC BY-SA 4.0、リポジトリの
  LICENSE は JKAN ソフトウェアの MIT で、記録に何が適用されるかは書かれていない。説明文の多くは HDX の写し。
  再配布する前に GFDRR (連絡先は目録のフッタ) に確認が要る。
- データ本体: RDL は何も許諾していない。元の配布元のライセンスに従う。RDL の license 欄は使えない (前節)。
  - CC BY / CC0 / ODbL / CC BY-SA と確かめられるもの: HDX 由来の約 71%。WorldPop を除いた HDX 由来では
    約 0.35 TB × 7 割前後で、0.2〜0.3 TB と見積もる (件数比で按分しただけで、大きさの偏りは見ていない)。
  - WorldPop (CC BY 4.0、約 15 TB 以上): 再配布はできるが、RDL を経由する理由がない。
  - ODbL のもの (HOT export、HeiGIT、Kontur): OSM の派生物で、同じ ODbL での再配布が条件。
  - CC BY-IGO (IDMC、REACH、UNHCR の一部、OCHA Pacific): 帰属表示で再配布できるが、CC BY 4.0 と同じではない
    (仲裁条項付き)。分けて扱うのが無難。
  - 再配布しないもの: UNOSAT の一部 (CC BY-NC-SA 3.0)、HeiGIT の PlanetScope 派生 (非商用)、UNDRR GAR 2015 (非商用)、
    EM-DAT (独自規約)、IOM の一部 (著作権留保)、UNHCR (Scientific Use License)、CC-BY-NC-SA-4.0 と記された記録。
  - 不明: HDX HAPI (resource ごと)、OCHA の旧規約、ライセンスなし。
- UNOSAT は記録数が最多 (約 1,393 件) だが、HDX 上のライセンスがデータセットごとに CC BY-SA、Other (NC-SA 3.0) などに
  分かれる。1 件ずつ HDX で確かめる必要がある。

## 6. 更新のしかた

- RDL の目録: git の中で JSON をその場で書き換える。版番号付きのリリースはない。2024-09 に `_datasets/json` を丸ごと
  消して戻し、2026-06-15 には削除してから全件入れ直している。`_datasets/json` への最後のコミットは 2026-06-17
  ("Fix hazard type mapping and some licenses") で、それ以降は記録が増えていない。過去の状態は git の履歴でしか残らない。
- 記録の `version` はほとんど空 (標本 400 件中 381 件が空)。その代わり、同じ系列の年や日付ごとに別の記録を作る
  (標本の 324 件で ID が `_2019` や `_20260101` のような年・日付で終わる)。
- 元の HDX: CKAN のデータセットを上書きする。標本の HDX の `metadata_modified` には 2026-09〜10 のものがあり、RDL の
  取り込み (2026-06) より新しい。RDL の記録は元とずれていく。
- WorldPop: 配布パスに版が入る (`R2025A/.../v1/`)。古い系列 (`Global_2000_2020`) と新しい系列 (`Global_2015_2030/R2025A`)
  が両方載っている。
- HOT export: `export.hotosm.org/downloads/...` は期限付きで、標本の 2 件は 404 だった。

## 7. すでに集めているものとの重なり

- WorldPop: 記録の約 12〜13%、resource の 67%、大きさの 95% 以上。直接 WorldPop から取るほうがよい。
- HDX: 記録の約 86%。HDX を集めているなら、RDL は HDX の一部に RDLS の分類 (要素、ハザード種別) を付けた索引にすぎない。
- GHSL: ID に `copernicus` を含む約 472 件の多くは HDX に載った GHSL の国別切り出し (標本で CC BY)。
- OSM: HOT export (約 723)、HeiGIT (約 350)、Kontur (約 328) は OSM の派生物。
- Meta Data for Good (約 203): 人口格子などの HDX 掲載分。
- World Bank WDI: 目立つ重なりは見つからなかった。世界銀行のものは JKAN 側では GFDRR のハザード 9 件程度で、
  Data Catalog の RDL コレクションの中身は確かめられていない (429)。

## 8. 選択肢

決めずに並べる。

| 案 | 内容 | 大きさ |
|---|---|---|
| A | RDL のメタデータだけを Parquet にして公開する。GitHub の `_datasets/json` を取る取得スクリプトと、HDX の `package_show` で元のライセンスを引き直した列を付ける | 約 108 MB (圧縮後はもっと小さい)。ただし記録のライセンスを GFDRR に確かめてから |
| B | A に加え、元のライセンスが CC BY / CC0 / ODbL / CC BY-SA と確かめられた HDX 由来のファイルを WorldPop を除いて集める | 0.2〜0.3 TB と推定 (未実測) |
| C | B に CC BY-IGO を別の構成として足す | B より 1 割前後増える見込み |
| D | WorldPop を含めて全部集める | 15〜50 TB の桁。WorldPop は元から取るほうが筋がよく、RDL 経由の意味が薄い |
| E | 集めない。RDL は分類付きの索引として参照するだけにし、必要な系列は元 (HDX、WorldPop、UNOSAT、FEWS NET) から取る | 0 |

補足:

- どの案でも、RDL の license 欄を再配布の根拠にしてはいけない。HDX の元のライセンスを引き直すのが前提になる。
- 世界銀行 Data Catalog の RDL コレクションは今回数えられなかった。API は文書化されているので、429 が解けてから
  `DatasetList` か `Search` で数え直す余地がある。
- 標本と問い合わせの結果は作業用の一時ディレクトリにだけ置いた。数え直す場合は、同じ乱数種 (データセット 400 件は
  `random.seed(20261006)`、resource 250 個は `random.seed(7)`、HDX 150 件は `random.seed(11)`) で再現できる。
