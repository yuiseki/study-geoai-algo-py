# PLATEAU を再配布しているものと、そこに付けられたライセンス

2026-09-30 に読んで確かめた内容。PLATEAU の公式の配布口は G 空間情報センター (geospatial.jp の CKAN、組織「都市局」) と `assets.cms.plateau.reearth.io` および `api.plateauview.mlit.go.jp` である。ここではその外側に PLATEAU のデータを置き直したものを探し、再配布した側が何のライセンスを宣言したかを記録する。書いてあることはすべて今日 curl で取った応答に基づく。確かめられなかったものは未確認と書く。

PLATEAU 自身の条件は、サイトポリシーの「3. 著作権について」により CC BY 4.0 での利用を認めるものである。したがって ODC BY や ODbL のような表示義務を保つライセンスを重ねることは妨げられない。逆に CC0 やパブリックドメイン、あるいは表示義務の無い形で宣言することは、元の条件と食い違う。この観点で各件を見た。

## 見つかったものの一覧

| 置き場 | 何か | 再配布側の宣言 | 国交省・自治体への出典表示 | 元の条件との整合 |
|---|---|---|---|---|
| source.coop/smartmaps/xing | PLATEAU の 3D Tiles と MVT、6,419 データセット | ライセンスの記載が無い | README に出典リンク、ビューアに「国土交通省 with UN Smart Maps」 | 判断できない (宣言が無い) |
| geospatial.jp 静岡市 plateau2mc_shizuoka | 静岡市の建物を Minecraft ワールドに変換 | `cc-by` / クリエイティブ・コモンズ 表示 | あり。本文に出典と CC BY 4.0 の明記 | 整合する |
| geospatial.jp 北海道 plateau-sapporo2020-flatgeobuf | 札幌市 3D 建物を FlatGeobuf 化 | `CC-BY` / CC-BY | あり。本文に PLATEAU と元データへのリンク | 整合する |
| geospatial.jp インディゴ株式会社 plateau-tokyo23ku-building-mvt-2020 | 東京 23 区の建物を MVT 化 (実体は GitHub) | `CC-BY` / CC-BY | あり。本文に元データセットへのリンク | 整合する |
| npm @ortho-earth/japan | PLATEAU 由来の建物名・座標・高さと、データセット目録を同梱 | `GPL-3.0-or-later`、加えて有償の商用ライセンスの案内 | あり。README に「Attribution (required)」の節と表示文例 | 要注意。下に書く |

## 1. source.coop/smartmaps/xing

`https://source.coop/smartmaps/xing` および `https://data.source.coop/smartmaps/xing/`。Web ページの題は「Vector Tiles and 3D Tiles from Project PLATEAU」。

PLATEAU 由来であることの確かめ方。`https://data.source.coop/smartmaps/xing/README.md` は 200 を返し、本文は次のとおりである。

```
# xing: Vector Tiles and 3D Tiles from Project PLATEAU

## Source
[3D都市モデル（Project PLATEAU）ポータルサイト](https://www.geospatial.jp/ckan/dataset/plateau)

- 標準製品仕様書V3に対応したデータのみを収録することにします。
```

さらに `https://data.source.coop/smartmaps/xing/01100_sapporo-shi_city_2020_citygml_6_op_bldg_3dtiles_01101_chuo-ku_lod2/tileset.json` は 200 で 107,646 バイトを返し、`properties` に 121 個の属性名が並ぶ。先頭は `meshcode`, `feature_type`, `city_code`, `city_name`, `gml_id`, `attributes`, `gml:name`, `bldg:class`, `bldg:usage`, `bldg:yearOfConstruction`, `bldg:measuredHeight`, `uro:BuildingIDAttribute_uro:buildingID` などで、CityGML と PLATEAU 拡張 (`uro:`) の名前空間そのものである。同じデータセットの `data/data175.b3dm` は HEAD 200、`content-length` 169,924、`last-modified` Thu, 21 Nov 2024 13:12:18 GMT。これらから PLATEAU の CityGML を変換したものと判断した。

再配布側の宣言。ライセンスの記載が見つからない。`https://source.coop/smartmaps/xing` の HTML (555,621 バイト) を取って `license`、`licence`、`cc-by`、`cc0` を大小文字を問わず探したが、一件も出てこなかった。これが Source Cooperative の仕様ではないことも確かめた。同じ組織の `https://source.coop/smartmaps/gel` の HTML には `license` が 4 回、`cc0` が 4 回出てくる。つまり Source Cooperative にはライセンスを載せる場所があり、gel はそこに CC0 を入れていて、xing は入れていない。`data.source.coop/smartmaps/xing/README.md` にもライセンスの行は無い。

