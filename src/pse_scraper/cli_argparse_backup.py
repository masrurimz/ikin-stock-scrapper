"""PSE Data Scraper CLI - Command line interface for scraping PSE Edge data."""

import argparse
import sys
import logging
from typing import Dict

from .core import PSEDataScraper
from .models.report_types import ReportType


def interactive_menu():
    """Interactive menu mode matching the original batch_file.py flow."""
    # Default settings
    settings = {
        "enable_logging": True,
        "use_proxies": False,
        "max_workers": 5,
        "default_save_format": ["csv"],
    }

    # Setup logging using the same system as PSEDataScraper
    from .utils.logging_config import setup_logging
    logger = setup_logging(settings["enable_logging"])
    
    # Also get a CLI-specific logger that shares the same handlers but doesn't duplicate
    cli_logger = logging.getLogger("PSEDataScraper.CLI")
    cli_logger.propagate = False  # Prevent duplicate messages
    if settings["enable_logging"]:
        # Add console handler to CLI logger to show CLI-specific messages
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        cli_logger.addHandler(ch)
        cli_logger.setLevel(logging.INFO)
    else:
        cli_logger.addHandler(logging.NullHandler())
        cli_logger.setLevel(logging.CRITICAL)

    try:
        scraper = PSEDataScraper(
            max_workers=settings["max_workers"],
            use_proxies=settings["use_proxies"],
            enable_logging=settings["enable_logging"],
        )

        # Mapping for menu choices to ReportType
        report_type_mapping = {
            1: ReportType.PUBLIC_OWNERSHIP,
            2: ReportType.QUARTERLY,
            3: ReportType.ANNUAL,
            4: ReportType.TOP_100_STOCKHOLDERS,
            5: ReportType.CASH_DIVIDENDS,
        }

        # Display program header
        print("\n" + "="*60)
        print("📈 PSE DATA SCRAPER - Philippine Stock Exchange")
        print("="*60)
        print("Scrape financial data from PSE Edge platform")
        print("\n🔍 SEARCH OPTIONS:")
        print("  • Company Symbol: SM, BDO, PLDT, etc.")  
        print("  • Single Company ID: Any number (1, 2, 3, etc.)")
        print("  • 🚀 BULK PROCESSING: Range of IDs (e.g., 1-100)")
        print("\n📊 AVAILABLE REPORTS:")
        print("  1. Public Ownership Report")
        print("  2. Quarterly Report")
        print("  3. Annual Report")
        print("  4. List of Top 100 Stockholders")
        print("  5. Declaration of Cash Dividends")

        # Main menu loop
        while True:
            print("\n============ MENU =============")
            print("|    1. Public Ownership")
            print("|    2. Quarterly Report")
            print("|    3. Annual Report")
            print("|    4. List of Top 100 Stockholders")
            print("|    5. Declaration of Cash Dividends")
            print("|    6. Settings")
            print("|    7. Exit")
            print("===============================")

            try:
                choice = int(input("Enter your choice: "))

                if choice == 7:  # Exit
                    if settings["enable_logging"]:
                        cli_logger.info("Program finished")
                    break

                elif choice == 6:  # Settings
                    while True:
                        print("\n========= SETTINGS ==========")
                        print(f"1. Logging: {'Enabled' if settings['enable_logging'] else 'Disabled'}")
                        print(f"2. Proxy: {'Enabled' if settings['use_proxies'] else 'Disabled'}")
                        print(f"3. Max Workers: {settings['max_workers']}")
                        print(f"4. Save Format: {' and '.join(settings['default_save_format'])}")
                        print("5. Back to Main Menu")
                        print("============================")

                        setting_choice = input("Select setting (1-5): ").strip()

                        if setting_choice == "1":
                            settings["enable_logging"] = not settings["enable_logging"]
                            
                            # Reinitialize scraper with new logging setting
                            scraper = PSEDataScraper(
                                max_workers=settings["max_workers"],
                                use_proxies=settings["use_proxies"],
                                enable_logging=settings["enable_logging"],
                            )
                            
                            # Update the logger for CLI too
                            logger = setup_logging(settings["enable_logging"])
                            
                            # Reconfigure CLI logger
                            cli_logger.handlers.clear()
                            cli_logger.propagate = False
                            if settings["enable_logging"]:
                                ch = logging.StreamHandler()
                                ch.setLevel(logging.INFO)
                                formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                                ch.setFormatter(formatter)
                                cli_logger.addHandler(ch)
                                cli_logger.setLevel(logging.INFO)
                            else:
                                cli_logger.addHandler(logging.NullHandler())
                                cli_logger.setLevel(logging.CRITICAL)
                            
                            print(f"Logging {'enabled' if settings['enable_logging'] else 'disabled'}")

                        elif setting_choice == "2":
                            settings["use_proxies"] = not settings["use_proxies"]
                            scraper.use_proxies = settings["use_proxies"]
                            print(f"Proxy {'enabled' if settings['use_proxies'] else 'disabled'}")

                        elif setting_choice == "3":
                            try:
                                new_workers = int(input("Enter number of max workers (1-10): "))
                                if 1 <= new_workers <= 10:
                                    settings["max_workers"] = new_workers
                                    scraper.max_workers = new_workers
                                    print(f"Max workers changed to {new_workers}")
                                else:
                                    print("Number of workers must be between 1-10")
                            except ValueError:
                                print("Please enter a valid number")

                        elif setting_choice == "4":
                            print("\nSelect save format:")
                            print("1. CSV only (default)")
                            print("2. JSON only")
                            print("3. Both CSV and JSON")
                            format_choice = input("Choice: ").strip()

                            if format_choice == "1":
                                settings["default_save_format"] = ["csv"]
                            elif format_choice == "2":
                                settings["default_save_format"] = ["json"]
                            elif format_choice == "3":
                                settings["default_save_format"] = ["csv", "json"]
                            else:
                                print("Invalid choice, keeping current format")

                            print(f"Save format set to: {' and '.join(settings['default_save_format'])}")

                        elif setting_choice == "5":
                            break

                        else:
                            print("Invalid choice")

                    continue

                # Validate choice / Report Process
                if choice not in report_type_mapping:
                    print("Invalid choice. Please try again.")
                    continue

                # Reset data before starting new search
                scraper.data = []
                scraper.stop_iteration = False
                if settings["enable_logging"]:
                    cli_logger.info("Starting new search")

                report_type = report_type_mapping[choice]
                filename = input("Enter output filename: ")
                
                print("\nCompany Selection Options:")
                print("1. Single company by symbol: Enter company symbol (e.g., 'SM', 'BDO', 'PLDT')")
                print("2. Single company by ID: Enter one company ID (e.g., '5')")
                print("3. Bulk processing: Enter company ID range (e.g., start=1, end=100)")
                print("   • Company IDs are sequential numbers in PSE database")
                print("   • Use bulk processing to scrape multiple companies at once")
                
                start_company = input("\nEnter company symbol OR starting company ID: ").strip()
                
                if not start_company:
                    print("Error: Company symbol/ID cannot be empty.")
                    continue
                
                # Check if it's a numeric ID (could be single or start of range)
                if start_company.isdigit():
                    end_company = input("Enter ending company ID for bulk processing (or press Enter for single company): ").strip()
                    
                    if end_company and end_company.isdigit():
                        # Bulk processing mode
                        start_id = int(start_company)
                        end_id = int(end_company)
                        
                        if end_id < start_id:
                            print("Error: Ending company ID must be greater than or equal to starting ID.")
                            continue
                        
                        company_count = end_id - start_id + 1
                        print(f"\n🔄 BULK PROCESSING MODE")
                        print(f"   Range: Company ID {start_id} to {end_id}")
                        print(f"   Total companies: {company_count}")
                        
                        # Ask for confirmation for large ranges
                        if company_count > 50:
                            print(f"\n⚠️  Large bulk operation detected!")
                            confirm = input(f"   Process {company_count} companies? This may take a while. (y/N): ").strip().lower()
                            if confirm != 'y' and confirm != 'yes':
                                print("Operation cancelled.")
                                continue
                        elif company_count > 10:
                            confirm = input(f"   Process {company_count} companies? (Y/n): ").strip().lower()
                            if confirm == 'n' or confirm == 'no':
                                print("Operation cancelled.")
                                continue
                        
                        print(f"\n🚀 Starting bulk processing...")
                        for i, company_id in enumerate(range(start_id, end_id + 1), 1):
                            print(f"   [{i:3d}/{company_count:3d}] Processing company ID {company_id}...")
                            if settings["enable_logging"]:
                                cli_logger.info(f"Processing company ID {company_id} ({i}/{company_count})")
                            scraper.scrape_data(str(company_id), report_type)
                    else:
                        # Single company by ID
                        print(f"\n📋 SINGLE COMPANY MODE")
                        print(f"   Processing company ID: {start_company}")
                        if settings["enable_logging"]:
                            cli_logger.info(f"Processing single company ID {start_company}")
                        scraper.scrape_data(start_company, report_type)
                else:
                    # Company symbol provided
                    print(f"\n📊 COMPANY SYMBOL MODE")
                    print(f"   Processing company: {start_company.upper()}")
                    if settings["enable_logging"]:
                        cli_logger.info(f"Processing company symbol {start_company}")
                    scraper.scrape_data(start_company.upper(), report_type)

                # Save results with default format
                scraper.save_results(filename, settings["default_save_format"])
                
                # Show completion summary
                print(f"\n✅ PROCESSING COMPLETED!")
                print(f"   📊 Records found: {len(scraper.data)}")
                print(f"   💾 Saved to: {filename}.{'/'.join(settings['default_save_format'])}")
                
                if len(scraper.data) == 0:
                    print(f"\n⚠️  NO DATA FOUND")
                    print(f"   This could mean:")
                    print(f"   • The company ID/symbol doesn't exist")
                    print(f"   • No reports of this type are available")
                    print(f"   • The company hasn't filed recent reports")
                else:
                    print(f"   🎉 Success! Found data for {len(scraper.data)} entries")

            except ValueError as e:
                if settings["enable_logging"]:
                    cli_logger.error(f"Input error: {e}")
                print("Invalid input. Please enter a valid number for menu choice.")

            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                continue

            except Exception as e:
                if settings["enable_logging"]:
                    cli_logger.error(f"Unexpected error: {e}")
                print(f"An error occurred: {e}")

    except KeyboardInterrupt:
        if settings["enable_logging"]:
            cli_logger.info("Program stopped by user")
        print("\nProgram stopped")

    except Exception as e:
        if settings["enable_logging"]:
            cli_logger.error(f"Fatal error: {e}")
        print(f"A fatal error occurred: {e}")


