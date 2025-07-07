"""
Report types enumeration for PSE data scraping.
"""

from enum import Enum


class ReportType(Enum):
    """Enum untuk jenis-jenis laporan yang tersedia"""

    PUBLIC_OWNERSHIP = "Public Ownership Report"
    QUARTERLY = "Quarterly Report"
    ANNUAL = "Annual Report"
    TOP_100_STOCKHOLDERS = "List of Top 100 Stockholders"
    CASH_DIVIDENDS = "Declaration of Cash Dividends"
    SHARE_BUYBACK = "Share Buy-Back Transactions"