出典表示。README に PLATEAU ポータルへのリンクがある。同じ場所に置かれた `index.html` (CesiumJS のビューア) は `const credit = new Cesium.Credit('国土交通省 with UN Smart Maps')` で国土交通省を表示する。したがって出典表示はデータの脇に存在する。

整合の判断。ライセンスの宣言が無いので、より緩い条件を主張しているわけではない。ただし再利用者から見ると、この置き場のデータをどの条件で使えるのかがこのページだけでは決まらない。README のリンク先に戻って PLATEAU のサイトポリシーを読む必要がある。CC0 のように元より緩い宣言をしている例ではないという点では食い違いは無いが、表示義務を伴うライセンスが明示されていないという意味で不十分である。

Source Cooperative 全体の機械可読な目録は取れなかった。`https://source.coop/api/v1/repositories?limit=100`、`.../api/repositories`、`.../api/v1/repositories/smartmaps/xing` はいずれも JSON ではなく Next.js の HTML を返す。`https://api.source.coop/...` は接続できず HTTP 000 だった。したがって Source Cooperative 全体に xing 以外の PLATEAU 再配布があるかどうかは未確認である。確かめたのは smartmaps 組織のページ (`https://source.coop/smartmaps`、200、140,696 バイト) だけで、そこに現れる PLATEAU は xing の記述のみだった。

## 2. Hugging Face datasets

見つからなかった。これは探した上での否定的な結果である。

`https://huggingface.co/api/datasets?search=<語>` を次の語で叩いた。結果はすべて 200 である。

| 検索語 | 件数 | 中身 |
|---|---:|---|
| `plateau` | 16 | すべて無関係 |
| `PLATEAU` | 16 | 同上 |
| `3d-city` | 0 | |
| `citygml` | 1 | `felix-propx/vienna-citygml` (ウィーン。日本ではない) |
| `都市モデル` | 0 | |
| `3d+city+model` | 0 | |
| `3dtiles` | 0 | |
| `b3dm` | 0 | |
| `MLIT` | 5 | 多言語 LLM の `mlit-alpaca-eval` など。地理データは `takarahomes/mlit-japan-real-estate-price-2005-2024q3` だけで、これは不動産価格であって PLATEAU ではない |
| `国土交通省` | 0 | |
| `japan+building` | 0 | |
| `plateau+3d` | 0 | |

`plateau` の 16 件の内訳は、フランス語の「plateau (高原、盤)」を含む Natura 2000 や data.gouv.fr のミラー、ボードゲーム用語集、臨床の「プラトー」、LLM 学習の停滞を指す `msr-spare-1/qwen3-*-plateau-*` である。`full=true` を付けてカードと説明文まで含めて取り直しても、PLATEAU と CityGML や国土交通省が同時に現れるものは無かった。

つまり 2026-09-30 の時点で Hugging Face に PLATEAU の再配布は無い。

## 3. PMTiles とタイルサーバー

どちらも見つからなかった。これも探した上での否定的な結果である。

`https://stars.optgeo.org/catalog` は 200 で 23,716 バイトを返す。`tiles` は 43 個で、キーは `tokachi20260911-ortho`, `hih-*` 19 個, `vbm`, `gaez-aez33`, `gaez-aez57`, `kitaphoto`, `kitaphoto17`, `mapterhorn-japan-bridge`, `mapterhorn-japan-bridge-lineage`, `pmtiles_jma_1saibun_hkd`, `pmtiles_ksj_n03_hkd`, `overture_*` 6 個, `openstreetmap_jp_planet`, `japan-seamless-aerial-z18`, `bvmap`, `seamlessphoto512`, `freetown-mapterhorn`, `glup2030_zoning`, `vlcm` である。PLATEAU のレイヤーは無い。

catalog 全体で `plateau` は 1 回だけ現れるが、それはデータではない。`kitaphoto17` の `description` の末尾が「Built 2026-08-26 for plateau-mago-implicit.」となっているもので、この作業の名前に plateau が入っているだけである。同じレイヤーの `attribution` は「国土地理院 シームレス空中写真 (GSI seamlessphoto) CC BY 4.0」で、中身は国土地理院の空中写真である。`citygml`、`3dtiles`、`b3dm` は catalog 内に 0 回。

