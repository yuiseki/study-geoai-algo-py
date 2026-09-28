# 台東区コミュニティバス「めぐりん」GTFS (公共交通オープンデータ)

2026-09-28 に取得して確かめた内容。

- データセット: <https://ckan.odpt.org/dataset/tokyo_taito_city_megurin_ccby40>
- 公開 URL (登録不要): `https://api-public.odpt.org/api/v4/files/odpt/TokyoTaitoCity/megurinCCBY40.zip?date=20251028`
- 配布: 公共交通オープンデータセンター (ODPT)。公開者は台東区。作成は株式会社アチピレーションテクノロジー (`feed_info.txt`)

## 中身

GTFS-JP の zip 1 つ (78,030 バイト)。版は `20250801_MEG001`、有効期間は 2025-08-10〜2026-12-31。

| ファイル | 行数 (見出し除く) | 中身 |
|---|---:|---|
| routes.txt | 4 | 北めぐりん (根岸まわり)、北めぐりん (浅草まわり)、南めぐりん、東西めぐりん |
| stops.txt | 128 | 停留所の名前と位置 |
| trips.txt | 290 | 便 |
| stop_times.txt | 8,261 | 便ごとの停車時刻。最初は 06:59、最後は 20:55 |
| shapes.txt | 2,637 | 路線の形 |
| calendar.txt | 2 | 平日と土日祝 |
| calendar_dates.txt | 54 | 祝日などの例外日 |
| transfers.txt | 24 | 乗り換え |

路線と曜日ごとの便数:

| 路線 | 平日 | 土日祝 |
|---|---:|---:|
| 北めぐりん (根岸まわり) | 31 | 27 |
| 北めぐりん (浅草まわり) | 57 | 32 |
| 南めぐりん | 42 | 30 |
| 東西めぐりん | 41 | 30 |

## 気をつけること

- ライセンスは CC BY 4.0 (データセットのページの記載)。同じ組織に「公共交通オープンデータ基本ライセンス」版のデータセット (`tokyo_taito_city_megurin`) もあるので、使うのは CC BY 4.0 版にする。
- `trips.txt` の `block_id` は 290 便すべて空。どの車両がどの便を走るかは書かれていない。営業所 (`jp_office_id`) は入っている。
- 便の ID に日本語 (`TRP_000001_土日祝001`) が入っている。
- 停留所名には路線内の番号が付いていて (`① 台東病院`)、128 停留所の名前はすべて違う。同じ場所の停留所を路線をまたいでまとめるには、名前ではなく位置で突き合わせる必要がある。

## これを使っているもの

[poc-stac-tokyo-taito](https://github.com/yuiseki/poc-stac-tokyo-taito) が、この GTFS から時刻ごとのバスの位置を補間して、状態タイル (MVT) として配信している。
ただしリポジトリには GTFS も取得スクリプトも入っていない。手元のクローンの `src/poc_stac_tokyo_taito/data/megurin/` にだけあり、上の公開 URL の zip と 13 ファイルすべてバイト単位で一致した。
同じ PoC は台東区の施設 CSV を東京都オープンデータカタログから取っている。そちらは [tokyo-ckan](../stac/tokyo-ckan.md) の組織 `t131067`。

## 学習ステップとの対応 (案)

- 10 CP-SAT / scheduling: `block_id` が空なので、便の始発と終着の時刻と停留所から「最少の車両で全便を回す割当」(vehicle scheduling) を解く。休憩や乗務時間の制約を足すと乗務員の勤務表にもなる。
- 7 Dijkstra / A*: 停留所と停車時刻から時刻付きのグラフを作り、乗り換えを含む最短時間の経路を探す。
- 9 facility location: 停留所の徒歩圏 (300〜500m) で人口メッシュをどれだけ覆えているかを測り、停留所を足す場所を選ぶ。

再現できるように、この zip を中身を変えずに <https://z.yuiseki.net/static/gtfs/odpt/TokyoTaitoCity/megurinCCBY40/20251028/megurinCCBY40.zip> に置いた。詳しくは [東京 23 区のバスの GTFS](../tokyo-gtfs/README.md)。
