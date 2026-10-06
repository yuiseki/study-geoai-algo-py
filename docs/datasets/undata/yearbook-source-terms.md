# 統計年鑑の Source 列に出てくる機関の利用条件

UNdata の統計年鑑 (Statistical Yearbook) の CSV は行ごとに Source 列を持ち、値を作った元の機関を名指しする。どの行を公開してよいかは、その元機関の条件で決める方針である。ここでは未確認だった 7 系統について、各機関自身の利用条件のページを 2026-10-06 に読んで確かめた。引用はすべて当日 curl で取得した本文そのままである。データそのものは取得していない。

判定は 4 種類のどれかで書く。商用を含めて再配布可 / 非商用のみ / 許可が要る / 不明。どれを公開に含めるかは判定であって決定ではない。

## 一覧

| 機関 (年鑑の表) | 判定 | 根拠の要点 |
|---|---|---|
| UNESCO 統計研究所 UIS (245, 285, 309, 319, 323) | 商用を含めて再配布可 (継承条件つき) | データ閲覧サイトと API が CC BY-SA 4.0 を明示 |
| UN Tourism (旧 UNWTO) (176) | 許可が要る | サイト規約が個人・非商用の利用に限り、再配布と派生物の作成を認めない |
| WIPO (264) | 許可が要る | 統計データセンターの利用条件が統計データセットの再公表を禁じる |
| 列国議会同盟 IPU (317) | 非商用のみ | CC BY-NC-SA 4.0、規約本文も商用目的を除外 |
| UNODC (328) | 許可が要る | データポータルの規約リンク先が国連一般規約 (個人・非商用、再配布不可) |
| IUCN レッドリスト (313) | 許可が要る | 商用利用も再掲載・再配布も、派生物を含めて事前の書面許可が要る |
| UNEP-WCMC / IUCN / BirdLife (145 の保護区・KBA 行) | 許可が要る | WDPA と KBA の両方の規約が商用利用と再配布を派生物も含めて禁じる |

集計値と生データの区別については、7 系統のうち明示的に区別している規約は無かった。IUCN と KBA は分類群や地点の名前とカテゴリだけを制限の外に置くが、国別の件数表には触れていない。WDPA、IUCN、KBA の 3 つは「派生物 (Derivative Works)」にも制限を掛けると明記している。

## 1. UNESCO 統計研究所 (UIS)

読んだページ (2026-10-06)。

- <https://databrowser.uis.unesco.org/terms-and-conditions> (UIS Data Browser の Terms and conditions)
- <https://api.uis.unesco.org/api/public/openapi/schema.json> (UIS Data API の説明文。ドキュメント画面 <https://api.uis.unesco.org/api/public/documentation/> の元データ)
- <https://www.unesco.org/en/terms-use> (UNESCO 全体の Terms of Use、Last update: 15 September 2026)

`uis.unesco.org` 本体は当日ボット対策の中間ページ (`/TSPD/`) しか返さず、`https://www.uis.unesco.org/en/terms-use` は 404 だった。UIS のデータの配布口であるデータ閲覧サイトと API の文言を一次資料とした。

再配布と商用利用。データ閲覧サイトの規約。

> The information available on this website has been posted with the intent that it be readily available for sharing and reproduction, in part or in whole, and by any means, without charge or further permission unless otherwise specified.

> The work of the UIS is licensed under the Creative Commons Attribution-ShareAlike 4.0 International license. To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/4.0/

API の説明文も同じ。

> The data is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/) license.

CC BY-SA 4.0 は商用利用を禁じない。条件は表示と継承 (改変物を同じライセンスで出すこと) である。

表示の書き方。

> In using UIS data you must give appropriate credit to the UIS using the following format: Source: (If appropriate "Adapted from") UNESCO Institute for Statistics (UIS), complete URL, date of extraction.

集計値と生データの区別は無い。データ全体が CC BY-SA 4.0 である。

注意点。UNESCO 全体の規約は 2026-09-15 に改定されており、データベースの実質的部分の抽出・再利用や商用利用を原則として禁じている。

