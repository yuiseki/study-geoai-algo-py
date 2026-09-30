# Protected Planet (WDPA)

2026-09-30 に読んで確かめた内容。数値は当日 curl で取った `https://www.protectedplanet.net/` の各ページと、当日ダウンロードした Sep2026 版の CSV 配布物、および UNEP-WCMC の ArcGIS FeatureServer への問い合わせから。ライセンスの引用は当日取得した `https://www.protectedplanet.net/en/legal` の本文そのまま。

まだこのカタログのどのデータセットにも使っていない。候補として調べたもの。

## 結論を先に

再配布は禁止されている。 派生物に含めての再配布も、事前の書面許可なしにはできない。商用利用も同じく禁止で、商用の定義はかなり広い。よってこのデータを材料にしてオープンなデータセットを作って公開することはできない。ダウンロード自体にログインもフォームも要らず自動化は容易だが、使えるのは手元の解析までで、成果物として配れるのは「ダウンロードできない形」の図や集計に限られる。

## 何なのか

- `https://www.protectedplanet.net/`。UNEP-WCMC (国連環境計画 世界自然保全モニタリングセンター) と IUCN (国際自然保護連合) が運営する、世界の保護区のデータベースの配布口。
- 中身は 2 つ。WDPA (World Database on Protected Areas、世界の保護地域データベース) と WD-OECM (World Database on Other Effective area-based Conservation Measures、保護区ではないが結果として保全に効いている区域のデータベース)。ほかに GD-PAME という管理有効性評価のデータベースもある。
- 各国政府、NGO、土地所有者、コミュニティからの提出を UNEP-WCMC が集約したもの。トップページの説明は「Protected Planet is the most up to date and complete source of data on protected areas and other effective area-based conservation measures (OECMs), updated monthly with submissions from governments, non-governmental organizations, landowners and communities.」
- 用途としては、国立公園や自然保護区のポリゴンが世界中ぶんまとまって手に入る唯一に近い場所。ある地点が保護区の中かどうか、ある地域の何割が保護されているか、といった問いに答えるための層。
- API のページによると、2025-11-01 に WDPA と WD-OECM は 1 つのデータベースに統合された。属性名も変わっており、実際 Sep2026 の CSV の列は `SITE_ID` / `SITE_PID` / `SITE_TYPE` / `TYPE` で、古い資料にある `WDPAID` / `WDPA_PID` / `GEOMETRY_TYPE` / `MARINE` は無かった。

## ライセンス (ここが本題)

`https://www.protectedplanet.net/en/legal` が唯一の条件。標準的なオープンライセンスではなく、UNEP-WCMC が一方的に定める利用規約である。CC BY でも ODbL でもない。

冒頭。

> Access to Data and any other content within the World Database on Protected and Conserved Areas (the "WDPCA Materials") and the Global Database on Protected Area Management Effectiveness (the "GD-PAME Materials") as made available through the ProtectedPlanet.net website is provided on the understanding that you read and consent to be bound to the Terms and Conditions set out below.

> PLEASE READ THESE TERMS AND CONDITIONS CAREFULLY. IF YOU DO NOT AGREE TO ANY OF THE TERMS AND CONDITIONS DO NOT DOWNLOAD. BY DOWNLOADING THE WDPCA AND GD-PAME MATERIALS MADE AVAILABLE ON PROTECTEDPLANET.NET YOU ACCEPT AND AGREE TO COMPLY WITH THE TERMS AND CONDITIONS BELOW.

### 商用利用は禁止

節の見出しがそのまま「No Commercial Use」。

> Neither (a) the WDPCA Materials and the GD-PAME Materials nor (b) any work derived from or based upon the WDPCA Materials and the GD-PAME Materials ("Derivative Works") may be put to Commercial Use without the prior written permission of UNEP-WCMC. For the purposes of these Terms and Conditions, "Commercial Use" means a) any use by, on behalf of, or to inform or assist the activities of, a commercial entity (an entity that operates 'for profit') or b) use by any individual or non-profit entity for the purposes of revenue generation. For commercial uses, please go to the IBAT website: https://www.ibat-alliance.org/.

