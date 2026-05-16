#!/usr/bin/env python3
"""
物件追跡ダッシュボード インデックスページ生成スクリプト

data/reports/ 配下の月次レポートをスキャンして、
GitHub Pages 用の tracking.md とサブページを生成する。
"""

from datetime import datetime
from pathlib import Path
import json
import argparse


def discover_reports(data_dir: Path):
    """
    data/reports/YYYY-MM/ 配下の全レポートを検出

    Returns:
        dict: { 'YYYY-MM': { 'prefecture_city': Path } }
    """
    reports_dir = data_dir / "reports"
    result = {}

    if not reports_dir.exists():
        return result

    for month_dir in sorted(reports_dir.iterdir(), reverse=True):
        if not month_dir.is_dir() or month_dir.name == "latest":
            continue
        # YYYY-MM 形式かチェック
        try:
            datetime.strptime(month_dir.name, '%Y-%m')
        except ValueError:
            continue

        month_key = month_dir.name
        result[month_key] = {}

        for report_file in sorted(month_dir.glob("*_report.md")):
            # 千葉県_市川市_report.md → 千葉県_市川市
            pref_city = report_file.stem.replace('_report', '')
            result[month_key][pref_city] = report_file

    return result


def discover_tracking_dbs(data_dir: Path):
    """data/tracking/ 配下の全追跡DBを検出"""
    tracking_dir = data_dir / "tracking"
    if not tracking_dir.exists():
        return {}

    dbs = {}
    for db_file in sorted(tracking_dir.glob("*_tracking_db.json")):
        pref_city = db_file.stem.replace('_tracking_db', '')
        dbs[pref_city] = db_file
    return dbs


def load_stats(db_path: Path) -> dict:
    """追跡DBから統計情報を読み込む"""
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
        props = db.get('properties', {})
        active = sum(1 for p in props.values() if p['status'] == 'active')
        sold = sum(1 for p in props.values() if p['status'] == 'sold_presumed')

        durations = []
        for p in props.values():
            if p['status'] == 'sold_presumed':
                first = datetime.strptime(p['first_seen'], '%Y-%m-%d')
                end = datetime.strptime(p.get('sold_date', p['last_seen']), '%Y-%m-%d')
                durations.append((end - first).days)

        avg_days = sum(durations) / len(durations) if durations else 0
        return {
            'total': len(props),
            'active': active,
            'sold': sold,
            'avg_days': avg_days,
        }
    except Exception:
        return {'total': 0, 'active': 0, 'sold': 0, 'avg_days': 0}


def generate_city_page(pref_city: str, month_reports: dict, db_path: Path,
                       output_dir: Path, baseurl: str = "/sumstock"):
    """
    市区町村ごとのダッシュボードページを生成

    output_dir/tracking/{pref_city}.md
    """
    parts = pref_city.split('_', 1)
    pref = parts[0] if len(parts) >= 2 else ''
    city = parts[1] if len(parts) >= 2 else pref_city

    output_path = output_dir / "tracking" / f"{pref_city}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stats = load_stats(db_path) if db_path and db_path.exists() else {}
    img_base = f"{baseurl}/docs/images/{pref_city}"

    lines = [
        "---",
        f"title: {city} 物件追跡ダッシュボード",
        "layout: default",
        f"parent: 物件追跡ダッシュボード",
        "nav_order: 1",
        "---",
        "",
        f"# {pref} {city} 物件追跡ダッシュボード",
        "",
        f"> データ更新: {datetime.now().strftime('%Y年%m月%d日')}",
        "",
        "## 📊 サマリー",
        "",
        "| 指標 | 値 |",
        "| --- | --- |",
        f"| 追跡物件数 | {stats.get('total', '-')}件 |",
        f"| 販売中 | {stats.get('active', '-')}件 |",
        f"| 販売終了（推定） | {stats.get('sold', '-')}件 |",
        f"| 平均掲載期間 | {stats.get('avg_days', 0):.1f}日 |",
        "",
        "## 📈 可視化",
        "",
        f"![掲載期間分布]({img_base}/listing_duration.png)",
        "",
        f"![価格推移]({img_base}/price_timeline.png)",
        "",
        f"![ステータス分布]({img_base}/status_distribution.png)",
        "",
        f"![価格変動分析]({img_base}/price_change_analysis.png)",
        "",
        "## 📅 月次レポート一覧",
        "",
        "| 月 | リンク |",
        "| --- | --- |",
    ]

    for month in sorted(month_reports.keys(), reverse=True):
        if pref_city in month_reports[month]:
            lines.append(f"| {month} | [レポートを見る]({baseurl}/data/reports/{month}/{pref_city}_report) |")

    lines += [
        "",
        "---",
        f"[← ダッシュボードトップに戻る]({baseurl}/tracking)",
    ]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    return output_path


