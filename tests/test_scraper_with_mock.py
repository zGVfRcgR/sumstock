#!/usr/bin/env python3
"""
Test script for the scraper with mock HTML data
"""

import sys
import os
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock HTML based on SumStock actual structure
MOCK_SUMSTOCK_HTML = """
<html>
<body>
<article class="bukkenListWrap">
    <div class="bukkenUnitBox">
        <h5 class="bukkenName">松戸市中金杉1丁目</h5>
        <div class="price">
            <span class="label">総額</span>
            <span class="bold">3,280<small>万円</small></span>
        </div>
        <div class="price">
            <span class="label">建物価格</span>
            <span class="bold">1,054<small>万円</small></span>
        </div>
        <div class="price">
            <span class="label">土地価格</span>
            <span class="bold">2,226<small>万円</small></span>
        </div>
        <div class="area">
            <span class="label">建物面積</span>
            <span class="value">112.85</span>
        </div>
        <div class="area">
            <span class="label">土地面積</span>
            <span class="value">151.45</span>
        </div>
        <div class="maker">積水ハウス</div>
    </div>
    <div class="bukkenUnitBox">
        <h5 class="bukkenName">松戸市小金原2丁目</h5>
        <div class="price">
            <span class="label">総額</span>
            <span class="bold">2,980<small>万円</small></span>
        </div>
        <div class="price">
            <span class="label">建物価格</span>
            <span class="bold">980<small>万円</small></span>
        </div>
        <div class="price">
            <span class="label">土地価格</span>
            <span class="bold">2,000<small>万円</small></span>
        </div>
        <div class="area">
            <span class="label">建物面積</span>
            <span class="value">105.32</span>
        </div>
        <div class="area">
            <span class="label">土地面積</span>
            <span class="value">140.50</span>
        </div>
        <div class="maker">ダイワハウス</div>
    </div>
</article>
</body>
</html>
"""

def test_selector_detection():
    """Test that selectors can find bukkenUnitBox elements"""
    soup = BeautifulSoup(MOCK_SUMSTOCK_HTML, 'html.parser')
    
    # Test SumStock-specific selectors
    selectors_to_test = [
        'div.bukkenUnitBox',
        'article.bukkenListWrap .bukkenUnitBox',
        '.bukkenUnitBox',
    ]
    
    print("Testing SumStock-specific selectors:")
    for selector in selectors_to_test:
        items = soup.select(selector)
        print(f"  Selector '{selector}': Found {len(items)} items")
        assert len(items) == 2, f"Expected 2 items, got {len(items)} for selector '{selector}'"
    
    # Test location extraction
    print("\nTesting location extraction:")
    items = soup.select('div.bukkenUnitBox')
    for i, item in enumerate(items, 1):
        # Test h5.bukkenName selector
        location_elem = item.select_one('h5.bukkenName')
        if location_elem:
            location = location_elem.get_text().strip()
            print(f"  Property {i} location: {location}")
            assert location in ['松戸市中金杉1丁目', '松戸市小金原2丁目']
    
    # Test price extraction with .bold class
    print("\nTesting price extraction with .bold class:")
    items = soup.select('div.bukkenUnitBox')
    for i, item in enumerate(items, 1):
        price_elems = item.select('span.bold')
        prices = []
        for elem in price_elems:
            # Extract number from bold span
            text = elem.get_text()
            # Remove 万円 and small tags
            text = text.replace('万円', '').strip()
            prices.append(text)
        print(f"  Property {i} prices: {prices}")
        assert len(prices) >= 3, f"Expected at least 3 prices, got {len(prices)}"
    
    print("\n✓ All tests passed!")

if __name__ == '__main__':
    test_selector_detection()
