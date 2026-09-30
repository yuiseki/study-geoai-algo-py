# GEBCO (GEBCO_2024 Grid)

2026-09-30 に読んで確かめた内容。大きさとファイル構成は CEDA の配布ディレクトリへの HEAD と Range による実測、格子の寸法は同じディレクトリに置かれている GEBCO_Grid_Documentation.pdf、ライセンスは gebco.net の Terms of use ページと配布元の README。

- 案内: `https://www.gebco.net/data-products/gridded-bathymetry-data`
- 配布: `https://dap.ceda.ac.uk/bodc/gebco/global/` (CEDA)。2024 年に BODC の Published Data Library から移された。
- 中身は全球の水深と標高を 15 秒間隔で繋いだ地形モデル。IHO と IOC の下の GEBCO と、日本財団の Seabed 2030 プロジェクトが作っている。
- planetarble は `configs/base/pipeline.yaml` の `processing.gebco_year: 2024` と、`configs/base/assets.yaml` の `gebco_latest_grid` (URL は `https://dap.ceda.ac.uk/bodc/gebco/global/gebco_2024/ice_surface_elevation/netcdf/GEBCO_2024_CF.nc`) でこれを指している。legacy の BMNG 経路で使う想定。

CEDA の `https://dap.ceda.ac.uk/bodc/gebco/global/` には `gebco_2014` から `gebco_2026` まで 10 版が並んでいる。GEBCO_2024 は最新ではない。gebco.net の現在の案内ページは GEBCO_2026 を主役にしている。

## 中身 (GEBCO_Grid_Documentation.pdf の本文)

> The GEBCO_2024 Grid was released in July 2024. It provides global coverage of elevation data, in meters, on a 15 arc-second interval geographic grid and consists of 43200 rows x 86400 columns, giving 3,732,480,000 data points. The data values are pixel-centre registered i.e. they refer to elevations, in meters, at the centre of grid cells.

2 つの版がある。`ice_surface_elevation` (氷の表面を含む) と `sub_ice_topography_bathymetry` (グリーンランドと南極の氷の下)。さらに `type_identifier_grid` があり、各格子の値がどの種類の元データに由来するかを示す。planetarble が指しているのは `ice_surface_elevation` のほう。

## 配布されているファイル (実測)

`gebco_2024/ice_surface_elevation/` の下に `netcdf/`、`geotiff/`、`esri_ascii_raster/` の 3 つ。

| ファイル | バイト数 |
|---|---:|
| `netcdf/GEBCO_2024_CF.nc` (全球 1 枚) | 7,466,018,396 |
| `geotiff/gebco_2024_geotiff.zip` (8 枚まとめて) | 4,257,768,030 |
| `geotiff/gebco_2024_n90.0_s0.0_w90.0_e180.0.tif` (日本を含む) | 933,255,948 |
| `netcdf/GEBCO_Grid_Documentation.pdf` | 231,864 |
| `netcdf/GEBCO_Grid_terms_of_use.pdf` | 145,503 |

GeoTIFF は 8 枚。南北 2 段 x 東西 4 列で、ファイル名に範囲が入っている (`n90.0_s0.0_w90.0_e180.0` など)。

`netcdf/00readme.txt` によると、DOI の記録を構成するのは netcdf ディレクトリの 5 ファイルだけで、GeoTIFF や ESRI ASCII は同じデータの別形式として後から置かれたもの。

## 取り出し方

split。1 枚の中は range。全球 netCDF を使うなら whole に近い。

- GeoTIFF は 8 枚に事前分割されている。日本が要るなら `gebco_2024_n90.0_s0.0_w90.0_e180.0.tif` の 1 枚。
- `https://dap.ceda.ac.uk/bodc/gebco/global/gebco_2024/ice_surface_elevation/geotiff/gebco_2024_n90.0_s0.0_w90.0_e180.0.tif` に `Range: bytes=0-1023` を投げて HTTP 206、1,024 バイトが返る。
- 先頭を読むと `II*\0`、IFD はオフセット 8。ImageWidth 21600、ImageLength 21600、BitsPerSample 16、SampleFormat 2 (符号付き整数)、Compression 1 (無圧縮)、RowsPerStrip 1、StripOffsets の要素数 21600。TileWidth タグは無い。
- つまり COG ではない。タイル化されていないしオーバービューも無い。ただし無圧縮で 1 行 1 ストリップなので、先頭の StripOffsets 配列 (オフセット 43430 から) を読めば任意の行の位置が正確に分かり、必要な行だけを Range で引ける。索引はファイル先頭付近にあるので、区分の条件は満たしている。
- 全球の netCDF (`GEBCO_2024_CF.nc`、7,466,018,396 バイト) も HTTP の Range は効く。先頭 1,024 バイトで HTTP 206、マジックは `\x89HDF\r\n\x1a\n` (HDF5)。ファイルの 1,000,000,000 バイト目から 1,024 バイトを要求しても HTTP 206 が返った。HDF5 の内部索引を辿れば部分読みはできるが、7.5GB を 1 本で扱うことになるので実用上は whole に近い。
- 認証は不要。`00README_catalogue_and_licence.txt` にも「Public data: access to these data is available to both registered and non-registered users.」とある。

## ライセンス

ここが他の 4 つと違う。ETOPO や Landsat と同じだと思って扱うと間違える。

gebco.net の Terms of use ページ (`https://www.gebco.net/data-products/gridded-bathymetry/terms-of-use`) の本文。配布ファイルに同梱されている `GEBCO_Grid_terms_of_use.pdf` も同じ文言。

