#!/usr/bin/env python3
"""
Test script for Bangladesh Laws HTML Scraper
Tests basic functionality with a few sample URLs
"""

import os
import sys
from bdlaws_scraper import BDLawsScraper

def test_basic_functionality():
    """Test basic scraper functionality"""
    print("Testing Bangladesh Laws HTML Scraper...")
    
    # Create a test scraper with minimal settings
    scraper = BDLawsScraper(
        base_url="http://bdlaws.minlaw.gov.bd",
        output_dir="test_output",
        delay=2.0  # Slower for testing
    )
    
    # Test URLs that should exist
    test_urls = [
        "http://bdlaws.minlaw.gov.bd/act-details-1106.html",
        "http://bdlaws.minlaw.gov.bd/act-list.php"
    ]
    
    print(f"Testing with {len(test_urls)} sample URLs...")
    
    try:
        # Test crawling with limited pages
        scraper.crawl_site(max_pages=5, start_urls=test_urls)
        
        print("\nTest Results:")
        print(f"- HTML files saved: {len(scraper.html_documents)}")
        print(f"- URLs visited: {len(scraper.visited_urls)}")
        
        # Check if files were created
        if os.path.exists("test_output"):
            file_count = sum(len(files) for _, _, files in os.walk("test_output"))
            print(f"- Files created on disk: {file_count}")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False

def test_folder_structure():
    """Test folder structure creation"""
    scraper = BDLawsScraper(output_dir="test_structure")
    
    test_cases = [
        ("http://bdlaws.minlaw.gov.bd/act-details-1106.html", "acts"),
        ("http://bdlaws.minlaw.gov.bd/rules-details-456.html", "rules"),
        ("http://bdlaws.minlaw.gov.bd/ordinance-details-789.html", "ordinances"),
        ("http://bdlaws.minlaw.gov.bd/act-list.php", "lists"),
    ]
    
    print("\nTesting folder structure creation...")
    
    for url, expected_folder in test_cases:
        file_path = scraper.create_folder_structure(url)
        actual_folder = os.path.dirname(file_path).split(os.sep)[-1]
        
        if actual_folder == expected_folder:
            print(f"✓ {url} -> {expected_folder}")
        else:
            print(f"✗ {url} -> Expected: {expected_folder}, Got: {actual_folder}")
    
    print("Folder structure test completed!")

if __name__ == "__main__":
    print("Bangladesh Laws HTML Scraper - Test Suite")
    print("=" * 60)
    
    # Test folder structure logic
    test_folder_structure()
    
    # Test basic functionality (only if not in CI environment)
    if "--skip-network" not in sys.argv:
        test_basic_functionality()
    else:
        print("\nSkipping network tests (--skip-network flag detected)")
    
    print("\nAll tests completed!")