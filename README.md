# Bangladesh Laws Text Scraper with Footnote References

A Python web scraper designed to extract text content from the Bangladesh Laws website (bdlaws.minlaw.gov.bd) while preserving important footnote references and tooltip information for AI tax lawyer applications.

## Features

- **Text Content Extraction**: Extracts clean text content from HTML pages
- **Footnote Reference Preservation**: Maintains reference numbers and their corresponding tooltip titles
- **Intelligent Categorization**: Automatically categorizes documents by law type (tax, corporate, etc.)
- **Cross-Reference Support**: Perfect for AI systems that need to follow legal references
- **Dual Output Format**: Saves both structured text files and JSON for different use cases
- **PDF Filtering**: Automatically skips PDF files and focuses only on HTML content
- **Respectful Crawling**: Implements rate limiting, robots.txt compliance, and error handling
- **Progress Tracking**: Real-time progress monitoring with detailed logging

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python run_scraper.py
```

### Advanced Options
```bash
# Scrape with custom parameters
python run_scraper.py --max-pages 2000 --delay 2.0 --output-dir my_legal_texts

# Use predefined starting URLs for comprehensive scraping
python run_scraper.py --use-predefined-urls --max-pages 3000
```

### Available Arguments
- `--max-pages`: Maximum number of pages to scrape (default: 1000)
- `--delay`: Delay between requests in seconds (default: 1.5)
- `--output-dir`: Output directory for text files (default: scraped_texts)
- `--start-url`: Starting URL for scraping
- `--use-predefined-urls`: Use predefined URLs for comprehensive coverage

## Output Structure

The scraper creates the following organized structure:

```
scraped_texts/
├── tax_law/
│   ├── act-details-1106.txt        # Tax-related laws as text
│   ├── act-details-1106.json       # Same content as JSON
│   └── ...
├── corporate_law/
│   ├── company-act-123.txt
│   ├── company-act-123.json
│   └── ...
├── constitutional_law/
├── civil_criminal_law/
├── labor_law/
├── general_law/
├── crawl_summary.json              # Summary statistics
└── scraper.log                     # Detailed logs
```

## File Format

Each document is saved in two formats:

### Text File (.txt)
```
Title: Income Tax Act 2023
URL: http://bdlaws.minlaw.gov.bd/act-details-1106.html
Category: tax_law
================================================================================

CONTENT:
এই আইনের উদ্দেশ্য পূরণকল্পে সরকার সরকারি গেজেটে প্রজ্ঞাপন দ্বারা বিধি প্রণয়ন করিতে পারিবে।

[REF_8][তবে শর্ত থাকে যে, এই আইনের তৃতীয় তফসিলের অনুচ্ছেদ (৩) এ উল্লিখিত ব্যবসায়ী কর্তৃক ব্যবসা পরিচালনার ক্ষেত্রে বিক্রয়, বিনিময় বা হস্তান্তরের উদ্দেশ্যে আমদানিকৃত, ক্রয়কৃত, অর্জিত বা অন্যকোনভাবে সংগৃহীত পণ্য বা সেবা উপকরণ হিসাবে গণ্য হইবে;]

FOOTNOTES:
----------------------------------------
[REF_8]: শর্তাংশ দফা (১৮ক) এর শর্তাংশের পরিবর্তে অর্থ আইন, ২০২২ (২০২২ সনের ১৩ নং আইন) এর ৫৬(ক) ধারাবলে প্রতিস্থাপিত যাহা ১ জুলাই ২০২২ তারিখ হইতে কার্যকর।
Position: 150
```

### JSON File (.json)
```json
{
  "title": "Income Tax Act 2023",
  "url": "http://bdlaws.minlaw.gov.bd/act-details-1106.html",
  "category": "tax_law",
  "text_content": "Main text with [REF_8] markers...",
  "footnotes": [
    {
      "ref_number": "8",
      "tooltip_title": "শর্তাংশ দফা (১৮ক) এর শর্তাংশের পরিবর্তে...",
      "position_in_text": 150
    }
  ]
}
```

## Footnote Reference System

The scraper identifies footnote elements like:
```html
<span class="footnote" title="Tooltip text here">
  <span class="word-formet">
    <sup class="bn">
      <a href="8">8</a>
    </sup>
  </span>
</span>
```

And converts them to:
- **Text marker**: `[REF_8]` in the main text
- **Reference data**: Complete tooltip information for cross-referencing

## Summary Data

The `crawl_summary.json` file contains:

```json
{
  "total_documents": 1250,
  "total_footnotes": 3456,
  "categories": {
    "tax_law": 400,
    "corporate_law": 300,
    "constitutional_law": 200,
    "civil_criminal_law": 250,
    "labor_law": 100
  },
  "total_pages_visited": 1500,
  "crawl_timestamp": "2024-01-15 10:30:00"
}
```

## Configuration

Modify `config.py` to customize:
- Starting URLs
- Tax-related keywords
- Content filtering settings
- Output format preferences

## Testing

Run the test suite to verify functionality:

```bash
# Test footnote extraction with sample HTML
python test_footnote_extraction.py

# Test folder structure logic only
python test_scraper.py --skip-network

# Test full functionality (requires internet connection)
python test_scraper.py
```

## Ethical Usage

This scraper is designed for:
- Legal research and analysis
- AI training for tax calculation systems
- Academic and educational purposes
- Building comprehensive legal reference databases
- Preserving legal documents in accessible HTML format

Please ensure compliance with:
- Website terms of service
- Local laws regarding web scraping
- Respectful crawling practices (rate limiting is implemented)

## Error Handling

The scraper includes robust error handling:
- Network timeouts and connection errors
- Malformed HTML or parsing errors
- Rate limiting and server overload protection
- Automatic retry mechanisms with exponential backoff

## Logging

Detailed logs are saved to `scraper.log` including:
- Pages successfully scraped
- Documents categorized and saved
- Errors and warnings
- Performance metrics

## Legal Disclaimer

This tool is intended for legitimate legal research and AI development purposes. Users are responsible for ensuring their use complies with applicable laws and website terms of service.