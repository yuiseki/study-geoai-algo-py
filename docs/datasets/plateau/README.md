# PLATEAU (国土交通省の 3D 都市モデル)

2026-09-28 に入口のページだけを見た。中身は調べていない。

- 入口: <https://www.mlit.go.jp/plateau/open-data/>
- データの実体: G 空間情報センター (社会基盤情報流通推進協議会が運用) の PLATEAU オープンデータポータル
- 入口のページの記載: 2021 年度の 56 都市から始まり、2025 年度末に約 300 都市まで広げる予定。形式は CityGML が基本で、都市ごとに地物の LOD と属性の一覧がある。

## この学習では深追いしない

- 量が多く、CityGML は扱いに手間がかかる。
- ライセンスの読み方がややこしい。入口のページには条件が書かれておらず、G 空間情報センターのデータセットごとに確かめる必要がある。
  以前の別の作業では「CC BY 4.0 と互換の枠だが、license_id は独自の値で、測量法の注記が付く」と整理した (今回は確かめていない)。
- 必要なものはほかで足りる。
  - 建物の 3D Tiles (属性付き): source.coop の [smartmaps/xing](../source-coop-smartmaps/xing.md) が PLATEAU を変換したもの
  - 建物の形: [Overture Maps](../stac/overture-maps.md) の buildings
  - 電柱、街灯、歩道など街路の状態: [みちよみ](../michiyomi/README.md)

使うことになったら、そのときに対象の都市とデータセットを決めて、ライセンスをデータセットごとに確かめる。

## 取り出し方

区分は catalog。深追いしないと決めた出どころだが、取り方そのものは調べれば分かったので記録しておく。ブラウザは要らない。G 空間情報センターの CKAN API が匿名で答える。

2026-09-30 に測った。

| 要求 | 応答 |
|---|---|
| `GET https://www.geospatial.jp/ckan/api/3/action/package_search?q=PLATEAU&rows=1` | 200、719,720 バイト。`result.count` は 495 |
| `GET .../package_search?fq=license_id:plateau&rows=0` | 200。`count` は 511 |
| `GET .../package_search?q=3D都市モデル&rows=0` | 200。`count` は 503 |
| `GET .../package_show?id=plateau-tokyo23ku-citygml-2020` | 200。`resources` のうち ZIP は 14 件 |

標準の CKAN API なので、`q` で検索し、`fq` で `license_id` などを絞り、`package_show` で 1 データセットの資源一覧を取れる。目録としてはこれで足りる。ただし `resources` の `size` は今日見た範囲ではすべて `null` で、大きさは目録からは分からない。実物に HEAD を投げて測ることになる。

分割の単位は 2 次メッシュ。東京 23 区の CityGML 2020 年度版の資源名は `533925`、`533934` のように並んでおり、それぞれが 1 zip になっている。ほかに「メタデータ」「拡張製品仕様」「コードリスト」の zip がある。

実体は AWS S3 で、こちらは Range が本当に効く。

| ファイル | 応答 |
|---|---|
| `https://gsic-opendata.s3.ap-northeast-1.amazonaws.com/national-gov/mlit/city-bureau/3d-city-model/2020/plateau-tokyo23ku-citygml-2020/tokyo23ku/udx131002020_2.zip` (メタデータ) | HEAD 200、`Content-Length: 6848`、`Accept-Ranges: bytes`。`-r 0-1023` は 206、`Content-Range: bytes 0-1023/6848` |
| 同じ場所の `533925_2.zip` (メッシュ 1 枚) | HEAD 200、`Content-Length: 66238706`。`-r 0-1023` は 206、`Content-Range: bytes 0-1023/66238706` |

したがって取り方は、CKAN API でデータセットを選び、`package_show` で資源の URL を得て、必要なメッシュの zip だけを S3 から取る、という流れになる。メッシュ 1 枚で 66,238,706 バイト、約 63MB。区分としては catalog の下に split (メッシュ単位) が入り、その中の zip は whole という三重になる。

Range は 206 を返すが、これを range に分類する理由にはならない。中身は zip に入った CityGML で、先頭に索引は無いし、末尾の中央ディレクトリを読んだところで取り出せるのはファイル名の一覧までである。地物を選んで引くことはできない。

ライセンスは `license_id` が `plateau`、`license_title` が「PLATEAU Site Policy 「３．著作権について」に拠る」で、CKAN の標準の値ではない。以前の整理 (CC BY 4.0 と互換の枠だが独自の値で測量法の注記が付く) と矛盾はしないが、本文まではたどっていない。使うことになったら、そのときに確かめる。
