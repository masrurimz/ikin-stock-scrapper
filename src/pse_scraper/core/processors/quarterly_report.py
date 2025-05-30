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
        Process quarterly report.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed data
        """
        try:
            # Find tables in the document
            tables = soup.find_all("table")
            if not tables:
                self.logger.warning(f"No tables found for {stock_name}")
                return None

            result = {"stock name": stock_name, "disclosure date": disclosure_date}
            
            # Process each table
            for i, table in enumerate(tables):
                table_data = self._extract_table_data(table)
                if table_data:
                    result.update(table_data)

            if len(result) > 2:  # More than just stock name and date
                self.logger.info(f"Successfully processed quarterly report for {stock_name}")
                return result
            else:
                self.logger.warning(f"No meaningful data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing quarterly report for {stock_name}: {e}")
            return None

    def _extract_table_data(self, table: BeautifulSoup) -> Dict:
        """
        Extract data from quarterly report table.

        Args:
            table: BeautifulSoup object of the table

        Returns:
            Dictionary containing table data
        """
        table_data = {}

        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) == 2:
                key = re.sub(
                    r"(?<=[A-Z])(?=[A-Z])", r" \t", cells[0].get_text(strip=True)
                )
                value = clean_text(cells[1].get_text())
                
                # Convert numeric values
                value = convert_to_numeric(value)
                
                if key and value:
                    table_data[key] = value

        return table_data
