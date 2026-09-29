# japan-seamlessphoto

2026-09-28 に読んで確かめた内容。数字はすべてこの日の実測。

- `https://source.coop/smartmaps/japan-seamlessphoto`
- 国土地理院のシームレス空中写真 (seamlessphoto) を日本全国分 PMTiles にまとめたもの。
- Web ページの説明: "Complete nationwide aerial imagery of Japan at maximum resolution (Zoom 18) from the Geospatial Information Authority of Japan (GSI) seamlessphoto dataset, packaged as PMTiles / MBTiles archive for efficient web distribution and processing."
- README.md は無い。

## ファイル

| key | 大きさ (バイト) | 更新 |
|---|---:|---|
| `pmtiles/seamlessphoto512.pmtiles` | 767,579,254,057 (767.58GB) | 2026-06-21 |
| `pmtiles/seamlessphoto512.pmtiles.sha256` | 91 | 2026-06-20 |
| `pmtiles/z18.pmtiles` | 424,950,358,986 (424.95GB) | 2026-06-17 |
| `pmtiles/z18.pmtiles.sha256` | 78 | 2026-06-10 |

## 中身 (PMTiles ヘッダとメタデータ)

どちらも PMTiles v3、タイルは JPEG (無圧縮で格納)、内部ディレクトリは gzip、clustered。

| | seamlessphoto512 | z18 |
|---|---|---|
| ズーム | 1 から 17 | 18 のみ |
| タイル | 512px に再タイル化 (メタデータの説明による) | 256px の z18 (メタデータの名前による) |
| bounds | 122.920532, 20.40642, 153.989868, 45.541946 | 同じ |
| タイル数 (addressed) | 9,772,357 | 28,162,630 |
| 中身の数 (contents) | 9,562,490 | 28,132,366 |

- seamlessphoto512 のメタデータ: name "GSI seamlessphoto 512px (z1-z17)"、description "GSI seamlessphoto re-tiled to 512px tiles, zoom 1-17 (from 256px z2-z18). CC BY 4.0 国土地理院"、attribution "国土地理院 シームレス空中写真 (GSI seamlessphoto) CC BY 4.0"。
- z18 のメタデータ: name "GSI seamlessphoto z18"、attribution は上と同じ。
- 先頭のタイルの先頭バイトは `ffd8ffe0 ... JFIF` で、JPEG であることを確かめた (1 枚だけ)。
- 撮影年や基準日はメタデータに無い。元のシームレス空中写真は撮影時期の異なる写真の継ぎ合わせなので、場所ごとに時期が違うはず (推測、未確認)。

## z.yuiseki.net の複製との突き合わせ

`https://z.yuiseki.net/static/gsi/seamlessphoto/` にある同名の 2 ファイルと比べた。

- 大きさ: バイト単位で一致 (767,579,254,057 と 424,950,358,986)。
- `.sha256` の中身: 2 つとも同じ文字列 (seamlessphoto512 は `404c2965...ed78`、z18 は `c839630f...daea`)。
- ヘッダを解析した結果とメタデータ JSON: 2 つとも一致。
- ファイル全体の SHA-256 は計算していない (大きすぎる)。したがって「同じものである」は、大きさ・ヘッダ・メタデータ・添付のハッシュ値の一致までしか確かめていない。

## 気づいたこと

- seamlessphoto512 のヘッダの center_zoom が 18 で、maxzoom 17 を超えている。
- Web ページは "PMTiles / MBTiles archive" と書くが、このリポジトリに MBTiles は無い (z 側には z18.mbtiles などがある)。
- z 側の `SHA256SUMS` では seamlessphoto512 と同じハッシュ値が `z1-z17.pmtiles` という名前で書かれている。命名の揺れ。
- z 側のファイルの更新日 (2026-06-09 から 06-10) より、こちらの更新日 (2026-06-17 から 06-21) が後。z から上げたものと考えると筋が通るが、確かめていない。

## ライセンス

メタデータには CC BY 4.0 (国土地理院) と書かれている。リポジトリに README やライセンス文書は無く、Web ページにもライセンスの記述は見つからなかった。国土地理院の利用規約との関係は未確認。

## 学習での使い道 (案)

- JPEG の復号に画像ライブラリが要る (study-geoai-algo-py の環境に入っているかは未確認)。
- 5 k-means/DBSCAN: 画素の色でクラスタリングし、水域・植生・市街地に分かれるかを見る。
- 6 PCA: タイルを小さな画像片に切って PCA し、主成分を画像として見る。
- 1 から 3: OSM など別のラベルと組み合わせて、タイル単位の分類 (建物がある/無い など) をする。
- 4 Cross Validation とデータリーク: 隣り合うタイルは似ているので、ランダム分割と空間ブロック分割で精度がどれだけ変わるかを見る題材になる。
