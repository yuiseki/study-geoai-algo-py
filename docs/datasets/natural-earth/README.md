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

## GeoPackage 一式 (natural_earth_vector.gpkg)

2026-10-02 に読んで確かめた内容。手元のファイルは sqlite3 の読み取り専用モードだけで開いた。配布元の zip は落としておらず、HEAD と、zip 末尾の中央ディレクトリと小さなメンバー (VERSION、README.md、CHANGELOG) だけを Range で読んだ。

### 何か

- 全テーマのベクターを 1 つにまとめた GeoPackage。本家のダウンロードページ (`https://www.naturalearthdata.com/downloads/`) の「Download all vector themes as ... GeoPackage (436 mb)」のリンク先、`https://naciscdn.org/naturalearth/packages/natural_earth_vector.gpkg.zip` の中身。
- 版は 5.1.2。ファイルの中に版番号は無く、同梱の VERSION が `5.1.2`、CHANGELOG の先頭が `2022-05-13: 5.1.2`。GitHub の最新リリースと同じ版 (上の「版が止まっている」)。
- 形式は SQLite 3、application_id は `GPKG`、user_version は 10200 (GeoPackage 1.2)。885,293,056 バイト。
- レイヤーは `gpkg_contents` に 183、すべて features。縮尺別に 10m が 116、50m が 42、110m が 25。型は POLYGON 108、LINESTRING 47、POINT 28。
- 地物数の合計 (`gpkg_ogr_contents`) は 350,371。
- 座標系は 182 レイヤーが EPSG:4326。`ne_10m_admin_0_names` だけ srs_id 0 (未定義の地理座標系) で、変換するときに注意が要る。
- `gpkg_metadata` の 183 行は GDAL が Shapefile から変換したときの `DBF_DATE_LAST_UPDATE` と文字コード (UTF-8) だけ。値は 2017-07-06 から 2022-05-13。
- GitHub の実データ 215 レイヤー (上の「レイヤーの数」) に対してこちらは 183。差の内訳は未確認。

主なレイヤー。

| レイヤー | 型 | 地物数 |
|---|---|---:|
| ne_10m_admin_0_countries | POLYGON | 258 |
| ne_10m_admin_1_states_provinces | POLYGON | 4,596 |
| ne_10m_admin_2_counties | POLYGON | 3,224 (米国のみ) |
| ne_10m_populated_places | POINT | 7,342 |
| ne_10m_roads | LINESTRING | 56,600 |
| ne_10m_railroads | LINESTRING | 25,413 |
| ne_10m_airports | POINT | 893 |
| ne_10m_urban_areas | POLYGON | 11,878 |
| ne_10m_time_zones | POLYGON | 120 |
| ne_110m_admin_0_countries | POLYGON | 177 |

### 配布元と手元のコピーの照合

配布元の zip への HEAD は HTTP 200、content-length 446,353,155、last-modified 2022-05-14 05:28:19 GMT、etag `"8d0a059e3e051f01cd206fdf006df3b6"`。中央ディレクトリのメンバーは 4 つ。

| メンバー | 圧縮後 | 展開後 | CRC-32 |
|---|---:|---:|---|
| packages/natural_earth_vector.gpkg | 446,315,480 | 885,293,056 | 0x47115ba4 |
| VERSION | 7 | 7 | |
| README.md | 1,979 | 4,692 | |
| CHANGELOG | 35,037 | 149,106 | |

z.yuiseki.net に置いてあるコピー (`/sata_hdd_24tb/www/html/static/gpkg/natural_earth_vector.gpkg`、`https://z.yuiseki.net/static/gpkg/`、Last-Modified 2025-10-04 01:52:18 GMT) は、ファイル全体の CRC-32 が 0x47115ba4、大きさが 885,293,056 バイトで、どちらも zip の記録と一致した。`gpkg_contents.last_change` も全レイヤーが 2022-05-13T22:59 から 23:00 (UTC) で、GitHub の v5.1.2 リリース (2022-05-13T23:24:34Z) の直前。配布物を展開して無改変で置いたものと判断している。

- CRC-32 は暗号学的ハッシュではない。sha256 での照合は zip 本体を落とす必要があるので行っていない (未確認)。
- z.yuiseki.net に置いたときの取得手順と取得元 URL の記録は見つけていない (未確認)。
- 2026-09-28 時点の [z-yuiseki-static/gpkg.md](../z-yuiseki-static/gpkg.md) では Natural Earth の配布物と同一かを未確認としていた。上の照合がその答えになる。

### ライセンスの補足

ライセンスの本文は上の「ライセンス」の節と同じ (GitHub の LICENSE.md も見出しが「Everything here is public domain.」で同文)。この節で足すのは第三者データのこと。

利用規約のページ (`https://www.naturalearthdata.com/about/terms-of-use/`、2026-10-02 に読んだ) には、Natural Earth 宛ての許諾が 4 者分載っている。どれも「Natural Earth is hereby granted a non-exclusive license to use the data being provided by ... for the sole purpose of creating a world base map」という同じ形の文面。

