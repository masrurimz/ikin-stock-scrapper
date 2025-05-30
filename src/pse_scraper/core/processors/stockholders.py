"""
Processor for stockholders reports (share structure data).
"""

import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup

from ...utils import clean_text


class StockholdersProcessor:
    """Processor for stockholders report data (share structure information)."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process stockholders report (extracts share structure data).

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed share structure data
        """
        try:
            # Find all tables - check both all tables and tables with class="type1"
            all_tables = soup.find_all("table")
            type1_tables = soup.find_all("table", {"class": "type1"})
            
            self.logger.info(f"Found {len(all_tables)} total tables, {len(type1_tables)} tables with class='type1' for {stock_name}")
            
            # Try type1 tables first (like old CLI)
            if len(type1_tables) >= 3:
                table = type1_tables[2]  # Third table with class type1
                self.logger.info(f"Using third table with class='type1' for {stock_name}")
                result = self._extract_share_structure_data(table, stock_name, disclosure_date)
                
                if result and len(result) > 2:
                    return result
            
            # Fallback to all tables if type1 approach fails
            if len(all_tables) >= 3:
                table = all_tables[2]  # Third table overall
                self.logger.info(f"Fallback: using third table overall for {stock_name}")
                result = self._extract_share_structure_data(table, stock_name, disclosure_date)
                
                if result and len(result) > 2:
                    return result
            
            self.logger.warning(f"No suitable tables found for {stock_name} (need at least 3 tables)")
            return None

        except Exception as e:
            self.logger.error(f"Error processing stockholders for {stock_name}: {e}")
            return None

    def _extract_share_structure_data(self, table: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract share structure data from the table (similar to old CLI's _process_stockholders).

        Args:
            table: BeautifulSoup object of the third table
            stock_name: Stock name
            report_date: Report date

        Returns:
            Dictionary containing share structure data
        """
        try:
            table_data = {"stock_name": stock_name, "disclosure_date": report_date}
            data_found = False
            
            # Debug: log table structure
            rows = table.find_all("tr")
            self.logger.info(f"Table has {len(rows)} rows for {stock_name}")
            
            # Process each row in the table (th/td pairs)
            for i, row in enumerate(rows):
                header = row.find("th")
                value_cell = row.find("td")
                
                if header and value_cell:
                    # Clean the header text
                    header_text = clean_text(header.get_text()).strip()
                    
                    # Get the value from span with class "valInput" first
                    value_span = value_cell.find("span", class_="valInput")
                    if value_span:
                        value_text = value_span.get_text(strip=True)
                    else:
                        # If no span with class valInput, get text directly
                        value_text = value_cell.get_text(strip=True)
                    
                    # Convert "-" to 0 and remove commas from numbers
                    value_text = "0" if value_text == "-" else value_text.replace(",", "")
                    
                    # Store in data dictionary with cleaned header as key
                    table_data[header_text] = value_text
                    data_found = True
                    self.logger.debug(f"Row {i}: {header_text}: {value_text}")
            
            if data_found:
                self.logger.info(f"Extracted {len(table_data)-2} share structure fields for {stock_name}")
                return table_data
            else:
                self.logger.warning(f"No th/td pairs found in table for {stock_name}")
                # Debug: show what we did find
                for i, row in enumerate(rows[:3]):  # Show first 3 rows for debugging
                    self.logger.debug(f"Row {i} content: {row}")
                return None

        except Exception as e:
            self.logger.error(f"Error extracting share structure data: {e}")
            return None
