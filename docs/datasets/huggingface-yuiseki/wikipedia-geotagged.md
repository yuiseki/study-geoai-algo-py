# wikipedia-geotagged

2026-09-28 に読んで確かめた内容。

- `https://huggingface.co/datasets/yuiseki/wikipedia-geotagged`
- 座標 (`{{coord}}`) を持つ Wikipedia の記事を、本文つきで 1 記事 1 行にしたもの。英語版と日本語版の 2 サブセット。
- 選び方は MediaWiki の GeoData 拡張の `geo_tags` 表に載っている記事をそのまま全部 (記事名前空間でリダイレクトでないもの)。場所かどうかの絞り込みはしていない。
- 作ったコード: `https://github.com/yuiseki/wikipedia-geotagged` (Apache-2.0)。`provenance.yaml` に元ファイル名、各処理の件数、修正履歴がある。

## 元データと基準日

- Wikipedia の `20260901` ダンプ (enwiki / jawiki の `geo_tags.sql.gz`, `page.sql.gz`, `page_props.sql.gz`, `pages-articles.xml.bz2`)。
- `provenance.yaml` の `built` は 2026-09-23。Hugging Face の最終更新は 2026-09-24。

## ファイル (API の tree で確認)

| パス | 大きさ (バイト) | 行数 (フッター) | 行グループ |
|---|---|---|---|
| `20260901.en/train-00000-of-00005.parquet` | 411,138,851 | 115,000 | 23 |
| `20260901.en/train-00001-of-00005.parquet` | 405,358,856 | 235,000 | 47 |
| `20260901.en/train-00002-of-00005.parquet` | 401,052,003 | 475,000 | 95 |
| `20260901.en/train-00003-of-00005.parquet` | 402,975,704 | 450,000 | 90 |
| `20260901.en/train-00004-of-00005.parquet` | 129,547,746 | 99,056 | 20 |
| `20260901.ja/train-00000-of-00002.parquet` | 403,813,016 | 185,000 | 37 |
| `20260901.ja/train-00001-of-00002.parquet` | 50,343,620 | 33,496 | 7 |
| `LICENSE`, `README.md`, `provenance.yaml` | 734 / 8,100 / 7,487 | | |

- 英語 1,374,056 行、日本語 218,496 行。カードの記事数と一致する。
- どれも 50MB を超えるので丸ごとは落としていない。行数と列はフッター、集計は必要な列だけを DuckDB 1.5.5 で読んだ (本文 `text` の列は読んでいない)。

## 列 (Parquet のスキーマ)

| 列 | 型 | 中身 (カードの説明) |
|---|---|---|
| `id` | VARCHAR | ページ ID (文字列) |
| `url` | VARCHAR | 記事の URL |
| `title` | VARCHAR | 記事名 |
| `text` | VARCHAR | wikitext を平文にした本文 |
| `qid` | VARCHAR | Wikidata の ID (`page_props` から) |
| `lat`, `lon` | DOUBLE | 主の tag の座標 |
| `gt_type` | VARCHAR | `city`, `landmark` など |
| `gt_globe` | VARCHAR | `earth` のほか `moon`, `mars` など |
| `gt_dim` | BIGINT | おおよその大きさ (m) |
| `gt_country` | VARCHAR | ISO 3166-1 |
| `gt_region` | VARCHAR | ISO 3166-2 |
| `gt_name` | VARCHAR | tag が持つ名前 |
| `gt_primary` | BOOLEAN | その tag が記事自身の位置か |
| `tags` | LIST(STRUCT(primary, lat, lon, dim, type, name, country, region, globe)) | ページ上の全 tag |

先頭 4 列は `wikimedia/wikipedia` と同じ名前と順番。文字数や言語の列は無い (`len(text)` とサブセット名で出す、とカードにある)。

## 実測 (2026-09-28)

| | `20260901.en` | `20260901.ja` |
|---|---|---|
| 行数 | 1,374,056 | 218,496 |
| `id` の重複 | 無し | 無し |
| `qid` あり | 1,373,275 | 216,440 |
| `qid` の重複 | 無し | 無し |
| `gt_type` あり | 583,118 | 163,459 |
| `gt_country` あり | 744,537 | 161,174 |
| `gt_region` あり | 256,823 | 58,071 |
| `gt_name` あり | 38,030 | 30,548 |
| `gt_globe` が earth 以外 | 3,306 | 303 |
| `gt_primary` が true | 1,244,962 | 166,937 |
| `lat = 0 かつ lon = 0` | 17 | 9 |

