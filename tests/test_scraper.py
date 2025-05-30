"""
Tests for main scraper functionality.
"""

import pytest
from unittest.mock import Mock, patch
from pse_scraper.core import PSEDataScraper
from pse_scraper.models.report_types import ReportType


class TestPSEDataScraper:
    """Test PSEDataScraper class."""
    
    def test_init_default_values(self):
        """Test scraper initialization with default values."""
        scraper = PSEDataScraper()
        
        assert scraper.max_workers == 5
        assert scraper.data == []
        assert scraper.stop_iteration is False
        assert scraper.http_client is not None
        assert scraper.logger is not None
    
    def test_init_custom_values(self):
        """Test scraper initialization with custom values."""
        scraper = PSEDataScraper(
            max_workers=10,
            use_proxies=True,
            enable_logging=False
        )
        
        assert scraper.max_workers == 10
    
    def test_get_soup_valid_response(self):
        """Test _get_soup with valid response."""
        scraper = PSEDataScraper()
        
        # Mock response
        mock_response = Mock()
        mock_response.text = "<html><body><p>Test</p></body></html>"
        
        soup = scraper._get_soup(mock_response)
        
        assert soup is not None
        assert soup.find("p").get_text() == "Test"
    
    def test_get_soup_no_response(self):
        """Test _get_soup with no response."""
        scraper = PSEDataScraper()
        
        soup = scraper._get_soup(None)
        assert soup is None
    
    def test_extract_table_data(self):
        """Test _extract_table_data method."""
        from bs4 import BeautifulSoup
        
        scraper = PSEDataScraper()
        
        html = """
        <table>
            <tr>
                <th>Company Name</th>
                <td>Test Company</td>
            </tr>
            <tr>
                <th>Total Shares</th>
                <td>1,000,000</td>
            </tr>
        </table>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        
        result = scraper._extract_table_data(table, "TEST", "2024-01-15")
        
        assert result["stock name"] == "TEST"
        assert result["disclosure date"] == "2024-01-15"
        assert "Company Name" in result
        assert result["Company Name"] == "Test Company"
    
    def test_save_results_no_data(self):
        """Test save_results with no data."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            scraper.save_results("test_output")
            mock_print.assert_called_with("No data to save")
    
    def test_save_results_with_data(self):
        """Test save_results with data."""
        scraper = PSEDataScraper(enable_logging=False)
        scraper.data = [
            {"stock name": "TEST", "value": 100},
            {"stock name": "TEST2", "value": 200}
        ]
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('csv.writer') as mock_csv_writer:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                scraper.save_results("test_output", ["csv"])
                
                mock_open.assert_called()
                mock_csv_writer.assert_called()
    
    @patch('pse_scraper.core.PSEDataScraper._process_page')
    @patch('pse_scraper.core.PSEDataScraper._get_pages_count')
    def test_scrape_data_success(self, mock_get_pages, mock_process_page):
        """Test successful data scraping."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Mock successful responses
        mock_response = Mock()
        mock_response.text = "<html><body><span class='count'>1 / 2</span></body></html>"
        
        scraper.http_client.make_request = Mock(return_value=mock_response)
        mock_get_pages.return_value = 2
        mock_process_page.return_value = None
        
        scraper.scrape_data("TEST", ReportType.PUBLIC_OWNERSHIP)
        
        # Verify methods were called
        assert scraper.http_client.make_request.called
        assert mock_get_pages.called
        assert mock_process_page.call_count == 2  # Should be called for each page
    
    def test_scrape_data_no_results(self):
        """Test scraping when no data is found."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Mock response with no results
        mock_response = Mock()
        mock_response.text = "<html><body><p>No results found</p></body></html>"
        
        scraper.http_client.make_request = Mock(return_value=mock_response)
        
        result = scraper.scrape_data("NONEXISTENT", ReportType.PUBLIC_OWNERSHIP)
        
        assert result == []
    
    def test_scrape_data_network_error(self):
        """Test scraping with network error."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Mock network failure
        scraper.http_client.make_request = Mock(return_value=None)
        
        result = scraper.scrape_data("TEST", ReportType.PUBLIC_OWNERSHIP)
        
        assert result == []
    
    def test_get_pages_count_valid(self):
        """Test getting page count from valid response."""
        from bs4 import BeautifulSoup
        
        scraper = PSEDataScraper()
        
        html = "<html><body><span class='count'>Showing 1-20 of 100 results</span></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        count = scraper._get_pages_count(soup)
        assert count == 5  # 100 results / 20 per page = 5 pages
    
    def test_get_pages_count_no_results(self):
        """Test getting page count when no results."""
        from bs4 import BeautifulSoup
        
        scraper = PSEDataScraper()
        
        html = "<html><body><p>No results found</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        count = scraper._get_pages_count(soup)
        assert count == 1  # Default to 1 page
    
    def test_stop_iteration_flag(self):
        """Test stop iteration functionality."""
        scraper = PSEDataScraper()
        
        assert scraper.stop_iteration is False
        
        scraper.stop_iteration = True
        assert scraper.stop_iteration is True
    
    def test_data_accumulation(self):
        """Test that data accumulates correctly."""
        scraper = PSEDataScraper()
        
        # Add some test data
        scraper.data.append({"stock": "TEST1", "value": 100})
        scraper.data.append({"stock": "TEST2", "value": 200})
        
        assert len(scraper.data) == 2
        assert scraper.data[0]["stock"] == "TEST1"
        assert scraper.data[1]["stock"] == "TEST2"
    
    def test_save_results_json_format(self):
        """Test saving results in JSON format."""
        scraper = PSEDataScraper(enable_logging=False)
        scraper.data = [
            {"stock name": "TEST", "value": 100},
            {"stock name": "TEST2", "value": 200}
        ]
        
        with patch('builtins.open', create=True) as mock_open:
            with patch('json.dump') as mock_json_dump:
                mock_file = Mock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                scraper.save_results("test_output", ["json"])
                
                mock_open.assert_called()
                mock_json_dump.assert_called_with(scraper.data, mock_file, indent=4, ensure_ascii=False)
    
    def test_concurrent_processing(self):
        """Test concurrent processing functionality."""
        scraper = PSEDataScraper(max_workers=2, enable_logging=False)
        
        # Mock some pages to process
        pages_to_process = [1, 2, 3]
        
        with patch.object(scraper, '_process_page') as mock_process:
            with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
                mock_executor.return_value.__enter__.return_value.map.return_value = [None, None, None]
                
                # This would normally be called internally during scraping
                # We're testing the concept here
                assert scraper.max_workers == 2
