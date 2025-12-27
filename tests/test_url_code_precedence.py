#!/usr/bin/env python3
"""
Test to verify that URL code always determines folder location
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from scrape_sumstock import get_location_from_url, parse_location_from_address


def test_url_determines_folder():
    """Test that URL code always determines the folder location"""
    
    # Test case 1: URL code 12217 should always return 市原市
    pref, city = get_location_from_url('https://sumstock.jp/search/02/12/12217')
    assert pref == '千葉県', f"Expected '千葉県', got '{pref}'"
    assert city == '市原市', f"Expected '市原市', got '{city}'"
    print("✓ URL code 12217 correctly returns 千葉県/市原市")
    
    # Test case 2: URL code 12215 should always return 柏市
    pref, city = get_location_from_url('https://sumstock.jp/search/02/12/12215')
    assert pref == '千葉県', f"Expected '千葉県', got '{pref}'"
    assert city == '柏市', f"Expected '柏市', got '{city}'"
    print("✓ URL code 12215 correctly returns 千葉県/柏市")
    
    # Test case 3: URL code 12220 should always return 流山市
    pref, city = get_location_from_url('https://sumstock.jp/search/02/12/12220')
    assert pref == '千葉県', f"Expected '千葉県', got '{pref}'"
    assert city == '流山市', f"Expected '流山市', got '{city}'"
    print("✓ URL code 12220 correctly returns 千葉県/流山市")
    
    # Test case 4: Even if address says 柏市, URL code 12217 should return 市原市
    # This is the key behavior: URL code takes precedence
    address_pref, address_city = parse_location_from_address('柏市名戸ケ谷１丁目', '')
    assert address_city == '柏市', f"Address parsing returned '{address_city}', expected '柏市'"
    
    # But URL code 12217 should still return 市原市 (not 柏市 from address)
    url_pref, url_city = get_location_from_url('https://sumstock.jp/search/02/12/12217')
    assert url_city == '市原市', f"URL code 12217 should return '市原市', got '{url_city}'"
    assert url_city != address_city, "URL code should determine folder, not address"
    print("✓ URL code takes precedence over address parsing")
    
    print("\nAll tests passed! URL code always determines folder location.")


if __name__ == '__main__':
    test_url_determines_folder()
