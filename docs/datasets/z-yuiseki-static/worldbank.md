# worldbank/

2026-09-28 に読んで確かめた内容。

- `https://z.yuiseki.net/static/worldbank/`
- 世界銀行の World Development Indicators (WDI) から、国別・年別の指標を抜き出した Parquet が 2 つ。どちらも小さいので全体をダウンロードして DuckDB 1.5.5 で集計した。

## ファイル

| ファイル | Content-Length (バイト) | Last-Modified | 行数 |
|---|---|---|---|
| wdi_basic_annual.parquet | 671,153 | 2026-05-31 07:53:15 GMT | 102,623 |
| wdi_indicators.parquet | 83,311 | 2026-05-31 07:28:58 GMT | 10,205 |

## 列 (2 つとも同じ縦持ちの形)

| 列 | 型 |
|---|---|
| iso3 | VARCHAR |
| year | BIGINT |
| indicator | VARCHAR (WDI の指標コード) |
| value | DOUBLE |

- value に NULL は無い (値の無い年は行ごと無い)。
- Parquet のメタデータは pandas と Arrow のもので、元の取得日や WDI の版の記録は無い。基準日は未確認。

## wdi_basic_annual.parquet

- 国と地域 217 (ISO3。`CHI` Channel Islands や `XKX` Kosovo も含む)。WLD などの集計地域は入っていない。
- 年は 1990〜2024 の毎年。2024 年は 2,273 行で、他の年 (2,679〜3,072 行) より少ない。
- 指標は 16。

| 指標コード | 行数 | 国の数 | 年 |
|---|---|---|---|
| AG.LND.FRST.ZS | 7,061 | 214 | 1990〜2023 |
| AG.SRF.TOTL.K2 | 7,286 | 216 | 1990〜2023 |
| EN.ATM.CO2E.PC | 6,437 | 211 | 1990〜2020 |
| IT.NET.USER.ZS | 6,214 | 213 | 1990〜2024 |
| NY.GDP.MKTP.CD | 7,206 | 214 | 1990〜2024 |
| NY.GDP.PCAP.CD | 7,206 | 214 | 1990〜2024 |
| NY.GNP.PCAP.CD | 6,782 | 207 | 1990〜2024 |
| SE.ADT.LITR.ZS | 1,013 | 162 | 1990〜2024 |
| SH.DYN.MORT | 6,860 | 196 | 1990〜2024 |
| SI.POV.GINI | 2,237 | 171 | 1990〜2024 |
| SL.UEM.TOTL.ZS | 6,349 | 187 | 1991〜2024 |
| SP.DYN.LE00.IN | 7,595 | 217 | 1990〜2024 |
| SP.DYN.TFRT.IN | 7,595 | 217 | 1990〜2024 |
| SP.POP.GROW | 7,592 | 217 | 1990〜2024 |
| SP.POP.TOTL | 7,595 | 217 | 1990〜2024 |
| SP.URB.TOTL.IN.ZS | 7,595 | 217 | 1990〜2024 |

- 識字率 (SE.ADT.LITR.ZS) とジニ係数 (SI.POV.GINI) は欠けが多い。

## wdi_indicators.parquet

- 国と地域 217 (wdi_basic_annual と同じ集合)。
- 年は 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023 の 8 時点だけ。
- 指標は 6: AG.SRF.TOTL.K2, NY.GDP.MKTP.CD, NY.GDP.PCAP.CD, SP.POP.GROW, SP.POP.TOTL, SP.URB.TOTL.IN.ZS。
- 10,205 行すべてが wdi_basic_annual に同じ (iso3, year, indicator) で存在し、値も一致した。つまり wdi_basic_annual の部分集合で、独自の情報は無い。

## 異常: EN.ATM.CO2E.PC の値

- (iso3, year, indicator) の組は 102,528 通りで、行数 102,623 より 95 少ない。重複はすべて EN.ATM.CO2E.PC で、5 か国 (PSE, AND, COD, ROU, TLS) の 1990〜2013 年の一部、計 190 行 (95 組)。重複した組の値は 2 つとも違う。例: ROU 2004 年は 4.52 と 444.86。
- 重複していない国も値が指標名 (1 人あたり CO2 排出量) と合わない。JPN は 1990 年 1018.62、2010 年 739.06、2020 年 64.25。USA は 1990 年 2223.83、2020 年 104.26。全体の中央値は 135.10、最大は 7201.70。
- 原因は調べていない。この指標は使わないか、WDI から取り直すのが安全。他の指標は JPN で見た限りもっともらしい (SP.POP.TOTL 1990 年 123,478,000、SP.DYN.LE00.IN 2023 年 84.04)。

## ライセンス

- 世界銀行のデータカタログの WDI のページに「This dataset is licensed under Creative Commons Attribution 4.0」とある。このファイルの抜き出し方に固有の条件があるかは未確認。

## 12 ステップで使えそうな場面 (案)

- 1 線形回帰: 1 人あたり GDP から平均寿命や乳幼児死亡率を説明する。対数変換の効き方を見る。
- 2〜3 Random Forest / XGBoost: 横持ちにして多数の指標から 1 つを予測する。欠けの多い列をどう扱うかも題材になる。
- 4 データリーク: 同じ国の別の年が訓練とテストにまたがると甘く出る。国単位の GroupKFold や時系列分割と比べる。
- 5 k-means、6 PCA: 国を指標の組で分類する、指標の次元を縮める。
- 11 SHAP: 木モデルの説明に使う。
- 地図と結ぶなら natural-earth/ の iso_a3 と iso3 で結合できる。WDI の 217 のうち ne_50m で 212、ne_110m で 167 が一致した。Natural Earth 側は France と Norway の iso_a3 が -99 なので、そのままでは落ちる ([natural-earth.md](natural-earth.md))。