> The GEBCO Grid is placed in the public domain and may be used free of charge.
> Use of the GEBCO Grid indicates that the user accepts the conditions of use and disclaimer information given below.
> Users are free to:
> Copy, publish, distribute and transmit The GEBCO Grid.
> Adapt The GEBCO Grid.
> Commercially exploit The GEBCO Grid, by, for example, combining it with other information, or by including it in their own product or application.
> Users must:
> Acknowledge the source of The GEBCO Grid. A suitable form of attribution is given in the documentation that accompanies The GEBCO Grid.
> Not use The GEBCO Grid in a way that suggests any official status or that GEBCO, or the IHO or IOC, endorses any particular application of The GEBCO Grid.
> Not mislead others or misrepresent The GEBCO Grid or its source.

安全についての但し書き。

> The GEBCO Grid should NOT be used for navigation or for any other purpose involving safety at sea.

指定されている表示文 (GEBCO_2024 の場合)。

> GEBCO Compilation Group (2024) GEBCO 2024 Grid (doi:10.5285/1c44ce99-0a0d-5f4f-e063-7086abc0ea0f)

読み取れること。GEBCO は「public domain に置く」と書くが、同じ文書で「Users must: Acknowledge the source」と義務を課している。これは CC0 ではない。CC0 は表示を含むあらゆる条件を放棄する宣言なので、表示が義務なら CC0 とは呼べない。実質は CC BY に近く、そこに「公式の地位を示唆しない」「誤解させない」という 2 条件が足されている。禁止事項ではないが、権利放棄でもない。区分としては「public domain と自称する、表示義務つきの自由利用許諾」である。

配布元の CEDA はさらに別の文言を出している。`gebco_2024/ice_surface_elevation/netcdf/00README_catalogue_and_licence.txt` の本文。

> licence:
>     Use of these data is covered by the following licence(s):
>     http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
>     When using these data you must cite them correctly using the citation given on the catalogue record.

英国の Open Government Licence v3.0。これも表示が義務のライセンスで、gebco.net の条件と向きは同じだが、名前の付いた別のライセンスである。同じファイルに 2 つの言い方が付いていることになる。どちらを採っても、表示なしで使ってよいという結論にはならない。

合成物としての注意。GEBCO 自身が、配っているのは元の測深データではなく派生物だと明言している。

> As The GEBCO Grid is created by interpolating, applying algorithms and mathematical techniques to bathymetric data, GEBCO considers the GEBCO Grid to be an information product.
> GEBCO does not provide the underlying source bathymetric data when distributing The GEBCO Grid.

GEBCO_2024 の中身は、SRTM15+ V2.6 を土台に Seabed 2030 の 4 地域センターの格子を重ね、グリーンランドと南極は BedMachine (Greenland v5、Antarctica v2)、北緯 60 度以北の陸は GMTED2010、スバールバルは Norwegian Polar Institute の地形モデルを使っている (いずれも GEBCO_Grid_Documentation.pdf の記述)。GEBCO の立場では、これらを混ぜて作った格子そのものが GEBCO の情報製品であり、元データの条件は付いて回らない。付いて回るのは上の「Users must」の 3 つである。

## 気をつけること

planetarble の `configs/base/assets.yaml` は GEBCO の license 欄を GEBCO Compilation Group (2024) の public domain と書く。前半は正しいが、表示が義務であることがここから読めない。README の「NASA/USGS public domain + NOAA CC0」というまとめ方では GEBCO が抜けている。legacy の BMNG 経路を使うと GEBCO が入るので、その経路では表示が必要になる。

さらに、GEBCO は [ETOPO 2022](../etopo/README.md) の海の部分の元データでもある。ユーザーガイドの出典表で GEBCO 2022 が layer source id 1 と 2 に入っている。つまり HLS 既定の経路 (ocean は ETOPO) でも、海のかたちは GEBCO 由来で、表示義務は間接的に付いて回ると読める。「NOAA CC0 だから表示不要」という結論には至らない。

CEDA は OGL v3.0 と書き、gebco.net は独自の Terms of use を示す。どちらか一方だけを見て済ませると、もう一方の条件を落とす。両方とも表示を求めている点は一致している。

GEBCO_2024 は最新ではない。CEDA には 2025 と 2026 がある。planetarble の `gebco_year: 2024` は固定値なので、版を上げたければ設定を変える必要がある。版が変わると同じ座標の値が変わる。

GeoTIFF は無圧縮 16bit で 1 枚 933MB。8 枚で約 7.4GB になり、netCDF の 7.47GB とほぼ同じ。GeoTIFF のほうが小さいわけではない。

航海に使うなという但し書きは、著作権の条件ではなく安全上の注意として明記されている。地図の描画には関係しないが、経路計画の題材にするときは意味が出る。

## 学習ステップでの使いどころ (案)

- 海の水深の原本として。[ETOPO 2022](../etopo/README.md) は GEBCO を土台に NOAA が繋ぎ直したもので、両者を同じ地点で比べると「繋ぎ方」で値がどれだけ変わるかを見られる。
- `type_identifier_grid` は各格子が実測か推定かを示す。観測の密度が偏ったデータで学習するとどうなるか、という題材にそのまま使える。実測の少ない海域で推定が効いていることが数字で見える。
- 6 PCA や 5 クラスタリング: 水深と傾斜から海底地形の型を分ける。
- 7 経路探索: 水深を制約にした航路。ただし航海には使えない (上の但し書き)。
- 全球が要らないなら GeoTIFF 8 枚のうち 1 枚。日本なら `gebco_2024_n90.0_s0.0_w90.0_e180.0.tif` (933,255,948 バイト)。それでも大きいので、StripOffsets を読んで必要な行だけ Range で引く。
