# PB2002 プレート境界 (fraxen/tectonicplates の GeoJSON)

2026-10-02 に読んで確かめた内容。中身の数字は yuisekin-z の `/sata_hdd_24tb/www/html/static/geojson/tectonicplates_GeoJSON_PB2002_boundaries.json` を Python の json で読んで数えた値。配布元との一致は sha256sum と git blob SHA-1 (GitHub の contents API)、取り出し方は `curl -r 0-1023` の応答から。ライセンスの原文は各 URL を同じ日に読んだもの。

- Peter Bird (UCLA) の全球のプレート境界モデル PB2002 (52 プレート) のうち、境界線 (boundaries) を GeoJSON にしたもの。1 地物が境界の 1 区間で、両側のプレートの略号と、沈み込み帯かどうかが付く。
- 系譜は 3 段。

| 段 | 作成者 | 時期 | 形式 | 所在 |
|---|---|---|---|---|
| 原典モデル PB2002 | Peter Bird (UCLA) | 論文 2003-03 (Crossref の published は 2003-03) | ASCII (`PB2002_boundaries.dig.txt` ほか) | <http://peterbird.name/oldFTP/PB2002/>、<http://peterbird.name/publications/2003_PB2002/2003_PB2002.htm> |
| シェープファイル版 | Hugo Ahlenius, Nordpil | 2014-06 に原典を取得、2014-06〜08 に作業 | Shapefile | <https://github.com/fraxen/tectonicplates> (ルート) |
| GeoJSON 版 | csterling (コミット b53c3b7d) | 2014-10-02 | GeoJSON | <https://github.com/fraxen/tectonicplates/tree/master/GeoJSON> |

- リポジトリの README の原文: 「This is a conversion of the dataset originally published in the paper _An updated digital model of plate boundaries_ by Peter Bird (Geochemistry Geophysics Geosystems, 4(3), 1027, doi:10.1029/2001GC000252, 2003).」「The data was downloaded from http://peterbird.name/oldFTP/PB2002/ in June 2014.」「Now with GeoJSON data, courtesy of csterling」
- リポジトリの最終 push は 2014-10-06、master の最新コミットは 339b0c56。タグは無く、版番号はモデル名の PB2002 だけ。archived ではない。stars 180、forks 147 (2026-10-02 の GitHub API)。
- 引用: Bird, P. (2003), An updated digital model of plate boundaries, Geochemistry Geophysics Geosystems, 4(3), 1027, doi:10.1029/2001GC000252.

## ライセンス

### 変換物 (シェープファイル版と GeoJSON 版): ODC-By 1.0

