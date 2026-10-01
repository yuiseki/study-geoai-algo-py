# OurAirports

2026-09-30 に読んで確かめた内容。

- 入口: <https://ourairports.com/>。データの説明は <https://ourairports.com/data/>。
- データの実体は GitHub の `davidmegginson/ourairports-data`。ダウンロードページの記載: 「Effective 3 November 2021, the download files are stored on GitHub, in the repository davidmegginson/ourairports-data. The old download links redirect to there.」
- 配布経路は 2 つあるが中身は同じ。`https://ourairports.com/data/airports.csv` は 301 で GitHub Pages に飛び、`https://davidmegginson.github.io/ourairports-data/airports.csv` と同じ ETag、同じバイト数、同じ Last-Modified を返した。
- 中身は世界の空港、滑走路、通信周波数、航法援助施設、国、一級行政区分。全部 UTF-8 の CSV で、点の座標を持つ。ポリゴンは無い。
- 集め方はクラウドソーシング。About ページの記載: 「OurAirports started in 2007 primarily to fill that gap: we encourage members to create and maintain data records for airports around the world, and they manage over 40,000 of them.」DAFIF が 2006 年に公開停止になった穴を埋める目的で始まったと書いてある。

## 配布ファイル (2026-09-30 に HEAD で確かめた)

Last-Modified はどれも `Wed, 30 Sep 2026 01:53:58 GMT` で同じ。これは GitHub Pages が配信物を作り直した時刻で、そのファイルの中身が変わった時刻ではない。中身が変わった時刻は下の「古くなっているか」に分けて書く。

| ファイル | バイト数 | Last-Modified (HTTP) |
|---|---:|---|
| airports.csv | 12,733,703 | 2026-09-30 01:53:58 GMT |
| runways.csv | 3,966,684 | 2026-09-30 01:53:58 GMT |
| navaids.csv | 1,524,946 | 2026-09-30 01:53:58 GMT |
| countries.csv | 24,583 | 2026-09-30 01:53:58 GMT |
| regions.csv | 485,265 | 2026-09-30 01:53:58 GMT |
| airport-frequencies.csv | 1,301,981 | 2026-09-30 01:53:58 GMT |
| airport-comments.csv | 4,681,039 | 2026-09-30 01:53:58 GMT |

合計 24,718,201 バイト。全部落としても 25MB 弱で、このカタログの中では最も小さい部類。

## airports.csv の中身 (落として数えた)

- 86,153 行 (ヘッダを除く)、19 列。
- 列: `id`, `ident`, `type`, `name`, `latitude_deg`, `longitude_deg`, `elevation_ft`, `continent`, `iso_country`, `iso_region`, `municipality`, `scheduled_service`, `icao_code`, `iata_code`, `gps_code`, `local_code`, `home_link`, `wikipedia_link`, `keywords`。
- `type` の内訳: small_airport 42,764、heliport 23,224、closed 13,548、medium_airport 4,106、seaplane_base 1,273、large_airport 1,175、balloonport 63。ヘリポートと閉鎖済みで 4 割を超える。
- 定期便のある空港 (`scheduled_service` が yes) は 4,335 件。
- IATA コードを持つ行は 9,053、ICAO コードを持つ行は 10,530。
- 座標が空の行は 0。標高が空の行は 14,953、市区町村名が空の行は 4,748、Wikipedia へのリンクを持つ行は 16,757。
- `iso_country` は 247 種類。多い順に US 32,668、BR 8,065、JP 3,747、CA 3,369、AU 2,795、MX 2,695、RU 1,839、FR 1,786。米国だけで 38% を占める。
- 日本 (JP) の 3,747 件の内訳: heliport 3,040、closed 419、small_airport 171、medium_airport 79、large_airport 29、seaplane_base 6、balloonport 3。定期便ありは 85 件。日本のデータはほとんどがヘリポートで、いわゆる空港は 300 件足らず。

## ライセンス

