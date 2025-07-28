#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

def debug_vat_structure():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # Establish session
    try:
        session.get('http://bdlaws.minlaw.gov.bd', timeout=10)
        print("Session established")
    except:
        pass
    
    url = 'http://bdlaws.minlaw.gov.bd/act-details-1106.html'
    response = session.get(url, timeout=30)
    print(f"Content size: {len(response.content)} bytes")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for part and chapter groups
    part_groups = soup.find_all('div', class_='act-part-group')
    chapter_groups = soup.find_all('div', class_='act-chapter-group')
    
    print(f"\nFound {len(part_groups)} part groups")
    print(f"Found {len(chapter_groups)} chapter groups")
    
    # Examine the first few part groups to see what they contain
    print("\n=== PART GROUPS (first 3) ===")
    for i, part in enumerate(part_groups[:3]):
        part_name = part.find('div', class_='act-part-name')
        if part_name:
            print(f"Part {i+1}: {part_name.get_text().strip()}")
        else:
            print(f"Part {i+1}: No act-part-name found")
            print(f"Part content preview: {part.get_text()[:200]}...")
    
    # Examine chapter groups
    print("\n=== CHAPTER GROUPS ===")
    for i, chapter in enumerate(chapter_groups[:3]):
        chapter_name = chapter.find('div', class_='act-chapter-name')
        if chapter_name:
            print(f"Chapter {i+1}: {chapter_name.get_text().strip()}")
        else:
            print(f"Chapter {i+1}: No act-chapter-name found")
            print(f"Chapter content preview: {chapter.get_text()[:200]}...")
    
    # Look for text patterns that might indicate misidentification
    print("\n=== TEXT PATTERN ANALYSIS ===")
    all_text = soup.get_text()
    
    # Count occurrences of common chapter/part keywords
    import re
    chapter_matches = re.findall(r'(প্রথম অধ্যায়|দ্বিতীয় অধ্যায়|তৃতীয় অধ্যায়)', all_text)
    part_matches = re.findall(r'(প্রথম অংশ|দ্বিতীয় অংশ|তৃতীয় অংশ)', all_text)
    
    print(f"Chapter keywords found: {len(chapter_matches)}")
    print(f"Part keywords found: {len(part_matches)}")
    
    if chapter_matches:
        print(f"Chapter examples: {chapter_matches[:5]}")
    if part_matches:
        print(f"Part examples: {part_matches[:5]}")

if __name__ == "__main__":
    debug_vat_structure()