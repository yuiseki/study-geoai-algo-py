# jp-admin-2026-09

2026-09-28 に読んで確かめた内容。

- <https://huggingface.co/datasets/yuiseki/jp-admin-2026-09>
- 47 都道府県と 1,918 市区町村 (政令市の区 171 を含む) の表。コード、漢字・かな・ローマ字の名前、代表点、2020 年国勢調査の人口・世帯数、ポリゴンを 1 行に持つ。
- 最終更新 2026-09-26。
- 名前とコードはアドレス・ベース・レジストリ (abr-src-2026-09)、ポリゴンと人口は国勢調査小地域境界 (estat-boundary-2020) から作られている。provenance.yaml が 2 つの入力をコミット (3677b24、823195c) で固定している。

## ファイル

| ファイル | 大きさ (バイト) | 行数 | 列 |
|---|---|---|---|
| prefectures.parquet | 79,657,124 | 47 | 10 + geometry |
| municipalities.parquet | 149,077,415 | 1,918 | 24 + geometry |
| provenance.yaml, LICENSE, README.md | | | |

- どちらも 50MB を超えるので、ダウンロードせずに URL から読んだ。フッターと geometry 以外の列だけを読んで集計した。geometry の列は読んでいない (ジオメトリの型と範囲は未確認)。
- 行グループは 1 つ、書き出しは parquet-cpp-arrow 20.0.0。GeoParquet の geo メタデータは無い。

## 列

municipalities:

| 列 | 型 |
|---|---|
| lg_code (6 桁), code5 (5 桁), pref_code | VARCHAR |
| pref, county, city, ward と、それぞれの _kana, _roma | VARCHAR |
| name, name_roma | VARCHAR (政令市の区は「浜松市中央区」の形) |
| efct_date | VARCHAR (1947-04-17 〜 2024-01-01) |
| rep_lon, rep_lat | DOUBLE |
| population, households, small_areas | BIGINT |
| geometry_source | VARCHAR |
| geometry | WKB (BLOB) |

prefectures: pref_code, pref, pref_kana, pref_roma (VARCHAR), municipalities, population, households (BIGINT), rep_lon, rep_lat (DOUBLE), geometry。

## 中身

- lg_code と code5 はどちらも 1,918 通りで重複なし。ward が入っている行 171、county が入っている行 923。
- geometry_source: census small areas 1,889、union of its wards 20 (政令市本体)、none 9。
- population が NULL の 9 行は、北方領土の 6 村 (色丹村、泊村、留夜別村、留別村、紗那村、蘂取村) と、2024-01-01 に新設された浜松市の 3 区 (中央区、浜名区、天竜区)。カードの説明と一致する。
- 人口の合計は、ward が NULL の行だけで 126,146,099 (区と市を両方足すと 153,154,439 になり二重計上)。prefectures の population の合計も 126,146,099、households の合計 55,830,154。都道府県ごとに、市区町村 (区を除く) の合計と prefectures の値はすべて一致した。
- prefectures の municipalities 列の合計は 1,747 (= 1,918 − 171)。
- 代表点の範囲: 経度 123.00〜145.58、緯度 24.34〜45.42。
- CRS: ファイルには記録が無い。カードと provenance.yaml は JGD2000 の経緯度としている。

## 気をつけること

- 名前とコードは 2026-09 時点、ポリゴンと人口は 2020 年。浜松市の 3 区は名前だけあって形が無く、浜松市本体は 2020 年の 7 区から作った形を持つ。
- 北方領土の 6 村は、代表点がすべて同じ点 (経度 145.582903、緯度 43.330036) になっている。北方領土の島の上ではなく根室付近の座標に見える (地図では確かめていない)。代表点で距離を測る用途ではこの 6 行を外す。
- 政令市は本体と区の両方が行になっている。人口の合計や面積の合計は ward が NULL の行で取るか、区だけを取る。
- カードは「LICENSE.data に 5 つの改変を列挙」と書いているが、ファイル一覧に LICENSE.data は無く、LICENSE がある (中身は読んでいない)。

## ライセンス

- Hugging Face のタグは cc-by-4.0。
- 元はアドレス・ベース・レジストリ (デジタル庁、公共データ利用規約 PDL1.0) と国勢調査小地域境界 (e-Stat、政府標準利用規約 第2.0版)。どちらも CC BY 4.0 互換を明記していて、継承 (share-alike) は無い。2 つの出典の表示が必要。

## 12 ステップで使えそうな場面 (案)

- 1〜3 回帰と木: 市区町村を行にして、人口、世帯数、面積 (ポリゴンから計算)、代表点の緯度経度、郡に属するか (county) などで人口密度や世帯人員を予測する。特徴量は他のデータを結んで増やす前提。
- 4 データリーク: pref_code を GroupKFold の groups にする。1,747 行 (区を除く) なら手元ですぐ回せる。
- 5 k-means/DBSCAN: 代表点を人口で重み付けしてクラスタリングし、都道府県の境界と比べる。
- 7 Dijkstra/A*: 市区町村の隣接は geo-triples-jp-gov の sfTouches にすでにあるので、それを辺、代表点どうしの距離を重みにしてグラフを作る。
- 8〜9 LP/MILP、facility location: 市区町村の代表点を需要点、人口を需要量にして施設配置を解く。47 都道府県版なら小さな練習問題になる。
- 10 CP-SAT: 都道府県や市区町村の隣接グラフで地図の塗り分け (隣り合うものを別の色に) を解く。
- 12 多目的最適化: 施設配置で費用とカバー人口の二目的。
