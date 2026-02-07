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
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Import location mapping functions
try:
    from location_mapping import PREFECTURE_MAP, CITY_MAP
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from location_mapping import PREFECTURE_MAP, CITY_MAP

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


def parse_manken_from_text(text: str) -> Optional[str]:
    """Parse text containing Japanese price formats and return a formatted string like '12,000万円'.

    Supports patterns like:
    - '1億2,000万円' -> 12000万円
    - '2,980万円' -> 2,980万円
    - '12000万円' -> 12,000万円
    Returns None if no price found.
    """
    if not text:
        return None
    s = re.sub(r'\s+', '', text)
    # First try 'X億Y万円'
    m = re.search(r'([0-9,]+)億([0-9,]+)万円', s)
    if m:
        try:
            oku = int(m.group(1).replace(',', ''))
            man = int(m.group(2).replace(',', ''))
            total_manken = oku * 10000 + man
            return f"{total_manken:,}万円"
        except ValueError:
            pass

    # Try 'X億万円' (no additional man)
    m2 = re.search(r'([0-9,]+)億万円', s)
    if m2:
        try:
            oku = int(m2.group(1).replace(',', ''))
            total_manken = oku * 10000
            return f"{total_manken:,}万円"
        except ValueError:
            pass

    # Try simple man-yen pattern: 'X,XXX万円' or 'XXXX万円'
    m3 = re.search(r'([0-9,]+)万円', s)
    if m3:
        try:
            val = int(m3.group(1).replace(',', ''))
            return f"{val:,}万円"
        except ValueError:
            pass

    # As a last resort, try to find any integer and treat it as man-yen
    m4 = re.search(r'([0-9,]+)', s)
    if m4:
        try:
            val = int(m4.group(1).replace(',', ''))
            return f"{val:,}万円"
        except ValueError:
            pass

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


def get_location_from_url(url: str) -> tuple[str, str]:
    """Get prefecture and city name directly from URL code
    
    This ensures that files are always saved to folders matching the URL code,
    preventing mismatches between URL and folder location.
    
    Args:
        url: SumStock URL (e.g., 'https://sumstock.jp/search/02/12/12217')
    
    Returns:
        Tuple of (prefecture_name, city_name) based on URL codes
        Returns ('その他', 'その他') if URL cannot be parsed
    """
    return _extract_location_from_url_code(url)


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
                    # Find the closest feature to the geocoded coordinates
                    closest_feature = None
                    min_distance = float('inf')
                    for feature in data['features']:
                        geom = feature['geometry']
                        if geom['type'] == 'Point':
                            lon_feat, lat_feat = geom['coordinates']
                            distance = math.sqrt((lat - lat_feat)**2 + (lon - lon_feat)**2)
                            if distance < min_distance:
                                min_distance = distance
                                closest_feature = feature
                    
                    if closest_feature:
                        props = closest_feature['properties']
                        pref_name = props.get('prefecture_name_ja', 'その他')
                        city_name = props.get('city_county_name_ja', 'その他')
                        return pref_name, city_name
                else:
                    pass
            else:
                pass
        except Exception as e:
            print(f"Warning: Failed to get location from API for {address}: {e}", file=sys.stderr)
    
    # Fallback: parse location from address string and URL
    return parse_location_from_address(address, url)


def _extract_location_from_url_code(url: str) -> tuple[str, str]:
    """Helper function to extract prefecture and city codes from URL
    
    Args:
        url: SumStock URL (e.g., 'https://sumstock.jp/search/02/12/12217')
    
    Returns:
        Tuple of (prefecture_name, city_name) based on URL codes
        Returns ('その他', 'その他') if URL cannot be parsed
    """
    if not url:
        return 'その他', 'その他'
    
    try:
        # Extract codes from URL pattern: /search/region/prefecture/city
        pattern = r'/search/(\d+)/(\d+)/(\d+)'
        match = re.search(pattern, url)
        if match:
            pref_code = match.group(2)  # Middle number is prefecture
            city_code = match.group(3)  # Last number is city
            pref_name = PREFECTURE_MAP.get(pref_code.zfill(2), 'その他')
            # Get city name from CITY_MAP
            pref_cities = CITY_MAP.get(pref_code.zfill(2), {})
            city_name = pref_cities.get(city_code, 'その他')
            return pref_name, city_name
    except Exception:
        pass
    
    return 'その他', 'その他'


