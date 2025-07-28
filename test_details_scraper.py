#!/usr/bin/env python3
"""
Test script for Bangladesh Laws Details Page Scraper
Tests focused scraping of only details pages with proper title extraction
"""

import os
import sys
from bdlaws_scraper import BDLawsScraper
from config import SAMPLE_DETAILS_URLS

def test_details_page_scraping():
    """Test scraping of specific details pages"""
    print("Testing Details Page Scraping")
    print("=" * 50)
    
    # Create a test scraper
    scraper = BDLawsScraper(
        base_url="http://bdlaws.minlaw.gov.bd",
        output_dir="test_details_output",
        delay=2.0
    )
    
    print(f"Testing with {len(SAMPLE_DETAILS_URLS)} sample details URLs...")
    
    for url in SAMPLE_DETAILS_URLS:
        print(f"\nTesting URL: {url}")
        
        # Check if it's identified as a details page
        is_details = scraper.is_details_page(url)
        print(f"  Identified as details page: {is_details}")
        
        if is_details:
            try:
                # Try to crawl the page
                discovered_urls = scraper.crawl_page(url)
                print(f"  Discovered {len(discovered_urls)} new URLs")
                
            except Exception as e:
                print(f"  Error crawling page: {e}")
    
    print(f"\nResults:")
    print(f"- Documents processed: {len(scraper.documents)}")
    
    if scraper.documents:
        print("\nProcessed Documents:")
        for i, doc in enumerate(scraper.documents, 1):
            print(f"{i}. Title: {doc.title}")
            print(f"   Category: {doc.category}")
            print(f"   Footnotes: {len(doc.footnotes)}")
            print(f"   File: {doc.file_path}")
            print()
    
    return len(scraper.documents) > 0

def test_title_extraction():
    """Test title extraction with sample HTML"""
    print("\nTesting Title Extraction")
    print("=" * 50)
    
    # Sample HTML with the structure you provided
    sample_html = '''
    <html>
    <body>
        <section class="bg-act-section padding-bottom-20">
            <div class="row">
                <div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">
                    <div class="text-center">
                        <h3>
                            অর্থ অধ্যাদেশ, ২০২৫
                        </h3>
                        <h4 style="color: #fff;"> (
                            ২০২৫ সনের ২৮ নং অধ্যাদেশ
                        )
                        </h4>
                    </div>
                </div>
            </div>
        </section>
        <p>This is the content of the document...</p>
    </body>
    </html>
    '''
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    scraper = BDLawsScraper()
    title = scraper.extract_document_title(soup)
    safe_filename = scraper.sanitize_filename(title)
    
    print(f"Extracted title: '{title}'")
    print(f"Safe filename: '{safe_filename}'")
    
    expected_title = "অর্থ অধ্যাদেশ, ২০২৫"
    if title.strip() == expected_title:
        print("✓ Title extraction working correctly!")
        return True
    else:
        print("✗ Title extraction failed")
        print(f"Expected: '{expected_title}'")
        print(f"Got: '{title}'")
        return False

def test_url_filtering():
    """Test URL filtering for details pages"""
    print("\nTesting URL Filtering")
    print("=" * 50)
    
    scraper = BDLawsScraper()
    
    test_urls = [
        "http://bdlaws.minlaw.gov.bd/act-details-950.html",
        "http://bdlaws.minlaw.gov.bd/rules-details-456.html", 
        "http://bdlaws.minlaw.gov.bd/ordinance-details-789.html",
        "http://bdlaws.minlaw.gov.bd/act-list.php",
        "http://bdlaws.minlaw.gov.bd/rules-list.php",
        "http://bdlaws.minlaw.gov.bd/about.html",
        "http://bdlaws.minlaw.gov.bd/contact.php"
    ]
    
    for url in test_urls:
        is_details = scraper.is_details_page(url)
        should_process = "YES" if is_details else "NO"
        print(f"  {url} -> Process: {should_process}")
    
    # Count how many should be processed
    details_count = sum(1 for url in test_urls if scraper.is_details_page(url))
    print(f"\n  Details pages identified: {details_count} out of {len(test_urls)}")
    
    return details_count == 3  # Should identify exactly 3 details pages

if __name__ == "__main__":
    print("Bangladesh Laws Details Page Scraper Test")
    print("=" * 60)
    
    # Test title extraction
    title_success = test_title_extraction()
    
    # Test URL filtering
    url_success = test_url_filtering()
    
    # Test details page scraping (only if not in CI environment)
    if "--skip-network" not in sys.argv:
        scraping_success = test_details_page_scraping()
    else:
        print("\nSkipping network tests (--skip-network flag detected)")
        scraping_success = True
    
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print(f"  Title Extraction: {'✓ PASS' if title_success else '✗ FAIL'}")
    print(f"  URL Filtering: {'✓ PASS' if url_success else '✗ FAIL'}")
    if "--skip-network" not in sys.argv:
        print(f"  Details Scraping: {'✓ PASS' if scraping_success else '✗ FAIL'}")
    
    if all([title_success, url_success, scraping_success]):
        print("\n🎉 All tests passed! The focused details scraper is ready.")
    else:
        print("\n❌ Some tests failed. Check the implementation.")