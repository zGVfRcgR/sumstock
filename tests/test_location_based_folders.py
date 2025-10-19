#!/usr/bin/env python3
"""
Test script for location-based folder structure
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.location_mapping import parse_url_location, get_prefecture_name, get_city_name
from scripts.scrape_sumstock import save_markdown_file


def test_parse_url_location():
    """Test URL parsing for location information"""
    print("Testing URL parsing...")
    
    # Test 1: Chiba - Matsudo (千葉県松戸市)
    url1 = "https://sumstock.jp/search/02/12/12207"
    pref_code, pref_name, city_code, city_name = parse_url_location(url1)
    print(f"  URL: {url1}")
    print(f"    Prefecture: {pref_code} -> {pref_name}")
    print(f"    City: {city_code} -> {city_name}")
    assert pref_name == "千葉県", f"Expected 千葉県, got {pref_name}"
    assert city_name == "松戸市", f"Expected 松戸市, got {city_name}"
    
    # Test 2: Chiba - Kashiwa (千葉県柏市)
    url2 = "https://sumstock.jp/search/02/12/12215"
    pref_code, pref_name, city_code, city_name = parse_url_location(url2)
    print(f"  URL: {url2}")
    print(f"    Prefecture: {pref_code} -> {pref_name}")
    print(f"    City: {city_code} -> {city_name}")
    assert pref_name == "千葉県", f"Expected 千葉県, got {pref_name}"
    assert city_name == "柏市", f"Expected 柏市, got {city_name}"
    
    # Test 3: Tokyo - Chiyoda-ku (東京都千代田区)
    url3 = "https://sumstock.jp/search/01/13/13101"
    pref_code, pref_name, city_code, city_name = parse_url_location(url3)
    print(f"  URL: {url3}")
    print(f"    Prefecture: {pref_code} -> {pref_name}")
    print(f"    City: {city_code} -> {city_name}")
    assert pref_name == "東京都", f"Expected 東京都, got {pref_name}"
    assert city_name == "千代田区", f"Expected 千代田区, got {city_name}"
    
    print("✓ All URL parsing tests passed!\n")


def test_folder_structure_creation():
    """Test that files are saved in correct location-based folders"""
    print("Testing folder structure creation...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='sumstock_location_test_')
    
    try:
        current_date = datetime.now()
        markdown_content = "# Test Content\n\nThis is a test."
        
        # Test 1: Save file for Matsudo, Chiba
        url1 = "https://sumstock.jp/search/02/12/12207"
        filepath1 = save_markdown_file(markdown_content, current_date, output_dir=temp_dir, url=url1)
        
        expected_path1 = os.path.join(temp_dir, "千葉県", "松戸市", current_date.strftime('%Y-%m-%d') + '.md')
        assert filepath1 == expected_path1, f"Expected {expected_path1}, got {filepath1}"
        assert os.path.exists(filepath1), f"File not created: {filepath1}"
        print(f"  ✓ Created: {filepath1}")
        
        # Test 2: Save file for Kashiwa, Chiba
        url2 = "https://sumstock.jp/search/02/12/12215"
        filepath2 = save_markdown_file(markdown_content, current_date, output_dir=temp_dir, url=url2)
        
        expected_path2 = os.path.join(temp_dir, "千葉県", "柏市", current_date.strftime('%Y-%m-%d') + '.md')
        assert filepath2 == expected_path2, f"Expected {expected_path2}, got {filepath2}"
        assert os.path.exists(filepath2), f"File not created: {filepath2}"
        print(f"  ✓ Created: {filepath2}")
        
        # Test 3: Save file for Chiyoda-ku, Tokyo
        url3 = "https://sumstock.jp/search/01/13/13101"
        filepath3 = save_markdown_file(markdown_content, current_date, output_dir=temp_dir, url=url3)
        
        expected_path3 = os.path.join(temp_dir, "東京都", "千代田区", current_date.strftime('%Y-%m-%d') + '.md')
        assert filepath3 == expected_path3, f"Expected {expected_path3}, got {filepath3}"
        assert os.path.exists(filepath3), f"File not created: {filepath3}"
        print(f"  ✓ Created: {filepath3}")
        
        # Verify directory structure
        print("\n  Directory structure:")
        for root, dirs, files in os.walk(temp_dir):
            level = root.replace(temp_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        print("\n✓ All folder structure tests passed!\n")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        print(f"Cleaned up test directory: {temp_dir}")


def test_fallback_for_unknown_location():
    """Test that unknown locations fall back to data/ directory"""
    print("\nTesting fallback for unknown locations...")
    
    temp_dir = tempfile.mkdtemp(prefix='sumstock_fallback_test_')
    
    try:
        current_date = datetime.now()
        markdown_content = "# Test Content\n"
        
        # Test with unknown city code
        url = "https://sumstock.jp/search/99/99/99999"
        filepath = save_markdown_file(markdown_content, current_date, output_dir=temp_dir, url=url)
        
        # Should fall back to data/その他/その他/
        expected_path = os.path.join(temp_dir, "その他", "その他", current_date.strftime('%Y-%m-%d') + '.md')
        assert filepath == expected_path, f"Expected {expected_path}, got {filepath}"
        assert os.path.exists(filepath), f"File not created: {filepath}"
        print(f"  ✓ Fallback to その他/その他/ for unknown location")
        
        print("✓ Fallback test passed!\n")
        
    finally:
        shutil.rmtree(temp_dir)
        print(f"Cleaned up test directory: {temp_dir}")


if __name__ == '__main__':
    print("=" * 70)
    print("Location-based Folder Structure Tests")
    print("=" * 70)
    print()
    
    test_parse_url_location()
    test_folder_structure_creation()
    test_fallback_for_unknown_location()
    
    print("=" * 70)
    print("✓ All location-based folder tests passed!")
    print("=" * 70)
