"""PSE Data Scraper CLI - Modern Click-based command line interface."""

import click
import sys
import logging
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

from .core import PSEDataScraper
from .models.report_types import ReportType


# Rich console for beautiful output
console = Console()

# Report type mappings
REPORT_TYPES = {
    "public_ownership": ReportType.PUBLIC_OWNERSHIP,
    "quarterly": ReportType.QUARTERLY, 
    "annual": ReportType.ANNUAL,
    "stockholders": ReportType.TOP_100_STOCKHOLDERS,
    "cash_dividends": ReportType.CASH_DIVIDENDS,
}

# CLI Context class to pass settings between commands
class CLIContext:
    def __init__(self):
        self.max_workers = 5
        self.use_proxies = False
        self.enable_logging = True
        self.formats = ["csv"]
        
@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def cli(ctx, version):
    """🚀 PSE Data Scraper - Philippine Stock Exchange data scraping tool.
    
    Scrape financial data from PSE Edge platform including ownership reports,
    quarterly/annual reports, stockholder lists, and dividend declarations.
    """
    if version:
        console.print("📈 [bold blue]PSE Data Scraper[/bold blue] v2.0.0")
        console.print("Philippine Stock Exchange data scraping tool")
        sys.exit(0)
        
    # Initialize context
    ctx.ensure_object(CLIContext)
    
    # If no subcommand is provided, start interactive mode
    if ctx.invoked_subcommand is None:
        ctx.invoke(interactive)


@cli.command()
@click.argument('company', required=True)
@click.argument('report_type', type=click.Choice(list(REPORT_TYPES.keys())))
@click.option('--output', '-o', default='pse_data', 
              help='Output filename (without extension)')
@click.option('--format', '-f', 'formats', multiple=True,
              type=click.Choice(['csv', 'json']), default=['csv'],
              help='Output formats (can specify multiple)')
@click.option('--workers', '-w', default=5, type=click.IntRange(1, 10),
              help='Number of concurrent workers (1-10)')
@click.option('--use-proxies/--no-proxies', default=False,
              help='Enable/disable proxy rotation')
@click.option('--no-logging', is_flag=True, default=False,
              help='Disable logging')
@click.pass_obj
def scrape(ctx: CLIContext, company: str, report_type: str, output: str, 
           formats: List[str], workers: int, use_proxies: bool, no_logging: bool):
    """Scrape data for a single company.
    
    COMPANY: Company symbol (e.g., 'SM', 'BDO') or numeric company ID
    REPORT_TYPE: Type of report to scrape
    
    Examples:
      pse-scraper scrape SM public_ownership --output sm_data
      pse-scraper scrape 123 annual_report --format json csv
    """
    enable_logging = not no_logging
    
    # Display configuration
    _display_scrape_config(company, report_type, output, formats, workers, use_proxies, enable_logging)
    
    # Initialize scraper
    with console.status("[bold green]Initializing scraper..."):
        scraper = PSEDataScraper(
            max_workers=workers,
            use_proxies=use_proxies,
            enable_logging=enable_logging
        )
    
    try:
        # Start scraping with progress indication
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Scraping {company.upper()} data...", total=None)
            scraper.scrape_data(company.upper(), REPORT_TYPES[report_type])
        
        # Save results
        with console.status("[bold blue]Saving results..."):
            scraper.save_results(output, list(formats))
        
        # Display results
        _display_results(scraper.data, output, formats)
        
    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️ Scraping interrupted by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Error during scraping: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.argument('start_id', type=int)
@click.argument('end_id', type=int)
@click.argument('report_type', type=click.Choice(list(REPORT_TYPES.keys())))
@click.option('--output', '-o', required=True,
              help='Output filename (without extension)')
@click.option('--format', '-f', 'formats', multiple=True,
              type=click.Choice(['csv', 'json']), default=['csv'],
              help='Output formats (can specify multiple)')
@click.option('--workers', '-w', default=5, type=click.IntRange(1, 10),
              help='Number of concurrent workers (1-10)')
@click.option('--use-proxies/--no-proxies', default=False,
              help='Enable/disable proxy rotation')
@click.option('--no-logging', is_flag=True, default=False,
              help='Disable logging')
@click.option('--force', is_flag=True, default=False,
              help='Skip confirmation for large ranges')
