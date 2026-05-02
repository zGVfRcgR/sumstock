#!/usr/bin/env python3
"""
Property Tracking System - Phase 1
物件追跡システム - 第1段階

スムストックの月次データを比較し、販売終了物件を検出する
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re


class PropertyTracker:
    """物件追跡システム"""
    
    def __init__(self, data_dir: str = "data", tracking_db: str = "tracking_db.json"):
        """
        Args:
            data_dir: スクレイピングデータのディレクトリ
            tracking_db: 追跡データベースファイル
        """
        self.data_dir = Path(data_dir)
        self.tracking_db_path = Path(tracking_db)
        self.tracking_db = self._load_tracking_db()
    
    def _load_tracking_db(self) -> Dict:
        """追跡データベースを読み込む"""
        if self.tracking_db_path.exists():
            with open(self.tracking_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"properties": {}, "statistics": {}}
    
    def _save_tracking_db(self):
        """追跡データベースを保存"""
        with open(self.tracking_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.tracking_db, f, ensure_ascii=False, indent=2)
    
    def generate_property_id(self, location: str, building_area: float, 
                            land_area: float) -> str:
        """
        物件のユニークIDを生成
        
        Args:
            location: 所在地（例：市川市中国分２丁目）
            building_area: 建物面積
            land_area: 土地面積
        
        Returns:
            ハッシュベースのユニークID
        """
        # 面積を丸めて多少の誤差を吸収
        building_area_rounded = round(building_area, 1)
        land_area_rounded = round(land_area, 1)
        
        # 所在地を正規化（全角・半角、スペースを統一）
        location_normalized = location.strip()
        
        # ハッシュ生成
        hash_input = f"{location_normalized}_{building_area_rounded}_{land_area_rounded}"
        return hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:16]
    
    def parse_markdown_data(self, md_file: Path) -> List[Dict]:
        """
        Markdownファイルから物件データを抽出
        
        Args:
            md_file: Markdownファイルのパス
        
        Returns:
            物件データのリスト
        """
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 取得日を抽出
        date_match = re.search(r'## 取得日: (\d{4})年(\d{2})月(\d{2})日', content)
        if not date_match:
            return []
        
        date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
        
        # 表データを抽出
        properties = []
        table_started = False
        
        for line in content.split('\n'):
            if line.startswith('| 所在地'):
                table_started = True
                continue
            if table_started and line.startswith('|') and not line.startswith('|---'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 8 and parts[0] and not parts[0].startswith('所在地'):
                    try:
                        property_data = {
                            'location': parts[0],
                            'total_price': self._parse_price(parts[1]),
                            'building_price': self._parse_price(parts[2]),
                            'building_area': self._parse_area(parts[3]),
                            'building_unit_price': self._parse_price(parts[4]),
                            'land_price': self._parse_price(parts[5]),
                            'land_area': self._parse_area(parts[6]),
                            'land_unit_price': self._parse_price(parts[7]),
                            'house_maker': parts[8] if len(parts) > 8 else '',
                            'date': date_str
                        }
                        properties.append(property_data)
                    except Exception as e:
                        print(f"Warning: Failed to parse line: {line[:50]}... Error: {e}")
        
        return properties
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """価格文字列をパース"""
        if not price_str or price_str == '-':
            return None
        price_str = re.sub(r'[万円,約/m²]', '', price_str).strip()
        try:
            return float(price_str)
        except ValueError:
            return None
    
    def _parse_area(self, area_str: str) -> Optional[float]:
        """面積文字列をパース"""
        if not area_str or area_str == '-':
            return None
        area_str = re.sub(r'[m²㎡,]', '', area_str).strip()
        try:
            return float(area_str)
        except ValueError:
            return None
    
    def update_property_tracking(self, properties: List[Dict], scan_date: str):
        """
        物件追跡データを更新
        
        Args:
            properties: 物件データのリスト
            scan_date: スキャン日（YYYY-MM-DD形式）
        """
        current_property_ids = set()
        
        for prop in properties:
            if not prop['building_area'] or not prop['land_area']:
                continue
            
            property_id = self.generate_property_id(
                prop['location'],
                prop['building_area'],
                prop['land_area']
            )
            current_property_ids.add(property_id)
            
            if property_id not in self.tracking_db['properties']:
                # 新規物件
                self.tracking_db['properties'][property_id] = {
                    'property_id': property_id,
                    'location': prop['location'],
                    'building_area': prop['building_area'],
                    'land_area': prop['land_area'],
                    'house_maker': prop['house_maker'],
                    'first_seen': scan_date,
                    'last_seen': scan_date,
                    'status': 'active',
                    'price_history': [{
                        'date': scan_date,
                        'total_price': prop['total_price'],
                        'change': None
                    }]
                }
            else:
                # 既存物件の更新
                tracked = self.tracking_db['properties'][property_id]
                tracked['last_seen'] = scan_date
                
                # 価格変更をチェック
                last_price = tracked['price_history'][-1]['total_price']
                current_price = prop['total_price']
                
                if current_price != last_price:
                    change = current_price - last_price if last_price else None
                    tracked['price_history'].append({
                        'date': scan_date,
                        'total_price': current_price,
                        'change': change
                    })
        
        # 消えた物件を検出
        for property_id, tracked in self.tracking_db['properties'].items():
            if tracked['status'] == 'active' and property_id not in current_property_ids:
                # 最後に見た日から今回のスキャン日が異なれば、販売終了と判定
                if tracked['last_seen'] != scan_date:
                    tracked['status'] = 'sold_presumed'
                    tracked['sold_date'] = scan_date
        
        self._save_tracking_db()
    
    def get_statistics(self) -> Dict:
        """統計情報を計算"""
        stats = {
            'total_tracked': len(self.tracking_db['properties']),
            'active': 0,
            'sold_presumed': 0,
            'avg_listing_duration': 0,
            'price_change_stats': {
                'decreased': 0,
                'increased': 0,
                'unchanged': 0
            }
        }
        
        listing_durations = []
        
        for prop in self.tracking_db['properties'].values():
            if prop['status'] == 'active':
                stats['active'] += 1
            elif prop['status'] == 'sold_presumed':
                stats['sold_presumed'] += 1
                
                # 販売期間を計算
                first_seen = datetime.strptime(prop['first_seen'], '%Y-%m-%d')
                sold_date = datetime.strptime(prop.get('sold_date', prop['last_seen']), '%Y-%m-%d')
                duration = (sold_date - first_seen).days
                listing_durations.append(duration)
            
            # 価格変動を分析
            if len(prop['price_history']) > 1:
                first_price = prop['price_history'][0]['total_price']
                last_price = prop['price_history'][-1]['total_price']
                if last_price < first_price:
                    stats['price_change_stats']['decreased'] += 1
                elif last_price > first_price:
                    stats['price_change_stats']['increased'] += 1
                else:
                    stats['price_change_stats']['unchanged'] += 1
        
        if listing_durations:
            stats['avg_listing_duration'] = sum(listing_durations) / len(listing_durations)
        
        return stats
    
    def generate_report(self) -> str:
        """分析レポートを生成"""
        stats = self.get_statistics()
        
        report = f"""
