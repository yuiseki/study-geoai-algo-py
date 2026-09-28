# Speedtest by Ookla Global Fixed and Mobile Network Performance Maps

2026-09-28 に読んで確かめた内容。

- 登録ページ: <https://registry.opendata.aws/speedtest-global-performance/>
- 説明: <https://github.com/teamookla/ookla-open-data>
- 置き場: S3 バケット `ookla-open-data` (us-west-2)。認証なしで一覧も取得もできる。
- 更新: 四半期ごと。

## 中身

Speedtest アプリの測定結果 (下り、上り、遅延) を、ズーム 16 の Web メルカトルタイル (赤道で約 610.8m 四方) ごとに平均したもの。
GPS 並みの位置精度がある測定だけを使っている。固定回線 (fixed) と携帯 (mobile) で別ファイル。

| 形式 | ファイル | 合計 | 期間 |
|---|---:|---:|---|
| Parquet | 60 (fixed 30, mobile 30) | 15.13GB | 2019 年第 1 四半期から 2026 年第 2 四半期 |
| Shapefile (zip) | 60 (fixed 30, mobile 30) | 12.15GB | 同上 |

1 ファイルが 1 四半期 1 種別で、Parquet は 1 つ 175〜262MB。置き方は Hive 形式の分割:

```
parquet/performance/type=mobile/year=2026/quarter=2/2026-04-01_performance_mobile_tiles.parquet
```

2026 年第 2 四半期の mobile は 3,381,216 タイル。列:

| 列 | 型 | 意味 |
|---|---|---|
| quadkey | VARCHAR | ズーム 16 のタイルの quadkey |
| tile | VARCHAR | タイルの形 (WKT、EPSG:4326) |
| tile_x, tile_y | DOUBLE | タイルの位置 |
| avg_d_kbps, avg_u_kbps | BIGINT | 平均の下り・上り速度 (kbps) |
| avg_lat_ms | BIGINT | 平均の遅延 (ms) |
| avg_lat_down_ms, avg_lat_up_ms | DOUBLE | 下り・上り中の遅延 (ms) |
| tests | BIGINT | 測定回数 |
| devices | BIGINT | 端末数 |
| quarter, type, year | | 分割の値が列にも入っている |

S3 は Range 要求に 206 を返すので、DuckDB でフッターだけ読める。

## 気をつけること

- ライセンスは CC BY-NC-SA 4.0 (登録ページの記載)。非営利に限られ、派生物も同じ条件になる。
- 引用の書式が決まっている (登録ページの Citation)。対象期間とアクセス日を入れる。
- 一覧には中身の無い「ディレクトリ」のキーが Parquet と Shapefile に 1 つずつある (2026 年第 2 四半期の mobile)。数えるときは大きさ 0 を除く。
- 値はタイル内の平均なので、測定回数 (`tests`) の少ないタイルはばらつきが大きい。

## 学習ステップとの対応 (案)

- 1〜3: 人口や建物密度から通信速度を予測する。`tests` で重み付けするかどうかも比べられる。
- 4: quadkey の上位桁でまとめると、そのまま空間ブロック CV の groups になる。
- 5: 速度と遅延でタイルをクラスタリングする。
- 9: 速度の遅いタイルに基地局を置く配置問題の需要側として使う (供給側は [OpenCelliD](../opencellid/README.md))。

## z.yuiseki.net のミラー

元のバケットは 2026-09-28 に毎秒 39KB〜1MB しか出ず、元のファイルは行グループが 4 つ (1 つ約 100 万行) しかないので、台東区の件数を数えるだけでも 60 秒で終わらなかった。
そこで 2026 年第 2 四半期の mobile と fixed を一度だけ取得し、Range 要求で読める形にして <https://z.yuiseki.net/static/ookla/> に置いた。

- パスの階層は元と同じ (`parquet/performance/type=.../year=.../quarter=.../`)。
- 元の列と値はすべてそのまま。`geometry` (GeoParquet) と `bbox` の列を足し、quadkey 順に 20,480 行ずつの行グループで書き直した。
- 行数、quadkey の集合、整数列の合計、全列の行ハッシュの合計が元と一致することを確かめた。
- 台東区付近を bbox の列で読むと、約 1MB を 0.5 秒で読める。区の形にかかるタイルは mobile も fixed も 62。
- ライセンスと引用の書式は、ミラーの LICENSE と README.md に書いた。
