# csv

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/csv/`
- ファイルは 1 つだけ。Geo-PKO (国連平和維持活動の部隊展開地点のデータセット) の版 2.3。版はファイル名 (`Geo_PKO_v2_3`) から。
- 1 行は「あるミッションの、ある年月の、ある地点への展開」。`source` 列は国連の配置図の番号 (`Map no. 4121 Rev. 20` など) で、配置図を読み取って作られたデータとわかる。
- ディレクトリ名は `csv/` だが、中身は Geo-PKO だけ。名前から中身は推測できない。

## ファイル

| ファイル | 形式 | 大きさ (Content-Length) | Last-Modified |
|---|---|---|---|
| `Geo_PKO_v2_3_location_map.csv` | CSV (UTF-8, BOM 付き) | 12,500,418 バイト | 2025-10-04 |

## 中身 (DuckDB 1.5.5 で集計)

- 21,243 行。完全に同じ行はない。
- 列は 122 個。主なもの:
  - 出典と時間: `source`, `mission`, `year`, `month` (整数), `date` (DATE。月初日)
  - 場所: `location`, `geosplit`, `country`, `latitude`, `longitude` (実数), `old_xy`, `geocomment`, `zone.de.confidence`, `adm1.id`, `adm1.name`, `prioid`
  - 部隊の規模: `battalion`, `company`, `platoon` (実数), `other.size`, `no.troops` (文字列。`unknown` が 537 行ある)
  - 部隊の種類 (多くは 0/1 の整数): `inf`, `fpu`, `res`, `fp`, `eng`, `sig`, `trans`, `riv`, `he.sup`, `sf`, `med`, `maint`, `recon`, `avia`, `mp`, `uav`, `armor` など
  - 派遣国: `no.tcc`, `nameoftcc_1` から `nameoftcc_17`, `notroopspertcc_1` から `notroopspertcc_17`, `tcc1` から `tcc17`
  - その他: `unpol.dummy`, `unmo.dummy`, `hq`, `lo`, `jmco`, `security.group.dummy`, `comments`, `cow_code`, `gwno`
- 期間: `date` の最古 1994-01-01、最新 2024-12-01。
- 範囲: 緯度 -25.97 から 45.81、経度 -91.52 から 126.46。緯度の欠損は 0 行。
- ミッションは 52 通り、国は 45 通り、地点名 (`location`) は 1,160 通り。

ミッションの上位 (行数, 年の範囲):

| mission | 行数 | 年 |
|---|---|---|
| MONUSCO | 1,788 | 2010-2024 |
| MONUC | 1,667 | 1999-2010 |
| UNOCI | 1,624 | 2004-2017 |
| UNIFIL | 1,464 | 1994-2024 |
| UNMIL | 1,260 | 2003-2018 |
| UNAMID | 1,236 | 2008-2020 |
| UNMISS | 1,104 | 2011-2024 |
| MINURSO | 1,054 | 1995-2024 |

国の上位: DRC 3,174 / Sudan 2,548 / Ivory Coast 1,627 / Lebanon 1,496 / Liberia 1,382 / Angola 1,305 / Haiti 1,156 / South Sudan 1,145 / Cyprus 992 / Western Sahara 958。

`no.troops` の上位: `150` が 6,118 / `0` が 6,033 / `35` が 1,712 / `650` が 1,271 / `300` が 1,094 / `unknown` が 537。

## 気をつけること

- `no.troops` や `notroopspertcc_*` は数値でなく文字列として読まれる (`unknown` などが混ざるため)。数値にするなら変換と欠損の扱いを決める。
- 部隊人数 150 や 650 が多いのは、配置図の部隊記号 (中隊や大隊) を標準の人数に置き換えている可能性がある。確かめていない。
- 同じ地点が月ごとに繰り返し現れるので、行を無作為に分けると同じ地点が学習と検証の両方に入る。
- ライセンス: 未確認 (ファイルにも置き場にも記載はない)。

## 12 ステップでの使い道 (案)

- 5 k-means / DBSCAN: ミッションごとの展開地点のまとまりを出す。
- 9 facility location: 展開地点を候補地、紛争の出来事 (`ucdp/` の GED) を需要点として置き、何か所に置けば近くを覆えるかを解く。
- 4 データリーク: 同じ地点の繰り返しがある状態での分割の仕方を試す題材。
- 1, 2 回帰 / 決定木: 部隊の種類や派遣国数から部隊規模を当てる (規模の値が記号由来なら意味が薄い点に注意)。
