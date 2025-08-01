#!/usr/bin/env python3
"""
Enhanced Legal Content Extractor v2.0
Advanced pattern recognition for complete Bengali legal text extraction
Phase 0 Completion Sprint - Target: 95%+ section coverage
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class EnhancedLegalExtractorV2:
    def __init__(self):
        self.version = "2.0.0"
        self.extraction_patterns = {
            'section_headers': [
                r'ধারা\s+(\d+)\.?',
                r'অনুচ্ছেদ\s+(\d+)\.?',
                r'Section\s+(\d+)\.?',
                r'(\d+)\s*\.\s*([ক-হ])',
                r'তফসিল\s+(\d+)',
                r'অংশ\s+(\d+)',
                r'অধ্যায়\s+(\d+)',
                r'পরিচ্ছেদ\s+(\d+)',
                r'উপধারা\s*\(([০-৯\d]+)\)',
                r'\(([০-৯\d]+)\)\s*[ক-হ]?'
            ],
            'content_patterns': [
                r'"([^"]+)"\s*অর্থ\s+([^;।]+)[;।]',
                r'অর্থ\s+([^;।]+)[;।]',
                r'বিধান\s+([^।]+)।',
                r'শর্ত\s+([^।]+)।',
                r'ব্যাখ্যা\s+([^।]+)।',
                r'নিয়ম\s+([^।]+)।',
                r'পদ্ধতি\s+([^।]+)।',
                r'প্রক্রিয়া\s+([^।]+)।'
            ],
            'cross_references': [
                r'ধারা\s+(\d+)\s*এর\s+অধীন',
                r'তফসিল\s+(\d+)\s*অনুযায়ী',
                r'অংশ\s+(\d+)\s*এর\s+বিধান',
                r'উপধারা\s*\((\d+)\)\s*অনুসারে',
                r'অনুচ্ছেদ\s+(\d+)\s*মতে'
            ],
            'legal_terms': [
                r'করদাতা',
                r'আয়কর',
                r'নির্ধারণী',
                r'রিটার্ন',
                r'কর\s+কর্তনকারী',
                r'কর\s+কমিশনার',
                r'বোর্ড',
                r'সরকার',
                r'আইন',
                r'বিধি',
                r'নির্দেশনা'
            ]
        }
        
        self.content_quality_thresholds = {
            'minimum_length': 100,
            'maximum_length': 10000,
            'required_bengali_ratio': 0.7
        }
        
        self.extraction_stats = {
            'total_sections_found': 0,
            'sections_with_content': 0,
            'missing_sections': [],
            'quality_sections': 0,
            'cross_references_found': 0
        }

    def extract_complete_legal_content(self, source_file_path: str) -> Dict:
        """
        Enhanced extraction with complete section coverage
        """
        print(f"🚀 Starting Enhanced Legal Extraction v{self.version}")
        print(f"📄 Source: {source_file_path}")
        
        if not os.path.exists(source_file_path):
            raise FileNotFoundError(f"Source file not found: {source_file_path}")
        
        # Read source file
        with open(source_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"📊 File size: {len(content):,} characters")
        
        # Enhanced section extraction
        sections = self._extract_sections_with_context(content)
        
        # Quality enhancement
        enhanced_sections = self._enhance_section_quality(sections, content)
        
        # Cross-reference mapping
        cross_references = self._map_cross_references(enhanced_sections, content)
        
        # Generate extraction report
        extraction_report = self._generate_extraction_report(enhanced_sections)
        
        result = {
            "metadata": {
                "extractor_version": self.version,
                "source_file": source_file_path,
                "extraction_date": datetime.now().isoformat(),
                "total_sections": len(enhanced_sections),
                "quality_sections": self.extraction_stats['quality_sections'],
                "coverage_percentage": (len(enhanced_sections) / 269) * 100 if enhanced_sections else 0,
                "extraction_method": "enhanced_pattern_matching_v2"
            },
            "sections": enhanced_sections,
            "cross_references": cross_references,
            "extraction_report": extraction_report,
            "statistics": self.extraction_stats
        }
        
        return result

    def _extract_sections_with_context(self, content: str) -> List[Dict]:
        """
        Extract sections with surrounding context for better quality
        """
        sections = []
        section_id = 0
        
        # Split content into manageable chunks
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                continue
            
            # Check for section headers
            section_match = self._identify_section_header(line)
            if section_match:
                # Save previous section if exists
                if current_section and section_content:
                    full_content = '\n'.join(section_content)
                    if self._is_quality_content(full_content):
                        sections.append({
                            'section_number': current_section['number'],
                            'title': current_section['title'],
                            'content': full_content,
                            'content_preview': full_content[:200] + "..." if len(full_content) > 200 else full_content,
                            'line_number': current_section['line'],
                            'character_count': len(full_content),
                            'quality_score': self._calculate_quality_score(full_content),
                            'type': 'enhanced_section'
                        })
                        self.extraction_stats['quality_sections'] += 1
                
                # Start new section
                current_section = {
                    'number': section_match['number'],
                    'title': section_match['title'],
                    'line': i
                }
                section_content = [line]
                section_id += 1
            
            elif current_section:
                # Add content to current section
                section_content.append(line)
                
                # Stop if we hit another major section
                if len(section_content) > 100 and self._is_major_break(line):
                    break
        
        # Handle last section
        if current_section and section_content:
            full_content = '\n'.join(section_content)
            if self._is_quality_content(full_content):
                sections.append({
                    'section_number': current_section['number'],
                    'title': current_section['title'],
                    'content': full_content,
                    'content_preview': full_content[:200] + "..." if len(full_content) > 200 else full_content,
                    'line_number': current_section['line'],
                    'character_count': len(full_content),
                    'quality_score': self._calculate_quality_score(full_content),
                    'type': 'enhanced_section'
                })
        
        self.extraction_stats['total_sections_found'] = len(sections)
        self.extraction_stats['sections_with_content'] = len([s for s in sections if len(s['content']) > 50])
        
        print(f"✅ Extracted {len(sections)} sections with enhanced quality")
        return sections

    def _identify_section_header(self, line: str) -> Optional[Dict]:
        """
        Identify section headers with enhanced pattern matching
        """
        for pattern in self.extraction_patterns['section_headers']:
            match = re.search(pattern, line)
            if match:
                return {
                    'number': match.group(1) if match.groups() else 'unknown',
                    'title': line.replace(match.group(0), '').strip()[:100],
                    'pattern_used': pattern
                }
        return None

    def _is_quality_content(self, content: str) -> bool:
        """
        Determine if content meets quality thresholds
        """
        if len(content) < self.content_quality_thresholds['minimum_length']:
            return False
        
        if len(content) > self.content_quality_thresholds['maximum_length']:
            return False
        
        # Check Bengali character ratio
        bengali_chars = len(re.findall(r'[অ-হ]', content))
        total_chars = len(content.replace(' ', '').replace('\n', ''))
        
        if total_chars > 0:
            bengali_ratio = bengali_chars / total_chars
            if bengali_ratio < self.content_quality_thresholds['required_bengali_ratio']:
                return False
        
        return True

    def _calculate_quality_score(self, content: str) -> float:
        """
        Calculate quality score for content
        """
        score = 0.0
        
        # Length score (0-3 points)
        if len(content) >= 200:
            score += 3
        elif len(content) >= 100:
            score += 2
        else:
            score += 1
        
        # Bengali content score (0-3 points)
        bengali_chars = len(re.findall(r'[অ-হ]', content))
        total_chars = len(content.replace(' ', '').replace('\n', ''))
        if total_chars > 0:
            bengali_ratio = bengali_chars / total_chars
            score += bengali_ratio * 3
        
        # Legal term density (0-2 points)
        legal_terms_found = 0
        for term in self.extraction_patterns['legal_terms']:
            if re.search(term, content):
                legal_terms_found += 1
        score += min(legal_terms_found / len(self.extraction_patterns['legal_terms']) * 2, 2)
        
        # Structure score (0-2 points)
        if re.search(r'[।;:]', content):
            score += 1
        if re.search(r'[ক-হ]\)', content):
            score += 1
        
        return min(score, 10.0)

    def _enhance_section_quality(self, sections: List[Dict], full_content: str) -> List[Dict]:
        """
        Enhance section quality with additional content extraction
        """
        enhanced_sections = []
        
        for section in sections:
            enhanced_section = section.copy()
            
            # Try to extract more content if section is too short
            if len(section['content']) < 200:
                additional_content = self._extract_additional_content(
                    section, full_content
                )
                if additional_content:
                    enhanced_section['content'] += '\n\n' + additional_content
                    enhanced_section['enhanced'] = True
            
            # Add legal interpretations if found
            interpretations = self._extract_interpretations(section['content'])
            if interpretations:
                enhanced_section['interpretations'] = interpretations
            
            # Add examples if found
            examples = self._extract_examples(section['content'])
            if examples:
                enhanced_section['examples'] = examples
            
            enhanced_sections.append(enhanced_section)
        
        return enhanced_sections

    def _extract_additional_content(self, section: Dict, full_content: str) -> str:
        """
        Extract additional related content for short sections
        """
        section_number = section['section_number']
        
        # Look for subsections
        subsection_pattern = f"({section_number}[ক-হ]|{section_number}\\([০-৯\\d]+\\))"
        subsection_matches = re.finditer(subsection_pattern, full_content)
        
        additional_content = []
        for match in subsection_matches:
            start = match.start()
            # Extract 500 characters after the match
            end = min(start + 500, len(full_content))
            subsection_text = full_content[start:end]
            
            # Clean and add if quality
            if self._is_quality_content(subsection_text):
                additional_content.append(subsection_text.strip())
        
        return '\n\n'.join(additional_content) if additional_content else ""

    def _extract_interpretations(self, content: str) -> List[str]:
        """
        Extract legal interpretations and explanations
        """
        interpretation_patterns = [
            r'ব্যাখ্যা[:\s]*([^।]+)।',
            r'অর্থাৎ[:\s]*([^।]+)।',
            r'উদাহরণ[:\s]*([^।]+)।'
        ]
        
        interpretations = []
        for pattern in interpretation_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                interpretations.append(match.group(1).strip())
        
        return interpretations

    def _extract_examples(self, content: str) -> List[str]:
        """
        Extract examples and illustrations
        """
        example_patterns = [
            r'যেমন[:\s]*([^।]+)।',
            r'দৃষ্টান্ত[:\s]*([^।]+)।',
            r'উদাহরণস্বরূপ[:\s]*([^।]+)।'
        ]
        
        examples = []
        for pattern in example_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                examples.append(match.group(1).strip())
        
        return examples

    def _map_cross_references(self, sections: List[Dict], full_content: str) -> Dict:
        """
        Map cross-references between sections
        """
        cross_refs = {}
        
        for section in sections:
            section_refs = []
            
            for pattern in self.extraction_patterns['cross_references']:
                matches = re.finditer(pattern, section['content'])
                for match in matches:
                    ref_info = {
                        'reference': match.group(0),
                        'referenced_section': match.group(1) if match.groups() else 'unknown',
                        'context': self._get_reference_context(match, section['content'])
                    }
                    section_refs.append(ref_info)
            
            if section_refs:
                cross_refs[section['section_number']] = section_refs
                self.extraction_stats['cross_references_found'] += len(section_refs)
        
        return cross_refs

    def _get_reference_context(self, match, content: str) -> str:
        """
        Get context around a cross-reference
        """
        start = max(0, match.start() - 50)
        end = min(len(content), match.end() + 50)
        return content[start:end].strip()

    def _is_major_break(self, line: str) -> bool:
        """
        Identify major section breaks
        """
        major_break_patterns = [
            r'^অংশ\s+\d+',
            r'^অধ্যায়\s+\d+',
            r'^তফসিল\s+\d+'
        ]
        
        for pattern in major_break_patterns:
            if re.match(pattern, line):
                return True
        return False

    def _generate_extraction_report(self, sections: List[Dict]) -> Dict:
        """
        Generate comprehensive extraction report
        """
        total_characters = sum(len(s['content']) for s in sections)
        quality_sections = [s for s in sections if s.get('quality_score', 0) >= 7.0]
        
        report = {
            'extraction_summary': {
                'total_sections_extracted': len(sections),
                'quality_sections': len(quality_sections),
                'total_content_characters': total_characters,
                'average_section_length': total_characters / len(sections) if sections else 0,
                'coverage_target': 269,
                'coverage_achieved': len(sections),
                'coverage_percentage': (len(sections) / 269) * 100,
                'missing_sections_count': max(0, 269 - len(sections))
            },
            'quality_analysis': {
                'high_quality_sections': len([s for s in sections if s.get('quality_score', 0) >= 8.0]),
                'medium_quality_sections': len([s for s in sections if 5.0 <= s.get('quality_score', 0) < 8.0]),
                'low_quality_sections': len([s for s in sections if s.get('quality_score', 0) < 5.0]),
                'average_quality_score': sum(s.get('quality_score', 0) for s in sections) / len(sections) if sections else 0
            },
            'content_analysis': {
                'sections_with_interpretations': len([s for s in sections if s.get('interpretations')]),
                'sections_with_examples': len([s for s in sections if s.get('examples')]),
                'cross_references_found': self.extraction_stats['cross_references_found'],
                'enhanced_sections': len([s for s in sections if s.get('enhanced')])
            }
        }
        
        return report

    def save_extracted_content(self, extracted_data: Dict, output_path: str) -> str:
        """
        Save extracted content with enhanced formatting
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(extracted_data, file, ensure_ascii=False, indent=2)
        
        print(f"💾 Enhanced extraction saved to: {output_path}")
        print(f"📊 Sections extracted: {len(extracted_data['sections'])}")
        print(f"📈 Coverage: {extracted_data['metadata']['coverage_percentage']:.1f}%")
        
        return output_path

def main():
    """
    Main execution function
    """
    extractor = EnhancedLegalExtractorV2()
    
    # Source file path
    source_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precise_structured_laws/Income_Tax_act-2023-bangla.txt"
    
    # Output path
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/phase0_completion_sprint/expanded_data/enhanced_legal_content_v2.json"
    
    try:
        # Extract content
        print("🚀 Starting Enhanced Legal Extraction...")
        extracted_data = extractor.extract_complete_legal_content(source_file)
        
        # Save results
        saved_path = extractor.save_extracted_content(extracted_data, output_file)
        
        # Print success report
        print("\n" + "="*60)
        print("✅ ENHANCED EXTRACTION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"📄 Source processed: {source_file}")
        print(f"💾 Results saved: {saved_path}")
        print(f"📊 Total sections: {extracted_data['metadata']['total_sections']}")
        print(f"📈 Coverage: {extracted_data['metadata']['coverage_percentage']:.1f}%")
        print(f"🎯 Quality sections: {extracted_data['metadata']['quality_sections']}")
        print("="*60)
        
        return extracted_data
        
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        raise

if __name__ == "__main__":
    main()