> For the avoidance of doubt, UNEP-WCMC reserves the right to determine whether a particular use of the WDPCA and GD-PAME Materials constitutes a Commercial Use or otherwise.

「営利企業による利用」だけでなく「営利企業の活動に情報を与える、または助ける利用」まで含む。さらに何が商用に当たるかの判定権は UNEP-WCMC が留保している。判断がこちら側に無い。

ダウンロードのモーダルにも同じ趣旨の文が埋め込まれていた (当日取得した HTML の `download-button` の属性)。

> Meaning any use by or for a commercial entity, whether revenue-generating or not, or any use that generates revenue for any type of entity.

### 再配布は禁止

節の見出しは「No Sub-licensing or Redistribution of WDPCA and GD-PAME Data」。

> The WDPCA and GD-PAME Materials may not be sub-licensed in whole or in part including within Derivative Works without the prior written permission of UNEP-WCMC. You may not redistribute the WDPCA and GD-PAME Data contained in the WDPCA and GD-PAME in whole or in part by any means including (but not limited to) electronic formats such as web downloads, through web services, through interactive web maps (including mobile applications) that grant users download access, KML Files or through file transfer protocols. If you know of others who wish to use the WDPCA and GD-PAME Data please refer them to ProtectedPlanet.net.

全部でも一部でも、派生物に入れる形でも、事前の書面許可なしには再配布できない。禁止の例に web ダウンロード、web サービス、ダウンロード可能な地図アプリ、KML、FTP が明示されている。

公開してよい形は次の節に限定されている。

> You may publish the WDPCA and GD-PAME Materials in whole or in part, including on-line, providing (a) the WDPCA and GD-PAME Data are not downloadable and (b) the proper attribution is clearly visible (see 'Attribution' below). You must ensure that the most recently available version of the WDPCA and GD-PAME Materials are being used and that the month and year of release is visible in the published version.

つまり「見せるのは可、取れるようにするのは不可」。加えて最新版を使うこと、版の年月を表示に出すことが条件に入っている。同じ節は刊行物 2 部の提出まで要求している。

> We require two free copies of all published materials to be provided to UNEP-WCMC.

### 権利は与えられない

> No rights in the WDPCA and GD-PAME Materials are granted to you by virtue of these Terms and Conditions or as a result of any use by you of the WDPCA and GD-PAME Materials. Neither UN Environment Programme nor IUCN assert any intellectual property rights in the data that is made available by third party data providers for inclusion in the WDPCA and GD-PAME. However, all intellectual property rights in the database itself are the property of UN Environment Programme and IUCN.

個々の提供元データについて UNEP-WCMC と IUCN は権利を主張しないが、データベースそのものの権利は両者が持つ、という構造。前半だけを読んで「元データは自由」と受け取らないこと。上の再配布禁止はデータベースの側から掛かっている。

### 引用の書き方 (規約で必須)

> UNEP-WCMC and IUCN (year), Protected Planet: [insert name of component database; The World Database on Protected and Conserved Areas (WDPCA)/The Global Database on Protected Areas Management Effectiveness (GD-PAME)] [On-line], [insert month/year of the version downloaded], Cambridge, UK: UNEP-WCMC and IUCN. Available at: www.protectedplanet.net.

サイトが埋め込んでいる当日の実物はこう。

> UNEP-WCMC and IUCN (2026), Protected Planet: The World Database on Protected Areas (WDPA) [Online], September 2026, Cambridge, UK: UNEP-WCMC and IUCN. Available at: www.protectedplanet.net.

FeatureServer の `copyrightText` には DOI も入っていた: `https://doi.org/10.34892/6fwd-af11`。

### 国ごとに別の条件が乗ることがある

配布物に同梱されている `WDPA_sources_Sep2026.csv` は 387 件の出典表で、`DISCLAIMER` 列を持つ。当日数えたところ 387 件中 18 件が `Not Reported` 以外の文言を入れていた。その中には UNEP-WCMC の規約とは独立に、追加の制限を課すものがある。

