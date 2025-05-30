"""
Processor for public ownership reports.
"""

import re
from typing import Dict, Optional
from bs4 import BeautifulSoup

from ...utils import clean_text, convert_to_numeric


class PublicOwnershipProcessor:
    """Processor for public ownership report data."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process public ownership report.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed data
        """
        try:
            # Find the public ownership table
            table = soup.find("table")
            if not table:
                self.logger.warning(f"No table found for {stock_name}")
                return None

            result = self._extract_table_data(table, stock_name, disclosure_date)
            
            if result:
                self.logger.info(f"Successfully processed public ownership for {stock_name}")
                return result
            else:
                self.logger.warning(f"No data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing public ownership for {stock_name}: {e}")
            return None

    def _extract_table_data(self, table: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract data from public ownership table.

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
                
                # Convert numeric values
                value = convert_to_numeric(value)
                
                table_data[key] = value

        return table_data
