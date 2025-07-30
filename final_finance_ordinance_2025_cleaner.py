#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Optimized Finance Ordinance 2025 Comprehensive Cleaning Script
===================================================================

Processes the raw Finance Ordinance 2025 file and transforms it into a clean, 
structured JSON file with proper Bengali numeral section parsing.

Author: Claude Code Assistant
Date: 2025-07-30
Version: 3.0 (Final Optimized)
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class FinalFinanceOrdinanceCleaner:
    """Final optimized cleaner for Finance Ordinance 2025"""
    
    def __init__(self, input_file: str, output_file: str):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.raw_data = None
        self.cleaned_data = {}
        
        # Bengali to English number mapping (corrected)
        self.bengali_to_english = {
            '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5',
            '৬': '6', '৭': '7', '৮': '8', '৯': '9', '০': '0'
        }
        
        # English to Bengali number mapping
        self.english_to_bengali = {v: k for k, v in self.bengali_to_english.items()}
        
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
        """Enhanced text cleaning"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove \r\n patterns and normalize line breaks
        text = re.sub(r'\\r\\n|\\n|\\r|\r\n|\n\r|\r|\n', ' ', text)
        
        # Remove excess whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Clean up formatting artifacts
        text = re.sub(r'\s*\(\s*\)', '', text)
        text = re.sub(r'\s*:\s*,', ',', text)
        text = re.sub(r'প্রিন্ট ভিউ\s+', '', text)
        
        return text.strip()
    
    def extract_all_content(self) -> str:
        """Extract all content from raw data"""
        full_content = ""
        
        if not self.raw_data or "structure" not in self.raw_data:
            return ""
        
        structure = self.raw_data["structure"]
        
        for item in structure:
            if isinstance(item, dict) and "title" in item:
                content = str(item["title"])
                full_content += " " + content
        
        return self.clean_text(full_content)
    
    def extract_header_info(self, full_text: str) -> Dict[str, str]:
        """Extract header information"""
        header = {
            "title": "অর্থ অধ্যাদেশ, ২০২৫",
            "ordinance_info": "( ২০২৫ সনের ২৮ নং অধ্যাদেশ )",
            "publish_date": "[ ০২ জুন, ২০২৫ ]",
            "introduction": "সরকারের আর্থিক প্রস্তাবাবলি কার্যকরকরণ এবং কতিপয় আইন সংশোধনকল্পে প্রণীত অধ্যাদেশ",
            "enactment_authority": "গণপ্রজাতন্ত্রী বাংলাদেশের সংবিধানের ৯৩ (১) অনুচ্ছেদে প্রদত্ত ক্ষমতাবলে রাষ্ট্রপতি"
        }
        
        # Extract ordinance number
        ordinance_match = re.search(r'২০২৫ সনের (\d+) নং অধ্যাদেশ', full_text)
        if ordinance_match:
            header["ordinance_info"] = f"( ২০২৫ সনের {ordinance_match.group(1)} নং অধ্যাদেশ )"
        
        # Extract publish date
        date_match = re.search(r'\[\s*(\d+\s+\w+\s*,\s*২০২৫)\s*\]', full_text)
        if date_match:
            header["publish_date"] = f"[ {date_match.group(1)} ]"
        
        return header
    
    def extract_all_sections(self, full_text: str) -> List[Dict[str, Any]]:
        """Extract all sections using Bengali numerals"""
        sections = []
        
        # Pattern for Bengali numerals followed by period
        bengali_pattern = r'([১২৩৪৫৬৭৮৯০]+)।\s*([^।]*(?:।[^।]*)*?)(?=[১২৩৪৫৬৭৮৯০]+।|$)'
        
        matches = list(re.finditer(bengali_pattern, full_text, re.MULTILINE | re.DOTALL))
        
        print(f"🔍 Found {len(matches)} sections with Bengali numerals")
        
        for match in matches:
            bengali_num = match.group(1)
            section_content = self.clean_text(match.group(2))
            
            if section_content and len(section_content) > 20:
                # Convert Bengali number to English
                english_num = self.bengali_to_int(bengali_num)
                
                # Extract title from first part of content
                title_match = re.match(r'^([^।]+)', section_content)
                title = title_match.group(1).strip() if title_match else f"ধারা {bengali_num}"
                
                # Limit title length
                if len(title) > 150:
                    title = title[:147] + "..."
                
                section = {
                    "number": bengali_num,
                    "english_number": str(english_num),
                    "title": title,
                    "content": section_content,
                    "subsections": self.extract_subsections(section_content),
                    "tax_rates": self.extract_rates_from_content(section_content),
                    "amendments": self.extract_amendment_info(section_content)
                }
                
                sections.append(section)
        
        return sections
    
    def extract_subsections(self, content: str) -> List[Dict[str, Any]]:
        """Extract subsections"""
        subsections = []
        
        patterns = [
            r'\(([১২৩৪৫৬৭৮৯০]+)\)\s*([^।]+।)',
            r'\(([ক-য])\)\s*([^।]+।)',
            r'\(([অ-ঔ])\)\s*([^।]+।)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                subsections.append({
                    "number": match.group(1),
                    "content": self.clean_text(match.group(2))
                })
        
        return subsections
    
    def extract_rates_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract tax rates from content"""
        rates = []
        
        rate_patterns = [
            r'([১২৩৪৫৬৭৮৯০\d]+(?:\.[১২৩৪৫৬৭৮৯০\d]+)?)\s*শতাংশ',
            r'([১২৩৪৫৬৭৮৯০\d]+(?:\.[১২৩৪৫৬৭৮৯০\d]+)?)\s*%',
            r'হার[^।]*([১২৩৪৫৬৭৮৯০\d]+(?:\.[১২৩৪৫৬৭৮৯০\d]+)?)',
        ]
        
        for pattern in rate_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                rate_value = match.group(1)
                # Convert Bengali numerals to English
                english_rate = self.convert_number_to_english(rate_value)
                
                rates.append({
                    "rate": english_rate,
                    "original": rate_value,
                    "context": self.get_surrounding_text(content, match.start(), match.end(), 50)
                })
        
        return rates
    
    def extract_amendment_info(self, content: str) -> List[Dict[str, str]]:
        """Extract amendment information"""
        amendments = []
        
        amendment_keywords = [
            "সংশোধন", "প্রতিস্থাপন", "সংযোজন", "বিলুপ্ত", "রহিত"
        ]
        
        for keyword in amendment_keywords:
            if keyword in content:
                # Find the law reference
                law_match = re.search(r'(\d+) সনের (\d+) নং আইন', content)
                if law_match:
                    amendments.append({
                        "type": keyword,
                        "law_year": law_match.group(1),
                        "law_number": law_match.group(2),
                        "description": self.get_surrounding_text(content, content.find(keyword), content.find(keyword) + len(keyword), 100)
                    })
        
        return amendments
    
    def organize_sections_by_chapters(self, sections: List[Dict]) -> List[Dict[str, Any]]:
        """Organize sections into chapters"""
        chapters = [
            {
                "number": "প্রথম অধ্যায়",
                "title": "প্রারম্ভিক",
                "sections": []
            },
            {
                "number": "দ্বিতীয় অধ্যায়",
                "title": "মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন, ২০১২ এর সংশোধন",
                "sections": []
            },
            {
                "number": "তৃতীয় অধ্যায়",
                "title": "আয়কর আইন, ২০২৩ এর সংশোধন",
                "sections": []
            },
            {
                "number": "চতুর্থ অধ্যায়",
                "title": "বিবিধ",
                "sections": []
            }
        ]
        
        for section in sections:
            english_num = int(section.get("english_number", 0))
            
            if english_num == 1:
                chapters[0]["sections"].append(section)
            elif 2 <= english_num <= 28:
                chapters[1]["sections"].append(section)
            elif 29 <= english_num <= 137:
                chapters[2]["sections"].append(section)
            else:
                chapters[3]["sections"].append(section)
        
        return chapters
    
    def extract_comprehensive_tax_info(self, sections: List[Dict]) -> Dict[str, Any]:
        """Extract comprehensive tax information"""
        tax_info = {
            "income_tax_rates_2025_26": [],
            "income_tax_rates_2026_27": [],
            "vat_rates": [],
            "supplementary_duty_rates": [],
            "schedules": [],
            "all_rates": []
        }
        
        for section in sections:
            section_rates = section.get("tax_rates", [])
            section_content = section.get("content", "")
            
            # Add all rates to comprehensive list
            for rate in section_rates:
                tax_info["all_rates"].append({
                    "section": section.get("number"),
                    "rate": rate["rate"],
                    "context": rate["context"]
                })
            
            # Check for specific tax types
            if "আয়কর" in section_content:
                if "২০২৫-২০২৬" in section_content or "২০২৫-২৬" in section_content:
                    tax_info["income_tax_rates_2025_26"].extend(section_rates)
                elif "২০২৬-২০২৭" in section_content or "২০২৆-২৭" in section_content:
                    tax_info["income_tax_rates_2026_27"].extend(section_rates)
            
            if "মূল্য সংযোজন কর" in section_content or "ভ্যাট" in section_content:
                tax_info["vat_rates"].extend(section_rates)
            
            if "সম্পূরক শুল্ক" in section_content:
                tax_info["supplementary_duty_rates"].extend(section_rates)
            
            if "তফসিল" in section_content or "সারণী" in section_content:
                tax_info["schedules"].append({
                    "section": section.get("number"),
                    "title": section.get("title"),
                    "content": section_content[:500] + "..." if len(section_content) > 500 else section_content
                })
        
        return tax_info
    
    def identify_key_sections(self, sections: List[Dict]) -> Dict[str, List[Dict]]:
        """Identify key sections"""
        key_sections = {
            "income_tax_schedules_130_137": [],
            "income_tax_amendments_29_129": [],
            "vat_amendments": [],
            "important_provisions": []
        }
        
        for section in sections:
            english_num = int(section.get("english_number", 0))
            content = section.get("content", "")
            
            if 130 <= english_num <= 137:
                key_sections["income_tax_schedules_130_137"].append(section)
            elif 29 <= english_num <= 129:
                key_sections["income_tax_amendments_29_129"].append(section)
            
            if "মূল্য সংযোজন কর" in content:
                key_sections["vat_amendments"].append(section)
            
            if any(keyword in content for keyword in ["তফসিল", "সারণী", "হার", "শতাংশ"]):
                key_sections["important_provisions"].append(section)
        
        return key_sections
    
    def bengali_to_int(self, bengali_num: str) -> int:
        """Convert Bengali number to integer"""
        try:
            english_num = ""
            for char in bengali_num:
                if char in self.bengali_to_english:
                    english_num += self.bengali_to_english[char]
                elif char.isdigit():
                    english_num += char
                else:
                    english_num += char  # Keep non-numeric characters
            
            return int(english_num) if english_num and english_num.isdigit() else 0
        except (ValueError, TypeError):
            return 0
    
    def convert_number_to_english(self, bengali_text: str) -> str:
        """Convert Bengali numerals in text to English"""
        result = ""
        for char in bengali_text:
            if char in self.bengali_to_english:
                result += self.bengali_to_english[char]
            else:
                result += char
        return result
    
    def get_surrounding_text(self, text: str, start: int, end: int, context_size: int) -> str:
        """Get surrounding text with context"""
        start_pos = max(0, start - context_size)
        end_pos = min(len(text), end + context_size)
        return self.clean_text(text[start_pos:end_pos])
    
    def create_final_structure(self) -> Dict[str, Any]:
        """Create the final clean structured JSON"""
        if not self.raw_data:
            return {}
        
        print("🔄 Extracting full content...")
        full_text = self.extract_all_content()
        
        print("🔄 Extracting header information...")
        header = self.extract_header_info(full_text)
        
        print("🔄 Extracting all sections...")
        all_sections = self.extract_all_sections(full_text)
        
        print("🔄 Organizing sections by chapters...")
        chapters = self.organize_sections_by_chapters(all_sections)
        
        print("🔄 Extracting tax information...")
        tax_info = self.extract_comprehensive_tax_info(all_sections)
        
        print("🔄 Identifying key sections...")
        key_sections = self.identify_key_sections(all_sections)
        
        # Create final structure
        final_structure = {
            "header": header,
            "chapters": chapters,
            "tax_information": tax_info,
            "key_sections": key_sections,
            "statistics": {
                "total_sections": len(all_sections),
                "total_chapters": len(chapters),
                "key_sections_count": sum(len(sections) for sections in key_sections.values()),
                "processing_date": "2025-07-30",
                "content_length": len(full_text),
                "version": "3.0 (Final Optimized)"
            },
            "metadata": {
                "source_file": str(self.input_file),
                "processing_script": "final_finance_ordinance_2025_cleaner.py",
                "format_version": "3.0",
                "structure_type": "final_optimized_hierarchical",
                "bengali_numerals_supported": True
            }
        }
        
        return final_structure
    
    def save_cleaned_data(self, data: Dict[str, Any]) -> bool:
        """Save the cleaned data"""
        try:
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
        print("🚀 Starting Final Optimized Finance Ordinance 2025 cleaning process...")
        
        if not self.load_raw_data():
            return False
        
        print("🔄 Processing with final optimized methods...")
        cleaned_data = self.create_final_structure()
        
        if not cleaned_data:
            print("❌ Failed to create cleaned structure")
            return False
        
        if not self.save_cleaned_data(cleaned_data):
            return False
        
        # Print detailed summary
        stats = cleaned_data.get("statistics", {})
        print("\n📈 Final Processing Summary:")
        print(f"   • Total Sections: {stats.get('total_sections', 0)}")
        print(f"   • Total Chapters: {stats.get('total_chapters', 0)}")
        print(f"   • Key Sections: {stats.get('key_sections_count', 0)}")
        print(f"   • Content Length: {stats.get('content_length', 0):,} characters")
        print(f"   • Processing Version: {stats.get('version', 'N/A')}")
        
        # Chapter breakdown
        chapters = cleaned_data.get("chapters", [])
        for i, chapter in enumerate(chapters):
            section_count = len(chapter.get("sections", []))
            print(f"   • {chapter.get('number', f'Chapter {i+1}')}: {section_count} sections")
        
        key_sections = cleaned_data.get("key_sections", {})
        print(f"   • Income Tax Schedules (130-137): {len(key_sections.get('income_tax_schedules_130_137', []))}")
        print(f"   • Income Tax Amendments (29-129): {len(key_sections.get('income_tax_amendments_29_129', []))}")
        print(f"   • VAT Amendments: {len(key_sections.get('vat_amendments', []))}")
        print(f"   • Important Provisions: {len(key_sections.get('important_provisions', []))}")
        
        tax_info = cleaned_data.get("tax_information", {})
        print(f"   • All Tax Rates Found: {len(tax_info.get('all_rates', []))}")
        print(f"   • Tax Schedules: {len(tax_info.get('schedules', []))}")
        
        print("✅ Final Optimized Finance Ordinance 2025 cleaning completed successfully!")
        return True

def main():
    """Main execution function"""
    input_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/fixed_structured_laws/অরথ_অধযদশ_২০২৫.json"
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precise_structured_laws/finance_ordinance_2025_cleaned_final.json"
    
    cleaner = FinalFinanceOrdinanceCleaner(input_file, output_file)
    
    success = cleaner.process()
    
    if success:
        print(f"\n🎉 Successfully processed Finance Ordinance 2025 with final optimized methods!")
        print(f"📁 Input: {input_file}")
        print(f"📁 Output: {output_file}")
        print(f"\n🔧 Ready for AI tax advisory system integration!")
        sys.exit(0)
    else:
        print(f"\n❌ Failed to process Finance Ordinance 2025")
        sys.exit(1)

if __name__ == "__main__":
    main()