`https://z.yuiseki.net/static/` は 200 で 3,419 バイトの nginx の自動一覧を返す。この HTML に `plateau` も `citygml` も現れない。ディレクトリは openstreetmap, tokyo-ckan-files, worldpop, gtfs, ksj, mlit-1km-fromto, hdx-meta, ookla, overture, cesg, planetarble, gsi, mapterhorn, kontur, worldbank, natural-earth, gpkg, ucdp, csv, geojson, wikimedia などで、PLATEAU の置き場は無い。なお一覧は最上位のみを見ており、各ディレクトリの中までは今日たどっていない。

## 4. geospatial.jp CKAN の中にある、都市局以外による再配布

ここが最も実のある場所だった。CKAN の API は匿名で答え、`organization` と `license_id` のファセットが使える。

`https://www.geospatial.jp/ckan/api/3/action/package_search?q=PLATEAU&rows=0&facet.field=["organization","license_id"]` は 200 で `count` 495 を返し、ファセットは次のとおりだった。

- organization: `toshi` (都市局) 491、`shizuoka-city` (静岡市) 1、`hokkaidopref-ss` (総合政策部) 1、`indigo` (インディゴ株式会社) 1、`data-xformer` 1
- license_id: `plateau` (PLATEAU Site Policy 「３．著作権について」に拠る) 487、`cc-by` 2、`CC-BY` 2、`notspecified` 2、`ol` (独自利用規約) 1、`odc-odbl` 1

都市局以外の 4 件を `package_search` で個別に見た。

### 4-1. 静岡市 plateau2mc_shizuoka

「静岡市Minecraft（マイクラ）ワールドデータ_3D都市モデルPLATEAU変換」。組織は静岡市、author と maintainer はいずれも「静岡市ＤＸ推進課」。

PLATEAU 由来であることは本文が明言している。「静岡市の3D都市モデル建物データ（CityGML形式）をMinecraftのワールドに変換しています。」とあり、出典として `https://www.geospatial.jp/ckan/dataset/plateau-22100-shizuoka-shi-2023` を挙げる。資源は 43 件で、利用マニュアルの PDF と、3 次メッシュごとの `523822_mcworld.zip` のような Minecraft ワールドである。1 件を実際に取りにいくと、`ckan-storage.s3.amazonaws.com` の署名付き URL に 302 で転送され、Range 要求に 206 で 100 バイトが返った。実物がある。

再配布側の宣言は `license_id` が `cc-by`、`license_title` が「クリエイティブ・コモンズ 表示」、`license_url` が `http://www.opendefinition.org/licenses/cc-by/`。

本文の記述をそのまま引く。

> 出展：本データは、国土交通省Project PLATEAU 3D都市モデル（CCBY4.0）https://www.geospatial.jp/ckan/dataset/plateau-22100-shizuoka-shi-2023　を加工して作成しています。

> ・改変・再配布・商用利用可能です。本データ及び元データの国土交通省PLATEAUを出典として表示してください。

出典表示は本文に明記されている。元の条件との整合も取れている。CC BY 4.0 で受けて CC BY で出しており、表示義務も文章で重ねて課している。なお本文には「法令・公序良俗に反する利用、第三者の権利を侵害する行為、Minecraftライセンスに反する行為を禁止します」という追加の制限があり、これは CC BY より厳しい方向の付記なので、元より緩い宣言という問題は起きない。

### 4-2. 北海道 plateau-sapporo2020-flatgeobuf

「PLATEAU 札幌市　３D建物データ2020（FlatGeobuf）【北海道】」。組織は「総合政策部」(`hokkaidopref-ss`)。

PLATEAU 由来であることは本文が明言している。

> 国土交通省PLATEAUで公開されている札幌市の３D建物データ（ファイルジオデータベース）を、北海道がFlatGeobuf形式に変換し、QGISで活用しやすいようにしたデータです。
> 国土交通省PLATEAU（https://www.mlit.go.jp/plateau/）
> 札幌市の元データ（https://www.geospatial.jp/ckan/dataset/plateau-01100-sapporo-shi-2020）

再配布側の宣言は `license_id` が `CC-BY`、`license_title` も「CC-BY」、`license_url` は `null`。`cc-by` (小文字) が CKAN の標準の値で表題とリンクを持つのに対し、こちらは大文字の独自の値で、リンクが無い。CC BY の何版なのかはここからは決まらない。

