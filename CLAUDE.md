# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🧠 Claude Code Workflow

## 🔑 Core Principles

- **NO HIGH-LEVEL BULLSHIT** – Show real code, not vague suggestions.
- **Terse, expert-level, casual communication** – Get to the point.
- **Anticipate needs** – Offer solutions they haven't asked for yet.

---

## 📋 Task Management

- Use `TodoWrite` / `TodoRead` *aggressively* for complex or multi-step tasks.
- Break tasks into concrete, actionable items.
- Mark todos as done immediately after completion.
- Use todos as your battle plan – always structure complex ops around them.

---

## 🔍 Search & Analysis

- Use `Task` tool for multi-round open-ended investigation.
- **Batch** search operations (esp. Bash) to minimize latency.
- Prefer `rg` (ripgrep) over `grep`, `fd` over `find`, etc.
- Read and diff multiple files at once where analysis demands it.

---

## 🧬 Code Changes

- Match existing code patterns – review similar files before adding new logic.
- Add comments only where the logic isn't self-evident.
- Don't touch unrelated files – surgical edits only.

---

## 🗃️ Git Workflow

- Commit at *logical checkpoints* with clear commit messages.
- Format commit messages:
  - `feat:`, `fix:`, `refactor:`, `chore:`, etc. + short summary
- Do **not** squash – user will squash and rename commits later.
- Never push unless explicitly instructed.
- Don't run deployment scripts unless told to.

---

## 📁 File Ops

- CREATE markdown files to document implemented logic.
- ALWAYS edit existing files if possible.
- NEVER delete MongoDB data without explicit confirmation.

---

## 🛠️ Tool Usage

- Batch all independent operations into single calls.
- Use absolute paths.
- Parallelize wherever possible:
  - e.g., `&` in Bash, `xargs -P`, background jobs.
- Use optimized tools (`rg`, `fd`, etc.) over slower legacy ones.

---

## 💬 Response Style

- Lead with the solution. Explain later, only if necessary.
- Show only relevant code (a few lines before/after).
- Reference files with this format:
  - `path/to/file.ts:42`
- Split large responses cleanly.
- No fluff. No filler.

---

## 🚫 What NOT to Do

- ❌ Don't update Git config
- ❌ Don't push to remote unless told to
- ❌ Don't deploy unless told to
- ❌ Don't touch unrelated DB entries

---

## Project Overview

PSE Data Scraper is a Python application that scrapes financial data from the Philippine Stock Exchange (PSE) Edge platform. It's built with a modular architecture and supports multiple report types including public ownership, annual/quarterly reports, stockholders lists, and cash dividends.

## Development Commands

### Setup and Installation

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Install development dependencies
make install-deps
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=pse_scraper

# Run specific test file
poetry run pytest tests/test_scraper.py
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/
# or
make format

# Run linting
poetry run flake8 src/
poetry run mypy src/
# or
make lint
```

### Building and Distribution

```bash
# Build executable for current platform
make build

# Clean build and rebuild
make build-clean

# Create release build
make release

# Test built executable
make test-executable
```

### Running the Application

```bash
# Interactive mode (default)
poetry run pse-scraper

# Direct CLI usage
poetry run pse-scraper SM public_ownership --output sm_data

# Share Buy-Back example
poetry run pse-scraper 180 share_buyback --output ali_buyback

