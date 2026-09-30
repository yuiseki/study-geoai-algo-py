# Natural Earth

2026-09-30 に読んで確かめた内容。大きさは配布元への HEAD、レイヤー数は GitHub の `nvkelso/natural-earth-vector` のツリー API。

- `https://www.naturalearthdata.com/`。1:10m、1:50m、1:110m の 3 縮尺で全世界。
- 配布は `https://naciscdn.org/naturalearth/{scale}/{cultural|physical}/{layer}.zip`。本家サイトのダウンロードボタンもここを指す。
- GitHub に版管理された本体がある: `nvkelso/natural-earth-vector` (ベクタ) と `nvkelso/natural-earth-raster`。
- 既に `yuiseki/ne-admin0-10m` の出典として使っている ([huggingface-yuiseki/ne-admin0-10m.md](../huggingface-yuiseki/ne-admin0-10m.md))。この項目はその上流のほう。

## ライセンス

利用規約の本文 (`https://www.naturalearthdata.com/about/terms-of-use/`) を読んだ。

> All versions of Natural Earth raster + vector map data found on this website are in the public domain. You may use the maps in any manner, including modifying the content and design, electronic dissemination, and offset printing.
> No permission is needed to use Natural Earth. Crediting the authors is unnecessary.

帰属表示すら不要と明記している。ここまで緩い地理データは少ない。任意で載せるなら `Made with Natural Earth.` が本家の推奨文。

## 版が止まっている

- GitHub の最新リリースは `v5.1.2`、2022-05-13。
- 配布ファイルの `Last-Modified` も 2022-05-13 で揃っている (50m の physical には 2021-09-04 のものもある)。
- つまり 4 年以上更新されていない。行政区域の変更、国名の変更、市町村合併は反映されない。「今の世界」が要る用途には向かない。逆に、版を固定した実験には都合が良い。

## レイヤーの数

`nvkelso/natural-earth-vector` の master にある `.shp` は 804 個。うち `updates/` (454)、`packages/` (88)、`tools/` (47) を除いた実データは 215 レイヤー。

| ディレクトリ | レイヤー数 |
|---|---:|
| 10m_cultural | 84 |
| 10m_physical | 50 |
| 50m_cultural | 26 |
| 50m_physical | 23 |
| 110m_cultural | 14 |
| 110m_physical | 18 |

主なファイルの大きさ (zip)。

| ファイル | 大きさ | Last-Modified |
|---|---:|---|
| ne_10m_admin_0_countries.zip | 4,930,492 | 2022-05-13 |
| ne_10m_admin_1_states_provinces.zip | 14,909,524 | 2022-05-13 |
| ne_10m_admin_2_counties.zip | 1,919,144 | 2022-05-13 |
| ne_10m_populated_places.zip | 2,811,199 | 2022-05-13 |
| ne_50m_land.zip | 457,183 | 2021-09-04 |

## 気をつけること

admin-2 は米国だけ。 `ne_10m_admin_2_counties` は 3,224 件で、全部アメリカの郡。他の 257 の国と地域に admin-2 は無い。世界の ADM2 が要るなら [geoBoundaries](../geoboundaries/README.md) (180 の国と地域、49,363 単位)。

郡の名前は一意ではない。 3,224 件の `NAME + TYPE` は 1,957 通りしかなく、52% の行は名前が複数の州に重複する。Washington County は 30 州、Jefferson County は 25 州にある。名前だけを与えて州を答えさせる問いは、半分について答えが定まらない。日本の市区町村名はほぼ一意なので、同じつもりで扱うと破綻する。

州の列が 2 通り混ざる。 admin-2 で郡を州に結ぶのは `REGION` (`WA`)。`ISO_3166_2` は `US-53` の形と `US-WA` の形が混在していて、結合キーには使えない。

国境には見方が複数ある。 既定の配布は de facto (実効支配) の見方。Natural Earth は 33 の「国ごとの見方」も公開していて、`boundaryView` 列がそれを区別する。既定だけを使うなら、そう書いておくべき。

## 取り出し方

split。レイヤーごとに 1 ファイルに分かれていて、必要なレイヤーの zip だけ引ける。ファイルの中を部分読みすることはできない。2026-09-30 に実測した。

分割の単位はレイヤーで、10m / 50m / 110m の 3 縮尺と cultural / physical の別に分かれて実データ 215 レイヤー。1 レイヤーが 1 つの zip になっている。

`https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip` で確かめた。

| 項目 | 値 |
|---|---|
| 応答 | HTTP/2 200、`content-type: application/zip` |
| 大きさ | 4,930,492 バイト、`accept-ranges: bytes` |
| Range 要求 | `curl -r 0-1023` が 206 と 1,024 バイト |
| 先頭 | `PK\x03\x04`、最初のエントリ名は `ne_10m_admin_0_countries.README.html` |

Range 自体は 206 を返すが、zip の目録は末尾にある。4,930,460 から 4,930,491 の 32 バイトを読むと `PK\x05\x06` (End of Central Directory) が 4,930,470 から始まり、エントリ数 7、中央ディレクトリはオフセット 4,929,768 から 702 バイトと書いてあった。つまり中身を選ぼうとすれば末尾と先頭で 2 回読むことになり、しかも取り出せるのは deflate された Shapefile の塊なので、空間的に絞ることはできない。

目録も無い。`https://naciscdn.org/naturalearth/10m/cultural/` は 200 を返すが本文が空で、ファイルの一覧は出ない。レイヤー名は GitHub の `nvkelso/natural-earth-vector` のツリーから得るしかない。

もっとも、10m の国が 4.93MB、州が 14.9MB で、最大でもこの程度なので、必要なレイヤーを丸ごと落とすことに実用上の困りは無い。
