# GeoNames

2026-09-30 に読んで確かめた内容。大きさは `https://download.geonames.org/export/dump/` への HEAD が返した `Content-Length` と `Last-Modified`、件数は小さいファイルを実際に落として数えた行数、全体の合計は `https://www.geonames.org/statistics/` が返した表から。

- `https://www.geonames.org/`。全世界の地名辞書 (gazetteer)。運営は Unxos GmbH (スイス、St. Gallen)、創始者は Marc Wick。about ページに書いてある。
- 配布は `https://download.geonames.org/export/dump/`。索引は Apache の自動生成一覧で、ページ冒頭に「The "last modified" timestamp is in Central European Time.」とある。
- 毎日作り直される。今日見た時点で主要ファイルの `Last-Modified` は 2026-09-30 01:50 から 02:05 GMT に集中していた。前日分の差分ファイル `modifications-2026-09-29.txt` と `deletes-2026-09-29.txt` も置いてある。
- ここのデータセットではまだ使っていない。ライセンスが緩いので候補として記録する。

## ライセンス

ダンプ一式に同梱される `readme.txt` の冒頭。

> This work is licensed under a Creative Commons Attribution 4.0 License,
> see https://creativecommons.org/licenses/by/4.0/
> The Data is provided "as is" without warranty or any representation of accuracy, timeliness or completeness.

サイトのフッター (トップページ、about ページとも同じ文言、リンク先は `https://creativecommons.org/licenses/by/4.0/`)。

> This work is licensed under a Creative Commons Attribution 4.0 License.

`https://www.geonames.org/export/` の Terms and Conditions。こちらは版番号を書いていない。

> free: GeoNames data is free, the data is available without costs.
> cc-by licence (creative commons attribution license). You should give credit to GeoNames when using data or web services with a link or another reference to GeoNames.
> commercial usage is allowed
> 'as is': The data is provided "as is" without warranty or any representation of accuracy, timeliness or completeness.

読み取れること。

- 名指しされているのは Creative Commons Attribution、版は 4.0。readme.txt とフッターが 4.0 と書き、リンク先も `licenses/by/4.0/`。ShareAlike も NonCommercial も NoDerivatives も付いていない。
- 表示は必要。Terms and Conditions が「You should give credit to GeoNames when using data or web services with a link or another reference to GeoNames」と書いている。リンクか、それ以外の参照でよい。
- 商用利用は可。Terms and Conditions に「commercial usage is allowed」とある。
- 無保証。3 か所すべてが「as is」と断っている。
- ウェブサービスも同じ cc-by だが、別に利用制限が付く。Terms and Conditions は「10,000 credits daily limit per application (identified by the parameter 'username'), the hourly limit is 1000 credits」と書き、超えると例外が返るとしている。SLA は premium web services だけの話としている。
- 有料の Premium Data (`https://www.geonames.org/products/premium-data.html`) は年 840 ユーロの購読。ページには「The premium data is available in tabulator separated flat files and in RDF format. The files have the same format as the freely available files.」とあり、無料版と形式が同じで、追加ファイル (airports、bounding boxes、countrysubdivisions、dependencies、spot city relation、un-locode-geonameid) と品質検査と過去版の保管が付く。このページ自体にはライセンス条項の記載が無く、購読データの再配布条件が無料版と同じかどうかは読み取れなかった。未確認。

つまり [geoboundaries](../geoboundaries/README.md) のように国ごとにライセンスが割れているのではなく、配布物全体が 1 つのライセンスで覆われている。[wikidata](../wikidata/README.md) の構造化データ (CC0) よりは厳しく、表示義務がある。share-alike が無いので、ODbL のデータと混ぜる場合の面倒はこちら側からは発生しない。

## 大きさ

HEAD が返した正確なバイト数。

