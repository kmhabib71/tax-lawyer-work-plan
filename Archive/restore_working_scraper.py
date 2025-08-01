#!/usr/bin/env python3
"""
Restore the working scraper by trying different approaches
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

def try_different_approaches(url):
    """Try different approaches to get the full content"""
    
    print(f"🔄 Trying different approaches for: {url}")
    
    # Approach 1: Different User-Agent
    headers_list = [
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'},
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'},
    ]
    
    for i, headers in enumerate(headers_list):
        print(f"📊 Approach {i+1}: Different User-Agent")
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if we have the expected content
            lineremoves = soup.find_all('div', class_='row lineremoves')
            txt_heads = soup.find_all('div', class_='txt-head')
            
            print(f"   Size: {len(response.content)} bytes")
            print(f"   'row lineremoves': {len(lineremoves)}")
            print(f"   'txt-head': {len(txt_heads)}")
            
            if lineremoves and txt_heads:
                print(f"   ✅ Found working approach!")
                return response.content, headers
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        time.sleep(1)
    
    # Approach 2: Add session and cookies
    print(f"📊 Approach: Session with cookies")
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # First make a request to the main site to establish session
        session.get('http://bdlaws.minlaw.gov.bd', timeout=10)
        time.sleep(2)
        
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        lineremoves = soup.find_all('div', class_='row lineremoves')
        txt_heads = soup.find_all('div', class_='txt-head')
        
        print(f"   Size: {len(response.content)} bytes")
        print(f"   'row lineremoves': {len(lineremoves)}")
        print(f"   'txt-head': {len(txt_heads)}")
        
        if lineremoves and txt_heads:
            print(f"   ✅ Found working approach with session!")
            return response.content, session.headers
            
    except Exception as e:
        print(f"   ❌ Session approach failed: {e}")
    
    # Approach 3: Wait and retry
    print(f"📊 Approach: Wait and retry (website might be loading)")
    try:
        time.sleep(5)
        response = requests.get(url, timeout=60)  # Longer timeout
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        lineremoves = soup.find_all('div', class_='row lineremoves')
        txt_heads = soup.find_all('div', class_='txt-head')
        
        print(f"   Size: {len(response.content)} bytes")
        print(f"   'row lineremoves': {len(lineremoves)}")
        print(f"   'txt-head': {len(txt_heads)}")
        
        if lineremoves and txt_heads:
            print(f"   ✅ Found working approach with wait!")
            return response.content, {}
            
    except Exception as e:
        print(f"   ❌ Wait approach failed: {e}")
    
    print("❌ All approaches failed - website structure may have changed")
    return None, None

def main():
    url = "http://bdlaws.minlaw.gov.bd/act-1541.html"
    content, headers = try_different_approaches(url)
    
    if content:
        print("✅ Successfully retrieved content with proper structure!")
        # Save successful content for analysis
        with open('successful_content.html', 'wb') as f:
            f.write(content)
        print("💾 Saved successful content to successful_content.html")
    else:
        print("❌ Could not retrieve content with expected structure")

if __name__ == "__main__":
    main()