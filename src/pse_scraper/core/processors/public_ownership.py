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
            # Pass the full soup instead of just finding one table
            result = self._extract_table_data(soup, stock_name, disclosure_date)
            
            if result and len(result) > 2:  # More than just stock name and disclosure date
                self.logger.info(f"Successfully processed public ownership for {stock_name}")
                return result
            else:
                self.logger.warning(f"No meaningful data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing public ownership for {stock_name}: {e}")
            return None

    def _extract_table_data(self, table: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract data from public ownership table.

        Args:
            table: BeautifulSoup object of the table (actually the full soup)
            stock_name: Stock name
            report_date: Report date

        Returns:
            Dictionary containing table data
        """
        # Initialize dictionary for storing data
        table_data = {"stock name": stock_name, "disclosure date": report_date}
        
        # Target fields we want to extract
        target_fields = {
            "Number of Issued Common Shares": "Number of Issued",
            "Less: Number of Treasury Common Shares, if any": "Less: Number of Treasury",
            "Number of Outstanding Common Shares": "Number of Outstanding",
            "Number of Listed Common Shares": "Number of Listed",
            "Total Number of Non-Public Shares": "Total Number of Non-Public",
            "Total Number of Shares Owned by the Public": "Total Number of Shares Owned",
            "Public Ownership Percentage": "Public Ownership Percentage",
            "Report Date": "Report Date"
        }
        
        # Find all tables in HTML
        tables = table.find_all('table')
        self.logger.info(f"Found {len(tables)} tables in the HTML")
        
        # Extract Report Date from page
        report_date_element = table.find("tr", string=lambda text: text and "Report Date" in text if text else False)
        if report_date_element:
            report_date_value = report_date_element.find_next("td")
            if report_date_value:
                table_data["Report Date"] = report_date_value.get_text(strip=True)
                self.logger.info(f"Found Report Date: {table_data['Report Date']}")
        
        # Alternative Report Date search
        if "Report Date" not in table_data:
            for tbl in tables:
                rows = tbl.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2 and "Report Date" in cells[0].get_text(strip=True):
                        report_date_value = cells[1].get_text(strip=True)
                        table_data["Report Date"] = report_date_value
                        self.logger.info(f"Found Report Date (alternative): {table_data['Report Date']}")
                        break
        
        # First, look for table with class='type1' which usually contains the data we're looking for
        for tbl in table.find_all('table', class_='type1'):
            rows = tbl.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    cell_text = cells[0].get_text(strip=True)
                    
                    # Check if this row contains one of our target fields
                    for field_name, search_text in target_fields.items():
                        if search_text in cell_text:
                            # Try to extract value from second cell
                            value_span = cells[1].find('span', class_='valInput')
                            if value_span:
                                value = value_span.get_text(strip=True)
                                table_data[field_name] = value
                                self.logger.info(f"Found {field_name}: {value}")
                            else:
                                # If no span with valInput class, get text directly
                                value = cells[1].get_text(strip=True)
                                table_data[field_name] = value
                                self.logger.info(f"Found {field_name} (direct text): {value}")
        
        # If we haven't found all fields, try a more general approach
        missing_fields = [field for field in target_fields.keys() if field not in table_data]
        if missing_fields:
            self.logger.info(f"Still missing fields: {missing_fields}. Trying more general approach...")
            
            # Try more general approach for missing fields
            for tbl in tables:
                rows = tbl.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        cell_text = cells[0].get_text(strip=True)
                        
                        for field_name in list(missing_fields):  # Use copy for safe iteration
                            search_text = target_fields[field_name]
                            if search_text in cell_text:
                                # Try different ways to extract value
                                value = None
                                
                                # First try to find span with any class
                                value_span = cells[1].find('span')
                                if value_span:
                                    value = value_span.get_text(strip=True)
                                else:
                                    # If no span, get text directly
                                    value = cells[1].get_text(strip=True)
                                
                                if value:
                                    table_data[field_name] = value
                                    self.logger.info(f"Found {field_name} (general approach): {value}")
                                    missing_fields.remove(field_name)
        
        # Special handling for Total Number of Non-Public Shares if still missing
        if "Total Number of Non-Public Shares" in missing_fields:
            # Try to calculate from other values if available
            if "Number of Outstanding Common Shares" in table_data and "Total Number of Shares Owned by the Public" in table_data:
                try:
                    outstanding = int(str(table_data["Number of Outstanding Common Shares"]).replace(',', ''))
                    public = int(str(table_data["Total Number of Shares Owned by the Public"]).replace(',', ''))
                    non_public = outstanding - public
                    table_data["Total Number of Non-Public Shares"] = f"{non_public:,}"
                    self.logger.info(f"Calculated Total Number of Non-Public Shares: {table_data['Total Number of Non-Public Shares']}")
                except (ValueError, TypeError) as e:
                    self.logger.error(f"Could not calculate Non-Public Shares: {e}")
        
        # Convert string values to numeric
        for field, value in table_data.items():
            if field in target_fields.keys():
                if field == "Public Ownership Percentage":
                    # Convert percentage to float
                    try:
                        numeric_value = float(str(value).replace('%', ''))
                        table_data[field] = numeric_value
                    except (ValueError, TypeError, AttributeError):
                        pass  # Keep original value if conversion fails
                else:
                    # Convert other values to integer (remove commas)
                    try:
                        numeric_value = int(str(value).replace(',', ''))
                        table_data[field] = numeric_value
                    except (ValueError, TypeError, AttributeError):
                        pass  # Keep original value if conversion fails
        
        return table_data
