#!/usr/bin/env python3
"""
Selective Tax Law Scraper - Choose specific documents with structured preservation
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin
import os
from datetime import datetime

class TaxLawSelector:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Tax-related keywords (English and Bengali)
        self.tax_keywords = [
            # English keywords
            'income tax', 'vat', 'value added tax', 'customs', 'duty', 'tariff',
            'revenue', 'tax administration', 'tax collection', 'excise',
            'withholding tax', 'advance tax', 'supplementary duty',
            'import duty', 'export duty', 'tax exemption', 'tax holiday',
            'finance', 'budget', 'fiscal', 'taxation', 'levy',
            
            # Bengali keywords
            'কর', 'আয়কর', 'মূল্য সংযোজন কর', 'শুল্ক', 'রাজস্ব',
            'অর্থ', 'বাজেট', 'আর্থিক', 'কর আদায়', 'কর প্রশাসন',
            'সম্পূরক শুল্ক', 'আমদানি শুল্ক', 'রপ্তানি শুল্ক'
        ]
    
    def scan_for_tax_laws(self, urls_file='smart_discovered_urls.txt'):
        """Scan URLs to identify tax-related laws"""
        
        print("🔍 Scanning for Tax-Related Laws...")
        print("=" * 50)
        
        # Load URLs
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ File not found: {urls_file}")
            return []
        
        tax_candidates = []
        
        print(f"📋 Scanning {len(urls)} URLs for tax relevance...")
        
        for i, url in enumerate(urls, 1):
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title
                    title = "Unknown"
                    bg_act_section = soup.find('section', class_='bg-act-section')
                    if bg_act_section:
                        h3_elem = bg_act_section.find('h3')
                        if h3_elem:
                            title = h3_elem.get_text().strip()
                    
                    # Check for tax keywords
                    full_text = soup.get_text().lower()
                    title_lower = title.lower()
                    
                    # Calculate relevance score
                    relevance_score = 0
                    matched_keywords = []
                    
                    for keyword in self.tax_keywords:
                        if keyword in title_lower:
                            relevance_score += 3  # Title matches are more important
                            matched_keywords.append(keyword)
                        elif keyword in full_text:
                            relevance_score += 1
                            matched_keywords.append(keyword)
                    
                    # If relevant, add to candidates
                    if relevance_score >= 2:  # Minimum relevance threshold
                        
                        # Get content preview
                        content_preview = soup.get_text()[:500].strip()
                        
                        # Count footnotes
                        footnotes = soup.find_all('a', class_='tooltip')
                        
                        candidate = {
                            'url': url,
                            'title': title,
                            'relevance_score': relevance_score,
                            'matched_keywords': list(set(matched_keywords)),
                            'content_preview': content_preview,
                            'footnotes_count': len(footnotes),
                            'content_length': len(soup.get_text())
                        }
                        
                        tax_candidates.append(candidate)
                        
                        print(f"✅ [{i}/{len(urls)}] FOUND: {title}")
                        print(f"    Score: {relevance_score}, Keywords: {matched_keywords[:3]}")
                    else:
                        print(f"⏭️  [{i}/{len(urls)}] Skip: {title[:50]}...")
                
            except Exception as e:
                print(f"❌ [{i}/{len(urls)}] Error: {url}")
            
            # Progress update
            if i % 50 == 0:
                print(f"📊 Progress: {i}/{len(urls)} scanned, {len(tax_candidates)} tax laws found")
        
        # Sort by relevance
        tax_candidates.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"\n🎯 Tax Law Discovery Complete!")
        print(f"📊 Found {len(tax_candidates)} tax-related laws")
        
        return tax_candidates
    
    def display_tax_laws_menu(self, tax_candidates):
        """Display interactive menu for law selection"""
        
        print(f"\n📋 Tax Laws Found (Top 20):")
        print("=" * 80)
        
        for i, candidate in enumerate(tax_candidates[:20], 1):
            print(f"{i:2d}. {candidate['title']}")
            print(f"    📊 Score: {candidate['relevance_score']} | 📝 Footnotes: {candidate['footnotes_count']} | 🔗 {candidate['url']}")
            print(f"    🏷️  Keywords: {', '.join(candidate['matched_keywords'][:5])}")
            print(f"    📄 Preview: {candidate['content_preview'][:100]}...")
            print()
        
        if len(tax_candidates) > 20:
            print(f"... and {len(tax_candidates) - 20} more")
        
        return tax_candidates
    
    def save_tax_laws_list(self, tax_candidates, filename='tax_laws_candidates.json'):
        """Save tax laws list for selection"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tax_candidates, f, indent=2, ensure_ascii=False)
        
        # Also create a simple URLs file for top candidates
        top_urls = [candidate['url'] for candidate in tax_candidates[:50]]  # Top 50
        
        with open('top_tax_urls.txt', 'w', encoding='utf-8') as f:
            for url in top_urls:
                f.write(f"{url}\n")
        
        print(f"💾 Saved {len(tax_candidates)} tax law candidates to {filename}")
        print(f"📄 Saved top {len(top_urls)} URLs to top_tax_urls.txt")
        
        return filename