def parse_location_from_address(address: str, url: str = '') -> tuple[str, str]:
    """Parse prefecture and city from Japanese address string and URL"""
    if not address:
        return 'その他', 'その他'
    
    # Get prefecture and city from URL if available
    if url:
        pref_name, city_name = _extract_location_from_url_code(url)
        if pref_name != 'その他' or city_name != 'その他':
            return pref_name, city_name
    
    # Fallback: parse from address string
    pref_name = 'その他'
    city_name = 'その他'
    
    # If prefecture not found in URL, try to find in address
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
    remaining = address
    
    # Remove prefecture if present
    if pref_name != 'その他' and pref_name in remaining:
        remaining = remaining.replace(pref_name, '', 1).strip()
    
    # Look for city name (市/区/町/村 until next 市/区/町/村 or space)
    # Pattern: match from start until we hit another 市/区/町/村 or number/space
    match = re.match(r'^(.+[市区町村])', remaining)
    if match:
        candidate = match.group(1).strip()
        # Validate it's a reasonable city name
        if len(candidate) >= 2 and len(candidate) <= 15 and any(suffix in candidate for suffix in ['区', '市', '町', '村']):
            city_name = candidate
    
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
                    'maker_image': '-',
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

                # Price extraction: iterate over all div.price blocks and use labels when present
                price_divs = item.select('div.price')
                for pd in price_divs:
                    try:
                        pd_text = pd.get_text(separator='', strip=True)
                        # Determine label if present
                        label_elem = pd.select_one('.label')
                        label_txt = label_elem.get_text(strip=True) if label_elem else ''
                        parsed = parse_manken_from_text(pd_text)
                        if not parsed:
                            continue
                        value_plain = parsed.replace('万円', '')
                        if '総' in label_txt or '総額' in label_txt:
                            prices_dict['total'] = value_plain
                        elif '建物' in label_txt:
                            prices_dict['building'] = value_plain
                        elif '土地' in label_txt:
                            prices_dict['land'] = value_plain
                        else:
                            # No explicit label: collect into a generic list for fallback
                            prices_dict.setdefault('_unlabeled', []).append(value_plain)
                    except Exception:
                        continue

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
                        t_raw = elem.get_text(separator='', strip=True)
                        parsed = parse_manken_from_text(t_raw)
                        if parsed:
                            bold_prices.append(parsed.replace('万円', ''))

                    # If we have two bold prices, map them conservatively:
                    # prefer to assign building and land if labels missing by position: assume order may be (total, building, land) or (building, land)
                    if len(bold_prices) >= 2:
                        # If total is missing and there are 3 values, assume first is total
                        if 'total' not in prices_dict and len(bold_prices) >= 3:
                            prices_dict['total'] = bold_prices[0]
                            # then building and land
                            prices_dict.setdefault('building', bold_prices[1])
                            prices_dict.setdefault('land', bold_prices[2])
                        elif len(bold_prices) == 2:
                            # two values: prefer building then land
                            prices_dict.setdefault('building', bold_prices[0])
                            prices_dict.setdefault('land', bold_prices[1])
                        else:
                            # fallback: if only one value, treat as total
                            prices_dict.setdefault('total', bold_prices[0])

                if 'total' not in prices_dict or 'building' not in prices_dict or 'land' not in prices_dict:
                    # final fallback: regex against full item text (order-based: total, building, land)
                    # final fallback: use the specialized parser to handle '億' fragments
                    # Try to find any price-like fragment inside the item
                    all_prices = []
                    # Look for full patterns like 'X億Y万円' first
                    for mfrag in re.finditer(r'[0-9,]+億[0-9,]+万円', item_text):
                        parsed = parse_manken_from_text(mfrag.group(0))
                        if parsed:
                            all_prices.append(parsed.replace('万円', ''))
                    if not all_prices:
                        # fallback to simpler man-yen matches
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
                
                # Calculate total price if missing or seems incorrect
                if property_data['total_price'] == '-' and property_data['building_price'] != '-' and property_data['land_price'] != '-':
                    try:
                        building_val = parse_price(property_data['building_price'])
                        land_val = parse_price(property_data['land_price'])
                        if building_val is not None and land_val is not None:
                            total_val = building_val + land_val
                            property_data['total_price'] = f"{total_val:,.0f}万円"
                    except:
                        pass
                elif property_data['total_price'] != '-' and property_data['building_price'] != '-' and property_data['land_price'] != '-':
                    try:
                        total_val = parse_price(property_data['total_price'])
                        building_val = parse_price(property_data['building_price'])
                        land_val = parse_price(property_data['land_price'])
                        if total_val is not None and building_val is not None and land_val is not None:
                            calculated_total = building_val + land_val
                            # If the difference is significant (>10%), recalculate
                            if abs(total_val - calculated_total) / calculated_total > 0.1:
                                property_data['total_price'] = f"{calculated_total:,.0f}万円"
                    except:
                        pass
                
                # Try to find house maker
                maker_patterns = ['積水ハウス', 'ダイワハウス', '大和ハウス', 'セキスイハイム', 
                                'パナホーム', 'ミサワホーム', 'ヘーベルハウス', '住友林業', 
                                'トヨタホーム', '三井ホーム']
                for maker in maker_patterns:
                    if maker in item_text:
                        property_data['maker'] = maker
                        break

                # Try to extract maker image from an element with class 'maker' if present
                try:
                    maker_elem = item.select_one('.maker')
                    img_url = None
                    if maker_elem:
                        img_tag = maker_elem.find('img')
                        if img_tag and img_tag.get('src'):
                            img_src = img_tag.get('src')
                            # Resolve relative URLs against the page URL
                            img_url = urljoin(response.url, img_src)
                    # If we didn't find an explicit .maker img, try common alternatives
                    if not img_url:
                        # look for any img inside the item whose alt contains maker name
                        if property_data['maker'] and property_data['maker'] != '-':
                            alt_img = item.find('img', alt=re.compile(re.escape(property_data['maker'])))
                            if alt_img and alt_img.get('src'):
                                img_url = urljoin(response.url, alt_img.get('src'))
                    if img_url:
                        property_data['maker_image'] = img_url
                except Exception:
                    # Non-fatal; continue without maker image
                    pass
                
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


