"""
Processor for cash dividends reports.
"""

import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup

from ...utils import clean_text, convert_to_numeric


class CashDividendsProcessor:
    """Processor for cash dividends report data."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process cash dividends report.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed data
        """
        try:
            # Find the cash dividends table
            table = soup.find("table")
            if not table:
                self.logger.warning(f"No table found for {stock_name}")
                return None

            result = self._extract_cash_dividends_data(table, stock_name, disclosure_date)
            
            if result:
                self.logger.info(f"Successfully processed cash dividends for {stock_name}")
                return result
            else:
                self.logger.warning(f"No data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing cash dividends for {stock_name}: {e}")
            return None

    def _extract_cash_dividends_data(self, table: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract data from cash dividends table.

        Args:
            table: BeautifulSoup object of the table
            stock_name: Stock name
            report_date: Report date

        Returns:
            Dictionary containing table data
        """
        table_data = {"stock name": stock_name, "disclosure date": report_date}

        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) == 2:
                key = re.sub(
                    r"(?<=[A-Z])(?=[A-Z])", r" \t", cells[0].get_text(strip=True)
                )
                value = clean_text(cells[1].get_text())
                
                # Convert numeric values for dividend amounts
                if any(keyword in key.lower() for keyword in ['amount', 'rate', 'dividend', 'price']):
                    value = convert_to_numeric(value)
                
                table_data[key] = value

        return table_data
