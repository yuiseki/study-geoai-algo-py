# geofabrik

2026-09-28 に読んで確かめた内容。大きさは HEAD の `Content-Length` (バイト)、時刻は UTC。

- `https://download.geofabrik.de/`
- ドイツの Geofabrik GmbH が OSM planet を地域ごとに切り出して配っているもの。形式は .osm.pbf が本体で、小さめの地域には Shapefile (`.shp.zip`) と GeoPackage (`.gpkg.zip`) もある。
- 機械向けの索引は `https://download.geofabrik.de/index-v1.json` (境界ポリゴン付き)。境界を抜いた `index-v1-nogeom.json` もあるとサイトの説明にある (こちらは読んでいない)。
- cng-data-antigravity は組み込みの出どころ `osm-japan` `osm-kanto` `osm-kansai` `osm-chubu` `osm-kyushu` `osm-tohoku` `osm-hokkaido` と、大陸・国 (`osm-asia` `osm-europe` など)、試験用の `osm-monaco` `osm-niue` にこれを使う (origin/main の `sources/geofabrik.py`)。`adapters/osm_pbf.py` は索引から `urls.pbf` を引き、PBF を丸ごとダウンロードしてから osmium で bbox を切り出す。日本全体なら 2.5GB を落とすことになる。

## index-v1.json

大きさ 3,791,593、Last-Modified 2026-09-27T03:59:52Z、ETag `"39dae9-65c6efb4a5ac1"`。全体をダウンロードして Python で読んだ。

- GeoJSON の FeatureCollection。地域 (feature) は 555。geometry はすべて MultiPolygon。`id` の重複は無い。
- properties: `id` と `name` と `urls` は全件、`parent` は 546 件、`iso3166-1:alpha2` は 191 件、`iso3166-2` は 71 件。ISO コードはどちらも配列。
- 最上位 (`parent` が無い) は 9: africa, antarctica, asia, australia-oceania, central-america, europe, north-america, russia, south-america。russia は大陸と同じ階層にある。
- 深さの分布: 最上位 9、1 段下 266、2 段下 207、3 段下 72、4 段下 1 (enfield → greater-london → england → united-kingdom → europe)。
- 子の多い親: north-america 62, africa 56, europe 53, england 47, asia 39, china 33, france 27, australia-oceania 23。
- `urls` の種類と件数: `pbf` 555, `pbf-internal` 555, `history` 555, `taginfo` 555, `updates` 555, `shp` 526。`pbf-internal` と `history` は `osm-internal.download.geofabrik.de` にあり、OSM アカウントでのログインが要る (サイトの説明による)。
- `shp` が無い 29 地域は大きいもの (大陸、us、germany、france、japan など)。
- 索引に `gpkg` の URL は無い。地域のページには `.gpkg.zip` が並んでいる (下記)。

## 日本と地方

日本は asia の子 `japan`、その子に 8 地方がある。URL は `https://download.geofabrik.de/asia/japan-latest.osm.pbf` と `https://download.geofabrik.de/asia/japan/<地方>-latest.osm.pbf`。

`-latest` は 302 で日付付きのファイル (`japan-260927.osm.pbf` など) へ飛ぶ。大きさはリダイレクト先のもの。

| id | 名前 | 実体 | 大きさ | 更新時刻 | .md5 |
|---|---|---|---|---|---|
| japan | Japan | japan-260927.osm.pbf | 2,538,602,425 | 2026-09-27T22:59:16Z | 77936bbe06258a7b2a4b0f00ff00ced9 |
| hokkaido | Hokkaidō | hokkaido-260927.osm.pbf | 189,226,627 | 2026-09-27T23:06:10Z | 38caccc44077198d6b9386ebbeb29b61 |
| tohoku | Tōhoku region | tohoku-260927.osm.pbf | 309,420,387 | 2026-09-27T23:05:12Z | b1f09ea61840f17b5e146b4f644a2691 |
| kanto | Kantō region | kanto-260927.osm.pbf | 514,374,202 | 2026-09-27T23:08:18Z | dfdd9e7226c5af60390ed78a9df51361 |
| chubu | Chūbu region | chubu-260927.osm.pbf | 510,905,267 | 2026-09-27T23:07:38Z | 447e43094b7983460f3acb1181406a09 |
| kansai | Kansai region (a.k.a. Kinki region) | kansai-260927.osm.pbf | 352,217,374 | 2026-09-27T23:03:26Z | 3794bb609a19c273da913110f848c524 |
| chugoku | Chūgoku region | chugoku-260927.osm.pbf | 236,159,583 | 2026-09-27T23:02:47Z | 956b7ee478eb163403069eb7115750c5 |
| shikoku | Shikoku | shikoku-260927.osm.pbf | 89,376,638 | 2026-09-27T23:05:05Z | 95aca1e23c1a94a2406ca087e3a94984 |
| kyushu | Kyūshū | kyushu-260927.osm.pbf | 314,848,808 | 2026-09-27T23:04:20Z | 915bd730c8a6b5e8f277ab3babb56d0b |

