#!/usr/bin/env python3
"""
Advanced usage examples for PSE Data Scraper.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pse_scraper.core import PSEDataScraper
from pse_scraper.models.report_types import ReportType


def scrape_with_proxies():
    """Example: Scrape with proxy rotation (requires proxies.txt)."""
    print("Example 1: Scraping with proxy rotation")
    print("-" * 40)
    
    # Create a sample proxies.txt file if it doesn't exist
    proxies_file = Path("proxies.txt")
    if not proxies_file.exists():
        print("Creating sample proxies.txt file...")
        with open(proxies_file, "w") as f:
            f.write("# Add your proxy list here, one per line\n")
            f.write("# Format: ip:port\n")
            f.write("# Example:\n")
            f.write("# 192.168.1.1:8080\n")
        print("Sample proxies.txt created. Add your proxies and run again.\n")
        return
    
    scraper = PSEDataScraper(
        max_workers=2,
        use_proxies=True,
        enable_logging=True
    )
    scraper.scrape_data("PLDT", ReportType.QUARTERLY)
    scraper.save_results("pldt_quarterly_with_proxies", ["json", "csv"])
    print(f"Found {len(scraper.data)} records\n")


def scrape_with_custom_config():
    """Example: Scrape with custom configuration."""
    print("Example 2: Scraping with custom configuration")
    print("-" * 40)
    
    scraper = PSEDataScraper(
        max_workers=10,  # High concurrency
        use_proxies=False,
        enable_logging=True
    )
    
    scraper.scrape_data("ALI", ReportType.TOP_100_STOCKHOLDERS)
    scraper.save_results("ali_stockholders_fast", ["json"])
    print(f"Found {len(scraper.data)} records\n")


def scrape_without_logging():
    """Example: Scrape without logging for clean output."""
    print("Example 3: Scraping without logging")
    print("-" * 40)
    
    scraper = PSEDataScraper(
        max_workers=3,
        use_proxies=False,
        enable_logging=False  # Disable logging
    )
    
    scraper.scrape_data("MEG", ReportType.PUBLIC_OWNERSHIP)
    scraper.save_results("meg_ownership_clean", ["csv"])
    print(f"Found {len(scraper.data)} records\n")


def main():
    """Run all advanced examples."""
    print("PSE Data Scraper - Advanced Usage Examples")
    print("=" * 50)
    
    try:
        scrape_with_proxies()
        scrape_with_custom_config()
        scrape_without_logging()
        
        print("All advanced examples completed!")
        
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    main()
