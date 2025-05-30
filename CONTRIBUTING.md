# Contributing to PSE Data Scraper

Thank you for your interest in contributing to PSE Data Scraper! We welcome contributions from everyone.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/your-username/pse-scraper.git
   cd pse-scraper
   ```

3. Install dependencies:

   ```bash
   poetry install
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management

### Environment Setup

```bash
# Install development dependencies
poetry install

# Activate virtual environment
poetry shell

# Run tests to ensure everything works
pytest
```

## Making Changes

### Before You Start

1. Create a new branch for your feature/fix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make sure tests pass:

   ```bash
   poetry run pytest
   ```

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run these tools before submitting:

```bash
# Format code
poetry run black .

# Check linting
poetry run flake8

# Type checking
poetry run mypy src/
```

### Testing

- Write tests for new functionality
- Ensure all tests pass:

  ```bash
  poetry run pytest
  ```

- Check test coverage:

  ```bash
  poetry run pytest --cov=pse_scraper
  ```

### Documentation

- Update README.md if you add new features
- Add docstrings to new functions and classes
- Update examples if necessary

## Submitting Changes

1. **Commit your changes:**

   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

2. **Push to your fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request:**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template

## Pull Request Guidelines

### PR Requirements

- [ ] All tests pass
- [ ] Code is formatted with Black
- [ ] No linting errors
- [ ] Type hints are added where appropriate
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive

### PR Description

Please include:

- **What** - Brief description of changes
- **Why** - Reason for the changes
- **How** - How the changes work
- **Testing** - How you tested the changes

## Types of Contributions

### Bug Fixes

- Report bugs via GitHub Issues
- Include reproduction steps
- Provide error messages and logs
- Test your fix thoroughly

### New Features

- Discuss major features in Issues first
- Keep features focused and atomic
- Add comprehensive tests
- Update documentation

### Report Types

If adding support for new PSE report types:

1. Create a new processor in `src/pse_scraper/core/processors/`
2. Add the report type to `ReportType` enum
3. Add tests in `tests/test_processors.py`
4. Update CLI help text
5. Add examples

### Documentation

- Fix typos and improve clarity
- Add usage examples
- Update API documentation
- Improve setup instructions

## Code Organization

```
src/pse_scraper/
├── core/                 # Core scraping logic
│   ├── __init__.py      # Main PSEDataScraper class
│   └── processors/       # Report-specific processors
├── models/              # Data models and enums
├── utils/               # Utility functions
└── cli.py               # Command-line interface
```

### Adding New Processors

1. Create `new_report.py` in `processors/`
2. Inherit from base functionality
3. Implement required methods
4. Add comprehensive tests
5. Update documentation

## Getting Help

- **Questions?** Open a GitHub Issue
- **Chat?** Use GitHub Discussions
- **Email?** Contact the maintainers

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the golden rule

## Recognition

Contributors will be:

- Listed in the repository contributors
- Mentioned in release notes for significant contributions
- Given credit in documentation where appropriate

Thank you for contributing to PSE Data Scraper! 🎉
