#!/usr/bin/env python3
"""
Fast Website Crawler for Bangladesh Laws - Optimized Version
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from collections import deque
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FastBDLawsCrawler:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.visited_urls = set()
        self.details_urls = set()
        self.queue = deque()
        self.lock = threading.Lock()
        
        # Create session pool
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_details_page(self, url):
        """Check if URL is a details page"""
        return '-details-' in url
    
    def should_crawl(self, url):
        """Determine if we should crawl this URL - FAST version"""
        # Quick checks first
        if url in self.visited_urls:
            return False
        
        if not url.startswith(self.base_url):
            return False
        
        # Skip non-essential files
        if any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.css', '.js']):
            return False
        
        # FOCUSED CRAWLING - only important pages
        important_patterns = [
            'act-list', 'rules-list', 'ordinance-list',
            '-details-', 'index.html', 'alphabetical', 'chronological'
        ]
        return any(pattern in url for pattern in important_patterns)
    
    def extract_links_fast(self, soup, current_url):
        """Fast link extraction focused on details pages"""
        links = set()
        
        # Focus on specific link patterns that likely lead to details
        selectors = [
            'a[href*="-details-"]',  # Direct details links
            'a[href*="act-"]',       # Act pages  
            'a[href*="rules-"]',     # Rules pages
            'a[href*="ordinance-"]', # Ordinance pages
        ]
        
        for selector in selectors:
            for link in soup.select(selector):
                href = link.get('href')
                if href:
                    full_url = urljoin(current_url, href)
                    clean_url = full_url.split('#')[0].split('?')[0]
                    
                    if clean_url.startswith(self.base_url):
                        links.add(clean_url)
                        
                        # Add details pages immediately
                        if self.is_details_page(clean_url):
                            with self.lock:
                                self.details_urls.add(clean_url)
        
        return links
    
    def crawl_page_fast(self, url):
        """Fast crawl of a single page"""
        try:
            with self.lock:
                if url in self.visited_urls:
                    return set()
                self.visited_urls.add(url)
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            new_links = self.extract_links_fast(soup, url)
            
            logger.info(f"✅ {url} -> {len(new_links)} links, {len(self.details_urls)} details total")
            return new_links
            
        except Exception as e:
            logger.error(f"❌ {url}: {e}")
            return set()
    
    def discover_urls_fast(self, max_workers=5):
        """Fast parallel discovery"""
        print("🚀 Starting FAST discovery mode...")
        
        # Key starting points
        start_urls = [
            f"{self.base_url}/laws-of-bangladesh-alphabetical-index.html",
            f"{self.base_url}/laws-of-bangladesh-chronological-index.html", 
            f"{self.base_url}/",
        ]
        
        # Add to queue
        for url in start_urls:
            self.queue.append(url)
        
        round_num = 1
        
        while self.queue:
            # Get current batch
            current_batch = []
            batch_size = min(20, len(self.queue))  # Process in batches
            
            for _ in range(batch_size):
                if self.queue:
                    current_batch.append(self.queue.popleft())
            
            if not current_batch:
                break
            
            print(f"🔄 Round {round_num}: Processing {len(current_batch)} URLs...")
            
            # Process batch in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(self.crawl_page_fast, url): url 
                    for url in current_batch
                }
                
                for future in as_completed(future_to_url):
                    new_links = future.result()
                    
                    # Add new links to queue (avoid duplicates)
                    for link in new_links:
                        if link not in self.visited_urls and link not in self.queue:
                            if self.should_crawl(link):
                                self.queue.append(link)
            
            print(f"   📊 Found {len(self.details_urls)} details pages so far")
            print(f"   📋 Queue: {len(self.queue)} URLs remaining")
            
            round_num += 1
            
            # Safety limit
            if round_num > 10:
                print("⏹️  Reached round limit")
                break
            
            # Small delay between rounds
            time.sleep(0.5)
        
        return sorted(list(self.details_urls))
    
    def save_results_fast(self, filename="fast_discovered_urls.txt"):
        """Save results quickly"""
        sorted_urls = sorted(list(self.details_urls))
        
        # Save URLs
        with open(filename, 'w', encoding='utf-8') as f:
            for url in sorted_urls:
                f.write(f"{url}\n")
        
        # Quick summary
        summary = {
            'total_found': len(sorted_urls),
            'total_crawled': len(self.visited_urls),
            'act_pages': len([u for u in sorted_urls if 'act-details' in u]),
            'rules_pages': len([u for u in sorted_urls if 'rules-details' in u]),
            'ordinance_pages': len([u for u in sorted_urls if 'ordinance-details' in u])
        }
        
        with open("fast_crawl_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        return sorted_urls, summary

def main():
    print("⚡ FAST Bangladesh Laws Crawler")
    print("=" * 40)
    print("🎯 Optimized for speed and efficiency")
    print("🔍 Parallel processing with focused targeting")
    print("=" * 40)
    
    crawler = FastBDLawsCrawler()
    
    start_time = time.time()
    
    try:
        # Fast discovery
        details_urls = crawler.discover_urls_fast(max_workers=5)
        
        # Save results
        urls, summary = crawler.save_results_fast()
        
        elapsed = time.time() - start_time
        
        print(f"\n⚡ FAST Crawl Complete! ({elapsed:.1f}s)")
        print(f"📊 Results:")
        print(f"   🔗 Pages crawled: {summary['total_crawled']}")
        print(f"   📋 Details pages: {summary['total_found']}")
        print(f"   ⚖️  Acts: {summary['act_pages']}")
        print(f"   📜 Rules: {summary['rules_pages']}")
        print(f"   📋 Ordinances: {summary['ordinance_pages']}")
        
        print(f"\n💾 Files created:")
        print(f"   📄 fast_discovered_urls.txt")
        print(f"   📊 fast_crawl_summary.json")
        
        print(f"\n🚀 Ready to scrape:")
        print(f"   python run_scraper.py --use-fast-urls")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped by user")
        urls, summary = crawler.save_results_fast("partial_fast_urls.txt")
        print(f"📊 Partial: {summary['total_found']} details pages")

if __name__ == "__main__":
    main()