# 物件追跡レポート
生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概要
- 追跡中の物件総数: {stats['total_tracked']}件
- 販売中: {stats['active']}件
- 販売終了（推定）: {stats['sold_presumed']}件

## 販売期間
- 平均販売期間: {stats['avg_listing_duration']:.1f}日

## 価格変動
- 値下げした物件: {stats['price_change_stats']['decreased']}件
- 値上げした物件: {stats['price_change_stats']['increased']}件
- 価格変更なし: {stats['price_change_stats']['unchanged']}件

## 最近販売終了した物件（推定）
"""
        
        # 最近販売終了した物件を表示
        sold_properties = [
            prop for prop in self.tracking_db['properties'].values()
            if prop['status'] == 'sold_presumed'
        ]
        sold_properties.sort(key=lambda x: x.get('sold_date', ''), reverse=True)
        
        for prop in sold_properties[:10]:
            first_price = prop['price_history'][0]['total_price']
            last_price = prop['price_history'][-1]['total_price']
            price_change = last_price - first_price if first_price else 0
            price_change_pct = (price_change / first_price * 100) if first_price else 0
            
            first_seen = datetime.strptime(prop['first_seen'], '%Y-%m-%d')
            sold_date = datetime.strptime(prop.get('sold_date', prop['last_seen']), '%Y-%m-%d')
            duration = (sold_date - first_seen).days
            
            report += f"""
### {prop['location']}
- 掲載期間: {duration}日
- 初回価格: {first_price:.0f}万円
- 最終価格: {last_price:.0f}万円
- 価格変動: {price_change:+.0f}万円 ({price_change_pct:+.1f}%)
- 建物面積: {prop['building_area']}m²
- 土地面積: {prop['land_area']}m²
"""
        
        return report


def main():
    """メイン処理"""
    tracker = PropertyTracker()
    
    # data/千葉県/市川市/配下のMarkdownファイルを処理
    city_dir = tracker.data_dir / "千葉県" / "市川市"
    
    if not city_dir.exists():
        print(f"Error: {city_dir} が見つかりません")
        return
    
    # 日付順にソートしてMarkdownファイルを処理
    md_files = sorted([f for f in city_dir.glob("*.md") if f.stem != "index"])
    
    print(f"処理するファイル数: {len(md_files)}")
    
    for md_file in md_files:
        print(f"処理中: {md_file.name}")
        properties = tracker.parse_markdown_data(md_file)
        
        if properties:
            # ファイル名から日付を取得（YYYY-MM-DD.md形式）
            scan_date = md_file.stem
            tracker.update_property_tracking(properties, scan_date)
            print(f"  {len(properties)}件の物件を処理")
    
    # レポート生成
    report = tracker.generate_report()
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    # レポートをファイルに保存
    report_path = tracker.data_dir / "tracking_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nレポートを保存しました: {report_path}")


if __name__ == "__main__":
    main()
