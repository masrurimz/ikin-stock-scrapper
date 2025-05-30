"""
Logging configuration for PSE scraper with Rich CLI integration.
"""

import os
import logging
import logging.handlers
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(enable_logging: bool = True, log_dir: str = "logs", 
                 cli_mode: bool = False, console: Optional[Console] = None) -> logging.Logger:
    """
    Configure logging system with Rich CLI integration.
    
    Args:
        enable_logging: Whether to enable logging
        log_dir: Directory to store log files
        cli_mode: Whether we're in CLI mode (affects console output)
        console: Rich console instance for CLI mode
        
    Returns:
        Configured logger instance
    """
    if not enable_logging:
        logger = logging.getLogger("null")
        logger.setLevel(logging.CRITICAL)
        logger.addHandler(logging.NullHandler())
        logger.propagate = False
        return logger
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("PSEDataScraper")
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # File handler for all logs
    fh = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "pse_scraper.log"), 
        maxBytes=5 * 1024 * 1024, 
        backupCount=5
    )
    fh.setLevel(logging.INFO)

    # File handler for errors only
    error_fh = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "pse_scraper_error.log"), 
        maxBytes=5 * 1024 * 1024, 
        backupCount=5
    )
    error_fh.setLevel(logging.ERROR)

    # Format for file handlers
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(file_formatter)
    error_fh.setFormatter(file_formatter)

    logger.addHandler(fh)
    logger.addHandler(error_fh)

    # Console handler - different behavior for CLI vs non-CLI mode
    if cli_mode and console:
        # Use Rich handler for beautiful CLI logging
        console_handler = RichHandler(
            console=console,
            show_time=False,
            show_path=False,
            show_level=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=False
        )
        console_handler.setLevel(logging.WARNING)  # Only show warnings/errors in CLI
        logger.addHandler(console_handler)
    elif not cli_mode:
        # Standard console handler for non-CLI usage
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)

    return logger


def setup_cli_logging(console: Console, enable_logging: bool = True) -> logging.Logger:
    """
    Setup logging specifically optimized for CLI usage with Rich.
    
    Args:
        console: Rich console instance
        enable_logging: Whether to enable logging
        
    Returns:
        Configured logger for CLI
    """
    return setup_logging(enable_logging=enable_logging, cli_mode=True, console=console)


def get_quiet_logger(name: str = "PSEDataScraper.Quiet") -> logging.Logger:
    """
    Get a logger that only logs to files, not console.
    Useful for CLI operations where we want clean output.
    
    Args:
        name: Logger name
        
    Returns:
        Quiet logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Only add file handlers
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # File handler for all logs
    fh = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "pse_scraper.log"), 
        maxBytes=5 * 1024 * 1024, 
        backupCount=5
    )
    fh.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    # Prevent propagation to parent loggers
    logger.propagate = False
    
    return logger
