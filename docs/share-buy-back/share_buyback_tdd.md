# Share Buy-Back Feature - Technical Design Document (TDD)

## System Overview

### Architecture Context
The PSE Data Scraper follows a layered architecture with clear separation of concerns:
- **Domain Layer**: Report type definitions and business entities
- **Data Access Layer**: Specialized processors for each report type
- **Business Logic Layer**: Core scraper orchestration and routing
- **Presentation Layer**: CLI interface with interactive and direct modes

### Integration Points
- **ReportType Enum**: Add SHARE_BUYBACK constant
- **Processor Interface**: Implement ShareBuybackProcessor following established pattern
- **Core Scraper Routing**: Add routing logic for share buyback documents
- **CLI Menu System**: Extend menu with option 8

## System Architecture

### High-Level Data Flow
```
User Input (Company ID/Symbol)
    ↓
CLI Interface (option 8)
    ↓
PSEDataScraper.scrape_data()
    ↓
Search PSE Edge for buyback disclosures
    ↓
_process_document_rows() → _process_single_row()
    ↓
_process_document() → ShareBuybackProcessor
    ↓
Extract data from HTML/iframe
    ↓
Return structured data
    ↓
Save to CSV/JSON files
```

### Component Architecture

#### Domain Layer: ReportType Enhancement
```python
class ReportType(Enum):
    # ... existing types ...
    SHARE_BUYBACK = "Share Buy-Back Transactions"
```

#### Data Access Layer: ShareBuybackProcessor
```python
class ShareBuybackProcessor:
    def __init__(self, logger):
        self.logger = logger
    
    def process(self, soup: BeautifulSoup, stock_name: str, disclosure_date: str) -> Optional[Dict]:
        """
        Process share buyback transaction document.
        
        Args:
            soup: BeautifulSoup object of the iframe document
            stock_name: Stock name/symbol (e.g., "ALI")
            disclosure_date: Disclosure date from search results
            
        Returns:
            Dictionary containing processed share buyback data or None if no data found
        """
        # soup: iframe content (BeautifulSoup object)
        # stock_name: extracted from <span id="companyStockSymbol">
        # disclosure_date: from search results
        # Returns: {"stock name": stock_name, "disclosure date": disclosure_date, ...extracted_fields}
        
    def _extract_share_buyback_data(self, soup: BeautifulSoup, stock_name: str, report_date: str) -> Dict:
        """Extract data from share buyback document following existing processor patterns."""
        
    def _extract_transaction_tables(self, soup: BeautifulSoup) -> Dict:
        """Extract tabular data from share buyback tables."""
        
    def _extract_form_fields(self, soup: BeautifulSoup) -> Dict:
        """Extract form field data from share buyback forms."""
```

#### Business Logic Layer: Core Scraper Integration
```python
# In PSEDataScraper._process_document_rows()
if report_type == ReportType.SHARE_BUYBACK:
    self._process_single_row(rows, report_type)

# In PSEDataScraper._process_document()
elif report_type == ReportType.SHARE_BUYBACK:
    from ..core.processors.share_buyback import ShareBuybackProcessor
    processor = ShareBuybackProcessor(self.logger)
    result = processor.process(iframe_soup, stock_name, disclosure_date)
```

#### Presentation Layer: CLI Updates
```python
# REPORT_TYPES mapping
REPORT_TYPES = {
    # ... existing mappings ...
    "share_buyback": ReportType.SHARE_BUYBACK,
}

# Interactive menu options
menu_options = [
    # ... existing options 1-7 ...
    "8. Share Buy-Back Transactions",
]

# Report type mapping for interactive mode
report_type_map = {
    # ... existing mappings 1-7 ...
    "8": ReportType.SHARE_BUYBACK,
}
```

## Data Models

### Input Data Contract
```typescript
interface ShareBuybackRequest {
    company: string;           // Company symbol or ID (e.g., "ALI" or "180")
    report_type: "share_buyback";
    output?: string;          // Output filename
    formats?: string[];       // ["csv", "json"]
    workers?: number;         // Concurrent workers
}
```

### PSE Edge Search Payload
```typescript
interface PSESearchPayload {
    keyword: string;          // Company ID
    tmplNm: string;          // "Share Buy-Back Transactions"
    sortType: "date";        // Fixed value
    dateSortType: "DESC";    // Fixed value  
    pageNo?: number;         // For pagination
}
```

### Output Data Contract
```typescript
interface ShareBuybackData {
    "stock name": string;        // "ALI" (from companyStockSymbol span)
    "disclosure date": string;   // Disclosure date from search results
    // Additional fields extracted from iframe document:
    // NOTE: Actual field structure needs verification from real share buyback documents
    // The reference image shows Public Ownership format, not share buyback format
    [field: string]: any;       // Dynamic fields based on actual document structure
}
```

