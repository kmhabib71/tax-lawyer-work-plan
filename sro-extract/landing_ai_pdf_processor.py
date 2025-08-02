import os
import json
from pathlib import Path
import time
from dotenv import load_dotenv
from agentic_doc.parse import parse

# Load environment variables from .env file
load_dotenv()
import os
import json
from pathlib import Path
import time
from dotenv import load_dotenv
from agentic_doc.parse import parse

# Load environment variables from .env file
load_dotenv()

# Folder configuration
ORGANIZED_FOLDER = "organized_files"  # Folder containing organized PDFs
OUTPUT_FOLDER = "extracted_output"  # Folder for output files

# Target years for SRO extraction (last 3 years)
TARGET_YEARS = ["2023", "2024", "2025"]

def save_as_markdown(pdf_name, markdown_content):
    """
    Save extracted markdown content to file
    """
    try:
        md_filename = f"{pdf_name}.md"
        md_path = os.path.join(OUTPUT_FOLDER, md_filename)
        
        with open(md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        
        print(f"Saved Markdown output to {md_path}")
        return md_path
    except Exception as e:
        print(f"Error saving Markdown file: {str(e)}")
        return None

def save_as_json(pdf_name, extracted_result):
    """
    Save extracted result as structured JSON with metadata
    """
    try:
        json_filename = f"{pdf_name}.json"
        json_path = os.path.join(OUTPUT_FOLDER, json_filename)
        
        # Create structured JSON with both markdown and chunks
        structured_data = {
            "document_name": pdf_name,
            "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "markdown_content": extracted_result.markdown if hasattr(extracted_result, 'markdown') else "",
            "chunks": extracted_result.chunks if hasattr(extracted_result, 'chunks') else [],
            "metadata": {
                "total_chunks": len(extracted_result.chunks) if hasattr(extracted_result, 'chunks') else 0,
                "extraction_engine": "landing_ai_agentic_doc"
            }
        }
        
        # Save JSON file
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(structured_data, json_file, ensure_ascii=False, indent=2)
        
        print(f"Saved JSON output to {json_path}")
        return json_path
    except Exception as e:
        print(f"Error saving JSON file: {str(e)}")
        return None

def process_pdf_with_landing_ai(pdf_path):
    """
    Process a PDF file using Landing AI Agentic Document Extraction
    """
    try:
        # Parse the PDF file using agentic-doc library
        result = parse(pdf_path)
        
        if result and len(result) > 0:
            return result[0]  # Return the first (and likely only) result
        else:
            print(f"No result returned for {pdf_path}")
            return None
    except Exception as e:
        print(f"Exception processing {pdf_path}: {str(e)}")
        return None

def get_target_pdfs():
    """
    Get all PDF files from target years (2023-2025) excluding _1 duplicates
    """
    target_pdfs = []
    
    # Check if organized folder exists
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

def process_all_pdfs():
    """
    Process all PDF files from target years (2023-2025) excluding duplicates
    """
    # Create output folder if it doesn't exist
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    
    # Get target PDF files
    target_pdfs = get_target_pdfs()
    
    if not target_pdfs:
        print(f"No PDF files found for target years {TARGET_YEARS} in '{ORGANIZED_FOLDER}' folder.")
        return
    
    print(f"Found {len(target_pdfs)} PDF files to process from years {TARGET_YEARS}.")
    print("Excluding _1 duplicate files...")
    
    # Group by category for better organization
    by_category = {}
    for pdf_info in target_pdfs:
        category = pdf_info['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(pdf_info)
    
    print(f"Categories found: {list(by_category.keys())}")
    
    processed_count = 0
    failed_count = 0
    
    # Process each PDF file
    for category, pdfs in by_category.items():
        print(f"\n--- Processing {category} SROs ({len(pdfs)} files) ---")
        
        for pdf_info in pdfs:
            pdf_path = pdf_info['path']
            filename = pdf_info['filename']
            year = pdf_info['year']
            
            print(f"Processing {category}-{year}: {filename}...")
            
            # Process PDF with Landing AI
            result = process_pdf_with_landing_ai(pdf_path)
            
            if result:
                # Create meaningful output name
                pdf_name_base = os.path.splitext(filename)[0]
                output_name = f"{category}_{year}_{pdf_name_base}"
                
                # Save in both formats
                if hasattr(result, 'markdown') and result.markdown:
                    save_as_markdown(output_name, result.markdown)
                
                save_as_json(output_name, result)
                processed_count += 1
            else:
                print(f"Failed to process {filename}")
                failed_count += 1
            
            # Add a small delay to avoid overwhelming the API
            time.sleep(2)
    
    print(f"\n--- Processing Complete ---")
    print(f"Successfully processed: {processed_count} files")
    print(f"Failed to process: {failed_count} files")
    print(f"Total files: {len(target_pdfs)} files")

def main():
    """
    Main function to run the PDF processor
    """
    print("Landing AI SRO Document Processor")
    print("==================================")
    print(f"Organized Files Folder: {ORGANIZED_FOLDER}")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    print(f"Target Years: {TARGET_YEARS}")
    print("Excluding duplicate files ending with '_1.pdf'")
    print()
    
    process_all_pdfs()
    
    print("Processing complete!")

if __name__ == "__main__":
    main()

# Folder configuration
ORGANIZED_FOLDER = "organized_files"  # Folder containing organized PDFs
OUTPUT_FOLDER = "extracted_output"  # Folder for output files

# Target years for SRO extraction (last 3 years)
TARGET_YEARS = ["2023", "2024", "2025"]

def save_as_markdown(pdf_name, markdown_content):
    """
    Save extracted markdown content to file
    """
    try:
        md_filename = f"{pdf_name}.md"
        md_path = os.path.join(OUTPUT_FOLDER, md_filename)
        
        with open(md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)
        
        print(f"Saved Markdown output to {md_path}")
        return md_path
    except Exception as e:
        print(f"Error saving Markdown file: {str(e)}")
        return None

def save_as_json(pdf_name, extracted_result):
    """
    Save extracted result as structured JSON with metadata
    """
    try:
        json_filename = f"{pdf_name}.json"
        json_path = os.path.join(OUTPUT_FOLDER, json_filename)
        
        # Create structured JSON with both markdown and chunks
        structured_data = {
            "document_name": pdf_name,
            "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "markdown_content": extracted_result.markdown if hasattr(extracted_result, 'markdown') else "",
            "chunks": extracted_result.chunks if hasattr(extracted_result, 'chunks') else [],
            "metadata": {
                "total_chunks": len(extracted_result.chunks) if hasattr(extracted_result, 'chunks') else 0,
                "extraction_engine": "landing_ai_agentic_doc"
            }
        }
        
        # Save JSON file
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(structured_data, json_file, ensure_ascii=False, indent=2)
        
        print(f"Saved JSON output to {json_path}")
        return json_path
    except Exception as e:
        print(f"Error saving JSON file: {str(e)}")
        return None

def process_pdf_with_landing_ai(pdf_path):
    """
    Process a PDF file using Landing AI Agentic Document Extraction
    """
    try:
        # Parse the PDF file using agentic-doc library
        result = parse(pdf_path)
        
        if result and len(result) > 0:
            return result[0]  # Return the first (and likely only) result
        else:
            print(f"No result returned for {pdf_path}")
            return None
    except Exception as e:
        print(f"Exception processing {pdf_path}: {str(e)}")
        return None

def get_target_pdfs():
    """
    Get all PDF files from target years (2023-2025) excluding _1 duplicates
    """
    target_pdfs = []
    
    # Check if organized folder exists
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

def process_all_pdfs():
    """
    Process all PDF files from target years (2023-2025) excluding duplicates
    """
    # Create output folder if it doesn't exist
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    
    # Get target PDF files
    target_pdfs = get_target_pdfs()
    
    if not target_pdfs:
        print(f"No PDF files found for target years {TARGET_YEARS} in '{ORGANIZED_FOLDER}' folder.")
        return
    
    print(f"Found {len(target_pdfs)} PDF files to process from years {TARGET_YEARS}.")
    print("Excluding _1 duplicate files...")
    
    # Group by category for better organization
    by_category = {}
    for pdf_info in target_pdfs:
        category = pdf_info['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(pdf_info)
    
    print(f"Categories found: {list(by_category.keys())}")
    
    processed_count = 0
    failed_count = 0
    
    # Process each PDF file
    for category, pdfs in by_category.items():
        print(f"\n--- Processing {category} SROs ({len(pdfs)} files) ---")
        
        for pdf_info in pdfs:
            pdf_path = pdf_info['path']
            filename = pdf_info['filename']
            year = pdf_info['year']
            
            print(f"Processing {category}-{year}: {filename}...")
            
            # Process PDF with Landing AI
            result = process_pdf_with_landing_ai(pdf_path)
            
            if result:
                # Create meaningful output name
                pdf_name_base = os.path.splitext(filename)[0]
                output_name = f"{category}_{year}_{pdf_name_base}"
                
                # Save in both formats
                if hasattr(result, 'markdown') and result.markdown:
                    save_as_markdown(output_name, result.markdown)
                
                save_as_json(output_name, result)
                processed_count += 1
            else:
                print(f"Failed to process {filename}")
                failed_count += 1
            
            # Add a small delay to avoid overwhelming the API
            time.sleep(2)
    
    print(f"\n--- Processing Complete ---")
    print(f"Successfully processed: {processed_count} files")
    print(f"Failed to process: {failed_count} files")
    print(f"Total files: {len(target_pdfs)} files")

def main():
    """
    Main function to run the PDF processor
    """
    print("Landing AI SRO Document Processor")
    print("==================================")
    print(f"Organized Files Folder: {ORGANIZED_FOLDER}")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    print(f"Target Years: {TARGET_YEARS}")
    print("Excluding duplicate files ending with '_1.pdf'")
    print()
    
    process_all_pdfs()
    
    print("Processing complete!")

if __name__ == "__main__":
    main()
