# Share Buy-Back Feature - UX Design Document (UXD)

## User Experience Overview

### Design Philosophy
Maintain complete consistency with existing CLI interface patterns to ensure zero learning curve for current users. The share buyback feature should feel like a natural extension of the existing tool.

### User Journey Goals
1. **Discoverability**: Users can easily find the new share buyback option
2. **Consistency**: Interaction patterns match existing report types exactly
3. **Efficiency**: Minimal steps to extract share buyback data
4. **Clarity**: Clear feedback on operation status and results

## User Interface Specifications

### CLI Menu Integration

#### Interactive Mode - Main Menu
```
📈 PSE DATA SCRAPER
Philippine Stock Exchange data scraping tool
⚙️ Configuration: 5 worker(s), no proxy, logging enabled

🔍 SEARCH OPTIONS:
  • Company Symbol: SM, BDO, PLDT, etc.
  • Single Company ID: Any number (1, 2, 3, etc.)
  • 🚀 BULK PROCESSING: Range of IDs (e.g., 1-100)

📊 AVAILABLE REPORTS:
  1. Public Ownership Report
  2. Quarterly Report
  3. Annual Report
  4. List of Top 100 Stockholders
  5. Declaration of Cash Dividends
  6. Share Buy-Back Transactions          ← NEW OPTION

========================================
MAIN MENU
========================================
1. Public Ownership
2. Quarterly Report
3. Annual Report
4. List of Top 100 Stockholders
5. Declaration of Cash Dividends
6. Settings
7. Exit
8. Share Buy-Back Transactions            ← NEW MENU ITEM
```

#### Menu Option Selection Flow
```
Enter your choice [1-8]: 8

Enter output filename: ali_buyback

Company Selection Options:
1. Single company by symbol: Enter company symbol (e.g., 'SM', 'BDO')
2. Single company by ID: Enter one company ID (e.g., '5')
3. Bulk processing: Enter company ID range

Enter company symbol OR starting company ID: 180
Enter ending company ID for bulk processing (or press Enter for single): [Enter]

🔍 Processing company ID: 180
🚀 Initializing scraper
🔍 Searching PSE database
📄 Parsing search results
📊 Analyzing report data
⬇️ Downloading reports
✅ Complete: Found 1 record(s)

✅ Successfully processed 180
   📊 Records found: 1
   🏢 Company: ALI
   📅 Latest report: 5/27/2025

💾 Saving results...

✅ PROCESSING COMPLETED!
📊 Records found: 1
🏢 Company: ALI
💾 Saved to: ali_buyback.csv
```

### Direct Command Mode Interface

#### Command Structure
```bash
# Single company by symbol
$ pse-scraper scrape ALI share_buyback --output ali_buyback

# Single company by ID
$ pse-scraper scrape 180 share_buyback --output ali_buyback

# Multiple output formats
$ pse-scraper scrape ALI share_buyback --format csv json --output ali_data

# With additional options
$ pse-scraper scrape ALI share_buyback --output ali_data --workers 3 --no-logging
```

#### Command Output
```
🔧 Scraping Configuration
┌─────────────┬──────────────────────────┐
│ Setting     │ Value                    │
├─────────────┼──────────────────────────┤
│ Company     │ ALI                      │
│ Report Type │ Share Buy Back           │
│ Output      │ ali_buyback              │
│ Formats     │ csv                      │
│ Workers     │ 5                        │
│ Proxies     │ Disabled                 │
│ Logging     │ Enabled                  │
└─────────────┴──────────────────────────┘

🔍 Processing ALI...
🚀 Initializing scraper
⬇️ Downloading reports (5 workers)
✅ Processing complete

✅ Successfully processed ALI
   📊 Records found: 1
   🏢 Company: Ayala Land, Inc.
   📅 Latest report: 5/27/2025

💾 Saving results...

┌────────────────────────────────────────┐
│              Results                   │
│                                        │
│ ✅ PROCESSING COMPLETED!              │
│                                        │
│ 📊 Records found: 1                   │
│ 🏢 Company: Ayala Land, Inc.          │
│ 💾 Saved to: ali_buyback.csv          │
└────────────────────────────────────────┘
```

### Bulk Processing Interface

#### Bulk Command
```bash
$ pse-scraper bulk 180 185 share_buyback --output bulk_buyback
```

