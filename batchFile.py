"""
Program Scraping Data PSE (Philippine Stock Exchange)
Program ini digunakan untuk mengambil data keuangan dari platform PSE Edge.

Fitur:
1. Public Ownership Report
2. Quarterly Report
3. Annual Report
4. List of Top 100 Stockholders
5. Declaration of Cash Dividends

Penggunaan:
1. Pilih jenis laporan (1-5)
2. Masukkan nama file output
3. Masukkan nomor iterasi awal
4. Masukkan nomor iterasi akhir (opsional)
5. Data akan disimpan dalam format JSON dan CSV
"""

#------------------------------------------------------------------------------
# 1. IMPORTS DAN SETUP
#------------------------------------------------------------------------------
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
import csv
import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
import logging.handlers
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from requests.exceptions import RequestException, ProxyError
import time
import os


#------------------------------------------------------------------------------
# 2. ENUMS DAN KONSTANTA
#------------------------------------------------------------------------------
class ReportType(Enum):
    """Enum untuk jenis-jenis laporan yang tersedia"""

    PUBLIC_OWNERSHIP = "Public Ownership Report"
    QUARTERLY = "Quarterly Report"
    ANNUAL = "Annual Report"
    TOP_100_STOCKHOLDERS = "List of Top 100 Stockholders"
    CASH_DIVIDENDS = "Declaration of Cash Dividends"


