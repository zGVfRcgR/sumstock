# Tests

This directory contains tests for the SumStock scraper.

## Test Files

### `test_scraper_with_mock.py`
Unit tests for basic selector functionality using mock HTML. Tests that:
- SumStock-specific selectors can find property elements (`div.bukkenUnitBox`)
- Location extraction from `h5.bukkenName` works
- Price extraction from `span.bold` elements works

### `test_scraper_integration.py`
Integration tests that verify the full scraping pipeline with mock HTML. Tests that:
- The `scrape_property_data()` function correctly extracts all property data
- Property locations, prices, areas, and maker information are extracted properly
- The scraper returns the expected number of properties

## Running Tests

Run individual tests:
```bash
python tests/test_scraper_with_mock.py
python tests/test_scraper_integration.py
```

Or run all tests:
```bash
python -m pytest tests/
```

## Mock Data

The tests use mock HTML that reflects the actual structure of SumStock.jp pages:
- Properties are in `<div class="bukkenUnitBox">` elements
- Locations are in `<h5 class="bukkenName">` elements
- Prices are in `<span class="bold">` elements
- Areas are in `<span class="value">` elements within `.area` divs
