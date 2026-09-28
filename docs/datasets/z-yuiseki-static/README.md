# z.yuiseki.net/static

`https://z.yuiseki.net/static/` は nginx の自動一覧 (autoindex) で公開しているファイル置き場。前段に Cloudflare がいる。
構成は 2026-09-28 にディレクトリ一覧をたどって確かめた。

## ディレクトリ

| ディレクトリ | 中身 | 詳細 |
|---|---|---|
| openstreetmap/ | (調査中) | [openstreetmap.md](openstreetmap.md) |
| overture/ | (調査中) | [overture.md](overture.md) |
| cesg/ | (調査中) | [cesg.md](cesg.md) |
| planetarble/ | (調査中) | [planetarble.md](planetarble.md) |
| gsi/ | (調査中) | [gsi.md](gsi.md) |
| mapterhorn/ | (調査中) | [mapterhorn.md](mapterhorn.md) |
| kontur/ | (調査中) | [kontur.md](kontur.md) |
| worldbank/ | (調査中) | [worldbank.md](worldbank.md) |
| natural-earth/ | (調査中) | [natural-earth.md](natural-earth.md) |
| gpkg/ | (調査中) | [gpkg.md](gpkg.md) |
| ucdp/ | (調査中) | [ucdp.md](ucdp.md) |
| csv/ | (調査中) | [csv.md](csv.md) |
| geojson/ | (調査中) | [geojson.md](geojson.md) |
| wikimedia/ | (調査中) | [wikimedia.md](wikimedia.md) |

データセットではないもの:

- `maps/` は地図の配信用素材。フォント (glyph PBF、84 書体)、スタイル JSON、スプライト、MapLibre GL JS 本体、表示テスト用 HTML。
- `tmp/` は一時置き場。発表資料 (`cng-japan-2026/`)、再現用の点群 (`github/odm/`)、中身の無いディレクトリなど。

## 読むときの注意

- 前段の Cloudflare は、あるファイルへの 1 回目の Range 要求に 206 ではなく 200 (ファイル全体の送信) を返すことがある。2 回目からは 206 になる。
  巨大ファイルでこれに当たると、先頭や末尾だけ読むつもりが全体のダウンロードになる。
- なので、読む前に curl で末尾だけを要求し、206 が返るまで最大 3 回試す。`--max-filesize` を付けておくと 200 のときは本文を読まずに止まる。

  ```sh
  curl -sS -r -8 --max-filesize 1048576 --max-time 10 -o /dev/null -w "%{http_code}\n" "$URL"
  ```

- 1 ファイルの調査は 60 秒で打ち切る。読めなかったものは「60 秒以内に読めなかった」と書いて深追いしない。
- DuckDB はこのリポジトリの uv 環境の 1.5.5 を使う (`uv run python`)。1.5.5 より前は使わない。
- 一覧の大きさは nginx の丸めた表示 (`6G` など) で、正確なバイト数ではない。正確な値は HEAD の `Content-Length` で取る。
