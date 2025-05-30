# PSE Scraper Tests

This directory contains test files for the PSE scraper.

## Running Tests

Make sure you have Poetry installed and dependencies are set up:

```bash
poetry install
```

Run all tests:

```bash
poetry run pytest
```

Run specific test file:

```bash
poetry run pytest tests/test_scraper.py
```

Run tests with coverage:

```bash
poetry run pytest --cov=pse_scraper
```

## Test Structure

- `test_scraper.py` - Core scraper functionality tests
- `test_processors.py` - Report processor tests
- `test_utils.py` - Utility function tests
- `test_models.py` - Model tests
