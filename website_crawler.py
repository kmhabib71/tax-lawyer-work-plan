#!/usr/bin/env python3
"""
Proper Website Crawler for Bangladesh Laws
Discovers URLs by following actual website links
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import json
from collections import deque
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BDLawsWebCrawler:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.visited_urls = set()
        self.details_urls = set()
        self.queue = deque()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_same_domain(self, url):
        """Check if URL belongs to the same domain"""
        return urlparse(url).netloc == urlparse(self.base_url).netloc
    
    def is_details_page(self, url):
        """Check if URL is a details page"""
        details_patterns = ['-details-', 'act-details', 'rules-details', 'ordinance-details']
        return any(pattern in url for pattern in details_patterns)
    
    def should_crawl(self, url):
        """Determine if we should crawl this URL"""
        # Skip if already visited
        if url in self.visited_urls:
            return False
        
        # Only crawl same domain
        if not self.is_same_domain(url):
            return False
        
        # Skip certain file types
        skip_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.gif']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Crawl list pages and details pages
        crawl_patterns = [
            'act-list', 'rules-list', 'ordinance-list', 
            '-details-', 'index', '/', 'home'
        ]
        return any(pattern in url for pattern in crawl_patterns)
    
    def extract_links(self, soup, current_url):
        """Extract all relevant links from a page"""
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            # Clean URL (remove fragments and query params for crawling)
            clean_url = full_url.split('#')[0].split('?')[0]
            
            if self.should_crawl(clean_url):
                links.add(clean_url)
                
                # If it's a details page, add to our collection
                if self.is_details_page(clean_url):
                    self.details_urls.add(clean_url)
        
        return links
    
    def crawl_page(self, url):
        """Crawl a single page and extract links"""
        try:
            logger.info(f"Crawling: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            new_links = self.extract_links(soup, url)
            
            # Add new links to queue
            for link in new_links:
                if link not in self.visited_urls:
                    self.queue.append(link)
            
            logger.info(f"Found {len(new_links)} links, {len(self.details_urls)} details pages so far")
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
    
    def discover_urls(self, max_pages=500, start_urls=None):
        """Main crawling method to discover all URLs"""
        # Start with known entry points
        if start_urls is None:
            start_urls = [
                f"{self.base_url}/",
                f"{self.base_url}/act-list.php",
                f"{self.base_url}/rules-list.php", 
                f"{self.base_url}/ordinance-list.php",
                # Add pagination if exists
                f"{self.base_url}/act-list.php?page=1",
                f"{self.base_url}/act-list.php?page=2",
                f"{self.base_url}/rules-list.php?page=1",
                f"{self.base_url}/ordinance-list.php?page=1",
            ]
        
        # Add start URLs to queue
        for url in start_urls:
            self.queue.append(url)
        
        pages_crawled = 0
        
        while self.queue and pages_crawled < max_pages:
            current_url = self.queue.popleft()
            
            if current_url in self.visited_urls:
                continue
            
            self.visited_urls.add(current_url)
            self.crawl_page(current_url)
            
            pages_crawled += 1
            
            # Be nice to the server
            time.sleep(1)
            
            if pages_crawled % 10 == 0:
                logger.info(f"Progress: {pages_crawled}/{max_pages} pages, {len(self.details_urls)} details pages found")
        
        return self.details_urls
    
    def check_pagination(self, soup):
        """Look for pagination links"""
        pagination_links = []
        
        # Common pagination patterns
        pagination_selectors = [
            'a[href*="page="]',
            'a[href*="p="]', 
            '.pagination a',
            '.pager a',
            'a:contains("Next")',
            'a:contains(">")',
            'a:contains("আরো")'  # Bengali "more"
        ]
        
        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    pagination_links.append(href)
        
        return pagination_links
    
    def save_results(self, filename="discovered_details_urls.txt"):
        """Save discovered URLs to file"""
        # Sort URLs for better organization
        sorted_urls = sorted(list(self.details_urls))
        
        with open(filename, 'w', encoding='utf-8') as f:
            for url in sorted_urls:
                f.write(f"{url}\n")
        
        # Also save detailed results as JSON
        results = {
            'total_details_pages': len(self.details_urls),
            'total_pages_crawled': len(self.visited_urls),
            'details_urls': sorted_urls,
            'crawl_summary': {
                'act_pages': len([u for u in sorted_urls if 'act-details' in u]),
                'rules_pages': len([u for u in sorted_urls if 'rules-details' in u]),
                'ordinance_pages': len([u for u in sorted_urls if 'ordinance-details' in u])
            }
        }
        
        with open(f"crawl_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return sorted_urls

def main():
    print("🕷️  Bangladesh Laws Website Crawler")
    print("=" * 50)
    print("🎯 Goal: Discover ALL details pages by following actual website links")
    print("🔍 Method: Systematic crawling of list pages and navigation")
    print("=" * 50)
    
    crawler = BDLawsWebCrawler()
    
    try:
        # Discover all URLs
        details_urls = crawler.discover_urls(max_pages=500)
        
        print(f"\n✅ Crawling Complete!")
        print(f"📊 Results:")
        print(f"   🔗 Total pages crawled: {len(crawler.visited_urls)}")
        print(f"   📋 Details pages found: {len(details_urls)}")
        
        # Save results
        saved_urls = crawler.save_results()
        
        print(f"💾 Files created:")
        print(f"   📄 discovered_details_urls.txt ({len(saved_urls)} URLs)")
        print(f"   📊 crawl_results.json (detailed analysis)")
        
        # Show breakdown
        act_count = len([u for u in saved_urls if 'act-details' in u])
        rules_count = len([u for u in saved_urls if 'rules-details' in u])
        ordinance_count = len([u for u in saved_urls if 'ordinance-details' in u])
        
        print(f"\n📈 Breakdown:")
        print(f"   ⚖️  Act details: {act_count}")
        print(f"   📜 Rules details: {rules_count}")
        print(f"   📋 Ordinance details: {ordinance_count}")
        
        print(f"\n🚀 Next steps:")
        print(f"   python run_scraper.py --use-discovered-urls")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Crawling stopped by user")
        print(f"📊 Partial results: {len(crawler.details_urls)} details pages found")
        crawler.save_results("partial_discovered_urls.txt")

if __name__ == "__main__":
    main()