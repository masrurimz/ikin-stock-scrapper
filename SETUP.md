# PSE Data Scraper Configuration

This file contains configuration instructions for the PSE Data Scraper project.

## Environment Setup

### 1. Install Poetry (if not already installed)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Install Project Dependencies

```bash
# Navigate to project directory
cd /path/to/pse-scraper

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 3. Verify Installation

```bash
# Test CLI
poetry run python cli.py --help

# Test basic functionality
poetry run python cli.py SM public_ownership --output test --no-logging

# Run examples
poetry run python examples/basic_usage.py

# Run tests (when available)
poetry run pytest
```

## Configuration Files

### Proxy Configuration (Optional)

Create a `proxies.txt` file in the project root if you want to use proxy rotation:

```
# One proxy per line in format: ip:port
192.168.1.1:8080
10.0.0.1:3128
# Add more proxies as needed
```

### Logging Configuration

Logs are automatically created in the `logs/` directory:
- `logs/pse_scraper.log` - General application logs
- `logs/pse_scraper_error.log` - Error logs only

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Poetry
- Black Formatter
- Pylance

### PyCharm

1. Set interpreter to Poetry virtual environment
2. Mark `src/` as Sources Root
3. Enable Black formatter in settings

## Development Workflow

1. **Make changes** to code
2. **Format code**: `poetry run black .`
3. **Check linting**: `poetry run flake8`
4. **Type checking**: `poetry run mypy src/`
5. **Run tests**: `poetry run pytest`
6. **Test examples**: `poetry run python examples/basic_usage.py`

## Package Building

```bash
# Build package
poetry build

# Publish to PyPI (when ready)
poetry publish
```
