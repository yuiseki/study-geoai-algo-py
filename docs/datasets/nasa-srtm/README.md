# NASA SRTM (と NASADEM)

2026-09-28 に読んで確かめた内容。数字は特に断りが無ければこの日の実測。公式ページや文書に書いてあるだけの値は「記載」と書き分ける。

- SRTM (Shuttle Radar Topography Mission) は 2000 年 2 月 11 日から 11 日間、スペースシャトル Endeavour (STS-99) がレーダー干渉で測った標高。NASA と NGA の共同で、ドイツとイタリアの宇宙機関も参加 (NASA Earthdata の製品ページの記載)。
- 範囲は北緯 60 度から南緯 56 度の陸地。1 度四方のタイルに分けて配る。
- 同じ観測から作った版がいくつもあり、配布元ごとに名前が違う。下の表で整理する。

## 版の違い

| 版 | 解像度 | 作り方 (記載) | 配布元の例 |
|---|---|---|---|
| SRTM v1.0 / v2.1 | 1 秒 (約 30m) と 3 秒 (約 90m) | v1 は未編集。v2 は NGA が海岸線や水面を整えたもの。欠測 (void) は -32768 | 今回は探していない |
| SRTM v3 (SRTMGL1 / SRTMGL3) | 1 秒 / 3 秒 | v2 の欠測を ASTER GDEM2、GMTED2010、NED で埋めた。「Version 3.0 に欠測は無い」 | LP DAAC、OpenTopography |
| NASADEM (NASADEM_HGT v001) | 1 秒 | SRTM の元の観測を処理し直したもの。ICESat の地上基準点で高さと傾きを補正し、欠測は ASTER GDEM、ALOS AW3D30 などで埋めた。LP DAAC が 2020 年 2 月に公開 | LP DAAC、Planetary Computer、OpenTopography |
| CGIAR-CSI SRTM 90m v4 | 3 秒 | CGIAR が独自の補間で欠測を埋めたもの | srtm.csi.cgiar.org |

- どれが推奨か: LP DAAC の DEM Comparison Guide は NASADEM について「vertical accuracy、swath consistency、uniformity を改善した」と書く。「こちらを使え」という明示の推奨文は、今回読んだページと文書には無かった。新しく作り直した版として NASADEM を第一候補、SRTM v3 を次の候補と読むのが自然 (推測)。
- CGIAR 版はライセンスが違う (後述)。学習用には選ばない。

## 形式 (SRTM User Guide V3, 2015 年 10 月改訂の記載)

- HGT: ヘッダ無しの 16 bit 符号付き整数、big-endian、行優先 (北の行から)。単位 m。
- 1 秒は 3,601 x 3,601、3 秒は 1,201 x 1,201。四辺の行と列は隣のタイルと重なり、同じ値を持つ。
- ファイル名 (例 N35E139) は南西隅の画素の中心の緯度経度。
- 垂直基準は「WGS84/EGM96 geoid」。NASA CMR のメタデータも SRTMGL1、NASADEM_HGT ともに `WGS84/EGM96`。
- 欠測値: v1.0 と v2.1 は -32768。v3 は欠測を埋めてあるので無い。
- 海は 0 m で平らにならされている (v2.1 の説明の記載と、下の実測で 0 の画素が多いこと)。

## 入手経路

ログイン無しで読めた経路を先に書く。

| 経路 | 版 | 形式 | ログイン | Range 要求 |
|---|---|---|---|---|
| OpenTopography の公開バケット `https://opentopography.s3.sdsc.edu/raster/SRTM_GL1/SRTM_GL1_srtm/N35E139.tif` | SRTM v3 1 秒 | GeoTIFF (512 タイル、DEFLATE、概観画像つき) | 不要 | 206 |
| Planetary Computer `nasadem` コレクション (Azure Blob `nasademeuwest/nasadem-cog`) | NASADEM | COG | 不要。ただし匿名の SAS トークンが要る | 206 (トークン付き) |
| AWS Open Data の Terrain Tiles (`s3://elevation-tiles-prod/skadi/`) | SRTM を元にした合成 (後述) | HGT の gzip | 不要 | 206 |
| NASA Earthdata (LP DAAC、`data.lpdaac.earthdatacloud.nasa.gov`) | SRTMGL1/GL3 v3、NASADEM | HGT の zip | 要ログイン (Earthdata Login) | 未確認 |
| OpenTopography の API (`portal.opentopography.org/API/globaldem`) | SRTMGL1 など | 切り出し | 要 API キー (401 が返った) | - |
| CGIAR-CSI | SRTM 90m v4 | 今回は取っていない | 未確認 | 未確認 |

