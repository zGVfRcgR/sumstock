# 路線価データ (Rosenka Data)

## 概要 (Overview)

このディレクトリには、物件の土地評価を参照するための路線価データが格納されています。

This directory contains route price (rosenka) data used to reference land evaluation for properties.

## データ形式 (Data Format)

路線価データは CSV 形式で保存されています:

```csv
location,lat,lon,rosenka_value
松戸市,35.7873,139.9026,12.5
```

### カラム説明 (Column Descriptions)

- **location**: 住所または地域名 (Address or location name)
- **lat**: 緯度 (Latitude)
- **lon**: 経度 (Longitude)
- **rosenka_value**: 路線価（万円/m²）(Route price in 10,000 yen per m²)

## 使い方 (Usage)

路線価データは `scripts/rosenka.py` モジュールによって自動的に読み込まれます。

```python
from rosenka import get_rosenka_for_property

# 物件の住所から路線価を取得
rosenka = get_rosenka_for_property('松戸市中金杉1丁目')
print(f"路線価: {rosenka}万円/m²")
```

## データソース (Data Sources)

現在のデータは参照用のサンプルデータです。本番環境では、以下のデータソースから最新の路線価データを取得することを推奨します:

The current data is sample reference data. For production use, it is recommended to obtain the latest route price data from the following sources:

- **国税庁 路線価図**: https://www.rosenka.nta.go.jp/
- **地価公示データ**: 国土交通省が公開する公示地価データ
- **都道府県別の路線価データ**: 各地方自治体が提供するデータ

## データ更新 (Data Updates)

路線価は毎年1月1日時点の価格として7月に公表されます。データは年次で更新する必要があります。

Route prices are published in July as prices as of January 1st of each year. Data needs to be updated annually.

### 更新手順 (Update Procedure)

1. 国税庁サイトから最新の路線価データをダウンロード
2. CSV 形式に変換（必要に応じて）
3. `rosenka_data.csv` ファイルを更新
4. テストを実行して動作確認

## 注意事項 (Notes)

- 路線価データの利用にあたっては、各データソースの利用規約を遵守してください
- データの精度や最新性については、データソースを確認してください
- 路線価は土地の評価額の参考値であり、実際の取引価格とは異なる場合があります

## ライセンス (License)

路線価データは国税庁等の公的機関が公開しているデータを基にしています。利用にあたっては各機関の利用規約に従ってください。

Route price data is based on data published by public institutions such as the National Tax Agency. Please comply with the terms of use of each institution when using the data.
