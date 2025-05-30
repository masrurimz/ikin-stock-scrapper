# Makefile for PSE Scraper executable builds
# Supports building platform-specific executables

.PHONY: help build clean install-deps test lint format release release-push

# Default target
help:
	@echo "🚀 PSE Scraper Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  build          - Build executable for current platform"
	@echo "  build-clean    - Clean build directories and build"
	@echo "  clean          - Clean build artifacts"
	@echo "  install-deps   - Install build dependencies"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linting"
	@echo "  format         - Format code"
	@echo "  release        - Create a release build"
	@echo "  release-push   - Create and push a release"
	@echo "  docker-build   - Build using Docker (for cross-platform)"
	@echo ""
	@echo "Platform-specific builds:"
	@echo "  build-windows  - Build for Windows (requires Windows or Docker)"
	@echo "  build-macos    - Build for macOS (requires macOS or Docker)"
	@echo "  build-linux    - Build for Linux (requires Linux or Docker)"

# Install dependencies
install-deps:
	@echo "📦 Installing dependencies..."
	poetry install
	poetry run pip install pyinstaller

# Build for current platform
build:
	@echo "🔨 Building executable for current platform..."
	poetry run python build_executable.py

# Clean and build
build-clean:
	@echo "🧹 Cleaning and building..."
	poetry run python build_executable.py --clean

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build dist releases __pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Run tests
test:
	@echo "🧪 Running tests..."
	poetry run pytest

# Run linting
lint:
	@echo "🔍 Running linting..."
	poetry run flake8 src/
	poetry run mypy src/

# Format code
format:
	@echo "✨ Formatting code..."
	poetry run black src/ tests/

# Create release build
release: clean
	@echo "📦 Creating release build..."
	poetry run python build_executable.py --clean

# Create and push release
release-push:
	@echo "🚀 Creating and pushing release..."
	@read -p "Enter version (e.g., 2.1.0): " version; \
	poetry run python release.py $$version --push

# Docker-based cross-platform builds
docker-build-windows:
	@echo "🐳 Building Windows executable using Docker..."
	docker run --rm -v $(PWD):/workspace python:3.10-windowsservercore \
		powershell -c "cd /workspace; pip install poetry; poetry install; poetry run python build_executable.py"

docker-build-linux:
	@echo "🐳 Building Linux executable using Docker..."
	docker run --rm -v $(PWD):/workspace python:3.10-slim \
		bash -c "cd /workspace && pip install poetry && poetry install && python build_executable.py"

# Development helpers
dev-setup:
	@echo "🛠️ Setting up development environment..."
	poetry install
	poetry run pre-commit install

# Check if executable works
test-executable:
	@echo "🧪 Testing built executable..."
	@if [ -f releases/pse-scraper-* ]; then \
		echo "Testing executable..."; \
		./releases/pse-scraper-* --version; \
	else \
		echo "❌ No executable found. Run 'make build' first."; \
	fi

# Show build info
info:
	@echo "📊 Build Information:"
	@echo "Platform: $$(python -c 'import platform; print(platform.system(), platform.machine())')"
	@echo "Python: $$(python --version)"
	@echo "Poetry: $$(poetry --version)"
	@if command -v pyinstaller >/dev/null 2>&1; then \
		echo "PyInstaller: $$(pyinstaller --version)"; \
	else \
		echo "PyInstaller: Not installed"; \
	fi
