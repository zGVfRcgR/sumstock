#!/usr/bin/env python3
"""
最新データ取得 + 追跡レポート更新 + ブログ議事録生成を一括実行するスクリプト。

処理概要:
1. SumStockから最新物件データを取得して data/<都道府県>/<市区町村>/<日付>.md を更新
2. 対象市区町村の追跡レポート (data/reports/*, data/tracking/*) を更新
3. ペルソナ対話形式のブログ議事録を blog/YYYY-MM-DD.md に追加
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from scrape_sumstock import (
    extract_urls_from_issue,
    format_markdown,
    get_location_from_url,
    parse_area,
    parse_price,
    read_urls_from_config,
    save_markdown_file,
    scrape_property_data,
)
from track_properties import process_city
from generate_tracking_index import generate_tracking_index


@dataclass
class CitySummary:
    prefecture: str
    city: str
    url: str
    file_path: Path
    property_count: int
    avg_total_price: float | None
    median_total_price: float | None
    avg_building_area: float | None
    avg_land_area: float | None
    top_maker: str
    max_total_price: float | None
    min_total_price: float | None


def resolve_target_urls(cli_urls: List[str]) -> List[str]:
    """処理対象URLを優先順位付きで解決する。"""
    if cli_urls:
        print(f"Using {len(cli_urls)} URL(s) from command-line arguments")
        return cli_urls

    config_urls = read_urls_from_config()
    if config_urls:
        print(f"Using {len(config_urls)} URL(s) from config file")
        return config_urls

    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_urls = extract_urls_from_issue(issue_body)
    if issue_urls:
        print(f"Using {len(issue_urls)} URL(s) from ISSUE_BODY")
        return issue_urls

    return []


def _avg(values: List[float]) -> float | None:
    return (sum(values) / len(values)) if values else None


def _median(values: List[float]) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    n = len(sorted_values)
    mid = n // 2
    if n % 2 == 1:
        return sorted_values[mid]
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2


def summarize_city(
    prefecture: str,
    city: str,
    url: str,
    file_path: Path,
    properties: List[Dict],
) -> CitySummary:
    """市区町村ごとの要約統計を作成する。"""
    total_prices: List[float] = []
    building_areas: List[float] = []
    land_areas: List[float] = []
    maker_counter: Counter[str] = Counter()

    for prop in properties:
        total_price = parse_price(prop.get("total_price", ""))
        if total_price is not None:
            total_prices.append(total_price)

        building_area = parse_area(prop.get("building_area", ""))
        if building_area is not None:
            building_areas.append(building_area)

        land_area = parse_area(prop.get("land_area", ""))
        if land_area is not None:
            land_areas.append(land_area)

        maker = (prop.get("maker") or "").strip()
        if maker and maker != "-":
            maker_counter[maker] += 1

    top_maker = maker_counter.most_common(1)[0][0] if maker_counter else "不明"
    return CitySummary(
        prefecture=prefecture,
        city=city,
        url=url,
        file_path=file_path,
        property_count=len(properties),
        avg_total_price=_avg(total_prices),
        median_total_price=_median(total_prices),
        avg_building_area=_avg(building_areas),
        avg_land_area=_avg(land_areas),
        top_maker=top_maker,
        max_total_price=max(total_prices) if total_prices else None,
        min_total_price=min(total_prices) if total_prices else None,
    )


def ensure_blog_index(blog_dir: Path):
    """ブログのトップページを作成する。"""
    blog_dir.mkdir(parents=True, exist_ok=True)
    index_path = blog_dir / "index.md"
    if index_path.exists():
        return

    content = """---
layout: default
title: ブログ議事録
nav_order: 3
has_children: true
---

# ブログ議事録

