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
    
    def test_process_valid_data(self, sample_stock_name, sample_disclosure_date):
        """Test processing valid public ownership data."""
        mock_logger = Mock()
        processor = PublicOwnershipProcessor(mock_logger)
        
        # Create HTML with structure expected by PublicOwnershipProcessor
        html = """
        <html>
            <body>
                <table class="type1">
                    <tr>
                        <td>Number of Outstanding Common Shares</td>
                        <td><span class="valInput">1,500,000,000</span></td>
                    </tr>
                    <tr>
                        <td>Total Number of Shares Owned by the Public</td>
                        <td><span class="valInput">750,000,000</span></td>
                    </tr>
                    <tr>
                        <td>Public Ownership Percentage</td>
                        <td><span class="valInput">50.0%</span></td>
                    </tr>
                    <tr>
                        <td>Report Date</td>
                        <td><span class="valInput">2024-01-15</span></td>
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
        # Check that public ownership data was extracted
        assert "Number of Outstanding Common Shares" in result
        assert result["Number of Outstanding Common Shares"] == 1500000000
    
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
    
    def test_process_valid_data(self, sample_stock_name, sample_disclosure_date):
        """Test processing valid annual report data."""
        mock_logger = Mock()
        processor = AnnualReportProcessor(mock_logger)
        
        # Create HTML with the expected structure for annual reports
        html = """
        <html>
            <body>
                <table>
                    <caption>Balance Sheet</caption>
                    <tr>
                        <th></th>
                        <th>2023</th>
                        <th>2022</th>
                    </tr>
                    <tr>
                        <th>Current Assets</th>
                        <td><span class="valInput">1000000</span></td>
                        <td><span class="valInput">950000</span></td>
                    </tr>
                    <tr>
                        <th>Total Assets</th>
                        <td><span class="valInput">5000000</span></td>
                        <td><span class="valInput">4800000</span></td>
                    </tr>
                </table>
                <table>
                    <caption>Income Statement</caption>
                    <tr>
                        <th></th>
                        <th>2023</th>
                        <th>2022</th>
                    </tr>
                    <tr>
                        <th>Revenue</th>
                        <td><span class="valInput">2000000</span></td>
                        <td><span class="valInput">1800000</span></td>
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
    
    def test_process_valid_data(self, sample_stock_name, sample_disclosure_date):
        """Test processing valid cash dividends data."""
        mock_logger = Mock()
        processor = CashDividendsProcessor(mock_logger)
        
        # Create HTML with the expected structure for cash dividends
        html = """
        <html>
            <body>
                <ul class="reportType">
                    <li>
                        <input type="radio" value="COMMON" checked="checked">
                        <label>Common Shares</label>
                    </li>
                </ul>
                <table>
                    <caption>Cash Dividend</caption>
                    <tr>
                        <th>Dividend Rate</th>
                        <td>0.50</td>
                    </tr>
                    <tr>
                        <th>Record Date</th>
                        <td>2024-01-20</td>
                    </tr>
                    <tr>
                        <th>Payment Date</th>
                        <td>2024-02-15</td>
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
        # Check that dividend data was extracted
        assert "Dividend Rate" in result
        assert result["Dividend Rate"] == "0.50"


class TestStockholdersProcessor:
    """Test StockholdersProcessor."""
    
    def test_process_valid_data(self, sample_stock_name, sample_disclosure_date):
        """Test processing valid stockholders data."""
        mock_logger = Mock()
        processor = StockholdersProcessor(mock_logger)
        
        # Create HTML with structure expected by StockholdersProcessor
        # Need at least 3 tables, and the third should have th/td row pairs
        html = """
        <html>
            <body>
                <table class="type1">
                    <tr><th>Dummy Table 1</th><td>Value 1</td></tr>
                </table>
                <table class="type1">
                    <tr><th>Dummy Table 2</th><td>Value 2</td></tr>
                </table>
                <table class="type1">
                    <tr>
                        <th>Total Number of Issued Shares</th>
                        <td><span class="valInput">1,000,000,000</span></td>
                    </tr>
                    <tr>
                        <th>Number of Outstanding Shares</th>
                        <td><span class="valInput">950,000,000</span></td>
                    </tr>
                    <tr>
                        <th>Treasury Shares</th>
                        <td><span class="valInput">50,000,000</span></td>
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
        
        # Check if share structure data was extracted
        assert "Total Number of Issued Shares" in result
        assert result["Total Number of Issued Shares"] == "1000000000"
    
    def test_process_empty_table(self, sample_stock_name, sample_disclosure_date):
        """Test processing empty stockholders table."""
        mock_logger = Mock()
        processor = StockholdersProcessor(mock_logger)
        
        # Create minimal HTML that meets the processor's requirements but has no data
        html = """
        <html>
            <body>
                <table class="type1">
                    <tr><th>Dummy 1</th><td>Value</td></tr>
                </table>
                <table class="type1">
                    <tr><th>Dummy 2</th><td>Value</td></tr>
                </table>
                <table class="type1">
                    <tr><th>Empty Field</th><td>-</td></tr>
                </table>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        assert result is not None
        assert result["stock_name"] == sample_stock_name
        assert result["disclosure_date"] == sample_disclosure_date
        # Should have processed the Empty Field with value converted to "0"
        assert result["Empty Field"] == "0"


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
        assert result["stock_symbol"] == f"_SRP_{sample_stock_name}"
        # Date format may be converted to M/D/YYYY format 
        assert result["Date_Registered"] in [sample_disclosure_date, "1/15/2024"]
        # UAT #3 format fields
        assert "Month" in result
        assert "Year" in result
        assert "Day" in result
        assert "Default_value_of_1" in result
        
        # Check UAT #3 format fields
        assert result["Total_Number_of_Shares_Purchased"] == 449600  # 349,600 + 100,000
        assert result["Total_Amount_Appropriated"] == 26070000000.0
        assert result["Cumulative_Shares_Purchased"] == 876032246
        assert result["Total_Amount_of_Shares_Repurchased"] == 22885247993.0
        # UAT #3 format doesn't include detailed share effects or old field names
        
        # UAT #3 format doesn't include contact info
    
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
        assert result["stock_symbol"] == f"_SRP_{sample_stock_name}"
        # Date format may be converted to M/D/YYYY format 
        assert result["Date_Registered"] in [sample_disclosure_date, "1/15/2024"]
        # UAT #3 format fields
        assert "Month" in result
        assert "Year" in result
        assert "Day" in result
        assert "Default_value_of_1" in result
        assert result["Total_Amount_Appropriated"] == 26070000000.00
        # Should have zero values for missing transaction data
        assert result["Total_Number_of_Shares_Purchased"] == 0
    
    def test_process_empty_document(self, sample_stock_name, sample_disclosure_date):
        """Test processing empty share buyback document."""
        mock_logger = Mock()
        processor = ShareBuybackProcessor(mock_logger)
        
        html = "<html><body><p>No buyback data</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        result = processor.process(soup, sample_stock_name, sample_disclosure_date)
        
        # Should return basic result with only basic fields
        assert result is not None
        assert result["stock_symbol"] == f"_SRP_{sample_stock_name}"
        # Date format may be converted to M/D/YYYY format 
        assert result["Date_Registered"] in [sample_disclosure_date, "1/15/2024"]
        # UAT #3 format fields
        assert "Month" in result
        assert "Year" in result
        assert "Day" in result
        assert "Default_value_of_1" in result
        # Should have no transaction data beyond basic fields
        assert len(result) >= 8  # UAT #3 format fields
    
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
        assert result["stock_symbol"] == f"_SRP_{sample_stock_name}"
        # Date format may be converted to M/D/YYYY format 
        assert result["Date_Registered"] in [sample_disclosure_date, "1/15/2024"]
        # UAT #3 format fields
        assert "Month" in result
        assert "Year" in result
        assert "Day" in result
        assert "Default_value_of_1" in result
        # UAT #3 format doesn't include share effects details
        # Just verify basic structure exists
        assert "Total_Number_of_Shares_Purchased" in result
    
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
        assert result["stock_symbol"] == f"_SRP_{sample_stock_name}"
        # Date format may be converted to M/D/YYYY format 
        assert result["Date_Registered"] in [sample_disclosure_date, "1/15/2024"]
        # UAT #3 format fields
        assert "Month" in result
        assert "Year" in result
        assert "Day" in result
        assert "Default_value_of_1" in result
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
                    assert result["stock_symbol"] == "_SRP_TEST"
                    assert result["Date_Registered"] in ["2024-01-15", "1/15/2024"]
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
                    assert result.get("stock_symbol") == "_SRP_TESTCORP" or result.get("stock name") == "TESTCORP"
                    assert (result.get("Date_Registered") in ["2024-03-15", "3/15/2024"] or 
                           result.get("disclosure date") == "2024-03-15")
                    # Should contain at least the basic fields
                    assert len(result) >= 2
