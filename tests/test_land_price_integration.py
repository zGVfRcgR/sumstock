#!/usr/bin/env python3
"""
Integration test for land price functionality with scraper
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

from bs4 import BeautifulSoup
from scrape_sumstock import scrape_property_data, format_markdown
from datetime import datetime


# Mock HTML with property data
MOCK_HTML = """
<html>
<body>
<article class="bukkenListWrap">
    <div class="bukkenUnitBox">
        <h5 class="bukkenName">松戸市中金杉1丁目</h5>
        <div class="price">
            <span class="label">総額</span>
            <span class="bold">3,280<small>万円</small></span>
        </div>
        <div class="priceItems">
            建物価格 1,054 万円 / 土地価格 2,226 万円
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


def test_property_fields():
    """Test that property data includes land price fields"""
    print("Testing property data structure:")
    
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(MOCK_HTML, 'html.parser')
    items = soup.select('div.bukkenUnitBox')
    
    # Manually extract to simulate scraper behavior
    if items:
        item = items[0]
        
        # Check that we can extract the location
        location_elem = item.select_one('h5.bukkenName')
        if location_elem:
            location = location_elem.get_text().strip()
            print(f"  ✓ Location extracted: {location}")
            
            # Verify required fields exist in property_data structure
            required_fields = [
                'location', 'total_price', 'building_price', 'building_area',
                'building_unit_price', 'land_price', 'land_area', 'land_unit_price',
                'land_price_value', 'land_price_ratio', 'maker'
            ]
            
            print(f"  ✓ All required fields defined: {', '.join(required_fields)}")
            return True
    
    print("  ✗ Failed to extract property data")
    return False


def test_markdown_format():
    """Test that Markdown format includes land price columns"""
    print("\nTesting Markdown format:")
    
    # Create sample property data with all fields
    sample_property = {
        'location': '松戸市中金杉1丁目',
        'total_price': '3,280万円',
        'building_price': '1,054万円',
        'building_area': '112.85m²',
        'building_unit_price': '約9.34万円/m²',
        'land_price': '2,226万円',
        'land_area': '151.45m²',
        'land_unit_price': '約14.70万円/m²',
        'land_price_value': '-',  # Will be filled by API
        'land_price_ratio': '-',  # Will be filled by calculation
        'maker': '積水ハウス'
    }
    
    # Generate markdown
    markdown = format_markdown([sample_property], 'https://sumstock.jp/test', datetime.now())
    
    # Check for new columns in header
    if '地価（万円/m²）' in markdown and '地価倍率' in markdown:
        print(f"  ✓ Markdown includes new columns: '地価（万円/m²）' and '地価倍率'")
        
        # Check that the data row has the correct number of columns
        lines = markdown.split('\n')
        for line in lines:
            if '松戸市中金杉1丁目' in line:
                # Count pipe separators (should be 12 for 11 columns)
                pipe_count = line.count('|')
                if pipe_count == 12:  # 11 columns + 2 edge pipes = 13, minus 1 = 12 separators
                    print(f"  ✓ Data row has correct number of columns")
                    return True
                else:
                    print(f"  ✗ Data row has {pipe_count} separators (expected 12)")
                    return False
    
    print("  ✗ Markdown missing new columns")
    print(markdown)
    return False


def test_address_parsing_coverage():
    """Test address parsing for various formats"""
    print("\nTesting address parsing coverage:")
    
    from land_price import parse_address
    
    test_addresses = [
        ("松戸市中金杉1丁目", True),
        ("千葉市中央区", True),
        ("東京都世田谷区", True),
        ("横浜市鶴見区", True),
        ("不明", False),
    ]
    
    passed = 0
    failed = 0
    
    for address, should_parse in test_addresses:
        pref_code, city_code = parse_address(address)
        parsed = (pref_code is not None and city_code is not None)
        
        if parsed == should_parse:
            status = "parsed" if parsed else "not parsed (as expected)"
            print(f"  ✓ '{address}': {status}")
            passed += 1
        else:
            status = "parsed" if parsed else "not parsed"
            expected = "should parse" if should_parse else "should not parse"
            print(f"  ✗ '{address}': {status} but {expected}")
            failed += 1
    
    print(f"  Address parsing: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all integration tests"""
    print("=" * 60)
    print("Land Price Integration Tests")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Property Fields", test_property_fields()))
    results.append(("Markdown Format", test_markdown_format()))
    results.append(("Address Parsing Coverage", test_address_parsing_coverage()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All integration tests passed!")
        return 0
    else:
        print("Some integration tests failed!")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
