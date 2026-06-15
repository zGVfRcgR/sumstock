#!/usr/bin/env python3
"""
Property Tracking Visualization
物件追跡データの可視化
"""

import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import japanize_matplotlib  # noqa: F401 – 日本語フォントを有効化
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import numpy as np


class PropertyVisualizer:
    """物件追跡データの可視化クラス"""
    
    def __init__(self, tracking_db_path: str, city_name: str = "", output_dir: str = "docs/images"):
        """
        Args:
            tracking_db_path: 追跡データベースファイルのパス
            city_name: 市区町村名（グラフタイトル用）
            output_dir: グラフ出力先ディレクトリ
        """
        with open(tracking_db_path, 'r', encoding='utf-8') as f:
            self.tracking_db = json.load(f)
        
        self.city_name = city_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # japanize_matplotlib のインポートにより日本語フォントが自動設定される
        plt.rcParams['axes.unicode_minus'] = False
    
    def _title(self, base: str) -> str:
        """市名付きタイトルを返す"""
        return f"{self.city_name} {base}" if self.city_name else base

    def plot_listing_duration_distribution(self):
        """販売期間の分布をプロット"""
        output_path = str(self.output_dir / "listing_duration.png")
        durations = []
        
        for prop in self.tracking_db['properties'].values():
            if prop['status'] == 'sold_presumed':
                first_seen = datetime.strptime(prop['first_seen'], '%Y-%m-%d')
                sold_date = datetime.strptime(prop.get('sold_date', prop['last_seen']), '%Y-%m-%d')
                duration = (sold_date - first_seen).days
                durations.append(duration)
        
        if not durations:
            print("No sold properties to visualize")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # ヒストグラム
        n, bins, patches = ax.hist(durations, bins=10, edgecolor='black', alpha=0.7)
        
        # 平均値の線
        mean_duration = np.mean(durations)
        ax.axvline(mean_duration, color='red', linestyle='--', linewidth=2,
                   label=f'平均: {mean_duration:.1f}日')
        
        ax.set_xlabel('掲載期間（日）', fontsize=12)
        ax.set_ylabel('物件数', fontsize=12)
        ax.set_title(self._title('物件掲載期間の分布'), fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_price_change_timeline(self):
        """価格変動のタイムラインをプロット"""
        output_path = str(self.output_dir / "price_timeline.png")
        fig, ax = plt.subplots(figsize=(12, 8))
        
        property_index = 0
        legend_labels = []
        
        for prop_id, prop in self.tracking_db['properties'].items():
            if len(prop['price_history']) > 1:
                dates = [datetime.strptime(h['date'], '%Y-%m-%d') for h in prop['price_history']]
                prices = [h['total_price'] for h in prop['price_history']]
                
                color = 'green' if prop['status'] == 'sold_presumed' else 'blue'
                marker = 'o' if prop['status'] == 'sold_presumed' else '^'
                
                ax.plot(dates, prices, marker=marker, linewidth=2, 
                       markersize=6, alpha=0.7, color=color)
                
                status_label = '販売終了（推定）' if prop['status'] == 'sold_presumed' else '販売中'
                if property_index < 3:
                    legend_labels.append(f"{prop['location'][:15]}... ({status_label})")
                
                property_index += 1
        
        ax.set_xlabel('日付', fontsize=12)
        ax.set_ylabel('価格（万円）', fontsize=12)
        ax.set_title(self._title('物件価格の推移'), fontsize=14, fontweight='bold')
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45, ha='right')
        
        ax.grid(True, alpha=0.3)
        if legend_labels:
            ax.legend(legend_labels[:3], loc='best')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_status_pie_chart(self):
        """物件ステータスの円グラフ"""
        output_path = str(self.output_dir / "status_distribution.png")
        status_counts = {'販売中': 0, '販売終了（推定）': 0}
        
        for prop in self.tracking_db['properties'].values():
            if prop['status'] == 'active':
                status_counts['販売中'] += 1
            elif prop['status'] == 'sold_presumed':
                status_counts['販売終了（推定）'] += 1
        
        if sum(status_counts.values()) == 0:
            print("No data to visualize")
            return

        fig, ax = plt.subplots(figsize=(8, 8))
        
        colors = ['#3498db', '#2ecc71']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(
            status_counts.values(),
            labels=status_counts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=explode,
            textprops={'fontsize': 12}
        )
        
        for i, (label, value) in enumerate(status_counts.items()):
            texts[i].set_text(f"{label}\n({value}件)")
        
        ax.set_title(self._title('物件ステータスの分布'), fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_price_change_analysis(self):
        """価格変動の分析グラフ"""
        output_path = str(self.output_dir / "price_change_analysis.png")
        price_changes = []
        
        for prop in self.tracking_db['properties'].values():
            if len(prop['price_history']) > 1:
                first_price = prop['price_history'][0]['total_price']
                last_price = prop['price_history'][-1]['total_price']
                
                if first_price:
                    change_pct = ((last_price - first_price) / first_price) * 100
                    price_changes.append({
                        'location': prop['location'],
                        'change_pct': change_pct,
                        'status': prop['status']
                    })
        
        if not price_changes:
            print("No price changes to visualize")
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        price_changes.sort(key=lambda x: x['change_pct'])
        
        colors = ['red' if pc['change_pct'] < 0 else 'green' for pc in price_changes]
        
        y_pos = range(len(price_changes))
        changes = [pc['change_pct'] for pc in price_changes]
        labels = [pc['location'][:25] + '...' if len(pc['location']) > 25 
                 else pc['location'] for pc in price_changes]
        
        ax.barh(y_pos, changes, color=colors, alpha=0.7)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel('価格変動率（%）', fontsize=12)
        ax.set_title(self._title('物件別価格変動'), fontsize=14, fontweight='bold')
        ax.axvline(0, color='black', linewidth=0.8)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def generate_all_visualizations(self):
        """すべての可視化を生成"""
        print(f"Generating visualizations for {self.city_name or 'all'}...")
        
        self.plot_listing_duration_distribution()
        self.plot_price_change_timeline()
        self.plot_status_pie_chart()
        self.plot_price_change_analysis()
        
        print(f"✅ All visualizations saved to {self.output_dir}")


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='物件追跡データの可視化')
    parser.add_argument('--tracking-db', help='追跡DBファイルパス（指定しない場合は全市自動検出）')
    parser.add_argument('--city-name', default='', help='市区町村名（グラフタイトル用）')
    parser.add_argument('--output-dir', help='グラフ出力ディレクトリ（省略可）')
    parser.add_argument('--data-dir', default='data', help='データディレクトリ（--tracking-db省略時に使用）')
    args = parser.parse_args()

    if args.tracking_db:
        output_dir = args.output_dir or 'docs/images'
        visualizer = PropertyVisualizer(args.tracking_db, args.city_name, output_dir)
        visualizer.generate_all_visualizations()
    else:
        # 全市自動処理
        tracking_dir = Path(args.data_dir) / "tracking"
        if not tracking_dir.exists():
            print(f"Error: {tracking_dir} が見つかりません。先に track_properties.py を実行してください。")
            return

        db_files = sorted(tracking_dir.glob("*_tracking_db.json"))
        if not db_files:
            print(f"Error: {tracking_dir} にDBファイルがありません")
            return

        print(f"可視化対象: {len(db_files)}市区町村")
        for db_file in db_files:
            # ファイル名から市名を抽出: 千葉県_市川市_tracking_db.json → 市川市
            stem = db_file.stem  # 千葉県_市川市_tracking_db
            parts = stem.replace('_tracking_db', '').split('_')
            city_name = '_'.join(parts[1:]) if len(parts) >= 2 else stem
            pref_city = stem.replace('_tracking_db', '')  # 千葉県_市川市

            output_dir = args.output_dir or f"docs/images/{pref_city}"
            visualizer = PropertyVisualizer(str(db_file), city_name, output_dir)
            visualizer.generate_all_visualizations()


