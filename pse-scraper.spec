# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PSE Scraper CLI
This creates a single executable file for the PSE Scraper
"""

import sys
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH)
src_path = project_root / "src"

# Analysis configuration
a = Analysis(
    ['src/pse_scraper/__main__.py'],  # Use a proper entry point
    pathex=[str(src_path)],  # Additional paths
    binaries=[],
    datas=[
        # Include any data files your application needs
        # ('src/pse_scraper/data', 'pse_scraper/data'),  # Uncomment if you have data files
    ],
    hiddenimports=[
        # Ensure all required modules are included
        'pse_scraper',
        'pse_scraper.core',
        'pse_scraper.core.processors',
        'pse_scraper.core.processors.public_ownership',
        'pse_scraper.core.processors.quarterly_report',
        'pse_scraper.core.processors.annual_report',
        'pse_scraper.core.processors.stockholders',
        'pse_scraper.core.processors.cash_dividends',
        'pse_scraper.core.processors.share_buyback',
        'pse_scraper.models',
        'pse_scraper.models.report_types',
        'pse_scraper.utils',
        'pse_scraper.utils.console',
        'pse_scraper.utils.http_client',
        'pse_scraper.utils.logging_config',
        'click',
        'rich',
        'rich.console',
        'rich.progress',
        'rich.table',
        'rich.panel',
        'rich.prompt',
        'rich.text',
        'rich.console',
        'rich.progress',
        'rich.table',
        'rich.panel',
        'rich.prompt',
        'rich.text',
        'requests',
        'bs4',
        'bs4.builder',
        'bs4.builder._html5lib',
        'bs4.builder._htmlparser',
        'bs4.builder._lxml',
        'bs4.element',
        'bs4.dammit',
        'beautifulsoup4',
        'html5lib',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'soupsieve',
        'webencodings',
        'six',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create single executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pse-scraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: 'assets/icon.ico'
)
