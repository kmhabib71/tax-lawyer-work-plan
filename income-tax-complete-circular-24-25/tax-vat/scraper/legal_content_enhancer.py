#!/usr/bin/env python3
"""
Legal Content Enhancer for Bangladesh Tax Law Files
==================================================

This script enhances the 1500+ scraped files to match the structured format
of the main data assets while preserving excellent table extraction.

Author: AI Tax Lawyer Bangladesh Project
Date: August 2025
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class BengaliLegalParser:
    """Bengali legal text parser with section detection"""
    
    def __init__(self):
        self.section_patterns = [
            r'ধারা\s*(\d+)',           # Section numbers
            r'অনুচ্ছেদ\s*(\d+)',       # Article numbers  
            r'উপ-ধারা\s*\((\d+)\)',   # Sub-sections
            r'দফা\s*\(([^)]+)\)',      # Clauses
            r'অংশ\s*(\d+)',           # Parts
            r'তফসিল\s*(\d+)',         # Schedules
            r'বিধি\s*(\d+)',          # Rules
            r'অধ্যায়\s*(\d+)',        # Chapters
        ]
        
        self.amendment_patterns = [
            r'সংশোধিত',               # Amended
            r'বিলুপ্ত',                # Deleted
            r'প্রতিস্থাপিত',           # Replaced
            r'সংযোজিত',               # Added
        ]
        
        self.reference_patterns = [
            r'ধারা\s*(\d+)',
            r'তফসিল\s*(\d+)',
            r'বিধি\s*(\d+)',
            r'অনুচ্ছেদ\s*(\d+)',
        ]

    def detect_legal_structure(self, text: str) -> Dict[str, Any]:
        """Detect legal structure in Bengali text"""
        structure = {
            'sections': [],
            'subsections': [],
            'clauses': [],
            'amendments': [],
            'references': [],
            'schedules': []
        }
        
        # Find sections
        for pattern in self.section_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                section_type = pattern.split('\\')[0]  # Get the Bengali term
                section_number = match.group(1)
                start_pos = match.start()
                
                structure['sections'].append({
                    'type': section_type,
                    'number': section_number,
                    'position': start_pos,
                    'match_text': match.group(0)
                })
        
        # Find amendments
        for pattern in self.amendment_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                structure['amendments'].append({
                    'type': match.group(0),
                    'position': match.start(),
                    'context': text[max(0, match.start()-50):match.end()+50]
                })
        
        # Find references
        for pattern in self.reference_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                structure['references'].append({
                    'reference': match.group(0),
                    'position': match.start()
                })
        
        return structure

    def split_into_sections(self, text: str, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into logical sections based on detected structure"""
        sections = []
        section_markers = structure['sections']
        
        if not section_markers:
            # If no sections found, return as single content block
            return [{
                'type': 'content',
                'title': 'মূল বিষয়বস্তু',
                'content': text,
                'structure_info': structure
            }]
        
        # Sort sections by position
        section_markers.sort(key=lambda x: x['position'])
        
        for i, section in enumerate(section_markers):
            start_pos = section['position']
            end_pos = section_markers[i + 1]['position'] if i + 1 < len(section_markers) else len(text)
            
            section_text = text[start_pos:end_pos].strip()
            
            sections.append({
                'type': section['type'],
                'number': section['number'],
                'title': self._extract_section_title(section_text),
                'content': section_text,
                'amendments': self._find_amendments_in_range(structure['amendments'], start_pos, end_pos),
                'references': self._find_references_in_range(structure['references'], start_pos, end_pos)
            })
        
        return sections

    def _extract_section_title(self, section_text: str) -> str:
        """Extract section title from text"""
        lines = section_text.split('\n')
        if len(lines) > 0:
            # First line is often the title
            title = lines[0].strip()
            # Remove the section number part
            title = re.sub(r'^[^।]+।', '', title).strip()
            return title[:100] if len(title) > 100 else title
        return "শিরোনাম নেই"

    def _find_amendments_in_range(self, amendments: List[Dict], start_pos: int, end_pos: int) -> List[Dict]:
        """Find amendments within a specific text range"""
        return [a for a in amendments if start_pos <= a['position'] <= end_pos]

    def _find_references_in_range(self, references: List[Dict], start_pos: int, end_pos: int) -> List[Dict]:
        """Find references within a specific text range"""
        return [r for r in references if start_pos <= r['position'] <= end_pos]

