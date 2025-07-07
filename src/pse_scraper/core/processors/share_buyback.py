"""
Processor for share buyback transaction reports.
"""

import re
from typing import Dict, Optional
from bs4 import BeautifulSoup

from ...utils import clean_text, convert_to_numeric


class ShareBuybackProcessor:
    """Processor for share buyback transaction report data."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process share buyback transaction report.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed data
        """
        try:
            self.logger.info(f"=== SHARE BUYBACK PROCESSOR DEBUG START ===")
            self.logger.info(f"Processing share buyback for {stock_name} on {disclosure_date}")
            
            # Debug: Log the HTML structure to understand the document
            self._debug_document_structure(soup, stock_name)
            
            # Extract share buyback data
            result = self._extract_share_buyback_data(soup, stock_name, disclosure_date)
            
            if result and len(result) > 2:  # More than stock_name and disclosure_date
                self.logger.info(f"Successfully processed share buyback for {stock_name}")
                self.logger.info(f"Extracted fields: {list(result.keys())}")
                self.logger.info(f"=== SHARE BUYBACK PROCESSOR DEBUG END ===")
                return result
            else:
                self.logger.warning(f"No share buyback data extracted for {stock_name}")
                self.logger.info(f"=== SHARE BUYBACK PROCESSOR DEBUG END ===")
                return None

        except Exception as e:
            self.logger.error(f"Error processing share buyback for {stock_name}: {e}")
            self.logger.info(f"=== SHARE BUYBACK PROCESSOR DEBUG END ===")
            return None

    def _debug_document_structure(self, soup: BeautifulSoup, stock_name: str):
        """Debug the document structure to understand share buyback format."""
        self.logger.info(f"=== DOCUMENT STRUCTURE DEBUG FOR {stock_name} ===")
        
        # Log basic document info
        title = soup.find("title")
        if title:
            self.logger.info(f"Document title: {title.get_text(strip=True)}")
        
        # Log company stock symbol
        stock_symbol = soup.find("span", {"id": "companyStockSymbol"})
        if stock_symbol:
            self.logger.info(f"Company stock symbol: {stock_symbol.get_text(strip=True)}")
        
        # Log all tables found
        all_tables = soup.find_all("table")
        self.logger.info(f"Found {len(all_tables)} tables in document")
        
        for i, table in enumerate(all_tables):
            self.logger.info(f"--- TABLE {i} ---")
            
            # Check for table caption
            table_caption = table.find("caption")
            if table_caption:
                caption_text = table_caption.get_text(strip=True)
                self.logger.info(f"Table {i} caption: '{caption_text}'")
            else:
                self.logger.info(f"Table {i}: NO CAPTION")
            
            # Check for table class
            table_class = table.get("class")
            if table_class:
                self.logger.info(f"Table {i} class: {table_class}")
            
            # Log first few rows to understand structure
            rows = table.find_all("tr")[:5]  # First 5 rows only
            for j, row in enumerate(rows):
                cells = row.find_all(["th", "td"])
                if cells:
                    cell_texts = [cell.get_text(strip=True)[:50] for cell in cells[:3]]  # First 3 cells, truncated
                    self.logger.info(f"Table {i} Row {j}: {cell_texts}")
        
        # Log all forms
        all_forms = soup.find_all("form")
        self.logger.info(f"Found {len(all_forms)} forms in document")
        
        for i, form in enumerate(all_forms):
            form_id = form.get("id")
            form_class = form.get("class")
            self.logger.info(f"Form {i}: id='{form_id}', class='{form_class}'")
            
            # Log form inputs
            inputs = form.find_all("input")[:10]  # First 10 inputs only
            for j, input_elem in enumerate(inputs):
                input_name = input_elem.get("name")
                input_type = input_elem.get("type")
                input_value = input_elem.get("value", "")[:30]  # Truncated
                self.logger.info(f"Form {i} Input {j}: name='{input_name}', type='{input_type}', value='{input_value}'")
        
        # Log any divs with specific classes that might contain data
        data_divs = soup.find_all("div", class_=re.compile(r"(data|content|report|buyback|transaction)"))
        self.logger.info(f"Found {len(data_divs)} potential data divs")
        
        for i, div in enumerate(data_divs[:5]):  # First 5 only
            div_class = div.get("class")
            div_text = div.get_text(strip=True)[:100]  # Truncated
            self.logger.info(f"Data div {i}: class='{div_class}', text='{div_text}'")
        
        self.logger.info(f"=== END DOCUMENT STRUCTURE DEBUG ===")

    def _extract_share_buyback_data(self, soup: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract data from share buyback document.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            report_date: Report date

        Returns:
            Dictionary containing share buyback data
        """
        table_data = {"stock_name": stock_name, "disclosure_date": report_date}
        
        self.logger.info(f"Starting data extraction for {stock_name}")
        
        # Strategy 1: Look for tables with share buyback related captions
        self._extract_from_captioned_tables(soup, table_data)
        
        # Strategy 2: Look for tables with specific classes
        self._extract_from_classed_tables(soup, table_data)
        
        # Strategy 3: Look for form data
        self._extract_from_forms(soup, table_data)
        
        # Strategy 4: General table scanning for key-value pairs
        self._extract_from_general_tables(soup, table_data)
        
        self.logger.info(f"Final extracted data for {stock_name}: {table_data}")
        return table_data

    def _extract_from_captioned_tables(self, soup: BeautifulSoup, table_data: Dict):
        """Extract data from tables with relevant captions."""
        self.logger.info("Strategy 1: Searching for captioned tables")
        
        # Look for tables with buyback-related captions
        buyback_keywords = ["buyback", "buy-back", "share", "transaction", "repurchase"]
        
        all_tables = soup.find_all("table")
        for i, table in enumerate(all_tables):
            table_caption = table.find("caption")
            if table_caption:
                caption_text = table_caption.get_text(strip=True).lower()
                self.logger.info(f"Checking table {i} caption: '{caption_text}'")
                
                # Check if caption contains buyback keywords
                if any(keyword in caption_text for keyword in buyback_keywords):
                    self.logger.info(f"Found buyback table with caption: '{caption_text}'")
                    self._extract_table_rows(table, table_data, f"captioned_table_{i}")

    def _extract_from_classed_tables(self, soup: BeautifulSoup, table_data: Dict):
        """Extract data from tables with specific classes."""
        self.logger.info("Strategy 2: Searching for classed tables")
        
        # Look for tables with common PSE classes
        common_classes = ["type1", "type2", "data", "report", "form"]
        
        for class_name in common_classes:
            tables = soup.find_all("table", class_=class_name)
            for i, table in enumerate(tables):
                self.logger.info(f"Found table with class '{class_name}' #{i}")
                self._extract_table_rows(table, table_data, f"classed_table_{class_name}_{i}")

    def _extract_from_forms(self, soup: BeautifulSoup, table_data: Dict):
        """Extract data from form elements."""
        self.logger.info("Strategy 3: Searching forms")
        
        all_forms = soup.find_all("form")
        for i, form in enumerate(all_forms):
            self.logger.info(f"Processing form {i}")
            
            # Extract input values
            inputs = form.find_all("input")
            for input_elem in inputs:
                input_name = input_elem.get("name")
                input_value = input_elem.get("value")
                
                if input_name and input_value:
                    field_name = f"form_{i}_{input_name}"
                    table_data[field_name] = input_value
                    self.logger.info(f"Extracted form data: {field_name} = {input_value}")

    def _extract_from_general_tables(self, soup: BeautifulSoup, table_data: Dict):
        """Extract data from general table scanning."""
        self.logger.info("Strategy 4: General table scanning")
        
        all_tables = soup.find_all("table")
        for i, table in enumerate(all_tables):
            self.logger.info(f"Scanning table {i} for key-value pairs")
            self._extract_table_rows(table, table_data, f"general_table_{i}")

    def _extract_table_rows(self, table: BeautifulSoup, table_data: Dict, source: str):
        """Extract key-value pairs from table rows."""
        rows = table.find_all("tr")
        self.logger.info(f"Processing {len(rows)} rows from {source}")
        
        for j, row in enumerate(rows):
            cells = row.find_all(["th", "td"])
            
            # Look for 2-column key-value pairs
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                
                if key and value:
                    # Clean up the key
                    clean_key = re.sub(r"[^\w\s]", " ", key).strip()
                    clean_key = re.sub(r"\s+", " ", clean_key)
                    
                    field_name = f"{source}_{clean_key}"
                    table_data[field_name] = value
                    self.logger.info(f"Extracted from {source} row {j}: {field_name} = {value}")
            
            # Look for multi-column data rows
            elif len(cells) > 2:
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                if any(cell_texts):  # If any cell has content
                    row_data = " | ".join(cell_texts)
                    field_name = f"{source}_row_{j}"
                    table_data[field_name] = row_data
                    self.logger.info(f"Extracted multi-column from {source} row {j}: {row_data}")