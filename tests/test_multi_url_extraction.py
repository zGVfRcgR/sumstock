#!/usr/bin/env python3
"""
Test script for multi-URL extraction functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrape_sumstock import extract_urls_from_issue


def test_extract_no_urls():
    """Test extracting URLs when issue body has no URLs"""
    issue_body = "これは普通のテキストです。URLは含まれていません。"
    urls = extract_urls_from_issue(issue_body)
    assert urls == [], f"Expected empty list, got {urls}"
    print("✓ Test passed: No URLs in issue body")


def test_extract_single_url():
    """Test extracting a single URL from issue body"""
    issue_body = "対象URL: https://sumstock.jp/search/02/12/12207"
    urls = extract_urls_from_issue(issue_body)
    assert len(urls) == 1, f"Expected 1 URL, got {len(urls)}"
    assert urls[0] == "https://sumstock.jp/search/02/12/12207", f"Expected specific URL, got {urls[0]}"
    print("✓ Test passed: Single URL extraction")


def test_extract_multiple_urls():
    """Test extracting multiple URLs from issue body"""
    issue_body = """対象URL: https://sumstock.jp/search/02/12/12207
対象URL: https://sumstock.jp/search/02/12/12208
対象URL: https://sumstock.jp/search/03/13/13301"""
    
    urls = extract_urls_from_issue(issue_body)
    assert len(urls) == 3, f"Expected 3 URLs, got {len(urls)}"
    assert urls[0] == "https://sumstock.jp/search/02/12/12207"
    assert urls[1] == "https://sumstock.jp/search/02/12/12208"
    assert urls[2] == "https://sumstock.jp/search/03/13/13301"
    print("✓ Test passed: Multiple URLs extraction")


def test_extract_urls_with_mixed_content():
    """Test extracting URLs from issue body with mixed content"""
    issue_body = """# 物件データ取得リクエスト

## 対象地域

千葉県の物件を以下のURLから取得してください：

1. 松戸市: https://sumstock.jp/search/02/12/12207
2. 柏市: https://sumstock.jp/search/02/12/12208

その他のコメントや説明がここに入ります。

もう一つ追加: https://sumstock.jp/search/02/12/12209"""
    
    urls = extract_urls_from_issue(issue_body)
    assert len(urls) == 3, f"Expected 3 URLs, got {len(urls)}"
    assert "https://sumstock.jp/search/02/12/12207" in urls
    assert "https://sumstock.jp/search/02/12/12208" in urls
    assert "https://sumstock.jp/search/02/12/12209" in urls
    print("✓ Test passed: URLs extraction with mixed content")


def test_extract_duplicate_urls():
    """Test extracting URLs when duplicates exist"""
    issue_body = """対象URL: https://sumstock.jp/search/02/12/12207
対象URL: https://sumstock.jp/search/02/12/12207
対象URL: https://sumstock.jp/search/02/12/12208"""
    
    urls = extract_urls_from_issue(issue_body)
    # Note: duplicates are preserved in the current implementation
    assert len(urls) == 3, f"Expected 3 URLs (including duplicate), got {len(urls)}"
    print("✓ Test passed: Duplicate URLs are extracted (as-is)")


def test_extract_urls_on_same_line():
    """Test extracting multiple URLs on the same line"""
    issue_body = "複数URL: https://sumstock.jp/search/02/12/12207 と https://sumstock.jp/search/02/12/12208"
    
    urls = extract_urls_from_issue(issue_body)
    assert len(urls) == 2, f"Expected 2 URLs, got {len(urls)}"
    assert urls[0] == "https://sumstock.jp/search/02/12/12207"
    assert urls[1] == "https://sumstock.jp/search/02/12/12208"
    print("✓ Test passed: Multiple URLs on same line")


if __name__ == '__main__':
    print("Running multi-URL extraction tests...\n")
    
    test_extract_no_urls()
    test_extract_single_url()
    test_extract_multiple_urls()
    test_extract_urls_with_mixed_content()
    test_extract_duplicate_urls()
    test_extract_urls_on_same_line()
    
    print("\n✓ All multi-URL extraction tests passed!")
