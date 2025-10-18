#!/usr/bin/env python3
"""
Test script for the scraper with mock data
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrape_sumstock import format_markdown, save_markdown_file

# Mock property data
mock_properties = [
    {
        'location': '松戸市中金杉1丁目',
        'total_price': '3,280万円',
        'building_price': '1,054万円',
        'building_area': '112.85m²',
        'building_unit_price': '約9.34万円/m²',
        'land_price': '2,226万円',
        'land_area': '151.45m²',
        'land_unit_price': '約14.70万円/m²',
        'maker': '積水ハウス'
    },
    {
        'location': '松戸市小金原2丁目',
        'total_price': '2,980万円',
        'building_price': '980万円',
        'building_area': '105.32m²',
        'building_unit_price': '約9.30万円/m²',
        'land_price': '2,000万円',
        'land_area': '140.50m²',
        'land_unit_price': '約14.23万円/m²',
        'maker': 'ダイワハウス'
    }
]

def test_format_and_save():
    """Test formatting and saving markdown"""
    url = "https://sumstock.jp/search/02/12/12207"
    date = datetime.now()
    
    # Format markdown
    markdown = format_markdown(mock_properties, url, date)
    
    print("Generated Markdown:")
    print("-" * 80)
    print(markdown)
    print("-" * 80)
    
    # Save to temp file
    output_dir = '/tmp/sumstock-test'
    filepath = save_markdown_file(markdown, date, output_dir)
    
    print(f"\nFile saved to: {filepath}")
    
    # Read and display the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\nFile content:")
    print("-" * 80)
    print(content)
    print("-" * 80)

if __name__ == '__main__':
    test_format_and_save()
