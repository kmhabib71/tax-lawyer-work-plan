#!/usr/bin/env python3
"""
ULTRA FAST Crawler - Maximum speed optimizations
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraFastCrawler:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.details_urls = set()
        
        # Optimized session with connection pooling
        self.session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(
            pool_connections=50,  # More connections
            pool_maxsize=50,
            max_retries=retry_strategy,
            pool_block=False
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_numbers_from_index(self, soup):
        """Ultra-fast number extraction using regex"""
        html_content = str(soup)
        
        # Extract all numbers from act/rules/ordinance links
        patterns = [
            r'/act-(\d+)\.html',
            r'/rules-(\d+)\.html', 
            r'/ordinance-(\d+)\.html'
        ]
        
        numbers = {'act': set(), 'rules': set(), 'ordinance': set()}
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, html_content)
            doc_type = ['act', 'rules', 'ordinance'][i]
            numbers[doc_type].update(matches)
        
        return numbers
    
    def test_details_url_fast(self, url):
        """Ultra-fast URL testing with minimal checks"""
        try:
            response = self.session.head(url, timeout=5)  # HEAD request is faster
            return response.status_code == 200
        except:
            try:
                # Fallback to GET with very short timeout
                response = self.session.get(url, timeout=3, stream=True)
                return response.status_code == 200
            except:
                return False
    
    def generate_details_urls(self, numbers):
        """Generate all possible details URLs"""
        urls = []
        
        for doc_type, nums in numbers.items():
            for num in nums:
                url = f"{self.base_url}/{doc_type}-details-{num}.html"
                urls.append(url)
        
        return urls
    
    def ultra_fast_discovery(self, max_workers=20):
        """Maximum speed discovery"""
        print("⚡ ULTRA FAST MODE: Maximum parallel processing")
        
        # Step 1: Get numbers from index pages (serial - fast enough)
        index_pages = [
            f"{self.base_url}/laws-of-bangladesh-alphabetical-index.html",
            f"{self.base_url}/laws-of-bangladesh-chronological-index.html"
        ]
        
        all_numbers = {'act': set(), 'rules': set(), 'ordinance': set()}
        
        for index_url in index_pages:
            print(f"🔍 Extracting numbers from: {index_url}")
            try:
                response = self.session.get(index_url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                numbers = self.extract_numbers_from_index(soup)
                for doc_type in all_numbers:
                    all_numbers[doc_type].update(numbers[doc_type])
                
            except Exception as e:
                logger.error(f"Error extracting from {index_url}: {e}")
        
        print(f"📊 Numbers found:")
        print(f"   ⚖️  Acts: {len(all_numbers['act'])}")
        print(f"   📜 Rules: {len(all_numbers['rules'])}")
        print(f"   📋 Ordinances: {len(all_numbers['ordinance'])}")
        
        # Step 2: Generate all possible URLs
        candidate_urls = self.generate_details_urls(all_numbers)
        total_candidates = len(candidate_urls)
        print(f"🎯 Testing {total_candidates} candidate URLs...")
        
        # Step 3: Ultra-fast parallel testing
        batch_size = 100  # Larger batches
        total_batches = (total_candidates + batch_size - 1) // batch_size
        
        for i in range(0, total_candidates, batch_size):
            batch = candidate_urls[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"⚡ Batch {batch_num}/{total_batches}: Testing {len(batch)} URLs with {max_workers} workers...")
            
            # Maximum parallel testing
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(self.test_details_url_fast, url): url 
                    for url in batch
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    if future.result():  # URL works
                        self.details_urls.add(url)
            
            print(f"   ✅ Found {len(self.details_urls)} working URLs so far")
            
            # Minimal delay
            time.sleep(0.1)
        
        return sorted(list(self.details_urls))
    
    def save_results(self, filename="ultra_fast_urls.txt"):
        """Save results"""
        sorted_urls = sorted(list(self.details_urls))
        
        with open(filename, 'w', encoding='utf-8') as f:
            for url in sorted_urls:
                f.write(f"{url}\n")
        
        summary = {
            'total_found': len(sorted_urls),
            'act_pages': len([u for u in sorted_urls if 'act-details' in u]),
            'rules_pages': len([u for u in sorted_urls if 'rules-details' in u]),
            'ordinance_pages': len([u for u in sorted_urls if 'ordinance-details' in u]),
            'sample_urls': sorted_urls[:10]
        }
        
        with open("ultra_fast_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return sorted_urls, summary

def main():
    print("⚡⚡ ULTRA FAST Bangladesh Laws Crawler ⚡⚡")
    print("=" * 55)
    print("🚀 Maximum parallel workers (20)")
    print("⚡ HEAD requests for speed")
    print("📦 Connection pooling")
    print("🎯 Batch processing (100 URLs/batch)")
    print("=" * 55)
    
    crawler = UltraFastCrawler()
    
    start_time = time.time()
    
    try:
        details_urls = crawler.ultra_fast_discovery(max_workers=20)
        urls, summary = crawler.save_results()
        
        elapsed = time.time() - start_time
        
        print(f"\n⚡⚡ ULTRA FAST Complete! ({elapsed:.1f}s) ⚡⚡")
        print(f"📊 Results:")
        print(f"   📋 Working details pages: {summary['total_found']}")
        print(f"   ⚖️  Acts: {summary['act_pages']}")
        print(f"   📜 Rules: {summary['rules_pages']}")
        print(f"   📋 Ordinances: {summary['ordinance_pages']}")
        print(f"   ⚡ Speed: {summary['total_found']/elapsed:.1f} URLs/second")
        
        print(f"\n💾 Files created:")
        print(f"   📄 ultra_fast_urls.txt")
        print(f"   📊 ultra_fast_summary.json")
        
        print(f"\n🚀 Ready to scrape:")
        print(f"   python run_scraper.py --use-ultra-fast-urls")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped by user")
        urls, summary = crawler.save_results("partial_ultra_fast.txt")
        print(f"📊 Partial: {summary['total_found']} details pages")

if __name__ == "__main__":
    main()