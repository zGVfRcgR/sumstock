# PR作成手順

## 方法1: GitHub Web UIを使用

1. GitHubリポジトリにアクセス
   https://github.com/zGVfRcgR/sumstock

2. 「Pull requests」タブをクリック

3. 「New pull request」ボタンをクリック

4. base: main ← compare: feature/property-tracking-system を選択

5. 「Create pull request」をクリック

6. タイトル:
   ```
   feat: 物件追跡システムの実装（可視化・GitHub Pages統合）
   ```

7. 説明欄に `PR_DESCRIPTION.md` の内容をコピー＆ペースト

8. 「Create pull request」をクリック

## 方法2: GitHub CLIを使用

```bash
# GitHub CLIにログイン
gh auth login

# ブランチをプッシュ
git push -u origin feature/property-tracking-system

# PRを作成
gh pr create \
  --title "feat: 物件追跡システムの実装（可視化・GitHub Pages統合）" \
  --body-file PR_DESCRIPTION.md \
  --base main \
  --head feature/property-tracking-system
```

## 方法3: コマンドラインでブランチプッシュのみ

```bash
# Personal Access Tokenを使用してプッシュ
git push https://<USERNAME>:<TOKEN>@github.com/zGVfRcgR/sumstock.git feature/property-tracking-system

# その後、GitHubのWeb UIからPRを作成
```

## ブランチの状態

```
現在のブランチ: feature/property-tracking-system
コミット数: 1
変更ファイル数: 20
  - 新規: 18ファイル
  - 変更: 2ファイル
```

## PRマージ後の確認事項

1. GitHub Actionsが正常に動作するか確認
   - `.github/workflows/property-tracking.yml` の実行ログをチェック

2. GitHub Pagesが更新されているか確認
   - https://zGVfRcgR.github.io/sumstock/tracking.html

3. 追跡データが生成されているか確認
   - tracking_db.json
   - data/tracking_report.md
   - docs/images/*.png

4. MLIT APIキーの設定（オプション）
   - Settings → Secrets → Actions
   - REINFOLIB_API_KEY を追加

## トラブルシューティング

### ブランチがプッシュできない
- Personal Access Token が必要な場合があります
- Settings → Developer settings → Personal access tokens で生成

### GitHub Actionsが失敗する
- 依存関係の確認: requirements.txt
- matplotlib, numpy が requirements.txt にあるか確認

### 画像が表示されない
- docs/images/ ディレクトリが正しくコミットされているか確認
- _config.yml の include 設定を確認
