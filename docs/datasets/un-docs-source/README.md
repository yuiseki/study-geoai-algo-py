# 国連文書 (docs.un.org / ODS)

2026-09-30 に読んで確かめた内容。ライセンスの記述は当日 curl で取った国連のページと、国連事務局の管理指令 ST/AI/189/Add.9/Rev.2 の PDF (当日取得、スキャンなので自分で OCR した) に基づく。件数と処理の数値は `yuiseki/un-docs` の `provenance.yaml` (当日取得) から引いたもので、国連側で確かめたものではない。

- `yuiseki/un-docs` ([huggingface-yuiseki/un-docs.md](../huggingface-yuiseki/un-docs.md)) の上流。
- 国連総会 (`A/...`) と安全保障理事会 (`S/...`) の公式文書。ODS (Official Document System) に入っているものを、UNDOCS という短縮リンクの仕組みから引く。
- 案内: `https://docs.un.org/` (「UNDOCS, also known as EZ-Link, was created in 2011 to provide a quick and easy way to link directly to documents within the Official Document System (ODS)」)
- 作ったコード: `https://github.com/yuiseki/undocs` (Apache-2.0、最終 push 2026-09-21)。

## 取り方 (当日確かめた)

人が見る URL は `https://docs.un.org/{lang}/{symbol}`。言語コードは ar / zh / en / fr / ru / es の 6 つ。

この URL が返す HTML は中身を持たず、実体の PDF は別の API にある。`https://docs.un.org/en/ST/AI/189/Add.9/Rev.2` (4,241 バイト) の中に次の 1 本のリンクだけがあった。

```
https://documents.un.org/api/symbol/access?s=ST/AI/189/Add.9/Rev.2&l=en&t=pdf
```

この API を直接叩くと PDF が返る (当日の実測)。

| 記号 | 応答 |
|---|---|
| `A/RES/55/2` | 200、application/pdf、63,788 バイト、9 ページ |
| `ST/AI/189/Add.9/Rev.2` | 200、application/pdf、437,237 バイト、7 ページ (テキスト層無しのスキャン) |
| `ST/AI/189/Add.9/Rev.3` | 200 だが 1,303 バイトの HTML (存在しない) |

`yuiseki/undocs` の `scripts/docs.un.org/fetch.py` もこの API を使う。既定は `--delay 2.5`、`--workers 4`。`Referer` に `https://docs.un.org/{lang}/{symbol}` を入れないと `/error` を返す、と冒頭のコメントにある。

## ライセンス

ここが本題で、開いたライセンスではない。互いに食い違う 3 つの文書がある。

### 1. 国連ウェブサイトの著作権表示

`https://www.un.org/en/about-us/copyright` (docs.un.org のフッターからのリンク先) の本文。

> Copyright © United Nations
> All rights reserved.
> None of the materials provided on this web site may be used, reproduced or transmitted, in whole or in part, in any form or by any means, electronic or mechanical, including photocopying, recording or the use of any information storage and retrieval system, except as provided for in the Terms and Conditions of Use of United Nations Web Sites, without permission in writing from the publisher.

### 2. 利用規約

`https://www.un.org/en/about-us/terms-of-use` の General (a)。

> The United Nations grants permission to Users to visit the Site and to download and copy the information, documents and materials (collectively, "Materials") from the Site for the User's personal, non-commercial use, without any right to resell or redistribute them or to compile or create derivative works therefrom, subject to the terms and conditions outlined below, and also subject to more specific restrictions that may apply to specific Material within this Site.

個人の非商用に限り、再配布権も派生物を作る権利も無い、と書いてある。これを字面どおり読めば、`yuiseki/un-docs` のような再配布データセットは作れない。

### 3. `yuiseki/un-docs` が典拠として挙げるページ

データセットの `LICENSE` と `provenance.yaml` は `https://shop.un.org/rights-permissions` を典拠にしている。当日このページを全文読んだが、議事文書 (parliamentary documentation) が著作権の対象外だという記述は無かった。書いてあるのは次のようなことで、どちらかといえば許可を要求する側の内容である。

> Prior express written permission is required in order to reproduce, republish, mirror, or translate any material from a book, periodical or other product from United Nations Publications featured on this website.

> No permission is necessary to reproduce excerpts from a non-sales publication provided that proper credits are given.

「非売の刊行物からの抜粋 (excerpts) は出典を書けば許可不要」とは書いてあるが、全文の再配布については書いていない。データセット側が典拠として示したページは、データセット側の主張を支えていない。

### 4. 本当の典拠になりうる文書