- md5 は `<地方>-latest.osm.pbf.md5` の中身 (md5 とファイル名 1 行)。ファイル本体の md5 は計算していない (全体を読む必要があるため)。
- 8 地方の合計は 2,516,528,886 で、japan より 22,073,539 小さい。地方の境界の隙間や海域の扱いの差と思われるが確かめていない。
- japan には `.shp.zip` が無い (索引にも無く、ページにも「not available for this region; try one of the sub-regions」とある)。
- 地方には `.shp.zip` と `.gpkg.zip` がある。kanto: `kanto-260927-free.shp.zip` 1,030,421,142 (2026-09-28T03:24:09Z)、`kanto-260927-free.gpkg.zip` 1,066,651,425 (同 03:24:24Z)。PBF より 4 時間ほど遅れて作られる。
- Shapefile は「完全ではなく、地物と属性を選んだもの」とサイトの技術説明にある。層の定義は `http://download.geofabrik.de/osm-data-in-gis-formats-free.pdf` (読んでいない)。

### PBF のヘッダ

japan と kanto は先頭 64KB を範囲要求 (206 を確認済み) で読み、HeaderBlock を Python 標準ライブラリで解いた。

| | japan-260927 | kanto-260927 |
|---|---|---|
| writingprogram | osmium/1.16.0 | osmium/1.16.0 |
| features | OsmSchema-V0.6, DenseNodes | 同じ |
| optional | Sort.Type_then_ID | 同じ |
| bbox 経度 | 122.5607 から 154.4709 | 134.045154 から 155.605818 |
| bbox 緯度 | 20.08228 から 45.815403 | 18.625054 から 37.15988 |
| 複製時刻 | 2026-09-27T20:23:36Z | 2026-09-27T20:23:36Z |
| 複製番号 | 4922 | 3440 |
| osmosis_replication_base_url | https://download.geofabrik.de/asia/japan-updates | https://download.geofabrik.de/asia/japan/kanto-updates |

- `Has_Metadata` が無い。サイトの説明どおり、利用者名・利用者 ID・変更セット ID は抜いてある (EU の個人情報保護のため)。全メタデータ付きは内部サーバーで OSM 貢献者だけが取れる。
- 索引の kanto の境界は 3 つのポリゴンで、経度 134.5757 から 154.4709、緯度 20.08228 から 37.15988。東端が南鳥島、南端が沖ノ鳥島の辺りまで届く。PBF ヘッダの bbox はこれより一回り広い。
- `updates/state.txt` は japan も kanto も `timestamp=2026-09-27T20:23:36Z`、元の OSM minutely の番号 7305216。sequenceNumber は PBF ヘッダの複製番号と一致した。

## 更新の頻度と古い版

- トップページに「updated every day」、技術説明に「Once a day, around 21:00 CET」に planet を更新して地域へ分割するとある。「Every couple of months」に新しい planet で作り直すともある。
- 実際、日付付きの PBF は 260921 から 260927 まで毎日並んでいる。大きさは 1 日に 80 万から 130 万バイトほど増えている (260921: 2,532,137,304、260927: 2,538,602,425)。
- 古い版はページの「raw directory index」に残っている。japan では毎年 1 月 1 日の版が 2014 年から (japan-140101.osm.pbf: 886,767,352)、月初の版が 260701, 260801, 260901、日次が直近 7 日。
- 年ごとの 1 月 1 日版の大きさ: 2014 886,767,352 / 2016 963,967,488 / 2018 1,168,789,601 / 2020 1,453,341,364 / 2022 1,710,874,862 / 2024 1,960,084,626 / 2026 2,342,296,009。12 年で 2.6 倍。
- `.osc.gz` の差分が `*-updates/` にあり、osmium や osmosis で手元の PBF を追いかけられる。

## z.yuiseki.net の複製との比較

`z-yuiseki-static/openstreetmap.md` の region/ にある日本の版と比べた。

| ファイル | 大きさ | 複製時刻 |
|---|---|---|
| z: japan-260423.osm.pbf | 2,407,046,008 | 2026-04-23T20:21:08Z |
| 本家: japan-260927.osm.pbf | 2,538,602,425 | 2026-09-27T20:23:36Z |
| z: kanto-260423.osm.pbf | 463,775,701 | 2026-04-23T20:21:08Z |
| 本家: kanto-260927.osm.pbf | 514,374,202 | 2026-09-27T20:23:36Z |

- writingprogram (osmium/1.16.0)、ヘッダの bbox は japan、kanto とも z の 260423 版と同じ値だった。
- 本家のディレクトリには 260423 の版はもう無い (月初版は 260701 から、年初版は 260101)。z の複製は本家から消えた版を保っている。

