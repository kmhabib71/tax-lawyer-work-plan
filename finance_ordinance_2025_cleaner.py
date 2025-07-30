#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finance Ordinance 2025 Comprehensive Cleaning Script
==================================================

Processes the raw Finance Ordinance 2025 file and transforms it into a clean, 
structured JSON file similar to the income tax act format.

Author: Claude Code Assistant
Date: 2025-07-30
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class FinanceOrdinanceCleaner:
    """Comprehensive cleaner for Finance Ordinance 2025"""
    
    def __init__(self, input_file: str, output_file: str):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.raw_data = None
        self.cleaned_data = {}
        
    def load_raw_data(self) -> bool:
        """Load the raw Finance Ordinance 2025 data"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)
            print(f"✅ Loaded raw data from {self.input_file}")
            print(f"📊 File size: {self.input_file.stat().st_size / (1024*1024):.1f}MB")
            return True
        except Exception as e:
            print(f"❌ Error loading raw data: {e}")
            return False
    
    def clean_text(self, text: str) -> str:
        """Clean raw text content removing HTML tags, excess whitespace, and formatting"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove \r\n patterns
        text = re.sub(r'\\r\\n|\\n|\\r|\r\n|\n\r|\r|\n', ' ', text)
        
        # Remove excess whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Clean up specific formatting artifacts
        text = re.sub(r'\s*\(\s*\)', '', text)  # Empty parentheses
        text = re.sub(r'\s*:\s*,', ',', text)   # Fix punctuation
        text = re.sub(r'\s*;\s*,', ',', text)   # Fix punctuation
        
        return text.strip()
    
    def extract_header_info(self, title_text: str) -> Dict[str, str]:
        """Extract header information from title text"""
        header = {
            "title": "অর্থ অধ্যাদেশ, ২০২৫",
            "ordinance_info": "",
            "publish_date": "",
            "introduction": ""
        }
        
        # Extract ordinance number
        ordinance_match = re.search(r'২০২৫ সনের (\d+) নং অধ্যাদেশ', title_text)
        if ordinance_match:
            header["ordinance_info"] = f"( ২০২৫ সনের {ordinance_match.group(1)} নং অধ্যাদেশ )"
        
        # Extract publish date
        date_match = re.search(r'\[\s*(\d+\s+\w+\s*,\s*২০২৫)\s*\]', title_text)
        if date_match:
            header["publish_date"] = f"[ {date_match.group(1)} ]"
        
        # Extract introduction
        intro_patterns = [
            r'সরকারের আর্থিক প্রস্তাবাবলি কার্যকরকরণ[^।]*।',
            r'যেহেতু[^;]*;'
        ]
        
        for pattern in intro_patterns:
            intro_match = re.search(pattern, title_text)
            if intro_match:
                header["introduction"] = self.clean_text(intro_match.group(0))
                break
        
        return header
    
    def identify_chapter_boundaries(self, text: str) -> List[Dict[str, Any]]:
        """Identify chapter boundaries and structure"""
        chapters = []
        
        # Chapter patterns
        chapter_patterns = [
            r'প্রথম অধ্যায়[^।]*প্রারম্ভিক',
            r'দ্বিতীয় অধ্যায়[^।]*মূল্য সংযোজন কর',
            r'তৃতীয় অধ্যায়[^।]*আয়কর আইন',
            r'চতুর্থ অধ্যায়[^।]*বিবিধ'
        ]
        
        chapter_names = [
            {"number": "প্রথম অধ্যায়", "title": "প্রারম্ভিক"},
            {"number": "দ্বিতীয় অধ্যায়", "title": "মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন, ২০১২ এর সংশোধন"},
            {"number": "তৃতীয় অধ্যায়", "title": "আয়কর আইন, ২০২৩ এর সংশোধন"},
            {"number": "চতুর্থ অধ্যায়", "title": "বিবিধ"}
        ]
        
        for i, chapter in enumerate(chapter_names):
            chapters.append({
                "number": chapter["number"],
                "title": chapter["title"],
                "sections": []
            })
        
        return chapters
    
    def extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """Extract sections with proper numbering and content"""
        sections = []
        
        # Bengali number pattern
        bengali_numbers = r'[১২৩৪৫৬৭৮৯০]+'
        
        # Section pattern - matches sections starting with Bengali numbers
        section_pattern = rf'({bengali_numbers})।\s*([^।]+(?:।[^।]*)*)'
        
        matches = re.finditer(section_pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            section_num = match.group(1)
            section_content = self.clean_text(match.group(2))
            
            if section_content and len(section_content) > 10:  # Filter out very short sections
                # Extract section title (first sentence)
                title_match = re.match(r'([^।]*)', section_content)
                title = title_match.group(1).strip() if title_match else f"ধারা {section_num}"
                
                sections.append({
                    "number": section_num,
                    "title": title,
                    "content": section_content,
                    "subsections": self.extract_subsections(section_content)
                })
        
        return sections
    
    def extract_subsections(self, content: str) -> List[Dict[str, Any]]:
        """Extract subsections from section content"""
        subsections = []
        
        # Subsection patterns
        subsection_patterns = [
            r'\(([১২৩৪৫৬৭৮৯০]+)\)\s*([^।]+।)',  # (১), (২), etc.
            r'([ক-য])\)\s*([^।]+।)',  # ক), খ), etc.
            r'([অ-ঔ])\)\s*([^।]+।)'   # অ), আ), etc.
        ]
        
        for pattern in subsection_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                subsection_num = match.group(1)
                subsection_content = self.clean_text(match.group(2))
                
                if subsection_content and len(subsection_content) > 5:
                    subsections.append({
                        "number": subsection_num,
                        "content": subsection_content
                    })
        
        return subsections
    
    def extract_tax_rates_and_schedules(self, text: str) -> Dict[str, Any]:
        """Extract tax rates and schedules for 2025-26 and 2026-27"""
        tax_info = {
            "income_tax_rates_2025_26": [],
            "income_tax_rates_2026_27": [],
            "vat_rates": [],
            "supplementary_duty_rates": [],
            "schedules": []
        }
        
        # Income tax rate patterns
        rate_patterns = [
            r'আয়কর[^।]*হার[^।]*২০২৫-২৬[^।]*।',
            r'আয়কর[^।]*হার[^।]*২০২৬-২৭[^।]*।',
            r'মূল্য সংযোজন কর[^।]*হার[^।]*।',
            r'সম্পূরক শুল্ক[^।]*হার[^।]*।'
        ]
        
        for pattern in rate_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                rate_text = self.clean_text(match.group(0))
                if "২০২৫-২৬" in rate_text:
                    tax_info["income_tax_rates_2025_26"].append(rate_text)
                elif "২০২৬-২৭" in rate_text:
                    tax_info["income_tax_rates_2026_27"].append(rate_text)
                elif "মূল্য সংযোজন কর" in rate_text:
                    tax_info["vat_rates"].append(rate_text)
                elif "সম্পূরক শুল্ক" in rate_text:
                    tax_info["supplementary_duty_rates"].append(rate_text)
        
        return tax_info
    
    def extract_key_sections_130_137(self, sections: List[Dict]) -> List[Dict[str, Any]]:
        """Extract key sections 130-137 (Income Tax schedules and rates)"""
        key_sections = []
        
        for section in sections:
            section_num = section.get("number", "")
            if section_num in ["১৩০", "১৩১", "১৩২", "১৩৩", "১৩৪", "১৩৫", "১ৃ৬", "১৩৭"]:
                key_sections.append({
                    "section": section_num,
                    "title": section.get("title", ""),
                    "content": section.get("content", ""),
                    "type": "income_tax_schedule",
                    "importance": "high"
                })
        
        return key_sections
    
    def extract_key_sections_29_129(self, sections: List[Dict]) -> List[Dict[str, Any]]:
        """Extract key sections 29-129 (Income Tax Act amendments)"""
        key_sections = []
        
        for section in sections:
            section_num = section.get("number", "")
            # Convert Bengali to int for comparison
            try:
                bengali_to_english = {
                    '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5',
                    '৬': '6', '৭': '7', '৮': '8', '৯': '9', '০': '0'
                }
                
                english_num = ""
                for char in section_num:
                    if char in bengali_to_english:
                        english_num += bengali_to_english[char]
                
                if english_num and 29 <= int(english_num) <= 129:
                    key_sections.append({
                        "section": section_num,
                        "title": section.get("title", ""),
                        "content": section.get("content", ""),
                        "type": "income_tax_amendment",
                        "importance": "high"
                    })
            except (ValueError, TypeError):
                continue
        
        return key_sections
    
    def create_clean_structure(self) -> Dict[str, Any]:
        """Create the clean structured JSON format"""
        if not self.raw_data:
            return {}
        
        # Get the raw content
        raw_title = self.raw_data.get("title", "")
        raw_structure = self.raw_data.get("structure", [])
        
        # Extract full text from structure
        full_text = ""
        for item in raw_structure:
            if isinstance(item, dict) and "title" in item:
                full_text += " " + str(item["title"])
        
        full_text = self.clean_text(full_text)
        
        # Create header
        header = self.extract_header_info(full_text)
        
        # Extract chapters
        chapters = self.identify_chapter_boundaries(full_text)
        
        # Extract all sections
        all_sections = self.extract_sections(full_text)
        
        # Distribute sections to chapters
        # Simple distribution based on section numbering
        chapter_1_sections = [s for s in all_sections if s["number"] == "১"]
        chapter_2_sections = [s for s in all_sections if 2 <= self._bengali_to_int(s["number"]) <= 28]
        chapter_3_sections = [s for s in all_sections if 29 <= self._bengali_to_int(s["number"]) <= 137]
        chapter_4_sections = [s for s in all_sections if self._bengali_to_int(s["number"]) > 137]
        
        if len(chapters) >= 4:
            chapters[0]["sections"] = chapter_1_sections
            chapters[1]["sections"] = chapter_2_sections
            chapters[2]["sections"] = chapter_3_sections
            chapters[3]["sections"] = chapter_4_sections
        
        # Extract tax information
        tax_info = self.extract_tax_rates_and_schedules(full_text)
        
        # Extract key sections
        key_sections_130_137 = self.extract_key_sections_130_137(all_sections)
        key_sections_29_129 = self.extract_key_sections_29_129(all_sections)
        
        # Create final structure
        cleaned_structure = {
            "header": header,
            "chapters": chapters,
            "tax_information": tax_info,
            "key_sections": {
                "income_tax_schedules_130_137": key_sections_130_137,
                "income_tax_amendments_29_129": key_sections_29_129
            },
            "statistics": {
                "total_sections": len(all_sections),
                "total_chapters": len(chapters),
                "key_sections_count": len(key_sections_130_137) + len(key_sections_29_129),
                "processing_date": "2025-07-30"
            }
        }
        
        return cleaned_structure
    
    def _bengali_to_int(self, bengali_num: str) -> int:
        """Convert Bengali number to integer"""
        try:
            bengali_to_english = {
                '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5',
                '৬': '6', '৭': '7', '৮': '8', '৯': '9', '০': '0'
            }
            
            english_num = ""
            for char in bengali_num:
                if char in bengali_to_english:
                    english_num += bengali_to_english[char]
            
            return int(english_num) if english_num else 0
        except (ValueError, TypeError):
            return 0
    
    def save_cleaned_data(self, data: Dict[str, Any]) -> bool:
        """Save the cleaned data to output file"""
        try:
            # Ensure output directory exists
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Saved cleaned data to {self.output_file}")
            print(f"📊 Output file size: {self.output_file.stat().st_size / (1024*1024):.1f}MB")
            return True
        except Exception as e:
            print(f"❌ Error saving cleaned data: {e}")
            return False
    
    def process(self) -> bool:
        """Main processing method"""
        print("🚀 Starting Finance Ordinance 2025 cleaning process...")
        
        # Load raw data
        if not self.load_raw_data():
            return False
        
        # Create clean structure
        print("🔄 Processing and cleaning data...")
        cleaned_data = self.create_clean_structure()
        
        if not cleaned_data:
            print("❌ Failed to create cleaned structure")
            return False
        
        # Save cleaned data
        if not self.save_cleaned_data(cleaned_data):
            return False
        
        # Print summary
        stats = cleaned_data.get("statistics", {})
        print("\n📈 Processing Summary:")
        print(f"   • Total Sections: {stats.get('total_sections', 0)}")
        print(f"   • Total Chapters: {stats.get('total_chapters', 0)}")
        print(f"   • Key Sections: {stats.get('key_sections_count', 0)}")
        print(f"   • Processing Date: {stats.get('processing_date', 'N/A')}")
        
        key_sections = cleaned_data.get("key_sections", {})
        print(f"   • Income Tax Schedules (130-137): {len(key_sections.get('income_tax_schedules_130_137', []))}")
        print(f"   • Income Tax Amendments (29-129): {len(key_sections.get('income_tax_amendments_29_129', []))}")
        
        tax_info = cleaned_data.get("tax_information", {})
        print(f"   • Tax Rates 2025-26: {len(tax_info.get('income_tax_rates_2025_26', []))}")
        print(f"   • Tax Rates 2026-27: {len(tax_info.get('income_tax_rates_2026_27', []))}")
        
        print("✅ Finance Ordinance 2025 cleaning completed successfully!")
        return True

def main():
    """Main execution function"""
    # File paths
    input_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/fixed_structured_laws/অরথ_অধযদশ_২০২৫.json"
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precise_structured_laws/finance_ordinance_2025_cleaned.json"
    
    # Create cleaner instance
    cleaner = FinanceOrdinanceCleaner(input_file, output_file)
    
    # Process the file
    success = cleaner.process()
    
    if success:
        print(f"\n🎉 Successfully processed Finance Ordinance 2025!")
        print(f"📁 Input: {input_file}")
        print(f"📁 Output: {output_file}")
        sys.exit(0)
    else:
        print(f"\n❌ Failed to process Finance Ordinance 2025")
        sys.exit(1)

if __name__ == "__main__":
    main()