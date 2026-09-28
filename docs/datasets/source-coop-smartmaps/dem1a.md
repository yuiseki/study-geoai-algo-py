# dem1a

2026-09-28 に読んで確かめた内容。

- `https://data.source.coop/smartmaps/dem1a/dem1a.pmtiles` (2,649,174,249 バイト、更新 2024-05-30)
- `dem1a/README.md` (298 バイト)。題は「PMTiles terrain tiles from dem1a by Geospatial Information Authority of Japan」。元データは「基盤地図情報（数値標高モデル）１ｍメッシュ（標高）」、「測量法に基づく国土地理院長承認（使用）R 6JHs 133」、Demo は <https://observablehq.com/d/c0a3f48cf7111cd2> (dem10a と同じ)。
- 基盤地図情報の版や基準日、作り方は書かれていない。

## 中身 (PMTiles のヘッダとディレクトリを Range 要求で読んだ)

- PMTiles v3、タイル形式 WebP (512x512、RGB)、タイル圧縮なし、clustered。
- ズーム 3 から 17。タイル数 1,034,775 (z17 が 774,996、z16 が 194,142、z15 が 48,856)。
- 実際にタイルがある範囲の外接矩形 (z17 のタイル座標から計算): 経度 140.749 から 142.103、緯度 36.858 から 40.233。座標から見ると茨城県北端から岩手県あたりの太平洋側で、全国ではない。
- エンコーディング: Mapbox Terrain-RGB と読むと値が妥当になる。z17 の 1 タイルで 5.4 から 56.2 m、z10 の 1 タイルで -1.4 から 512.4 m。海の画素は RGB (1,134,160) で 0.0 m。Terrarium と読むと合わない。

## 気づいたこと

- ヘッダの bounds と center が全部 0。メタデータは `{"description":"","format":"webp","name":"","type":"baselayer","version":"1"}` だけ。
- source.coop の Web ページの説明は「No Description Provided」。
- dem10a と同じ作りで、範囲は dem10a (仙台周辺) を含むもっと広い範囲。

## ライセンス

未確認。書かれているのは国土地理院の測量法に基づく使用承認番号 (R 6JHs 133) だけ。

## 学習で使うなら (案)

- 1m の細かい標高なので、狭い範囲の地形特徴量 (傾斜、起伏、凹凸) の元になる。
- ステップ 1 から 3: 地点ごとの標高、傾斜を特徴量に。ステップ 5 と 6: 地形指標を並べて k-means や PCA。
- ステップ 7: 傾斜コストの格子で最短経路。
- 範囲が東北の一部に限られる。全国で揃えるなら japan-geotiff-dem か mapterhorn-japan-bridge。
