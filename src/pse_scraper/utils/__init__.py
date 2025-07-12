"""
Utility functions for PSE data scraping.
"""

import re
import datetime
import logging
from typing import Optional, Tuple


def clean_text(text: str) -> str:
    """
    Membersihkan teks dari karakter khusus.

    Args:
        text: Teks yang akan dibersihkan

    Returns:
        Teks yang sudah dibersihkan
    """
    return text.strip().replace(",", "").replace("%", "")


def parse_date(date_str: str) -> Optional[str]:
    """
    Mengubah format tanggal dari string ke format yang diinginkan.

    Args:
        date_str: String tanggal dari website

    Returns:
        String tanggal dalam format YYYY-MM-DD
    """
    try:
        return datetime.datetime.strptime(date_str, "%b %d, %Y %I:%M %p").strftime(
            "%Y-%m-%d"
        )
    except ValueError:
        logging.getLogger(__name__).error(f"Error parsing date: {date_str}")
        return None


def extract_edge_no(onclick: str) -> Optional[str]:
    """
    Mengambil edge no dari atribut onclick.

    Args:
        onclick: Atribut onclick dari tag HTML

    Returns:
        Edge no
    """
    match = re.search(r"openPopup\('(.+?)'\)", onclick)
    return match.group(1) if match else None


def convert_to_numeric(value):
    """
    Convert string values to numeric types where appropriate.
    
    Args:
        value: The string value to convert
        
    Returns:
        Numeric value if conversion is possible, otherwise the original string
    """
    if not value or not isinstance(value, str):
        return value
    
    # Remove commas from numbers
    value = value.replace(',', '')
    
    # Try to convert to numeric type
    try:
        # Check if it's a float
        if '.' in value:
            return float(value)
        # Check if it's an integer
        else:
            return int(value)
    except (ValueError, TypeError):
        # If conversion fails, return the original value
        return value


def clean_stockholders_text(text):
    """Clean text by removing extra whitespace and HTML entities"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    return text


def parse_date_registered(date_str: str) -> Optional[Tuple[str, int, int, int]]:
    """
    Parse Date Registered into components for UAT #3 format.
    
    Args:
        date_str: Date string from "Date Registered" field
        
    Returns:
        Tuple of (full_date, month, year, day) or None if parsing fails
    """
    if not date_str:
        return None
        
    # Clean the date string
    date_str = date_str.strip()
    
    # Try different date formats commonly used in PSE documents
    formats = [
        "%m/%d/%Y",      # 5/27/2025
        "%m/%d/%y",      # 5/27/25  
        "%d/%m/%Y",      # 27/5/2025
        "%Y-%m-%d",      # 2025-05-27
        "%b %d, %Y",     # May 27, 2025
        "%B %d, %Y",     # May 27, 2025
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.datetime.strptime(date_str, fmt)
            # Return in M/D/YYYY format as required by UAT #3
            formatted_date = f"{date_obj.month}/{date_obj.day}/{date_obj.year}"
            return (
                formatted_date,
                date_obj.month,
                date_obj.year,
                date_obj.day
            )
        except ValueError:
            continue
    
    logging.getLogger(__name__).error(f"Error parsing date registered: {date_str}")
    return None
