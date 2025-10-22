#!/usr/bin/env python3
"""
Real Estate Information Library API Client
不動産情報ライブラリAPI クライアント

国土交通省の不動産情報ライブラリAPI (https://www.reinfolib.mlit.go.jp/) を利用するためのPythonクラス

公式APIマニュアル: https://www.reinfolib.mlit.go.jp/help/apiManual/
"""

import json
import gzip
from typing import Dict, List, Optional, Any
import requests


class RealEstateInfoLibAPIError(Exception):
    """不動産情報ライブラリAPIのエラー基底クラス"""
    pass


class RealEstateInfoLibAPIAuthError(RealEstateInfoLibAPIError):
    """API認証エラー"""
    pass


class RealEstateInfoLibAPIRateLimitError(RealEstateInfoLibAPIError):
    """APIレート制限エラー"""
    pass


class RealEstateInfoLibAPI:
    """
    不動産情報ライブラリAPI クライアントクラス
    
    このクラスは国土交通省の不動産情報ライブラリAPIへのアクセスを提供します。
    
    使用例:
        >>> api = RealEstateInfoLibAPI(api_key="your-api-key")
        >>> # 不動産取引価格情報を取得
        >>> data = api.get_transaction_price(year="2022", area="13")
        >>> # 地価公示情報を取得
        >>> data = api.get_land_price(year="2024", area="13")
    
    APIドキュメント:
        https://www.reinfolib.mlit.go.jp/help/apiManual/
    """
    
    # APIベースURL
    BASE_URL = "https://www.reinfolib.mlit.go.jp/ex-api/external/"
    
    # API種類コード
    API_TYPES = {
        "transaction_price": "XIT001",  # 不動産価格（取引価格・成約価格）情報取得API
        "land_price": "XIT002",  # 地価公示・都道府県地価調査情報取得API
        "city_list": "XIT003",  # 都道府県内市区町村一覧取得API
        "appraisal_report": "XIT004",  # 鑑定評価書情報API
        "point_data": "XPT002",  # 地価公示・地価調査のポイント（点）API
    }
    
    def __init__(self, api_key: str, timeout: int = 30):
        """
        RealEstateInfoLibAPIクライアントを初期化
        
        Args:
            api_key: APIキー（国土交通省から発行されたもの）
            timeout: リクエストのタイムアウト秒数（デフォルト: 30秒）
        
        Raises:
            ValueError: api_keyが空の場合
        """
        if not api_key or not api_key.strip():
            raise ValueError("APIキーが必要です")
        
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
    
    def _make_request(
        self,
        api_type: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        APIリクエストを実行
        
        Args:
            api_type: API種類コード（例: "XIT001"）
            params: リクエストパラメータ
        
        Returns:
            APIレスポンスのJSONデータ
        
        Raises:
            RealEstateInfoLibAPIAuthError: 認証エラー
            RealEstateInfoLibAPIRateLimitError: レート制限エラー
            RealEstateInfoLibAPIError: その他のAPIエラー
        """
        url = f"{self.BASE_URL}{api_type}"
        
        # リクエストヘッダー設定
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Accept-Encoding": "gzip",
        }
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params or {},
                timeout=self.timeout
            )
            
            # ステータスコードに応じたエラーハンドリング
            if response.status_code == 401:
                raise RealEstateInfoLibAPIAuthError(
                    "API認証に失敗しました。APIキーを確認してください。"
                )
            elif response.status_code == 429:
                raise RealEstateInfoLibAPIRateLimitError(
                    "APIレート制限に達しました。しばらく待ってから再試行してください。"
                )
            elif response.status_code != 200:
                raise RealEstateInfoLibAPIError(
                    f"APIリクエストが失敗しました。ステータスコード: {response.status_code}"
                )
            
            # gzipレスポンスの処理
            if response.headers.get('Content-Encoding') == 'gzip':
                try:
                    decoded_data = gzip.decompress(response.content)
                    return json.loads(decoded_data)
                except Exception as e:
                    raise RealEstateInfoLibAPIError(
                        f"gzipレスポンスのデコードに失敗しました: {e}"
                    )
            else:
                return response.json()
        
        except requests.exceptions.Timeout:
            raise RealEstateInfoLibAPIError(
                f"リクエストがタイムアウトしました（{self.timeout}秒）"
            )
        except requests.exceptions.RequestException as e:
            raise RealEstateInfoLibAPIError(
                f"ネットワークエラーが発生しました: {e}"
            )
    
    def get_transaction_price(
        self,
        year: str,
        area: str,
        quarter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        不動産取引価格情報を取得
        
        Args:
            year: 取得年（例: "2022"）
            area: 地域コード（例: "13" = 東京都）
            quarter: 四半期（オプション、例: "1", "2", "3", "4"）
        
        Returns:
            不動産取引価格情報のJSONデータ（GeoJSON形式）
        
        例:
            >>> api = RealEstateInfoLibAPI(api_key="your-key")
            >>> data = api.get_transaction_price(year="2022", area="13")
        """
        params = {
            "year": year,
            "area": area,
        }
        
        if quarter:
            params["quarter"] = quarter
        
        return self._make_request(self.API_TYPES["transaction_price"], params)
    
    def get_land_price(
        self,
        year: str,
        area: str
    ) -> Dict[str, Any]:
        """
        地価公示・都道府県地価調査情報を取得
        
        Args:
            year: 取得年（例: "2024"）
            area: 地域コード（例: "13" = 東京都）
        
        Returns:
            地価公示情報のJSONデータ（GeoJSON形式）
        
        例:
            >>> api = RealEstateInfoLibAPI(api_key="your-key")
            >>> data = api.get_land_price(year="2024", area="13")
        """
        params = {
            "year": year,
            "area": area,
        }
        
        return self._make_request(self.API_TYPES["land_price"], params)
    
    def get_city_list(self, prefecture_code: str) -> Dict[str, Any]:
        """
        都道府県内市区町村一覧を取得
        
        Args:
            prefecture_code: 都道府県コード（例: "13" = 東京都）
        
        Returns:
            市区町村一覧のJSONデータ
        
        例:
            >>> api = RealEstateInfoLibAPI(api_key="your-key")
            >>> cities = api.get_city_list(prefecture_code="13")
        """
        params = {
            "area": prefecture_code,
        }
        
        return self._make_request(self.API_TYPES["city_list"], params)
    
    def get_appraisal_report(
        self,
        year: str,
        area: str,
        division: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        鑑定評価書情報を取得
        
        Args:
            year: 取得年（例: "2024"）
            area: 地域コード（例: "13" = 東京都）
            division: 用途区分（オプション）
        
        Returns:
            鑑定評価書情報のJSONデータ
        
        例:
            >>> api = RealEstateInfoLibAPI(api_key="your-key")
            >>> data = api.get_appraisal_report(year="2024", area="13")
        """
        params = {
            "year": year,
            "area": area,
        }
        
        if division:
            params["division"] = division
        
        return self._make_request(self.API_TYPES["appraisal_report"], params)
    
    def get_point_data(
        self,
        response_format: str,
        z: int,
        x: int,
        y: int,
        year: str,
        priceClassification: Optional[str] = None,
        useCategoryCode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        地価公示・地価調査のポイント（点）データを取得
        
        Args:
            response_format: 応答形式 ("geojson" or "pbf")
            z: ズームレベル（縮尺）
            x: タイル座標のX値
            y: タイル座標のY値
            year: 対象年（例: "2024"）
            priceClassification: 地価情報区分コード（オプション、"0" or "1"）
            useCategoryCode: 用途区分コード（オプション、例: "00,03,05"）
        
        Returns:
            地価ポイントデータのJSONデータ（GeoJSON形式）
        
        例:
            >>> api = RealEstateInfoLibAPI(api_key="your-key")
            >>> data = api.get_point_data("geojson", 13, 7312, 3008, "2024")
        """
        params = {
            "response_format": response_format,
            "z": z,
            "x": x,
            "y": y,
            "year": year,
        }
        
        if priceClassification:
            params["priceClassification"] = priceClassification
        
        if useCategoryCode:
            params["useCategoryCode"] = useCategoryCode
        
        return self._make_request(self.API_TYPES["point_data"], params)
    
    def close(self):
        """
        セッションをクローズ
        """
        self.session.close()
    
    def __enter__(self):
        """コンテキストマネージャー対応（with文で使用可能）"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー対応（with文で使用可能）"""
        self.close()


if __name__ == "__main__":
    import os
    
    # APIキーを環境変数から取得
    api_key = os.getenv("REINFOLIB_API_KEY")
    if not api_key:
        print("エラー: REINFOLIB_API_KEY環境変数が設定されていません。")
        exit(1)
    
    # APIクライアントを初期化
    api = RealEstateInfoLibAPI(api_key)
    
    try:
        # 地価公示・地価調査のポイントデータを取得（東京駅周辺の例）
        # ズームレベル13, タイル座標は東京駅周辺の例
        data = api.get_point_data(
            response_format="geojson",
            z=13,
            x=7312,
            y=3008,
            year="2024"
        )
        
        print("APIレスポンス:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
    except RealEstateInfoLibAPIError as e:
        print(f"APIエラー: {e}")
    except Exception as e:
        print(f"予期せぬエラー: {e}")
    finally:
        api.close()
