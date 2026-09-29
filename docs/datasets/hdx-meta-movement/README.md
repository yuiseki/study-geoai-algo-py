# Meta の移動データ (HDX): Movement Range Maps と Movement Distribution

2026-09-29 に読んで確かめた内容。Facebook の位置情報を共有している利用者から、行政区域ごとの 1 日の移動の程度を出したもの。どちらも Humanitarian Data Exchange (HDX) で配られている。

- 公開者: AI for Good at Meta (旧 Data for Good at Meta)。HDX の組織名は `meta`
- ページは人が開く前提で、WebFetch や素の curl には 403 を返す。CKAN の API (`https://data.humdata.org/api/3/action/package_show?id=...`) は User-Agent を付ければ読める。
- ファイルの URL (`/dataset/.../resource/.../download/...`) は、署名付きの S3 の URL (`hdx-production-filestore`、us-east-1) へ 302 で飛ぶ。S3 は初回から 206 を返す。署名は時間で切れるので、URL を保存するなら API の resource URL のほうにする。

| | Movement Range Maps | Movement Distribution |
|---|---|---|
| ページ | <https://data.humdata.org/dataset/movement-range-maps> | <https://data.humdata.org/dataset/movement-distribution> |
| 期間 | 2020-03-01〜2022-05-22 (更新は終了) | 2022-12 から。ただし残るのは直近約 90 日 |
| 更新 | 無し | 2 週間ごと (2026-03 から) |
| ライセンス | CC BY | CC BY |
| 形 | zip の中の TSV 1 本 | CSV (期間ごとに 1 本) |
| 単位 | 行政区域 × 日 | 行政区域 × 日 × 距離の区分 |
| 区域 | GADM (米国は FIPS の郡) | GADM |

## Movement Range Maps

COVID-19 の外出自粛への反応を見るためのデータ。2022-05-22 で更新を止めている。

| ファイル | 大きさ | 中身 |
|---|---:|---|
| `movement-range-data-2020-03-01--2020-12-31.zip` | 56.6MB (展開すると 451MB) | 2020 年分 |
| `movement-range-data-2022-05-22.zip` | 73.1MB (展開すると 599MB) | 2021-01-01〜2022-05-22 |
| `readme.txt` | 961 バイト | 列の説明 |

- 2021〜2022 年分は 6,950,198 行、153 か国。日本は 199,928 行、679 区域 (GADM の level 2、市区町村)。
- 東京都 (`JPN.41`) は 53 区市町村のうち 50 があり、日の出町、檜原村、奥多摩町が無い。23 区はすべてある。
- 名前に長音記号の入る区域は `polygon_name` が文字列の `NA` になっている (台東区 `JPN.41.51_1`、江東区、文京区、中央区、大田区、府中市、八王子市、西東京市、青梅市など)。結合は名前でなく `polygon_id` で行う。
- 列: `ds` (日付)、`country` (ISO 3 文字)、`polygon_source` (GADM か FIPS)、`polygon_id`、`polygon_name`、`all_day_bing_tiles_visited_relative_change` (訪れた Bing タイルの数の、基準からの変化率)、`all_day_ratio_single_tile_users` (1 日中 1 つのタイルから出なかった人の割合)、`baseline_name`、`baseline_type`。
- 基準は 2020 年 2 月 (`full_february`) の曜日ごとの値 (`DAY_OF_WEEK`)。
- zip は deflate なので、行を選んで部分読みはできない。中央ディレクトリは Range で読める (64KB ほど) ので、中身の一覧と先頭行だけなら丸ごと落とさずに見られる。全部を読むと 73MB を流すことになり、この回線で約 2 分だった。

## Movement Distribution

住んでいる場所 (夜にいることが多い場所) から、その日どれだけ離れたかの分布。交通、観光、避難などに使う想定のデータ。

- 1 ファイルは 4 日〜2 週間分。2026-09-29 の時点で 12 本 (2026-06-01〜2026-08-31)、CSV の合計は 0.94GB。これより古い分は HDX から消えている。
- 列: `gadm_id`、`gadm_name`、`country`、`polygon_level`、`home_to_ping_distance_category` (`0`、`(0, 10)`、`[10, 100)`、`100+`、単位は km)、`distance_category_ping_fraction` (その区分の人の割合)、`ds`。
- 2026-07-13〜16 の 4 日分 (48.8MB) で 617,908 行、217 か国、38,751 区域。日本は level 2 の 1,802 区域で、東京都 (`JPN.41`) の 53 区市町村はすべてある。台東区は `JPN.41.51_1` (`Taitō`)。
- 作り方: 1 人につきその日の位置の更新を 1 つ無作為に選び、家からの距離を区分し、少ない区域を落とし、雑音を足す (データセットの methodology の記載)。
- 雑音のため、割合が負になる行がある (日本の 28,740 行のうち 1,593 行)。4 区分の割合の和も 1 にならない (0.43 のものもある)。
- CSV なので、列だけ読むことも行だけ読むこともできない。区域を絞るにも全体を流す必要がある (48.8MB で約 80 秒)。
- 2026-03 に区域の組み直しがあり、それまであった区域の一部が消えた (データセットの注記)。
- 台東区の例 (2026-07-13〜16): 家から動かない (`0`) が 0.35〜0.36、10km 未満が 0.56〜0.57、10〜100km が 0.07、100km 以上が約 0.01。

## ライセンスと扱い

- どちらも HDX の記載は CC BY (Creative Commons Attribution International)。Meta の組織のデータセットには別の条件のもの (`hdx-other`、`other-pd-nr`) もあるので、使うたびにデータセットごとに確かめる。
- 出典は「Data for Good at Meta, Movement Range Maps (または Movement Distribution), HDX」と書く。
- Movement Distribution は直近 90 日しか残らない。時系列として使うなら、取った分を自分で残しておかないと再現できない。CC BY なので、ミラーすることはライセンス上できる。

## 同じ組織の他のデータ

HDX の `meta` には 224 のデータセットがある。ほとんど (約 180) は国ごとの High Resolution Population Density Maps で、日本の分 (`japan-high-resolution-population-density-maps-demographic-estimates`、CC BY) もある。
ほかに Social Connectedness Index、Relative Wealth Index、Commuting Zones、AI-Detected Missing Roads など。中身はまだ見ていない。

## 学習ステップとの対応 (案)

- 5 クラスタリング、6 PCA: 区市町村を、4 区分の割合の組や、曜日ごとの形で型に分ける。
- 1〜3 回帰: 区市町村の人口密度や駅の数から、家から動かない人の割合を予測する。
- 4 Cross Validation: 日付で分けるか、都道府県でまとめて分けるか。
- Movement Range Maps は、2020 年の緊急事態宣言の前後で、変化率がどう動いたかの時系列に使える。
