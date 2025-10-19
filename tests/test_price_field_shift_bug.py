#!/usr/bin/env python3
"""
Test to demonstrate the price field shift bug.
This test shows what happens when prices appear in the DOM without proper label association.
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after adding to path
from scripts.scrape_sumstock import scrape_property_data

# Mock HTML where prices appear in a different order or without clear labels
# This simulates the bug scenario where the DOM structure doesn't match expectations
BUGGY_HTML_SCENARIO = """
<html>
<body>
<article class="bukkenListWrap">
    <div class="bukkenUnitBox">
        <h5 class="bukkenName">松戸市中金杉1丁目</h5>
        <!-- In this scenario, only building and land prices are present as bold elements -->
        <!-- The total price might be calculated or displayed differently -->
        <div class="price">
            <span class="bold">1,054<small>万円</small></span>
        </div>
        <div class="price">
            <span class="bold">2,226<small>万円</small></span>
        </div>
        <div class="area">
            <span class="value">112.85</span>
        </div>
        <div class="area">
            <span class="value">151.45</span>
        </div>
        <div class="maker">積水ハウス</div>
    </div>
</article>
</body>
</html>
"""

def test_price_field_shift_bug():
    """Test that demonstrates the price field shift bug"""
    print("Testing price field shift bug scenario...")
    print("Expected: building=1,054, land=2,226")
    print("Bug: total=1,054 (should be building), building=2,226 (should be land), land=- (empty)")
    
    # Mock the requests.get call
    mock_response = MagicMock()
    mock_response.content = BUGGY_HTML_SCENARIO.encode('utf-8')
    mock_response.raise_for_status = MagicMock()
    
    with patch('requests.get', return_value=mock_response):
        properties = scrape_property_data('https://sumstock.jp/search/02/12/12207')
    
    if len(properties) >= 1:
        prop = properties[0]
        print(f"\nActual extracted values:")
        print(f"  Total Price: {prop['total_price']}")
        print(f"  Building Price: {prop['building_price']}")
        print(f"  Land Price: {prop['land_price']}")
        
        # This demonstrates the bug - prices are shifted
        if prop['total_price'] == '1,054万円' and prop['building_price'] == '2,226万円' and prop['land_price'] == '-':
            print("\n✗ BUG CONFIRMED: Prices are shifted!")
            print("  - Total contains building price (1,054)")
            print("  - Building contains land price (2,226)")
            print("  - Land is empty")
            return True
        else:
            print("\n✓ No bug detected or bug already fixed")
            return False
    else:
        print("No properties found")
        return False

if __name__ == '__main__':
    bug_exists = test_price_field_shift_bug()
    sys.exit(0 if bug_exists else 1)
