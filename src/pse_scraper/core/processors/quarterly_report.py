"""
Processor for quarterly reports.
"""

import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup

from ...utils import clean_text, convert_to_numeric


class QuarterlyReportProcessor:
    """Processor for quarterly report data."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process quarterly report with comprehensive data extraction matching original implementation.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed data
        """
        try:
            self.logger.info(f"Processing quarterly report for {stock_name} on {disclosure_date}")
            
            # Create a flat dictionary with all data for output in the same format as other features
            result = {
                "stock name": stock_name,
                "disclosure date": disclosure_date,
                "period_ended_date": "",
                "fiscal_year_ended_date": ""
            }
            
            # Extract period ended date directly from the HTML
            period_ended_row = soup.find("th", string="For the period ended")
            if period_ended_row and period_ended_row.find_next("td"):
                result["period_ended_date"] = clean_text(period_ended_row.find_next("td").text)
                self.logger.info(f"Found period ended date: {result['period_ended_date']}")
            
            # Process financial statements with comprehensive field extraction
            self._process_balance_sheet_comprehensive(soup, result)
            self._process_income_statement_comprehensive(soup, result)
            self._process_eps_comprehensive(soup, result)
            
            # Also keep the original table processing for backward compatibility and create duplicate fields
            for table in soup.find_all("table"):
                table_caption = table.find("caption")
                if (
                    table_caption
                    and table_caption.get_text(strip=True).lower() == "balance sheet"
                ):
                    grid = self._process_table_grid(table)
                    if grid:
                        result.update(
                            {
                                "Year Ending": clean_text(grid[0][0]) if len(grid) > 0 and len(grid[0]) > 0 else "",
                                "Previous Year Ending": clean_text(grid[1][1]) if len(grid) > 1 and len(grid[1]) > 1 else "",
                                "Current Assets Year Ending": clean_text(grid[2][1]) if len(grid) > 2 and len(grid[2]) > 1 else "",
                                "Current Assets Previous Year Ending": clean_text(grid[2][2]) if len(grid) > 2 and len(grid[2]) > 2 else "",
                                "Total Assets Year Ending": clean_text(grid[3][1]) if len(grid) > 3 and len(grid[3]) > 1 else "",
                                "Total Assets Previous Year Ending": clean_text(grid[3][2]) if len(grid) > 3 and len(grid[3]) > 2 else "",
                                "Current Liabilities Year Ending": clean_text(grid[4][1]) if len(grid) > 4 and len(grid[4]) > 1 else "",
                                "Current Liabilities Previous Year Ending": clean_text(grid[4][2]) if len(grid) > 4 and len(grid[4]) > 2 else "",
                                "Total Liabilities Year Ending": clean_text(grid[5][1]) if len(grid) > 5 and len(grid[5]) > 1 else "",
                                "Total Liabilities Previous Year Ending": clean_text(grid[5][2]) if len(grid) > 5 and len(grid[5]) > 2 else "",
                                "RetainedEarnings/(Deficit) Year Ending": clean_text(grid[6][1]) if len(grid) > 6 and len(grid[6]) > 1 else "",
                                "RetainedEarnings/(Deficit) Previous Year Ending": clean_text(grid[6][2]) if len(grid) > 6 and len(grid[6]) > 2 else "",
                                "Stockholders' Equity Year Ending": clean_text(grid[7][1]) if len(grid) > 7 and len(grid[7]) > 1 else "",
                                "Stockholders' Equity Previous Year Ending": clean_text(grid[7][2]) if len(grid) > 7 and len(grid[7]) > 2 else "",
                                "Stockholders' Equity - Parent Year Ending": clean_text(grid[8][1]) if len(grid) > 8 and len(grid[8]) > 1 else "",
                                "Stockholders' Equity - Parent Previous Year Ending": clean_text(grid[8][2]) if len(grid) > 8 and len(grid[8]) > 2 else "",
                                "Book Value Per Share Year Ending": clean_text(grid[9][1]) if len(grid) > 9 and len(grid[9]) > 1 else "",
                                "Book Value Per Share Previous Year Ending": clean_text(grid[9][2]) if len(grid) > 9 and len(grid[9]) > 2 else ""
                            }
                        )
                elif (
                    table_caption
                    and table_caption.get_text(strip=True).lower() == "income statement"
                ):
                    grid = self._process_table_grid(table)
                    if grid and len(grid) >= 11 and len(grid[0]) >= 5:
                        result.update(
                            {
                                f"Gross Revenue {clean_text(grid[0][1])}": clean_text(grid[1][1]),
                                f"Gross Revenue {clean_text(grid[0][2])}": clean_text(grid[1][2]),
                                f"Gross Revenue {clean_text(grid[0][3])}": clean_text(grid[1][3]),
                                f"Gross Revenue {clean_text(grid[0][4])}": clean_text(grid[1][4]),
                                f"Gross Expenses {clean_text(grid[0][1])}": clean_text(grid[2][1]),
                                f"Gross Expenses {clean_text(grid[0][2])}": clean_text(grid[2][2]),
                                f"Gross Expenses {clean_text(grid[0][3])}": clean_text(grid[2][3]),
                                f"Gross Expenses {clean_text(grid[0][4])}": clean_text(grid[2][4]),
                                f"Non Operating Income {clean_text(grid[0][1])}": clean_text(grid[3][1]),
                                f"Non Operating Income {clean_text(grid[0][2])}": clean_text(grid[3][2]),
                                f"Non Operating Income {clean_text(grid[0][3])}": clean_text(grid[3][3]),
                                f"Non Operating Income {clean_text(grid[0][4])}": clean_text(grid[3][4]),
                                f"Non Operating Expenses {clean_text(grid[0][1])}": clean_text(grid[4][1]),
                                f"Non Operating Expenses {clean_text(grid[0][2])}": clean_text(grid[4][2]),
                                f"Non Operating Expenses {clean_text(grid[0][3])}": clean_text(grid[4][3]),
                                f"Non Operating Expenses {clean_text(grid[0][4])}": clean_text(grid[4][4]),
                                f"Income/(Loss) Before Tax {clean_text(grid[0][1])}": clean_text(grid[5][1]),
                                f"Income/(Loss) Before Tax {clean_text(grid[0][2])}": clean_text(grid[5][2]),
                                f"Income/(Loss) Before Tax {clean_text(grid[0][3])}": clean_text(grid[5][3]),
                                f"Income/(Loss) Before Tax {clean_text(grid[0][4])}": clean_text(grid[5][4]),
                                f"Income Tax Expense {clean_text(grid[0][1])}": clean_text(grid[6][1]),
                                f"Income Tax Expense {clean_text(grid[0][2])}": clean_text(grid[6][2]),
                                f"Income Tax Expense {clean_text(grid[0][3])}": clean_text(grid[6][3]),
                                f"Income Tax Expense {clean_text(grid[0][4])}": clean_text(grid[6][4]),
                                f"Net Income/(Loss) After Tax {clean_text(grid[0][1])}": clean_text(grid[7][1]),
                                f"Net Income/(Loss) After Tax {clean_text(grid[0][2])}": clean_text(grid[7][2]),
                                f"Net Income/(Loss) After Tax {clean_text(grid[0][3])}": clean_text(grid[7][3]),
                                f"Net Income/(Loss) After Tax {clean_text(grid[0][4])}": clean_text(grid[7][4]),
                                f"Net Income/(Loss) Attributable to Parent Equity Holder {clean_text(grid[0][1])}": clean_text(grid[8][1]),
                                f"Net Income/(Loss) Attributable to Parent Equity Holder {clean_text(grid[0][2])}": clean_text(grid[8][2]),
                                f"Net Income/(Loss) Attributable to Parent Equity Holder {clean_text(grid[0][3])}": clean_text(grid[8][3]),
                                f"Net Income/(Loss) Attributable to Parent Equity Holder {clean_text(grid[0][4])}": clean_text(grid[8][4]),
                                f"Earnings/(Loss) Per Share (Basic) {clean_text(grid[0][1])}": clean_text(grid[9][1]),
                                f"Earnings/(Loss) Per Share (Basic) {clean_text(grid[0][2])}": clean_text(grid[9][2]),
                                f"Earnings/(Loss) Per Share (Basic) {clean_text(grid[0][3])}": clean_text(grid[9][3]),
                                f"Earnings/(Loss) Per Share (Basic) {clean_text(grid[0][4])}": clean_text(grid[9][4]),
                                f"Earnings/(Loss) Per Share (Diluted) {clean_text(grid[0][1])}": clean_text(grid[10][1]),
                                f"Earnings/(Loss) Per Share (Diluted) {clean_text(grid[0][2])}": clean_text(grid[10][2]),
                                f"Earnings/(Loss) Per Share (Diluted) {clean_text(grid[0][3])}": clean_text(grid[10][3]),
                                f"Earnings/(Loss) Per Share (Diluted) {clean_text(grid[0][4])}": clean_text(grid[10][4]),
                            }
                        )

            # Create duplicate fields with different naming conventions
            self._create_duplicate_fields(result)
            
            return result
        except Exception as e:
            self.logger.error(f"Error in quarterly report processing: {e}")
            return None

    def _process_table_grid(self, table):
        """Process table into a grid format for easier data extraction."""
        try:
            grid = []
            rows = table.find_all("tr")
            
            for row in rows:
                cells = row.find_all(["th", "td"])
                row_data = []
                for cell in cells:
                    # Get text from span with class valInput if available, otherwise get cell text
                    span = cell.find("span", class_="valInput")
                    if span:
                        cell_text = span.get_text(strip=True)
                    else:
                        cell_text = cell.get_text(strip=True)
                    row_data.append(cell_text)
                grid.append(row_data)
            
            return grid
        except Exception as e:
            self.logger.error(f"Error processing table grid: {e}")
            return []

    def _create_duplicate_fields(self, result: Dict) -> None:
        """Create duplicate fields with different naming conventions to match original system."""
        try:
            # Create duplicate fields for Income Statement data with both IS_ prefix and without
            is_fields_to_duplicate = [
                "Gross Revenue",
                "Gross Expense", 
                "Non-Operating Income",
                "Non-Operating Expense",
                "Income/(Loss) Before Tax",
                "Income Tax Expense", 
                "Net Income/(Loss) After Tax",
                "Net Income Attributable toParent Equity Holder",
                "Earnings/(Loss) Per Share(Basic)",
                "Earnings/(Loss) Per Share(Diluted)"
            ]
            
            # Period variations for Income Statement
            period_variations = [
                ("Current Year \n         (3 Months)", "Current Year(3 Months)"),
                ("Previous Year \n         (3 Months)", "Previous Year(3 Months)"),
                ("Current Year-To-Date", "Current Year-To-Date"),
                ("Previous Year-To-Date", "Previous Year-To-Date")
            ]
            
            # Create duplicate IS_ fields
            for field in is_fields_to_duplicate:
                for original_period, duplicate_period in period_variations:
                    is_key = f"IS_{field}_{original_period}"
                    duplicate_key = f"{field} {duplicate_period}"
                    
                    if is_key in result:
                        result[duplicate_key] = result[is_key]
            
            # Create Balance Sheet duplicates
            bs_fields_to_duplicate = [
                ("Current Assets", "Current Assets"),
                ("Total Assets", "Total Assets"), 
                ("Current Liabilities", "Current Liabilities"),
                ("Total Liabilities", "Total Liabilities"),
                ("RetainedEarnings/(Deficit)", "RetainedEarnings/(Deficit)"),
                ("Stockholders' Equity", "Stockholders' Equity"),
                ("Stockholders' Equity - Parent", "Stockholders' Equity - Parent"),
                ("Book Value Per Share", "Book Value Per Share")
            ]
            
            # Create BS duplicate fields for Year Ending/Previous Year Ending
            for bs_field, duplicate_field in bs_fields_to_duplicate:
                bs_year_key = f"BS_{bs_field}_Fiscal Year Ended (Audited)"
                bs_period_key = f"BS_{bs_field}_Period Ended"
                
                if bs_year_key in result:
                    result[f"{duplicate_field} Year Ending"] = result[bs_year_key]
                if bs_period_key in result:
                    result[f"{duplicate_field} Previous Year Ending"] = result[bs_period_key]
            
            # Create EPS duplicates
            eps_fields = result.get("EPS_Earnings/(Loss) Per Share (Basic)_Previous Year (Trailing 12 months)", "")
            if eps_fields:
                result["EPS_Earnings/(Loss) Per Share (Basic)_Previous Year (Trailing 12 months)"] = eps_fields
                
            eps_diluted_fields = result.get("EPS_Earnings/(Loss) Per Share (Diluted)_Previous Year (Trailing 12 months)", "")
            if eps_diluted_fields:
                result["EPS_Earnings/(Loss) Per Share (Diluted)_Previous Year (Trailing 12 months)"] = eps_diluted_fields
                
        except Exception as e:
            self.logger.error(f"Error creating duplicate fields: {e}")

    def _process_balance_sheet_comprehensive(self, soup: BeautifulSoup, result: Dict) -> None:
        """Process balance sheet with comprehensive field extraction."""
        try:
            # Find balance sheet table
            tables = soup.find_all("table")
            balance_sheet_table = None
            
            for table in tables:
                table_text = table.get_text().lower()
                if "balance sheet" in table_text or table.get('id') == 'BS':
                    balance_sheet_table = table
                    break
            
            if not balance_sheet_table:
                self.logger.warning("Balance sheet table not found")
                return
                
            # Process table using grid approach
            grid = self._process_table_grid(balance_sheet_table)
            if not grid or len(grid) < 3:
                return
                
            # Extract data based on grid structure
            bs_items = [
                "Current Assets",
                "Total Assets", 
                "Current Liabilities",
                "Total Liabilities",
                "RetainedEarnings/(Deficit)",
                "Stockholders' Equity",
                "Stockholders' Equity - Parent",
                "Book Value per Share"  # Use lowercase "per" to match original
            ]
            
            # Find header row for periods
            period_ended_col = 1
            fiscal_year_col = 2
            
            # Extract fiscal year ended date if available
            if len(grid) > 0 and len(grid[0]) > fiscal_year_col:
                fiscal_date = clean_text(grid[0][fiscal_year_col])
                if fiscal_date and "2025" in fiscal_date:
                    result["fiscal_year_ended_date"] = fiscal_date
                    result[f"BS_Mar 31 2025_Period Ended"] = fiscal_date
            
            # Process each balance sheet item
            for i, item in enumerate(bs_items, start=2):  # Start from row 2
                if i < len(grid):
                    row = grid[i]
                    
                    if len(row) > period_ended_col:
                        period_value = self._convert_to_numeric(clean_text(row[period_ended_col]))
                        result[f"BS_{item}_Period Ended"] = period_value
                        
                    if len(row) > fiscal_year_col:
                        fiscal_value = self._convert_to_numeric(clean_text(row[fiscal_year_col]))
                        result[f"BS_{item}_Fiscal Year Ended (Audited)"] = fiscal_value
                        
        except Exception as e:
            self.logger.error(f"Error in comprehensive balance sheet processing: {e}")

    def _process_income_statement_comprehensive(self, soup: BeautifulSoup, result: Dict) -> None:
        """Process income statement with comprehensive field extraction."""
        try:
            # Find income statement table
            tables = soup.find_all("table")
            income_table = None
            
            for table in tables:
                table_text = table.get_text().lower()
                if "income statement" in table_text or table.get('id') == 'IS':
                    income_table = table
                    break
            
            if not income_table:
                self.logger.warning("Income statement table not found")
                return
                
            # Process table using grid approach
            grid = self._process_table_grid(income_table)
            if not grid or len(grid) < 11:
                return
                
            # Income statement items mapping
            is_items = [
                "Gross Revenue",
                "Gross Expense", 
                "Non-Operating Income",
                "Non-Operating Expense",
                "Income/(Loss) Before Tax",
                "Income Tax Expense", 
                "Net Income/(Loss) After Tax",
                "Net Income Attributable toParent Equity Holder",
                "Earnings/(Loss) Per Share(Basic)",
                "Earnings/(Loss) Per Share(Diluted)"
            ]
            
            # Period headers - with exact spacing from original
            periods = [
                "Current Year \n         (3 Months)",
                "Previous Year \n         (3 Months)", 
                "Current Year-To-Date",
                "Previous Year-To-Date"
            ]
            
            # Extract headers from first row
            if len(grid[0]) >= 5:
                for col in range(1, 5):  # Columns 1-4 are the data columns
                    if col < len(periods) + 1:
                        period = periods[col - 1]
                        
                        # Process each income statement item
                        for item_idx, item in enumerate(is_items, start=1):
                            if item_idx < len(grid) and col < len(grid[item_idx]):
                                value = self._convert_to_numeric(clean_text(grid[item_idx][col]))
                                result[f"IS_{item}_{period}"] = value
                                
        except Exception as e:
            self.logger.error(f"Error in comprehensive income statement processing: {e}")

    def _process_eps_comprehensive(self, soup: BeautifulSoup, result: Dict) -> None:
        """Process EPS data with comprehensive field extraction."""
        try:
            # Find EPS table (usually contains "Trailing 12 months")
            tables = soup.find_all("table")
            eps_table = None
            
            for table in tables:
                table_text = table.get_text()
                if "trailing 12 months" in table_text.lower() or "eps" in table_text.lower():
                    eps_table = table
                    break
            
            if not eps_table:
                self.logger.warning("EPS table not found")
                return
                
            # Look for EPS data rows
            rows = eps_table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    item_text = clean_text(cells[0].get_text())
                    
                    # Look for basic EPS
                    if "earnings" in item_text.lower() and "basic" in item_text.lower():
                        if len(cells) > 1:
                            value = self._convert_to_numeric(clean_text(cells[1].get_text()))
                            result["EPS_Earnings/(Loss) Per Share (Basic)_Previous Year (Trailing 12 months)"] = value
                    
                    # Look for diluted EPS  
                    elif "earnings" in item_text.lower() and "diluted" in item_text.lower():
                        if len(cells) > 1:
                            value = self._convert_to_numeric(clean_text(cells[1].get_text()))
                            result["EPS_Earnings/(Loss) Per Share (Diluted)_Previous Year (Trailing 12 months)"] = value
                            
        except Exception as e:
            self.logger.error(f"Error in comprehensive EPS processing: {e}")

    def _convert_to_numeric(self, value):
        """Convert string value to numeric, handling various formats."""
        if not value or value == '-':
            return None
            
        # Clean the value
        value = clean_text(value)
        value = value.replace(',', '').replace('(', '-').replace(')', '')
        
        try:
            # Try to convert to float
            return float(value)
        except (ValueError, TypeError):
            return None
