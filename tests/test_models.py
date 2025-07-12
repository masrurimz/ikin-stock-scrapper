"""
Tests for report type models.
"""

import pytest
from pse_scraper.models.report_types import ReportType


class TestReportType:
    """Test ReportType enum."""
    
    def test_report_type_values(self):
        """Test that all report types have correct values."""
        assert ReportType.PUBLIC_OWNERSHIP.value == "Public Ownership Report"
        assert ReportType.ANNUAL.value == "Annual Report"
        assert ReportType.QUARTERLY.value == "Quarterly Report"
        assert ReportType.CASH_DIVIDENDS.value == "Declaration of Cash Dividends"
        assert ReportType.TOP_100_STOCKHOLDERS.value == "List of Top 100 Stockholders"
        assert ReportType.SHARE_BUYBACK.value == "Share Buy-Back Transactions"
    
    def test_report_type_from_string(self):
        """Test creating ReportType from string."""
        assert ReportType("Public Ownership Report") == ReportType.PUBLIC_OWNERSHIP
        assert ReportType("Annual Report") == ReportType.ANNUAL
        assert ReportType("Quarterly Report") == ReportType.QUARTERLY
        assert ReportType("Declaration of Cash Dividends") == ReportType.CASH_DIVIDENDS
        assert ReportType("List of Top 100 Stockholders") == ReportType.TOP_100_STOCKHOLDERS
        assert ReportType("Share Buy-Back Transactions") == ReportType.SHARE_BUYBACK
    
    def test_report_type_invalid(self):
        """Test invalid report type raises ValueError."""
        with pytest.raises(ValueError):
            ReportType("INVALID")
    
    def test_all_report_types_exist(self):
        """Test that all expected report types exist."""
        expected_types = {
            "Public Ownership Report",
            "Annual Report", 
            "Quarterly Report",
            "Declaration of Cash Dividends",
            "List of Top 100 Stockholders",
            "Share Buy-Back Transactions"
        }
        actual_types = {rt.value for rt in ReportType}
        assert actual_types == expected_types
    
    def test_enum_members_exist(self):
        """Test that all expected enum members exist."""
        assert hasattr(ReportType, 'PUBLIC_OWNERSHIP')
        assert hasattr(ReportType, 'ANNUAL')
        assert hasattr(ReportType, 'QUARTERLY')
        assert hasattr(ReportType, 'CASH_DIVIDENDS')
        assert hasattr(ReportType, 'TOP_100_STOCKHOLDERS')
        assert hasattr(ReportType, 'SHARE_BUYBACK')