| ファイル | バイト数 | Last-Modified (GMT) | 行数 |
|---|---:|---|---:|
| allCountries.zip | 422,001,054 | 2026-09-30 01:59:42 | 未計測 (落としていない) |
| alternateNamesV2.zip | 204,801,624 | 2026-09-30 02:04:39 | 未計測 |
| alternateNames.zip | 202,851,111 | 2026-09-30 02:01:47 | 未計測 |
| cities500.zip | 13,862,679 | 2026-09-30 01:59:42 | 未計測 |
| cities1000.zip | 11,052,449 | 2026-09-30 01:59:42 | 未計測 |
| cities5000.zip | 5,707,770 | 2026-09-30 01:59:42 | 未計測 |
| cities15000.zip | 3,359,659 | 2026-09-30 01:59:42 | 34,152 |
| JP.zip | 4,959,038 | 2026-09-30 01:55:59 | 103,760 |
| alternatenames/JP.zip | 3,759,281 | 2026-09-30 02:03:30 | 341,777 |
| admin1CodesASCII.txt | 151,583 | 2026-09-30 01:59:42 | 3,865 |
| admin2Codes.txt | 2,375,171 | 2026-09-30 01:59:42 | 47,643 |
| featureCodes_en.txt | 58,642 | (未取得) | 685 |
| countryInfo.txt | 31,678 | 2026-09-30 02:05:00 | 未計測 |
| iso-languagecodes.txt | 137,908 | 2026-09-30 01:50:31 | 未計測 |
| hierarchy.zip | 2,132,624 | 2026-09-30 02:04:47 | 未計測 |
| adminCode5.zip | 366,715 | 2026-09-30 01:59:42 | 未計測 |
| shapes_simplified_low.json.zip | 1,302,545 | 2026-09-30 02:04:59 | 未計測 |

- 索引に並ぶ国別 zip は 253 個。ほかに `no-country.zip` と、国別の別名を置く `alternatenames/` という下位ディレクトリが 1 つある。索引の項目数は全部で 288。
- `readme.txt` は `featureCodes.txt` があると書いているが、そのファイル名は 404 を返した。実在するのは言語別の `featureCodes_en.txt`、`featureCodes_bg.txt`、`featureCodes_nb.txt`、`featureCodes_nn.txt`、`featureCodes_no.txt`、`featureCodes_ru.txt`、`featureCodes_sv.txt` の 7 個。
- 統計ページの合計は 13,465,076 件、252 の国と地域。日本は 23 位で 103,760 件。この数は JP.zip を展開して数えた行数と一致した。
- about ページの記述は「over 25 million geographical names and consists of over 12 million unique features whereof 4.8 million populated places and 16 million alternate names」「one out of nine feature classes and further subcategorized into one out of 645 feature codes」。ただし `featureCodes_en.txt` の行数は 685 で、うち 1 行は `null`、残り 684 行が `クラス.コード` の形をしていた。about の 645 とは合わない。
- cities15000.txt は 34,152 行、244 の国と地域にまたがり、うち日本は 1,300 件。readme.txt は cities15000 を「ca 25.000」と書いているが実際は 34,152 件で、readme の概数は古い。

## スキーマ

`readme.txt` から。主表 `geoname` の列は次の 19 列、タブ区切りの UTF-8。

| # | 列 | 内容 (readme の記述) |
|---:|---|---|
| 1 | geonameid | integer id of record in geonames database |
| 2 | name | name of geographical point (utf8) varchar(200) |
| 3 | asciiname | name of geographical point in plain ascii characters, varchar(200) |
| 4 | alternatenames | alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000) |
| 5 | latitude | latitude in decimal degrees (wgs84) |
| 6 | longitude | longitude in decimal degrees (wgs84) |
| 7 | feature class | char(1) |
| 8 | feature code | varchar(10) |
| 9 | country code | ISO-3166 2-letter country code |
| 10 | cc2 | alternate country codes, comma separated |
| 11 | admin1 code | fipscode (subject to change to iso code), varchar(20) |
| 12 | admin2 code | code for the second administrative division, a county in the US, varchar(80) |
| 13 | admin3 code | varchar(20) |
| 14 | admin4 code | varchar(20) |
| 15 | population | bigint |
| 16 | elevation | in meters, integer |
| 17 | dem | digital elevation model, srtm3 or gtopo30 |
| 18 | timezone | the iana timezone id, varchar(40) |
| 19 | modification date | yyyy-MM-dd |

`alternate names` 表の列は 10 列。

| # | 列 | 内容 |
|---:|---|---|
| 1 | alternateNameId | the id of this alternate name |
| 2 | geonameid | geonameId referring to id in table 'geoname' |
| 3 | isolanguage | iso 639 の 2 文字か 3 文字。`zh-CN` のような国別変種、`zh-Hant` のような変種名も入る。ほかに `post` (郵便番号)、`iata`/`icao`/`faac` (空港)、`fr_1793` (フランス革命期の名)、`abbr` (略称)、`link` (ウェブサイト、多くは Wikipedia)、`wkdt` (Wikidata の id) |
| 4 | alternate name | varchar(400) |
| 5 | isPreferredName | '1', if this alternate name is an official/preferred name |
| 6 | isShortName | '1', if this is a short name like 'California' for 'State of California' |
| 7 | isColloquial | '1', if this alternate name is a colloquial or slang term. Example: 'Big Apple' for 'New York' |
| 8 | isHistoric | '1', if this alternate name is historic and was used in the past |
| 9 | from | from period when the name was used |
| 10 | to | to period when the name was used |

