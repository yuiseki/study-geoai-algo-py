# World Bank Data360

2026-09-30 に読んで確かめた内容。件数はこの日に API を叩いて数えたもの。

- 世界銀行が各国際機関の指標をまとめて配信している新しい基盤。
- 入口: `https://data360.worldbank.org/`
- API: `https://data360api.worldbank.org/`
- OpenAPI 定義: `https://github.com/worldbank/open-api-specs` の `Data360 Open_API.json`
- 親項目は [README.md](README.md)。

## 世界銀行のデータではない

これが一番大事な点。Data360 は世界銀行のデータを配るところではなく、
各機関の指標を一つの API に集めたところ。

`searchv2` に `series_description/database_id` のファセットを投げると、
指標 12,510 件が 170 のデータベースに分かれていた。上位を挙げる。

| データベース | 指標 | 出どころ |
|---|---:|---|
| WB_WDI | 1,546 | 世界銀行 |
| IMF_BOP | 1,147 | IMF |
| WB_EDSTATS | 1,073 | 世界銀行 |
| WB_ES | 585 | 世界銀行 |
| IMF_IFS | 496 | IMF |
| WB_GS | 364 | 世界銀行 |
| WB_FINDEX | 281 | 世界銀行 |
| IMF_GFS_SOO | 219 | IMF |
| BS_SGI | 194 | Bertelsmann Stiftung |
| WB_HNP | 193 | 世界銀行 |
| WEF_GCI | 170 | 世界経済フォーラム |
| FAO_AS | 106 | FAO |
| VDEM_CORE | 85 | V-Dem |
| OWID_CB | 77 | Our World in Data |
| OECD_IDD | 54 | OECD |
| FH_FIW | 43 | Freedom House |

世界銀行のドメインで配られているからといって世界銀行のライセンスが当たるわけではない。

## ライセンスは半分が外部

上位 30 のデータベースについて、指標を 1 件ずつ取ってメタデータのライセンス欄を読んだ。
結果は [data360-licences.tsv](data360-licences.tsv)。

| 記載 | 件数 |
|---|---:|
| License Specified Externally | 12 |
| CC BY 4.0 | 11 |
| CC BY-4.0 | 1 |
| CC-BY 4.0 | 1 |
| CC BY-NC-ND | 1 |
| None | 1 |
| 記載無し | 1 |
| この指標の記述が返らない | 2 |

CC BY 4.0 を指すものが 13、外部を指すものが 12。ほぼ半々だった。

`License Specified Externally` は「外部のサイトを見て同意してから使え」という意味で、
実際の条件は書かれていない。IMF の 4 つは `https://www.imf.org/external/terms.htm`、
OECD は `https://www.oecd.org/termsandconditions/`、V-Dem は FAQ ページを指す。
API からは条件が読めない。

`WEF_TTDI` (世界経済フォーラムの旅行・観光開発指数) は CC BY-NC-ND で、
非営利かつ改変不可。世界銀行の API から同じ形で取れるのに、他の指標と混ぜて
再配布することができない。

`WB_ESG` は名前が WB で始まるのにライセンス名が `None`、URI は
`https://www.iea.org/terms` で国際エネルギー機関を指している。
接頭辞から発行元を推測すると間違える。

`WB_IDS` はライセンスの記載自体が無かった。`IMF_BOP` と `ITU_DH` は
`indicators` が返す指標 ID を `metadata` に渡しても、その ID の記述が返ってこない。
指標として存在するのに条件が読めない状態で、記載無しとは別の困り方になる。

## CC BY の書き方が揃っていない

同じ CC BY 4.0 を指す名前が三通りあった。

| 書かれ方 | 例 |
|---|---|
| `CC BY-4.0` | WB_WDI |
| `CC BY 4.0` | WB_EDSTATS ほか多数 |
| `CC-BY 4.0` | WB_SPI |

`uri` はどれも `https://creativecommons.org/licenses/by/4.0/` で揃っているので、
名前ではなく URI で照合する。

## 追加条項の有無も揃っていない

ライセンスの `note` に紛争解決の追加条項 (WIPO 調停と UNCITRAL 仲裁。全文は
[README.md](README.md) のライセンスの節) が入っているものと、`null` のものがある。
CC BY を名乗る 13 件のうち、10 件が `note` を持ち 3 件が持たない。
持たないのは WB_WDI、FAO_AS、OWID_CB だった。

同じ CC BY 4.0 でも、追加条項が付いているかどうかが記載から分かれる。
識別子だけを見て一括りにはできない。

## データの取り方

```
https://data360api.worldbank.org/data360/data
  ?DATABASE_ID=WB_WDI&INDICATOR=WB_WDI_SP_POP_TOTL&REF_AREA=JPN
  &timePeriodFrom=2020&timePeriodTo=2022
```

応答は SDMX に近い形。`OBS_VALUE`、`TIME_PERIOD`、`REF_AREA` に加えて
`SEX`、`AGE`、`URBANISATION`、`COMP_BREAKDOWN_1..3` の分解軸が常に付く。
使わない軸には `_T` (合計) や `_Z` (該当なし) が入る。

Indicators API v2 の平たい `{country, date, value}` とは形が違う。
指標 ID も `SP.POP.TOTL` ではなく `WB_WDI_SP_POP_TOTL` と接頭辞が付く。

1 回の呼び出しは最大 1,000 件。続きは `skip` で送る。

| エンドポイント | 方式 | 必須の引数 |
|---|---|---|
| `/data360/data` | GET | `DATABASE_ID` |
| `/data360/indicators` | GET | `datasetId` |
| `/data360/disaggregation` | GET | `datasetId` |
| `/data360/metadata` | POST | body に `query` (OData 形式) |
| `/data360/searchv2` | POST | body に検索条件 |

`/data360/indicators?datasetId=WB_WDI` は指標 ID の配列を返す。1,499 件だった。
ファセットが示す 1,546 件とは一致しない。ずれはもっと大きくなることもあり、
IMF_BOP はファセットが 1,147、`indicators` が 5,209 だった。
どちらを母数にするかは用途で選ぶ。両方を記録しておくのが安全。

`/data360/metadata` の `$filter` は効きが緩い。
`$filter=series_description/idno eq 'WB_WDI_SP_POP_TOTL'` を投げたのに、
返ってきた 5 件のうち一致するのは 1 件だけで、残りは WB_GS と WB_HNP の
別の人口指標だった。1 件を指定したつもりで別のデータベースの値を読む事故が起きる。
`idno` と `database_id` を応答側で確かめる。

## 一括配布は無い

`/data360/databases` や `/data360/datasets` は空を返す。OpenAPI 定義にも
一括ダウンロードのエンドポイントは無い。手元に置きたいなら
`/data360/data` を 1,000 件ずつ回すか、旧来の一括 zip
([README.md](README.md) の一括配布の節) を使う。

## 取り出し方

区分は catalog。指標を検索して絞り込んでから、必要な国と年だけ引く。

| 手段 | 実測 |
|---|---|
| `searchv2` | 12,510 指標 / 170 データベースをファセットで数えられる |
| `indicators` | WB_WDI で 1,499 件の ID |
| `data` | 1 回 1,000 件、`skip` で続き |
| ダンプ | 無い |

認証は要らない。ただしライセンスがデータベースごとに違うので、
引いたものをそのまま貯めると、手元で条件の違うものが混ざる。
`metadata` のライセンス欄も一緒に取って残しておく。