- ウクライナの保護区 (METADATAID 367): 「No commercial use of dataset is allowed unless written permission of authors provided.」
- アンギラの保護区 (METADATAID 1117): 「These data should not be distributed or used for any commercial purposes without due consent from the Government of Anguilla, Department of Natural Resources.」
- Natura 2000 (METADATAID 1832): 英国部分は JNCC の end user licence に個別に同意する必要がある、と書いてある。

日本の 28 件の出典はいずれも `DISCLAIMER` が `Not Reported` だった。例外は林野庁の「Rare Population Protected Forest of Japan」(METADATAID 2007) で、条件ではなく注記として「For conservation purposes, if the protected area name contains "species name", it is masked with "XXX"」とある。

なお WDPA のマニュアル (同梱 PDF) には、そもそも提供元が制限を付けたデータを UNEP-WCMC が受け入れうることが書かれている。

> UNEP-WCMC may accept data with restrictions. This includes data that is available for onward release but not for commercial use ... and data that is made available only to UNEP-WCMC, UN Environment and IUCN, and is not for onward release.

### 判断

- オープンデータではない。Open Definition の意味でも、再配布と商用利用の両方が事前書面許可を要する時点で当てはまらない。
- 派生オープンデータセットの材料にはできない。規約は「Derivative Works に含めた再配布」を名指しで禁じている。geoBoundaries や Natural Earth と同じ扱いにはできない。
- 手元での解析と、ダウンロードできない形での図・集計の公開はできる。ただし最新版を使うこと、版の年月を出すこと、規定の引用を出すことが条件。
- 規約は予告なく変わりうると本文に書いてある (「reserves the right to vary these Terms and Conditions from time to time without notice」)。ここに引いた文言も 2026-09-30 時点のもの。
- 曖昧さは UNEP-WCMC に有利に読まない。商用かどうかの判定権が先方にある以上、境界事例は先方の判断次第になる。

## ダウンロードにログインは要るか (実測)

要らない。認証もフォームも通らずに取れた。自動化の妨げにはならない。制約はライセンスのほうにしか無い。

サイトのダウンロードボタンは `POST /downloads` に JSON を投げ、返ってきた URL を開くだけの仕組みだった。当日、Cookie も認証ヘッダも無しで叩いた結果。

| 要求 | 応答 |
|---|---|
| `POST /downloads` `{"domain":"general","format":"csv","token":"wdpa"}` | 200、`{"id":"wdpa-csv","url":"https://d1gam3xoknrgr2.cloudfront.net/current/WDPA_Sep2026_Public_csv.zip", ...}` |
| `POST /downloads` `{"domain":"general","format":"shp","token":"JPN"}` | 200、`.../WDPA_WDOECM_Sep2026_Public_JPN_shp.zip` |
| `POST /downloads` `{"domain":"general","format":"gdb","token":"all"}` | 200、`.../WDPA_WDOECM_Sep2026_Public_all.zip` |
| `GET /downloads` | 500 (パラメータ無しでは動かない) |

返る URL は CloudFront の固定パスで、そこへの HEAD も GET もそのまま通る。当日の実測。

| ファイル | Content-Length | Last-Modified |
|---|---:|---|
| `current/WDPA_Sep2026_Public_csv.zip` | 23,820,193 | 2026-09-01 06:49 GMT |
| `current/WDPA_Sep2026_Public.zip` (File Geodatabase) | 1,753,365,806 | 2026-09-01 06:51 GMT |
| `current/WDPA_Sep2026_Public_shp.zip` | 4,171,199,249 | 2026-09-01 07:09 GMT |
| `current/WDOECM_Sep2026_Public.zip` | 58,102,576 | 2026-09-01 18:18 GMT |
| `current/WDPA_WDOECM_Sep2026_Public_all.zip` | 1,800,238,364 | 2026-09-19 18:09 GMT |
| `current/WDPA_WDOECM_Sep2026_Public_JPN_shp.zip` | 172,922,591 | 2026-09-02 13:28 GMT |
| `current/WDPA_WDOECM_Sep2026_Public_JPN_csv.zip` | 11,558,680 | 2026-09-08 07:30 GMT |