出典表示は本文にある。author と maintainer はどちらも「－」で、組織名だけが手がかりになる。

元の条件との整合は取れている。CC BY を名乗っているので表示義務は保たれている。

今日の時点で資源の 3 件のうち 1 件が壊れている。LOD1 の `ckan01100_sapporo-shi_lod1_building.zip` は 302 のあと `fs_download` に転送され、そこが HTTP 500 で 12,692 バイトの HTML を返す。Range 要求でも素の GET でも同じ 500 で、先頭 4 バイトは `<!DO` である。LOD2 の `01100_sapporo-shi_lod2_building.zip` と説明用の JPEG は Range 要求に 206 を返すので、壊れているのは LOD1 の 1 件だけである。

### 4-3. インディゴ株式会社 plateau-tokyo23ku-building-mvt-2020

「3D都市モデル（Project PLATEAU）東京都23区（Building-MVT 2020年度）」。組織は「インディゴ株式会社」、author と maintainer は `indigo-lab`。

PLATEAU 由来であることは本文が明言している。

> [3D都市モデル（Project PLATEAU）東京都23区（CityGML 2020年度）](https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-citygml-2020) で公開されている CityGML データのうち、建築物 (bldg:Building) について Mapbox Vector Tile 形式に変換したデータセットです。

再配布側の宣言は `license_id` が `CC-BY`、`license_title` も「CC-BY」、`license_url` は `null`。北海道の件と同じ、リンクの無い独自の値である。

出典表示は本文にある。

注意すべきは、この CKAN のデータセットにはデータの実体が無いことである。資源は 1 件だけで、`name` が「GitHub repository: plateau-tokyo23ku-building-mvt-2020」、`format` が `URL`、`url` が `https://github.com/indigo-lab/plateau-tokyo23ku-building-mvt-2020` である。つまり CKAN 側は目録の項目であり、タイルそのものは GitHub にある。GitHub 側のリポジトリが何を宣言しているかは、この文書では確かめていない。GitHub 上の派生は別の文書 (`downstream-github.md`) の対象なので、そちらに任せる。

### 4-4. data-xformer fme-plateau-2025 (データではない)

「FMEワークスペース例 [PLATEAU 2025 品質検査]」。組織は `data-xformer`、author と maintainer は「飯嶋孝史」。`license_id` は `cc-by`。

これは PLATEAU のデータの再配布ではない。資源は `.fmw` の FME ワークスペース 2 件で、標準製品仕様書 5 版に基づく CityGML を検査するためのプログラムである。本文も「これらのワークスペースは非公式に作成したものであり、その実行結果は Project PLATEAU における正式な合否判定には使用できない」と書いている。都市データそのものは含まれていないので、再配布の事例からは外す。

### 4-5. 都市局自身による、既定と違うライセンスの 4 件 (参考)

再配布ではないが、ファセットを見ていて目に入ったので記録する。いずれも組織は都市局で、公式の配布である。

- `3daiready` 「3D都市モデル（PROJECT PLATEAU）3D都市モデル自動生成システム学習データ」は `license_id` が `odc-odbl`、`license_title` が「Open Data Commons Open Database License」。487 件が `plateau` の独自の値である中で、これだけ ODbL になっている。
- `plateau-27999-osaka-shi-2025` 「2025年大阪・関西万博会場　3D都市モデル（Project PLATEAU）」は `license_id` が `ol` (独自利用規約)。本文は「どなたでも無償で利用できますが、商業目的、販売促進、広告利用、商品化などの営利目的での使用は一切認められていません」として、別途の利用規約 PDF への同意を求める。CC BY 4.0 より厳しい。
- `plateau` (ポータルサイト) と `plateau-usecase-portal` は `license_id` が `notspecified`。

これらは公式側の話なので、条件の読み解きは `licence-in-practice.md` の担当である。ここでは、再配布側を評価するときに「PLATEAU なら一律 CC BY 4.0」とは限らない出どころが公式の中にもある、という事実だけを置いておく。

### 4-6. PLATEAU 由来ではないと判断したもの

`q=3D都市モデル` (count 503) のファセットには `shizuokapref` が 2 件現れる。`shizuoka-kowan` (静岡県 港湾台帳) と `shizuoka-gyokou` (静岡県 漁港台帳) で、どちらも `license_id` は `cc-by`、本文に「クリエイティブ・コモンズ（CC BY 4.0）」とある。ただし本文は「静岡県が管理する港湾の台帳データ及び港湾施設の３D都市モデルです」と書くだけで、PLATEAU を出典として挙げていない。静岡県が自ら整備した施設の 3D モデルと読める。PLATEAU 由来と判断する材料が無いので、再配布の事例からは外す。

