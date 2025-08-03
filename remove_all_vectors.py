#!/usr/bin/env python3
"""
Remove all search_vectors from JSON files to drastically reduce file size
"""

import json
import sys
import os
from pathlib import Path

def remove_search_vectors_from_object(obj):
    """Recursively remove search_vectors from any object"""
    vectors_removed = 0
    
    if isinstance(obj, dict):
        # Remove search_vectors if it exists
        if 'search_vectors' in obj:
            del obj['search_vectors']
            vectors_removed += 1
            print(f"Removed search_vectors object")
        
        # Recursively process all values
        for key, value in obj.items():
            vectors_removed += remove_search_vectors_from_object(value)
            
    elif isinstance(obj, list):
        # Process each item in the list
        for item in obj:
            vectors_removed += remove_search_vectors_from_object(item)
    
    return vectors_removed

def remove_vectors_from_file(file_path):
    """Remove search_vectors from a JSON file"""
    print(f"Processing: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    # Get original file size
    original_size = os.path.getsize(file_path)
    print(f"Original file size: {original_size:,} bytes ({original_size / (1024*1024):.1f} MB)")
    
    try:
        # Read the JSON file
        print("Reading JSON file...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Original structure loaded successfully")
        
        # Remove search_vectors
        print("Removing all search_vectors objects...")
        vectors_removed = remove_search_vectors_from_object(data)
        print(f"Total search_vectors objects removed: {vectors_removed}")
        
        # Create backup of current file
        backup_path = file_path + '.backup_vectors'
        print(f"Creating backup: {backup_path}")
        if os.path.exists(file_path):
            import shutil
            shutil.copy2(file_path, backup_path)
        
        # Write cleaned data
        print("Writing cleaned JSON...")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Get new file size
        new_size = os.path.getsize(file_path)
        size_reduction = original_size - new_size
        reduction_percent = (size_reduction / original_size * 100)
        
        print(f"New file size: {new_size:,} bytes ({new_size / (1024*1024):.1f} MB)")
        print(f"Size reduction: {size_reduction:,} bytes ({size_reduction / (1024*1024):.1f} MB)")
        print(f"Reduction percentage: {reduction_percent:.1f}%")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
        return False
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

def main():
    # File to process
    file_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ai-tax-lawyer-bangladesh/data/income_tax_comprehensive/sro_so_circular/income_tax_circular_2024_25_ultra_enriched.json"
    
    print("=== Complete Vector Removal Tool ===")
    print(f"Target file: {file_path}")
    print("Will remove all 'search_vectors' objects containing:")
    print("- content_vector arrays")
    print("- keyword_vector arrays") 
    print("- Any other vector arrays")
    print()
    
    success = remove_vectors_from_file(file_path)
    
    if success:
        print("\n✅ Complete vector removal completed successfully!")
        print("📁 Current file backed up with .backup_vectors extension")
        print("🎯 All search_vectors objects removed from JSON structure")
        print("💾 Massive file size reduction achieved!")
    else:
        print("\n❌ Vector removal failed!")
        
if __name__ == "__main__":
    main()