#### Bulk Processing Output
```
🔧 Bulk Processing Configuration
┌─────────────┬──────────────────────────┐
│ Setting     │ Value                    │
├─────────────┼──────────────────────────┤
│ ID Range    │ 180 - 185                │
│ Count       │ 6                        │
│ Report Type │ Share Buy Back           │
│ Output      │ bulk_buyback             │
│ Formats     │ csv                      │
│ Workers     │ 5                        │
│ Proxies     │ Disabled                 │
│ Logging     │ Enabled                  │
└─────────────┴──────────────────────────┘

🚀 BULK PROCESSING: 6 companies (ID 180 - 185)

Processing company ID 180 (1/6) ████████████████████ 100%
   ✅ ID 180: Found 1 record(s)
Processing company ID 181 (2/6) ████████████████████ 100%
   ⚠️ ID 181: No data found
Processing company ID 182 (3/6) ████████████████████ 100%
   ⚠️ ID 182: No data found
Processing company ID 183 (4/6) ████████████████████ 100%
   ⚠️ ID 183: No data found
Processing company ID 184 (5/6) ████████████████████ 100%
   ⚠️ ID 184: No data found
Processing company ID 185 (6/6) ████████████████████ 100%
   ⚠️ ID 185: No data found

✅ BULK PROCESSING COMPLETED!
   📊 Total records found: 1
   🏢 Companies processed: 6
   📈 Companies with data: 1
   🎯 Success rate: 16.7%

💾 Saving results...

┌────────────────────────────────────────┐
│              Results                   │
│                                        │
│ ✅ PROCESSING COMPLETED!              │
│                                        │
│ 📊 Records found: 1                   │
│ 🏢 Companies processed: 6             │
│ 📈 Companies with data: 1             │
│ 🎯 Success rate: 16.7%                │
│ 💾 Saved to: bulk_buyback.csv         │
└────────────────────────────────────────┘
```

## User Interaction Patterns

### Input Validation

#### Company Input Validation
```
Enter company symbol OR starting company ID: [INVALID_INPUT]
❌ Error: Company symbol/ID cannot be empty.

Enter company symbol OR starting company ID: @#$
❌ Error: Invalid company identifier format.
```

#### Bulk Range Validation
```
Enter ending company ID for bulk processing: 175
❌ Error: Ending ID must be >= starting ID.

Enter company symbol OR starting company ID: 180
Enter ending company ID for bulk processing: 190
Process 11 companies? This may take a while. [y/N]: n
Operation cancelled
```

### Progress Indicators

#### Single Company Processing
```
🔍 Processing company: ALI
⬇️ [████████████████████] 100% ✅ Complete: Found 1 record(s)
```

#### Bulk Processing Progress
```
Processing companies 180-185 [██████████████████░░] 83% (5/6)
   ✅ ID 185: Found 0 record(s)
```

### Error Handling UX

#### No Data Found
```
⚠️ No data found for company 'XYZ'
   💡 This might be because:
      • Company symbol doesn't exist
      • No share buyback reports available
      • Company ID is invalid
      • Try checking PSE website directly
```

#### Network Issues
```
❌ Error during scraping: Connection timeout
   💡 Please check your internet connection and try again.
```

#### Invalid Company ID
```
❌ Error: Company ID '999999' not found
   💡 Please verify the company ID exists on PSE Edge.
```

## Output Format Specifications

### CSV Output Format
```csv
stock_name,disclosure_date,Date Registered,Month,Year,Day,Default value of 1,value_1,value_2,value_3,value_4
ALI,5/27/2025,5/27/2025,5,2025,27,1,5800000,26070000000,843277246,22110774348
```

### JSON Output Format
```json
[
  {
    "stock_name": "ALI",
    "disclosure_date": "5/27/2025",
    "Date Registered": "5/27/2025",
    "Month": 5,
    "Year": 2025,
    "Day": 27,
    "Default value of 1": 1,
    "value_1": 5800000,
    "value_2": 26070000000,
    "value_3": 843277246,
    "value_4": 22110774348
  }
]
```

## Accessibility Considerations

### CLI Accessibility
- **Screen Reader Support**: All output uses standard text that works with screen readers
- **Color Independence**: Status indicators use symbols (✅, ❌, ⚠️) in addition to colors
- **Keyboard Navigation**: All functionality accessible via keyboard only
- **Font Support**: Uses standard ASCII characters and common Unicode symbols

### Visual Design
- **Contrast**: High contrast between text and background
- **Typography**: Monospace font ensures consistent alignment
- **Iconography**: Consistent use of emojis for visual categorization
- **Spacing**: Clear visual hierarchy with appropriate whitespace

## Responsive Design