議事文書がパブリックドメインだという主張の出どころは、このページではなく国連事務局の管理指令のほうだと考えられる。`ST/AI/189/Add.9/Rev.2` (1987-09-17、COPYRIGHT IN UNITED NATIONS PUBLICATIONS: GENERAL PRINCIPLES, PRACTICE AND PROCEDURE) を当日取得した。スキャンなので以下は自分で OCR した文字列であり、誤読が混じっている可能性がある。

第 2 項。

> The following categories of material will, as at present, be left in the public domain, i.e., the United Nations will not seek copyright therefor unless, prior to issue and in exceptional circumstances, the Publications Board decides otherwise, in consultation with the Office of Legal Affairs.

続けて (a) Official Records、(b) United Nations documents (「written material officially issued under a United Nations document symbol」)、(c) Public information material (「the term does not include public information material that is offered for sale」) の 3 つを挙げる。

第 7 項。

> The general rule for Official Records, United Nations documents and public information material is that these publications will be in the public domain. However, in exceptional circumstances, author departments may apply to the Publications Board to obtain copyright protection for such materials.

`A/...` と `S/...` の決議・記録はこの (a) と (b) に当たる。つまり「文書記号を持つ非売の文書はパブリックドメイン」という `yuiseki/un-docs` の `LICENSE` の主張自体は、この管理指令に根拠がある。

この OCR の読みは独立な出典で裏付けられる。`yuiseki/un-docs` の `LICENSE` は典拠を 2 つ挙げており、もう一方の `https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/United_Nations` を当日読むと、同じ管理指令を日付ごと記録している。

> The United Nations' basic policy towards copyrighting as set forth in administrative instruction ST/AI/189/Add.9/Rev.1 of 26 March 1985 was not to seek copyright with the intention of thus facilitating dissemination as widely as possible of the ideas in United Nations publications. Under ST/AI/189/Add.9/Rev.2 of 17 September 1987, the United Nations would still not seek copyright for official records, documents and public i(以下略)

Wikimedia Commons には `{{PD-UN-doc}}` というタグもある。つまり典拠 2 本のうち `shop.un.org` は主張を支えないが、Commons のほうは管理指令へ正しく繋がっている。孫引きを避けるべきという上の注意は変わらないが、主張そのものが典拠なしというわけではない。

### 判断

- 標準的なオープンライセンスは付いていない。CC BY でも CC0 でも PDL でもなく、そもそも「ライセンス」という形の許諾が無い。あるのは「著作権を取りに行かない」という 1987 年の内部方針と、それと矛盾するウェブサイト規約である。
- Open Definition の意味で「オープン」とは言えない。オープンかどうかは許諾の文言で決まるが、その文言が無い。パブリックドメインだとすれば結果として自由に使えるが、それは許諾されたからではなく権利が発生していない (と国連が言っている) からで、根拠の強さが違う。
- 矛盾は解消していない。管理指令は「文書はパブリックドメイン」と言い、同じ組織のウェブサイト規約は「個人の非商用限り、再配布不可」と言う。規約はサイトからの取得行為に掛かる契約的な条件で、著作権の有無とは別の層だと読むこともできるが、どちらが優先するかを国連は書いていない。ここは国連側に有利に解釈せず、食い違ったままだと記す。
- 例外条項がある。第 2 項も第 7 項も「exceptional circumstances」で Publications Board が著作権を取りうるとしている。「文書記号があるから必ずパブリックドメイン」ではなく、「原則としてそうする」である。個々の文書について確かめる手段は見つけていない。
- 管理指令は 1987 年のもので、第 1 項に「revises, on an experimental basis until the end of 1989」とある。1989 年末以降どうなったかは未確認。`Rev.3` と `Add.9/Rev.2/Amend.1` は ODS に無かったので、この Addendum の最新版ではあると見える。
- 使えるか。全文を再配布する用途では、根拠が 1987 年の内部方針 1 本に掛かっていて、サイト規約とは正面から矛盾している。学習や研究で手元に置くぶんには問題になりにくいが、「オープンライセンスのデータセットの材料にする」と言い切れる状態ではない。この項目の結論は「使うなら根拠が薄いことを自覚して使う」であって、「CC BY 相当」ではない。

## 気をつけること

`shop.un.org/rights-permissions` を典拠として引き写さないこと。 `yuiseki/un-docs` の `LICENSE` も `provenance.yaml` もこの URL を挙げるが、当日読んだかぎりそこに議事文書の話は無い。同じ `LICENSE` が挙げるもう一方の Wikimedia Commons のページは管理指令へ正しく繋がっているので、引くならそちらか、`ST/AI/189/Add.9/Rev.2` そのものを引く。

国連の紋章は別枠。 規約とは別に `shop.un.org/rights-permissions` は「Use and display of the United Nations emblem is highly restricted」と書き、事前の書面同意を求めている。文書の PDF の 1 ページ目には紋章が入っている。本文テキストだけを配るなら関係しないが、PDF そのものや画像を配るときは別の条件が掛かる。

