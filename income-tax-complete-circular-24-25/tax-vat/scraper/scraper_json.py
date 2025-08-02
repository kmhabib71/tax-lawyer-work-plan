import csv
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse

# Function to extract main content while preserving structure
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
            if not element.get_text(strip=True) and element.name not in ['br', 'hr']:
                element.decompose()
        
        # Extract structured content as hierarchical JSON
        hierarchy_data = extract_element_hierarchy(main_content)
        # Convert to structured JSON with identifiers
        structured_data = convert_to_structured_json(hierarchy_data)
        return structured_data
    else:
        return {}

# Helper function to recursively extract element content with structure
def extract_element_content(element):
    if element.name in ['script', 'style']:
        return ""
    
    # For block-level elements, we want to preserve their structure
    if element.name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'blockquote', 'pre']:
        text = element.get_text(strip=True)
        if text:
            # Return element type and content for structured representation
            return f"[{element.name.upper()}]{text}[/{element.name.upper()}]"
        else:
            return ""
    elif element.name in ['br', 'hr']:
        return f"[{element.name.upper()}]"
    elif element.name == 'ul':
        items = []
        for li in element.find_all('li', recursive=False):
            item_content = extract_element_content(li)
            if item_content:
                items.append(item_content)
        if items:
            return f"[UL]{ ''.join(items) }[/UL]"
        else:
            return ""
    elif element.name == 'ol':
        items = []
        for li in element.find_all('li', recursive=False):
            item_content = extract_element_content(li)
            if item_content:
                items.append(item_content)
        if items:
            return f"[OL]{ ''.join(items) }[/OL]"
        else:
            return ""
    else:
        # For other elements, recursively process children
        contents = []
        for child in element.find_all(True, recursive=False):
            child_content = extract_element_content(child)
            if child_content:
                contents.append(child_content)
        return ''.join(contents)

# Function to extract hierarchical content structure
def extract_element_hierarchy(element):
    if element.name in ['script', 'style']:
        return None
    
    # Get text content of this specific element (not including children)
    element_text = ''
    if element.string:
        element_text = element.string.strip()
    elif element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'blockquote', 'pre', 'strong', 'em']:
        # For text elements, get only direct text, not text from children
        element_text = ''.join([text for text in element.contents if isinstance(text, str)]).strip()
    
    # Create a dictionary to represent this element
    element_data = {
        "tag": element.name,
        "text": element_text if element_text else None,
        "children": []
    }
    
    # Add attributes if they exist
    if element.attrs:
        element_data["attributes"] = element.attrs
    
    # Process children
    for child in element.find_all(recursive=False):
        child_data = extract_element_hierarchy(child)
        if child_data is not None:
            element_data["children"].append(child_data)
    
    # If no children and no text, return None to avoid empty elements
    if not element_data["children"] and not element_data["text"] and not element_data.get("attributes"):
        return None
    
    # If no children, simplify the structure
    if not element_data["children"]:
        element_data.pop("children")
    
    return element_data

# Function to convert hierarchical structure to structured JSON with identifiers
def convert_to_structured_json(hierarchy_data):
    if not hierarchy_data:
        return {}
    
    # Create structured data
    structured_data = {}
    
    # Process the hierarchy recursively
    def process_element(element, parent_dict, depth=0):
        if not element:
            return
        
        # Get the text content
        text = element.get("text", "")
        
        # If this element has text that starts with a number, letter, or symbol, use it as an identifier
        if text:
            # Check if text starts with a number, letter, or symbol (including Bangla characters)
            import re
            # Pattern to match if text starts with a number, letter, or symbol (including Bangla)
            pattern = r'^[\u0980-\u09FF\u0021-\u002F\u003A-\u0040\u005B-\u0060\u007B-\u007E\u0030-\u0039\u0041-\u005A\u0061-\u007A]'
            match = re.match(pattern, text)
            
            if match:
                # For better keys, use more of the text content as the key
                # Extract the first meaningful part (like section numbers, letters, etc.)
                # For content that starts with parentheses or brackets, use the first few characters
                if text.startswith('(') or text.startswith('['):
                    # Use the first part inside the parenthesis/bracket
                    key = text[:10]  # Take first 10 characters
                else:
                    key_parts = re.split(r'[\s\-\:\(\)]', text, 2)  # Split into at most 3 parts
                    if len(key_parts) >= 2:
                        # Use first two parts as key for better identification
                        key = "_".join(key_parts[:2])
                    else:
                        key = key_parts[0] if key_parts else text[:30]  # Limit key length
                
                # Clean the key to make it a valid identifier
                key = re.sub(r'[^\w\u0980-\u09FF]', '_', key)
                # If key is empty or just underscores, use a generic name
                if not key or key.strip('_') == '':
                    key = "content"
                
                # Handle duplicate keys more intelligently
                # If the key already exists and has the same value, skip it
                if key in parent_dict and parent_dict[key] == text:
                    return
                # If the key exists but with different value, create a list or append suffix
                elif key in parent_dict:
                    # Check if the existing value is already a list
                    if isinstance(parent_dict[key], list):
                        # Add to the list if not already there
                        if text not in parent_dict[key]:
                            parent_dict[key].append(text)
                    else:
                        # Convert to list if values are related (similar start)
                        existing_text = parent_dict[key]
                        # If texts are similar, group them in a list
                        if existing_text[:20] == text[:20]:  # First 20 chars match
                            parent_dict[key] = [existing_text, text]
                        else:
                            # Otherwise, use numbered suffixes
                            original_key = key
                            counter = 1
                            while f"{original_key}_{counter}" in parent_dict:
                                counter += 1
                            parent_dict[f"{original_key}_{counter}"] = text
                else:
                    parent_dict[key] = text
            else:
                # Just add the text to content array
                if "content" not in parent_dict:
                    parent_dict["content"] = []
                # Avoid duplicate content entries
                if text not in parent_dict["content"]:
                    parent_dict["content"].append(text)
        elif element.get("tag") == "a" and element.get("attributes", {}).get("href"):
            # Special handling for links
            href = element["attributes"]["href"]
            if "links" not in parent_dict:
                parent_dict["links"] = []
            # Avoid duplicate links
            link_entry = {"url": href, "text": text}
            if link_entry not in parent_dict["links"]:
                parent_dict["links"].append(link_entry)
        
        # Process children
        children = element.get("children", [])
        if children:
            # For deeper nesting, we want to flatten the structure
            # If we're at depth > 3, add children directly to parent
            if depth > 3:
                for child in children:
                    process_element(child, parent_dict, depth + 1)
            else:
                # Create a children dict if not exists
                if "children" not in parent_dict:
                    parent_dict["children"] = {}
                for child in children:
                    process_element(child, parent_dict["children"], depth + 1)
    
    # Process the root element
    process_element(hierarchy_data, structured_data)
    
    # Flatten the structure if it's too deeply nested
    def flatten_structure(data):
        if isinstance(data, dict):
            # If this dict only has one key "children", flatten it
            while "children" in data and len(data) == 1:
                data = data["children"]
                if not isinstance(data, dict):
                    break
            # If we still have a dict, process all keys
            if isinstance(data, dict):
                for key, value in list(data.items()):
                    data[key] = flatten_structure(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                data[i] = flatten_structure(item)
        return data
    
    structured_data = flatten_structure(structured_data)
    
    return structured_data

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
