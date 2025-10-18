---
layout: default
title: はじめに
parent: ドキュメント
nav_order: 1
---

# はじめに

sumstockへようこそ！このガイドでは、プロジェクトの概要と基本情報を説明します。

## プロジェクト概要

sumstockは、[SumStock.jp](https://sumstock.jp/)から物件情報を自動的に取得し、GitHub Pagesで公開するシステムです。

### 主な特徴

- **自動データ取得**: GitHub Actionsによる定期的なスクレイピング
- **Markdown形式**: 見やすい表形式でデータを表示
- **履歴管理**: 取得日ごとにデータを保存
- **静的サイト**: GitHub Pagesで無料公開

## システム構成

### データフロー

1. GitHub Actionsが定期的に実行される
2. SumStock.jpから物件情報をスクレイピング
3. データをMarkdown形式に整形
4. `data/YYYY-MM-DD.md`として保存
5. PRを自動作成し、マージ後に自動公開

### ディレクトリ構成

```
sumstock/
├── data/              # 物件データ（日付ごと）
│   ├── index.md       # データ一覧ページ
│   └── YYYY-MM-DD.md  # 各日のデータ
├── docs/              # ドキュメント
├── .github/           # GitHub Actions設定
└── index.md           # トップページ
```

## 前提条件

このサイトを閲覧するには、特別な環境は不要です。Webブラウザがあれば閲覧できます。

開発に参加する場合は、以下が必要です：

- Git
- Ruby（Jekyll開発時）
- Python（スクレイピングスクリプト開発時）

## 次のステップ

- [使い方](usage.html)でデータの閲覧方法を確認
- [データ一覧](../data/)で最新の物件情報を確認
