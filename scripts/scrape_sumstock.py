#!/usr/bin/env python3
"""
SumStock property data scraper
Scrapes property information from SumStock.jp and generates Markdown files
"""

import os
import sys
import re
import json
import math
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Import location mapping functions
try:
    from location_mapping import PREFECTURE_MAP
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from location_mapping import PREFECTURE_MAP

# Import Real Estate API client
try:
    from real_estate_api import RealEstateInfoLibAPI
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from real_estate_api import RealEstateInfoLibAPI


def extract_urls_from_issue(issue_body: str) -> List[str]:
    """Extract all SumStock URLs from issue body"""
    # Look for SumStock URLs in the issue body
    url_pattern = r'https://sumstock\.jp/search/\d+/\d+/\d+'
    matches = re.findall(url_pattern, issue_body)
    return matches


def parse_price(price_str: str) -> Optional[float]:
    """Parse price string and return value in man-yen (万円)"""
    if not price_str or price_str == '-':
        return None
    # Remove '万円' and commas, convert to float
    price_str = price_str.replace('万円', '').replace(',', '').strip()
    try:
        return float(price_str)
    except ValueError:
        return None


def parse_area(area_str: str) -> Optional[float]:
    """Parse area string and return value in m²"""
    if not area_str or area_str == '-':
        return None
    # Remove 'm²' and commas, convert to float
    area_str = area_str.replace('m²', '').replace('㎡', '').replace(',', '').strip()
    try:
        return float(area_str)
    except ValueError:
        return None