@click.pass_obj
def bulk(ctx: CLIContext, start_id: int, end_id: int, report_type: str,
         output: str, formats: List[str], workers: int, use_proxies: bool, 
         no_logging: bool, force: bool):
    """Bulk scrape multiple companies by ID range.
    
    START_ID: Starting company ID
    END_ID: Ending company ID  
    REPORT_TYPE: Type of report to scrape
    
    Examples:
      pse-scraper bulk 1 100 public_ownership --output bulk_data
      pse-scraper bulk 50 75 annual_report --format json --force
    """
    if end_id < start_id:
        console.print("[bold red]❌ Error: Ending ID must be >= starting ID[/bold red]")
        sys.exit(1)
    
    enable_logging = not no_logging
    company_count = end_id - start_id + 1
    
    # Confirmation for large ranges
    if not force and company_count > 10:
        if not Confirm.ask(f"Process {company_count} companies? This may take a while."):
            console.print("[yellow]Operation cancelled[/yellow]")
            sys.exit(0)
    
    # Display configuration
    _display_bulk_config(start_id, end_id, report_type, output, formats, workers, use_proxies, enable_logging)
    
    # Initialize scraper
    with console.status("[bold green]Initializing scraper..."):
        scraper = PSEDataScraper(
            max_workers=workers,
            use_proxies=use_proxies,
            enable_logging=enable_logging
        )
    
    try:
        # Bulk scraping with progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Processing companies...", total=company_count)
            
            for i, company_id in enumerate(range(start_id, end_id + 1), 1):
                progress.update(task, description=f"Processing company ID {company_id}")
                scraper.scrape_data(str(company_id), REPORT_TYPES[report_type])
                progress.advance(task)
        
        # Save results
        with console.status("[bold blue]Saving results..."):
            scraper.save_results(output, list(formats))
        
        # Display results
        _display_results(scraper.data, output, formats, is_bulk=True, company_count=company_count)
        
    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️ Bulk processing interrupted by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Error during bulk processing: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.pass_obj
def interactive(ctx: CLIContext):
    """Start interactive mode with guided menus."""
    _run_interactive_mode(ctx)


@cli.command()
@click.pass_obj  
def config(ctx: CLIContext):
    """Configure default settings for the scraper."""
    console.print(Panel.fit("⚙️ PSE Scraper Configuration", style="bold blue"))
    
    while True:
        # Display current settings
        table = Table(title="Current Settings")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Max Workers", str(ctx.max_workers))
        table.add_row("Use Proxies", "Yes" if ctx.use_proxies else "No")
        table.add_row("Enable Logging", "Yes" if ctx.enable_logging else "No")
        table.add_row("Default Formats", ", ".join(ctx.formats))
        
        console.print(table)
        console.print()
        
        choices = [
            "1. Change max workers",
            "2. Toggle proxy usage", 
            "3. Toggle logging",
            "4. Change default formats",
            "5. Back to main menu"
        ]
        
        for choice in choices:
            console.print(choice)
        
        selection = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="5")
        
        if selection == "1":
            new_workers = click.prompt("Enter max workers (1-10)", type=click.IntRange(1, 10), 
                                     default=ctx.max_workers)
            ctx.max_workers = new_workers
            console.print(f"[green]✓ Max workers set to {new_workers}[/green]")
            
        elif selection == "2":
            ctx.use_proxies = not ctx.use_proxies
            console.print(f"[green]✓ Proxy usage {'enabled' if ctx.use_proxies else 'disabled'}[/green]")
            
        elif selection == "3":
            ctx.enable_logging = not ctx.enable_logging
            console.print(f"[green]✓ Logging {'enabled' if ctx.enable_logging else 'disabled'}[/green]")
            
        elif selection == "4":
            console.print("Select formats (space-separated): csv json both")
            format_input = Prompt.ask("Formats", default=" ".join(ctx.formats))
            
            if "both" in format_input.lower():
                ctx.formats = ["csv", "json"]
            elif "json" in format_input.lower() and "csv" not in format_input.lower():
                ctx.formats = ["json"]
            else:
                ctx.formats = ["csv"]
            
            console.print(f"[green]✓ Default formats set to: {', '.join(ctx.formats)}[/green]")
            
        elif selection == "5":
            break
        
        console.print()


def _display_scrape_config(company: str, report_type: str, output: str, 
                          formats: List[str], workers: int, use_proxies: bool, enable_logging: bool):
    """Display scraping configuration."""
    table = Table(title="🔧 Scraping Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Company", company.upper())
    table.add_row("Report Type", report_type.replace("_", " ").title())
    table.add_row("Output", output)
    table.add_row("Formats", ", ".join(formats))
    table.add_row("Workers", str(workers))
    table.add_row("Proxies", "Enabled" if use_proxies else "Disabled")
    table.add_row("Logging", "Enabled" if enable_logging else "Disabled")
    
    console.print(table)
    console.print()


