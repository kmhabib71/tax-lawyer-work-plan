#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Finance Ordinance 2025 Comprehensive Cleaning Script
============================================================

Processes the raw Finance Ordinance 2025 file and transforms it into a clean, 
structured JSON file with improved section parsing and tax rate extraction.

Author: Claude Code Assistant
Date: 2025-07-30
Version: 2.0 (Enhanced)
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class EnhancedFinanceOrdinanceCleaner:
    """Enhanced cleaner for Finance Ordinance 2025 with better section parsing"""
    
    def __init__(self, input_file: str, output_file: str):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.raw_data = None
        self.cleaned_data = {}
        
        # Bengali to English number mapping
        self.bengali_to_english = {
            '১': '1', '২': '2', 'ৃ': '3', '৪': '4', '৫': '5',
            '৬': '6', '৭': '7', '৮': '8', '৯': '9', '৯': '0'
        }
        
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
        """Enhanced text cleaning with better HTML and formatting removal"""
        if not text:
            return ""
        
        # Remove HTML tags and their content
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove \r\n patterns and normalize line breaks
        text = re.sub(r'\\r\\n|\\n|\\r|\r\n|\n\r|\r|\n', ' ', text)
        
        # Remove excess whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Clean up specific formatting artifacts
        text = re.sub(r'\s*\(\s*\)', '', text)  # Empty parentheses
        text = re.sub(r'\s*:\s*,', ',', text)   # Fix punctuation
        text = re.sub(r'\s*;\s*,', ',', text)   # Fix punctuation
        text = re.sub(r'\s*।\s*।', '।', text)   # Double periods
        
        # Clean up section markers
        text = re.sub(r'প্রিন্ট ভিউ\s+', '', text)
        
        return text.strip()
    
    def extract_all_content(self) -> str:
        """Extract all content from the raw data structure"""
        full_content = ""
        
        if not self.raw_data or "structure" not in self.raw_data:
            return ""
        
        structure = self.raw_data["structure"]
        
        for item in structure:
            if isinstance(item, dict):
                if "title" in item:
                    content = str(item["title"])
                    full_content += " " + content
                
                # Check for nested content
                if "content" in item:
                    content = str(item["content"])
                    full_content += " " + content
        
        return self.clean_text(full_content)
    
    def extract_header_info(self, full_text: str) -> Dict[str, str]:
        """Extract comprehensive header information"""
        header = {
            "title": "অর্থ অধ্যাদেশ, ২০২৫",
            "ordinance_info": "",
            "publish_date": "",
            "introduction": "",
            "enactment_authority": "",
            "objective": ""
        }
        
        # Extract ordinance number
        ordinance_patterns = [
            r'২০২৫ সনের (\d+) নং অধ্যাদেশ',
            r'(\d+) নং অধ্যাদেশ'
        ]
        
        for pattern in ordinance_patterns:
            match = re.search(pattern, full_text)
            if match:
                header["ordinance_info"] = f"( ২০২৫ সনের {match.group(1)} নং অধ্যাদেশ )"
                break
        
        # Extract publish date
        date_patterns = [
            r'\[\s*(\d+\s+\w+\s*,\s*২০২৫)\s*\]',
            r'(\d+\s+\w+\s*,\s*২০২৫)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, full_text)
            if match:
                header["publish_date"] = f"[ {match.group(1)} ]"
                break
        
        # Extract enactment authority
        authority_match = re.search(r'গণপ্রজাতন্ত্রী বাংলাদেশের সংবিধানের ৯৩ \(১\) অনুচ্ছেদে প্রদত্ত ক্ষমতাবলে রাষ্ট্রপতি[^।]*।', full_text)
        if authority_match:
            header["enactment_authority"] = self.clean_text(authority_match.group(0))
        
        # Extract objective
        objective_match = re.search(r'সরকারের আর্থিক প্রস্তাবাবলি কার্যকরকরণ[^।]*।', full_text)
        if objective_match:
            header["objective"] = self.clean_text(objective_match.group(0))
        
        # Combine introduction
        intro_parts = []
        if header["objective"]:
            intro_parts.append(header["objective"])
        if header["enactment_authority"]:
            intro_parts.append(header["enactment_authority"])
        
        header["introduction"] = " ".join(intro_parts)
        
        return header
    
    def extract_chapters_and_sections(self, full_text: str) -> List[Dict[str, Any]]:
        """Extract chapters and their sections with improved parsing"""
        chapters = []
        
        # Define chapter patterns and boundaries
        chapter_patterns = [
            {
                "number": "প্রথম অধ্যায়",
                "title": "প্রারম্ভিক",
                "start_pattern": r'প্রথম অধ্যায়\s+প্রারম্ভিক',
                "end_pattern": r'দ্বিতীয় অধ্যায়'
            },
            {
                "number": "দ্বিতীয় অধ্যায়",
                "title": "মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন, ২০১২ এর সংশোধন",
                "start_pattern": r'দ্বিতীয় অধ্যায়\s+মূল্য সংযোজন কর',
                "end_pattern": r'তৃতীয় অধ্যায়'
            },
            {
                "number": "তৃতীয় অধ্যায়",
                "title": "আয়কর আইন, ২০২৩ এর সংশোধন",
                "start_pattern": r'তৃতীয় অধ্যায়\s+আয়কর আইন',
                "end_pattern": r'চতুর্থ অধ্যায়'
            },
            {
                "number": "চতুর্থ অধ্যায়",
                "title": "বিবিধ",
                "start_pattern": r'চতুর্থ অধ্যায়\s+বিবিধ',
                "end_pattern": r'$'  # End of text
            }
        ]
        
        for i, chapter_info in enumerate(chapter_patterns):
            chapter = {
                "number": chapter_info["number"],
                "title": chapter_info["title"],
                "sections": []
            }
            
            # Find chapter content boundaries
            start_match = re.search(chapter_info["start_pattern"], full_text)
            if i < len(chapter_patterns) - 1:
                end_match = re.search(chapter_patterns[i + 1]["start_pattern"], full_text)
            else:
                end_match = None
            
            if start_match:
                start_pos = start_match.end()
                end_pos = end_match.start() if end_match else len(full_text)
                chapter_content = full_text[start_pos:end_pos]
                
                # Extract sections from chapter content
                chapter["sections"] = self.extract_sections_from_content(chapter_content, i + 1)
            
            chapters.append(chapter)
        
        return chapters
    
    def extract_sections_from_content(self, content: str, chapter_num: int) -> List[Dict[str, Any]]:
        """Extract sections from chapter content with better parsing"""
        sections = []
        
        # Different section patterns for different chapters
        if chapter_num == 1:  # First chapter (introductory)
            section_pattern = r'(\d+)।\s*([^।]+(?:।[^।]*)*?)(?=\d+।|$)'
        else:  # Other chapters
            section_pattern = r'(\d+)।\s*([^।]+(?:।[^।]*)*?)(?=\d+।|$)'
        
        matches = list(re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL))
        
        for match in matches:
            section_num = match.group(1)
            section_content = self.clean_text(match.group(2))
            
            if section_content and len(section_content) > 20:
                # Extract section title (first sentence or clause)
                title_patterns = [
                    r'^([^।]+।)',  # First sentence
                    r'^([^।]+)',   # First clause
                ]
                
                title = f"ধারা {section_num}"
                for pattern in title_patterns:
                    title_match = re.match(pattern, section_content)
                    if title_match:
                        potential_title = self.clean_text(title_match.group(1))
                        if len(potential_title) < 150:  # Reasonable title length
                            title = potential_title
                        break
                
                section = {
                    "number": section_num,
                    "title": title,
                    "content": section_content,
                    "subsections": self.extract_subsections(section_content),
                    "amendments": self.extract_amendments(section_content) if chapter_num > 1 else [],
                    "tax_rates": self.extract_tax_rates_from_section(section_content)
                }
                
                sections.append(section)
        
        return sections
    
    def extract_subsections(self, content: str) -> List[Dict[str, Any]]:
        """Extract subsections with better pattern recognition"""
        subsections = []
        
        subsection_patterns = [
            r'\(([১২৩৪৫৬৭৮৯০]+)\)\s*([^।]+।)',  # (১), (২), etc.
            r'\(([ক-য])\)\s*([^।]+।)',          # (ক), (খ), etc.
            r'\(([অ-ঔ])\)\s*([^।]+।)',          # (অ), (আ), etc.
            r'([ক-য])\)\s*([^।]+।)',            # ক), খ), etc.
            r'([অ-ঔ])\)\s*([^।]+।)',            # অ), আ), etc.
        ]
        
        for pattern in subsection_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                subsection_num = match.group(1)
                subsection_content = self.clean_text(match.group(2))
                
                if subsection_content and len(subsection_content) > 10:
                    subsections.append({
                        "number": subsection_num,
                        "content": subsection_content
                    })
        
        return subsections
    
    def extract_amendments(self, content: str) -> List[Dict[str, Any]]:
        """Extract amendment information from section content"""
        amendments = []
        
        amendment_patterns = [
            r'(\d+) সনের (\d+) নং আইনের ধারা (\d+)',
            r'উক্ত আইনের ধারা (\d+)',
            r'সংশোধন',
            r'প্রতিস্থাপন',
            r'সংযোজন',
            r'বিলুপ্ত'
        ]
        
        for pattern in amendment_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                amendment_text = match.group(0)
                # Find surrounding context
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 100)
                context = content[start:end]
                
                amendments.append({
                    "type": "amendment",
                    "reference": amendment_text,
                    "context": self.clean_text(context)
                })
        
        return amendments
    
    def extract_tax_rates_from_section(self, content: str) -> List[Dict[str, Any]]:
        """Extract tax rates and percentages from section content"""
        tax_rates = []
        
        rate_patterns = [
            r'(\d+(?:\.\d+)?)\s*শতাংশ',  # X শতাংশ
            r'(\d+(?:\.\d+)?)\s*%',       # X%
            r'(\d+(?:\.\d+)?)\s*percent', # X percent
            r'হার\s*(\d+(?:\.\d+)?)',     # হার X
        ]
        
        for pattern in rate_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                rate_value = match.group(1)
                # Find surrounding context
                start = max(0, match.start() - 30)
                end = min(len(content), match.end() + 30)
                context = content[start:end]
                
                tax_rates.append({
                    "rate": rate_value,
                    "unit": "percentage",
                    "context": self.clean_text(context)
                })
        
        return tax_rates
    
    def extract_comprehensive_tax_information(self, full_text: str) -> Dict[str, Any]:
        """Extract comprehensive tax information and schedules"""
        tax_info = {
            "income_tax_rates_2025_26": [],
            "income_tax_rates_2026_27": [],
            "vat_rates": [],
            "supplementary_duty_rates": [],
            "customs_duty_rates": [],
            "schedules": [],
            "tax_slabs": [],
            "exemptions": []
        }
        
        # Income tax rate patterns for specific years
        year_patterns = {
            "2025-26": [r'২০২৫-২৬\s*অর্থবছরে?[^।]*আয়কর[^।]*।', r'২০২৫-২৬[^।]*হার[^।]*।'],
            "2026-27": [r'২০২৬-২৭\s*অর্থবছরে?[^।]*আয়কর[^।]*।', r'২০২৬-২৭[^।]*হার[^।]*।']
        }
        
        for year, patterns in year_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    rate_text = self.clean_text(match.group(0))
                    key = f"income_tax_rates_{year.replace('-', '_')}"
                    tax_info[key].append({
                        "year": year,
                        "description": rate_text,
                        "rates": self.extract_rates_from_text(rate_text)
                    })
        
        # VAT and supplementary duty patterns
        vat_patterns = [
            r'মূল্য সংযোজন কর[^।]*(\d+(?:\.\d+)?)\s*শতাংশ[^।]*।',
            r'ভ্যাট[^।]*(\d+(?:\.\d+)?)\s*%[^।]*।'
        ]
        
        for pattern in vat_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                tax_info["vat_rates"].append({
                    "description": self.clean_text(match.group(0)),
                    "rate": match.group(1) if len(match.groups()) > 0 else "N/A"
                })
        
        # Extract tax schedules (tables and structured data)
        schedule_patterns = [
            r'তফসিল[^।]*।',
            r'সারণী[^।]*।',
            r'Schedule[^।]*।'
        ]
        
        for pattern in schedule_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                schedule_text = self.clean_text(match.group(0))
                tax_info["schedules"].append({
                    "type": "schedule",
                    "content": schedule_text
                })
        
        return tax_info
    
    def extract_rates_from_text(self, text: str) -> List[str]:
        """Extract numeric rates from text"""
        rate_pattern = r'(\d+(?:\.\d+)?)\s*(?:শতাংশ|%|percent)'
        matches = re.findall(rate_pattern, text, re.IGNORECASE)
        return matches
    
    def identify_key_sections(self, chapters: List[Dict]) -> Dict[str, List[Dict]]:
        """Identify and categorize key sections"""
        key_sections = {
            "income_tax_schedules_130_137": [],
            "income_tax_amendments_29_129": [],
            "vat_amendments": [],
            "customs_amendments": [],
            "tax_rates": [],
            "important_provisions": []
        }
        
        for chapter in chapters:
            for section in chapter.get("sections", []):
                section_num = section.get("number", "")
                section_content = section.get("content", "")
                
                # Convert Bengali numbers to English for comparison
                english_num = self.bengali_to_int(section_num)
                
                # Categorize sections
                if 130 <= english_num <= 137:
                    key_sections["income_tax_schedules_130_137"].append({
                        "section": section_num,
                        "title": section.get("title", ""),
                        "content": section_content,
                        "type": "income_tax_schedule",
                        "importance": "high"
                    })
                elif 29 <= english_num <= 129:
                    key_sections["income_tax_amendments_29_129"].append({
                        "section": section_num,
                        "title": section.get("title", ""),
                        "content": section_content,
                        "type": "income_tax_amendment",
                        "importance": "high"
                    })
                
                # Check for VAT amendments
                if "মূল্য সংযোজন কর" in section_content or "ভ্যাট" in section_content:
                    key_sections["vat_amendments"].append({
                        "section": section_num,
                        "title": section.get("title", ""),
                        "content": section_content,
                        "type": "vat_amendment"
                    })
                
                # Check for tax rates
                if section.get("tax_rates"):
                    key_sections["tax_rates"].append({
                        "section": section_num,
                        "title": section.get("title", ""),
                        "rates": section["tax_rates"]
                    })
        
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
            
            return int(english_num) if english_num else 0
        except (ValueError, TypeError):
            return 0
    
    def create_enhanced_structure(self) -> Dict[str, Any]:
        """Create the enhanced clean structured JSON format"""
        if not self.raw_data:
            return {}
        
        print("🔄 Extracting full content...")
        full_text = self.extract_all_content()
        
        if not full_text:
            print("⚠️ No content extracted from raw data")
            return {}
        
        print("🔄 Extracting header information...")
        header = self.extract_header_info(full_text)
        
        print("🔄 Extracting chapters and sections...")
        chapters = self.extract_chapters_and_sections(full_text)
        
        print("🔄 Extracting tax information...")
        tax_info = self.extract_comprehensive_tax_information(full_text)
        
        print("🔄 Identifying key sections...")
        key_sections = self.identify_key_sections(chapters)
        
        # Calculate statistics
        total_sections = sum(len(chapter.get("sections", [])) for chapter in chapters)
        
        # Create final structure
        cleaned_structure = {
            "header": header,
            "chapters": chapters,
            "tax_information": tax_info,
            "key_sections": key_sections,
            "statistics": {
                "total_sections": total_sections,
                "total_chapters": len(chapters),
                "key_sections_count": sum(len(sections) for sections in key_sections.values()),
                "processing_date": "2025-07-30",
                "content_length": len(full_text),
                "version": "2.0 (Enhanced)"
            },
            "metadata": {
                "source_file": str(self.input_file),
                "processing_script": "enhanced_finance_ordinance_2025_cleaner.py",
                "format_version": "2.0",
                "structure_type": "enhanced_hierarchical"
            }
        }
        
        return cleaned_structure
    
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
        print("🚀 Starting Enhanced Finance Ordinance 2025 cleaning process...")
        
        # Load raw data
        if not self.load_raw_data():
            return False
        
        # Create enhanced structure
        print("🔄 Processing and cleaning data with enhanced methods...")
        cleaned_data = self.create_enhanced_structure()
        
        if not cleaned_data:
            print("❌ Failed to create cleaned structure")
            return False
        
        # Save cleaned data
        if not self.save_cleaned_data(cleaned_data):
            return False
        
        # Print comprehensive summary
        stats = cleaned_data.get("statistics", {})
        print("\n📈 Enhanced Processing Summary:")
        print(f"   • Total Sections: {stats.get('total_sections', 0)}")
        print(f"   • Total Chapters: {stats.get('total_chapters', 0)}")
        print(f"   • Key Sections: {stats.get('key_sections_count', 0)}")
        print(f"   • Content Length: {stats.get('content_length', 0):,} characters")
        print(f"   • Processing Version: {stats.get('version', 'N/A')}")
        
        key_sections = cleaned_data.get("key_sections", {})
        print(f"   • Income Tax Schedules (130-137): {len(key_sections.get('income_tax_schedules_130_137', []))}")
        print(f"   • Income Tax Amendments (29-129): {len(key_sections.get('income_tax_amendments_29_129', []))}")
        print(f"   • VAT Amendments: {len(key_sections.get('vat_amendments', []))}")
        print(f"   • Tax Rate Sections: {len(key_sections.get('tax_rates', []))}")
        
        tax_info = cleaned_data.get("tax_information", {})
        print(f"   • Tax Rates 2025-26: {len(tax_info.get('income_tax_rates_2025_26', []))}")
        print(f"   • Tax Rates 2026-27: {len(tax_info.get('income_tax_rates_2026_27', []))}")
        print(f"   • VAT Rates: {len(tax_info.get('vat_rates', []))}")
        print(f"   • Tax Schedules: {len(tax_info.get('schedules', []))}")
        
        print("✅ Enhanced Finance Ordinance 2025 cleaning completed successfully!")
        return True

def main():
    """Main execution function"""
    # File paths
    input_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/fixed_structured_laws/অরথ_অধযদশ_২০২৫.json"
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precise_structured_laws/finance_ordinance_2025_cleaned_enhanced.json"
    
    # Create enhanced cleaner instance
    cleaner = EnhancedFinanceOrdinanceCleaner(input_file, output_file)
    
    # Process the file
    success = cleaner.process()
    
    if success:
        print(f"\n🎉 Successfully processed Finance Ordinance 2025 with enhanced methods!")
        print(f"📁 Input: {input_file}")
        print(f"📁 Output: {output_file}")
        sys.exit(0)
    else:
        print(f"\n❌ Failed to process Finance Ordinance 2025")
        sys.exit(1)

if __name__ == "__main__":
    main()