# mobility-gtfs-pmtiles

2026-09-28 に読んで確かめた内容。

- `https://source.coop/smartmaps/mobility-gtfs-pmtiles`
- MobilityData の Mobility Database Catalog にある、有効な (active) GTFS をすべて取り込んで 1 つの PMTiles にしたもの (リポジトリ内 README.md より)。README には「作業中で、データは更新される」とある。
- 取得と変換のスクリプトは <https://github.com/optgeo/mmx-gtfs> (Mobility Database の Refresh Token が要る)。
- 基準日: ファイルの更新日時は 2024-04-28。フィードの取得日はファイル内に記録が無く未確認。

## ファイル

| ファイル | 大きさ (バイト) | 更新日時 |
|---|---:|---|
| README.md | 468 | 2024-04-28 |
| mobility.pmtiles | 685,198,437 | 2024-04-28 |

## 中身 (mobility.pmtiles のヘッダとメタデータ)

- PMTiles v3、タイル形式 MVT、タイル圧縮 gzip、clustered。
- ズーム: ヘッダは 1 から 14。メタデータの minzoom は 0。
- 範囲 (bounds): -158.23, -45.95, 178.14, 85.05 (北端はメルカトルの上限)。
- タイル数: addressed 896,699、entries 896,294、contents 892,751 (同じ中身のタイルが一部共有されている)。
- 生成: `tippecanoe v2.28.0`, `tippecanoe -f -o a.mbtiles '--maximum-zoom=14' --drop-densest-as-needed a.jsons`。`--drop-densest-as-needed` なので低ズームでは地物が間引かれている。

レイヤー (tilestats の地物数とジオメトリ型):

| レイヤー | 地物数 | 型 | 属性 |
|---|---:|---|---|
| aggregated_routes | 1,656,280 | LineString | agency_id, agency_name, frequency (1 から 42,717), next_stop_id, next_stop_name, prev_stop_id, prev_stop_name |
| aggregated_stops | 691,511 | Point | count (1 から 47,685), similar_stop_id, similar_stop_name |
| routes | 90,410 | LineString | route_id, route_name |
| stops | 1,593,628 | Point | route_ids (JSON 配列の文字列), stop_id, stop_name |

## 気づいた異常

- メタデータの name と description が `a.mbtiles` のまま。
- ヘッダの minzoom (1) とメタデータの minzoom (0) が食い違う。
- stop_id, route_id, stop_name に前後の空白が残っている値がある (例: `'       175'`, `'     14425'`)。フィード間で ID を突き合わせるときは正規化が要る。
- stop_id に負の値の文字列 (`-187` など) がある。
- ID はフィードごとの ID で、stops と routes にはフィードを区別する列が無い。別フィードの同じ ID が衝突しうる。

## ライセンス

- 未確認。GTFS はフィードごとに提供者の利用条件が違い、このファイルにはフィードごとの条件が記録されていない。使う前に Mobility Database で個々のフィードの条件を確かめる。
- 変換スクリプトの GitHub リポジトリ (optgeo/mmx-gtfs) の LICENSE は CC0 1.0。これはコードの条件。

## 12 ステップでの使いみち (案)

- 7 Dijkstra / A*: aggregated_routes の停留所間の線をグラフの辺にし、frequency を重みに使う。ただしタイルから取り出すとタイル境界で線が切れるので、つなぎ直しが要る。本格的にやるなら元の GTFS を使うほうが素直。
- 5 DBSCAN: stops の点から停留所の密集地をクラスタリングする。aggregated_stops がすでに近接停留所をまとめたものなので、自分の結果と比べられる。
- 9 facility location: 停留所を候補地や需要点にする。
- 1, 3 回帰 / GBDT: H3 などで集計した停留所数や運行頻度を、人口 (h3ys-worldpop) などから予測する。
