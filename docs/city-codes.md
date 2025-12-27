# City Codes Reference

This document lists the correct city codes for SumStock URLs.

## URL Format

SumStock URLs follow this format:
```
https://sumstock.jp/search/{region}/{prefecture}/{city}
```

For example:
- `https://sumstock.jp/search/02/12/12215` - 千葉県 柏市 (Kashiwa City, Chiba Prefecture)

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

**Symptom**: Files in `data/千葉県/柏市` (Kashiwa City) contain data for a different city.

**Root Cause**: The scraper saves files based on the addresses found in the scraped data, not the URL code. If the wrong URL is used, data will be saved in the wrong folder.

**Solution**: 
1. Verify the URL uses the correct city code from the table above
2. Move misplaced files to the correct city folder
3. Update the URL reference in the file to match the actual data

### Verification

To verify URLs match the data, check that:
- The city code in the URL matches the city mentioned in the data
- For example, if data contains "柏市" (Kashiwa City) addresses, the URL should use code `12215`

## Reference

See `scripts/location_mapping.py` for the complete mapping of all city codes.
