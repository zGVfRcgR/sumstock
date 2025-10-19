#!/usr/bin/env python3
"""
Integration test for the scraper with mock HTML data
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after adding to path
from scripts.scrape_sumstock import scrape_property_data

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

def test_scrape_with_mock_html():
    """Test scraping with mock HTML"""
    print("Testing scraper with mock SumStock HTML...")
    
    # Mock the requests.get call
    mock_response = MagicMock()
    mock_response.content = MOCK_SUMSTOCK_HTML.encode('utf-8')
    mock_response.raise_for_status = MagicMock()
    
    with patch('requests.get', return_value=mock_response):
        properties = scrape_property_data('https://sumstock.jp/search/02/12/12207')
    
    # Verify we got properties
    assert len(properties) > 0, f"Expected properties to be found, got {len(properties)}"
    print(f"✓ Found {len(properties)} properties")
    
    # Verify first property
    if len(properties) >= 1:
        prop1 = properties[0]
        print(f"\nProperty 1:")
        print(f"  Location: {prop1['location']}")
        print(f"  Total Price: {prop1['total_price']}")
        print(f"  Building Price: {prop1['building_price']}")
        print(f"  Building Area: {prop1['building_area']}")
        print(f"  Land Price: {prop1['land_price']}")
        print(f"  Land Area: {prop1['land_area']}")
        print(f"  Maker: {prop1['maker']}")
        
        # Verify expected values
        assert '松戸市中金杉1丁目' in prop1['location'], f"Expected location to contain '松戸市中金杉1丁目', got '{prop1['location']}'"
        assert '3,280万円' in prop1['total_price'], f"Expected total price '3,280万円', got '{prop1['total_price']}'"
        assert '1,054万円' in prop1['building_price'], f"Expected building price '1,054万円', got '{prop1['building_price']}'"
        assert '積水ハウス' in prop1['maker'], f"Expected maker '積水ハウス', got '{prop1['maker']}'"
        
        print("✓ Property 1 data is correct")
    
    # Verify second property
    if len(properties) >= 2:
        prop2 = properties[1]
        print(f"\nProperty 2:")
        print(f"  Location: {prop2['location']}")
        print(f"  Total Price: {prop2['total_price']}")
        print(f"  Building Price: {prop2['building_price']}")
        print(f"  Maker: {prop2['maker']}")
        
        # Verify expected values
        assert '松戸市小金原2丁目' in prop2['location'], f"Expected location to contain '松戸市小金原2丁目', got '{prop2['location']}'"
        assert '2,980万円' in prop2['total_price'], f"Expected total price '2,980万円', got '{prop2['total_price']}'"
        assert 'ダイワハウス' in prop2['maker'], f"Expected maker 'ダイワハウス', got '{prop2['maker']}'"
        
        print("✓ Property 2 data is correct")
    
    print("\n✓ All integration tests passed!")
    return properties

if __name__ == '__main__':
    test_scrape_with_mock_html()
