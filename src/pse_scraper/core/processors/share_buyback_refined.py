"""
Refined processor for share buyback transaction reports based on real data analysis.
"""

import re
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from datetime import datetime

from ...utils import clean_text, convert_to_numeric


class ShareBuybackProcessorRefined:
    """Refined processor for share buyback transaction report data."""

    def __init__(self, logger):
        self.logger = logger

    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process share buyback transaction report with refined extraction.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            disclosure_date: Disclosure date

        Returns:
            Dictionary containing processed data
        """
        try:
            self.logger.info(f"Processing refined share buyback for {stock_name} on {disclosure_date}")
            
            # Extract structured share buyback data
            result = self._extract_refined_buyback_data(soup, stock_name, disclosure_date)
            
            if result and len(result) > 2:  # More than stock_name and disclosure_date
                self.logger.info(f"Successfully processed refined share buyback for {stock_name}")
                self.logger.info(f"Extracted transactions: {result.get('total_transactions', 0)}")
                self.logger.info(f"Total shares purchased: {result.get('total_shares_purchased', 0)}")
                return result
            else:
                self.logger.warning(f"No refined share buyback data extracted for {stock_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error processing refined share buyback for {stock_name}: {e}")
            return None

    def _extract_refined_buyback_data(self, soup: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """
        Extract refined share buyback data based on discovered structure.

        Args:
            soup: BeautifulSoup object of the document
            stock_name: Stock name
            report_date: Report date

        Returns:
            Dictionary containing refined share buyback data
        """
        result = {
            "stock_name": stock_name,
            "disclosure_date": report_date
        }
        
        # Extract transaction details
        transactions = self._extract_transaction_details(soup)
        if transactions:
            result.update(transactions)
        
        # Extract before/after share counts
        share_effects = self._extract_share_effects(soup)
        if share_effects:
            result.update(share_effects)
        
        # Extract program summary
        program_summary = self._extract_program_summary(soup)
        if program_summary:
            result.update(program_summary)
        
        # Extract contact information
        contact_info = self._extract_contact_info(soup)
        if contact_info:
            result.update(contact_info)
        
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
                if header_found and cell_texts[0] and "," in cell_texts[0]:  # Date format check
                    date_str = cell_texts[0]
                    shares_str = cell_texts[1].replace(",", "") if len(cell_texts) > 1 else ""
                    price_str = cell_texts[2] if len(cell_texts) > 2 else ""
                    
                    try:
                        shares = int(shares_str) if shares_str.isdigit() else 0
                        price = float(price_str) if price_str.replace(".", "").isdigit() else 0
                        
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
            "total_transaction_value": round(total_value, 2),
            "transactions": transactions
        }
        
        # Add individual transaction details
        for i, txn in enumerate(transactions[:5]):  # Limit to first 5 transactions
            result[f"transaction_{i+1}_date"] = txn["date"]
            result[f"transaction_{i+1}_shares"] = txn["shares"]
            result[f"transaction_{i+1}_price"] = txn["price"]
            result[f"transaction_{i+1}_value"] = txn["value"]
        
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