def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> tuple[int, int]:
    """Convert latitude/longitude to tile coordinates"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def geocode_address(address: str) -> Optional[tuple[float, float]]:
    """Geocode address to latitude/longitude"""
    try:
        geolocator = Nominatim(user_agent="sumstock-scraper")
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        return None
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None


def get_location_from_api(address: str, api_client, url: str = '') -> tuple[str, str]:
    """Get prefecture and city name from address using Real Estate API or fallback parsing"""
    if not address or address == '不明':
        return 'その他', 'その他'
    
    # Try API first if available
    if api_client:
        try:
            coords = geocode_address(address)
            if coords:
                lat, lon = coords
                x, y = deg2num(lat, lon, 13)
                
                data = api_client.get_point_data("geojson", 13, x, y, "2024")
                if data and 'features' in data and data['features']:
                    # Get location from first feature
                    feature = data['features'][0]
                    props = feature['properties']
                    pref_name = props.get('prefecture_name_ja', 'その他')
                    city_name = props.get('city_name_ja', 'その他')
                    return pref_name, city_name
        except Exception as e:
            print(f"Warning: Failed to get location from API for {address}: {e}", file=sys.stderr)
    
    # Fallback: parse location from address string and URL
    return parse_location_from_address(address, url)


def parse_location_from_address(address: str, url: str = '') -> tuple[str, str]:
    """Parse prefecture and city from Japanese address string and URL"""
    if not address:
        return 'その他', 'その他'
    
    # Get prefecture from URL if available
    pref_name = 'その他'
    if url:
        try:
            # Extract prefecture code from URL pattern: /search/region/prefecture/city
            pattern = r'/search/(\d+)/(\d+)/(\d+)'
            match = re.search(pattern, url)
            if match:
                pref_code = match.group(2)  # Middle number is prefecture
                pref_name = PREFECTURE_MAP.get(pref_code.zfill(2), 'その他')
        except:
            pass
    
    # If prefecture not found in URL, try to find in address
    if pref_name == 'その他':
        prefectures = [
            '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
            '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
            '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
            '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
            '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
            '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
            '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
        ]
        
        for pref in prefectures:
            if pref in address:
                pref_name = pref
                break
    
    # Extract city name from address
    city_name = 'その他'
    remaining = address
    
    # Remove prefecture if present
    if pref_name != 'その他' and pref_name in remaining:
        remaining = remaining.replace(pref_name, '', 1).strip()
    
    # Look for common city patterns
    city_patterns = [
        r'^([^市区町村]+[市区町村])',  # Match until next 区/市/町/村
        r'^([^0-9]+)',  # Match until numbers
    ]
    for pattern in city_patterns:
        match = re.search(pattern, remaining)
        if match:
            candidate = match.group(1).strip()
            # Validate it's a reasonable city name (contains 市区町村 and not too long)
            if any(suffix in candidate for suffix in ['区', '市', '町', '村']) and len(candidate) <= 20:
                city_name = candidate
                break
    
    return pref_name, city_name


def calculate_unit_price(price: Optional[float], area: Optional[float]) -> Optional[float]:
    """Calculate unit price (price per m²)"""
    if price is None or area is None or area == 0:
        return None
    return price / area


def scrape_property_data(url: str) -> List[Dict]:
    """Scrape property data from SumStock URL"""
    # Initialize API client for land price lookup
    api_key = os.getenv("REINFOLIB_API_KEY")
    api_client = None
    if api_key:
        try:
            api_client = RealEstateInfoLibAPI(api_key)
        except Exception as e:
            print(f"Warning: Failed to initialize Real Estate API client: {e}", file=sys.stderr)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        properties = []
        
        # Try multiple selectors to find property listings
        # SumStock-specific selectors first, then common patterns for property listing sites
        selectors = [
            'div.bukkenUnitBox',
            'article.bukkenListWrap .bukkenUnitBox',
            '.bukkenUnitBox',
            'div.property-item',
            'div.property-card',
            'div.property',
            'li.property-item',
            'div[class*="property"]',
            'article.property',
            'div.bukken-item',
            'div.item',
            'tr.property',
        ]
        
        property_items = []
        for selector in selectors:
            items = soup.select(selector)
            if items and len(items) > 0:
                property_items = items
                print(f"Found {len(items)} items using selector: {selector}", file=sys.stderr)
                break
        
        # If no items found with specific selectors, try to find all divs with data
        if not property_items:
            print("Warning: No property items found with standard selectors", file=sys.stderr)
            # Return empty list - the calling code will handle this
            return []
        
        for item in property_items:
            try:
                # Initialize with default values
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
                    'land_value': '-'
                }
                
                # Get item text once for efficiency
                item_text = item.get_text()
                
                # Try to extract location
                # First try SumStock-specific h5.bukkenName element
                location_elem = item.select_one('h5.bukkenName')
                if location_elem:
                    property_data['location'] = location_elem.get_text().strip()
                else:
                    # Fallback to regex patterns
                    location_patterns = [
                        re.compile(r'[都道府県][市区町村].*?[0-9０-９]+丁目'),
                        re.compile(r'[市区町村].*?[0-9０-９]'),
                    ]
                    
                    for pattern in location_patterns:
                        match = pattern.search(item_text)
                        if match:
                            property_data['location'] = match.group(0).strip()
                            break
                
                # Price extraction (label-aware):
                # - total: take from `div.price`
                # - building/land: take from `div.priceItems` using label-aware regex
                prices_dict = {}

                # Total price: usually in div.price
                total_elem = item.select_one('div.price')
                if total_elem:
                    total_text = total_elem.get_text(separator=' ', strip=True)
                    m = re.search(r'([0-9,]+)\s*万円', total_text)
                    if m:
                        prices_dict['total'] = m.group(1)

                # Building / Land: try to parse from div.priceItems (label + number)
                price_items_elem = item.select_one('div.priceItems')
                if price_items_elem:
                    pi_text = price_items_elem.get_text(separator=' ', strip=True)
                    # e.g. "建物価格 1,054 万円 / 土地価格 2,226 万円"
                    b_match = re.search(r'建物価格[^0-9\n\r\u3000-]*([0-9,]+)\s*万円', pi_text)
                    l_match = re.search(r'土地価格[^0-9\n\r\u3000-]*([0-9,]+)\s*万円', pi_text)
                    if b_match:
                        prices_dict['building'] = b_match.group(1)
                    if l_match:
                        prices_dict['land'] = l_match.group(1)

                # Fallbacks: if above didn't find some entries, try span.bold (often contains building/land),
                # then finally a regex against the whole item text.
                if 'building' not in prices_dict or 'land' not in prices_dict:
                    # collect numbers from span.bold in DOM order
                    bold_price_elems = item.select('span.bold')
                    bold_prices = []
                    for elem in bold_price_elems:
                        t = elem.get_text(separator='', strip=True).replace('万円', '')
                        if t:
                            bold_prices.append(t)

                    # If we have two bold prices, map them to building and land
                    if len(bold_prices) >= 2:
                        if 'building' not in prices_dict:
                            prices_dict['building'] = bold_prices[0]
                        if 'land' not in prices_dict:
                            prices_dict['land'] = bold_prices[1]

                if 'total' not in prices_dict or 'building' not in prices_dict or 'land' not in prices_dict:
                    # final fallback: regex against full item text (order-based: total, building, land)
                    price_pattern = re.compile(r'([0-9,]+)\s*万円')
                    all_prices = price_pattern.findall(item_text)
                    if all_prices:
                        if 'total' not in prices_dict and len(all_prices) >= 1:
                            prices_dict['total'] = all_prices[0]
                        if 'building' not in prices_dict and len(all_prices) >= 2:
                            prices_dict['building'] = all_prices[1]
                        if 'land' not in prices_dict and len(all_prices) >= 3:
                            prices_dict['land'] = all_prices[2]
                
                # Try to find area elements with label-based extraction
                areas_dict = {}
                
                # Try to find area divs with labels (SumStock-specific structure)
                area_divs = item.select('div.area')
                for area_div in area_divs:
                    # Try multiple selector patterns for labels (more robust)
                    label_elem = area_div.select_one('span.label, .label, [class*="label"]')
                    value_elem = area_div.select_one('span.value, .value, [class*="value"]')
                    
                    if label_elem and value_elem:
                        # Normalize label text by removing extra whitespace
                        label = re.sub(r'\s+', '', label_elem.get_text().strip())
                        value = value_elem.get_text().replace('m²', '').replace('㎡', '').strip()
                        
                        # Map labels to standardized keys using normalized text
                        # Use component matching since whitespace has been normalized
                        if '建物' in label and '面積' in label:
                            areas_dict['building'] = value
                        elif '土地' in label and '面積' in label:
                            areas_dict['land'] = value
                
                # Fallback: If label-based extraction didn't work, try extracting all .value elements
                if not areas_dict:
                    area_elems = item.select('.area .value')
                    areas = []
                    if area_elems:
                        for elem in area_elems:
                            text = elem.get_text().replace('m²', '').replace('㎡', '').strip()
                            if text:
                                areas.append(text)
                    
                    # Further fallback to regex pattern if no .value elements found
                    if not areas:
                        area_pattern = re.compile(r'([0-9.]+)\s*[m²㎡]')
                        areas = area_pattern.findall(item_text)
                    
                    # Map fallback areas array to dict (order-based)
                    if len(areas) >= 1:
                        areas_dict['building'] = areas[0]
                    if len(areas) >= 2:
                        areas_dict['land'] = areas[1]
                
                # Process prices using the dictionary
                if 'total' in prices_dict:
                    property_data['total_price'] = f"{prices_dict['total']}万円"
                
                if 'building' in prices_dict:
                    property_data['building_price'] = f"{prices_dict['building']}万円"
                    building_price = parse_price(property_data['building_price'])
                    if 'building' in areas_dict:
                        property_data['building_area'] = f"{areas_dict['building']}m²"
                        building_area = parse_area(property_data['building_area'])
                        unit_price = calculate_unit_price(building_price, building_area)
                        if unit_price:
                            property_data['building_unit_price'] = f"約{unit_price:.2f}万円/m²"
                
                if 'land' in prices_dict:
                    property_data['land_price'] = f"{prices_dict['land']}万円"
                    land_price = parse_price(property_data['land_price'])
                    if 'land' in areas_dict:
                        property_data['land_area'] = f"{areas_dict['land']}m²"
                        land_area = parse_area(property_data['land_area'])
                        unit_price = calculate_unit_price(land_price, land_area)
                        if unit_price:
                            property_data['land_unit_price'] = f"約{unit_price:.2f}万円/m²"
                
                # Try to find house maker
                maker_patterns = ['積水ハウス', 'ダイワハウス', '大和ハウス', 'セキスイハイム', 
                                'パナホーム', 'ミサワホーム', 'ヘーベルハウス', '住友林業', 
                                'トヨタホーム', '三井ホーム']
                for maker in maker_patterns:
                    if maker in item_text:
                        property_data['maker'] = maker
                        break
                
                # Get land value from Real Estate Information Library API
                if api_client and property_data['location'] != '不明':
                    try:
                        coords = geocode_address(property_data['location'])
                        if coords:
                            lat, lon = coords
                            x, y = deg2num(lat, lon, 13)
                            tile_data = api_client.get_point_data("geojson", 13, x, y, "2024")
                            if tile_data and 'features' in tile_data:
                                # Find closest point
                                min_distance = float('inf')
                                closest_price = None
                                for feature in tile_data['features']:
                                    prop = feature['properties']
                                    point_coords = feature['geometry']['coordinates']
                                    point_lon, point_lat = point_coords[0], point_coords[1]
                                    # Simple Euclidean distance (approx for small areas)
                                    distance = math.sqrt((lat - point_lat)**2 + (lon - point_lon)**2)
                                    if distance < min_distance:
                                        min_distance = distance
                                        price_str = prop.get('u_current_years_price_ja', '')
                                        if price_str:
                                            closest_price = price_str
                                if closest_price:
                                    # Convert from yen to man-yen (万円)
                                    # closest_price is like "178,000(円/㎡)"
                                    try:
                                        yen_str = closest_price.replace(',', '').replace('(円/㎡)', '')
                                        yen_value = int(yen_str)
                                        man_yen = yen_value // 10000  # Convert to 万円
                                        property_data['land_value'] = f"{man_yen}万円/㎡"
                                    except (ValueError, AttributeError):
                                        property_data['land_value'] = closest_price
                    except Exception as e:
                        print(f"Warning: Failed to get land value for {property_data['location']}: {e}", file=sys.stderr)
                
                # Only add if we found at least some data
                if property_data['location'] != '不明' or prices_dict:
                    properties.append(property_data)
                
            except Exception as e:
                print(f"Error parsing property item: {e}", file=sys.stderr)
                continue
        
        return properties
        
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}", file=sys.stderr)
        return []
    finally:
        if api_client:
            api_client.close()


def format_markdown(properties: List[Dict], url: str, date: datetime) -> str:
    """Format property data as Markdown"""
    date_str = date.strftime('%Y年%m月%d日')
    
    markdown = f"""---
