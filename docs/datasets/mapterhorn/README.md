# Mapterhorn (本家配布)

2026-09-28 に読んで確かめた内容。

- 配布元: `https://download.mapterhorn.com/`。索引は `download_urls.json`。
- 中身は全球の標高タイル (地形タイル)。Terrarium 方式で標高を RGB に符号化した 512px の可逆 WebP を、PMTiles に束ねたもの。ベクタタイルではない。
- 本家の Data Access ページ (`https://mapterhorn.com/data-access`) の記載: 「Mapterhorn distributes Terrarium-encoded terrain rgb tiles as webp images with 512 pixel width.」
- 1 枚ずつ引く XYZ も公開されている: `https://tiles.mapterhorn.com/{z}/{x}/{y}.webp`。TileJSON (`https://tiles.mapterhorn.com/tilejson.json`) は `"encoding":"terrarium"`、`"tileSize":512` を返した。
- ミラー: Source Coop (`https://data.source.coop/mapterhorn/mapterhorn/`)。`mirrorstatus.json` を見ると、ミラー済みは一部のファイルだけ (多くのファイルの行が空)。`last_update` は 2026-09-14 06:06 UTC。

## download_urls.json の構造

```json
{"version": "0.0.13",
 "items": [{"name": "planet.pmtiles", "url": "...", "md5sum": "...", "size": 355579263191,
            "min_lon": -180.0, "min_lat": -85.05, "max_lon": 180.0, "max_lat": 85.05,
            "min_zoom": 0, "max_zoom": 12}, ...]}
```

- `version` は `0.0.13`。日付ではなく版番号で、ファイル名にも URL にも版は入っていない (URL は固定で中身が差し替わる)。
- ファイルは 459 個 (索引 161,912 バイト)。md5 は 459 個すべて違う。

| 種類 | 個数 | ズーム | 合計バイト数 | 備考 |
|---|---:|---|---:|---|
| planet.pmtiles | 1 | 0-12 | 355,579,263,191 | 全球 |
| 6-{x}-{y}.pmtiles | 458 | 13 から (最大 13-18) | 9,578,376,220,504 | z6 のタイル 1 枚分の範囲ごと |

- 地域別ファイルの名前は z6 のタイル番号 `6-x-y`。最大ズームは地域で違う: z13 のみ 155 個、z13-14 が 102、z13-15 が 53、z13-16 が 93、z13-17 が 43、z13-18 が 12。高精度の元データがある地域ほど深い。
- 地域別の大きさは 299 バイトから 614,918,478,203 バイト (6-33-22、スイス周辺、z13-18)。299 バイト以下のものが 19 個あり、6-0-20 のヘッダを読むと 4,096 タイルがすべて同じ 52 バイトのタイル 1 枚を指していた (中身の無い海の範囲と読める)。
- 東京を含むのは `6-56-25.pmtiles` (65,616,250,120 バイト、z13-16、md5 `d824e9b63839674699469fcee98ff228`、Last-Modified 2026-09-13)。

## planet.pmtiles (Range 要求でヘッダとメタデータを読んだ)

- HEAD: `Content-Length` 355,579,263,191、`Last-Modified` 2026-09-11 14:58:22 GMT、Cloudflare 配信。Range 要求は 206 を返す。
- md5 (索引の値): `4bf586b043f7619d9a9442b43c163f36`。
- PMTiles v3、clustered、内部圧縮 gzip、タイル圧縮 none、タイル形式 4 (WebP)。
- ズーム 0-12。bounds は全球 (-180, -85.0511287, 180, 85.0511287)、center (0, 0) の z6。
- addressed tiles 13,485,266、中身のあるエントリ 9,394,750、中身の違うタイル 9,316,839。
- メタデータは attribution だけ: `<a href="https://mapterhorn.com/attribution">© Mapterhorn</a>`。符号化方式はメタデータに無く、本家のページと TileJSON に書いてある。

## 標高の符号化 (タイルをデコードして確かめた)

- Terrarium: `elevation = (R * 256 + G + B / 256) - 32768` (m)。
- z0 の 1 枚: 512x512、VP8L (可逆)。Terrarium で -71.0 から 5,604.0 m。Mapbox Terrain-RGB の式だと 827,043 m 以上になり、明らかに合わない。
- 富士山頂を含む z12 (3626, 1617): 1,304.5 から 3,771.0 m。z12 の平均化で山頂 (3,776 m) より少し低いと読める。
- 東京タワー付近 z13 (7275, 3226): -2.0 から 36.5 m。z16 (58207, 25811): 6.8125 から 29.5 m。

## z.yuiseki.net の複製 (2026-01-06 版) との比較

同じ版ではない。本家は新しい版に置き換わっている。

