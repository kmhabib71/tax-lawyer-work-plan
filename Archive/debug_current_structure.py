#!/usr/bin/env python3
"""
Debug the current structure with proper session setup
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_with_session():
    url = "http://bdlaws.minlaw.gov.bd/act-1541.html"
    
    # Use the same session setup as the working scraper
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        # Establish session
        try:
            session.get("http://bdlaws.minlaw.gov.bd", timeout=10)
            print("📡 Session established")
        except:
            print("⚠️  Could not establish main session")
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"📄 Content size: {len(response.content)} bytes")
        print()
        
        # Check all the patterns we expect
        patterns = {
            'act-chapter-group': soup.find_all('div', class_='act-chapter-group'),
            'row lineremoves': soup.find_all('div', class_='row lineremoves'),
            'lineremoves': soup.find_all('div', class_='lineremoves'),
            'txt-head': soup.find_all('div', class_='txt-head'),
            'txt-details': soup.find_all('div', class_='txt-details'),
        }
        
        for pattern_name, elements in patterns.items():
            print(f"🔍 {pattern_name}: {len(elements)} found")
            
            if elements and len(elements) < 10:
                for i, elem in enumerate(elements[:3]):
                    text = elem.get_text().strip()[:100].replace('\n', ' ')
                    print(f"   Sample {i+1}: {text}...")
        
        print()
        
        # Look for the exact structure from content-structure.md
        print("=== LOOKING FOR EXPECTED STRUCTURE ===")
        
        # Check for the row lineremoves pattern
        lineremoves_divs = soup.find_all('div', class_='row lineremoves')
        print(f"Found {len(lineremoves_divs)} 'row lineremoves' divs")
        
        for i, div in enumerate(lineremoves_divs[:3]):
            print(f"\n--- Row {i+1} ---")
            
            # Look for different possible structures
            txt_head_options = [
                div.find('div', class_='txt-head'),
                div.find('div', class_='col-sm-3 txt-head'),
                div.find('div', attrs={'class': lambda x: x and 'txt-head' in ' '.join(x) if x else False}),
            ]
            
            txt_details_options = [
                div.find('div', class_='txt-details'),
                div.find('div', class_='col-sm-9 txt-details'),
                div.find('div', attrs={'class': lambda x: x and 'txt-details' in ' '.join(x) if x else False}),
            ]
            
            for j, (head, details) in enumerate(zip(txt_head_options, txt_details_options)):
                if head and details:
                    head_text = head.get_text().strip()[:50]
                    details_text = details.get_text().strip()[:100]
                    print(f"   Option {j+1}: HEAD='{head_text}' DETAILS='{details_text}...'")
                    break
            else:
                print(f"   No txt-head/txt-details combination found")
                # Show what's actually in this div
                child_divs = div.find_all('div', recursive=False)
                print(f"   Direct children: {len(child_divs)}")
                for k, child in enumerate(child_divs[:3]):
                    classes = ' '.join(child.get('class', []))
                    text = child.get_text().strip()[:50].replace('\n', ' ')
                    print(f"     Child {k+1}: class='{classes}' text='{text}...'")
        
        # Save the actual HTML for manual inspection
        with open('current_structure.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"\n💾 Saved current HTML structure to current_structure.html")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_with_session()