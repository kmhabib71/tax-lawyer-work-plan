#!/usr/bin/env python3
"""
Smart Crawler that understands the BD Laws URL patterns
/act-XXXX.html -> /act-details-XXXX.html
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartBDLawsCrawler:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.details_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def convert_to_details_url(self, list_url):
        """Convert list page URL to details page URL"""
        # /act-1539.html -> /act-details-1539.html
        patterns = [
            (r'/act-(\d+)\.html', r'/act-details-\1.html'),
            (r'/rules-(\d+)\.html', r'/rules-details-\1.html'),
            (r'/ordinance-(\d+)\.html', r'/ordinance-details-\1.html'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, list_url):
                details_url = re.sub(pattern, replacement, list_url)
                return urljoin(self.base_url, details_url)
        
        return None
    
    def test_details_url(self, details_url):
        """Test if a details URL actually works"""
        try:
            response = self.session.get(details_url, timeout=15)
            if response.status_code == 200:
                # Quick check if it's a real details page
                if 'bg-act-section' in response.text or len(response.text) > 5000:
                    return True
            return False
        except:
            return False
    
    def extract_list_urls(self, soup, current_url):
        """Extract list page URLs that can be converted to details"""
        list_urls = set()
        
        # Look for patterns like /act-1234.html
        patterns = [r'/act-\d+\.html', r'/rules-\d+\.html', r'/ordinance-\d+\.html']
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            for pattern in patterns:
                if re.search(pattern, href):
                    list_urls.add(full_url)
                    break
        
        return list_urls
    
    def process_list_url_batch(self, list_urls):
        """Process a batch of list URLs to find working details URLs"""
        working_details = []
        
        for list_url in list_urls:
            details_url = self.convert_to_details_url(list_url)
            if details_url and self.test_details_url(details_url):
                working_details.append(details_url)
                self.details_urls.add(details_url)
        
        return working_details
    
    def discover_all_details_urls(self, max_workers=10):
        """Main discovery method"""
        print("🧠 Smart Discovery: Converting list URLs to details URLs")
        
        # Get list URLs from index pages
        index_pages = [
            f"{self.base_url}/laws-of-bangladesh-alphabetical-index.html",
            f"{self.base_url}/laws-of-bangladesh-chronological-index.html"
        ]
        
        all_list_urls = set()
        
        for index_url in index_pages:
            print(f"🔍 Scanning: {index_url}")
            try:
                response = self.session.get(index_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                list_urls = self.extract_list_urls(soup, index_url)
                all_list_urls.update(list_urls)
                
                print(f"   📋 Found {len(list_urls)} list URLs")
            except Exception as e:
                logger.error(f"Error scanning {index_url}: {e}")
        
        print(f"\n📊 Total list URLs found: {len(all_list_urls)}")
        print(f"🔄 Converting to details URLs and testing...")
        
        # Process in batches with parallel testing
        list_urls_list = list(all_list_urls)
        batch_size = 50
        total_batches = (len(list_urls_list) + batch_size - 1) // batch_size
        
        for i in range(0, len(list_urls_list), batch_size):
            batch = list_urls_list[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"🔄 Batch {batch_num}/{total_batches}: Testing {len(batch)} URLs...")
            
            # Test batch in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {}
                
                for list_url in batch:
                    details_url = self.convert_to_details_url(list_url)
                    if details_url:
                        future = executor.submit(self.test_details_url, details_url)
                        future_to_url[future] = details_url
                
                for future in as_completed(future_to_url):
                    details_url = future_to_url[future]
                    if future.result():  # URL works
                        self.details_urls.add(details_url)
            
            print(f"   ✅ Found {len(self.details_urls)} working details URLs so far")
            
            # Small delay between batches
            time.sleep(0.5)
        
        return sorted(list(self.details_urls))
    
    def save_results(self, filename="smart_discovered_urls.txt"):
        """Save discovered URLs"""
        sorted_urls = sorted(list(self.details_urls))
        
        # Save URLs
        with open(filename, 'w', encoding='utf-8') as f:
            for url in sorted_urls:
                f.write(f"{url}\n")
        
        # Create summary
        summary = {
            'total_found': len(sorted_urls),
            'act_pages': len([u for u in sorted_urls if 'act-details' in u]),
            'rules_pages': len([u for u in sorted_urls if 'rules-details' in u]),
            'ordinance_pages': len([u for u in sorted_urls if 'ordinance-details' in u]),
            'sample_urls': sorted_urls[:10]
        }
        
        with open("smart_crawl_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return sorted_urls, summary

def main():
    print("🧠 SMART Bangladesh Laws Crawler")
    print("=" * 45)
    print("🎯 Converts /act-XXXX.html to /act-details-XXXX.html")
    print("✅ Tests each URL to ensure it works")
    print("⚡ Parallel processing for speed")
    print("=" * 45)
    
    crawler = SmartBDLawsCrawler()
    
    start_time = time.time()
    
    try:
        # Smart discovery
        details_urls = crawler.discover_all_details_urls(max_workers=10)
        
        # Save results
        urls, summary = crawler.save_results()
        
        elapsed = time.time() - start_time
        
        print(f"\n🧠 Smart Discovery Complete! ({elapsed:.1f}s)")
        print(f"📊 Results:")
        print(f"   📋 Working details pages: {summary['total_found']}")
        print(f"   ⚖️  Acts: {summary['act_pages']}")
        print(f"   📜 Rules: {summary['rules_pages']}")
        print(f"   📋 Ordinances: {summary['ordinance_pages']}")
        
        print(f"\n💾 Files created:")
        print(f"   📄 smart_discovered_urls.txt")
        print(f"   📊 smart_crawl_summary.json")
        
        print(f"\n🚀 Ready to scrape:")
        print(f"   python run_scraper.py --use-smart-urls")
        
        # Show samples
        print(f"\n📋 Sample URLs found:")
        for url in summary['sample_urls'][:5]:
            print(f"   - {url}")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped by user")
        urls, summary = crawler.save_results("partial_smart_urls.txt")
        print(f"📊 Partial: {summary['total_found']} details pages")

if __name__ == "__main__":
    main()