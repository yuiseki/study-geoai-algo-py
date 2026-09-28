# データセットの出どころ

学習に使うデータの候補として、5 つの STAC カタログを読んで整理したもの。
数字は 2026-09-28 に各カタログを読んで確かめた値。

## 一覧

| カタログ | 中身 | 規模 | データの形 | ライセンス | 入口 |
|---|---|---|---|---|---|
| fao-ferspas | FAO の農業・食料系ラスタ (干ばつ指数、作物、土壌、降水など) | 1,921 コレクション / 639,947 ファイル / 約 21TB | COG (全件 `.tif`) | コレクションごと。CC-BY-4.0 1,074、CC-BY-SA-4.0 548、CC-BY-NC-SA-4.0 291 など | `items.parquet`, `collections.parquet`, `search.parquet` |
| mlit-nlftp | 国土数値情報 (鉄道、バス停、浸水想定、将来推計人口メッシュなど) | 110 データセット / 21,603 ファイル / 228.2GB | zip (Shapefile / GeoJSON / GML) | 年ごとに違う。再配布可は 11,538 ファイル (93.2GB) | `items.parquet` (1.4MB), `collections/index.json` |
| tokyo-ckan | 東京都オープンデータカタログ (施設一覧、統計表など) | 95 組織 / 9,698 データセット / 83,821 ファイル | CSV, XLSX, PDF, GeoJSON など | ほぼ CC-BY-4.0 (9,695 件) | `items.parquet`, `assets.parquet` |
| Overture Maps | 全世界の建物、道路、POI、行政区域、住所、土地被覆 | 最新は 2026-09-23.1。建物だけで 25 億件 | GeoParquet (S3 / Azure) | テーマごと。多くは ODbL-1.0、land_cover は CC-BY-4.0 | `catalog.json` から種類ごとの `collection.json` |
| WorldPop | 全世界の人口グリッド (総人口、年齢性別、都市化度) | 248 か国 / 2015〜2030 年 | GeoTIFF (100m と 1km) | 全件 CC-BY-4.0 | STAC API `https://api.stac.worldpop.org` |

fao-ferspas、mlit-nlftp、tokyo-ckan は yuiseki が作った非公式ミラーで、持っているのはメタデータだけ。
データ本体は公開元のサーバーにある。

## カタログごとの要点

### fao-ferspas

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

### mlit-nlftp

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

### tokyo-ckan

- `https://stac.yuiseki.net/tokyo-ckan/`
- 1 組織 = 1 コレクション、1 データセット = 1 Item、1 ファイル = 1 asset。
- 区市町村をまたいで比べるなら「共通項目」(families) から。43 種類あり、うち 23 種類はデジタル庁の自治体標準オープンデータセット。

気をつけること:

- CKAN には場所も時刻も無いので、どちらも推定値。どう推定したかが `tokyo:footprint_basis` と `tokyo:datetime_basis` に書いてある。
- 場所は公開した組織の管轄区域の矩形。データの点がその中にあるとは限らない。
- 時刻がデータの時期を表すのは、`datetime_basis` が `resource-name` か `dataset-title` のものだけ。
- 同じ名前のデータセットでも列構成が同じとは限らない。`family_layout_match` で確かめる。

### Overture Maps

- `https://stac.overturemaps.org/catalog.json` がリリース一覧。最新は `2026-09-23.1`。
- テーマ 6 つ、種類 15 個。各種類の `collection.json` に行数、列名、Parquet の置き場所がある。
- S3 の Parquet は Range 要求に 206 を返すので、DuckDB などで必要な範囲だけ読める。
- テーマごとに PMTiles もある (`tiles.overturemaps.org`)。

| テーマ / 種類 | 行数 | ライセンス |
|---|---:|---|
| addresses/address | 474,186,531 | other |
| base/bathymetry | 407,277 | CC0-1.0 |
| base/infrastructure | 157,617,917 | ODbL-1.0 |
| base/land | 75,848,834 | ODbL-1.0 |
| base/land_cover | 123,302,114 | CC-BY-4.0 |
| base/land_use | 56,097,254 | ODbL-1.0 |
| base/water | 66,204,219 | ODbL-1.0 |
| buildings/building | 2,533,842,612 | ODbL-1.0 |
| buildings/building_part | 4,486,107 | ODbL-1.0 |
| divisions/division | 4,688,229 | ODbL-1.0 |
| divisions/division_area | 1,080,667 | ODbL-1.0 |
| divisions/division_boundary | 87,530 | ODbL-1.0 |
| places/place | 81,455,423 | other |
| transportation/connector | 421,978,977 | ODbL-1.0 |
| transportation/segment | 352,054,710 | ODbL-1.0 |

`other` の places と addresses は、元データごとに条件が違う。<https://docs.overturemaps.org/attribution/> を見る。

### WorldPop

- `https://stac.worldpop.org/` は STAC Browser で、実体は STAC API `https://api.stac.worldpop.org`。
- 1 か国 = 1 コレクション。日本 (JPN) は 65 件 = 16 年 × (総人口 100m / 総人口 1km / 年齢性別 100m / 年齢性別 1km) + 都市化度 1。
- 日本の総人口は 100m 版が約 104MB (37,258 x 25,773 画素)、1km 版が約 2.1MB。

気をつけること:

- `datetime` はデータの年ではなくリリース日 (全件 2025-01-01)。年で絞るときは `year` を使う。
- `data.worldpop.org` は `Accept-Ranges: bytes` を返すのに、Range 要求を無視してファイル全体を 200 で返す。
  GDAL の `/vsicurl/` は開けないので、丸ごとダウンロードしてから読む。速度は 30 秒で 4〜11MB だった。

## 学習ステップとの対応 (案)

| ステップ | 使えそうなデータ |
|---|---|
| 1〜3 回帰・分類、木、Boosting | WorldPop の人口と Overture の建物・POI をメッシュで集計して、人口を予測する |
| 4 Cross Validation とデータリーク | 同じメッシュ表を、ランダム分割と空間ブロック分割 (GroupKFold / verde) で比べる |
| 5 k-means / DBSCAN | Overture の places や tokyo-ckan の施設一覧の点をクラスタリングする |
| 6 PCA | FAO の多数のラスタを同じ格子で読んで、次元を圧縮する |
| 7 Dijkstra / A* | Overture の transportation (segment と connector) で道路グラフを作る |
| 8〜9 LP / MILP、assignment / facility location | mlit-nlftp の将来推計人口メッシュと施設 (医療機関、学校、避難施設) で配置と割当を解く |
| 10 CP-SAT / scheduling | 未定 |
| 11 SHAP / calibration | 1〜3 で作ったモデルを説明・較正する |
| 12 多目的最適化 | 8〜9 の配置問題に、距離とコストなど複数の目的を与える |
