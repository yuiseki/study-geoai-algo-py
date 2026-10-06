# OpenFlights

2026-10-06 に読んで確かめた内容。日付は GitHub の commits API で、データファイルごとに
最後に中身が変わったコミットを引いた値。規約と件数は配布元の記述を引用した。

- 案内: `https://openflights.org/data.php`
- 配布: `https://github.com/jpatokal/openflights` の `data/`
- 空港の [OurAirports](../ourairports/README.md) と比べる用途で調べた。結論はそちらを使う。

## 古い

この項目を立てた理由がこれ。名前が似ているので取り違えが起きる。

配布元が自分でそう書いている。

> As of January 2017, the OpenFlights Airports Database contains over 10,000 airports,
> train stations and ferry terminals spanning the globe

> Warning: The third-party that OpenFlights uses for route data ceased providing updates
> in June 2014. The current data is of historical value only.

路線は third-party の供給が 2014 年 6 月に止まっており、配布元自身が
「historical value only」と書いている。

GitHub のファイルごとの最終更新も、これと整合する。

| ファイル | 最後に中身が変わったコミット |
|---|---|
| airports.dat | 2019-05-13 (座標の修正) |
| airports-extended.dat | 2019-05-13 (同じコミット) |
| routes.dat | 2017-02-02 |
| airlines.dat | 2017-02-02 |
| planes.dat | 2019-05-07 |
| countries.dat | 2020-01-31 |

リポジトリ自体は動いている (2026-09-21 に push) が、それは website のコードの話。
`data/README.md` は「これは live data のスナップショットである」と書き、
pull request を受け付けないとしている。

> Since these files are only snapshots of live data, pull requests are not accepted.

live data がどれだけ更新されているかは未確認。少なくとも GitHub に置かれた配布物は、
空港が 2019 年、路線が 2017 年のコミットで止まっている。

## OurAirports との比較

| | OurAirports | OpenFlights |
|---|---|---|
| 空港 | 86,205 (2026-10-06 の配布元の表示) | 10,000 超 (2017 年 1 月時点と明記) |
| 更新 | 毎晩 | 上の表のとおり |
| ライセンス | パブリックドメイン | ODbL |
| 路線 | 無し | 67,663 便 / 3,321 空港 / 548 航空会社 (2014 年 6 月) |

OpenFlights の空港データは DAFIF (2006) と OurAirports 由来で、一部が未検証のユーザー投稿。
上流が OurAirports なので、OurAirports を使えば同じものが新しい状態で手に入る。

OpenFlights にしか無いものが一つある。路線。どの空港とどの空港が直行便で結ばれているか
というグラフは、地名の共起として素材になる。ただし 2014 年の状態であることを明示して使う。

## ライセンス

リポジトリ全体は AGPL-3.0。これは website のコードに当たる。

`data/LICENSE` は別に置かれていて、ODC Open Database License (ODbL) の全文 (25,313 バイト)。
データに当たるのはこちら。

ODbL には share-alike がある。派生データベースを配るときは同じ条件が付く。
OurAirports のパブリックドメインと混ぜると、混ぜた先が ODbL に引きずられる。

## 取り出し方

区分は whole。`data/` の .dat を個別に落とす。最大の `routes.dat` で 2,377,148 バイト、
`airports-extended.dat` で 1,670,162 バイト。全部でも 30MB に満たない。

`DAFIFT_0610_ed6.zip` (24,400,351 バイト) が同じディレクトリにある。
2006 年の DAFIF のアーカイブで、米国が公開を止めた当時のもの。

## 気をつけること

名前の取り違えが実際に起きている。2026-09-25 にこの比較を報告した 5 日後、
「OurAirports が古くなっているはず」という前提で話が進んだ。古いのはこちら。
`OpenAirports` という存在しない名前も同じ日に出ている。

リポジトリの `pushed_at` を鮮度と読むと間違える。2026-09-21 に push されているが、
データファイルは 2017 年から 2020 年で止まっている。鮮度はファイル単位で見る。