### Terminal Width Adaptation
```
# Wide Terminal (>100 chars)
┌─────────────────────────────────────────────────────────────────────┐
│                              Results                                │
│                                                                     │
│ ✅ PROCESSING COMPLETED!                                           │
│                                                                     │
│ 📊 Records found: 1                                               │
│ 🏢 Company: Ayala Land, Inc.                                      │
│ 💾 Saved to: ali_buyback.csv                                      │
└─────────────────────────────────────────────────────────────────────┘

# Narrow Terminal (<80 chars)
Results:
✅ PROCESSING COMPLETED!
📊 Records found: 1
🏢 Company: Ayala Land, Inc.
💾 Saved to: ali_buyback.csv
```

### Mobile Terminal Support
- **Line Wrapping**: Graceful handling of long filenames and company names
- **Scrolling**: Progress updates that don't overwhelm small screens
- **Touch Support**: All functionality works with touch-based terminal apps

## User Feedback and Validation

### Success Feedback
```
✅ Successfully processed ALI
   📊 Records found: 1
   🏢 Company: Ayala Land, Inc.
   📅 Latest report: 5/27/2025
```

### Warning Feedback
```
⚠️ No data found for company 'BDO'
   💡 This company may not have share buyback disclosures
```

### Error Feedback
```
❌ Error during scraping: Network timeout
   🔄 Retrying... (Attempt 2/3)
```

### Progress Feedback
```
🔍 Searching PSE database...
📄 Found 1 disclosure document
📊 Extracting data from document...
✅ Extraction complete
```

## Help and Documentation

### Help Text Integration
```bash
$ pse-scraper scrape --help
Usage: pse-scraper scrape [OPTIONS] COMPANY REPORT_TYPE

  Scrape data for a single company.

  COMPANY: Company symbol (e.g., 'SM', 'BDO') or numeric company ID
  REPORT_TYPE: Type of report to scrape

Options:
  --output, -o TEXT              Output filename (without extension)
  --format, -f [csv|json]        Output formats (can specify multiple)
  --workers, -w INTEGER RANGE    Number of concurrent workers (1-10)
  --use-proxies / --no-proxies   Enable/disable proxy rotation
  --no-logging                   Disable logging
  --help                         Show this message and exit.

Report Types:
  public_ownership     Public Ownership Report
  quarterly           Quarterly Report
  annual              Annual Report
  stockholders        List of Top 100 Stockholders
  cash_dividends      Declaration of Cash Dividends
  share_buyback       Share Buy-Back Transactions  ← NEW
```

### Interactive Help
```
📊 AVAILABLE REPORTS:
  1. Public Ownership Report
  2. Quarterly Report
  3. Annual Report
  4. List of Top 100 Stockholders
  5. Declaration of Cash Dividends
  6. Share Buy-Back Transactions    ← Extract corporate share buyback data

Enter your choice [1-8]: ?

Report Type Details:
1. Public Ownership - Company ownership structure and percentages
2. Quarterly Report - Quarterly financial statements
3. Annual Report - Annual financial statements
4. List of Top 100 Stockholders - Major shareholders information
5. Declaration of Cash Dividends - Dividend payment announcements
6. Share Buy-Back Transactions - Corporate share repurchase data
7. Settings - Configure scraper options
8. Exit - Close the application
```

## Performance Indicators

### Loading States
```
🚀 Initializing scraper with 5 worker(s)...
🔍 Searching PSE database for share buyback data...
📄 Processing 1 document found...
⬇️ Downloading report data...
📊 Extracting share buyback information...
💾 Saving to ali_buyback.csv...
✅ Complete!
```

### Time Indicators
```
⏱️ Processing started: 2025-07-06 14:30:15
⏱️ Estimated time remaining: ~30 seconds
⏱️ Processing completed: 2025-07-06 14:30:45 (30 seconds)
```

## User Testing Scenarios

### Scenario 1: First-Time User
1. User starts application
2. Sees new option 8 in menu
3. Selects option 8
4. Follows prompts to extract ALI share buyback data
5. Receives clear success feedback with file location

### Scenario 2: Power User
1. User runs direct command: `pse-scraper scrape ALI share_buyback`
2. Sees familiar progress indicators
3. Receives output in expected format
4. Can immediately process next company

### Scenario 3: Bulk Processing User
1. User runs bulk command for range 180-190
2. Sees progress bar with per-company results
3. Receives summary with success rate
4. Can identify which companies had data

### Scenario 4: Error Recovery
1. User enters invalid company ID
2. Receives clear error message with suggestions
3. Can retry with correct input
4. Succeeds on second attempt