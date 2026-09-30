# Meta のデータ (HDX): Movement Range Maps、Movement Distribution、Commuting Zones、Business Activity Trends

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
- Movement Distribution は直近 90 日しか残らない。時系列として使うなら、取った分を自分で残しておかないと再現できない。CC BY なので、ミラーすることはライセンス上できる。z.yuiseki.net にミラーを置いた (下の「z.yuiseki.net のミラー」)。

## 同じ組織の他のデータ

HDX の `meta` には 224 のデータセットがある。ほとんど (約 180) は国ごとの High Resolution Population Density Maps で、日本の分 (`japan-high-resolution-population-density-maps-demographic-estimates`、CC BY) もある。
ほかに Social Connectedness Index、Relative Wealth Index、Commuting Zones、Business Activity Trends during Crisis、AI-Detected Missing Roads など。Commuting Zones と Business Activity Trends は下で見た。残りの中身はまだ見ていない。

## Commuting Zones

<https://data.humdata.org/dataset/commuting-zones>、CC BY。人の移動のまとまりから求めた通勤圏のポリゴン (2023 年 3 月版、CSV 1 本 16.5MB)。

- 6,541 の通勤圏、215 か国。日本は 54。列は `region`、`fbcz_id`、`name`、`fbcz_id_num`、`cz_gen_ds` (`3/5/23`)、`win_population`、`win_roads_km`、`area`、`country` (英語の国名)、`geography` (WKT、WGS 84)。
- 33 の通勤圏 (Juneau、Zadar、Stanley、長崎など、海岸線の細かいもの) は WKT が 32,759 文字で切れていて、ポリゴンとして読めない。表計算ソフトの 1 セルの上限 (32,767 文字) で切れたものと思われる。ほかに 1 つ (米国の covenant life) が ST_IsValid で false。
- `win_population` は上下が切りそろえてある (winsorize) ように見える。最大値 4,442,659.362 と最小値 1,924.466 に 328 ずつ (5%) が並ぶ。日本では名古屋、大阪、千葉、横浜、さいたまが同じ値。大都市の人口の比較には使えない。

## Business Activity Trends during Crisis

<https://data.humdata.org/dataset/facebook-business-activity-trends-during-crisis>、CC BY。災害の前後で Facebook のビジネスページの活動がどう変わったか。行政区域 × 業種 × 日ごとに、活動が平時の分布のどの分位にあたるか (`activity_quantile`)。

- 災害ごとに CSV 1 本、5 本で 154MB、1,888,011 行。ブラジル南部の洪水 (2024-05〜07)、中東欧の洪水 (2024-09〜10、8 か国)、ハリケーン Beryl (2024-06〜10、14 か国)、Helene (2024-09〜10、米国)、ロサンゼルスの山火事 (2025-01〜03)。
- ファイルによって列が違う。ブラジルのものだけ `polygon_level`、`polygon_version`、`latitude`、`longitude` を持ち、country が 2 文字 (`BR`)。ほかは 3 文字。
- 業種の無い行が、ブラジルでは空、ほかでは文字列の `NA`。`All` とは別の行。
- 米国の 3 本 (Helene、Beryl、ロサンゼルス) には、同じ区域・業種・日の行が 2 つ以上あるものが多く (Helene は 48,764 組)、値が少しずつ違う。どちらが正しいかは分からない。
- 日本は含まない。

## z.yuiseki.net のミラー (2026-09-29)

Movement Distribution、Movement Range Maps、Commuting Zones、Business Activity Trends の 4 つを、元のファイルのままと Parquet の両方で <https://z.yuiseki.net/static/hdx-meta/> に置いた。取得スクリプトは [scripts/mirror_hdx_meta.py](../../../scripts/mirror_hdx_meta.py)、テストは [tests/test_mirror_hdx_meta.py](../../../tests/test_mirror_hdx_meta.py)。置いたものの説明、出典の表示、加工の中身は、置き場の README.md、LICENSE、manifest.json にある。

| Parquet | 行数 | 大きさ | 期間 |
|---|---:|---:|---|
| movement-distribution/movement_distribution_2026.parquet | 11,735,260 | 89.2MB | 2026-06-01〜2026-08-31 |
| movement-range-maps/movement_range_2020.parquet | 5,229,342 | 38.9MB | 2020-03-01〜2020-12-31 |
| movement-range-maps/movement_range_2021.parquet | 5,287,242 | 38.6MB | 2021 |
| movement-range-maps/movement_range_2022.parquet | 1,662,956 | 12.2MB | 2022-01-01〜2022-05-22 |
| commuting-zones/commuting_zones.parquet (GeoParquet) | 6,541 | 13.6MB | 2023-03 |
| facebook-business-activity-trends-during-crisis/business_activity_trends.parquet | 1,888,011 | 10.4MB | 2024-05〜2025-03 |

