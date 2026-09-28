# geojson

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/geojson/`
- 出どころの違う小さなファイルが 4 つ。そのうち `conflicts.json` は GeoJSON ではない (下を参照)。
- 4 つとも丸ごと落として Python の json で読んだ。

## ファイル

| ファイル | 中身 | 大きさ (Content-Length) | Last-Modified |
|---|---|---|---|
| `cable-geo.json` | 海底ケーブルの経路 | 708,963 バイト | 2025-09-20 |
| `conflicts.json` | MapLibre のスタイル JSON (GeoJSON ではない) | 1,538 バイト | 2026-04-09 |
| `tectonicplates_GeoJSON_PB2002_boundaries.json` | プレート境界 (PB2002) | 226,378 バイト | 2025-10-04 |
| `usgs_m45_month.geojson` | USGS の M4.5 以上の地震、1 か月分 | 425,000 バイト | 2025-10-04 |

## cable-geo.json

- FeatureCollection。`name` は `submarine_cables`、`crs` は CRS84。
- 681 地物、すべて MultiLineString。ケーブルの `id` は 666 通り (1 本のケーブルが複数の地物に分かれている場合がある)。
- 属性は `id`, `name`, `color`, `feature_id`, `coordinates` の 5 つ。`coordinates` は属性の中の 1 点 (ラベル位置と思われる。未確認)。
- 範囲: 経度 -180.00 から 180.00、緯度 -55.01 から 78.22。
- 出どころはファイルの中に書かれていない。ファイル名と属性の形は TeleGeography の Submarine Cable Map の配布物に似ているが、未確認。
- ライセンス: 未確認。

## tectonicplates_GeoJSON_PB2002_boundaries.json

- FeatureCollection。241 地物、すべて LineString。
- 属性は `LAYER`, `Name`, `Source`, `PlateA`, `PlateB`, `Type`。`Name` は `AF-AN` のようにプレートの略号の組。
- `Type` は空文字が 176、`subduction` が 65。
- `PlateA` と `PlateB` に出てくるプレートは 52 通り。
- `Source` の上位: `Mueller et al. [1987]` 31 / `by Peter Bird, September 2001` 24 / `by Peter Bird, 1999` 21 / `by Peter Bird, October 2001` 16。ファイル名の PB2002 と合わせ、Peter Bird (2002) のプレート境界モデルを GeoJSON にしたものと読める。
- 範囲: 経度 -180 から 180、緯度 -66.16 から 86.80。
- ライセンス: 未確認。

## usgs_m45_month.geojson

- USGS の地震フィード `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson` を保存したもの (`metadata.url` による)。`metadata.generated` は 2025-09-22 11:23:41 UTC。
- 601 地物、すべて Point (経度, 緯度, 深さ km)。`metadata.count` も 601。
- 地震の時刻の範囲は 2025-08-23 12:24:53 UTC から 2025-09-22 09:02:43 UTC。1 か月分のスナップショットで、更新はされていない。
- 属性は 26 個: `mag`, `place`, `time`, `updated` (ミリ秒のエポック), `tz`, `url`, `detail`, `felt`, `cdi`, `mmi`, `alert`, `status`, `tsunami`, `sig`, `net`, `code`, `ids`, `sources`, `types`, `nst`, `dmin`, `rms`, `gap`, `magType`, `type`, `title`。
- マグニチュードは 4.5 から 7.8。整数部の分布は 4 が 429 / 5 が 162 / 6 が 8 / 7 が 2。
- `magType` は `mb` が 515 / `mww` が 81 / `ml` が 3 / `mw` と `mwr` が各 1。
- 深さは 7.466 から 639.511 km。`status` は全件 `reviewed`、`type` は全件 `earthquake`。`tsunami` が 1 の地物は 13。
- `alert` は空が 547 / green 49 / orange 3 / yellow 1 / red 1。
- 範囲 (`bbox`): 経度 -179.369 から 179.8605、緯度 -61.8842 から 83.8394。
- ライセンス: 未確認。

## conflicts.json (異常)

- 1,538 バイトしかなく、中身は GeoJSON ではなく MapLibre のスタイル JSON (`version: 8`, `name: "UCDP Conflicts"`)。
- ソースは `mbtiles://{conflicts}` で、`ocean`, `land`, `lakes`, `conflicts` の 4 層を描く。`conflicts` 層は属性 `best` の値で円の大きさと色を段階的に変える。`best` は `ucdp/` の GED の死者数の列名と同じ。
- tileserver-gl などに載せる地図の設定と思われ、データは入っていない。拡張子とディレクトリ名に反して、学習には使えない。

## 12 ステップでの使い道 (案)

- 5 DBSCAN: 地震の震央を密度でまとめ、プレート境界に沿って並ぶかを見る。
- 1, 2 回帰 / 決定木: 地震からプレート境界までの距離や深さを特徴量にする (境界への距離は自分で計算する)。件数が 601 と少ないので練習向け。
- 7 Dijkstra / A*: 海底ケーブルの線を陸揚げ地点でつないだグラフを作り、最短経路や、ある 1 本が切れたときの迂回を調べる (端点の同定は自分でする必要がある)。
- 12 多目的最適化: ケーブル経路の長さと、プレート境界や地震の多い場所からの距離の両立を考える題材。
