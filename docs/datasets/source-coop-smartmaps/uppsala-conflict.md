# uppsala-conflict

2026-09-28 に読んで確かめた内容。

- `https://source.coop/smartmaps/uppsala-conflict`
- source.coop 上の題名は「PMTiles of UCDP (Uppsala Conflict Data Program) Georeferenced Event Dataset (GED) Global ver. 23.1」。説明欄は「See https://github.com/optgeo/uppsala-conflict」だけ。リポジトリ内に README.md は無い。
- GitHub の optgeo/uppsala-conflict の README も、元データを UCDP GED Global version 23.1 (<https://ucdp.uu.se/downloads/index.html#ged_global>) としている。同じ README には IPFS の CID (`Qmeguu9vsViuKh5m4rc1zhCsYuzwjMxEwa7YYRvKrgGQ5C`) と、`make world` で作る手順がある。
- 版 23.1 は属性 `year` の範囲 (1989 から 2022) とも合う。
- 版 25.1 の CSV を別の置き場で整理したものが [../z-yuiseki-static/ucdp.md](../z-yuiseki-static/ucdp.md) にある。

## ファイル

| ファイル | 大きさ (バイト) | 更新日時 |
|---|---:|---|
| a.pmtiles | 136,162,985 | 2024-06-29 |

## 中身 (ヘッダとメタデータ)

- PMTiles v3、タイル形式 MVT、タイル圧縮 gzip、clustered。
- ズーム 0 から 12。タイル数 72,181 (addressed = entries = contents)。
- 範囲 (bounds): -117.3, -37.81, 155.90, 68.98 (25.1 の CSV の緯度経度の範囲と同じ)。
- 生成: `tippecanoe v2.28.0`, `tippecanoe --drop-densest-as-needed '--maximum-zoom=12' -f -o a.pmtiles`。低ズームでは点が間引かれている。
- レイヤーは `event` の 1 つ。tilestats の地物数 316,818、ジオメトリは Point。属性 46 個。

属性 (値の範囲は tilestats の min / max):

- 識別: `id` (4 から 468,640), `relid` (Number、0 のみ), `year` (1989 から 2022), `active_year` (0, 1), `code_status` (Clear のみ)
- 種類: `type_of_violence` (1, 2, 3)
- 紛争と当事者: `conflict_new_id`, `conflict_name`, `dyad_new_id`, `dyad_name`, `side_a`, `side_b` と各 `*_dset_id`, `*_new_id`
- 出典: `number_of_sources` (-1 から 361), `source_article`, `source_office`, `source_date`, `source_headline`, `source_original`
- 場所: `where_prec` (1 から 7), `where_coordinates`, `where_description`, `adm_1`, `adm_2`, `priogrid_gid`, `country`, `country_id`, `region` (Africa, Americas, Asia, Europe, Middle East)
- 時間: `event_clarity` (1, 2), `date_prec` (1 から 5), `date_start`, `date_end` (文字列、`1989-01-01 00:00:00.000` の形)
- 死者数: `deaths_a` (最大 14,162), `deaths_b` (最大 9,505), `deaths_civilians` (最大 40,000), `deaths_unknown` (最大 75,340), `best` (最大 75,340), `high` (最大 74,256), `low` (最大 75,482)
- 国コード: `gwnoa`, `gwnob` (どちらも String)
- 緯度経度の列は無い (ジオメトリになっている)。

## 気づいた異常

- `relid` が Number 型で、値が 0 しか無い。25.1 の CSV では `relid` は文字列の識別子なので、タイル化のときに数値として読まれて情報が失われた可能性がある (推測)。
- `high` の最大 (74,256) が `best` の最大 (75,340) や `low` の最大 (75,482) より小さい。最大値どうしは同じ行とは限らないが、low と high が入れ替わっている行があるかもしれない。行ごとの確認はしていない。
- `source_date` に `1753-01-01` がある (SQL Server の datetime の最小値と同じで、欠損の埋め値と見られる)。空文字列もある。
- `number_of_sources` に -1 がある (欠損の符号と見られる)。
- レイヤー名が `event`、メタデータの name が `a.pmtiles`。
- 1 ファイル 1 版で、版が名前に入っていない。今後差し替えられたら区別できない。

## ライセンス

- 未確認 (source.coop のページにも PMTiles のメタデータにも記載が無い)。
- GitHub の optgeo/uppsala-conflict の LICENSE は MIT。これは作成スクリプトの条件で、データの条件ではない。
- GitHub の README は引用文献として Davies, Pettersson & Öberg (2023) と Sundberg & Melander (2013) を挙げている。

## 12 ステップでの使いみち (案)

- 学習には 25.1 の CSV ([../z-yuiseki-static/ucdp.md](../z-yuiseki-static/ucdp.md)) のほうが扱いやすい。こちらは地図表示用で、表として使うには MVT のデコードと、間引かれていない z12 のタイルを全部読む手間が要る。
- 使う場合の題材は 25.1 と同じ: 1 ロジスティック回帰 (死者数が閾値を超えるか)、2, 3 GBDT (`type_of_violence` の分類)、4 年で分ける CV、5 DBSCAN (ホットスポット)、11 SHAP。
- 版の違いを使う題材: 23.1 (2022 年まで) で学習し、25.1 の 2023 年と 2024 年で検証する、時間方向の外挿の練習。ただし 25.1 では過去の行も改訂されうるので、id で突き合わせて差分を確かめてから使う。
