"""
Processor for annual reports.
"""

import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup

from ...utils import clean_text, convert_to_numeric


class AnnualReportProcessor:
    """Processor for annual report data."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process annual report with comprehensive financial data extraction.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed financial data
        """
        try:
            # Find tables in the document
            tables = soup.find_all("table")
            if not tables:
                self.logger.warning(f"No tables found for {stock_name}")
                return None

            table_data = {"stock name": stock_name, "disclosure date": disclosure_date}
            
            # Process each table looking for Balance Sheet and Income Statement
            for table in tables:
                table_caption = table.find("caption")
                
                # Process Balance Sheet
                if table_caption and table_caption.get_text(strip=True).lower() == "balance sheet":
                    grid = self._process_table_grid(table)
                    if grid:
                        self._extract_balance_sheet_data(grid, table_data)
                
                # Process Income Statement
                elif table_caption and table_caption.get_text(strip=True).lower() == "income statement":
                    grid = self._process_table_grid(table)
                    if grid:
                        self._extract_income_statement_data(grid, table_data)

            if len(table_data) > 2:  # More than just stock name and date
                self.logger.info(f"Successfully processed annual report for {stock_name}")
                return table_data
            else:
                self.logger.warning(f"No meaningful data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing annual report for {stock_name}: {e}")
            return None

    def _process_table_grid(self, table: BeautifulSoup) -> List[List[str]]:
        """
        Process table into a 2D grid structure.

        Args:
            table: BeautifulSoup table object

        Returns:
            2D list representing the table grid
        """
        grid = []
        rows = table.find_all("tr")
        
        for row in rows:
            cells = row.find_all(["th", "td"])
            row_data = []
            for cell in cells:
                # Get text from span with class "valInput" if available
                value_span = cell.find("span", class_="valInput")
                if value_span:
                    text = value_span.get_text(strip=True)
                else:
                    text = cell.get_text(strip=True)
                row_data.append(text)
            if row_data:  # Only add non-empty rows
                grid.append(row_data)
        
        return grid

    def _extract_balance_sheet_data(self, grid: List[List[str]], table_data: Dict) -> None:
        """
        Extract Balance Sheet data from table grid.

        Args:
            grid: 2D list representing the table
            table_data: Dictionary to store extracted data
        """
        try:
            # Find the correct row indices by looking for specific row labels
            current_assets_row = None
            total_assets_row = None
            current_liabilities_row = None
            total_liabilities_row = None
            retained_earnings_row = None
            stockholders_equity_row = None
            stockholders_equity_parent_row = None
            book_value_row = None
            
            # Find the rows by their labels
            for i, row in enumerate(grid):
                if len(row) > 0:
                    row_label = row[0].lower()
                    if 'current assets' in row_label:
                        current_assets_row = i
                    elif 'total assets' in row_label:
                        total_assets_row = i
                    elif 'current liabilities' in row_label:
                        current_liabilities_row = i
                    elif 'total liabilities' in row_label:
                        total_liabilities_row = i
                    elif 'retained earnings' in row_label or 'deficit' in row_label:
                        retained_earnings_row = i
                    elif "stockholders' equity" in row_label and 'parent' not in row_label:
                        stockholders_equity_row = i
                    elif "stockholders' equity - parent" in row_label or ('parent' in row_label and 'equity' in row_label):
                        stockholders_equity_parent_row = i
                    elif 'book value' in row_label:
                        book_value_row = i
            
            # Extract values using the identified row indices
            if current_assets_row is not None and len(grid[current_assets_row]) >= 3:
                table_data['Current Assets Year Ending'] = clean_text(grid[current_assets_row][1])
                table_data['Current Assets Previous Year Ending'] = clean_text(grid[current_assets_row][2])
            
            if total_assets_row is not None and len(grid[total_assets_row]) >= 3:
                table_data['Total Assets Year Ending'] = clean_text(grid[total_assets_row][1])
                table_data['Total Assets Previous Year Ending'] = clean_text(grid[total_assets_row][2])
            
            if current_liabilities_row is not None and len(grid[current_liabilities_row]) >= 3:
                table_data['Current Liabilities Year Ending'] = clean_text(grid[current_liabilities_row][1])
                table_data['Current Liabilities Previous Year Ending'] = clean_text(grid[current_liabilities_row][2])
            
            if total_liabilities_row is not None and len(grid[total_liabilities_row]) >= 3:
                table_data['Total Liabilities Year Ending'] = clean_text(grid[total_liabilities_row][1])
                table_data['Total Liabilities Previous Year Ending'] = clean_text(grid[total_liabilities_row][2])
            
            if retained_earnings_row is not None and len(grid[retained_earnings_row]) >= 3:
                table_data['RetainedEarnings/(Deficit) Year Ending'] = clean_text(grid[retained_earnings_row][1])
                table_data['RetainedEarnings/(Deficit) Previous Year Ending'] = clean_text(grid[retained_earnings_row][2])
            
            if stockholders_equity_row is not None and len(grid[stockholders_equity_row]) >= 3:
                table_data["Stockholders' Equity Year Ending"] = clean_text(grid[stockholders_equity_row][1])
                table_data["Stockholders' Equity Previous Year Ending"] = clean_text(grid[stockholders_equity_row][2])
            
            if stockholders_equity_parent_row is not None and len(grid[stockholders_equity_parent_row]) >= 3:
                table_data["Stockholders' Equity - Parent Year Ending"] = clean_text(grid[stockholders_equity_parent_row][1])
                table_data["Stockholders' Equity - Parent Previous Year Ending"] = clean_text(grid[stockholders_equity_parent_row][2])
            
            if book_value_row is not None and len(grid[book_value_row]) >= 3:
                table_data['Book Value Per Share Year Ending'] = clean_text(grid[book_value_row][1])
                table_data['Book Value Per Share Previous Year Ending'] = clean_text(grid[book_value_row][2])
            
            self.logger.info("Processed Balance Sheet data")
        except (IndexError, KeyError) as e:
            self.logger.error(f"Error processing Balance Sheet: {e}")

    def _extract_income_statement_data(self, grid: List[List[str]], table_data: Dict) -> None:
        """
        Extract Income Statement data from table grid.

        Args:
            grid: 2D list representing the table
            table_data: Dictionary to store extracted data
        """
        try:
            # Find the correct row indices by looking for specific row labels
            revenue_row = None
            expense_row = None
            non_op_income_row = None
            non_op_expense_row = None
            income_before_tax_row = None
            income_tax_row = None
            net_income_row = None
            net_income_parent_row = None
            eps_basic_row = None
            eps_diluted_row = None
            
            # Find the rows by their labels
            for i, row in enumerate(grid):
                if len(row) > 0:
                    row_label = row[0].lower()
                    if 'revenue' in row_label or 'gross revenue' in row_label:
                        revenue_row = i
                    elif 'expense' in row_label or 'gross expense' in row_label:
                        expense_row = i
                    elif 'non-operating income' in row_label or 'non operating income' in row_label:
                        non_op_income_row = i
                    elif 'non-operating expense' in row_label or 'non operating expense' in row_label:
                        non_op_expense_row = i
                    elif 'income before tax' in row_label or 'income/(loss) before tax' in row_label:
                        income_before_tax_row = i
                    elif 'income tax' in row_label:
                        income_tax_row = i
                    elif ('net income' in row_label or 'net income/(loss)' in row_label) and 'parent' not in row_label and 'attributable' not in row_label:
                        net_income_row = i
                    elif ('attributable to parent' in row_label or 'parent equity holder' in row_label):
                        net_income_parent_row = i
                    elif 'earnings per share (basic)' in row_label or 'eps (basic)' in row_label:
                        eps_basic_row = i
                    elif 'earnings per share (diluted)' in row_label or 'eps (diluted)' in row_label:
                        eps_diluted_row = i
            
            # Get the column headers (years)
            years = []
            if len(grid) > 0 and len(grid[0]) > 1:
                for i in range(1, len(grid[0])):
                    if grid[0][i]:
                        years.append(clean_text(grid[0][i]))
            
            # Extract values using the identified row indices
            if revenue_row is not None and len(grid[revenue_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[revenue_row]):
                        key = f"Gross Revenue {year}"
                        table_data[key] = clean_text(grid[revenue_row][i])
            
            if expense_row is not None and len(grid[expense_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[expense_row]):
                        key = f"Gross Expenses {year}"
                        table_data[key] = clean_text(grid[expense_row][i])
            
            if non_op_income_row is not None and len(grid[non_op_income_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[non_op_income_row]):
                        key = f"Non Operating Income {year}"
                        table_data[key] = clean_text(grid[non_op_income_row][i])
            
            if non_op_expense_row is not None and len(grid[non_op_expense_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[non_op_expense_row]):
                        key = f"Non Operating Expenses {year}"
                        table_data[key] = clean_text(grid[non_op_expense_row][i])
            
            if income_before_tax_row is not None and len(grid[income_before_tax_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[income_before_tax_row]):
                        key = f"Income/(Loss) Before Tax {year}"
                        table_data[key] = clean_text(grid[income_before_tax_row][i])
            
            if income_tax_row is not None and len(grid[income_tax_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[income_tax_row]):
                        key = f"Income Tax Expense {year}"
                        table_data[key] = clean_text(grid[income_tax_row][i])
            
            if net_income_row is not None and len(grid[net_income_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[net_income_row]):
                        key = f"Net Income/(Loss) After Tax {year}"
                        table_data[key] = clean_text(grid[net_income_row][i])
            
            if net_income_parent_row is not None and len(grid[net_income_parent_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[net_income_parent_row]):
                        key = f"Net Income/(Loss) Attributable to Parent Equity Holder {year}"
                        table_data[key] = clean_text(grid[net_income_parent_row][i])
            
            if eps_basic_row is not None and len(grid[eps_basic_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[eps_basic_row]):
                        key = f"Earnings/(Loss) Per Share (Basic) {year}"
                        table_data[key] = clean_text(grid[eps_basic_row][i])
            
            if eps_diluted_row is not None and len(grid[eps_diluted_row]) >= 2:
                for i, year in enumerate(years, 1):
                    if i < len(grid[eps_diluted_row]):
                        key = f"Earnings/(Loss) Per Share (Diluted) {year}"
                        table_data[key] = clean_text(grid[eps_diluted_row][i])
            
            self.logger.info("Processed Income Statement data")
        except (IndexError, KeyError) as e:
            self.logger.error(f"Error processing Income Statement: {e}")