def generate_tracking_index(data_dir: Path, output_dir: Path, baseurl: str = "/sumstock"):
    """メインの tracking.md インデックスページを生成"""
    all_reports = discover_reports(data_dir)
    dbs = discover_tracking_dbs(data_dir)

    # 全市のセット
    all_cities = set()
    for month_cities in all_reports.values():
        all_cities.update(month_cities.keys())
    all_cities.update(dbs.keys())
    all_cities = sorted(all_cities)

    # 市ごとのサブページを生成
    for pref_city in all_cities:
        db_path = dbs.get(pref_city)
        generate_city_page(pref_city, all_reports, db_path, output_dir, baseurl)

    # メインインデックスを生成
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    index_path = output_dir / "tracking.md"

    lines = [
        "---",
        "title: 物件追跡ダッシュボード",
        "layout: default",
        "nav_order: 2",
        "has_children: true",
        "---",
        "",
        "# 🏠 物件追跡ダッシュボード",
        "",
        f"> 最終更新: {now}",
        "",
        "スムストックの中古住宅物件データを毎月追跡し、価格変動・販売期間を分析します。",
        "",
        "## 🏙️ 市区町村別ダッシュボード",
        "",
    ]

    # 市ごとのサマリーテーブル
    lines += [
        "| 市区町村 | 追跡件数 | 販売中 | 販売終了(推定) | 平均掲載期間 | 詳細 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for pref_city in all_cities:
        parts = pref_city.split('_', 1)
        city = parts[1] if len(parts) >= 2 else pref_city
        stats = load_stats(dbs[pref_city]) if pref_city in dbs else {}
        lines.append(
            f"| {city} "
            f"| {stats.get('total', '-')} "
            f"| {stats.get('active', '-')} "
            f"| {stats.get('sold', '-')} "
            f"| {stats.get('avg_days', 0):.1f}日 "
            f"| [詳細]({baseurl}/tracking/{pref_city}) |"
        )

    # 月次レポート一覧
    lines += [
        "",
        "## 📅 月次レポート一覧",
        "",
        "> 各月のレポートをクリックすると詳細を確認できます。",
        "",
    ]

    for month in sorted(all_reports.keys(), reverse=True):
        lines.append(f"### {month}")
        lines.append("")
        lines.append("| 市区町村 | レポート |")
        lines.append("| --- | --- |")
        for pref_city in sorted(all_reports[month].keys()):
            parts = pref_city.split('_', 1)
            city = parts[1] if len(parts) >= 2 else pref_city
            lines.append(
                f"| {city} "
                f"| [レポート]({baseurl}/data/reports/{month}/{pref_city}_report) |"
            )
        lines.append("")

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"✅ tracking.md を生成しました: {index_path}")
    print(f"✅ 市区町村サブページ {len(all_cities)}件を生成しました")


def main():
    parser = argparse.ArgumentParser(description='物件追跡インデックスページを生成')
    parser.add_argument('--data-dir', default='data', help='データディレクトリ')
    parser.add_argument('--output-dir', default='.', help='出力ディレクトリ（tracking.mdの場所）')
    parser.add_argument('--baseurl', default='/sumstock', help='GitHub Pages baseurl')
    args = parser.parse_args()

    generate_tracking_index(
        Path(args.data_dir),
        Path(args.output_dir),
        args.baseurl,
    )


if __name__ == "__main__":
    main()
