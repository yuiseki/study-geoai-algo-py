# 収集の記録 (2026-10-06)

`/sata_hdd_24tb/hf_data/natural-earth/` で全ベクターレイヤーを取得し、レイヤーごとに GeoParquet に変換した。公開先は `yuiseki/natural-earth` を予定している (この時点では dry run のみ)。

## レイヤーの一覧の出どころ

GitHub の `nvkelso/natural-earth-vector` の最新リリースタグ v5.1.2 (commit f1890d9f152c) のツリーを公開 API で読み、6 つのデータディレクトリにある `.shp` をレイヤーとした。master のツリーも同じ 215 個だった。配布元の CDN には一覧が無いので、これ以外に根拠のある一覧は無い。

| 縮尺と分類 | レイヤー | 地物 | zip (バイト) | Parquet (バイト) |
|---|---:|---:|---:|---:|
| 10m cultural | 84 | 284,733 | 744,523,979 | 381,972,925 |
| 10m physical | 50 | 51,445 | 52,386,303 | 50,821,783 |
| 50m cultural | 26 | 10,588 | 20,514,395 | 9,271,397 |
| 50m physical | 23 | 7,614 | 7,564,947 | 5,243,477 |
| 110m cultural | 14 | 2,176 | 1,434,480 | 1,492,445 |
| 110m physical | 18 | 1,207 | 3,397,505 | 1,464,682 |
| 計 | 215 | 357,763 | 829,821,609 | 450,266,709 |

zip は 206 個。10m cultural の zip が大きいのは、後述の 4 レイヤーのために 380MB のテーマパッケージ `10m_cultural.zip` を丸ごと取ったからである。

## 単独の zip が無いレイヤー

215 のうち 12 は `<layer>.zip` が CDN に無く、403 が返る。

- `ne_10m_parks_and_protected_lands_*` の 4 つは、ダウンロードページがリンクしている束 `ne_10m_parks_and_protected_lands.zip` に入っている。
- 残る 8 つ (`ne_10m_admin_0_names`、`ne_10m_admin_1_states_provinces_scale_rank_minor_islands`、`ne_10m_admin_2_counties_lines`、`ne_10m_admin_2_counties_to_match`、`ne_50m_admin_0_breakaway_disputed_areas_scale_rank`、`ne_50m_admin_1_seams`、`ne_50m_airports`、`ne_50m_ports`) はテーマパッケージ `10m_cultural.zip` と `50m_cultural.zip` にしか無い。
- ダウンロードページの `ne_50m_airports.zip` と `ne_50m_ports.zip`、2 つの `*_shp_scale_rank.zip`、`10m-admin-0-boundary-lines-maritime.zip` のリンクは切れている (403)。
- 逆に、ツリーにはあるがページからリンクされていないレイヤーが 13 ある。`ne_10m_urban_areas_landscan` などは単独の zip が CDN に存在するのに、ページからはたどれない。

取れなかったレイヤーは無い。

## 版

版は 1 つではない。ディレクトリ名は GitHub のリリースに合わせて v5.1.2 としたが、各 zip の `VERSION.txt` が名乗る版はばらばらだった。

| VERSION.txt | レイヤー数 |
|---|---:|
| 5.1.1 | 69 |
| 4.1.0 | 65 |
| 5.0.0 | 42 |
| 5.1.0 | 18 |
| 5.1.2 | 7 |
| 5.0.0-pre9 | 6 |
| 2.0.0 | 2 |
| 無し | 6 |

- 5.1.2 を名乗るのは populated places の 6 つと `ne_50m_admin_0_boundary_lines_disputed_areas` だけで、CHANGELOG の 5.1.2 の変更点と一致する。
- 2.0.0 は `ne_50m_airports` と `ne_50m_ports`。テーマパッケージにしか無いレイヤーで、長く更新されていない。
- 5.0.0-pre9 はリリース前の版番号のまま配られている (`ne_10m_coastline` など 6 つ)。
- 無しの 6 つはテーマパッケージから取ったレイヤーで、自分の `VERSION.txt` を持たない。
- ダウンロードページがリンクの横に書く版は zip とよく食い違う。53 レイヤーはページが 4.0.0、zip が 4.1.0 だった。
- CDN の Last-Modified は 2022-05-13 (95)、2021-09-04 (65)、2021-12-08 (45)、2022-05-05 (1)。

## 検証

`02_verify.py` は全部通った。215 レイヤーすべてで `.dbf`、`.shx`、Parquet の地物数が一致し、削除済みレコードは無かった。属性 11,756,311 セルを Python で `.dbf` から読んだ値と 1 つずつ比べ、ジオメトリは WKB を GDAL の読みと比べて、差は 0 だった。テストは 35 件通り、ruff も通る。

ジオメトリの妥当性は数えただけで直していない。

- 不正 (ST_IsValid が偽) は 58 レイヤーで 2,445 件。うち 2,238 件が `ne_10m_urban_areas_landscan`。次は 10m の水深 (F 5000 で 51 件など)。`ne_10m_admin_0_countries` にも 1 件ある。
- null は 7 レイヤーで 533 件。うち 505 件は `ne_10m_admin_0_names` の全件。

## 意外だったこと

- `ne_10m_admin_0_names` はジオメトリを持たない。505 件すべてが null shape で、`.prj` も無い (GitHub にも無い)。実体は国名の属性表である。GeoPackage 調査で srs_id 0 だった理由はこれで説明できる。DuckDB は全件 null だと GeoParquet の `geo` メタデータを書かないので、このレイヤーだけ Parquet の GEOMETRY 論理型で EPSG:4326 を持たせた。
- 37 レイヤーに `.cpg` が無い。国ごとの見方の 33 レイヤーなどで、LDID は 0。全部の文字列が UTF-8 として読めたので UTF-8 とした。
- 69 レイヤーが文字列の詰め物に空白ではなく NUL を使っている (2,315,021 値)。GDAL は最初の NUL で値を切るので結果は同じになるが、素朴な dBASE 読み取りでは NUL の付いた文字列になる。
- GDAL は文字列の先頭の空白も落とす。`ne_10m_rivers_lake_centerlines_scale_rank` の `name_ja` に先頭が空白の値が 6 つあり (` 左江` など)、Parquet では空白が落ちている。
- `50m_cultural.zip` には GitHub のツリーに無い `ne_10m_admin_1_sel` が混ざっている。取り込んでいない。

## ラスター

10m と 50m のラスターのページから zip を 52 個 (10m が 38、50m が 14) 見つけ、HEAD で合計 6,699,100,477 バイトだった。2GB を超えるので落としていない。一覧は MANIFEST.json の `rasters` にある。110m のラスターのページは無い。

## ライセンス

利用規約のページ (`https://www.naturalearthdata.com/about/terms-of-use/`) の文言は README.md の「ライセンス」の節に引いたものと変わっていなかった。第三者のデータの記載 (The Washington Post、EC JRC IES、XNR Productions、International Mapping Associates、Wikidata) も同じである。
