# Overture Maps

2026-09-28 に読んで確かめた内容。

- `https://stac.overturemaps.org/catalog.json` がリリース一覧。最新は `2026-09-23.1`。
- テーマ 6 つ、種類 15 個。各種類の `collection.json` に行数、列名、Parquet の置き場所がある。
- S3 の Parquet は Range 要求に 206 を返すので、DuckDB などで必要な範囲だけ読める。
- テーマごとに PMTiles もある (`tiles.overturemaps.org`)。

| テーマ / 種類 | 行数 | ライセンス |
|---|---:|---|
| addresses/address | 474,186,531 | other |
| base/bathymetry | 407,277 | CC0-1.0 |
| base/infrastructure | 157,617,917 | ODbL-1.0 |
| base/land | 75,848,834 | ODbL-1.0 |
| base/land_cover | 123,302,114 | CC-BY-4.0 |
| base/land_use | 56,097,254 | ODbL-1.0 |
| base/water | 66,204,219 | ODbL-1.0 |
| buildings/building | 2,533,842,612 | ODbL-1.0 |
| buildings/building_part | 4,486,107 | ODbL-1.0 |
| divisions/division | 4,688,229 | ODbL-1.0 |
| divisions/division_area | 1,080,667 | ODbL-1.0 |
| divisions/division_boundary | 87,530 | ODbL-1.0 |
| places/place | 81,455,423 | other |
| transportation/connector | 421,978,977 | ODbL-1.0 |
| transportation/segment | 352,054,710 | ODbL-1.0 |

`other` の places と addresses は、元データごとに条件が違う。<https://docs.overturemaps.org/attribution/> を見る。