layout: default
title: {date.strftime('%Y-%m-%d')}
parent: データ一覧
nav_order: {date.strftime('%Y%m%d')}
---

# スムストック物件データ

## 取得日: {date_str}
### 参照URL: [{url}]({url})

| 所在地（町名） | 総額 | 建物価格 | 建物面積 | 建物単価（万円/m²） | 土地価格 | 土地面積 | 土地単価（万円/m²） | ハウスメーカー | 公示地価（万円/㎡） |
|----------------|-------|------------|-------------|------------------------|------------|-------------|------------------------|----------------|----------------|
"""
    
    if not properties:
        markdown += "| データなし | - | - | - | - | - | - | - | - | - |\n"
    else:
        for prop in properties:
            markdown += f"| {prop['location']} | {prop['total_price']} | {prop['building_price']} | {prop['building_area']} | {prop['building_unit_price']} | {prop['land_price']} | {prop['land_area']} | {prop['land_unit_price']} | {prop['maker']} | {prop['land_value']} |\n"
    
    markdown += "\n---\n\n**注意**: データは自動的に取得されます。\n"
    
    return markdown


def save_markdown_file(markdown: str, date: datetime, pref_name: str, city_name: str, output_dir: str = 'data', suffix: str = ''):
    """Save Markdown content to file
    
    Args:
        markdown: Markdown content to save
        date: Date for filename
        pref_name: Prefecture name for folder structure
        city_name: City name for folder structure
        output_dir: Output directory path
        suffix: Optional suffix for filename (e.g., '_1', '_2')
    """
    # Create folder structure: data/prefecture/city/
    # Always create folders even for unknown locations (その他)
    output_dir = os.path.join(output_dir, pref_name, city_name)
    
    os.makedirs(output_dir, exist_ok=True)
    filename = date.strftime('%Y-%m-%d') + suffix + '.md'
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Saved data to {filepath}")
    return filepath


def main():
    """Main function"""
    # Initialize API client
    api_key = os.environ.get('REAL_ESTATE_API_KEY', '')
    if api_key:
        api_client = RealEstateInfoLibAPI(api_key)
    else:
        api_client = None
    
    # Get issue body from environment variable
    issue_body = os.environ.get('ISSUE_BODY', '')
    
    # Determine URLs to process
    if len(sys.argv) > 1:
        # Use command-line arguments
        urls = sys.argv[1:]
    else:
        # Extract from issue body
        urls = extract_urls_from_issue(issue_body)
    
    if not urls:
        print("Error: No SumStock URL found. Please provide URL as argument or in ISSUE_BODY environment variable.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(urls)} URL(s) to process")
    
    # Get current date
    current_date = datetime.now()
    
    # Track all created file paths
    filepaths = []
    
    # Process each URL
    for i, url in enumerate(urls, start=1):
        print(f"\n[{i}/{len(urls)}] Scraping data from: {url}")
        
        # Scrape data
        properties = scrape_property_data(url)
        
        if not properties:
            print(f"Warning: No property data found for URL {i}. Creating file with empty data.", file=sys.stderr)
        
        # Get location from first property using API or address parsing
        if properties:
            first_location = properties[0].get('location', '')
            pref_name, city_name = get_location_from_api(first_location, api_client, url)
        else:
            pref_name, city_name = 'その他', 'その他'
        
        # Format as Markdown
        markdown = format_markdown(properties, url, current_date)
        
        # Save to file with location-based folder structure
        # No suffix needed when using location folders (each location gets its own folder)
        filepath = save_markdown_file(markdown, current_date, pref_name, city_name)
        filepaths.append(filepath)
        
        print(f"Successfully processed {len(properties)} properties from URL {i}")
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Total URLs processed: {len(urls)}")
    print(f"Total files created: {len(filepaths)}")
    
    # Output filepath for GitHub Actions
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            # Output comma-separated file paths
            f.write(f"filepath={','.join(filepaths)}\n")
            f.write(f"date={current_date.strftime('%Y-%m-%d')}\n")
            f.write(f"count={len(filepaths)}\n")


if __name__ == '__main__':
    main()
