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

## 取り出し方

未確認。一括ダウンロードにも API にもトークンが要り、2026-09-30 の時点で持っていないので実測できていない。確かめるにはアカウントを作って API アクセストークンを発行する必要がある。

トークン無しで分かったところまでを書く。

| 要求 | 応答 |
|---|---|
| `curl -sI https://www.opencellid.org/downloads.php` | 200。前段は Cloudflare。本文はトークン入力欄で、リンクは出ない |
| `curl 'https://opencellid.org/ocid/downloads?token=&type=full&file=cell_towers.csv.gz'` | 200 だが本文は 43 バイトの `{"status":"error","message":"INVALID_DATA"}` |
| 同じ URL に `curl -r 0-1023` | 200、43 バイト。エラー応答が返っただけで、Range の可否は分からない |
| `curl 'https://opencellid.org/cell/getInArea?key=&BBOX=139.7,35.6,139.8,35.7&format=json'` | 401、`{"error":"API Key not known: ","code":2}` |

ダウンロードページの本文にはこう書いてある。

> Download computed cell data for individual countries or the world. Enter your API access token to see download links.

> Country exports, the worldwide database and daily changes are available with an API access token.

文面どおりなら split になる。国別の書き出しがあり、全世界のファイルもあり、日ごとの差分もある。分割の単位は国 (列の `mcc` が Mobile Country Code なので、おそらく MCC 単位) で、個数は国の数ぶん。ただしこれはページの記述であって、こちらで数えたものではない。区分は実測に基づくという約束に従い、確かめるまでは 未確認 とする。

API のほうは catalog に近い使い方ができそうに見える。ドキュメントの目次に「List cells in an area」「Count cells in an area」があり、範囲を指定して引く口がある。ただし上のとおり key 無しでは 401 で、範囲指定が実際にどこまで効くかは確かめていない。

確かめるのに要るもの。

- OpenCelliD のアカウントと API アクセストークン。
- トークンを入れた状態で `downloads.php` が出す実際のリンク。そこで初めて、国別ファイルの一覧、それぞれの大きさ、全世界ファイルの大きさ、Range が 206 を返すかどうかが測れる。