| | 本家 (0.0.13) | z.yuiseki.net 2026-01-06 |
|---|---:|---:|
| planet.pmtiles のバイト数 | 355,579,263,191 | 663,868,447,387 |
| addressed tiles | 13,485,266 | 13,532,395 |
| 中身のあるエントリ | 9,394,750 | 9,396,124 |
| z0 タイルのバイト数 | 121,656 | 245,114 |
| 富士山 z12 タイルのバイト数 | 143,580 | 370,622 |

- 大きさが約半分になった理由は、標高の量子化と読める。B チャンネル (1 m 未満の端数) の値の種類を数えると、本家は z0 で 1 種類 (0 だけ、1 m 刻み)、z12 で 2 種類 (0 と 128、0.5 m 刻み)、z13 で 4 種類 (0.25 m 刻み)、z16 で 32 種類 (1/32 m 刻み)。複製 (2026-01-06) は z0 も z12 も 256 種類あった。ズームが上がるほど細かく刻む方式に変わったと考えると説明できる。
- 同じタイルを本家と複製でデコードした差: z0 で最大 17.46 m、平均 0.137 m。富士山 z12 で最大 11.75 m、平均 0.140 m。量子化だけなら差は刻み幅 (z0 で 1 m、z12 で 0.5 m) 以内のはずなので、元データの差し替えもあると読める (確かめていない)。
- 本家の過去版を置いている場所は見つからなかった。2026-01-06 版は z.yuiseki.net の複製でしか読めない可能性がある。

## 元にしている標高データとライセンス

- `https://download.mapterhorn.com/attribution.json` (94,917 バイト) に 151 件。各件に source、name、producer、license、license_pdf、resolution、access_year、元データの tar の URL と大きさがある。元データの tar の合計は 19,760,172,544,000 バイト。
- 全球の土台は Copernicus GLO-30 (30 m、「COPERNICUS full, free and open license」)。本家トップの一覧は「Global, 30 m」から始まり、国や州ごとの高精度データ (0.25 m から 20 m) で上書きしている。
- 解像度の内訳 (件数): 1 m が 75、5 m が 30、0.5 m が 19、10 m が 10、2 m が 9、ほか。
- ライセンスの書き方はばらばら (表記ゆれ込みで 30 種類)。多いのは CC BY 4.0 系 (表記ゆれを合わせて 50 件超)、Public Domain (U.S. Government Work) 34、Licence Ouverte 2.0 が 21、Datenlizenz Deutschland 系、CC0 系。
- 日本: 国土地理院の基盤地図情報 数値標高モデル 6 件 (jpdem1a 1 m、jpdem5a/5b/5c 5 m、jpdem10a/10b 10 m)。ライセンス欄は「国土地理院コンテンツ利用規約／測量法に基づく国土地理院長承認（使用）R 8JHs 131」。
- Mapterhorn 全体としてのタイルのライセンスは、読んだページ (トップ、Attribution、Data Access) には書いていなかった。未確認。使うときは少なくとも「© Mapterhorn」と attribution ページへのリンクを表示し、使う範囲の元データごとの条件 (国土地理院の出典表示など) に従う。

## 気づいた異常

- cng-data-antigravity の README と `sources/mapterhorn_pmtiles.py` は Mapterhorn を「Global OSM-based vector tiles」と書いているが、誤り。本家の説明、TileJSON、ヘッダのタイル形式 (WebP)、デコード結果のどれもが、標高のラスタタイル (Terrarium) であることを示す。OSM とも関係が無い。
- 同ツールの `fetch_planet_entry()` は `download_urls.json` の `items` から `planet.pmtiles` を探す。この構造は今の索引と合っている。ただし planet は z12 までで、z13 以上は 458 個の地域別ファイルにある。bbox で切り出すときに planet だけを見ると高ズームが抜ける。
- URL は固定のまま中身が差し替わる。2026-01-06 版から今の版で、同じタイルの標高が最大 17 m 変わった。学習に使うときは `version` と md5 を記録する。
- 索引の bounds と PMTiles ヘッダの bounds が地域別ファイルでずれる: 6-56-25 は索引で min_lat 31.952、ヘッダで 32.3986。ヘッダのほうは中身のある範囲に縮めていると読める。

## 学習ステップでの使いどころ (案)

- 点に標高と傾斜 (隣の画素との差) を付けて、1 線形回帰、2 Random Forest、3 XGBoost の特徴量にする。11 SHAP で標高の効き方を見る。
- 4 Cross Validation: 標高は空間的に強く相関するので、ランダム分割と空間ブロック分割で評価が変わる様子を見る題材になる。
- 6 PCA: 標高、傾斜、起伏などの地形量をまとめて主成分に落とす。
- 7 Dijkstra/A*: 標高差を辺のコストにして登りを避ける経路。12 多目的最適化で距離と累積標高の二つを天秤にかける。
- 9 facility location: 標高 (浸水しにくさ) を候補地の条件にする。
- 全体は巨大なので、`pmtiles extract --bbox` (本家の手順) か Range 要求で必要な範囲だけを引く。東京なら planet から z12 まで、`6-56-25.pmtiles` から z13-16。
