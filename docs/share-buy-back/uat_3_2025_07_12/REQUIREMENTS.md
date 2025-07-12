# UAT Feedback #3 - New Output Structure for Share Buy-Back Data

**Date**: July 12, 2025  
**Status**: New Requirement  
**Priority**: High

## Client Request

Client wants the share buy-back output to have a new structure with columns extracted from "Date Registered" field.

### Required Output Format

```
stock_symbol | Date_Registered | Month | Year | Default_value_of_1 | Day | value_1 | value_2 | value_3 | value_4
ALI          | 5/27/2025       | 5     | 2025 | 1                  | 27  | 5800000 | 26070000000 | 843277246 | 22110774348
```

### Column Specifications

1. **stock_symbol** - Company stock symbol (e.g., ALI)
2. **Date_Registered** - Full date from "Date Registered" field (format: M/D/YYYY)
3. **Month** - Extracted month number from Date Registered
4. **Year** - Extracted year from Date Registered
5. **Default_value_of_1** - Static value of 1 for all records
6. **Day** - Extracted day number from Date Registered
7. **value_1** - Share buy-back value 1 (existing data)
8. **value_2** - Share buy-back value 2 (existing data)
9. **value_3** - Share buy-back value 3 (existing data)
10. **value_4** - Share buy-back value 4 (existing data)

## Current vs Requested Format

### Current Format (from UAT #2)

The current implementation returns comprehensive transaction data with fields like:

- Company symbol
- Disclosure date
- Transaction details
- Share counts
- Financial amounts

### Requested Format

Simplified structure focusing on:

- Date parsing (Month, Year, Day extraction)
- Static default value
- Core numerical values (value_1 through value_4)

## Implementation Notes

1. **Date Parsing**: Need to extract Month, Year, and Day from "Date Registered" field
2. **Value Mapping**: Map existing share buy-back values to value_1, value_2, value_3, value_4
3. **Static Field**: Add constant value of 1 for "Default_value_of_1" column
4. **Format Consistency**: Ensure date format matches M/D/YYYY pattern

## Next Steps

1. Analyze current share buy-back processor output
2. Identify which existing values should map to value_1-4
3. Implement date parsing logic
4. Update output format to match requirements
5. Test with ALI (Company ID 180) data