- 元のファイルは 22 本、1,245,212,427 bytes (`<dataset>/original/`)。Parquet は合計 202,882,696 bytes。名前は HDX の名前を整えたもの (拡張子の無い `Movement Distribution 1 June - 15 June, 2026` は `movement-distribution-1-june-15-june-2026.csv`)。HDX での名前、resource id、URL、sha256 は manifest.json にある。
- どれも HDX の API で license_id が `cc-by` であることを確かめてから置いた。
- 元のファイルはすべて、S3 の ETag (MD5) と一致することを確かめた。Movement Range Maps の 2020 年の zip は、API の示す大きさ (56,561,599 bytes) と配られるファイル (56,560,052 bytes) が違う。配られたほうが ETag と一致し、zip としても壊れていない。API の大きさが古いと考えられる。
- Parquet は zstd、国、区域、日付の順に並べてある。型は日付と double と整数だけ付け、ID は文字列のまま。行数と数値の列の合計が元のファイルと一致することを確かめてから置いた。どれも 512MB 未満。
- 公開 URL で確かめた: どの Parquet も `curl -r -100` に初回から 206。DuckDB の httpfs で、Movement Distribution の日本 (546,312 行、1,804 区域)、Movement Range Maps の台東区 `JPN.41.51_1` (813 行、名前は `NA`) などの集計がローカルのファイルと一致した。
- HTTP の URL には `*` が使えない (DuckDB は `allow_asterisks_in_http_paths` を求める)。年ごとのファイルは `read_parquet([...])` に並べる。

### Movement Distribution のミラーで分かったこと

- 12 本の CSV の期間は、境目の日で重なる。2026-06-15〜16、07-01、08-01 の行 (617,668 行) は 2 つのファイルにあり、値はすべて同じだった。HDX の更新日が新しいファイルの行を残し、古いほうを落とした。`1 June - 15 June` のファイルは実際には 06-16 まである。
- 6/15〜7/1 の 4 本 (元の名前は `combined_part1`〜`4`) は、日でなく行数で切ってあり、6/19、6/23、6/27 は 2 つのファイルに分かれて入っている (区域は重ならない)。4 本とも 656,243 行。
- 2026-06-01〜08-31 の 92 日のうち 16 日が無い (8 月の 4、5、7、9、10、13、17、19〜22、24、26、28〜30 日)。`2026-08-18_to_2026-08-31` のファイルにある日は 18、23、25、27、31 日の 5 日だけ。ファイル名の期間を信じず、`ds` で確かめること。
- 1 日はおよそ 154,400 行 (38,600 区域 × 4 区分)。日本は 1,804 区域 (level 2)。割合が負の行は全体で 301,846 行。
- HDX から消えたファイルは消さずに残す。2 週間ごとに次のコマンドを流すと、新しいファイルだけを落とし、残っているすべての CSV から Parquet を作り直す。

```sh
cd study-geoai-algo-py
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 \
  uv run python -u scripts/mirror_hdx_meta.py > /tmp/study-geoai-mirror-hdx-meta/logs/run-$(date +%Y%m%dT%H%M%S).log 2>&1
```

- 同じ resource のまま中身が差し替わった場合は、古いファイルを `original/superseded/` に移して残す (Parquet には使わない)。

## 学習ステップとの対応 (案)

- 5 クラスタリング、6 PCA: 区市町村を、4 区分の割合の組や、曜日ごとの形で型に分ける。
- 1〜3 回帰: 区市町村の人口密度や駅の数から、家から動かない人の割合を予測する。
- 4 Cross Validation: 日付で分けるか、都道府県でまとめて分けるか。
- Movement Range Maps は、2020 年の緊急事態宣言の前後で、変化率がどう動いたかの時系列に使える。

## 取り出し方

区分は whole。元のファイルはどれも必要な範囲だけを引けない。
z.yuiseki.net のミラー (Parquet) だけが range。2026-09-30 に実測した。

### 署名付き S3 は Range を受ける

HDX の resource URL は署名付きの S3 (`hdx-production-filestore`) へ 302 で飛ぶ。
API を叩くときと同じく、User-Agent を付ける必要がある。

