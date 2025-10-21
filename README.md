# sumstock

スムストック（[SumStock.jp](https://sumstock.jp/)）から物件データを取得して公開するサイトです。

## 概要

このプロジェクトは、SumStock.jpから物件情報を定期的に取得し、GitHub Pagesで公開するシステムです。

- **自動データ取得**: GitHub Actionsによる定期スクレイピング
- **データ公開**: Markdown形式の表で見やすく表示
- **履歴管理**: 取得日ごとにデータを保存
- **地価データ取得**: 国土交通省の不動産情報ライブラリAPIを使用した地価データの自動取得（オプション）

## 公開URL

GitHub Pages: [https://zGVfRcgR.github.io/sumstock/](https://zGVfRcgR.github.io/sumstock/)

## ディレクトリ構成

- `data/` - 取得した物件データ（日付ごとのMarkdownファイル）
- `docs/` - プロジェクトのドキュメント
- `scripts/` - スクレイピングスクリプト
- `tests/` - テストコード
- `.github/workflows/` - GitHub Actions設定

## 機能

### 地価データ取得機能

物件の住所から国土交通省の不動産情報ライブラリAPIを使用して地価（地価公示・都道府県地価調査）を自動取得します。

#### 利用方法

1. **APIキーの取得**: [不動産情報ライブラリ](https://www.reinfolib.mlit.go.jp/)でAPIキーを申請
2. **環境変数の設定**: `REINFOLIB_API_KEY` に取得したAPIキーを設定
3. **自動取得**: スクレイピング時に自動的に地価データが取得され、以下の情報が追加されます：
   - **地価（万円/m²）**: 該当地域の公示地価
   - **地価倍率**: 物件の土地単価を地価で割った倍率（例: 1.23x）

#### 注意事項

- APIキーが設定されていない場合、地価データは「-」と表示されます
- 地価データは年次更新のため、最新データが利用可能です
- 住所から市区町村を自動判定し、該当地域の平均地価を取得します

## 開発

### セットアップ

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# テストの実行
python tests/test_land_price.py
python tests/test_land_price_integration.py
```

詳細は[ドキュメント](https://zGVfRcgR.github.io/sumstock/docs/)をご覧ください。
