#!/usr/bin/env python3
"""
Test script for land_price module
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

from land_price import parse_address, calculate_ratio, get_land_price_info


def test_parse_address():
    """Test address parsing functionality"""
    print("Testing parse_address():")
    
    # Test cases with expected results
    test_cases = [
        ("松戸市中金杉1丁目", ("12", "207")),
        ("千葉市中央区本町", ("12", "101")),
        ("東京都千代田区丸の内", ("13", "101")),
        ("世田谷区三軒茶屋", ("13", "112")),
        ("横浜市鶴見区", ("14", "101")),
        ("さいたま市大宮区", ("11", "103")),
        ("柏市柏", ("12", "215")),
        ("不明な住所", (None, None)),
        ("", (None, None)),
    ]
    
    passed = 0
    failed = 0
    
    for address, expected in test_cases:
        result = parse_address(address)
        if result == expected:
            print(f"  ✓ '{address}' -> {result}")
            passed += 1
        else:
            print(f"  ✗ '{address}' -> {result} (expected {expected})")
            failed += 1
    
    print(f"  Parse address tests: {passed} passed, {failed} failed\n")
    return failed == 0


def test_calculate_ratio():
    """Test ratio calculation functionality"""
    print("Testing calculate_ratio():")
    
    test_cases = [
        (50.0, 25.0, "2.00x"),
        (30.5, 25.0, "1.22x"),
        (100.0, 50.0, "2.00x"),
        (25.0, 25.0, "1.00x"),
        (None, 25.0, None),
        (50.0, None, None),
        (50.0, 0, None),
        (0, 25.0, "0.00x"),
    ]
    
    passed = 0
    failed = 0
    
    for unit_price, land_price, expected in test_cases:
        result = calculate_ratio(unit_price, land_price)
        if result == expected:
            print(f"  ✓ calculate_ratio({unit_price}, {land_price}) -> {result}")
            passed += 1
        else:
            print(f"  ✗ calculate_ratio({unit_price}, {land_price}) -> {result} (expected {expected})")
            failed += 1
    
    print(f"  Ratio calculation tests: {passed} passed, {failed} failed\n")
    return failed == 0


def test_get_land_price_info_without_api():
    """Test get_land_price_info without API key (should return None gracefully)"""
    print("Testing get_land_price_info() without API key:")
    
    # Ensure API key is not set
    old_key = os.environ.get('REINFOLIB_API_KEY')
    if 'REINFOLIB_API_KEY' in os.environ:
        del os.environ['REINFOLIB_API_KEY']
    
    try:
        # Test with valid address
        result = get_land_price_info("松戸市中金杉1丁目")
        if result == (None, None):
            print(f"  ✓ Returns (None, None) when API key is not available")
            return True
        else:
            print(f"  ✗ Expected (None, None), got {result}")
            return False
    finally:
        # Restore API key if it was set
        if old_key is not None:
            os.environ['REINFOLIB_API_KEY'] = old_key


def test_integration():
    """Test integration of all functions"""
    print("Testing integration:")
    
    # Test the flow: address -> codes -> price (simulated) -> ratio
    address = "松戸市中金杉1丁目"
    pref_code, city_code = parse_address(address)
    
    if pref_code == "12" and city_code == "207":
        print(f"  ✓ Address '{address}' parsed correctly")
        
        # Simulate land price and calculate ratio
        simulated_land_price = 25.5
        unit_price = 14.7  # Example unit price
        ratio = calculate_ratio(unit_price, simulated_land_price)
        
        if ratio == "0.58x":
            print(f"  ✓ Ratio calculated correctly: {ratio}")
            return True
        else:
            print(f"  ✗ Expected ratio '0.58x', got '{ratio}'")
            return False
    else:
        print(f"  ✗ Address parsing failed: got ({pref_code}, {city_code})")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Land Price Module Tests")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Address Parsing", test_parse_address()))
    results.append(("Ratio Calculation", test_calculate_ratio()))
    results.append(("API Fallback", test_get_land_price_info_without_api()))
    results.append(("Integration", test_integration()))
    
    # Summary
    print("=" * 60)
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
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
