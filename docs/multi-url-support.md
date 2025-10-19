# Multi-URL Support

このドキュメントでは、スクレイパーの複数URL処理機能について説明します。

## 概要

`scripts/scrape_sumstock.py` は、Issue本文やCLI引数から複数のSumStock URLを抽出し、それぞれを処理できるようになりました。

## 主な機能

### 1. 複数URLの抽出

Issue本文に含まれるすべてのSumStock URLが自動的に抽出されます：

```
対象URL: https://sumstock.jp/search/02/12/12207
対象URL: https://sumstock.jp/search/02/12/12208
対象URL: https://sumstock.jp/search/02/12/12209
```

### 2. 個別ファイル生成

各URLに対して個別のMarkdownファイルが生成されます：

- 複数URL: `YYYY-MM-DD_1.md`, `YYYY-MM-DD_2.md`, `YYYY-MM-DD_3.md`
- 単一URL: `YYYY-MM-DD.md` (従来通り、サフィックスなし)

### 3. 後方互換性

既存の単一URL処理は完全に互換性が保たれています。

## 使用方法

### CLI引数で複数URL指定

```bash
python scripts/scrape_sumstock.py \
  "https://sumstock.jp/search/02/12/12207" \
  "https://sumstock.jp/search/02/12/12208" \
  "https://sumstock.jp/search/02/12/12209"
```

**出力:**
```
Found 3 URL(s) to process

[1/3] Scraping data from: https://sumstock.jp/search/02/12/12207
Saved data to data/千葉県/松戸市/2025-10-19.md
Successfully processed X properties from URL 1

[2/3] Scraping data from: https://sumstock.jp/search/02/12/12208
Saved data to data/千葉県/野田市/2025-10-19.md
Successfully processed X properties from URL 2

[3/3] Scraping data from: https://sumstock.jp/search/02/12/12209
Saved data to data/千葉県/茂原市/2025-10-19.md
Successfully processed X properties from URL 3

=== Summary ===
Total URLs processed: 3
Total files created: 3
```

### 環境変数で複数URL指定

```bash
export ISSUE_BODY="対象URL: https://sumstock.jp/search/02/12/12207
対象URL: https://sumstock.jp/search/02/12/12208"
python scripts/scrape_sumstock.py
```

### GitHub Actions連携

GitHub Actionsから実行する際、Issue本文に複数のURLが含まれていても自動的に処理されます。

**GITHUB_OUTPUT出力例:**
```
filepath=data/千葉県/松戸市/2025-10-19.md,data/千葉県/野田市/2025-10-19.md,data/千葉県/茂原市/2025-10-19.md
date=2025-10-19
count=3
```

## API変更

### `extract_urls_from_issue(issue_body: str) -> List[str]`

従来の `extract_url_from_issue` から変更。Issue本文から全てのSumStock URLを抽出します。

**戻り値:**
- URLのリスト（0個以上）
- URLが見つからない場合は空のリスト

**例:**
```python
from scripts.scrape_sumstock import extract_urls_from_issue

issue_body = """
対象URL: https://sumstock.jp/search/02/12/12207
対象URL: https://sumstock.jp/search/02/12/12208
"""

urls = extract_urls_from_issue(issue_body)
# => ['https://sumstock.jp/search/02/12/12207', 'https://sumstock.jp/search/02/12/12208']
```

### `save_markdown_file(markdown, date, output_dir='data', suffix='')`

新しい `suffix` パラメータを追加。複数ファイル生成時に数字サフィックスを付与します。

**パラメータ:**
- `suffix`: ファイル名のサフィックス（例: `_1`, `_2`）

## テスト

### ユニットテスト

```bash
# URL抽出機能のテスト
python tests/test_multi_url_extraction.py
```

**テストケース:**
- URLなし
- 単一URL
- 複数URL
- 混在コンテンツ
- 重複URL
- 同一行の複数URL

### E2Eテスト

```bash
# 複数URL処理のE2Eテスト
python tests/test_multi_url_e2e.py
```

**テストケース:**
- 複数URLからの個別ファイル生成
- ファイル名のサフィックス検証
- 単一URL時のサフィックスなし検証

### デモ

```bash
# 機能デモの実行
python tests/demo_multi_url.py
```

## ファイル命名規則と保存先

ファイルは都道府県・市区町村ごとのフォルダに保存されます：

### フォルダ構造
```
data/
├── 千葉県/
│   ├── 松戸市/
│   │   └── YYYY-MM-DD.md
│   └── 柏市/
│       └── YYYY-MM-DD.md
└── 東京都/
    └── 千代田区/
        └── YYYY-MM-DD.md
```

### ファイル名
- すべてのファイル: `YYYY-MM-DD.md` (日付ベース)
- 同じ日に同じ地域の複数URLを処理する場合、既存ファイルが上書きされます

### 場所の抽出
URLから都道府県コードと市区町村コードを抽出します：
- 例: `https://sumstock.jp/search/02/12/12207`
  - 都道府県コード: `12` → `千葉県`
  - 市区町村コード: `12207` → `松戸市`
  - 保存先: `data/千葉県/松戸市/YYYY-MM-DD.md`

## 制限事項と注意点

1. **重複URL**: 重複したURLはそのまま処理されます（重複排除は行われません）
2. **順序**: URLは抽出された順序で処理されます
3. **ファイル上書き**: 同じ日に複数回実行すると、既存ファイルが上書きされます

## トラブルシューティング

### URLが抽出されない

Issue本文のフォーマットを確認してください。URLは以下のパターンに一致する必要があります：

```
https://sumstock.jp/search/\d+/\d+/\d+
```

### ファイルが生成されない

エラーメッセージを確認してください：

```bash
python scripts/scrape_sumstock.py 2>&1 | tee scraper.log
```

## 関連ドキュメント

- [tests/test_multi_url_extraction.py](../tests/test_multi_url_extraction.py): URL抽出テスト
- [tests/test_multi_url_e2e.py](../tests/test_multi_url_e2e.py): E2Eテスト
- [tests/demo_multi_url.py](../tests/demo_multi_url.py): 機能デモ
