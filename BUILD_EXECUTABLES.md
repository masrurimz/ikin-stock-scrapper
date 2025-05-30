# Building Executable Files

This document explains how to create platform-specific executable files for the PSE Scraper CLI, so users don't need to install Python to use the tool.

## Quick Start

### Prerequisites
- Python 3.10+
- Poetry (for dependency management)
- Git (for version control)

### Build for Current Platform

```bash
# Install build dependencies
make install-deps

# Build executable for your current platform
make build

# Clean build and rebuild
make build-clean
```

The executable will be created in the `releases/` directory with a platform-specific name like:
- `pse-scraper-macos-arm64` (macOS Apple Silicon)
- `pse-scraper-macos-x64` (macOS Intel)
- `pse-scraper-linux-x64` (Linux 64-bit)
- `pse-scraper-windows-x64.exe` (Windows 64-bit)

### Test the Executable

```bash
# Test that the executable works
make test-executable

# Or manually test
./releases/pse-scraper-* --version
```

## Detailed Build Process

### Manual Build Process

```bash
# 1. Install PyInstaller
poetry run pip install pyinstaller

# 2. Build using the Python script
poetry run python build_executable.py

# 3. Or build with cleaning
poetry run python build_executable.py --clean
```

### Build Options

The `build_executable.py` script supports several options:

```bash
poetry run python build_executable.py --help
```

Options:
- `--clean`: Clean build directories before building
- `--skip-deps`: Skip dependency installation

### Platform-Specific Builds

#### Current Platform
```bash
make build
```

#### Cross-Platform with Docker
```bash
# Build for Linux (from any platform)
make docker-build-linux

# Build for Windows (requires Docker Desktop on Windows)
make docker-build-windows
```

## Automated Builds with GitHub Actions

The project includes GitHub Actions workflows for automated cross-platform builds.

### Triggering Builds

1. **Release Builds**: Push a version tag
   ```bash
   git tag v2.0.1
   git push origin v2.0.1
   ```

2. **Manual Builds**: Use GitHub's "Actions" tab to trigger a manual build

### Supported Platforms

The automated build creates executables for:
- **Linux x64** (Ubuntu-based)
- **Windows x64** (Windows Server-based)
- **macOS x64** (Intel-based Mac)
- **macOS ARM64** (Apple Silicon Mac)

### Download Built Executables

1. Go to the "Actions" tab in your GitHub repository
2. Click on a completed workflow run
3. Download the artifacts from the "Artifacts" section
4. For tagged releases, executables are also attached to the GitHub release

## File Structure

```
pse-scraper/
├── build_executable.py       # Main build script
├── pse-scraper.spec          # PyInstaller configuration
├── Makefile                  # Build automation
├── .github/
│   └── workflows/
│       └── build-executables.yml  # CI/CD for cross-platform builds
├── releases/                 # Generated executables (git-ignored)
├── build/                    # Temporary build files (git-ignored)
└── dist/                     # PyInstaller output (git-ignored)
```

## Customization

### Modifying the Build

Edit `pse-scraper.spec` to customize the PyInstaller build:

- **Add data files**: Add to the `datas` list
- **Add hidden imports**: Add to the `hiddenimports` list
- **Exclude modules**: Add to the `excludes` list
- **Add an icon**: Set the `icon` parameter

### Build Script Customization

Modify `build_executable.py` to:
- Change output directory
- Add custom post-build steps
- Modify platform detection
- Add additional checks

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Add missing modules to `hiddenimports` in the spec file
   - Check that all dependencies are installed

2. **Large File Size**
   - Add unnecessary modules to `excludes` in the spec file
   - Enable UPX compression (if available)

3. **Missing Data Files**
   - Add data files to the `datas` list in the spec file

4. **Cross-Platform Issues**
   - Use the GitHub Actions workflow for consistent builds
   - Test on the target platform

### Debugging

1. **Enable Debug Mode**
   ```python
   # In pse-scraper.spec, change:
   debug=True
   ```

2. **Check Dependencies**
   ```bash
   poetry run python -c "import pse_scraper; print('Import successful')"
   ```

3. **Test PyInstaller Directly**
   ```bash
   poetry run pyinstaller --onefile src/pse_scraper/cli.py
   ```

## Size Optimization

The built executables are optimized for size:

1. **UPX Compression**: Enabled by default (if UPX is available)
2. **Module Exclusion**: Common heavy modules are excluded
3. **Single File**: Everything is bundled into one executable

Typical sizes:
- **Linux**: ~15-20 MB
- **Windows**: ~18-25 MB  
- **macOS**: ~18-25 MB

## Distribution

### GitHub Releases

The automated workflow creates GitHub releases with:
- Platform-specific executables
- SHA256 checksums
- Release notes

### Manual Distribution

1. Build the executable
2. Test on the target platform
3. Create a ZIP/archive if needed
4. Upload to your distribution platform

### Installation Instructions for Users

Provide users with simple instructions:

```bash
# Download the executable for your platform
# Make it executable (Unix/Linux/macOS)
chmod +x pse-scraper-*

# Run the tool
./pse-scraper-* --help

# On Windows, just double-click or run from command prompt
pse-scraper-windows-x64.exe --help
```

## Security Considerations

1. **Code Signing**: Consider signing executables for Windows/macOS
2. **Checksums**: Always provide SHA256 checksums
3. **Virus Scanning**: Test with antivirus software
4. **Supply Chain**: Use trusted build environments (GitHub Actions)

## Performance

The executable starts slightly slower than the Python script due to unpacking, but runtime performance is identical since it's the same Python code.

Startup time comparison:
- **Python script**: ~0.1-0.2 seconds
- **Executable**: ~0.3-0.5 seconds

Runtime performance is identical for actual scraping operations.
