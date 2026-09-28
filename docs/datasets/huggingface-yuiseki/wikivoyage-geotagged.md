# wikivoyage-geotagged

2026-09-28 に読んで確かめた内容。

- `https://huggingface.co/datasets/yuiseki/wikivoyage-geotagged`
- 座標を持つ英語版 Wikivoyage の記事を、本文つきで 1 記事 1 行にしたもの。`wikipedia-geotagged` と同じコード、同じ列で作られていて、縦に連結できる。
- 作ったコード: `https://github.com/yuiseki/wikivoyage-geotagged` (Apache-2.0)。

## 元データと基準日

- 英語版 Wikivoyage の `20260901` ダンプ (`enwikivoyage-20260901-geo_tags.sql.gz`, `page.sql.gz`, `page_props.sql.gz`, `pages-articles.xml.bz2`)。
- `provenance.yaml` の `built` は 2026-09-23。Hugging Face の最終更新は 2026-09-24。

## ファイル (API の tree で確認)

| パス | 大きさ (バイト) | 行数 (フッター) | 行グループ |
|---|---|---|---|
| `20260901.en/train-00000-of-00001.parquet` | 101,638,314 | 29,505 | 6 |
| `LICENSE`, `README.md`, `provenance.yaml` | 734 / 5,209 / 3,908 | | |

- 50MB を超えるので丸ごとは落としていない。DuckDB 1.5.5 で必要な列だけを読んだ (本文の長さを測るため `text` の列も読んだ。15 秒)。

## 列

`wikipedia-geotagged` と同じ 15 列、同じ型。`id`, `url`, `title`, `text`, `qid` (VARCHAR), `lat`, `lon` (DOUBLE), `gt_type`, `gt_globe` (VARCHAR), `gt_dim` (BIGINT), `gt_country`, `gt_region`, `gt_name` (VARCHAR), `gt_primary` (BOOLEAN), `tags` (STRUCT のリスト)。

## 実測 (2026-09-28)

| | 値 |
|---|---|
| 行数 | 29,505 (`id` の重複無し) |
| `qid` あり | 29,399 (`qid` の重複無し) |
| `gt_type`, `gt_country`, `gt_region`, `gt_name` | 全行 NULL |
| `gt_globe = 'earth'` | 全行 |
| `gt_primary = true` | 全行 |
| tag の数 | 全行 1 個 |
| `gt_dim` | 全行 1000 |
| 緯度の範囲 | -90 から 90 |
| 経度の範囲 | -179.750833 から 179.966667 |
| 本文の文字数 | 合計 234,427,662、平均 7,945、中央値 4,151、最小 83、最大 255,588 |

- 大まかな分布 (経度 -30 から 60 を欧州アフリカ、60 以上をアジアオセアニア、それ以外を南北アメリカとして): 北の欧州アフリカ 10,695、北のアメリカ 9,470、北のアジアオセアニア 5,333、南のアジアオセアニア 1,646、南のアメリカ 1,318、南の欧州アフリカ 1,043。
- 極や原点にある記事: `North Pole` (90, 0.00001)、`South Pole` (-90, 0.00001)、`Arctic` と `Islands of the Arctic Ocean` (89.9997, 0.0001)、`Magellan-Elcano circumnavigation` と `Voyages of James Cook` (0, 0)。
- 国や地域の列は全部空なので、国別の集計はこのデータだけではできない。`qid` で `wikidata-gazetteer` の `country` を引くか、座標から判定する。

## ライセンス

- カードとタグは `cc-by-sa-4.0`。`provenance.yaml` は Wikivoyage 自身の rightsinfo で確かめたと書く。
- 表示と継承 (share-alike) が要る。

## 気づいた異常

- `LICENSE` の本文が「The text in this dataset comes from the English Wikipedia」で、`wikipedia-geotagged` の `LICENSE` と同じ文面 (734 バイトで大きさも同じ)。Wikivoyage と書くべきところの写し間違いと見える。ライセンス自体は同じ CC BY-SA 4.0。
- `gt_dim` が全行 1000 で、大きさの情報になっていない。カードは「おおよその大きさ」と説明するが、Wikivoyage では既定値だけが入っていると見える (未確認)。
- `provenance.yaml` の出力先は `articles.parquet` だが、実物は `20260901.en/train-00000-of-00001.parquet`。
- 座標が `(0, 0)` の記事が 2 件あり、どちらも旅程 (航海) の記事。場所ではない。
- カードが書くとおり、旅程、旅の話題、会話帳も含まれる。3.3% が `wikidata-gazetteer` に無い、とカードにある (未実測)。

## 他のデータとの関係

- `wikipedia-geotagged` と連結できる。同じ場所の記事が `qid` で両方にある。
- `qid` で `wikidata-gazetteer` に結合して、国、種類 (`instance_of`)、人口、`sitelinks` を足せる。

## 12 ステップでの使い道 (案)

- 5 k-means / DBSCAN: 3 万点ほどの世界の旅行先。手元で回しやすい大きさで、密集地 (欧州、北米) と疎な地域の差がはっきり出る。
- 1 線形回帰, 3 Gradient Boosting: 本文の長さ (旅行ガイドとしての書き込み量) を目的変数に、`wikidata-gazetteer` から結合した人口や `sitelinks` で回帰する。
- 4 データリーク: `wikipedia-geotagged` と連結すると同じ `qid` が両方に出るので、`qid` 単位で分割する練習になる。
- 9 facility location の需要点や候補地の代用 (旅行先の点) にはなるが、需要量に当たる列は無い。
- 位置以外の列 (種類、国) がすべて空なので、単体では分類の題材にならない。
