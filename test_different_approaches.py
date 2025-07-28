#!/usr/bin/env python3
"""
Test different approaches to get the content
"""

import requests
from bs4 import BeautifulSoup
import time
import json

def test_selenium_like_approach():
    """Test with selenium-like delays and multiple requests"""
    
    url = "http://bdlaws.minlaw.gov.bd/act-1541.html"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    })
    
    try:
        print("🔄 Approach 1: Multiple step loading")
        
        # Step 1: Visit main site
        print("   📡 Visiting main site...")
        main_response = session.get("http://bdlaws.minlaw.gov.bd", timeout=15)
        print(f"   📄 Main site: {main_response.status_code}")
        
        # Step 2: Wait a bit
        time.sleep(3)
        
        # Step 3: Visit target URL
        print("   🎯 Visiting target URL...")
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"   📊 Content size: {len(response.content)} bytes")
        print(f"   🔍 row lineremoves: {len(soup.find_all('div', class_='row lineremoves'))}")
        print(f"   🔍 txt-head: {len(soup.find_all('div', class_='txt-head'))}")
        
        return soup
        
    except Exception as e:
        print(f"   ❌ Approach 1 failed: {e}")
        return None

def test_direct_content_url():
    """Test if there's a different URL for the content"""
    
    # Sometimes the content is loaded from a different endpoint
    possible_urls = [
        "http://bdlaws.minlaw.gov.bd/act-1541.html",
        "http://bdlaws.minlaw.gov.bd/acts/act-1541.html",
        "http://bdlaws.minlaw.gov.bd/content/act-1541.html",
        "http://bdlaws.minlaw.gov.bd/act-details-1541.html",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    })
    
    for i, url in enumerate(possible_urls):
        try:
            print(f"🔄 Testing URL {i+1}: {url}")
            response = session.get(url, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                lineremoves = len(soup.find_all('div', class_='row lineremoves'))
                txt_head = len(soup.find_all('div', class_='txt-head'))
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📊 Size: {len(response.content)} bytes")
                print(f"   🔍 row lineremoves: {lineremoves}")
                print(f"   🔍 txt-head: {txt_head}")
                
                if lineremoves > 0 or txt_head > 0:
                    print(f"   🎯 FOUND CONTENT!")
                    return soup, url
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)
    
    return None, None

def test_ajax_endpoints():
    """Test if content is loaded via AJAX"""
    
    base_url = "http://bdlaws.minlaw.gov.bd"
    
    # Common AJAX endpoints
    ajax_endpoints = [
        f"{base_url}/api/act/1541",
        f"{base_url}/ajax/act-content/1541",
        f"{base_url}/get-act-content.php?id=1541",
        f"{base_url}/load-content.php?act=1541",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/html, */*',
    })
    
    for endpoint in ajax_endpoints:
        try:
            print(f"🔄 Testing AJAX: {endpoint}")
            response = session.get(endpoint, timeout=15)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📊 Size: {len(response.content)} bytes")
                
                # Try to parse as JSON
                try:
                    data = response.json()
                    print(f"   📋 JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    return data, endpoint
                except:
                    # Try as HTML
                    if 'lineremoves' in response.text or 'txt-head' in response.text:
                        print(f"   🎯 Found HTML content with expected patterns!")
                        return response.text, endpoint
            else:
                print(f"   ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.5)
    
    return None, None

def main():
    print("=== TESTING DIFFERENT CONTENT LOADING APPROACHES ===\n")
    
    # Test 1: Multi-step loading
    soup1 = test_selenium_like_approach()
    if soup1 and soup1.find_all('div', class_='row lineremoves'):
        print("✅ Multi-step approach worked!")
        return
    
    print()
    
    # Test 2: Different URLs
    soup2, working_url = test_direct_content_url()
    if soup2 and soup2.find_all('div', class_='row lineremoves'):
        print(f"✅ Different URL approach worked: {working_url}")
        return
    
    print()
    
    # Test 3: AJAX endpoints
    content, ajax_url = test_ajax_endpoints()
    if content:
        print(f"✅ AJAX approach worked: {ajax_url}")
        return
    
    print("\n❌ All approaches failed. The content structure may have fundamentally changed.")

if __name__ == "__main__":
    main()