`q=CityGML` (count 485) のファセットには `osakapref-keikakuchousei` が 2 件ある。`osaka-r7-hirakata` と `osaka-r7-higashiosaka` で、いずれも大阪府の都市計画基礎調査であり、資源に `CityGML.zip` を含む。`license_id` は `cc-by`。本文は都市計画法第 6 条に基づく調査と説明するだけで PLATEAU に触れない。形式が CityGML なだけで PLATEAU の再配布ではないと判断した。

## 5. npm と PyPI

npm に 1 件、PLATEAU 由来のデータを同梱しているものがある。PyPI には見つからなかった。

### 5-1. データを同梱していない npm パッケージ (4 件)

`https://registry.npmjs.org/-/v1/search?text=...` で `plateau`、`citygml`、`3d-tiles plateau`、`plateau 3d` を検索し、PLATEAU を名乗るものの tarball を実際に落として中身を一覧した。

| パッケージ | 版 | 宣言 | 展開後 | 中身 |
|---|---|---|---:|---|
| `mt3d-plugin-plateau` | 1.0.0 | MIT | 101,526 | `dist/` と `src/index.js` と `src/plateau.svg` のみ。データ無し |
| `oh-my-plateau` | 0.0.6 | 宣言無し (`license` が null) | 5,492 | `lib/index.js` 2,905 バイトのみ。CityGML の緯度経度を入れ替える道具 |
| `@yodolabs/plateau-r3f` | 0.1.4 | MIT | 583,167 | `dist/` のバンドルとソースマップと README のみ。データ無し |
| `@yodolabs/plateau-creative-mcp` | 0.1.3 | MIT | 363,870 | `dist/` 以下のコード 167 ファイル。`ArtifactDownloader.js` や `OverpassClient.js` があり、実行時に取りに行く作りでデータ同梱は無い |

これらはいずれも PLATEAU を扱うコードであって、PLATEAU のデータを再配布していない。MIT や無宣言であっても、同梱しているものが自作のコードであれば PLATEAU の条件とは無関係である。

### 5-2. @ortho-earth/japan はデータを同梱している

`https://www.npmjs.com/package/@ortho-earth/japan`、版 1.10.0、展開後 5,553,503 バイト、247 ファイル。説明は「Serverless, dependency-free 3D globe of Japan for any web page — GSI vector tiles and MLIT PLATEAU buildings drawn on a true sphere with WebGPU/WebGL2.」。

tarball を落として中を見ると、コードとは別に次のファイルが入っている。

- `package/assets/plateau-sets.json` 75,803 バイト。市区町村ごとに `name` と `base` と `bbox` が並ぶ配列である。例は `{"name": "いの町", "base": "https://api.plateauview.mlit.go.jp/datacatalog/3dtiles/39386-bldg-lod2-notexture-latest/", "bbox": [133.157806667, 33.510056387000006, 133.474502218, 33.831970559]}`。URL の一覧という点では目録だが、`bbox` は PLATEAU のデータセットの実際の範囲を測って書き出した値であり、PLATEAU 由来の情報である。
- `package/assets/plateau-landmarks.json` 8,869 バイト。`{"ver":1,"h":60,"note":"[名前,経度,緯度,高さm,同居企業名]。高さ降順。タイル注記と同名の棟は除外済み","f":[["東京スカイツリー",139.81092,35.71024,635,""],["横浜ランドマークタワー",139.63147,35.45459,305,""],...]}` という形で、建物の名前と座標と高さを持つ。名前と高さは PLATEAU の `gml:name` と `bldg:measuredHeight` に対応する属性であり、抽出した表である。これは紛れもなく PLATEAU から取り出した内容の同梱である。
- `package/assets/plateau-exclude.json` 1,247 バイト。`_readme` に「焼き（scripts/bake-plateau.mjs）と生経路（decodeBatch）で捨てる地物＝base URL → gml_id の配列」とあり、`https://api.plateauview.mlit.go.jp/datacatalog/3dtiles/13104-brid-lod2-texture-latest/` をキーに `brid_c31d14e8-c71d-4bf7-8313-5914aa00a1fb` のような PLATEAU の gml_id を並べる。PLATEAU の識別子そのものである。

