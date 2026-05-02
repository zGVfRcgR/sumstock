# 物件追跡システム クイックスタートガイド

## 🚀 5分で始める物件追跡

### 前提条件

✅ Python 3.7以上がインストール済み  
✅ スムストックのデータが`data/`ディレクトリにある  
✅ 必要なパッケージがインストール済み

```bash
pip install matplotlib numpy requests beautifulsoup4
```

---

## 📊 基本的な使い方

### Step 1: 物件追跡を実行

```bash
python3 scripts/track_properties.py
```

**出力:**
- `tracking_db.json` - 追跡データベース
- `data/tracking_report.md` - 分析レポート

**確認事項:**
- 追跡物件総数
- 販売中 vs 販売終了の件数
- 平均販売期間
- 価格変動の統計

### Step 2: グラフを生成

```bash
python3 scripts/visualize_tracking.py
```

**出力:**
- `docs/images/listing_duration.png` - 販売期間分布
- `docs/images/price_timeline.png` - 価格変動タイムライン
- `docs/images/status_distribution.png` - ステータス分布
- `docs/images/price_change_analysis.png` - 価格変動分析

### Step 3: MLIT APIとの照合（オプション）

```bash
# APIキーを設定
export REINFOLIB_API_KEY="your-api-key-here"

# 照合を実行
python3 scripts/match_with_mlit.py
```

**出力:**
- `data/mlit_matching_report.md` - MLIT照合レポート

**注意:** APIキーがない場合は、参考情報なしでレポートが生成されます。

---

## 📈 生成されるレポートの見方

### 追跡レポート (`data/tracking_report.md`)

```markdown
# 物件追跡レポート

## 概要
- 追跡中の物件総数: 11件
- 販売中: 3件
- 販売終了（推定）: 8件

## 販売期間
- 平均販売期間: 78.9日

## 最近販売終了した物件（推定）
### 市川市堀之内４丁目
- 掲載期間: 181日
- 初回価格: 8280万円
- 最終価格: 7980万円
- 価格変動: -300万円 (-3.6%)
```

**読み方:**
- **平均販売期間**: この市区町村で物件が売れるまでの平均日数
- **価格変動**: マイナスは値下げ、プラスは値上げ
- **掲載期間**: 長いほど売れにくい物件

---

## 🔄 定期実行の設定

### 月次で自動実行（推奨）

#### GitHub Actionsの例

`.github/workflows/monthly-tracking.yml`:

```yaml
name: Monthly Property Tracking

on:
  schedule:
    - cron: '0 0 1 * *'  # 毎月1日 午前0時
  workflow_dispatch:     # 手動実行も可能

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install matplotlib numpy
      
      - name: Run tracking
        run: python3 scripts/track_properties.py
      
      - name: Generate visualizations
        run: python3 scripts/visualize_tracking.py
      
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add tracking_db.json data/*.md docs/images/*.png
          git commit -m "🤖 Update property tracking [$(date +'%Y-%m-%d')]"
          git push
```

#### Cronジョブの例（Linuxサーバー）

```bash
# 毎月1日 午前2時に実行
0 2 1 * * cd /path/to/sumstock && python3 scripts/track_properties.py && python3 scripts/visualize_tracking.py
```

---

## 🔍 よくある質問

### Q1: データが更新されない

**確認事項:**
1. `data/`ディレクトリに新しいMarkdownファイルがあるか
2. ファイル名が`YYYY-MM-DD.md`形式になっているか
3. スクレイピングが正常に動作しているか

**解決方法:**
```bash
# データの確認
ls -l data/千葉県/市川市/*.md

# 手動でスクレイピング
python3 scripts/scrape_sumstock.py
```

### Q2: グラフが日本語で表示されない

**原因:** システムに日本語フォントがない

**解決方法:**
1. 現状のまま使用（英語のラベル）
2. 日本語フォントをインストール（Linux）:
   ```bash
   sudo apt-get install fonts-noto-cjk
   ```

