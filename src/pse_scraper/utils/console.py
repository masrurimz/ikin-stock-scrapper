"""Console utilities for cross-platform support."""

import sys
import platform
from typing import Any
from rich.console import Console as RichConsole


def _setup_windows_console():
    """Setup Windows console for UTF-8 support."""
    if platform.system() == "Windows":
        try:
            # Try to enable UTF-8 mode
            import os
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            
            # For Windows 10 version 1903 and later
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # UTF-8 code page
            
            # Reconfigure stdout/stderr for UTF-8
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
                
        except Exception:
            # Fallback: just set environment variables
            import os
            os.environ['PYTHONIOENCODING'] = 'utf-8'


class SafeConsole(RichConsole):
    """
    Rich Console wrapper for consistent cross-platform output.
    Handles UTF-8 encoding and emoji support across platforms.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize console with UTF-8 support."""
        # Setup Windows console for UTF-8
        _setup_windows_console()
        
        # Configure Rich console for UTF-8 and emoji support
        kwargs.setdefault('force_terminal', True)
        kwargs.setdefault('width', None)  # Auto-detect width
        
        # On Windows, ensure we handle encoding properly
        if platform.system() == "Windows":
            kwargs.setdefault('legacy_windows', False)
            
        super().__init__(*args, **kwargs)
    
    def print(self, *objects: Any, **kwargs) -> None:
        """Print with proper encoding handling."""
        try:
            super().print(*objects, **kwargs)
        except UnicodeEncodeError:
            # Fallback: convert problematic characters
            safe_objects = []
            for obj in objects:
                if isinstance(obj, str):
                    # Replace problematic Unicode characters
                    safe_str = obj.encode('ascii', 'replace').decode('ascii')
                    safe_objects.append(safe_str)
                else:
                    safe_objects.append(obj)
            super().print(*safe_objects, **kwargs)


# Create a global console instance
console = SafeConsole()
