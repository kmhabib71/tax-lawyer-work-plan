#!/usr/bin/env python3
"""
Analyze the HTML structure of Bangladesh Laws to understand formatting
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_document_structure(url):
    """Analyze the HTML structure of a legal document"""
    
    print(f"🔍 Analyzing: {url}")
    print("=" * 80)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find main content area
        content_area = soup.find('section', class_='bg-act-section')
        if not content_area:
            content_area = soup.find('div', class_='main-content') or soup.find('main') or soup
        
        print("📋 DOCUMENT STRUCTURE ANALYSIS")
        print("=" * 50)
        
        # Extract title
        title_elem = content_area.find('h3') if content_area else soup.find('h3')
        if title_elem:
            title = title_elem.get_text().strip()
            print(f"📖 Title: {title}")
        
        print(f"\n🏗️  HTML STRUCTURE:")
        print(f"Content area tag: {content_area.name if content_area else 'Not found'}")
        print(f"Content area class: {content_area.get('class') if content_area else 'None'}")
        
        # Analyze all elements in content area
        if content_area:
            elements = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'strong', 'b'])
            
            print(f"\n📊 CONTENT ELEMENTS ({len(elements)} total):")
            
            structure_patterns = {}
            
            for i, elem in enumerate(elements[:30]):  # First 30 elements
                text = elem.get_text().strip()
                if len(text) > 100:
                    text = text[:100] + "..."
                
                # Analyze patterns
                classes = elem.get('class', [])
                class_str = ' '.join(classes) if classes else 'no-class'
                
                # Check for structural indicators
                indicators = []
                if re.match(r'^\d+\.', text):
                    indicators.append('NUMBERED')
                if any(word in text for word in ['অধ্যায়', 'chapter']):
                    indicators.append('CHAPTER')
                if any(word in text for word in ['ধারা', 'section']):
                    indicators.append('SECTION')
                if any(word in text for word in ['উপ-ধারা', 'subsection']):
                    indicators.append('SUBSECTION')
                if any(word in text for word in ['দফা', 'clause']):
                    indicators.append('CLAUSE')
                if any(word in text for word in ['উপ-দফা', 'subclause']):
                    indicators.append('SUBCLAUSE')
                if any(word in text for word in ['অনুচ্ছেদ', 'article']):
                    indicators.append('ARTICLE')
                
                indicator_str = ', '.join(indicators) if indicators else 'CONTENT'
                
                print(f"{i+1:2d}. [{elem.name}] [{class_str}] [{indicator_str}]")
                print(f"    {text}")
                
                # Track patterns
                pattern_key = f"{elem.name}_{class_str}_{indicator_str}"
                structure_patterns[pattern_key] = structure_patterns.get(pattern_key, 0) + 1
            
            print(f"\n📈 STRUCTURE PATTERNS:")
            for pattern, count in sorted(structure_patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"   {pattern}: {count} times")
        
        # Analyze footnotes
        footnotes = soup.find_all('a', class_='tooltip')
        print(f"\n📝 FOOTNOTES ({len(footnotes)} found):")
        
        for i, footnote in enumerate(footnotes[:5]):  # First 5 footnotes
            text = footnote.get_text().strip()
            tooltip = footnote.get('title', footnote.get('data-original-title', ''))
            print(f"{i+1}. Text: '{text}' | Tooltip: '{tooltip[:100]}...'")
        
        # Look for specific structural elements
        print(f"\n🔍 SPECIFIC ELEMENTS:")
        
        # Check for different heading levels
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            if headings:
                print(f"   H{level} headings: {len(headings)}")
                for h in headings[:3]:
                    print(f"      - {h.get_text().strip()[:50]}...")
        
        # Check for lists
        lists = soup.find_all(['ul', 'ol'])
        if lists:
            print(f"   Lists: {len(lists)}")
        
        # Check for tables
        tables = soup.find_all('table')
        if tables:
            print(f"   Tables: {len(tables)}")
        
        # Check for divs with specific classes
        special_divs = soup.find_all('div', class_=True)
        div_classes = {}
        for div in special_divs:
            classes = ' '.join(div.get('class', []))
            div_classes[classes] = div_classes.get(classes, 0) + 1
        
        if div_classes:
            print(f"   Div classes:")
            for class_name, count in sorted(div_classes.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"      {class_name}: {count}")
        
        return soup, content_area
        
    except Exception as e:
        print(f"❌ Error analyzing {url}: {e}")
        return None, None

def main():
    # Analyze the specific URL provided
    url = "http://bdlaws.minlaw.gov.bd/act-details-1541.html"
    soup, content_area = analyze_document_structure(url)
    
    if soup:
        print(f"\n💾 Analysis complete!")
        print(f"📄 Use this analysis to build a structured scraper")
        
        # Save raw HTML for inspection
        with open('sample_document.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        print(f"💾 Raw HTML saved to: sample_document.html")

if __name__ == "__main__":
    main()