class LegalContentEnhancer:
    """Main enhancer class for processing scraped legal files"""
    
    def __init__(self):
        self.parser = BengaliLegalParser()
        
    def enhance_file(self, file_path: str) -> Dict[str, Any]:
        """Enhance a single scraped JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('status') != 'success':
                return data  # Return unchanged if failed
                
            enhanced_data = self._transform_to_structured_format(data)
            return enhanced_data
            
        except Exception as e:
            return {
                'error': f"Enhancement failed: {str(e)}",
                'original_file': file_path,
                'status': 'enhancement_failed'
            }
    
    def _transform_to_structured_format(self, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform original scraped data to structured legal format"""
        
        main_content = original_data.get('main_content', '')
        tables = original_data.get('tables', [])
        
        # Parse legal structure
        structure = self.parser.detect_legal_structure(main_content)
        sections = self.parser.split_into_sections(main_content, structure)
        
        # Determine document type from title or URL
        doc_type = self._classify_document_type(original_data.get('title', ''), original_data.get('url', ''))
        
        enhanced_data = {
            'metadata': {
                'source_url': original_data.get('url', ''),
                'original_title': original_data.get('title', ''),
                'document_type': doc_type,
                'enhancement_version': '1.0',
                'enhancement_date': '2025-08-02',
                'structure_detected': {
                    'sections_count': len(structure['sections']),
                    'amendments_count': len(structure['amendments']),
                    'references_count': len(structure['references']),
                    'tables_count': len(tables)
                }
            },
            
            'header': {
                'title': self._clean_title(original_data.get('title', '')),
                'document_type': doc_type,
                'source': 'taxvatpoint.com',
                'language': 'bengali' if self._is_bengali_content(main_content) else 'mixed'
            },
            
            'content': {
                'sections': self._format_sections(sections),
                'tables': self._enhance_tables(tables),
                'legal_structure': structure,
                'full_text': main_content  # Preserve original for fallback
            },
            
            'forms': original_data.get('forms', []),
            
            'quality_metrics': {
                'content_length': len(main_content),
                'structure_richness': self._calculate_structure_richness(structure),
                'table_richness': len(tables),
                'enhancement_confidence': self._calculate_enhancement_confidence(structure, tables, main_content)
            }
        }
        
        return enhanced_data
    
    def _classify_document_type(self, title: str, url: str) -> str:
        """Classify document type based on title and URL"""
        title_lower = title.lower()
        url_lower = url.lower()
        
        if 'income-tax' in url_lower or 'আয়কর' in title:
            if 'schedule' in url_lower or 'তফসিল' in title:
                return 'income_tax_schedule'
            elif 'section' in url_lower or 'ধারা' in title:
                return 'income_tax_section'
            else:
                return 'income_tax_general'
        elif 'vat' in url_lower or 'ভ্যাট' in title or 'মূল্য সংযোজন কর' in title:
            return 'vat_related'
        elif 'tds' in url_lower or 'উৎসে কর' in title:
            return 'tds_rules'
        elif 'customs' in url_lower or 'কাস্টমস' in title:
            return 'customs_related'
        elif 'sro' in url_lower:
            return 'statutory_regulatory_order'
        else:
            return 'general_legal_document'
    
    def _clean_title(self, title: str) -> str:
        """Clean and standardize title"""
        # Remove website suffix
        title = re.sub(r'\s*–\s*Tax VAT Point$', '', title)
        return title.strip()
    
    def _is_bengali_content(self, text: str) -> bool:
        """Check if content is primarily in Bengali"""
        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
        total_chars = len(re.findall(r'[a-zA-Z\u0980-\u09FF]', text))
        return bengali_chars / max(total_chars, 1) > 0.5
    
    def _format_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sections to match target structure"""
        formatted_sections = []
        
        for section in sections:
            formatted_section = {
                'number': section.get('number', ''),
                'title': section.get('title', ''),
                'content_text': section.get('content', ''),
                'type': section.get('type', 'content'),
                'subsections': [],  # Will be populated if detected
                'clauses': [],     # Will be populated if detected  
                'amendments': section.get('amendments', []),
                'references': section.get('references', [])
            }
            formatted_sections.append(formatted_section)
        
        return formatted_sections
    
    def _enhance_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance table data with better structure"""
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
        """Classify table type based on headers"""
        headers = ' '.join(table.get('headers', [])).lower()
        
        if 'rate' in headers or 'হার' in headers:
            return 'tax_rate_table'
        elif 'schedule' in headers or 'তফসিল' in headers:
            return 'schedule_table'
        elif 'exemption' in headers or 'অব্যাহতি' in headers:
            return 'exemption_table'
        else:
            return 'general_table'
    
    def _calculate_structure_richness(self, structure: Dict[str, Any]) -> float:
        """Calculate how rich the detected structure is"""
        score = 0
        score += min(len(structure['sections']) * 0.3, 3.0)
        score += min(len(structure['amendments']) * 0.2, 2.0)
        score += min(len(structure['references']) * 0.1, 1.0)
        return min(score, 10.0)
    
    def _calculate_enhancement_confidence(self, structure: Dict[str, Any], tables: List, content: str) -> float:
        """Calculate confidence in enhancement quality"""
        confidence = 5.0  # Base confidence
        
        # Boost confidence based on detected elements
        if len(structure['sections']) > 0:
            confidence += 2.0
        if len(tables) > 0:
            confidence += 2.0
        if len(structure['amendments']) > 0:
            confidence += 0.5
        if len(structure['references']) > 0:
            confidence += 0.5
        if len(content) > 1000:
            confidence += 1.0
            
        return min(confidence, 10.0)

