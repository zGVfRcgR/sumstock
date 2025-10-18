# sumstock

スムストック（[SumStock.jp](https://sumstock.jp/)）から物件データを取得して公開するサイトです。

## 概要

このプロジェクトは、SumStock.jpから物件情報を定期的に取得し、GitHub Pagesで公開するシステムです。

- **自動データ取得**: GitHub Actionsによる定期スクレイピング
- **データ公開**: Markdown形式の表で見やすく表示
- **履歴管理**: 取得日ごとにデータを保存

## 公開URL

GitHub Pages: [https://zGVfRcgR.github.io/sumstock/](https://zGVfRcgR.github.io/sumstock/)

## ディレクトリ構成

- `data/` - 取得した物件データ（日付ごとのMarkdownファイル）
- `docs/` - プロジェクトのドキュメント
- `.github/workflows/` - GitHub Actions設定

## 開発

詳細は[ドキュメント](https://zGVfRcgR.github.io/sumstock/docs/)をご覧ください。