- `movement-range-data-2022-05-22.zip`: 転送を追うと 200、Content-Length 73,054,975、`Accept-Ranges: bytes`。`curl -L -r 0-1023` に 206 と 1,024 バイト、`curl -L -r -64` に 206 と 64 バイト。
- `Movement Distribution Maps_2026-07-13_to_2026-07-16.csv`: 転送を追うと 200、Content-Length 48,830,570、`Accept-Ranges: bytes`。`curl -L -r 0-1023` に 206、`curl -L -r -64` に 206。末尾 64 バイトの中身は `"KNA","1","0","0.4019950687407667","2026-07-16"` で、CSV の最後の行が読めた。

206 は返る。返るだけで、引けるものが無い。

### Movement Range Maps の zip は中に大きな塊が 1 つだけ

zip の中央ディレクトリは Range で読める。末尾 64 バイトに `PK\x05\x06` があり、
エントリ 2 個、中央ディレクトリの大きさ 131 バイト、位置 73,054,822 と読めた。
そこを `curl -r 73054819-73054949` で引く (206、131 バイト) と、中身は次の 2 つだった。

| 名前 | 圧縮方式 | 圧縮後 | 展開後 | 位置 |
|---|---:|---:|---:|---:|
| `movement-range-2022-05-22.txt` | 8 (deflate) | 73,054,214 | 598,707,347 | 0 |
| `README.` | 8 (deflate) | 509 | 961 | 73,054,273 |

TSV が 1 本の deflate の流れとして 73MB 入っている。deflate は途中から展開できないので、
日本の 199,928 行だけが欲しくても、73,054,214 バイトを引いて 598,707,347 バイトに展開するしかない。
一覧と先頭の行だけを見るなら 2 回の Range 要求 (64 バイトと 131 バイト) で済むが、行は 1 行も取れない。

mlit-1km-fromto の zip は月ごとにメンバーが分かれていたので月単位で引けたが、こちらはメンバーが 1 つなので何も選べない。

### Movement Distribution の CSV は索引が無い

48,830,570 バイトの素の CSV で、圧縮もされていない。
Range で任意のバイト範囲は引けるが、どの区域の行がどのバイト位置にあるかを知る手立てが無い。
先頭の 1,024 バイトを引けば列名と最初の数行は見えるし、末尾 64 バイトを引けば最後の行は見えるが、
その間を探すには全体を流すことになる。上の本文のとおり、48.8MB で約 80 秒だった。

Commuting Zones (16.5MB の CSV 1 本) と Business Activity Trends (5 本で 154MB の CSV) も同じで、whole。

### ミラー (Parquet) は range

| ファイル | 大きさ | `curl -r -8` の 8 バイト | フッターの長さ | フッター本体の Range |
|---|---:|---|---:|---|
| `https://z.yuiseki.net/static/hdx-meta/movement-range-maps/movement_range_2021.parquet` | 38,566,824 | `2a ee 00 00 50 41 52 31` | 60,970 | `bytes=38505846-38566815` に 206、60,970 バイト |
| `https://z.yuiseki.net/static/hdx-meta/movement-distribution/movement_distribution_2026.parquet` | 89,222,790 | `e8 cb 01 00 50 41 52 31` | 117,736 | `bytes=89105046-89222781` に 206、117,736 バイト |

どちらも末尾 4 バイトは `PAR1`、`curl -r 0-1023` は 206 と 1,024 バイト。
Parquet のフッターはファイルの末尾にあるので、末尾を引いて長さを知り、そこから戻ってフッターを読む往復が要る。

pyarrow 20.0.0 に Range 要求だけを出す読み取り器を渡して数えた。
`movement_range_2021.parquet` から `polygon_id` と `ds` の 2 列を最初の行グループ分だけ読むと、
要求は合計 3 回 (末尾 65,536 バイトが 1 回、列の塊が 2 回)、流れたのは 75,278 バイト、0.2 秒。
53 行グループ、1 つ 100,352 行。ファイル全体の 0.2% で済む。

元の zip で 73MB を流して 599MB に展開していたものが、7 万バイトの往復 3 回になる。
ミラーを作った意味はここにある。

### まとめ

| 経路 | 区分 | 根拠 |
|---|---|---|
| HDX の CKAN API | catalog に近い | `package_show` が 200。resource の一覧と license_id が取れる。bbox や日時では絞れない |
| Movement Range Maps の zip | whole | 中央ディレクトリは Range で読めるが、中身は 598,707,347 バイトに展開される deflate の塊が 1 つ |
| Movement Distribution の CSV | whole | 206 は返るが、行の位置を知る索引が無い |
| Commuting Zones、Business Activity Trends の CSV | whole | 同上 |
| z.yuiseki.net の Parquet | range | 末尾 4 バイトが `PAR1`、2 列 1 行グループを 3 回の要求、75,278 バイトで読めた |
