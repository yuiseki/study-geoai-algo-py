# 地球地図日本 (Global Map Japan)

2026-10-03 に読んで確かめた内容。ページは curl で取得して読んだ。大きさと Last-Modified は HEAD、ZIP の中身は HTTP Range で各 ZIP の目録 (central directory) だけを読み、属性は第 2.2 版の全レイヤの ZIP から `.dbf` と `.met` を Range で数本だけ取り出して見た。

- 入口: <https://www.gsi.go.jp/kankyochiri/gm_jpn.html> (英語版 <https://www.gsi.go.jp/kankyochiri/gm_japan_e.html>)
- e-Gov データポータル: <https://data.e-gov.go.jp/data/dataset/mlit_20160819_0035> (API は `package_show?id=mlit_20160819_0035`)
- 作成: 国土地理院 (e-Gov のメタデータでは作成者「応用地理部」、公開者「国土交通省」)。国土地理院技術資料 D1-No.576「地球地図日本（第２版）ベクタデータ」。ラスタは D1-No.459「地球地図日本（第1.0版）」と D1-No.464「地球地図日本（第1.1版）」。
- 中身は、縮尺 100 万分の 1 の日本全域の地図。ベクタ 4 レイヤ (行政界、水系、人口集中域、交通) とラスタ 4 種 (標高、土地被覆、土地利用、植生)。
- 版はベクタが第 2 版 (2011 年公開)、第 2.1 版 (2015 年)、第 2.2 版 (2016 年)、ラスタが第 1.0 版 (2000 年)、第 1.1 版 (2006 年)。どれも同じページから取れる。

## 一次配布元と国際的な地球地図の関係

