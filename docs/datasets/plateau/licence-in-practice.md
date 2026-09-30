# PLATEAU のライセンスが実際にどう扱われているか

2026-09-30 に読んで確かめた内容。国土交通省のサイトポリシーと FAQ、G空間情報センター CKAN の API、OpenStreetMap wiki と talk-ja / imports メーリングリストのアーカイブ、GitHub の検索 API と各リポジトリの README、Source Cooperative、Hugging Face の API、Internet Archive の CDX API と各スナップショットを、curl と gh コマンドで直接取得して確認した。以下は原文の引用とその出どころを軸に、誰が何を言っているのかを（a）国土交通省の言明、（b）コミュニティの合意プロセスが決めたこと、（c）個々のプロジェクトが自分で名乗っていること、の三つに分けて記述する。この三つは重みが違う。

## 1. 国土交通省が言っていること

### 1.1 サイトポリシー第3節（現行）

https://www.mlit.go.jp/plateau/site-policy/

> 当ウェブサイトで公開している情報（「G空間情報センター」にて公開している3D都市モデルのオープンデータを含む。以下「コンテンツ」といいます。）の著作権は、特記されていない限り国土交通省に帰属し（なお、「G空間情報センター」にて公開している3D都市モデルのオープンデータの著作権は、各地方公共団体に帰属）、権利表記の記載がない限り「公共データ利用規約（第1.0版）」（PDL1.0）に準拠した利用条件の下で、利用することができます。

> （３）その他
> 本利用ルールは、クリエイティブ・コモンズ・ライセンスの表示4.0 国際ライセンス（以下「CC BY」）と互換性があります。国土交通省都市局国際・デジタル政策課は、本利用ルールが適用されるコンテンツについて、利用者がCC BYに従って利用することを許諾します。また、利用者がOpen Data CommonsによるODC BY又はODbLでの利用を希望する場合に、それを妨げるものではありません。

CC BY については「許諾します」という能動的な許諾であり、ODC BY と ODbL については「妨げるものではありません」という不作為の表明である。文言のレベルが違う。後述するとおり、OSM 側の実務はこの後者の一文にぶら下がっている。

### 1.2 FAQ はサイトポリシーより強い言い方をしている

https://www.mlit.go.jp/plateau/faq/

> Q 3D都市モデルのデータには何らかの権利が存在しますか。
> A PLATEAUが提供する3D都市モデルの著作権はすべて地方公共団体に帰属していますが、これを公共データ利用規約（第1.0版）、CC BY4.0、ODC BY、ODbLの各種オープンライセンスに基づきオープンデータとして提供しています。
> このため、3D都市モデルはどなたでも商用利用も含めて無料で自由にご利用いただけます。詳細はPLATEAU Policyをご覧ください。

FAQ は ODbL を「妨げない」ではなく「各種オープンライセンスに基づきオープンデータとして提供しています」と書いている。つまり国土交通省自身が、少なくとも FAQ のレベルでは多重ライセンスとして説明している。サイトポリシーの慎重な文言と FAQ の断定的な文言が併存しており、両者は同じ強さではない。実務が依拠すべき正文はサイトポリシーのほうだが、FAQ の存在は「多重ライセンスと読んでよい」という解釈を国土交通省が黙認どころか自ら流布していることの証拠になる。

### 1.3 CKAN のメタデータは古い節見出しを指している

https://www.geospatial.jp/ckan/api/3/action/package_show?id=plateau-tokyo23ku-citygml-2020

```
license_id       = 'plateau'
license_title    = 'PLATEAU Site Policy 「３．著作権について」に拠る'
license_url      = 'https://www.mlit.go.jp/plateau/site-policy/'
isopen           = True
restriction      = '利用規約による'
license_agreement = 'Project PLATEAUのサイトポリシーに従って、どなたでも、複製、公衆送信、翻訳・変形等の翻案等、自由に利用できます。商用利用も可能です。（https://www.mlit.go.jp/plateau/site-policy/）'
```

license_title が指す「３．著作権について」という節は、現行のサイトポリシーには存在しない。現行の第3節の見出しは「コンテンツの利用」である。同じ古い見出しは PLATEAU 公式の学習コンテンツにも残っている。

https://www.mlit.go.jp/plateau/learning/tpc03-1/

> G空間情報センターで公開されているPLATEAUの3D都市モデルは商用利用も含め、無償で利用できます。PLATEAUのライセンス情報については、サイトポリシー（ ）の 「３．著作権について」を参照してください。

