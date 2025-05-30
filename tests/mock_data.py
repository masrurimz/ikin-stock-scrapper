"""
Mock data and fixtures for testing PSE scraper functionality.
"""

# Sample HTML responses for different report types
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
                <tr>
                    <th>Date Filed</th>
                    <td>Mar 15, 2024 09:30 AM</td>
                </tr>
            </table>
        </div>
    </body>
</html>
"""

SAMPLE_ANNUAL_REPORT_HTML = """
<html>
    <body>
        <div class="results">
            <span class="count">1 result found</span>
            <table class="financial-data">
                <tr>
                    <th>Total Assets</th>
                    <td>25,000,000,000</td>
                </tr>
                <tr>
                    <th>Total Liabilities</th>
                    <td>15,000,000,000</td>
                </tr>
                <tr>
                    <th>Total Equity</th>
                    <td>10,000,000,000</td>
                </tr>
                <tr>
                    <th>Net Income</th>
                    <td>2,500,000,000</td>
                </tr>
            </table>
            <table class="ratios">
                <tr>
                    <th>Return on Assets</th>
                    <td>10.5%</td>
                </tr>
                <tr>
                    <th>Return on Equity</th>
                    <td>25.0%</td>
                </tr>
            </table>
        </div>
    </body>
</html>
"""

SAMPLE_CASH_DIVIDENDS_HTML = """
<html>
    <body>
        <div class="results">
            <span class="count">Multiple dividends found</span>
            <table class="dividend-table">
                <tr>
                    <th>Ex-Date</th>
                    <td>Dec 15, 2023</td>
                </tr>
                <tr>
                    <th>Record Date</th>
                    <td>Dec 18, 2023</td>
                </tr>
                <tr>
                    <th>Payment Date</th>
                    <td>Jan 15, 2024</td>
                </tr>
                <tr>
                    <th>Dividend Rate</th>
                    <td>₱2.50 per share</td>
                </tr>
            </table>
        </div>
    </body>
</html>
"""

SAMPLE_STOCKHOLDERS_HTML = """
<html>
    <body>
        <div class="results">
            <span class="count">Top 100 stockholders</span>
            <table class="stockholders-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Name</th>
                        <th>Shares Held</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>ABC Holdings Corporation</td>
                        <td>450,000,000</td>
                        <td>30.5%</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>XYZ Investment Fund</td>
                        <td>225,000,000</td>
                        <td>15.2%</td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>Individual Investor Group</td>
                        <td>150,000,000</td>
                        <td>10.1%</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </body>
</html>
"""

SAMPLE_EMPTY_RESULTS_HTML = """
<html>
    <body>
        <div class="results">
            <span class="count">No results found</span>
            <p>No data available for the selected criteria.</p>
        </div>
    </body>
</html>
"""

SAMPLE_MALFORMED_HTML = """
<html>
    <body>
        <div class="results">
            <span class="count">Results found</span>
            <table>
                <tr>
                    <th>Company Name
                    <td>Incomplete Corp</td>
                </tr>
                <tr>
                    <th>Value</th>
                    <td>123,456
                </tr>
            </table>
        </div>
    </body>
"""

# Sample data structures
SAMPLE_SCRAPED_DATA = [
    {
        "stock name": "TEST1",
        "disclosure date": "2024-01-15",
        "Company Name": "Test Corporation 1",
        "Total Outstanding Shares": "1000000000",
        "Public Ownership Level": "45.5%"
    },
    {
        "stock name": "TEST2", 
        "disclosure date": "2024-01-16",
        "Company Name": "Test Corporation 2",
        "Total Outstanding Shares": "2000000000",
        "Public Ownership Level": "38.2%"
    },
    {
        "stock name": "TEST3",
        "disclosure date": "2024-01-17", 
        "Company Name": "Test Corporation 3",
        "Total Outstanding Shares": "500000000",
        "Public Ownership Level": "52.1%"
    }
]

# Test configurations
TEST_CONFIGURATIONS = {
    "default": {
        "max_workers": 1,
        "enable_logging": False,
        "use_proxies": False
    },
    "concurrent": {
        "max_workers": 3,
        "enable_logging": False,
        "use_proxies": False
    },
    "production": {
        "max_workers": 5,
        "enable_logging": True,
        "use_proxies": True
    }
}

# Common test parameters
TEST_STOCK_NAMES = ["TEST", "SAMPLE", "MOCK", "DEMO"]
TEST_DATES = ["2024-01-15", "2024-02-20", "2024-03-25", "2024-04-30"]

# Error scenarios for testing
ERROR_SCENARIOS = {
    "network_timeout": {
        "error_type": "requests.exceptions.Timeout",
        "description": "Network request timeout"
    },
    "connection_error": {
        "error_type": "requests.exceptions.ConnectionError", 
        "description": "Network connection failed"
    },
    "http_error": {
        "error_type": "requests.exceptions.HTTPError",
        "description": "HTTP error response"
    },
    "parse_error": {
        "error_type": "BeautifulSoup parsing error",
        "description": "HTML parsing failed"
    }
}
