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
- 2026-09-29 に mobile の 2026 年第 1 四半期と 2025 年第 4 四半期も同じ形で足した (3-C で四半期の間の一致を測るため)。この 2 つは元のファイルで `avg_lat_down_ms` と `avg_lat_up_ms` が整数で、2026 年第 2 四半期では小数。まとめて読むときは `union_by_name` を使うか型をそろえる。
- 同じタイルの四半期の間の一致は低い。23 区のすべてのタイルで、前の四半期の速度が今の四半期を説明するのは R² 0.15 ほど。両方で測定が 100 回以上のタイルに限ると 0.8 前後 (`src/003-C-noise-ceiling/`)。

## 取り出し方

区分は range。分割の単位としては split も併せ持つ。2026-09-30 に実測した。

元の S3 バケットの Parquet で確かめた値。ファイルは
`https://ookla-open-data.s3.us-west-2.amazonaws.com/parquet/performance/type=mobile/year=2026/quarter=2/2026-04-01_performance_mobile_tiles.parquet`。

| 確かめたこと | 結果 |
|---|---|
| `curl -sI` | 200、Content-Length 184,560,046、Accept-Ranges: bytes |
| `curl -r 0-1023` | 206、1,024 バイト |
| `curl -r -8` | 206、8 バイト |
| 末尾 8 バイト | `e4 2c 00 00 50 41 52 31` |
| 末尾 4 バイト | `PAR1` |
| フッターの長さ | 11,492 バイト |
| フッター本体 `bytes=184548546-184560037` | 206、11,492 バイト |

Parquet のフッターはファイルの末尾にあるので、先頭の 1,024 バイトを読んでも索引は得られない。
末尾を引いて長さを知り、そこから戻ってフッターを読む、という 2 段の往復が要る。

pyarrow 20.0.0 に Range 要求だけを出す読み取り器を渡して、要求の回数と流れたバイト数を数えた。
`quadkey` と `avg_d_kbps` の 2 列を、最初の行グループ分だけ読んだ結果:

- 要求は合計 3 回。1 回目が末尾 65,536 バイト (フッター 11,492 バイトがこの中に収まる)、残り 2 回が 2 つの列の塊。
- 流れたのは 10,527,984 バイト、7.4 秒。全体 184,560,046 バイトの 5.7%。

この 10.5MB が最小単位になる。元のファイルは 4 行グループしか無く、1 つが 1,048,576 行あるため、
台東区の 62 タイルだけが欲しくても 100 万行分の列の塊を引くことになる。
range ではあるが、粒度が粗い。上の「z.yuiseki.net のミラー」で行グループを 20,480 行に刻み直したのはこれが理由。

ミラー (`https://z.yuiseki.net/static/ookla/parquet/performance/type=mobile/year=2026/quarter=2/2026-04-01_performance_mobile_tiles.parquet`) も同じ手順で確かめた。

- `curl -sI` は 200、Content-Length 193,117,396、Accept-Ranges: bytes。
- `curl -r -8` は 206 で `61 aa 05 00 50 41 52 31`。末尾 4 バイトは `PAR1`、フッターは 371,297 バイト。
- フッターが 64KB に収まらないので、末尾の読みが 2 回になる。同じ 2 列 1 行グループの読み取りは合計 4 回の要求、566,015 バイト、0.3 秒だった。行グループは 166 個。
- 引くバイト数は元の 5.4%、時間は 25 分の 1 になる。代わりにフッターが 32 倍に膨らみ、最初の往復が 1 回増える。

split の面。S3 の一覧 (`?list-type=2&prefix=parquet/performance/`) は匿名で 200 を返し、62 キーが並ぶ。
Hive 形式の `type=` `year=` `quarter=` で切ってあるので、四半期と種別で必要なファイルだけを選べる。

Shapefile の側は whole。
`https://ookla-open-data.s3.us-west-2.amazonaws.com/shapefiles/performance/type=mobile/year=2026/quarter=2/2026-04-01_performance_mobile_tiles.zip`
は 185,168,307 バイトで `curl -r 0-1023` に 206 を返し、末尾 64 バイトから zip の中央ディレクトリ (5 エントリ) も読める。
ただし中身は 1 つの Shapefile の一式なので、必要な範囲だけを引くことはできない。
