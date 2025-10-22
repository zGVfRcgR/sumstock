#!/usr/bin/env python3
"""
Test script for Real Estate Information Library API client
"""

import sys
import os
import json
import gzip
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.real_estate_api import (
    RealEstateInfoLibAPI,
    RealEstateInfoLibAPIError,
    RealEstateInfoLibAPIAuthError,
    RealEstateInfoLibAPIRateLimitError
)


# モックレスポンスデータ
MOCK_TRANSACTION_PRICE_RESPONSE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [139.6917, 35.6895]
            },
            "properties": {
                "取引価格": 50000000,
                "面積": 100.0,
                "取引時期": "2022年第1四半期"
            }
        }
    ]
}

MOCK_LAND_PRICE_RESPONSE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [139.6917, 35.6895]
            },
            "properties": {
                "標準地番号": "東京-1",
                "価格": 500000,
                "調査年": "2024"
            }
        }
    ]
}

MOCK_CITY_LIST_RESPONSE = {
    "cities": [
        {"code": "13101", "name": "千代田区"},
        {"code": "13102", "name": "中央区"},
        {"code": "13103", "name": "港区"}
    ]
}


def test_api_initialization():
    """Test API initialization"""
    # 正常な初期化
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    assert api.api_key == "test-api-key"
    assert api.timeout == 30  # デフォルトタイムアウト
    print("✓ Test passed: API initialization with valid key")
    
    # カスタムタイムアウト
    api = RealEstateInfoLibAPI(api_key="test-api-key", timeout=60)
    assert api.timeout == 60
    print("✓ Test passed: API initialization with custom timeout")


def test_api_initialization_without_key():
    """Test API initialization without API key"""
    try:
        api = RealEstateInfoLibAPI(api_key="")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "APIキー" in str(e)
        print("✓ Test passed: API initialization fails without key")


def test_context_manager():
    """Test context manager support"""
    with RealEstateInfoLibAPI(api_key="test-api-key") as api:
        assert api.api_key == "test-api-key"
    print("✓ Test passed: Context manager support")


@patch('scripts.real_estate_api.requests.Session.get')
def test_get_transaction_price_success(mock_get):
    """Test successful transaction price retrieval"""
    # モックレスポンスを設定
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.json.return_value = MOCK_TRANSACTION_PRICE_RESPONSE
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    result = api.get_transaction_price(year="2022", area="13")
    
    assert result == MOCK_TRANSACTION_PRICE_RESPONSE
    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) > 0
    
    # リクエストが正しく呼ばれたか確認
    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["params"]["year"] == "2022"
    assert call_kwargs["params"]["area"] == "13"
    
    print("✓ Test passed: Get transaction price success")


@patch('scripts.real_estate_api.requests.Session.get')
def test_get_transaction_price_with_quarter(mock_get):
    """Test transaction price retrieval with quarter parameter"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.json.return_value = MOCK_TRANSACTION_PRICE_RESPONSE
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    result = api.get_transaction_price(year="2022", area="13", quarter="1")
    
    # リクエストパラメータに四半期が含まれているか確認
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["params"]["quarter"] == "1"
    
    print("✓ Test passed: Get transaction price with quarter")


@patch('scripts.real_estate_api.requests.Session.get')
def test_get_land_price_success(mock_get):
    """Test successful land price retrieval"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.json.return_value = MOCK_LAND_PRICE_RESPONSE
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    result = api.get_land_price(year="2024", area="13")
    
    assert result == MOCK_LAND_PRICE_RESPONSE
    assert result["type"] == "FeatureCollection"
    
    # リクエストパラメータの確認
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["params"]["year"] == "2024"
    assert call_kwargs["params"]["area"] == "13"
    
    print("✓ Test passed: Get land price success")


