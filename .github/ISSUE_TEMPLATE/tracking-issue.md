---
name: データ取得用トラッキングIssue
about: SumStockから自動的にデータを取得するための設定Issue
title: '[TRACKING] SumStockデータ取得'
labels: tracking
assignees: ''
---

## 🎯 データ取得対象URL

以下のURLから物件データを取得します：

- https://sumstock.jp/search/02/12/12207（例：松戸市）
- https://sumstock.jp/search/13/01/13101（例：千代田区）

**URLフォーマット**: `https://sumstock.jp/search/{都道府県コード}/{市区町村コード上2桁}/{市区町村コード}`
- 例: `/02/12/12207` → 千葉県(02) 松戸市(12207)

複数のURLを追加する場合は、上記のようにリスト形式で記載してください。

## 📋 取得設定

- **取得頻度**: 毎月1日 00:00 UTC
- **出力先**: `data/YYYY-MM-DD.md`
- **フォーマット**: Markdown形式の表

## 📝 メモ

このIssueは自動データ取得のために使用されます。クローズしないでください。

URLを追加・変更したい場合は、上記のURLリストを編集してください。
現在のスクリプトは最初に見つかったSumStock URLを使用します。
