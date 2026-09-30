# KartaView と GrabMaps 360 Imagery

2026-09-28 に読んで確かめた内容。数字はこの日に API とサイトから読んだ値で、推定は「推定」と書く。

## 何か

- KartaView (<https://kartaview.org/>) は道路沿いの画像を投稿・公開するプラットフォーム。運営は Grab。
  - OSM Wiki と Wikipedia によると、元は OpenStreetView (2009 年)。2016 年に Telenav が引き取り OpenStreetCam に、2019-12-12 に Grab へ売却、2020 年 11 月に KartaView へ改名。
- GrabMaps 360 Imagery は、GrabMaps が KartaCam2 (Grab 製の 360 度カメラ) で撮った画像。別サービスではなく、KartaView の中にユーザー `OpenStreetView` (userId 44) の投稿として入っている。
  - サイトの紹介ページ `https://kartaview.org/landing/open-imagery` は「Open dataset collected by GrabMaps with KartaCam2 in Yogyakarta, Langkawi and Krabi」と書く (ページは JavaScript 描画なので、配信中の `main.*.js` から文言を読んだ)。
  - 引用の仕方として「GrabMaps 360 Imagery Dataset, 2024. Retrieved from https://kartaview.org/landing/open-imagery. Licensed under CC-BY-SA.」が指定されている。

## 規模 (サイトの記載)

公開データセット (open-imagery ページの記載値。自分で数えたものではない):

| 都市 | 画像 | 道路延長 |
|---|---|---|
| Yogyakarta, Indonesia | 1,604,699 | 11,469.78 km |
| Langkawi, Malaysia | 29,719 | 120.77 km |
| Krabi, Thailand | 104,258 | 694.91 km |
| 合計 | 1,738,676 | 12,285.46 km、30.79 TiB |

3 都市の和は合計欄と一致する。同じページに「Over 967,000 km of Roads collected across Singapore, 78 cities in Thailand, 89 in Indonesia, 29 in the Philippines, 30 in Malaysia, 27 in Vietnam, 17 in Cambodia」とあり、こちらは「Ask us」「Contact Us」(grabmaps.contact@grab.com) の案内で、公開データではなく問い合わせ先の商用データとして書かれている。

KartaView 全体の撮影枚数や国別の統計は、公開されている場所を見つけられなかった (未確認)。

## 入手経路

### API (ログイン不要で読めた)

ベースは `https://api.openstreetcam.org`。読み出しに認証は要らなかった。User-Agent を付けて逐次で叩いた。

| 要求 | 結果 |
|---|---|
| `POST /1.0/list/nearby-photos/` (`lat`, `lng`, `radius` をフォームで) | 200。半径内の写真を返す。東京駅 (35.6812, 139.7671) 半径 200m で 115 件、約 6 秒 |
| `GET /2.0/photo/?lat=..&lng=..&radius=200` | 400 (apiCode 408 "Query timeout. Narrow your filter")。25 秒待って失敗 |
| `GET /2.0/photo/{id}` | 200。1 枚の詳細 (位置、撮影日時、向き、画素数、ぼかし状態、画像 URL) |
| `GET /2.0/sequence/{id}` | 200。撮影列の詳細 (機材名、国コード、住所、枚数、bbox) |
| `GET /2.0/detection/?sequenceId=..` | 404 (HTML のエラーページ)。検出結果の取り方は見つけられなかった |

nearby-photos の 1 件目 (東京駅付近、写真 id 1248011617) で取れたメタデータ:

- 位置 35.680189, 139.766645、`heading` 168.72、`shot_date` 2019-12-11 05:28:26、`projection` PLANE、撮影者 `mi-mitz`
- `autoImgProcessingResult` BLURRED、`visibility` public、`width` x `height` 4032 x 3024
- 画像は `https://storage13.openstreetcam.org/files/photo/.../proc/...jpg` からログイン無しで取れた (2,774,809 バイト、4032 x 3024)。`th` (サムネイル) と `lth` (大きめのサムネイル) もある

地域ごとの nearby-photos の中身:

| 地点 | 半径 | 件数 | 360 度 (SPHERE) | 撮影者の上位 | 撮影日の範囲 |
|---|---|---|---|---|---|
| 東京駅 | 200m | 115 | 0 | mi-mitz 112, Matt H@Japan 3 | 2018-05-27 〜 2019-12-11 |
| シンガポール (1.2838, 103.8515) | 200m | 1,000 (total 1,458) | 813 | OpenStreetView 813, grabsg 186 | 2019-03-19 〜 2023-07-25 |
| バンコク (13.7466, 100.5393) | 200m | 212 | 0 | koki2529 108, suwich 37, grabth-napittha 32 | |
| ジョグジャカルタ (-7.7925, 110.3658) | 100m | 589 | 59 | puput-puspananda 301, djalu 86, dwi-heridani 62, OpenStreetView 59 | 2020-04-08 〜 2022-08-10 |

1 回で返るのは最大 1,000 件だった (シンガポールで `totalFilteredItems` 1,458 に対して 1,000 件)。

360 度画像の例:

- シンガポール、写真 id 1881617433、sequence 8343753。機材 `KartaCam360LiteV1`、`shotDate` 2023-07-25 03:03:07。`wrapped_proc` の画像は 11,117,947 バイト、13000 x 6500 (正距円筒)
- ジョグジャカルタ、sequence 11616132。機材 `KartaCam2`、3,242 枚、`dateAdded` 2025-11-19。写真 1 枚 (2627367743) の `wrapped_proc` は HEAD で 36,719,119 バイト (本体は取っていない)

### 一括ダウンロード

- open-imagery ページの手順は、Azure Storage Explorer で SAS URL `https://kartaimagestorage.blob.core.windows.net/grab2cmntmini?...` を開くもの。「sample (mini dataset)」で、3 都市がトップのフォルダーとして見えると書かれている。
- この SAS の有効期限は `se=2026-03-18T17:44:15Z`。一覧の要求は 403 AuthenticationFailed ("Signature not valid in the specified time frame") で、2026-09-28 時点では使えなかった。
- 全量 (30.79 TiB) をオフラインで取る公開の手段は見つけられなかった。OSM Wiki には「As of June 2020, there are no batch downloading possibilities available」とある。
- source.coop や S3 のミラーは見つけられなかった (未確認)。

## ライセンス

KartaView の利用規約 (`/terms`、配信中の JS に入っている本文) の記載:

> Grab would like to open source KartaView's codes, under the terms of the MIT License, and by licensing the street images made available on KartaView and 3D spatial data under Creative Commons Attribution-ShareAlike 4.0 International ("CC-By-SA License")

> The content which you submit, post, display, upload on or via KartaView is therefore subject to the rules of the afore-mentioned MIT License and CC-By-SA License

FAQ も「Images you are uploading are available under the Creative Commons Attributions-ShareAlike 4.0」。

読み取れること:

- 画像は KartaView 全体に一律で CC BY-SA 4.0。撮影者ごとに選ぶ仕組みは見当たらなかった。API の写真・撮影列のメタデータにもライセンスの項目は無い。
- 「CC BY-SA 4.0 の公開画像あり」は GrabMaps 専用の公開ではなく、KartaView に載っている画像全部 (日本の個人投稿も含む) のこと。GrabMaps 360 Imagery の 3 都市もその一部で、引用文も「Licensed under CC-BY-SA」。
- 商用の東南アジア 160 都市超のデータは「問い合わせ」になっていて、ライセンスの記載は無い (未確認)。
- メタデータ (位置・日時・向き) については規約に個別の記載が無い。「street images ... and 3D spatial data」に含まれるかは未確認。
- 検出結果など派生データ: CC BY-SA は翻案物に同じライセンスを求めるので、画像から作った検出結果の点データも CC BY-SA 4.0 で出すのが安全、と読める (法的な判断は未確認)。OSM の編集に使う場合の扱いは未確認。

## プライバシー

- FAQ: 「We use computer vision to blur out any Private Identifiable Information (PII) such as faces and number plates」、公開まで 1〜2 日かかる。
- 見た 3 枚は `autoImgProcessingResult` がいずれも BLURRED だった。実際にぼかされているかは画像で確かめていない。

## 気をつけること

- 東京駅の 1 件目は新幹線ホームから車両を撮った写真で、道路ではなかった。nearby-photos は「近くの写真」を返すだけで、道路上とは限らない。`way_id` や `match_*` は空だった。
- 360 度画像のメタデータの `width` x `height` が 2560 x 1440 なのに、実物は 13000 x 6500 だった。画素数はメタデータを信じずに実物で確かめる。
- ジョグジャカルタの写真で `shotDate` (2025-11-19 11:13:26) が撮影列の `dateAdded` (10:42:29) より後。時刻のタイムゾーンが揃っていないように見える (理由は未確認)。
- `/2.0/photo/` の範囲検索は 200m でもタイムアウトした。範囲で探すなら `/1.0/list/nearby-photos/` を使い、1 回 1,000 件の上限に気をつける。
- 公開サンプルの SAS URL は期限切れ。サイトの記載だけで「ダウンロードできる」と判断しない。
- 画像は 1 枚 3〜37MB。1 都市全部でも TB 級になる (推定、合計 30.79 TiB からの割り算)。
- 日本は個人投稿が中心で、見た地点に 360 度画像は無かった。GrabMaps の 360 度画像は東南アジア。

## 12 ステップでの使い道 (案)

画像認識の深層学習は範囲外なので、画像そのものではなくメタデータか、既存の検出器 (範囲外) で作った点データを使う形になる。

| ステップ | 使い方 |
|---|---|
| 5 k-means / DBSCAN | 写真の位置 (lat/lng) を DBSCAN にかけて、撮影列や撮影が集中する区間を取り出す。電柱・街灯の検出点があれば、同じ物体の重複検出をまとめる |
| 7 Dijkstra / A* | 撮影済み区間を OSM 道路グラフに載せ、未撮影区間を回る経路を作る |
| 8〜9 LP / MILP、facility location | 電柱・街灯の検出点を基地局の設置候補地として、需要 (WorldPop の人口など) に対する配置を解く。候補地の出どころとして使う |
| 4 Cross Validation とデータリーク | 同じ撮影列の連続写真は数 m 間隔で似ているので、写真単位でランダムに分けるとリークする。sequence_id で GroupKFold する例になる |
| 1〜3 回帰・分類 | 未確認。検出点の密度をメッシュ特徴量にする程度 |

## 取り出し方

区分は catalog。API で場所を指定して写真を絞り、選んだ 1 枚だけを引ける。画像そのものは Range が効かないので、1 枚は whole になる。一括ダウンロードの経路は 2026-09-30 の時点で塞がっている。

目録として使える口:

| 要求 | 応答 |
|---|---|
| `POST https://api.openstreetcam.org/1.0/list/nearby-photos/` (`lat=35.6812&lng=139.7671&radius=200`) | 200、79,504 バイトの JSON。`currentPageItems` 115 件、`totalFilteredItems` 115。認証不要 |

返る 1 件には `id`、`sequence_id`、`sequence_index`、`lat`、`lng`、`date_added`、`timestamp`、`username` と、画像のパス 3 種 (`name` が本体、`lth_name` と `th_name` がサムネイル) が入る。緯度経度と半径で絞れて、選んだものの URL がそのまま得られるので、目録として成立している。ただし 1 回の応答は 1,000 件が上限で、bbox ではなく中心と半径でしか指定できない。日時で絞る口は見つけていない (未確認)。

画像の Range は効かない。東京駅付近の写真 (id 1248011617、`storage13/files/photo/2021/3/4/proc/3442397_48108_60412cebefb7d.jpg`) で測った。

| 要求 | 応答 |
|---|---|
| `curl -sI https://storage13.openstreetcam.org/files/photo/2021/3/4/proc/3442397_48108_60412cebefb7d.jpg` | 200、`Content-Length: 2774809`、`accept-ranges: bytes`、`Content-Type: image/jpeg` |
| `curl -r 0-1023` 同じ URL | 200、2,774,809 バイト。206 ではなく全体が返った |

`accept-ranges: bytes` と申告しているのに、Range を投げると 200 でファイル全体を送ってくる。ヘッダを信じると 1KB のつもりが 2.8MB 落ちる。JPEG なので途中まで読んでも意味が無く、いずれにせよ 1 枚は丸ごと取ることになるが、「Accept-Ranges があるから部分読みできる」という前提で組むと転送量の見積もりが桁で外れる。

一括ダウンロードは取れない。

| 要求 | 応答 |
|---|---|
| `GET https://kartaimagestorage.blob.core.windows.net/grab2cmntmini?restype=container&comp=list` | 409、`<Code>PublicAccessNotPermitted</Code>`「Public access is not permitted on this storage account.」 |

2026-09-28 には SAS の期限切れ (403 AuthenticationFailed) だったものが、今日は SAS 無しの要求に対して 409 を返している。どちらにせよ、公開サンプル (mini dataset) の一覧は取れない。全量 30.79 TiB を落とす公開の手段は見つけていない (未確認)。

まとめると、使える形はこうなる。地点を決めて `nearby-photos` を叩き、返ってきたメタデータ (位置、撮影日時、向き、撮影列) だけで済む用途なら、画像を 1 枚も落とさずに済む。画像が要るなら 1 枚 3MB から 37MB を丸ごと、必要な枚数ぶん取る。1 都市ぶんをまとめて取る道は無い。
