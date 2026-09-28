# OpenCelliD

2026-09-28 に読んで確かめた内容。

- ダウンロードページ: <https://www.opencellid.org/downloads.php>
- 形式の説明: <https://docs.opencellid.org/docs/downloads/database-format>
- 運営: Unwired Labs

## 中身

携帯電話の基地局 (セル) の推定位置を、利用者の観測から集めたもの。国別のファイル、全世界のファイル、日ごとの差分がある。

- ファイルは `cell_towers.csv` と、差分の `cell_towers_diff-*.csv.gz`。
- 含まれるのは、直近 18 か月に観測されたセルだけ。それより古いものは API でしか引けない。
- 毎日 02:00 GMT までに作り直される。
- 観測に頼っているので、全基地局の台帳ではない。地域、事業者、方式で網羅度が違う。

列:

| 列 | 型 | 意味 |
|---|---|---|
| radio | string | 方式 (GSM, UMTS, LTE, CDMA など) |
| mcc | integer | 国番号 (Mobile Country Code) |
| net | integer | 事業者番号 (MNC、CDMA は SID) |
| area | integer | LAC、LTE は TAC、CDMA は NID |
| cell | integer | セル ID |
| unit | integer | UMTS の PSC、LTE の PCI。GSM と CDMA は空 |
| lon, lat | double | 推定位置 (度) |
| range | integer | 推定のカバー半径 (m) |
| samples | integer | そのセルに割り当てた観測数 |
| changeable | integer | 廃止。常に 1 |
| created, updated | integer | 初めて見た時刻と最後に見た時刻 (Unix 秒、UTC) |
| averageSignal | integer | 廃止。常に 0 |

## 取り方

ダウンロードには API アクセストークンが要る。アカウントを作ってトークンを発行し、ダウンロードページに入力するとリンクが出る。
このため、ファイルの大きさや件数はまだ確かめていない。

## 気をつけること

- ライセンスは CC BY-SA 4.0 (API の結果、一括ダウンロード、日次差分のすべて)。
  使うときは OpenCelliD の名前、出典へのリンク、ライセンスへのリンクを見える場所に出し、手を加えたならその旨も書く。
- 位置は推定値で、実際の基地局の場所ではない。`range` と `samples` で確からしさを見る。
- source.coop の [smartmaps/opencellid](../source-coop-smartmaps/opencellid.md) に、これを元にしたらしい PMTiles がある。

## 学習ステップとの対応 (案)

- 5: 基地局の点を DBSCAN でまとめる。
- 9: 既存の基地局を供給側、[Ookla の速度タイル](../ookla-speedtest/README.md) を需要側にして配置問題を作る。
