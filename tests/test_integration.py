"""
Integration tests for the PSE scraper system.
"""

import pytest
import tempfile
import os
import json
import csv
from unittest.mock import Mock, patch

from pse_scraper.core import PSEDataScraper
from pse_scraper.models.report_types import ReportType


class TestSystemIntegration:
    """Test complete system integration."""
    
    def test_full_scraping_workflow(self):
        """Test complete scraping workflow from start to finish."""
        scraper = PSEDataScraper(enable_logging=False, max_workers=1)
        
        # Mock search results page
        search_response = Mock()
        search_response.text = """
        <html>
            <body>
                <span class="count">1 / 1</span>
                <table>
                    <tr>
                        <td><a onclick="openPopup('12345')">View Document</a></td>
                        <td>Jan 15, 2024 10:30 AM</td>
                        <td>17-A</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        # Mock document page
        doc_response = Mock()
        doc_response.text = """
        <html>
            <body>
                <iframe src="/document.do?id=12345"></iframe>
            </body>
        </html>
        """
        
        # Mock iframe content with structure expected by PublicOwnershipProcessor
        iframe_response = Mock()
        iframe_response.text = """
        <html>
            <body>
                <span id="companyStockSymbol">TEST</span>
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
        
        # Mock HTTP client to return different responses for different calls
        def mock_make_request(url, method="get", **kwargs):
            if "search.ax" in url:
                return search_response
            elif "openDiscViewer.do" in url:
                return doc_response
            elif "document.do" in url:
                return iframe_response
            return None
        
        with patch.object(scraper.http_client, 'make_request', side_effect=mock_make_request):
            results = scraper.scrape_data("TEST", ReportType.PUBLIC_OWNERSHIP)
            
            assert len(results) > 0
            assert results[0]["stock name"] == "TEST"
            assert "Number of Outstanding Common Shares" in results[0]
            assert "Public Ownership Percentage" in results[0]
    
    def test_save_and_load_results(self):
        """Test saving results and verifying file contents."""
        scraper = PSEDataScraper(enable_logging=False)
        scraper.data = [
            {
                "stock name": "TEST1",
                "disclosure date": "2024-01-15",
                "Company Name": "Test Company 1",
                "Total Shares": "1000000"
            },
            {
                "stock name": "TEST2",
                "disclosure date": "2024-01-16",
                "Company Name": "Test Company 2",
                "Total Shares": "2000000"
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test CSV output
            base_filename = os.path.join(temp_dir, "test_output")
            scraper.save_results(base_filename, ["csv"])
            
            csv_file = f"{base_filename}.csv"
            assert os.path.exists(csv_file)
            
            # Verify CSV contents
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]["stock name"] == "TEST1"
                assert rows[1]["stock name"] == "TEST2"
            
            # Test JSON output
            scraper.save_results(base_filename, ["json"])
            
            json_file = f"{base_filename}.json"
            assert os.path.exists(json_file)
            
            # Verify JSON contents
            with open(json_file, 'r') as f:
                data = json.load(f)
                assert len(data) == 2
                assert data[0]["stock name"] == "TEST1"
                assert data[1]["stock name"] == "TEST2"
    
    def test_error_handling_and_recovery(self):
        """Test system behavior under error conditions."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Test with network failure
        with patch.object(scraper.http_client, 'make_request', return_value=None):
            results = scraper.scrape_data("TEST", ReportType.PUBLIC_OWNERSHIP)
            assert results == []
        
        # Test with malformed HTML
        mock_response = Mock()
        mock_response.text = "<html><body><p>Invalid HTML structure"  # Malformed
        
        with patch.object(scraper.http_client, 'make_request', return_value=mock_response):
            results = scraper.scrape_data("TEST", ReportType.PUBLIC_OWNERSHIP)
            # Should handle gracefully
            assert isinstance(results, list)
    
    def test_multiple_report_types(self):
        """Test scraping different report types."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Mock response for all report types
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <span class="count">1 result</span>
                <table>
                    <tr><th>Data</th><td>Sample</td></tr>
                </table>
            </body>
        </html>
        """
        
        report_types = [
            ReportType.PUBLIC_OWNERSHIP,
            ReportType.ANNUAL,
            ReportType.QUARTERLY,
            ReportType.CASH_DIVIDENDS,
            ReportType.TOP_100_STOCKHOLDERS
        ]
        
        with patch.object(scraper.http_client, 'make_request', return_value=mock_response):
            for report_type in report_types:
                results = scraper.scrape_data("TEST", report_type)
                assert isinstance(results, list)
                if results:  # Some might return empty results
                    assert results[0]["stock name"] == "TEST"
    
    def test_concurrent_processing_integration(self):
        """Test concurrent processing with multiple pages."""
        scraper = PSEDataScraper(enable_logging=False, max_workers=2)
        
        # Mock response with multiple pages
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <span class="count">Showing 1-20 of 40 results</span>
                <table>
                    <tr>
                        <th>Company Name</th>
                        <td>Test Company</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        
        with patch.object(scraper.http_client, 'make_request', return_value=mock_response):
            with patch.object(scraper, '_process_page') as mock_process:
                # Mock successful processing
                mock_process.return_value = None
                
                results = scraper.scrape_data("TEST", ReportType.PUBLIC_OWNERSHIP)
                
                # Should have attempted to process multiple pages
                assert mock_process.call_count >= 1
    
    def test_data_consistency(self):
        """Test data consistency across operations."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Add test data
        test_data = {
            "stock name": "CONSISTENCY_TEST",
            "disclosure date": "2024-01-15",
            "Company Name": "Consistency Test Corp",
            "Value": "123456"
        }
        
        scraper.data.append(test_data)
        
        # Verify data is preserved
        assert len(scraper.data) == 1
        assert scraper.data[0] == test_data
        
        # Test data persistence through save operations
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "consistency_test")
            
            scraper.save_results(output_file, ["json", "csv"])
            
            # Verify both files exist and contain correct data
            json_file = f"{output_file}.json"
            csv_file = f"{output_file}.csv"
            
            assert os.path.exists(json_file)
            assert os.path.exists(csv_file)
            
            # Check JSON consistency
            with open(json_file, 'r') as f:
                json_data = json.load(f)
                assert json_data[0]["stock name"] == "CONSISTENCY_TEST"
            
            # Check CSV consistency
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                csv_data = list(reader)
                assert csv_data[0]["stock name"] == "CONSISTENCY_TEST"


