# スムストック物件追跡システム - 実装完了報告

## 📋 プロジェクト概要

スムストックから取得した物件情報を時系列で追跡し、販売状況・価格変動を分析するシステムを実装しました。

**実装日**: 2026年5月2日  
**ステータス**: Phase 1 & 2 完了、Phase 3 実装済み（APIキー設定で有効化）

---

## ✅ 完了した機能

### Phase 1: 基本追跡システム

✅ **月次データ比較機能**
- 前月と今月のデータを自動比較
- 消えた物件を「販売終了（推定）」として検出
- 価格変更の自動記録

✅ **物件追跡データベース**
- 各物件にユニークIDを自動生成
- 初回掲載日・最終確認日の記録
- ステータス管理（active / sold_presumed）
- 価格変動履歴の保存

✅ **統計分析**
- 平均販売期間の計算
- 価格変動パターンの分析
- 販売終了物件の集計

**実装ファイル**: `scripts/track_properties.py`

### Phase 2: 可視化システム

✅ **4種類のグラフ生成**
1. **販売期間の分布ヒストグラム** - 何日で売れるか
2. **価格変動タイムライン** - 時系列での価格推移
3. **ステータス分布円グラフ** - 販売中vs販売終了の割合
4. **価格変動分析バーチャート** - 値下げ/値上げの状況

✅ **レポート自動生成**
- Markdown形式の分析レポート
- 最近売れた物件の詳細情報
- 価格変動率の計算

**実装ファイル**: 
- `scripts/visualize_tracking.py`
- 出力先: `docs/images/*.png`

### Phase 3: MLIT API連携（実験的）

✅ **国土交通省API統合**
- 既存の`real_estate_api.py`を活用
- 取引価格情報APIとの連携
- 類似物件のマッチング機能

✅ **マッチングアルゴリズム**
- 建物面積・土地面積での照合（±10%の許容範囲）
- 所在地での絞り込み
- 取引時期での絞り込み

✅ **参考情報として表示**
- 確実な同一物件ではないことを明記
- マッチング信頼度を表示
- 複数候補がある場合は全て表示

**実装ファイル**: `scripts/match_with_mlit.py`

---

## 🎯 実行結果（市川市のデータで検証）

### 追跡結果
- **追跡物件総数**: 11件
- **販売中**: 3件
- **販売終了（推定）**: 8件
- **平均販売期間**: 78.9日

### 価格変動分析
- **値下げした物件**: 2件
- **値上げした物件**: 1件
- **最大値下げ**: -300万円（-3.6%）

### 最長掲載物件
- 市川市堀之内４丁目: 181日間掲載後に販売終了
- 初回価格: 8,280万円 → 最終価格: 7,980万円

---

## 📊 生成されるデータ・グラフ

### 1. 追跡データベース (`tracking_db.json`)

```json
{
  "properties": {
    "property_id": {
      "location": "市川市中国分２丁目",
      "building_area": 130.58,
      "land_area": 103.00,
      "first_seen": "2025-10-01",
      "last_seen": "2026-03-01",
      "status": "active",
      "price_history": [
        {"date": "2025-10-01", "total_price": 2698, "change": null},
        {"date": "2026-03-01", "total_price": 2498, "change": -200}
      ]
    }
  }
}
```

### 2. 可視化グラフ

**生成されたグラフ**:
- `docs/images/listing_duration.png` - 販売期間分布
- `docs/images/price_timeline.png` - 価格変動タイムライン
- `docs/images/status_distribution.png` - ステータス円グラフ
- `docs/images/price_change_analysis.png` - 価格変動分析

### 3. レポート

- `data/tracking_report.md` - 分析レポート
- `data/mlit_matching_report.md` - MLIT照合レポート

---

## 🔧 使い方

### 基本的な実行方法

```bash
# 1. 物件追跡を実行（データベース更新）
python3 scripts/track_properties.py

# 2. グラフ生成
python3 scripts/visualize_tracking.py

# 3. MLIT APIとの照合（オプション、APIキー必要）
export REINFOLIB_API_KEY="your-api-key"
python3 scripts/match_with_mlit.py
```

### GitHub Actionsでの自動実行設定例

```yaml
name: Monthly Property Tracking

on:
  schedule:
    - cron: '0 0 1 * *'  # 毎月1日に実行

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
      
      - name: Track properties
        run: python3 scripts/track_properties.py
      
      - name: Generate visualizations
        run: python3 scripts/visualize_tracking.py
      
      - name: Commit results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add tracking_db.json data/*.md docs/images/*.png
          git commit -m "Update property tracking data"
          git push
```

---

## 🌐 国土交通省APIの活用可能性

### ✅ 可能なこと

**取引価格情報API (XIT001)** を使用して：
1. **実際の成約価格データ取得** - 過去の不動産取引情報
2. **地域・時期での絞り込み** - 都道府県・四半期単位
3. **物件詳細の取得** - 建物面積、土地面積、建築年など