| 提供者 | 対象 |
|---|---|
| The Washington Post | 記載なし (世界の基図の作成用) |
| European Commission, Joint Research Centre, Institute for Environment and Sustainability | 河川と湖 (欧州のみ) |
| XNR Productions | 道路 (北米のみ) |
| International Mapping Associates, Inc. | タイムゾーン |

- これらは Natural Earth への非独占の許諾で、そこに由来する部分の権利関係を Natural Earth の public domain 宣言がどこまで覆うかは、規約の文面からは判断できない (未確認)。Natural Earth 自身は全体を public domain として配っている。
- 同じページに、20 以上の言語の名前は Wikidata (CC0) から取ったとある。
- 「public domain」の宣言が日本などの各国法でどう扱われるかも未確認。CC0 のような整えられた放棄文書ではない。

### 国境の見方と係争地

- 既定は de facto。国のページ (`https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/`、2026-10-02) に「Natural Earth shows de facto boundaries by default according to who controls the territory, versus de jure.」とある。
- この GeoPackage には国ごとの見方 (point of view) の変種 `ne_10m_admin_0_countries_xxx` が 33 レイヤー入っている: arg, bdg, bra, chn, deu, egy, esp, fra, gbr, grc, idn, ind, iso, isr, ita, jpn, kor, mar, nep, nld, pak, pol, prt, pse, rus, sau, swe, tlc, tur, twn, ukr, usa, vnm。
- 係争地のレイヤー (`*_disputed_areas`、`*_breakaway_disputed_areas`) と、南極の領有主張 (`ne_10m_admin_0_antarctic_claims`) も入っている。特定の国の見方では受け入れられない境界や主張を含むので、使うときは既定が de facto であることを書いておく。

### yuiseki/ne-admin0-10m との重なり

- `https://huggingface.co/datasets/yuiseki/ne-admin0-10m` (lastModified 2026-09-26) は 10m の admin-0 (258)、admin-1 (4,596)、admin-2 (3,224) の 3 レイヤーを、レイヤー別 zip と Parquet で持っている。この GeoPackage の同名 3 レイヤーと件数は一致する。
- admin-0 と admin-2 は、HF の Parquet を NE_ID で突き合わせて属性 168 列と 61 列を比べ、差は 0 行だった。HF 側が足した 4 列 (`geometrySource`、`datasetVersion`、`boundaryView`、`adminLevel`) は除いた。
- ジオメトリの一致と admin-1 の属性の一致は比べていない (未確認)。
- 版の表記が違う。HF 側は 5.1.1 (本家のレイヤー別ページも version 5.1.1 と表示し、HF のカードはレイヤー別 zip の VERSION.txt が 5.1.1 だと書いている)。GeoPackage 側は 5.1.2。CHANGELOG では 5.1.1 から 5.1.2 の変更は populated places の Londonderry/Derry の表記と `ne_50m_admin_0_boundary_lines_disputed_areas` への TLC の見方の追加だけで、10m の admin-0/1/2 は変わっていない。内容が同じことと矛盾はしない。
- 重なるのは 183 レイヤー中この 3 つだけ。残りの 180 (国ごとの見方 33、海岸線、河川、道路、鉄道、都市、50m と 110m の全部など) は HF に無い。

### 取り出し方

whole。2026-10-02 に実測した。

- 配布元の zip は 446,353,155 バイト。`curl -r 0-1023` は 206 と 1,024 バイトを返すが、中身は 446,315,480 バイトに圧縮された GeoPackage 1 つで、その中の一部だけを取り出すことはできない。全部落として展開するしかない。
- z.yuiseki.net の展開済みのコピー (885,293,056 バイト) は SQLite なので、Range が確実に効けば必要なページだけ読める形ではある。ただし応答が安定しない。
  - 1 回目の `curl -r 0-1023` (Accept-Encoding: identity) は 200 (全体の送信) で、その直前の HEAD は cf-cache-status: MISS だった。続けて送った gzip 付きは 206。その後 identity、gzip、ヘッダー無しを 3 回ずつ送ると 9 回とも 206 (cf-cache-status: BYPASS)。
  - `ogrinfo -ro -so /vsicurl/...` は「Range downloading not supported by this server!」で開けなかった。詳細ログでは、Range 付きの最初の GET に 200 (BYPASS) が返り、そこで GDAL が諦めていた。2026-09-28 の 3 回と合わせて 4 回とも同じ。
  - 885MB は、z.yuiseki.net で以前に確かめた Cloudflare のキャッシュの上限 512MB を超えている。前段が初回の Range を無視しているとすれば説明できるが、原因は未確認。
- 一部のレイヤーだけが要るなら、上の「取り出し方」のレイヤー別 zip (split) のほうが軽い。全部が要るなら zip 446MB を落とすか、z.yuiseki.net の展開済みのもの 885MB を落とす。