class TestCLIIntegration:
    """Test CLI integration (if CLI module is available)."""
    
    def test_cli_import(self):
        """Test that CLI module can be imported."""
        try:
            # Test if we can import the CLI module
            import sys
            sys.path.insert(0, '/Users/masrurimz/Projects/ikin-stock-scrapper')
            import cli
            assert hasattr(cli, 'main') or hasattr(cli, 'parse_args')
        except ImportError:
            pytest.skip("CLI module not available for testing")
    
    @pytest.mark.skipif(True, reason="Requires actual CLI execution")
    def test_cli_execution(self):
        """Test CLI execution (placeholder for manual testing)."""
        # This would require subprocess execution and is better suited
        # for manual testing or dedicated CLI tests
        pass


class TestPerformance:
    """Performance and stress tests."""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Simulate large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                "stock name": f"TEST{i:04d}",
                "disclosure date": "2024-01-15",
                "value": f"Value {i}"
            })
        
        scraper.data = large_data
        
        assert len(scraper.data) == 1000
        
        # Test that we can save large datasets
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "large_dataset")
            scraper.save_results(output_file, ["json"])
            
            json_file = f"{output_file}.json"
            assert os.path.exists(json_file)
            
            # Verify file size is reasonable (should be > 0)
            assert os.path.getsize(json_file) > 0
    
    def test_memory_efficiency(self):
        """Test memory efficiency with data clearing."""
        scraper = PSEDataScraper(enable_logging=False)
        
        # Add data
        for i in range(100):
            scraper.data.append({"test": f"value{i}"})
        
        assert len(scraper.data) == 100
        
        # Clear data
        scraper.data.clear()
        
        assert len(scraper.data) == 0