if __name__ == "__main__":
    main()

    
    def plot_listing_duration_distribution(self, output_path: str = "docs/images/listing_duration.png"):
        """販売期間の分布をプロット"""
        durations = []
        
        for prop in self.tracking_db['properties'].values():
            if prop['status'] == 'sold_presumed':
                first_seen = datetime.strptime(prop['first_seen'], '%Y-%m-%d')
                sold_date = datetime.strptime(prop.get('sold_date', prop['last_seen']), '%Y-%m-%d')
                duration = (sold_date - first_seen).days
                durations.append(duration)
        
        if not durations:
            print("No sold properties to visualize")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # ヒストグラム
        n, bins, patches = ax.hist(durations, bins=10, edgecolor='black', alpha=0.7)
        
        # 平均値の線
        mean_duration = np.mean(durations)
        ax.axvline(mean_duration, color='red', linestyle='--', linewidth=2,
                   label=f'平均: {mean_duration:.1f}日')
        
        ax.set_xlabel('掲載期間（日）', fontsize=12)
        ax.set_ylabel('物件数', fontsize=12)
        ax.set_title('物件掲載期間の分布', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # ディレクトリを作成
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_price_change_timeline(self, output_path: str = "docs/images/price_timeline.png"):
        """価格変動のタイムラインをプロット"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        property_index = 0
        legend_labels = []
        
        for prop_id, prop in self.tracking_db['properties'].items():
            if len(prop['price_history']) > 1:
                dates = [datetime.strptime(h['date'], '%Y-%m-%d') for h in prop['price_history']]
                prices = [h['total_price'] for h in prop['price_history']]
                
                # プロット
                color = 'green' if prop['status'] == 'sold_presumed' else 'blue'
                marker = 'o' if prop['status'] == 'sold_presumed' else '^'
                
                ax.plot(dates, prices, marker=marker, linewidth=2, 
                       markersize=6, alpha=0.7, color=color)
                
                # ラベル（最初の3件のみ）
                status_label = '販売終了（推定）' if prop['status'] == 'sold_presumed' else '販売中'
                if property_index < 3:
                    legend_labels.append(f"{prop['location'][:15]}... ({status_label})")
                
                property_index += 1
        
        ax.set_xlabel('日付', fontsize=12)
        ax.set_ylabel('価格（万円）', fontsize=12)
        ax.set_title('物件価格の推移', fontsize=14, fontweight='bold')
        
        # 日付フォーマット
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45, ha='right')
        
        ax.grid(True, alpha=0.3)
        ax.legend(legend_labels[:3], loc='best')
        
        plt.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_status_pie_chart(self, output_path: str = "docs/images/status_distribution.png"):
        """物件ステータスの円グラフ"""
        status_counts = {'販売中': 0, '販売終了（推定）': 0}
        
        for prop in self.tracking_db['properties'].values():
            if prop['status'] == 'active':
                status_counts['販売中'] += 1
            elif prop['status'] == 'sold_presumed':
                status_counts['販売終了（推定）'] += 1
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        colors = ['#3498db', '#2ecc71']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(
            status_counts.values(),
            labels=status_counts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=explode,
            textprops={'fontsize': 12}
        )
        
        # 件数を追加
        for i, (label, value) in enumerate(status_counts.items()):
            texts[i].set_text(f"{label}\n({value}件)")
        
        ax.set_title('物件ステータスの分布', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_price_change_analysis(self, output_path: str = "docs/images/price_change_analysis.png"):
        """価格変動の分析グラフ"""
        price_changes = []
        
        for prop in self.tracking_db['properties'].values():
            if len(prop['price_history']) > 1:
                first_price = prop['price_history'][0]['total_price']
                last_price = prop['price_history'][-1]['total_price']
                
                if first_price:
                    change_pct = ((last_price - first_price) / first_price) * 100
                    price_changes.append({
                        'location': prop['location'],
                        'change_pct': change_pct,
                        'status': prop['status']
                    })
        
        if not price_changes:
            print("No price changes to visualize")
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # ソート
        price_changes.sort(key=lambda x: x['change_pct'])
        
        # バーの色を決定（値下げは赤、値上げは緑）
        colors = ['red' if pc['change_pct'] < 0 else 'green' for pc in price_changes]
        
        # 横棒グラフ
        y_pos = range(len(price_changes))
        changes = [pc['change_pct'] for pc in price_changes]
        labels = [pc['location'][:25] + '...' if len(pc['location']) > 25 
                 else pc['location'] for pc in price_changes]
        
        bars = ax.barh(y_pos, changes, color=colors, alpha=0.7)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel('価格変動率（%）', fontsize=12)
        ax.set_title('物件別価格変動', fontsize=14, fontweight='bold')
        ax.axvline(0, color='black', linewidth=0.8)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def generate_all_visualizations(self):
        """すべての可視化を生成"""
        print("Generating visualizations...")
        
        self.plot_listing_duration_distribution()
        self.plot_price_change_timeline()
        self.plot_status_pie_chart()
        self.plot_price_change_analysis()
        
        print("\nAll visualizations generated successfully!")


if __name__ == "__main__":
    main()
