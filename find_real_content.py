#!/usr/bin/env python3
"""
Find the real content area of Bangladesh Laws documents
"""

import requests
from bs4 import BeautifulSoup
import re

def find_real_content_area(url):
    """Find where the actual legal content is located"""
    
    print(f"🔍 Finding real content in: {url}")
    print("=" * 80)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check different potential content areas
        content_candidates = [
            ('bg-act-section', soup.find('section', class_='bg-act-section')),
            ('main-content', soup.find('div', class_='main-content')),
            ('content', soup.find('div', class_='content')),
            ('container', soup.find('div', class_='container')),
            ('body', soup.find('body')),
            ('main', soup.find('main')),
        ]
        
        print("📋 Content area candidates:")
        
        for name, area in content_candidates:
            if area:
                # Count meaningful elements
                meaningful_elements = area.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table'])
                text_content = area.get_text().strip()
                
                print(f"\n🔍 {name}:")
                print(f"   Elements: {len(meaningful_elements)}")
                print(f"   Text length: {len(text_content)}")
                print(f"   Preview: {text_content[:200]}...")
                
                # Look for Bengali legal keywords
                bengali_keywords = ['ধারা', 'অধ্যায়', 'দফা', 'উপ-ধারা', 'অনুচ্ছেদ', 'বিধান', 'আইন']
                keyword_count = sum(1 for keyword in bengali_keywords if keyword in text_content)
                print(f"   Bengali legal keywords: {keyword_count}")
                
                # Look for section numbers
                section_patterns = [r'\d+\.', r'ধারা\s*\d+', r'অধ্যায়\s*\d+']
                section_matches = sum(len(re.findall(pattern, text_content)) for pattern in section_patterns)
                print(f"   Section patterns found: {section_matches}")
                
                # Check for tables
                tables = area.find_all('table')
                print(f"   Tables: {len(tables)}")
                
                # Check for footnotes
                footnotes = area.find_all('a', class_='tooltip')
                print(f"   Footnotes: {len(footnotes)}")
                
                # Score this candidate
                score = (len(meaningful_elements) * 0.1 + 
                        keyword_count * 10 + 
                        section_matches * 5 + 
                        len(tables) * 15 + 
                        len(footnotes) * 2)
                print(f"   📊 Score: {score:.1f}")
        
        # Also check all divs and sections to find content
        print(f"\n🔍 Scanning all sections and divs for content...")
        
        all_sections = soup.find_all(['section', 'div'])
        best_candidates = []
        
        for i, section in enumerate(all_sections):
            text_content = section.get_text().strip()
            if len(text_content) < 1000:  # Skip short sections
                continue
            
            # Count Bengali legal indicators
            bengali_keywords = ['ধারা', 'অধ্যায়', 'দফা', 'উপ-ধারা', 'অনুচ্ছেদ', 'বিধান']
            keyword_count = sum(1 for keyword in bengali_keywords if keyword in text_content)
            
            # Look for section numbers
            section_patterns = [r'\d+\.', r'ধারা\s*\d+']
            section_matches = sum(len(re.findall(pattern, text_content)) for pattern in section_patterns)
            
            tables = section.find_all('table')
            footnotes = section.find_all('a', class_='tooltip')
            
            if keyword_count > 0 or section_matches > 0 or len(tables) > 0 or len(footnotes) > 0:
                score = keyword_count * 10 + section_matches * 5 + len(tables) * 15 + len(footnotes) * 2
                
                classes = section.get('class', [])
                class_str = ' '.join(classes) if classes else 'no-class'
                
                best_candidates.append({
                    'element': section,
                    'tag': section.name,
                    'classes': class_str,
                    'text_length': len(text_content),
                    'keywords': keyword_count,
                    'sections': section_matches,
                    'tables': len(tables),
                    'footnotes': len(footnotes),
                    'score': score,
                    'preview': text_content[:300]
                })
        
        # Sort by score
        best_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n🏆 Best content candidates (top 5):")
        for i, candidate in enumerate(best_candidates[:5]):
            print(f"\n{i+1}. [{candidate['tag']}] [{candidate['classes']}]")
            print(f"   📊 Score: {candidate['score']:.1f}")
            print(f"   📝 Text: {candidate['text_length']} chars")
            print(f"   🔤 Keywords: {candidate['keywords']}")
            print(f"   📋 Sections: {candidate['sections']}")
            print(f"   📊 Tables: {candidate['tables']}")
            print(f"   📝 Footnotes: {candidate['footnotes']}")
            print(f"   📄 Preview: {candidate['preview']}...")
        
        if best_candidates:
            # Save the best candidate
            best_element = best_candidates[0]['element']
            with open('best_content_area.html', 'w', encoding='utf-8') as f:
                f.write(str(best_element.prettify()))
            print(f"\n💾 Best content area saved to: best_content_area.html")
            
            return best_element
        else:
            print(f"❌ No good content candidates found!")
            return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    url = "http://bdlaws.minlaw.gov.bd/act-details-1541.html"
    best_content = find_real_content_area(url)
    
    if best_content:
        print(f"\n✅ Found the real content area!")
        print(f"Tag: {best_content.name}")
        print(f"Classes: {best_content.get('class', [])}")

if __name__ == "__main__":
    main()