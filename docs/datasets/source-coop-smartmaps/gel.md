# gel

2026-09-28 に読んで確かめた内容。数字はすべてこの日の実測。

- `https://source.coop/smartmaps/gel` (Web ページの名前は "Smart Maps Global Elevation Tiles")
- 全世界の標高を RGB に詰めたタイル (terrain RGB) を 1 つの PMTiles にしたもの。UN Smart Maps Group の成果。
- `README.md` (2,030 バイト) がある。以下の出典や日付は README による。

## 元データと作り方 (README による)

- ズーム 6 から 12: NASADEM (SRTM を ASTER GDEM と ALOS 30m DEM で補ったもの、約 30m)。
- ズーム 2 から 5: 地球地図 (Global Map, ISCGM)。
- 変換は 2022 年 10 月。
- 範囲: ズーム 2 から 5 は北緯 85 度から南緯 85 度、ズーム 6 から 12 は北緯 60 度から南緯 56 度。
- Web ページの説明: "WEBP elevation tiles, with mapbox pixel packing" (Mapbox の terrain RGB の符号化)。
- 技術的な詳細は README が挙げる Qiita の記事 2 本にある (読んでいない)。

## ファイル

| key | 大きさ (バイト) | 更新 |
|---|---:|---|
| `README.md` | 2,030 | 2024-04-16 |
| `gel.pmtiles` | 195,962,954,103 (195.96GB) | 2024-04-10 |

README は大きさを "182.5 GB" と書く。195,962,954,103 バイトを 2^30 で割ると 182.5 なので、GiB で書いた値と見れば一致する。

## 中身 (PMTiles ヘッダとメタデータ)

- PMTiles v3、内部ディレクトリは gzip、clustered。
- ズーム 2 から 12。
- タイル数 (addressed) 5,085,551、中身の数 (contents) 2,705,287。中身の数が半分ほどなので、同じタイル (海など) の重複が多いと見られる。
- 先頭のタイルの先頭バイトは `RIFF....WEBPVP8L` で、可逆 WebP だった (1 枚だけ確かめた)。

## 気づいたこと

- ヘッダの tile_type が 0 (unknown)、tile_compression も 0 (unknown)。実際は WebP なので、ヘッダだけを見るビューアやライブラリは形式を判定できない可能性がある。
- ヘッダの bounds と center がすべて 0。
- メタデータ JSON が `{}` (26 バイト、gzip 込み) で空。出典もズームも書かれていない。
- README の "Zoom level: 6 to 12" はズーム 6 から 12 の話で、ファイル全体は 2 から 12。

## ライセンス

README に CC0 (No Rights Reserved) と書かれている。元データ (NASADEM、地球地図) 側の条件との関係は未確認。

## 学習での使い道 (案)

- 画素の復号に WebP 対応の画像ライブラリが要る (環境に入っているかは未確認)。標高は Mapbox 方式なら `-10000 + (R*65536 + G*256 + B) * 0.1` だが、このファイルで確かめてはいない。
- 7 Dijkstra/A*: 標高から傾斜を求めてコストにし、山越えの最短経路を解く。
- 12 多目的最適化: 距離と登りの合計を 2 つの目的にしてパレート解を並べる。
- 1 線形回帰: 標高を説明変数にして気温など別のデータを回帰する。
- 5, 6: 標高・傾斜・起伏などの地形量を作り、PCA やクラスタリングで地形の型を分ける。
