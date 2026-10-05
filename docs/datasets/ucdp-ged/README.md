# UCDP GED (Georeferenced Event Dataset) 25.1

2026-10-02 に読んで確かめた内容。大きさと Last-Modified は HEAD と `curl -r 0-1023` の応答、件数と列は yuisekin-z にある複製 `/sata_hdd_24tb/www/html/static/ucdp/GEDEvent_v25_1.csv` を DuckDB 1.5.5 (`read_csv(..., sample_size = -1)`) で数えた値、列の意味は codebook 25.1 (`https://ucdp.uu.se/downloads/ged/ged251.pdf`、52 ページ) から。分布の一部は [z-yuiseki-static/ucdp.md](../z-yuiseki-static/ucdp.md) (2026-09-28 に数えたもの) から引いた。

- 作成はスウェーデンのウプサラ大学 平和・紛争研究学部の Uppsala Conflict Data Program (UCDP)。codebook の表紙に「The current version of the dataset is 25.1」「Data extracted from UCDP systems on 2025-03-19」「This version compiled and updated by Stina Högbladh (2025)」とある。
- 組織的暴力の出来事 1 件を 1 行とし、場所 (村や町の単位まで)、日付 (日の単位まで)、死者数の推定 (best、high、low) を持つ。codebook の出来事の定義は「An incident where armed force was used by an organized actor against another organized actor, or against civilians, resulting in at least 1 direct death at a specific location and a specific date」。
- 期間は 1989-01-01 から 2024-12-31 (codebook の「GED 25.1 is a global dataset that covers the world between 1989-01-01 and 2024-12-31.」と、実データの `date_start` の最古と `date_end` の最新が一致)。
- 情報源は通信社の報道、BBC Monitoring による各地報道の翻訳、地元メディアや NGO の報告など。人手で整理し、取得と絞り込みに自動化を併用している (codebook 第 4 章)。
- 配布は `https://ucdp.uu.se/downloads/ged/ged251-csv.zip`。25.1 はいまは旧版のページ `https://ucdp.uu.se/downloads/olddw.html` の「GED 25.1:」に載っている。現行の `https://ucdp.uu.se/downloads/` は 26.1 を載せている。
- 公式の公開日は書かれていない (未確認)。サーバの Last-Modified は zip が 2025-06-11 09:43:52 GMT、codebook が 2025-06-18 08:54:31 GMT、zip の中の CSV の時刻は 2025-03-31 23:15。

## ライセンス

現行のダウンロードページ `https://ucdp.uu.se/downloads/` (2026-10-02 に取得、26.1 を載せている) の冒頭。原文は 2 つ目の文の途中をダッシュでつないでいる。ここではその位置で引用を分けた。

> This page provides free downloads of all current UCDP datasets. Each entry includes a codebook and, where available, a version history. All datasets are free of charge and licensed under CC BY 4.0

> you are free to use and redistribute them provided you cite the relevant publications listed with each dataset.

「CC BY 4.0」は `https://creativecommons.org/licenses/by/4.0/` へのリンク。

25.1 が現行だった時期の同じページ (Wayback の 20250722052538 と 20251118170945) のフッター。

> Except where otherwise noted, content on this site is licensed under a Creative Commons Attribution 4.0 International license (CC BY 4.0)

ほかの場所。

- codebook 25.1 には "licen"、"Creative"、"CC BY"、"commercial"、"redistribut" のどの語も無い。あるのは「All formats are available for download free of charge (no registration required)」と引用の依頼だけ。
- zip と CSV の中にもライセンスの記載は無い。
- 旧版ページ `https://ucdp.uu.se/downloads/olddw.html` にもライセンスの文言は無く、「For current versions of all UCDP datasets as well as citation information, please visit the UCDP Dataset Download Center.」とだけある。

読み取れること。

- ライセンスは CC BY 4.0。ShareAlike も NonCommercial も付いていない。再配布、変換したものの再配布、商用利用は CC BY 4.0 の範囲で認められる。継承は求められない。
- 表示が要る。作成者 (UCDP, Uppsala University)、ライセンス名とその URL、元データへのリンク、改変したならその旨。
- 論文の引用が求められている。現行ページは再配布を「provided you cite the relevant publications」と条件づけている。

codebook 25.1 の表紙が求める引用。

> When using this data, please always cite:
> Sundberg, Ralph, and Erik Melander, 2013, "Introducing the UCDP Georeferenced Event Dataset", Journal of Peace Research, vol.50, no.4, 523-532
> When appropriate, also cite this codebook: Högbladh Stina, 2025, "UCDP GED Codebook version 25.1", Department of Peace and Conflict Research, Uppsala University
> Always include the Version number in analyses using the dataset.

