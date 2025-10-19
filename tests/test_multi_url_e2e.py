#!/usr/bin/env python3
"""
End-to-end test for multi-URL processing
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.scrape_sumstock import scrape_property_data, format_markdown, save_markdown_file

# Mock HTML for two different locations
MOCK_HTML_LOCATION_1 = """
<html>
<body>
<article class="bukkenListWrap">
    <div class="bukkenUnitBox">
        <h5 class="bukkenName">松戸市中金杉1丁目</h5>
        <div class="price">
            <span class="bold">3,280<small>万円</small></span>
        </div>
    </div>
</article>
</body>
</html>
"""

MOCK_HTML_LOCATION_2 = """
<html>
<body>
<article class="bukkenListWrap">
    <div class="bukkenUnitBox">
        <h5 class="bukkenName">柏市光ヶ丘2丁目</h5>
        <div class="price">
            <span class="bold">2,500<small>万円</small></span>
        </div>
    </div>
</article>
</body>
</html>
"""


def test_multiple_url_file_generation():
    """Test that multiple URLs generate separate files with correct naming"""
    print("Testing multi-URL file generation...\n")
    
    # Create temporary directory for test output
    temp_dir = tempfile.mkdtemp(prefix='sumstock_test_')
    
    try:
        # Mock responses for different URLs
        def mock_get(url, **kwargs):
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            
            if '12207' in url:
                mock_response.content = MOCK_HTML_LOCATION_1.encode('utf-8')
            elif '12208' in url:
                mock_response.content = MOCK_HTML_LOCATION_2.encode('utf-8')
            else:
                mock_response.content = b"<html><body></body></html>"
            
            return mock_response
        
        urls = [
            "https://sumstock.jp/search/02/12/12207",
            "https://sumstock.jp/search/02/12/12208"
        ]
        
        current_date = datetime.now()
        filepaths = []
        
        with patch('requests.get', side_effect=mock_get):
            for i, url in enumerate(urls, start=1):
                print(f"Processing URL {i}: {url}")
                
                # Scrape data
                properties = scrape_property_data(url)
                print(f"  Found {len(properties)} properties")
                
                # Format as Markdown
                markdown = format_markdown(properties, url, current_date)
                
                # Save with suffix
                suffix = f"_{i}" if len(urls) > 1 else ""
                filepath = save_markdown_file(markdown, current_date, output_dir=temp_dir, suffix=suffix)
                filepaths.append(filepath)
                print(f"  Saved to: {filepath}")
        
        # Verify files were created
        assert len(filepaths) == 2, f"Expected 2 files, got {len(filepaths)}"
        
        # Verify file names
        expected_filename_1 = current_date.strftime('%Y-%m-%d') + '_1.md'
        expected_filename_2 = current_date.strftime('%Y-%m-%d') + '_2.md'
        
        assert expected_filename_1 in filepaths[0], f"Expected {expected_filename_1} in {filepaths[0]}"
        assert expected_filename_2 in filepaths[1], f"Expected {expected_filename_2} in {filepaths[1]}"
        
        # Verify files exist and contain expected content
        for i, filepath in enumerate(filepaths, start=1):
            assert os.path.exists(filepath), f"File {filepath} does not exist"
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check that the file contains the correct URL
            expected_url = urls[i-1]
            assert expected_url in content, f"Expected {expected_url} in file {i}"
            
            print(f"\n✓ File {i} verified:")
            print(f"  Path: {filepath}")
            print(f"  Size: {len(content)} bytes")
            print(f"  Contains URL: {expected_url}")
        
        print("\n✓ All multi-URL file generation tests passed!")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up test directory: {temp_dir}")


def test_single_url_no_suffix():
    """Test that single URL doesn't add suffix to filename"""
    print("\nTesting single URL file generation (no suffix)...\n")
    
    temp_dir = tempfile.mkdtemp(prefix='sumstock_test_single_')
    
    try:
        mock_response = MagicMock()
        mock_response.content = MOCK_HTML_LOCATION_1.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        
        url = "https://sumstock.jp/search/02/12/12207"
        current_date = datetime.now()
        
        with patch('requests.get', return_value=mock_response):
            properties = scrape_property_data(url)
            markdown = format_markdown(properties, url, current_date)
            
            # Single URL - no suffix
            filepath = save_markdown_file(markdown, current_date, output_dir=temp_dir, suffix="")
            
            # Verify filename has NO suffix
            expected_filename = current_date.strftime('%Y-%m-%d') + '.md'
            assert expected_filename in filepath, f"Expected {expected_filename} in {filepath}"
            assert os.path.exists(filepath), f"File {filepath} does not exist"
            
            print(f"✓ Single URL file verified:")
            print(f"  Path: {filepath}")
            print(f"  Filename (no suffix): {expected_filename}")
        
        print("\n✓ Single URL test passed!")
        
    finally:
        shutil.rmtree(temp_dir)
        print(f"Cleaned up test directory: {temp_dir}")


if __name__ == '__main__':
    print("=" * 70)
    print("Running end-to-end multi-URL tests")
    print("=" * 70)
    
    test_multiple_url_file_generation()
    test_single_url_no_suffix()
    
    print("\n" + "=" * 70)
    print("✓ All end-to-end tests passed!")
    print("=" * 70)
