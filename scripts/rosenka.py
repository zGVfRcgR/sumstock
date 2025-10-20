#!/usr/bin/env python3
"""
Rosenka (route price) lookup module
Provides geocoding and rosenka value lookup functionality
"""

import os
import csv
from typing import Optional, Tuple, Dict
import re


# Mock geocoding data for common locations (in real implementation, use Nominatim or Google Maps API)
MOCK_GEOCODING = {
    '松戸市中金杉1丁目': (35.7873, 139.9026),
    '松戸市小金原2丁目': (35.7991, 139.9486),
    '柏市': (35.8677, 139.9750),
    '市川市': (35.7226, 139.9306),
}


def load_rosenka_data(csv_path: str = None) -> Dict[str, float]:
    """
    Load rosenka data from CSV file
    
    Args:
        csv_path: Path to rosenka CSV file. If None, uses default path.
    
    Returns:
        Dictionary mapping location keys to rosenka values (万円/m²)
    """
    if csv_path is None:
        # Default path relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, '..', 'data', 'rosenka', 'rosenka_data.csv')
    
    rosenka_data = {}
    
    if not os.path.exists(csv_path):
        # Return empty dict if file doesn't exist (will use mock data)
        return rosenka_data
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Expected columns: location, lat, lon, rosenka_value
                location = row.get('location', '').strip()
                rosenka_value = row.get('rosenka_value', '').strip()
                
                if location and rosenka_value:
                    try:
                        rosenka_data[location] = float(rosenka_value)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Warning: Could not load rosenka data from {csv_path}: {e}")
    
    return rosenka_data


def geocode(address: str) -> Optional[Tuple[float, float]]:
    """
    Convert address to (latitude, longitude) coordinates
    
    In production, this would use a geocoding service like:
    - Nominatim (OpenStreetMap)
    - Google Geocoding API
    - 国土地理院 API
    
    For now, uses mock data for testing purposes.
    
    Args:
        address: Address string (e.g., "松戸市中金杉1丁目")
    
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    # Try exact match first
    if address in MOCK_GEOCODING:
        return MOCK_GEOCODING[address]
    
    # Try partial matching for city names
    for known_address, coords in MOCK_GEOCODING.items():
        if known_address in address or address in known_address:
            return coords
    
    return None


def normalize_location(location: str) -> str:
    """
    Normalize location string for matching
    Extracts city/town name from full address
    
    Args:
        location: Full location string (e.g., "松戸市中金杉1丁目")
    
    Returns:
        Normalized location string
    """
    # Remove extra whitespace
    location = location.strip()
    
    # Extract city name (市区町村)
    # Pattern: XXX市/区/町/村 followed by optional area name
    match = re.search(r'([^都道府県]+?[市区町村])', location)
    if match:
        return match.group(1)
    
    return location


def find_rosenka(address: str, rosenka_data: Dict[str, float] = None) -> Optional[float]:
    """
    Find rosenka value for a given address
    
    Args:
        address: Address string (e.g., "松戸市中金杉1丁目")
        rosenka_data: Optional dictionary of rosenka data. If None, loads from default path.
    
    Returns:
        Rosenka value in 万円/m² or None if not found
    """
    if rosenka_data is None:
        rosenka_data = load_rosenka_data()
    
    # Try exact match first
    if address in rosenka_data:
        return rosenka_data[address]
    
    # Try normalized location matching
    normalized = normalize_location(address)
    if normalized in rosenka_data:
        return rosenka_data[normalized]
    
    # Try partial matching
    for location, value in rosenka_data.items():
        if location in address or address in location:
            return value
    
    # If no data file exists, use mock data based on city
    # Mock rosenka values (example values in 万円/m²)
    mock_rosenka = {
        '松戸市': 12.5,
        '柏市': 15.0,
        '市川市': 18.0,
        '船橋市': 20.0,
    }
    
    # Try to find city in address
    for city, value in mock_rosenka.items():
        if city in address:
            return value
    
    return None


def get_rosenka_for_property(location: str) -> Optional[float]:
    """
    Main function to get rosenka value for a property location
    
    This is the main entry point for the scraper to use.
    
    Args:
        location: Property location string
    
    Returns:
        Rosenka value in 万円/m² or None if not found
    """
    # Load rosenka data once
    rosenka_data = load_rosenka_data()
    
    # Find rosenka value
    return find_rosenka(location, rosenka_data)


def calculate_rosenka_ratio(building_unit_price_str: str, rosenka_value: Optional[float]) -> Optional[float]:
    """
    Calculate ratio of building unit price to rosenka
    
    Args:
        building_unit_price_str: Building unit price string (e.g., "約6.96万円/m²")
        rosenka_value: Rosenka value in 万円/m²
    
    Returns:
        Ratio (building_unit_price / rosenka) or None if calculation not possible
    """
    if not building_unit_price_str or building_unit_price_str == '-':
        return None
    
    if rosenka_value is None or rosenka_value == 0:
        return None
    
    # Extract numeric value from building unit price string
    # Expected format: "約6.96万円/m²" or similar
    match = re.search(r'([0-9.]+)', building_unit_price_str)
    if not match:
        return None
    
    try:
        building_unit_price = float(match.group(1))
        ratio = building_unit_price / rosenka_value
        return ratio
    except (ValueError, ZeroDivisionError):
        return None
