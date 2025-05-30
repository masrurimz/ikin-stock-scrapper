# PSE Data Scraper

A modern, modular Python web scraping ## 🛠 Installation

### Option 1: Pre-built Executables (Recommended for End Users)

Download platform-specific executables that don't require Python installation:

1. **Go to the [Releases](../../releases) page**

2. **Download the executable for your platform:**
   - `pse-scraper-macos-arm64` (macOS Apple Silicon)
   - `pse-scraper-macos-x64` (macOS Intel)
   - `pse-scraper-linux-x64` (Linux 64-bit)
   - `pse-scraper-windows-x64.exe` (Windows 64-bit)

3. **Make it executable (Unix/Linux/macOS):**

```bash
chmod +x pse-scraper-*
```

4. **Run directly:**

```bash
./pse-scraper-* --help
# or on Windows
pse-scraper-windows-x64.exe --help
```

### Option 2: Development Installation

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
```ppine Stock Exchange (PSE) data. This project has been completely restructured to follow Python best practices with a clean, maintainable architecture.

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

### Option 1: Pre-built Executables (Recommended for End Users)

Download platform-specific executables that don't require Python installation:

1. **Go to the [Releases](../../releases) page**
2. **Download the executable for your platform:**
   - `pse-scraper-macos-arm64` (macOS Apple Silicon)
   - `pse-scraper-macos-x64` (macOS Intel)
   - `pse-scraper-linux-x64` (Linux 64-bit)
   - `pse-scraper-windows-x64.exe` (Windows 64-bit)
3. **Make it executable (Unix/Linux/macOS):**
```bash
chmod +x pse-scraper-*
```
4. **Run directly:**
```bash
./pse-scraper-* --help
# or on Windows
pse-scraper-windows-x64.exe --help
```

### Option 2: Development Installation

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

### Option 3: Building Executables

To build platform-specific executables yourself:

```bash
# Build for current platform
make build

# Or use the Python script directly
poetry run python build_executable.py

# Clean build and rebuild
make build-clean
```

See [BUILD_EXECUTABLES.md](BUILD_EXECUTABLES.md) for detailed build instructions and cross-platform building.

## 📖 Usage

PSE Data Scraper offers two modes of operation and can be used as a standalone executable or Python package:

### 🚀 Quick Start with Executable

If you downloaded a pre-built executable:

```bash
# Start interactive mode
./pse-scraper-* 

# Quick scrape example
./pse-scraper-* scrape SM public_ownership --output sm_ownership

# Get help
./pse-scraper-* --help
```

### 🖥️ Interactive Menu Mode (Default)

When run without arguments, the scraper starts an interactive menu matching the original interface:

```bash
# Start interactive mode
pse-scraper
# or explicitly
pse-scraper --interactive
```

The interactive menu provides:
- **Main Menu**: Choose from 5 report types
- **Settings**: Configure logging, proxy, workers, and output formats
- **Iteration Support**: Single or batch processing with iteration ranges
- **Real-time Configuration**: Adjust settings without restarting

**Interactive Menu Features:**
1. **Public Ownership Report** - Company ownership structure
2. **Quarterly Report** - Financial statements 
3. **Annual Report** - Annual financial data
4. **List of Top 100 Stockholders** - Major shareholders
5. **Declaration of Cash Dividends** - Dividend announcements
6. **Settings** - Configure scraper behavior
7. **Exit** - Close the application

### ⚡ Command Line Mode

For automation and scripting, use direct command line arguments:

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
