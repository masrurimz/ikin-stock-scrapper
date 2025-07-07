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
from pse_scraper.core.processors.share_buyback import ShareBuybackProcessor


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


class TestShareBuybackProcessor:
    """Test ShareBuybackProcessor."""
    
    def test_process_valid_data(self, sample_stock_name, sample_disclosure_date):
        """Test processing valid share buyback data."""
        mock_logger = Mock()
        processor = ShareBuybackProcessor(mock_logger)
        
        # Create realistic share buyback HTML based on our real data analysis
        html = """
        <html>
            <body>
                <table>
                    <caption>Details of Share Buy-Back Transaction(s)</caption>
                    <tr>
                        <th>Date of Transaction</th>
                        <th>Number of Shares Purchased</th>
                        <th>Price Per Share</th>
                    </tr>
                    <tr>
                        <td>Jul 4, 2025</td>
                        <td>349,600</td>
                        <td>27.00</td>
                    </tr>
                    <tr>
                        <td>Jul 4, 2025</td>
                        <td>100,000</td>
                        <td>27.05</td>
                    </tr>
                </table>
                
                <table>
                    <caption>Effects on Number of Shares</caption>
                    <tr>
                        <th></th>
                        <th>Before</th>
                        <th>After</th>
                    </tr>
                    <tr>
                        <td>Outstanding Shares</td>
                        <td>14,562,064,253</td>
                        <td>14,561,614,653</td>
                    </tr>
                    <tr>
                        <td>Treasury Shares</td>
                        <td>2,150,755,595</td>
                        <td>2,151,205,195</td>
                    </tr>
                </table>
                
                <table class="type1">
                    <tr>
                        <td>Cumulative Number of Shares Purchased to Date</td>
                        <td>876,032,246</td>
                    </tr>
                    <tr>
                        <td>Total Amount Appropriated for the Buy-Back Program</td>
                        <td>26,070,000,000.00</td>
                    </tr>
                    <tr>
                        <td>Total Amount of Shares Repurchased</td>
                        <td>22,885,247,993.00</td>
                    </tr>
                </table>
                
                <table class="type2">
                    <tr>
                        <td>Name</td>
                        <td>Michael Blase Aquilizan</td>
                    </tr>
                    <tr>
                        <td>Designation</td>
                        <td>Department Manager</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock_name"] == sample_stock_name
        assert result["disclosure_date"] == sample_disclosure_date
        assert "is_amended_report" in result
        
        # Check transaction summary
        assert result["total_transactions"] == 2
        assert result["total_shares_purchased"] == 449600  # 349,600 + 100,000
        assert result["weighted_average_price"] > 0
        assert result["total_transaction_value"] > 0
        
        # Check share effects
        assert result["outstanding_shares_before"] == 14562064253
        assert result["outstanding_shares_after"] == 14561614653
        assert result["outstanding_shares_change"] == 449600
        assert result["treasury_shares_before"] == 2150755595
        assert result["treasury_shares_after"] == 2151205195
        assert result["treasury_shares_change"] == 449600
        
        # Check program summary
        assert result["cumulative_shares_purchased"] == 876032246
        assert result["total_program_budget"] == 26070000000.00
        assert result["total_amount_spent"] == 22885247993.00
        
        # Check contact info
        assert result["contact_name"] == "Michael Blase Aquilizan"
        assert result["contact_designation"] == "Department Manager"
    
    def test_process_no_transaction_table(self, sample_stock_name, sample_disclosure_date):
        """Test processing when no transaction table exists."""
        mock_logger = Mock()
        processor = ShareBuybackProcessor(mock_logger)
        
        html = """
        <html>
            <body>
                <table class="type1">
                    <tr>
                        <td>Total Amount Appropriated for the Buy-Back Program</td>
                        <td>26,070,000,000.00</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock_name"] == sample_stock_name
        assert result["disclosure_date"] == sample_disclosure_date
        assert "is_amended_report" in result
        assert result["total_program_budget"] == 26070000000.00
        # Should not have transaction data
        assert "total_transactions" not in result
    
    def test_process_empty_document(self, sample_stock_name, sample_disclosure_date):
        """Test processing empty share buyback document."""
        mock_logger = Mock()
        processor = ShareBuybackProcessor(mock_logger)
        
        html = "<html><body><p>No buyback data</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        # Should return basic result with only basic fields
        assert result is not None
        assert result["stock_name"] == sample_stock_name
        assert result["disclosure_date"] == sample_disclosure_date
        assert "is_amended_report" in result
        # Should have no transaction data beyond basic fields
        assert len(result) == 3  # Only basic fields: stock_name, disclosure_date, is_amended_report
    
    def test_process_partial_data(self, sample_stock_name, sample_disclosure_date):
        """Test processing with only some data sections."""
        mock_logger = Mock()
        processor = ShareBuybackProcessor(mock_logger)
        
        html = """
        <html>
            <body>
                <table>
                    <caption>Effects on Number of Shares</caption>
                    <tr>
                        <th></th>
                        <th>Before</th>
                        <th>After</th>
                    </tr>
                    <tr>
                        <td>Outstanding Shares</td>
                        <td>1,000,000</td>
                        <td>900,000</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock_name"] == sample_stock_name
        assert result["disclosure_date"] == sample_disclosure_date
        assert "is_amended_report" in result
        assert result["outstanding_shares_before"] == 1000000
        assert result["outstanding_shares_after"] == 900000
        assert result["outstanding_shares_change"] == 100000
    
    def test_process_invalid_numeric_data(self, sample_stock_name, sample_disclosure_date):
        """Test processing with invalid numeric data."""
        mock_logger = Mock()
        processor = ShareBuybackProcessor(mock_logger)
        
        html = """
        <html>
            <body>
                <table>
                    <caption>Details of Share Buy-Back Transaction(s)</caption>
                    <tr>
                        <th>Date of Transaction</th>
                        <th>Number of Shares Purchased</th>
                        <th>Price Per Share</th>
                    </tr>
                    <tr>
                        <td>Jul 4, 2025</td>
                        <td>invalid_number</td>
                        <td>invalid_price</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        # Should handle invalid data gracefully
        assert result is not None
        assert result["stock_name"] == sample_stock_name
        assert result["disclosure_date"] == sample_disclosure_date
        assert "is_amended_report" in result
        # Should have empty transaction summary since data is invalid
        assert result.get("total_transactions", 0) == 0


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
            StockholdersProcessor(mock_logger),
            ShareBuybackProcessor(mock_logger)
        ]
        
        empty_html = "<html><body></body></html>"
        soup = BeautifulSoup(empty_html, 'html.parser')
        
        for processor in processors:
            result = processor.process(soup, "TEST", "2024-01-15")
            # Some processors might return None, others might return minimal data
            if result is not None:
                # ShareBuybackProcessor uses different key format
                if hasattr(processor, '__class__') and 'ShareBuyback' in processor.__class__.__name__:
                    assert result["stock_name"] == "TEST"
                    assert result["disclosure_date"] == "2024-01-15"
                else:
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
            StockholdersProcessor(mock_logger),
            ShareBuybackProcessor(mock_logger)
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
            # Some processors might return None for complex HTML that doesn't match their pattern
            if result is not None:
                if hasattr(result, 'get'):
                    # For ShareBuybackProcessor which uses different key format
                    assert result.get("stock_name") == "TESTCORP" or result.get("stock name") == "TESTCORP"
                    assert result.get("disclosure_date") == "2024-03-15" or result.get("disclosure date") == "2024-03-15"
                    # Should contain at least the basic fields
                    assert len(result) >= 2
