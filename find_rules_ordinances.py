#!/usr/bin/env python3
"""
Specialized crawler to find Rules and Ordinances
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

class RulesOrdinancesFinder:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.rules_urls = set()
        self.ordinances_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_for_rules_ordinances(self):
        """Search different areas of the website for Rules and Ordinances"""
        
        # Test different potential URLs
        search_urls = [
            f"{self.base_url}/rules-list.php",
            f"{self.base_url}/ordinance-list.php",
            f"{self.base_url}/statutory-rules.php", 
            f"{self.base_url}/subordinate-legislation.php",
            f"{self.base_url}/emergency-ordinances.php",
            f"{self.base_url}/",  # Main page
            f"{self.base_url}/laws-of-bangladesh.html",
        ]
        
        print("🔍 Searching for Rules and Ordinances in different sections...")
        
        for search_url in search_urls:
            print(f"\n📋 Checking: {search_url}")
            try:
                response = self.session.get(search_url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for rules and ordinances patterns
                    rules_found = 0
                    ordinances_found = 0
                    
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(search_url, href)
                        
                        # Rules patterns
                        if any(pattern in href.lower() for pattern in ['rules-', 'rule-']):
                            if 'details' in href or re.search(r'rules?-\d+', href):
                                self.rules_urls.add(full_url)
                                rules_found += 1
                        
                        # Ordinances patterns  
                        if any(pattern in href.lower() for pattern in ['ordinance-', 'ord-']):
                            if 'details' in href or re.search(r'ordinance-\d+', href):
                                self.ordinances_urls.add(full_url)
                                ordinances_found += 1
                    
                    print(f"   📜 Rules found: {rules_found}")
                    print(f"   📋 Ordinances found: {ordinances_found}")
                    
                    # Show some samples
                    if rules_found > 0 or ordinances_found > 0:
                        print(f"   📄 Sample links:")
                        sample_count = 0
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            text = link.get_text().strip()
                            if any(pat in href.lower() for pat in ['rules-', 'ordinance-']) and sample_count < 5:
                                print(f"      {href} -> {text[:50]}")
                                sample_count += 1
                
                else:
                    print(f"   ❌ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            time.sleep(1)  # Be respectful
    
    def test_pattern_ranges(self):
        """Test numerical patterns for rules and ordinances"""
        print(f"\n🔢 Testing numerical patterns...")
        
        # Test some common ranges
        test_ranges = [
            range(1, 51),      # 1-50
            range(100, 151),   # 100-150
            range(500, 551),   # 500-550
        ]
        
        patterns = [
            "rules-details-{}.html",
            "ordinance-details-{}.html",
            "rules-{}.html", 
            "ordinance-{}.html"
        ]
        
        working_urls = []
        
        for pattern in patterns:
            print(f"\n🧪 Testing pattern: {pattern}")
            
            for test_range in test_ranges:
                found_in_range = 0
                
                for num in test_range:
                    test_url = f"{self.base_url}/{pattern.format(num)}"
                    
                    try:
                        response = self.session.head(test_url, timeout=5)
                        if response.status_code == 200:
                            working_urls.append(test_url)
                            found_in_range += 1
                            
                            if 'rules' in pattern:
                                self.rules_urls.add(test_url)
                            else:
                                self.ordinances_urls.add(test_url)
                    except:
                        pass
                
                if found_in_range > 0:
                    print(f"   ✅ Range {test_range.start}-{test_range.stop-1}: {found_in_range} found")
                
                time.sleep(0.5)  # Small delay
        
        return working_urls
    
    def save_results(self):
        """Save found Rules and Ordinances URLs"""
        
        # Combine with existing Acts URLs if available
        all_urls = set()
        
        # Load existing Acts
        try:
            with open('smart_discovered_urls.txt', 'r', encoding='utf-8') as f:
                acts_urls = [line.strip() for line in f if line.strip()]
            all_urls.update(acts_urls)
            print(f"📋 Loaded {len(acts_urls)} existing Acts URLs")
        except FileNotFoundError:
            print("📋 No existing Acts URLs found")
        
        # Add Rules and Ordinances
        all_urls.update(self.rules_urls)
        all_urls.update(self.ordinances_urls)
        
        # Save complete list
        sorted_urls = sorted(list(all_urls))
        
        with open('complete_legal_urls.txt', 'w', encoding='utf-8') as f:
            for url in sorted_urls:
                f.write(f"{url}\n")
        
        # Create summary
        summary = {
            'total_urls': len(sorted_urls),
            'acts': len([u for u in sorted_urls if 'act-details' in u]),
            'rules': len([u for u in sorted_urls if 'rules-details' in u or 'rules-' in u]),
            'ordinances': len([u for u in sorted_urls if 'ordinance-details' in u or 'ordinance-' in u]),
            'rules_urls': sorted(list(self.rules_urls)),
            'ordinances_urls': sorted(list(self.ordinances_urls))
        }
        
        with open('complete_legal_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary

def main():
    print("📜 Rules & Ordinances Finder")
    print("=" * 40)
    print("🎯 Search for secondary legislation")
    print("🔍 Test different URL patterns")
    print("=" * 40)
    
    finder = RulesOrdinancesFinder()
    
    try:
        # Search in different sections
        finder.search_for_rules_ordinances()
        
        # Test numerical patterns
        pattern_results = finder.test_pattern_ranges()
        
        # Save results
        summary = finder.save_results()
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   📋 Total URLs: {summary['total_urls']}")
        print(f"   ⚖️  Acts: {summary['acts']}")
        print(f"   📜 Rules: {summary['rules']}")
        print(f"   📋 Ordinances: {summary['ordinances']}")
        
        print(f"\n💾 Files created:")
        print(f"   📄 complete_legal_urls.txt")
        print(f"   📊 complete_legal_summary.json")
        
        if summary['rules'] > 0 or summary['ordinances'] > 0:
            print(f"\n🚀 Ready to scrape complete database:")
            print(f"   python run_scraper.py --use-complete-urls")
        else:
            print(f"\n📋 Only Acts found - use existing:")
            print(f"   python run_scraper.py --use-smart-urls")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Search stopped by user")

if __name__ == "__main__":
    main()