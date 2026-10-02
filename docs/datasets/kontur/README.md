# Kontur Population (2023-11-01 版)

2026-10-02 に読んで確かめた内容。中身は yuisekin-z の `/www/html/static/kontur/kontur_population_20231101.gpkg` を sqlite3 で読み取り専用 (`?mode=ro`) で開いて数えた値。来歴とライセンスは HDX の CKAN API (`package_show`)、取得元 S3 への HEAD と Range 要求、kontur.io と HDX のライセンス説明ページから。取り出し方は `curl -r 0-1023` で実測した。

- Kontur (`https://www.kontur.io/`) が作った全球の人口分布。H3 の六角形 (解像度 8、約 400m) ごとに人が何人いるかをベクタで持つ。
- 配布は HDX (Humanitarian Data Exchange) のデータセット `kontur-population-dataset` (id `38f46aa9-00dd-4ac9-98c9-5ecaea384c9f`)。タイトルは「Kontur Population: Global Population Density for 400m H3 Hexagons」。実体は Kontur の S3 に置かれた `kontur_population_20231101.gpkg.gz`。
- HDX の `dataset_date` は `[2020-03-11T00:00:00 TO 2023-11-01T23:59:59]`、`metadata_modified` は 2026-05-07。2026-10-02 の時点で 2023-11-01 版が最新で、過去の版 (2022-06-30、2021-11-09、2020-09-28、2020-03-11) も同じデータセットに残っている。
- 作り方 (HDX の methodology_other の要約): GHSL (GHS-POP R2023A) と Facebook/Meta の HRSL を重ね、OpenStreetMap を手がかりに採石場、大きな道路、湖、森林などを無人にする。Microsoft Building Footprints、LINZ NZ Building Outlines、Copernicus Land Cover 100m で分布を補正し、国連 World Population Prospects 2022 Revision の行政区画の総数に合うよう係数をかける。
- HDX の caveats は「Dataset is primarily designed to support visualization behind https://disaster.ninja project and may not be suitable for your specific needs.」と書いている。可視化が主目的のデータ。

## ライセンス

HDX の CKAN API (`https://data.humdata.org/api/3/action/package_show?id=kontur-population-dataset`、2026-10-02 取得) の値。

- `license_id`: `cc-by`
- `license_title`: `Creative Commons Attribution International (CC BY)`
- `license_url`: `http://www.opendefinition.org/licenses/cc-by`
- `license_other`: None

HDX のライセンス説明 (`https://data.humdata.org/faqs/licenses` は `https://docs.humdata.org/about/data-licenses` へ転送される) の CC BY の節。

> Under the CC BY license, you are free to share (copy and redistribute the material in any medium or format) and or adapt (remix, transform, and build upon the material) for any purpose, even commercially. The licensor cannot revoke these freedoms as long as you follow the license terms. The license terms are that you must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. Additionally, you may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

この節の deed と license のリンク先は `https://creativecommons.org/licenses/by/4.0/` と `https://creativecommons.org/licenses/by/4.0/legalcode`。

Kontur のデータセット紹介ページ (`https://www.kontur.io/datasets/population-dataset/`)。リンク先は上の HDX の説明。

> Kontur Population is available under Creative Commons Attribution International (CC BY) license. You can use it for any purpose, even commercially.

読み取れること。

- 再配布は可。改変 (Parquet への変換、国ごとの切り出しなど) も可。ただし変更したことを示す (「indicate if changes were made」)。
- 商用利用は可。HDX と kontur.io の両方が「even commercially」と書いている。
- 表示は必要。クレジット、ライセンスへのリンク、変更の有無。share-alike は無い。
- 版は 4.0 と読むのが自然。HDX の説明ページが 4.0 にリンクしている。ただし API と kontur.io は「CC BY」としか書かず、データセット自体に「4.0」と書かれた箇所は無い。Open Definition の `cc-by` ページも 1.0 から 4.0 までを並べるだけ。
- ファイルの中にライセンス表記は無い。GeoPackage に `gpkg_metadata` テーブルは無く、S3 のオブジェクトにもライセンスを示すヘッダーは無い。

未確認のこと。

- Kontur が指定する表示の文言。見つからなかった。kontur.io/datasets の「Full list of sources」に「© Kontur https://kontur.io/」に続けて HRSL、GHS-POP R2023A、Copernicus、Microsoft Buildings、LINZ、Geoalert、OpenStreetMap を並べた行があるが、Kontur の商用データカタログ全体の一覧で、どの行が Kontur Population 用かはページから確定できない。
- 入力データのライセンスとの関係。HDX の caveats は入力に ODbL のもの (Microsoft Buildings、OpenStreetMap、Geoalert Urban Mapping) と CC BY 4.0 のもの (LINZ NZ Building Outlines) を挙げている。ODbL の入力から作ったものを CC BY で出していることを、Kontur がどう整理しているか (ODbL の Produced Work として扱っているのか) はどの資料にも書かれていない。安全側に寄せるなら、Kontur の表示に加えて入力側、特に OpenStreetMap と Microsoft の帰属を併記する。
- HRSL は caveats に「Licence - Creative Commons Attribution International」とあるが、GHS-POP と Copernicus はライセンス名の記載が無い。それぞれの原ライセンスは確かめていない。
- HDX のデータセットページ本体 (HTML) は直接取得で 403 になり、読んでいない。API に無い注記がページにある可能性は残る。HDX の利用規約 (Terms of Service) も読んでいない。

