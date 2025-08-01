#!/usr/bin/env python3
"""
Simple Legal Content Extractor
Extracts actual legal content from Bengali tax law text files
Phase 0 - Real work, no exaggeration
"""

import re
import json
from pathlib import Path

class SimpleLegalExtractor:
    def __init__(self):
        self.sections_found = 0
        self.content_extracted = []
        
    def extract_sections_from_text(self, text_file_path, output_file_path):
        """Extract actual legal sections from text file"""
        print(f"Starting extraction from: {text_file_path}")
        
        with open(text_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple section detection - look for section patterns
        section_patterns = [
            r'ধারা\s+(\d+)([ক-হ]?)\s*।?\s*([^\n]+)',  # Bengali section pattern
            r'অনুচ্ছেদ\s+(\d+)([ক-হ]?)\s*।?\s*([^\n]+)',  # Article pattern
        ]
        
        extracted_sections = []
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                section_num = match.group(1)
                subsection = match.group(2) if match.group(2) else ""
                title = match.group(3).strip()
                
                # Get some content after the section heading
                start_pos = match.end()
                # Look for next 500 characters for content
                section_content = content[start_pos:start_pos+500].strip()
                
                extracted_sections.append({
                    "section_number": f"{section_num}{subsection}",
                    "title": title,
                    "content_preview": section_content[:200] + "..." if len(section_content) > 200 else section_content,
                    "type": "section"
                })
                
                self.sections_found += 1
        
        # Save extracted content
        output_data = {
            "metadata": {
                "source_file": str(text_file_path),
                "extraction_date": "2025-08-01",
                "sections_found": len(extracted_sections),
                "extraction_method": "simple_pattern_matching"
            },
            "sections": extracted_sections
        }
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"Extraction completed:")
        print(f"- Sections found: {len(extracted_sections)}")
        print(f"- Output saved to: {output_file_path}")
        
        return len(extracted_sections)

def main():
    extractor = SimpleLegalExtractor()
    
    # Extract from Income Tax Act
    source_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precise_structured_laws/Income_Tax_act-2023-bangla.txt"
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/extracted_legal_content.json"
    
    if Path(source_file).exists():
        sections_count = extractor.extract_sections_from_text(source_file, output_file)
        print(f"\n✅ Real work completed: {sections_count} sections extracted")
        print(f"✅ File created: {output_file}")
    else:
        print(f"❌ Source file not found: {source_file}")

if __name__ == "__main__":
    main()