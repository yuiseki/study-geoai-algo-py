# Geo-PKO 2.3 (Geocoded Peacekeeping Operations)

2026-10-02 に読んで確かめた内容。件数と列は yuisekin-z の `/www/html/static/csv/Geo_PKO_v2_3_location_map.csv` を DuckDB 1.5.5 と Python の csv モジュールで読んで数えた値。配布元との照合、ライセンスの所在の調査は同日の来歴調査の結果。codebook は PDF を取得して本文を読んだ。

- 国連平和維持活動 (PKO) の部隊展開を、地点単位で記録したデータセット。1 行は「あるミッションの、ある配置図 (年月) における、ある展開地点」。地点名、座標、部隊の規模と種類、司令部、派遣国 (TCC) などを持つ。
- 作成者は Deniz Cil (University of Maryland)、Hanne Fjelde、Lisa Hultman、Desirée Nilsson (Uppsala University, Department of Peace and Conflict Research)。出典は Dashboard リポジトリの about.md (<https://github.com/geopko/Geo-PKO-Shiny-Dashboard/blob/HEAD/about.md>)。
- 作り方は、国連が公表したミッションの展開配置図 (UN Library 経由で入手、地図番号と改訂番号で参照) を人手で読み取り、地点を座標化したもの。codebook によると座標は既定で National Geospatial-Intelligence Agency から取り、Google Earth、UCDP GED Point Dataset v.1.1、元の配置図で照合している。
- 公開元は Uppsala University の Department of Peace and Conflict Research。正規ページは <https://www.uu.se/en/department/peace-and-conflict-research/research/research-data/geo-pko-dataset>。ページには「The Geo-PKO dataset v 2.3 provides data on UN peacekeeping missions from 1994 to 2024.」「The dataset is current as of December 2024.」とある。
- codebook は「Dataset Version 2.3」「Codebook updated February 2025」(<https://www.uu.se/download/18.74301a071971546b354496ad/1749556887803/Codebook_v.2.3.pdf>、346,424 バイト)。
- 版の履歴は UU ページによると v1.1 (2019、アフリカの国内紛争ミッションのみ)、v2.0 (2020、全世界)、以降は年次で追加。旧版は Lisa Hultman に問い合わせる方式で、ページには置かれていない。
- v2.3 の正式な公開日は書かれていない (未確認)。配布ファイルの HTTP Last-Modified は `Tue, 10 Jun 2025 12:01:27 GMT`。
- 資金は Folke Bernadotte Academy、Knut and Alice Wallenberg Foundation、Smith Richardson Foundation、米国防総省 Minerva Initiative (about.md より)。

## 配布ファイル

UU ページに 2 種類が 3 形式ずつ並ぶ。大きさはページの表示。

| 種類 | ファイル | 表示サイズ |
|---|---|---|
| location-map | `Geo_PKO_v.2.3_location_map.csv` / `.rds` / `.xlsx` | 12 MB / 349 kB / 8 MB |
| location-month | `Geo_PKO_v.2.3_location_month.csv` / `.rds` / `.xlsx` | 46 MB / 816 kB / 31 MB |

- location-map は UU ページの言葉で「the original dataset described in the codebook」。配置図 1 枚ごと、地点ごとの記録で、同じ期間に改訂版があれば改訂版だけを使う。
- location-month は、次の配置図まで展開が続くと仮定して月ごとに展開したもの。こちらは読んでいない。
- location-map の CSV は <https://www.uu.se/download/18.74301a071971546b354496ae/1749556887874/Geo_PKO_v.2.3_location_map.csv>。Content-Length は 12,500,418 バイト。
- 公開元はハッシュを公表していない。

## ライセンス

データ本体のライセンスは、どこにも明示されていない。名前も版も条文も見つからなかった。

2026-10-02 に確かめた場所と結果。

| 場所 | ライセンス表記 |
|---|---|
| UU の Geo-PKO ページ | なし。引用文献の提示と、旧版の問い合わせ先だけ |
| codebook v2.3 の PDF | なし。「licen」「copyright」「cite」「redistribut」「commercial」「terms」で全文を検索して 0 件 |
| UU サイトの About this website (<https://www.uu.se/en/about-website>) | 著作権や再利用の条項なし (アクセシビリティとクッキーだけ) |
| GitHub geopko/Geo-PKO-R | リポジトリの LICENSE は GPL-2.0。v2.0 の CSV (`data/Geo_PKO_v.2.0.csv`) を同梱 |
| GitHub geopko/Geo-PKO-Shiny-Dashboard | リポジトリの LICENSE は GPL-2.0。v2.3 の CSV と XLSX を同梱 |
| Harvard Dataverse で「Geo-PKO」を検索 | 該当 1 件は別論文 (マリの警察) の replication data。Geo-PKO 本体は無い |
| Zenodo で「Geo-PKO」を検索 | 0 件 |
| OSF の検索 API | エラー応答で確かめられず |
| UCDP のダウンロードセンター (<https://ucdp.uu.se/downloads/>) | Geo-PKO の記載なし。UCDP の他のデータのライセンスは Geo-PKO には及ばない |
| JPR の replication data (<https://www.prio.org/journals/jpr/replicationdata>) | Cil, Fjelde and Hultman の zip が載っているが、取得先が Microsoft のログインへ転送され、取れなかった。中身とライセンスは未確認 |
| 論文 (Crossref) | SAGE の標準の再利用権と TDM ライセンス。論文本文のもので、データのライセンスではない |

読み取れること。

- 無変更の再配布、Parquet などに変換したものの再配布、商用利用、継承 (share-alike) のいずれについても、明示の許可も禁止も見つからない。どれも未確認。
- 旧版は問い合わせ制で配っており、自由な再配布を前提にした記述は見当たらない。

### GitHub の GPL-2.0

geopko の 2 つのリポジトリは、どちらも LICENSE が GPL-2.0 の全文で、データファイルを同梱している。ただし、これがデータを覆うのかは分からない。

- リポジトリの説明は「code to this application」「datasets used to produce the Geo-PKO Github pages」で、データの正本は UU ページへ誘導している。GPL がデータにも及ぶと読むことは文言の上では可能だが、作成者の意図は確かめられない。
- GPL がデータに及ぶなら再配布はできるが、ライセンス文の同梱と同じライセンスでの再配布という条件が付く。及ばないなら、手がかりは下の引用の依頼しか残らない。
- しかも Dashboard リポジトリの v2.3 CSV (`data/Geo_PKO_v.2.3_location_map.csv`、12,507,605 バイト、21,278 行、SHA-256 `226cd7a8ea26f4ff970659d86a99c5d5b4098f4e4e253ac8843b8a0822a1184d`、コミット 3ba33e94、2025-05-04「Updating data files for v.2.3」) は UU の配布版と中身が違う。行が 13 多い。z.yuiseki.net にあるのは UU の配布版のほうで、GitHub 版ではない。

### 求められている引用

UU ページと GitHub (Geo-PKO-R の about.Rmd、Dashboard の data.md) に同じ依頼がある。data.md (<https://github.com/geopko/Geo-PKO-Shiny-Dashboard/blob/HEAD/data.md>、2026-10-02 取得) の文言。

> When using the data (including this website), please cite:
> Cil, D., Fjelde, H., Hultman, L., & Nilsson, D. (2020). Mapping blue helmets: Introducing the Geocoded Peacekeeping Operations (Geo-PKO) dataset. Journal of Peace Research, 57(2), 360–370.

DOI は <https://doi.org/10.1177/0022343319871978>。学術的な引用の依頼で、ライセンスの帰属条件として書かれたものではない。

### CC BY-NC-ND という誤った手がかり

Web 検索の要約に「Geo-PKO は CC BY-NC-ND」という趣旨の文が出た。元をたどると、Geo-PKO を使った別の論文 (International Interactions など) の論文のライセンスだった。データのライセンスではない。

### 上流の素材

元になっているのは国連の配置図 (国連の著作物) と NGA の地名の座標。Geo-PKO は地図そのものではなく、地図から読み取った事実の表だが、国連の地図の利用条件がどこまで及ぶかは未確認。

## 中身

- CSV、UTF-8、BOM 付き。12,500,418 バイト。
- 物理的な行数は 21,265 (見出しを含む)。レコードは 21,243 件。差の 21 は `comments` 列の値の中の改行で、21 件のレコードが 2 行にまたがる。行数を `wc -l` で数えると多く出る。
- 列は 114。Python の csv モジュールで数えても、DuckDB の `describe` でも 114 で、全レコードが 114 列だった。列名に重複は無い。
- 完全に同じレコードは無い。`mission`、`source`、`location` の組も重複が無い。
- 期間は `date` の最古が 1994-01-01、最新が 2024-12-01。`date` は月初日で、codebook によると `year` と `month` は配置図の発行の年月。
- 緯度は -25.965278 から 45.81444、経度は -91.51806 から 126.45633。緯度経度の欠損は 0 件、(0, 0) も 0 件。
- ミッションは 52 通り、国 (`country`) は 45 通り、地点名 (`location`) は 1,160 通り、`source` (配置図の番号) は 1,262 通り。ミッションと `source` の組は 1,264 で、これが配置図の枚数に当たる。同じミッションの同じ年月に別の配置図が 2 枚ある例は無かった。

### 列

| 群 | 列 |
|---|---|
| 出典と時間 | `source` (`Map no. 4309 Rev. 1` など), `mission`, `year`, `month`, `date` |
| 場所 | `location`, `geosplit`, `country`, `latitude`, `longitude`, `old_xy`, `geocomment`, `zone.de.confidence`, `adm1.id`, `adm1.name`, `prioid` |
| 部隊の規模 | `battalion`, `company`, `platoon` (実数), `other.size`, `comment.on.unit`, `no.troops` |
| 部隊の種類 | `rpf`, `rpf.no`, `inf`, `inf.no`, `fpu`, `fpu.no`, `res`, `res.no`, `fp`, `fp.no`, `eng`, `sig`, `trans`, `riv`, `he.sup`, `sf`, `med`, `maint`, `recon`, `avia`, `mp`, `demining`, `uav`, `obs.base`, `cantonment`, `disarmament`, `other.type`, `armor`, `he.sup.lw`, `troop.type` |
| 派遣国 | `no.tcc`, `nameoftcc_1` から `nameoftcc_17`, `notroopspertcc_1` から `notroopspertcc_17`, `tcc1` から `tcc17` (3 種類 x 17 で 51 列) |
| その他 | `unpol.dummy`, `unmo.dummy`, `unmo.coding.quality`, `hq`, `lo`, `jmco`, `security.group.dummy`, `comments`, `cow_code`, `gwno` |

### 数の分布

レコードの多いミッション。

| ミッション | 件数 | 最初 | 最後 |
|---|---:|---|---|
| MONUSCO | 1,788 | 2010-07 | 2024-11 |
| MONUC | 1,667 | 1999-11 | 2010-04 |
| UNOCI | 1,624 | 2004-05 | 2017-01 |
| UNIFIL | 1,464 | 1994-01 | 2024-11 |
| UNMIL | 1,260 | 2003-12 | 2018-03 |
| UNAMID | 1,236 | 2008-04 | 2020-10 |
| UNMISS | 1,104 | 2011-10 | 2024-10 |
| MINURSO | 1,054 | 1995-03 | 2024-08 |
| UNFICYP | 992 | 1994-05 | 2024-12 |
| UNISFA | 917 | 2011-10 | 2024-09 |

国では DRC 3,174、Sudan 2,548、Ivory Coast 1,627、Lebanon 1,496、Liberia 1,382 の順。年ごとのレコード数は 1994 年の 286 から 2006 年の 1,110 までばらつき、2016 年以降は 652 から 774 の間にある。

`hq` は codebook によると 0 が司令部でない、1 が TCC の司令部、2 がセクター司令部、3 がミッション司令部で、複数を兼ねるときは高いほうを入れる。件数は 0 が 16,253、1 が 1,336、2 が 2,388、3 が 1,266。`unmo.dummy` (軍事監視員) が 1 のレコードは 5,497、`unpol.dummy` (国連警察) が 1 は 3,592、`inf` (歩兵) が 1 は 13,646。

## 気をつけること

`no.troops` は数えた人数ではなく推定値で、しかも文字列。 codebook は「The estimate is made by multiplying the deployed units coded in "battalion", "company", "platoon", "other" and "comment on unit" with their standard unit size」と書き、標準の人数を大隊 650、中隊 150、小隊 35 としている。実際に値の上位は `150` が 6,118、`0` が 6,033、`35` が 1,712、`650` が 1,271、`300` が 1,094 で、単位の倍数が並ぶ。単位の大きさが配置図に無いときは `unknown` で、537 件ある。数値として読むと 537 件が落ちるか、読み込みが止まる。

`0` 人の地点が 3 割近くある。 `no.troops` が `0` のレコードは 6,033 件。codebook によると部隊の規模の列は軍の部隊だけを数え、軍事監視員、警察、警備、司令部は入らない。6,033 件のうち 3,627 件は `unmo.dummy`、`unpol.dummy`、`hq` のどれかが立っていた。人数を重みにして密度を見ると、こうした地点は消える。

欠損は文字列の `NA`。 `zone.de.confidence` は `NA` が 18,067 件、`geosplit` は `NA` が 3,028 件。DuckDB はこれらの列を文字列として読む。`NA` を欠損として扱うなら、読むときに `nullstr` で指定する。

`zone.de.confidence` は codebook の説明と合わない。 codebook は「This variable is only coded for UNOCI, in all other cases the variable is given as "NA"」と書く。ところが `NA` でないレコード 3,176 件のうち UNOCI は 626 件で、UNDOF (712 件が 1)、UNFICYP、UNOMIG、UNIKOM、UNMEE、UNPROFOR などにも 0 か 1 が入っていた。何を表しているのかは未確認。使うなら UNOCI に絞る。

部隊の数が小数になる行がある。 codebook によると、配置図が「A and B」のように複数の地点をまとめて書いているときは地点を分け (`geosplit` が 1)、部隊の数を等分する。そのため `battalion`、`company`、`platoon` のどれかが小数のレコードが 136 件ある。`geosplit` が 1 のレコードは 138 件。

`country` は当時の国名。 codebook の例では、Juba は南スーダン独立前は Sudan、後は South Sudan。国で集計すると、同じ場所が年で別の国に入る。

1 行は配置図 1 枚の 1 地点で、月ごとではない。 配置図の発行は不定期なので、行の時間間隔はミッションごとにまちまち。月ごとの連続した系列が要るなら、公開元が作った location-month を使うほうが早い (こちらは「次の配置図まで続く」という仮定入り)。

同じ「v2.3」が 2 つある。 UU の配布版と GitHub の Dashboard リポジトリ版はバイト列も行数も違う。ファイル名と版番号だけでは区別できないので、SHA-256 と取得元を控える。

部隊配置の情報だが、対象は 2024 年 12 月までの公開地図に由来する過去のもの。列の構成から見て個人の情報は含まないが、全レコードは点検していない。

## 取り出し方

whole。1 ファイル 12,500,418 バイトの CSV を丸ごと取る。2026-10-02 に実測した。

| 要求した URL | `curl -r 0-1023` の応答 |
|---|---|
| UU の配布 (`.../Geo_PKO_v.2.3_location_map.csv`) | 200。Range を無視して全体 (Content-Length 12,500,418) を返した |
| z.yuiseki.net (`/static/csv/Geo_PKO_v2_3_location_map.csv`) | 206、`content-range: bytes 0-1023/12500418` |

- 配布元は Range を受け付けない。z.yuiseki.net は 206 を返すが、索引の無い CSV なので、範囲で取れるのは先頭の見出しの確認まで。ミッションや年で行を選ぶことはできない。
- 分割も目録も無い。形式違い (rds、xlsx) と、月ごとに展開した location-month があるだけ。
- 12.5MB なので丸ごとで困ることはない。

## z.yuiseki.net の写し

<https://z.yuiseki.net/static/csv/Geo_PKO_v2_3_location_map.csv> に location-map の CSV が 1 つだけある。ディレクトリの説明は [z-yuiseki-static/csv.md](../z-yuiseki-static/csv.md)。

- 実体は yuisekin-z の `/www/html/static/csv/Geo_PKO_v2_3_location_map.csv`。Last-Modified は `Sat, 04 Oct 2025 01:46:37 GMT`。
- 12,500,418 バイト、SHA-256 `1db2da8e691a57db7f8aac671ad6ce6de93741e5a8813add36be35d700b39ff9`、MD5 `924659ee85a3f06f551482df8392eaab`。
- UU の配布版をメモリ上で取得して比べ、バイト単位で一致した (差分 0 バイト、SHA-256 も一致)。最初の 1 回だけ計測側のパイプラインで別のハッシュが出たが、その後の 3 回はすべて上の値に一致した。
- ファイル名は配布の `Geo_PKO_v.2.3_...` から `Geo_PKO_v2_3_...` に変わっている。中身は同じなので、取得後に改名したものと見られる。
- csv.md は列を 122 と書いているが、2026-10-02 に数え直すと 114 だった。行数 21,243 は一致する。

## 学習ステップとの対応 (案)

- 5 k-means / DBSCAN: 展開地点の座標をミッションごとにまとめ、司令部 (`hq`) の配置と比べる。21,243 件の座標は異なり数で 1,160 点しか無く、同じ点が配置図ごとに繰り返し現れるので、地点を先に一意にする。地点名と座標の組では 1,207 通りで、同じ座標に別の地点名が付いた例がある (綴りの揺れか別の場所かは未確認)。
- 1, 2 回帰 / 決定木: 部隊の種類や派遣国の数から `hq` の段階を当てる。`no.troops` は推定値で `unknown` を含むので、目的変数にするなら単位の列から作り直す。
- 4 交差検証とデータリーク: 同じ地点が配置図ごとに繰り返し現れるので、ランダムに分けると同じ地点が学習と検証の両方に入る。ミッションか年でまとめて分ける。
