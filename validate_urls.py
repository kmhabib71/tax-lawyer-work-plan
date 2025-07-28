#!/usr/bin/env python3
"""
Validate URLs to check if they contain real legal content
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class URLValidator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.valid_urls = []
        self.invalid_urls = []
        self.empty_urls = []
    
    def validate_single_url(self, url):
        """Validate if a URL contains real legal content"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return {'url': url, 'status': 'http_error', 'code': response.status_code}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content_text = soup.get_text().strip()
            
            # Check for real content indicators
            content_indicators = [
                'bg-act-section',           # Main content section
                'আইন',                     # Bengali for "law"
                'অধ্যাদেশ',                 # Bengali for "ordinance" 
                'বিধিমালা',                 # Bengali for "rules"
                'ধারা',                     # Bengali for "section"
                'অনুচ্ছেদ',                 # Bengali for "article"
                'section',
                'article',
                'whereas',                   # Common in legal preambles
                'be it enacted',
                'be it resolved'
            ]
            
            # Check for error/empty page indicators
            error_indicators = [
                'page not found',
                '404',
                'error',
                'not available',
                'under construction',
                'coming soon'
            ]
            
            content_lower = content_text.lower()
            
            # Check for errors first
            if any(error in content_lower for error in error_indicators):
                return {'url': url, 'status': 'error_page', 'length': len(content_text)}
            
            # Check content length
            if len(content_text) < 500:  # Too short to be a real legal document
                return {'url': url, 'status': 'too_short', 'length': len(content_text)}
            
            # Check for legal content indicators
            indicator_count = sum(1 for indicator in content_indicators if indicator in content_lower)
            
            if indicator_count >= 2:  # At least 2 legal indicators
                # Try to extract title
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
                    'status': 'valid', 
                    'title': title,
                    'length': len(content_text),
                    'footnotes': len(footnotes),
                    'indicators': indicator_count
                }
            else:
                return {'url': url, 'status': 'no_legal_content', 'length': len(content_text), 'indicators': indicator_count}
                
        except Exception as e:
            return {'url': url, 'status': 'exception', 'error': str(e)}
    
    def validate_urls_from_file(self, filename, max_workers=8, sample_size=None):
        """Validate URLs from a file"""
        
        # Load URLs
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            return
        
        print(f"📋 Loaded {len(urls)} URLs from {filename}")
        
        # Sample for testing if requested
        if sample_size and sample_size < len(urls):
            import random
            urls = random.sample(urls, sample_size)
            print(f"🎯 Testing sample of {len(urls)} URLs")
        
        # Categorize URLs
        acts_urls = [u for u in urls if 'act-details' in u]
        rules_urls = [u for u in urls if 'rules-details' in u]
        ordinance_urls = [u for u in urls if 'ordinance-details' in u]
        
        print(f"📊 URL breakdown:")
        print(f"   ⚖️  Acts: {len(acts_urls)}")
        print(f"   📜 Rules: {len(rules_urls)}")
        print(f"   📋 Ordinances: {len(ordinance_urls)}")
        
        print(f"\n🔍 Validating content...")
        
        results = []
        batch_size = 50
        total_batches = (len(urls) + batch_size - 1) // batch_size
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"🔄 Batch {batch_num}/{total_batches}: Validating {len(batch)} URLs...")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(self.validate_single_url, url): url 
                    for url in batch
                }
                
                for future in as_completed(future_to_url):
                    result = future.result()
                    results.append(result)
                    
                    if result['status'] == 'valid':
                        self.valid_urls.append(result)
                        print(f"   ✅ VALID: {result['title'][:50]}...")
                    elif result['status'] in ['too_short', 'no_legal_content', 'error_page']:
                        self.invalid_urls.append(result)
                        print(f"   ❌ INVALID: {result['url']} ({result['status']})")
                    else:
                        self.empty_urls.append(result)
            
            time.sleep(0.5)  # Small delay between batches
        
        return results
    
    def save_validation_results(self, results):
        """Save validation results"""
        
        # Save valid URLs only
        valid_urls_list = [r['url'] for r in results if r['status'] == 'valid']
        
        with open('validated_legal_urls.txt', 'w', encoding='utf-8') as f:
            for url in valid_urls_list:
                f.write(f"{url}\n")
        
        # Save detailed analysis
        validation_summary = {
            'total_tested': len(results),
            'valid_urls': len([r for r in results if r['status'] == 'valid']),
            'invalid_urls': len([r for r in results if r['status'] in ['too_short', 'no_legal_content', 'error_page']]),
            'error_urls': len([r for r in results if r['status'] in ['http_error', 'exception']]),
            'validation_details': results,
            'valid_breakdown': {
                'acts': len([r for r in results if r['status'] == 'valid' and 'act-details' in r['url']]),
                'rules': len([r for r in results if r['status'] == 'valid' and 'rules-details' in r['url']]),
                'ordinances': len([r for r in results if r['status'] == 'valid' and 'ordinance-details' in r['url']])
            }
        }
        
        with open('validation_results.json', 'w', encoding='utf-8') as f:
            json.dump(validation_summary, f, indent=2, ensure_ascii=False)
        
        return validation_summary

def main():
    print("🔍 URL Content Validator")
    print("=" * 40)
    print("✅ Validates if URLs contain real legal content")
    print("❌ Filters out empty/fake pages")
    print("=" * 40)
    
    validator = URLValidator()
    
    # Test complete URLs file
    filename = 'complete_legal_urls.txt'
    
    # First, test a small sample to see the pattern
    print("🧪 Testing sample of 20 URLs to check pattern...")
    sample_results = validator.validate_urls_from_file(filename, sample_size=20)
    
    if sample_results:
        sample_valid = len([r for r in sample_results if r['status'] == 'valid'])
        sample_total = len(sample_results)
        validity_rate = (sample_valid / sample_total) * 100
        
        print(f"\n📊 Sample Results:")
        print(f"   ✅ Valid: {sample_valid}/{sample_total} ({validity_rate:.1f}%)")
        
        if validity_rate > 50:
            # High validity rate, continue with full validation
            print(f"\n🚀 Good validity rate! Running full validation...")
            full_results = validator.validate_urls_from_file(filename)
            summary = validator.save_validation_results(full_results)
            
            print(f"\n🎉 Validation Complete!")
            print(f"📊 Final Results:")
            print(f"   📋 Total tested: {summary['total_tested']}")
            print(f"   ✅ Valid URLs: {summary['valid_urls']}")
            print(f"   ❌ Invalid URLs: {summary['invalid_urls']}")
            print(f"   🔗 Error URLs: {summary['error_urls']}")
            print(f"\n📈 Valid Breakdown:")
            print(f"   ⚖️  Acts: {summary['valid_breakdown']['acts']}")
            print(f"   📜 Rules: {summary['valid_breakdown']['rules']}")
            print(f"   📋 Ordinances: {summary['valid_breakdown']['ordinances']}")
            
            print(f"\n💾 Files created:")
            print(f"   📄 validated_legal_urls.txt ({summary['valid_urls']} URLs)")
            print(f"   📊 validation_results.json")
            
            if summary['valid_urls'] > 0:
                print(f"\n🚀 Ready to scrape validated URLs:")
                print(f"   python resume_scraper.py --urls-file validated_legal_urls.txt --session-name validated")
        else:
            print(f"\n⚠️  Low validity rate ({validity_rate:.1f}%). Many URLs may be fake.")
            print(f"💡 Recommendation: Use only Acts URLs which are proven to work:")
            print(f"   python resume_scraper.py --urls-file smart_discovered_urls.txt --session-name acts_only")

if __name__ == "__main__":
    main()