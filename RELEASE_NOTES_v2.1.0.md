# PSE Data Scraper v2.1.0 Release Notes

## 🚀 New Features

### Share Buy-Back Transaction Support

- Complete Share Buy-Back feature implementation
- Interactive CLI menu option (Menu #8)
- Amendment detection for revised reports
- SRP prefix standardization (`_SRP_ALI`, `_SRP_FPH` format)

### Enhanced Data Processing

- UAT Feedback #3 implementation with date component parsing
- Per-company filtering and latest record extraction
- Proxy support enabled by default for better bulk processing

## 🔧 Enhancements

- Updated CLI display text to reflect UAT #3 format
- Professional column naming in CSV outputs
- Real data validation against live PSE sources

## 🐛 Bug Fixes

- Fixed simplified mode to return latest record per company
- Resolved UAT feedback issues for Share Buy-Back processing
- Improved date parsing reliability

## 💻 Usage Examples

```bash
# Share Buy-Back scraping
poetry run pse-scraper scrape 180 share_buyback --output ali_buyback

# Interactive mode with new Menu #8
poetry run pse-scraper
```

## 🎯 What's Changed Since v2.0.0

**Major Additions (15 commits):**

1. Complete Share Buy-Back infrastructure
2. UAT Feedback integration
3. SRP prefix standardization
4. Enhanced proxy support
5. Date component parsing

**Breaking Changes:** None - full backward compatibility maintained

---

**Release Date:** July 2025  
**Previous Version:** v2.0.0
