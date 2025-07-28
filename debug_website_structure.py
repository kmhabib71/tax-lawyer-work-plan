#!/usr/bin/env python3
"""
Debug script to check the current website structure
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_website_structure():
    url = "http://bdlaws.minlaw.gov.bd/act-1541.html"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== DEBUGGING WEBSITE STRUCTURE ===")
        print(f"✅ Successfully fetched: {url}")
        print(f"📄 Page size: {len(response.content)} bytes")
        print()
        
        # Check for different section div patterns
        patterns_to_check = [
            'row lineremoves',
            'lineremoves',
            'row',
            'txt-head',
            'txt-details'
        ]
        
        for pattern in patterns_to_check:
            divs = soup.find_all('div', class_=pattern)
            print(f"🔍 Divs with class '{pattern}': {len(divs)}")
            
            if divs and len(divs) < 10:  # Show samples if not too many
                for i, div in enumerate(divs[:3]):
                    text = div.get_text().strip()[:100]
                    print(f"   Sample {i+1}: {text}...")
        
        print()
        
        # Look for Bengali section numbers
        all_divs = soup.find_all('div')
        section_divs = []
        
        for div in all_divs:
            text = div.get_text()
            if re.search(r'[০-৯]+।', text):  # Bengali section numbers
                section_divs.append(div)
        
        print(f"🔢 Divs containing Bengali section numbers: {len(section_divs)}")
        
        # Show first few section patterns
        for i, div in enumerate(section_divs[:5]):
            text = div.get_text().strip()
            match = re.search(r'([০-৯]+)।[^।]*', text)
            if match:
                section_text = match.group(0)[:150]
                print(f"   Section {i+1}: {section_text}...")
        
        print()
        
        # Check for the specific structure from content-structure.md
        lineremoves_divs = soup.find_all('div', class_='row lineremoves')
        print(f"🎯 'row lineremoves' divs: {len(lineremoves_divs)}")
        
        for i, div in enumerate(lineremoves_divs):
            # Look for txt-head and txt-details within each
            txt_head = div.find('div', class_='txt-head')
            txt_details = div.find('div', class_='txt-details')
            
            if txt_head and txt_details:
                head_text = txt_head.get_text().strip()[:50]
                print(f"   ✅ Row {i+1} has txt-head: '{head_text}...'")
            else:
                # Check if it has other class combinations
                col_sm_3 = div.find('div', class_='col-sm-3')
                col_sm_9 = div.find('div', class_='col-sm-9')
                if col_sm_3 and col_sm_9:
                    head_text = col_sm_3.get_text().strip()[:50]
                    print(f"   📋 Row {i+1} has col-sm-3: '{head_text}...'")
        
        # Try alternative selectors
        print("\n=== ALTERNATIVE SELECTORS ===")
        
        # Check for sections with specific patterns
        alternative_patterns = [
            soup.find_all('div', attrs={'class': lambda x: x and 'txt-head' in ' '.join(x) if x else False}),
            soup.find_all('div', attrs={'class': lambda x: x and 'col-sm-3' in ' '.join(x) if x else False}),
        ]
        
        for i, pattern_results in enumerate(alternative_patterns):
            print(f"Pattern {i+1}: {len(pattern_results)} matches")
            for j, div in enumerate(pattern_results[:3]):
                text = div.get_text().strip()[:60]
                print(f"   Match {j+1}: {text}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_website_structure()