地球地図は、各国の地理空間情報当局が共通の仕様 (Global Map Specifications) で作った 100 万分の 1 の地図で、地球地図国際運営委員会 (ISCGM) が取りまとめていた。国土地理院の地球地図トップページ (<https://www.gsi.go.jp/kankyochiri/globalmap.html>) の説明:

> 2016年8月、第23回地球地図国際運営委員会において、地球地図プロジェクトの目的はほぼ達成されたとの理解のもと、ISCGMの解散と地球地図データの国連地理空間情報課への移管が決議され、20年間に渡る地球地図プロジェクトは完了しました。

> 地球地図国際運営委員会が公開していた地球地図はGlobal Map data archivesで公開されています。
> 地球地図日本及び地球地図全球版のデータについては、国土地理院のウェブサイトより公開します。

- ISCGM の配布物は GitHub の Global Map data archives (<https://globalmaps.github.io/>、組織 <https://github.com/globalmaps>) に移っている。国別版はリポジトリ `gm<国コード><版>` (例 `gmjo10`) に置かれているが、日本は置かれていない。一覧 (<https://github.com/globalmaps/projectmanagement/blob/master/REPOS.md>) の日本の行は `gmjp at [the national site](http://www.gsi.go.jp/kankyochiri/gm_japan_e.html)` で、国土地理院のページを指している。`globalmaps` 組織の 144 リポジトリに `jp` を含む名前は無かった。
- したがって地球地図日本の一次配布元は国土地理院のサイト (`www1.gsi.go.jp/geowww/globalmap-gsi/download/data/gm-japan/`) だけ。e-Gov データポータルの 18 件のリソースも、この URL を直接指している。
- Global Map のメタデータ一覧 (<https://github.com/globalmaps/metadata/blob/master/metadata.csv>) には日本の 3 つの版 (`gmjp20`、`gmjp21`、`gmjp22`) の説明がある。第 2.0 版は 2010 年 4 月 1 日時点の市町村合併に合わせ、100 万分の 1 国際図などから更新したもの。人口は平成 17 年 (2005 年) 国勢調査。
- 地球地図全球版 (標高、土地被覆 GLCNMO、植生) は別のデータで、国土地理院の別ページ (`gm_global.html`) と GitHub の `gm_el_v1` などで配られている。[GEL](../source-coop-smartmaps/gel.md) のズーム 2 から 5 の元データとして挙がっている「地球地図」は、範囲が全球なので全球版の標高と考えられるが、GEL 側の記述では版を特定できない (未確認)。

## 配布ファイル

ページの一覧表と e-Gov のリソースは同じ 18 本。URL は `https://www1.gsi.go.jp/geowww/globalmap-gsi/download/data/gm-japan/<ファイル名>`。

| ファイル | 版 | 中身 | bytes | Last-Modified |
|---|---|---|---:|---|
| `gm-jpn-all_u_2_2.zip` | 2.2 | 全レイヤ (ベクタ) | 9,688,166 | 2023-07-19 |
| `gm-jpn-all_u_2_1.zip` | 2.1 | 全レイヤ (ベクタ) | 8,471,554 | 2015-11-04 |
| `gm-jpn-all_u_2.zip` | 2 | 全レイヤ (ベクタ) | 8,922,182 | 2014-11-12 |
| `gm-jpn-trans_u_2_2.zip` | 2.2 | 交通 | 4,848,845 | 2017-05-01 |
| `gm-jpn-trans_u_2_1.zip` | 2.1 | 交通 | 4,319,472 | 2015-07-31 |
| `gm-jpn-trans_u_2.zip` | 2 | 交通 | 4,175,729 | 2014-11-12 |
| `gm-jpn-bnd_u_2_1.zip` | 2.1 | 行政界 | 3,350,961 | 2015-11-04 |
| `gm-jpn-bnd_u_2.zip` | 2 | 行政界 | 3,530,869 | 2014-11-12 |
| `gm-jpn-hydro_u_2.zip` | 2 | 水系 | 1,128,363 | 2014-11-12 |
| `gm-jpn-pop_u_2.zip` | 2 | 人口集中域 | 89,483 | 2014-11-12 |
| `gm-jpn-el_u_1_1.zip` | 1.1 | 標高 (TIFF) | 485,452 | 2014-11-12 |
| `gm-jpn-el_u_1_0.zip` | 1.0 | 標高 (TIFF) | 461,988 | 2014-11-12 |
| `gm-jpn-lc_u_1_1.zip` | 1.1 | 土地被覆 (TIFF) | 192,967 | 2014-11-12 |
| `gm-jpn-lc_u_1_0.zip` | 1.0 | 土地被覆 (TIFF) | 194,604 | 2014-11-12 |
| `gm-jpn-lu_u_1_1.zip` | 1.1 | 土地利用 (TIFF) | 158,567 | 2014-11-12 |
| `gm-jpn-lu_u_1_0.zip` | 1.0 | 土地利用 (TIFF) | 107,315 | 2014-11-12 |
| `gm-jpn-ve_u_1_1.zip` | 1.1 | 植生 (TIFF) | 242,107 | 2014-11-12 |
| `gm-jpn-ve_u_1_0.zip` | 1.0 | 植生 (TIFF) | 191,396 | 2014-11-12 |

- 合計 50,560,020 バイト (約 51MB)。全部を取っても小さい。
- ページの表記は「Shape (ZIP, 9.2MB)」のような丸めた値。e-Gov の `size` (例 第 2.2 版全レイヤ 8,700,000) は実際の大きさと合わない。
- 第 2.1 版と第 2.2 版は差分の版で、ページの説明は次のとおり。各版の全レイヤ ZIP には、更新の無いレイヤも含めて全部が入っている。

> 地球地図第2.1版は、地球地図第2版のうち、境界及び交通のうち空港のみを時点修正（2015年1月1日現在）したものです（2015年7月31日公開）。
> 地球地図第2.2版は、地球地図第2.1版のうち、交通のうち道路・鉄道・鉄道駅を時点修正（2016年3月26日現在）したものです（2016年3月31日公開）。

- ほかに閲覧ソフト `Global_Map_Viewer_Ver.2.zip` (技術資料 D1-No.598) が同じページにある。

### 公開後の置き換え

Last-Modified と ZIP 内の日付から、公開後に中身が置き換わったものがある。

- `gm-jpn-all_u_2_2.zip` (2023-07-19): 中の `polbnda_jpn.dbf` だけが 2023-07-19 付け。`gm-jpn-bnd_u_2_1.zip` の同じファイルと比べると 2,914 行中 5 行が違い、北海道の松前町 (`Masaki Cho` から `Matsumae Cho`)、愛媛県の松前町 (`Matsumae Cho` から `Masaki Cho`)、市町村コード 06024 の行 (`Akita Ken / Higashinaruse Mura` から `Yamagata Ken / Sakata Shi`) が直っている。`.shp` は同じ (CRC 一致)。`gm-jpn-bnd_u_2_1.zip` と `gm-jpn-all_u_2_1.zip` は直っていない。
- `gm-jpn-trans_u_2_2.zip` (2017-05-01): 中の `roadl_jpn.*` が 2017-04-28 付け。投影情報 (`.prj`) が ITRF94 から JGD2000 の表記に変わっている。置き換え前のファイルは取れない。
- e-Gov のメタデータは 2023-03-13 が最終更新で、この置き換えを反映していない。

## 中身

### 共通

- 縮尺は 100 万分の 1 (`.met` の `denominator` が 1000000)。
- 範囲は東経 122 度から 154 度、北緯 20 度から 46 度 (`.met` の bounding box)。
- 座標は経緯度。`.met` の測地系は ITRF94 (GRS80)。`.prj` は大半が `GCS_ITRF_1994`、第 2.2 版の `roadl_jpn.prj` だけ `JGD2000`。国土地理院の FAQ (<https://www.gsi.go.jp/kankyochiri/gm_faq.html>) は「地球地図データの精度や縮尺レベルの場合、WGS84座標系との差はほとんど無い」と書いている。
- メタデータは Global Map Metadata Profile 2.0 の XML (`<レイヤ>_jpn.met`)。言語は英語。
- ベクタは Shapefile。属性の名前は Global Map Specifications の略号 (`f_code`、`nam`、`soc` など)。仕様は <https://github.com/globalmaps/specifications>。

### ベクタ (第 2.2 版の全レイヤ ZIP で確かめた)

| レイヤ | ファイル | 件数 | 主な属性 |
|---|---|---:|---|
| 行政界 | `polbnda_jpn` (面) | 2,914 | `nam` 都道府県、`laa` 市区町村、`pop` 人口、`ypc` 人口の年、`adm_code` 市区町村コード |
| 行政界 | `polbndl_jpn` (線)、`coastl_jpn` (海岸線) | 未確認 | |
| 水系 | `riverl_jpn`、`inwatera_jpn`、`miscl_jpn`、`miscp_jpn` | 未確認 | |
| 人口集中域 | `builtupa_jpn` (面) | 221 | `nam` 名前、`pop`、`ypc` |
| 人口集中域 | `builtupp_jpn` (点) | 1,640 | `nam` 名前、`pop`、`ypc` |
| 交通 | `roadl_jpn` (道路) | 31,642 | `exs`、`rst`、`med`、`rtt`、`loc` などのコード |
| 交通 | `raill_jpn` (鉄道)、`ferryl_jpn`、`portp_jpn` | 未確認 | |
| 交通 | `rstatp_jpn` (駅) | 108 | `nam` 駅名 |
| 交通 | `airp_jpn` (空港) | 92 | `nam`、`iko` (ICAO)、`ita` (IATA) |

- 地名はすべてローマ字。`polbnda_jpn.dbf` は全 2,914 行が ASCII で、日本語の地名は無い。都道府県は `Hokkai Do`、市区町村は `Sapporo Shi` のように行政の種類が分かち書きされる。点と面の人口集中域、駅、空港の `nam` は大文字 (`SAPPORO`)。住所の属性は無い。
- `polbnda_jpn` の `ypc` は 2,900 行が 2014、14 行が 0。市区町村コードは JIS の 5 桁 (`01100` は札幌市)。
- 人口集中域の `pop` は確かめた先頭の行で `-99999999` (欠測)。どれだけの行に値があるかは未確認。

### ラスタ (第 1.1 版)

- ZIP の中は `jpn/<種類>.tif` と `.tfw`、`.aux`、`Read_me.txt`。
- 標高 `el.tif` は 4,199 × 3,600 画素、8 ビット、非圧縮 (15,132,709 バイト)。`.tfw` の画素の大きさは 0.00833333 度 (30 秒)、左上は東経 120.004 度、北緯 49.996 度。土地被覆 `lc.tif` もほぼ同じ大きさ (15,136,309 バイト)。
- 標高の値の意味は確かめていない。ページには「標高については凡例はございません」とあり、ほかのラスタの凡例は Global Map Specifications を見るよう書かれている (未確認)。

## 取り出し方

区分は split。版とレイヤで 18 本に分かれていて、必要な ZIP だけ取れる。いちばん小さいのは人口集中域の 89,483 バイト、いちばん大きいのは第 2.2 版の全レイヤで 9,688,166 バイト。

- `curl -r 0-1023` は 206 を返す (`gm-jpn-pop_u_2.zip` で確かめた)。ZIP の目録はファイルの末尾にあるので、Range で目録を読み、必要な `.dbf` や `.met` だけを取り出せる。第 2.2 版の全レイヤ ZIP の目録は 5,010 バイトの取得で読めた。ただし Shapefile の中は索引が無く地物の部分集合は選べないので、range には入れない。
- 目録は国土地理院のページの HTML と e-Gov の CKAN API。CKAN では版とレイヤを名前で区別できるが、範囲や時刻では絞れない。

## ライセンス

### 国土地理院の規約

地球地図日本のページの本文:

> 本データには、「国土地理院コンテンツ利用規約」が適用されます。

国土地理院コンテンツ利用規約 (<https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html>、令和 7 年 11 月 20 日改正、2026-10-03 に読んだ):

> 本サイトのコンテンツには特段の記載が無い限り公共データ利用規約（第1.0 版）（PDL1.0）が適用されています。

> ア　コンテンツを利用する際は、出典を記載してください。出典の記載方法は以下の例を参考にしてください。
> 　　（出典記載例）
> 　　　出典：国土地理院ウェブサイト　（当該ページのURL）

> イ　コンテンツを編集・加工等して利用する場合は、上記出典とは別に、編集・加工等を行ったことを記載してください。（略）なお、編集・加工した情報を、あたかも国土地理院が作成したかのような態様で公表・利用してはいけません。

地球地図の FAQ (<https://www.gsi.go.jp/kankyochiri/gm_faq.html>、2026-10-03 に読んだ):

> 地球地図日本の場合、商用・非商用に関わらず、出典の記載をお願いしています。詳しくは「国土地理院コンテンツ利用規約」をご覧ください。

同じ FAQ の出典の記載例は `Global Map Japan` と `©　Geospatial Information Authority of Japan`。

- PDL1.0 は [ABR](../abr/README.md) などと同じ規約で、CC BY 4.0 と互換。商用利用も再配布 (Hugging Face に置くこと) もできる。条件は出典の記載と、加工した場合はその旨の記載。
- ラスタ ZIP の `Read_me.txt` も同じ趣旨 ("The data is available at no charge, regardless of the non-profit objectives and commercial use, under the "Geospatial Information Authority of Japan Website Terms of Use"")。

### 測量法の承認

- 国土地理院技術資料の扱いを書いたページ (<https://www.gsi.go.jp/REPORT/TECHNICAL/technical.html>) は、技術資料について「測量法に定める測量成果及び測量記録は含まれません」とし、ウェブサイトに掲載されているものは「国土地理院コンテンツ利用規約に従ってください。商用利用も可能です。」と書く。
- 技術資料リスト-5 (<https://www.gsi.go.jp/REPORT/TECHNICAL/gsigijutsu5.htm>) で、D1-No.459、464、576 (地球地図日本の各版) の「適用利用規約」は「2：国土地理院コンテンツ利用規約」。
- 測量成果の利用手続のページ (<https://www.gsi.go.jp/LAW/2930-index.html>) は「技術資料（デジタル標高地形図等）」を「測量成果に該当しないコンテンツ」に挙げている。
- 以上から、地球地図日本は基本測量成果ではなく、測量法第 29 条・第 30 条の承認申請は要らないと読める。ただし地球地図日本を名指しで「申請不要」とした記述は見つけていない。

### e-Gov のメタデータとの関係

- e-Gov のデータセットの `license_id` は `null`。18 件のリソースそれぞれの `license_id` が `cc-by` で、e-Gov のライセンス一覧での名前は「CC BY」(版の指定なし。一覧には別に `cc-by-4.0` もある)。
- 配布元の規約は PDL1.0 で、CC BY 4.0 と互換なので、条件は食い違わない。ただし e-Gov の `cc-by` が CC BY の何版を指すのかは書かれていない。

### データに埋め込まれた古い利用条件

第 2.2 版の全レイヤ ZIP の `.met` (`trans_jpn.met`、`pop_jpn.met`、`bnd_jpn.met` で確かめた) の `otherConstraints` には、古い条件がそのまま残っている:

> Global Map Japan is subject to copyright law of Japan and copyright protection by an international treaty. Application procedure is required in using the product, except for non-commercial purpose and use in small quantity. Acknowledgement of written sources and report of utilization in an appropriate manner is necessary in using the product. (In case of use in small quantity, acknowledgement of written sources is necessary, but report of utilization is not required.)

- 「非商用で少量の利用を除き申請が要る」という内容で、現在のページ、FAQ、`Read_me.txt` (商用も可、出典の記載のみ) と食い違う。メタデータの日付は 2015 年と 2016 年で、ページと規約のほうが新しい。現在の条件はページの記載 (コンテンツ利用規約) と読むのが自然だが、国土地理院がこの食い違いに触れた記述は見つけていない (未確認)。
- Hugging Face に置くなら、元の ZIP をそのまま置くとこの古い文言も一緒に配ることになる。README で現在の規約を示しておく必要がある。

## 未確認の点

- 地球地図日本を名指しで「測量法の承認申請は不要」とした国土地理院の記述。
- `.met` に残る古い利用条件 (非商用・少量以外は申請が必要) が、現在も何らかの効力を持つか。
- e-Gov の `cc-by` の版。
- 水系、行政界の線、鉄道などのレイヤの件数と属性。人口集中域の `pop` に値がある行の数。
- 標高ラスタの値の意味と、ラスタの凡例。
- 2017 年と 2023 年に置き換えられる前のファイルを取る手段 (ページにも e-Gov にも無い)。今後の更新は、e-Gov の更新頻度が「更新しない」で、ページにも予定の記載は無い。
- [GEL](../source-coop-smartmaps/gel.md) が使った「地球地図」の版。