### NASA Earthdata (LP DAAC)

- CMR (`cmr.earthdata.nasa.gov`) の検索はログイン無しでできる。コレクション ID は SRTMGL1 `C2763266360-LPCLOUD`、SRTMGL3 `C2763266377-LPCLOUD`、NASADEM_HGT `C2763264762-LPCLOUD`。
- グラニュール (タイル) 数: SRTMGL1 14,297、SRTMGL3 14,297、NASADEM_HGT 14,520。
- N35E139 の大きさ (CMR の値): SRTMGL1 8.46189MB、SRTMGL3 1.09992MB、NASADEM 8.63923MB (いずれも zip)。
- 全体の大きさは製品ページの記載で SRTMGL1 99,883.2MB、NASADEM 103,565.8MB。
- ファイルの GET は `urs.earthdata.nasa.gov` へ 302 で飛ばされ、401 になった。要ログイン。
- 旧 URL の `e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/...` と `.../NASADEM_HGT.001/...` は 404 だった。
- NASADEM は NetCDF4 版 (NASADEM_NC)、SRTM v3 も NetCDF4 版 (SRTMGL1_NC) がある (記載)。各画素の出どころを示す NUM 層も別製品で配る。

### Planetary Computer (NASADEM)

- STAC: `https://planetarycomputer.microsoft.com/api/stac/v1/collections/nasadem`。タイトル "NASADEM HGT v001"、`gsd` 30。
- アセットは `elevation` 1 つで、型は `image/tiff; application=geotiff; profile=cloud-optimized`。
- 東京を含むアイテムは `NASADEM_HGT_n35e139`、href は `https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/NASADEM_HGT_n35e139.tif`。
- トークン無しの要求は 409。`https://planetarycomputer.microsoft.com/api/sas/v1/token/nasademeuwest/nasadem-cog` からログイン無しでトークンを取ると読める。トークンの期限は取得から約 45 分だった。
- `-r -8` (末尾からの Range) は 200 が返って全体を返そうとした。`-r 0-7` なら 206。GDAL の `/vsicurl/` は問題なく開けた。

### AWS Open Data の Terrain Tiles (skadi)

- `registry.opendata.aws` に SRTM や NASADEM の単独の登録は見つからなかった (`/nasadem/`、`/srtm/` は 404。registry の GitHub の datasets 一覧にも無い)。
- 代わりに Mapzen の Terrain Tiles (`terrain-tiles`) があり、その `skadi/` が SRTM と同じ 1 度四方、同じ名前の HGT を gzip で置いている。バケット一覧も匿名で取れる。
- `skadi/N35/N35E139.hgt.gz`: 10,294,039 バイト、Last-Modified 2016-04-26。展開すると 25,934,402 バイト (= 3,601 x 3,601 x 2)。
- ただし中身は SRTM そのものではない。下の実測のとおり、海に海底地形が入っている。

## 日本の 1 タイル (N35E139、東京と神奈川の大部分) を 3 経路で読んだ

3 つとも 3,601 x 3,601、Int16、画素 1/3600 度、左上 (138.9998611, 36.0001389)、NoData -32768 と宣言。

| | OpenTopography SRTM_GL1 | Planetary Computer NASADEM | Terrain Tiles skadi |
|---|---|---|---|
| ファイル | 10,623,899 バイト (GeoTIFF) | 10,517,920 バイト (COG) | 10,294,039 バイト (hgt.gz) |
| GDAL の表示 | タイル 512x512、DEFLATE、概観 1801/901/451。`LAYOUT=COG` の表示は無い | `LAYOUT=COG`、DEFLATE、タイル 512x512、概観 1800/900/450、Last-Modified 2021-06-08 | SRTMHGT ドライバ |
| 最小 / 最大 (m) | -76 / 1,731 | -86 / 1,719 | -1,512 / 1,731 |
| -32768 の画素 | 0 | 0 | 0 |
| 0 の画素 | 3,703,203 | 3,716,317 | 53,864 |
| 負の画素 | 54,178 | 76,503 | 3,511,154 |

