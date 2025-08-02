#!/usr/bin/env python3
"""
Enhanced Legal Content Processor for Bangladesh Tax Law Files
============================================================

This script creates professional-grade structured legal documents that match
the target format of main data assets with proper chapters->sections->subsections hierarchy.

Author: AI Tax Lawyer Bangladesh Project
Date: August 2025
Version: 2.0 - Professional Grade Enhancement
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class LegalSection:
    """Represents a legal section with proper hierarchy"""
    number: str
    title: str
    content_text: str
    subsections: List['LegalSubsection']
    clauses: List['LegalClause']
    tables: List[Dict[str, Any]]
    references: List[str]
    amendments: List[str]

@dataclass
class LegalSubsection:
    """Represents a legal subsection"""
    identifier: str
    text: str
    clauses: List['LegalClause']
    tables: List[Dict[str, Any]]

@dataclass
class LegalClause:
    """Represents a legal clause"""
    identifier: str
    text: str
    sub_clauses: List['LegalSubClause']
    tables: List[Dict[str, Any]]

@dataclass
class LegalSubClause:
    """Represents a legal sub-clause"""
    identifier: str
    text: str

class ProfessionalBengaliLegalParser:
    """Advanced Bengali legal text parser with professional-grade structure detection"""
    
    def __init__(self):
        # Enhanced section patterns with proper hierarchy
        self.section_patterns = {
            'chapter': [
                r'(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম|নবম|দশম)\s*অধ্যায়',
                r'অধ্যায়\s*(\d+)',
                r'Chapter\s*(\d+)'
            ],
            'section': [
                r'^(\d+)।\s*',  # Main section numbers like "১।"
                r'ধারা\s*(\d+)',
                r'Section\s*(\d+)'
            ],
            'subsection': [
                r'\((\d+)\)\s*',  # Subsections like "(১)"
                r'উপ-ধারা\s*\((\d+)\)'
            ],
            'clause': [
                r'\(([ক-ঞ])\)\s*',  # Bengali letters in parentheses
                r'\(([a-z])\)\s*',   # English letters in parentheses  
                r'দফা\s*\(([^)]+)\)'
            ],
            'sub_clause': [
                r'\(([অ-ঔ])\)\s*',   # Bengali vowels for sub-clauses
                r'\(([i-v]+)\)\s*'    # Roman numerals
            ],
            'schedule': [
                r'(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম)\s*তফসিল',
                r'(\d+)(st|nd|rd|th)\s*[Ss]chedule',
                r'তফসিল\s*(\d+)'
            ],
            'part': [
                r'অংশ\s*(\d+)',
                r'[Pp]art\s*(\d+)'
            ]
        }
        
        self.amendment_patterns = [
            r'সংশোধিত',
            r'বিলুপ্ত', 
            r'প্রতিস্থাপিত',
            r'সংযোজিত',
            r'রহিত',
            r'সংশোধন',
            r'পরিবর্তে'
        ]
        
        self.reference_patterns = [
            r'ধারা\s*(\d+)',
            r'তফসিল\s*(\d+)', 
            r'বিধি\s*(\d+)',
            r'অনুচ্ছেদ\s*(\d+)',
            r'Section\s*(\d+)',
            r'Schedule\s*(\d+)'
        ]

    def parse_document_structure(self, text: str) -> Dict[str, Any]:
        """Parse complete document structure with proper hierarchy"""
        
        # Clean and normalize text
        text = self._normalize_text(text)
        
        # Detect document type and structure
        doc_info = self._extract_document_info(text)
        
        # Parse hierarchical structure
        chapters = self._parse_chapters(text)
        if not chapters:
            # Fallback to sections if no chapters found
            sections = self._parse_sections(text)
            chapters = [{
                'number': 'একক',
                'title': 'মূল বিষয়বস্তু',
                'sections': sections
            }]
        
        return {
            'header': doc_info,
            'chapters': chapters,
            'structure_quality': self._assess_structure_quality(chapters)
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize text for better parsing"""
        # Remove website noise
        text = re.sub(r'Click here to see.*?version', '', text)
        text = re.sub(r'Note:.*?shall prevail\.', '', text)
        text = re.sub(r'বিশেষ দ্রষ্টব্য:.*', '', text)
        
        # Normalize spacing
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'।\s*', '। ', text)
        
        return text.strip()

    def _extract_document_info(self, text: str) -> Dict[str, Any]:
        """Extract document header information"""
        header = {}
        
        # Extract title patterns
        title_patterns = [
            r'আয়কর আইন[^।]*',
            r'মূল্য সংযোজন কর[^।]*',
            r'কাস্টমস আইন[^।]*',
            r'অর্থ আইন[^।]*',
            r'Income Tax Act[^।]*',
            r'VAT[^।]*'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text)
            if match:
                header['title'] = match.group(0).strip()
                break
        
        # Extract schedule/section info
        if 'তফসিল' in text or 'Schedule' in text:
            schedule_match = re.search(r'(ষষ্ঠ|সপ্তম|অষ্টম|৬ষ্ঠ|৭ম|৮ম)\s*তফসিল', text)
            if schedule_match:
                header['schedule_info'] = schedule_match.group(0)
        
        # Extract law reference
        law_ref = re.search(r'২০২[০-৯]\s*সনের\s*\d+\s*নং\s*আইন', text)
        if law_ref:
            header['law_reference'] = law_ref.group(0)
        
        return header

    def _parse_chapters(self, text: str) -> List[Dict[str, Any]]:
        """Parse chapters with sections"""
        chapters = []
        
        # Find chapter boundaries
        chapter_matches = []
        for pattern in self.section_patterns['chapter']:
            for match in re.finditer(pattern, text):
                chapter_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'number': match.group(1) if match.groups() else match.group(0),
                    'match_text': match.group(0)
                })
        
        if not chapter_matches:
            return []
        
        # Sort by position
        chapter_matches.sort(key=lambda x: x['start'])
        
        # Extract chapter content
        for i, chapter in enumerate(chapter_matches):
            start_pos = chapter['start']
            end_pos = chapter_matches[i + 1]['start'] if i + 1 < len(chapter_matches) else len(text)
            
            chapter_text = text[start_pos:end_pos]
            chapter_title = self._extract_chapter_title(chapter_text)
            
            # Parse sections within this chapter
            sections = self._parse_sections(chapter_text)
            
            chapters.append({
                'number': chapter['number'],
                'title': chapter_title,
                'sections': sections
            })
        
        return chapters

    def _extract_chapter_title(self, chapter_text: str) -> str:
        """Extract clean chapter title"""
        lines = chapter_text.split('\n')
        if lines:
            # Look for title in first few lines
            for line in lines[:3]:
                line = line.strip()
                if line and not re.match(r'^[\d।\(\)]+', line):
                    # Clean the line
                    title = re.sub(r'^[^a-zA-Zঅ-ৱ]*', '', line)
                    if len(title) > 5:
                        return title[:100]
        return "অধ্যায়"

    def _parse_sections(self, text: str) -> List[Dict[str, Any]]:
        """Parse sections with proper hierarchy"""
        sections = []
        
        # Find section boundaries
        section_matches = []
        for pattern in self.section_patterns['section']:
            for match in re.finditer(pattern, text):
                section_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'number': match.group(1) if match.groups() else match.group(0),
                    'pattern': pattern
                })
        
        if not section_matches:
            # Create single section from entire text
            return [{
                'number': '১',
                'title': self._extract_first_meaningful_line(text),
                'content_text': text,
                'subsections': [],
                'clauses': [],
                'tables': []
            }]
        
        # Sort by position
        section_matches.sort(key=lambda x: x['start'])
        
        # Extract section content
        for i, section in enumerate(section_matches):
            start_pos = section['start']
            end_pos = section_matches[i + 1]['start'] if i + 1 < len(section_matches) else len(text)
            
            section_text = text[start_pos:end_pos]
            
            # Extract section components
            section_data = self._parse_section_content(section_text, section['number'])
            sections.append(section_data)
        
        return sections

    def _extract_first_meaningful_line(self, text: str) -> str:
        """Extract first meaningful line as title"""
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not re.match(r'^[\d।\(\)\s]*$', line):
                # Clean and return
                title = re.sub(r'^[\d।\(\)\s]*', '', line).strip()
                return title[:100] if len(title) > 100 else title
        return "বিষয়বস্তু"

    def _parse_section_content(self, section_text: str, section_number: str) -> Dict[str, Any]:
        """Parse individual section with subsections and clauses"""
        
        # Extract title
        title = self._extract_section_title(section_text)
        
        # Parse subsections
        subsections = self._parse_subsections(section_text)
        
        # Parse clauses (if no subsections)
        clauses = self._parse_clauses(section_text) if not subsections else []
        
        # Extract references and amendments
        references = self._extract_references(section_text)
        amendments = self._extract_amendments(section_text)
        
        return {
            'number': section_number,
            'title': title,
            'content_text': section_text.strip(),
            'subsections': subsections,
            'clauses': clauses,
            'tables': [],  # Will be filled by table processor
            'references': references,
            'amendments': amendments
        }

    def _extract_section_title(self, section_text: str) -> str:
        """Extract section title with better logic"""
        lines = section_text.split('\n')
        
        # Look for title patterns
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            
            # Skip empty lines and pure numbers
            if not line or re.match(r'^[\d।\(\)\s]*$', line):
                continue
            
            # Look for title-like patterns
            if re.search(r'[।:]', line):
                # Split on sentence enders and take first part
                parts = re.split(r'[।:]', line)
                if parts[0].strip():
                    title = re.sub(r'^[\d।\(\)\s]*', '', parts[0]).strip()
                    if len(title) > 5:
                        return title[:150]
            
            # Fallback: clean the line
            title = re.sub(r'^[\d।\(\)\s]*', '', line).strip()
            if len(title) > 10:
                return title[:150]
        
        return "ধারা বিষয়বস্তু"

    def _parse_subsections(self, text: str) -> List[Dict[str, Any]]:
        """Parse subsections within a section"""
        subsections = []
        
        # Find subsection patterns
        subsection_matches = []
        for pattern in self.section_patterns['subsection']:
            for match in re.finditer(pattern, text):
                subsection_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'identifier': match.group(1),
                    'pattern': pattern
                })
        
        if not subsection_matches:
            return []
        
        # Sort by position
        subsection_matches.sort(key=lambda x: x['start'])
        
        # Extract subsection content
        for i, subsection in enumerate(subsection_matches):
            start_pos = subsection['start']
            end_pos = subsection_matches[i + 1]['start'] if i + 1 < len(subsection_matches) else len(text)
            
            subsection_text = text[start_pos:end_pos].strip()
            
            # Parse clauses within this subsection
            clauses = self._parse_clauses(subsection_text)
            
            subsections.append({
                'identifier': subsection['identifier'],
                'text': subsection_text,
                'clauses': clauses,
                'tables': []
            })
        
        return subsections

    def _parse_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Parse clauses within a section or subsection"""
        clauses = []
        
        # Find clause patterns
        clause_matches = []
        for pattern in self.section_patterns['clause']:
            for match in re.finditer(pattern, text):
                clause_matches.append({
                    'start': match.start(),
                    'end': match.end(), 
                    'identifier': match.group(1),
                    'pattern': pattern
                })
        
        if not clause_matches:
            return []
        
        # Sort by position
        clause_matches.sort(key=lambda x: x['start'])
        
        # Extract clause content
        for i, clause in enumerate(clause_matches):
            start_pos = clause['start']
            end_pos = clause_matches[i + 1]['start'] if i + 1 < len(clause_matches) else len(text)
            
            clause_text = text[start_pos:end_pos].strip()
            
            # Parse sub-clauses
            sub_clauses = self._parse_sub_clauses(clause_text)
            
            clauses.append({
                'identifier': clause['identifier'],
                'text': clause_text,
                'sub_clauses': sub_clauses,
                'tables': []
            })
        
        return clauses

    def _parse_sub_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Parse sub-clauses within a clause"""
        sub_clauses = []
        
        # Find sub-clause patterns
        for pattern in self.section_patterns['sub_clause']:
            for match in re.finditer(pattern, text):
                sub_clauses.append({
                    'identifier': match.group(1),
                    'text': text[match.start():].split('\n')[0].strip()
                })
        
        return sub_clauses

    def _extract_references(self, text: str) -> List[str]:
        """Extract legal references"""
        references = []
        for pattern in self.reference_patterns:
            matches = re.findall(pattern, text)
            references.extend([f"ধারা {m}" if pattern.startswith(r'ধারা') else m for m in matches])
        return list(set(references))

    def _extract_amendments(self, text: str) -> List[str]:
        """Extract amendment information"""
        amendments = []
        for pattern in self.amendment_patterns:
            if re.search(pattern, text):
                amendments.append(pattern)
        return amendments

    def _assess_structure_quality(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the quality of parsed structure"""
        total_sections = sum(len(chapter.get('sections', [])) for chapter in chapters)
        total_subsections = sum(
            sum(len(section.get('subsections', [])) for section in chapter.get('sections', []))
            for chapter in chapters
        )
        
        return {
            'chapters_count': len(chapters),
            'sections_count': total_sections,
            'subsections_count': total_subsections,
            'quality_score': min(10.0, (total_sections * 2 + total_subsections) / 5),
            'structure_depth': 'chapters->sections->subsections' if total_subsections > 0 else 'chapters->sections'
        }

class ProfessionalLegalContentEnhancer:
    """Professional-grade legal content enhancer"""
    
    def __init__(self):
        self.parser = ProfessionalBengaliLegalParser()
        
    def enhance_file(self, file_path: str) -> Dict[str, Any]:
        """Enhance a single scraped JSON file to professional quality"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('status') != 'success':
                return data
                
            enhanced_data = self._transform_to_professional_format(data)
            return enhanced_data
            
        except Exception as e:
            return {
                'error': f"Enhancement failed: {str(e)}",
                'original_file': file_path,
                'status': 'enhancement_failed'
            }
    
    def _transform_to_professional_format(self, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform to professional legal document format"""
        
        main_content = original_data.get('main_content', '')
        tables = original_data.get('tables', [])
        
        # Parse with professional parser
        parsed_structure = self.parser.parse_document_structure(main_content)
        
        # Integrate tables into appropriate sections
        self._integrate_tables(parsed_structure['chapters'], tables)
        
        # Determine document classification
        doc_classification = self._classify_document(original_data, parsed_structure)
        
        # Build professional structure
        enhanced_data = {
            'header': self._build_professional_header(parsed_structure['header'], doc_classification),
            'chapters': parsed_structure['chapters'],
            'metadata': {
                'source_url': original_data.get('url', ''),
                'original_title': original_data.get('title', ''),
                'enhancement_version': '2.0',
                'enhancement_date': '2025-08-02',
                'document_classification': doc_classification,
                'structure_quality': parsed_structure['structure_quality'],
                'processing_confidence': self._calculate_confidence(parsed_structure)
            },
            'forms': original_data.get('forms', [])
        }
        
        return enhanced_data

    def _build_professional_header(self, parsed_header: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        """Build professional document header"""
        header = {
            'title': parsed_header.get('title', classification['title']),
            'document_type': classification['type'],
            'language': classification['language']
        }
        
        # Add additional header fields based on content
        if 'schedule_info' in parsed_header:
            header['schedule_info'] = parsed_header['schedule_info']
        if 'law_reference' in parsed_header:
            header['ordinance_info'] = parsed_header['law_reference']
        
        return header

    def _classify_document(self, original_data: Dict[str, Any], parsed_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Classify document with enhanced logic"""
        title = original_data.get('title', '').lower()
        url = original_data.get('url', '').lower()
        content = original_data.get('main_content', '').lower()
        
        # Determine document type
        if 'schedule' in url or 'তফসিল' in content:
            doc_type = 'legal_schedule'
        elif 'section' in url or 'ধারা' in content:
            doc_type = 'legal_section'
        elif 'act' in url or 'আইন' in content:
            doc_type = 'legal_act'
        elif 'rules' in url or 'বিধি' in content:
            doc_type = 'legal_rules'
        else:
            doc_type = 'legal_document'
        
        # Determine language
        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', content))
        english_chars = len(re.findall(r'[a-zA-Z]', content))
        total_chars = bengali_chars + english_chars
        
        if total_chars == 0:
            language = 'unknown'
        elif bengali_chars / total_chars > 0.7:
            language = 'bengali'
        elif english_chars / total_chars > 0.7:
            language = 'english'
        else:
            language = 'mixed'
        
        # Generate clean title
        clean_title = self._generate_clean_title(original_data, parsed_structure)
        
        return {
            'type': doc_type,
            'language': language,
            'title': clean_title
        }

    def _generate_clean_title(self, original_data: Dict[str, Any], parsed_structure: Dict[str, Any]) -> str:
        """Generate clean, professional title"""
        original_title = original_data.get('title', '')
        
        # Remove website suffix
        title = re.sub(r'\s*–\s*Tax VAT Point$', '', original_title)
        
        # If we have a better title from parsing, use it
        if 'title' in parsed_structure.get('header', {}):
            parsed_title = parsed_structure['header']['title']
            if len(parsed_title) > len(title):
                title = parsed_title
        
        return title.strip()

    def _integrate_tables(self, chapters: List[Dict[str, Any]], tables: List[Dict[str, Any]]) -> None:
        """Integrate tables into appropriate sections"""
        if not tables:
            return
        
        # For now, add tables to the first section that has content
        for chapter in chapters:
            for section in chapter.get('sections', []):
                if section.get('content_text') and len(section['content_text']) > 100:
                    section['tables'] = self._enhance_tables(tables)
                    return
        
        # Fallback: add to first section
        if chapters and chapters[0].get('sections'):
            chapters[0]['sections'][0]['tables'] = self._enhance_tables(tables)

    def _enhance_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance table metadata"""
        enhanced_tables = []
        
        for i, table in enumerate(tables):
            enhanced_table = {
                'table_id': f"table_{i+1}",
                'headers': table.get('headers', []),
                'data': table.get('data', []),
                'metadata': {
                    'row_count': len(table.get('data', [])),
                    'column_count': len(table.get('headers', [])),
                    'table_type': self._classify_table_type(table)
                }
            }
            enhanced_tables.append(enhanced_table)
        
        return enhanced_tables

    def _classify_table_type(self, table: Dict[str, Any]) -> str:
        """Classify table type based on content"""
        headers_text = ' '.join(table.get('headers', [])).lower()
        
        if 'rate' in headers_text or 'হার' in headers_text or '%' in headers_text:
            return 'tax_rate_table'
        elif 'schedule' in headers_text or 'তফসিল' in headers_text:
            return 'schedule_table'
        elif 'exemption' in headers_text or 'অব্যাহতি' in headers_text:
            return 'exemption_table'
        elif 'year' in headers_text or 'বছর' in headers_text or 'সাল' in headers_text:
            return 'yearly_data_table'
        else:
            return 'general_table'

    def _calculate_confidence(self, parsed_structure: Dict[str, Any]) -> float:
        """Calculate processing confidence based on structure quality"""
        quality = parsed_structure.get('structure_quality', {})
        
        base_confidence = 5.0
        
        # Boost for good structure
        base_confidence += min(quality.get('sections_count', 0) * 0.5, 3.0)
        base_confidence += min(quality.get('subsections_count', 0) * 0.3, 2.0)
        
        # Bonus for deep structure
        if quality.get('structure_depth') == 'chapters->sections->subsections':
            base_confidence += 1.0
        
        return min(base_confidence, 10.0)

def enhance_directory_professional(input_dir: str, output_dir: str) -> Dict[str, Any]:
    """Enhance all JSON files with professional quality"""
    enhancer = ProfessionalLegalContentEnhancer()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = {
        'total_files': 0,
        'successful_enhancements': 0,
        'failed_enhancements': 0,
        'high_quality_files': 0,
        'processing_log': []
    }
    
    for json_file in input_path.glob('*.json'):
        try:
            print(f"Processing: {json_file.name}")
            
            enhanced_data = enhancer.enhance_file(str(json_file))
            
            # Save enhanced file
            output_file = output_path / f"professional_{json_file.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
            
            results['total_files'] += 1
            
            if enhanced_data.get('status') != 'enhancement_failed':
                results['successful_enhancements'] += 1
                confidence = enhanced_data.get('metadata', {}).get('processing_confidence', 0)
                
                if confidence >= 8.0:
                    results['high_quality_files'] += 1
                
                results['processing_log'].append({
                    'file': json_file.name,
                    'status': 'success',
                    'confidence': confidence,
                    'structure_quality': enhanced_data.get('metadata', {}).get('structure_quality', {}),
                    'document_type': enhanced_data.get('metadata', {}).get('document_classification', {}).get('type', 'unknown')
                })
            else:
                results['failed_enhancements'] += 1
                results['processing_log'].append({
                    'file': json_file.name,
                    'status': 'failed',
                    'error': enhanced_data.get('error', 'Unknown error')
                })
                
        except Exception as e:
            results['failed_enhancements'] += 1
            results['processing_log'].append({
                'file': json_file.name,
                'status': 'exception',
                'error': str(e)
            })
    
    # Save comprehensive report
    report_file = output_path / 'professional_enhancement_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n🚀 Professional Enhancement Complete!")
    print(f"Total files: {results['total_files']}")
    print(f"Successful: {results['successful_enhancements']}")
    print(f"High quality (8.0+): {results['high_quality_files']}")
    print(f"Failed: {results['failed_enhancements']}")
    print(f"Success rate: {results['successful_enhancements']/max(results['total_files'], 1)*100:.1f}%")
    print(f"Quality rate: {results['high_quality_files']/max(results['total_files'], 1)*100:.1f}%")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        input_directory = "test_sample"
        output_directory = "professional_test_output"
        print("🧪 TESTING MODE - Professional Enhancement")
    else:
        input_directory = "json_output"
        output_directory = "professional_enhanced_output"
        print("🚀 FULL MODE - Professional Enhancement (1524 Files)")
    
    print("Bangladesh Professional Legal Content Enhancer v2.0")
    print("================================================")
    print(f"Input: {input_directory}")
    print(f"Output: {output_directory}")
    print()
    
    results = enhance_directory_professional(input_directory, output_directory)