25.1 が現行だった時期のダウンロードページ (上と同じ Wayback の 2 時点) の GED の欄「Please cite:」。

> • Davies, S., Pettersson, T., Sollenberg, M., & Öberg, M. (2025). Organized violence 1989–2024, and the challenges of identifying civilian victims. Journal of Peace Research, 62(4).
> • Sundberg, Ralph and Erik Melander (2013) Introducing the UCDP Georeferenced Event Dataset. Journal of Peace Research 50(4).
> • UCDP is part of and funded by DEMSCORE, national research infrastructure grant 2021-00162 from the Swedish Research Council.

DOI は Sundberg と Melander (2013) が 10.1177/0022343313484347、Davies ほか (2025) が 10.1177/00223433251345636 (Crossref で確認)。現行ページの 26.1 の欄は別の論文 (Davies, Pettersson, Öberg 2026) を挙げているが、25.1 に対応するのは上の 2025 年の論文。

未確認のこと。

- 25.1 が出た時点で、データセットそのものが CC BY 4.0 だと明言されていたか。当時の明記はサイト全体のフッター「content on this site」だけ。データセット単位の文言は現行ページにしか無く、それも「all current UCDP datasets」と書いていて、旧版になった 25.1 を名指ししていない。
- 論文の引用を再配布の条件とする書き方が、CC BY 4.0 の表示の方法の指定 (「in any reasonable manner requested by the Licensor」) に収まるのか、追加の条件に当たるのか。引用を併記すれば両方を満たす。
- `source_article` と `source_headline` には報道記事の見出しが入っている。codebook 5.3 は「The full texts of these sources are often copyrighted to news agencies/publishers.」と書く。入っているのは全文でなく見出しと媒体名と日付だが、見出しが CC BY の対象外になりうるかは分からない。
- API (`https://ucdp.uu.se/apidocs/`) はアクセストークンが要る。その利用規約は読んでいない。
- UCDP に問い合わせはしていない。

## 中身

zip の中は `GEDEvent_v25_1.csv` が 1 つ。UTF-8 のカンマ区切りで、見出し行がある。値に `;` で区切った複数の値と `"` の引用が入る。

- 385,918 行。`id` と `relid` はどちらも 385,918 通りで重複が無い。
- 列は 49 個 (列名と中身の分け方は [z-yuiseki-static/ucdp.md](../z-yuiseki-static/ucdp.md) にもある)。
  - 識別: `id`, `relid`, `year`, `active_year`, `code_status`
  - 暴力の種類: `type_of_violence`。codebook では 1 が state-based conflict、2 が non-state conflict、3 が one-sided violence
  - 紛争と当事者: `conflict_dset_id`, `conflict_new_id`, `conflict_name`, `dyad_dset_id`, `dyad_new_id`, `dyad_name`, `side_a_dset_id`, `side_a_new_id`, `side_a`, `side_b_dset_id`, `side_b_new_id`, `side_b`
  - 出典: `number_of_sources`, `source_article`, `source_office`, `source_date`, `source_headline`, `source_original`
  - 場所: `where_prec`, `where_coordinates`, `where_description`, `adm_1`, `adm_2`, `latitude`, `longitude`, `geom_wkt` (`POINT (経度 緯度)`), `priogrid_gid`, `country`, `country_id`, `region`
  - 時間: `event_clarity`, `date_prec`, `date_start`, `date_end`
  - 死者数: `deaths_a`, `deaths_b`, `deaths_civilians`, `deaths_unknown`, `best`, `high`, `low`
  - 国コード: `gwnoa`, `gwnob`
- `year` は 1989 から 2024。`code_status` は全行が `Clear`。`active_year` は真が 373,463 行、偽が 12,455 行。
- 緯度経度の欠損は 0 行。国は 124 通り、紛争 (`conflict_new_id`) は 1,531 通り (この 2 つは既存メモの値)。
- `best` の合計は 3,957,143、`low` の合計は 3,294,758、`high` の合計は 5,833,924。`best` の最大は 121,848 で、Ethiopia: Government の 2022-08-24 から 2022-10-24 までの 1 行。
- `best` は全行で `deaths_a + deaths_b + deaths_civilians + deaths_unknown` に等しい。

`type_of_violence` の分布 (既存メモの値)。

| 値 | 意味 (codebook) | 行数 | `best` の合計 |
|---|---|---:|---:|
| 1 | state-based conflict | 271,331 | 2,373,140 |
| 2 | non-state conflict | 54,982 | 390,988 |
| 3 | one-sided violence | 59,605 | 1,193,015 |

