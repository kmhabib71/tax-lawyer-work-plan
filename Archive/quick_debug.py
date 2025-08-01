#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

def quick_debug():
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
    
    url = 'http://bdlaws.minlaw.gov.bd/act-1541.html'
    response = session.get(url, timeout=30)
    print(f"Content size: {len(response.content)} bytes")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for different possible row classes
    row_classes = ['row lineremoves', 'row', 'lineremoves']
    for cls in row_classes:
        divs = soup.find_all('div', class_=cls)
        print(f"Found {len(divs)} divs with class '{cls}'")
    
    # Check for txt-head and txt-details
    txt_heads = soup.find_all('div', class_='txt-head')
    txt_details = soup.find_all('div', class_='txt-details')
    print(f"Found {len(txt_heads)} txt-head divs")
    print(f"Found {len(txt_details)} txt-details divs")
    
    # Look for section numbers in text
    import re
    all_text = soup.get_text()
    section_matches = re.findall(r'[০-৯]+।', all_text)
    print(f"Found section numbers: {section_matches[:10]}...")  # First 10

if __name__ == "__main__":
    quick_debug()