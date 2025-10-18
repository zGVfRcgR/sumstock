---
layout: default
title: GitHub Pages セットアップガイド
nav_order: 3
---

# GitHub Pages セットアップガイド

このガイドでは、このリポジトリでGitHub Pagesを有効化する方法を説明します。

## セットアップ手順

### 1. GitHub Pagesを有効化する

1. GitHubリポジトリページにアクセス: [https://github.com/zGVfRcgR/sumstock](https://github.com/zGVfRcgR/sumstock)
2. 「Settings」タブをクリック
3. 左サイドバーの「Pages」をクリック
4. 「Source」セクションで以下を設定：
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/ (root)`
5. 「Save」ボタンをクリック

### 2. デプロイを確認

- 設定を保存すると、GitHubが自動的にサイトをビルドしてデプロイします
- 「Actions」タブでビルドの進行状況を確認できます
- デプロイが完了すると、Settings → Pagesに公開URLが表示されます

### 3. サイトにアクセス

公開URL: [https://zGVfRcgR.github.io/sumstock/](https://zGVfRcgR.github.io/sumstock/)

## 使用している技術

- **Jekyll**: 静的サイトジェネレータ
- **Just the Docs**: ドキュメントサイト用のJekyllテーマ
- **GitHub Pages**: 無料のホスティングサービス

## ファイル構成

```
sumstock/
├── _config.yml          # Jekyll設定ファイル
├── Gemfile              # Ruby依存関係
├── .gitignore           # Git除外設定
├── requirements.txt     # Python依存関係
├── index.md             # トップページ
├── setup-guide.md       # このガイド
├── data/                # 物件データディレクトリ
│   ├── index.md         # データ一覧ページ
│   ├── sample.md        # サンプルデータ
│   └── YYYY-MM-DD.md    # 各日の物件データ（自動生成）
├── docs/                # ドキュメントディレクトリ
│   ├── index.md
│   ├── getting-started.md
│   └── usage.md
├── scripts/             # データ取得スクリプト
│   ├── README.md
│   ├── scrape_sumstock.py
│   └── test_scraper.py
└── .github/
    └── workflows/
        ├── jekyll.yml         # 自動デプロイワークフロー
        └── scrape-sumstock.yml # データ取得ワークフロー
```

## データ取得の設定

### Tracking Issueの作成

データ取得ワークフローは、"tracking"ラベルが付いたIssueからURLを自動抽出します。

1. 新しいIssueを作成
2. Issue本文にSumStockのURLを記載（例：`https://sumstock.jp/search/02/12/12207`）
3. "tracking"ラベルを追加
4. Issueを保存（クローズしないでください）

ワークフローは、このIssueからURLを読み取り、データを取得します。

### ワークフローの権限設定

GitHub Actionsがデータを自動で取得してPRを作成するには、適切な権限が必要です：

1. リポジトリの「Settings」→「Actions」→「General」を開く
2. 「Workflow permissions」セクションで以下を確認：
   - 「Read and write permissions」が選択されている
   - 「Allow GitHub Actions to create and approve pull requests」にチェックが入っている

## カスタマイズ

### サイトタイトルやデザインを変更する

`_config.yml`ファイルを編集してください：

```yaml
title: あなたのサイトタイトル
description: サイトの説明
color_scheme: dark  # light または dark
```

### 新しいページを追加する

1. 新しい`.md`ファイルを作成
2. ファイルの先頭にFront Matterを追加：

```yaml
---
layout: default
title: ページタイトル
nav_order: 4
---
```

3. Markdownでコンテンツを記述

### ローカルで確認する（オプション）

```bash
# 依存関係をインストール
bundle install

# ローカルサーバーを起動
bundle exec jekyll serve

# ブラウザで http://localhost:4000/sumstock/ にアクセス
```

## トラブルシューティング

### サイトが表示されない

- Actions タブでビルドエラーがないか確認
- Settings → Pages で正しいブランチとフォルダが選択されているか確認
- 数分待ってから再度アクセス（初回デプロイには時間がかかる場合があります）

### スタイルが適用されない

- `_config.yml`の`baseurl`と`url`が正しく設定されているか確認
- ブラウザのキャッシュをクリア

## 参考リンク

- [GitHub Pages公式ドキュメント](https://docs.github.com/ja/pages)
- [Jekyll公式ドキュメント](https://jekyllrb.com/docs/)
- [Just the Docs テーマドキュメント](https://just-the-docs.github.io/just-the-docs/)