近年の行数。2012 年に 18,540 行へ跳ねてから多い。

| 年 | 行数 |
|---|---:|
| 2020 | 13,432 |
| 2021 | 17,254 |
| 2022 | 20,774 |
| 2023 | 26,486 |
| 2024 | 28,816 |

位置の精度 `where_prec` は 1 から 7。codebook では 1 が正確な地点、2 が既知の地点から半径約 25km 以内、3 が第 2 階層の行政区画の代表点、4 が第 1 階層の代表点、5 が川や国境のような線や境界のはっきりしない範囲の代表点、6 が国しか分からない、7 が公海や国際空域。分布は 1 が 179,745、2 が 92,676、3 が 55,381、4 が 36,336、5 が 16,648、6 が 4,881、7 が 251 (既存メモの値)。4 以上は 58,116 行。

日付の精度 `date_prec` は 1 から 5。1 が日付まで分かる、2 が 2〜6 日の幅、3 が週、4 が 8〜30 日の幅か月、5 が 1 か月を超え 1 年以内。`date_start` と `date_end` が違う行は 57,245。

## 気をつけること

`source_headline` は古い行で空。 `source_headline`、`source_office`、`source_date` が空の行は 97,913 で、そのうち 97,912 行は `source_article` に値がある。この 97,913 行は `number_of_sources` が `-1` の行とちょうど同じ数。年で見ると 1989 年から 2013 年に集中していて (2012 年は 18,540 行中 6,585、2013 年は 24,521 行中 2,470)、2014 年以降は年に 0 から 3 行しか無い。codebook は、これらの列は 2014 年以降の収集分、2013 年の大半、改訂された出来事にしか無く、古いデータでは空、`number_of_sources` は `-1` になると書き、「-1 does NOT mean information on the source is missing」としている。古い行の出典は `source_article` の自由記述 (`Reuters 18 Jan 1989 "KABUL REPORTS ..."` のような形、R や AFP などの略記あり) にしか無い。見出しを特徴量にすると、年と強く結びついた欠損になる。

見出しがその出来事の記事とは限らない。 `source_article` と `source_headline` は出来事 1 件に複数の記事を `;` で並べる。ファイル先頭の行 (id 244657) は 2017-07-31 のカブールのイラク大使館への攻撃 (死者 6) だが、並ぶ見出しの 2 つはヘラートのモスク攻撃の記事だった。1 本の記事が複数の出来事を扱うことがあり、見出しの文面だけでは出来事を特定できない。`source_article` の最長は 29,230 文字。

DuckDB の既定の型推定では読めない。 既定の `read_csv` は `gwnoa` を BIGINT と推定し、138,884 行目 (id 122098、`gwnoa` が `2;200;900`) で Conversion Error になって止まる。`sample_size = -1` で全行から推定すると `gwnoa` は VARCHAR になる。`2;200;900` の行は 95 で、どれもオーストラリア・英国・米国の政府が side_a の Iraq の行だった。`gwnob` は逆に、既定の推定では VARCHAR、全行から推定すると BIGINT (値がある行は 30,256)。型は全行で推定するか、明示する。

`low <= best <= high` が成り立たない行がある。 4,967 行。`best < low` が 1,415、`best > high` が 3,594、`low > high` が 3,394。codebook は event_clarity が 2 の出来事について、中から特定できた個別の出来事の死者を差し引くため「the ‘high estimate’ may at times be lower than the ‘best’ or ‘low’ estimate」と書く。ただし実際は event_clarity が 1 の行も 2,637 行あり、2 の行は 2,330 だった。clarity 1 の側の説明は codebook に見つけていない (未確認)。区間として使うなら先に検査する。

`best` は裾が長い。 最大 121,848 は 2 か月にわたる 1 行。`best` が 0 の行は 30,021 (既存メモの値)。回帰の目的変数にするなら対数などで変換する。

位置と日付の精度が行ごとに違う。 `where_prec` が 4 以上の 58,116 行は州や国の代表点で、点の位置に意味が無い。`date_prec` が大きい行は期間の幅を持つ。空間や時間で集計する前に精度で絞る。