PLATEAU 由来であることは、公式の配信元 `api.plateauview.mlit.go.jp` の URL と PLATEAU の gml_id が直接書かれていることから確定できる。

再配布側の宣言は `package.json` の `license` が `GPL-3.0-or-later`。同梱の `LICENSE` は GNU General Public License Version 3 の全文である。README の末尾はこう書いている。

> ## License
>
> GPL-3.0-or-later ([LICENSE](LICENSE)). A commercial license — without GPL obligations such as disclosing your site's source — is available: contact kenji.yoshida.home.2026@gmail.com.

出典表示はある。README に独立した節がある。

> ## Attribution (required)
>
> The map data comes with attribution obligations. **Displaying attribution is the embedder's duty.**

そこに挙がる 3 つのうちの 1 つが `[MLIT Project PLATEAU](https://www.mlit.go.jp/plateau/)` で、表示の文例も示されている。

> Source: GSI Optimized Vector Tiles (experimental), GSI elevation tiles (DEM10B), MLIT PLATEAU, JAXA AW3D30 (created by processing these data sources)

さらに「The built-in `attr` instrument (bottom right) covers this by default. If you remove it, the obligation does not disappear」と、義務が消えないことまで書いている。表示義務の扱いは丁寧である。

元の条件との整合について。CC0 のように緩める方向の食い違いではない。表示義務は保たれており、むしろ強調されている。ただし 2 点ひっかかる。

1 つ目は、GPL-3.0-or-later をデータに被せていることである。GPL はソフトウェアのライセンスであり、CC BY 4.0 のデータに GPL を重ねたとき、その同梱データの再利用者に何が課されるのかがはっきりしない。README は「The map data comes with attribution obligations」としてデータ側の義務を別枠で説明しているので、著者はコードとデータを分けて考えている可能性がある。ただしパッケージの `license` フィールドは 1 つしか無く、同梱の `assets/*.json` がその 1 つに含まれるのかどうかは、パッケージのメタデータからは決まらない。

2 つ目は、GPL の義務を外す有償の商用ライセンスを売っていることである。自作のコードについてはこれは何の問題も無い。しかし PLATEAU 由来の `plateau-landmarks.json` や `plateau-exclude.json` の部分については、著者は元データの権利者ではないので、そこに掛かる条件を外す権利を持たない。CC BY 4.0 の表示義務は、著者が誰に何を売っても消えない。README がまさに「If you remove it, the obligation does not disappear」と書いているので、著者自身がこの区別を理解している可能性は高い。それでも、パッケージのライセンス表記を見ただけの人が「有償版なら表示不要」と誤解しうる構えになっている。断定はしない。これは読んだ範囲から立てた指摘であって、著者に確認したものではない。

### 5-3. PyPI

見つからなかった。`https://pypi.org/pypi/plateau/json` は 200 を返すが、これは「A Python library to manage (create, read, update, delete) large amounts of tabular data in a blob store」で、kartothek の後継にあたる MIT ライセンスのライブラリである。国土交通省の PLATEAU とは名前が同じだけの別物である。`https://pypi.org/search/?q=plateau`、`q=citygml`、`q=plateau-3d` はいずれも 200 を返すが、PyPI の検索は HTML のみで JSON の API を持たないため、今日は機械可読な形での網羅的な確認ができていない。PyPI に PLATEAU のデータを同梱したパッケージがあるかどうかは未確認とする。

## 未確認のまま残ったこと

- Source Cooperative 全体の横断検索。JSON の API が見つからず、smartmaps 組織のページしか見ていない。他の組織に PLATEAU の再配布があるかは未確認である。
- `4-3` のインディゴ株式会社の実体である GitHub リポジトリ `indigo-lab/plateau-tokyo23ku-building-mvt-2020` が宣言しているライセンス。GitHub 上の派生は別の文書の担当なので今日は開いていない。
- PyPI の網羅的な検索。HTML しか返らないので機械可読な確認ができていない。
- `z.yuiseki.net/static/` は最上位の一覧のみを見た。各ディレクトリの中に PLATEAU 由来のファイルが混ざっている可能性は否定できない。
- `assets.cms.plateau.reearth.io` および `api.plateauview.mlit.go.jp` そのものは公式の配信口なので、今日は再配布の対象として調べていない。
- 再配布側が宣言したライセンスが、実際にデータのどの範囲に掛かっているかの法的な評価。ここに書いたのは各者が何と書いたかと、その字面が PLATEAU の条件とどう並ぶかだけである。
