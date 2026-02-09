---
layout: default
title: Navigation Structure
parent: ドキュメント
nav_order: 5
---

# Navigation Structure

このドキュメントは、サイトのナビゲーション構造について説明します。

## 概要

このサイトは、Just the Docs テーマを使用して、階層的なナビゲーション構造を実装しています。
データは都道府県と市町村で分類され、各日付のデータは市町村の下に配置されます。

## 階層構造

```
データ一覧 (root)
└── 千葉県 (Prefecture)
    ├── 市原市 (City)
    │   ├── 2025-12-27 (Date)
    │   ├── 2026-01-01
    │   └── 2026-02-01
    ├── 市川市
    │   ├── 2025-10-19
    │   └── ...
    └── その他の市町村...
```

## Front Matter の構造

### データ一覧ページ (`data/index.md`)
```yaml
---
layout: default
title: データ一覧
nav_order: 2
has_children: true
---
```

### 都道府県ページ (`data/千葉県/index.md`)
```yaml
---
layout: default
title: 千葉県
parent: データ一覧
has_children: true
nav_order: 10
---
```

### 市町村ページ (`data/千葉県/市川市/index.md`)
```yaml
---
layout: default
title: 市川市
parent: 千葉県
has_children: true
nav_order: 10
---
```

### 日付データページ (`data/千葉県/市川市/2025-10-19.md`)
```yaml
---
layout: default
title: 2025-10-19
parent: 市川市
---
```

## 新しいデータの追加

スクレイパースクリプト (`scripts/scrape_sumstock.py`) は、新しいデータを追加する際に自動的に以下を行います：

1. 都道府県のインデックスページが存在しない場合、作成する
2. 市町村のインデックスページが存在しない場合、作成する
3. 日付データファイルを適切な親 (市町村) で作成する

## 手動でインデックスページを生成する

既存のデータディレクトリに対してインデックスページを生成する場合は、以下のスクリプトを実行します：

```bash
python3 scripts/generate_index_pages.py
```

このスクリプトは：
- すべての都道府県ディレクトリにインデックスページを作成
- すべての市町村ディレクトリにインデックスページを作成
- 既存のデータファイルの front matter を更新

## 利点

この階層的な構造により：

- ユーザーは都道府県から市町村、日付へと簡単にナビゲートできます
- データの整理と管理が容易になります
- 新しい都道府県や市町村のデータを追加しても、自動的に適切な階層に配置されます
- サイトのナビゲーションが自動的に更新されます