25.1 は旧版。 2026-10-02 の時点で現行は 26.1 (`https://ucdp.uu.se/downloads/ged/ged261-csv.zip`、39,122,522 バイト、Last-Modified 2026-06-08 19:54:24 GMT)。現行ページには月ごとの候補版 (`downloads/candidateged/GEDEvent_v26_0_7.csv` など) も並ぶ。codebook は分析に版番号を必ず書くよう求めている。26.1 は 417,968 行、期間は 1989-01-01 から 2025-12-31 で、25.1 より 32,050 行多く 1 年長い。列は 49 で、名前も並びも 25.1 と同じ (2026-10-02 に見出し行を比べた)。値の型や意味が変わったかは確かめていない (未確認)。codebook 26.1 には「5.8. Variables present in previous versions of GED not used in version 26.1」という節がある。

題材の性質。 紛争の死者、加害者と被害者の区分、村の単位の位置を含む。個人名の列は無い (列名からの判断で、値の中の人名は未確認)。

年で行数が大きく変わり、同じ紛争の行がたくさんある。 無作為に分けると、同じ紛争や近い日付の行が学習と検証にまたがる。時間か紛争で分ける。

## 取り出し方

区分は whole。2026-10-02 に実測した。

| 要求した URL | 応答 | 全体の大きさ | Last-Modified (GMT) |
|---|---|---:|---|
| `https://ucdp.uu.se/downloads/ged/ged251-csv.zip` | `-r 0-1023` に 206、`Accept-Ranges: bytes` | 29,307,888 | 2025-06-11 09:43:52 |
| `https://z.yuiseki.net/static/ucdp/ged251-csv.zip` | `-r 0-1023` に 206、`cf-cache-status: HIT` | 29,307,888 | 2025-06-11 09:43:52 |
| `https://z.yuiseki.net/static/ucdp/GEDEvent_v25_1.csv` | `-r 0-1023` に 206 | 250,393,383 | 2025-03-31 14:15:16 |

- Range 要求は通るが、必要な行だけを選ぶ手段にならない。zip の中身は deflate された CSV 1 本 (250,393,383 バイトを 29,307,682 バイトに圧縮) で、目録は末尾にあり、行や地域や年の索引は無い。z.yuiseki.net の展開済み CSV も索引の無い 1 本で、先頭の見出しを読む以上のことはできない。
- 分割されたファイルも無い。25.1 の形式は旧版ページに CSV の zip、Stata (`ged251-dta.zip`、44,003,039 バイト)、R (`ged251-rds.zip`、31,072,041 バイト)、Excel (`ged251-xlsx.zip`、102,661,468 バイト) の 4 つが並ぶが、どれも全体を 1 つにしたもの。最小の単位は CSV の zip の 29.3MB。
- 小さいので丸ごと落とせばよい。正本から 1KB の Range に 4.4 秒、z.yuiseki.net からは 0.05 秒だった。
- API (`https://ucdp.uu.se/apidocs/`) で絞って引けるかもしれないが、アクセストークンが要り、試していない (未確認)。

## z.yuiseki.net の複製

`https://z.yuiseki.net/static/ucdp/` に `ged251-csv.zip` と、それを展開した `GEDEvent_v25_1.csv` がある。置き場は yuisekin-z の `/sata_hdd_24tb/www/html/static/ucdp/`。詳しくは [z-yuiseki-static/ucdp.md](../z-yuiseki-static/ucdp.md)。

- zip は正本、手元、公開 URL の 3 つで大きさ (29,307,888 バイト) と Last-Modified (2025-06-11 09:43:52 GMT) が一致する。手元の zip の sha256 は `e256f1fb20a579d8b2f910e5bae212f486d3002adaa2e4359ace740c737da05d`。
- UCDP はチェックサムを公開していない。2026-10-02 に正本を丸ごと取り直し、sha256 が手元の zip と一致した (`e256f1fb...`)。バイト単位で同じ。
- 手元の `GEDEvent_v25_1.csv` は zip の中のメンバーと大きさ (250,393,383 バイト)、時刻、CRC-32 (`b9cb2d26`)、sha256 (`3f286de84cc0cb9152403f53e6aea2ac604d623f156e61079338596e09e8b550`) が一致した。zip を展開したものと同じ。単体の CSV は UCDP の配布には無い。

### 26.1

2026-10-02 に 26.1 を取り、25.1 の隣に置いた。

| ファイル | 大きさ (バイト) | Last-Modified | sha256 |
|---|---:|---|---|
| `ged261-csv.zip` | 39,122,522 | 2026-06-08 19:54:24 GMT | `8c941d84954e555ee2e54f40fa04d9203bf1e2f962203d0a9930966c4947c667` |
| `ged261.pdf` (codebook) | 917,038 | 2026-05-20 09:54:52 GMT | `f767380ebbf365aec7586f98b6d100cafb69fb54010a908604d53bd9ad655972` |
| `GEDEvent_v26_1.csv` (zip を展開したもの) | 273,992,720 | 2026-03-30 (zip の中の時刻) | |

