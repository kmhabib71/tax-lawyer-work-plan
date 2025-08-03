#!/usr/bin/env python3
"""
Analyze missing topics 1-30 and prepare data for merging
"""

import json
import sys
import os
from pathlib import Path

def analyze_source_files():
    """Analyze the source extraction files"""
    
    print("=== Missing Topics Analysis ===")
    
    # File paths
    file1_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25/archive/1.extraction.json"
    file2_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25/archive/2.extraction.json"
    target_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ai-tax-lawyer-bangladesh/data/income_tax_comprehensive/sro_so_circular/income_tax_circular_2024_25_ultra_enriched.json"
    
    # Load current target file
    print(f"Loading target file: {target_path}")
    with open(target_path, 'r', encoding='utf-8') as f:
        target_data = json.load(f)
    
    print(f"Target file has topics: {len(target_data.get('topics_index', {}))}")
    print(f"Structured content starts from topic: {min(map(int, target_data.get('structured_content', {}).keys())) if target_data.get('structured_content') else 'None'}")
    
    # Analyze file 1 (from line 630+)
    print(f"\nLoading file 1: {file1_path}")
    try:
        with open(file1_path, 'r', encoding='utf-8') as f:
            file1_data = json.load(f)
        print(f"File 1 loaded successfully - contains {len(file1_data)} chunks")
        
        # Look for tax content after index 630
        relevant_chunks = []
        for i, chunk in enumerate(file1_data):
            if i >= 629:  # Line 630+ (0-indexed)
                if 'text' in chunk and len(chunk['text']) > 50:
                    relevant_chunks.append({
                        'index': i,
                        'text_preview': chunk['text'][:100] + '...' if len(chunk['text']) > 100 else chunk['text'],
                        'chunk_type': chunk.get('chunk_type', 'unknown')
                    })
        
        print(f"Found {len(relevant_chunks)} relevant chunks after line 630")
        for chunk in relevant_chunks[:5]:  # Show first 5
            print(f"  Index {chunk['index']}: {chunk['chunk_type']} - {chunk['text_preview']}")
            
    except Exception as e:
        print(f"Error loading file 1: {e}")
    
    # Analyze file 2 (complete file)
    print(f"\nLoading file 2: {file2_path}")
    try:
        with open(file2_path, 'r', encoding='utf-8') as f:
            file2_data = json.load(f)
        print(f"File 2 loaded successfully - contains {len(file2_data)} chunks")
        
        # Analyze structure
        chunk_types = {}
        text_chunks = 0
        for chunk in file2_data:
            chunk_type = chunk.get('chunk_type', 'unknown')
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            if 'text' in chunk and len(chunk['text']) > 50:
                text_chunks += 1
        
        print(f"Chunk types in file 2: {chunk_types}")
        print(f"Substantial text chunks: {text_chunks}")
        
        # Show sample content
        print("\nSample content from file 2:")
        for i, chunk in enumerate(file2_data[:10]):
            if 'text' in chunk:
                preview = chunk['text'][:80] + '...' if len(chunk['text']) > 80 else chunk['text']
                print(f"  Chunk {i}: {chunk.get('chunk_type', 'unknown')} - {preview}")
        
    except Exception as e:
        print(f"Error loading file 2: {e}")
    
    return target_data, file1_data, file2_data

def find_topic_patterns(data, filename):
    """Find patterns that might indicate topic structures"""
    print(f"\n=== Topic Pattern Analysis for {filename} ===")
    
    topic_indicators = []
    for i, chunk in enumerate(data):
        if 'text' in chunk:
            text = chunk['text']
            # Look for patterns like "১.", "২.", "Topic", "বিষয়"
            if any(pattern in text for pattern in ['১.', '২.', '৩.', 'Topic', 'বিষয়', 'করহার', 'আয়কর']):
                topic_indicators.append({
                    'index': i,
                    'text': text[:150] + '...' if len(text) > 150 else text,
                    'chunk_type': chunk.get('chunk_type', 'unknown')
                })
    
    print(f"Found {len(topic_indicators)} potential topic indicators:")
    for indicator in topic_indicators[:10]:  # Show first 10
        print(f"  Index {indicator['index']}: {indicator['text']}")
    
    return topic_indicators

def main():
    print("Analyzing missing topics 1-30 data...")
    
    try:
        target_data, file1_data, file2_data = analyze_source_files()
        
        # Find topic patterns in both files
        if file1_data:
            file1_patterns = find_topic_patterns(file1_data, "1.extraction.json")
        
        if file2_data:
            file2_patterns = find_topic_patterns(file2_data, "2.extraction.json")
        
        print("\n=== Summary ===")
        print("✅ Successfully analyzed source files")
        print("✅ Found patterns that could contain missing topics 1-30")
        print("✅ Ready to create merge strategy")
        
        print("\n📋 Next Steps:")
        print("1. Extract structured content from file 1 (line 630+)")
        print("2. Extract all structured content from file 2")
        print("3. Convert to same format as topics 31-212")
        print("4. Merge into target file")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()