ダウンロードのモーダルは商用か非商用かを選ばせるが、これは画面上の分岐にすぎず、サーバ側で何かを検証してはいない。規約への同意は「ダウンロードした時点で同意したことになる」という形で、同意の記録は取られていない。技術的に止められていないことと、許諾されていることは別である。

### API は鍵が要る

- `https://api.protectedplanet.net/v3/protected_areas?per_page=1` は 401、`{"error":"Unauthorized. Invalid or expired token."}`。
- `https://api.protectedplanet.net/v4/sites?per_page=1` は 404 (パスが違う可能性がある。v4 の正しい経路は未確認)。
- API のトップページは鍵の申請を求め、さらに「The API is not available for commercial use.」と書いている。
- v3 は 2026-05-01 に停止予定と書いてあるが、当日 401 を返したので稼働はしている。停止の実施状況は未確認。

### ArcGIS の FeatureServer は鍵なしで問い合わせできた

`https://data-gis.unep-wcmc.org/server/rest/services/ProtectedSites/The_World_Database_of_Protected_Areas/FeatureServer`。ダウンロードページに「ESRI Web Service」として載っている。当日、認証なしで件数問い合わせが通った。

| レイヤ | 形状 | `where=1=1` の件数 |
|---|---|---:|
| 0 `WDPA_point_latest` | esriGeometryMultipoint | 7,747 |
| 1 `WDPA_poly_latest` | esriGeometryPolygon | 307,019 |

`ISO3='JPN'` でのポリゴン件数は 6,913。いずれも下の CSV の集計と完全に一致した。

## 中身 (Sep2026 版の CSV を実際に数えた)

`WDPA_Sep2026_Public_csv.zip` を展開すると `WDPA_Sep2026_Public_csv.csv` (152,242,086 バイト)、出典表 `WDPA_sources_Sep2026.csv` (120,414 バイト)、英西仏露アラビア語のマニュアルとメタデータの PDF が入っている。

保護区 (WDPA) 側。

- 行数 314,766。`SITE_PID` は 314,766 で全部異なり、`SITE_ID` は 312,943。つまり 1 つのサイトが複数の部分に分かれている行がある。トップページが掲げる「312,943 Protected Areas」は `SITE_ID` のほうと一致する。
- 形状の別は `TYPE` 列。ポリゴン 307,019、ポイント 7,747。ポイントが 2.5% にあたる。
- 指定の階層 `DESIG_TYPE`: National 278,598、Regional 32,535、International 3,371、Not Applicable 262。
- ISO3 の値は 244 種類 (複数国にまたがるものは `;` 区切りなので分解して数えた)。

OECM (WD-OECM) 側は別ファイル `WDOECM_Sep2026_Public_csv.zip` (11,492,352 バイト)。

- 行数 7,699、`SITE_ID` で 7,663。トップページの「7,663 OECMs」と一致する。
- ポリゴン 7,554、ポイント 145。
- 国は 18 しか無い。多い順に SWE 5,411、UKR 639、CAN 507、JPN 446、MAR 338、PHL 178、COL 67、ABNJ 38。OECM はまだ報告している国が偏っている。

トップページが当日掲げていた全球の数値 (Statistics updated: Sep 2026)。

| 指標 | 値 |
|---|---|
| 陸域と内水面の保護区被覆 | 17.36% |
| 海域の保護区被覆 | 9.81% |
| 陸域と内水面の保護区 + OECM 被覆 | 18.45% |
| 海域の保護区 + OECM 被覆 | 10.03% |

### IUCN 管理カテゴリ

`IUCN_CAT` 列。同梱マニュアル (WDPA_WDOECM_Manual_1_6.pdf) によれば、値は提供元が申告するもので、1 つの値しか入らない。Ia から VI までの 6 段階 7 種類に加えて、3 つの非値がある。