> Except as expressly permitted under these Terms, under an applicable license, or specific authorization by UNESCO, the extraction or reutilization of all or a Substantial Part of the contents of a UNESCO database, or the repeated or systematic extraction or reutilization of insubstantial parts of its contents, is prohibited without prior written authorization

ただし同じ規約は、個別のライセンスがある素材はそのライセンスに従うと書いている。

> Where a Material is made available under an Intergovernmental Organization (IGO) Creative Commons license or other specific license, the User may use that Material in accordance with the terms of that license. ... Nothing in these Terms restricts rights expressly granted by a Creative Commons license, other applicable license or specific authorization issued by UNESCO.

UIS のデータには CC BY-SA 4.0 が明示されているので、こちらが優先すると読める。禁止事項を並べた第 7 条 (商用利用、データベースの抽出、AI 学習用データセットへの組み込みなど) も、前置きで適用ライセンスがある場合を除いている。

> Except where expressly permitted under Section 5, under an applicable license or under a specific authorization issued by UNESCO, the User shall not: (a) use the Sites or Materials for commercial purposes; ...

判定: 商用を含めて再配布可。ただし CC BY ではなく CC BY-SA 4.0 なので、UIS の行を含む公開物には継承条件が掛かる。他の行が CC BY 系で、全体を CC BY-SA 以外で出す予定なら、UIS の行だけ別ファイル・別ライセンスにする必要がありうる。

## 2. UN Tourism (旧 世界観光機関 UNWTO)

読んだページ (2026-10-06)。

- <https://www.untourism.int/copyright> (見出しは「Copyright」、本文の節は「Terms and conditions」)
- <https://www.untourism.int/tourism-statistics/tourism-statistics-database> (Tourism Statistics Database の案内)
- <https://www.untourism.int/tourism-data/un-tourism-tourism-dashboard> (ライセンスの記載なし)

`https://www.untourism.int/terms-of-use` は 404 だった。統計データベースの案内ページの脚注は「© Copyrights UN Tourism 2025. All rights reserved.」で、データ固有のライセンス表示は無い。一括ダウンロードの zip (`UN_Tourism_bulk_data_download_05_2026.zip`) の中央ディレクトリだけを読んだが、入っているのは xlsx とメタデータ PDF で、ライセンスのファイルは無かった。

再配布と商用利用。サイト規約の冒頭。

> The World Tourism Organization grants permission to Users to visit the Site and to download and copy the information, documents and materials (collectively, "Materials") from the Site for the User's personal, non-commercial use, without any right to resell or redistribute them or to compile or create derivative works there from, subject to the terms and conditions outlined below, and also subject to more specific restrictions that may apply to specific Materials within this Site.

国連の一般規約とほぼ同じ文面である。個人的・非商用の利用だけを許し、再販、再配布、編集物や派生物の作成を認めない。

統計データベースの案内ページには、学生・大学研究者向けの無償提供の特別取り決めがある。データの入手自体が通常は有償であることを示唆している。

> Note to students and university researchers: to be able to obtain data from the UN Tourism database free of charge you should send a formal request in writing (letter from your University, Faculty, etc. and signed by your professor/tutor; pdf is acceptable) in accordance with the special arrangement to support students and university researchers .

集計値と生データの区別は無い。

判定: 許可が要る。個人・非商用の範囲を超える再配布は規約上認められていない。

## 3. 世界知的所有権機関 (WIPO)

読んだページ (2026-10-06)。

- <https://www.wipo.int/en/web/ip-statistics/about> (About the WIPO IP Statistics Data Center、節「Conditions of use」)
- <https://www.wipo.int/en/web/terms-of-use> (WIPO 全体の Terms of Use)

`https://www.wipo.int/en/web/about-wipo/terms-of-use` は 404 だった。

統計データ固有の条件。

> By using WIPO's statistical data, users agree not to republish or commercially re-sell WIPO's statistical datasets.  In addition, when employing WIPO's statistics data in any written work, users shall cite "WIPO Statistics Database" as the source of the data.

全体規約は新しいオンラインコンテンツを CC BY 4.0 で出すとしている。

> Except for some content published under more restrictive terms, new WIPO online publications and other online content are issued under an Attribution 4.0 International CC license (CC BY 4.0) .