`alternateNames.zip` は旧版で、9 列目と 10 列目が無い。readme は「obsolete use V2」と書き、将来消すとしている。

feature class は 9 種類。readme の記述のまま。

| class | 内容 |
|---|---|
| A | country, state, region,... |
| H | stream, lake, ... |
| L | parks,area, ... |
| P | city, village,... |
| R | road, railroad |
| S | spot, building, farm |
| T | mountain,hill,rock,... |
| U | undersea |
| V | forest,heath,... |

feature code はその下位区分で、`featureCodes_en.txt` は `A.ADM1`、`first-order administrative division`、`a primary administrative division of a country, such as a state in the United States` のように、コード・短い名前・説明の 3 列。684 コードが 9 クラスに分かれていた (ほかに `null` の行が 1 つ)。

日本の 103,760 件の内訳。

| class | 件数 |
|---|---:|
| P (集落) | 50,801 |
| S (建物・施設) | 23,415 |
| T (山・地形) | 12,462 |
| H (水系) | 9,528 |
| A (行政区画) | 4,697 |
| L (地域・公園) | 1,911 |
| R (道路・鉄道) | 855 |
| V (森林) | 72 |
| U (海底地形) | 19 |

## 気をつけること

行政階層は 4 段 + 別ファイルの 5 段目。 主表の列は admin1 から admin4 まで。5 段目は `adminCode5.zip` に `geonameId, adm5code` として別置きになっている。readme は「the new adm5 column is not yet exported in the other files (in order to not break import scripts)」と説明している。日本では admin1 が 103,685 行、admin2 が 84,961 行、admin3 が 34,630 行で埋まっており、admin4 は 138 行しか無い。階層が深いほど空欄が増える。

admin1 の符号は FIPS なので、日本の県コードとは別物。 readme は「Most adm1 are FIPS codes. ISO codes are used for US, CH, BE and ME」と書いている。日本の admin1 コードを `admin1CodesASCII.txt` で見ると JP.01 が Aichi、JP.12 が Hokkaido、JP.40 が Tokyo、JP.47 が Okinawa で、ローマ字表記のアルファベット順に 01 から 47 が振られている。JIS や ISO 3166-2 の並び (北海道が先頭) とは一致しない。[geoboundaries](../geoboundaries/README.md) や国土数値情報と突き合わせるときは、この符号をそのまま鍵にできない。

日本の admin2 の中身は geonameId。 `admin2Codes.txt` の日本の行は `JP.13.1847945` のように 3 つ目が 7 桁の数字で、末尾の geonameId 列と同じ値だった。JP.txt でも admin2 列の 84,624 行が 7 桁の数字で、異なり数は 1,390。一方 admin3 列は 34,514 行が 5 桁で、京都市の行は `26102` という JIS の市区町村コードに見える値だった。つまり同じ「第 2 階層」という語でも、国によって符号の体系が違う。

行政階層の粒度が他の出典と揃わない。 日本の `feature code` が ADM2 の地物は 1,190 件、ADM3 は 1,101 件。[geoboundaries](../geoboundaries/README.md) の日本 ADM2 は 1,745 件、市区町村は 1,741。数が合わない。GeoNames の ADMx は行政の何段目かであって、他の出典の ADMx と同じ対象を指すとは限らない。歴史上の区画 (ADM2H が 214、ADM3H が 182、ADM4H が 682) も同じファイルに混ざっているので、現行の区画だけが欲しければ末尾 H を除く必要がある。

別名は公式・短縮・俗称・歴史を区別する。 列は isPreferredName、isShortName、isColloquial、isHistoric の 4 つで、それぞれ独立の旗。日本の別名 341,777 行で数えると、公式/優先 3,851、短縮 1,035、俗称 1,788、歴史 1,112。つまり 99% 以上はどの旗も立っていない、ただの表記違いということになる。「公式名」を取りたければ isPreferredName で絞る必要があり、絞ると激減する。

日本語の名前はある。ただし主表の name には無い。 JP.txt の name 列 103,760 件のうち、日本語の文字を含むものは 21 件だけで、103,738 件はラテン文字だけだった。日本語は別名側にある。日本の別名の言語別内訳は ja が 174,917 行で最多、次が言語コードの空欄 125,536、`link` 10,773、`wkdt` 8,003、en 3,157。ja の別名を持つ geonameId は 87,383 件。

