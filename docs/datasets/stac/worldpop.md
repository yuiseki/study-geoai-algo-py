# WorldPop

2026-09-28 に読んで確かめた内容。

- `https://stac.worldpop.org/` は STAC Browser で、実体は STAC API `https://api.stac.worldpop.org`。
- 1 か国 = 1 コレクション。日本 (JPN) は 65 件 = 16 年 × (総人口 100m / 総人口 1km / 年齢性別 100m / 年齢性別 1km) + 都市化度 1。
- 日本の総人口は 100m 版が約 104MB (37,258 x 25,773 画素)、1km 版が約 2.1MB。

気をつけること:

- `datetime` はデータの年ではなくリリース日 (全件 2025-01-01)。年で絞るときは `year` を使う。
- `data.worldpop.org` は `Accept-Ranges: bytes` を返すのに、Range 要求を無視してファイル全体を 200 で返す。
  GDAL の `/vsicurl/` は開けないので、丸ごとダウンロードしてから読む。速度は 30 秒で 4〜11MB だった。

## z.yuiseki.net のミラー

`data.worldpop.org` は Range を無視するので、日本の総人口の 2020 年と 2025 年 (100m と 1km) を一度だけ取得し、値を変えずに COG にして <https://z.yuiseki.net/static/worldpop/> に置いた。パスは元の `GIS/` 以降と同じ。
取得と変換は `scripts/mirror_worldpop.py` で、`--year` を足して流し直せば年を増やせる (置いてあるものは飛ばす)。

- 2026-09-28 の HTTPS は 1 本あたり約 50kB/s だったので、100m は FTP (`ftp.worldpop.org`、途中から読める) で取り、先頭が HTTPS のものと一致することを確かめた。
- 変換の前後で、大きさ、座標系、geotransform、nodata、型、全画素が一致した。
- 公開 URL から台東区付近の窓を 0.3 秒で読める。
- `study_geoai.worldpop.grid(con, area, 2020)` で、画素の中心が範囲の中にある画素を 1 行ずつ読む。台東区の 2020 年の 100m 版は 1,422 画素、合計 214,562 人 (国勢調査は 211,444 人)。

rasterio で読むときの落とし穴: このマシンのシェルは anaconda の `GDAL_DRIVER_PATH`、`GDAL_DATA`、`PROJ_DATA` を export している。rasterio に同梱の GDAL がこれを拾うと、nodata が None になって -99999 が人口として足され、EPSG コードも引けなくなる。`study_geoai` を import すると、この 3 つを外す。