`documents.un.org` の robots.txt は API を禁じている。 当日取得した内容は次のとおりで、`yuiseki/undocs` の取得スクリプトが叩く `/api/symbol/access` はこの `Disallow: /api` に当たる。

```
User-agent: *
Disallow: /doc
Disallow: /access
Disallow: /api
```

`docs.un.org` のほうは robots.txt を返さない (どのパスでも言語選択の HTML が返る)。大量取得するなら、少なくとも `fetch.py` の既定の 2.5 秒間隔は緩めない。

`l=ja` は失敗せず英語を返す。 `fetch.py` のコメントと `provenance.yaml` の既知の制限の両方に書いてある。公式 6 言語以外を投げると、英語 PDF がそのバイト列のまま返ってきて、気づかずに重複が積み上がる。失敗が失敗の顔をしない種類の罠。

スキャン文書がある。 テキスト層を持たない PDF が一定数ある (`yuiseki/un-docs` では 39,363 件中 1,864 件)。上流から取っただけでは本文が取れず、OCR が要る。`ST/AI/189/Add.9/Rev.2` 自体がその例で、pdftotext は 0 行を返した。

地理の列は無い。 文書記号、日付、本文があるだけで、座標も国コードも無い。地名は本文中の文字列としてしか存在しない。

## 取り出し方

区分は split。目録が無いので catalog にはならない。2026-09-30 に curl で確かめた。

API は文書記号 1 件ずつを返す。ここが唯一の取り口である。

| 要求 | 応答 |
|---|---|
| `https://documents.un.org/api/symbol/access?s=A/RES/55/1&l=en&t=pdf` | 200、application/pdf、18,671 バイト |
| `https://documents.un.org/api/symbol/access?s=A/RES/55/2&l=en&t=pdf` | 200、application/pdf、63,788 バイト |
| `https://documents.un.org/api/symbol/access?s=A/RES/55/3&l=en&t=pdf` | 200、application/pdf、26,672 バイト |
| `https://documents.un.org/api/symbol/access?s=A/RES/99/999&l=en&t=pdf` | 200、text/html、1,303 バイト (存在しない) |

`ST/AI/189/Add.9/Rev.2` は 200 で 437,237 バイトの PDF (version 1.3、7 ページ) が返り、302 で `https://documents.un.org/doc/undoc/gen/ns0/000/81/img/ns000081.pdf` へ転送されていた。既存の記述は `Referer` が無いと `/error` を返すとしているが、当日 `Referer` を付けずに投げても同じ 437,237 バイトが返った。挙動が変わったのか、転送を追ったことで結果的に通ったのかは切り分けていない (未確認)。付けておくほうが安全である。

1 文書が 1 ファイルとして分かれているので split に当たる。必要な文書だけを取れる点は満たしているが、条件は「記号を既に知っていること」である。

目録は無い。`https://documents.un.org/api/symbol/search?s=A/RES/55` と `https://documents.un.org/api/documents?q=test` はどちらも 404 で 29 バイトの JSON を返した。日付や主題や発行機関で絞って記号の一覧を得る手段を、当日この API 上に見つけられなかった。したがって「探してから選ぶ」という catalog の条件は満たさない。実際の取得は `A/RES/{会期}/{番号}` のような記号の規則から候補を組み立てて総当たりする形になり、`yuiseki/undocs` もそうしている。

存在しない記号が 404 でなく 200 で返るのは罠である。上の `A/RES/99/999` は 200 の 1,303 バイトで、HTTP の状態符号だけを見ていると成功に見える。総当たりする以上、content-type が application/pdf であることと本文の先頭が `%PDF` であることを毎回確かめないと、HTML のかけらが文書として積み上がる。

個々の PDF は Range を受ける。転送先の `https://documents.un.org/doc/undoc/gen/ns0/000/81/img/ns000081.pdf` は content-length 437,237、accept-ranges: bytes で、`-r 0-1023` が 206 と 1,024 バイトを返した。ただし 1 文書が数十 KB から数百 KB しかないので、部分読みに実用上の意味は無い。

全体の件数は未確認。`yuiseki/un-docs` 側の 39,363 件は派生データの数であって、ODS に何件あるかではない。国連側で数えるには、記号の一覧を返す仕組みか ODS の検索インターフェースの機械可読な出口が要る。当日はどちらも見つからなかった。

`robots.txt` が `Disallow: /api` を含むことは変わらない。総当たりで叩く以上、`yuiseki/undocs` の既定である 2.5 秒間隔と並列 4 を緩めないこと。