ダウンロードページの Terms of use の原文:

> All data is released to the Public Domain, and comes with no guarantee of accuracy or fitness for use.

同じページの、帰属表示についての原文:

> You can even use them to set up your own, competing airport web site if you'd like! We'd love you to give us credit, like we give credit to our sources, but you're not required to.

About ページの原文:

> Many web sites, smartphone apps, and other services rely on OurAirport's data, which is all in the Public Domain (no permission required).

読んだ範囲では、データの一部を除く但し書きは見つからなかった。「All data」と書いてあり、ファイルごとの例外も、元データ由来の制約も書かれていない。ただし次の 2 点は注意が要る。

- GitHub リポジトリの `LICENSE` は The Unlicense で、本文は「This is free and unencumbered software released into the public domain.」から始まり、一貫して software としか言っていない。データを名指しでパブリックドメインにしているのはサイト側の文で、リポジトリの LICENSE ではない。
- About ページの Credits には元にした情報源が並んでいる。FAA、DAFIF、Geonames、navaid.com、SoaringWeb.org、Great Circle Mapper、Wikipedia、Kwik Navigation Flight Planner など。これらから取り込んだ値まで本当にパブリックドメインに置けるかは、サイトの宣言以上の根拠を確かめていない。未確認。

## 古くなっているか

結論としては、古くなってはいない。毎晩更新されていて、その更新は空のコミットではなく実際に中身が変わっている。ただし「ファイルによっては何か月も止まっている」のは事実で、ダウンロードページの表示がそれを隠している。

GitHub API で確かめたこと。

- リポジトリの `pushed_at` は 2026-09-30T01:53:22Z。`archived` は false、`disabled` は false。
- 最新コミットは `f31ef57d` 2026-09-30T01:53:18Z、メッセージは `data update`。作者は OurAirports support。
- 直近 100 コミットは 2026-06-23 から 2026-09-30 まで、1 日 1 本ずつ途切れなく並んでいる。毎日 01:53 UTC 前後。
- コミット総数は 1,773 (`per_page=1` のページネーションの last から)。リポジトリ作成は 2021-11-02。
- 直近 7 コミットの差分を見ると、どれも実際に行が動いている。2026-09-30 は airports.csv が +8 -6 と runways.csv が +1 -1、2026-09-27 は airports.csv が +44 -44、airport-frequencies.csv が +2、runways.csv が +8 -2、regions.csv が +1 -1。空コミットではない。

ファイルごとに、実際に中身が変わった直近のコミット日時を `commits?path=` で引いた。

| ファイル | 中身が最後に変わった日 | 直前 |
|---|---|---|
| airports.csv | 2026-09-30 | 2026-09-29、2026-09-28 と毎日 |
| runways.csv | 2026-09-30 | 2026-09-29、2026-09-28 と毎日 |
| airport-frequencies.csv | 2026-09-28 | 2026-09-27、2026-09-26 |
| airport-comments.csv | 2026-09-29 | 2026-09-23、2026-09-20 |
| regions.csv | 2026-09-29 | 2026-09-27、2026-09-11 |
| navaids.csv | 2026-07-30 | 2026-06-18、2026-05-28、その前は 2025-03-02 |
| countries.csv | 2025-02-28 | 2025-02-21、2025-02-01 |

`countries.csv` は 19 か月動いていない。`navaids.csv` は 2025-03-02 から 2026-05-28 まで 1 年 3 か月動かず、そのあと 3 回だけ動いた。空港と滑走路は毎日動いている。

ここが紛らわしいところで、`https://ourairports.com/data/` のページは 7 ファイルすべてについて「last modified Sep 30, 2026」と表示する。この表示は HTTP の Last-Modified、つまり Pages の配信物を作り直した時刻をそのまま出している。リポジトリの README はこの食い違いを自分で認めている。

> Note: OurAirports generates the files every day, but GitHub updates the date only when the contents have changed. As a result, files that change rarely, like countries.csv, may show a date weeks or months in the past.

