# PLATEAU を使う GitHub のプロジェクトがライセンスをどう扱っているか

2026-09-30 に読んで確かめた内容。GitHub の検索 API でリポジトリを列挙し、そのうち 38 件について
リポジトリのメタデータ、ファイルツリー、README、リリース資産、一部のソースファイルを実際に取得して
数えた。数値はすべてこの日に取得したものであり、この 38 件の外側には一般化しない。

## 先に結論

調べた 38 件のうち、PLATEAU 由来のデータをリポジトリ本体またはリリースに含めて再配布していたのは
18 件だった。その 18 件のうち 16 件はデータの出典を書いていた。「ほとんどが何も言っていない」という
仮説は、この標本では成り立たなかった。ただし後述のとおり標本の選び方に偏りがあるので、日本語の
オープンデータ全体に広げて読むことはできない。

コードだけでデータを実行時に取得する 19 件は、データのライセンスを書く義務を負わない。これを
不履行として数えてはいない。

## 1. 検索 API で何件見えたか

gh CLI の認証済みトークンで叩いた。認証済みなので検索 30 回/分、コード検索 10 回/分、通常 API
5000 回/時であり、呼び出しの間隔を空けたのでスロットリングは発生しなかった。

リポジトリ検索 (https://api.github.com/search/repositories?q=...) の total_count:

| クエリ | 件数 |
|---|---|
| `PLATEAU CityGML` | 54 |
| `PLATEAU 3D都市モデル` | 37 |
| `PLATEAU 都市モデル` | 37 |
| `PLATEAU MLIT` | 27 |
| `PLATEAU 国土交通省` | 6 |
| `plateau in:name 3d` | 12 |
| `PLATEAU plateau-` | 3033 |
| `plateau geospatial.jp` | 0 |

`PLATEAU plateau-` の 3033 件は地形としての plateau を含む雑音であり、母集団の推定には使えない。
`plateau geospatial.jp` が 0 件なのは、リポジトリ検索が名前と説明と README の一部しか見ないため
であって、geospatial.jp を参照しているリポジトリが無いという意味ではない。実際、後述のコード検索
では 972 件が当たっている。

コード検索 (https://api.github.com/search/code?q=...) の total_count:

| クエリ | 件数 |
|---|---|
| `出典 PLATEAU` | 1456 |
| `www.geospatial.jp plateau` | 972 |
| `assets.cms.plateau.reearth.io` | 281 |

コード検索の結果は API 側で先頭 1000 件までしか返らず、私が実際に見たのは各クエリの先頭 100 件だけ
である。`assets.cms.plateau.reearth.io` の先頭 100 件には maplibre/navara が 13 ファイル、
eukarya-inc/PLATEAU-VIEW が 10 ファイル、reearth/reearth-visualizer が 9 ファイルで現れた。

上の 4 つのリポジトリ検索の結果を統合して重複を除くと 100 件になった。この 100 件が標本の母集団である。

## 2. 標本 38 件の選び方

上記 100 件から、次の規則で 38 件を選んだ。

1. 公式の Project-PLATEAU org 以外でスター数上位のもの全部 (11 件)
2. 名前または説明からデータの変換物を配布していそうなもの全部 (mvt, pmtiles, tiles, data, db, import)
3. スター 0 の小規模なアプリやビューアから、地域と用途が重ならないように広く
4. 対照として公式 org から 2 件 (plateau2minecraft, PLATEAU-VIEW-4.0)

規則 2 のせいで、再配布しているリポジトリが標本内で過剰に代表されている。つまり「再配布 18 件」と
いう比率は母集団の比率ではない。一方で「再配布している 18 件のうち何件が出典を書いたか」という
比率のほうは、再配布側を意図的に集めた結果なので、再配布するリポジトリの実態には近いはずである。

## 3. PLATEAU 由来データを再配布している 18 件

判定は、リポジトリのファイルツリー (git/trees?recursive=1) とリリース資産の一覧を取得して、
PLATEAU 由来のタイル、CityGML、PMTiles、GeoJSON、b3dm、CSV が含まれるかで行った。

| リポジトリ | スター | リポジトリのライセンス | LICENSE ファイル | 再配布しているもの | 出典 | データのライセンス |
|---|---|---|---|---|---|---|
| Synesthesias/PLATEAU-SDK-for-Unity | 120 | MIT | あり | Tests/TestData の CityGML 一式 | なし | なし |
| Project-PLATEAU/plateau2minecraft | 85 | MIT | あり | world_data/world_data.zip (29MB) | なし | なし |
| ozekik/plateaukit | 30 | MIT | あり | tests/fixtures の CityGML zip 3 本 | あり | CC BY 4.0 を明記 |
| indigo-lab/plateau-tokyo23ku-building-mvt-2020 | 14 | なし | あり | pbf タイル 3672 枚 | あり | CC-BY-4.0 を明記 |
| indigo-lab/plateau-lod2-mvt | 9 | CC-BY-4.0 | あり | pbf タイル 3672 枚 | あり | CC-BY-4.0 を明記 |
| raokiey/plateau-gis-data-downloader | 3 | NOASSERTION | あり | data/code_list.csv (11MB) | あり | CC BY 4.0 を明記 |
| ymd5022002/plateau-lod2-mvt-ic4 | 1 | CC-BY-4.0 | あり | pbf タイル 3672 枚 | あり | CC-BY-4.0 を明記 |
| tatsuya1970/hiroshima-kart | 0 | NOASSERTION | あり | public/data の LOD2 メッシュとテクスチャ | あり | CC BY 4.0 を明記 |
| khttr8921/nagoya-3d-map-public | 0 | MIT | あり | artifact/data の区別建物 JSON 16 本 | あり | 条件のみ記載 |
| mypaceotoko/jiyugaoka-digital-twin | 0 | NOASSERTION | あり | data/processed/plateau_buildings.json ほか | あり | 政府標準利用規約 2.0 を明記 |
| shiwaku/plateau-2024-building-attributes | 0 | MIT | あり | output/ の属性整備状況 CSV 3 本 | あり | 利用規約へのリンク |
| shiwaku/mlit-plateau-bldg-pmtiles | 0 | MIT | あり | summary/2023 の集計 CSV | あり | CC BY 4.0 を明記 |
| shu-ii/plateau-data | 0 | なし | なし | リリース資産の PMTiles 2 本 | あり | CC-BY-4.0 を明記 |
| mikazuki-main/plateau-kouchi-building-mvt-2023 | 0 | CC-BY-4.0 | あり | pbf タイル 213 枚 | あり | CC-BY-4.0 を明記 |
| eda-hotori/yumeshima2025-xyz-tiles | 0 | なし | なし | 航空写真の xyz タイル 2273 枚 | あり | 配布元規約を引用 |
| donkeykey/futako-hanabi | 0 | なし | なし | public/data/tiles の pbf 493 枚 | あり | なし |
| naogify/silhouette-guessr | 0 | なし | なし | public/tile3d の b3dm 391 本 | あり | なし |
| wata909/plateau-tottori | 0 | なし | なし | docs/data の関連 GeoJSON 7 本 | あり | サイトポリシーへのリンク |

集計。再配布 18 件のうち、

- 出典を書いているもの 16 件、書いていないもの 2 件
- データのライセンス名 (CC BY 4.0 など) を明記しているもの 10 件
- ライセンス名は書かず規約や条件へのリンクにとどめたもの 4 件
- データについて何も書いていないもの 4 件
- 出典もライセンスも一切書いていないもの 2 件 (Synesthesias/PLATEAU-SDK-for-Unity と
  Project-PLATEAU/plateau2minecraft、いずれも国土交通省の委託または直営のリポジトリ)
- LICENSE ファイルが無いもの 5 件 (shu-ii/plateau-data, eda-hotori/yumeshima2025-xyz-tiles,
  donkeykey/futako-hanabi, naogify/silhouette-guessr, wata909/plateau-tottori)

## 4. コードだけの 19 件

これらは PLATEAU のデータを実行時に取得するか、利用者が自分でダウンロードする前提であり、
データのライセンスを掲げる義務は無い。それでも書いているかどうかだけを記録した。

| リポジトリ | スター | ライセンス | データのライセンスへの言及 |
|---|---|---|---|
| MIERUNE/plateau-gis-converter | 103 | MIT | 著作権の帰属のみ |
| ksasao/PlateauCityGmlSharp | 47 | Apache-2.0 | なし |
| pixelx-jp/plateau-creative-mcp | 32 | MIT | CC BY 4.0 を明記 |
| nneri-hin/Plateau-Blender-Importer | 28 | MIT | なし |
| MIERUNE/plateau-qgis-plugin | 12 | GPL-2.0 | CC BY 4.0 と政府標準利用規約 2.0 を明記 |
| pixelx-jp/plateau-bridge | 9 | MIT | CC BY 4.0 を明記 |
| shiena/godot-plateau | 9 | MIT | なし |
| pacificspatial/flateau | 14 | CC0-1.0 | CC BY 4.0 と出典文を明記 |
| raokiey/plateau-geo-tools | 1 | MIT | 出典のみ |
| BoxPistols/drone-mapper-plateau | 1 | なし | CC BY 4.0 を明記 |
| Invest-AItech/plateau-building-db | 0 | なし | CC BY 4.0 を明記 |
| Y-Kanekoo/machi-karte | 0 | MIT | CC BY 4.0 と政府標準利用規約を明記 |
| shiwaku/plateau-lod1-bldg-pmtiles | 0 | CC-BY-4.0 | CC-BY-4.0 を明記 |
| shiwaku/mlit-plateau-bldg-2023-on-maplibre | 0 | MIT | 地図の attribution にのみ記載 |
| kaujisoft/plateau_to_minecraft | 0 | なし | 利用規約に従えとだけ記載 |
| uedayou/plateau-elevation-normalizer | 0 | MIT | なし |
| marzipan99/plateau-viewer | 0 | MIT | なし |
| kentaro-maker/nextjs-threejs-city | 0 | なし | なし |
| osmfj/MLIT_PLATEAU_import | 0 | CC0-1.0 | なし |

集計。コードのみ 19 件のうち、ライセンス名を明記 8 件、規約や出典のみ 4 件、言及なし 7 件。

判別できなかったものが 1 件ある。Project-PLATEAU/PLATEAU-VIEW-4.0 は
extension/src/shared/plateau/featureInspector/attributes_test_v3.csv (4.6MB) を含むが、これが
PLATEAU の実データの再配布なのか属性仕様のテスト用表なのか、ファイルを開かずには決められなかった
ので、再配布 18 件にも コードのみ 19 件にも入れていない。標本 38 件の内訳は 18 + 19 + 1 である。

## 5. とくによくやっている例

tatsuya1970/hiroshima-kart は、コードとデータでライセンスを分け、さらに加工内容をファイル単位で
表にしている。https://github.com/tatsuya1970/hiroshima-kart/blob/main/DATA_LICENSE.md

> このリポジトリは、**コード**と**データ**で異なるライセンスが適用されます。
> 出典: 国土交通省「3D都市モデル（Project PLATEAU）広島市（2024年度）」
> ライセンス: クリエイティブ・コモンズ 表示 4.0 国際 (CC BY 4.0)

加工内容の表には「CityGML から頂点・UV を抽出し、テクスチャアトラスの座標系へ変換」「1,386 棟分の
個別画像を 4096px のアトラス 6 枚へ再配置」といった具体が並んでいる。CC BY が求める改変の表示を、
条文の文言をなぞるのではなく実際の処理として書いた例であり、調べた 38 件で最も厚い。

mypaceotoko/jiyugaoka-digital-twin は ATTRIBUTION.md を別立てにし、OpenStreetMap の ODbL と
PLATEAU を取り違えないように分けている。https://github.com/mypaceotoko/jiyugaoka-digital-twin/blob/main/ATTRIBUTION.md

> The code license (MIT) does **not** apply to the data; each data source keeps its own license.
> **License**: 政府標準利用規約（第2.0版）準拠 / compatible with CC BY 4.0
> **Credit**: 出典: 国土交通省 Project PLATEAU（東京都23区 3D都市モデル）を編集・加工して作成

PLATEAU のライセンスを CC BY 4.0 とだけ書かず、政府標準利用規約 2.0 との関係まで書いているのは
38 件のうちこれと MIERUNE/plateau-qgis-plugin と Y-Kanekoo/machi-karte の 3 件だけだった。

ozekik/plateaukit は、再配布しているのがテスト用の CityGML 3 本だけであるにもかかわらず、その
3 本をファイル名で名指しして出典を書いている。https://github.com/ozekik/plateaukit#クレジット-credits

> - `tests/fixtures/30422_taiji-cho_2021_citygml_2_op.zip`, `tests/fixtures/30422_taiji-cho_city_2021_citygml_4_op.zip`: PLATEAUデータセット ([国土交通省 Project PLATEAU](https://www.mlit.go.jp/plateau/site-policy/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ja))

pixelx-jp/plateau-bridge は、出典表示を文書ではなく成果物に自動で埋め込む方式をとっている。
https://github.com/pixelx-jp/plateau-bridge/blob/main/src/plateau_bridge/attribution.py

> Per plan §Attribution: every artifact carries provenance, so downstream tools
> (poster renderers, GLB exporters, MCP servers) inherit it automatically.

PMTiles や GeoParquet では属性列として、3D Tiles では tileset.json のルートの asset.extras に
書き込む。出典が人の善意ではなくパイプラインの出力として保たれる設計であり、調べた中で唯一だった。

indigo-lab/plateau-lod2-mvt の README の書き方は、ymd5022002/plateau-lod2-mvt-ic4 と
mikazuki-main/plateau-kouchi-building-mvt-2023 にそのまま引き継がれている。後者は高知市という
別のデータセットに書き換えたうえで、同じ構造を保っている。

> 本データセットは [CC-BY-4.0](LICENSE) で提供されます。
> また、本データセットは [3D 都市モデル（Project PLATEAU）高知市（2023 年度）](https://www.geospatial.jp/ckan/dataset/plateau-39201-kouchi-shi-2023) を加工して作成したものです。
> 本データセットの使用・加工にあたっては、[PLATEAU Policy](https://www.mlit.go.jp/plateau/site-policy/) を確認し、権利者の権利を侵害しないように留意してください。

出典の書き方が複製されて伝播しているのは、この標本で見つかった唯一の伝播経路である。

## 6. 引っかかる例

eda-hotori/yumeshima2025-xyz-tiles は、2025 年大阪・関西万博会場の航空写真を xyz タイル 2273 枚に
変換して GitHub Pages で配信している。README は配布元の条件を正直に引用している。
https://github.com/eda-hotori/yumeshima2025-xyz-tiles

> 利用規約は配布元ページに準じます。
> https://www.geospatial.jp/ckan/dataset/plateau-27999-osaka-shi-2025
> > どなたでも無償で利用できますが、商業目的、販売促進、広告利用、商品化などの営利目的での使用は一切認められていません。

PLATEAU のデータがすべて CC BY 4.0 だという通念に対する反例がここにある。引用された条件が正しい
なら、このデータセットは CC BY 4.0 ではなく、営利利用を禁じる個別条件が付いている。出典を書いた
うえで条件も引用しているので、この作者の扱いは雑ではない。ただし、その条件を保ったまま再配布物を
公開の CDN に置くことが配布元の想定どおりかは、私には判断できなかった。

naogify/silhouette-guessr は PLATEAU の 3D Tiles を b3dm 391 本そのまま含んでいるが、LICENSE
ファイルが無く、GitHub のライセンス欄も空である。README には出典だけがある。
https://github.com/naogify/silhouette-guessr

> ## 出典
> - 国土交通省 PLATEAU（https://www.mlit.go.jp/plateau/）

出典としては足りているが、ライセンスの明示が無いリポジトリは既定では全権利留保として読まれる。
CC BY 4.0 のデータを含むリポジトリ全体が全権利留保に見える状態は、再利用しようとする側から見ると
上流より制限が強く見えてしまう。同じ形は donkeykey/futako-hanabi と wata909/plateau-tottori にも
ある。3 件とも出典は書いているので、意図的な囲い込みではなく LICENSE を置き忘れた形である。

Synesthesias/PLATEAU-SDK-for-Unity は Tests/TestData 以下に PLATEAU の CityGML 一式を含むが、
README に出典の記載は無い。ただしこれは国土交通省の委託で開発された SDK であり、README は
「ソースコードおよび関連ドキュメントの著作権は国土交通省に帰属します」と書いている。権利者自身が
配っている形なので、他者への出典表示義務が生じる場面とは異なる。Project-PLATEAU/plateau2minecraft
の world_data.zip も同じ立場である。この 2 件を落ち度として数えるのは公平でない。

方法上の注意として、shiwaku/mlit-plateau-bldg-2023-on-maplibre の README は 0 バイトである。
README だけを見る調査ならこれは無言に分類される。しかし index.html を開くと、地図の attribution
コントロールに出典が入っている。

> attribution: '<a href="https://www.geospatial.jp/ckan/dataset/plateau">3D都市モデルPLATEAU建築物モデル（国土交通省）</a>'

見せる先が README ではなく地図の画面であるという判断であり、CC BY の求める合理的な方法としては
むしろ的確である。README 検査だけで無言と数える調査は、この種の実装を取りこぼす。

## 7. 決められなかったこと

- 母集団の大きさ。リポジトリ検索は名前と説明と README の一部しか見ず、クエリごとに 54 件から
  3033 件まで散らばった。コード検索の 1456 件、972 件、281 件も先頭 1000 件までの打ち切りが入る。
  PLATEAU を使うリポジトリの総数は、この方法では出せない。
- Project-PLATEAU/PLATEAU-VIEW-4.0 の attributes_test_v3.csv が実データかテスト用の表か。
- リポジトリ外に置かれたデータの出典表示。shiwaku 系の PMTiles は S3、wata909/plateau-tottori の
  PMTiles は R2、pacificspatial/flateau の GeoParquet は Source Cooperative にある。配信先での
  出典表示の有無は、GitHub 側からは確かめられなかった。
- 各データセットの実際の利用条件。geospatial.jp の個別ページを開いていないので、eda-hotori が
  引用した営利禁止条件がその 1 データセット固有のものか、より広い範囲に及ぶのかは確認していない。
- 私が見たのは README とファイルツリーと一部のソースだけである。各リポジトリのサイトや配布物の
  中に別の出典表示があるかどうかは、本文中で個別に触れた 2 件を除いて調べていない。
