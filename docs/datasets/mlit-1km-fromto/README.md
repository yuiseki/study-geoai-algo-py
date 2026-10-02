# 全国の人流オープンデータ (1km メッシュ、市区町村単位発地別)

2026-09-29 に読んで確かめた内容。

- データセット: <https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto> (G 空間情報センター)
- 作成: 国土交通省 不動産・建設経済局 情報活用推進課。元は Agoop 社の SDK を組み込んだスマートフォンアプリの GPS データ (定義書の参考資料)
- 期間: 2019-01〜2021-12 の各月。2024-10 以降は更新されていない (metadata_modified)

## 取得

- ページには「ダウンロードはユーザ登録の後、ログイン状態で行ってください」とある。
- ただし、CKAN の API (`/ckan/api/3/action/package_show?id=mlit-1km-fromto`) にはログインなしで答え、そこに並ぶ resource の URL も、ログインなしで署名付きの S3 の URL (`ckan-storage.s3.amazonaws.com`、有効 1 時間) へ 302 で飛ぶ。`curl -L` で中身が落ちてくる (東京都の 2 つの zip と規約、定義書で確かめた)。
- ログインを求めているのはページの案内文だけで、サーバーは強制していない。G 空間情報センターのサイトの規約でログインが条件になっているのかは、確かめていない。
- 105 リソース。都道府県ごとの zip が 2 種類 × 47 本、ほかに規約、定義書、解析例などの PDF と、マスタの zip が 3 本。
  - `monthly_mdp_mesh1km_NN.zip` (1km メッシュ別): 47 本で 178.9MB。東京都は 2.7MB
  - `monthly_fromto_city_NN.zip` (市区町村単位の発地別): 47 本で 12.8MB。東京都は 0.45MB
  - `attribute.zip` (メッシュの中心と範囲の経緯度): 7.9MB
- zip の中は `13/2019/01/monthly_mdp_mesh1km.csv.zip` のように、月ごとの zip が入れ子になっている (東京都は 36 か月)。S3 は Range を受けるが、入れ子の zip の中の CSV なので、部分読みはできない。

## 中身

滞在人口は、その月の 1 日あたりの平均。10 人未満の値は出力しない。

1km メッシュ別 (`monthly_mdp_mesh1km.csv`):

| 列 | 中身 |
|---|---|
| mesh1kmid | 3 次メッシュのコード (8 桁) |
| prefcode、citycode | 都道府県と市区町村のコード |
| year、month | 年と月 |
| dayflag | 0 休日、1 平日、2 全日 |
| timezone | 0 昼 (11〜14 時台の平均)、1 深夜 (1〜4 時台)、2 終日 |
| population | 滞在人口 |

- 東京都は 36 か月で 494,246 行。2021-12 は、区分の組ごとに 1,404〜1,557 メッシュ。
- 2021-12 の全日、昼に台東区 (13106) で最も多いのは 53394652 の 63,678 人 (休日の昼なら 53394653 の 51,346 人)。

市区町村単位の発地別 (`monthly_fromto_city.csv`): 列は year、month、dayflag、timezone、prefcode、citycode (滞在先)、from_area、population。from_area は居住地の区分で、0 同じ市区町村、1 同じ都道府県の別の市区町村、2 同じ地方ブロックの別の都道府県、3 別の地方ブロック。発地の市区町村は分からない。

- 福岡県那珂川市は、2019 年のデータだけ旧那珂川町のコード (40305) になっている (定義書)。
- 定義書 (2021-02) の期間は 2020-12 までだが、実際のファイルには 2021 年分も入っている。

## ライセンス

- 「全国の人流オープンデータ利用規約」(令和 3 年 1 月 27 日)。政府標準利用規約 (第 2.0 版) に準拠し、CC BY 4.0 と互換。複製、公衆送信、翻案、商用利用ができる。
- 出典の書き方: 「出典：「全国の人流オープンデータ」（国土交通省）（https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto）」。加工したときは「……を加工して作成」と書き足す。
- 再配布できるので、z.yuiseki.net/static/ に Parquet でミラーした (次の節)。

## ミラー (z.yuiseki.net/static/mlit-1km-fromto/)

2026-09-29 に作った。取得スクリプトは [scripts/mirror_mlit_jinryu.py](../../../scripts/mirror_mlit_jinryu.py)、テストは [tests/test_mirror_mlit_jinryu.py](../../../tests/test_mirror_mlit_jinryu.py)。99 リソースを CKAN の API から取り、入れ子の zip の CSV を種類ごとに 1 つの Parquet にまとめた。行数と population の合計が元の CSV と一致することを確かめてから置いている。