最新の物件取得結果を、各ペルソナの視点で議事録として記録します。
"""
    index_path.write_text(content, encoding="utf-8")


def _fmt_money(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:,.0f}万円"


def _fmt_area(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}m²"


def render_minutes(date: datetime, summaries: List[CitySummary]) -> str:
    """ペルソナ対話形式のブログ議事録を生成する。"""
    total_properties = sum(s.property_count for s in summaries)
    priced_avgs = [s.avg_total_price for s in summaries if s.avg_total_price is not None]
    portfolio_avg = _avg(priced_avgs)

    hottest_city = max(summaries, key=lambda s: s.property_count, default=None)
    richest_city = max(
        summaries,
        key=lambda s: s.max_total_price if s.max_total_price is not None else -1,
        default=None,
    )

    lines: List[str] = [
        "---",
        "layout: default",
        f"title: {date.strftime('%Y-%m-%d')} 定例議事",
        "parent: ブログ議事録",
        "---",
        "",
        f"# 物件データ定例議事録 ({date.strftime('%Y-%m-%d')})",
        "",
        f"- 取得日時: {date.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 対象市区町村数: {len(summaries)}",
        f"- 取得物件総数: {total_properties}件",
        f"- 全体平均価格(市区町村平均): {_fmt_money(portfolio_avg)}",
        "",
        "## 取得サマリー",
        "",
        "| 都道府県 | 市区町村 | 件数 | 平均価格 | 中央価格 | 建物面積平均 | 土地面積平均 | 主なハウスメーカー | データ |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]

    for s in sorted(summaries, key=lambda x: (x.prefecture, x.city)):
        lines.append(
            "| "
            f"{s.prefecture} | {s.city} | {s.property_count} | {_fmt_money(s.avg_total_price)} | "
            f"{_fmt_money(s.median_total_price)} | {_fmt_area(s.avg_building_area)} | {_fmt_area(s.avg_land_area)} | "
            f"{s.top_maker} | [データ](/sumstock/{s.file_path.as_posix()}) |"
        )

    lines += [
        "",
        "## Step1: 専門家たちの協議",
        "",
        "### 会話ログ",
        "",
        "@analyst: "
        + (
            f"今回の取得は{len(summaries)}市区町村・{total_properties}件です。"
            f"件数最多は{hottest_city.prefecture}{hottest_city.city}で{hottest_city.property_count}件、"
            f"市区町村平均価格の全体平均は{_fmt_money(portfolio_avg)}でした。"
            if hottest_city
            else "今回の取得結果から有効な統計は算出できませんでした。"
        ),
        "",
        "@investor: "
        + (
            f"最高価格帯は{richest_city.prefecture}{richest_city.city}の{_fmt_money(richest_city.max_total_price)}です。"
            "価格レンジの広い市は、利回りだけでなく出口時の流動性も同時に見たいですね。"
            if richest_city
            else "投資判断に必要な価格データが不足しています。"
        ),
        "",
        "@mansion: 立地の比較軸を揃えるため、駅距離・再開発有無・管理状態の3点を最低限合わせて評価しましょう。",
        "",
        "@housemaker: 面積バランスとメーカー傾向から、同価格帯でも住み心地の差は大きいです。家事動線と断熱性能を優先して見たいです。",
        "",
        "@planner: 誘導区域の内外で将来の生活利便性に差が出る可能性があります。取得時点から都市計画の整合性を確認しましょう。",
        "",
        "@legal: 契約段階では境界確定、私道負担、契約不適合責任の範囲を先に明確化してください。",
        "",
        "## Step2: @denier による全否定",
        "",
        "@denier: いいえ、その見方は楽観的すぎます。"
        "掲載データはあくまで募集条件で、成約条件ではありません。"
        "金利上昇、空室期間、修繕費増、エリア流動性低下が同時に来たら、前提はすぐ崩れます。"
        "平均値で安心した瞬間に負けます。",
        "",
        "## Step3: 各専門家の最終コメント",
        "",
        "- @analyst: 次回は前月比を同一指標で固定し、変化率を時系列で検証します。",
        "- @investor: 価格帯別に出口戦略を分け、CF悪化シナリオを先に潰します。",
        "- @mansion: 物件個別情報だけでなく、管理体制と立地優位性を必ず重ねて判断します。",
        "- @housemaker: 面積数値に加えて、暮らしやすさを左右する動線と性能を確認します。",
        "- @planner: 持続可能なエリアかどうかを都市計画の視点で継続確認します。",
        "- @legal: 最終契約前に法務・税務の専門家確認を必ず実施してください。",
        "- @denier: そもそも前提が脆い案件は、見送る勇気が最適解です。",
    ]

    return "\n".join(lines) + "\n"


def run_tracking_for_updated_cities(data_dir: Path, summaries: List[CitySummary]):
    """更新対象市区町村のみ追跡レポートを更新する。"""
    touched = sorted({(s.prefecture, s.city) for s in summaries})
    for pref, city in touched:
        city_dir = data_dir / pref / city
        if city_dir.exists():
            process_city(data_dir, pref, city, city_dir)


def main():
    parser = argparse.ArgumentParser(
        description="最新物件取得 + 追跡更新 + ペルソナ議事ブログ生成"
    )
    parser.add_argument("urls", nargs="*", help="対象のSumStock URL (省略時は設定/Issueから解決)")
    parser.add_argument("--data-dir", default="data", help="データディレクトリ")
    parser.add_argument("--blog-dir", default="blog", help="ブログ議事録ディレクトリ")
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="スクレイピングをスキップし、最新ファイルから議事のみ再生成",
    )
    args = parser.parse_args()

    current_date = datetime.now()
    data_dir = Path(args.data_dir)
    blog_dir = Path(args.blog_dir)
    ensure_blog_index(blog_dir)

    summaries: List[CitySummary] = []

    if args.skip_scrape:
        print("Skipping scrape. Building minutes from latest report files is not supported in this mode.")
        print("Please run without --skip-scrape to collect fresh summaries.")
        return 0

    urls = resolve_target_urls(args.urls)
    if not urls:
        print(
            "Error: No SumStock URL found. Provide URL argument or config/scrape_urls.txt or ISSUE_BODY.",
            file=sys.stderr,
        )
        return 1

    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}] Scraping: {url}")
        properties = scrape_property_data(url)

        pref_name, city_name = get_location_from_url(url)
        markdown = format_markdown(properties, url, current_date, pref_name, city_name)
        file_path = Path(save_markdown_file(markdown, current_date, pref_name, city_name, output_dir=str(data_dir)))

        summaries.append(
            summarize_city(pref_name, city_name, url, file_path, properties)
        )

        print(f"  -> {pref_name} {city_name}: {len(properties)}件")

    run_tracking_for_updated_cities(data_dir, summaries)
    generate_tracking_index(data_dir, Path('.'))

    minutes = render_minutes(current_date, summaries)
    minutes_path = blog_dir / f"{current_date.strftime('%Y-%m-%d')}.md"
    minutes_path.write_text(minutes, encoding="utf-8")
    print(f"✅ 議事録を生成しました: {minutes_path}")

    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"minutes_path={minutes_path.as_posix()}\n")
            f.write(f"cities={len(summaries)}\n")
            f.write(f"properties={sum(s.property_count for s in summaries)}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
