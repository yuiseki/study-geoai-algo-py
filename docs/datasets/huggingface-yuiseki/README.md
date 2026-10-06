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
| worldbank-wdi | 2026-10-04 | cc-by-4.0 (世界銀行の紛争解決条項つき) | 1M-10M | WDI の一括 zip 7 版 (2024-05-30〜2026-10-01) を版ごとのサブセットで。縦持ちの値と指標説明・脚注の Parquet、作り直した CSV。どれかの版で CC BY 以外か空と表示された 74 指標 (SIPRI、IEA、WDPA、CC BY-NC など) を全版から除外。元の zip は置かない | [../worldbank/README.md](../worldbank/README.md) |
| pwt | 2026-10-05 | cc-by-4.0 | 1M-10M | Penn World Table 8.0〜11.0 の 7 版。版と表ごとのサブセット 41。Stata のファイルから変換 | [../penn-maddison/README.md](../penn-maddison/README.md) |
| maddison-project | 2026-10-05 | cc-by-4.0 | 100K-1M | Maddison Project 2018、2020、2023。版をまたいで積めない | [../penn-maddison/README.md](../penn-maddison/README.md) |
| undp-hdr | 2026-10-05 | other (CC BY 3.0 IGO) | 100K-1M | 人間開発指数 HDR 2025。横持ちと縦持ち。毎年全系列を計算し直す | [../undp-hdr/README.md](../undp-hdr/README.md) |
| unhcr-refugee-stats | 2026-10-05 | cc-by-4.0 | 100K-1M | UNHCR 難民統計の 5 系統と国の一覧 (取得日 2026-10-04)。第三者 (IDMC、UNRWA) は除外 | [../unhcr/README.md](../unhcr/README.md) |
| un-statistical-yearbook | 2026-10-06 | other (UNdata の規約と元の機関の規約) | 100K-1M | 国連統計年鑑の CSV (SYB68 32 表、SYB61 1 表)。行ごとの出典の機関の規約で再配布できる行だけ (22 表 105,902 行)。WHO、ITU、IMF、IUCN、UNODC、UN Tourism、WIPO、IPU、UNEP-WCMC は除外、UIS は CC BY-SA 4.0 | [../undata/README.md](../undata/README.md) |
| undata-sdmx | 2026-10-06 | other (UNdata の規約と作成機関の規約) | 1M-10M | UNdata SDMX API の UNSD の 5 本 (エネルギー統計、エネルギーバランス、国民経済計算の主要集計、SEEA の大気排出とエネルギー)。539 万件。NA_MAIN の IMF 作成行と Eurostat の Kosovo 行は除外。上書き型なので最新の回だけを置く | [../undata/README.md](../undata/README.md) |
| opencellid | 2026-10-06 | cc-by-sa-4.0 | 1M-10M | OpenCelliD の全世界の基地局 (2026-10-06 版、550 万件)。直近 18 か月に観測されたセルだけが入るので日付の版を積む形。mcc、net、area 順の GeoParquet | [../opencellid/README.md](../opencellid/README.md) |
| gsi-evacuation-sites-jp | 2026-10-06 | cc-by-4.0 (PDL1.0) | 100K-1M | 国土地理院の指定緊急避難場所 115,872 件と指定避難所 83,391 件 (2026-10-05 版)。毎朝作り直される上書き型で最新に追随。ご利用上の注意 1〜4 を原文で引用 | [../gsi-evacuation-sites/README.md](../gsi-evacuation-sites/README.md) |
| natural-earth | 2026-10-06 | パブリックドメイン | 100K-1M | Natural Earth v5.1.2 の全ベクタ 215 レイヤー (10m、50m、110m)、357,763 地物。レイヤーごとの GeoParquet と元の zip。ラスタは未収録 | [../natural-earth/README.md](../natural-earth/README.md) |
| mlit-toshi-keikaku-jp | 2026-10-06 | cc-by-4.0 (PDL1.0) | 100K-1M | 国交省都市局の都市計画決定 GIS データ令和 7 年度版。47 都道府県の shp、GeoJSON、CityGML と 26 レイヤーの GeoParquet (424,335 地物)。国土数値情報 A55 の上流。旧 A29 の市町村条件が 22 市町村で未確認 | [../mlit-toshi-keikaku/README.md](../mlit-toshi-keikaku/README.md) |
| gsj-reports | 2026-10-07 | cc-by-4.0 | 10K-100K | GSJ の地質調査所月報 (1950〜2001) と地質調査研究報告 (2001〜2026) の本文テキスト。PDF 4,166 本の文字層を pdftotext で抽出した 1 ページ 1 行の JSONL 2 本 (49,065 ページ、2.6 億文字)。PDF は含まない | (study の資料なし) |
| nilim-disaster-reports | 2026-10-07 | cc-by-4.0 (PDL1.0) | <1K | 国総研の災害現地調査報告のうち、国総研が単独で出し他の権利表記が無い 26 報告 (国総研資料と建築災害速報、883 ページ) の本文テキスト JSONL。共同刊行・共著・判断不能の 118 報告は除外し、理由を EXCLUDE.txt と RIGHTS_REVIEW.tsv に記録。PDF は含まない | (study の資料なし) |
| env-redlist-jp | 2026-10-05 | cc-by-4.0 | 1K-10K | 環境省レッドリスト第 5 次の分類群 8 つ | [../env-redlist/README.md](../env-redlist/README.md) |
| gsi-global-map-jp | 2026-10-05 | cc-by-4.0 (PDL1.0) | 10K-100K | 地球地図日本のベクタ 3 版 × 15 層を GeoParquet に、ラスタは元の zip | [../gsi-global-map-japan/README.md](../gsi-global-map-japan/README.md) |
| ekidata-jp | 2026-10-05 | other (駅データ.jp 利用規約) | 10K-100K | 駅データ.jp の無料 CSV (駅、路線、事業者、接続駅) を日付の版ごとに。駅に点 | (study の資料なし) |
| geonames | 2026-10-02 | cc-by-4.0 | 10M-100M | GeoNames のダンプを夜ごとの版で。サブセットは `20261001.geoname` など 4 つ。元の zip と型付きの Parquet (地名辞書は GeoParquet) | [../geonames/README.md](../geonames/README.md) |
| meta-move-dist | 2026-10-02 | cc-by-4.0 | 10M-100M | Meta の Movement Distribution を HDX の 90 日を超えて保持。元の CSV と年ごとの Parquet (2026-06-01〜) | [../hdx-meta-movement/README.md](../hdx-meta-movement/README.md) |
| meta-range-maps-2022-05 | 2026-10-02 | cc-by-4.0 | 10M-100M | Meta の Movement Range Maps (2020-03-01〜2022-05-22、終了済み)。元の zip と年ごとの Parquet | [../hdx-meta-movement/README.md](../hdx-meta-movement/README.md) |
| mlit-1km-fromto-2022-01 | 2026-10-02 | cc-by-4.0 | 10M-100M | 全国の人流オープンデータの元の zip 99 本と Parquet 5 本 (メッシュ別 3,808 万行)。ブルームフィルタ無し | [../mlit-1km-fromto/README.md](../mlit-1km-fromto/README.md) |
| ucdp-ged | 2026-10-02 | cc-by-4.0 | 100K-1M | UCDP GED を版ごとのサブセットで (19.1〜26.1 の 8 版)。元の zip と codebook、型付きの GeoParquet | [../ucdp-ged/README.md](../ucdp-ged/README.md) |
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