### Database Schema
No database changes required - follows existing file-based output pattern.

## API Specifications

### CLI Interface Contract

#### Interactive Mode
```bash
# User selects option 8 from menu
$ pse-scraper
> 8
Enter output filename: ali_buyback
Enter company symbol OR starting company ID: ALI
```

#### Direct Command Mode
```bash
$ pse-scraper scrape ALI share_buyback --output ali_buyback
$ pse-scraper scrape 180 share_buyback --format csv json
```

#### Bulk Processing Mode
```bash
$ pse-scraper bulk 180 185 share_buyback --output bulk_buyback
```

### Internal API Contracts

#### Processor Interface
```python
def process(
    self, 
    soup: BeautifulSoup, 
    stock_name: str, 
    disclosure_date: str
) -> Optional[Dict]:
    """
    Process share buyback document and extract structured data.
    
    Args:
        soup: Parsed HTML of the disclosure document
        stock_name: Stock symbol (e.g., "ALI")
        disclosure_date: Date of disclosure (e.g., "5/27/2025")
    
    Returns:
        Dictionary with extracted data or None if no data found
    
    Raises:
        Exception: For processing errors (logged, not propagated)
    """
```

## Integration Design

### PSE Edge Integration Points

#### Search Phase ✅ (Verified)
- **Method**: POST to `https://edge.pse.com.ph/companyDisclosures/search.ax`
- **Payload**: `{keyword: company_id, tmplNm: "Share Buy-Back Transactions", sortType: "date", dateSortType: "DESC", pageNo: 1}`
- **Response**: HTML with search results table containing clickable links with edge_no in onclick handlers
- **Confirmed Template**: "Share Buy-Back Transactions" (exact match found in live data)
- **Confirmed PSE Form**: "9-1" (consistent across all share buyback entries)

#### Document Retrieval Phase ✅ (Verified)
- **Method**: GET `https://edge.pse.com.ph/openDiscViewer.do?edge_no={extracted_edge_no}`
- **Response**: HTML page containing iframe element
- **Iframe Processing**: Extract iframe src attribute and make additional request
- **Confirmed Flow**: Same as existing processors (matches core implementation)

#### Data Extraction Phase ⚠️ (Needs Implementation)
- **Stock Name**: Extract from `<span id="companyStockSymbol">` in iframe content
- **Document Data**: Parse HTML tables, forms, or structured content within iframe
- **Field Mapping**: **REQUIRES ACTUAL DOCUMENT ANALYSIS** - Cannot access iframe content directly
- **Data Structure**: Follow existing processor pattern with `{"stock name": str, "disclosure date": str, ...}`

#### Technical Findings from Live PSE Edge Data
```html
<!-- Sample search result row -->
<tr>
  <td><a href="#viewer" onclick="openPopup('06f23f9fa8cd469fec6e1601ccee8f59');return false;">Share Buy-Back Transactions</a></td>
  <td class="alignC">Jul 04, 2025 08:08 AM</td>
  <td class="alignC">9-1</td>
  <td class="alignC">C04793-2025</td>
</tr>
```

**Document Processing Pattern:**
1. Extract `edge_no` from onclick handler: `06f23f9fa8cd469fec6e1601ccee8f59`
2. Request: `https://edge.pse.com.ph/openDiscViewer.do?edge_no=06f23f9fa8cd469fec6e1601ccee8f59`
3. Parse iframe src from response
4. Fetch iframe content and parse with BeautifulSoup
5. Extract data using table parsing (similar to cash_dividends.py pattern)

### Existing System Integration

#### Report Type Registration
```python
# File: src/pse_scraper/models/report_types.py
SHARE_BUYBACK = "Share Buy-Back Transactions"  # Add to enum
```

#### Processor Registration
```python
# File: src/pse_scraper/core/processors/__init__.py
from .share_buyback import ShareBuybackProcessor
__all__ = [..., "ShareBuybackProcessor"]
```

#### Routing Integration
```python
# File: src/pse_scraper/core/__init__.py
# Add to _process_document_rows() and _process_document()
```

#### CLI Integration
```python
# File: src/pse_scraper/cli.py
# Add to REPORT_TYPES, menu_options, and report_type_map
```

## Error Handling Strategy

### Error Categories

#### Network Errors
- **PSE Edge Unavailable**: Retry with existing HTTPClient logic
- **Document Not Found**: Log warning, return None
- **Timeout Issues**: Use existing timeout handling

#### Parsing Errors
- **Invalid HTML Structure**: Log error, attempt fallback parsing
- **Missing Data Fields**: Log warning, return partial data
- **Data Type Conversion**: Log error, keep original string value

#### Business Logic Errors
- **No Buyback Disclosures**: Return None, display "No data found"
- **Invalid Company ID**: Follow existing error handling pattern
- **Empty Search Results**: Log info, return None