## 気をつけること

- `-latest` の URL は 302 リダイレクト。HEAD で大きさを見るならリダイレクトを追う (`curl -L`)。追わないと `Content-Length` が出ない。
- 索引の `urls` には `gpkg` が無いが、地方のページには `.gpkg.zip` がある。技術説明には `bz2` のキーも書かれているが、索引の 555 件のどれにも無い。
- 月初版は 260101 のあと 260701 まで飛んでいる (260201 から 260601 がページに無い)。
- japan-200101.osm.pbf だけ更新時刻が 2020-02-19 で、ほかの年初版 (1 月 2 日前後) とずれている。
- cng-data-antigravity の組み込みは 7 地方で、索引にある chugoku と shikoku が入っていない。shikoku は 89MB で日本の地方では最小なので、手元で試すにはこれが向く。
- 日本の地方の PBF は小さくても 89MB あり、全体をダウンロードするのは 50MB 超になる。小さく試すなら monaco や andorra (z 側の記録で 0.65MB から 3.4MB) を使う。

## ライセンス

- サイトのフッターに「Data processed by Geofabrik GmbH and created by OpenStreetMap Contributors | License: ODbL 1.0」とあり、ODbL は `http://opendatacommons.org/licenses/odbl/` へリンクしている。技術説明のページには「Data/Maps Copyright 2019 Geofabrik GmbH and OpenStreetMap Contributors」と「Data: ODbL 1.0」、`https://www.openstreetmap.org/copyright` へのリンクがある。
- 帰属表示は「© OpenStreetMap contributors」(OSM 本家の copyright ページ) に従う形になる。Geofabrik 独自の帰属表示の要求があるかは未確認。

## 12 ステップでの使いどころ (案)

- 7: shikoku などの地方 PBF から道路網を作り、Dijkstra と A* を比べる。慣れたら kanto。日付付きの版があるので、道路の追加前後で最短経路が変わるかも見られる。
- 8, 9: 同じ道路網と POI (amenity など) で施設配置と割り当ての MILP。地方ごとに規模を変えて解ける大きさを測れる。
- 5: POI の点を DBSCAN にかけて繁華街を切り出す。
- 1, 2, 3, 11: `.gpkg.zip` の建物や土地利用の層を表にして、面積や種類から別の属性を回帰・分類する。SHAP で効いた特徴を見る。
- 4: 地方ごとに分けて学習と評価をすれば、地域をまたいだときの成績の落ち方 (空間的な外挿) を確かめられる。日付付きの版を使えば、未来のデータを混ぜるリークの練習にもなる。
- 6: 年初版を並べて、地方ごと・タグごとの件数の変化を行列にして PCA。ただし件数を数えるには PBF 全体を読む必要がある。
- 10, 12: 直接の材料は無い。7 から 9 の道路網と施設を流用する。

## 取り出し方

split。地域ごとに事前分割されていて、必要な地域のファイルだけ引ける。ただしその中の PBF は whole で、部分読みはできない。2026-09-30 に実測した。

分割の単位は Geofabrik が定義した地域で、`https://download.geofabrik.de/index-v1.json` に 555 件ある。この索引は `Content-Length` 3,791,593、`Accept-Ranges: bytes` を返し、`curl -r 0-1023` は 206 と 1,024 バイトを返した。各 feature が MultiPolygon の境界を持つので、bbox から地域を選んでから引ける。目録として使えるのはこの索引までで、その先のファイルには索引が無い。

日本で最小の地方 shikoku で確かめた。

| 項目 | 値 |
|---|---|
| 要求した URL | `https://download.geofabrik.de/asia/japan/shikoku-latest.osm.pbf` |
| 応答 | 302 で `shikoku-260929.osm.pbf` へ、追って 200 |
| 大きさ | 89,483,612 バイト、`Accept-Ranges: bytes` |
| Range 要求 | `curl -r 0-1023` が 206 と 1,024 バイト |

Range は HTTP としては通るが、PBF の構造上そこから必要な範囲を選べない。先頭 256 バイトを読むと `00 00 00 0e` に続いて `OSMHeader` があり、BlobHeader は 14 バイト、その datasize は 180 だった。つまり最初のデータ blob はバイト 198 から始まる。以降はこの blob が末尾まで並ぶだけで、どの blob にどの範囲が入っているかを示す表はファイルのどこにも無い。bbox で切るには全体を読んで osmium にかけるしかない。

`.shp.zip` と `.gpkg.zip` も同じで、zip の中央ディレクトリは末尾にあり、Range で中身を選ぶことはできない。

したがって、最小単位は地域 1 つ分のファイル全体になる。日本の地方では shikoku の 89MB が最小で、日本全体なら 2.5GB を落とすことになる。もっと小さく試すなら monaco や andorra。
