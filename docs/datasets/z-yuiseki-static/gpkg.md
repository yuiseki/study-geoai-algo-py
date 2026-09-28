# gpkg/

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/gpkg/`
- Natural Earth のベクターを 1 つにまとめた GeoPackage が 1 つ。

## ファイル

| ファイル | Content-Length (バイト) | Last-Modified | 中身 |
|---|---|---|---|
| natural_earth_vector.gpkg | 885,293,056 | 2025-10-04 01:52:18 GMT | GeoPackage |

- 先頭 100 バイトだけ Range で読んだ。SQLite 3 形式、application_id は `GPKG`、user_version は 10200 (GeoPackage 1.2)。
- ページサイズ 4096 バイト、ページ数 216,136。掛けると 885,293,056 で Content-Length と一致する。
- `natural_earth_vector.gpkg` は Natural Earth が全レイヤーをまとめて配る GeoPackage と同じ名前だが、同一のものかは確かめていない。Natural Earth の版も未確認。

## レイヤー一覧: 60 秒以内に読めなかった

- ogrinfo (`/home/yuiseki/anaconda3/bin/ogrinfo -ro -so -q /vsicurl/...`) は「Range downloading not supported by this server!」で開けなかった。3 回試して 3 回とも同じ。
- curl で確かめたこと (各 1 回):
  - `Range: bytes=0-16383` を `Accept-Encoding: gzip` 付きで送ると 200 (全体の送信) が返った。
  - 同じ Range を `Accept-Encoding: identity` で送ると 206 が返った。
  - ヘッダーを付けない curl は 206 だった。
  - GDAL の詳細ログでは、Range 付きの GET に 200 (cf-cache-status: BYPASS) が返っていた。
- もしも前段の Cloudflare が圧縮を受け付ける要求には Range を無視して全体を返すのだとすれば、GDAL が開けないことを説明できる。`CPL_CURL_GZIP=NO` と `GDAL_HTTP_HEADERS="Accept-Encoding: identity"` を 1 回ずつ試したが、どちらも同じエラーだった。深追いはしていない。
- kontur/ の .gpkg も同じエラーで開けなかった。GDAL で直接読みたいなら、この点を先に解決するか、ファイルを手元に落として読む (885MB)。

## natural-earth/ との重なり

- natural-earth/ の 3 つ (ne_110m_admin_0_countries, ne_50m_admin_0_countries, ne_10m_admin_1_states_provinces) が、この GeoPackage にレイヤーとして入っているかは、レイヤー一覧が読めなかったので確かめていない。
- 形式の違いは確か: natural-earth/ は列を絞った GeoParquet、こちらは GeoPackage。
- こちらが 885MB あるので、3 レイヤーより多くのもの (海岸線、河川、都市、道路など) が入っている可能性はあるが、未確認。

## ライセンス

- Natural Earth の Terms of Use に「All versions of Natural Earth raster + vector map data found on this website are in the public domain.」とある。このファイルが Natural Earth の配布物そのままかは未確認。

## 12 ステップで使えそうな場面 (案)

中身を確かめていないので、Natural Earth の一般的なレイヤーがあると仮定した案。

- 7 Dijkstra/A*: 道路や鉄道のレイヤーがあればグラフにして経路を解く。
- 9 facility location: 都市 (populated places) の点を需要点や候補地にする。
- 5 k-means/DBSCAN: 都市の点の空間クラスタリング。
- 表の学習には natural-earth/ の GeoParquet のほうが手軽。
