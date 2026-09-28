# cogenerate

2026-09-28 に読んで確かめた内容。

- `https://data.source.coop/smartmaps/cogenerate/`
- `README.md` (3,960 バイト、更新 2026-07-31) あり。source.coop の Web ページの題は「Japan GSI Disaster-Response Aerial Imagery (COGs)」。
- 標高や地形ではなく、国土地理院の災害対応の空中写真 (正射画像 / 正射画像速報) を COG にしたもの。国土地理院の XYZ タイル (`https://cyberjapandata.gsi.go.jp/xyz/<layer id>/{z}/{x}/{y}.png`) を z18 でつなぎ直している。変換は [`optgeo/cogenerate`](https://github.com/optgeo/cogenerate)。発行は UN Smart Maps Group。
- ファイル名は国土地理院のレイヤー ID そのまま (`<ID>.tif`)。README の例: `20260729kumamoto_yatsushiro_0729do_sokuho.tif` はレイヤー `20260729kumamoto_yatsushiro_0729do_sokuho` で、2026-07-29 撮影。
- 災害が起きるたびに増える、と README は書く。

## 件数と大きさ

- tif が 157 件、合計 427,705,750,375 バイト (約 427.7GB)。README を入れて 158 件。更新日は 2026-07-31 から 2026-08-19。
- 最小 1,554,494 バイト (`20170705typhoon3_0707dol3.tif`)、最大 48,655,094,466 バイト (`20240102noto_0405_0426do.tif`)。50MB 未満は 12 件。
- 名前の末尾で分けると: `dol` 系 83、`do` 45、`do_sokuho` 14、`doh` 5、`apsar...` 8、`uav` 1、`dosha` 1。
- 先頭の年: 1948 と 1962 が 1 件ずつ、2013 年から 2026 年が残り (2016 年が 40 件で最多、熊本地震)。

## 中身 (gdalinfo の /vsicurl/ で 5 件のヘッダを読んだ)

読んだのは `20170705typhoon3_0707dol3.tif`、`19480000dol.tif`、`20171011kirishima_apsar171012ew.tif`、`20260729kumamoto_yatsushiro_0729do_sokuho.tif`、`20240102noto_0405_0426do.tif`。

- 5 件とも: EPSG:3857、画素 0.5972 m (z18 相当)、Byte の RGBA 4 バンド、`LAYOUT=COG`、DEFLATE 圧縮、512x512 のタイル、オーバービューあり (2 から 10 段)。
- 大きさの例: `20240102noto_0405_0426do.tif` は 155,904 x 294,912 画素、経度 136.56 から 137.39、緯度 36.60 から 37.86 (能登半島)。`20260729kumamoto_yatsushiro_0729do_sokuho.tif` は 64,000 x 76,800 画素。
- nodata: 4 件は全バンド 0。`20171011kirishima_apsar171012ew.tif` だけ nodata の指定が無い。
- 画素値の統計は取っていない (巨大なため)。

## 気づいたこと

- README は `_do` / `_do_sokuho` (正射画像) の COG と書くが、実際には `dol`、`doh`、`apsar` (名前から見ると SAR 由来か、未確認)、`uav`、`dosha` など README に説明の無い種類が混ざる。1948 年と 1962 年のもの (災害対応ではなさそう) もある。
- 同じ場所・同じ日の速報と通常版が両方ある (例: `20260729kumamoto_yatsushiro_0729do.tif` と `..._0729do_sokuho.tif`)。
- 命名の揺れ: `20190704_kagoshima_...` や `20240102_noto_...` のように日付の後に `_` があるものと無いもの (`20240102noto_...`)。末尾の番号も `dol1` と `dol01` が混在。
- RGB に nodata 0 が付いているので、真っ黒の画素は nodata 扱いになる (README も、元画像で黒く塗られた画素は透明にした、と書く)。
- README の注意: 自動処理のため構造物の周りに歪みや継ぎ目があり、雲で地表が見えない所もある。測量の基図ではなく災害対応の画像として扱う。

## ライセンス

README の記載: 元の画像は国土地理院。出典の表示が必須 (「国土地理院」と <https://maps.gsi.go.jp/development/ichiran.html> へのリンク)。レイヤーごとの追加条件はその一覧で ID を検索して確かめる。COG 化などの梱包部分は CC0-1.0 だが、国土地理院の出典表示の条件は消えない。一覧にまだ載っていないレイヤーもあり、その場合は条件を突き合わせられていない、とも書かれている。

## 学習で使うなら (案)

- 標高データではないので、地形の特徴量には使わない。
- 画像の画素値 (RGB) を特徴量にした被災箇所の分類なら、ステップ 1 から 3 (ロジスティック回帰、Random Forest、XGBoost) の題材になる。ただしラベルは別に要る。
- ステップ 4: 同じ災害の画像を学習と評価に分けると隣接画素でリークするので、災害ごと・地域ごとの分割を試す題材になる。
- ステップ 5 と 6: 画素の RGB を k-means でクラスタリング (土砂、水、植生の粗い分け)、PCA で色空間を縮める。
- ファイルが大きいので、COG の Range 読みで小さい窓だけ切り出して使う。
