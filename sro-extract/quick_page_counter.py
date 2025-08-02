#!/usr/bin/env python3
"""
Quick PDF Page Counter Sample for SRO Documents
Tests first 5 files from each category to estimate total pages
"""

import os
import subprocess
from pathlib import Path

# Target years for SRO analysis
TARGET_YEARS = ["2023", "2024", "2025"]
ORGANIZED_FOLDER = "organized_files"

def count_pdf_pages(pdf_path):
    """
    Count pages in a PDF file using Windows pdfinfo via PowerShell
    """
    try:
        # Convert WSL path to Windows path for PowerShell
        windows_path = pdf_path.replace('/mnt/d/', 'D:\\').replace('/', '\\')
        
        # Use PowerShell to call pdfinfo on Windows with proper command syntax
        powershell_cmd = ['powershell.exe', '-Command', f"pdfinfo '{windows_path}'"]
        result = subprocess.run(powershell_cmd,
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            # Parse output to find page count
            for line in result.stdout.split('\n'):
                if line.startswith('Pages:'):
                    pages = int(line.split(':')[1].strip())
                    return pages
        
        return 0
        
    except Exception as e:
        print(f"Error reading {pdf_path}: {str(e)}")
        return 0

def get_target_pdfs():
    """
    Get all PDF files from target years (2023-2025) excluding _1 duplicates
    """
    target_pdfs = []
    
    if not os.path.exists(ORGANIZED_FOLDER):
        print(f"Organized folder '{ORGANIZED_FOLDER}' does not exist.")
        return target_pdfs
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(ORGANIZED_FOLDER):
        # Check if this path contains any target year
        if any(year in root for year in TARGET_YEARS):
            for file in files:
                # Skip _1 duplicate files and only process PDFs
                if file.lower().endswith('.pdf') and not file.endswith('_1.pdf'):
                    pdf_path = os.path.join(root, file)
                    # Extract category from path
                    path_parts = root.split(os.sep)
                    category = ""
                    year = ""
                    
                    for part in path_parts:
                        if "SROs" in part:
                            category = part.replace(" SROs", "")
                        if part in TARGET_YEARS:
                            year = part
                    
                    target_pdfs.append({
                        'path': pdf_path,
                        'filename': file,
                        'category': category,
                        'year': year
                    })
    
    return target_pdfs

def main():
    """
    Sample a few files from each category to estimate total pages
    """
    print("Quick SRO PDF Page Counter (Sample)")
    print("=" * 50)
    print(f"Target Years: {TARGET_YEARS}")
    print()
    
    # Get target PDF files
    target_pdfs = get_target_pdfs()
    
    if not target_pdfs:
        print(f"No PDF files found for target years {TARGET_YEARS}")
        return
    
    # Group by category
    by_category = {}
    for pdf_info in target_pdfs:
        category = pdf_info['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(pdf_info)
    
    print(f"Total files found: {len(target_pdfs)}")
    print(f"Categories: {list(by_category.keys())}")
    print()
    
    # Sample first 5 files from each category
    total_sample_pages = 0
    total_sample_files = 0
    estimates = {}
    
    for category, pdfs in by_category.items():
        print(f"--- {category} SROs (Sample: 5/{len(pdfs)} files) ---")
        
        sample_pdfs = pdfs[:5]  # Take first 5 files
        category_sample_pages = 0
        
        for pdf_info in sample_pdfs:
            pdf_path = pdf_info['path']
            filename = pdf_info['filename']
            year = pdf_info['year']
            
            pages = count_pdf_pages(pdf_path)
            category_sample_pages += pages
            total_sample_pages += pages
            total_sample_files += 1
            
            print(f"  {year}: {filename} -> {pages} pages")
        
        # Calculate estimates
        avg_pages_per_file = category_sample_pages / len(sample_pdfs) if sample_pdfs else 0
        estimated_total_pages = avg_pages_per_file * len(pdfs)
        
        estimates[category] = {
            'total_files': len(pdfs),
            'sample_files': len(sample_pdfs),
            'sample_pages': category_sample_pages,
            'avg_pages': avg_pages_per_file,
            'estimated_total': estimated_total_pages
        }
        
        print(f"  Sample: {len(sample_pdfs)} files, {category_sample_pages} pages")
        print(f"  Average: {avg_pages_per_file:.1f} pages per file")
        print(f"  Estimated total: {estimated_total_pages:.0f} pages for all {len(pdfs)} files")
        print()
    
    # Overall estimates
    overall_avg = total_sample_pages / total_sample_files if total_sample_files else 0
    estimated_total = sum(est['estimated_total'] for est in estimates.values())
    
    print("=" * 60)
    print("ESTIMATED TOTALS")
    print("=" * 60)
    
    for category, est in estimates.items():
        print(f"{category:12}: {est['total_files']:3d} files × {est['avg_pages']:4.1f} avg = {est['estimated_total']:5.0f} pages")
    
    print("-" * 50)
    print(f"{'TOTAL':12}: {len(target_pdfs):3d} files × {overall_avg:4.1f} avg = {estimated_total:5.0f} pages")
    print()
    
    print("PROCESSING ESTIMATES:")
    print(f"• Estimated total pages: {estimated_total:,.0f}")
    print(f"• Processing time estimate: {estimated_total * 0.5:.0f}-{estimated_total * 2:.0f} minutes")
    print(f"• Landing AI API calls: {len(target_pdfs)}")
    print(f"• Estimated cost: ${estimated_total * 0.01:.2f}-${estimated_total * 0.05:.2f}")

if __name__ == "__main__":
    main()