"""
Test configuration and fixtures.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Define mock data directly in conftest to avoid import issues
SAMPLE_PUBLIC_OWNERSHIP_HTML = """
<html>
    <body>
        <div class="results">
            <span class="count">Showing 1-1 of 1 results</span>
            <table class="data-table">
                <tr>
                    <th>Company Name</th>
                    <td>Sample Corporation Inc.</td>
                </tr>
                <tr>
                    <th>Total Outstanding Shares</th>
                    <td>1,500,000,000</td>
                </tr>
                <tr>
                    <th>Public Ownership Level</th>
                    <td>45.25%</td>
                </tr>
            </table>
        </div>
    </body>
</html>
"""

SAMPLE_SCRAPED_DATA = [
    {
        "stock name": "TEST1",
        "disclosure date": "2024-01-15",
        "Company Name": "Test Corporation 1",
        "Total Outstanding Shares": "1000000000"
    }
]

TEST_CONFIGURATIONS = {
    "default": {
        "max_workers": 1,
        "enable_logging": False,
        "use_proxies": False
    }
}


@pytest.fixture
def sample_html():
    """Sample HTML for testing."""
    return """
    <html>
        <body>
            <table>
                <tr>
                    <th>Company Name</th>
                    <td>Sample Company</td>
                </tr>
                <tr>
                    <th>Total Shares</th>
                    <td>1,000,000</td>
                </tr>
                <tr>
                    <th>Share Price</th>
                    <td>125.50</td>
                </tr>
            </table>
        </body>
    </html>
    """


@pytest.fixture
def sample_stock_name():
    """Sample stock name for testing."""
    return "TEST"


@pytest.fixture
def sample_disclosure_date():
    """Sample disclosure date for testing."""
    return "2024-01-15"


@pytest.fixture
def mock_http_response():
    """Mock HTTP response for testing."""
    response = Mock()
    response.text = SAMPLE_PUBLIC_OWNERSHIP_HTML
    response.status_code = 200
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def sample_scraped_data():
    """Sample scraped data for testing."""
    return SAMPLE_SCRAPED_DATA.copy()


@pytest.fixture
def test_config():
    """Test configuration for scraper."""
    return TEST_CONFIGURATIONS["default"]


@pytest.fixture
def public_ownership_html():
    """Sample public ownership HTML."""
    return SAMPLE_PUBLIC_OWNERSHIP_HTML


@pytest.fixture
def empty_results_html():
    """Sample empty results HTML."""
    return "<html><body><p>No results found</p></body></html>"


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()
