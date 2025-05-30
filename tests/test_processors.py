"""
Tests for report processors.
"""

import pytest
from unittest.mock import Mock
from bs4 import BeautifulSoup

from pse_scraper.core.processors.public_ownership import PublicOwnershipProcessor
from pse_scraper.core.processors.annual_report import AnnualReportProcessor
from pse_scraper.core.processors.quarterly_report import QuarterlyReportProcessor
from pse_scraper.core.processors.cash_dividends import CashDividendsProcessor
from pse_scraper.core.processors.stockholders import StockholdersProcessor


class TestPublicOwnershipProcessor:
    """Test PublicOwnershipProcessor."""
    
    def test_process_valid_data(self, sample_html, sample_stock_name, sample_disclosure_date):
        """Test processing valid public ownership data."""
        mock_logger = Mock()
        processor = PublicOwnershipProcessor(mock_logger)
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock name"] == sample_stock_name
        assert result["disclosure date"] == sample_disclosure_date
        assert "Company Name" in result
        assert result["Company Name"] == "Sample Company"
    
    def test_process_no_table(self, sample_stock_name, sample_disclosure_date):
        """Test processing when no table exists."""
        mock_logger = Mock()
        processor = PublicOwnershipProcessor(mock_logger)
        
        html = "<html><body><p>No table here</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is None
        mock_logger.warning.assert_called()


class TestAnnualReportProcessor:
    """Test AnnualReportProcessor."""
    
    def test_process_valid_data(self, sample_html, sample_stock_name, sample_disclosure_date):
        """Test processing valid annual report data."""
        mock_logger = Mock()
        processor = AnnualReportProcessor(mock_logger)
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock name"] == sample_stock_name
        assert result["disclosure date"] == sample_disclosure_date
    
    def test_process_no_tables(self, sample_stock_name, sample_disclosure_date):
        """Test processing when no tables exist."""
        mock_logger = Mock()
        processor = AnnualReportProcessor(mock_logger)
        
        html = "<html><body><p>No tables here</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is None
        mock_logger.warning.assert_called()


class TestQuarterlyReportProcessor:
    """Test QuarterlyReportProcessor."""
    
    def test_process_valid_data(self, sample_html, sample_stock_name, sample_disclosure_date):
        """Test processing valid quarterly report data."""
        mock_logger = Mock()
        processor = QuarterlyReportProcessor(mock_logger)
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock name"] == sample_stock_name
        assert result["disclosure date"] == sample_disclosure_date


class TestCashDividendsProcessor:
    """Test CashDividendsProcessor."""
    
    def test_process_valid_data(self, sample_html, sample_stock_name, sample_disclosure_date):
        """Test processing valid cash dividends data."""
        mock_logger = Mock()
        processor = CashDividendsProcessor(mock_logger)
        
        soup = BeautifulSoup(sample_html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock name"] == sample_stock_name
        assert result["disclosure date"] == sample_disclosure_date


class TestStockholdersProcessor:
    """Test StockholdersProcessor."""
    
    def test_process_valid_data(self, sample_stock_name, sample_disclosure_date):
        """Test processing valid stockholders data."""
        mock_logger = Mock()
        processor = StockholdersProcessor(mock_logger)
        
        # Create HTML with stockholders table
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Shares</th>
                        <th>Percentage</th>
                    </tr>
                    <tr>
                        <td>John Doe</td>
                        <td>1,000,000</td>
                        <td>10.5%</td>
                    </tr>
                    <tr>
                        <td>Jane Smith</td>
                        <td>500,000</td>
                        <td>5.2%</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock name"] == sample_stock_name
        assert result["disclosure date"] == sample_disclosure_date
        
        # Check if stockholder data was extracted
        stockholder_keys = [key for key in result.keys() if key.startswith("stockholder_")]
        assert len(stockholder_keys) > 0
    
    def test_process_empty_table(self, sample_stock_name, sample_disclosure_date):
        """Test processing empty stockholders table."""
        mock_logger = Mock()
        processor = StockholdersProcessor(mock_logger)
        
        html = """
        <html>
            <body>
                <table>
                    <tr><th>Empty Table</th></tr>
                </table>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock name"] == sample_stock_name
        assert result["disclosure date"] == sample_disclosure_date


class TestProcessorIntegration:
    """Integration tests for all processors."""
    
    def test_all_processors_handle_empty_soup(self):
        """Test that all processors handle empty soup gracefully."""
        mock_logger = Mock()
        processors = [
            PublicOwnershipProcessor(mock_logger),
            AnnualReportProcessor(mock_logger),
            QuarterlyReportProcessor(mock_logger),
            CashDividendsProcessor(mock_logger),
            StockholdersProcessor(mock_logger)
        ]
        
        empty_html = "<html><body></body></html>"
        soup = BeautifulSoup(empty_html, 'html.parser')
        
        for processor in processors:
            result = processor.process(soup, "TEST", "2024-01-15")
            # Some processors might return None, others might return minimal data
            if result is not None:
                assert result["stock name"] == "TEST"
                assert result["disclosure date"] == "2024-01-15"
    
    def test_all_processors_handle_complex_html(self):
        """Test processors with complex HTML structure."""
        mock_logger = Mock()
        processors = [
            PublicOwnershipProcessor(mock_logger),
            AnnualReportProcessor(mock_logger),
            QuarterlyReportProcessor(mock_logger),
            CashDividendsProcessor(mock_logger),
            StockholdersProcessor(mock_logger)
        ]
        
        complex_html = """
        <html>
            <body>
                <div class="header">
                    <h1>PSE Report</h1>
                </div>
                <div class="content">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Description</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Company Name</td>
                                <td>Test Corporation</td>
                            </tr>
                            <tr>
                                <td>Total Assets</td>
                                <td>1,500,000,000</td>
                            </tr>
                            <tr>
                                <td>Revenue</td>
                                <td>750,000,000</td>
                            </tr>
                        </tbody>
                    </table>
                    <table class="financial-data">
                        <tr>
                            <th>Current Assets</th>
                            <td>500,000,000</td>
                        </tr>
                        <tr>
                            <th>Current Liabilities</th>
                            <td>200,000,000</td>
                        </tr>
                    </table>
                </div>
                <div class="footer">
                    <p>End of report</p>
                </div>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(complex_html, 'html.parser')
        
        for processor in processors:
            result = processor.process(soup, "TESTCORP", "2024-03-15")
            assert result is not None
            assert result["stock name"] == "TESTCORP"
            assert result["disclosure date"] == "2024-03-15"
            # Should contain at least the basic fields (stock name and date)
            assert len(result) >= 2  # At least stock name and date
