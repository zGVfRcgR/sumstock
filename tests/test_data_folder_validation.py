#!/usr/bin/env python3
"""
Test to validate that data files are in the correct folders and URLs match the data.
"""

import os
import sys
import re
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from location_mapping import CITY_MAP, PREFECTURE_MAP

# Constants
NO_DATA_INDICATOR = 'データなし'


def get_prefecture_code_from_name(pref_name):
    """Get prefecture code from name by reversing PREFECTURE_MAP"""
    for code, name in PREFECTURE_MAP.items():
        if name == pref_name:
            return code
    return None


def extract_url_from_file(filepath):
    """Extract the SumStock URL from a markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'https://sumstock\.jp/search/\d+/\d+/(\d+)', content)
        if match:
            return match.group(1)
    return None


def extract_city_from_data(filepath):
    """Extract city names from the data table in a markdown file"""
    cities = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find all location entries in the table (format: | 市川市... | or | 柏市... |)
        # Skip table headers by checking for specific text
        matches = re.findall(r'\|\s*([^|]+[市区町村][^|]*)\s*\|', content)
        for match in matches:
            # Skip headers and metadata
            if '所在地' in match or '町名' in match:
                continue
            # Extract city name (市/区/町/村 suffix)
            # Only match characters that typically appear in city names (not 県)
            city_match = re.search(r'([^都道府県]+[市区町村])', match.strip())
            if city_match:
                cities.add(city_match.group(1))
    return cities


def get_city_name_from_code(pref_code, city_code):
    """Get city name from code using location mapping"""
    pref_cities = CITY_MAP.get(pref_code, {})
    return pref_cities.get(city_code, None)


def validate_data_folder_structure():
    """
    Validate that data files are in correct folders and URLs match data.
    Returns list of issues found.
    """
    issues = []
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Check all markdown files in prefecture/city structure
    for md_file in data_dir.rglob('*.md'):
        # Skip index files
        if md_file.name in ['index.md', 'sample.md']:
            continue
        
        # Get folder structure: data/{prefecture}/{city}/{file}
        parts = md_file.parts
        if len(parts) < 4:
            continue
            
        folder_city = parts[-2]  # The city folder name
        folder_pref = parts[-3]  # The prefecture folder name
        
        # Extract URL city code from file
        url_city_code = extract_url_from_file(md_file)
        if not url_city_code:
            issues.append(f"{md_file.relative_to(data_dir)}: No URL found in file")
            continue
        
        # Get expected city name from URL code
        # Extract prefecture code from folder structure using the mapping
        pref_code = get_prefecture_code_from_name(folder_pref)
        if not pref_code:
            # Skip validation for prefectures not in our mapping
            continue
        
        url_city_name = get_city_name_from_code(pref_code, url_city_code)
        
        # Extract actual cities from data
        data_cities = extract_city_from_data(md_file)
        
        # Validate: folder should match URL and data
        if url_city_name and url_city_name != folder_city:
            issues.append(
                f"{md_file.relative_to(data_dir)}: "
                f"Folder is '{folder_city}' but URL code {url_city_code} is for '{url_city_name}'"
            )
        
        # Validate: data should be for the same city as folder
        if data_cities:
            # Check if any data city matches the folder city exactly
            has_matching_city = any(city == folder_city for city in data_cities)
            if not has_matching_city and NO_DATA_INDICATOR not in data_cities:
                issues.append(
                    f"{md_file.relative_to(data_dir)}: "
                    f"Folder is '{folder_city}' but data is for {', '.join(data_cities)}"
                )
    
    return issues


def test_data_folder_structure():
    """Test that all data files are in correct folders"""
    issues = validate_data_folder_structure()
    
    if issues:
        print("Data folder structure validation FAILED:")
        for issue in issues:
            print(f"  - {issue}")
        assert False, f"Found {len(issues)} data folder structure issues"
    else:
        print("Data folder structure validation PASSED")


if __name__ == '__main__':
    test_data_folder_structure()