日本語の別名は漢字とかなが混在する。 ja の 174,917 行を字種で分けると、漢字を含むものが 90,501、かなだけのものが 84,012、ラテン文字だけが 399。同じ地物に複数の表記が並ぶ。京都市 (geonameId 1857910) の ja 別名は `京都市` (isPreferredName=1)、`Kyōto-shi`、`きょうとし`、`京都`、`キョウト` の 5 つで、漢字・ひらがな・カタカナ・ローマ字がすべて ja として入っている。読み仮名と表記を区別する列は無いので、字種で自分で分けることになる。

Wikidata へつなぐ鍵が別名表に入っている。 isolanguage が `wkdt` の行の値が Wikidata の Q id (`Q31685451` など)。日本では 8,001 件の geonameId に付いていた。JP.txt 全体の 103,760 件に対して 8% 弱なので、[wikidata](../wikidata/README.md) 側と結合できるのは一部だけ。isolanguage が `link` の行 (日本で 10,773) は Wikipedia の URL で、こちらはパーセント符号化の違う同じ記事が重複して入っていることがある。

feature code の一覧の数が公称と合わない。 about ページは 645 コードと書くが `featureCodes_en.txt` は 684 コードだった。readme が挙げる `featureCodes.txt` に至ってはファイルが無い。ドキュメントの数字と実ファイルが食い違うので、コード体系は必ず実ファイル側を見る。

毎日置き換わる。 URL は固定で中身が差し替わる。版番号もチェックサムも索引に無い。再現性が要るなら落とした日の `Last-Modified` とバイト数を記録する。日次で追随するなら `modifications-<date>.txt` と `deletes-<date>.txt`、別名は `alternateNamesModifications-<date>.txt` と `alternateNamesDeletes-<date>.txt` が使える。

境界は簡略版しかない。 readme が挙げる `shapes_simplified_low` と `shapes_simplified_low.json` は国の境界の簡略形で、zip で 1,302,545 バイトしかない。面が要るなら [geoboundaries](../geoboundaries/README.md) や国土数値情報を使う。GeoNames は点の辞書として扱う。

## 取り出し方

split。国ごとに zip が分かれていて、必要な国だけ引ける。全世界が要るときだけ whole の `allCountries.zip` になる。2026-09-30 に実測した。

分割の単位は国で、索引ページ `https://download.geonames.org/export/dump/` から `XX.zip` の形の項目を数えると 253 個あった。別名も同じ単位で `alternatenames/XX.zip` に分かれている。索引は Apache の自動生成一覧なので、bbox でも日時でも絞れない。国コードで選ぶだけ。

| 要求した URL | 応答 | 大きさ | Range 要求 |
|---|---|---:|---|
| `.../export/dump/JP.zip` | 200、`Accept-Ranges: bytes` | 4,959,038 | 206 と 1,024 バイト |
| `.../export/dump/allCountries.zip` | 200、`Accept-Ranges: bytes` | 422,001,054 | 206 と 1,024 バイト |

どちらも Range 要求は通るが、中身を選ぶことはできない。JP.zip の先頭 256 バイトは `PK\x03\x04` に続いて最初のエントリ `readme.txt` で、zip の目録は末尾にある。しかも中身は deflate されたタブ区切りテキストで、行や地域の索引を持たない。部分読みでできるのはヘッダの確認までで、地物を取り出すには 1 国分を丸ごと展開することになる。

日本は 4.96MB、全世界は 422MB。国単位なら十分小さい。全世界が要る場合は whole として扱う。

毎日同じ URL の中身が差し替わるので、版を固定して引く手段は無い。落とした日の `Last-Modified` とバイト数を控えるしかない。

## z.yuiseki.net のスナップショット

上流は毎日同じ URL の中身を差し替え、過去の版は有料の購読でしか残らない。CC BY 4.0 なので、その日のダンプを元のまま残し、Parquet を添えて <https://z.yuiseki.net/static/geonames/> に日付ごとのディレクトリで置いた。取得スクリプトは [scripts/mirror_geonames.py](../../../scripts/mirror_geonames.py)、テストは [tests/test_mirror_geonames.py](../../../tests/test_mirror_geonames.py)。定期実行はしていない。取りたい日に手で流す。

