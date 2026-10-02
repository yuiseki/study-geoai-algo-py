# Hugging Face の yuiseki のデータセット

<https://huggingface.co/yuiseki/datasets> の公開データセット。2026-09-28 に Hugging Face の API (`/api/datasets?author=yuiseki`) で一覧を取った時点で 26 個。
1 データセット 1 ファイル。ライセンスと件数の区分は、Hugging Face のタグの値。

## 地理に関わるもの

| データセット | 更新 | ライセンス (タグ) | 件数の区分 | 中身 | 詳細 |
|---|---|---|---|---|---|
| osm-tokyo23-src-2026-08 | 2026-09-15 | odbl | 1M-10M | 23 区の OSM 凍結 pbf と osm2pgsql 形式 Parquet 4 表 (点 30.7 万、面 143.7 万) | [osm-tokyo23-src-2026-08.md](osm-tokyo23-src-2026-08.md) |
| osm-japan-src-2026-08 | 2026-09-25 | odbl | 10M-100M | 全国の OSM 凍結 pbf 2.8GB と osm2pgsql 形式 Parquet 4 表 (面 3,328 万) | [osm-japan-src-2026-08.md](osm-japan-src-2026-08.md) |
| osm-tokyo23-qa-2026-08 | 2026-09-23 | odbl | 1K 未満 | 215 問の答えと SQL / Overpass クエリ、聞き返し要否つき | [osm-tokyo23-qa-2026-08.md](osm-tokyo23-qa-2026-08.md) |
| osm-tokyo23-questions | 2026-09-23 | odbl | 1K 未満 | 23 区についての英語の質問 215 問 (答えなし) | [osm-tokyo23-questions.md](osm-tokyo23-questions.md) |
| osm-wikidata-brand-tokyo23 | 2026-09-17 | odbl | 1K 未満 | 23 区のブランド 892 件の OSM 表記と Wikidata 名の対照 | [osm-wikidata-brand-tokyo23.md](osm-wikidata-brand-tokyo23.md) |
| osm-wikidata-brand-jp | 2026-09-17 | odbl | 1K-10K | 全国のブランド 1,859 件の OSM 表記と Wikidata 名の対照 | [osm-wikidata-brand-jp.md](osm-wikidata-brand-jp.md) |
| osm-wiki | 2026-09-17 | (なし) | (なし) | OSM Wiki 8 言語 78,178 ページの平文 (2026-01-30 ダンプ) | [osm-wiki.md](osm-wiki.md) |
| osm-tag-corpus | 2026-09-07 | odbl | 10K-100K | OSM タグ 9,803 種の多言語説明と世界での使用回数 | [osm-tag-corpus.md](osm-tag-corpus.md) |
| text2geoql | 2026-08-29 | odbl | 1K-10K | TRIDENT 中間言語から Overpass QL への合成対 4,897 件 | [text2geoql.md](text2geoql.md) |
| mlit-1km-fromto-2022-01 | 2026-10-02 | cc-by-4.0 | 10M-100M | 全国の人流オープンデータの元の zip 99 本と Parquet 5 本 (メッシュ別 3,808 万行)。ブルームフィルタ無し | [../mlit-1km-fromto/README.md](../mlit-1km-fromto/README.md) |
| npa-traffic-accidents | 2026-10-02 | cc-by-4.0 | 1M-10M | 警察庁の交通事故オープンデータ 2019〜2025 年。年と票ごとのサブセット 21 個、本票に 10 進の緯度経度と点 | [../npa-traffic-accidents/README.md](../npa-traffic-accidents/README.md) |
| worldpop-jp-2026-01 | 2026-10-02 | cc-by-4.0 | 1K-10K | WorldPop R2025A の日本、2015〜2030 年。人口 100m/1km、年齢・性別 1km、都市化度の元の GeoTIFF 1,024 本と COG、一覧の Parquet | [../stac/worldpop.md](../stac/worldpop.md) |
| ourairports-2026-08 | 2026-10-02 | other (public domain) | 10K-100K | OurAirports の 2026-08-31 の commit の 7 つの CSV と型付きの Parquet (空港 86,002 件) | [../ourairports/README.md](../ourairports/README.md) |
| estat-boundary-2020 | 2026-09-26 | cc-by-4.0 | 100K-1M | 2020 年国勢調査の小地域ポリゴン 23 万件と人口・世帯 | [estat-boundary-2020.md](estat-boundary-2020.md) |
| jp-admin-2026-09 | 2026-09-26 | cc-by-4.0 | 1K-10K | 都道府県 47 と市区町村 1,918 のコード・読み・ポリゴン・人口 | [jp-admin-2026-09.md](jp-admin-2026-09.md) |
| abr-src-2026-09 | 2026-09-26 | cc-by-4.0 | 1M-10M | アドレス・ベース・レジストリの町字 72.7 万件と代表点 (境界なし) | [abr-src-2026-09.md](abr-src-2026-09.md) |
| geo-triples-jp-gov | 2026-09-26 | cc-by-4.0 | 100K-1M | 国勢調査境界の都道府県・市区町村の隣接と包含の三つ組と文 | [geo-triples-jp-gov.md](geo-triples-jp-gov.md) |
| geo-triples-japan | 2026-09-26 | odbl | 1M-10M | OSM の全国の市区町村と POI 8 万の空間関係の三つ組と文 | [geo-triples-japan.md](geo-triples-japan.md) |
| geo-triples-tokyo23 | 2026-09-25 | odbl | 1M-10M | 東京 23 区と POI と Natural Earth の空間関係の三つ組と文 | [geo-triples-tokyo23.md](geo-triples-tokyo23.md) |
| ne-admin0-10m | 2026-09-26 | other | 1K-10K | Natural Earth 5.1.1 の 10m の国・州と米国の郡 (3 層) | [ne-admin0-10m.md](ne-admin0-10m.md) |
| wikipedia-geotagged | 2026-09-24 | cc-by-sa-4.0 | 100K-1M | 座標付きの英語版と日本語版 Wikipedia の本文。英 137 万件、日 22 万件 (2026-09-01 ダンプ) | [wikipedia-geotagged.md](wikipedia-geotagged.md) |
| wikivoyage-geotagged | 2026-09-24 | cc-by-sa-4.0 | 10K-100K | 座標付きの英語版 Wikivoyage 2.9 万件の本文。種類と国の列はすべて空 | [wikivoyage-geotagged.md](wikivoyage-geotagged.md) |
| wikidata-gazetteer | 2026-09-21 | cc0-1.0 | 10M-100M | 位置を持つ Wikidata 項目 1,220 万件と 553 言語の名前 6,250 万件 (2026-08-31 ダンプ) | [wikidata-gazetteer.md](wikidata-gazetteer.md) |
| un-docs | 2026-09-21 | other | 10K-100K | 国連の総会と安保理の英語文書 3.9 万件 (1945〜2023)。位置の列は無い | [un-docs.md](un-docs.md) |