- どれも欠測 (-32768) は 0 個。
- skadi と SRTM_GL1 を、SRTM_GL1 が正の画素で比べると 99.81% が同じ値。陸は SRTM v3 と読める。一方で skadi は 0 m の画素がほぼ無く、負の画素が 351 万個、最小 -1,512 m。海を別の海底地形データで置き換えていると考えると説明できる (joerd の attribution には SRTM のほか ETOPO1 なども並ぶ。どれが入ったかは確かめていない)。
- NASADEM と SRTM_GL1 を同じ画素で比べると、値が一致するのは 22.65%、差 (NASADEM − SRTM) の平均は -0.98 m、差の絶対値の 99 パーセンタイルは 8 m。同じ観測でも版で値が違う。
- 最高点はどちらも北緯 35.83 度、東経 139.012 度付近 (NASADEM 1,719 m、SRTM 1,731 m)。

## ライセンスと帰属表示

- NASA の Data Use Guidance (`https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance`。CMR の LicenseURL `earthdata.nasa.gov/earth-observation-data/data-use-policy` はここへ転送される) の記載:
  - "Unless the content is marked with a use restriction or license, data provided from a NASA-led mission are licensed as Creative Commons Zero (CC0)."
  - "NASA material is not protected by copyright within the United States, unless noted."
  - 引用は強く求める ("data users are very strongly urged to cite the data")。
- SRTMGL1 と NASADEM の製品ページには、個別の制限ではなく "This dataset is openly shared, without restriction, in accordance with the EOSDIS Data Use and Citation Guidance" と書かれている。
- まとめると、NASA 自身は「CC0」と明記しており、あわせて「米国内では著作権の対象外 (パブリックドメイン)」とも書いている。ユーザーの表の「原則 CC0」は NASA の書き方どおり。ただし SRTM の個別ページに CC0 の文字は無く、上の一般方針が当たるという読み方になる。
- 引用の例 (NASADEM の製品ページの記載): "NASADEM Merged DEM Global 1 arc second V001 [Dataset]. NASA Land Processes Distributed Active Archive Center. https://doi.org/10.5067/MEASURES/NASADEM/NASADEM_HGT.001"。SRTMGL1 の DOI は `10.5067/MEASURES/SRTM/SRTMGL1.003`。
- 配布元ごとの書き方の違い:
  - Planetary Computer の STAC は `license: proprietary` とし、LP DAAC の citation policy へのリンクを置く。CC0 とは書いていない。
  - Terrain Tiles の attribution.md は "SRTM is a public domain dataset" と書き、表示例として "SRTM data courtesy of the U.S. Geological Survey" を挙げる。skadi には SRTM 以外のデータも混ざるので、その表示だけでは足りない可能性がある (未確認)。
  - CGIAR-CSI 版は別物: "Users are prohibited from any commercial, non-free resale, or redistribution without explicit written permission from CIAT." と書かれており、CC0 でもパブリックドメインでもない。
  - OpenTopography のバケットの個別の条件は未確認。

## 気をつけること

- HGT は big-endian。NumPy で直接読むなら `np.fromfile(path, '>i2').reshape(3601, 3601)`。GDAL (SRTMHGT ドライバ) なら自動で扱う。
- 隣のタイルと端の 1 行 1 列が重なるので、つなぐときは重複を落とす。
- SRTM の海は 0 m。海と陸の境界を 0 で判定すると、0 m 付近の低地と区別できない。NASADEM には水域マスク層がある (記載)。
- レーダーが返した面の高さなので、建物や森林の上面が混ざると言われる (今回読んだ公式文書では確かめていない)。見通し計算では地面と建物を区別できない点に注意する。
- 範囲は北緯 60 度まで。日本は全域入る。
- LP DAAC の HEAD 要求は、ログイン無しでも署名付き URL への 303 を返した。GET では 302 でログインへ飛ばされる。HEAD が通っても取れるとは限らない。

## 学習での使い道 (案)

見通し (line of sight) の計算自体は 12 ステップのどれかのアルゴリズムではなく、前処理の幾何計算になる。基地局候補と需要点の組ごとに、標高の断面を引いて電波の通り道 (フレネルゾーン) が地面に当たるかを判定し、「どの候補がどの需要点を覆えるか」の 0/1 行列を作る。この行列が 8〜9 の入力になる。

