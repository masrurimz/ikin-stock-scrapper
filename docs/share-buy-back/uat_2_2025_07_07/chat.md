# UAT Feedback #2 - July 7, 2025 16:17

## Chat Log

```
[07/07/25, 16.17.14] Mas Khoirur Rodziqin EE USI: Pak, collect the data for last/recent posted share buyback, only 5 items needs to be captured
[07/07/25, 16.17.14] Mas Khoirur Rodziqin EE USI: This the data to be captured for ALI
[07/07/25, 16.17.15] Mas Khoirur Rodziqin EE USI: The same info is required for those stocks that has published the share buyback
[07/07/25, 16.17.15] Mas Khoirur Rodziqin EE USI: 5 items means 
1.⁠ ⁠date
2.⁠ ⁠Total Number of Shares Purchased
3.⁠ ⁠Cummulative
4.⁠ ⁠Togal ammount Appropriate
5.⁠ ⁠Total ammount of shares
?
[07/07/25, 16.17.27] Mas Khoirur Rodziqin EE USI: Ini data yang perlu dicapture
[07/07/25, 16.17.41] Mas Khoirur Rodziqin EE USI: Ini item itemnya, yang dilingkati di gambar
[07/07/25, 16.17.52] Mas Khoirur Rodziqin EE USI: Terus capture cuma yang latest
[07/07/25, 16.18.26] Mas Khoirur Rodziqin EE USI: Dari semua data yang ana di share buyback
```

## Summary

**Key Requirements:**
1. **Latest/Recent Only**: Capture only the most recent posted share buyback (not all historical data)
2. **Simplified Output**: Only 5 essential fields needed
3. **Apply to All Stocks**: Same 5-field format for all companies with share buyback data

**5 Required Fields:**
1. Date (disclosure date)
2. Total Number of Shares Purchased (in the transaction)
3. Cumulative (cumulative shares purchased to date)
4. Total Amount Appropriated (program budget)
5. Total Amount of Shares (repurchased/spent)

**Translation Notes:**
- "Ini data yang perlu dicapture" = "This is the data that needs to be captured"
- "Ini item itemnya, yang dilingkati di gambar" = "These are the items, the ones circled in the image"
- "Terus capture cuma yang latest" = "Then capture only the latest"
- "Dari semua data yang ana di share buyback" = "From all the share buyback data available"

## Impact Assessment

**Current vs Requested:**
- Current: 17 fields with complete transaction details
- Requested: 5 core fields with latest data only

**Implementation Options:**
1. Add simplified output mode/flag
2. Create new report type for simplified data
3. Modify existing output to focus on latest only
4. Add configuration option for field selection