# PSE Data Scraper

A modern, modular Python web scraping project for Philippine Stock Exchange (PSE) data. This project has been completely restructured to follow Python best practices with a clean, maintainable architecture.

## 🚀 Features

- **Public Ownership Reports** - Scrape company ownership data
- **Annual Reports** - Extract annual financial reports  
- **Quarterly Reports** - Get quarterly financial data
- **Top 100 Stockholders** - List major shareholders
- **Cash Dividends** - Declaration and payment information
- **Concurrent Processing** - Multi-threaded scraping for better performance
- **Multiple Output Formats** - Save data as JSON or CSV
- **Robust Error Handling** - Comprehensive logging and error management
- **Modular Architecture** - Clean separation of concerns
- **Extensible Design** - Easy to add new report types

## 📁 Project Structure

```
pse-scraper/
├── src/pse_scraper/          # Main package
│   ├── core/                 # Core scraping logic
│   │   ├── __init__.py      # Main PSEDataScraper class
│   │   └── processors/       # Report-specific processors
│   ├── models/              # Data models
│   │   └── report_types.py  # Report type enums
│   └── utils/               # Utility functions
├── examples/                # Usage examples
├── tests/                   # Test suite
├── docs/                    # Documentation
├── cli.py                   # Command-line interface
└── pyproject.toml          # Poetry configuration
```

## 🛠 Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd ikin-stock-scrapper
```

2. **Install dependencies using Poetry:**
```bash
poetry install
```

3. **Activate the virtual environment:**
```bash
poetry shell
```

## 📖 Usage

### Command Line Interface

The new CLI provides a clean interface for scraping data:

```bash
# Basic usage
pse-scraper SM public_ownership --output sm_ownership

# Multiple formats
pse-scraper BDO annual_report --output bdo_annual --formats json csv

# Custom configuration
pse-scraper PLDT quarterly_report --workers 3 --use-proxies

# Cash dividends
pse-scraper JFC cash_dividends --output jfc_dividends --formats json

# Stockholders report
pse-scraper ALI stockholders --output ali_stockholders
```

**Using with Poetry:**
```bash
poetry run pse-scraper SM public_ownership --output sm_ownership
```

### Programmatic Usage

```python
from pse_scraper.core import PSEDataScraper
from pse_scraper.models.report_types import ReportType

# Initialize scraper
scraper = PSEDataScraper(
    max_workers=5,
    use_proxies=False,
    enable_logging=True
)

# Scrape data
scraper.scrape_data("SM", ReportType.PUBLIC_OWNERSHIP)

# Save results
scraper.save_results("sm_ownership", ["json", "csv"])
```

### Available Report Types

- `public_ownership` - Public Ownership Reports
- `annual_report` - Annual Financial Reports
- `quarterly_report` - Quarterly Financial Reports  
- `cash_dividends` - Cash Dividend Declarations
- `stockholders` - Top 100 Stockholders

## 📚 Examples

Check the `examples/` directory for detailed usage examples:

- `basic_usage.py` - Simple scraping examples
- `advanced_usage.py` - Advanced configuration options
- `batch_scraping.py` - Scraping multiple companies

Run examples:
```bash
poetry run python examples/basic_usage.py
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pse_scraper

# Run specific test file
poetry run pytest tests/test_scraper.py
```

## 🔧 Dependencies

### Core Dependencies
- **requests** (^2.31.0) - HTTP library for web requests
- **beautifulsoup4** (^4.12.0) - HTML parsing library  
- **html5lib** (^1.1) - HTML5 parser for BeautifulSoup

### Development Dependencies
- **pytest** (^7.4.0) - Testing framework
- **black** (^23.0.0) - Code formatter
- **flake8** (^6.0.0) - Code linter
- **mypy** (^1.5.0) - Type checker

## 🏗 Architecture

### Core Components

1. **PSEDataScraper** - Main scraper class handling the scraping workflow
2. **Processors** - Specialized classes for different report types
3. **HTTPClient** - Robust HTTP client with retry logic and proxy support
4. **Utilities** - Helper functions for text processing and data conversion

### Key Features

- **Modular Design** - Each report type has its own processor
- **Concurrent Processing** - Configurable thread pool for parallel requests
- **Error Handling** - Comprehensive logging and graceful error recovery
- **Data Validation** - Type conversion and data cleaning utilities
- **Flexible Output** - Support for multiple output formats

## 🚀 Getting Started

1. **Quick Test:**
```bash
poetry run pse-scraper SM public_ownership --output test_output
```

2. **Explore Examples:**
```bash
poetry run python examples/basic_usage.py
```

3. **Run Tests:**
```bash
poetry run pytest
```

## 📝 Migration from v1.x

The project has been completely restructured. Key changes:

- **New CLI interface** - Replace `batchFile.py` usage with `cli.py`
- **Modular architecture** - Code split into logical modules
- **Improved error handling** - Better logging and recovery
- **Enhanced performance** - Optimized concurrent processing
- **Better testing** - Comprehensive test suite

### Old vs New Usage

**Old:**
```bash
python batchFile.py
```

**New:**
```bash
pse-scraper <COMPANY> <REPORT_TYPE> --output <FILENAME>
# or with Poetry
poetry run pse-scraper <COMPANY> <REPORT_TYPE> --output <FILENAME>
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the `examples/` directory for usage patterns
2. Review the test files for expected behavior
3. Open an issue on the repository

- pytest: Testing framework
- black: Code formatter
- flake8: Linting
- mypy: Type checking

Run tests:

```bash
poetry run pytest
```

Format code:

```bash
poetry run black .
```

Lint code:

```bash
poetry run flake8
```
