#!/usr/bin/env python3
"""
Script to find available details pages by testing URL patterns
"""

import requests
from bs4 import BeautifulSoup
import time
import concurrent.futures
from urllib.parse import urljoin

def test_details_url(base_url, url_type, number):
    """Test if a specific details URL exists"""
    url = f"{base_url}/{url_type}-details-{number}.html"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find title
            title = "Unknown"
            bg_act_section = soup.find('section', class_='bg-act-section')
            if bg_act_section:
                h3_elem = bg_act_section.find('h3')
                if h3_elem:
                    title = h3_elem.get_text().strip()
            
            # Check for footnotes
            footnotes = soup.find_all('a', class_='tooltip')
            
            return {
                'url': url,
                'title': title,
                'footnotes': len(footnotes),
                'status': 'success'
            }
    except Exception as e:
        return {
            'url': url,
            'status': 'error',
            'error': str(e)
        }
    
    return {
        'url': url,
        'status': 'not_found'
    }

def find_available_details():
    """Find available details pages by testing common patterns"""
    base_url = "http://bdlaws.minlaw.gov.bd"
    
    print("🔍 Finding Available Details Pages")
    print("=" * 50)
    
    # Test different URL types and number ranges
    url_types = ['act', 'rules', 'ordinance']
    
    # Test some common ranges (adjust based on what we find)
    test_ranges = [
        range(1, 51),      # 1-50
        range(900, 1000),  # 900-999 (where we know 950 works)
        range(1100, 1150), # 1100-1149 (where we know 1106 works)
        range(1, 11),      # 1-10 (very early ones)
    ]
    
    available_pages = []
    
    for url_type in url_types:
        print(f"\n📋 Testing {url_type} pages...")
        
        for test_range in test_ranges:
            print(f"   Testing range {test_range.start}-{test_range.stop-1}...")
            
            # Test in batches to be nice to the server
            batch_size = 5
            for i in range(0, len(test_range), batch_size):
                batch = list(test_range)[i:i+batch_size]
                
                # Test batch with threading for speed
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futures = {
                        executor.submit(test_details_url, base_url, url_type, num): num 
                        for num in batch
                    }
                    
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        if result['status'] == 'success':
                            available_pages.append(result)
                            print(f"      ✅ Found: {result['url']}")
                            print(f"         Title: {result['title']}")
                            if result['footnotes'] > 0:
                                print(f"         📝 Footnotes: {result['footnotes']}")
                
                # Small delay between batches
                time.sleep(1)
    
    print(f"\n📊 Summary: Found {len(available_pages)} available details pages")
    
    if available_pages:
        print("\n📋 All Available Pages:")
        for page in available_pages:
            print(f"   {page['url']} - {page['title']}")
        
        # Save to a file for the scraper
        with open('available_details_urls.txt', 'w', encoding='utf-8') as f:
            for page in available_pages:
                f.write(f"{page['url']}\n")
        
        print(f"\n💾 URLs saved to: available_details_urls.txt")
        print("   You can use these URLs for comprehensive scraping!")
    
    return available_pages

if __name__ == "__main__":
    available = find_available_details()
    
    if available:
        print(f"\n🚀 To scrape all {len(available)} pages, you can:")
        print("   1. Use test mode first: python run_scraper.py --test-mode")
        print("   2. Then modify config.py to use the available URLs")
        print("   3. Or create a new script to use available_details_urls.txt")
    else:
        print("\n❌ No pages found. The website structure might have changed.")
        print("   Try checking the website manually or adjusting the search ranges.")