## 中身

| 項目 | 値 |
|---|---|
| 形式 | GeoPackage 1.2 (`application_id` 1196444487 = `GPKG`、`user_version` 10200) |
| 大きさ | .gpkg 6,711,951,360 バイト (ページ 4,096 バイト × 1,638,660)。配布の .gpkg.gz は 2,436,991,241 バイト |
| レイヤー | `population` の 1 つ (features) |
| 件数 | 32,957,699 (`gpkg_ogr_contents` と全行の count(*) が一致) |
| CRS | EPSG:3857 (WGS 84 / Pseudo-Mercator)。HDX の codebook の「geom [geometry]: Polygon, EPSG:3857」と一致 |
| 範囲 (`gpkg_contents`) | x -20,037,508.34 から 20,037,508.34、y -18,447,868.77 から 17,407,833.04 |
| `last_change` | 2023-10-31T08:25:20.521Z |

列は 4 つ。

| 列 | 型 | 中身 |
|---|---|---|
| fid | INTEGER PRIMARY KEY AUTOINCREMENT | 1 から 32,957,699 |
| geom | GEOMETRY | 六角形のポリゴン (GeoPackage バイナリ) |
| h3 | TEXT | H3 のセル ID。全行 15 文字 |
| population | REAL | そのセルの人数 |

全行を数えた結果 (sqlite3 で 1 回の全走査が約 1 分 45 秒)。

- H3 の解像度は全行 8。セル ID の先頭 2 文字が全 32,957,699 行で `88` だった (2 文字目が解像度)。
- `h3` は重複が無い。同じ値が 2 回以上出る ID は 0 件。
- 空 (NULL) は geom、h3、population のどれも 0 件。
- population は最小 1、最大 40,673、合計 8,031,924,024。全行が整数値で、REAL の型だが小数は無い。0 以下の行も 1 未満の行も無い。つまり人のいないセルは行ごと無い。
- geom は 32,957,690 行が Polygon (165 バイト)、9 行が MultiPolygon (267 バイト)。MultiPolygon になった理由は確かめていない (日付変更線で割ったものかもしれない。未確認)。
- 先頭 3 行は `88f3a6db3bfffff`、`88f3a6db17fffff`、`88f2a40257fffff` で、どれも population 1。並びは H3 の ID 順ではない。

## 気をつけること

空間索引が無い。 `gpkg_extensions` テーブルが無く、R-tree (`rtree_population_geom`) も無い。`h3` 列にも索引は無い。索引として持っているのは fid の主キーだけ。QGIS や ogr2ogr で範囲を指定して開いても、中では 32,957,699 行の全走査になる。国や県だけ欲しいときも、一度は全行を読む。

CRS が EPSG:3857。 緯度経度ではなくウェブメルカトルのメートル。面積を出すのに geom の面積をそのまま使うと高緯度ほど大きく出る。H3 の解像度 8 のセルはどれもほぼ同じ面積なので、面積が要るなら h3 から計算するほうが素直。h3 列があるので、geom を捨てて h3 だけで扱うこともできる。

人のいないセルは無い。 行があるのは人数 1 以上のセルだけ。「その場所に行が無い」は「0 人」を意味する。セル単位で回帰や分類をするとき、0 のセルを自分で足すかどうかを決める必要がある。

値は推計で、整数に丸められている。 国連 WPP の行政区画の総数に合わせて配った推計値。セルの人数を観測値として扱えない。合計 8,031,924,024 は 2023 年の世界人口の推計として扱える大きさだが、どの年の WPP の数字に合わせたものかは HDX の記述 (2022 Revision) 以上には確かめていない。

可視化用のデータ。 HDX の caveats がそう断っている。細かい地点での人数の正確さを期待しない。

.gpkg と .gz は同じもの。 z.yuiseki.net にはどちらも置いてあるが、片方で足りる (下の節)。

## 取り出し方

区分は whole (全球の 1 ファイル)。ただし HDX には国ごとに分けた版が別のデータセットとしてあり、そちらを使えば split になる。2026-10-02 に実測した。

