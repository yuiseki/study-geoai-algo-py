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
