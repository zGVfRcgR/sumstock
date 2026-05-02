# 📊 物件追跡システムの実装

## 概要

スムストックの物件データを時系列で追跡し、販売状況・価格変動を分析・可視化するシステムを実装しました。

## 🎯 実装した機能

### 1. 物件追跡システム (Phase 1)
- ✅ 月次データの自動比較
- ✅ 販売終了物件の自動検出
- ✅ 価格変動の完全な履歴記録
- ✅ 統計分析（平均販売期間、価格変動率など）

### 2. 可視化システム (Phase 2)
- ✅ **販売期間の分布ヒストグラム** - 何日で売れるか
- ✅ **価格変動タイムライン** - 時系列での価格推移
- ✅ **ステータス分布円グラフ** - 販売中vs販売終了
- ✅ **価格変動分析バーチャート** - 値下げ/値上げの状況

### 3. MLIT API連携 (Phase 3)
- ✅ 国土交通省APIとの統合
- ✅ 類似物件のマッチング
- ✅ 参考情報レポート生成

### 4. GitHub Actions自動化
- ✅ 毎月2日に自動実行
- ✅ 追跡分析 → グラフ生成 → GitHub Pages更新
- ✅ 自動コミット＆デプロイ

### 5. GitHub Pages統合
- ✅ 追跡ダッシュボードページ
- ✅ グラフと分析レポートの表示
- ✅ トップページからリンク

## 📁 新規ファイル

### コアスクリプト (3ファイル)
```
scripts/track_properties.py       (341行) - 物件追跡
scripts/visualize_tracking.py     (220行) - 可視化
scripts/match_with_mlit.py        (219行) - MLIT API連携
scripts/README_TRACKING.md                - スクリプト説明
```

### GitHub Actions
```
.github/workflows/property-tracking.yml   - 自動実行ワークフロー
```

### GitHub Pages
```
tracking.md                               - ダッシュボードページ
```

### ドキュメント (4ファイル)
```
PROPERTY_TRACKING_SUMMARY.md              - 総合報告書
docs/sold_property_tracking_proposal.md   - 詳細提案書
docs/property_tracking_implementation.md  - 実装報告
docs/QUICK_START_TRACKING.md              - クイックスタート
```

### 生成データ
```
tracking_db.json                          - 追跡データベース
data/tracking_report.md                   - 分析レポート
data/mlit_matching_report.md              - MLIT照合レポート
docs/images/listing_duration.png          - 販売期間グラフ
docs/images/price_timeline.png            - 価格変動グラフ
docs/images/status_distribution.png       - ステータス円グラフ
docs/images/price_change_analysis.png     - 価格変動分析
```

### 設定変更
```
_config.yml                               - Jekyll設定更新
index.md                                  - トップページ更新
```

## 📊 検証結果（市川市データで実証）

```
追跡物件総数: 11件
販売中: 3件
販売終了（推定）: 8件
平均販売期間: 78.9日
価格変動あり: 3件
```

**最長掲載物件:**
- 市川市堀之内４丁目: 181日間掲載
- 価格変動: 8,280万円 → 7,980万円（-3.6%）

**最速売却物件:**
- 市川市東菅野１丁目: 36日で売却

## 🚀 使い方

### 手動実行
```bash
# 1. 物件追跡
python3 scripts/track_properties.py

# 2. グラフ生成
python3 scripts/visualize_tracking.py

# 3. MLIT API連携（オプション）
export REINFOLIB_API_KEY="your-api-key"
python3 scripts/match_with_mlit.py
```

### 自動実行
GitHub Actionsにより以下のスケジュールで自動実行されます：

- **毎月1日**: スクレイピング（既存）
- **毎月2日**: 追跡分析＆可視化（新規）
- **mainへのpush時**: 即時実行

結果はGitHub Pagesに自動公開されます：
- URL: `https://zGVfRcgR.github.io/sumstock/tracking.html`

## 💡 このシステムの価値

### 購入検討者向け
- 「この価格帯なら平均○○日で売れる」
- 「値下げは掲載△△日後が多い」
- 「このエリアは需要が高い」

### 売却検討者向け
- 市場データに基づく価格戦略
- 販売期間の予測
- 値下げタイミングの判断

### データ分析・研究者向け
- 中古住宅市場の動向分析
- ハウスメーカー別の比較
- 地域別市場活性度

## 🔍 技術的な詳細

### 物件の特定方法
所在地＋建物面積＋土地面積からMD5ハッシュを生成し、ユニークIDとして使用

### 販売終了の検出
前月のスクレイピングで存在した物件が、今月のスクレイピングで見つからない場合、「販売終了（推定）」と判定

### 価格変動の記録
各スクレイピング時点での価格を記録し、履歴として保存

### MLIT APIとの照合
建物面積・土地面積（±10%）、所在地（市区町村）、取引時期で絞り込み、類似物件を検索

## 📚 関連ドキュメント

- [総合報告書](../PROPERTY_TRACKING_SUMMARY.md) - システム全体の概要
- [詳細提案書](../docs/sold_property_tracking_proposal.md) - 設計思想と実装方針
- [実装報告](../docs/property_tracking_implementation.md) - 実装の詳細
- [クイックスタート](../docs/QUICK_START_TRACKING.md) - すぐに使える手順

## ⚠️ 注意事項

1. **販売終了の判定は推定です**
   - 物件が掲載から削除されたことを検出しますが、実際の売却とは限りません
   - 掲載停止や一時的な非公開の可能性もあります

2. **MLIT APIマッチングは参考情報です**
   - 個別物件の完全な特定はできません
   - 類似物件の成約事例として参考にしてください

3. **価格情報は参考値です**
   - 最新の正確な情報は公式サイトでご確認ください

## ✅ チェックリスト

- [x] Phase 1: 物件追跡システム実装
- [x] Phase 2: 可視化システム実装
- [x] Phase 3: MLIT API連携実装
- [x] GitHub Actions自動化設定
- [x] GitHub Pages統合
- [x] ドキュメント整備
- [x] 市川市データでの動作確認
- [ ] マージ後の動作確認
- [ ] MLIT APIキーの設定（オプション）

## 🔧 マージ後の設定

### MLIT APIキーの設定（オプション）

MLIT APIとの照合機能を有効にする場合：

1. GitHubリポジトリの Settings → Secrets → Actions
2. `REINFOLIB_API_KEY` という名前でシークレットを追加
3. 国土交通省から取得したAPIキーを値として設定

※ APIキーがない場合でも、スムストックデータのみでの追跡は正常に動作します。

---

**実装完了日**: 2026年5月2日  
**テスト**: 市川市データで動作確認済み  
**ステータス**: 本番運用可能
