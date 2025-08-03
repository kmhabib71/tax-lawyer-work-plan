#!/usr/bin/env python3
"""
Extract structured content for topics 1-30 based on topics_index from ultra_enriched file
"""

import json
import re
from typing import Dict, List, Any

def load_ultra_enriched_file():
    """Load the target ultra enriched file"""
    target_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ai-tax-lawyer-bangladesh/data/income_tax_comprehensive/sro_so_circular/income_tax_circular_2024_25_ultra_enriched.json"
    
    with open(target_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_extraction_files():
    """Load content from both extraction files"""
    file1_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25/archive/1.extraction.json"
    file2_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25/archive/2.extraction.json"
    
    print("Loading extraction files...")
    
    # Load file1 - it's an array, so slice from index 629
    with open(file1_path, 'r', encoding='utf-8') as f:
        file1_data = json.load(f)
        if isinstance(file1_data, list) and len(file1_data) > 629:
            file1_data = file1_data[629:]  # From index 630 (0-based)
    
    with open(file2_path, 'r', encoding='utf-8') as f:
        file2_data = json.load(f)
    
    return file1_data, file2_data

def create_structured_content(content_text):
    """Create structured content in the same format as existing topics"""
    structured_content = {
        "bengali_text": "",
        "legal_references": [],
        "tables_and_schedules": [],
        "calculation_formulas": [],
        "examples": []
    }
    
    if not content_text:
        return structured_content
    
    # Clean Bengali text
    bengali_text = re.sub(r'<!--.*?-->', '', content_text)
    bengali_text = re.sub(r'<[^>]+>', ' ', bengali_text)
    bengali_text = re.sub(r'\s+', ' ', bengali_text)
    structured_content["bengali_text"] = bengali_text.strip()
    
    # Extract tables
    table_pattern = r'<table[^>]*>(.*?)</table>'
    tables = re.findall(table_pattern, content_text, re.DOTALL)
    
    for i, table in enumerate(tables):
        table_data = {
            "table_id": f"table_{i+1}",
            "headers": [],
            "rows": [],
            "context": "Tax policy information"
        }
        
        # Extract headers
        header_pattern = r'<th[^>]*>(.*?)</th>'
        headers = re.findall(header_pattern, table, re.DOTALL)
        table_data["headers"] = [re.sub(r'<[^>]+>', '', h).strip() for h in headers]
        
        # Extract rows
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, table, re.DOTALL)
        
        for row in rows:
            if '<th' not in row:
                cell_pattern = r'<td[^>]*>(.*?)</td>'
                cells = re.findall(cell_pattern, row, re.DOTALL)
                clean_cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                if clean_cells:
                    table_data["rows"].append(clean_cells)
        
        if table_data["headers"] or table_data["rows"]:
            structured_content["tables_and_schedules"].append(table_data)
    
    # Extract legal references
    legal_patterns = [
        r'এস\.?\s*আর\.?\s*ও\.?\s*নং?\.?\s*[০-৯\-/]+',
        r'আইন,?\s*[০-৯]{4}',
        r'ধারা\s*[০-৯]+',
        r'অনুচ্ছেদ\s*[০-৯]+',
        r'প্রজ্ঞাপন\s*নং?\.?\s*[০-৯\-/]+'
    ]
    
    for pattern in legal_patterns:
        matches = re.findall(pattern, content_text)
        for match in matches:
            clean_match = match.strip()
            if clean_match and clean_match not in structured_content["legal_references"]:
                structured_content["legal_references"].append(clean_match)
    
    # Extract calculation formulas
    calc_patterns = [
        r'[০-৯]+%',
        r'[০-৯,]+\s*টাকা',
        r'[০-৯]+\.[০-৯]+%',
        r'[০-৯]+\s*লক্ষ\s*টাকা',
        r'[০-৯]+\s*কোটি\s*টাকা'
    ]
    
    for pattern in calc_patterns:
        matches = re.findall(pattern, content_text)
        for match in matches:
            clean_match = match.strip()
            if clean_match and clean_match not in structured_content["calculation_formulas"]:
                structured_content["calculation_formulas"].append(clean_match)
    
    return structured_content

