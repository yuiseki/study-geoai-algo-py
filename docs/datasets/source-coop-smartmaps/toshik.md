# toshik

2026-09-28 に読んで確かめた内容。

- `https://source.coop/smartmaps/toshik` (source.coop 上の題名は「都市計画決定PMTiles」)
- 国土交通省の都市計画決定 GIS データ (<https://www.mlit.go.jp/toshi/tosiko/toshi_tosiko_tk_000087.html>) を加工して 1 つの PMTiles にしたもの (リポジトリ内 README.md より)。
- 元データの仕様書として <https://www.mlit.go.jp/toshi/tosiko/content/001609328.pdf> が README に挙がっている。
- 基準日: 元データの年度はファイルにも README にも無く未確認。ファイルの更新日時は 2024-05-08。

## ファイル

| ファイル | 大きさ (バイト) | 更新日時 |
|---|---:|---|
| README.md | 2,630 | 2024-05-08 |
| a.pmtiles | 159,930,151 | 2024-05-08 |

## 中身 (a.pmtiles のヘッダとメタデータ)

- PMTiles v3、タイル形式 MVT、タイル圧縮 gzip、clustered。
- ズーム 0 から 14。タイル数 addressed 56,496、entries 55,261、contents 53,100。
- 範囲 (bounds): 124.07, 24.33, 145.04, 45.45。
- 生成: `tippecanoe v2.28.0`, `tippecanoe -f -o a.pmtiles` (オプション指定なし。tippecanoe の既定ではタイルが大きすぎると地物が落とされる)。

レイヤー 21 個 (tilestats の地物数、ジオメトリ型、都道府県の種類数):

| レイヤー | 内容 (README) | 地物数 | 型 | 都道府県数 |
|---|---|---:|---|---:|
| youto | 用途地域 | 101,464 | Polygon | 47 |
| douro | 都市計画道路 | 146,132 | LineString | 46 |
| kouen | 公園 | 43,550 | Polygon | 46 |
| koudoti | 高度地区 | 18,179 | Polygon | 32 |
| senbiki | 区域区分 | 16,215 | Polygon | 46 |
| tokei | 都市計画区域 | 12,111 | Polygon | 47 |
| chikukei | 地区計画 | 9,087 | Polygon | 46 |
| tkbt | 特別用途地区 | 9,063 | Polygon | 47 |
| ritteki | 立地適正化計画 | 7,994 | Polygon | 46 |
| bouka | 防火準防火 | 7,908 | Polygon | 47 |
| tochiku | 土地区画整理事業 | 5,748 | Polygon | 47 |
| koudori | 高度利用地区 | 878 | Polygon | 45 |
| rekifuu | 歴史的風土保存地区など | 77 | Polygon | 4 |
| soubou | 航空機騒音障害防止地区など | 51 | Polygon | 1 |
| tokuteiyuudou | 特定用途誘導地区 | 6 | Polygon | 4 |
| tokuteibouka | 特定防火街区整備地区 | 5 | Polygon | 3 |
| kyojyuchosei | 居住調整地域 | 4 | Polygon | 1 |
| fukkousaiseikyoten | 一団地の復興再生拠点市街地形成施設 | 2 | Polygon | 1 |
| tokureiyouseki | 特例容積率適用地区 | 2 | Polygon | 2 |
| kousoujyukyo | 高層住居誘導地区 | 1 | Polygon | 1 |
| ryokukachiiki | 緑化地域 | 1 | Polygon | 1 |

主な属性:

- 共通: `Citycode` (5 桁)、`Cityname`、`Pref`、`kubunID` (区分コード)。多くのレイヤーに `告示番号`、`決定日`、`決定者`、`名称` がある。
- youto: `YoutoID` (0 から 13)、`用途地域`、`建ぺい率` (20 から 400)、`容積率` (40 から 1,300)。
- douro: `区分` (道路 / 広場)、`決定区分` (市 / 県)。
- tkbt: `youtoID` (0 から 11)、`用途区分`。
- tokei: `tokeiname`。senbiki, ritteki: `区域区分`。
- コードの意味は README のコード表 (用途地域 1 から 13、区域区分 22, 23、防火 24, 25 など) に載っている。

## 気づいた異常

- README の「basic schema」(code, name, date, status, by, no, city に統一) と実際の属性が違う。タイルには `kubunID`, `YoutoID`, `名称`, `決定日`, `決定者`, `告示番号`, `Citycode` などが元の名前のまま入っている。
- 同じ意味の属性で名前と型が揺れる。`kubunID` は Number のレイヤーと String のレイヤーがある。tokureiyouseki だけ `KubunID` (大文字 K)。kousoujyukyo は `告示年月日` と `決定権者` を使い、`告示番号` が Number。
- `決定日` の書式が混在: `1949-10-04`、`1982/07/07`、`1977/02/14 00:00:00`、`2020-04-14 17:19:28`、`H18.06.07`、`昭和42年12月15日`、`191228`、`-`、`0`。`1899-12-30` (Excel の日付 0 と見られる) や `1879/11/3` もある。
- kouen の `名称` に改行 (`\r\n`) が先頭に何個も付いた値がある。senbiki の `告示番号` に `\r\n` だけの値がある。
- koudori の `告示番号` に建築基準法の注記の文章が入っている。
- `決定者` に市名 (日進市, 瀬戸市, 稲沢市, 都城市) と「市」「県」が混在する。
- README の表記は「特定防火街区整備地区」、データの `Type` は「特定防災街区整備地区」。
- レイヤーによって都道府県の数が大きく違う (koudoti は 32)。制度上の分布か元データの未整備かは未確認。

## ライセンス

- README に「都市計画決定GISデータ（国土交通省）を加工して使用」という出典表示がある。利用条件そのものは未確認。

## 12 ステップでの使いみち (案)

- 2 決定木 / Random Forest: 用途地域を、容積率・建ぺい率や周辺の地価 (next-ksj の L01) から当てる多クラス分類。
- 1 回帰 / 3 GBDT / 11 SHAP: 地価公示 (next-ksj の L01) の説明変数として、地点が属する用途地域や容積率を空間結合して足す。
- 4 CV とデータリーク: 同じ市区町村の区域が同じ告示で決まるので、`Citycode` 単位の group CV の題材になる。
- 9 facility location: 公園 (kouen) や立地適正化計画の誘導区域 (ritteki) を、施設の候補地や制約として使う。
- 8 LP / MILP: 用途地域ごとの容積率を上限にした土地利用配分の制約。
- 前処理 (日付の正規化、属性名の統一) 自体が良い練習題材になる。
