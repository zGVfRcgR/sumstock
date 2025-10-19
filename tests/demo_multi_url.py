#!/usr/bin/env python3
"""
Demo script showing multi-URL functionality
This demonstrates how to use the scraper with multiple URLs
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrape_sumstock import extract_urls_from_issue

def demo_single_url():
    """Demo 1: Single URL via CLI (backward compatible)"""
    print("=" * 70)
    print("Demo 1: Single URL via CLI")
    print("=" * 70)
    print("\nCommand:")
    print('  python scripts/scrape_sumstock.py "https://sumstock.jp/search/02/12/12207"')
    print("\nExpected output:")
    print("  - Single file: data/YYYY-MM-DD.md (no suffix)")
    print("  - File contains data from URL: https://sumstock.jp/search/02/12/12207")
    print()


def demo_multiple_urls_cli():
    """Demo 2: Multiple URLs via CLI"""
    print("=" * 70)
    print("Demo 2: Multiple URLs via CLI")
    print("=" * 70)
    print("\nCommand:")
    print('  python scripts/scrape_sumstock.py \\')
    print('    "https://sumstock.jp/search/02/12/12207" \\')
    print('    "https://sumstock.jp/search/02/12/12208" \\')
    print('    "https://sumstock.jp/search/02/12/12209"')
    print("\nExpected output:")
    print("  - Three files:")
    print("    * data/YYYY-MM-DD_1.md (from URL ...12207)")
    print("    * data/YYYY-MM-DD_2.md (from URL ...12208)")
    print("    * data/YYYY-MM-DD_3.md (from URL ...12209)")
    print()


def demo_issue_body_single():
    """Demo 3: Single URL via ISSUE_BODY (backward compatible)"""
    print("=" * 70)
    print("Demo 3: Single URL via ISSUE_BODY (backward compatible)")
    print("=" * 70)
    print("\nCommand:")
    print('  export ISSUE_BODY="対象URL: https://sumstock.jp/search/02/12/12207"')
    print('  python scripts/scrape_sumstock.py')
    print("\nExpected output:")
    print("  - Single file: data/YYYY-MM-DD.md (no suffix)")
    print("  - File contains data from URL: https://sumstock.jp/search/02/12/12207")
    print()


def demo_issue_body_multiple():
    """Demo 4: Multiple URLs via ISSUE_BODY"""
    print("=" * 70)
    print("Demo 4: Multiple URLs via ISSUE_BODY")
    print("=" * 70)
    print('\nIssue body example:')
    print("""
# 物件データ取得リクエスト

## 対象地域

千葉県の物件を以下のURLから取得してください：

1. 松戸市: https://sumstock.jp/search/02/12/12207
2. 柏市: https://sumstock.jp/search/02/12/12208
3. 市川市: https://sumstock.jp/search/02/12/12209
""")
    print("\nCommand:")
    print('  export ISSUE_BODY="<issue body from above>"')
    print('  python scripts/scrape_sumstock.py')
    print("\nExpected output:")
    print("  - Three files:")
    print("    * data/YYYY-MM-DD_1.md (from URL ...12207)")
    print("    * data/YYYY-MM-DD_2.md (from URL ...12208)")
    print("    * data/YYYY-MM-DD_3.md (from URL ...12209)")
    print()


def demo_github_actions():
    """Demo 5: GitHub Actions integration"""
    print("=" * 70)
    print("Demo 5: GitHub Actions Integration")
    print("=" * 70)
    print("\nWhen triggered from GitHub Actions:")
    print("  - Issue body is automatically extracted")
    print("  - All URLs found in the issue are processed")
    print("  - GITHUB_OUTPUT receives comma-separated file paths")
    print("\nExample GITHUB_OUTPUT:")
    print("  filepath=data/2025-10-19_1.md,data/2025-10-19_2.md,data/2025-10-19_3.md")
    print("  date=2025-10-19")
    print("  count=3")
    print()


def show_url_extraction_examples():
    """Show examples of URL extraction"""
    print("=" * 70)
    print("URL Extraction Examples")
    print("=" * 70)
    
    # Example 1: Simple list
    example1 = """対象URL: https://sumstock.jp/search/02/12/12207
対象URL: https://sumstock.jp/search/02/12/12208"""
    
    urls1 = extract_urls_from_issue(example1)
    print(f"\nExample 1 - Simple list:")
    print(f"  Input: {repr(example1)}")
    print(f"  Extracted URLs: {len(urls1)} URLs")
    for i, url in enumerate(urls1, 1):
        print(f"    {i}. {url}")
    
    # Example 2: Markdown with mixed content
    example2 = """# 物件データ取得

千葉県:
- https://sumstock.jp/search/02/12/12207
- https://sumstock.jp/search/02/12/12208

東京都:
- https://sumstock.jp/search/13/01/13101"""
    
    urls2 = extract_urls_from_issue(example2)
    print(f"\nExample 2 - Markdown with mixed content:")
    print(f"  Extracted URLs: {len(urls2)} URLs")
    for i, url in enumerate(urls2, 1):
        print(f"    {i}. {url}")
    
    # Example 3: No URLs
    example3 = "これは普通のテキストです。URLは含まれていません。"
    urls3 = extract_urls_from_issue(example3)
    print(f"\nExample 3 - No URLs:")
    print(f"  Input: {repr(example3)}")
    print(f"  Extracted URLs: {len(urls3)} URLs")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("MULTI-URL SCRAPER FUNCTIONALITY DEMO")
    print("=" * 70)
    print()
    
    demo_single_url()
    demo_multiple_urls_cli()
    demo_issue_body_single()
    demo_issue_body_multiple()
    demo_github_actions()
    show_url_extraction_examples()
    
    print("=" * 70)
    print("For more information, see the tests in:")
    print("  - tests/test_multi_url_extraction.py")
    print("  - tests/test_multi_url_e2e.py")
    print("=" * 70)