- 大きさと Last-Modified は、正本 `https://ucdp.uu.se/downloads/ged/ged261-csv.zip` の応答と一致した。zip は `unzip -t` で壊れていない。中身は `GEDEvent_v26_1.csv` の 1 本で、展開のときに CRC を照合した。
- 公開の日付はページにも codebook にも書かれていない (未確認)。codebook には「Data extracted from UCDP systems on 2026-03-30」とある。
- 26.1 についてダウンロードのページが引用を求めるのは、Davies, Pettersson, Öberg (2026)「Organized violence 1989–2025, and violent political protests」Journal of Peace Research (https://doi.org/10.1093/jopres/xjag046) と Sundberg, Melander (2013)。codebook 26.1 の表紙は Sundberg, Melander (2013) と、場合によって codebook 自体 (Högbladh 2026) の引用を求める。DOI が解決するかは確かめていない (未確認)。
- ライセンスは同じダウンロードのページの CC BY 4.0 (上のライセンスの節の文)。codebook 26.1 の本文にはライセンスの語が無い。

## Hugging Face

<https://huggingface.co/datasets/yuiseki/ucdp-ged> に、版ごとのサブセット (`26.1` から `19.1` までの 8 版) で置いた。19.1 は旧版ページで codebook の付いた最も古い版 (18.1 と 17.1 には codebook のリンクが無い、2026-10-02 に確認)。説明できないデータを配らないため、それより前は置かない。各版の zip と codebook をそのまま置き、型を列名で決めた GeoParquet を添えた。コードは <https://github.com/yuiseki/ucdp-ged>。

- 型は列名で決める。`gwnoa` と `gwnob` は文字列、`active_year` は codebook の定義どおり整数の 1 か 0 (19.1〜24.1 の CSV は 1/0、25.1 と 26.1 の CSV は true/false と書くので 1/0 に読み替える。2026-10-02 の 8 版化の前は 25.1 と 26.1 だけで、真偽値だった)、`date_start` と `date_end` は TIMESTAMP。規則に無い列は文字列として通し、型に合わない値があれば変換を止める。旧版を足すときに列の違いが表に出る。
- 上げる前に DuckDB で確かめた: 行数と id の一意性、全列の型、GeoParquet 1.0.0 と全行の点、ジオメトリによる絞り込みと緯度経度による絞り込みの件数の一致、`best` と `deaths_civilians` の合計と暴力の種類ごとの件数が csv モジュールで数えた値と一致、spatial 拡張なしでも開ける、ブルームフィルタ無し。上げた後に `hf://` から読んで同じ値になった。
- 19.1 だけ違う点: シリアを含まない (codebook「Data for Syria is not included in 19.1 version – a separate release V 652.1601.1911 was released for the period 2016-01-01 to 2019-11-30 on 2019-12-17.」、この別リリースは置いていない)。列は 42 で、`relid`、`code_status`、`conflict_dset_id`、`dyad_dset_id`、`side_a_dset_id`、`side_b_dset_id`、`where_description` が無い。日付に時刻が付かない。20.1〜26.1 は同じ 49 列。
- 版は同じ系列を年で切ったものではない。UCDP は過去の出来事も版ごとに直す。シリアを除いた 2010 年は、19.1 で 6,008 件・死者 30,862、26.1 で 9,139 件・死者 34,898。両方の版にある出来事のうち 1,908 件は `best` が違う。
- 19.1〜24.1 の引用は、各 codebook の表紙が求める Sundberg, Melander (2013) と、場合によって codebook 自体 (Högbladh、各版の年)。旧版ページには版ごとの引用の一覧が無い。
- 26.1 も `best` は全行で 4 つの `deaths_*` の和に等しい。`low <= best <= high` が成り立たない行は 26.1 で 5,075。

## 学習ステップとの対応 (案)

- 1 ロジスティック回帰: 出来事の死者が一定数を超えるかを、種類、地域、年、精度から当てる。
- 2, 3 Random Forest / XGBoost: `type_of_violence` の分類や `best` の回帰。`best` の裾と、`low`、`high` との食い違いを先に扱う。
- 4 Cross Validation とデータリーク: 年で分けるか、紛争 (`conflict_new_id`) でまとめて分けるか。`source_headline` の欠損が年と結びつくこともリークの題材になる。
- 5 k-means / DBSCAN: 緯度経度で出来事のホットスポットを出す。`where_prec` で絞るかどうかで結果が変わる。
- 11 SHAP / calibration: 上の分類モデルの説明と確率の較正。