- `Not Reported`: カテゴリが不明、または提供元が情報を出していない。
- `Not Applicable`: 指定の種類としてカテゴリが適用されないもの。マニュアルによると WDPA では世界遺産と UNESCO MAB 生物圏保存地域だけ。OECM のデータベースではこれが唯一の許容値。
- `Not Assigned`: 提供元が IUCN のカテゴリ制度を使わないことを選んだもの。

全球の内訳 (314,766 行)。

| カテゴリ | 件数 |
|---|---:|
| IV | 95,696 |
| Not Reported | 55,044 |
| V | 52,716 |
| Not Assigned | 43,007 |
| Ia | 23,368 |
| III | 22,412 |
| VI | 10,072 |
| II | 7,260 |
| Ib | 4,328 |
| Not Applicable | 863 |

カテゴリが実質的に入っていない行 (Not Reported、Not Assigned、Not Applicable の合計) が 98,914 で、全体の 31% にあたる。カテゴリで絞る解析をすると、この 3 割が黙って落ちる。

### 更新頻度

マニュアルの 4.3 節。

> A new version of the WDPA is released every month and made available through the Protected Planet webpage (http://www.protectedplanet.net). ... Each monthly release is accompanied by a dedicated webpage listing the countries or territories that have been updated, and the number of records added, removed or updated.

メタデータの Maintenance 欄も「Data are updated on a monthly basis.」。ファイル名に `Sep2026` のように年月が入り、URL のパスは `current/` 固定。過去版の URL は未確認。

### 日本 (ISO3 = JPN)

- 保護区 6,954 件。うちポリゴン 6,913、ポイント 41。国のページの「Polygons 99% / Points 1%」と合う。
- OECM 446 件。
- 国のページによると、国内指定だけに絞ると 6,887 件、管理有効性評価があるのは 5 件。
- IUCN カテゴリは IV が 4,463 (64.18%)、V が 2,213 (31.82%)、VI 100、III 46、Ib 45、Not Reported 36、II 32、Not Applicable 14、Ia 5。日本は IV と V に極端に偏っている。
- 指定の種類で多いもの: 都道府県の鳥獣保護区 3,630、特別緑地保全地区 643、都道府県自然環境保全地域 545、希少個体群保護林 530、都道府県立自然公園 310。
- ガバナンスは Sub-national ministry or agency が 5,950 (85.56%)、Federal or national ministry or agency が 937 (13.47%)。
- 国のページが出す公式の被覆率は、陸域と内水面が 110,715 km2 / 372,246 km2 = 29.74%、海域が 560,806 km2 / 4,066,374 km2 = 13.79%。OECM を足すと陸域 111,324 km2 = 29.91%。
- 出典は 28 件で、環境省、林野庁、水産庁、国土交通省、文部科学省、都道府県。`YEAR` は 2014 から 2024、`UPDATE_YR` は 2021 から 2026。

## 気をつけること

ポイントは境界が無いという意味。 マニュアルによれば、提供元が境界を出せなかったサイトは緯度経度 1 点として入る。ポリゴンとポイントは別のフィーチャクラスとして保持される。さらに「その点が中心とは限らない」と明記されている。

> The central point of each protected area is usually requested but this is not always possible, so users should not assume that all points in the WDPA or OECM database represent the central point of a given protected area or OECM.

マニュアルはポイントの扱いを解析結果を左右する判断として扱えと言っている。除けば保護面積を過小に見積もり、報告面積でバッファを切って含めれば総量は保つが位置が不確かになる、という整理。日本はポイントが 41 件しかないので影響は小さいが、国によっては全部がポイントということもありうる (国別の内訳は未確認)。

件数をそのまま数えると重複する。 同じ場所が国立公園であり世界遺産でありラムサール条約湿地であることがあり、WDPA はそれぞれを別のレコードとして持つ。国のページにも注意書きが出ていた。

> Some geographic locations are designated more than once, e.g., as both a National Park (a national designation) and a World Heritage Site (an international designation). In the WDPA, these designations are counted as separate protected areas, meaning this number might appear higher than expected.

マニュアルの推奨は、被覆率を出すなら必ず重ね合わせを解消した平坦な層を作れ、というもの。

> When calculating coverage statistics using the WDPA or OECM database it is important to create a 'flat' layer which contains no overlaps to ensure that there is no double counting of protection. This can be done using a variety of GIS software tools. ... During the dissolve process, attribute information will be lost.

実際に日本で確かめた。`GIS_AREA` から `GIS_M_AREA` を引いた陸域ぶんを 6,954 行そのまま合計すると 115,232 km2 になるが、公式の値は 110,715 km2。単純合計は 4% 多い。海域ぶんの単純合計は 359,902 km2 で、公式の 560,806 km2 とは逆に大きく下回る (どの範囲を海域として数えるかの定義が違うと読めるが、確かめていない)。どちらにせよ、行を足し上げた数字は公式の被覆率と一致しない。

保護区と OECM も重なりうる。 マニュアルによれば本来は重ならないはずだが、実際には重なる場合があり、UNEP-WCMC が統計を出すときは重なった部分を保護区としてのみ数えている。2 つのデータベースを単純に結合して面積を足すと二重に数えることになる。

版を跨いで比べない。 規約は「古い版を使うな」と明示している。

> Unless required to do so for specific analyses, you should not use any version of the WDPA and GD-PAME Materials after it has been superseded by a subsequent version. It is your responsibility to check if an update of the WDPA and GD-PAME Materials is available.

毎月変わるうえ、レコードは追加だけでなく削除もされる。学習に使うなら取得した年月を必ず記録する。URL は `current/` 固定なので、ファイル名の年月だけが版の手掛かりになる。

配布物の年月が揃っていない。 FeatureServer の `copyrightText` は当日「[August 2026]」と書いていたが、件数は Sep2026 の CSV と完全に一致した。文字列のほうが更新から取り残されていると読める。表示された年月をそのまま版として記録すると 1 か月ずれる。

列の名前が 2025-11 に変わった。 `WDPAID` や `GEOMETRY_TYPE` を前提に書かれたコードや解説は、Sep2026 の配布物では動かない。統合の変更点一覧として `https://wcmc.io/WDPA_changes_2025` が案内されているが、内容は未確認。

Take-down 方針がある。 規約に、著作権その他の申し立てがあればデータセットの当該部分を速やかに取り下げる、と書いてある。特定のレコードが将来消えることがありうる。

## 確かめられなかったこと

- 過去版の入手経路。`current/` 以外のパスは試していない。
- 国ごとのポイント比率の一覧。日本 (41/6,954) と全球 (7,747/314,766) しか数えていない。
- v4 API の正しい経路と、v3 が実際に停止するかどうか。
- `https://wcmc.io/WDPA_changes_2025` の中身。
- 書面許可を求めた場合に何が認められるか。規約は `protectedareas@unep-wcmc.org` への連絡を指示しているが、実際の運用は分からない。

## 学習ステップでの使いどころ (案、ただし再配布不可を前提に)

- 点が保護区の中かどうかを判定する二値の特徴量を作る。1 線形回帰から 3 XGBoost までの説明変数として素直。
- 4 Cross Validation: 保護区は空間的に強く固まるので、ランダム分割と空間ブロック分割で評価が変わる題材になる。
- 9 facility location: 保護区を避ける制約として使う。
- 成果として出せるのは図と集計まで。ポリゴンそのものを含む成果物は公開できない。

## 取り出し方

split。ただしこの判定は技術的な話であって、取ってよいかどうかとは別である。上の「ライセンス」の節が先に効く。

- 配布は月ごとの全球 1 式と、国別・サイト別の分割。CloudFront の直 URL が認証なしで通り、`POST https://www.protectedplanet.net/downloads` に JSON を投げると直 URL が返る。
- UNEP-WCMC の ArcGIS FeatureServer は無認証でクエリでき、bbox や属性で絞れるので catalog に近い使い方もできる。ポイント 7,747 / ポリゴン 307,019 / 日本のポリゴン 6,913 を返し、CSV の集計と一致した。
- 公式 API (`/v3/...`) は鍵が要る。鍵なしでは 401 `Unauthorized. Invalid or expired token.`。

技術的な障壁はほぼ無い。制約はライセンスだけにある。