### Q3: MLIT APIが使えない

**確認事項:**
1. 環境変数`REINFOLIB_API_KEY`が設定されているか
2. APIキーが有効か

**確認方法:**
```bash
echo $REINFOLIB_API_KEY
```

**注意:** APIキーがなくても、スムストックデータのみでの追跡は可能です。

### Q4: 物件が正しく検出されない

**原因:** Markdownファイルのフォーマットが変わった可能性

**解決方法:**
1. サンプルファイルでテスト:
   ```bash
   python3 -c "
   from scripts.track_properties import PropertyTracker
   tracker = PropertyTracker()
   props = tracker.parse_markdown_data('data/千葉県/市川市/2026-05-01.md')
   print(f'Found {len(props)} properties')
   "
   ```

---

## 📊 データ構造

### tracking_db.json

```json
{
  "properties": {
    "abc123def456": {
      "property_id": "abc123def456",
      "location": "市川市中国分２丁目",
      "building_area": 130.58,
      "land_area": 103.0,
      "house_maker": "ヤマダホームズ",
      "first_seen": "2025-10-01",
      "last_seen": "2026-03-01",
      "status": "active",
      "price_history": [
        {
          "date": "2025-10-01",
          "total_price": 2698,
          "change": null
        },
        {
          "date": "2026-03-01",
          "total_price": 2498,
          "change": -200
        }
      ]
    }
  },
  "statistics": {}
}
```

**フィールド説明:**
- `property_id`: 所在地+面積から生成されるユニークID
- `status`: "active" = 販売中, "sold_presumed" = 販売終了推定
- `price_history`: 価格変動の履歴（日付順）
- `change`: 前回からの価格変動（万円）

---

## 🎯 実践例

### 例1: 特定エリアの販売動向を確認

```bash
# 市川市のデータを追跡
python3 scripts/track_properties.py

# レポートを確認
cat data/tracking_report.md
```

### 例2: 価格変動のパターンを分析

```bash
# グラフを生成
python3 scripts/visualize_tracking.py

# 価格変動分析グラフを確認
open docs/images/price_change_analysis.png
```

### 例3: 複数市区町村を追跡

`scripts/track_properties.py`を編集:

```python
# 複数の市区町村を処理
cities = ["市川市", "船橋市", "松戸市"]

for city in cities:
    city_dir = tracker.data_dir / "千葉県" / city
    if city_dir.exists():
        print(f"\n=== {city} ===")
        # ... 処理 ...
```

---

## 📚 関連ドキュメント

- **詳細な提案書**: `docs/sold_property_tracking_proposal.md`
- **実装報告**: `docs/property_tracking_implementation.md`
- **総合報告書**: `PROPERTY_TRACKING_SUMMARY.md`
- **MLIT API リファレンス**: `docs/real_estate_api_reference.md`

---

## 🆘 トラブルシューティング

### エラー: "No module named 'matplotlib'"

```bash
pip install matplotlib numpy
```

### エラー: "tracking_db.json が見つからない"

```bash
# 初回実行でデータベースが作成されます
python3 scripts/track_properties.py
```

### エラー: "data/ ディレクトリが見つからない"

```bash
# カレントディレクトリを確認
pwd

# リポジトリルートに移動
cd /workspaces/sumstock
```

---

## ✅ チェックリスト

初回セットアップ:
- [ ] Python 3.7以上をインストール
- [ ] 依存パッケージをインストール
- [ ] スムストックデータが存在することを確認
- [ ] 追跡スクリプトを実行
- [ ] レポートが生成されることを確認

定期運用:
- [ ] 月次でスクレイピング実行
- [ ] 追跡スクリプトを実行
- [ ] グラフを生成
- [ ] レポートを確認・分析
- [ ] 結果をGitにコミット

---

**最終更新**: 2026-05-02  
**バージョン**: 1.0
