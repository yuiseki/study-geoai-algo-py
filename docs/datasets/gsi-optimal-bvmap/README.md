# 国土地理院 最適化ベクトルタイル (optimal_bvmap)

2026-09-29 に、リポジトリ <https://github.com/gsi-cyberjapan/optimal_bvmap> の README と、PMTiles のヘッダーとメタデータ (Range 要求で先頭と 4KB だけ) を読んで確かめた内容。

- 国土地理院が試験公開しているベクトルタイル。地理院地図 Vector の地理院ベクトルタイルを設計し直したもの。公開は 2022-09-06 から、PMTiles 版は 2023-08-30 から。
- データソースは「数値地図 (国土基本情報) - 地図情報 等」。国土数値情報の N13 道路データと同じ元データ。データ更新は 2026-07-01 時点 (README)、PMTiles のファイルの最終更新は 2026-09-17。
- 「基本測量成果と位置付けているものではありません」とあり、検証中のため URL や属性が変わる可能性がある。
- デモ: <https://gsi-cyberjapan.github.io/optimal_bvmap/>

## ファイル

| 形式 | URL | 備考 |
|---|---|---|
| PMTiles | `https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/optimal_bvmap-v1.pmtiles` | 16,900,763,181 バイト。Amazon S3 から配信 |
| XYZ | `https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/{z}/{x}/{y}.pbf` | 2023-10-01 時点で更新を止めている |

- Range 要求に、1 回目から 206 を返した (2 回試した)。z.yuiseki.net の Cloudflare のような「初回だけ 200」は無い。Cloud Native に読める。
- PMTiles v3、クラスタ化済み、タイルは gzip の MVT。ズーム 4〜16 (17 の情報は 16 に含めてオーバーズーム)。範囲は経度 122.0〜154.77、緯度 17.03〜46.0。
- タイル 2,582,172 種 (アドレス 2,949,893)。ルートのディレクトリ 2,376 バイト、葉のディレクトリ 5.8MB。
- ズームは地理院タイル (ラスタ) より 1 小さい。ベクトルタイルの z16 は、ラスタの z17 と同じデータ。
- 作り方 (メタデータの generator_options): 縮尺ごとに tippecanoe で 4 つの MBTiles (5000k は z4〜7、1000k は z8〜10、200k は z11〜13、25k は z14〜16) を作り、tile-join でまとめている。stars.optgeo.org の bvmap も同じ 4 つの MBTiles の構成なので、この出力から作られていると考えられる。

## レイヤー (24)

| レイヤー | ズーム | 属性 |
|---|---|---|
| RdCL 道路中心線 | 4〜16 | vt_code, vt_rdctg (道路の種別), vt_rnkwidth (幅員区分), vt_width, vt_lvorder (上下の順), vt_motorway, vt_tollsect, vt_drworder, vt_flag17 |
| RdEdg 道路縁、RdCompt 道路構成線 | 16 | vt_code |
| RailCL 鉄道中心線 | 4〜16 | vt_railstate, vt_rtcode, vt_sngldbl, vt_lvorder ほか |
| BldA 建物 | 14〜16 | vt_code, vt_lvorder |
| Cntr 等高線 | 9〜16 | vt_alti |
| Isbt 等深線 | 14〜16 | vt_depth |
| Anno 注記 | 4〜16 | vt_text, vt_code ほか |
| そのほか | | AdmArea, AdmBdry, Cstline, PwrTrnsmL, RailTrCL, RvrCL, SpcfArea, StrctArea, StrctLine, TpgphArea, TpgphLine, WA, WL, WRltLine, WStrA, WStrL |

地物種別コードと属性の意味は、README から辿れる一覧 (optbv_featurecodes、optbv_dataspec、optbv_attribute の PDF と Excel) にある (中身は未確認)。

## ライセンス

- 「国土地理院コンテンツ利用規約に従って利用できます。データを利用する際は、『国土地理院最適化ベクトルタイル』などと、出典の明示を行ってください」(README)。
- N13 (国土数値情報) は元資料の欄に「測量法に基づく国土地理院長承認 (複製)」があり、ファイルの再配布には承認が要る (2026-09-29 にユーザーが判断)。こちらは基本測量成果と位置付けられていないが、再配布の扱いは確かめていない。Range で読んで分析するだけなら、出典の明示で足りる。

## このリポジトリでの使い道 (案)

- N13 の代わりの道路網: RdCL は N13 とほぼ同じ属性 (種別、幅員、上下の順) を持ち、Range で必要な範囲のタイルだけ読める。N13 の zip を丸ごと取る必要が無くなる。
- ただし、タイルの端で線が切られ、tippecanoe で簡略化されている (-S 2)。道路網にするには、隣のタイルとの境目で線をつなぎ直す必要がある。z16 のタイルを使えば、簡略化の影響は小さいと考えられる (確かめていない)。
- 建物 (BldA) と等高線 (Cntr) も同じ仕組みで読める。

## 取り出し方

range。2026-09-30 に実測し直した。

`https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/optimal_bvmap-v1.pmtiles` の HEAD は 200 で、`Content-Length` 16,900,763,181、`Accept-Ranges: bytes`、`Last-Modified` Thu, 17 Sep 2026 07:32:00 GMT、`ETag` `"dfa81a9cba11aad28247d63a2d8361ec-2015"`。`Server: AmazonS3` に `x-cache: Hit from cloudfront` が重なっており、Amazon S3 を CloudFront で配信している。

`curl -s -r 0-1023` は 206 と 1,024 バイトを返した。先頭 127 バイトの Range 要求も 206 と 127 バイトで、先頭 7 バイトは `PMTiles`、8 バイト目 (spec version) は 3。

| 項目 | 値 |
|---|---:|
| ルートディレクトリの位置 | 127 |
| ルートディレクトリの長さ | 2,376 |
| メタデータの位置 / 長さ | 2,503 / 4,168 |
| 葉ディレクトリの位置 / 長さ | 6,671 / 5,755,653 |
| タイルデータの位置 | 5,762,324 |
| アドレスされたタイル数 | 2,949,893 |
| ディレクトリ項目 | 2,894,857 |
| 中身の異なるタイル | 2,582,172 |

ズームは 4 から 16。ヘッダの 101 バイト目 (min zoom) と 102 バイト目 (max zoom) を 1 バイトずつ読んだ値で、TileJSON やページの記載ではない。bounds は 103 バイト目からの int32 4 つ (1e-7 度単位) を読んで、経度 122.0 から 154.766667、緯度 17.03498 から 46.0。

16.9GB のファイルに対して、ルートディレクトリまで含めて先頭 2,503 バイトで索引の入口に届く。メタデータも 6,671 バイト目までに収まっているので、レイヤー構成を知るのに 7KB も要らない。

XYZ の `https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/{z}/{x}/{y}.pbf` はまだ生きている。台東区付近の `14/14552/6451.pbf` は 200 と 77,733 バイトを返した。こちらは Range ではなくタイル 1 枚につき 1 要求になる。ただし 2023-10-01 時点で更新を止めているので、新しいデータが要るなら PMTiles を読む。