#------------------------------------------------------------------------------
# 3. KELAS UTAMA
#------------------------------------------------------------------------------
class PSEDataScraper:
    """
    Kelas utama untuk scraping data dari PSE Edge.
    Menangani proses pengambilan dan pemrosesan data dari berbagai jenis laporan.
    """

    #--------------------------------------------------------------------------
    # 3.1 INISIALISASI DAN SETUP
    #--------------------------------------------------------------------------
    def __init__(
        self,
        max_workers: int = 5,
        use_proxies: bool = False,
        enable_logging: bool = True,
    ):
        """
        Inisialisasi konfigurasi dasar dan sesi requests.

        Args:
            max_workers: Jumlah worker untuk concurrent processing
            use_proxies: Flag untuk menggunakan proxy
            enable_logging: Flag untuk mengaktifkan/nonaktifkan logging
        """
        self.BASE_URL = "https://edge.pse.com.ph"
        self.FORM_ACTION_URL = f"{self.BASE_URL}/companyDisclosures/search.ax"
        self.OPEN_DISC_URL = f"{self.BASE_URL}/openDiscViewer.do"

        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        self.session = requests.Session()
        self.data = []
        self.max_workers = max_workers
        self.use_proxies = use_proxies
        self.proxies = self._load_proxies() if use_proxies else []
        self.enable_logging = enable_logging
        self.stop_iteration = False

        # Setup logging jika diaktifkan
        if enable_logging:
            self._setup_logging()
        else:
            self.logger = self._get_null_logger()

    def _get_null_logger(self):
        """Membuat logger yang tidak melakukan apa-apa ketika logging dinonaktifkan"""
        logger = logging.getLogger("null")
        logger.setLevel(logging.CRITICAL)  # Set level sangat tinggi
        logger.addHandler(logging.NullHandler())
        logger.propagate = False  # Mencegah propagasi ke root logger
        return logger

    def _setup_logging(self):
        """Konfigurasi sistem logging"""
        if not os.path.exists("logs"):
            os.makedirs("logs")

        self.logger = logging.getLogger("PSEDataScraper")
        self.logger.setLevel(logging.INFO)

        # File handler untuk semua log
        fh = logging.handlers.RotatingFileHandler(
            "logs/pse_scraper.log", maxBytes=5 * 1024 * 1024, backupCount=5  # 5MB
        )
        fh.setLevel(logging.INFO)

        # File handler khusus untuk error
        error_fh = logging.handlers.RotatingFileHandler(
            "logs/pse_scraper_error.log", maxBytes=5 * 1024 * 1024, backupCount=5
        )
        error_fh.setLevel(logging.ERROR)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Format log
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        error_fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(error_fh)
        self.logger.addHandler(ch)

    def _load_proxies(self) -> List[str]:
        """
        Load daftar proxy dari file.
        Format file: satu proxy per baris (ip:port)
        """
        try:
            with open("proxies.txt", "r") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.logger.warning("File proxies.txt tidak ditemukan")
            return []

    def _get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Mengambil proxy secara random dari daftar"""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {"http": f"http://{proxy}", "https": f"https://{proxy}"}

    #--------------------------------------------------------------------------
    # 3.2 HTTP REQUEST UTILITIES
    #--------------------------------------------------------------------------
    def _make_request(
        self,
        url: str,
        method: str = "get",
        params: Dict = None,
        data: Dict = None,
        retries: int = 3,
        timeout: int = 30,
    ) -> Optional[requests.Response]:
        """
        Membuat HTTP request dengan penanganan error dan retry.

        Args:
            url: URL tujuan
            method: Metode HTTP (get/post)
            params: Parameter URL
            data: Data untuk request POST
            retries: Jumlah percobaan ulang jika gagal
            timeout: Timeout dalam detik

        Returns:
            Response object jika berhasil, None jika gagal
        """
        for attempt in range(retries):
            try:
                proxy = self._get_random_proxy() if self.use_proxies else None
                response = self.session.request(
                    method,
                    url,
                    headers=self.HEADERS,
                    params=params,
                    data=data,
                    proxies=proxy,
                    timeout=timeout,
                )
                response.raise_for_status()
                return response

            except ProxyError:
                self.logger.warning(f"Proxy error on attempt {attempt + 1}")
                if proxy and proxy["http"] in self.proxies:
                    self.proxies.remove(proxy["http"])

            except RequestException as e:
                self.logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return None

            time.sleep(random.uniform(1, 3))  # Random delay between retries

        return None

    def _get_soup(self, response: requests.Response) -> Optional[BeautifulSoup]:
        """
        Membuat objek BeautifulSoup dari response HTTP.

        Args:
            response: Response object dari requests

        Returns:
            BeautifulSoup object untuk parsing HTML
        """
        if not response:
            return None
        return BeautifulSoup(response.text, "html.parser")

    #--------------------------------------------------------------------------
    # 3.3 DATA PARSING UTILITIES
    #--------------------------------------------------------------------------
    def _clean_text(self, text: str) -> str:
        """
        Membersihkan teks dari karakter khusus.

        Args:
            text: Teks yang akan dibersihkan

        Returns:
            Teks yang sudah dibersihkan
        """
        return text.strip().replace(",", "").replace("%", "")

    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Mengubah format tanggal dari string ke format yang diinginkan.

        Args:
            date_str: String tanggal dari website

        Returns:
            String tanggal dalam format YYYY-MM-DD
        """
        try:
            return datetime.datetime.strptime(date_str, "%b %d, %Y %I:%M %p").strftime(
                "%Y-%m-%d"
            )
        except ValueError:
            self.logger.error(f"Error parsing date: {date_str}")
            return None

    def _extract_table_data(
        self, table: BeautifulSoup, stock_name: str, report_date: str
    ) -> Dict:
        """
        Mengambil data dari tabel.

        Args:
            table: BeautifulSoup object dari tabel
            stock_name: Nama saham
            report_date: Tanggal laporan

        Returns:
            Dictionary berisi data tabel
        """
        table_data = {"stock name": stock_name, "disclosure date": report_date}

        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) == 2:
                key = re.sub(
                    r"(?<=[A-Z])(?=[A-Z])", r" \t", cells[0].get_text(strip=True)
                )
                value = self._clean_text(cells[1].get_text())
                table_data[key] = value

        return table_data

    def _process_table_grid(self, table: BeautifulSoup) -> List[List[str]]:
        """
        Mengambil data dari tabel grid.

        Args:
            table: BeautifulSoup object dari tabel

        Returns:
            List of List berisi data tabel grid
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
        
    def _extract_edge_no(self, onclick: str) -> Optional[str]:
        """
        Mengambil edge no dari atribut onclick.

        Args:
            onclick: Atribut onclick dari tag HTML

        Returns:
            Edge no
        """
        match = re.search(r"openPopup\('(.+?)'\)", onclick)
        return match.group(1) if match else None

    #--------------------------------------------------------------------------
    # 3.4 MAIN SCRAPING PROCESS
    #--------------------------------------------------------------------------
    def scrape_data(self, company_id: str, report_type: ReportType) -> None:
        """
        Mengambil data dari PSE Edge dengan concurrent processing.

        Args:
            company_id: ID perusahaan
            report_type: Jenis laporan
        """
        try:
            self.logger.info(
                f"Starting data scraping for company_id: {company_id}, report_type: {report_type.value} URL {self.FORM_ACTION_URL}"
            )
            self.stop_iteration = False

            payload = {
                "keyword": company_id,
                "tmplNm": report_type.value,
                "sortType": "date",
                "dateSortType": "DESC",
                # "cmpySortType": "ASC"
            }

            response = self._make_request(self.FORM_ACTION_URL, "post", data=payload)
            if not response:
                self.logger.error(
                    f"Failed to get initial data for company_id: {company_id}"
                )
                return

            # self.logger.info(f"URL {self.FORM_ACTION_URL}")
            soup = self._get_soup(response)
            if not soup:
                return

            pages_count = self._get_pages_count(soup)
            if not pages_count:
                return

            self.logger.info(f"Found {pages_count} pages to process")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                for page in range(1, pages_count + 1):
                    payload["pageNo"] = page
                    futures.append(
                        executor.submit(self._process_page, payload.copy(), report_type)
                    )

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        self.logger.error(f"Error in concurrent processing: {e}")
        except Exception as e:
            self.logger.error(f"Error in scrape_data: {e}")

    def _get_pages_count(self, soup: BeautifulSoup) -> Optional[int]:
        """
        Mengambil jumlah halaman dari hasil pencarian.

        Args:
            soup: BeautifulSoup object dari hasil pencarian

        Returns:
            Jumlah halaman
        """
        count_elem = soup.find("span", {"class": "count"})
        if not count_elem:
            return None

        match = re.search(r"\d+\s*/\s*(\d+)", count_elem.get_text())
        return int(match.group(1)) if match else None

    def _process_page(self, payload: Dict, report_type: ReportType) -> None:
        """
        Memproses halaman hasil pencarian.

        Args:
            payload: Data payload untuk request
            report_type: Jenis laporan
        """
        try:
            response = self._make_request(self.FORM_ACTION_URL, "post", data=payload)
            if not response:
                return

            soup = self._get_soup(response)
            if not soup:
                return

            self._process_document_rows(soup, report_type)
        except Exception as e:
            self.logger.error(f"Error processing page: {e}")

    def _process_document_rows(
        self, soup: BeautifulSoup, report_type: ReportType
    ) -> None:
        """
        Memproses baris dokumen dari hasil pencarian.

        Args:
            soup: BeautifulSoup object dari hasil pencarian
            report_type: Jenis laporan
        """
        rows = soup.find_all("td")
        if not rows:
            return

        if report_type == ReportType.PUBLIC_OWNERSHIP:
            # Single row processing for Public Ownership
            if not rows:
                return

            row = rows[0]
            links = row.find_all("a", onclick=True)
            if not links:
                return

            date_cell = links[0].parent.find_next_sibling("td")
            if not date_cell:
                return

            disclosure_date = self._parse_date(date_cell.get_text(strip=True))
            if not disclosure_date:
                return

            edge_no = self._extract_edge_no(links[0].get("onclick", ""))
            if not edge_no:
                return

            self._process_document(edge_no, disclosure_date, report_type)
            return  # Berhenti setelah memproses satu data
        elif report_type == ReportType.ANNUAL:
            # Process only first valid row for quarterly
            if not rows:
                return

            row = rows[0]
            links = row.find_all("a", onclick=True)
            if not links:
                return

            date_cell = links[0].parent.find_next_sibling("td")
            if not date_cell:
                return

            disclosure_date = self._parse_date(date_cell.get_text(strip=True))
            if not disclosure_date:
                return

            edge_no = self._extract_edge_no(links[0].get("onclick", ""))
            if not edge_no:
                return
            if self.enable_logging:
                self.logger.info(
                    f"Processing edge_no: {edge_no}, disclosure_date: {disclosure_date}, report_type: {report_type.value}, date: {date_cell.get_text(strip=True)}"
                )
            self._process_document(edge_no, disclosure_date, report_type)
            return

        elif report_type == ReportType.TOP_100_STOCKHOLDERS:
            # Process only first valid row for stockholders
            for row in rows:
                links = row.find_all("a", onclick=True)
                if not links:
                    continue

                date_cell = links[0].parent.find_next_sibling("td")
                if not date_cell:
                    continue

                PSE_Form_Number = (
                    date_cell.find_next_sibling("td").get_text(strip=True)
                    if date_cell.find_next_sibling("td").get_text(strip=True)
                    == "17-12-A"
                    else ""
                )
                if not PSE_Form_Number:
                    continue

                disclosure_date = self._parse_date(date_cell.get_text(strip=True))
                if not disclosure_date:
                    continue

                edge_no = self._extract_edge_no(links[0].get("onclick", ""))
                if not edge_no:
                    continue

                self._process_document(edge_no, disclosure_date, report_type)
                return  # Berhenti setelah memproses satu data

        elif report_type == ReportType.CASH_DIVIDENDS:
            # Process only first valid row for cash dividends
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

                disclosure_date = self._parse_date(date_cell.get_text(strip=True))
                if not disclosure_date:
                    continue

                edge_no = self._extract_edge_no(links[0].get("onclick", ""))
                if not edge_no:
                    continue

                self._process_document(edge_no, disclosure_date, report_type)
                # return  # Berhenti setelah memproses satu data
        else:
            # Process only first valid row for other report types
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

                disclosure_date = self._parse_date(date_cell.get_text(strip=True))
                if not disclosure_date:
                    continue

                edge_no = self._extract_edge_no(links[0].get("onclick", ""))
                if not edge_no:
                    continue

                self._process_document(edge_no, disclosure_date, report_type)
                return  # Berhenti setelah memproses satu data

    def _process_document(
        self, edge_no: str, disclosure_date: str, report_type: ReportType
    ) -> None:
        """
        Memproses dokumen dari edge no.

        Args:
            edge_no: Edge no
            disclosure_date: Tanggal pengungkapan
            report_type: Jenis laporan
        """
        response = self._make_request(self.OPEN_DISC_URL, params={"edge_no": edge_no})
        if not response:
            return

        soup = self._get_soup(response)
        if not soup:
            return

        iframe = soup.find("iframe")
        if not iframe or not iframe.get("src"):
            return

        iframe_src = urljoin(self.BASE_URL, iframe["src"])
        iframe_response = self._make_request(iframe_src)
        if not iframe_response:
            return

        iframe_soup = self._get_soup(iframe_response)
        if not iframe_soup:
            return

        stock_name = iframe_soup.find("span", {"id": "companyStockSymbol"})
        if not stock_name:
            return

        stock_name = stock_name.get_text(strip=True)

        if report_type == ReportType.PUBLIC_OWNERSHIP:
            result = self._process_public_ownership(
                iframe_soup, stock_name, disclosure_date
            )
        elif report_type == ReportType.ANNUAL:
            result = self._process_annual_report(
                iframe_soup, stock_name, disclosure_date
            )
        elif report_type == ReportType.QUARTERLY:
            result = self._process_quarterly_report(iframe_soup, stock_name, disclosure_date)
        elif report_type == ReportType.CASH_DIVIDENDS and self.stop_iteration == False:
            result = self._process_cash_dividends(
                iframe_soup, stock_name, disclosure_date
            )
        elif (
            report_type == ReportType.TOP_100_STOCKHOLDERS
            and self.stop_iteration == False
        ):
            result = self._process_stockholders(
                iframe_soup, stock_name, disclosure_date
            )
        else:
            return

        if result:
            self.data.append(result)
            
    #--------------------------------------------------------------------------
    # 3.5 REPORT-SPECIFIC PROCESSING
    #--------------------------------------------------------------------------
    def _process_public_ownership(
        self, iframe_soup: BeautifulSoup, stock_name: str, report_date: str
    ) -> Optional[Dict]:
        """
        Memproses data kepemilikan publik.
        Mengambil data dari tabel laporan kepemilikan publik.

        Args:
            iframe_soup: BeautifulSoup object dari iframe
            stock_name: Nama saham
            report_date: Tanggal laporan

        Returns:
            Dictionary berisi data kepemilikan publik
        """
        # Inisialisasi dictionary untuk menyimpan data
        table_data = {"stock name": stock_name, "disclosure date": report_date}
        
        # Target fields yang ingin kita ekstrak
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
        
        # Cari semua tabel dalam HTML
        tables = iframe_soup.find_all('table')
        self.logger.info(f"Found {len(tables)} tables in the HTML")
        
        # Ekstrak Report Date dari halaman
        report_date_element = iframe_soup.find("tr", string=lambda text: text and "Report Date" in text if text else False)
        if report_date_element:
            report_date_value = report_date_element.find_next("td")
            if report_date_value:
                table_data["Report Date"] = report_date_value.get_text(strip=True)
                self.logger.info(f"Found Report Date: {table_data['Report Date']}")
        
        # Alternatif pencarian Report Date
        if "Report Date" not in table_data:
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2 and "Report Date" in cells[0].get_text(strip=True):
                        report_date_value = cells[1].get_text(strip=True)
                        table_data["Report Date"] = report_date_value
                        self.logger.info(f"Found Report Date (alternative): {table_data['Report Date']}")
                        break
        
        # Pertama, cari tabel dengan class='type1' yang biasanya berisi data yang kita cari
        for table in iframe_soup.find_all('table', class_='type1'):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    cell_text = cells[0].get_text(strip=True)
                    
                    # Periksa apakah baris ini berisi salah satu field target kita
                    for field_name, search_text in target_fields.items():
                        if search_text in cell_text:
                            # Coba ekstrak nilai dari sel kedua
                            value_span = cells[1].find('span', class_='valInput')
                            if value_span:
                                value = value_span.get_text(strip=True)
                                table_data[field_name] = value
                                self.logger.info(f"Found {field_name}: {value}")
                            else:
                                # Jika tidak ada span dengan class valInput, ambil teks langsung
                                value = cells[1].get_text(strip=True)
                                table_data[field_name] = value
                                self.logger.info(f"Found {field_name} (direct text): {value}")
        
        # Jika kita belum menemukan semua field, coba pendekatan yang lebih umum
        missing_fields = [field for field in target_fields.keys() if field not in table_data]
        if missing_fields:
            self.logger.info(f"Still missing fields: {missing_fields}. Trying more general approach...")
            
            # Coba pendekatan yang lebih umum untuk field yang hilang
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        cell_text = cells[0].get_text(strip=True)
                        
                        for field_name in list(missing_fields):  # Gunakan salinan untuk iterasi yang aman
                            search_text = target_fields[field_name]
                            if search_text in cell_text:
                                # Coba cara berbeda untuk mengekstrak nilai
                                value = None
                                
                                # Pertama coba cari span dengan class apapun
                                value_span = cells[1].find('span')
                                if value_span:
                                    value = value_span.get_text(strip=True)
                                else:
                                    # Jika tidak ada span, ambil teks langsung
                                    value = cells[1].get_text(strip=True)
                                
                                if value:
                                    table_data[field_name] = value
                                    self.logger.info(f"Found {field_name} (general approach): {value}")
                                    missing_fields.remove(field_name)
        
        # Penanganan khusus untuk Total Number of Non-Public Shares jika masih hilang
        if "Total Number of Non-Public Shares" in missing_fields:
            # Coba hitung dari nilai lain jika tersedia
            if "Number of Outstanding Common Shares" in table_data and "Total Number of Shares Owned by the Public" in table_data:
                try:
                    outstanding = int(table_data["Number of Outstanding Common Shares"].replace(',', ''))
                    public = int(table_data["Total Number of Shares Owned by the Public"].replace(',', ''))
                    non_public = outstanding - public
                    table_data["Total Number of Non-Public Shares"] = f"{non_public:,}"
                    self.logger.info(f"Calculated Total Number of Non-Public Shares: {table_data['Total Number of Non-Public Shares']}")
                except (ValueError, TypeError) as e:
                    self.logger.error(f"Could not calculate Non-Public Shares: {e}")
        
        # Konversi nilai-nilai string menjadi numerik
        numeric_data = {}
        for field, value in table_data.items():
            if field in target_fields.keys():
                if field == "Public Ownership Percentage":
                    # Konversi persentase menjadi float
                    try:
                        numeric_value = float(value.replace('%', ''))
                        table_data[field] = numeric_value
                    except (ValueError, TypeError, AttributeError):
                        pass  # Biarkan nilai asli jika konversi gagal
                else:
                    # Konversi nilai lain menjadi integer (menghapus koma)
                    try:
                        numeric_value = int(value.replace(',', ''))
                        table_data[field] = numeric_value
                    except (ValueError, TypeError, AttributeError):
                        pass  # Biarkan nilai asli jika konversi gagal
        
        return table_data

    def _process_annual_report(
        self, iframe_soup: BeautifulSoup, stock_name: str, report_date: str
    ) -> Optional[Dict]:
        """
        Memproses data laporan tahunan.
        Mengambil semua baris dari tabel laporan menggunakan pendekatan yang lebih robust
        dengan mencari baris berdasarkan label.

        Args:
            iframe_soup: BeautifulSoup object dari iframe
            stock_name: Nama saham
            report_date: Tanggal laporan

        Returns:
            Dictionary berisi data laporan tahunan
        """
        table_data = {"stock name": stock_name, "disclosure date": report_date}
        
        # Process each table in the document
        for table in iframe_soup.find_all("table"):
            table_caption = table.find("caption")
            
            # Process Balance Sheet
            if table_caption and table_caption.get_text(strip=True).lower() == "balance sheet":
                grid = self._process_table_grid(table)
                if grid:
                    try:
                        # Find the correct row indices by looking for specific row labels
                        current_assets_row = None
                        total_assets_row = None
                        current_liabilities_row = None
                        total_liabilities_row = None
                        retained_earnings_row = None
                        stockholders_equity_row = None
                        stockholders_equity_parent_row = None
                        book_value_row = None
                        
                        # Find the rows by their labels
                        for i, row in enumerate(grid):
                            if len(row) > 0:
                                row_label = row[0].lower()
                                if 'current assets' in row_label:
                                    current_assets_row = i
                                elif 'total assets' in row_label:
                                    total_assets_row = i
                                elif 'current liabilities' in row_label:
                                    current_liabilities_row = i
                                elif 'total liabilities' in row_label:
                                    total_liabilities_row = i
                                elif 'retained earnings' in row_label or 'deficit' in row_label:
                                    retained_earnings_row = i
                                elif "stockholders' equity" in row_label and 'parent' not in row_label:
                                    stockholders_equity_row = i
                                elif "stockholders' equity - parent" in row_label or ('parent' in row_label and 'equity' in row_label):
                                    stockholders_equity_parent_row = i
                                elif 'book value' in row_label:
                                    book_value_row = i
                        
                        # Extract values using the identified row indices
                        if current_assets_row is not None and len(grid[current_assets_row]) >= 3:
                            table_data['Current Assets Year Ending'] = self._clean_text(grid[current_assets_row][1])
                            table_data['Current Assets Previous Year Ending'] = self._clean_text(grid[current_assets_row][2])
                        
                        if total_assets_row is not None and len(grid[total_assets_row]) >= 3:
                            table_data['Total Assets Year Ending'] = self._clean_text(grid[total_assets_row][1])
                            table_data['Total Assets Previous Year Ending'] = self._clean_text(grid[total_assets_row][2])
                        
                        if current_liabilities_row is not None and len(grid[current_liabilities_row]) >= 3:
                            table_data['Current Liabilities Year Ending'] = self._clean_text(grid[current_liabilities_row][1])
                            table_data['Current Liabilities Previous Year Ending'] = self._clean_text(grid[current_liabilities_row][2])
                        
                        if total_liabilities_row is not None and len(grid[total_liabilities_row]) >= 3:
                            table_data['Total Liabilities Year Ending'] = self._clean_text(grid[total_liabilities_row][1])
                            table_data['Total Liabilities Previous Year Ending'] = self._clean_text(grid[total_liabilities_row][2])
                        
                        if retained_earnings_row is not None and len(grid[retained_earnings_row]) >= 3:
                            table_data['RetainedEarnings/(Deficit) Year Ending'] = self._clean_text(grid[retained_earnings_row][1])
                            table_data['RetainedEarnings/(Deficit) Previous Year Ending'] = self._clean_text(grid[retained_earnings_row][2])
                        
                        if stockholders_equity_row is not None and len(grid[stockholders_equity_row]) >= 3:
                            table_data["Stockholders' Equity Year Ending"] = self._clean_text(grid[stockholders_equity_row][1])
                            table_data["Stockholders' Equity Previous Year Ending"] = self._clean_text(grid[stockholders_equity_row][2])
                        
                        if stockholders_equity_parent_row is not None and len(grid[stockholders_equity_parent_row]) >= 3:
                            table_data["Stockholders' Equity - Parent Year Ending"] = self._clean_text(grid[stockholders_equity_parent_row][1])
                            table_data["Stockholders' Equity - Parent Previous Year Ending"] = self._clean_text(grid[stockholders_equity_parent_row][2])
                        
                        if book_value_row is not None and len(grid[book_value_row]) >= 3:
                            table_data['Book Value Per Share Year Ending'] = self._clean_text(grid[book_value_row][1])
                            table_data['Book Value Per Share Previous Year Ending'] = self._clean_text(grid[book_value_row][2])
                            
                        self.logger.info("Processed Balance Sheet data")
                    except (IndexError, KeyError) as e:
                        self.logger.error(f"Error processing Balance Sheet: {e}")
            
            # Process Income Statement
            elif table_caption and table_caption.get_text(strip=True).lower() == "income statement":
                grid = self._process_table_grid(table)
                if grid:
                    try:
                        # Find the correct row indices by looking for specific row labels
                        revenue_row = None
                        expense_row = None
                        non_op_income_row = None
                        non_op_expense_row = None
                        income_before_tax_row = None
                        income_tax_row = None
                        net_income_row = None
                        net_income_parent_row = None
                        eps_basic_row = None
                        eps_diluted_row = None
                        
                        # Find the rows by their labels
                        for i, row in enumerate(grid):
                            if len(row) > 0:
                                row_label = row[0].lower()
                                if 'revenue' in row_label or 'gross revenue' in row_label:
                                    revenue_row = i
                                elif 'expense' in row_label or 'gross expense' in row_label:
                                    expense_row = i
                                elif 'non-operating income' in row_label or 'non operating income' in row_label:
                                    non_op_income_row = i
                                elif 'non-operating expense' in row_label or 'non operating expense' in row_label:
                                    non_op_expense_row = i
                                elif 'income before tax' in row_label or 'income/(loss) before tax' in row_label:
                                    income_before_tax_row = i
                                elif 'income tax' in row_label:
                                    income_tax_row = i
                                elif ('net income' in row_label or 'net income/(loss)' in row_label) and 'parent' not in row_label and 'attributable' not in row_label:
                                    net_income_row = i
                                elif ('attributable to parent' in row_label or 'parent equity holder' in row_label):
                                    net_income_parent_row = i
                                elif 'earnings per share (basic)' in row_label or 'eps (basic)' in row_label:
                                    eps_basic_row = i
                                elif 'earnings per share (diluted)' in row_label or 'eps (diluted)' in row_label:
                                    eps_diluted_row = i
                        
                        # Get the column headers (years)
                        years = []
                        if len(grid) > 0 and len(grid[0]) > 1:
                            for i in range(1, len(grid[0])):
                                if grid[0][i]:
                                    years.append(self._clean_text(grid[0][i]))
                        
                        # Extract values using the identified row indices
                        if revenue_row is not None and len(grid[revenue_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[revenue_row]):
                                    key = f"Gross Revenue {year}"
                                    table_data[key] = self._clean_text(grid[revenue_row][i])
                        
                        if expense_row is not None and len(grid[expense_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[expense_row]):
                                    key = f"Gross Expenses {year}"
                                    table_data[key] = self._clean_text(grid[expense_row][i])
                        
                        if non_op_income_row is not None and len(grid[non_op_income_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[non_op_income_row]):
                                    key = f"Non Operating Income {year}"
                                    table_data[key] = self._clean_text(grid[non_op_income_row][i])
                        
                        if non_op_expense_row is not None and len(grid[non_op_expense_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[non_op_expense_row]):
                                    key = f"Non Operating Expenses {year}"
                                    table_data[key] = self._clean_text(grid[non_op_expense_row][i])
                        
                        if income_before_tax_row is not None and len(grid[income_before_tax_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[income_before_tax_row]):
                                    key = f"Income/(Loss) Before Tax {year}"
                                    table_data[key] = self._clean_text(grid[income_before_tax_row][i])
                        
                        if income_tax_row is not None and len(grid[income_tax_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[income_tax_row]):
                                    key = f"Income Tax Expense {year}"
                                    table_data[key] = self._clean_text(grid[income_tax_row][i])
                        
                        if net_income_row is not None and len(grid[net_income_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[net_income_row]):
                                    key = f"Net Income/(Loss) After Tax {year}"
                                    table_data[key] = self._clean_text(grid[net_income_row][i])
                        
                        if net_income_parent_row is not None and len(grid[net_income_parent_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[net_income_parent_row]):
                                    key = f"Net Income/(Loss) Attributable to Parent Equity Holder {year}"
                                    table_data[key] = self._clean_text(grid[net_income_parent_row][i])
                        
                        if eps_basic_row is not None and len(grid[eps_basic_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[eps_basic_row]):
                                    key = f"Earnings/(Loss) Per Share (Basic) {year}"
                                    table_data[key] = self._clean_text(grid[eps_basic_row][i])
                        
                        if eps_diluted_row is not None and len(grid[eps_diluted_row]) >= 2:
                            for i, year in enumerate(years, 1):
                                if i < len(grid[eps_diluted_row]):
                                    key = f"Earnings/(Loss) Per Share (Diluted) {year}"
                                    table_data[key] = self._clean_text(grid[eps_diluted_row][i])
                                    
                        self.logger.info("Processed Income Statement data")
                    except (IndexError, KeyError) as e:
                        self.logger.error(f"Error processing Income Statement: {e}")

        return table_data

    def _process_balance_sheet_enhanced(self, table, data_dict):
        """
        Process the balance sheet table and extract relevant data.
        
        Args:
            table: BeautifulSoup object for the table
            data_dict: Dictionary to store the extracted data
        """
        try:
            # Find all rows
            rows = table.find_all('tr')
            
            # Find the headers (periods)
            headers = []
            target_columns = {}
            
            # Process header row
            if len(rows) > 0:
                header_row = rows[0]
                header_cells = header_row.find_all(['th', 'td'])
                
                # Extract header texts
                for i, cell in enumerate(header_cells):
                    header_text = self._clean_text(cell.get_text().strip())
                    if header_text and i > 0:  # Skip the first column (item names)
                        headers.append(header_text)
                        target_columns[header_text] = i
            
            self.logger.info(f"Balance Sheet headers: {headers}")
            self.logger.info(f"Balance Sheet target columns: {target_columns}")
            
            # Process each row to extract balance sheet items
            for row in rows[1:]:  # Skip the header row
                cells = row.find_all(['th', 'td'])
                if len(cells) < 2:
                    continue
                
                item_name = self._clean_text(cells[0].get_text().strip())
                
                # Skip empty rows or section headers
                if not item_name or "Balance Sheet" in item_name:
                    continue
                
                # Initialize the item in the data dictionary if it doesn't exist
                if item_name not in data_dict:
                    data_dict[item_name] = {}
                
                # Extract values for each period
                for header, col_index in target_columns.items():
                    if col_index < len(cells):
                        value = self._clean_text(cells[col_index].get_text().strip())
                        data_dict[item_name][header] = self._convert_to_numeric(value)
        except Exception as e:
            self.logger.error(f"Error processing balance sheet: {e}")

    def _process_quarterly_report(self, iframe_soup: BeautifulSoup, stock_name: str, report_date: str) -> Optional[Dict]:
        """
        Memproses data laporan kuartalan dengan metode yang lebih komprehensif.
        Menggunakan pendekatan untuk mengekstrak data dari tabel Balance Sheet, Income Statement, dan EPS.

        Args:
            iframe_soup: BeautifulSoup object dari iframe
            stock_name: Nama saham
            report_date: Tanggal laporan

        Returns:
            Dictionary berisi data laporan kuartalan dengan struktur internal tetapi format output yang sama dengan fitur lain, atau None jika terjadi error
        """
        try:
            self.logger.info(f"Processing quarterly report for {stock_name} on {report_date}")
            
            # Initialize dictionaries to store data
            balance_sheet_data = {}
            income_statement_data = {}
            eps_data = {}
            
            # Extract period ended date directly from the HTML
            period_ended_date = ""
            period_ended_row = iframe_soup.find("th", string="For the period ended")
            if period_ended_row and period_ended_row.find_next("td"):
                period_ended_date = self._clean_text(period_ended_row.find_next("td").text)
                self.logger.info(f"Found period ended date: {period_ended_date}")
            
            # Extract fiscal year ended date from the balance sheet table
            fiscal_year_ended_date = ""
            balance_sheet_table = iframe_soup.find("table", id="BS")
            
            if balance_sheet_table:
                fiscal_year_header = None
                for th in balance_sheet_table.find_all("th"):
                    if "Fiscal Year Ended" in th.text:
                        fiscal_year_header = th
                        break
                
                if fiscal_year_header:
                    header_row = fiscal_year_header.find_parent("tr")
                    date_row = header_row.find_next("tr")
                    
                    if date_row:
                        date_cells = date_row.find_all("td")
                        if len(date_cells) > 1:
                            span = date_cells[1].find("span", class_="valInput")
                            if span:
                                fiscal_year_ended_date = self._clean_text(span.text)
                                self.logger.info(f"Found fiscal year ended date: {fiscal_year_ended_date}")
                            else:
                                fiscal_year_ended_date = self._clean_text(date_cells[1].text)
                                self.logger.info(f"Found fiscal year ended date (from td): {fiscal_year_ended_date}")
            
            # Find all tables in the document
            tables = iframe_soup.find_all("table")
            self.logger.info(f"Found {len(tables)} tables in the document")
            
            # Process each table to extract data
            for i, table in enumerate(tables):
                preview = table.get_text()[:100].replace('\n', '').strip()
                self.logger.info(f"Table {i+1} preview: {preview}...")
                
                # Process Balance Sheet table
                if "Balance Sheet" in preview or table.get('id') == "BS":
                    self.logger.info(f"Processing Balance Sheet table (Table {i+1})")
                    self._process_balance_sheet_enhanced(table, balance_sheet_data)
                
                # Process Income Statement table
                elif "Income Statement" in preview or table.get('id') == "IS":
                    self.logger.info(f"Processing Income Statement table (Table {i+1})")
                    self._process_income_statement_enhanced(table, income_statement_data)
                
                # Process EPS table (Trailing 12 Months)
                elif "Trailing 12 months" in preview or "EPS" in preview:
                    self.logger.info(f"Processing EPS table (Table {i+1})")
                    self._process_eps_table_enhanced(table, eps_data)
            
            # HTML export disabled as requested
            pass
            
            # Create a flat dictionary with all data for output in the same format as other features
            table_data = {
                "stock name": stock_name,
                "disclosure date": report_date,
                "period_ended_date": period_ended_date,
                "fiscal_year_ended_date": fiscal_year_ended_date
            }
            
            # Flatten the nested dictionaries to match the output format of other features
            # Balance Sheet data
            for item_name, item_data in balance_sheet_data.items():
                for period, value in item_data.items():
                    key = f"BS_{item_name}_{period}"
                    table_data[key] = value
            
            # Income Statement data
            for item_name, item_data in income_statement_data.items():
                for period, value in item_data.items():
                    key = f"IS_{item_name}_{period}"
                    table_data[key] = value
            
            # EPS data
            for item_name, item_data in eps_data.items():
                for period, value in item_data.items():
                    key = f"EPS_{item_name}_{period}"
                    table_data[key] = value
            
            # Also keep the original table processing for backward compatibility
            for table in iframe_soup.find_all("table"):
                table_caption = table.find("caption")
                if (
                    table_caption
                    and table_caption.get_text(strip=True).lower() == "balance sheet"
                ):
                    grid = self._process_table_grid(table)
                    if grid:
                        table_data.update(
                            {
                                "Year Ending": self._clean_text(grid[0][0]),
                                "Previous Year Ending": self._clean_text(grid[1][1]),
                                "Current Assets Year Ending": self._clean_text(grid[2][1]),
                                "Current Assets Previous Year Ending": self._clean_text(grid[2][2]),
                                "Total Assets Year Ending": self._clean_text(grid[3][1]),
                                "Total Assets Previous Year Ending": self._clean_text(grid[3][2]),
                                "Current Liabilities Year Ending": self._clean_text(grid[4][1]),
                                "Current Liabilities Previous Year Ending": self._clean_text(grid[4][2]),
                                "Total Liabilities Year Ending": self._clean_text(grid[5][1]),
                                "Total Liabilities Previous Year Ending": self._clean_text(grid[5][2]),
                                "RetainedEarnings/(Deficit) Year Ending": self._clean_text(grid[6][1]),
                                "RetainedEarnings/(Deficit) Previous Year Ending": self._clean_text(grid[6][2]),
                                "Stockholders' Equity Year Ending": self._clean_text(grid[7][1]),
                                "Stockholders' Equity Previous Year Ending": self._clean_text(grid[7][2]),
                                "Stockholders' Equity - Parent Year Ending": self._clean_text(grid[8][1]),
                                "Stockholders' Equity - Parent Previous Year Ending": self._clean_text(grid[8][2]),
                                "Book Value Per Share Year Ending": self._clean_text(grid[9][1]),
                                "Book Value Per Share Previous Year Ending": self._clean_text(grid[9][2])
                            }
                        )
                elif (
                    table_caption
                    and table_caption.get_text(strip=True).lower() == "income statement"
                ):
                    grid = self._process_table_grid(table)
                    if grid:
                        table_data.update(
                            {
                                f"Gross Revenue {self._clean_text(grid[0][1])}": self._clean_text(grid[1][1]),
                                f"Gross Revenue {self._clean_text(grid[0][2])}": self._clean_text(grid[1][2]),
                                f"Gross Revenue {self._clean_text(grid[0][3])}": self._clean_text(grid[1][3]),
                                f"Gross Revenue {self._clean_text(grid[0][4])}": self._clean_text(grid[1][4]),
                                f"Gross Expenses {self._clean_text(grid[0][1])}": self._clean_text(grid[2][1]),
                                f"Gross Expenses {self._clean_text(grid[0][2])}": self._clean_text(grid[2][2]),
                                f"Gross Expenses {self._clean_text(grid[0][3])}": self._clean_text(grid[2][3]),
                                f"Gross Expenses {self._clean_text(grid[0][4])}": self._clean_text(grid[2][4]),
                                f"Non Operating Income {self._clean_text(grid[0][1])}": self._clean_text(grid[3][1]),
                                f"Non Operating Income {self._clean_text(grid[0][2])}": self._clean_text(grid[3][2]),
                                f"Non Operating Income {self._clean_text(grid[0][3])}": self._clean_text(grid[3][3]),
                                f"Non Operating Income {self._clean_text(grid[0][4])}": self._clean_text(grid[3][4]),
                                f"Non Operating Expenses {self._clean_text(grid[0][1])}": self._clean_text(grid[4][1]),
                                f"Non Operating Expenses {self._clean_text(grid[0][2])}": self._clean_text(grid[4][2]),
                                f"Non Operating Expenses {self._clean_text(grid[0][3])}": self._clean_text(grid[4][3]),
                                f"Non Operating Expenses {self._clean_text(grid[0][4])}": self._clean_text(grid[4][4]),
                                f"Income/(Loss) Before Tax {self._clean_text(grid[0][1])}": self._clean_text(grid[5][1]),
                                f"Income/(Loss) Before Tax {self._clean_text(grid[0][2])}": self._clean_text(grid[5][2]),
                                f"Income/(Loss) Before Tax {self._clean_text(grid[0][3])}": self._clean_text(grid[5][3]),
                                f"Income/(Loss) Before Tax {self._clean_text(grid[0][4])}": self._clean_text(grid[5][4]),
                                f"Income Tax Expense {self._clean_text(grid[0][1])}": self._clean_text(grid[6][1]),
                                f"Income Tax Expense {self._clean_text(grid[0][2])}": self._clean_text(grid[6][2]),
                                f"Income Tax Expense {self._clean_text(grid[0][3])}": self._clean_text(grid[6][3]),
                                f"Income Tax Expense {self._clean_text(grid[0][4])}": self._clean_text(grid[6][4]),
                                f"Net Income/(Loss) After Tax {self._clean_text(grid[0][1])}": self._clean_text(grid[7][1]),
                                f"Net Income/(Loss) After Tax {self._clean_text(grid[0][2])}": self._clean_text(grid[7][2]),
                                f"Net Income/(Loss) After Tax {self._clean_text(grid[0][3])}": self._clean_text(grid[7][3]),
                                f"Net Income/(Loss) After Tax {self._clean_text(grid[0][4])}": self._clean_text(grid[7][4]),
                                f"Net Income/(Loss) Attributable to Parent Equity Holder {self._clean_text(grid[0][1])}": self._clean_text(grid[8][1]),
                                f"Net Income/(Loss) Attributable to Parent Equity Holder {self._clean_text(grid[0][2])}": self._clean_text(grid[8][2]),
                                f"Net Income/(Loss) Attributable to Parent Equity Holder {self._clean_text(grid[0][3])}": self._clean_text(grid[8][3]),
                                f"Net Income/(Loss) Attributable to Parent Equity Holder {self._clean_text(grid[0][4])}": self._clean_text(grid[8][4]),
                                f"Earnings/(Loss) Per Share (Basic) {self._clean_text(grid[0][1])}": self._clean_text(grid[9][1]),
                                f"Earnings/(Loss) Per Share (Basic) {self._clean_text(grid[0][2])}": self._clean_text(grid[9][2]),
                                f"Earnings/(Loss) Per Share (Basic) {self._clean_text(grid[0][3])}": self._clean_text(grid[9][3]),
                                f"Earnings/(Loss) Per Share (Basic) {self._clean_text(grid[0][4])}": self._clean_text(grid[9][4]),
                                f"Earnings/(Loss) Per Share (Diluted) {self._clean_text(grid[0][1])}": self._clean_text(grid[10][1]),
                                f"Earnings/(Loss) Per Share (Diluted) {self._clean_text(grid[0][2])}": self._clean_text(grid[10][2]),
                                f"Earnings/(Loss) Per Share (Diluted) {self._clean_text(grid[0][3])}": self._clean_text(grid[10][3]),
                                f"Earnings/(Loss) Per Share (Diluted) {self._clean_text(grid[0][4])}": self._clean_text(grid[10][4]),
                            }
                        )
            
            return table_data
        except Exception as e:
            self.logger.error(f"Error in quarterly report processing: {e}")
            return None

    def _convert_to_numeric(self, value):
        """
        Convert string values to numeric types where appropriate.
        
        Args:
            value: The string value to convert
            
        Returns:
            Numeric value if conversion is possible, otherwise the original string
        """
        if not value or not isinstance(value, str):
            return value
        
        # Remove commas from numbers
        value = value.replace(',', '')
        
        # Try to convert to numeric type
        try:
            # Check if it's a float
            if '.' in value:
                return float(value)
            # Check if it's an integer
            else:
                return int(value)
        except (ValueError, TypeError):
            # If conversion fails, return the original value
            return value

    def _process_income_statement_enhanced(self, table, data_dict):
        """
        Process the income statement table and extract data.
        
        Args:
            table: BeautifulSoup object for the table
            data_dict: Dictionary to store the extracted data
        """
        try:
            # Find all rows
            rows = table.find_all('tr')
            
            # Find the headers (periods)
            headers = []
            target_columns = {}
            
            # Process header row
            if len(rows) > 0:
                header_row = rows[0]
                header_cells = header_row.find_all(['th', 'td'])
                
                # Extract header texts
                for i, cell in enumerate(header_cells):
                    header_text = self._clean_text(cell.get_text().strip())
                    if header_text and i > 0:  # Skip the first column (item names)
                        headers.append(header_text)
                        target_columns[header_text] = i
            
            self.logger.info(f"Income Statement headers: {headers}")
            self.logger.info(f"Income Statement target columns: {target_columns}")
            
            # Process each row to extract income statement items
            for row in rows[1:]:  # Skip the header row
                cells = row.find_all(['th', 'td'])
                if len(cells) < 2:
                    continue
                
                item_name = self._clean_text(cells[0].get_text().strip())
                
                # Skip empty rows or section headers
                if not item_name or "Income Statement" in item_name:
                    continue
                
                # Initialize the item in the data dictionary if it doesn't exist
                if item_name not in data_dict:
                    data_dict[item_name] = {}
                
                # Extract values for each period
                for header, col_index in target_columns.items():
                    if col_index < len(cells):
                        value = self._clean_text(cells[col_index].get_text().strip())
                        data_dict[item_name][header] = self._convert_to_numeric(value)
        except Exception as e:
            self.logger.error(f"Error processing income statement: {e}")

    def _process_eps_table_enhanced(self, table, data_dict):
        """
        Process the EPS (Earnings Per Share) table and extract data.
        
        Args:
            table: BeautifulSoup object for the table
            data_dict: Dictionary to store the extracted data
        """
        try:
            # Extract headers (column names)
            headers = []
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    header_text = self._clean_text(th.get_text().strip())
                    if header_text:
                        headers.append(header_text)
            
            self.logger.info(f"EPS table headers: {headers}")
            
            # Process each row to extract EPS items
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip the header row
                cells = row.find_all(['th', 'td'])
                if len(cells) < 2:
                    continue
                
                item_name = self._clean_text(cells[0].get_text().strip())
                
                # Skip empty rows
                if not item_name:
                    continue
                
                # Initialize the item in the data dictionary if it doesn't exist
                if item_name not in data_dict:
                    data_dict[item_name] = {}
                
                # Extract values for each period
                for i, header in enumerate(headers):
                    if i > 0 and i < len(cells):  # Skip the first column (item name)
                        value = self._clean_text(cells[i].get_text().strip())
                        data_dict[item_name][header] = self._convert_to_numeric(value)
        except Exception as e:
            self.logger.error(f"Error processing EPS table: {e}")

    def _clean_stockholders_text(self, text):
        """Clean text by removing extra whitespace and HTML entities"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        return text

    def _extract_stockholders_table_data(self, html_content):
        """Extract table data using multiple patterns to handle different HTML structures"""
        all_data = []
        
        # Convert BeautifulSoup object to string if needed
        if not isinstance(html_content, str):
            html_content = str(html_content)
        
        # Try different patterns to extract data
        patterns = [
            # Pattern 1: Standard table row with label in first cell, value in second
            r'<tr[^>]*>\s*<td[^>]*>(Number of [^<]+|PCD Nominee[^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*</tr>',
            
            # Pattern 2: Alternative format with th instead of td for headers
            r'<tr[^>]*>\s*<th[^>]*>(Number of [^<]+|PCD Nominee[^<]+)</th>\s*<td[^>]*>([^<]+)</td>\s*</tr>',
            
            # Pattern 3: Look for specific text patterns regardless of HTML structure
            r'(Number of Issued Common Shares|Number of Treasury Common Shares|Number of Outstanding Common Shares|Number of Listed Common Shares|Number of Lodged Common Shares|PCD Nominee - Filipino|PCD Nominee - Non-Filipino|Number of Certificated Common Shares)[^0-9]+(\d[\d,]+)'
        ]
        
        # Try all patterns and collect all matches
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                label = self._clean_stockholders_text(match[0])
                value = self._clean_stockholders_text(match[1])
                
                # Skip invalid values (like single digits that are likely not share counts)
                if value.isdigit() and len(value) < 3:
                    continue
                    
                all_data.append([label, value])
        
        # If we found data, return it
        if all_data:
            return all_data
        
        # If no data found, return empty list
        self.logger.warning("No share data found in the HTML. The URL may require authentication or the HTML structure is different.")
        return []

    def _process_stockholders(
        self, iframe_soup: BeautifulSoup, stock_name: str, report_date: str
    ) -> Optional[Dict]:
        """
        Memproses data pemegang saham.
        Mengambil data dari tabel pemegang saham dengan pendekatan hybrid.
        Mencoba metode BeautifulSoup terlebih dahulu, jika gagal menggunakan regex.

        Args:
            iframe_soup: BeautifulSoup object dari iframe
            stock_name: Nama saham
            report_date: Tanggal laporan

        Returns:
            Dictionary berisi data pemegang saham
        """
        # Inisialisasi dictionary untuk menyimpan data
        table_data = {"stock_name": stock_name, "disclosure_date": report_date}
        data_found = False
        
        # METODE 1: Pendekatan BeautifulSoup seperti di file asli
        try:
            # Cari tabel dengan class "type1"
            tables = iframe_soup.find_all("table", {"class": "type1"})
            if len(tables) >= 3:
                table = tables[2]  # Ambil tabel ketiga seperti di file asli
                
                # Process each row in the table
                for row in table.find_all("tr"):
                    header = row.find("th")
                    value = row.find("td")
                    if header and value:
                        # Clean the header text and remove extra spaces
                        header_text = self._clean_text(header.text).strip()
                        
                        # Get the value from span with class "valInput"
                        value_span = value.find("span", {"class": "valInput"})
                        if value_span:
                            value_text = value_span.text.strip()
                        else:
                            # If no span with class valInput, get text directly
                            value_text = value.text.strip()
                            
                        # Convert "-" to 0 and remove commas from numbers
                        value_text = "0" if value_text == "-" else value_text.replace(",", "")
                        
                        # Store in data dictionary with cleaned header as key
                        table_data[header_text] = value_text
                        data_found = True
        except Exception as e:
            self.logger.warning(f"Error in BeautifulSoup approach: {e}")
        
        # METODE 2: Jika metode BeautifulSoup gagal, gunakan pendekatan regex
        if not data_found:
            self.logger.info("BeautifulSoup approach failed, trying regex approach")
            
            # Convert BeautifulSoup object to string for regex processing
            html_content = str(iframe_soup)
            
            # Extract share data using the enhanced method
            share_data = self._extract_stockholders_table_data(html_content)
            
            if share_data:
                for row in share_data:
                    # Use the label as key to avoid duplicates
                    label = row[0]
                    value = row[1].replace(',', '').replace('"', '')
                    # Convert "-" to 0
                    value = "0" if value == "-" else value
                    table_data[label] = value
                    data_found = True
        
        # Return data if found, otherwise return None
        if data_found and len(table_data) > 2:  # More than 2 because we always have stock_name and disclosure_date
            self.logger.info(f"Extracted {len(table_data)-2} data points for {stock_name}")
            return table_data
        else:
            self.logger.warning(f"No share data found for {stock_name} on {report_date}")
            return None

    def _process_cash_dividends(
        self, iframe_soup: BeautifulSoup, stock_name: str, report_date: str
    ) -> Optional[Dict]:
        """
        Memproses data dividen tunai.
        Mengambil semua baris dari tabel dividen.

        Args:
            iframe_soup: BeautifulSoup object dari iframe
            stock_name: Nama saham
            report_date: Tanggal laporan

        Returns:
            Dictionary berisi data dividen tunai
        """
        # Cek apakah ada input dengan value COMMON yang terpilih
        common_input = None
        report_type_ul = iframe_soup.find("ul", {"class": "reportType"})
        if report_type_ul:
            for input_elem in report_type_ul.find_all("input"):
                if input_elem.get("checked") and input_elem.get("value") == "COMMON":
                    common_input = input_elem
                    break

        if not common_input:
            return None

        table_data = {"stock_name": stock_name, "disclosure_date": report_date}

        # Cari tabel dengan caption "cash dividend"
        for table in iframe_soup.find_all("table"):
            table_caption = table.find("caption")
            if table_caption and table_caption.get_text(strip=True).lower() == "cash dividend":
                # Proses setiap baris dalam tabel
                for row in table.find_all("tr"):
                    cells = row.find_all(["th", "td"])
                    if len(cells) == 2:
                        # Ekstrak kunci dan nilai
                        key = re.sub(
                            r"(?<=[A-Z])(?=[A-Z])",
                            r" \t",
                            cells[0].get_text(strip=True),
                        )
                        value = self._clean_text(cells[1].get_text())
                        table_data[key] = value

        # Jika data ditemukan dan memiliki checked COMMON, return data dan set flag untuk keluar dari iterasi
        if len(table_data) > 2:  # Lebih dari 2 karena minimal ada stock_name dan disclosure_date
            self.stop_iteration = True

        return table_data
        
    #--------------------------------------------------------------------------
    # 3.6 DATA OUTPUT AND STORAGE
    #--------------------------------------------------------------------------
    def save_results(self, filename: str, formats: List[str] = ["csv"]) -> None:
        """
        Menyimpan hasil scraping ke file dengan format yang dipilih.

        Args:
            filename: Nama file untuk output (tanpa ekstensi)
            formats: List format file yang diinginkan ('json' dan/atau 'csv')
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
                    # Create an empty CSV file with a header row
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
#------------------------------------------------------------------------------
def main():
    """
    Fungsi utama program.
    Menampilkan menu dan menangani input pengguna.
    """
    # Default settings
    settings = {
        "enable_logging": True,  # Default logging off
        "use_proxies": False,  # Default proxy off
        "max_workers": 1,
        "default_save_format": ["csv"],  # Default hanya csv
    }

    # Setup basic logging untuk main function jika dibutuhkan
    if settings["enable_logging"]:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger = logging.getLogger("main")
    else:
        # Nonaktifkan semua root logger
        logging.basicConfig(level=logging.CRITICAL)
        logger = logging.getLogger("null")
        logger.setLevel(logging.CRITICAL)
        logger.propagate = False
        logger.addHandler(logging.NullHandler())

    # Main Program
    try:
        scraper = PSEDataScraper(
            max_workers=settings["max_workers"],
            use_proxies=settings["use_proxies"],
            enable_logging=settings["enable_logging"],
        )

        # Mapping for menu choices to ReportType
        report_type_mapping = {
            1: ReportType.PUBLIC_OWNERSHIP,
            2: ReportType.QUARTERLY,
            3: ReportType.ANNUAL,
            4: ReportType.TOP_100_STOCKHOLDERS,
            5: ReportType.CASH_DIVIDENDS,
        }

        # Menu
        while True:
            print("\n============ MENU =============")
            print("|    1. Public Ownership")
            print("|    2. Quarterly Report")
            print("|    3. Annual Report")
            print("|    4. List of Top 100 Stockholders")
            print("|    5. Declaration of Cash Dividends")
            print("|    6. Settings")
            print("|    7. Exit")
            print("===============================")

            try:
                choice = int(input("Enter your choice: "))

                if choice == 7:  # Exit
                    if settings["enable_logging"]:
                        logger.info("Program finished")
                    break

                elif choice == 6:  # Settings
                    while True:
                        print("\n========= SETTINGS ==========")
                        print(
                            f"1. Logging: {'Enabled' if settings['enable_logging'] else 'Disabled'}"
                        )
                        print(
                            f"2. Proxy: {'Enabled' if settings['use_proxies'] else 'Disabled'}"
                        )
                        print(f"3. Max Workers: {settings['max_workers']}")
                        print(
                            f"4. Save Format: {' and '.join(settings['default_save_format'])}"
                        )
                        print("5. Back to Main Menu")
                        print("============================")

                        setting_choice = input("Select setting (1-5): ").strip()

                        if setting_choice == "1":
                            settings["enable_logging"] = not settings["enable_logging"]
                            # Reset root logger jika logging dinonaktifkan
                            if not settings["enable_logging"]:
                                # Nonaktifkan semua root logger
                                for handler in logging.root.handlers[:]:
                                    logging.root.removeHandler(handler)
                                logging.basicConfig(level=logging.CRITICAL)
                            else:
                                # Aktifkan kembali root logger jika logging diaktifkan
                                for handler in logging.root.handlers[:]:
                                    logging.root.removeHandler(handler)
                                logging.basicConfig(
                                    level=logging.INFO,
                                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                )
                            
                            # Reinisialisasi scraper dengan pengaturan baru
                            scraper = PSEDataScraper(
                                max_workers=settings["max_workers"],
                                use_proxies=settings["use_proxies"],
                                enable_logging=settings["enable_logging"],
                            )
                            print(
                                f"Logging {'enabled' if settings['enable_logging'] else 'disabled'}"
                            )

                        elif setting_choice == "2":
                            settings["use_proxies"] = not settings["use_proxies"]
                            scraper.use_proxies = settings["use_proxies"]
                            print(
                                f"Proxy {'enabled' if settings['use_proxies'] else 'disabled'}"
                            )

                        elif setting_choice == "3":
                            try:
                                new_workers = int(
                                    input("Enter number of max workers (1-10): ")
                                )
                                if 1 <= new_workers <= 10:
                                    settings["max_workers"] = new_workers
                                    scraper.max_workers = new_workers
                                    print(f"Max workers changed to {new_workers}")
                                else:
                                    print("Number of workers must be between 1-10")
                            except ValueError:
                                print("Please enter a valid number")

                        elif setting_choice == "4":
                            print("\nSelect save format:")
                            print("1. CSV only (default)")
                            print("2. JSON only")
                            print("3. Both CSV and JSON")
                            format_choice = input("Choice: ").strip()

                            if format_choice == "1":
                                settings["default_save_format"] = ["csv"]
                            elif format_choice == "2":
                                settings["default_save_format"] = ["json"]
                            elif format_choice == "3":
                                settings["default_save_format"] = ["csv", "json"]
                            else:
                                print("Invalid choice, keeping current format")

                            print(
                                f"Save format set to: {' and '.join(settings['default_save_format'])}"
                            )

                        elif setting_choice == "5":
                            break

                        else:
                            print("Invalid choice")

                    continue

                # Validasi choice / Report Process
                if choice not in report_type_mapping:
                    print("Invalid choice. Please try again.")
                    continue

                # Reset data sebelum memulai pencarian baru
                scraper.data = []
                scraper.stop_iteration = False
                if settings["enable_logging"]:
                    logger.info("Starting new search")

                report_type = report_type_mapping[choice]
                filename = input("Enter output filename: ")
                start_iteration = int(input("Enter start iteration: "))
                end_iteration = input(
                    "Enter end iteration (leave empty for single iteration): "
                )

                if end_iteration:
                    for i in range(start_iteration, int(end_iteration) + 1):
                        if settings["enable_logging"]:
                            logger.info(f"Processing iteration {i}")
                        scraper.scrape_data(str(i), report_type)
                        # if scraper.stop_iteration:
                        #     break
                else:
                    scraper.scrape_data(str(start_iteration), report_type)

                # Simpan hasil dengan format default
                scraper.save_results(filename, settings["default_save_format"])

            except ValueError as e:
                if settings["enable_logging"]:
                    logger.error(f"Input error: {e}")
                print("Invalid input. Please enter a number.")

            except Exception as e:
                if settings["enable_logging"]:
                    logger.error(f"Unexpected error: {e}")
                print(f"An error occurred: {e}")

    except KeyboardInterrupt:
        if settings["enable_logging"]:
            logger.info("Program stopped by user")
        print("\nProgram stopped")

    except Exception as e:
        if settings["enable_logging"]:
            logger.error(f"Fatal error: {e}")
        print(f"A fatal error occurred: {e}")


if __name__ == "__main__":
    main()
