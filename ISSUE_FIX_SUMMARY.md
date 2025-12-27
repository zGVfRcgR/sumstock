# Data Folder Issue Fix - Summary

## Issue Description

Files in `data/千葉県/柏市` (Kashiwa City, Chiba Prefecture) folder contained data from different cities.

## Root Cause Analysis

1. The SumStock scraper (`scripts/scrape_sumstock.py`) determines the folder location based on the city names found in the scraped property addresses, NOT from the URL city code.

2. When the URL code doesn't match the actual data returned by the website, files get saved in folders that don't match their URL reference.

3. Specific issues found:
   - URL code `12217` (市原市/Ichihara City) was used but returned data for 柏市 (Kashiwa City)
   - URL code `12220` (流山市/Nagareyama City) was used but files were placed in wrong folders

## Correct City Codes

According to `scripts/location_mapping.py`:

| City Code | City Name (Japanese) | City Name (English) |
|-----------|---------------------|---------------------|
| 12203 | 市川市 | Ichikawa City |
| 12207 | 松戸市 | Matsudo City |
| 12215 | 柏市 | Kashiwa City |
| 12217 | 市原市 | Ichihara City |
| 12220 | 流山市 | Nagareyama City |

## Files Fixed

### Moved Files
1. `data/千葉県/市原市/2025-10-19.md` → `data/千葉県/柏市/2025-10-19.md`
   - Had URL 12217 but contained 柏市 data
   
2. `data/千葉県/我孫子市/2025-10-19.md` → `data/千葉県/流山市/2025-10-19.md`
   - Had URL 12220 and contained 流山市 data
   
3. `data/千葉県/柏市/2025-12-01.md` → `data/千葉県/流山市/2025-12-01.md`
   - Had URL 12220 and contained 流山市 data
   
4. `data/その他/その他/2025-11-01.md` → `data/千葉県/流山市/2025-11-01.md`
   - Had URL 12220 but was in wrong folder (empty data)

### Updated URLs
Updated URL references in 柏市 files from code 12217 (incorrect) to 12215 (correct):
- `data/千葉県/柏市/2025-10-19.md`
- `data/千葉県/柏市/2025-10-22.md`
- `data/千葉県/柏市/2025-10-23.md`
- `data/千葉県/柏市/2025-11-01.md`

## Validation

Created `tests/test_data_folder_validation.py` to automatically validate:
- Files are in folders matching their URL city code
- Data in files matches the folder location
- All validation tests now pass ✅

## Documentation

Created `docs/city-codes.md` with:
- City code reference table
- Common issues and solutions
- Verification guidelines

## Result

All data files are now correctly organized:
- ✅ 市川市: Code 12203, all files contain 市川市 data
- ✅ 松戸市: Code 12207, all files contain 松戸市 data
- ✅ 柏市: Code 12215, all files contain 柏市 data
- ✅ 流山市: Code 12220, all files contain 流山市 data

## Prevention

The validation test can be run before commits to detect similar issues:
```bash
python tests/test_data_folder_validation.py
```
