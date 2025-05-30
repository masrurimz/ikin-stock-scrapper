"""
Logging configuration for PSE scraper.
"""

import os
import logging
import logging.handlers


def setup_logging(enable_logging: bool = True, log_dir: str = "logs") -> logging.Logger:
    """
    Configure logging system.
    
    Args:
        enable_logging: Whether to enable logging
        log_dir: Directory to store log files
        
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

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    error_fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(error_fh)
    logger.addHandler(ch)

    return logger
