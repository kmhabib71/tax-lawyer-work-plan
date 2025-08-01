#!/usr/bin/env python3
"""
Debug crawler to understand the website structure
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def debug_website_structure():
    """Debug what links actually exist on key pages"""
    base_url = "http://bdlaws.minlaw.gov.bd"
    
    test_pages = [
        f"{base_url}/laws-of-bangladesh-alphabetical-index.html",
        f"{base_url}/laws-of-bangladesh-chronological-index.html"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for test_url in test_pages:
        print(f"\n🔍 Analyzing: {test_url}")
        print("=" * 60)
        
        try:
            response = session.get(test_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            print(f"📊 Total links found: {len(all_links)}")
            
            # Analyze link patterns
            patterns = {}
            details_links = []
            sample_links = []
            
            for link in all_links:
                href = link['href']
                full_url = urljoin(test_url, href)
                
                # Count patterns
                if 'act-' in href:
                    patterns['act-'] = patterns.get('act-', 0) + 1
                if 'rules-' in href:
                    patterns['rules-'] = patterns.get('rules-', 0) + 1
                if 'ordinance-' in href:
                    patterns['ordinance-'] = patterns.get('ordinance-', 0) + 1
                if '-details-' in href:
                    patterns['-details-'] = patterns.get('-details-', 0) + 1
                    details_links.append(full_url)
                
                # Collect samples
                if len(sample_links) < 10:
                    sample_links.append(full_url)
            
            print(f"\n📋 Link patterns found:")
            for pattern, count in patterns.items():
                print(f"   {pattern}: {count}")
            
            if details_links:
                print(f"\n✅ Details pages found: {len(details_links)}")
                for url in details_links[:5]:
                    print(f"   - {url}")
            else:
                print(f"\n❌ No -details- pages found!")
            
            print(f"\n📄 Sample links:")
            for url in sample_links:
                print(f"   - {url}")
            
            # Check for different link structures
            print(f"\n🔍 Looking for alternative patterns...")
            
            # Check for different href patterns
            alt_patterns = {}
            for link in all_links:
                href = link['href']
                text = link.get_text().strip()
                
                # Look for numeric patterns
                if any(c.isdigit() for c in href):
                    if '.html' in href and 'act' in href:
                        alt_patterns['act-NUMBER.html'] = alt_patterns.get('act-NUMBER.html', 0) + 1
                    if '.html' in href and 'rules' in href:
                        alt_patterns['rules-NUMBER.html'] = alt_patterns.get('rules-NUMBER.html', 0) + 1
                
                # Sample numeric links
                if any(c.isdigit() for c in href) and len(sample_links) < 20:
                    print(f"   🔢 {href} -> {text[:50]}")
            
            print(f"\n📊 Alternative patterns:")
            for pattern, count in alt_patterns.items():
                print(f"   {pattern}: {count}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_known_details_pages():
    """Test the structure of known working details pages"""
    print(f"\n🧪 Testing known details pages structure:")
    print("=" * 50)
    
    known_pages = [
        "http://bdlaws.minlaw.gov.bd/act-details-950.html",
        "http://bdlaws.minlaw.gov.bd/act-details-1106.html"
    ]
    
    session = requests.Session()
    
    for url in known_pages:
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find title
                title = "Unknown"
                bg_act_section = soup.find('section', class_='bg-act-section')
                if bg_act_section:
                    h3_elem = bg_act_section.find('h3')
                    if h3_elem:
                        title = h3_elem.get_text().strip()
                
                print(f"✅ {url}")
                print(f"   Title: {title}")
                
                # Check for navigation or related links
                nav_links = soup.find_all('a', href=True)
                details_in_nav = [link['href'] for link in nav_links if '-details-' in link['href']]
                
                if details_in_nav:
                    print(f"   🔗 Related details links: {len(details_in_nav)}")
                    for link in details_in_nav[:3]:
                        print(f"      - {link}")
            else:
                print(f"❌ {url}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {e}")

if __name__ == "__main__":
    print("🔧 DEBUGGING Bangladesh Laws Website Structure")
    print("=" * 60)
    
    # Debug main index pages
    debug_website_structure()
    
    # Test known pages
    test_known_details_pages()
    
    print(f"\n💡 Analysis complete!")
    print(f"This will help us understand why the crawler isn't finding details pages.")