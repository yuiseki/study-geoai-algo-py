# z.yuiseki.net/static/overture/

実測日 2026-09-28。`https://z.yuiseki.net/static/overture/` にある 2 ファイルを HEAD と範囲要求で読んで確かめた内容。

## まとめ

- 中身は Overture Maps の建物・交通・水域を全世界 z0-14 のベクタタイルにした PMTiles 1 つ (60,314,320,253 バイト)。
- もう 1 つの `divisions_country_region.parquet` は 0 バイトで、中身が無い。
- Overture の生の Parquet (places など) はここには無い。行単位のデータが要るときは本家 S3 を読む ([../stac/overture-maps.md](../stac/overture-maps.md))。

| ファイル | 大きさ (Content-Length) | Last-Modified | 中身 |
|---|---:|---|---|
| overture.pmtiles | 60,314,320,253 | 2025-09-20 10:59:04 GMT | 全世界ベクタタイル、層は building / transportation / water |
| divisions_country_region.parquet | 0 | 2026-05-31 06:36:56 GMT | 空 |

## overture.pmtiles

範囲要求で先頭 16 KiB (ヘッダとルートディレクトリ) と、メタデータ部分 4,423 バイトだけを読んだ。1 回目の末尾要求は 200 が返り (`--max-filesize` で止めた)、2 回目から 206 になった。

ヘッダ (PMTiles v3):

| 項目 | 値 |
|---|---|
| タイル形式 | MVT (tile_type 1) |
| 圧縮 | タイル gzip、ディレクトリ gzip |
| ズーム | 0 から 14 |
| 範囲 | -180, -85.0511287, 180, 85.0511287 (全世界) |
| clustered | 1 |
| アドレス付きタイル数 | 246,613,266 |
| タイルエントリ数 | 47,523,567 |
| 中身の異なるタイル数 | 36,934,865 |
| タイルデータ部 | 60,234,439,105 バイト |
| リーフディレクトリ | 79,860,341 バイト |

メタデータ:

- `name`: Overture、`type`: overlay
- `attribution`: OpenStreetMap と Overture Maps Foundation へのリンク
- `planetiler:version` 0.8.3、`planetiler:buildtime` 2024-11-11T10:25:18.054Z、`planetiler:githash` 0af757e2bfc0807d259ea78e53d78b42bc3488d1
- `tilestats` は無い

ベクタ層 (fields の数の大半は `name:xx` の多言語名):

| 層 | ズーム | 属性数 (うち name:*) | name:* 以外の属性 |
|---|---|---:|---|
| building | 13-14 | 563 (547) | class, subtype, name, height, min_height, num_floors, min_floor, level, facade_color, facade_material, roof_color, roof_direction, roof_material, roof_orientation, roof_shape, parts |
| transportation | 4-14 | 509 (490) | class, subtype, name, access, access_when, is_abandoned, is_bridge, is_covered, is_indoor, is_link, is_tunnel, is_under_construction, level, max_speed, max_speed_when, min_speed, min_speed_when, surface, width |
| water | 0-14 | 611 (605) | class, subtype, name, is_intermittent, is_salt, level |

版について:

- どの Overture リリースから作ったかは、メタデータに書かれていない。未確認。
- 分かっているのは Planetiler のビルド日時が 2024-11-11 であることだけ。それ以前に出たリリースのどれかから作ったことになる。
- ファイルの Last-Modified (2025-09-20) はビルドから 10 か月後。後から置き直したものと見える (推測)。
- 本家 STAC の最新 (2026-09-23.1) と比べると、ほぼ 2 年古い。places、addresses、divisions、base の land/land_use/land_cover などの層は入っていない。

ライセンス:

- この版そのもののライセンス表記は、メタデータの attribution (OSM と Overture) しか無い。未確認。
- 参考: 本家 STAC の現行リリースでは buildings、transportation、base/water はいずれも ODbL-1.0。

## divisions_country_region.parquet

- HEAD の Content-Length は 0。Cloudflare のキャッシュを外した GET (`cf-cache-status: MISS`) でも 200 で 0 バイトだった。オリジン側で空のファイル。
- Parquet として読めるものは何も無い。名前から、Overture の divisions を国と地域で切り出す途中で失敗した残骸と見える (推測)。

## 12 ステップでの使いどころ (案)

PMTiles は描画用のタイルで、属性は MVT に焼き込まれ、座標はタイルごとに量子化されている。学習用の表として使うには向かない。使うとしても背景地図か、狭い範囲のタイルを数枚取り出す程度。

- 7 Dijkstra/A*: transportation 層の z14 タイルから道路線を取り出して小さなグラフを作る練習。ただし線はタイル境界で切れているので、つなぎ直しが要る。経路の練習なら cesg/tokyo の Valhalla タイルや OSM から作るほうが素直。
- 1 線形回帰 / 2 Random Forest: building 層の height と num_floors などを使って高さを予測する。ただし 2024 年時点の版で、属性の欠けが多いと考えられる (未確認)。本家 S3 の buildings Parquet を範囲で読むほうがよい。
- それ以外のステップでは、結果を重ねて見るための背景地図として使う。
