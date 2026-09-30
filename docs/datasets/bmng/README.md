# NASA Blue Marble Next Generation (BMNG)

2026-09-30 に読んで確かめた内容。ファイルの有無と大きさは eoimages への HEAD と Range による実測、ライセンスは NASA のメディア利用指針の本文。

- 案内: `https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/`
- 地形と水深の陰影を入れた版の案内: `https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-topography-bathymetry/`
- 配布: `https://eoimages.gsfc.nasa.gov/images/imagerecords/`
- 中身は MODIS から作った、雲の無い地球の月別のトゥルーカラー合成画像。2004 年の 12 か月分。
- 案内ページの本文。

> Blue Marble: Next Generation offers a years worth of monthly composites at a spatial resolution of 500 meters. These monthly images reveal seasonal changes to the land surface: the green-up and dying-back of vegetation in temperate regions such as North America and Europe, dry and wet seasons in the tropics, and advancing and retreating Northern Hemisphere snow cover.

> This version of the maps includes shading for topography and bathymetry.

- planetarble (`configs/base/assets.yaml`) は `world.topo.bathy.200408` の 8 枚のパネルと、2km の全球 1 枚を指している。`processing.tile_source` を `bmng` に戻したときの土台。

## 配布されている画像 (実測)

2004 年の 12 か月それぞれに imagerecord の番号が別に振られている。2km の全球 JPEG (`world.topo.bathy.2004MM.3x5400x2700.jpg`) の有無で 12 か月すべてを確認した。

| 月 | imagerecord |
|---|---|
| 2004-01 | 73580 |
| 2004-02 | 73605 |
| 2004-03 | 73630 |
| 2004-04 | 73655 |
| 2004-05 | 73701 |
| 2004-06 | 73726 |
| 2004-07 | 73751 |
| 2004-08 | 73776 |
| 2004-09 | 73801 |
| 2004-10 | 73826 |
| 2004-11 | 73884 |
| 2004-12 | 73909 |

500m は 1 か月あたり 8 枚のパネルに分かれる。A から D が東西 4 列、1 と 2 が南北 2 段。2004 年 8 月 (73776) の PNG の大きさ。

| パネル | バイト数 |
|---|---:|
| C1 | 482,260,830 |
| D1 | 359,953,725 |
| B1 | 305,691,691 |
| A1 | 284,592,743 |
| B2 | 255,933,485 |
| D2 | 251,646,053 |
| C2 | 230,149,525 |
| A2 | 113,362,109 |
| 合計 (8 枚) | 2,283,590,161 |

- パネル 1 枚は 21600 x 21600 の 8bit RGB (PNG の IHDR を読んだ値。幅と高さが 0x5460、bit depth 8、colour type 2)。8 枚を並べると 86400 x 43200 になり、赤道で 1 画素約 463m。
- 同じパネルは JPEG でも置かれている。A1 の JPEG は 54,280,546 バイトで、PNG の 5 分の 1 以下。
- 2km の全球 1 枚は JPEG が 2,308,163 バイト (`Last-Modified: Fri, 14 Dec 2012 19:03:56 GMT`)、PNG が 14,793,567 バイト。
- 2004 年 7 月のパネル (73751 の A1.png、284,866,056 バイト) も同じ形で置かれている。月をまたいでファイル名の規則は同じ。

## 取り出し方

split。1 枚の中は whole。

- 月 12 通り x パネル 8 枚で事前分割されている。必要な月の必要なパネルだけを名前で指定して引ける。
- `https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73776/world.topo.bathy.200408.3x21600x21600.A1.png` に `Range: bytes=0-1023` を投げると HTTP 206、1,024 バイトが返る。サーバーは Range に応じる。
- ただし PNG は 1 本の zlib ストリームで、先頭から順に伸長しないと途中の行が取れない。索引に当たるものが無いので、206 が返っても部分的な画像は得られない。1 枚を使うなら 1 枚を全部落とすしかない。同じ理由で 2km の JPEG も whole。
- 実質的に部分読みができるのは「どのパネルを落とすか」の粒度まで。最小単位は 2km 全球の JPEG で 2,308,163 バイト、500m のパネル 1 枚で最小 113,362,109 バイト (A2)、最大 482,260,830 バイト (C1)。

planetarble が指している URL は今日は使えない。

- `https://neo.gsfc.nasa.gov/archive/bluemarble/bmng/world_500m/world.topo.bathy.200408.3x21600x21600.A1_geo.tif` は HTTP 301 で `https://science.nasa.gov/earth/nasa-earth-observations-neo/` に飛ぶ。リダイレクトを追うと HTTP 200 で `content-type: text/html`、255,227 バイトの HTML が返る。画像ではない。
- 同じ名前の `_geo.tif` を eoimages 側で試すと HTTP 404。ジオリファレンス済みの GeoTIFF の配布先は今回見つからなかった (未確認)。今日 eoimages から取れるのは PNG と JPEG だけで、位置合わせは自分で入れる必要がある (全球等緯度経度なので、範囲が分かればワールドファイルで足りる)。
- assets.yaml の 2km の URL (`https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73776/world.topo.bathy.200408.3x5400x2700.jpg`) は HTTP 200 で生きていて、Range も 206 を返す。8 枚のパネルの側だけが死んでいる。

