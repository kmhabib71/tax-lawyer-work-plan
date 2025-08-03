#!/usr/bin/env python3
"""
Remove title_vector arrays from JSON files to reduce file size
"""

import json
import sys
import os
from pathlib import Path

def remove_vectors_from_object(obj):
    """Recursively remove title_vector from any object"""
    if isinstance(obj, dict):
        # Remove title_vector if it exists
        if 'title_vector' in obj:
            del obj['title_vector']
            print(f"Removed title_vector with {len(obj.get('title_vector', []))} elements")
        
        # Recursively process all values
        for key, value in obj.items():
            obj[key] = remove_vectors_from_object(value)
            
    elif isinstance(obj, list):
        # Process each item in the list
        return [remove_vectors_from_object(item) for item in obj]
    
    return obj

def remove_vectors_from_file(file_path):
    """Remove title_vector arrays from a JSON file"""
    print(f"Processing: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    # Get original file size
    original_size = os.path.getsize(file_path)
    print(f"Original file size: {original_size:,} bytes")
    
    try:
        # Read the JSON file
        print("Reading JSON file...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Original structure loaded successfully")
        
        # Remove vectors
        print("Removing title_vector arrays...")
        cleaned_data = remove_vectors_from_object(data)
        
        # Create backup
        backup_path = file_path + '.backup'
        print(f"Creating backup: {backup_path}")
        os.rename(file_path, backup_path)
        
        # Write cleaned data
        print("Writing cleaned JSON...")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        # Get new file size
        new_size = os.path.getsize(file_path)
        print(f"New file size: {new_size:,} bytes")
        print(f"Size reduction: {original_size - new_size:,} bytes ({((original_size - new_size) / original_size * 100):.1f}%)")
        
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
    
    print("=== Vector Removal Tool ===")
    print(f"Target file: {file_path}")
    print()
    
    success = remove_vectors_from_file(file_path)
    
    if success:
        print("\n✅ Vector removal completed successfully!")
        print("📁 Original file backed up with .backup extension")
        print("🎯 title_vector arrays removed from JSON structure")
    else:
        print("\n❌ Vector removal failed!")
        
if __name__ == "__main__":
    main()