- 置き場は yuisekin-z の `/www/html/static/mlit-1km-fromto/` で、nginx がこれを `https://z.yuiseki.net/static/mlit-1km-fromto/` として配る。
- 定期実行はしていない。上流は 2024-10 から更新されていないので、取り直す理由が無い。

| ファイル | 行数 | 大きさ |
|---|---:|---:|
| monthly_mdp_mesh1km.parquet | 38,079,507 | 111.9MB (380 行グループ) |
| monthly_fromto_city.parquet | 2,340,980 | 5.5MB |
| attribute_mesh1km.parquet | 775,000 (2019 年版と 2020 年版で 387,500 ずつ) | 7.1MB (GeoParquet 1.0.0、範囲の四角形) |
| prefcode_citycode_master.parquet | 3,792 | 34KB |
| regioncode_master.parquet | 94 | 2KB |

- ほかに元の license.pdf と opendatadefinition.pdf、manifest.json (取得した各ファイルの URL、大きさ、sha256、Last-Modified)、README.md、LICENSE。
- コードは元のとおりの文字列 (prefcode は `'01'`、month は `'01'`)。数値と比べると一致しないので、`where prefcode = '13'` のように文字列で絞る。
- 属性とマスタには 2019 年版と 2020 年版があり、`version` 列で分けてある。属性は 70 行 (主に那珂川のコード)、市区町村マスタは 50 行 (東京 23 区の名前が 2019 年版では「東京２３区千代田区」) 違う。結合するときは `version = '2020'` などで片方に絞らないと行が倍になる。
- メッシュ別は都道府県、年、月の順に並べてあるので、東京都 (494,246 行) の件数と合計は公開 URL から 0.4 秒で出た。Cloudflare は 3 回とも初回から 206 を返した。
- 取得した zip は `/tmp/study-geoai-mirror-mlit-jinryu/raw/` に残る。もう一度流すと、大きさが同じ zip は取り直さない。

## 学習ステップとの対応 (案)

- 5 クラスタリング、6 PCA: メッシュを、平日と休日、昼と深夜の 4 つの値の比で型に分ける (住宅地、業務地、繁華街)。
- 1〜3 回帰: Overture の建物や POI、WorldPop の夜間人口から、昼の滞在人口を予測する。
- 4 Cross Validation: 月で分けるか、区でまとめて分けるか。2020 年 4〜5 月は緊急事態宣言で分布がずれる。
- 9 施設配置: 需要を夜間人口でなく昼の滞在人口にすると、選ぶ場所がどう変わるか。

## 取り出し方

区分は range。分割の単位としては split (47 都道府県 x 2 種類) も併せ持つ。2026-09-30 に実測した。

上の「取得」の節に「入れ子の zip の中の CSV なので、部分読みはできない」と書いたが、
実際に Range を投げて確かめると、月ごとのファイルなら丸ごと落とさずに取り出せた。訂正としてここに残す。

### 署名付き S3 の挙動

CKAN の resource URL
`https://www.geospatial.jp/ckan/dataset/8fd79f08-00e6-4d14-9c89-e3bdca66af11/resource/3b69ffab-2fb8-4901-9cf3-9da2c19e3351/download/monthly_mdp_mesh1km_13.zip`
は 302 で `ckan-storage.s3.amazonaws.com` の署名付き URL へ飛ぶ。

- 飛んだ先に `curl -sI` を投げると 403 Forbidden。署名が GET 用なので、HEAD は通らない。
- 同じ URL に `curl -r 0-1023` を投げると 206 と 1,024 バイトが返る。`curl -r -8` も 206 と 8 バイト。
- CKAN の URL に `curl -L -r 0-1023` でも 206 と 1,024 バイト。転送をまたいでも Range は生きている。

大きさを知りたいときは HEAD ではなく CKAN の API の `size` (東京都のメッシュ別で 2,707,401 バイト) を使う。

### zip の中身を Range で選ぶ

zip の中央ディレクトリはファイルの末尾にあるので、Parquet と同じ 2 段の往復になる。

