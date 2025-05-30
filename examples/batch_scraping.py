#!/usr/bin/env python3
"""
Batch scraping example for multiple companies.
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pse_scraper.core import PSEDataScraper
from pse_scraper.models.report_types import ReportType


def batch_scrape_public_ownership():
    """Example: Batch scrape public ownership for multiple companies."""
    print("Batch Scraping: Public Ownership Reports")
    print("=" * 50)
    
    companies = ["SM", "BDO", "JFC", "ALI", "PLDT"]
    all_data = []
    
    for company in companies:
        print(f"Scraping {company}...")
        
        scraper = PSEDataScraper(max_workers=3, enable_logging=False)
        scraper.scrape_data(company, ReportType.PUBLIC_OWNERSHIP)
        
        print(f"  Found {len(scraper.data)} records for {company}")
        all_data.extend(scraper.data)
        
        # Small delay to be respectful to the server
        time.sleep(1)
    
    # Save all data to a single file
    if all_data:
        # Create a temporary scraper just for saving
        temp_scraper = PSEDataScraper(enable_logging=False)
        temp_scraper.data = all_data
        temp_scraper.save_results("batch_public_ownership", ["json", "csv"])
        
        print(f"\nBatch scraping completed!")
        print(f"Total records: {len(all_data)}")
        print(f"Companies processed: {len(companies)}")
    else:
        print("No data found for any company.")


def batch_scrape_with_different_reports():
    """Example: Scrape different report types for different companies."""
    print("\nBatch Scraping: Different Report Types")
    print("=" * 50)
    
    scraping_tasks = [
        ("SM", ReportType.PUBLIC_OWNERSHIP, "sm_ownership"),
        ("BDO", ReportType.ANNUAL, "bdo_annual"),
        ("JFC", ReportType.CASH_DIVIDENDS, "jfc_dividends"),
        ("ALI", ReportType.QUARTERLY, "ali_quarterly"),
        ("PLDT", ReportType.TOP_100_STOCKHOLDERS, "pldt_stockholders"),
    ]
    
    for company, report_type, filename in scraping_tasks:
        print(f"Scraping {company} - {report_type.value}...")
        
        try:
            scraper = PSEDataScraper(max_workers=2, enable_logging=False)
            scraper.scrape_data(company, report_type)
            scraper.save_results(filename, ["csv"])
            
            print(f"  ✓ Found {len(scraper.data)} records")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print("\nDifferent report types scraping completed!")


def main():
    """Run batch scraping examples."""
    try:
        batch_scrape_public_ownership()
        batch_scrape_with_different_reports()
        
    except KeyboardInterrupt:
        print("\nBatch scraping interrupted by user.")
    except Exception as e:
        print(f"Error in batch scraping: {e}")


if __name__ == "__main__":
    main()
