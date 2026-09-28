# tokyo-ckan

2026-09-28 に読んで確かめた内容。

- `https://stac.yuiseki.net/tokyo-ckan/`
- 1 組織 = 1 コレクション、1 データセット = 1 Item、1 ファイル = 1 asset。
- 区市町村をまたいで比べるなら「共通項目」(families) から。43 種類あり、うち 23 種類はデジタル庁の自治体標準オープンデータセット。

気をつけること:

- CKAN には場所も時刻も無いので、どちらも推定値。どう推定したかが `tokyo:footprint_basis` と `tokyo:datetime_basis` に書いてある。
- 場所は公開した組織の管轄区域の矩形。データの点がその中にあるとは限らない。
- 時刻がデータの時期を表すのは、`datetime_basis` が `resource-name` か `dataset-title` のものだけ。
- 同じ名前のデータセットでも列構成が同じとは限らない。`family_layout_match` で確かめる。
