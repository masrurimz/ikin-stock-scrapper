"""
Core PSE data scraper implementation.
"""

import re
import json
import csv
import os
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

from ..models.report_types import ReportType
from ..utils.http_client import HTTPClient
from ..utils.logging_config import setup_logging
from ..utils import (
    clean_text, parse_date, extract_edge_no, convert_to_numeric, clean_stockholders_text
)


class PSEDataScraper:
    """
    Main class for scraping data from PSE Edge.
    Handles the process of fetching and processing data from various report types.
    """

    def __init__(
        self,
        max_workers: int = 5,
        use_proxies: bool = False,
        enable_logging: bool = True,
        cli_mode: bool = False,
    ):
        """
        Initialize basic configuration and requests session.

        Args:
            max_workers: Number of workers for concurrent processing
            use_proxies: Flag to use proxy rotation
            enable_logging: Flag to enable/disable logging
            cli_mode: Flag to enable CLI mode with quiet logging
        """
        self.BASE_URL = "https://edge.pse.com.ph"
        self.FORM_ACTION_URL = f"{self.BASE_URL}/companyDisclosures/search.ax"
        self.OPEN_DISC_URL = f"{self.BASE_URL}/openDiscViewer.do"

        self.data = []
        self.max_workers = max_workers
        self.stop_iteration = False

        # Setup logging first (needed for _load_proxies)
        if cli_mode and enable_logging:
            # Use quiet logger for CLI mode to avoid interfering with Rich output
            from ..utils.logging_config import get_quiet_logger
            self.logger = get_quiet_logger("PSEDataScraper.CLI")
        else:
            # Standard logging for non-CLI usage
            self.logger = setup_logging(enable_logging)
        
        # Setup HTTP client
        proxies = self._load_proxies() if use_proxies else []
        self.http_client = HTTPClient(use_proxies=use_proxies, proxies=proxies)

    def _load_proxies(self) -> List[str]:
        """
        Load proxy list from file.
        File format: one proxy per line (ip:port)
        """
        try:
            with open("proxies.txt", "r") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.logger.warning("File proxies.txt not found")
            return []

    def _get_soup(self, response) -> Optional[BeautifulSoup]:
        """
        Create BeautifulSoup object from HTTP response.

        Args:
            response: Response object from requests

        Returns:
            BeautifulSoup object for HTML parsing
        """
        if not response:
            return None
        return BeautifulSoup(response.text, "html.parser")

    def _extract_table_data(
        self, table: BeautifulSoup, stock_name: str, report_date: str
    ) -> Dict:
        """
        Extract data from table.

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
                table_data[key] = value

        return table_data

    def _process_table_grid(self, table: BeautifulSoup) -> List[List[str]]:
        """
        Extract data from table grid.

        Args:
            table: BeautifulSoup object of the table

        Returns:
            List of Lists containing table grid data
        """
        rows = table.find_all("tr")
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

    def scrape_data(self, company_id: str, report_type: ReportType, progress_callback=None, simplified: bool = False) -> List[Dict]:
        """
        Scrape data from PSE Edge with concurrent processing.

        Args:
            company_id: Company ID
            report_type: Report type
            progress_callback: Optional callback function for progress updates
            simplified: If True, return simplified output format with latest data only
            
        Returns:
            List of dictionaries containing scraped data
        """
        try:
            if progress_callback:
                progress_callback("initializing", f"Starting scraper for {company_id}")
                
            # Auto-enable simplified mode for share buyback reports (UAT Feedback #2)
            if report_type == ReportType.SHARE_BUYBACK:
                simplified = True
                self.logger.info(f"Auto-enabled simplified mode for share buyback report (UAT Feedback #2)")
                
            self.logger.info(
                f"Starting data scraping for company_id: {company_id}, report_type: {report_type.value}, simplified: {simplified}"
            )
            self.stop_iteration = False
            self.simplified_mode = simplified  # Store simplified flag for processors

            payload = {
                "keyword": company_id,
                "tmplNm": report_type.value,
                "sortType": "date",
                "dateSortType": "DESC",
            }

            if progress_callback:
                progress_callback("searching", f"Searching PSE database for {company_id}")

            response = self.http_client.make_request(self.FORM_ACTION_URL, "post", data=payload)
            if not response:
                self.logger.error(f"Failed to get initial data for company_id: {company_id}")
                if progress_callback:
                    progress_callback("error", f"Failed to connect to PSE database")
                return []

            if progress_callback:
                progress_callback("parsing", "Parsing search results")

            soup = self._get_soup(response)
            if not soup:
                if progress_callback:
                    progress_callback("error", "Failed to parse search results")
                return []

            pages_count = self._get_pages_count(soup)
            if not pages_count:
                if progress_callback:
                    progress_callback("empty", "No reports found")
                return []

            self.logger.info(f"Found {pages_count} pages to process")
            
            if progress_callback:
                progress_callback("processing", f"Found {pages_count} page(s) of results")

            if progress_callback:
                worker_info = f"using {self.max_workers} worker(s)" if self.max_workers > 1 else "single-threaded"
                progress_callback("downloading", f"Starting parallel processing {worker_info}")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for page in range(1, pages_count + 1):
                    payload["pageNo"] = page
                    futures.append(
                        executor.submit(self._process_page, payload.copy(), report_type)
                    )

                completed_pages = 0
                total_pages = len(futures)
                for future in as_completed(futures):
                    try:
                        future.result()
                        completed_pages += 1
                        if progress_callback:
                            if self.max_workers > 1:
                                progress_callback("downloading", f"Pages completed: {completed_pages}/{total_pages} (concurrent processing)")
                            else:
                                progress_callback("downloading", f"Processing page {completed_pages}/{total_pages}")
                    except Exception as e:
                        self.logger.error(f"Error in concurrent processing: {e}")
                        if progress_callback:
                            progress_callback("warning", f"Error processing page: {str(e)[:50]}...")
                            
            # For simplified mode, return only the latest record per company/symbol
            if simplified and self.data:
                self.logger.info(f"Simplified mode: Filtering to latest record per company from {len(self.data)} total records")
                
                # Group records by company symbol/name and keep only the latest (first) for each
                latest_per_company = {}
                for record in self.data:
                    # Get company identifier (symbol for share buyback, stock name for others)
                    company_id = record.get('symbol') or record.get('stock name') or record.get('company_name') or record.get('stock_name')
                    if company_id and company_id not in latest_per_company:
                        latest_per_company[company_id] = record
                
                # Convert back to list, preserving original order
                self.data = list(latest_per_company.values())
                self.logger.info(f"Simplified mode: Kept {len(self.data)} latest records for {len(latest_per_company)} companies")
                            
            if progress_callback:
                records_found = len(self.data)
                if records_found > 0:
                    if simplified:
                        progress_callback("success", f"Found latest record (simplified mode)")
                    else:
                        progress_callback("success", f"Found {records_found} record(s)")
                else:
                    progress_callback("empty", "No data found in reports")
                        
            return self.data
        except Exception as e:
            self.logger.error(f"Error in scrape_data: {e}")
            if progress_callback:
                progress_callback("error", f"Scraping failed: {str(e)[:50]}...")
            return []

    def _get_pages_count(self, soup: BeautifulSoup) -> int:
        """
        Get number of pages from search results.

        Args:
            soup: BeautifulSoup object from search results

        Returns:
            Number of pages (defaults to 1 if not found)
        """
        count_elem = soup.find("span", {"class": "count"})
        if not count_elem:
            return 1

        text = count_elem.get_text()
        
        # Try different patterns for page count
        # Pattern 1: "1 / 5" format
        match = re.search(r"\d+\s*/\s*(\d+)", text)
        if match:
            return int(match.group(1))
        
        # Pattern 2: "Showing 1-20 of 100 results" format
        match = re.search(r"of\s+(\d+)\s+results?", text, re.IGNORECASE)
        if match:
            total_results = int(match.group(1))
            # Calculate pages assuming 20 results per page
            return (total_results + 19) // 20  # Ceiling division
        
        return 1

    def _process_page(self, payload: Dict, report_type: ReportType) -> None:
        """
        Process search results page.

        Args:
            payload: Payload data for request
            report_type: Report type
        """
        try:
            response = self.http_client.make_request(self.FORM_ACTION_URL, "post", data=payload)
            if not response:
                return

            soup = self._get_soup(response)
            if not soup:
                return

            self._process_document_rows(soup, report_type)
        except Exception as e:
            self.logger.error(f"Error processing page: {e}")

    def _process_document_rows(self, soup: BeautifulSoup, report_type: ReportType) -> None:
        """
        Process document rows from search results.

        Args:
            soup: BeautifulSoup object from search results
            report_type: Report type
        """
        rows = soup.find_all("td")
        if not rows:
            return

        if report_type == ReportType.PUBLIC_OWNERSHIP:
            self._process_single_row(rows, report_type)
        elif report_type == ReportType.ANNUAL:
            self._process_single_row(rows, report_type)
        elif report_type == ReportType.SHARE_BUYBACK:
            self._process_single_row(rows, report_type)
        elif report_type == ReportType.TOP_100_STOCKHOLDERS:
            self._process_stockholders_rows(rows, report_type)
        elif report_type == ReportType.CASH_DIVIDENDS:
            self._process_cash_dividends_rows(rows, report_type)
        else:
            self._process_other_rows(rows, report_type)

    def _process_single_row(self, rows, report_type: ReportType):
        """Process single row for reports that only need first entry."""
        if not rows:
            return

        row = rows[0]
        links = row.find_all("a", onclick=True)
        if not links:
            return

        date_cell = links[0].parent.find_next_sibling("td")
        if not date_cell:
            return

        disclosure_date = parse_date(date_cell.get_text(strip=True))
        if not disclosure_date:
            return

        edge_no = extract_edge_no(links[0].get("onclick", ""))
        if not edge_no:
            return

        self._process_document(edge_no, disclosure_date, report_type)

    def _process_stockholders_rows(self, rows, report_type: ReportType):
        """Process rows for stockholders report."""
        for row in rows:
            links = row.find_all("a", onclick=True)
            if not links:
                continue

            date_cell = links[0].parent.find_next_sibling("td")
            if not date_cell:
                continue

            PSE_Form_Number = (
                date_cell.find_next_sibling("td").get_text(strip=True)
                if date_cell.find_next_sibling("td").get_text(strip=True) == "17-12-A"
                else ""
            )
            if not PSE_Form_Number:
                continue

            disclosure_date = parse_date(date_cell.get_text(strip=True))
            if not disclosure_date:
                continue

            edge_no = extract_edge_no(links[0].get("onclick", ""))
            if not edge_no:
                continue

            self._process_document(edge_no, disclosure_date, report_type)
            return

    def _process_cash_dividends_rows(self, rows, report_type: ReportType):
        """Process rows for cash dividends report."""
        for row in rows:
            links = row.find_all("a", onclick=True)
            if not links:
                continue

            date_cell = links[0].parent.find_next_sibling("td")
            if not date_cell:
                continue

            PSE_Form_Number = date_cell.find_next_sibling("td").get_text(strip=True)
            if not PSE_Form_Number:
                continue

            disclosure_date = parse_date(date_cell.get_text(strip=True))
            if not disclosure_date:
                continue

            edge_no = extract_edge_no(links[0].get("onclick", ""))
            if not edge_no:
                continue

            self._process_document(edge_no, disclosure_date, report_type)

    def _process_other_rows(self, rows, report_type: ReportType):
        """Process rows for other report types."""
        for row in rows:
            links = row.find_all("a", onclick=True)
            if not links:
                continue

            date_cell = links[0].parent.find_next_sibling("td")
            if not date_cell:
                continue

            PSE_Form_Number = date_cell.find_next_sibling("td").get_text(strip=True)
            if not PSE_Form_Number:
                continue

            disclosure_date = parse_date(date_cell.get_text(strip=True))
            if not disclosure_date:
                continue

            edge_no = extract_edge_no(links[0].get("onclick", ""))
            if not edge_no:
                continue

            self._process_document(edge_no, disclosure_date, report_type)
            return

    def _process_document(self, edge_no: str, disclosure_date: str, report_type: ReportType) -> None:
        """
        Process document from edge no.

        Args:
            edge_no: Edge number
            disclosure_date: Disclosure date
            report_type: Report type
        """
        response = self.http_client.make_request(self.OPEN_DISC_URL, params={"edge_no": edge_no})
        if not response:
            return

        soup = self._get_soup(response)
        if not soup:
            return

        iframe = soup.find("iframe")
        if not iframe or not iframe.get("src"):
            return

        iframe_src = urljoin(self.BASE_URL, iframe["src"])
        iframe_response = self.http_client.make_request(iframe_src)
        if not iframe_response:
            return

        iframe_soup = self._get_soup(iframe_response)
        if not iframe_soup:
            return

        stock_name = iframe_soup.find("span", {"id": "companyStockSymbol"})
        if not stock_name:
            return

        stock_name = stock_name.get_text(strip=True)

        # Process based on report type
        result = None
        if report_type == ReportType.PUBLIC_OWNERSHIP:
            from ..core.processors.public_ownership import PublicOwnershipProcessor
            processor = PublicOwnershipProcessor(self.logger)
            result = processor.process(iframe_soup, stock_name, disclosure_date)
        elif report_type == ReportType.ANNUAL:
            from ..core.processors.annual_report import AnnualReportProcessor
            processor = AnnualReportProcessor(self.logger)
            result = processor.process(iframe_soup, stock_name, disclosure_date)
        elif report_type == ReportType.QUARTERLY:
            from ..core.processors.quarterly_report import QuarterlyReportProcessor
            processor = QuarterlyReportProcessor(self.logger)
            result = processor.process(iframe_soup, stock_name, disclosure_date)
        elif report_type == ReportType.SHARE_BUYBACK:
            from ..core.processors.share_buyback import ShareBuybackProcessor
            processor = ShareBuybackProcessor(self.logger)
            result = processor.process(iframe_soup, stock_name, disclosure_date, simplified=getattr(self, 'simplified_mode', False))
            # Don't stop iteration for share buyback to capture all reports including amendments
            # But if simplified mode, stop after first successful result
            if getattr(self, 'simplified_mode', False) and result:
                self.stop_iteration = True
        elif report_type == ReportType.CASH_DIVIDENDS and not self.stop_iteration:
            from ..core.processors.cash_dividends import CashDividendsProcessor
            processor = CashDividendsProcessor(self.logger)
            result = processor.process(iframe_soup, stock_name, disclosure_date)
            if result:
                self.stop_iteration = True
        elif report_type == ReportType.TOP_100_STOCKHOLDERS and not self.stop_iteration:
            from ..core.processors.stockholders import StockholdersProcessor
            processor = StockholdersProcessor(self.logger)
            result = processor.process(iframe_soup, stock_name, disclosure_date)

        if result:
            self.data.append(result)

    def save_results(self, filename: str, formats: List[str] = ["csv"]) -> None:
        """
        Save scraping results to file with selected formats.

        Args:
            filename: Output filename (without extension)
            formats: List of desired file formats ('json' and/or 'csv')
        """
        if not self.data:
            self.logger.info("No data to save")
            print("No data to save")
            return

        saved_files = []

        # JSON saving
        if "json" in formats:
            try:
                with open(f"{filename}.json", "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
                saved_files.append(f"{filename}.json")
            except Exception as e:
                self.logger.error(f"Error saving JSON file: {e}")
                print(f"Error saving JSON file: {e}")

        # CSV saving
        if "csv" in formats:
            try:
                if len(self.data) > 0:
                    with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        headers = self.data[0].keys()
                        writer.writerow(headers)
                        for row in self.data:
                            writer.writerow(row.values())
                    saved_files.append(f"{filename}.csv")
                else:
                    with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["No data found"])
                    saved_files.append(f"{filename}.csv")
                    self.logger.warning("Created CSV file with no data")
            except Exception as e:
                self.logger.error(f"Error saving CSV file: {e}")
                print(f"Error saving CSV file: {e}")

        if saved_files:
            saved_files_str = " and ".join(saved_files)
            self.logger.info(f"Results saved to {saved_files_str}")
            print(f"Results saved to {saved_files_str}")

        if not saved_files:
            self.logger.error("Failed to save file in any format")
            print("Failed to save file in any format")
