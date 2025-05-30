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
        Process cash dividends report (matches old CLI logic).

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed data
        """
        try:
            # Check if there's an input with value COMMON that is checked (like old CLI)
            common_input = None
            report_type_ul = soup.find("ul", {"class": "reportType"})
            if report_type_ul:
                for input_elem in report_type_ul.find_all("input"):
                    if input_elem.get("checked") and input_elem.get("value") == "COMMON":
                        common_input = input_elem
                        break

            if not common_input:
                self.logger.warning(f"No checked COMMON input found for {stock_name}")
                return None

            result = self._extract_cash_dividends_data(soup, stock_name, disclosure_date)
            
            if result and len(result) > 2:  # More than stock_name and disclosure_date
                self.logger.info(f"Successfully processed cash dividends for {stock_name}")
                return result
            else:
                self.logger.warning(f"No dividend data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing cash dividends for {stock_name}: {e}")
            return None

    def _extract_cash_dividends_data(self, soup: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract data from cash dividends document (matches old CLI logic).

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            report_date: Report date

        Returns:
            Dictionary containing cash dividends data
        """
        table_data = {"stock_name": stock_name, "disclosure_date": report_date}

        # Debug: log all tables found
        all_tables = soup.find_all("table")
        self.logger.info(f"Found {len(all_tables)} tables for {stock_name}")
        
        # Look for table with caption "cash dividend" (like old CLI)
        cash_dividend_table_found = False
        for i, table in enumerate(all_tables):
            table_caption = table.find("caption")
            caption_text = table_caption.get_text(strip=True).lower() if table_caption else "no caption"
            self.logger.debug(f"Table {i}: caption = '{caption_text}'")
            
            if table_caption and caption_text == "cash dividend":
                cash_dividend_table_found = True
                self.logger.info(f"Found cash dividend table for {stock_name}")
                
                # Process each row in the table
                for row in table.find_all("tr"):
                    cells = row.find_all(["th", "td"])
                    if len(cells) == 2:
                        # Extract key and value (matching old CLI regex)
                        key = re.sub(
                            r"(?<=[A-Z])(?=[A-Z])",
                            r" \t",
                            cells[0].get_text(strip=True),
                        )
                        value = clean_text(cells[1].get_text())
                        table_data[key] = value
                        self.logger.debug(f"Extracted: {key}: {value}")

        if not cash_dividend_table_found:
            self.logger.warning(f"No table with 'cash dividend' caption found for {stock_name}")
            # Debug: log first few table captions
            for i, table in enumerate(all_tables[:5]):  # First 5 tables
                caption = table.find("caption")
                caption_text = caption.get_text(strip=True) if caption else "NO CAPTION"
                self.logger.debug(f"Table {i} caption: '{caption_text}'")

        self.logger.info(f"Extracted {len(table_data)-2} dividend fields for {stock_name}")
        return table_data