| ステップ | 使い方 |
|---|---|
| 1〜3 回帰・分類、木、Boosting | 標高、傾斜、周囲の起伏を特徴量にして、Ookla Speedtest の速度や OpenCelliD の基地局の有無を予測する |
| 4 Cross Validation とデータリーク | 標高は空間的に強く相関するので、ランダム分割と空間ブロック分割の差が出やすい |
| 6 PCA | 1 画素の周りの標高パッチ (例 9x9) を 81 次元のベクトルと見て圧縮し、地形の型を取り出す |
| 5 k-means / DBSCAN | 6 の結果や傾斜などで地形をクラスタに分ける |
| 7 Dijkstra / A* | 傾斜をコストにして、保守車両や光ファイバーの敷設経路を解く |
| 8〜9 LP / MILP、facility location | 見通しで作った被覆行列で、最大被覆問題や集合被覆問題として基地局を選ぶ |
| 12 多目的最適化 | 被覆人口と基地局数 (費用) を 2 つの目的にしてパレート解を並べる |

- NASADEM の COG (約 10MB/タイル) なら東京周辺は 1 枚で足り、GDAL か rasterio で読める。rasterio がこのリポジトリの環境に入っているかは確かめていない (今回は GDAL の CLI と NumPy だけを使った)。

## 取り出し方

split。1 度四方のタイルに事前分割されていて、必要な枚数だけ引けばよい。1 枚が約 10MB なので、タイルの中まで部分読みする必要はほとんど無い。ただし公開されている 3 経路はどれも Range が効くので、経路によっては range も併用できる。2026-09-30 に実測した。

分割の単位と個数は、1 度四方のタイルで SRTMGL1 が 14,297 枚、NASADEM_HGT が 14,520 枚 (上の CMR の値)。ファイル名が南西隅の緯度経度なので、欲しい場所からファイル名を直接組み立てられる。目録を引かずに済むのが、この出典の実務上の利点になる。

| 経路 | HEAD | Range 0-1023 |
|---|---|---|
| OpenTopography `https://opentopography.s3.sdsc.edu/raster/SRTM_GL1/SRTM_GL1_srtm/N35E139.tif` | 200、`Content-Length` 10,623,899、`Accept-Ranges: bytes`、`Server: MinIO` | 206、1,024 バイト |
| Planetary Computer `https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/NASADEM_HGT_n35e139.tif` (SAS トークン付き) | 200、`Content-Length` 10,517,920、`Accept-Ranges: bytes` | 206、1,024 バイト |
| Terrain Tiles `https://s3.amazonaws.com/elevation-tiles-prod/skadi/N35/N35E139.hgt.gz` | 200、`Content-Length` 10,294,039、`Accept-Ranges: bytes`、`Last-Modified` Tue, 26 Apr 2016 23:47:27 GMT | 206、1,024 バイト |

OpenTopography と Planetary Computer は GeoTIFF なので、引いた先頭 1,024 バイトから索引の位置が読める。どちらも先頭 4 バイトが `II*\0` (リトルエンディアンの古典 TIFF) で、5 バイト目からの uint32 が最初の IFD の位置。OpenTopography は 8、Planetary Computer は 192。どちらも先頭付近にあり、ヘッダだけ読んで必要なタイルを選べる。

Planetary Computer はトークンが要る。トークン無しで blob を GET すると 409 が返った。`https://planetarycomputer.microsoft.com/api/sas/v1/token/nasademeuwest/nasadem-cog` はログイン無しで 200 とトークン (296 文字) を返し、これを query string に付ければ読める。有効期限は取得から約 45 分。

Planetary Computer だけは catalog も使える。`https://planetarycomputer.microsoft.com/api/stac/v1/search?collections=nasadem&bbox=139.6,35.6,139.8,35.8` は 200 で 2,579 バイトを返し、bbox で該当するアイテムに絞れる。ファイル名を自分で組み立てずに済ませたいならこちら。

skadi は gzip なので、Range で 206 が返っても途中から解凍できない。事実上 1 タイル丸ごと引くことになる。1 枚 10,294,039 バイトなので問題にならないが、部分読みの手段としては数えない。

NASA Earthdata (LP DAAC) の直接取得は未確認。GET が `urs.earthdata.nasa.gov` へ 302 で飛ばされて 401 になるので、Range 以前に取得ができていない。確かめるには Earthdata Login のアカウントと、そのトークンを付けた要求が要る。CGIAR-CSI 版も未確認で、そもそもライセンスが再配布を禁じているので試していない。
