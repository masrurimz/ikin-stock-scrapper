# UAT Feedback #2 - Simplified Share Buyback Output

## Date: July 7, 2025 16:17

## Requirements Summary

### Primary Request
**Simplified data capture for share buyback reports with only the most recent/latest data and 5 essential fields.**

### Scope
- **Target**: All companies with published share buyback data
- **Frequency**: Latest/most recent report only (not historical)
- **Output**: Simplified 5-field format

### Required 5 Fields

| # | Field Name | Description | Current Mapping |
|---|------------|-------------|-----------------|
| 1 | Date | Disclosure date | `disclosure_date` |
| 2 | Total Number of Shares Purchased | Shares in this transaction | `total_shares_purchased` |
| 3 | Cumulative | Cumulative shares purchased to date | `cumulative_shares_purchased` |
| 4 | Total Amount Appropriated | Program budget allocation | `total_program_budget` |
| 5 | Total Amount of Shares | Total amount spent on repurchases | `total_amount_spent` |

### Expected Simplified Output Format

```csv
date,total_shares_purchased,cumulative_shares_purchased,total_program_budget,total_amount_spent
2025-07-07,1400000,876032246,26070000000.0,22885247993.0
```

### Business Context

**Why Simplified?**
- Focus on key financial metrics only
- Easier analysis and reporting
- Reduced data complexity
- Latest data more relevant than historical

**Use Case:**
- Quick financial analysis
- Reporting to stakeholders
- Monitoring recent buyback activity
- Simplified data export

### Implementation Considerations

**Option 1: Configuration Flag**
- Add `--simplified` or `--summary` flag
- Keep existing detailed output as default
- Allow users to choose format

**Option 2: New Report Type**
- Create `share_buyback_summary` report type
- Maintain existing `share_buyback` for detailed data
- Clear separation of use cases

**Option 3: Output Format Option**
- Add format parameter (detailed/summary)
- Single processor with conditional output
- Flexible based on user needs

**Option 4: Latest-Only Mode**
- Add `--latest-only` flag
- Return only most recent document
- Apply simplified field selection

### Current vs Requested Comparison

**Current Output (17 fields):**
```csv
stock_name,disclosure_date,is_amended_report,total_transactions,total_shares_purchased,weighted_average_price,total_transaction_value,outstanding_shares_before,outstanding_shares_after,outstanding_shares_change,treasury_shares_before,treasury_shares_after,treasury_shares_change,cumulative_shares_purchased,total_program_budget,total_amount_spent,contact_name,contact_designation
```

**Requested Output (5 fields):**
```csv
date,total_shares_purchased,cumulative_shares_purchased,total_program_budget,total_amount_spent
```

**Reduction:** 70% fewer fields, focus on core financial metrics

### Quality Requirements

- **Accuracy**: Maintain data quality with simplified output
- **Performance**: Should be faster with fewer fields
- **Compatibility**: Ensure existing detailed mode still works
- **Documentation**: Clear usage instructions for both modes

### Acceptance Criteria

- [ ] Simplified 5-field output available
- [ ] Latest-only data capture working
- [ ] Compatible with all companies having share buyback data
- [ ] Performance maintained or improved
- [ ] Existing detailed functionality preserved
- [ ] Clear documentation and usage examples