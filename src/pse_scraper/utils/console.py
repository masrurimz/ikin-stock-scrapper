"""Console utilities for cross-platform support."""

from typing import Any
from rich.console import Console as RichConsole


class SafeConsole(RichConsole):
    """
    Rich Console wrapper for consistent cross-platform output.
    Relies on proper UTF-8 encoding configuration for emoji support.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize console with UTF-8 support."""
        # Set force_terminal to True for consistent output in executables
        kwargs.setdefault('force_terminal', True)
        super().__init__(*args, **kwargs)


# Create a global console instance
console = SafeConsole()
