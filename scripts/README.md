# SumStock Scraper Scripts

このディレクトリには、SumStock.jpから物件データを取得するためのスクリプトが含まれています。

## ファイル

- `scrape_sumstock.py` - SumStockのWebサイトをスクレイピングして物件データを取得するメインスクリプト
- `test_scraper.py` - スクレイパーの機能をテストするためのスクリプト（モックデータを使用）
- `real_estate_api.py` - 国土交通省の不動産情報ライブラリAPIクライアント
- `real_estate_api_example.py` - 不動産情報ライブラリAPIの使用例
- `location_mapping.py` - 地域コードと地域名のマッピング

## 使用方法

### 基本的な使用方法

```bash
python scripts/scrape_sumstock.py "https://sumstock.jp/search/02/12/12207"
```

### Issue本文からURLを自動抽出

```bash
export ISSUE_BODY="対象URL: https://sumstock.jp/search/02/12/12207"
python scripts/scrape_sumstock.py
```

## 依存関係

スクリプトを実行する前に、必要なPythonパッケージをインストールしてください：

```bash
pip install -r requirements.txt
```

必要なパッケージ：
- `requests` - HTTPリクエスト用
- `beautifulsoup4` - HTMLパース用
- `lxml` - HTMLパーサー

## 出力形式

スクリプトは`data/`ディレクトリに、取得日をファイル名としたMarkdownファイルを生成します：

```
data/YYYY-MM-DD.md
```

各ファイルには以下の情報が含まれます：
- 取得日
- 参照URL
- 物件データ（表形式）
  - 所在地
  - 総額
  - 建物価格・面積・単価
  - 土地価格・面積・単価
  - ハウスメーカー

## GitHub Actionsとの統合

このスクリプトは`.github/workflows/scrape-sumstock.yml`ワークフローから自動的に実行されます。

- **トリガー**: 
  - スケジュール実行（毎月1日）
  - 手動実行（workflow_dispatch）

- **処理フロー**:
  1. IssueからURLを抽出
  2. データをスクレイピング
  3. Markdownファイルを生成
  4. 新しいブランチを作成
  5. Pull Requestを作成

## テスト

モックデータを使用してスクリプトの機能をテストできます：

```bash
python scripts/test_scraper.py
```

## 不動産情報ライブラリAPI

国土交通省の不動産情報ライブラリAPIを利用して、地価公示や不動産取引価格などの公的データを取得できます。

### APIキーの取得

1. [不動産情報ライブラリ](https://www.reinfolib.mlit.go.jp/)にアクセス
2. APIキーを申請・取得
3. 環境変数に設定: `export REINFOLIB_API_KEY="your-api-key"`

### 使用例

```python
from scripts.real_estate_api import RealEstateInfoLibAPI

# APIクライアントを初期化
api = RealEstateInfoLibAPI(api_key="your-api-key")

# 不動産取引価格を取得（東京都、2022年）
transaction_data = api.get_transaction_price(year="2022", area="13")

# 地価公示情報を取得（東京都、2024年）
land_price_data = api.get_land_price(year="2024", area="13")

# 市区町村一覧を取得（東京都）
city_list = api.get_city_list(prefecture_code="13")
```

詳細は `real_estate_api_example.py` を参照してください。

### API機能

- **不動産取引価格情報取得** (`get_transaction_price`)
  - 実際の不動産取引価格データをGeoJSON形式で取得
  - パラメータ: 年、地域コード、四半期（オプション）

- **地価公示情報取得** (`get_land_price`)
  - 地価公示・都道府県地価調査データを取得
  - パラメータ: 年、地域コード

- **市区町村一覧取得** (`get_city_list`)
  - 都道府県内の市区町村一覧を取得
  - パラメータ: 都道府県コード

- **鑑定評価書情報取得** (`get_appraisal_report`)
  - 鑑定評価書情報を取得
  - パラメータ: 年、地域コード、用途区分（オプション）

### エラーハンドリング

- `RealEstateInfoLibAPIAuthError`: API認証エラー
- `RealEstateInfoLibAPIRateLimitError`: レート制限エラー
- `RealEstateInfoLibAPIError`: その他のAPIエラー

### 参考リンク

- [公式APIマニュアル](https://www.reinfolib.mlit.go.jp/help/apiManual/)
- [pyreinfolib (参考実装)](https://github.com/matsudan/pyreinfolib)

## 注意事項

- スクレイピングはSumStock.jpの利用規約を遵守して実行してください
- 過度なアクセスを避け、サーバーに負荷をかけないように注意してください
- HTMLの構造が変更された場合、スクリプトの更新が必要になる可能性があります
- 不動産情報ライブラリAPIの利用規約とレート制限を遵守してください