def enhance_directory(input_dir: str, output_dir: str) -> Dict[str, Any]:
    """Enhance all JSON files in a directory"""
    enhancer = LegalContentEnhancer()
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = {
        'total_files': 0,
        'successful_enhancements': 0,
        'failed_enhancements': 0,
        'processing_log': []
    }
    
    for json_file in input_path.glob('*.json'):
        try:
            print(f"Enhancing: {json_file.name}")
            
            enhanced_data = enhancer.enhance_file(str(json_file))
            
            # Save enhanced file
            output_file = output_path / f"enhanced_{json_file.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
            
            results['total_files'] += 1
            
            if enhanced_data.get('status') != 'enhancement_failed':
                results['successful_enhancements'] += 1
                confidence = enhanced_data.get('quality_metrics', {}).get('enhancement_confidence', 0)
                results['processing_log'].append({
                    'file': json_file.name,
                    'status': 'success',
                    'confidence': confidence
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
    
    # Save processing report
    report_file = output_path / 'enhancement_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nEnhancement Complete!")
    print(f"Total files: {results['total_files']}")
    print(f"Successful: {results['successful_enhancements']}")
    print(f"Failed: {results['failed_enhancements']}")
    print(f"Success rate: {results['successful_enhancements']/max(results['total_files'], 1)*100:.1f}%")
    
    return results

if __name__ == "__main__":
    # Example usage
    input_directory = "json_output"
    output_directory = "enhanced_output"
    
    print("Bangladesh Tax Law Content Enhancer")
    print("==================================")
    print(f"Input: {input_directory}")
    print(f"Output: {output_directory}")
    print()
    
    results = enhance_directory(input_directory, output_directory)