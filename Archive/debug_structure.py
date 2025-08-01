#!/usr/bin/env python3
"""
Debug script to understand why structure detection is failing
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_document_structure(url):
    """Debug why the structure detection is failing"""
    
    print(f"🔍 Debugging: {url}")
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
        
        print(f"📋 Content area found: {content_area.name if content_area else 'None'}")
        print(f"Content area class: {content_area.get('class') if content_area else 'None'}")
        
        if content_area:
            # Get all elements
            elements = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'strong', 'b', 'table'])
            
            print(f"\n📊 Found {len(elements)} elements:")
            print("-" * 50)
            
            # Patterns for detection
            patterns = {
                'chapter': [
                    r'(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম|নবম|দশম)\s*অধ্যায়',
                    r'অধ্যায়\s*[-:]?\s*\d+',
                    r'CHAPTER\s+[IVXLCDM]+',
                    r'Chapter\s+\d+',
                ],
                'section': [
                    r'^\d+\.',
                    r'ধারা\s*[-:]?\s*\d+',
                    r'Section\s+\d+',
                ],
                'subsection': [
                    r'^\(\d+\)',
                    r'উপ-ধারা\s*[-:]?\s*\(\d+\)',
                ],
                'clause': [
                    r'^\([^\d\)][^\)]*\)',
                    r'দফা\s*[-:]?\s*\([^\)]+\)',
                ],
                'subclause': [
                    r'^\([ivxlcdm]+\)',
                    r'উপ-দফা\s*[-:]?\s*\([ivxlcdm]+\)',
                ]
            }
            
            def identify_element_type(text):
                text_cleaned = text.strip()
                for element_type, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        if re.search(pattern, text_cleaned, re.IGNORECASE):
                            return element_type
                return 'content'
            
            # Analyze each element
            for i, elem in enumerate(elements[:50]):  # First 50 elements
                text = elem.get_text().strip()
                if not text:
                    continue
                
                if len(text) > 100:
                    display_text = text[:100] + "..."
                else:
                    display_text = text
                
                element_type = identify_element_type(text)
                classes = elem.get('class', [])
                class_str = ' '.join(classes) if classes else 'no-class'
                
                print(f"{i+1:2d}. [{elem.name}] [{class_str}] [{element_type}]")
                print(f"    {display_text}")
                
                # Check for specific patterns
                if 'অধ্যায়' in text:
                    print(f"    *** CHAPTER FOUND: {text}")
                if re.search(r'^\d+\.', text):
                    print(f"    *** SECTION PATTERN: {text}")
                if 'ধারা' in text:
                    print(f"    *** SECTION KEYWORD: {text}")
                if elem.name == 'table':
                    print(f"    *** TABLE FOUND")
                
                print()
            
            # Check for tables specifically
            tables = content_area.find_all('table')
            print(f"\n📊 Tables found: {len(tables)}")
            for i, table in enumerate(tables):
                print(f"Table {i+1}: {len(table.find_all('tr'))} rows")
            
            # Look for footnotes
            footnotes = soup.find_all('a', class_='tooltip')
            print(f"\n📝 Footnotes found: {len(footnotes)}")
            if footnotes:
                for i, fn in enumerate(footnotes[:5]):
                    print(f"Footnote {i+1}: {fn.get_text()}")
        
        return soup, content_area
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def main():
    url = "http://bdlaws.minlaw.gov.bd/act-details-1541.html"
    soup, content_area = debug_document_structure(url)
    
    if soup and content_area:
        # Save the content area HTML for inspection
        with open('debug_content_area.html', 'w', encoding='utf-8') as f:
            f.write(str(content_area.prettify()))
        print(f"\n💾 Content area HTML saved to: debug_content_area.html")

if __name__ == "__main__":
    main()