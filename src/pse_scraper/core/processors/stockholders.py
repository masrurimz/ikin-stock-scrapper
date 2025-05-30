"""
Processor for stockholders reports.
"""

import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup

from ...utils import clean_text, clean_stockholders_text, convert_to_numeric


class StockholdersProcessor:
    """Processor for top 100 stockholders report data."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process stockholders report.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed data
        """
        try:
            # Find the stockholders table
            table = soup.find("table")
            if not table:
                self.logger.warning(f"No table found for {stock_name}")
                return None

            result = self._extract_stockholders_data(table, stock_name, disclosure_date)
            
            if result:
                self.logger.info(f"Successfully processed stockholders for {stock_name}")
                return result
            else:
                self.logger.warning(f"No data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing stockholders for {stock_name}: {e}")
            return None

    def _extract_stockholders_data(self, table: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract data from stockholders table using grid processing.

        Args:
            table: BeautifulSoup object of the table
            stock_name: Stock name
            report_date: Report date

        Returns:
            Dictionary containing table data
        """
        try:
            # Process table as grid to handle complex layout
            grid = self._process_table_grid(table)
            
            if not grid:
                return None

            table_data = {"stock name": stock_name, "disclosure date": report_date}
            
            # Process the grid data to extract stockholder information
            for i, row in enumerate(grid):
                if i == 0:  # Skip header row
                    continue
                    
                if len(row) >= 3:  # Assuming at least name, shares, percentage columns
                    stockholder_name = clean_stockholders_text(row[0])
                    shares = clean_stockholders_text(row[1])
                    percentage = clean_stockholders_text(row[2])
                    
                    if stockholder_name and shares:
                        # Convert shares to numeric if possible
                        shares = convert_to_numeric(shares)
                        percentage = convert_to_numeric(percentage.replace('%', '')) if percentage else ''
                        
                        table_data[f"stockholder_{i}_name"] = stockholder_name
                        table_data[f"stockholder_{i}_shares"] = shares
                        table_data[f"stockholder_{i}_percentage"] = percentage

            return table_data

        except Exception as e:
            self.logger.error(f"Error extracting stockholders data: {e}")
            return None

    def _process_table_grid(self, table: BeautifulSoup) -> List[List[str]]:
        """
        Extract data from table grid.

        Args:
            table: BeautifulSoup object of the table

        Returns:
            List of Lists containing table grid data
        """
        try:
            rows = table.find_all("tr")
            if not rows:
                return []

            max_cols = max(
                sum(int(col.get("colspan", 1)) for col in row.find_all(["th", "td"]))
                for row in rows
            )
            grid = [[""] * max_cols for _ in range(len(rows))]

            for i, row in enumerate(rows):
                col_idx = 0
                for cell in row.find_all(["th", "td"]):
                    while col_idx < max_cols and grid[i][col_idx] != "":
                        col_idx += 1

                    colspan = int(cell.get("colspan", 1))
                    rowspan = int(cell.get("rowspan", 1))
                    text = cell.get_text(strip=True)

                    for r in range(rowspan):
                        for c in range(colspan):
                            if i + r < len(grid) and col_idx + c < len(grid[0]):
                                grid[i + r][col_idx + c] = text

                    col_idx += colspan

            return grid

        except Exception as e:
            self.logger.error(f"Error processing table grid: {e}")
            return []
