# WorldPop

2026-09-28 に読んで確かめた内容。

- `https://stac.worldpop.org/` は STAC Browser で、実体は STAC API `https://api.stac.worldpop.org`。
- 1 か国 = 1 コレクション。日本 (JPN) は 65 件 = 16 年 × (総人口 100m / 総人口 1km / 年齢性別 100m / 年齢性別 1km) + 都市化度 1。
- 日本の総人口は 100m 版が約 104MB (37,258 x 25,773 画素)、1km 版が約 2.1MB。

気をつけること:

- `datetime` はデータの年ではなくリリース日 (全件 2025-01-01)。年で絞るときは `year` を使う。
- `data.worldpop.org` は `Accept-Ranges: bytes` を返すのに、Range 要求を無視してファイル全体を 200 で返す。
  GDAL の `/vsicurl/` は開けないので、丸ごとダウンロードしてから読む。速度は 30 秒で 4〜11MB だった。