しかし全体規約の冒頭は、サービス固有の条件があればそちらが当たると書いている。

> Unless service-specific terms of use apply, by browsing the WIPO website and using its online services, the user agrees to the following:

統計データセンターは固有の条件 (上の Conditions of use) を持つので、CC BY 4.0 ではなくそちらが当たると読む。

集計値と生データの区別。明示の区別は無い。ただし文言は「statistical datasets」の再公表を禁じる一方で、文章の中で統計値を使う場合は出典表示を条件に認めている。個々の数値を論文や記事で引くのは可、データセットとして再び公開するのは不可、という線引きと読める。年鑑の表の行を CSV として公開するのは後者に当たる。

判定: 許可が要る。

## 4. 列国議会同盟 (IPU)、Parline / Women in National Parliaments

読んだページ (2026-10-06)。

- <https://www.ipu.org/terms-use> (ipu.org、data.ipu.org、parliamentaryindicators.org 共通の Terms of Use、Last update: 24 April 2024)
- <https://data.ipu.org/> (Parline。フッターに CC BY-NC-SA 4.0 のバッジと <https://creativecommons.org/licenses/by-nc-sa/4.0/> へのリンク)

規約は 3 サイト共通と明記している。

> Use of the Inter-Parliamentary Union (IPU) websites, ipu.org, data.ipu.org and parliamentaryindicators.org, constitutes acceptance of these Terms of Use.

商用利用。

> All content on the IPU websites or extracts thereof may be displayed, reproduced, translated or adapted for research or personal use but not for sale or for use in conjunction with commercial purposes.

> The IPU's open access policy applies to all the publications published by the IPU and is subject to the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

再配布。データセットについては、無償で公開することを条件に、許可なく再提供してよいと読める。

> Permission from the IPU is not required for the use of IPU materials issued under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. You may also use our Application Programming Interface (API) to facilitate access to our datasets, either through a separate website or through another type of software application. Any IPU datasets must also be made available to the public free of charge.

> Any use of datasets from data.ipu.org should be attributed as follows: "Inter-Parliamentary Union: dataset_name, month_year" (for example "Inter-Parliamentary Union: Women's Caucuses, September 2017"). If you share or facilitate access to the datasets, you must include the same acknowledgement requirement in any sub-licences of the data that you grant, and require that any sub-licensees do the same, by providing the Uniform Resource Locator (URL) of these terms of use.

集計値と生データの区別は無い。

判定: 非商用のみ。無償での再配布は表示と継承の条件つきで認められるが、商用利用は除外されている。

## 5. 国連薬物犯罪事務所 (UNODC)、dataUNODC

読んだページ (2026-10-06)。

- <https://dataunodc.un.org/> (当日は <https://data.unodc.org/> にリダイレクト。フッターの「Terms and Conditions」のリンク先が下の legal、「Copyright」のリンク先が国連の著作権ページ)
- <https://www.unodc.org/unodc/legal.html> (Terms of Use)
- <https://www.un.org/en/about-us/copyright> (国連の Copyright)

データポータル固有のライセンス表示は見つからなかった。旧来のデータページの URL (`/dp-intentional-homicide-victims`) もトップへ転送された。ポータルのフッターが指す規約は UNODC のサイト規約で、文面は国連一般規約と同じである。

> The United Nations grants permission to Users to visit the Site and to download and copy the information, documents and materials (collectively, "Materials") from the Site for the User's personal, non-commercial use, without any right to resell or redistribute them or to compile or create derivative works therefrom, subject to the terms and conditions outlined below, and also subject to more specific restrictions that may apply to specific Material within this Site.

国連の著作権ページ。

> None of the materials provided on this web site may be used, reproduced or transmitted, in whole or in part, in any form or by any means, ... except as provided for in the Terms and Conditions of Use of United Nations Web Sites, without permission in writing from the publisher.

集計値と生データの区別は無い。

判定: 許可が要る。データポータルが指す規約は個人・非商用に限り、再配布と派生物の作成を認めない。なお同じ数値が data.un.org の Homicide Statistics にも載っており、そちらには UNdata の規約が当たると README.md で整理した。年鑑の行を「UNODC の条件で読む」方針なら、UNdata 側の扱いとは食い違う。

