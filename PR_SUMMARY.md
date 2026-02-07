# Prefecture/Municipality Hierarchy Implementation

## Summary

This PR implements a hierarchical navigation structure for the sumstock website, organizing data by prefecture (都道府県) and municipality (市町村).

## Changes Made

### 1. Created Index Pages
- Added `index.md` for each prefecture directory (e.g., `data/千葉県/index.md`)
- Added `index.md` for each city/municipality directory (e.g., `data/千葉県/市川市/index.md`)
- These index pages establish the navigation hierarchy using Jekyll front matter

### 2. Updated Data File Front Matter
- Changed all date data files to use `parent: <city_name>` instead of `parent: データ一覧`
- Removed obsolete `categories` and `order` fields
- Removed unnecessary `nav_order` fields from data files
- This creates a proper 3-level hierarchy: データ一覧 > Prefecture > City > Date

### 3. Updated Scraper Script (`scripts/scrape_sumstock.py`)
- Modified `format_markdown()` to use simplified front matter with proper parent hierarchy
- Added `ensure_prefecture_index()` function to create prefecture index pages if they don't exist
- Added `ensure_city_index()` function to create city index pages if they don't exist
- Updated `save_markdown_file()` to call these functions before saving data files

### 4. Created Utility Script
- Added `scripts/generate_index_pages.py` to generate index pages for existing data directories
- Can be run manually to regenerate all index pages if needed

### 5. Added Documentation
- Created `docs/NAVIGATION_STRUCTURE.md` explaining the navigation hierarchy and how it works

## Navigation Structure

```
データ一覧 (Data Index)
└── 千葉県 (Chiba Prefecture)
    ├── 市原市 (Ichihara City)
    │   ├── 2025-12-27
    │   ├── 2026-01-01
    │   └── 2026-02-01
    ├── 市川市 (Ichikawa City)
    │   ├── 2025-10-19
    │   ├── 2025-10-22
    │   └── ...
    └── ... (other cities)
```

## Testing

The changes have been tested by:
1. Verifying all index pages are created with correct front matter
2. Verifying all data files have correct parent references
3. Testing the scraper functions to ensure index pages are created automatically
4. Checking that the hierarchy structure follows Just the Docs theme requirements

## Impact

- **User Experience**: Users can now navigate data by prefecture and city, making it easier to find specific regional data
- **Data Organization**: Data is logically organized in a clear hierarchy
- **Maintainability**: Future data additions will automatically be placed in the correct hierarchy
- **Backward Compatibility**: All existing data files remain in their current locations, only front matter was updated

## Files Changed

### New Files
- `data/千葉県/index.md`
- `data/千葉県/市原市/index.md`
- `data/千葉県/市川市/index.md`
- `data/千葉県/松戸市/index.md`
- `data/千葉県/柏市/index.md`
- `data/千葉県/流山市/index.md`
- `scripts/generate_index_pages.py`
- `docs/NAVIGATION_STRUCTURE.md`

### Modified Files
- `scripts/scrape_sumstock.py`
- All date data files in `data/千葉県/*/` (31 files) - front matter updated

## Next Steps

Once this PR is merged:
1. The Jekyll site will be rebuilt automatically via GitHub Actions
2. The navigation on https://zgvfrcgr.github.io/sumstock/data/ will show the new hierarchy
3. Future scraping runs will automatically create index pages for new prefectures/cities