def _display_bulk_config(start_id: int, end_id: int, report_type: str, output: str,
                        formats: List[str], workers: int, use_proxies: bool, enable_logging: bool):
    """Display bulk processing configuration."""
    company_count = end_id - start_id + 1
    
    table = Table(title="🔧 Bulk Processing Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("ID Range", f"{start_id} - {end_id}")
    table.add_row("Company Count", str(company_count))
    table.add_row("Report Type", report_type.replace("_", " ").title())
    table.add_row("Output", output)
    table.add_row("Formats", ", ".join(formats))
    table.add_row("Workers", str(workers))
    table.add_row("Proxies", "Enabled" if use_proxies else "Disabled")
    table.add_row("Logging", "Enabled" if enable_logging else "Disabled")
    
    console.print(table)
    console.print()


def _display_results(data: List, output: str, formats: List[str], 
                    is_bulk: bool = False, company_count: int = 0):
    """Display scraping results."""
    if len(data) == 0:
        console.print(Panel(
            "[bold red]⚠️ NO DATA FOUND[/bold red]\n\n"
            "This could mean:\n"
            "• The company ID/symbol doesn't exist\n"
            "• No reports of this type are available\n" 
            "• The company hasn't filed recent reports",
            title="Results",
            style="red"
        ))
    else:
        result_text = f"[bold green]✅ PROCESSING COMPLETED![/bold green]\n\n"
        result_text += f"📊 Records found: [bold]{len(data)}[/bold]\n"
        result_text += f"💾 Saved to: [bold]{output}.{'/'.join(formats)}[/bold]"
        
        if is_bulk:
            result_text += f"\n🏢 Companies processed: [bold]{company_count}[/bold]"
            
        console.print(Panel(result_text, title="Results", style="green"))


def _run_interactive_mode(ctx: CLIContext):
    """Run the interactive CLI mode."""
    # Setup logging
    from .utils.logging_config import setup_logging
    logger = setup_logging(ctx.enable_logging)
    cli_logger = logging.getLogger("PSEDataScraper.CLI")
    cli_logger.propagate = False
    
    if ctx.enable_logging:
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
            max_workers=ctx.max_workers,
            use_proxies=ctx.use_proxies,
            enable_logging=ctx.enable_logging,
        )

        # Display header
        console.print(Panel.fit(
            "📈 [bold blue]PSE DATA SCRAPER[/bold blue]\n"
            "Philippine Stock Exchange data scraping tool",
            style="blue"
        ))
        
        console.print("\n🔍 [bold]SEARCH OPTIONS:[/bold]")
        console.print("  • Company Symbol: SM, BDO, PLDT, etc.")
        console.print("  • Single Company ID: Any number (1, 2, 3, etc.)")
        console.print("  • 🚀 BULK PROCESSING: Range of IDs (e.g., 1-100)")
        
        console.print("\n📊 [bold]AVAILABLE REPORTS:[/bold]")
        reports = [
            "1. Public Ownership Report",
            "2. Quarterly Report", 
            "3. Annual Report",
            "4. List of Top 100 Stockholders",
            "5. Declaration of Cash Dividends"
        ]
        for report in reports:
            console.print(f"  {report}")

        # Main menu loop
        while True:
            console.print("\n" + "="*40)
            console.print("[bold cyan]MAIN MENU[/bold cyan]")
            console.print("="*40)
            
            menu_options = [
                "1. Public Ownership",
                "2. Quarterly Report", 
                "3. Annual Report",
                "4. List of Top 100 Stockholders",
                "5. Declaration of Cash Dividends",
                "6. Settings",
                "7. Exit"
            ]
            
            for option in menu_options:
                console.print(option)
            
            try:
                choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7"])
                
                if choice == "7":  # Exit
                    console.print("[green]👋 Goodbye![/green]")
                    break
                    
                elif choice == "6":  # Settings
                    _interactive_settings(ctx, scraper, cli_logger)
                    continue
                
                # Handle report selection
                report_type_map = {
                    "1": ReportType.PUBLIC_OWNERSHIP,
                    "2": ReportType.QUARTERLY,
                    "3": ReportType.ANNUAL, 
                    "4": ReportType.TOP_100_STOCKHOLDERS,
                    "5": ReportType.CASH_DIVIDENDS,
                }
                
                report_type = report_type_map[choice]
                
                # Reset data
                scraper.data = []
                scraper.stop_iteration = False
                
                filename = Prompt.ask("Enter output filename")
                
                console.print("\n[bold]Company Selection Options:[/bold]")
                console.print("1. Single company by symbol: Enter company symbol (e.g., 'SM', 'BDO')")
                console.print("2. Single company by ID: Enter one company ID (e.g., '5')")
                console.print("3. Bulk processing: Enter company ID range")
                
                start_company = Prompt.ask("Enter company symbol OR starting company ID").strip()
                
                if not start_company:
                    console.print("[red]Error: Company symbol/ID cannot be empty.[/red]")
                    continue
                
                # Process input
                if start_company.isdigit():
                    end_company = Prompt.ask("Enter ending company ID for bulk processing (or press Enter for single)", default="")
                    
                    if end_company and end_company.isdigit():
                        # Bulk processing
                        start_id = int(start_company)
                        end_id = int(end_company)
                        
                        if end_id < start_id:
                            console.print("[red]Error: Ending ID must be >= starting ID.[/red]")
                            continue
                        
                        company_count = end_id - start_id + 1
                        
                        # Confirmation for large ranges
                        if company_count > 10:
                            if not Confirm.ask(f"Process {company_count} companies? This may take a while."):
                                console.print("[yellow]Operation cancelled[/yellow]")
                                continue
                        
                        # Bulk processing with progress
                        with Progress(console=console) as progress:
                            task = progress.add_task("Processing companies...", total=company_count)
                            
                            for i, company_id in enumerate(range(start_id, end_id + 1), 1):
                                progress.update(task, description=f"Processing company ID {company_id}")
                                scraper.scrape_data(str(company_id), report_type)
                                progress.advance(task)
                    else:
                        # Single company by ID
                        console.print(f"Processing company ID: [bold]{start_company}[/bold]")
                        scraper.scrape_data(start_company, report_type)
                else:
                    # Company symbol
                    console.print(f"Processing company: [bold]{start_company.upper()}[/bold]")
                    scraper.scrape_data(start_company.upper(), report_type)

                # Save results
                scraper.save_results(filename, ctx.formats)
                
                # Display results
                _display_results(scraper.data, filename, ctx.formats)

            except KeyboardInterrupt:
                console.print("\n[yellow]Operation cancelled by user[/yellow]")
                continue
            except Exception as e:
                console.print(f"[red]An error occurred: {e}[/red]")

    except KeyboardInterrupt:
        console.print("\n[green]Program stopped[/green]")
    except Exception as e:
        console.print(f"[red]A fatal error occurred: {e}[/red]")