### ⚠️ 制約事項

1. **物件の特定が困難**
   - MLITデータはプライバシー保護のため個別物件を特定できない形式
   - 面積・場所での推定マッチングのみ可能
   - 完全な確実性は期待できない

2. **タイムラグがある**
   - 取引データは四半期ごとに公開
   - 実際の成約から2〜6ヶ月遅れる
   - リアルタイム追跡には不向き

3. **マッチング精度に限界**
   - 同じエリアに類似物件がある場合、特定困難
   - 建物面積が完全一致しても別物件の可能性
   - **参考情報**としての利用に限定すべき

### 💡 推奨される活用方法

**スムストックデータのみでの追跡を主軸とし、MLIT APIは補助的に活用**

```
主要データソース: スムストック（確実、リアルタイム）
  ├─ 販売期間の追跡
  ├─ 価格変動の記録
  ├─ 販売終了の検出
  └─ 市場動向の分析

補助データソース: MLIT API（参考情報、四半期遅れ）
  └─ 類似物件の実際の成約価格
      └─ 「この近くで○○万円で取引された物件がある」
```

---

## 📈 このシステムで得られる価値あるデータ

### 1. 購入検討者向け

- **販売期間の傾向**: 「この価格帯なら平均120日で売れる」
- **価格戦略の洞察**: 「値下げは掲載60日後が多い」
- **市場の活発度**: 「このエリアは需要が高く早く売れる」
- **適正価格の判断**: 「似た物件がいくらで売れたか」

### 2. 売却検討者向け

- **適切な価格設定**: 市場データに基づく価格戦略
- **販売期間の予測**: どのくらいで売れそうか
- **値下げタイミング**: いつ値下げすべきか
- **エリア比較**: 売りやすいエリアはどこか

### 3. データ分析・研究者向け

- **中古住宅市場の動向分析**
- **ハウスメーカー別の売れ行き比較**
- **地域別不動産市場の活性度**
- **季節性・トレンドの発見**

---

## 🎯 実装の優先順位と理由

### ✅ Phase 1 & 2を最優先（完了）

**理由**:
- 確実に実現可能
- 高い精度のデータ
- ユーザーにとって価値が高い
- 実装コストが低い
- リアルタイム性が高い

### ⚪ Phase 3は補助的に実装（完了、オプション）

**理由**:
- マッチング精度に限界がある
- 四半期ごとのタイムラグ
- API利用料・レート制限の考慮必要
- 参考情報としては有用

---

## 📁 実装されたファイル一覧

```
scripts/
├── track_properties.py        # 物件追跡システム（Phase 1）
├── visualize_tracking.py      # 可視化システム（Phase 2）
└── match_with_mlit.py         # MLIT API連携（Phase 3）

docs/
├── sold_property_tracking_proposal.md  # 提案書
├── property_tracking_implementation.md # この実装報告書
└── images/
    ├── listing_duration.png
    ├── price_timeline.png
    ├── status_distribution.png
    └── price_change_analysis.png

data/
├── tracking_report.md         # 分析レポート
└── mlit_matching_report.md    # MLIT照合レポート

tracking_db.json               # 追跡データベース
```

---

## 🚀 次のステップ（推奨）

### 1. データ収集の拡大
- [ ] 他の市区町村のデータも追跡
- [ ] より長期間のデータ蓄積

### 2. 分析の高度化
- [ ] 季節性の分析
- [ ] ハウスメーカー別の詳細分析
- [ ] 価格帯別の販売速度分析

### 3. UI/UX改善
- [ ] インタラクティブなダッシュボード
- [ ] Plotlyでの動的グラフ
- [ ] GitHub Pagesでの公開

### 4. MLIT API活用の精緻化（オプション）
- [ ] マッチングアルゴリズムの改善
- [ ] 信頼度スコアの算出ロジック強化
- [ ] 地価公示データとの組み合わせ

---

## 📝 まとめ

### ✅ 実現できたこと

1. **確実な販売追跡システム** - スムストックデータのみで販売終了を検出
2. **価格変動の記録** - 時系列での価格推移を追跡
3. **統計分析とレポート** - 平均販売期間、価格変動率など
4. **可視化システム** - 4種類のグラフで直感的に理解
5. **MLIT API連携の基盤** - 参考情報として実際の成約価格を照合

### 🎯 このシステムの価値

- **データに基づく意思決定** - 感覚ではなく実データで判断
- **市場の透明性向上** - 価格・販売期間の実態を可視化
- **購入・売却の指針** - より良い不動産取引をサポート

### 💡 MLIT APIの位置づけ

国土交通省の不動産情報ライブラリAPIは、**参考情報として有用**ですが、スムストックデータのみでも十分に価値あるシステムが構築できました。MLIT APIは補助的な役割として、ユーザーに追加の市場情報を提供します。

---

**実装者**: GitHub Copilot CLI  
**実装日**: 2026-05-02  
**テスト済み**: 市川市のデータで動作確認完了
