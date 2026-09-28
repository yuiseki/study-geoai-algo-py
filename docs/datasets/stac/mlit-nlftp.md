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
