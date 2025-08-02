#!/usr/bin/env python3
"""
JSON File Structure Analyzer for 1500+ Tax Law Files
Categorizes files into structured (with tables) vs unstructured (plain text)
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def analyze_json_file(file_path):
    """Analyze a single JSON file and return its structure type"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        structure_info = {
            'file': file_path.name,
            'has_tables': False,
            'table_count': 0,
            'has_forms': False,
            'content_length': 0,
            'structure_type': 'unknown',
            'quality_score': 0
        }
        
        # Check for tables
        if 'tables' in data and isinstance(data['tables'], list):
            structure_info['has_tables'] = len(data['tables']) > 0
            structure_info['table_count'] = len(data['tables'])
            
            # Analyze table quality
            for table in data['tables']:
                if isinstance(table, dict) and 'headers' in table and 'data' in table:
                    if len(table.get('headers', [])) > 0 and len(table.get('data', [])) > 0:
                        structure_info['quality_score'] += 2  # High quality table
                    else:
                        structure_info['quality_score'] += 1  # Some structure
        
        # Check for forms
        if 'forms' in data and isinstance(data['forms'], list):
            structure_info['has_forms'] = len(data['forms']) > 0
        
        # Check main content
        if 'main_content' in data:
            content = str(data['main_content'])
            structure_info['content_length'] = len(content)
            
            # Look for structured indicators in content
            structured_indicators = [
                'Table', 'Serial No.', 'Rate', '(1)', '(2)', '(3)',
                'Schedule', 'Part', 'Section', 'Clause', 'Paragraph',
                'percentage', '%', 'taka', 'amount'
            ]
            
            indicator_count = sum(1 for indicator in structured_indicators 
                                if indicator.lower() in content.lower())
            structure_info['quality_score'] += indicator_count
        
        # Determine structure type
        if structure_info['has_tables'] and structure_info['table_count'] > 0:
            if structure_info['quality_score'] >= 5:
                structure_info['structure_type'] = 'highly_structured'
            else:
                structure_info['structure_type'] = 'moderately_structured'
        elif structure_info['quality_score'] >= 3:
            structure_info['structure_type'] = 'semi_structured'
        else:
            structure_info['structure_type'] = 'unstructured'
        
        return structure_info
        
    except Exception as e:
        return {
            'file': file_path.name,
            'error': str(e),
            'structure_type': 'error'
        }

def main():
    """Main analysis function"""
    json_dir = Path("income-tax-complete-circular-24-25/tax-vat/json_output")
    
    if not json_dir.exists():
        print(f"Directory not found: {json_dir}")
        return
    
    results = {
        'highly_structured': [],
        'moderately_structured': [],
        'semi_structured': [],
        'unstructured': [],
        'error': []
    }
    
    stats = defaultdict(int)
    
    print("🔍 Analyzing 1500+ JSON files...")
    print("=" * 60)
    
    json_files = list(json_dir.glob("*.json"))
    total_files = len(json_files)
    
    for i, file_path in enumerate(json_files, 1):
        if i % 100 == 0:
            print(f"Progress: {i}/{total_files} files analyzed...")
        
        analysis = analyze_json_file(file_path)
        structure_type = analysis['structure_type']
        results[structure_type].append(analysis)
        stats[structure_type] += 1
    
    print("\n📊 ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"Total Files Analyzed: {total_files}")
    print(f"Highly Structured (Ready for RAGFlow): {stats['highly_structured']}")
    print(f"Moderately Structured: {stats['moderately_structured']}")
    print(f"Semi-Structured: {stats['semi_structured']}")
    print(f"Unstructured (Need Processing): {stats['unstructured']}")
    print(f"Errors: {stats['error']}")
    
    # Save detailed results
    with open("json_structure_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Create priority lists
    ready_for_ragflow = results['highly_structured'] + results['moderately_structured']
    needs_processing = results['semi_structured'] + results['unstructured']
    
    print(f"\n✅ READY FOR RAGFLOW: {len(ready_for_ragflow)} files")
    print("Top 10 ready files:")
    for i, file_info in enumerate(ready_for_ragflow[:10], 1):
        print(f"  {i}. {file_info['file']} (Tables: {file_info['table_count']}, Score: {file_info['quality_score']})")
    
    print(f"\n⚠️ NEEDS PROCESSING: {len(needs_processing)} files")
    print("Top 10 files needing work:")
    for i, file_info in enumerate(needs_processing[:10], 1):
        print(f"  {i}. {file_info['file']} (Type: {file_info['structure_type']})")
    
    # Save file lists
    with open("ragflow_ready_files.txt", "w") as f:
        for file_info in ready_for_ragflow:
            f.write(f"{file_info['file']}\n")
    
    with open("needs_processing_files.txt", "w") as f:
        for file_info in needs_processing:
            f.write(f"{file_info['file']}\n")
    
    print(f"\n📝 Results saved to:")
    print(f"  - json_structure_analysis.json (detailed analysis)")
    print(f"  - ragflow_ready_files.txt ({len(ready_for_ragflow)} files)")
    print(f"  - needs_processing_files.txt ({len(needs_processing)} files)")

if __name__ == "__main__":
    main()