def find_content_for_topic(topic_info, file1_data, file2_data):
    """Find content for a specific topic based on its title and page reference"""
    title_bengali = topic_info["title_bengali"]
    page_ref = topic_info.get("page_reference", 1)
    file_location = topic_info.get("file_location", 1)
    
    print(f"Looking for topic: {title_bengali} (Page: {page_ref}, File: {file_location})")
    
    # Choose the appropriate file based on file_location
    if file_location == 1:
        search_data = file1_data
    else:
        search_data = file2_data
    
    # Search in the appropriate data structure
    content_text = ""
    
    if isinstance(search_data, dict) and 'markdown' in search_data:
        markdown_content = search_data['markdown']
        content_text = find_topic_content_in_markdown(title_bengali, markdown_content)
    elif isinstance(search_data, list):
        content_text = find_topic_content_in_chunks(title_bengali, search_data)
    elif isinstance(search_data, str):
        content_text = find_topic_content_in_markdown(title_bengali, search_data)
    
    return content_text

def find_topic_content_in_markdown(title_bengali, markdown_content):
    """Find topic content in markdown by searching for title patterns"""
    # Look for section headers that match the topic title
    title_keywords = re.findall(r'[\u0980-\u09FF]+', title_bengali)
    
    if not title_keywords:
        return ""
    
    # Try to find the section with this title
    lines = markdown_content.split('\n')
    start_idx = -1
    
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in title_keywords):
            start_idx = i
            break
    
    if start_idx == -1:
        return ""
    
    # Extract content from this line until the next major section
    content_lines = []
    for i in range(start_idx, min(start_idx + 50, len(lines))):
        line = lines[i]
        # Stop if we hit another major section
        if i > start_idx and re.match(r'^[০-৯]+\.', line.strip()):
            break
        content_lines.append(line)
    
    return '\n'.join(content_lines)

def find_topic_content_in_chunks(title_bengali, chunks_data):
    """Find topic content in chunk-based data"""
    title_keywords = re.findall(r'[\u0980-\u09FF]+', title_bengali)
    
    if not title_keywords:
        return ""
    
    # Search through chunks for relevant content
    relevant_chunks = []
    
    for chunk in chunks_data:
        if isinstance(chunk, dict) and 'text' in chunk:
            text = chunk['text']
            if any(keyword in text for keyword in title_keywords):
                relevant_chunks.append(text)
    
    return ' '.join(relevant_chunks[:3])  # Limit to first 3 relevant chunks

def extract_structured_content_for_topics_1_30():
    """Main function to extract structured content for topics 1-30"""
    print("Starting extraction for topics 1-30 based on topics_index...")
    
    # Load data
    ultra_enriched = load_ultra_enriched_file()
    file1_data, file2_data = load_extraction_files()
    
    # Get topics_index for topics 1-30
    topics_index = ultra_enriched.get("topics_index", {})
    
    # Initialize structured_content if it doesn't exist
    if "structured_content" not in ultra_enriched:
        ultra_enriched["structured_content"] = {}
    
    # Process each topic 1-30
    for topic_num in range(1, 31):
        topic_key = str(topic_num)
        
        if topic_key in topics_index:
            topic_info = topics_index[topic_key]
            print(f"\nProcessing Topic {topic_num}: {topic_info['title_bengali']}")
            
            # Find content for this topic
            content_text = find_content_for_topic(topic_info, file1_data, file2_data)
            
            # Create structured content
            structured_content = create_structured_content(content_text)
            
            # Add to ultra_enriched
            ultra_enriched["structured_content"][topic_key] = structured_content
            
            print(f"✅ Added structured content: {len(structured_content['bengali_text'])} chars, "
                  f"{len(structured_content['tables_and_schedules'])} tables, "
                  f"{len(structured_content['legal_references'])} references")
        else:
            print(f"⚠️ Topic {topic_num} not found in topics_index")
    
    # Save the updated file
    output_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ai-tax-lawyer-bangladesh/data/income_tax_comprehensive/sro_so_circular/income_tax_circular_2024_25_ultra_enriched.json"
    
    print(f"\nSaving updated file to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ultra_enriched, f, ensure_ascii=False, indent=2)
    
    print("✅ Successfully updated structured content for topics 1-30 based on topics_index!")
    
    # Summary
    topics_with_content = sum(1 for i in range(1, 31) if ultra_enriched["structured_content"].get(str(i), {}).get("bengali_text"))
    print(f"📊 Summary: {topics_with_content}/30 topics have Bengali content")

if __name__ == "__main__":
    extract_structured_content_for_topics_1_30()