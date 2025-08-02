import csv
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse

# Function to extract main content
def extract_main_content(soup):
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Try to find main content area
    # Look for common content containers
    content_selectors = [
        'main',
        '[role="main"]',
        '.main-content',
        '.content',
        '.post-content',
        '.entry-content',
        '.article-content',
        '#content',
        '.container',
        '.page-content'
    ]
    
    main_content = None
    for selector in content_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # If no main content area found, use body
    if not main_content:
        main_content = soup.find('body')
    
    # Remove common non-content elements
    if main_content:
        # Remove headers, navbars, sidebars, footers
        for element in main_content.select('header, nav, aside, footer, .header, .navbar, .sidebar, .footer'):
            element.decompose()
        
        # Remove empty elements
        for element in main_content.find_all():
            if not element.get_text(strip=True):
                element.decompose()
        
        return main_content.get_text(separator=' ', strip=True)
    else:
        return ""

# Function to extract text content
def extract_text(soup):
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and clean it
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    return text

# Function to extract tables
def extract_tables(soup):
    tables = []
    for table in soup.find_all('table'):
        table_data = []
        headers = []
        
        # Extract headers
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                headers.append(th.get_text(strip=True))
        
        # Extract rows
        for row in table.find_all('tr')[1:]:
            row_data = []
            for cell in row.find_all(['td', 'th']):
                row_data.append(cell.get_text(strip=True))
            if row_data:
                table_data.append(row_data)
        
        tables.append({
            'headers': headers,
            'data': table_data
        })
    return tables

# Function to extract forms
def extract_forms(soup):
    forms = []
    for form in soup.find_all('form'):
        form_data = {
            'action': form.get('action', ''),
            'method': form.get('method', 'get'),
            'inputs': []
        }
        
        # Extract input fields
        for input_tag in form.find_all(['input', 'textarea', 'select']):
            input_data = {
                'name': input_tag.get('name', ''),
                'type': input_tag.get('type', ''),
                'value': input_tag.get('value', ''),
                'placeholder': input_tag.get('placeholder', '')
            }
            form_data['inputs'].append(input_data)
        
        forms.append(form_data)
    return forms

# Function to scrape a single URL
def scrape_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        return {
            'url': url,
            'title': title,
            'main_content': extract_main_content(soup),
            'tables': extract_tables(soup),
            'forms': extract_forms(soup),
            'status': 'success'
        }
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'status': 'failed'
        }

# Main function to process all URLs from CSV
def main():
    # Read URLs from CSV
    urls = []
    with open('sitemap.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            urls.append(row[0])  # First column contains URLs
    
    print(f"Found {len(urls)} URLs to scrape")
    
    # Scrape each URL
    results = []
    for i, url in enumerate(urls):
        print(f"Scraping {i+1}/{len(urls)}: {url}")
        result = scrape_url(url)
        results.append(result)
        
        # Be respectful to the server by adding a delay
        time.sleep(1)
    
    # Save results in JSON format
    save_results_json(results)
    print("Scraping completed!")

# Function to save results in JSON format
def save_results_json(results):
    # Save all results in a single JSON file
    with open('scraped_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Also save each result as individual JSON files
    import os
    if not os.path.exists('json_output'):
        os.makedirs('json_output')
    
    for i, result in enumerate(results):
        if result['status'] == 'success':
            # Create a shorter filename from the URL
            # Extract the last part of the URL path
            url_path = urlparse(result['url']).path
            if url_path and url_path != '/':
                # Get the last part of the path and clean it
                filename_part = url_path.strip('/').split('/')[-1]
                # If the last part is empty, use the second to last
                if not filename_part and len(url_path.strip('/').split('/')) > 1:
                    filename_part = url_path.strip('/').split('/')[-2]
                # If still empty, use a generic name with index
                if not filename_part:
                    filename_part = f"page_{i+1}"
            else:
                filename_part = f"page_{i+1}"
            
            # Clean filename to remove invalid characters
            filename_part = "".join(c for c in filename_part if c.isalnum() or c in (' ', '-', '_')).rstrip()
            # Limit filename length
            filename_part = filename_part[:100] if len(filename_part) > 100 else filename_part
            # If filename is empty, use index
            if not filename_part:
                filename_part = f"page_{i+1}"
            
            filename = f"json_output/{filename_part}.json"
            
            # Save individual JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(results)} results to JSON format")

if __name__ == "__main__":
    main()
