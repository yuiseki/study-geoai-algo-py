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

2026-09-29 に `scripts/mirror_mlit_jinryu.py` で作った。99 リソースを CKAN の API から取り、入れ子の zip の CSV を種類ごとに 1 つの Parquet にまとめた。行数と population の合計が元の CSV と一致することを確かめてから置いている。

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