## 6. IUCN レッドリスト (国別の絶滅危惧種数)

読んだページ (2026-10-06)。

- <https://www.iucnredlist.org/terms/terms-of-use> (The IUCN Red List Terms and Conditions of Use, version 3.1, June 2024)
- <https://www.iucnredlist.org/resources/summary-statistics> (Summary Statistics。国別の件数表 Table 5、6a〜6d、8a〜8d の案内。独自のライセンス表示は無い)

対象範囲。表の形のデータも含む。

> For the purposes of this Agreement, IUCN Red List Data comprise all tabular, and all spatial and associated attribute data, contained within The IUCN Red List.

商用利用。

> Neither (a) IUCN Red List Data nor (b) any work derived from or based upon IUCN Red List Data (i.e., "Derivative Works") may be put to Commercial Use without the prior written permission of IUCN. For the purposes of these Terms and Conditions, "Commercial Use" means a) any use by, on behalf of, or to inform or assist the activities of, a commercial entity (an entity that operates 'for profit') or b) use by any individual or non-profit entity for the purposes of revenue generation.

再配布。

> All forms of reposting, and any sub-licensing, reselling, or other forms of redistribution of IUCN Red List Data in their original format, either whole or in part, alone or combined with other data, including within Derivative Works, are strictly prohibited without the prior written permission of IUCN.

許される利用。

> you are hereby granted a non-transferable license to use, download and print IUCN Red List, without requesting prior permission, solely for conservation or education purposes, scientific analyses, and research.

集計値と生データの区別。制限の外に置かれているのは、個々の分類群に付いたカテゴリだけである。

> However, IUCN warrants that you are free to view and query The IUCN Red List, and places no restrictions on use of the IUCN Red List Categories associated with each named taxonomic entity.

国別の件数表 (Summary Statistics の Table 5 など) を別扱いにする文言は無い。件数表はレッドリストのサイト上に表として載っているので「all tabular ... data contained within The IUCN Red List」に含まれると読むのが自然だが、規約が明示しているわけではない。また派生物の定義は「transformative and include originality」を要し、そうでなければ再掲載・再配布として扱うと書く。年鑑の表は件数を並べ替えただけなので、派生物ではなく再掲載・再配布に当たると読める。

> To be considered a Derivative Work, the new work must be transformative and include originality on the part of the creator, otherwise it may simply be considered Reposting or Redistribution, depending on the way the new work is made available.

判定: 許可が要る。件数表が「IUCN Red List Data」に入るかは明文が無いが、入らないと読む根拠も規約の中には無い。

## 7. UNEP-WCMC、IUCN、BirdLife International (表 145 の保護区・KBA の行)

表 145 の保護区と KBA の行は、WDPA (世界保護地域データベース) と World Database of Key Biodiversity Areas の重ね合わせから計算した国別の割合である。元データは 2 つの規約に掛かる。WDPA の規約は ../protected-planet/README.md に 2026-09-30 時点の全文の要点がある。ここでは 2026-10-06 に再取得して文言が変わっていないことを確かめたうえで、集計値に関わる部分だけを引く。

読んだページ (2026-10-06)。

- <https://www.protectedplanet.net/en/legal> (WDPCA と GD-PAME の Terms and Conditions)
- <https://www.keybiodiversityareas.org/termsofservice> (当日は `/en/termsofservice` に転送。The World Database of Key Biodiversity Areas Terms and Conditions of Use, Version 2.0 (November 2023))

### WDPA (UNEP-WCMC と IUCN)

商用利用。派生物も明示的に含む。

> Neither (a) the WDPCA Materials and the GD-PAME Materials nor (b) any work derived from or based upon the WDPCA Materials and the GD-PAME Materials ("Derivative Works") may be put to Commercial Use without the prior written permission of UNEP-WCMC.

> For the avoidance of doubt, UNEP-WCMC reserves the right to determine whether a particular use of the WDPCA and GD-PAME Materials constitutes a Commercial Use or otherwise .

再配布。

