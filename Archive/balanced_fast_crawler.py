#!/usr/bin/env python3
"""
BALANCED FAST Crawler - Optimized but server-friendly
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

class BalancedFastCrawler:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.details_urls = set()
        
        # Optimized but respectful session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_numbers_from_index(self, soup):
        """Extract numbers from index pages"""
        html_content = str(soup)
        
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
    
    def test_details_url_balanced(self, url):
        """Balanced URL testing - GET but with short timeout"""
        try:
            response = self.session.get(url, timeout=8)  # Reasonable timeout
            if response.status_code == 200:
                # Quick content check
                if len(response.text) > 5000 or 'bg-act-section' in response.text:
                    return True
            return False
        except:
            return False
    
    def generate_details_urls(self, numbers):
        """Generate details URLs from extracted numbers"""
        urls = []
        
        for doc_type, nums in numbers.items():
            for num in nums:
                url = f"{self.base_url}/{doc_type}-details-{num}.html"
                urls.append(url)
        
        return urls
    
    def balanced_discovery(self, max_workers=8):
        """Balanced speed discovery"""
        print("⚡ BALANCED FAST MODE: Optimized speed with reliability")
        
        # Extract numbers from index pages
        index_pages = [
            f"{self.base_url}/laws-of-bangladesh-alphabetical-index.html",
            f"{self.base_url}/laws-of-bangladesh-chronological-index.html"
        ]
        
        all_numbers = {'act': set(), 'rules': set(), 'ordinance': set()}
        
        for index_url in index_pages:
            print(f"🔍 Extracting numbers from: {index_url}")
            try:
                response = self.session.get(index_url, timeout=20)
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
        
        # Generate candidate URLs
        candidate_urls = self.generate_details_urls(all_numbers)
        total_candidates = len(candidate_urls)
        print(f"🎯 Testing {total_candidates} candidate URLs...")
        
        # Balanced parallel testing
        batch_size = 40  # Smaller batches, more manageable
        total_batches = (total_candidates + batch_size - 1) // batch_size
        
        for i in range(0, total_candidates, batch_size):
            batch = candidate_urls[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"⚡ Batch {batch_num}/{total_batches}: Testing {len(batch)} URLs with {max_workers} workers...")
            
            # Parallel testing with reasonable limits
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(self.test_details_url_balanced, url): url 
                    for url in batch
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        if future.result():  # URL works
                            self.details_urls.add(url)
                    except Exception as e:
                        logger.debug(f"Error testing {url}: {e}")
            
            print(f"   ✅ Found {len(self.details_urls)} working URLs so far")
            
            # Respectful delay
            time.sleep(0.3)
        
        return sorted(list(self.details_urls))
    
    def save_results(self, filename="balanced_fast_urls.txt"):
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
        
        with open("balanced_fast_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return sorted_urls, summary

def main():
    print("⚡ BALANCED FAST Bangladesh Laws Crawler ⚡")
    print("=" * 50)
    print("🎯 8 parallel workers (server-friendly)")
    print("✅ GET requests with content validation")
    print("📦 40 URLs per batch")
    print("⏱️  Respectful delays")
    print("=" * 50)
    
    crawler = BalancedFastCrawler()
    
    start_time = time.time()
    
    try:
        details_urls = crawler.balanced_discovery(max_workers=8)
        urls, summary = crawler.save_results()
        
        elapsed = time.time() - start_time
        
        print(f"\n⚡ BALANCED FAST Complete! ({elapsed:.1f}s)")
        print(f"📊 Results:")
        print(f"   📋 Working details pages: {summary['total_found']}")
        print(f"   ⚖️  Acts: {summary['act_pages']}")
        print(f"   📜 Rules: {summary['rules_pages']}")
        print(f"   📋 Ordinances: {summary['ordinance_pages']}")
        if elapsed > 0:
            print(f"   ⚡ Speed: {summary['total_found']/elapsed:.1f} URLs/second")
        
        print(f"\n💾 Files created:")
        print(f"   📄 balanced_fast_urls.txt")
        print(f"   📊 balanced_fast_summary.json")
        
        print(f"\n🚀 Ready to scrape:")
        print(f"   python run_scraper.py --use-balanced-urls")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped by user")
        urls, summary = crawler.save_results("partial_balanced.txt")
        print(f"📊 Partial: {summary['total_found']} details pages")

if __name__ == "__main__":
    main()