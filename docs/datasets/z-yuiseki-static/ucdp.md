# ucdp

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/ucdp/`
- UCDP (Uppsala Conflict Data Program) の GED (Georeferenced Event Dataset) 版 25.1。組織的暴力の出来事 1 件を 1 行とし、場所 (緯度経度) と日付と死者数を持つ。
- 版はファイル名 (`GEDEvent_v25_1`, `ged251`) から。期間は下の実測のとおり 1989 年から 2024 年まで。

## ファイル

| ファイル | 形式 | 大きさ (Content-Length) | Last-Modified |
|---|---|---|---|
| `GEDEvent_v25_1.csv` | CSV | 250,393,383 バイト | 2025-03-31 |
| `ged251-csv.zip` | zip (中に `GEDEvent_v25_1.csv` が 1 つ) | 29,307,888 バイト | 2025-06-11 |

- zip を落として展開した CSV は 250,393,383 バイトで、CSV 単体と同じ大きさ。先頭 64KiB と末尾 64KiB を範囲要求で取って突き合わせ、どちらも一致した。全体の一致までは確かめていない (CSV 単体を丸ごと落としていないため)。
- 同じものなので、使うときは 28MB の zip を落とすほうがよい。

## 中身 (zip 内の CSV を DuckDB 1.5.5 で集計)

- 385,918 行。`id` は 385,918 通りで重複なし。
- 列は 49 個。主なもの:
  - 識別: `id` (整数), `relid` (文字列), `year` (整数), `active_year` (真偽), `code_status`
  - 暴力の種類: `type_of_violence` (整数 1/2/3)
  - 紛争と当事者: `conflict_new_id`, `conflict_name`, `dyad_new_id`, `dyad_name`, `side_a`, `side_b` (と各 `*_dset_id`)
  - 出典: `number_of_sources`, `source_article`, `source_office`, `source_date`, `source_headline`, `source_original`
  - 場所: `where_prec` (位置の精度 1 から 7), `where_coordinates`, `where_description`, `adm_1`, `adm_2`, `latitude`, `longitude` (実数), `geom_wkt`, `priogrid_gid`, `country`, `country_id`, `region`
  - 時間: `event_clarity`, `date_prec` (日付の精度 1 から 5), `date_start`, `date_end` (TIMESTAMP)
  - 死者数: `deaths_a`, `deaths_b`, `deaths_civilians`, `deaths_unknown`, `best`, `high`, `low` (整数)
  - 国コード: `gwnoa` (整数), `gwnob` (文字列。複数国が入るため)
- 期間: `date_start` の最古 1989-01-01、`date_end` の最新 2024-12-31。
- 範囲: 緯度 -37.81 から 68.98、経度 -117.3 から 155.90。緯度経度の欠損は 0 行。国は 124 通り、紛争 (`conflict_new_id`) は 1,531 通り。
- `best` (死者数の最良推定) の合計 3,957,143。最大 121,848。`best` が 0 の行は 30,021。

`type_of_violence` の分布:

| 値 | 行数 | `best` の合計 |
|---|---|---|
| 1 | 271,331 | 2,373,140 |
| 2 | 54,982 | 390,988 |
| 3 | 59,605 | 1,193,015 |

(値の意味はファイルの中に書かれていない。UCDP の codebook では 1 が国家が当事者の紛争、2 が非国家間、3 が一方的暴力のはずだが、今回 codebook は読んでおらず未確認。)

`region` の分布: Middle East 122,215 / Asia 97,879 / Africa 68,354 / Americas 48,884 / Europe 48,586。

国の上位: Syria 87,861 / Afghanistan 42,220 / Ukraine 31,547 / Mexico 21,550 / India 17,997 / Colombia 14,620 / Iraq 9,438 / Bosnia-Herzegovina 9,340 / DR Congo (Zaire) 8,901 / Myanmar (Burma) 8,476。

年ごとの行数は 1989 年 2,624 から 2011 年 7,715 までは数千台、2012 年に 18,540 へ跳ね、2024 年が最多の 28,816。

`where_prec` の分布: 1 が 179,745 / 2 が 92,676 / 3 が 55,381 / 4 が 36,336 / 5 が 16,648 / 6 が 4,881 / 7 が 251。
`date_prec` の分布: 1 が 328,673 / 2 が 43,246 / 3 が 2,475 / 4 が 8,116 / 5 が 3,408。

## 気をつけること

- 位置と日付の精度は行ごとに違う。`where_prec` が大きい行は地点ではなく州や国の代表点の可能性がある。空間の分析では精度で絞る。
- `best` は裾が極端に長い (最大 121,848)。回帰の目的変数にするなら対数変換などが要る。
- 年で行数が大きく変わるので、年をまたいで無作為に分けるとリークになりやすい。時間で分ける。
- ライセンス: 未確認 (ファイルの中にも置き場にもライセンスの記載はない)。

## 12 ステップでの使い道 (案)

- 1 ロジスティック回帰: ある出来事の死者が一定数を超えるかを、種類・地域・年から当てる。
- 2, 3 Random Forest / XGBoost: `type_of_violence` の分類や `best` の回帰。
- 4 Cross Validation とデータリーク: 年での分割と無作為分割の差を見る題材。同じ紛争の行が学習と検証に割れるリークも見られる。
- 5 k-means / DBSCAN: 緯度経度で出来事のホットスポットを出す。
- 11 SHAP / calibration: 上の分類モデルの説明と確率の較正。
