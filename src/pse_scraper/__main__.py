#!/usr/bin/env python3
"""
Main entry point for the PSE Scraper CLI when run as a module or executable.
This handles the import paths correctly for both development and packaged versions.
"""

import sys
import os
import platform
from pathlib import Path

# Setup UTF-8 encoding for Windows as early as possible
def _setup_utf8_encoding():
    """Setup UTF-8 encoding for cross-platform support."""
    if platform.system() == "Windows":
        try:
            # Set environment variables
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            os.environ['PYTHONUTF8'] = '1'
            
            # Try to set console code page to UTF-8
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # UTF-8 code page
            kernel32.SetConsoleCP(65001)        # UTF-8 input code page
            
            # Reconfigure stdout/stderr if possible
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
                
        except Exception:
            # Fallback: just ensure environment variables are set
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            os.environ['PYTHONUTF8'] = '1'

# Setup UTF-8 before any other imports
_setup_utf8_encoding()

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
        print(f"Python path: {sys.path}")
        print(f"Frozen: {getattr(sys, 'frozen', False)}")
        print(f"Application path: {application_path}")
        if hasattr(sys, '_MEIPASS'):
            print(f"MEI temp path: {sys._MEIPASS}")
        print("Please ensure the PSE Scraper package is properly installed.")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