def command_line_mode():
    """Command line argument mode for non-interactive usage."""
def command_line_mode():
    """Command line argument mode for non-interactive usage."""
    parser = argparse.ArgumentParser(
        description="PSE Data Scraper - Scrape data from PSE Edge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using company symbols:
  pse-scraper SM public_ownership --output sm_ownership
  pse-scraper BDO annual_report --output bdo_annual --formats json csv
  pse-scraper PLDT quarterly_report --workers 3 --use-proxies
  
  # Using numeric company IDs (for bulk processing):
  pse-scraper 1 cash_dividends --output company_1_dividends
  pse-scraper 15 stockholders --output company_15_stockholders
  
  # Interactive mode (recommended for bulk processing):
  pse-scraper --interactive
        """
    )
    
    parser.add_argument(
        "company_id",
        nargs="?",
        help="Company ID/Stock Symbol (e.g., 'SM', 'BDO', 'PLDT') or numeric company ID (e.g., 1, 2, 3). If not provided, interactive mode starts."
    )
    
    parser.add_argument(
        "report_type",
        nargs="?",
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
        "--interactive", "-i",
        action="store_true",
        help="Start interactive menu mode"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="PSE Data Scraper 2.0.0"
    )

    args = parser.parse_args()

    # If no arguments or interactive flag, start interactive mode
    if not args.company_id or not args.report_type or args.interactive:
        interactive_menu()
        return

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


def main():
    """Main CLI function that determines which mode to use."""
    command_line_mode()
