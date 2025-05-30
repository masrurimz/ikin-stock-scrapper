# PSE Stock Scraper

A Python web scraping project for Philippine Stock Exchange (PSE) data using Poetry for dependency management.

## Features

1. Public Ownership Report
2. Quarterly Report  
3. Annual Report
4. List of Top 100 Stockholders
5. Declaration of Cash Dividends

## Installation

1. Install dependencies:

```bash
poetry install
```

2. Activate the virtual environment:

```bash
poetry shell
```

## Usage

Run the scraper using:

```bash
poetry run python batchFile.py
```

Or use the Poetry script:

```bash
poetry run pse-scraper
```

## Dependencies

- requests: HTTP library for API calls
- beautifulsoup4: HTML parsing library  
- html5lib: HTML5 parser for BeautifulSoup
- lxml: XML and HTML parser (optional, will fallback to html5lib if not available)

## Development

Development dependencies include:

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
