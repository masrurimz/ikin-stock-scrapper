"""
Tests for utility functions.
"""

import pytest
import logging
from unittest.mock import Mock, patch
from pse_scraper.utils import (
    clean_text,
    parse_date,
    extract_edge_no,
    convert_to_numeric,
    clean_stockholders_text
)
from pse_scraper.utils.http_client import HTTPClient
from pse_scraper.utils.logging_config import setup_logging


class TestCleanText:
    """Test clean_text function."""
    
    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        assert clean_text("  Hello World  ") == "Hello World"
        assert clean_text("1,000,000") == "1000000"
        assert clean_text("50%") == "50"
    
    def test_clean_text_empty(self):
        """Test clean_text with empty string."""
        assert clean_text("") == ""
        assert clean_text("   ") == ""


class TestParseDate:
    """Test parse_date function."""
    
    def test_parse_date_valid(self):
        """Test parsing valid dates."""
        assert parse_date("Jan 15, 2024 10:30 AM") == "2024-01-15"
        assert parse_date("Dec 31, 2023 11:59 PM") == "2023-12-31"
    
    def test_parse_date_invalid(self):
        """Test parsing invalid dates."""
        assert parse_date("invalid date") is None
        assert parse_date("") is None


class TestExtractEdgeNo:
    """Test extract_edge_no function."""
    
    def test_extract_edge_no_valid(self):
        """Test extracting valid edge numbers."""
        onclick = "openPopup('12345')"
        assert extract_edge_no(onclick) == "12345"
        
        onclick = "openPopup('ABC123')"
        assert extract_edge_no(onclick) == "ABC123"
    
    def test_extract_edge_no_invalid(self):
        """Test extracting from invalid onclick."""
        assert extract_edge_no("invalid onclick") is None
        assert extract_edge_no("") is None


class TestConvertToNumeric:
    """Test convert_to_numeric function."""
    
    def test_convert_to_numeric_integer(self):
        """Test converting to integer."""
        assert convert_to_numeric("123") == 123
        assert convert_to_numeric("1,000") == 1000
    
    def test_convert_to_numeric_float(self):
        """Test converting to float."""
        assert convert_to_numeric("123.45") == 123.45
        assert convert_to_numeric("1,000.50") == 1000.50
    
    def test_convert_to_numeric_non_numeric(self):
        """Test with non-numeric strings."""
        assert convert_to_numeric("abc") == "abc"
        assert convert_to_numeric("") == ""
        assert convert_to_numeric(None) is None


class TestCleanStockholdersText:
    """Test clean_stockholders_text function."""
    
    def test_clean_stockholders_text_basic(self):
        """Test basic stockholders text cleaning."""
        text = "  Multiple   spaces   "
        assert clean_stockholders_text(text) == "Multiple spaces"
    
    def test_clean_stockholders_text_html_entities(self):
        """Test cleaning HTML entities."""
        text = "Company&nbsp;Name&amp;Co"
        assert clean_stockholders_text(text) == "Company Name&Co"
    
    def test_clean_stockholders_text_empty(self):
        """Test with empty text."""
        assert clean_stockholders_text("") == ""
        assert clean_stockholders_text(None) == ""


class TestHTTPClient:
    """Test HTTPClient functionality."""
    
    def test_init_default(self):
        """Test HTTPClient initialization with defaults."""
        client = HTTPClient()
        assert client.session is not None
        assert client.use_proxies is False
        assert client.proxies == []
    
    def test_init_custom(self):
        """Test HTTPClient initialization with custom values."""
        proxies = ["192.168.1.1:8080", "192.168.1.2:8080"]
        client = HTTPClient(use_proxies=True, proxies=proxies)
        assert client.use_proxies is True
        assert client.proxies == proxies
    
    @patch('pse_scraper.utils.http_client.requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful HTTP request."""
        client = HTTPClient()
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        response = client.make_request("http://example.com")
        
        assert response == mock_response
        mock_request.assert_called_once()
    
    @patch('pse_scraper.utils.http_client.requests.Session.request')
    def test_make_request_failure(self, mock_request):
        """Test failed HTTP request."""
        from requests.exceptions import RequestException
        
        client = HTTPClient()
        
        mock_request.side_effect = RequestException("Network error")
        
        response = client.make_request("http://example.com", retries=1)
        
        assert response is None
    
    def test_get_random_proxy_no_proxies(self):
        """Test getting proxy when no proxies available."""
        client = HTTPClient()
        proxy = client.get_random_proxy()
        assert proxy is None
    
    def test_get_random_proxy_with_proxies(self):
        """Test getting proxy when proxies are available."""
        proxies = ["192.168.1.1:8080", "192.168.1.2:8080"]
        client = HTTPClient(use_proxies=True, proxies=proxies)
        proxy = client.get_random_proxy()
        assert proxy is not None
        assert "http" in proxy
        assert "https" in proxy


class TestLoggingConfig:
    """Test logging configuration."""
    
    def test_setup_logging_enabled(self):
        """Test setting up logging when enabled."""
        logger = setup_logging(enable_logging=True)
        assert logger is not None
        assert logger.name == "PSEDataScraper"
    
    def test_setup_logging_disabled(self):
        """Test setting up logging when disabled.""" 
        logger = setup_logging(enable_logging=False)
        assert logger is not None
        assert logger.name == "null"
        assert logger.level == logging.CRITICAL
