# 不動産情報ライブラリAPI クイックリファレンス

## セットアップ

```bash
# 依存関係のインストール
pip install -r requirements.txt

# APIキーの設定
export REINFOLIB_API_KEY="your-api-key-here"
```

## 基本的な使い方

```python
from scripts.real_estate_api import RealEstateInfoLibAPI

# APIクライアントの初期化
api = RealEstateInfoLibAPI(api_key="your-api-key")
```

## 地域コード一覧（主要都道府県）

| コード | 都道府県 |
|--------|----------|
| 01     | 北海道   |
| 11     | 埼玉県   |
| 12     | 千葉県   |
| 13     | 東京都   |
| 14     | 神奈川県 |
| 23     | 愛知県   |
| 26     | 京都府   |
| 27     | 大阪府   |
| 28     | 兵庫県   |
| 40     | 福岡県   |

## APIメソッド一覧

### 1. 不動産取引価格情報の取得

```python
# 基本的な使い方
data = api.get_transaction_price(
    year="2022",      # 取得年
    area="13",        # 地域コード（東京都）
    quarter="1"       # 四半期（オプション: 1-4）
)

# 年間データを取得（四半期なし）
data = api.get_transaction_price(year="2022", area="13")
```

**レスポンス形式**: GeoJSON

### 2. 地価公示情報の取得

```python
data = api.get_land_price(
    year="2024",      # 取得年
    area="13"         # 地域コード（東京都）
)
```

**レスポンス形式**: GeoJSON

### 3. 市区町村一覧の取得

```python
cities = api.get_city_list(
    prefecture_code="13"  # 都道府県コード（東京都）
)
```

**レスポンス形式**: JSON

### 4. 鑑定評価書情報の取得

```python
data = api.get_appraisal_report(
    year="2024",      # 取得年
    area="13",        # 地域コード（東京都）
    division="01"     # 用途区分（オプション）
)
```

**レスポンス形式**: GeoJSON

## エラーハンドリング

```python
from scripts.real_estate_api import (
    RealEstateInfoLibAPI,
    RealEstateInfoLibAPIError,
    RealEstateInfoLibAPIAuthError,
    RealEstateInfoLibAPIRateLimitError
)

try:
    api = RealEstateInfoLibAPI(api_key="your-api-key")
    data = api.get_transaction_price(year="2022", area="13")
    
except RealEstateInfoLibAPIAuthError:
    print("認証エラー: APIキーが無効です")
    
except RealEstateInfoLibAPIRateLimitError:
    print("レート制限: しばらく待ってから再試行してください")
    
except RealEstateInfoLibAPIError as e:
    print(f"APIエラー: {e}")
```

## コンテキストマネージャーの使用

```python
# with文を使用すると自動的にセッションがクローズされます
with RealEstateInfoLibAPI(api_key="your-api-key") as api:
    data = api.get_transaction_price(year="2022", area="13")
    # データを処理...
# ここでセッションが自動的にクローズされます
```

## データの保存

```python
import json

with RealEstateInfoLibAPI(api_key="your-api-key") as api:
    data = api.get_land_price(year="2024", area="13")
    
    # GeoJSON形式で保存
    with open("land_price_data.geojson", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

## 実用例

### 例1: 東京都の2022年不動産取引価格を取得

```python
from scripts.real_estate_api import RealEstateInfoLibAPI

with RealEstateInfoLibAPI(api_key="your-api-key") as api:
    data = api.get_transaction_price(year="2022", area="13")
    
    print(f"取得件数: {len(data['features'])}")
    
    # 最初の5件を表示
    for i, feature in enumerate(data['features'][:5], 1):
        props = feature['properties']
        print(f"{i}. {props}")
```

### 例2: 複数都道府県の地価公示を一括取得

```python
from scripts.real_estate_api import RealEstateInfoLibAPI

prefectures = {
    "13": "東京都",
    "14": "神奈川県",
    "11": "埼玉県",
    "12": "千葉県"
}

with RealEstateInfoLibAPI(api_key="your-api-key") as api:
    for code, name in prefectures.items():
        print(f"\n{name}の地価公示を取得中...")
        data = api.get_land_price(year="2024", area=code)
        print(f"  取得件数: {len(data['features'])}")
```

### 例3: 市区町村一覧を取得して表示

```python
from scripts.real_estate_api import RealEstateInfoLibAPI

with RealEstateInfoLibAPI(api_key="your-api-key") as api:
    cities = api.get_city_list(prefecture_code="13")
    
    print("東京都の市区町村一覧:")
    for city in cities.get('cities', []):
        print(f"  {city['code']}: {city['name']}")
```

## テストの実行

```bash
# API機能のテスト
python3 tests/test_real_estate_api.py

# 使用例の実行
python3 scripts/real_estate_api_example.py
```

## トラブルシューティング

### APIキーエラー
```
ValueError: APIキーが必要です
```
→ APIキーを正しく設定してください

### 認証エラー
```
RealEstateInfoLibAPIAuthError: API認証に失敗しました
```
→ APIキーが有効か確認してください

### レート制限エラー
```
RealEstateInfoLibAPIRateLimitError: APIレート制限に達しました
```
→ しばらく待ってから再試行してください

### ネットワークエラー
```
RealEstateInfoLibAPIError: ネットワークエラーが発生しました
```
→ インターネット接続を確認してください

## 参考リンク

- [公式APIマニュアル](https://www.reinfolib.mlit.go.jp/help/apiManual/)
- [不動産情報ライブラリ](https://www.reinfolib.mlit.go.jp/)
- [pyreinfolib (参考実装)](https://github.com/matsudan/pyreinfolib)
- [国土交通省](https://www.mlit.go.jp/)

## ライセンス・利用規約

- このPythonクラスはMITライセンスで提供されます
- 不動産情報ライブラリAPIの利用規約を遵守してください
- APIのレート制限を守ってください
- 取得したデータの利用は国土交通省の規約に従ってください
