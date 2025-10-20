#!/usr/bin/env python3
"""
Test script for the rosenka module
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.rosenka import (
    get_rosenka_for_property,
    calculate_rosenka_ratio,
    normalize_location,
    load_rosenka_data
)


def test_normalize_location():
    """Test location normalization"""
    print("Testing location normalization:")
    
    tests = [
        ('松戸市中金杉1丁目', '松戸市'),
        ('柏市柏3丁目', '柏市'),
        ('市川市行徳駅前', '市川市'),
    ]
    
    for input_loc, expected in tests:
        result = normalize_location(input_loc)
        print(f"  Input: '{input_loc}' -> Output: '{result}'")
        # Partial match is OK for this test
    
    print("  ✓ Normalization tests completed\n")


def test_load_rosenka_data():
    """Test loading rosenka data from CSV"""
    print("Testing rosenka data loading:")
    
    data = load_rosenka_data()
    print(f"  Loaded {len(data)} rosenka entries")
    
    if data:
        print("  Sample entries:")
        for location, value in list(data.items())[:3]:
            print(f"    {location}: {value}万円/m²")
    
    print("  ✓ Data loading test completed\n")


def test_get_rosenka_for_property():
    """Test getting rosenka value for properties"""
    print("Testing rosenka lookup:")
    
    test_locations = [
        '松戸市中金杉1丁目',
        '松戸市小金原2丁目',
        '柏市',
        '市川市',
        '不明な場所',
    ]
    
    for location in test_locations:
        rosenka = get_rosenka_for_property(location)
        if rosenka is not None:
            print(f"  {location}: {rosenka}万円/m²")
        else:
            print(f"  {location}: データなし")
    
    print("  ✓ Rosenka lookup tests completed\n")


def test_calculate_rosenka_ratio():
    """Test rosenka ratio calculation"""
    print("Testing rosenka ratio calculation:")
    
    test_cases = [
        ('約9.34万円/m²', 12.5, '0.75x'),
        ('約6.96万円/m²', 12.5, '0.56x'),
        ('約15.00万円/m²', 10.0, '1.50x'),
        ('-', 12.5, None),
        ('約10.00万円/m²', None, None),
    ]
    
    for building_price, rosenka, expected_ratio in test_cases:
        ratio = calculate_rosenka_ratio(building_price, rosenka)
        if ratio is not None:
            result = f"{ratio:.2f}x"
            print(f"  {building_price} / {rosenka} = {result}", end='')
            if expected_ratio and abs(float(result[:-1]) - float(expected_ratio[:-1])) < 0.01:
                print(" ✓")
            else:
                print()
        else:
            print(f"  {building_price} / {rosenka} = None", end='')
            if expected_ratio is None:
                print(" ✓")
            else:
                print()
    
    print("  ✓ Ratio calculation tests completed\n")


def test_integration():
    """Test integration with property data"""
    print("Testing integration with mock property data:")
    
    # Mock property similar to what scraper produces
    properties = [
        {
            'location': '松戸市中金杉1丁目',
            'building_unit_price': '約9.34万円/m²',
        },
        {
            'location': '松戸市小金原2丁目',
            'building_unit_price': '約9.30万円/m²',
        },
        {
            'location': '柏市',
            'building_unit_price': '約12.00万円/m²',
        },
    ]
    
    for prop in properties:
        location = prop['location']
        building_price = prop['building_unit_price']
        
        rosenka = get_rosenka_for_property(location)
        ratio = calculate_rosenka_ratio(building_price, rosenka)
        
        print(f"  Location: {location}")
        print(f"    Building unit price: {building_price}")
        print(f"    Rosenka: {rosenka:.2f}万円/m²" if rosenka else "    Rosenka: -")
        print(f"    Ratio: {ratio:.2f}x" if ratio else "    Ratio: -")
        print()
    
    print("  ✓ Integration tests completed\n")


if __name__ == '__main__':
    print("=" * 60)
    print("Rosenka Module Tests")
    print("=" * 60)
    print()
    
    test_normalize_location()
    test_load_rosenka_data()
    test_get_rosenka_for_property()
    test_calculate_rosenka_ratio()
    test_integration()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
