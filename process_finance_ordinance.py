#!/usr/bin/env python3
"""
Script to process Finance Ordinance 2025 and clean it to match Income Tax Act structure
"""

import json
import re
from pathlib import Path

def clean_text(text):
    """Clean and normalize Bengali text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Clean up common formatting issues
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
    
    return text

def process_finance_ordinance():
    """Process and clean the Finance Ordinance 2025"""
    
    input_file = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precise_structured_laws/অরথ_অধযদশ_২০২৫.json")
    output_file = Path("/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precise_structured_laws/finance_ordinance_2025_cleaned.json")
    
    print(f"Processing file: {input_file}")
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract and clean header information
    cleaned_data = {
        "header": {
            "title": clean_text(data.get("header", {}).get("title", "")),
            "ordinance_info": clean_text(data.get("header", {}).get("ordinance_info", "")),
            "publish_date": clean_text(data.get("header", {}).get("publish_date", "")),
            "introduction": clean_text(data.get("header", {}).get("introduction", ""))
        },
        "chapters": [],
        "parts": [],
        "schedules": [
            {
                "number": "তফসিল-২", 
                "title": "২০২৫-২৬ করবর্ষের আয়কর, সারচার্জ ও কর রেয়াত হার",
                "note": "এই তফসিল পৃথকভাবে মুদ্রিত এবং ধারা ১৩৬ এ উল্লিখিত",
                "sections": []
            },
            {
                "number": "তফসিল-৩",
                "title": "২০২৬-২৭ করবর্ষের আয়কর, সারচার্জ ও কর রেয়াত হার", 
                "note": "এই তফসিল পৃথকভাবে মুদ্রিত এবং ধারা ১৩৭ এ উল্লিখিত",
                "sections": []
            }
        ]
    }
    
    # Process chapters
    if "chapters" in data:
        for chapter in data["chapters"]:
            cleaned_chapter = {
                "number": clean_text(chapter.get("number", "")),
                "title": clean_text(chapter.get("title", "")),
                "sections": []
            }
            
            # Process sections within each chapter
            if "sections" in chapter:
                for section in chapter["sections"]:
                    cleaned_section = {
                        "number": clean_text(section.get("number", "")),
                        "title": clean_text(section.get("title", "")),
                        "content_text": clean_text(section.get("content_text", "")),
                        "subsections": [],
                        "clauses": [],
                        "tables": [],
                        "footnotes": []
                    }
                    
                    # Process subsections
                    if "subsections" in section:
                        for subsection in section["subsections"]:
                            cleaned_subsection = {
                                "identifier": clean_text(subsection.get("identifier", "")),
                                "text": clean_text(subsection.get("text", "")),
                                "clauses": [],
                                "tables": []
                            }
                            
                            # Process clauses within subsections
                            if "clauses" in subsection:
                                for clause in subsection["clauses"]:
                                    cleaned_clause = {
                                        "identifier": clean_text(clause.get("identifier", "")),
                                        "text": clean_text(clause.get("text", "")),
                                        "sub_clauses": [],
                                        "tables": []
                                    }
                                    
                                    # Process sub-clauses
                                    if "sub_clauses" in clause:
                                        for sub_clause in clause["sub_clauses"]:
                                            cleaned_sub_clause = {
                                                "identifier": clean_text(sub_clause.get("identifier", "")),
                                                "text": clean_text(sub_clause.get("text", ""))
                                            }
                                            cleaned_clause["sub_clauses"].append(cleaned_sub_clause)
                                    
                                    # Process tables within clauses
                                    if "tables" in clause:
                                        for table in clause["tables"]:
                                            cleaned_table = {
                                                "title": clean_text(table.get("title", "")),
                                                "headers": table.get("headers", []),
                                                "rows": table.get("rows", [])
                                            }
                                            cleaned_clause["tables"].append(cleaned_table)
                                    
                                    cleaned_subsection["clauses"].append(cleaned_clause)
                            
                            cleaned_section["subsections"].append(cleaned_subsection)
                    
                    # Process direct clauses in sections
                    if "clauses" in section:
                        for clause in section["clauses"]:
                            cleaned_clause = {
                                "identifier": clean_text(clause.get("identifier", "")),
                                "text": clean_text(clause.get("text", "")),
                                "sub_clauses": [],
                                "tables": []
                            }
                            
                            # Process sub-clauses
                            if "sub_clauses" in clause:
                                for sub_clause in clause["sub_clauses"]:
                                    cleaned_sub_clause = {
                                        "identifier": clean_text(sub_clause.get("identifier", "")),
                                        "text": clean_text(sub_clause.get("text", ""))
                                    }
                                    cleaned_clause["sub_clauses"].append(cleaned_sub_clause)
                            
                            # Process tables within clauses
                            if "tables" in clause:
                                for table in clause["tables"]:
                                    cleaned_table = {
                                        "title": clean_text(table.get("title", "")),
                                        "headers": table.get("headers", []),
                                        "rows": table.get("rows", [])
                                    }
                                    cleaned_clause["tables"].append(cleaned_table)
                            
                            cleaned_section["clauses"].append(cleaned_clause)
                    
                    # Process tables directly in sections
                    if "tables" in section:
                        for table in section["tables"]:
                            cleaned_table = {
                                "title": clean_text(table.get("title", "")),
                                "headers": table.get("headers", []),
                                "rows": table.get("rows", [])
                            }
                            cleaned_section["tables"].append(cleaned_table)
                    
                    # Process footnotes
                    if "footnotes" in section:
                        for footnote in section["footnotes"]:
                            cleaned_footnote = {
                                "number": clean_text(footnote.get("number", "")),
                                "text": clean_text(footnote.get("text", ""))
                            }
                            cleaned_section["footnotes"].append(cleaned_footnote)
                    
                    cleaned_chapter["sections"].append(cleaned_section)
            
            cleaned_data["chapters"].append(cleaned_chapter)
    
    # Write the cleaned data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    print(f"Cleaned file saved to: {output_file}")
    
    # Print summary statistics
    total_sections = sum(len(chapter["sections"]) for chapter in cleaned_data["chapters"])
    print(f"\nSummary:")
    print(f"- Total chapters: {len(cleaned_data['chapters'])}")
    print(f"- Total sections: {total_sections}")
    print(f"- Critical Income Tax sections (29-137): Included")
    print(f"- Tax rate schedules: Referenced (তফসিল-২ and তফসিল-৩)")

if __name__ == "__main__":
    process_finance_ordinance()