# USGS の地震フィードと ComCat

2026-10-02 に読んで確かめた内容。中身の数は z.yuiseki.net に置いた `usgs_m45_month.geojson` を Python の json で読んで数えた値 ([geojson](../z-yuiseki-static/geojson.md) の記録と同じ)。フィードと API の応答は 2026-10-02 に curl で取った。ComCat API で同じ期間を取り直した照合は、同じ日の来歴調査で行った。

- 米国地質調査所 (USGS) の Earthquake Hazards Program が配る地震の震源一覧。
- リアルタイムのフィードは `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/` の下に、規模 (significant、4.5、2.5、1.0、all) と期間 (hour、day、week、month) の組で 20 本ある。説明ページ `https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php` に、month の組は「Past 30 Days Updated every minute.」とある。
- もとになっているのは ANSS Comprehensive Earthquake Catalog (ComCat)。期間、範囲、規模で絞って引ける FDSN イベント API が `https://earthquake.usgs.gov/fdsnws/event/1/` にある。
- ここで扱うのは、フィード `4.5_month.geojson` (タイトル「USGS Magnitude 4.5+ Earthquakes, Past Month」) をある時点で保存したスナップショット `usgs_m45_month.geojson`。生成は 2025-09-22 11:23:41 UTC。
- 震源の値は USGS 自身 (`us`) のほか、各地の観測網が寄与している。このファイルでは Alaska Earthquake Center (`ak`)、National Tsunami Warning Center (`at`)、`pt`、`nn` が出てくる。寄与者の一覧は `https://earthquake.usgs.gov/data/catalog/contributors/`。

## ライセンス

フィード、イベント API、ComCat の各ページにはライセンスや著作権の記述が無い。2026-10-02 に geojson.php、fdsnws/event/1/、data/comcat/、data/catalog/contribute/ と寄与者 ak、at、pt、nn の各ページを licen、copyright、public domain、restrict、terms of use、redistribut で探して、どれも 0 件だった。根拠になるのは USGS 全体の方針ページ。

<https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits> (2026-10-02 閲覧)。

> USGS-authored or produced data and information are considered to be in the U.S. Public Domain. While the content of most USGS websites is in the U.S. Public Domain, not all information, illustrations, or photographs on our site are. Some non-USGS photographs, images, and/or graphics that appear on USGS websites are used by the USGS with permission from the copyright holder (as required by USGS policy on the use of copyrighted material). These materials are generally marked as being copyrighted. To use these copyrighted materials, you must obtain permission from the copyright holder under copyright law.

> When using information from USGS information products, publications, or websites, we ask that proper credit be given. Credit can be provided by including a citation such as the following:
> Credit: U.S. Geological Survey
> Department of the Interior/USGS

<https://www.usgs.gov/information-policies-and-instructions/acknowledging-or-crediting-usgs> (2026-10-02 閲覧)。

> Most U.S. Geological Survey (USGS) information resides in the Public Domain and may be used without restriction. When using information from USGS information products, publications, or websites, we ask that proper credit be given.

同じページの例文は、無償で使うとき「(Product or data name) courtesy of the U.S. Geological Survey」、加工して売るとき「Source of (product or data name): U.S. Geological Survey」(例「Source of Parkfield seismic data: U.S. Geological Survey」)。

読み取れること。

