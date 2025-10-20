# 路線価機能の実装概要 (Rosenka Feature Implementation Summary)

## 概要 (Overview)

物件の住所から路線価（rosenka）を取得し、建物単価との倍率を計算して出力に追加する機能を実装しました。

This implementation adds the ability to retrieve route price (rosenka) from property addresses and calculate the ratio with building unit prices, adding them to the output.

## 実装内容 (Implementation Details)

### 1. 新規ファイル (New Files)

#### `scripts/rosenka.py`
路線価の検索と倍率計算を行うモジュール

Main functions:
- `get_rosenka_for_property(location)`: 住所から路線価を取得
- `calculate_rosenka_ratio(building_unit_price, rosenka)`: 建物単価と路線価の倍率を計算
- `load_rosenka_data(csv_path)`: CSVファイルから路線価データを読み込み
- `normalize_location(location)`: 住所の正規化（市区町村レベルへの変換）

#### `data/rosenka/rosenka_data.csv`
路線価データを格納するCSVファイル

Format:
```csv
location,lat,lon,rosenka_value
松戸市,35.7873,139.9026,12.5
```

#### `data/rosenka/README.md`
路線価データの説明とデータソースの情報

### 2. 変更ファイル (Modified Files)

#### `scripts/scrape_sumstock.py`

変更内容:
1. rosenkaモジュールのインポート追加
2. property_dataに`rosenka_value`と`rosenka_ratio`フィールドを追加
3. 物件ごとに路線価を取得し、倍率を計算するロジックを追加
4. Markdownテーブルに「路線価（万円/m²）」と「路線価倍率」列を追加

### 3. テストファイル (Test Files)

#### `tests/test_rosenka.py`
路線価モジュールの単体テスト

Tests:
- 住所の正規化機能
- 路線価データの読み込み
- 住所から路線価の検索
- 倍率の計算
- 統合テスト

#### `tests/test_scraper_with_rosenka.py`
スクレイパーとの統合テスト

Tests:
- 路線価機能を含めた完全なスクレイピングフロー
- Markdown出力に路線価列が含まれることの確認

## 出力フォーマット (Output Format)

### Markdownテーブル (Markdown Table)

```markdown
| 所在地（町名） | 総額 | 建物価格 | 建物面積 | 建物単価（万円/m²） | 土地価格 | 土地面積 | 土地単価（万円/m²） | ハウスメーカー | 路線価（万円/m²） | 路線価倍率 |
|----------------|-------|------------|-------------|------------------------|------------|-------------|------------------------|----------------|-------------------|------------|
| 松戸市中金杉1丁目 | 3,280万円 | 1,054万円 | 112.85m² | 約9.34万円/m² | 2,226万円 | 151.45m² | 約14.70万円/m² | 積水ハウス | 12.50万円/m² | 0.75x |
```

### データフィールド (Data Fields)

- **路線価（万円/m²）**: 該当地域の路線価。データが見つからない場合は `-`
- **路線価倍率**: 建物単価 ÷ 路線価。計算できない場合は `-`
  - 例: 建物単価 9.34万円/m² ÷ 路線価 12.5万円/m² = 0.75x

## 路線価倍率の意味 (Meaning of Rosenka Ratio)

路線価倍率は、建物の価格が路線価（土地の評価額の基準）の何倍になっているかを示します:

- **1.0x未満**: 建物単価が路線価より低い（土地の評価が高い、または建物の評価が低い）
- **1.0x前後**: 建物単価が路線価と同程度
- **1.0x超**: 建物単価が路線価より高い（建物の価値が高い）

## データ更新 (Data Updates)

路線価データは年次で更新が必要です:

1. 毎年7月に国税庁から最新の路線価が公表される
2. `data/rosenka/rosenka_data.csv` を更新
3. テストを実行して動作確認

詳細は `data/rosenka/README.md` を参照してください。

## 使用例 (Usage Example)

### スクレイパーの実行 (Running the Scraper)

```bash
cd /home/runner/work/sumstock/sumstock
python scripts/scrape_sumstock.py https://sumstock.jp/search/02/12/12207
```

出力されるMarkdownファイルには、路線価と路線価倍率の列が自動的に追加されます。

### プログラムからの使用 (Programmatic Usage)

```python
from rosenka import get_rosenka_for_property, calculate_rosenka_ratio

# 路線価の取得
location = "松戸市中金杉1丁目"
rosenka = get_rosenka_for_property(location)
if rosenka:
    print(f"路線価: {rosenka}万円/m²")

# 倍率の計算
building_unit_price = "約9.34万円/m²"
ratio = calculate_rosenka_ratio(building_unit_price, rosenka)
if ratio:
    print(f"路線価倍率: {ratio:.2f}x")
```

## 制限事項と今後の拡張 (Limitations and Future Extensions)

### 現在の制限事項 (Current Limitations)

1. **データソース**: サンプルデータを使用（実際の国税庁データは未統合）
2. **ジオコーディング**: モックデータで実装（APIは未使用）
3. **データの粒度**: 市区町村レベルが中心（町丁目レベルのデータは限定的）

### 今後の拡張案 (Future Extensions)

1. 国税庁の路線価データとの統合
2. ジオコーディングAPIの統合（Nominatim、Google Maps API等）
3. より詳細な地点ごとの路線価データ
4. 路線価の年次データ管理（複数年の履歴）
5. 地価公示データとの連携

## テスト (Testing)

すべてのテストを実行:

```bash
# 路線価モジュールのテスト
python tests/test_rosenka.py

# 統合テスト
python tests/test_scraper_with_rosenka.py

# 既存のテスト（回帰テスト）
python tests/test_scraper_with_mock.py
```

## 参考資料 (References)

- 国税庁 路線価図: https://www.rosenka.nta.go.jp/
- 国土交通省 地価公示: https://www.land.mlit.go.jp/landPrice/
- data/rosenka/README.md: 路線価データの詳細説明