- 置き場は yuisekin-z の `/www/html/static/geonames/` で、nginx がこれを `https://z.yuiseki.net/static/geonames/` として配る。
- ディレクトリ名は allCountries.zip の Last-Modified の UTC の日付。最初の 1 本は 2026-10-01 (Last-Modified は `Thu, 01 Oct 2026 02:08:51 GMT`)。
- 置いたのは allCountries.zip、alternateNamesV2.zip、hierarchy.zip、adminCode5.zip と小さい表 6 つ、readme.txt。国別の zip と cities は allCountries の部分集合なので置いていない。旧版の alternateNames.zip も置いていない。
- Parquet は `geoname/part-00〜03.parquet` (地名辞書、GeoParquet 1.0.0、`geometry` は点)、`alternate_names.parquet`、`hierarchy.parquet`、`admin_code5.parquet`。合わせて 1.3GB (raw を含む)。
- 地名辞書は country_code、geonameid の順に並べ、国の途中では切らずに 4 つに分けた。いちばん大きい part-01 で 178MB。どの国がどのファイルにあるかは manifest.json の `countries` にある。

| ファイル | 行数 | 国 |
|---|---:|---|
| geoname/part-00.parquet | 3,936,115 | 国コード無し (7,112 行) から FO まで |
| geoname/part-01.parquet | 3,987,139 | FR から NL まで (JP はここ) |
| geoname/part-02.parquet | 2,874,228 | NO から UM まで |
| geoname/part-03.parquet | 2,674,735 | US から ZW まで |
| alternate_names.parquet | 19,219,062 | |
| hierarchy.parquet | 519,183 | |
| admin_code5.parquet | 78,514 | |

地名辞書は合計 13,472,217 行で、allCountries.txt の行数と一致することを確かめてから置いた。統計ページの 13,465,076 件 (9-30 に読んだ値) とは 7,141 違う。

作るときに分かったこと:

- 型は readme.txt の列のとおり。ID、population、elevation、dem は整数、緯度経度は DOUBLE、modification_date は DATE、それ以外は文字列 (admin1_code の `01` のような先頭のゼロは残る)。整数の列は cast の前に正規表現で形を確かめる。DuckDB の cast は `'12.5'` を丸めて通してしまうため。
- 別名の 4 つの旗 (is_preferred_name など) は、元の `'1'` か空を真偽値にした。それ以外の値が来たら止まる。
- ファイルは引用符を使わないタブ区切りで、名前に `"` を含む行がある (2026-10-01 版で name 列の 623 行。例は `Schronisko "Nad Śnieżnymi Kotłami"`)。read_csv には `quote = ''` と `escape = ''` を渡している。
- alternateNamesV2.zip には iso-languagecodes.txt の写しも入っている。zip と同じ名前のファイルを取り出す。
- 配布元はとても遅い。2026-10-01 は 1 秒に 70〜140KB で、allCountries.zip だけで約 50 分かかった。途中で切れたら If-Range 付きの Range 要求で続きから取る。版が変わっていれば 200 で全体が返るので、混ざらない。取り終わったら全ファイルの Last-Modified をもう一度取り、取り始めと違えば止まる。

照合 (2026-10-01 版、上の「日本の名前」の節は 9-30 版で数えたもの):

- 日本は 103,761 件。9-30 は 103,760 件で、feature class の内訳は L が 1 件増えた (1,911 から 1,912) ほかは同じ。
- 日本の別名は 341,783 行 (9-30 は 341,777 行)。公式/優先 3,852、短縮 1,035、俗称 1,790、歴史 1,113。
- 京都市 (1857910) の ja の別名は `京都市` (is_preferred_name が真)、`Kyōto-shi`、`きょうとし`、`京都`、`キョウト` の 5 つで、上の節と同じ。
- 公開 URL への最初の Range 要求は 10 秒で切れ、そのあと 3 回は 206 だった (Cloudflare がキャッシュを埋める初回だけ遅い)。DuckDB の httpfs で part-01 から日本の件数を数えるのに 0.17 秒、2 回目は 0.06 秒。

## Hugging Face

<https://huggingface.co/datasets/yuiseki/geonames> に、夜ごとの版を年月なしの名前で置いた。サブセットは `20261001.geoname`、`20261001.alternate_names`、`20261001.hierarchy`、`20261001.admin_code5` の 4 つ。次の夜を取ったら横に足す。コードは <https://github.com/yuiseki/geonames>。

- 20261001 は、z.yuiseki.net の 2026-10-01 の置き場の raw/ を、manifest の sha256 と照合して取り込んだもの (`01_download.py --from`)。
- Parquet は作り直した。行数は z と同じで、バイト列は並列書き込みのため違う。ブルームフィルタは無し。
- 日本の ja の別名は、2026-10-01 の版の地名辞書と結んで数えると 174,920 行 (上の節の 174,917 行は、9-30 の版を国別の alternatenames/JP.zip で数えた値)。
- カードの SQL (京都市の日本語の別名) は、HF から 12 秒で返った。