この注記は GitHub 上の日付について書いたもので、サイトの表示のほうがむしろ実態から外れている。ファイルの新しさを見るなら、HTTP の Last-Modified でもサイトの表示でもなく、`commits?path=` を見る。

編集を受け付けているか。受け付けている。

- `https://ourairports.com/stats/contributors.html` の「Last 30 days」は、Airports added の上位 10 人が @Bill35 (103)、@Capitano.Nico (15)、@Thomas_lmt (6)、@F0RD (6)、@Ford (6)、@Jan_Olieslagers (3)、@Pugliapilot (3)、@matt7782 (3)、@asedrio23 (3)、@animebirder (2)。Airports updated は @Bill35 (222)、@Jan_Olieslagers (19) から始まる。直近 30 日で上位 10 人だけで 150 件の追加と 260 件超の更新がある。
- コメントの RSS (`https://ourairports.com/comments.rss`) の最新は 2026-09-28、その前が 2026-09-22、2026-09-19。
- リポジトリの README に投稿の窓口が書いてある。「Please do not create pull requests. To add new airports or update information for existing ones, please go to https://ourairports.com and create a free account. Your updates will appear in the next daily data dump to GitHub.」

止まっているのは維持者の応答のほうで、データではない。Issue は 27 件が open。維持者の返信が付いた Issue で最後に動いたのは #46「Daily dump broken?」で、最終更新は 2025-12-01。2026 年に立った Issue #47 (2026-01-23)、#48 (2026-04-29)、#49 (2026-06-23)、#50 (2026-07-25) はいずれも返信が 0 件のまま。2022 年に立った #11「Missing recent changes?」や #13「ourairports.com site is down」も open のまま残っている。

## 気をつけること

- ダウンロードページの「last modified」を信じない。7 ファイルすべてが今日の日付に見えるが、`countries.csv` の中身は 2025-02-28 から変わっていない。実際の鮮度は GitHub の `commits?path=<file>` で見る。
- 更新は毎日だが、日付の列がデータの中に無い。`airports.csv` には「この行がいつ更新されたか」を示す列が無く、行単位の鮮度は CSV だけでは分からない。追うならリポジトリのコミット履歴を自分で辿ることになる。
- `type` が `closed` の行が 13,548 件ある。空港の一覧として素朴に使うと、すでに無い飛行場が 16% 混ざる。日本でも 3,747 件のうち 419 件が closed。
- ヘリポートが 23,224 件あり、日本に至っては 3,747 件のうち 3,040 件がヘリポート。「空港の数」を数える題材にすると、`type` で絞らない限り意味のある数にならない。
- コードの信頼度にばらつきがある。Issue #49 (2026-06-23、返信 0 件) は、IATA の公式コード検索と突き合わせた結果として、IATA コードを持つ 9,055 件のうち 272 件 (3.0%) が確認できなかったと報告している。内訳は small_airport 138、heliport 92、medium_airport 31、seaplane_base 8、large_airport 3。報告者自身が「These 272 are not all errors」と断っているので、誤りの数ではなく突き合わせで解決しなかった数と読む。この数字は報告者の集計であって、こちらで再検証していない。
- 編集そのものが壊れているという報告が 2 件、返信なしで残っている。Issue #39 (2025-04-21)「Impossible to edit airports」と Issue #47 (2026-01-23)「Cannot edit airport information after logging into ourairports.com」。上の貢献者統計を見る限り編集できている人はいるので、全員が詰まっているわけではない。ログインが要るのでこちらでは再現していない。未確認。
- パブリックドメインの宣言はサイトの文で、リポジトリの LICENSE は software としか書いていない (上のライセンスの節を参照)。厳密さが要る用途では、根拠としてサイトのページを引く。
- Excel で直接開くと文字化けする。ページに書いてあるとおり UTF-8 で、Excel はそれを検出しない。

