#!/usr/bin/env python3
"""
不動産情報ライブラリAPI 使用例

このスクリプトは、RealEstateInfoLibAPIクラスの使用例を示します。

実行方法:
    export REINFOLIB_API_KEY="your-api-key-here"
    python3 scripts/real_estate_api_example.py

または、APIキーを引数として渡す:
    python3 scripts/real_estate_api_example.py your-api-key-here
"""

import os
import sys
import json

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from real_estate_api import RealEstateInfoLibAPI


def example_get_transaction_price():
    """取引価格情報の取得例"""
    print("\n=== 不動産取引価格情報の取得例 ===")
    
    api_key = os.environ.get('REINFOLIB_API_KEY')
    if not api_key:
        print("注意: REINFOLIB_API_KEY環境変数が設定されていません")
        print("この例ではダミーキーを使用します（実際のAPIリクエストは失敗します）")
        api_key = "dummy-api-key"
    
    try:
        with RealEstateInfoLibAPI(api_key=api_key) as api:
            # 東京都（地域コード: 13）の2022年第1四半期の取引価格情報を取得
            data = api.get_transaction_price(
                year="2022",
                area="13",
                quarter="1"
            )
            
            print(f"取得した物件数: {len(data.get('features', []))}")
            
            # 最初の数件を表示
            for i, feature in enumerate(data.get('features', [])[:3]):
                print(f"\n物件 {i+1}:")
                properties = feature.get('properties', {})
                for key, value in properties.items():
                    print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"エラー: {e}")
        print("注意: 有効なAPIキーが必要です")


def example_get_land_price():
    """地価公示情報の取得例"""
    print("\n=== 地価公示情報の取得例 ===")
    
    api_key = os.environ.get('REINFOLIB_API_KEY')
    if not api_key:
        print("注意: REINFOLIB_API_KEY環境変数が設定されていません")
        api_key = "dummy-api-key"
    
    try:
        with RealEstateInfoLibAPI(api_key=api_key) as api:
            # 東京都（地域コード: 13）の2024年の地価公示情報を取得
            data = api.get_land_price(
                year="2024",
                area="13"
            )
            
            print(f"取得した地点数: {len(data.get('features', []))}")
            
            # 最初の数件を表示
            for i, feature in enumerate(data.get('features', [])[:3]):
                print(f"\n地点 {i+1}:")
                properties = feature.get('properties', {})
                for key, value in properties.items():
                    print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"エラー: {e}")
        print("注意: 有効なAPIキーが必要です")


def example_get_city_list():
    """市区町村一覧の取得例"""
    print("\n=== 都道府県内市区町村一覧の取得例 ===")
    
    api_key = os.environ.get('REINFOLIB_API_KEY')
    if not api_key:
        print("注意: REINFOLIB_API_KEY環境変数が設定されていません")
        api_key = "dummy-api-key"
    
    try:
        with RealEstateInfoLibAPI(api_key=api_key) as api:
            # 東京都（地域コード: 13）の市区町村一覧を取得
            data = api.get_city_list(prefecture_code="13")
            
            print(f"取得した市区町村数: {len(data.get('cities', []))}")
            
            # 最初の10件を表示
            for city in data.get('cities', [])[:10]:
                print(f"  {city.get('code')}: {city.get('name')}")
    
    except Exception as e:
        print(f"エラー: {e}")
        print("注意: 有効なAPIキーが必要です")


def example_error_handling():
    """エラーハンドリングの例"""
    print("\n=== エラーハンドリングの例 ===")
    
    from real_estate_api import (
        RealEstateInfoLibAPIError,
        RealEstateInfoLibAPIAuthError,
        RealEstateInfoLibAPIRateLimitError
    )
    
    try:
        # 無効なAPIキーで初期化（空文字列）
        api = RealEstateInfoLibAPI(api_key="")
    except ValueError as e:
        print(f"初期化エラー: {e}")
    
    try:
        # 無効なAPIキーでリクエスト
        with RealEstateInfoLibAPI(api_key="invalid-key") as api:
            data = api.get_transaction_price(year="2022", area="13")
    except RealEstateInfoLibAPIAuthError as e:
        print(f"認証エラー: {e}")
    except RealEstateInfoLibAPIRateLimitError as e:
        print(f"レート制限エラー: {e}")
    except RealEstateInfoLibAPIError as e:
        print(f"APIエラー: {e}")


def example_save_to_file():
    """取得したデータをファイルに保存する例"""
    print("\n=== データのファイル保存例 ===")
    
    api_key = os.environ.get('REINFOLIB_API_KEY')
    if not api_key:
        print("注意: REINFOLIB_API_KEY環境変数が設定されていません")
        print("この例をスキップします")
        return
    
    try:
        with RealEstateInfoLibAPI(api_key=api_key) as api:
            # 東京都の2024年地価公示情報を取得
            data = api.get_land_price(year="2024", area="13")
            
            # GeoJSON形式で保存
            output_file = "/tmp/land_price_tokyo_2024.geojson"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"データを保存しました: {output_file}")
            print(f"ファイルサイズ: {os.path.getsize(output_file)} バイト")
    
    except Exception as e:
        print(f"エラー: {e}")


def main():
    """メイン関数"""
    print("=" * 60)
    print("不動産情報ライブラリAPI 使用例")
    print("=" * 60)
    
    # コマンドライン引数からAPIキーを取得
    if len(sys.argv) > 1:
        os.environ['REINFOLIB_API_KEY'] = sys.argv[1]
        print(f"\nAPIキーが設定されました（コマンドライン引数から）")
    elif os.environ.get('REINFOLIB_API_KEY'):
        print(f"\nAPIキーが設定されています（環境変数から）")
    else:
        print("\n警告: APIキーが設定されていません")
        print("使用方法:")
        print("  export REINFOLIB_API_KEY='your-api-key'")
        print("  python3 scripts/real_estate_api_example.py")
        print("または:")
        print("  python3 scripts/real_estate_api_example.py 'your-api-key'")
        print("\nAPIキーなしでデモを続行します（エラーが発生します）\n")
    
    # 各例を実行
    example_get_transaction_price()
    example_get_land_price()
    example_get_city_list()
    example_error_handling()
    example_save_to_file()
    
    print("\n" + "=" * 60)
    print("全ての例を実行しました")
    print("=" * 60)


if __name__ == '__main__':
    main()
