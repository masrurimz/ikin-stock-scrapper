"""
Processor for share buyback transaction reports.
"""

import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup

from ...utils import clean_text, parse_date_registered


class ShareBuybackProcessor:
    """Processor for share buyback transaction report data."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process share buyback transaction report - returns latest record only in UAT #3 format.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing UAT #3 formatted data (latest record only)
        """
        try:
            self.logger.info(f"Processing share buyback for {stock_name} on {disclosure_date} (UAT #3 format)")
            
            # Extract structured share buyback data in UAT #3 format
            result = self._extract_buyback_data(soup, stock_name, disclosure_date)
            
            if result and len(result) > 2:  # More than stock_name and disclosure_date
                self.logger.info(f"Successfully processed share buyback for {stock_name} in UAT #3 format")
                self.logger.info(f"Latest record with {len(result)} fields extracted")
                return result
            else:
                self.logger.warning(f"No share buyback data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing share buyback for {stock_name}: {e}")
            return None

    def _extract_buyback_data(self, soup: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract share buyback data in UAT #3 format (latest record only).

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            report_date: Report date

        Returns:
            Dictionary containing UAT #3 formatted share buyback data
        """
        # Check if this is an amended report
        page_content = soup.get_text()
        is_amended = ("[Amend" in page_content or "Amend-" in page_content or 
                     "amended" in page_content.lower() or "amendment" in page_content.lower())
        
        # Debug logging for amendment detection
        self.logger.info(f"Amendment detection for {stock_name} on {report_date}: {is_amended}")
        if is_amended:
            self.logger.info(f"Amendment keywords found in document content")
        
        # Extract core data
        transactions = self._extract_transaction_details(soup)
        program_summary = self._extract_program_summary(soup)
        
        # Extract Date Registered for UAT #3 format
        date_registered_info = self._extract_date_registered(soup)
        
        # Always return UAT #3 format (simplified: latest record only)
        if date_registered_info:
            # Use Date Registered from document
            result = {
                "stock_symbol": f"_SRP_{stock_name}",
                "Date_Registered": date_registered_info["full_date"],
                "Month": date_registered_info["month"],
                "Year": date_registered_info["year"],
                "Default_value_of_1": 1,
                "Day": date_registered_info["day"],
                "Total_Number_of_Shares_Purchased": transactions.get("total_shares_purchased", 0) if transactions else 0,
                "Total_Amount_Appropriated": program_summary.get("total_program_budget", 0) if program_summary else 0,
                "Cumulative_Shares_Purchased": program_summary.get("cumulative_shares_purchased", 0) if program_summary else 0,
                "Total_Amount_of_Shares_Repurchased": program_summary.get("total_amount_spent", 0) if program_summary else 0,
            }
            self.logger.info(f"UAT #3 format for {stock_name}: {result}")
        else:
            # Fallback: use disclosure_date for date parsing
            fallback_date_info = parse_date_registered(report_date)
            if fallback_date_info:
                result = {
                    "stock_symbol": f"_SRP_{stock_name}",
                    "Date_Registered": fallback_date_info[0],
                    "Month": fallback_date_info[1],
                    "Year": fallback_date_info[2],
                    "Default_value_of_1": 1,
                    "Day": fallback_date_info[3],
                    "Total_Number_of_Shares_Purchased": transactions.get("total_shares_purchased", 0) if transactions else 0,
                    "Total_Amount_Appropriated": program_summary.get("total_program_budget", 0) if program_summary else 0,
                    "Cumulative_Shares_Purchased": program_summary.get("cumulative_shares_purchased", 0) if program_summary else 0,
                    "Total_Amount_of_Shares_Repurchased": program_summary.get("total_amount_spent", 0) if program_summary else 0,
                }
                self.logger.info(f"UAT #3 format for {stock_name} using disclosure_date fallback: {result}")
            else:
                # Last resort: minimal UAT #3 structure 
                result = {
                    "stock_symbol": f"_SRP_{stock_name}",
                    "Date_Registered": report_date,
                    "Month": 0,
                    "Year": 0,
                    "Default_value_of_1": 1,
                    "Day": 0,
                    "Total_Number_of_Shares_Purchased": transactions.get("total_shares_purchased", 0) if transactions else 0,
                    "Total_Amount_Appropriated": program_summary.get("total_program_budget", 0) if program_summary else 0,
                    "Cumulative_Shares_Purchased": program_summary.get("cumulative_shares_purchased", 0) if program_summary else 0,
                    "Total_Amount_of_Shares_Repurchased": program_summary.get("total_amount_spent", 0) if program_summary else 0,
                }
                self.logger.warning(f"Using minimal UAT #3 format for {stock_name} (date parsing failed)")
        
        return result

    def _extract_transaction_details(self, soup: BeautifulSoup) -> Dict:
        """Extract transaction details from buyback table."""
        self.logger.info("Extracting transaction details")
        
        # Look for table with caption containing "share buy-back transaction"
        for table in soup.find_all("table"):
            caption = table.find("caption")
            if caption and "share buy-back transaction" in caption.get_text().lower():
                self.logger.info("Found share buyback transaction table")
                return self._parse_transaction_table(table)
        
        return {}

    def _parse_transaction_table(self, table: BeautifulSoup) -> Dict:
        """Parse the transaction table to extract structured data."""
        transactions = []
        total_shares = 0
        weighted_avg_price = 0
        total_value = 0
        
        rows = table.find_all("tr")
        header_found = False
        
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 3:
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Skip header row
                if not header_found and "Date" in cell_texts[0]:
                    header_found = True
                    continue
                
                # Parse transaction rows
                if header_found and cell_texts[0] and any(month in cell_texts[0] for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                    date_str = cell_texts[0]
                    shares_str = cell_texts[1].replace(",", "") if len(cell_texts) > 1 else ""
                    price_str = cell_texts[2] if len(cell_texts) > 2 else ""
                    
                    try:
                        shares = int(shares_str) if shares_str.isdigit() else 0
                        price = float(price_str) if price_str.replace(".", "").replace(",", "").isdigit() else 0
                        
                        if shares > 0 and price > 0:
                            transaction = {
                                "date": date_str,
                                "shares": shares,
                                "price": price,
                                "value": shares * price
                            }
                            transactions.append(transaction)
                            total_shares += shares
                            total_value += transaction["value"]
                            
                            self.logger.info(f"Transaction: {date_str}, {shares:,} shares @ ₱{price}")
                    except (ValueError, IndexError):
                        continue
        
        # Calculate weighted average price
        if total_shares > 0:
            weighted_avg_price = total_value / total_shares
        
        result = {
            "total_transactions": len(transactions),
            "total_shares_purchased": total_shares,
            "weighted_average_price": round(weighted_avg_price, 2),
            "total_transaction_value": round(total_value, 2)
        }
        
        return result

    def _extract_share_effects(self, soup: BeautifulSoup) -> Dict:
        """Extract before/after share effects."""
        self.logger.info("Extracting share effects")
        
        # Look for table with caption containing "effects on number of shares"
        for table in soup.find_all("table"):
            caption = table.find("caption")
            if caption and "effects on number of shares" in caption.get_text().lower():
                self.logger.info("Found share effects table")
                return self._parse_effects_table(table)
        
        return {}

    def _parse_effects_table(self, table: BeautifulSoup) -> Dict:
        """Parse the effects table to extract before/after data."""
        result = {}
        
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 3:
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                if "Outstanding Shares" in cell_texts[0]:
                    try:
                        before = int(cell_texts[1].replace(",", "")) if len(cell_texts) > 1 else 0
                        after = int(cell_texts[2].replace(",", "")) if len(cell_texts) > 2 else 0
                        result["outstanding_shares_before"] = before
                        result["outstanding_shares_after"] = after
                        result["outstanding_shares_change"] = before - after
                        
                        self.logger.info(f"Outstanding shares: {before:,} → {after:,}")
                    except ValueError:
                        pass
                
                elif "Treasury Shares" in cell_texts[0]:
                    try:
                        before = int(cell_texts[1].replace(",", "")) if len(cell_texts) > 1 else 0
                        after = int(cell_texts[2].replace(",", "")) if len(cell_texts) > 2 else 0
                        result["treasury_shares_before"] = before
                        result["treasury_shares_after"] = after
                        result["treasury_shares_change"] = after - before
                        
                        self.logger.info(f"Treasury shares: {before:,} → {after:,}")
                    except ValueError:
                        pass
        
        return result

    def _extract_program_summary(self, soup: BeautifulSoup) -> Dict:
        """Extract buyback program summary data."""
        self.logger.info("Extracting program summary")
        
        result = {}
        
        # Look for tables with key-value pairs
        for table in soup.find_all("table", class_="type1"):
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    if "Cumulative Number of Shares Purchased" in key:
                        try:
                            result["cumulative_shares_purchased"] = int(value.replace(",", ""))
                            self.logger.info(f"Cumulative shares: {result['cumulative_shares_purchased']:,}")
                        except ValueError:
                            pass
                    
                    elif "Total Amount Appropriated" in key:
                        try:
                            result["total_program_budget"] = float(value.replace(",", ""))
                            self.logger.info(f"Program budget: ₱{result['total_program_budget']:,.2f}")
                        except ValueError:
                            pass
                    
                    elif "Total Amount of Shares Repurchased" in key:
                        try:
                            result["total_amount_spent"] = float(value.replace(",", ""))
                            self.logger.info(f"Total spent: ₱{result['total_amount_spent']:,.2f}")
                        except ValueError:
                            pass
        
        return result

    def _extract_date_registered(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract Date Registered field from the document."""
        self.logger.info("Extracting Date Registered")
        
        # Pattern 1: Look in type1 tables for key-value pairs
        for table in soup.find_all("table", class_="type1"):
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    if "Date Registered" in key:
                        date_info = parse_date_registered(value)
                        if date_info:
                            self.logger.info(f"Found Date Registered: {value} -> {date_info[0]}")
                            return {
                                "full_date": date_info[0],
                                "month": date_info[1],
                                "year": date_info[2],
                                "day": date_info[3]
                            }
        
        # Pattern 2: Text-based search across all tables
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    if "Date Registered" in cell_text and i + 1 < len(cells):
                        value = cells[i + 1].get_text(strip=True)
                        date_info = parse_date_registered(value)
                        if date_info:
                            self.logger.info(f"Found Date Registered: {value} -> {date_info[0]}")
                            return {
                                "full_date": date_info[0],
                                "month": date_info[1],
                                "year": date_info[2],
                                "day": date_info[3]
                            }
        
        # Pattern 3: Search for any element containing "Date Registered"
        date_registered_element = soup.find(string=lambda text: text and "Date Registered" in text if text else False)
        if date_registered_element:
            # Find the next sibling or cell that might contain the date value
            parent = date_registered_element.parent
            if parent:
                next_cell = parent.find_next("td")
                if next_cell:
                    value = next_cell.get_text(strip=True)
                    date_info = parse_date_registered(value)
                    if date_info:
                        self.logger.info(f"Found Date Registered: {value} -> {date_info[0]}")
                        return {
                            "full_date": date_info[0],
                            "month": date_info[1],
                            "year": date_info[2],
                            "day": date_info[3]
                        }
        
        self.logger.warning("Date Registered field not found in document")
        return None

    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information."""
        self.logger.info("Extracting contact information")
        
        result = {}
        
        # Look for tables with contact info (usually type2 class)
        for table in soup.find_all("table", class_="type2"):
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    if "Name" in key:
                        result["contact_name"] = value
                        self.logger.info(f"Contact name: {value}")
                    
                    elif "Designation" in key:
                        result["contact_designation"] = value
                        self.logger.info(f"Contact designation: {value}")
        
        return result