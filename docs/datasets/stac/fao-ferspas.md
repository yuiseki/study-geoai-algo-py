# fao-ferspas

2026-09-28 に読んで確かめた内容。

- `https://stac.yuiseki.net/fao-ferspas/`
- 静的な STAC JSON は無く、GeoParquet の表が本体 (`catalog.json` は 404)。
- `items.parquet` の 1 行が 1 ファイル。`season`, `crop`, `ssp` などの次元が列になっている。
- `search.parquet` は BM25 の全文検索索引、`embeddings*.parquet` は意味検索用のベクトル。

気をつけること (実際に試して分かったこと):

- `data_href` の `storage.cloud.google.com` は Google ログインに飛ばされて取れない。
  `data_gs_href` の `gs://` を `https://storage.googleapis.com/` に置き換えると匿名で読める。
- 57 バケットのうち 3 つは匿名だと 403。`fao-gismgr-asis-data` (18,917 ファイル)、`fao-gismgr-rdms-data` (1,245)、`fao-gismgr-seap-data` (1)。
  README の例に出てくる ASI-D (農業ストレス指数) は asis に入っているので読めない。
- 読めるバケットのファイルは COG で、GDAL で部分読みできた (例: GAEZ-V5 は 256x256 タイル、概観 5 段)。

## このリポジトリでの使い方 (2026-09-29)

- AgERA5 の月別 4 つ (`AGERA5-PF-M`、`AGERA5-ET0-M`、`AGERA5-TMAX-AVG-M`、`AGERA5-TMIN-AVG-M`) を [study_geoai.ferspas](../../../src/study_geoai/ferspas.py) で読む。1 ファイルが 1 か月の全球 (3600 x 1800、0.1 度、float32、nodata -9999、256 x 256 のタイル、概観 4 段)。
- ライセンスは collections.parquet の license 列で、雨と基準蒸発散量が CC-BY-SA-4.0、2 つの気温が CC-BY-4.0。
- 日本の範囲 (東経 122〜149 度、北緯 24〜46 度) を 1 か月読むのに、キャッシュなしで約 4 秒。12 並列で 564 か月が約 150 秒。
- 1979-01 から 2025-12 まで、4 変数とも 564 か月が揃い、日本の陸の格子に欠けた月は無かった。中心が陸でも AgERA5 が海として扱う格子が 5 つある。
- 使った実験: 004-D、005-E、005-F、006-C、011-C。同じデータをタイルとして配信する別の実験に [poc-cng-ferspas-udf](https://github.com/yuiseki/poc-cng-ferspas-udf) がある。