## 空港のデータとして何を使うか

このカタログにある、空港を含むほかの出どころと比べた。

- [Natural Earth](../natural-earth/README.md) の `ne_10m_airports.zip` を落として数えたところ、893 件だった (zip 290,778 バイト、Last-Modified 2021-12-08)。主要な空港だけで、こちらのほうがよほど古い。小縮尺の地図に主要空港を置くには足りるが、網羅性は無い。
- [Overture Maps](../stac/overture-maps.md) の `base/infrastructure` テーマ (157,617,917 件、ODbL-1.0) が空港を持つ。スキーマ (`schema/base/infrastructure.yaml`) の `subtype` の enum に `airport` があり、`class` の enum に `airport`、`airport_gate`、`airstrip`、`apron` がある。説明文は「Various features from OpenStreetMap such as bridges, airport runways, aerialways, or communication towers and lines.」で、出どころは OSM。ポリゴンや線が要るならこちら。
- [OpenStreetMap Japan PMTiles](../openstreetmap-japan-pmtiles/README.md) には `aeroway` レイヤー (z10-14) がある。[z.yuiseki.net の OSM タイル](../z-yuiseki-static/openstreetmap.md) にも `aerodrome_label` と `aeroway` がある。表示用。

使い分けはこうなる。

- 空港の点と、IATA / ICAO コードと、定期便の有無が要るなら OurAirports。この用途で 86,153 件を 12.7MB の CSV で配っているものは、このカタログの中にほかに無い。Natural Earth の 893 件では足りず、Overture / OSM はコードの付き方が一定でない。
- 空港の形 (滑走路、エプロン、ターミナルのポリゴン) が要るなら Overture の `base/infrastructure` か OSM。OurAirports には滑走路の長さと方位はあるが (`runways.csv`)、形は無い。
- 主要空港を数十件だけ地図に置くなら Natural Earth で足りる。

OurAirports を避ける理由は、古さではなく質のばらつきにある。closed とヘリポートの比率、行単位の更新日が無いこと、コードの 3% が突き合わせ不能という報告。どれも `type` と `scheduled_service` で絞り、コードを鵜呑みにしないことで扱える範囲。

## 学習ステップとの対応 (案)

- 1 線形回帰、2 Random Forest、3 XGBoost: `scheduled_service` が yes かどうかを、標高、緯度経度、`type`、国、最寄りの都市の有無から当てる二値分類。86,153 行は手元で回る大きさで、正例が 4,335 件なので不均衡データの題材にもなる。
- 4 Cross Validation: 空港は国ごとに固まっている (US だけで 38%)。ランダム分割と国単位のグループ分割で評価が変わる様子を見る題材になる。
- 7 Dijkstra / A*: 定期便のある 4,335 空港を節点にした最短経路。辺は自分で作る必要があり、`airports.csv` に路線の情報は無い。
- 9 facility location: 既存の空港の位置を所与として、ヘリポートの配置を問う。日本は 3,040 件あるので国内だけで完結する。
- 11 SHAP: 上の分類器で、標高と国と `type` のどれが効いているかを見る。
- ほかの出どころと繋ぐ鍵として使いやすい。`iso_country` は ISO 3166-1 alpha-2 で、[Natural Earth](../natural-earth/README.md) や [geoBoundaries](../geoboundaries/README.md) と突き合わせられる。`wikipedia_link` を持つ 16,757 件は [Wikidata](../wikidata/README.md) に繋げられる。

## 取り出し方

区分は whole。ただし Range 要求そのものは効く。全部落としても 24,718,201 バイトなので、部分取得を考える理由が無い。

2026-09-30 に GitHub Pages で測った。

