# opencellid

2026-09-28 に読んで確かめた内容。

- `https://source.coop/smartmaps/opencellid` (source.coop 上の題名は「OpenCellid PMTiles - FOIL4G (Free and Open Information Library for Geospatial)」)
- OpenCelliD (<https://opencellid.org/>) の携帯電話基地局 (セル) の位置データを PMTiles にしたもの。リポジトリ内に README.md は無い。
- source.coop のページの説明欄 (YAML 風の記述) による出どころ: `data_id: opencellid_full`、`file_format: gzipped_csv`、`file_size: 105MB`、取得元 `https://opencellid.org/ocid/downloads?token={api_key}&type=full&file=cell_towers.csv.gz`。つまり全件版の CSV から作ったもの。
- 基準日: 属性 `updated` の最大値が 1718409542 (2024-06-14T23:59:02Z)、ファイルの更新日時が 2024-06-15。2024-06-14 時点の全件版と見られる。

## ファイル

| ファイル | 大きさ (バイト) | 更新日時 |
|---|---:|---|
| cellid.pmtiles | 559,569,057 | 2024-06-15 |

## 中身 (ヘッダとメタデータ)

- PMTiles v3、タイル形式 MVT、タイル圧縮 gzip、clustered。
- ズーム 0 から 14。タイル数 1,364,455 (addressed = entries = contents)。
- 範囲 (bounds): -175.34, -54.84, 179.33, 78.23。
- 生成: `tippecanoe v2.28.0`, `tippecanoe -o a.pmtiles -f '-L{"file": "", "format": "csv"}'` (CSV を標準入力から読んでいる)。`--drop-densest-as-needed` などの指定は無い。
- レイヤーは `a` の 1 つ。tilestats の地物数 4,835,586、ジオメトリは Point。

属性 (値の範囲は tilestats の min / max):

| 属性 | 型 | 範囲や値 |
|---|---|---|
| radio | String | CDMA, GSM, LTE, NR, UMTS の 5 種 |
| mcc | Number | 202 から 748 (国コード) |
| net | Number | 0 から 20,002 (事業者コード) |
| area | Number | 0 から 16,777,214 |
| cell | Number | 0 から 59,650,502,930 |
| unit | Number | -1 から 511 |
| range | Number | 500 から 99,488 |
| samples | Number | 1 から 201 |
| changeable | Number | 1 のみ |
| created | Number | 0 から 1718409244 (Unix 時刻) |
| updated | Number | 1671062408 (2022-12-15) から 1718409542 (2024-06-14) |
| averageSignal | Number | 0 のみ |

## 気づいた異常

- `averageSignal` は全件 0、`changeable` は全件 1 で、情報を持たない。
- `created` の最小値が 0 (1970-01-01) で、欠損が 0 で埋められていると見られる。
- `updated` の最小値が 2022-12-15 で、それ以前の更新日が無い。取り込みの都合で一括更新された可能性があるが未確認。
- `range` の最小値が 500 で、500 未満の値が無い。下限で丸められているかは未確認。
- レイヤー名が `a`、メタデータの name が `a.pmtiles` で、中身を表さない。
- `cell` が最大 596 億で、倍精度の範囲内だが 32 bit 整数には収まらない。

## ライセンス

- source.coop のページの説明欄に `license: CC-BY-SA-4.0`、`attributions: OpenCelliD, https://opencellid.org/` とある。
- OpenCelliD 本家の条件と一致するかは、ここでは確かめていない。

## 12 ステップでの使いみち (案)

- 5 k-means / DBSCAN: 基地局の点を都市ごとにクラスタリングする。radio 別に密度の違いを比べる。
- 2, 3 決定木 / GBDT: 位置と samples, range から radio (GSM / UMTS / LTE / NR) を分類する。
- 4 CV とデータリーク: 同じ場所に複数の radio の局が重なりうるので、ランダム分割だと位置で答えが漏れる。空間ブロック CV の題材。
- 9 facility location / set cover: 既存局の range を被覆半径として、人口 (h3ys-worldpop) を覆う最小の局の組を選ぶ。
- 注意: 使うには MVT をデコードする必要がある。元の CSV (105MB) を直接使うほうが楽だが、取得には OpenCelliD の API キーが要る。
