"""
PSE Data Scraper

A modern, modular Python web scraping library for Philippine Stock Exchange (PSE) data.
"""

__version__ = "2.0.0"
__author__ = "Muhammad Zahid Masruri"
__email__ = "masruri03@gmail.com"

from .core import PSEDataScraper
from .models.report_types import ReportType

__all__ = ["PSEDataScraper", "ReportType"]
