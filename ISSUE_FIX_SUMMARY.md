# Data Folder Issue Fix - Summary

## Issue Description

Files in `data/千葉県/柏市` (Kashiwa City, Chiba Prefecture) folder contained data from different cities.

## Root Cause Analysis

1. The SumStock scraper (`scripts/scrape_sumstock.py`) originally determined the folder location based on the city names found in the scraped property addresses, NOT from the URL city code.

2. When the URL code didn't match the actual data returned by the website, files got saved in folders that didn't match their URL reference.

3. Specific issues found:
   - URL code `12217` (市原市/Ichihara City) was used but returned data for 柏市 (Kashiwa City)
   - URL code `12220` (流山市/Nagareyama City) was used but files were placed in wrong folders

## Solution Implemented

### Phase 1: Fixed Existing Data (Initial Commits)

**Correct City Codes**

According to `scripts/location_mapping.py`:

| City Code | City Name (Japanese) | City Name (English) |
|-----------|---------------------|---------------------|
| 12203 | 市川市 | Ichikawa City |
| 12207 | 松戸市 | Matsudo City |
| 12215 | 柏市 | Kashiwa City |
| 12217 | 市原市 | Ichihara City |
| 12220 | 流山市 | Nagareyama City |

**Files Fixed**

Moved Files:
1. `data/千葉県/市原市/2025-10-19.md` → `data/千葉県/柏市/2025-10-19.md`
   - Had URL 12217 but contained 柏市 data
   
2. `data/千葉県/我孫子市/2025-10-19.md` → `data/千葉県/流山市/2025-10-19.md`
   - Had URL 12220 and contained 流山市 data
   
3. `data/千葉県/柏市/2025-12-01.md` → `data/千葉県/流山市/2025-12-01.md`
   - Had URL 12220 and contained 流山市 data
   
4. `data/その他/その他/2025-11-01.md` → `data/千葉県/流山市/2025-11-01.md`
   - Had URL 12220 but was in wrong folder (empty data)

Updated URLs in 柏市 files from code 12217 (incorrect) to 12215 (correct):
- `data/千葉県/柏市/2025-10-19.md`
- `data/千葉県/柏市/2025-10-22.md`
- `data/千葉県/柏市/2025-10-23.md`
- `data/千葉県/柏市/2025-11-01.md`

### Phase 2: Prevention (Latest Commit)

**Changed Scraper Behavior**: Implemented user feedback to ensure **URL code always determines folder location**.

**New Function**: `get_location_from_url(url)`
- Extracts prefecture and city codes directly from URL
- Returns location based on URL code, not scraped addresses
- Example: URL `12217` → Always saves to `data/千葉県/市原市/`

**Modified Main Logic**:
```python
# OLD: Used addresses from scraped data
if properties:
    first_location = properties[0].get('location', '')
    pref_name, city_name = get_location_from_api(first_location, api_client, url)

# NEW: Uses URL code directly
pref_name, city_name = get_location_from_url(url)
```

**Warning System**: If URL code doesn't match scraped addresses, logs a warning but saves to URL-determined folder:
```
Warning: URL code indicates '市原市' but scraped data contains '柏市' addresses. 
Saving to '市原市' folder based on URL.
```

## Validation

**Tests Created**:
1. `tests/test_data_folder_validation.py` - Validates folder location matches URL code and data
2. `tests/test_url_code_precedence.py` - Verifies URL code always determines folder

**Documentation**:
- `docs/city-codes.md` - City code reference table with updated behavior description
- All validation tests pass ✅

## Result

**Before**: Files saved based on scraped addresses → mismatches when URL doesn't match data

**After**: Files always saved based on URL code → consistent, predictable organization

All data files now correctly organized:
- ✅ 市川市: Code 12203, all files contain 市川市 data
- ✅ 松戸市: Code 12207, all files contain 松戸市 data
- ✅ 柏市: Code 12215, all files contain 柏市 data
- ✅ 流山市: Code 12220, all files contain 流山市 data

## Future Behavior

**URL code determines folder** - regardless of scraped data content:
- URL with code `12217` → Always saves to `data/千葉県/市原市/`
- URL with code `12215` → Always saves to `data/千葉県/柏市/`
- Prevents future mismatches between URL and folder location
