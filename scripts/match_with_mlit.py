#!/usr/bin/env python3
"""
MLIT API Integration Example - Phase 3
国土交通省API連携の例（実験的）

売却済みと推定される物件に対して、MLITの取引価格データから類似物件を検索
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# real_estate_api.pyをインポート
try:
    from real_estate_api import RealEstateInfoLibAPI, RealEstateInfoLibAPIError
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from real_estate_api import RealEstateInfoLibAPI, RealEstateInfoLibAPIError


class MLITPropertyMatcher:
    """MLIT APIを使った物件マッチングクラス"""
    
    def __init__(self, tracking_db_path: str = "tracking_db.json", 
                 api_key: Optional[str] = None):
        """
        Args:
            tracking_db_path: 追跡データベースファイル
            api_key: MLIT APIキー（環境変数REINFOLIB_API_KEYから取得も可能）
        """
        with open(tracking_db_path, 'r', encoding='utf-8') as f:
            self.tracking_db = json.load(f)
        
        self.api_key = api_key or os.getenv("REINFOLIB_API_KEY")
        if self.api_key:
            self.api = RealEstateInfoLibAPI(self.api_key)
        else:
            print("Warning: REINFOLIB_API_KEY not set. MLIT API features disabled.")
            self.api = None
    
    def get_sold_properties(self) -> List[Dict]:
        """販売終了した物件のリストを取得"""
        sold_properties = []
        
        for prop_id, prop in self.tracking_db['properties'].items():
            if prop['status'] == 'sold_presumed':
                sold_properties.append(prop)
        
        return sold_properties
    
    def find_similar_transactions(self, property_data: Dict, 
                                   prefecture_code: str = "12") -> List[Dict]:
        """
        MLIT APIから類似取引を検索
        
        Args:
            property_data: 物件データ
            prefecture_code: 都道府県コード（デフォルト: 12 = 千葉県）
        
        Returns:
            類似取引のリスト
        """
        if not self.api:
            print("MLIT API is not available. Set REINFOLIB_API_KEY environment variable.")
            return []
        
        # 推定売却日から四半期を計算
        sold_date = datetime.strptime(
            property_data.get('sold_date', property_data['last_seen']), 
            '%Y-%m-%d'
        )
        year = str(sold_date.year)
        quarter = str((sold_date.month - 1) // 3 + 1)
        
        try:
            # MLIT APIから取引価格データを取得
            print(f"Fetching MLIT data for {year} Q{quarter}, area {prefecture_code}...")
            data = self.api.get_transaction_price(
                year=year,
                area=prefecture_code,
                quarter=quarter
            )
            
            # 類似物件を抽出
            similar_transactions = []
            
            if 'features' in data:
                for feature in data['features']:
                    props = feature.get('properties', {})
                    
                    # 建物面積でフィルタリング（±10%以内）
                    building_area = props.get('建物面積', 0)
                    land_area = props.get('土地面積', 0)
                    
                    if building_area and land_area:
                        building_match = abs(building_area - property_data['building_area']) / property_data['building_area'] < 0.1
                        land_match = abs(land_area - property_data['land_area']) / property_data['land_area'] < 0.1
                        
                        # 所在地でもフィルタリング（同じ市区町村）
                        location = props.get('市区町村名', '')
                        location_match = any(loc in property_data['location'] for loc in location.split())
                        
                        if building_match and land_match and location_match:
                            similar_transactions.append({
                                'transaction_price': props.get('取引価格', 'N/A'),
                                'building_area': building_area,
                                'land_area': land_area,
                                'location': props.get('所在地', 'N/A'),
                                'transaction_period': props.get('取引時期', 'N/A'),
                                'building_year': props.get('建築年', 'N/A'),
                                'structure': props.get('構造', 'N/A'),
                                'confidence': 'high' if building_match and land_match else 'medium'
                            })
            
            return similar_transactions
        
        except RealEstateInfoLibAPIError as e:
            print(f"MLIT API Error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def generate_matching_report(self, output_path: str = "data/mlit_matching_report.md"):
        """MLITマッチングレポートを生成"""
        sold_properties = self.get_sold_properties()
        
        report = f"""# MLIT API マッチングレポート
生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概要
このレポートは、スムストックで販売終了した物件と、国土交通省の不動産取引価格情報を照合した結果です。

⚠️ **注意**: このマッチングは参考情報です。同一物件であることを保証するものではありません。

---

## 販売終了物件とMLIT取引データの照合

"""
        
        for i, prop in enumerate(sold_properties, 1):
            report += f"""
### {i}. {prop['location']}

**スムストックデータ:**
- 建物面積: {prop['building_area']}m²
- 土地面積: {prop['land_area']}m²
- 掲載期間: {prop['first_seen']} ～ {prop['last_seen']}
- 最終価格: {prop['price_history'][-1]['total_price']:.0f}万円

"""
            
            # MLIT APIが利用可能な場合、類似取引を検索
            if self.api:
                similar = self.find_similar_transactions(prop, prefecture_code="12")
                
                if similar:
                    report += "**類似取引（MLIT）:**\n\n"
                    for j, trans in enumerate(similar[:3], 1):  # 最大3件
                        report += f"""
{j}. 取引価格: {trans['transaction_price']}
   - 建物面積: {trans['building_area']}m²
   - 土地面積: {trans['land_area']}m²
   - 取引時期: {trans['transaction_period']}
   - 建築年: {trans['building_year']}
   - マッチング信頼度: {trans['confidence']}
"""
                else:
                    report += "**類似取引が見つかりませんでした**\n"
            else:
                report += "**MLIT APIが利用できません。環境変数REINFOLIB_API_KEYを設定してください。**\n"
            
            report += "\n---\n"
        
        # レポートを保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Matching report saved: {output_path}")
        return report


def main():
    """メイン処理"""
    print("=== MLIT API Integration Example (Phase 3) ===\n")
    
    # APIキーのチェック
    api_key = os.getenv("REINFOLIB_API_KEY")
    if not api_key:
        print("⚠️  環境変数 REINFOLIB_API_KEY が設定されていません。")
        print("    MLIT APIとの照合機能は無効化されます。\n")
        print("設定方法:")
        print("  export REINFOLIB_API_KEY='your-api-key-here'\n")
    
    # マッチャーを初期化してレポート生成
    matcher = MLITPropertyMatcher()
    
    # 販売終了物件の数を表示
    sold_count = len(matcher.get_sold_properties())
    print(f"販売終了物件数: {sold_count}件\n")
    
    # レポート生成
    print("マッチングレポートを生成中...\n")
    matcher.generate_matching_report()
    
    print("\n✅ 完了しました！")
    
    if not api_key:
        print("\n💡 ヒント: MLIT APIキーを設定すると、実際の取引価格との照合が可能になります。")


if __name__ == "__main__":
    main()