- USGS が作ったデータは米国のパブリックドメイン。再配布、Parquet などへの変換、商用利用を制限する記述は見つからなかった。販売用のクレジット例まで用意されている。
- クレジットは義務ではなく依頼 (「we ask」)。書くなら「Credit: U.S. Geological Survey」か「USGS Magnitude 4.5+ Earthquakes, Past Month courtesy of the U.S. Geological Survey」。
- ComCat そのものの引用は References ページ (<https://earthquake.usgs.gov/data/catalog/references.php>、2026-10-02 閲覧) にある「U.S. Geological Survey, 2017, Advanced National Seismic System (ANSS) Comprehensive Catalog of Earthquake Events and Products.」で、DOI は <https://doi.org/10.5066/F7MS3QZH>。DataCite のメタデータでは `rightsList` が空で、DOI の側にライセンス表記は無い。
- 例外として名指しされているのは USGS 以外の写真、画像、図で、一般に著作権表示が付いている。このファイルに入っているのは数値、地名の文字列、USGS の URL だけ。
- 他の観測網が寄与した震源の値の扱いは 未確認。方針は「USGS-authored or produced」をパブリックドメインとしていて、寄与分を含むとも含まないとも書いていない。制限する記述も見つからなかった。各観測網のサイトの利用条件は読んでいない。このファイルでは、優先解 (`net`) が USGS 以外なのは 4 件 (`ak` 3、`nn` 1)、`sources` に `us` 以外を含むのは 25 件。
- USGS のロゴは別の使用規則がある。データには関係しない。

## 中身

ファイル内の `metadata` (原文のまま)。

| 項目 | 値 |
|---|---|
| `generated` | 1758540221000 (2025-09-22 11:23:41 UTC) |
| `url` | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson` |
| `title` | `USGS Magnitude 4.5+ Earthquakes, Past Month` |
| `api` | `1.14.1` |
| `status` | 200 |
| `count` | 601 |

- FeatureCollection。601 地物、すべて Point で、座標は経度、緯度、深さ (km)。
- 地震の時刻は 2025-08-23 12:24:53 UTC から 2025-09-22 09:02:43 UTC まで。生成時刻から遡る約 30 日。
- 大きさは 425,000 バイト。sha256 は `188802c7f79228010bd6237d5a44268e35410399132ee9c764fd9ae0a990adff`。
- 属性は 26 個: `mag`, `place`, `time`, `updated` (ミリ秒のエポック), `tz`, `url`, `detail`, `felt`, `cdi`, `mmi`, `alert`, `status`, `tsunami`, `sig`, `net`, `code`, `ids`, `sources`, `types`, `nst`, `dmin`, `rms`, `gap`, `magType`, `type`, `title`。
- マグニチュードは 4.5 から 7.8。整数部の分布は 4 が 429、5 が 162、6 が 8、7 が 2。
- `magType` は `mb` 515、`mww` 81、`ml` 3、`mw` と `mwr` が各 1。種類の違うマグニチュードが 1 列に混ざっている。
- 深さは 7.466 から 639.511 km。
- `status` は全件 `reviewed`、`type` は全件 `earthquake`。`tsunami` が 1 のものは 13。
- `alert` は空が 547、green 49、orange 3、yellow 1、red 1。
- `net` は `us` 597、`ak` 3、`nn` 1。
- `bbox` は経度 -179.369 から 179.8605、緯度 -61.8842 から 83.8394。
- `place` は「3 km WSW of Sındırgı, Turkey」のような文字列。USGS が地名辞書から作ったものと思われるが、その地名データの出どころは 未確認。

## 気をつけること

同じファイルはもう取れない。 フィードは同じ URL の中身を差し替え続ける。2026-10-02 に取ると `Last-Modified` は `Fri, 02 Oct 2026 04:49:06 GMT`、`Cache-Control` は `public, max-age=60` で、中身は 528 地物、`metadata.generated` は 2026-10-02 04:49:06 UTC、`metadata.api` は `2.7.0` だった。2025-09-22 の版は USGS からは手に入らない。geojson.php は「USGS Earthquakes Feed Life Cycle Policy」へリンクしているが、リンク先 `https://earthquake.usgs.gov/earthquakes/feed/policy.php` は 2026-10-02 に 404 で、フィードの保存や廃止の方針は 未確認。

API で同じ期間を取り直しても同じ集合にならない。 イベント API に `starttime=2025-08-22T11:23:41&endtime=2025-09-22T11:23:41&minmagnitude=4.5` を投げると、2026-10-02 には 774 件が返った。スナップショットは 601 件。

| 照合 (2026-10-02) | 件数 |
|---|---:|
| スナップショットの地物 | 601 |
| うち、今の照会でも ID (`ids` の別名を含む) で見つかる | 579 |
| うち、マグニチュードの値が変わった | 119 |
| 今の照会に無い | 22 |
| 今の照会にだけあって、スナップショットに無い | 195 |
| 今の照会の合計 | 774 |

今の照会に無い 22 件は、イベント ID を指定するとどれも今も存在した。マグニチュードが 4.2 から 4.4 に下げられて 4.5 未満になったもので、削除ではない。

マグニチュードは後から直る。 スナップショットの `status` は全件 `reviewed` だが、それでも 1 年後に 119 件の値が変わり、22 件が閾値を割った。このファイルは 2025-09-22 11:23:41 UTC 時点の速報値の記録で、今の ComCat とは一致しない。確定したカタログとして使うなら API で取り直す。

`url` と `detail` は USGS の今のページを指している。 イベントの詳細はそこから引けるが、リンク先の中身は保存時点のものではない。

## 取り出し方

フィードは whole、ComCat のイベント API は catalog に近い。2026-10-02 に実測した。

フィードは全部落とすしかない。

| 要求 | 応答 |
|---|---|
| `4.5_month.geojson` への HEAD | 200。`Content-Length` も `Accept-Ranges` も無い |
| 同じ URL に `Accept-Encoding: gzip` | 200、gzip で 45,400 バイト |
| 同じ URL に `-r 0-1023` | 200 で 369,360 バイト全体が返った (206 にならない) |
| `all_month.geojson` | 200、7,637,938 バイト |

選べるのは規模と期間の組 (20 本) だけで、範囲や時刻では絞れない。いちばん大きい `all_month` でも 7.6MB なので、丸ごと取って困る大きさではない。

ComCat のイベント API は、期間 (`starttime`、`endtime`)、矩形の範囲 (`minlatitude`、`maxlatitude`、`minlongitude`、`maxlongitude`)、規模 (`minmagnitude`) で絞って、必要な分だけ引ける。`count` で件数だけを先に聞ける。

| 照会 (`https://earthquake.usgs.gov/fdsnws/event/1/count?format=geojson&...`) | 応答 |
|---|---|
| 2025-08-22T11:23:41 から 2025-09-22T11:23:41、M4.5 以上 | `{"count":774,"maxAllowed":20000}` |
| 同じ条件に緯度 20 から 50、経度 120 から 155 を足す | `{"count":43,"maxAllowed":20000}` |

- `maxAllowed` が 20000 なので、1 回の照会で返るのは 20,000 件まで。それを超える期間は分けて引く。
- `application.json` で、絞り込みに使える `catalogs` と `contributors` の一覧が取れる。
- 認証は要らなかった。
- 目録は API そのもので、STAC ではない。返るのはその時点の値なので、版を固定して引く手段は無い。引いた日時を控える。

## 学習ステップとの対応 (案)

- 5 DBSCAN: 震央を密度でまとめ、同じディレクトリのプレート境界 (PB2002) に沿って並ぶかを見る。
- 1, 2 回帰 / 決定木: 深さやプレート境界までの距離を特徴量にする。601 件と少ないので練習向け。
- 4 Cross Validation: 時刻で分けるか、地域でまとめて分けるか。件数が足りなければ API で期間を延ばして取る。
- 版の違い: スナップショットと今の API の結果を ID で突き合わせると、速報値と改訂後の値の差を題材にできる。

## z.yuiseki.net

置いてあるのは 2025-09-22 の版の 1 本だけ。詳しくは [geojson](../z-yuiseki-static/geojson.md)。

- `https://z.yuiseki.net/static/geojson/usgs_m45_month.geojson`。実体は yuisekin-z の `/www/html/static/geojson/usgs_m45_month.geojson`。
- 2026-10-02 の HEAD は 200、`Content-Length` 425,000、`Last-Modified` は `Sat, 04 Oct 2025 01:46:47 GMT`。これはサーバに置いた日で、生成日 (2025-09-22) とは別。
- ローカルの sha256 は上の値と同じで、公開 URL から取ったものも同じハッシュだった (来歴調査で確認)。
- フィードを定期的に取って溜める仕組みは無い。置かれているのはこの 1 時点だけ。
