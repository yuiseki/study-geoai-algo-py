# kontur/

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/kontur/`
- Kontur Population (Kontur が配布する世界の人口分布) の GeoPackage と、その gzip と、ダウンロードのログ。

## ファイル

| ファイル | Content-Length (バイト) | Last-Modified | 中身 |
|---|---|---|---|
| kontur_population_20231101.gpkg | 6,711,951,360 | 2023-10-31 17:21:47 GMT | GeoPackage |
| kontur_population_20231101.gpkg.gz | 2,436,991,241 | 2023-10-31 17:21:47 GMT | 上の gzip |
| kontur-dl.log | 650 | 2026-05-01 10:16:18 GMT | 取得時のログ |

- 版はファイル名の `20231101` (2023-11-01)。
- Last-Modified は 2 つとも同じ時刻。wget が配布元の更新時刻をそのまま残したものと考えられる (未確認)。

## kontur_population_20231101.gpkg

- 先頭 100 バイトだけ Range で読んだ。SQLite 3 形式、application_id は `GPKG`、user_version は 10200 (GeoPackage 1.2)。
- ページサイズ 4096 バイト、ページ数 1,638,660。掛けると 6,711,951,360 で Content-Length と一致する。
- レイヤー一覧と件数は 60 秒以内に読めなかった。ogrinfo の `/vsicurl/` は「Range downloading not supported by this server!」で開けない。事情は [gpkg.md](gpkg.md) と同じ。
- H3 の解像度 (Kontur は 400m / 3km / 22km の版を出している) はファイルからは確かめていない。

## kontur_population_20231101.gpkg.gz

- 先頭の gzip ヘッダーに元のファイル名 `kontur_population_20231101.gpkg` と、時刻 2023-10-31 08:25:20 UTC が入っている。
- 末尾 4 バイト (ISIZE、展開後の大きさを 2^32 で割った余り) は 2,416,984,064。.gpkg の大きさ 6,711,951,360 を 2^32 で割った余りと一致する。
- つまり .gpkg と同じものの圧縮版である可能性が高い (中身を展開して照合はしていない)。使うのはどちらか片方でよい。

## kontur-dl.log

中身 (要約):

- `START 2026-05-01T19:08:17+09:00`
- wget の進捗の最後の 2 行 (2,379,850K で 100%、所要 7m32s)
- `WGET DONE` と `GUNZIP DONE` がどちらも `2026-05-01T19:08:17+09:00`
- その時点の `ls -l` (ログ 264 バイト、.gpkg 6,711,951,360、.gpkg.gz 2,436,991,241)
- `DONE`

気づいたこと:

- START、WGET DONE、GUNZIP DONE の時刻がすべて同じ秒。wget は 7m32s かかっているので、時刻を記録した順番か方法がおかしい。ログの時刻は当てにしない。
- gunzip の後も .gz が残っている (`gunzip -k` 相当)。同じ中身を 2 回置いていることになり、約 2.4GB が重複。

## ライセンス

- Kontur のデータセット紹介ページ (kontur.io) には「Creative Commons Attribution International (CC BY) license」とある。版の番号 (4.0 など) と、この 2023-11-01 版に付いた条件は HDX のページが 403 で読めず未確認。
- 2026-10-02 に HDX の API で確かめた。license_id は `cc-by`。版番号の明記は無いまま。詳しくは [../kontur/README.md](../kontur/README.md)。

## 12 ステップで使えそうな場面 (案)

- 5 k-means/DBSCAN: 人口の多いセルを点にして都市圏をまとめる。
- 8 LP/MILP、9 facility location: 需要点 (人口) として施設の配置を解く。国や地域で切り出して小さくしてから使う。
- 1〜3 回帰と木: 他のデータ (WDI など) と結んで説明変数や目的変数にする。
- 4 データリーク: 隣り合う六角形は値が似るので、ランダム分割と空間ブロック分割の差を見る題材になる。
- 6 GB を超えるので、そのまま学習に使うより、国単位などに切り出したものを別に作るのが先。