## Parquet を URL から読むときの挙動 (2026-09-29 に測った)

`https://huggingface.co/datasets/<名前>/resolve/<コミット>/<パス>` は、Xet の CDN (`us.aws.cdn.hf.co/xet-bridge-us/...`) へ転送される。

- Range 要求に 206 で応える。`curl -L -r -8` で末尾 8 バイトを求めると、Parquet の終わりの印 `PAR1` だけが返った。z.yuiseki.net の Cloudflare のような「初回だけ 200」は、2 回試して見られなかった。
- DuckDB 1.5.5 も部分取得で読む。`call enable_logging('HTTP')` のあと `duckdb_logs_parsed('HTTP')` で、要求ごとの Range と応答の状態が見られる。HEAD が 1 回 (200) と、GET が列ごと・行グループごとに数回 (206)。
- ただし、読み飛ばせるのは列と行グループの単位まで。osm-tokyo23-src の line 表 (25.95MB) では次のとおり。

| クエリ | GET の数 | 取得量 |
|---|---:|---:|
| `count(*)` | 1 | 0.03MB (末尾のメタデータ) |
| `highway` の列だけ | 4 | 0.19MB |
| 道路網に要る列と形 (`way`) | 7 | 23.56MB |

- 形の列がファイルの大部分を占めるうえ、bbox の列が無く、行が空間の順に並んでいないので、範囲で絞っても行グループを飛ばせない。形を読むなら全体を読むのとほぼ同じになる。この大きさなら、一度読んで範囲ごとに `/tmp/study-geoai/` にキャッシュする。
- URL にはブランチ名でなくコミットのハッシュを入れて版を固定する (`/api/datasets/<名前>` の `sha`)。

## 地理と関係ないもの (調べていない)

onomatopoeia-ja, onomatopoeia-ja-flat, sake_qa, scp-jp-plain, g-uc, open2ch-livejupiter-qa (どれも 2024-03〜04 の更新)。
