#!/usr/bin/env python3
"""
Basic usage examples for PSE Data Scraper.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pse_scraper.core import PSEDataScraper
from pse_scraper.models.report_types import ReportType


def scrape_public_ownership():
    """Example: Scrape public ownership report for SM."""
    print("Example 1: Scraping public ownership for SM")
    print("-" * 40)
    
    scraper = PSEDataScraper(max_workers=3)
    scraper.scrape_data("SM", ReportType.PUBLIC_OWNERSHIP)
    scraper.save_results("sm_public_ownership", ["json", "csv"])
    print(f"Found {len(scraper.data)} records\n")


def scrape_annual_report():
    """Example: Scrape annual report for BDO."""
    print("Example 2: Scraping annual report for BDO")
    print("-" * 40)
    
    scraper = PSEDataScraper(max_workers=3)
    scraper.scrape_data("BDO", ReportType.ANNUAL)
    scraper.save_results("bdo_annual_report", ["csv"])
    print(f"Found {len(scraper.data)} records\n")


def scrape_cash_dividends():
    """Example: Scrape cash dividends for JFC."""
    print("Example 3: Scraping cash dividends for JFC")
    print("-" * 40)
    
    scraper = PSEDataScraper(max_workers=2)
    scraper.scrape_data("JFC", ReportType.CASH_DIVIDENDS)
    scraper.save_results("jfc_cash_dividends", ["json"])
    print(f"Found {len(scraper.data)} records\n")


def main():
    """Run all basic examples."""
    print("PSE Data Scraper - Basic Usage Examples")
    print("=" * 50)
    
    try:
        scrape_public_ownership()
        scrape_annual_report()
        scrape_cash_dividends()
        
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    main()