CKAN の license_title は文字列として固定されており、サイトポリシーの改訂に追随していない。ライセンスの実体はリンク先の現行文であって、CKAN の文言ではない。CKAN 側だけを機械的に読む実装は、存在しない節を参照し続けることになる。

### 1.4 例外パッケージは license_id も違う

https://www.geospatial.jp/ckan/api/3/action/package_show?id=plateau-27999-osaka-shi-2025

```
license_id       = 'ol'
license_title    = '独自利用規約'
isopen           = True
license_agreement = '国土交通省都市局が作成した「2025年大阪・関西万博　3D都市モデル（Project PLATEAU）」データには、博覧会協会その他第三者が保有する著作権・商標などの知的財産が含まれています。 商業目的、販売促進、広告利用、商品化などの営利目的での使用は一切認められていません。'
```

既存の整理では「license_id 'plateau' を持ちつつ商用利用を禁ずるパッケージ」として記録されていたが、実際にはこのパッケージの license_id は 'plateau' ではなく 'ol'（独自利用規約）である。一方で isopen は True のままで、営利利用の全面禁止と両立していない。CKAN のフラグは法的な判断の代わりにならない。

## 2. コミュニティのプロセスが決めたこと

### 2.1 ODbL で使えるという読みは 2022 年 4 月の talk-ja で確定した

疑義を出したのは Kentaro Hatori（はとちゃん）である。

https://lists.openstreetmap.org/pipermail/talk-ja/2022-April/011126.html

> ・Plateauの利用規約について、政府標準利用規約（第2.0版）やCC Byに準拠であることは確認できました。
> ・利用者がOpen Data CommonsによるODC BYまたは ODbLでの利用を妨げるものではないということで、CC ByとODbLの矛盾については、特別許可を得ることで解消すると思われます。
> ・Plateusの説明では「測量」と明記されていますが、そのことでOSMがこれまで地図ではなく絵図との取り扱いであったものが、測量法の対象とならないかが確認できませんでした。
> ・Plateauを作成した日付は確認できましたが、ベースとした測量データが何でいつ作成されたのかが確認できませんでした。地理情報は日々変わっているので測量した日付は重要なファクタと思います。

回答したのは Satoshi IIDA（nyampire）である。

https://lists.openstreetmap.org/pipermail/talk-ja/2022-April/011127.html

> -> いえ、この場合の「妨げるものではない」は、「そのライセンスを選択して適用しても良いよ」の意味なので、
> 私達がODbLを選択することで、特別許可を得る必要なく、ライセンス互換となります。

> -> 市町村によっては調査年のメタデータが公開されています。（45/56都市中）
> また、元データは「都市計画基礎調査（都市計画法により実施）」などを組み合わせたものであり、測量法の範疇外で行われています。
> ここに記載があります。
> https://www.chisou.go.jp/tiiki/toshisaisei/yuushikisya/20210803/DUPwg01_sankou1.pdf

この二往復が wiki のトークページに要約として転記され、コミュニティの結論として扱われている。

https://wiki.openstreetmap.org/wiki/JA_talk:MLIT_PLATEAU/imports_outline?action=raw

> ===ライセンス・測量法との関係について===
> : Plateauの利用規約について
> : 利用者がOpen Data CommonsによるODC BYまたは ODbLでの利用を妨げるものではないということで、CC ByとODbLの矛盾については、特別許可を得ることで解消すると思われます。（はとちゃん）
> :: いえ、この場合の「妨げるものではない」は、「そのライセンスを選択して適用しても良いよ」の意味なので、私達がODbLを選択することで、特別許可を得る必要なく、ライセンス互換となります。（いいだ）

重要なのは、この解釈が国土交通省に照会して得た回答ではなく、公開文書の文言をコミュニティ側で読んだ結果だという点である。wiki の「Link to permission (if required): NONE」は、許諾を取る必要がないという判断の記録であって、許諾が存在するという記録ではない。

### 2.2 アンケートで測られたのはライセンスではない

https://wiki.openstreetmap.org/wiki/JA_talk:MLIT_PLATEAU/imports_outline?action=raw

> 2022年5月8日、アンケートの実施を締め切りました。
> アンケート実施期間: 2022年4月24日〜5月8日
> 回答者数: 75
> アンケート呼びかけの実施: Talk-ja ML, Slack OSM Japan, Twitter, Facebook, osm.orgメッセージ機能(4月27日時点で、Japan地域上位100名程度に送付)

