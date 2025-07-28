#!/usr/bin/env python3
"""
Test script to check URL discovery from list pages
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def test_url_discovery():
    """Test what URLs are discovered from list pages"""
    base_url = "http://bdlaws.minlaw.gov.bd"
    test_pages = [
        "http://bdlaws.minlaw.gov.bd/act-list.php",
        "http://bdlaws.minlaw.gov.bd/rules-list.php", 
        "http://bdlaws.minlaw.gov.bd/ordinance-list.php"
    ]
    
    print("Testing URL Discovery from List Pages")
    print("=" * 50)
    
    for test_url in test_pages:
        print(f"\n🔍 Testing: {test_url}")
        
        try:
            response = requests.get(test_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            all_links = []
            details_links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(test_url, href)
                
                if full_url.startswith(base_url):
                    all_links.append(full_url)
                    
                    # Check if it's a details page
                    if '-details-' in full_url:
                        details_links.append(full_url)
            
            print(f"   📊 Total links found: {len(all_links)}")
            print(f"   🎯 Details pages found: {len(details_links)}")
            
            if details_links:
                print("   📋 Sample details pages:")
                for url in details_links[:5]:  # Show first 5
                    print(f"      - {url}")
                if len(details_links) > 5:
                    print(f"      ... and {len(details_links) - 5} more")
            else:
                print("   ❌ No details pages found!")
                print("   🔍 Sample links found:")
                for url in all_links[:10]:  # Show first 10 links
                    print(f"      - {url}")
            
            time.sleep(2)  # Be nice to the server
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Testing sample details pages:")
    
    # Test known details pages
    sample_details = [
        "http://bdlaws.minlaw.gov.bd/act-details-950.html",
        "http://bdlaws.minlaw.gov.bd/act-details-1106.html"
    ]
    
    for url in sample_details:
        print(f"\n🔍 Testing: {url}")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find title
                bg_act_section = soup.find('section', class_='bg-act-section')
                if bg_act_section:
                    h3_elem = bg_act_section.find('h3')
                    if h3_elem:
                        title = h3_elem.get_text().strip()
                        print(f"   ✅ Title found: {title}")
                    else:
                        print("   ⚠️ No h3 in bg-act-section")
                else:
                    print("   ⚠️ No bg-act-section found")
                
                # Check for footnotes
                footnotes = soup.find_all('a', class_='tooltip')
                print(f"   📝 Footnotes found: {len(footnotes)}")
                
            else:
                print(f"   ❌ Status code: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    test_url_discovery()