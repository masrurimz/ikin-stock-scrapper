#!/usr/bin/env python3
"""
Main entry point for the PSE Scraper CLI when run as a module or executable.
This handles the import paths correctly for both development and packaged versions.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path for proper imports
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller executable
    application_path = Path(sys.executable).parent
else:
    # Running as a normal Python script
    application_path = Path(__file__).parent.parent.parent

# Ensure the package can be imported
src_path = application_path / 'src'
if src_path.exists():
    sys.path.insert(0, str(src_path))

def main():
    """Main entry point for the CLI."""
    try:
        # Import and run the CLI
        from pse_scraper.cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure the PSE Scraper package is properly installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