- 座標の範囲: `gt_globe = 'earth'` に限ると英語は緯度 -90 から 90、経度 -180 から 180 に収まる。日本語も同じ範囲に収まる。earth 以外を含めると英語の経度は -330 から 359.91 になる (火星や水星などは 0 から 360 の経度で入っている)。
- earth 以外の内訳 (英語): moon 1,855, mars 478, mercury 476, venus 119, ganymede 69, titan 53, io 45, enceladus 34 など。
- `gt_country` の上位
  - 英語: 空 629,519, US 193,829, GB 72,264, PL 50,645, IR 27,515, CA 26,484, AU 23,106, JP 18,242, DE 15,649, IN 14,847
  - 日本語: JP 124,816, 空 57,322, IT 8,647, US 6,179, FR 2,790, DE 2,743, CN 1,426, ES 1,203, GB 1,108
- `gt_type` の上位
  - 英語: 空 790,938, landmark 219,744, city 152,669, edu 40,764, railwaystation 40,478, mountain 27,798, waterbody 20,437, adm2nd 18,720
  - 日本語: landmark 84,952, 空 55,037, city 42,467, railwaystation 15,403, mountain 3,663, adm2nd 2,910 ... admin2nd 300 (カードにある綴りの誤り)
- 1 記事あたりの tag の数 (英語): 1 個 1,293,697, 2 個 42,269, 3 個 6,519, 4 個 3,053。日本語: 1 個 194,577, 2 個 16,442, 3 個 2,106。

## ライセンス

- カードとタグは `cc-by-sa-4.0`。`LICENSE` は Wikipedia の本文として CC BY-SA 4.0 (古い版は GFDL も) と書き、座標は GeoData、Wikidata ID は CC0 だが本文のライセンスは変わらない、とする。
- 表示と継承 (share-alike) が要る。著者は `url` の履歴で辿る。

## 気づいた異常

- `gt_primary` が false の行がある。英語 129,094 行 (うち tag が 1 個だけの行が 98,849)、日本語 51,559 行。カードは「`lat`, `lon`, `gt_*` は主の tag」と書くが、主の tag を持たない記事では主でない tag の値が入っていると見える (未確認)。記事の位置として使うなら `gt_primary` で絞るか、どう扱うかを決める。
- 座標が `(0, 0)` の記事が英語 17、日本語 9 ある。
- `qid` を持つ英語の記事は実測 1,373,275。`provenance.yaml` の `with_a_wikidata_item: 1373281` と 6 件ずれる。
- tag が 3 個の英語の記事は実測 6,519。カードと `provenance.yaml` は 6,520。
- `provenance.yaml` の英語の `articles_not_redirects` は 1,374,075 で、公開されている行数 1,374,056 と 19 件ずれる (説明は無い)。
- カードの YAML の `size_categories` は `1M<n<10M` だが、Hugging Face の API が返すタグは `size_categories:100K<n<1M`。行数の合計 1,592,552 はカードのほうに合う。
- `LICENSE` は「English Wikipedia」とだけ書き、日本語版に触れていない (ライセンスは同じ CC BY-SA 4.0)。
- カードが書くとおり、場所でない記事 (人物、出来事、組織) も含まれる。英語の 6.1% が `wikidata-gazetteer` に無い、とカードにある (未実測)。

## 他のデータとの関係

- `qid` で `wikidata-gazetteer` の `places` に結合できる。場所かどうかの絞り込みは `instance_of` でするのが確かだとカードにある。
- `z-yuiseki-static/wikimedia.md` の重要度表とは `qid` (`wikidata_id`) か `title` で結合できる見込み (未確認)。重要度表は記事とリダイレクトの両方に同じ ID が出るので、結合前に畳む。
- `wikivoyage-geotagged` と列が同じで縦に連結できる。

## 12 ステップでの使い道 (案)

本文は LLM 向けだが、`text` を読まずに位置と属性だけの点データ (約 159 万点) として使える。

- 5 k-means / DBSCAN: 記事の位置 (earth かつ `gt_primary`) をクラスタリングする。英語と日本語で密度の偏り (日本語は JP に集中) を比べられる。
- 1 ロジスティック回帰, 2 Random Forest: 座標から `gt_country` を当てる (空の 46% を当てる題材にもなる)。`gt_type` を座標、`gt_dim`、`len(text)` から当てる分類。
- 1 線形回帰, 3 Gradient Boosting: `len(text)` や tag の数を目的変数にした回帰。`wikidata-gazetteer` の `sitelinks` や `population` を結合して特徴量にする。
- 4 データリーク: 同じ場所の英語版と日本語版が `qid` で重なるので、`qid` でまとめずに分けると漏れる。空間的に近い記事が学習と検証に割れる空間的なリークの題材にもなる。
- 11 SHAP: 記事の長さの回帰で、どの属性が効いているかを見る。
- 7 以降 (経路、最適化) には直接は使えない。施設配置 (9) の需要点の代用にする程度。
