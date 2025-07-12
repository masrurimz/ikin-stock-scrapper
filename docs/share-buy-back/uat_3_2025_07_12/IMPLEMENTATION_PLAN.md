# Implementation Plan for UAT #3 - New Share Buy-Back Output Structure

## Analysis Summary

### Current Output Fields (from share_buyback.py)

Based on the existing ShareBuybackProcessor, we extract:

**Transaction Data:**

- `total_shares_purchased` (from transaction table)
- `weighted_average_price`
- `total_transaction_value`
- `cumulative_shares_purchased` (from program summary)

**Program Summary:**

- `total_program_budget` (Total Amount Appropriated)
- `total_amount_spent` (Total Amount of Shares Repurchased)

**Share Effects:**

- `outstanding_shares_before/after`
- `treasury_shares_before/after`

## Value Mapping for New Format

Based on the client example values and existing extracted data:

```
ALI | 5/27/2025 | 5 | 2025 | 1 | 27 | 5800000 | 26070000000 | 843277246 | 22110774348
```

**Proposed Mapping:**

- `value_1` = `total_shares_purchased` (5,800,000)
- `value_2` = `total_program_budget` (26,070,000,000)
- `value_3` = `cumulative_shares_purchased` (843,277,246)
- `value_4` = `total_amount_spent` (22,110,774,348)

## Required Changes

### 1. Date Parsing Logic

Need to extract "Date Registered" field from the document and parse it into:

- Full date (M/D/YYYY format)
- Month number
- Year
- Day number

### 2. Extend Existing Process Method

Add UAT #3 format support to existing `process()` method:

```python
def process(self, soup, stock_name, disclosure_date, simplified=False):
    """Process share buyback - now returns UAT #3 format by default"""
```

### 3. Date Registered Extraction

Search for "Date Registered" field in the document:

- Look in meta information tables
- Parse date from format variations
- Handle different date formats (MM/DD/YYYY, M/D/YYYY, etc.)

### 4. CLI Integration

Add new output format option to CLI for UAT #3 structure

## Implementation Steps

1. **Add date registered extraction method to ShareBuybackProcessor**
2. **Extend existing process() method with uat3_format parameter**
3. **Add date parsing utilities for Month/Year/Day extraction**
4. **Update CLI to support UAT #3 format option**
5. **Test with ALI company data (ID 180)**
6. **Validate output matches client requirements**

## Files to Modify

- `src/pse_scraper/core/processors/share_buyback.py` - Extend process() method with UAT #3 format
- `src/pse_scraper/cli.py` - Add UAT #3 format option  
- Test with Company ID 180 (ALI) to validate output structure
