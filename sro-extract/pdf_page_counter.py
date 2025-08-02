#!/usr/bin/env python3
"""
PDF Page Counter for SRO Documents
Counts total pages in 321 target PDF files (2023-2025, excluding duplicates)
Uses pdfinfo command as fallback when PyPDF2 not available
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
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Parse output to find page count
            for line in result.stdout.split('\n'):
                if line.startswith('Pages:'):
                    pages = int(line.split(':')[1].strip())
                    return pages
        
        print(f"Unable to read pages from {pdf_path}")
        print(f"PowerShell error: {result.stderr}")
        return 0
        
    except subprocess.TimeoutExpired:
        print(f"Timeout reading {pdf_path}")
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
                        'year': year,
                        'relative_path': os.path.relpath(pdf_path, ORGANIZED_FOLDER)
                    })
    
    return target_pdfs

def main():
    """
    Main function to count pages in all target PDFs
    """
    print("SRO PDF Page Counter")
    print("=" * 40)
    print(f"Target Years: {TARGET_YEARS}")
    print("Excluding duplicate files ending with '_1.pdf'")
    print()
    
    # Get target PDF files
    target_pdfs = get_target_pdfs()
    
    if not target_pdfs:
        print(f"No PDF files found for target years {TARGET_YEARS}")
        return
    
    print(f"Found {len(target_pdfs)} PDF files to analyze")
    
    # Group by category for analysis
    by_category = {}
    for pdf_info in target_pdfs:
        category = pdf_info['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(pdf_info)
    
    print(f"Categories: {list(by_category.keys())}")
    print()
    
    total_pages = 0
    total_files = 0
    category_stats = {}
    
    # Count pages for each category
    for category, pdfs in by_category.items():
        print(f"--- {category} SROs ---")
        category_pages = 0
        category_files = len(pdfs)
        
        for pdf_info in pdfs:
            pdf_path = pdf_info['path']
            filename = pdf_info['filename']
            year = pdf_info['year']
            
            pages = count_pdf_pages(pdf_path)
            category_pages += pages
            
            if pages > 0:
                print(f"  {year}: {filename} -> {pages} pages")
            else:
                print(f"  {year}: {filename} -> ERROR reading file")
        
        category_stats[category] = {
            'files': category_files,
            'pages': category_pages
        }
        
        print(f"  {category} Total: {category_files} files, {category_pages} pages")
        print(f"  {category} Average: {category_pages/category_files:.1f} pages per file")
        print()
        
        total_pages += category_pages
        total_files += category_files
    
    # Final summary
    print("=" * 50)
    print("SUMMARY STATISTICS")
    print("=" * 50)
    
    for category, stats in category_stats.items():
        print(f"{category:12}: {stats['files']:3d} files, {stats['pages']:5d} pages")
    
    print("-" * 40)
    print(f"{'TOTAL':12}: {total_files:3d} files, {total_pages:5d} pages")
    print(f"{'AVERAGE':12}: {total_pages/total_files:.1f} pages per file")
    print()
    
    # Additional insights
    print("PROCESSING ESTIMATES:")
    print(f"• Total PDF pages to process: {total_pages:,}")
    print(f"• Average processing time estimate: {total_pages * 0.5:.0f}-{total_pages * 2:.0f} minutes")
    print(f"• Landing AI API calls needed: {total_files}")
    print(f"• Estimated processing cost: ${total_pages * 0.01:.2f}-${total_pages * 0.05:.2f}")

if __name__ == "__main__":
    main()