@patch('scripts.real_estate_api.requests.Session.get')
def test_get_city_list_success(mock_get):
    """Test successful city list retrieval"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.json.return_value = MOCK_CITY_LIST_RESPONSE
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    result = api.get_city_list(prefecture_code="13")
    
    assert result == MOCK_CITY_LIST_RESPONSE
    assert "cities" in result
    assert len(result["cities"]) == 3
    
    print("✓ Test passed: Get city list success")


@patch('scripts.real_estate_api.requests.Session.get')
def test_gzip_response_handling(mock_get):
    """Test gzip compressed response handling"""
    # gzip圧縮されたレスポンスを作成
    json_data = json.dumps(MOCK_TRANSACTION_PRICE_RESPONSE).encode('utf-8')
    compressed_data = gzip.compress(json_data)
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {'Content-Encoding': 'gzip'}
    mock_response.content = compressed_data
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    result = api.get_transaction_price(year="2022", area="13")
    
    assert result == MOCK_TRANSACTION_PRICE_RESPONSE
    
    print("✓ Test passed: Gzip response handling")


@patch('scripts.real_estate_api.requests.Session.get')
def test_auth_error_handling(mock_get):
    """Test authentication error handling"""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="invalid-key")
    
    try:
        result = api.get_transaction_price(year="2022", area="13")
        assert False, "Should raise RealEstateInfoLibAPIAuthError"
    except RealEstateInfoLibAPIAuthError as e:
        assert "認証" in str(e)
        print("✓ Test passed: Auth error handling")


@patch('scripts.real_estate_api.requests.Session.get')
def test_rate_limit_error_handling(mock_get):
    """Test rate limit error handling"""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    
    try:
        result = api.get_transaction_price(year="2022", area="13")
        assert False, "Should raise RealEstateInfoLibAPIRateLimitError"
    except RealEstateInfoLibAPIRateLimitError as e:
        assert "レート制限" in str(e)
        print("✓ Test passed: Rate limit error handling")


@patch('scripts.real_estate_api.requests.Session.get')
def test_general_http_error_handling(mock_get):
    """Test general HTTP error handling"""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    
    try:
        result = api.get_transaction_price(year="2022", area="13")
        assert False, "Should raise RealEstateInfoLibAPIError"
    except RealEstateInfoLibAPIError as e:
        assert "500" in str(e)
        print("✓ Test passed: General HTTP error handling")


@patch('scripts.real_estate_api.requests.Session.get')
def test_timeout_error_handling(mock_get):
    """Test timeout error handling"""
    import requests
    mock_get.side_effect = requests.exceptions.Timeout()
    
    api = RealEstateInfoLibAPI(api_key="test-api-key", timeout=5)
    
    try:
        result = api.get_transaction_price(year="2022", area="13")
        assert False, "Should raise RealEstateInfoLibAPIError"
    except RealEstateInfoLibAPIError as e:
        assert "タイムアウト" in str(e)
        print("✓ Test passed: Timeout error handling")


@patch('scripts.real_estate_api.requests.Session.get')
def test_network_error_handling(mock_get):
    """Test network error handling"""
    import requests
    mock_get.side_effect = requests.exceptions.RequestException("Network error")
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    
    try:
        result = api.get_transaction_price(year="2022", area="13")
        assert False, "Should raise RealEstateInfoLibAPIError"
    except RealEstateInfoLibAPIError as e:
        assert "ネットワークエラー" in str(e)
        print("✓ Test passed: Network error handling")


@patch('scripts.real_estate_api.requests.Session.get')
def test_api_headers_configuration(mock_get):
    """Test API request headers configuration"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.json.return_value = MOCK_TRANSACTION_PRICE_RESPONSE
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="my-secret-key")
    result = api.get_transaction_price(year="2022", area="13")
    
    # ヘッダーが正しく設定されているか確認
    call_kwargs = mock_get.call_args.kwargs
    headers = call_kwargs["headers"]
    assert headers["Ocp-Apim-Subscription-Key"] == "my-secret-key"
    assert headers["Accept-Encoding"] == "gzip"
    
    print("✓ Test passed: API headers configuration")


@patch('scripts.real_estate_api.requests.Session.get')
def test_get_appraisal_report_success(mock_get):
    """Test successful appraisal report retrieval"""
    mock_response_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "鑑定評価額": 1000000,
                    "評価年": "2024"
                }
            }
        ]
    }
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.json.return_value = mock_response_data
    mock_get.return_value = mock_response
    
    api = RealEstateInfoLibAPI(api_key="test-api-key")
    result = api.get_appraisal_report(year="2024", area="13", division="01")
    
    assert result == mock_response_data
    
    # パラメータの確認
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["params"]["year"] == "2024"
    assert call_kwargs["params"]["area"] == "13"
    assert call_kwargs["params"]["division"] == "01"
    
    print("✓ Test passed: Get appraisal report success")


if __name__ == '__main__':
    print("Running Real Estate Information Library API tests...\n")
    
    # 初期化テスト
    test_api_initialization()
    test_api_initialization_without_key()
    test_context_manager()
    
    # APIメソッドテスト
    test_get_transaction_price_success()
    test_get_transaction_price_with_quarter()
    test_get_land_price_success()
    test_get_city_list_success()
    test_get_appraisal_report_success()
    
    # エラーハンドリングテスト
    test_gzip_response_handling()
    test_auth_error_handling()
    test_rate_limit_error_handling()
    test_general_http_error_handling()
    test_timeout_error_handling()
    test_network_error_handling()
    
    # その他の機能テスト
    test_api_headers_configuration()
    
    print("\n✓ All Real Estate Information Library API tests passed!")