def _interactive_settings(ctx: CLIContext, scraper: PSEDataScraper, cli_logger):
    """Handle interactive settings menu."""
    while True:
        console.print("\n[bold cyan]SETTINGS[/bold cyan]")
        console.print("="*30)
        
        settings_table = Table()
        settings_table.add_column("Option", style="cyan")
        settings_table.add_column("Current Value", style="green")
        
        settings_table.add_row("1. Logging", "Enabled" if ctx.enable_logging else "Disabled")
        settings_table.add_row("2. Proxy", "Enabled" if ctx.use_proxies else "Disabled") 
        settings_table.add_row("3. Max Workers", str(ctx.max_workers))
        settings_table.add_row("4. Save Format", " and ".join(ctx.formats))
        settings_table.add_row("5. Back to Main Menu", "")
        
        console.print(settings_table)
        
        setting_choice = Prompt.ask("Select setting", choices=["1", "2", "3", "4", "5"])
        
        if setting_choice == "1":
            ctx.enable_logging = not ctx.enable_logging
            # Reinitialize scraper - simplified for interactive mode
            console.print(f"[green]✓ Logging {'enabled' if ctx.enable_logging else 'disabled'}[/green]")
            
        elif setting_choice == "2":
            ctx.use_proxies = not ctx.use_proxies
            scraper.use_proxies = ctx.use_proxies
            console.print(f"[green]✓ Proxy {'enabled' if ctx.use_proxies else 'disabled'}[/green]")
            
        elif setting_choice == "3":
            new_workers = click.prompt("Enter number of max workers (1-10)", 
                                     type=click.IntRange(1, 10), default=ctx.max_workers)
            ctx.max_workers = new_workers
            scraper.max_workers = new_workers
            console.print(f"[green]✓ Max workers changed to {new_workers}[/green]")
            
        elif setting_choice == "4":
            console.print("\nSelect save format:")
            console.print("1. CSV only (default)")
            console.print("2. JSON only") 
            console.print("3. Both CSV and JSON")
            
            format_choice = Prompt.ask("Choice", choices=["1", "2", "3"], default="1")
            
            if format_choice == "1":
                ctx.formats = ["csv"]
            elif format_choice == "2":
                ctx.formats = ["json"]
            elif format_choice == "3":
                ctx.formats = ["csv", "json"]
                
            console.print(f"[green]✓ Save format set to: {' and '.join(ctx.formats)}[/green]")
            
        elif setting_choice == "5":
            break


def main():
    """Main CLI entry point."""
    cli()


if __name__ == '__main__':
    main()