class StructuredTaxScraper:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_structured_content(self, soup):
        """Extract content while preserving legal structure"""
        
        structured_content = {
            'sections': [],
            'chapters': [],
            'subsections': [],
            'footnotes': [],
            'raw_content': ''
        }
        
        # Find main content area
        content_area = soup.find('section', class_='bg-act-section')
        if not content_area:
            content_area = soup.find('div', class_='main-content') or soup.find('main') or soup
        
        # Extract structured elements
        current_section = None
        current_chapter = None
        
        for element in content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'div']):
            text = element.get_text().strip()
            if not text:
                continue
            
            # Detect chapters (অধ্যায়)
            if any(keyword in text for keyword in ['অধ্যায়', 'chapter', 'CHAPTER']):
                current_chapter = {
                    'title': text,
                    'sections': [],
                    'html': str(element)
                }
                structured_content['chapters'].append(current_chapter)
            
            # Detect sections (ধারা)
            elif any(keyword in text for keyword in ['ধারা', 'section', 'SECTION']) or re.match(r'^\d+\.', text):
                current_section = {
                    'title': text,
                    'content': [],
                    'subsections': [],
                    'html': str(element)
                }
                structured_content['sections'].append(current_section)
                if current_chapter:
                    current_chapter['sections'].append(current_section)
            
            # Regular content
            else:
                if current_section:
                    current_section['content'].append({
                        'text': text,
                        'html': str(element)
                    })
        
        # Extract footnotes with structure
        for footnote in soup.find_all('a', class_='tooltip'):
            footnote_data = {
                'text': footnote.get_text().strip(),
                'tooltip': footnote.get('title', ''),
                'html': str(footnote),
                'position': len(structured_content['footnotes'])
            }
            structured_content['footnotes'].append(footnote_data)
        
        # Get raw content for fallback
        structured_content['raw_content'] = content_area.get_text() if content_area else soup.get_text()
        
        return structured_content
    
    def scrape_selected_laws(self, selected_urls, output_dir='structured_tax_laws'):
        """Scrape selected laws with structure preservation"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        scraped_documents = []
        
        for i, url in enumerate(selected_urls, 1):
            print(f"\n🔄 [{i}/{len(selected_urls)}] Scraping: {url}")
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = "Unknown"
                bg_act_section = soup.find('section', class_='bg-act-section')
                if bg_act_section:
                    h3_elem = bg_act_section.find('h3')
                    if h3_elem:
                        title = h3_elem.get_text().strip()
                
                # Extract structured content
                structured_content = self.extract_structured_content(soup)
                
                # Create document object
                document = {
                    'url': url,
                    'title': title,
                    'scraped_at': datetime.now().isoformat(),
                    'structured_content': structured_content,
                    'raw_html': str(soup)
                }
                
                # Create clean filename
                clean_title = re.sub(r'[^\w\s-]', '', title).strip()
                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                filename = f"{clean_title}.json"
                
                # Save structured document
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(document, f, indent=2, ensure_ascii=False)
                
                scraped_documents.append(document)
                
                print(f"✅ Saved: {title}")
                print(f"   📊 Chapters: {len(structured_content['chapters'])}")
                print(f"   📋 Sections: {len(structured_content['sections'])}")
                print(f"   📝 Footnotes: {len(structured_content['footnotes'])}")
                
            except Exception as e:
                print(f"❌ Error scraping {url}: {e}")
        
        # Save summary
        summary = {
            'total_documents': len(scraped_documents),
            'scraped_at': datetime.now().isoformat(),
            'documents': [{'title': doc['title'], 'url': doc['url']} for doc in scraped_documents]
        }
        
        with open(os.path.join(output_dir, 'scraping_summary.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 Structured scraping complete!")
        print(f"📊 {len(scraped_documents)} documents saved to {output_dir}/")
        
        return scraped_documents

def main():
    print("🎯 SELECTIVE TAX LAW SCRAPER")
    print("=" * 50)
    print("🔍 Step 1: Identify tax-related laws")
    print("📋 Step 2: Choose specific documents")  
    print("🏗️  Step 3: Scrape with structure preservation")
    print("=" * 50)
    
    # Step 1: Scan for tax laws
    selector = TaxLawSelector()
    tax_candidates = selector.scan_for_tax_laws()
    
    if not tax_candidates:
        print("❌ No tax-related laws found!")
        return
    
    # Step 2: Display and save candidates
    selector.display_tax_laws_menu(tax_candidates)
    candidates_file = selector.save_tax_laws_list(tax_candidates)
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Review tax_laws_candidates.json to see all candidates")
    print(f"2. Edit top_tax_urls.txt to select specific URLs you want")
    print(f"3. Run structured scraping:")
    print(f"   python selective_tax_scraper.py --scrape-selected")
    
    # Optional: Immediate scraping of top candidates
    response = input(f"\n❓ Scrape top 10 tax laws now? (y/n): ").lower()
    if response == 'y':
        top_10_urls = [candidate['url'] for candidate in tax_candidates[:10]]
        
        scraper = StructuredTaxScraper()
        scraper.scrape_selected_laws(top_10_urls)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--scrape-selected':
        # Scrape from selected URLs file
        try:
            with open('top_tax_urls.txt', 'r', encoding='utf-8') as f:
                selected_urls = [line.strip() for line in f if line.strip()]
            
            scraper = StructuredTaxScraper()
            scraper.scrape_selected_laws(selected_urls)
        except FileNotFoundError:
            print("❌ top_tax_urls.txt not found. Run without --scrape-selected first.")
    else:
        main()