# Share Buy-Back Feature Specification

## Overview
Add support for scraping Share Buy-Back Transactions from PSE Edge platform as menu option 8.

## Requirements

### Functional Requirements
- Add new report type: "Share Buy-Back Transactions" 
- Extend CLI menu with option "8. Share Buy-Back Transactions"
- Extract share buyback data with fields: stock symbol, Date Registered, Month, Year, Default value of 1, Day, value_1, value_2, value_3, value_4
- Support both single company and bulk processing modes
- Save results in CSV/JSON formats like existing report types

### Technical Requirements
- Follow existing processor interface pattern: `process(soup, stock_name, disclosure_date) -> Optional[Dict]`
- Handle HTML structure specific to share buyback reports
- Extract data from "Share Buy-Back Transactions" template
- Route through existing core scraper logic
- Maintain backward compatibility

### Expected Data Structure
Based on PDF sample analysis:
```
{
    "stock_name": "ALI",
    "disclosure_date": "5/27/2025", 
    "Date Registered": "5/27/2025",
    "Month": 5,
    "Year": 2025,
    "Default value of 1": 1,
    "Day": 27,
    "value_1": 5800000,
    "value_2": 26070000000,
    "value_3": 843277246,
    "value_4": 22110774348
}
```

## Implementation Plan

### Files to Modify
1. `src/pse_scraper/models/report_types.py` - Add SHARE_BUYBACK enum
2. `src/pse_scraper/core/processors/share_buyback.py` - New processor class
3. `src/pse_scraper/core/processors/__init__.py` - Export new processor
4. `src/pse_scraper/core/__init__.py` - Add routing logic
5. `src/pse_scraper/cli.py` - Add menu option and CLI mapping

### Implementation Order
1. Domain layer: Add ReportType.SHARE_BUYBACK
2. Data layer: Create ShareBuybackProcessor
3. Business layer: Add core scraper routing  
4. Interface layer: Update CLI menu and mappings
5. Testing: Verify end-to-end functionality

### Design Decisions
- Follow existing processor pattern for consistency
- Use same row processing approach as other report types (likely `_process_single_row`)
- Parse HTML for share buyback specific table structure
- Extract numeric values and dates using existing utility functions

### Risk Assessment
- **Low Risk**: Following established patterns
- **Potential Issues**: Unknown HTML structure for share buyback reports
- **Mitigation**: Analyze sample URLs to understand structure before implementation

### Success Criteria
- Menu option 8 appears and functions correctly
- Can scrape share buyback data for sample company ID 180
- Data extracted matches expected format from PDF sample
- Integration with existing CLI modes (interactive, direct command, bulk)
- No regression in existing report types