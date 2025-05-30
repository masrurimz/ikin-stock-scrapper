"""PSE Data Scraper CLI - Command line interface for scraping PSE Edge data."""

import argparse
import sys

from .core import PSEDataScraper
from .models.report_types import ReportType


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="PSE Data Scraper - Scrape data from PSE Edge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pse-scraper SM public_ownership --output sm_ownership
  pse-scraper BDO annual_report --output bdo_annual --formats json csv
  pse-scraper PLDT quarterly_report --workers 3 --use-proxies
  pse-scraper JFC cash_dividends --output jfc_dividends --formats json
  pse-scraper ALI stockholders --output ali_stockholders
        """
    )
    
    parser.add_argument(
        "company_id",
        help="Company ID/Stock Symbol (e.g., SM, BDO, PLDT)"
    )
    
    parser.add_argument(
        "report_type",
        choices=["public_ownership", "annual_report", "quarterly_report", "cash_dividends", "stockholders"],
        help="Type of report to scrape"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="pse_data",
        help="Output filename (without extension, default: pse_data)"
    )
    
    parser.add_argument(
        "--formats", "-f",
        nargs="+",
        choices=["json", "csv"],
        default=["csv"],
        help="Output formats (default: csv)"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=5,
        help="Number of concurrent workers (default: 5)"
    )
    
    parser.add_argument(
        "--use-proxies", "-p",
        action="store_true",
        help="Use proxy rotation (requires proxies.txt file)"
    )
    
    parser.add_argument(
        "--no-logging",
        action="store_true",
        help="Disable logging"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="PSE Data Scraper 2.0.0"
    )

    args = parser.parse_args()

    # Map human-readable report types to enum values
    report_type_mapping = {
        "public_ownership": ReportType.PUBLIC_OWNERSHIP,
        "annual_report": ReportType.ANNUAL,
        "quarterly_report": ReportType.QUARTERLY,
        "cash_dividends": ReportType.CASH_DIVIDENDS,
        "stockholders": ReportType.TOP_100_STOCKHOLDERS,
    }

    # Convert report type string to enum
    try:
        report_type = report_type_mapping[args.report_type]
    except KeyError:
        print(f"Error: Invalid report type '{args.report_type}'")
        print(f"Available types: {', '.join(report_type_mapping.keys())}")
        sys.exit(1)

    # Display configuration
    print(f"PSE Data Scraper v2.0.0")
    print(f"Company: {args.company_id}")
    print(f"Report Type: {report_type.value}")
    print(f"Output: {args.output}")
    print(f"Formats: {', '.join(args.formats)}")
    print(f"Workers: {args.workers}")
    print(f"Use Proxies: {args.use_proxies}")
    print("-" * 50)

    # Initialize scraper
    scraper = PSEDataScraper(
        max_workers=args.workers,
        use_proxies=args.use_proxies,
        enable_logging=not args.no_logging
    )

    try:
        # Start scraping
        scraper.scrape_data(args.company_id.upper(), report_type)
        
        # Save results
        scraper.save_results(args.output, args.formats)
        
        print(f"\nScraping completed successfully!")
        print(f"Total records found: {len(scraper.data)}")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during scraping: {e}")
        sys.exit(1)
