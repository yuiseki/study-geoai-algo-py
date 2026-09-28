# mlit-nlftp

2026-09-28 に読んで確かめた内容。

- `https://stac.yuiseki.net/mlit-nlftp/`
- 入口は 4 つ (データセット別、地域別、ライセンス別、分類別)。横断的な問いには `items.parquet` を 1 回引く。
- `AGENTS.md` がカタログ直下と各データセットにあり、使い方と落とし穴が書いてある。

気をつけること:

- ライセンスはデータセットではなく年に付く。`redistribution` 列 (`allowed` / `not-allowed` / `check`) で絞る。
- 最新年は都道府県ごとに違う。`is_latest` は地域ごとの最新を表す。
- 範囲 (footprint) は都道府県の外接矩形で、中身の実測ではない。
- 測地系が JGD2011 と JGD2000 で混ざる。古い Shapefile は Shift-JIS。
- Python の `urllib` の既定 User-Agent だと Cloudflare に 403 を返される。
- DuckDB で空間関数を使うなら 1.5.5 以上 (1.3.2 は落ちる)。

## z.yuiseki.net のミラー

国土数値情報は zip しか配っておらず、部分読みができない。そこで東京都の 4 データセットの最新年 (どれも CC BY 4.0) を一度だけ取得し、GeoParquet にして <https://z.yuiseki.net/static/ksj/> に置いた。
選ぶときに `redistribution = 'allowed'` を確かめている。README.md に元の URL と取得日時、LICENSE に出典の表示を書いた。

| データセット | 年 | 台東区の中の行数 |
|---|---|---:|
| P04 医療機関 | 2020 | 496 |
| P29 学校 | 2023 | 70 |
| A31a 洪水浸水想定区域 (都の管理河川 2 ファイルと、関東地方整備局の国の管理河川を半分に分けた 2 ファイル) | 2025 | 1,917 |
| mesh500r6 500m メッシュ別将来推計人口 (R6 国政局推計) | 2024 | 57 |

- 座標は元の JGD2011 (EPSG:6668) のまま。bbox の列を足し、Hilbert 順に 10,240 行ずつの行グループで書いた。
- A31a は zip の中の多数の GeoJSON を 1 つにまとめ、元のファイル名を `source_file` の列に入れた。種類 (計画規模、想定最大規模など) ごとに属性の列名が違う。
- `study_geoai.ksj.read(con, area, "A31a")` で、範囲の中の行を読む。
