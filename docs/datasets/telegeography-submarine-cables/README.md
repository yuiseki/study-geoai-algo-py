# TeleGeography Submarine Cable Map (cable-geo.json)

2026-10-02 に読んで確かめた内容。ローカルの写し (`/sata_hdd_24tb/www/html/static/geojson/cable-geo.json`) は丸ごと Python の json で読んで数えた。現在の配布元の大きさと Last-Modified は HEAD と `curl -r 0-1023` の応答、現行版の地物数は 2026-10-02 04:40 UTC に配布元から取った本文をメモリ上で数えた値。ライセンスの文言は TeleGeography の各ページ、submarinecablemap.com の JS バンドル、Wayback Machine の取得分から。

- 海底通信ケーブルの経路線の GeoJSON。TeleGeography (法人名 PriMetrica, Inc. dba TeleGeography、米国の通信調査会社) が無料で公開している地図 Submarine Cable Map (<https://www.submarinecablemap.com>) の表示用データ。
- 経路は測量した実経路ではなく、TeleGeography が手で描いたもの。FAQ (<https://www2.telegeography.com/submarine-cable-faqs-frequently-asked-questions>) に「TeleGeography draws the cable routes and plots the landing points with Adobe Illustrator . Using Avenza's MAPublisher plug-in, which works with Illustrator, two sets of data are exported as GeoJSON files: the cable routes and landing points.」とある。
- 現在の配布元は <https://www.submarinecablemap.com/api/v3/cable/cable-geo.json>。地図の Web アプリが読み込む API で、ダウンロード用として案内された URL ではない。
- 以前は GitHub リポジトリ `telegeography/www.submarinecablemap.com` の `web/public/api/v3/cable/cable-geo.json` に置かれ、README (Wayback 2022-08-16 取得分) が raw の URL を「Submarine Cables GeoJSON」としてリンクしていた。このリポジトリは 2026-10-02 に 404。Wayback では 2022-11-10 まで 200、2024-06-21 以降は 404 で、消えた正確な時期は未確認。
- サイトの About 画面 (JS バンドル `/assets/index-DQqjuvIf.js` 内の文言) は「We no longer maintain and update a repository on GitHub for our data or our source code.」と書いている。
- ファイルの中に版番号、日付、出典、ライセンスの記載は無い。

## ライセンス

結論: この版のデータを再配布してよいとするライセンスは見つからなかった。関係する記述は次の 3 つで、互いに食い違う。

### 旧 GitHub リポジトリの CC BY-NC-SA 3.0

README の License 節 (Wayback 2022-11-10 と 2022-03-07 の取得分、<https://github.com/telegeography/www.submarinecablemap.com>)。リンク先は <https://creativecommons.org/licenses/by-nc-sa/3.0/>。

> License Our map is made available under the following Creative Commons License: Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0) .

リポジトリ直下の LICENSE (Wayback 2022-08-16 取得分、`/blob/master/LICENSE`) の冒頭。

> Creative Commons Legal Code
> Attribution-NonCommercial-ShareAlike 3.0 Unported

- 当時はリポジトリに GeoJSON 自体が置かれ、README が同じ節でそのダウンロードを案内していた。当時の版のデータにはこのライセンスが及んでいたと読める。
- ただしリポジトリは 2024-06 までに消えている。ローカルの写しは 2025 年 7 月から 8 月の版 (下の「z.yuiseki.net」を参照) で、リポジトリに載ったことが無い。旧リポジトリのライセンスはこの版には及ばない。
- 旧版に付いた CC BY-NC-SA 3.0 の許諾は取り消せないが、ローカルの写しは旧版そのものではなく、その後に更新された版。

### 現在のサイトの CC BY-SA 4.0 (地図への言及、URL、スクリーンショットだけ)

submarinecablemap.com の About 画面の License 節 (JS バンドル内の文言、2026-10-02 取得)。

> Any reference to TeleGeography's Submarine Cable Map, URL, or any screencapture of the map is made available under the Creative Commons License: Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). Head here for more information about using a TeleGeography map in your work.

> If you wish to license our data for commercial purposes, fill out of the form on this page.

後者のリンク先は <https://www2.telegeography.com/license-geocoded-map-data>。

<https://www2.telegeography.com/license-telegeography-map> (2026-10-02 取得。Wayback の 2023-06-04 と 2025-07-19 の取得分も同じ文言)。

> Any reference to a TeleGeography map, URL, or any related screen capture is made available under the Creative Commons License: Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). This means that you may use our maps in your work, but TeleGeography must be properly credited.

> Does this Creative Commons license apply to all maps? This applies to all publicly available TeleGeography maps.

- 名指しされているのは「地図への言及、URL、スクリーンショット」で、GeoJSON のデータは挙がっていない。CC BY-SA 4.0 がデータに及ぶかは未確認で、文面からはむしろ及ばないと読める。

### 元データは有料購読者に限る

同じ license-telegeography-map ページの FAQ。

> I'm a student looking for the underlying data. Is the data available? ... Access to the underlying databases remains restricted to paying subscribers.

> Can I embed your map on my site? TeleGeography's interactive cable map is not an embeddable resource. If you'd like to access the underlying data for a project, you may license our map data.

Submarine Cable FAQ (<https://www2.telegeography.com/submarine-cable-faqs-frequently-asked-questions>、2026-10-02 取得)。

> We no longer maintain or update a GitHub repository for our data or source code. The raw, geocoded data underlying TeleGeography's interactive maps is available via an annual license. Map data is delivered as a JSON API, which includes GeoJSON and JSON files.

- <https://www2.telegeography.com/license-geocoded-map-data> は「Get the raw geocoded data behind TeleGeography's signature maps」として、年間ライセンスで GeoJSON と JSON の API を S3 経由で納品すると説明している。
- 有料製品の Terms and Conditions (<https://www2.telegeography.com/terms> から辿る PDF、revised 04-27-2025) は注文を交わした顧客向けの契約条件で、無料の地図の閲覧者には直接当てはまらない書き方。公開地図の利用規約にあたる独立したページは見つからなかった (`/terms-of-use` は 404)。
- robots.txt は `User-agent: *` に `Disallow:` が空 (全許可)。取得してよいかを示すだけで、再配布の許諾ではない。

読み取れること。

| 項目 | 確かめたこと |
|---|---|
| この版のデータのライセンス | 明示されたものは見つからない |
| 無改変の再配布、変換形 (Parquet など) の再配布 | 許す記述は見つからない。サイトは元データを有料ライセンスとしている |
| 商用利用 | 旧 GitHub の条件では不可 (NC)。現行サイトは商用のデータ利用を有料ライセンスへ誘導している |
| 継承 (SA) | 旧 GitHub の条件でも現行の地図の条件でも付く |
| 表示 | 定型文は見つからない。地図については「TeleGeography must be properly credited」とだけある |

旧条件 (NC あり、データを含めて配布) と現行の条件 (地図は NC なしの CC BY-SA 4.0、ただしデータは有料) は向きが逆。問い合わせ先として公開されているのは sales@telegeography.com (データのライセンス)、press@telegeography.com (報道・研究者)、cablemap@telegeography.com (地図の訂正)。どの法域で著作物やデータベース権の対象になるかは未確認。

## 中身

トップレベルはローカルの写しも現行版も同じ形で、`{"type": "FeatureCollection", "name": "submarine_cables", "crs": CRS84, "features": [...]}`。

| 項目 | ローカルの写し | 現在の配布元 (2026-10-02 04:40 UTC 取得) |
|---|---:|---:|
| 大きさ (バイト) | 708,963 | 754,154 |
| Last-Modified | 2025-09-20 05:08:25 GMT (z.yuiseki.net の応答) | 2026-09-30 19:51:36 GMT |
| 地物数 | 681 | 733 |
| ケーブルの `id` の種類 | 666 | 712 |
| SHA-256 | `852bc76c5c70d7e556092ba9fd1caa5fc8fe7c11a82b6e1b136dde0e0fcadea6` | `a16447c7c766358a43d12091059f67efe807e91c82acc609d15356db42b5ab3d` |

属性は 5 つ。

| 属性 | 中身 (ローカルの写しの例) |
|---|---|
| `id` | ケーブルの識別子。`manx-northern-ireland` |
| `name` | ケーブルの名前。`Manx-Northern Ireland` |
| `color` | 地図で塗る色。`#b99633`。ローカルの写しで 534 通り |
| `feature_id` | 地物の識別子。`manx-northern-ireland-0` のように `id` に番号を付けたもの。681 地物ですべて一意 |
| `coordinates` | 属性の中の 1 点 `[経度, 緯度]`。ラベル位置と思われるが未確認 |

ローカルの写しで数えたこと。

- 幾何は 681 地物すべて MultiLineString。1 地物の線の本数は 1 から 35、合計 1,872 本。頂点は合計 13,609。
- 666 の `id` のうち 651 は 1 地物、15 は 2 地物に分かれている (`tanjung-pandan-sungai-kakap`、`connected-coast`、`medloop` など)。
- 範囲は経度 -180.00 から 180.00、緯度 -55.01 から 78.22 (`z-yuiseki-static/geojson.md` の値)。
- `feature_id` で現行版と比べると、現行版にしか無いものが 79、ローカルにしか無いものが 27。

経路の幾何しか入っていない。長さ、陸揚げ地点、所有者、供用開始年は、同じ API のケーブルごとの JSON (`/api/v3/cable/<id>.json`) にある。`manx-northern-ireland.json` は 406 バイトで、`length` (`"59 km"`)、`landing_points` (id、名前、国)、`owners`、`suppliers`、`rfs`、`rfs_year`、`is_planned`、`url`、`notes` を持っていた。ケーブルの一覧 `/api/v3/cable/all.json` (41,148 バイト) は `id` と `name` の組が 712 個。陸揚げ地点の GeoJSON `/api/v3/landing-point/landing-point-geo.json` は 361,179 バイト (HEAD)。この 3 つは 2026-10-02 に応答を見ただけで、ライセンスの事情は cable-geo.json と同じ。

## 気をつけること

- 測量した経路ではない。Illustrator で描いた線なので、海底の実際の位置や距離の計算には使えない。長さが要るなら、線から測るのではなく、ケーブルごとの JSON の `length` を見る。
- 1 本のケーブルが複数の地物に分かれることがある。ケーブル単位で数えるなら `feature_id` ではなく `id` でまとめる。
- 線どうしはつながっていない。陸揚げ地点はこのファイルに無く、グラフにするには端点を陸揚げ地点の GeoJSON と自分で突き合わせる必要がある。
- 日付変更線で線が切られている。ローカルの写しで、経度の絶対値が 179.999 以上の頂点を持つケーブルが 32 (`asia-america-gateway-aag-cable-system`、`bifrost`、`e2a` など)。1 本の線の中で隣り合う頂点の経度差が 180 を超える所は 0 で、またぐ所は MultiLineString の別の線に分かれている。距離や長さを計算するときは、切れ目をつなぎ直す必要がある。
- URL は固定で中身が差し替わる。版番号もチェックサムも無い。ローカルの写しと現行版は地物数が 681 と 733 で違う。
- データとして配っているものではない。ライセンスの節のとおり、再配布してよいとする記述は見つかっていない。

## 取り出し方

区分は whole。2026-10-02 に実測した。

- 経路の幾何はこの 1 ファイルにしか無い。現行版で 754,154 バイト。
- `curl -r 0-1023` は 206 を返した (`Content-Range: bytes 0-1023/754154`、`Accept-Ranges: bytes`)。ただし中身は索引の無い 1 つの JSON で、地物や範囲を選んで引くことはできない。
- ケーブルごとの JSON (`/api/v3/cable/<id>.json`) は id で 1 本ずつ引けるが、幾何は入っていない。
- 目録として使えるのは `all.json` (id と名前の一覧) だけで、bbox や日時では絞れない。

## z.yuiseki.net

- `https://z.yuiseki.net/static/geojson/cable-geo.json` に 1 本だけある。実体は yuisekin-z の `/sata_hdd_24tb/www/html/static/geojson/cable-geo.json` で、708,963 バイト、mtime は 2025-09-20 14:08 (JST)。`curl -r 0-1023` は 206 を返した。
- 中身は TeleGeography の API が 2025 年 7 月中旬から 8 月末まで配っていた版と同じ。根拠は、ローカルの SHA-1 (base32 で `EBR3JJE6PWU6HXUSIBHYVRGHWHYLEFMX`) が、Wayback Machine の CDX で `www.submarinecablemap.com/api/v3/cable/cable-geo.json` の digest と一致するのが 2025-07-17 から 2025-08-28 の取得分だけで、直前 (2025-07-10) と直後 (2025-08-31) は別の digest だったこと。
- mtime の 2025-09-20 は写した日と考えられるが、取得した日そのものは未確認。取得したときに利用条件へ同意した記録は無い。
- 同じディレクトリの他のファイルは [z-yuiseki-static/geojson.md](../z-yuiseki-static/geojson.md)。

## 学習ステップとの対応 (案)

- 7 Dijkstra / A*: ケーブルの線と陸揚げ地点をつないだグラフで、2 地点間の経路や、1 本が切れたときの迂回を調べる。端点の同定は自分でする。
- 12 多目的最適化: 経路の長さと、プレート境界や地震の多い場所からの距離の両立を考える題材 (`z-yuiseki-static/geojson.md` のプレート境界と地震のファイルと組み合わせる)。
- どちらも手元で使うまでにとどまる。再配布できるライセンスが見つかっていないので、派生物を公開する用途には向かない。