Q2「あなたは、Plateau建物データのインポートに賛成でしょうか、反対でしょうか」の有効回答は 72 で、賛成 33 票（45.8%）、どちらかといえば賛成 16 票（22.2%）、反対 1 票（1.4%）、どちらかといえば反対 0 票である。Q3 の形状置き換えについては積極的に賛成 32 票、どちらかといえば賛成 32 票、積極的に反対 1 票である。

設問はいずれも既存形状の置き換えの是非、マッパーのモチベーション、品質管理の手順についてであり、ライセンスの可否を問う設問は存在しない。imports ML への投稿で nyampire がアンケート結果を援用したときの表現は次のとおりである。

https://lists.openstreetmap.org/pipermail/imports/2022-August/006941.html

> Japanese community have discussed it already in the Talk-ja ML since April 2022.
> And had a questionary for mappers in the Japan region showed that approximately 70 per cent were 'in favour' and 'somewhat in favour' of this import.

70% という数字はインポートそのものへの賛否であって、ライセンス解釈への賛同ではない。

### 2.3 imports ML ではライセンスは一度も論点にならなかった

2022 年 8 月の imports メーリングリストのスレッドは 3 通で完結している（006941、006942、006943）。唯一の外部からの応答は Marc_marc によるもので、指摘はリンク切れ、英訳、ref タグ、addr:full の分解、タグ上書きの方針、チェンジセットの説明文についてである。

https://lists.openstreetmap.org/pipermail/imports/2022-August/006942.html

> in the Schedule section, "2022/04 questionnaire for Japanese Mapper. Result: here" seems to have a missing link
> it's greet that the script is opensource !

> Tag merge : I don't like the idea of automatically overwriting
> the values in osm with the values from the import.

ライセンスについての言及はない。つまり国際的なインポートレビューの場で PLATEAU のライセンスが精査された形跡はなく、異議が出なかったことをもって通過したという形である。OSM Foundation の Licensing Working Group による裁定を示す文書は見つけられなかった（未確認。lists.openstreetmap.org の legal-talk を横断検索する手段を持っておらず、wiki からのリンクも存在しないため、そもそも照会が行われたのかどうかを確かめられなかった）。

### 2.4 2023 年 9 月の再開アナウンス

https://lists.openstreetmap.org/pipermail/talk-ja/2023-September/011361.html

> 現状、手順としては概ね確立しており、初心者でも問題なく実施可能です。
> （というか、初心者や海外の方による野良インポートがいくつか行われており、都度リバートしています）

> 具体的には、作業をしたいと考えるかたが、
> このTalk-jaで（できればSlackにも追加で）、対象の市町村を宣言し、
> 一週間程度待って特に反対や意見がなければ実施するという形にしたいです。

この投稿もライセンスには触れていない。2022 年 4 月に固まった読みが、以後は再検討されずに前提として運用されている。

## 3. 個々のプロジェクトが自分で名乗っていること

以下はいずれも第三者が自分の判断で付けたライセンス表示であり、国土交通省が認定したものではない。

### 3.1 変換ツール本体はコードのライセンスしか持たない

yuuhayashi/citygml-osm は OSM wiki が公式の変換スクリプトとして指定しているものだが、README はほぼ wiki へのポインタのみで、LICENSE.txt は MIT ライセンスである。

https://raw.githubusercontent.com/yuuhayashi/citygml-osm/master/LICENSE.txt

> The MIT License (MIT)
> Copyright (c) 2021 Yuu Hayashi

出力データのライセンスについての記述はリポジトリ内に見当たらない。つまりデータ側の扱いは wiki のインポート outline に外部化されている。

### 3.2 派生データセットに CC BY 4.0 を付けている例

indigo-lab/plateau-tokyo23ku-building-mvt-2020 は、変換後のベクトルタイルそのものに CC BY 4.0 を宣言している。

https://raw.githubusercontent.com/indigo-lab/plateau-tokyo23ku-building-mvt-2020/main/README.md