def ensure_prefecture_index(output_dir: str, pref_name: str):
    """Ensure prefecture index.md exists
    
    Args:
        output_dir: Base output directory (e.g., 'data')
        pref_name: Prefecture name
    """
    pref_dir = os.path.join(output_dir, pref_name)
    index_path = os.path.join(pref_dir, 'index.md')
    
    # Only create if it doesn't exist
    if os.path.exists(index_path):
        return
    
    os.makedirs(pref_dir, exist_ok=True)
    
    content = f"""---
layout: default
title: {pref_name}
parent: データ一覧
has_children: true
nav_order: 10
---

# {pref_name}

このページには{pref_name}の市町村別データが表示されています。

各市町村を選択してデータをご覧ください。
"""
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created prefecture index: {index_path}")


def ensure_city_index(output_dir: str, pref_name: str, city_name: str):
    """Ensure city index.md exists
    
    Args:
        output_dir: Base output directory (e.g., 'data')
        pref_name: Prefecture name
        city_name: City name
    """
    city_dir = os.path.join(output_dir, pref_name, city_name)
    index_path = os.path.join(city_dir, 'index.md')
    
    # Only create if it doesn't exist
    if os.path.exists(index_path):
        return
    
    os.makedirs(city_dir, exist_ok=True)
    
    content = f"""---
layout: default
title: {city_name}
parent: {pref_name}
has_children: true
nav_order: 10
---

# {city_name}

このページには{pref_name}{city_name}の日付別データが表示されています。

各日付を選択してデータをご覧ください。
"""
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created city index: {index_path}")


def format_markdown(properties: List[Dict], url: str, date: datetime, pref_name: str = 'その他', city_name: str = 'その他') -> str:
    """Format property data as Markdown with proper parent hierarchy
    
    The front matter uses parent: city_name to establish the hierarchy:
    データ一覧 > Prefecture > City > Date
    """
    date_str = date.strftime('%Y年%m月%d日')
    
    # Use parent-child hierarchy for proper navigation
    markdown = f"""---
layout: default
title: {date.strftime('%Y-%m-%d')}
parent: {city_name}
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
            # If a maker image URL is present, render an inline image; otherwise render maker text
            maker_cell = prop.get('maker', '-')
            maker_img = prop.get('maker_image', '-')
            if maker_img and maker_img != '-':
                # Use HTML <img> to ensure sizing works in markdown renderers
                maker_cell = f"<img src=\"{maker_img}\" alt=\"{prop.get('maker','')}\" style=\"height:32px;\">"

            markdown += f"| {prop['location']} | {prop['total_price']} | {prop['building_price']} | {prop['building_area']} | {prop['building_unit_price']} | {prop['land_price']} | {prop['land_area']} | {prop['land_unit_price']} | {maker_cell} | {prop['land_value']} |\n"
    
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
    # Ensure prefecture and city index pages exist
    ensure_prefecture_index(output_dir, pref_name)
    ensure_city_index(output_dir, pref_name, city_name)
    
    # Create folder structure: data/prefecture/city/
    # Always create folders even for unknown locations (その他)
    city_dir = os.path.join(output_dir, pref_name, city_name)
    
    os.makedirs(city_dir, exist_ok=True)
    filename = date.strftime('%Y-%m-%d') + suffix + '.md'
    filepath = os.path.join(city_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"Saved data to {filepath}")
    return filepath


def main():
    """Main function"""
    # Initialize API client
    api_key = os.environ.get('REINFOLIB_API_KEY', '')
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
        
        # Get location directly from URL code to ensure consistency
        # This prevents mismatches where URL code doesn't match scraped addresses
        pref_name, city_name = get_location_from_url(url)
        
        # Log a warning if URL code doesn't match scraped data
        if properties:
            first_location = properties[0].get('location', '')
            if first_location and first_location != '不明':
                # Parse city from first property address
                data_pref, data_city = parse_location_from_address(first_location, '')
                if data_city != city_name and data_city != 'その他' and city_name != 'その他':
                    print(f"Warning: URL code indicates '{city_name}' but scraped data contains '{data_city}' addresses. "
                          f"Saving to '{city_name}' folder based on URL.", file=sys.stderr)
        
        # Format as Markdown
        markdown = format_markdown(properties, url, current_date, pref_name, city_name)
        
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