> The WDPCA and GD-PAME Materials may not be sub-licensed in whole or in part including within Derivative Works without the prior written permission of UNEP-WCMC. You may not redistribute the WDPCA and GD-PAME Data contained in the WDPCA and GD-PAME in whole or in part by any means including (but not limited to) electronic formats such as web downloads, ...

公開してよい形。

> You may publish the WDPCA and GD-PAME Materials in whole or in part, including on-line, providing (a) the WDPCA and GD-PAME Data are not downloadable and (b) the proper attribution is clearly visible (see 'Attribution' below).

集計値と生データの区別は無い。国別の被覆率は「work derived from or based upon」に当たり、商用利用の禁止が掛かる。サブライセンスの禁止も派生物を含む。一方、再配布の禁止の文は対象を「the WDPCA and GD-PAME Data」と書いており、派生物の再配布そのものまで禁じているかは、サブライセンス禁止の文と合わせて読む必要がある。ダウンロードできる形の公開は「Publishing」の節の条件 (a) を満たさない。

### KBA (BirdLife International が KBA パートナーシップを代表)

対象範囲。

> For the purposes of this Agreement, KBA Data comprise all tabular, and all spatial and associated attribute, data contained within The World Database of Key Biodiversity Areas™.

商用利用。

> You may not use, nor facilitate or assist others to use,  either (a) KBA Data or (b) any Derivative Works (as further defined in clause 5) for Commercial Use without the prior written permission of the KBA Secretariat, which grants permission on behalf of the owners of the relevant intellectual property rights.

再配布。派生物を名指しで含む。

> Except as provided in this section 4, all forms of reposting, and any sub-licensing, reselling, or other forms of redistribution or communication to the public of the KBA Data in their original format, either whole or in part, alone or combined with other data, including within Derivative Works (as defined below) are strictly prohibited without the prior written permission of the KBA Secretariat.

派生物の扱い。版 2.0 の変更点として、派生物を許可なく配布できるとしていた旧文言を削ったと書いている。

> Section 4. Clarification added that permission must be sought for reposting and/or redistribution of Derivative Works.

> Deletion of wording indicating that Derivative Works could be produced and distributed without prior written consent, given the new text added to Section 4 requiring permission to be sought for reposting or redistribution of Derivative Works.

制限の外に置かれているのは KBA の名前と該当基準だけである。

> However, the KBA Partners warrant that you are free to view and query The KBA Website, and place no restrictions on the identity of named KBAs and the criteria under which they qualify.

許される利用は保全・教育・科学的分析・研究に限られる。

> you are hereby granted a non-transferable license to use, download and print the materials contained in The KBA Website, without requesting prior permission, solely for conservation or education purposes, scientific analyses, and research.

商用の許諾は IBAT (Integrated Biodiversity Assessment Tool) 経由で有償で出す仕組みになっている。

> KBA Partners agree to grant BirdLife permission to license KBA Data for commercial use on their behalf via the Integrated Biodiversity Assessment Tool (IBAT), ...

判定: 許可が要る。WDPA と KBA のどちらも、派生物に商用利用の禁止を掛け、KBA は派生物の再配布にも書面許可を要求する。国別の割合という集計値を別扱いにする文言はどちらにも無い。表 145 の残りの行 (FAO の森林面積など) は FAO の CC BY 4.0 で読める。

## 補足

- いずれの規約も予告なく変わりうると本文に書いている。ここの引用は 2026-10-06 時点のもの。UNESCO の全体規約は 2026-09-15 に改定されたばかりである。
- UIS、WIPO、IUCN、KBA、WDPA の 5 つは、規約の解釈権を機関側に留保するか、サービス固有の条件を優先させる構造になっている。境界事例は機関側の判断次第になる。
- 「許可が要る」の 5 系統 (UN Tourism、WIPO、UNODC、IUCN、表 145 の保護区・KBA 行) の問い合わせ先は、それぞれ規約本文に書かれている。UN Tourism は info@untourism.int、WIPO の統計は規約に窓口の明記なし (全体の連絡先は <https://www.wipo.int/contact/en/>)、IUCN は Red List Unit、KBA は science@birdlife.org、WDPA は Protected Planet の規約が案内する窓口 (商用は IBAT)。