# Using built executable
./releases/pse-scraper-* --help
```

## Architecture

### Core Components

1. **PSEDataScraper** (`src/pse_scraper/core/__init__.py`)
   - Main orchestration class that coordinates scraping workflow
   - Handles concurrent processing with ThreadPoolExecutor
   - Manages HTTP client and progress callbacks
   - Routes processing to specialized processors based on report type

2. **Report Processors** (`src/pse_scraper/core/processors/`)
   - Specialized classes for each report type (public ownership, annual, quarterly, stockholders, cash dividends)
   - Each processor handles specific parsing logic for its report format
   - Implements consistent interface with `process()` method

3. **HTTPClient** (`src/pse_scraper/utils/http_client.py`)
   - Handles HTTP requests with retry logic and proxy support
   - Manages session state and error handling

4. **CLI Interface** (`src/pse_scraper/cli.py`)
   - Click-based command line interface with Rich UI components
   - Supports both interactive menu mode and direct command execution
   - Provides progress tracking and configuration management

### Data Flow

1. User initiates scraping via CLI or programmatic API
2. PSEDataScraper sends search request to PSE Edge with company ID and report type
3. Parses search results to determine number of pages
4. Processes pages concurrently using ThreadPoolExecutor
5. For each document found, extracts edge_no and fetches detailed report
6. Routes document to appropriate processor based on report type
7. Processor extracts structured data from HTML
8. Results are aggregated and saved to CSV/JSON

### Report Types

The application supports 6 main report types defined in `ReportType` enum:

- `PUBLIC_OWNERSHIP` - Company ownership structure
- `ANNUAL` - Annual financial reports
- `QUARTERLY` - Quarterly financial reports  
- `TOP_100_STOCKHOLDERS` - Major shareholders lists
- `CASH_DIVIDENDS` - Dividend declarations
- `SHARE_BUYBACK` - Share buyback transactions (✅ Menu option 8)

### Adding New Report Types

1. Add new enum value to `ReportType` in `src/pse_scraper/models/report_types.py`
2. Create processor class in `src/pse_scraper/core/processors/`
3. Implement `process(soup, stock_name, disclosure_date)` method
4. Add processor import and routing in `PSEDataScraper._process_document()`
5. Update CLI mapping in `src/pse_scraper/cli.py` REPORT_TYPES dict

### Configuration

- **pyproject.toml** - Poetry configuration with dependencies and build settings
- **Makefile** - Build automation with common development tasks
- **pse-scraper.spec** - PyInstaller specification for executable builds

### Key Dependencies

- **requests** - HTTP client for web scraping
- **beautifulsoup4** - HTML parsing
- **click** - CLI framework
- **rich** - Enhanced terminal output and progress bars
- **pytest** - Testing framework

### Testing Strategy

- Unit tests for individual processors and utilities
- Integration tests for end-to-end scraping workflows
- Mock data for consistent testing without external dependencies
- Coverage reporting to ensure comprehensive test coverage

## Development Notes

### CLI Menu System

The interactive CLI uses a numbered menu system (1-8) with the following options:
1. Public Ownership
2. Quarterly Report  
3. Annual Report
4. List of Top 100 Stockholders
5. Declaration of Cash Dividends
6. Settings
7. Exit
8. Share Buy-Back Transactions ✅

When adding new report types, maintain this numbering for backward compatibility.

### Share Buy-Back Feature

**✅ Fully Implemented with UAT Validation**

The Share Buy-Back feature (menu option 8) extracts comprehensive buyback transaction data including:

**Transaction Details:**
- Individual transaction records with dates, shares, and prices
- Aggregated totals and weighted average prices
- Transaction count and total value

**Share Effects:**
- Before/after outstanding shares counts
- Before/after treasury shares counts  
- Net change calculations

**Program Summary:**
- Cumulative shares purchased to date
- Total program budget allocation
- Total amount spent on repurchases

**Amendment Detection:**
- `is_amended_report` field tracks amended documents
- Automatically detects [Amend-1], amended, amendment keywords
- Captures most recent versions of reports

**Real Data Example (ALI - Company ID 180):**
```csv
ALI,2025-07-07,True,10,1400000,27.25,38152915.0,14562064253,14560664253,1400000,2150755595,2152155595,1400000,876032246,26070000000.0,22885247993.0,Michael Blase Aquilizan,Department Manager
```

**Usage:**
```bash
# Command line
poetry run pse-scraper scrape 180 share_buyback --output results

# Interactive mode - select option 8
poetry run pse-scraper
```

### Processor Pattern

Each report processor follows a consistent pattern:

- Accept BeautifulSoup object, stock name, and disclosure date
- Extract relevant data using CSS selectors or parsing logic
- Return structured dictionary with standardized field names
- Handle edge cases and malformed HTML gracefully

### Concurrent Processing

The scraper uses ThreadPoolExecutor for parallel page processing. The `max_workers` parameter controls concurrency level. Progress callbacks are thread-safe and provide real-time status updates.

### Error Handling

The application implements comprehensive error handling:

- HTTP request failures are retried with exponential backoff
- Parsing errors are logged but don't stop processing
- Missing data fields are handled gracefully
- Progress callbacks receive error status updates
