# GHSL (Global Human Settlement Layer)

2026-09-30 に読んで確かめた内容。大きさと版は配布サーバへの HEAD、ライセンスは欧州委員会の法的通知の本文。

- 欧州委員会 共同研究センター (JRC) が作る、全球の人の居住の格子データ。
- 案内: `https://human-settlement.emergency.copernicus.eu/`
- 直接配布: `https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/`
- 主な製品は GHS-POP (人口)、GHS-BUILT-S (建物の延床)、GHS-BUILT-H (建物の高さ)、GHS-SMOD (都市化度の区分)。この項目で実際に叩いたのは GHS-POP。

## 過去だけでなく将来がある

GHS-POP の R2023A、モルワイデ図法 1km を 1975 年から 5 年刻みで確かめたところ、12 のエポックがすべて 200 を返した。

```
1975 1980 1985 1990 1995 2000 2005 2010 2015 2020 2025 2030
```

2035 年は無い。つまり 2020 年までが観測に基づく再構成で、2025 年と 2030 年は推計。同じ製品、同じ格子、同じ形式で過去と将来が並ぶので、時系列をそのまま外挿の検証に使える。ファイルの Last-Modified はすべて 2025-01-27 で、将来分が後から足されたのではなく一度に作られている。

| エポック | バイト数 |
|---|---:|
| E1975 | 297,529,739 |
| E2020 | 322,293,568 |
| E2025 | 323,340,844 |
| E2030 | 324,363,154 |

ファイル名の形。

```
GHS_POP_E{年}_GLOBE_R2023A_54009_1000/V1-0/GHS_POP_E{年}_GLOBE_R2023A_54009_1000_V1_0.zip
```

`54009` は EPSG:54009 (World Mollweide)、`1000` は 1km。ページの記述では解像度と図法の組み合わせが製品ごとに違い、すべての組み合わせがあるわけではない。

版は R2020A、R2023A、R2024A が案内ページに出てくる。ここで確かめたのは R2023A。

## ライセンス

配布ページの表記。

> © European Union, 1995-2025. Reuse of this data is authorised with proper acknowledgment of the source.

その根拠になる欧州委員会の法的通知 (`https://commission.europa.eu/legal-notice_en`) の本文。

> Unless otherwise indicated (e.g. in individual copyright notices), content owned by the EU on this website is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) licence. This means that reuse is allowed, provided appropriate credit is given and changes are indicated.

CC BY 4.0。share-alike は無い。ただし同じ通知が続けて、EU が権利を持たない部分は別に権利処理が要ると書いている。

> To use or reproduce content that is not owned by the EU, you may need to seek permission directly from the rightholders.

## 気をつけること

ダウンロード画面が JavaScript で組み立てられる。`download.php?ds=pop` の HTML には製品の一覧も年の一覧も入っておらず、選択肢は画面側で作られる。機械で取るなら上の命名規則で直接叩くほうが確実で、実際この項目の数字はそうやって取った。どのエポックがあるかは、叩いてみるまで分からない。

配布ページに GADM のライセンスページ (`https://gadm.org/license.html`) へのリンクがある。GADM は商用利用を認めない非開放ライセンスなので、GADM 由来の境界を使う製品があるなら、その製品だけ扱いが違うことになる。どの製品がそうなのかはページが JavaScript で描くため未確認。GHSL の製品を集計や境界の切り出しに使うときは、その製品の技術資料で出どころを確かめる必要がある。

人口の格子は推計であって観測ではない。2020 年以前も含めて、国勢調査の値を建物の分布で空間的に割り振ったもの。日本のように小地域の国勢調査境界が公開されている国 (`yuiseki/estat-boundary-2020`) では、集計値はそちらのほうが原典に近い。GHSL の利点は全球で同じ方法と同じ格子であること。

図法がモルワイデ。緯度経度の格子ではないので、他のデータと重ねるときは再投影が要る。面積が保存される図法なので、面積あたりの集計には向く。

## 取り出し方

split。全球 1 枚のほかにタイル分割が置いてあり、必要なタイルだけ引ける。ファイルは zip なので中の部分読みはできず、COG ではない。2026-09-30 に実測した。

GHS-POP R2023A のモルワイデ 1km、E2020 で確かめた。全球 1 枚はこれ。

| 項目 | 値 |
|---|---|
| URL | `.../GHS_POP_E2020_GLOBE_R2023A_54009_1000/V1-0/GHS_POP_E2020_GLOBE_R2023A_54009_1000_V1_0.zip` |
| 応答 | HTTP/2 200、`content-type: application/zip`、`accept-ranges: bytes` |
| 大きさ | 322,293,568 バイト |
| Range 要求 | `curl -r 0-1023` が 206 と 1,024 バイト |

同じ `V1-0/` の下に `tiles/` があり、こちらは Apache の自動生成一覧が返る。実際に取って `R{行}_C{列}.zip` の形を数えると 375 個あった。分割の単位はこのタイルで、1 枚が 2MB 前後。

| 項目 | 値 |
|---|---|
| URL | `.../V1-0/tiles/GHS_POP_E2020_GLOBE_R2023A_54009_1000_V1_0_R7_C22.zip` |
| 応答 | HTTP/2 200、`accept-ranges: bytes` |
| 大きさ | 2,048,895 バイト |
| Range 要求 | `curl -r 0-1023` が 206 と 1,024 バイト |
| 先頭 | `PK\x03\x04`、最初のエントリ名がタイル名 `GHS_POP_E2020_GLOBE_R2023A_54009_1000_V1_0_...` で始まる |

どちらも Range は 206 を返すが、zip なので意味のある部分読みにはならない。中央ディレクトリは末尾にあり、GeoTIFF は deflate の中に入っているので、COG のようにヘッダだけ読んで必要なタイルを抜く使い方はできない。ESA WorldCover との一番の違いがここで、あちらは裸の COG、こちらは zip。

したがって、必要な範囲が狭ければ 375 枚のタイルから該当するものだけを落とすのが正しい引き方になる。ただしタイルの行と列がどの緯度経度に当たるかを示す格子ファイルは確かめていないので 未確認。確かめるには JRC が配っているタイル区画の Shapefile を見るか、タイルを 1 枚展開して GeoTIFF のジオリファレンスを読む必要がある。

エポックは 1975 から 2030 まで 12 個あるが、これは時間の分割であって空間の分割ではない。1 エポック 1 ファイル (またはその 375 タイル) という構造は全エポックで同じ。