## ライセンス

BMNG の個別ページにライセンスの記載は無かった。NASA 全体のメディア利用指針 (`https://www.nasa.gov/nasa-brand-center/images-and-media/`) の本文。

> NASA content – images, audio, video, and media files used in the rendition of 3-dimensional models, such as texture maps and polygon data in any format – generally are not subject to copyright in the United States. You may use this material for educational or informational purposes, including photo collections, textbooks, public exhibits, computer graphical simulations and Internet Web pages. This general permission extends to personal Web pages.

表示についての一文。

> News outlets, schools, and text-book authors may use NASA content without needing explicit permission, subject to compliance with these guidelines. NASA content used in a factual manner that does not imply endorsement may be used without needing explicit permission. NASA should be acknowledged as the source of the material.

除外されるもの。

> The NASA Insignia, Logotype, identifiers, and imagery are not in the public domain.

NASA Earthdata 側の文書 (`https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance`) はデータについて CC0 と言い切る。

> Unless the content is marked with a use restriction or license, data provided from a NASA-led mission are licensed as Creative Commons Zero (CC0). While there are no restrictions on the use of these data, data users are very strongly urged to cite the data used in their work products.

読み取れること。BMNG は「米国内で著作権の対象にならない」もので、NASA を出典として挙げることが求められる。これは CC0 の明示的な権利放棄とは違う。NASA は「NASA does not license the use of NASA materials or sign licensing agreements」とも書いていて、ライセンスを付与するという形を取らない。ETOPO の CC0 が「世界に対して権利を放棄する」と言い切っているのに対し、こちらは米国の著作権法上の地位の説明と、条件付きの一般許可の組み合わせである。区分としては「public domain (米国において) + 出典表示の要請」で、Landsat の「制限なし + 表示は任意」より表示についての言い方がやや強い。

Earthdata の CC0 の一文は「data provided from a NASA-led mission」を対象にしていて、BMNG は MODIS を元に NASA Earth Observatory が作った画像製品なので、こちらに当たると読むこともできる。どちらの文書を当てても結論は「使ってよい、NASA を出典に挙げる」で変わらない。

planetarble の assets.yaml は license 欄を NASA Earth Observatory の「credit NASA」、attribution 欄を「Image courtesy NASA Earth Observatory」と書いている。上の指針と食い違わない。

合成物としての注意。BMNG そのものは MODIS の観測から作られていて、地形と水深の陰影を足した版では標高と水深のデータが重なっている。その陰影に何を使ったかは、今日読んだページからは分からなかった (未確認)。もし [GEBCO](../gebco/README.md) 由来なら表示義務が付いて回る。

## 気をつけること

planetarble の assets.yaml に書かれた 8 枚の 500m パネルの URL は今日はすべて死んでいる。neo.gsfc.nasa.gov がドメインごと science.nasa.gov に畳まれた。リダイレクト先が HTTP 200 で HTML を返すので、ダウンローダーが成功と判断して 255KB の HTML を `.tif` として保存する。SHA256 の検証が無ければ、壊れた入力で処理が進む。legacy 経路を動かすなら URL を eoimages の PNG か JPEG に差し替える必要がある。

eoimages にあるのは PNG と JPEG で、GeoTIFF は無い。planetarble のパイプラインは `_geo.tif` を前提にしている。

2004 年の 12 か月分しかない。20 年以上前の状態で、都市の広がりや氷河の後退はその後の変化を反映しない。見た目の土台としては今も使えるが、観測として使うなら [HLS](../hls/README.md) や [Landsat](../landsat-c2-l2/README.md) を見る。

500m と書かれているが、8 枚を並べた 86400 x 43200 は赤道で 1 画素約 463m。高緯度では経度方向がさらに細かくなる (等緯度経度なので)。

PNG は Range 要求に 206 を返すが、部分的に取り出せるという意味ではない。206 が返ることだけを根拠に range に分類すると間違える。

パネルの大きさが 113MB から 482MB までばらつく。C1 (ユーラシア北部を含む) が一番大きく、A2 (南米の西側と太平洋) が一番小さい。海と雲が多い範囲ほど圧縮が効く。

## 学習ステップでの使いどころ (案)

- 地図の土台としての見た目の確認。ラベルやマーカーを重ねたときの読みやすさを見る題材。
- 5 クラスタリング、6 PCA: RGB 3 チャンネルしかないので特徴量としては弱いが、色だけでどこまで陸の区分ができるかを見る出発点にはなる。分光バンドを足すと何が変わるかを [HLS](../hls/README.md) と比べられる。
- 8 時系列: 12 か月分あるので、季節による植生と積雪の変化を同じ画素で追える。年をまたがないので変化検出の練習にはならない。
- 全球を見るだけなら 2km の JPEG 1 枚 (2,308,163 バイト) で足りる。500m が要るなら該当するパネルだけを落とす。