> # ライセンス
>
> 本データセットは [CC-BY-4.0](LICENSE) で提供されます。
> 使用の際にはこのレポジトリへのリンクを提示してください。
>
> また、本データセットは [3D都市モデル（Project PLATEAU）東京都23区（CityGML 2020年度）](https://www.geospatial.jp/ckan/dataset/plateau-tokyo23ku-citygml-2020) を
> 加工して作成したものです。
> 本データセットの使用・加工にあたっては、[PLATEAU Policy](https://www.mlit.go.jp/plateau/site-policy/) を確認し、権利者の権利を侵害しないように留意してください。

同じ作者の indigo-lab/plateau-lod2-mvt は GitHub のリポジトリ設定として CC-BY-4.0 を宣言している（gh api repos/indigo-lab/plateau-lod2-mvt の license.spdx_id が CC-BY-4.0）。

### 3.3 Source Cooperative 上の再配布

Pacific Spatial Solutions の Flateau は、PLATEAU の建築物 LOD0 を GeoParquet と GeoPackage に変換して Source Cooperative で配布している。

https://source.coop/pacificspatial/flateau

> You can download and use our data freely under CC-BY 4.0 license. We used PLATEAU data so you also need to follow their term of use.
>
> (c) Pacific Spatial Solutions, inc. 2023 CC-BY. This data is made available under a Creative Commons Attribution 4.0 International license. Original building data are from PROJECT PLATEAU (https://www.mlit.go.jp/plateau/)

日本語部分は次のとおりである。

https://raw.githubusercontent.com/pacificspatial/flateau/main/data/plateau/README.md

> データは自由にお使いいただけますが、[CC BY 4.0ライセンス]（https://creativecommons.org/licenses/by/4.0/legalcode.ja） に従います。
>
> - 出典：国土交通省PLATEAU (https://www.mlit.go.jp/plateau/)
> 「3D都市モデル（Project PLATEAU）」（国土交通省）(https://www.geospatial.jp/ckan/dataset/plateau） をもとにジオメトリから各種統計データを算出しオンラインまたはGISソフトウェアで利用しやすいフォーマットに変換。 [Pacific Spatial Solutions株式会社](https://pacificspatial.com) 作成

Source Cooperative のページによれば、作成 2024-04-04、最終更新 2025-08-21、直近 28 日のダウンロード 2,960 件、配信 94.3 GB である。派生物に CC BY 4.0 を付けたうえで、原典の利用規約にも従えと重ねて書く形になっている。

### 3.4 PMTiles としての再配布

shiwaku/mlit-plateau-bldg-pmtiles は、同じ Flateau を経由した PMTiles を配布しており、ライセンス欄の書き方が年次によって割れている。

https://raw.githubusercontent.com/shiwaku/mlit-plateau-bldg-pmtiles/main/README.md

> ## 3D都市モデル（Project PLATEAU）建築物モデル（2022年）PMTiles
> ### データの出典
> - [法務省地図XMLアダプトプロジェクト](https://github.com/amx-project)にて公開されている、[3D都市モデル（Project PLATEAU）建築物モデルLOD1のPMTiles](https://github.com/amx-project/apb)をリネームしたもの
> - 対象都市：日本全国123都市（2022年公開時点）
> ...
> - ライセンス：-

> ## 3D都市モデル（Project PLATEAU）建築物モデル（2023年）PMTiles
> ### データの出典
> - [Pacific Spatial Solutions株式会社](https://pacificspatial.com/)が作成した、[3D都市モデル（Project PLATEAU）建築物モデルLOD0のGeoParquet形式のデータ](https://beta.source.coop/repositories/pacificspatial/flateau/description/)（CC BY 4.0ライセンス）
> ...
> - ライセンス：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

2022 年版はライセンスが「-」のまま公開されている。上流の PMTiles にライセンス表示がなかったものを、そのまま空欄で引き継いでいる。全国規模の PLATEAU 由来タイルが、出典表示だけでライセンス未記載のまま流通している実例である。

### 3.5 コードとデータでライセンスを分ける例

pixelx-jp/plateau-bridge は、コードとデータを明示的に分けている。

https://raw.githubusercontent.com/pixelx-jp/plateau-bridge/main/README.md

> ## License
>
> Code: MIT. Data: CC BY 4.0 (inherited from PLATEAU).

> All outputs auto-embed:
>
> > © Project PLATEAU / MLIT — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

> For PNG/SVG/PDF this is a corner watermark; for GLB it's in `asset.extras.attribution`; for mp4 it's a tail card. If you fuse with OSM at runtime, ODbL attribution is added automatically. We do not redistribute OSM-fused parquet.

出力物への帰属表示を自動注入し、OSM と融合した派生物は再配布しないという方針を明記している。PLATEAU 側を CC BY として扱い、ODbL の伝染を再配布しないことで回避するという整理である。

### 3.6 分布の傾向

GitHub のリポジトリ検索（`plateau citygml` で 54 件、`PLATEAU 3D都市モデル` で 37 件）を見る限り、圧倒的多数はツールやビューアであり、ライセンスは MIT か Apache-2.0 である。データそのものを再配布しているものは少なく、その場合はほぼ例外なく CC BY 4.0 が選ばれている。ODbL や ODC BY を選んで PLATEAU 派生データを配布している例は、OSM へのインポートを除いて見つけられなかった。

Hugging Face には PLATEAU の 3D 都市モデル由来のデータセットは見つからなかった（https://huggingface.co/api/datasets?search=plateau および search=PLATEAU の結果はいずれもフランス語の plateau、医療用語、強化学習の plateau に関するもので、該当なし）。

## 4. 反対の読み、すなわち測量法

### 4.1 サイトポリシー自身が但し書きを持っている

現行のサイトポリシー第3節には、CC BY 互換の宣言の直前に次の但し書きがある。

https://www.mlit.go.jp/plateau/site-policy/

> （２）個別法令による利用の制約があるコンテンツについて
> 一部のコンテンツには、個別法令により利用に制約がある場合があります。特に、以下に記載する法令についてはご注意ください。詳しくは各法令をご参照ください。
> ・測量法に基づく公共測量の測量成果の利用について（3D都市モデル整備のための測量マニュアル）
> https://www.mlit.go.jp/plateau/libraries/handbooks/

つまり国土交通省は、著作権法上はオープンライセンスだと言いつつ、測量法による別系統の制約がありうることを自ら注記している。この注記は 2022 年の talk-ja 議論の時点のサイトポリシーには存在しなかった（後述）。

### 4.2 測量マニュアルの実際の記述

https://www.mlit.go.jp/plateau/file/libraries/doc/plateau_doc_0010_ver03.pdf

> 3D都市モデル成果と測量法の関係
>
> 3D都市モデルは、新規計測により得られた測量成果または既存の測量成果が原典データとなる。これらの測量成果を用いて3D都市モデルを作成する場合は、測量法に基づき「公共測量」または「基本測量及び公共測量以外の測量」として国土地理院または国土交通大臣に申請しなければならない。

> 公共測量の測量標・測量成果の使用承認申請
> 公共測量の測量成果を使用して測量を実施しようとする者は、あらかじめ、当該測量成果を得た測量計画機関の承認を得なければならない。［測量法第44条］

条文の適用対象は「測量成果を使用して測量を実施しようとする者」である。PLATEAU のデータを閲覧、可視化、変換、再配布する行為はここでいう測量ではない。マニュアル全体も、3D 都市モデルを新たに作る側の手続きを定めたものであって、公開済みデータの利用者に承認申請を課すものではない。したがって測量法の注記は、データ利用一般を制限する根拠にはなっていない。ただしサイトポリシーが「詳しくは各法令をご参照ください」と投げている以上、境界の判断は利用者に委ねられている。

### 4.3 PLATEAU 自身が測量法の位置づけを語った記事

PLATEAU Journal j011「地図は誰のもの？3Dモデルオープンデータ周辺の権利を多角的に考える。」（2022.2.3、齋藤精一、弁護士の水野祐、国土交通省の内山裕弥による鼎談）が、測量法の性格を正面から扱っている。

https://www.mlit.go.jp/plateau/journal/j011/

齋藤の問いは次のとおりである。

> あえて言うと、測量法が若干今の時代にアップデートされていない印象があるのですが、測量法の現代的な意義についてはどのように考えられるでしょうか？

これに対する回答が、実務上もっともよく引かれる整理である。

> 測量法はクオリティの担保なんです。測量法上決められたプロセスで精度管理されているので、みんなが地図を信用できる。また、公共測量と言いたい場合はこうしてというだけで、測量法自体の規制法ではないんです。ただ、公共測量は膨大な作業でルールも多いので、測量法を守った測量ができるのは、実質的には専門家を持つ測量会社などに限られてきます。

> 公共測量成果は申請すれば入手可能ですが、入手までいくつかステップを踏まないといけない。煩雑かつインターフェースも難しく、もったいないんです。

「測量法自体の規制法ではない」という一文は、PLATEAU の公式媒体に載った弁護士の見解であって、国土交通省の法令解釈そのものではない。記事の形式は鼎談のインタビューである。それでも、PLATEAU 側が測量法を利用制限の根拠とは考えていないことの傍証としては強い。

### 4.4 talk-ja での処理

前掲のとおり、はとちゃんの測量法についての疑義に対する nyampire の回答は、PLATEAU の元データが都市計画基礎調査に由来し測量法の範疇外だというものだった。この回答は 2022 年 4 月の時点のものであり、2025 年に追加されたサイトポリシーの測量法注記を踏まえたものではない。この点は誰も再検討していない。

なお、これ以外に「PLATEAU はこの用途には使えない」と主張する公開文書は見つけられなかった。GitHub の code 検索、Web 検索のいずれでも、PLATEAU のライセンスに異議を唱える文書は発見できていない（未確認。日本語圏のブログや Zenn、Qiita、はてなブックマークなどを横断的に検索する手段を用いていないため、存在しないとまでは言えない）。

## 5. 多重ライセンスの文言は変わったか

Internet Archive の CDX API でスナップショット一覧を取得し（collapse=digest で 39 件）、各時点の本文を確認した。

https://web.archive.org/cdx/search/cdx?url=www.mlit.go.jp/plateau/site-policy/

2022 年 11 月以前のスナップショットは、当時のサイトが JavaScript で本文を描画する SPA だったため、保存された HTML にも main チャンクの JS にも本文が含まれておらず、本文を読み出せない（未確認。20210326135915 から 20220809173827 までのスナップショットで本文抽出を試み、いずれも本文が 28 文字のシェルのみだった。static/js/main.*.chunk.js も取得して ODbL、互換、政府標準利用規約、測量法のいずれも含まないことを確認した）。

読み出せた最古のスナップショットは 2022-11-27 で、そこにはすでに ODC BY と ODbL の一文がある。

https://web.archive.org/web/20221127194233id_/https://www.mlit.go.jp/plateau/site-policy/

> ② 本利用ルールは、平成２８年４月１日に定めたものです。本利用ルールは、政府標準利用規約（第2.0版）に準拠しています。（略）
> ③ 本利用ルールは、クリエイティブ・コモンズ・ライセンスの表示4.0国際（https://creativecommons.org/licenses/by/4.0/legalcode.ja に規定される著作権利用許諾条件。以下「CC BY」といいます。）と互換性があり、本利用ルールが適用されるコンテンツはCC BYに従うことでも利用することができます。また、利用者がOpen Data CommonsによるODC BY（https://opendatacommons.org/licenses/by/1-0/）又はODbL（https://opendatacommons.org/licenses/odbl/）での利用を希望する場合に、それを妨げるものではありません。

より早い時点の証拠は、Internet Archive ではなく talk-ja のアーカイブから得られる。2022-04-04 のはとちゃんの投稿が「利用者がOpen Data CommonsによるODC BYまたは ODbLでの利用を妨げるものではない」という文言を引用しているため、この一文は遅くとも 2022 年 4 月 4 日には存在していた。

https://lists.openstreetmap.org/pipermail/talk-ja/2022-April/011126.html

スナップショットを追うと、2025 年に別の変化が起きている。

| 時点 | 準拠する規約 | CC BY の言い方 | ODC BY / ODbL | 測量法の注記 |
| --- | --- | --- | --- | --- |
| 2022-11-27 | 政府標準利用規約（第2.0版） | CC BY に従うことでも利用することができます | あり | なし |
| 2025-01-18 | 政府標準利用規約 | 「許諾します」なし | あり | なし |
| 2025-07-15 | 公共データ利用規約（第1.0版）PDL1.0 | 許諾します | あり | あり |
| 2026-09-30（現行） | 公共データ利用規約（第1.0版）PDL1.0 | 許諾します | あり | あり |

（2025-03-26 と 2025-04-29 のスナップショットは本文を含まないシェルだったため、切り替え時期は 2025-01-18 から 2025-07-15 の間としか特定できない。未確認。）

整理すると、ODC BY と ODbL の一文は少なくとも 2022 年 4 月から現在まで一貫して存在し、変更されていない。変わったのは基盤となる規約（政府標準利用規約 2.0 から PDL1.0 へ）、CC BY についての表現（「従うことでも利用できます」から「許諾します」へ、つまりより能動的な許諾へ）、そして測量法の注記の追加（2025 年）である。ODbL の根拠は揺らいでいないが、測量法の注記だけが後から足されている。

## 6. 実務の土台は見かけよりも薄い

ここまでの確認から、次のことが言える。

第一に、OSM へのインポートを支える「ODbL で使ってよい」という判断は、国土交通省への照会や書面の許諾ではなく、サイトポリシーの「妨げるものではありません」という一文をコミュニティ側で読んだ結果である。読み手は一人（nyampire）であり、それに同意した公開の記録は wiki のトークページへの転記だけである。OSM wiki の「ODbL Compliance verified: yes」は、検証を行った主体も方法も書かれていない自己申告である。

第二に、2022 年 4 月から 5 月にかけて実施された 75 人規模のアンケートは、ライセンスの可否を問うていない。「約 70% が賛成」という imports ML での説明は、形状置き換えの是非への賛否である。ライセンス解釈にコミュニティの多数が同意したという記録は存在しない。

第三に、imports メーリングリストという国際的なレビューの場では、ライセンスは一度も論点にならなかった。3 通のスレッドで唯一の外部からの応答はタグ設計についてのものである。異議が出なかったことは承認ではない。

第四に、国土交通省側の文言は FAQ とサイトポリシーで強さが異なる。FAQ は ODbL を含む多重ライセンスとして提供していると断言しており、サイトポリシーは不作為の表明にとどまる。実務は事実上 FAQ の強さで運用されている。

第五に、CKAN のメタデータは現行のサイトポリシーの節構成に追随しておらず、例外パッケージでは isopen=True と営利利用の全面禁止が同居している。CKAN のフラグを信じて自動判定する実装は誤る。

第六に、派生データを再配布している第三者は、ほぼ全員が CC BY 4.0 を選んでいる。これは安全側の選択であり、それ自体は妥当である。ただし PMTiles のように、ライセンス欄が「-」のまま全国規模で配布されている例も現に存在する。

以上を踏まえると、PLATEAU を CC BY 4.0 として扱うことには、国土交通省の能動的な許諾（「許諾します」）という明示の根拠がある。一方、ODbL として扱うことの根拠は、不作為の表明の一文と、それを 2022 年に一人が読んだ解釈と、FAQ の断定的な記述である。この二つは同じ強さではない。OSM へのインポートはこの薄いほうに乗っている。

## 7. 参照した一次資料

- https://www.mlit.go.jp/plateau/site-policy/
- https://www.mlit.go.jp/plateau/faq/
- https://www.mlit.go.jp/plateau/learning/tpc03-1/
- https://www.mlit.go.jp/plateau/journal/j011/
- https://www.mlit.go.jp/plateau/file/libraries/doc/plateau_doc_0010_ver03.pdf
- https://www.geospatial.jp/ckan/api/3/action/package_show?id=plateau-tokyo23ku-citygml-2020
- https://www.geospatial.jp/ckan/api/3/action/package_show?id=plateau-27999-osaka-shi-2025
- https://wiki.openstreetmap.org/wiki/MLIT_PLATEAU/imports_outline?action=raw
- https://wiki.openstreetmap.org/wiki/JA_talk:MLIT_PLATEAU/imports_outline?action=raw
- https://lists.openstreetmap.org/pipermail/talk-ja/2022-April/011126.html
- https://lists.openstreetmap.org/pipermail/talk-ja/2022-April/011127.html
- https://lists.openstreetmap.org/pipermail/talk-ja/2023-September/011361.html
- https://lists.openstreetmap.org/pipermail/imports/2022-August/006941.html
- https://lists.openstreetmap.org/pipermail/imports/2022-August/006942.html
- https://lists.openstreetmap.org/pipermail/imports/2022-August/006943.html
- https://raw.githubusercontent.com/yuuhayashi/citygml-osm/master/LICENSE.txt
- https://raw.githubusercontent.com/indigo-lab/plateau-tokyo23ku-building-mvt-2020/main/README.md
- https://source.coop/pacificspatial/flateau
- https://raw.githubusercontent.com/pacificspatial/flateau/main/data/plateau/README.md
- https://raw.githubusercontent.com/shiwaku/mlit-plateau-bldg-pmtiles/main/README.md
- https://raw.githubusercontent.com/pixelx-jp/plateau-bridge/main/README.md
- https://web.archive.org/cdx/search/cdx?url=www.mlit.go.jp/plateau/site-policy/
- https://web.archive.org/web/20221127194233id_/https://www.mlit.go.jp/plateau/site-policy/
