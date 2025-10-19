#!/usr/bin/env python3
"""
Test to verify price extraction works correctly with labels.
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after adding to path
from scripts.scrape_sumstock import scrape_property_data

# Test case 1: Properly labeled HTML (should extract correctly)
LABELED_HTML = """
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
</article>
</body>
</html>
"""

# Test case 2: Labeled HTML but prices in different DOM order (building comes before total)
REORDERED_LABELED_HTML = """
<html>
<body>
<article class="bukkenListWrap">
    <div class="bukkenUnitBox">
        <h5 class="bukkenName">松戸市小金原2丁目</h5>
        <div class="price">
            <span class="label">建物価格</span>
            <span class="bold">980<small>万円</small></span>
        </div>
        <div class="price">
            <span class="label">土地価格</span>
            <span class="bold">2,000<small>万円</small></span>
        </div>
        <div class="price">
            <span class="label">総額</span>
            <span class="bold">2,980<small>万円</small></span>
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

# Test case 3: HTML with only some labels (mixed scenario)
PARTIAL_LABELED_HTML = """
<html>
<body>
<article class="bukkenListWrap">
    <div class="bukkenUnitBox">
        <h5 class="bukkenName">松戸市六実3丁目</h5>
        <div class="price">
            <span class="label">建物価格</span>
            <span class="bold">1,200<small>万円</small></span>
        </div>
        <div class="price">
            <span class="label">土地価格</span>
            <span class="bold">1,800<small>万円</small></span>
        </div>
        <div class="area">
            <span class="label">建物面積</span>
            <span class="value">95.00</span>
        </div>
        <div class="area">
            <span class="label">土地面積</span>
            <span class="value">120.00</span>
        </div>
        <div class="maker">セキスイハイム</div>
    </div>
</article>
</body>
</html>
"""

def test_labeled_prices():
    """Test that properly labeled prices are extracted correctly"""
    print("=" * 80)
    print("TEST 1: Properly labeled HTML (standard order)")
    print("=" * 80)
    print("Expected: total=3,280, building=1,054, land=2,226")
    
    mock_response = MagicMock()
    mock_response.content = LABELED_HTML.encode('utf-8')
    mock_response.raise_for_status = MagicMock()
    
    with patch('requests.get', return_value=mock_response):
        properties = scrape_property_data('https://sumstock.jp/test')
    
    if len(properties) >= 1:
        prop = properties[0]
        print(f"\nActual extracted values:")
        print(f"  Total Price: {prop['total_price']}")
        print(f"  Building Price: {prop['building_price']}")
        print(f"  Land Price: {prop['land_price']}")
        print(f"  Building Area: {prop['building_area']}")
        print(f"  Land Area: {prop['land_area']}")
        
        assert prop['total_price'] == '3,280万円', f"Expected total '3,280万円', got '{prop['total_price']}'"
        assert prop['building_price'] == '1,054万円', f"Expected building '1,054万円', got '{prop['building_price']}'"
        assert prop['land_price'] == '2,226万円', f"Expected land '2,226万円', got '{prop['land_price']}'"
        assert prop['building_area'] == '112.85m²', f"Expected building area '112.85m²', got '{prop['building_area']}'"
        assert prop['land_area'] == '151.45m²', f"Expected land area '151.45m²', got '{prop['land_area']}'"
        
        print("\n✓ TEST 1 PASSED: Labeled prices extracted correctly!")
        return True
    else:
        print("\n✗ TEST 1 FAILED: No properties found")
        return False

def test_reordered_labeled_prices():
    """Test that labeled prices in different DOM order are still extracted correctly"""
    print("\n" + "=" * 80)
    print("TEST 2: Labeled HTML with reordered prices (building before total)")
    print("=" * 80)
    print("Expected: total=2,980, building=980, land=2,000 (despite DOM order)")
    
    mock_response = MagicMock()
    mock_response.content = REORDERED_LABELED_HTML.encode('utf-8')
    mock_response.raise_for_status = MagicMock()
    
    with patch('requests.get', return_value=mock_response):
        properties = scrape_property_data('https://sumstock.jp/test')
    
    if len(properties) >= 1:
        prop = properties[0]
        print(f"\nActual extracted values:")
        print(f"  Total Price: {prop['total_price']}")
        print(f"  Building Price: {prop['building_price']}")
        print(f"  Land Price: {prop['land_price']}")
        
        # The key test: even though building appears first in DOM, it should still be mapped correctly
        assert prop['total_price'] == '2,980万円', f"Expected total '2,980万円', got '{prop['total_price']}'"
        assert prop['building_price'] == '980万円', f"Expected building '980万円', got '{prop['building_price']}'"
        assert prop['land_price'] == '2,000万円', f"Expected land '2,000万円', got '{prop['land_price']}'"
        
        print("\n✓ TEST 2 PASSED: Reordered labeled prices extracted correctly!")
        return True
    else:
        print("\n✗ TEST 2 FAILED: No properties found")
        return False

def test_partial_labeled_prices():
    """Test HTML with only building and land labels (no total)"""
    print("\n" + "=" * 80)
    print("TEST 3: Partial labeled HTML (no total price label)")
    print("=" * 80)
    print("Expected: total=-, building=1,200, land=1,800")
    
    mock_response = MagicMock()
    mock_response.content = PARTIAL_LABELED_HTML.encode('utf-8')
    mock_response.raise_for_status = MagicMock()
    
    with patch('requests.get', return_value=mock_response):
        properties = scrape_property_data('https://sumstock.jp/test')
    
    if len(properties) >= 1:
        prop = properties[0]
        print(f"\nActual extracted values:")
        print(f"  Total Price: {prop['total_price']}")
        print(f"  Building Price: {prop['building_price']}")
        print(f"  Land Price: {prop['land_price']}")
        
        # When total is not labeled, it should remain as default '-'
        assert prop['building_price'] == '1,200万円', f"Expected building '1,200万円', got '{prop['building_price']}'"
        assert prop['land_price'] == '1,800万円', f"Expected land '1,800万円', got '{prop['land_price']}'"
        
        print("\n✓ TEST 3 PASSED: Partial labeled prices extracted correctly!")
        return True
    else:
        print("\n✗ TEST 3 FAILED: No properties found")
        return False

if __name__ == '__main__':
    all_passed = True
    
    try:
        if not test_labeled_prices():
            all_passed = False
    except AssertionError as e:
        print(f"\n✗ TEST 1 FAILED: {e}")
        all_passed = False
    
    try:
        if not test_reordered_labeled_prices():
            all_passed = False
    except AssertionError as e:
        print(f"\n✗ TEST 2 FAILED: {e}")
        all_passed = False
    
    try:
        if not test_partial_labeled_prices():
            all_passed = False
    except AssertionError as e:
        print(f"\n✗ TEST 3 FAILED: {e}")
        all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)

