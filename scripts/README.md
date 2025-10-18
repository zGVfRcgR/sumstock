# SumStock Scraper Scripts

このディレクトリには、SumStock.jpから物件データを取得するためのスクリプトが含まれています。

## ファイル

- `scrape_sumstock.py` - SumStockのWebサイトをスクレイピングして物件データを取得するメインスクリプト
- `test_scraper.py` - スクレイパーの機能をテストするためのスクリプト（モックデータを使用）

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

## 注意事項

- スクレイピングはSumStock.jpの利用規約を遵守して実行してください
- 過度なアクセスを避け、サーバーに負荷をかけないように注意してください
- HTMLの構造が変更された場合、スクリプトの更新が必要になる可能性があります