| 要求 | 応答 |
|---|---|
| `curl -sI https://davidmegginson.github.io/ourairports-data/airports.csv` | 200、`accept-ranges: bytes`、`etag: "6abc6bb6-c24d07"` (c24d07 は 12,733,703 バイト)、`server: GitHub.com` |
| `curl -r 0-1023 .../airports.csv` | 206、1,024 バイト。返ってきたのは CSV の見出し行 (`"id","ident","type","name",...`) |
| `curl -r 0-1023 .../countries.csv` | 206、1,024 バイト |
| `curl -sI https://ourairports.com/data/airports.csv` | 301、`location` は上の GitHub Pages。`server: nginx/1.27.5` |

GitHub Pages は Range に本当に 206 で答える。ヘッダの申告どおりだった。

それでも range に分類しないのは、CSV に索引が無いからである。先頭 1,024 バイトを取っても見出し行と最初の数行が返るだけで、「日本の空港だけ」や「定期便のある空港だけ」を引くことはできない。区分の表が range の条件として「索引がファイルの先頭付近にあること」を挙げているのは、まさにこの違いを指している。バイト位置は選べるが、意味のある部分集合は選べない。

split でもない。7 ファイルは地域で割ったものではなく、空港・滑走路・周波数・航法援助施設・国・一級行政区分・コメントという種類で分かれている。必要な種類だけを取るという意味では 7 つから選べるが、地理で絞る分割ではない。

| ファイル | バイト数 |
|---|---:|
| airports.csv | 12,733,703 |
| runways.csv | 3,966,684 |
| navaids.csv | 1,524,946 |
| countries.csv | 24,583 |
| regions.csv | 485,265 |
| airport-frequencies.csv | 1,301,981 |
| airport-comments.csv | 4,681,039 |
| 合計 | 24,718,201 |

最小単位は 1 ファイル。空港だけなら 12,733,703 バイト、全部でも 25MB 弱。これは落としきってから DuckDB なり pandas なりで絞るほうが、範囲要求を組み立てるより速いし確実である。whole がここでは正しい答えになる。

## z.yuiseki.net のスナップショット

上流は毎晩同じ URL の中身を差し替え、行に更新日の列が無い。分析を再現するにはその日のファイルを自分で残すしかないので、<https://z.yuiseki.net/static/ourairports/> に日付ごとのディレクトリで置いた。取得スクリプトは [scripts/mirror_ourairports.py](../../../scripts/mirror_ourairports.py)、テストは [tests/test_mirror_ourairports.py](../../../tests/test_mirror_ourairports.py)。定期実行はしていない。取りたい日に手で流す。

- 取るのは GitHub の最新 commit で、ファイルは `raw.githubusercontent.com/<sha>/` から引く。GitHub Pages の URL は中身が差し替わるので使わない。落としたファイルは、その commit の tree にある git blob の SHA-1 と大きさで照合してから置く。
- ディレクトリ名は commit の UTC の日付。最初の 1 本は 2026-10-01 (commit `b6268327`、airports は 86,154 行で、9-30 の 86,153 行から 1 行増えた)。
- 中身は `csv/` (元の 7 ファイルをそのまま)、7 つの Parquet、`manifest.json`。airports と navaids は `geometry` 列 (点) を足した GeoParquet 1.0.0。合わせて 32MB。
- 列の型は名前で決める。`id` と `*ref` は BIGINT、`*_ft`、`*_khz`、`lighted`、`closed` は INTEGER、`*_deg`、`*_mhz` は DOUBLE、それ以外は文字列。`regions.local_code` の `02` は引用符なしで書かれているので、型を推論させると先頭のゼロが落ちる。
- 整数の列に整数でない値があると止まる。DuckDB の cast は `'12.5'` を INTEGER にするときエラーにせず 13 に丸めるので、cast の前に正規表現で形を確かめている。
- `airport-comments.csv` の見出しは `"id", "threadRef", ...` のようにカンマの後に空白がある。Parquet の列名では空白を落とした。
- 公開 URL への `curl -r -8` は 3 回とも 206。DuckDB の httpfs で `airports.parquet` から日本の定期便あり (85 件) と全件数を数えるのに 0.12 秒。