| 要求した URL | `curl -r 0-1023` の応答 | 大きさ |
|---|---|---:|
| S3 の `kontur_datasets/kontur_population_20231101.gpkg.gz` | 206、`Content-Range: bytes 0-1023/2436991241` | 2,436,991,241 |
| z.yuiseki.net の `.gpkg` | 1 回目 200 (`Content-Length` 全体、`cf-cache-status: BYPASS`)、続く 3 回は 206 | 6,711,951,360 |
| z.yuiseki.net の `.gpkg.gz` | 200 (1 回だけ試した) | 2,436,991,241 |

Range が通っても部分読みにはならない。

- 配布の本体は gzip の 1 本の流れなので、途中から展開できない。最小単位は 2.44GB。
- 展開後の .gpkg は Range で引けても、上に書いたとおり空間索引が無く、行の並びも空間順かどうか分からない。必要な範囲のページだけを選ぶ手段が無い。SQLite の主キーの B-tree をたどれば fid で行は引けるが、fid と場所の対応は無い。
- 既存のメモ [z-yuiseki-static/kontur.md](../z-yuiseki-static/kontur.md) にあるとおり、2026-09-28 には ogrinfo の `/vsicurl/` が「Range downloading not supported by this server!」で開けなかった。今日の curl では 206 が返ったので、Range 自体は効いている。最初の要求だけ 200 になるのが ogrinfo を止めた理由かもしれないが、確かめていない。

国ごとの版。

- HDX の Kontur の組織には「Japan: Population Density for 400m H3 Hexagons」のような国別のデータセットがある。日本は `kontur-population-japan` で、2023-11-01 版の `kontur_population_JP_20231101.gpkg.gz` は HDX の size で 16,070,678 バイト。S3 への HEAD も `Content-Length: 16070678`、`Last-Modified: Tue, 31 Oct 2023 16:34:24 GMT` を返した。ライセンスは同じ `cc-by`。
- HDX の検索 (`organization:kontur`、`"Population Density for 400m H3 Hexagons"`) が返した 500 件のうち、タイトルが「<国名>: Population Density for 400m H3 Hexagons」の形のものは 250 件。国別の版の総数と、国別の中身が全球版の切り出しと一致するかは未確認。

## z.yuiseki.net

`https://z.yuiseki.net/static/kontur/` に、配布元の .gz と、それを展開した .gpkg と、取得ログの 3 つがある。置き場は yuisekin-z の `/www/html/static/kontur/`。詳しくは [z-yuiseki-static/kontur.md](../z-yuiseki-static/kontur.md)。

| ファイル | バイト数 | Last-Modified (GMT) |
|---|---:|---|
| kontur_population_20231101.gpkg | 6,711,951,360 | 2023-10-31 17:21:47 |
| kontur_population_20231101.gpkg.gz | 2,436,991,241 | 2023-10-31 17:21:47 |
| kontur-dl.log | 650 | 2026-05-01 10:16:18 |

配布元と同じものであることの根拠。

- .gz の大きさ 2,436,991,241 バイトは、HDX のリソースの size と、S3 への HEAD の `Content-Length` と一致する。
- S3 の ETag は `"eb20be29371859e4e836aedd12a471e9-291"` で、マルチパートアップロードの形。ローカルの .gz を 8 MiB ずつ区切って各 MD5 を連結し、さらに MD5 を取ると同じ `eb20be29371859e4e836aedd12a471e9-291` になった。HDX の hash も同じ値。.gz は配布元とバイト単位で同一と見てよい。
- .gpkg は .gz の展開物。gzip ヘッダーの元のファイル名が `kontur_population_20231101.gpkg`、末尾の ISIZE が .gpkg の大きさを 2^32 で割った余りと一致する。.gpkg の `last_change` 2023-10-31T08:25:20.521Z も gzip ヘッダーの時刻 2023-10-31 08:25:20 UTC と一致する。ただし展開しての突き合わせはしていない。
- ログには取得元の URL が書かれていない。中身は時刻、wget の進捗の最後の 2 行 (100%、7m32s)、`ls -l`、`DONE` だけ。取得元は上の大きさと ETag の一致から特定したもので、ログからの裏付けは無い。ログの START、WGET DONE、GUNZIP DONE の時刻はすべて 2026-05-01T19:08:17+09:00 で、7 分 32 秒かかった取得と合わない。ログの時刻は当てにしない。

## 学習ステップとの対応 (案)

- 5 k-means/DBSCAN: 人口の多いセルを点にして都市圏をまとめる。
- 8 LP/MILP、9 facility location: 人口を需要点として施設の配置を解く。全球のままでは大きすぎるので、国別の版 (日本は 16MB) から始める。
- 1〜3 回帰と木: [WorldPop](../stac/worldpop.md) や [GHSL](../ghsl/README.md) と同じ場所で比べる。Kontur は GHSL を入力の 1 つにしているので、独立な比較にはならない。
- 4 データリーク: 隣り合う六角形は値が似る。ランダム分割と空間ブロック分割 (H3 の親セルでまとめる) の差を見る題材になる。人のいないセルが行ごと無いことも、分割の偏りとして効く。