1. `curl -r -64` で末尾 64 バイトを引く (206、64 バイト)。`PK\x05\x06` が見つかり、エントリ 76 個、中央ディレクトリの大きさ 5,287 バイト、位置 2,702,092 と読めた。
2. `curl -r 2702092-2707378` で中央ディレクトリを引く (206、5,287 バイト)。76 エントリの名前、圧縮方式、位置、大きさが並ぶ。例: `13/2021/12/monthly_mdp_mesh1km.csv.zip` は方式 8 (deflate)、圧縮後 73,521 バイト、展開後 73,782 バイト、位置 2,628,503。
3. `curl -r 2628503-2628532` でローカルヘッダの 30 バイトを引き (206)、名前と拡張領域の長さからデータの開始位置 2,628,571 を出す。
4. `curl -r 2628571-2702091` でそのメンバーだけを引く (206、73,521 バイト)。展開すると 73,782 バイトの内側の zip になり、その中の `monthly_mdp_mesh1km.csv` は 13,399 行。1 行目は
   `mesh1kmid,prefcode,citycode,year,month,dayflag,timezone,population`、2 行目は `53394519,13,13101,2021,12,0,0,10745` だった。

合計 4 回の要求、78,892 バイトで 1 か月分が取れる。ファイル全体 2,707,401 バイトの 2.9%。
zip のメンバーはそれぞれ独立に deflate されているので、そのメンバーの先頭から引けば単独で展開できる。

ただし、CSV そのものの部分読みはできない。ある月のある市区町村だけを引くことはできず、その月の全行を展開することになる。
刻める最小の単位は「都道府県 x 種類 x 年 x 月」。

### ミラー (Parquet) は range

`https://z.yuiseki.net/static/mlit-1km-fromto/monthly_mdp_mesh1km.parquet` で確かめた。

| 確かめたこと | 結果 |
|---|---|
| `curl -sI` | 200、Content-Length 111,927,571、Accept-Ranges: bytes |
| `curl -r 0-1023` | 206、1,024 バイト |
| `curl -r -8` | 206、8 バイト。中身は `54 d7 03 00 50 41 52 31` |
| 末尾 4 バイト | `PAR1` |
| フッターの長さ | 251,732 バイト |
| フッター本体 `bytes=111675831-111927562` | 206、251,732 バイト |

フッターが 64KB に収まらないので、末尾の読みが 2 回になる。
pyarrow 20.0.0 に Range 要求だけを出す読み取り器を渡し、`mesh1kmid` と `population` の 2 列を最初の行グループ分だけ読むと、
要求は合計 4 回 (末尾 2 回、列の塊 2 回)、流れたのは 636,036 バイト、0.3 秒。380 行グループ、1 つ 100,352 行。

上流の zip は月で刻むのが限界だったが、Parquet は列でも行グループでも刻める。
都道府県、年、月の順に並べてあるので、東京都だけを読むときに読む行グループも絞られる。

### まとめ

| 経路 | 区分 | 根拠 |
|---|---|---|
| CKAN の API | catalog に近い | 105 リソースの一覧がログイン無しで 200。bbox や日時では絞れず、名前で選ぶだけ |
| 署名付き S3 の zip | range (月単位)、split (47 都道府県 x 2 種類) | 末尾 64 バイトから中央ディレクトリを辿り、4 回の要求 78,892 バイトで 1 か月の CSV を取り出せた |
| zip の中の 1 か月の CSV | whole | deflate の連続した流れなので、途中の行だけは引けない |
| z.yuiseki.net の Parquet | range | 末尾 4 バイトが `PAR1`、2 列 1 行グループを 4 回の要求、636,036 バイトで読めた |

## Hugging Face の凍結版

<https://huggingface.co/datasets/yuiseki/mlit-1km-fromto-2022-01> に、元の zip と PDF 99 本と Parquet 5 本を置いた。コードは <https://github.com/yuiseki/mlit-1km-fromto-2022-01>。名前の年月は、ファイルの中身が最後に変わった月。

- 2026-10-02 に取り直すと、99 本すべての Last-Modified が 2026-09-30 になっていた。中身は 2026-09-29 に取ったものとバイト単位で同じで、置き直されただけだった。版の確認は日付ではなく、9-29 の sha256 との照合で行う。
- Parquet はブルームフィルタ無しで書いた。DuckDB は、統計で除外できた行グループについても、絞り込みに使った列のブルームフィルタを読みにいく。dayflag と timezone はどの行グループにも 0〜2 があるので、台東区の 1 か月を引くクエリが HF から 1,114 回の要求と 32 秒になった。無しで書くと 12 回と 7 秒。z.yuiseki.net の Parquet (この節より上のミラー) も 2026-10-02 にブルームフィルタ無しで書き直した (メッシュ別は 111,927,571 から 104,065,028 バイト。値は両方向の差分で 0 行)。
