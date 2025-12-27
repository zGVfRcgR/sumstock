# City Codes Reference

This document lists the correct city codes for SumStock URLs.

## URL Format

SumStock URLs follow this format:
```
https://sumstock.jp/search/{region}/{prefecture}/{city}
```

For example:
- `https://sumstock.jp/search/02/12/12215` - 千葉県 柏市 (Kashiwa City, Chiba Prefecture)

## Important: URL Code Determines Folder Location

**The scraper now uses the URL code to determine where files are saved**, regardless of what addresses appear in the scraped data. This ensures consistency and prevents mismatches.

Example:
- URL with code `12217` → Always saves to `data/千葉県/市原市/`
- URL with code `12215` → Always saves to `data/千葉県/柏市/`

Even if the scraped data contains addresses from a different city, the file will be saved according to the URL code.

## Chiba Prefecture (千葉県) City Codes

Based on `scripts/location_mapping.py`, the correct city codes are:

| City Code | City Name (Japanese) | City Name (English) |
|-----------|---------------------|---------------------|
| 12203 | 市川市 | Ichikawa City |
| 12207 | 松戸市 | Matsudo City |
| 12215 | 柏市 | Kashiwa City |
| 12217 | 市原市 | Ichihara City |
| 12220 | 流山市 | Nagareyama City |

## Common Issues

### Issue: Data from one city appears in another city's folder

**Previous Behavior**: The scraper saved files based on the addresses found in the scraped data, which could cause mismatches when the URL code didn't match the actual data.

**Current Behavior**: The scraper now **always saves files based on the URL code**, ensuring that:
- Files are consistently organized by URL code
- No mismatch between URL and folder location
- Easy to predict where files will be saved

**Warning System**: If the URL code doesn't match the scraped addresses, the scraper will log a warning but still save to the folder determined by the URL code.

### Verification

To verify URLs are correct:
- Check that the city code in the URL is what you intend to scrape
- For example, to scrape 柏市 (Kashiwa City), use code `12215` not `12217`

## Reference

See `scripts/location_mapping.py` for the complete mapping of all city codes.
