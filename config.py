"""
Configuration file for Bangladesh Laws Text Scraper with Footnote References
"""

# Scraping Configuration
SCRAPER_CONFIG = {
    'base_url': 'http://bdlaws.minlaw.gov.bd',
    'max_pages': 1000,
    'delay_between_requests': 1.5,  # seconds
    'timeout': 30,  # seconds
    'retries': 3,
    'output_directory': 'scraped_texts'
}

# Specific starting URLs for different law categories
# These list pages contain links to the details pages we want to scrape
START_URLS = [
    'http://bdlaws.minlaw.gov.bd/act-list.php',
    'http://bdlaws.minlaw.gov.bd/rules-list.php', 
    'http://bdlaws.minlaw.gov.bd/ordinance-list.php',
    'http://bdlaws.minlaw.gov.bd/',  # Main page for discovery
]

# Example details page URLs (for testing)
SAMPLE_DETAILS_URLS = [
    'http://bdlaws.minlaw.gov.bd/act-details-950.html',
    'http://bdlaws.minlaw.gov.bd/act-details-1106.html',
]

# Tax-related keywords for better categorization
TAX_KEYWORDS = [
    'income tax', 'vat', 'value added tax', 'customs', 'duty', 'tariff',
    'revenue', 'tax administration', 'tax collection', 'excise',
    'withholding tax', 'advance tax', 'supplementary duty',
    'import duty', 'export duty', 'tax exemption', 'tax holiday'
]

# Content filtering settings
CONTENT_FILTERS = {
    'min_content_length': 100,  # Minimum characters for valid content
    'exclude_extensions': ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
    'exclude_domains': [],  # Add domains to exclude if needed
    'include_only_text': True
}

# Output format settings
OUTPUT_CONFIG = {
    'save_as_json': True,
    'save_as_text': True,
    'save_as_csv': False,  # Can be enabled if needed
    'include_metadata': True,
    'compress_output': False
}