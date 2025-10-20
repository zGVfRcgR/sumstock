#!/usr/bin/env python3
"""
Test script for the scraper with rosenka integration
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrape_sumstock import scrape_property_data, format_markdown
from bs4 import BeautifulSoup

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


def test_scraper_with_rosenka():
    """Test scraper integration with rosenka"""
    print("Testing scraper with rosenka integration:\n")
    
    # Parse mock HTML
    from scripts.scrape_sumstock import BeautifulSoup
    soup = BeautifulSoup(MOCK_SUMSTOCK_HTML, 'html.parser')
    
    # Mock the scrape_property_data function to use our HTML
    # We'll manually parse the data similar to what the scraper does
    from scripts.scrape_sumstock import (
        parse_price, parse_area, calculate_unit_price
    )
    from scripts.rosenka import get_rosenka_for_property, calculate_rosenka_ratio
    
    property_items = soup.select('div.bukkenUnitBox')
    properties = []
    
    for item in property_items:
        property_data = {
            'location': '不明',
            'total_price': '-',
            'building_price': '-',
            'building_area': '-',
            'building_unit_price': '-',
            'land_price': '-',
            'land_area': '-',
            'land_unit_price': '-',
            'maker': '-',
            'rosenka_value': '-',
            'rosenka_ratio': '-'
        }
        
        # Extract location
        location_elem = item.select_one('h5.bukkenName')
        if location_elem:
            property_data['location'] = location_elem.get_text().strip()
        
        # Extract prices
        price_elems = item.select('span.bold')
        prices = []
        for elem in price_elems:
            text = elem.get_text().replace('万円', '').strip()
            prices.append(text)
        
        if len(prices) >= 1:
            property_data['total_price'] = f"{prices[0]}万円"
        if len(prices) >= 2:
            property_data['building_price'] = f"{prices[1]}万円"
        if len(prices) >= 3:
            property_data['land_price'] = f"{prices[2]}万円"
        
        # Extract areas
        area_elems = item.select('.area .value')
        areas = []
        for elem in area_elems:
            text = elem.get_text().strip()
            areas.append(text)
        
        if len(areas) >= 1:
            property_data['building_area'] = f"{areas[0]}m²"
            building_price = parse_price(property_data['building_price'])
            building_area = parse_area(property_data['building_area'])
            unit_price = calculate_unit_price(building_price, building_area)
            if unit_price:
                property_data['building_unit_price'] = f"約{unit_price:.2f}万円/m²"
        
        if len(areas) >= 2:
            property_data['land_area'] = f"{areas[1]}m²"
            land_price = parse_price(property_data['land_price'])
            land_area = parse_area(property_data['land_area'])
            unit_price = calculate_unit_price(land_price, land_area)
            if unit_price:
                property_data['land_unit_price'] = f"約{unit_price:.2f}万円/m²"
        
        # Extract maker
        maker_elem = item.select_one('.maker')
        if maker_elem:
            property_data['maker'] = maker_elem.get_text().strip()
        
        # Get rosenka value and calculate ratio
        if property_data['location'] != '不明':
            rosenka_value = get_rosenka_for_property(property_data['location'])
            if rosenka_value is not None:
                property_data['rosenka_value'] = f"{rosenka_value:.2f}万円/m²"
                
                # Calculate rosenka ratio
                ratio = calculate_rosenka_ratio(property_data['building_unit_price'], rosenka_value)
                if ratio is not None:
                    property_data['rosenka_ratio'] = f"{ratio:.2f}x"
        
        properties.append(property_data)
    
    # Display results
    print(f"Found {len(properties)} properties:\n")
    for i, prop in enumerate(properties, 1):
        print(f"Property {i}:")
        print(f"  Location: {prop['location']}")
        print(f"  Total Price: {prop['total_price']}")
        print(f"  Building Price: {prop['building_price']}")
        print(f"  Building Area: {prop['building_area']}")
        print(f"  Building Unit Price: {prop['building_unit_price']}")
        print(f"  Land Price: {prop['land_price']}")
        print(f"  Land Area: {prop['land_area']}")
        print(f"  Land Unit Price: {prop['land_unit_price']}")
        print(f"  Maker: {prop['maker']}")
        print(f"  Rosenka: {prop['rosenka_value']}")
        print(f"  Rosenka Ratio: {prop['rosenka_ratio']}")
        print()
    
    # Test markdown generation
    print("Generating Markdown output:\n")
    print("-" * 80)
    markdown = format_markdown(properties, 'https://sumstock.jp/test', datetime.now())
    print(markdown)
    print("-" * 80)
    
    # Verify rosenka fields are present in markdown
    assert '路線価（万円/m²）' in markdown, "Rosenka header not found in markdown"
    assert '路線価倍率' in markdown, "Rosenka ratio header not found in markdown"
    assert '12.50万円/m²' in markdown, "Rosenka value not found in markdown"
    
    # Verify ratio is calculated and present
    for prop in properties:
        if prop['rosenka_ratio'] != '-':
            assert prop['rosenka_ratio'] in markdown, f"Ratio {prop['rosenka_ratio']} not found in markdown"
    
    print("\n✓ All integration tests passed!")


if __name__ == '__main__':
    print("=" * 80)
    print("Scraper with Rosenka Integration Test")
    print("=" * 80)
    print()
    
    test_scraper_with_rosenka()
    
    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print("=" * 80)