### Error Recovery
```python
try:
    # Primary extraction strategy
    result = self._extract_buyback_data(soup)
except Exception as e:
    self.logger.error(f"Primary extraction failed: {e}")
    try:
        # Fallback extraction strategy
        result = self._extract_fallback_data(soup)
    except Exception as e2:
        self.logger.error(f"Fallback extraction failed: {e2}")
        return None
```

## Performance Considerations

### Response Time Targets
- **Single Company**: <30 seconds (matching existing report types)
- **Bulk Processing**: Linear scaling with existing performance
- **Memory Usage**: Minimal impact on existing memory footprint

### Optimization Strategies
- **Concurrent Processing**: Leverage existing ThreadPoolExecutor
- **HTTP Connection Reuse**: Use existing HTTPClient session management
- **Parsing Efficiency**: Minimal DOM traversal, targeted element selection

### Scalability
- **Horizontal Scaling**: No changes to existing concurrent processing
- **Resource Usage**: Follow existing patterns for memory management
- **Caching**: Utilize existing response caching mechanisms

## Security Considerations

### Input Validation
- **Company ID Validation**: Use existing validation patterns
- **SQL Injection Prevention**: Not applicable (no database)
- **Path Traversal**: Use existing file output validation

### Data Security
- **No Sensitive Data**: Public disclosure information only
- **Output File Security**: Follow existing file permission patterns
- **Network Security**: Use existing HTTPS enforcement

### Authentication
- **No Authentication Required**: Public PSE Edge data
- **Rate Limiting**: Respect existing request throttling
- **User Agent**: Use existing user agent strings

## Monitoring and Observability

### Logging Strategy
```python
# Follow existing logging patterns
self.logger.info(f"Processing share buyback for {stock_name}")
self.logger.warning(f"No buyback data found for {stock_name}")
self.logger.error(f"Extraction failed for {stock_name}: {error}")
self.logger.debug(f"Extracted fields: {field_count}")
```

### Metrics Collection
- **Success Rate**: Percentage of successful extractions
- **Processing Time**: Average time per company
- **Error Rate**: Frequency of extraction failures
- **Data Quality**: Completeness of extracted fields

### Health Checks
- **Functionality Verification**: Test against known sample (company ID 180)
- **Performance Monitoring**: Track processing times
- **Error Rate Monitoring**: Alert on high failure rates

## Testing Strategy

### Unit Testing
```python
class TestShareBuybackProcessor:
    def test_process_valid_document(self):
        # Test with sample HTML from company ID 180
        
    def test_process_empty_document(self):
        # Test with document containing no buyback data
        
    def test_date_parsing(self):
        # Test date component extraction
        
    def test_numeric_conversion(self):
        # Test value extraction and conversion
```

### Integration Testing
```python
class TestShareBuybackIntegration:
    def test_end_to_end_extraction(self):
        # Test complete flow for company ID 180
        
    def test_cli_menu_option(self):
        # Test menu option 8 functionality
        
    def test_bulk_processing(self):
        # Test bulk mode with share buyback
```

### Manual Testing Scenarios
1. **Happy Path**: Company ID 180 (known to have share buyback data)
2. **No Data Path**: Company with no buyback disclosures
3. **Invalid Company**: Non-existent company ID
4. **Network Issues**: Test with simulated connectivity problems

## Deployment Strategy

### Development Phase
1. **Local Development**: Implement following TDD specifications
2. **Unit Testing**: Verify individual components
3. **Integration Testing**: Test with real PSE Edge data
4. **Manual Validation**: Compare output with sample PDF

### Release Strategy
1. **Feature Branch**: Implement in dedicated branch
2. **Code Review**: Follow existing review process
3. **Merge to Main**: After all tests pass
4. **Version Tagging**: Update version for release

### Rollback Plan
- **No Breaking Changes**: Feature is purely additive
- **Rollback Strategy**: Remove new menu option, revert enum
- **Data Migration**: No data migration required

## Dependencies and Constraints

### Internal Dependencies
- **ReportType Enum**: Must extend existing enum
- **Processor Pattern**: Must follow established interface
- **HTTPClient**: Reuse existing HTTP handling
- **Logging**: Use existing logging infrastructure

### External Dependencies
- **PSE Edge Availability**: Dependent on external service
- **HTML Structure Stability**: Risk of structure changes
- **Network Connectivity**: Standard internet connectivity required

### Technical Constraints
- **Backward Compatibility**: Cannot break existing functionality
- **Performance**: Must not degrade existing performance
- **Memory Usage**: Must not significantly increase memory footprint
- **Python Version**: Must work with existing Python 3.x requirements

### Business Constraints
- **Timeline**: Implementation within defined sprint
- **Resources**: Single developer implementation
- **Quality**: Must match existing code quality standards
- **Documentation**: Must provide comprehensive documentation