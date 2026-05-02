# Property Tracking Scripts

物件追跡システムのスクリプト群です。

## スクリプト一覧

### track_properties.py
物件の追跡と分析を行うメインスクリプト。

**機能:**
- 月次データの比較
- 販売終了物件の検出
- 価格変動の記録
- 統計分析

**実行:**
```bash
python3 scripts/track_properties.py
```

### visualize_tracking.py
追跡データを可視化するスクリプト。

**機能:**
- 販売期間の分布グラフ
- 価格変動タイムライン
- ステータス分布円グラフ
- 価格変動分析バーチャート

**実行:**
```bash
python3 scripts/visualize_tracking.py
```

### match_with_mlit.py
国土交通省APIとの照合スクリプト（オプション）。

**機能:**
- 類似物件の検索
- マッチング候補の抽出
- 参考情報レポート生成

**実行:**
```bash
export REINFOLIB_API_KEY="your-api-key"
python3 scripts/match_with_mlit.py
```

## 依存関係

```bash
pip install matplotlib numpy
```

## 詳細ドキュメント

- [クイックスタートガイド](../docs/QUICK_START_TRACKING.md)
- [システム概要](../PROPERTY_TRACKING_SUMMARY.md)
- [提案書](../docs/sold_property_tracking_proposal.md)
- [実装報告](../docs/property_tracking_implementation.md)
