# mapterhorn-japan-bridge

2026-09-28 に読んで確かめた内容。

- `https://data.source.coop/smartmaps/mapterhorn-japan-bridge/japan.pmtiles` (2,006,733,489 バイト、更新 2026-08-09)
- `README.md` (3,181 バイト、更新 2026-08-08)。
- [Mapterhorn](https://mapterhorn.com/) の形式に合わせた日本の地形タイル。README は「暫定の橋渡し製品で、Mapterhorn の公式配布ではない」と書く。上流の日本 1m 標高 (`jpdem1a`) が 2026 年 7 月の国土地理院の北海道の測量更新をまだ取り込んでいないため作った、上流が取り込めば役目を終える、とのこと。
- 作り方: [`hfu/mapterhorn`](https://github.com/hfu/mapterhorn) (mapterhorn/mapterhorn のフォーク) で、smartmaps/japan-geotiff-dem から生成。1m を優先し、1m が無いところは 5m、10m で埋める。
- ビューア: <https://mapterhorn.com/viewer/#url=https://data.source.coop/smartmaps/mapterhorn-japan-bridge/japan.pmtiles>

## 中身 (PMTiles のヘッダとディレクトリを Range 要求で読んだ)

- PMTiles v3、タイル形式 WebP (512x512)、タイル圧縮なし、clustered ではない。
- ズーム 6 から 16。タイル数 20,418 (z16 が 14,592、z15 が 3,648、z14 が 1,056、z13 が 320、z12 が 608)。
- ヘッダの bounds: 経度 135.0 から 142.03125、緯度 40.979898 から 45.0890355。center は z12、(140.9, 41.85)。
- z16 のタイルがある範囲の外接矩形: 経度 140.449 から 141.680、緯度 41.706 から 43.197。座標から見ると北海道の南西部で、北海道全体でも日本全体でもない。
- メタデータは `{"attribution": "国土地理院 (GSI Japan). Processed with Mapterhorn (japan-bridge, interim)."}` だけ。
- エンコーディング: Terrarium。README の式 `elevation = (R*256 + G + B/256) - 32768` で z16 の 1 タイルが 83.6 から 150.3 m、z11 の海の画素は RGB (128,0,0) で 0 m になった。

## 気づいたこと

- README には「z/x/y ごとの `{z}-{x}-{y}.pmtiles` も置いてある」とあるが、一覧には `japan.pmtiles` と `README.md` の 2 つしか無い。
- タイル数が z12 (608) より z13 (320) のほうが少ない。低ズームは広い範囲 (5m / 10m で埋めた部分か) を持ち、高ズームは狭い範囲しか無い、と考えると説明できるが、確かめていない。
- ヘッダの bounds は z16 の実際の範囲よりずっと広い。
- README は「範囲は広がっていき、そのたびに全体を作り直す」と書く。URL は同じでも中身が変わる前提で、使うときは日付を記録する。

## ライセンス

README の記載: 元データは国土地理院 (smartmaps/japan-geotiff-dem 経由)、「測量法に基づく国土地理院長承認（複製）R8JHf51」。タイル化などの梱包部分は CC0-1.0。ただし国土地理院の出典表示の条件は CC0 で消えない、と明記されている。

## 学習で使うなら (案)

- ブラウザの地図 (MapLibre の raster-dem) で地形を見るのに向く。学習の特徴量としては、数値がそのまま入った japan-geotiff-dem のほうが扱いやすい。
- 範囲が北海道南西部に限られる今は、その範囲の題材 (ステップ 1 から 3 の標高、傾斜の特徴量、ステップ 7 の傾斜コスト経路) に使える。
- Terrarium のデコード (式 1 行) を練習する材料として手頃。
