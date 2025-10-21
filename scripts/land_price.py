#!/usr/bin/env python3
"""
Land price lookup module using Real Estate Information Library API
国土交通省不動産情報ライブラリAPIを使用した地価取得モジュール
"""

import os
import re
from typing import Optional, Tuple
import requests


# API configuration
API_BASE_URL = "https://www.reinfolib.mlit.go.jp/api/point"
DEFAULT_YEAR = "2023"  # Default year for land price data


def parse_address(address: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse address string to extract prefecture and city information
    
    Args:
        address: Japanese address string (e.g., "松戸市中金杉1丁目")
    
    Returns:
        Tuple of (prefecture_code, city_code) or (None, None) if parsing fails
    """
    if not address:
        return None, None
    
    # City name to code mapping with prefecture information
    # Format: 'city_name': ('pref_code', 'city_code')
    city_to_codes = {
        # 千葉県 (12)
        '千葉市': ('12', '100'),
        '千葉市中央区': ('12', '101'),
        '千葉市花見川区': ('12', '102'),
        '千葉市稲毛区': ('12', '103'),
        '千葉市若葉区': ('12', '104'),
        '千葉市緑区': ('12', '105'),
        '千葉市美浜区': ('12', '106'),
        '銚子市': ('12', '202'),
        '市川市': ('12', '203'),
        '船橋市': ('12', '204'),
        '館山市': ('12', '205'),
        '木更津市': ('12', '206'),
        '松戸市': ('12', '207'),
        '野田市': ('12', '208'),
        '茂原市': ('12', '209'),
        '成田市': ('12', '210'),
        '佐倉市': ('12', '211'),
        '東金市': ('12', '212'),
        '旭市': ('12', '213'),
        '習志野市': ('12', '214'),
        '柏市': ('12', '215'),
        '勝浦市': ('12', '216'),
        '市原市': ('12', '217'),
        '流山市': ('12', '218'),
        '八千代市': ('12', '219'),
        '我孫子市': ('12', '220'),
        '鴨川市': ('12', '221'),
        '鎌ケ谷市': ('12', '222'),
        '君津市': ('12', '223'),
        '富津市': ('12', '224'),
        '浦安市': ('12', '225'),
        '四街道市': ('12', '226'),
        '袖ケ浦市': ('12', '227'),
        '八街市': ('12', '228'),
        '印西市': ('12', '229'),
        '白井市': ('12', '230'),
        '富里市': ('12', '231'),
        '南房総市': ('12', '232'),
        '匝瑳市': ('12', '233'),
        '香取市': ('12', '234'),
        '山武市': ('12', '235'),
        'いすみ市': ('12', '236'),
        '大網白里市': ('12', '237'),
        # 東京都 (13)
        '千代田区': ('13', '101'),
        '中央区': ('13', '102'),
        '港区': ('13', '103'),
        '新宿区': ('13', '104'),
        '文京区': ('13', '105'),
        '台東区': ('13', '106'),
        '墨田区': ('13', '107'),
        '江東区': ('13', '108'),
        '品川区': ('13', '109'),
        '目黒区': ('13', '110'),
        '大田区': ('13', '111'),
        '世田谷区': ('13', '112'),
        '渋谷区': ('13', '113'),
        '中野区': ('13', '114'),
        '杉並区': ('13', '115'),
        '豊島区': ('13', '116'),
        '北区': ('13', '117'),
        '荒川区': ('13', '118'),
        '板橋区': ('13', '119'),
        '練馬区': ('13', '120'),
        '足立区': ('13', '121'),
        '葛飾区': ('13', '122'),
        '江戸川区': ('13', '123'),
        '八王子市': ('13', '201'),
        '立川市': ('13', '202'),
        '武蔵野市': ('13', '203'),
        '三鷹市': ('13', '204'),
        '青梅市': ('13', '205'),
        '府中市': ('13', '206'),
        '昭島市': ('13', '207'),
        '調布市': ('13', '208'),
        '町田市': ('13', '209'),
        '小金井市': ('13', '210'),
        '小平市': ('13', '211'),
        '日野市': ('13', '212'),
        '東村山市': ('13', '213'),
        '国分寺市': ('13', '214'),
        '国立市': ('13', '215'),
        '福生市': ('13', '218'),
        '狛江市': ('13', '219'),
        '東大和市': ('13', '220'),
        '清瀬市': ('13', '221'),
        '東久留米市': ('13', '222'),
        '武蔵村山市': ('13', '223'),
        '多摩市': ('13', '224'),
        '稲城市': ('13', '225'),
        '羽村市': ('13', '227'),
        'あきる野市': ('13', '228'),
        '西東京市': ('13', '229'),
        # 埼玉県 (11)
        'さいたま市': ('11', '100'),
        'さいたま市西区': ('11', '101'),
        'さいたま市北区': ('11', '102'),
        'さいたま市大宮区': ('11', '103'),
        'さいたま市見沼区': ('11', '104'),
        'さいたま市中央区': ('11', '105'),
        'さいたま市桜区': ('11', '106'),
        'さいたま市浦和区': ('11', '107'),
        'さいたま市南区': ('11', '108'),
        'さいたま市緑区': ('11', '109'),
        'さいたま市岩槻区': ('11', '110'),
        # 神奈川県 (14)
        '横浜市': ('14', '100'),
        '横浜市鶴見区': ('14', '101'),
        '横浜市神奈川区': ('14', '102'),
        '横浜市西区': ('14', '103'),
        '横浜市中区': ('14', '104'),
        '横浜市南区': ('14', '105'),
        '横浜市保土ケ谷区': ('14', '106'),
        '横浜市磯子区': ('14', '107'),
        '横浜市金沢区': ('14', '108'),
        '横浜市港北区': ('14', '109'),
        '横浜市戸塚区': ('14', '110'),
        '横浜市港南区': ('14', '111'),
        '横浜市旭区': ('14', '112'),
        '横浜市緑区': ('14', '113'),
        '横浜市瀬谷区': ('14', '114'),
        '横浜市栄区': ('14', '115'),
        '横浜市泉区': ('14', '116'),
        '横浜市青葉区': ('14', '117'),
        '横浜市都筑区': ('14', '118'),
    }
    
    # Try to find city in address and return codes
    # Sort by length (longest first) to match more specific names first
    for city_name in sorted(city_to_codes.keys(), key=len, reverse=True):
        if city_name in address:
            pref_code, city_code = city_to_codes[city_name]
            return pref_code, city_code
    
    return None, None


def fetch_land_price(pref_code: str, city_code: str, year: str = DEFAULT_YEAR) -> Optional[float]:
    """
    Fetch land price from Real Estate Information Library API
    
    Args:
        pref_code: Prefecture code (e.g., "12" for Chiba)
        city_code: City code (e.g., "207" for Matsudo)
        year: Year for land price data (default: 2023)
    
    Returns:
        Average land price in man-yen per m² (万円/m²), or None if data not available
    """
    # Get API key from environment variable
    api_key = os.environ.get('REINFOLIB_API_KEY')
    
    if not api_key:
        # API key not available - return None silently
        return None
    
    if not pref_code or not city_code:
        return None
    
    try:
        # Prepare API parameters
        params = {
            'key': api_key,
            'pref': pref_code,
            'city': city_code,
            'year': year
        }
        
        # Make API request
        response = requests.get(API_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Extract land price data
        # The API returns a list of land price points
        if not data or not isinstance(data, dict):
            return None
        
        # Get the data array from the response
        points = data.get('data', [])
        if not points or not isinstance(points, list):
            return None
        
        # Calculate average land price from all points
        prices = []
        for point in points:
            # Land price is usually in yen per m²
            price = point.get('currentYearPrice') or point.get('price')
            if price and isinstance(price, (int, float)):
                # Convert from yen to man-yen (万円)
                prices.append(price / 10000)
        
        if not prices:
            return None
        
        # Return average price
        avg_price = sum(prices) / len(prices)
        return round(avg_price, 2)
        
    except requests.RequestException:
        # Network error or API error - return None silently
        return None
    except (ValueError, KeyError):
        # JSON parsing error - return None silently
        return None


def calculate_ratio(unit_price: Optional[float], land_price: Optional[float]) -> Optional[str]:
    """
    Calculate ratio of property unit price to land price
    
    Args:
        unit_price: Property unit price in man-yen per m² (万円/m²)
        land_price: Reference land price in man-yen per m² (万円/m²)
    
    Returns:
        Ratio as a formatted string (e.g., "1.23x"), or None if calculation not possible
    """
    if unit_price is None or land_price is None or land_price == 0:
        return None
    
    ratio = unit_price / land_price
    return f"{ratio:.2f}x"


def get_land_price_info(address: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Get land price and related information for an address
    
    Args:
        address: Japanese address string
    
    Returns:
        Tuple of (land_price_value, formatted_string)
        - land_price_value: Land price in man-yen per m² (万円/m²)
        - formatted_string: Formatted string for display (e.g., "約25.5万円/m²")
    """
    # Parse address to get codes
    pref_code, city_code = parse_address(address)
    
    if not pref_code or not city_code:
        return None, None
    
    # Fetch land price from API
    land_price = fetch_land_price(pref_code, city_code)
    
    if land_price is None:
        return None, None
    
    # Format for display
    formatted = f"約{land_price:.2f}万円/m²"
    
    return land_price, formatted
