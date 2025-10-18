# GitHub Actions Workflows

このディレクトリには、sumstockプロジェクトの自動化ワークフローが含まれています。

## ワークフロー一覧

### 1. Jekyll Site Deployment (`jekyll.yml`)

GitHub Pagesへの自動デプロイを行います。

- **トリガー**: 
  - `main`ブランチへのpush
  - 手動実行（workflow_dispatch）
- **処理内容**:
  - Jekyllサイトのビルド
  - GitHub Pagesへのデプロイ

### 2. SumStock Data Scraping (`scrape-sumstock.yml`)

SumStock.jpから物件データを自動取得します。

- **トリガー**:
  - スケジュール実行: 毎月1日 00:00 UTC
  - 手動実行（workflow_dispatch）: オプションでURLを指定可能
- **処理内容**:
  1. "tracking"ラベルが付いたIssueからURLを抽出
  2. 指定されたURLから物件データをスクレイピング
  3. データを整形してMarkdownファイルを生成
  4. 新しいブランチを作成
  5. Pull Requestを自動作成

## 手動実行方法

### SumStock Data Scrapingを手動実行

1. GitHubリポジトリの「Actions」タブを開く
2. 「Scrape SumStock Data」ワークフローを選択
3. 「Run workflow」ボタンをクリック
4. （オプション）「url」フィールドにSumStockのURLを入力
5. 「Run workflow」をクリックして実行

URLを指定しない場合は、"tracking"ラベルが付いたIssueから自動的にURLを抽出します。

## 必要な権限

ワークフローが正常に動作するには、以下の権限が必要です：

- **contents: write** - ファイルの作成とコミット
- **pull-requests: write** - PRの作成
- **issues: read** - Issueの読み取り

これらの権限は、リポジトリの Settings → Actions → General → Workflow permissions で設定できます。

## トラブルシューティング

### ワークフローが失敗する

1. Actionsタブでエラーログを確認
2. 必要な権限が設定されているか確認
3. "tracking"ラベルのIssueが存在し、有効なURLが記載されているか確認

### PRが作成されない

1. Workflow permissions が「Read and write permissions」に設定されているか確認
2. 「Allow GitHub Actions to create and approve pull requests」にチェックが入っているか確認

### データが取得できない

1. 指定したURLが正しいか確認
2. SumStock.jpのサイト構造が変更されていないか確認
3. ネットワーク接続の問題がないか確認

## 関連ファイル

- `/scripts/scrape_sumstock.py` - スクレイピングスクリプト
- `/scripts/README.md` - スクリプトの詳細ドキュメント
- `/requirements.txt` - Python依存関係
- `/.github/ISSUE_TEMPLATE/tracking-issue.md` - トラッキングIssueのテンプレート