リポジトリの `LICENSE.md` (<https://raw.githubusercontent.com/fraxen/tectonicplates/master/LICENSE.md>)。元は Markdown の太字。

> This collection of data is made available under the Open Data Commons Attribution License: [http://opendatacommons.org/licenses/by/1.0/](http://opendatacommons.org/licenses/by/1.0/)

README.md の License 節。

> This collection is made available under the Open Data Commons Attribution License: http://opendatacommons.org/licenses/by/1.0/, please refer to LICENSE.md for more information.
> Please consider giving Hugo Ahlenius, Nordpil and Peter Bird credit and recognition as a data source.

シェープファイルのメタデータ `PB2002_boundaries.shp.xml` の useLimit。

> This dataset is made available under the Open Data Commons Attribution License: http://opendatacommons.org/licenses/by/1.0/

ODC-By 1.0 の本文 (<https://opendatacommons.org/licenses/by/1-0/>) から、条件に関わるところ。

> 3.1: These rights explicitly include commercial use, and do not exclude any field of endeavour.

> 4.2: If You Publicly Convey this Database, any Derivative Database, or the Database as part of a Collective Database, then You must:
> a. Do so only under the terms of this License;
> b. Include a copy of this License or its Uniform Resource Identifier (URI) with the Database or Derivative Database, including both in the Database or Derivative Database and in any relevant documentation;
> c. Keep intact any copyright or Database Right notices and notices that refer to this License; and
> d. If it is not possible to put the required notices in a particular file due to its structure, then You must include the notices in a location (such as a relevant directory) where users would be likely to look for it.

> 4.4: You may not sublicense the Database. You may not impose any further restrictions on the exercise of the rights granted or affirmed under this License.

読み取れること。

- 商用利用は可 (3.1)。無改変の再配布も、Parquet などに変換した Derivative Database の配布も許されている (3.1 b と e)。
- 公衆に配るときは、ライセンス本文か URI を同梱し、ドキュメントにも書き、既存の権利表記とライセンス表記を残す (4.2 b, c)。データベースそのものや Derivative Database は ODC-By 1.0 の条件で出す (4.2 a)。ODbL のような share-alike の条項は無く、地図画像のような Produced Work にはこの縛りは掛からない (4.3 は「Contains information from DATABASE NAME which is made available under the ODC Attribution License.」という表記例を示す)。
- Hugo Ahlenius, Nordpil と Peter Bird のクレジットは README の要望 (「Please consider」) で、ライセンス本文の義務ではない。
- GitHub API のライセンス判定は `other` / SPDX `NOASSERTION`。自動判定できていないだけで、文面は上のとおり。
- `LICENSE.md` が入ったのは 2014-08-11 (コミット 039e4e03、Hugo Ahlenius)、GeoJSON はその後の 2014-10-02 に csterling が入れた。リポジトリの ODC-By が GeoJSON にも及ぶと読むのが自然だが、csterling 本人の宣言は無い。未確認。
- GeoJSON ファイルの中にはライセンスも出典も書かれていない。配るときは 4.2 b, c の表記を別に付ける必要がある。

### 原典モデル (Peter Bird, PB2002): 明示ライセンス無し

- 次の 3 つを読んだが、ライセンス、利用条件、copyright の表記はどれにも無かった。<http://peterbird.name/oldFTP/PB2002/> (ファイル一覧と「Relevant Publication」の表記だけ)、<http://peterbird.name/oldFTP/PB2002/2001GC000252_readme.txt> と <http://peterbird.name/publications/2003_PB2002/2003_PB2002.htm> (licen、copyright、permission、terms、redistrib で検索して該当なし)。
- トップページ <http://peterbird.name/> には「You are welcome to download many of my finite-element and graphical programs, and to use any figures, maps, or images that you might find useful in teaching or research presentations.」とある。図版とプログラムの話で、データセットのライセンスではない。
- 論文 (doi:10.1029/2001GC000252、出版社は AGU) の Crossref の license は `http://onlinelibrary.wiley.com/termsAndConditions#vor`。論文本体の出版社の規約で、CC ライセンスではない。データは論文の補足資料として出た経緯があり、その権利が AGU/Wiley 側にあるかは未確認 (Wiley の論文ページは HTTP 403 で読めなかった)。
- ODC-By を付けたのは変換者の Ahlenius で、原典の権利者の Bird ではない。ODC-By 1.0 の 2.4 は、個々の Contents の権利を対象にしないとしている。原典の座標に権利がどこまで及ぶかは法域による。再配布、改変、商用利用について、Bird 側の許諾の文面も禁止の文面も見つかっていない。
- 学術データとして 20 年以上広く再配布されている (fork 147) が、それ自体は許諾の証拠にならない。

### Dryad の CC0 アーカイブ (中身は未確認)

- Bird は 2025-11-04 に Dryad で「Kinematic and dynamic modeling of lithosphere deformation: Tools and results」(doi:10.5061/dryad.cnp5hqcjb) を公開している。API はライセンスを CC0-1.0 と返す。
- zip は 415MB で 20MB の上限を超えるため落としていない。README は API が 401、Web が 403 で読めなかった。PB2002 のファイルが含まれるかは未確認。含まれていれば、原典側に CC0 の経路ができる。

## 中身

| 項目 | 値 |
|---|---|
| 大きさ | 226,378 バイト |
| SHA-256 | 42b3e0876a7e40f133e958ba7ab85f8851b5c693a046fbc3b138e7751863d92a |
| 形 | FeatureCollection。トップレベルのキーは `type` と `features` だけで、`crs` は無い |
| 地物 | 241、すべて LineString |
| 頂点 | 6,292 (1 地物あたり 2〜272)。すべて 2 次元 (経度, 緯度) |
| 範囲 | 経度 -180 から 180、緯度 -66.1632 から 86.8049 |

属性は 6 つで、全地物が同じ並び。

| 属性 | 中身 |
|---|---|
| `LAYER` | 全件 `plate boundary` |
| `Name` | 両側のプレートの略号の組。`AF-AN` のような `-` が 176、`EU/AF` のような `/` が 44、`EU\AF` のような `\` が 21。異なり数は 182 |
| `Source` | 区間ごとの出典。異なり数 63。上位は `Mueller et al. [1987]` 31、`by Peter Bird, September 2001` 24、`by Peter Bird, 1999` 21、`by Peter Bird, October 2001` 16、`Peter Bird, June 2002` 15 |
| `PlateA`, `PlateB` | プレートの略号。2 列に出てくるのは 52 通りで、PB2002 の 52 プレートと数が合う |
| `Type` | 空文字が 176、`subduction` が 65 |

- `Name` はどの地物でも `PlateA` と `PlateB` を区切り文字でつないだものと一致した。区切りが `/` か `\` の 65 件はちょうど `Type` が `subduction` の 65 件で、`-` の 176 件はすべて空文字。`/` と `\` がどちらのプレートが沈み込む側かを表すと思われるが、原典の説明は読んでいない。未確認。
- `Source` の値は原典の各区間の見出し行にある出典の表記から来ている (調査報告による)。
- 原典の `PB2002_boundaries.dig.txt` は 229 区間。241 との差は、README の「The main edits regarded segments spanning the -180/180 boundary, which had to be manually split and moved.」で説明できる。経度がちょうど ±180 の点を持つ地物は 18 あった。件ごとの照合はしていない。
- 地物数 241 は、シェープファイルの `.shx` (2,028 バイト) から計算される件数とも一致する。
- 同じ `GeoJSON/` ディレクトリには `PB2002_plates.json` (327,718 バイト)、`PB2002_orogens.json` (33,209 バイト)、`PB2002_steps.json` (10,371,475 バイト) もある (GitHub の contents API が返した大きさ)。z.yuiseki.net にあるのは boundaries だけ。

## 気をつけること

境界の線はあるが、プレートの面は無い。 このファイルは境界線だけ。点がどのプレートに入るかを判定したいなら、同じリポジトリの `PB2002_plates.json` を別に取る必要がある。

orogen の注意書きが落ちる。 Bird のページは、Persia-Tibet-Burma などの「orogen」(造山帯) の領域では境界が単純化されていて「not to be taken literally」と警告している。その範囲は `PB2002_orogens.json` 側にあり、boundaries 単体には含まれない。大陸内部の境界を距離計算に使うときは、この領域の線を真に受けない。

日付変更線で切ってある。 原典の区間を ±180 で手作業で分割してあるので、1 本の境界が複数の地物に分かれている。経度 ±180 の点を持つ 18 地物は、`PA-BR`、`BR-AU`、`KE-AU`、`KE/PA`、`NA/PA`、`PA-AN` の 6 つの `Name` に 3 地物ずつだった。`Name` は 182 通りで地物は 241 なので、日付変更線と関係なく同じ組が複数の地物になっているものもある。長さを境界ごとに合計するなら `Name` でまとめる。

座標は経度緯度の度。 `crs` は書かれていないが、値の範囲は経度 -180 から 180、緯度 -66 から 87 で、WGS84 の経度緯度として読める。距離を出すなら測地線か投影を使う。

沈み込みの向きは名前の区切りにしか無い。 `Type` は `subduction` か空文字の 2 値で、海嶺やトランスフォーム断層の区別は無い。PB2002 の境界の分類 (拡大、収束、トランスフォームなど) は `PB2002_steps.json` 側にあると思われるが、中身は読んでいない。未確認。

モデルは 2002 年で止まっている。 版は PB2002 の 1 つだけで、GitHub 側も 2014-10-06 から更新が無い。

## 取り出し方

区分は whole。1 ファイル 226,378 バイトで、全部落とすのが最も簡単。2026-10-02 に実測した。

| 要求した URL | 応答 | Content-Range |
|---|---|---|
| `https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json` に `-r 0-1023` | 206、`Accept-Ranges: bytes` | `bytes 0-1023/226378` |
| `https://z.yuiseki.net/static/geojson/tectonicplates_GeoJSON_PB2002_boundaries.json` に `-r 0-1023` | 206 (`cf-cache-status: HIT`) | `bytes 0-1023/226378` |

どちらも Range は通るが、GeoJSON には索引が無いので、地物の部分集合をバイト範囲で選ぶことはできない。部分読みでできるのは先頭の形の確認まで。最小単位が 226KB なので、range にする意味も無い。

リポジトリには Shapefile 版と GeoJSON 版が boundaries、plates、orogens、steps に分かれて置かれていて、要るものだけを選べるという意味では split に近い。ただし分割はデータの種類で、地域や範囲では選べない。

## z.yuiseki.net のコピー

- yuisekin-z の `/sata_hdd_24tb/www/html/static/geojson/tectonicplates_GeoJSON_PB2002_boundaries.json` を、nginx が <https://z.yuiseki.net/static/geojson/tectonicplates_GeoJSON_PB2002_boundaries.json> として配っている。置いてあるのは boundaries の 1 ファイルだけ。ディレクトリ全体のことは [z-yuiseki-static/geojson.md](../z-yuiseki-static/geojson.md) にある。
- 大きさは 226,378 バイト、Last-Modified は `Sat, 04 Oct 2025 01:51:49 GMT` (ファイルの mtime は 2025-10-04 10:51:49 +0900)。
- 中身は fraxen/tectonicplates の `GeoJSON/PB2002_boundaries.json` をそのまま名前だけ変えたもの。根拠は次の 3 つ (調査報告による。手元の SHA-256 はこの文書のために計算し直して同じ値だった)。
  - git blob SHA-1 が両方 43acb5894299e203ae3a4a57ef5afc2b5c329221 (手元は `git hash-object`、配布元は GitHub の contents API)。
  - SHA-256 が手元、raw.githubusercontent.com から取ったもの、公開 URL から取ったもので、どれも 42b3e0876a7e40f133e958ba7ab85f8851b5c693a046fbc3b138e7751863d92a。
  - 大きさがどれも 226,378 バイト。
- ファイル名はリポジトリの zip 内のパス `tectonicplates-master/GeoJSON/...` をつないだ形と読めるが、取得経路そのものは未確認。
- [z-yuiseki-static/geojson.md](../z-yuiseki-static/geojson.md) (2026-09-28) ではライセンスを未確認としていた。上の ODC-By 1.0 が変換物のライセンスにあたる。

## 学習ステップとの対応 (案)

- 5 DBSCAN: 同じディレクトリの `usgs_m45_month.geojson` の震央をクラスタにまとめ、境界線に沿って並ぶかを見る。
- 1, 2 回帰 / 決定木: 地震から最寄りの境界までの距離と、その境界が沈み込み帯かどうかを特徴量にして、震源の深さを当てる。距離は自分で計算する。
- 8 空間統計: 境界からの距離の帯ごとに地震の密度を数える。日付変更線での分割と orogen の単純化が、距離の誤差の出どころになる。
