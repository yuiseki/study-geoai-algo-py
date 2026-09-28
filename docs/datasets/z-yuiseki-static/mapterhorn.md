# mapterhorn

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/mapterhorn/`
- 中身は `2026-01-06/planet.pmtiles` の 1 ファイルだけ。[Mapterhorn](https://mapterhorn.com/) が配っている全球の標高タイル (地形タイル) の複製。
- ディレクトリ名の 2026-01-06 が版 (Mapterhorn 側のリリース日) と読める。ファイルの Last-Modified は 2026-01-07。
- SHA256SUMS や README は置いていない (`mapterhorn/` 直下と `2026-01-06/` の両方で 404)。

## ファイル

| ファイル | バイト数 | 形式 | ズーム | タイル | タイル数 |
|---|---:|---|---|---|---:|
| 2026-01-06/planet.pmtiles | 663,868,447,387 | PMTiles, webp | 0-12 | 512px (最初のタイル) | 13,532,395 |

- 大きさは HEAD の `Content-Length`。
- PMTiles v3、clustered、内部圧縮 gzip、タイル圧縮 none。
- bounds は全球 (-180, -85.0511287, 180, 85.0511287)、center は (0, 0) の z6。
- タイル数はヘッダの addressed tiles。中身のあるエントリは 9,396,124、中身の違うタイルは 9,318,520。z0-12 の全タイル数 (22,369,621) より少ないので、海など省かれたタイルがある。
- 最初のタイル 1 枚は WebP の可逆形式 (VP8L)、512x512。標高を RGB に符号化した画像を劣化させないための可逆と読める。
- メタデータは attribution だけ: `<a href="https://mapterhorn.com/attribution">© Mapterhorn</a>`。name、description、符号化方式 (Terrarium か Mapbox RGB か) は書いていない。

## 気づいたこと

- 標高の符号化方式がメタデータに無い。デコードの式を決める前に、Mapterhorn の文書で確かめる必要がある (今回は未確認)。
- z12 までしか無い。Mapterhorn が z13 以上を別ファイルで配っているかは、ここでは確かめていない。
- 版は 2026-01-06 の 1 つだけ。古い版は置いていない。

## ライセンス

- 未確認。メタデータは attribution ページへのリンクだけで、そのページ (`https://mapterhorn.com/attribution`) は元データの一覧を `https://download.mapterhorn.com/attribution.json` に置いていると書いている。元データごとにライセンスが違う可能性があり、中身は読んでいない。
- 使うときは少なくとも「© Mapterhorn」とリンクの表示が要る。

## 学習ステップでの使いどころ (案)

- 標高は多くの地理的な問いで効く説明変数。点に標高 (と、隣のタイルとの差から傾斜) を付けて 1 線形回帰や 2 Random Forest、3 XGBoost の特徴量にする。11 SHAP で標高がどれだけ効いたかを見るのにも向く。
- 標高差や傾斜を辺のコストにすれば 7 Dijkstra/A* で「登りを避ける経路」が作れる。12 多目的最適化で距離と登りの二つを天秤にかける題材にもなる。
- 9 facility location で、標高 (浸水しにくさ) を施設候補の条件にする使い方もある。
- 全体は 663GB あるので、PMTiles の範囲要求で必要なタイルだけを引く。全球の粗い標高なら planetarble/ETOPO_2022_15s_bed.tif (3.5GB) のほうが扱いやすい。
