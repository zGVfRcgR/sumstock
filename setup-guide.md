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
├── index.md             # トップページ
├── docs/                # ドキュメントディレクトリ
│   ├── index.md
│   ├── getting-started.md
│   └── usage.md
└── .github/
    └── workflows/
        └── jekyll.yml   # 自動デプロイワークフロー
```

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
