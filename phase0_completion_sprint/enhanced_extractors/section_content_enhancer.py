#!/usr/bin/env python3
"""
Section Content Enhancer
Enhance existing 269 sections with full content from source file
Phase 0 Completion Sprint - Fill missing content gaps
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class SectionContentEnhancer:
    def __init__(self):
        self.version = "1.0.0"
        self.source_file_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/precise_structured_laws/Income_Tax_act-2023-bangla.txt"
        self.existing_content_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ragflow_organized/phase0_data/phase0_completion_workspace/extracted_content/extracted_legal_content.json"
        
        self.enhancement_stats = {
            'sections_processed': 0,
            'sections_enhanced': 0,
            'content_added_chars': 0,
            'quality_improved': 0
        }

    def enhance_all_sections(self) -> Dict:
        """
        Enhance all existing 269 sections with full content
        """
        print(f"🚀 Starting Section Content Enhancement v{self.version}")
        
        # Load existing content
        existing_data = self.load_existing_content()
        print(f"📊 Found {len(existing_data['sections'])} existing sections")
        
        # Load source file
        source_content = self.load_source_file()
        print(f"📄 Source file loaded: {len(source_content):,} characters")
        
        # Enhance each section
        enhanced_sections = []
        for i, section in enumerate(existing_data['sections']):
            print(f"🔍 Processing section {i+1}/{len(existing_data['sections'])}: {section['section_number']}")
            
            enhanced_section = self.enhance_single_section(section, source_content)
            enhanced_sections.append(enhanced_section)
            
            self.enhancement_stats['sections_processed'] += 1
            if enhanced_section.get('enhanced', False):
                self.enhancement_stats['sections_enhanced'] += 1
        
        # Create enhanced dataset
        enhanced_data = {
            "metadata": {
                "enhancer_version": self.version,
                "source_file": self.source_file_path,
                "enhancement_date": datetime.now().isoformat(),
                "sections_found": len(enhanced_sections),
                "sections_enhanced": self.enhancement_stats['sections_enhanced'],
                "full_content_sections": len([s for s in enhanced_sections if len(s.get('full_content', '')) > 200]),
                "coverage_percentage": (len(enhanced_sections) / 269) * 100,
                "enhancement_method": "content_expansion_and_quality_improvement"
            },
            "sections": enhanced_sections,
            "enhancement_report": self.generate_enhancement_report(enhanced_sections),
            "statistics": self.enhancement_stats
        }
        
        return enhanced_data

    def load_existing_content(self) -> Dict:
        """Load existing extracted content"""
        with open(self.existing_content_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def load_source_file(self) -> str:
        """Load source file content"""
        with open(self.source_file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def enhance_single_section(self, section: Dict, source_content: str) -> Dict:
        """
        Enhance a single section with full content
        """
        enhanced_section = section.copy()
        
        # Extract more complete content based on section number
        section_number = section['section_number']
        
        # Find all references to this section in source
        full_content = self.extract_full_section_content(section_number, source_content)
        
        if full_content and len(full_content) > len(section.get('content_preview', '')):
            enhanced_section['full_content'] = full_content
            enhanced_section['content_length'] = len(full_content)
            enhanced_section['enhanced'] = True
            enhanced_section['enhancement_date'] = datetime.now().isoformat()
            
            # Add quality metrics
            enhanced_section['quality_metrics'] = self.calculate_quality_metrics(full_content)
            
            # Extract legal terms
            enhanced_section['legal_terms'] = self.extract_legal_terms(full_content)
            
            # Add cross-references
            enhanced_section['cross_references'] = self.find_cross_references(full_content)
            
            self.enhancement_stats['content_added_chars'] += len(full_content)
            
            if enhanced_section['quality_metrics']['quality_score'] > 7.0:
                self.enhancement_stats['quality_improved'] += 1
        
        return enhanced_section

    def extract_full_section_content(self, section_number: str, source_content: str) -> str:
        """
        Extract full content for a specific section
        """
        # Multiple patterns to find section content
        section_patterns = [
            f"ধারা {section_number}[^০-৯]*?([^।]*?।)",
            f"ধারা {section_number}[^।]*?([^।]*?।[^।]*?।)",
            f'" {section_number} "[^"]*?"[^"]*?"([^।]*?।)',
            f'" {section_number} "[^।]*?([^।]*?।[^।]*?।[^।]*?।)',
        ]
        
        extracted_content = []
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, source_content, re.DOTALL)
            for match in matches:
                content = match.group(1) if match.groups() else match.group(0)
                content = content.strip()
                
                if len(content) > 50 and content not in extracted_content:
                    extracted_content.append(content)
        
        # Also look for definition patterns
        definition_patterns = [
            f'" [^"]*{section_number}[^"]*" অর্থ ([^;।]*[;।])',
            f'{section_number}[^।]*?অর্থ ([^;।]*[;।])'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, source_content)
            for match in matches:
                definition = match.group(1).strip()
                if len(definition) > 20:
                    extracted_content.append(f"সংজ্ঞা: {definition}")
        
        # Combine all extracted content
        if extracted_content:
            # Remove duplicates and combine
            unique_content = []
            for content in extracted_content:
                if content not in unique_content:
                    unique_content.append(content)
            
            return '\n\n'.join(unique_content)
        
        return ""

    def calculate_quality_metrics(self, content: str) -> Dict:
        """
        Calculate quality metrics for content
        """
        metrics = {
            'character_count': len(content),
            'word_count': len(content.split()),
            'sentence_count': len(re.findall(r'[।!?]', content)),
            'bengali_ratio': 0.0,
            'legal_term_density': 0.0,
            'quality_score': 0.0
        }
        
        # Calculate Bengali character ratio
        bengali_chars = len(re.findall(r'[অ-হ]', content))
        total_chars = len(content.replace(' ', '').replace('\n', ''))
        if total_chars > 0:
            metrics['bengali_ratio'] = bengali_chars / total_chars
        
        # Calculate legal term density
        legal_terms = ['আয়কর', 'করদাতা', 'কর', 'রিটার্ন', 'নির্ধারণী', 'বোর্ড', 'কমিশনার', 'আইন', 'বিধি', 'অর্থ']
        terms_found = sum(1 for term in legal_terms if term in content)
        metrics['legal_term_density'] = terms_found / len(legal_terms)
        
        # Calculate overall quality score
        score = 0.0
        
        # Length score (0-4 points)
        if metrics['character_count'] >= 500:
            score += 4
        elif metrics['character_count'] >= 300:
            score += 3
        elif metrics['character_count'] >= 150:
            score += 2
        else:
            score += 1
        
        # Bengali content score (0-3 points)
        score += metrics['bengali_ratio'] * 3
        
        # Legal term score (0-2 points)  
        score += metrics['legal_term_density'] * 2
        
        # Structure score (0-1 point)
        if metrics['sentence_count'] >= 2:
            score += 1
        
        metrics['quality_score'] = min(score, 10.0)
        
        return metrics

    def extract_legal_terms(self, content: str) -> List[str]:
        """
        Extract legal terms from content
        """
        legal_terms_patterns = [
            'আয়কর', 'করদাতা', 'কর কমিশনার', 'বোর্ড', 'রিটার্ন', 'নির্ধারণী',
            'উৎসে কর', 'অগ্রিম কর', 'ন্যূনতম কর', 'সারচার্জ', 'জরিমানা',
            'আবেদন', 'আপিল', 'ট্রাইব্যুনাল', 'নোটিশ', 'নির্দেশনা'
        ]
        
        found_terms = []
        for term in legal_terms_patterns:
            if term in content:
                found_terms.append(term)
        
        return found_terms

    def find_cross_references(self, content: str) -> List[Dict]:
        """
        Find cross-references in content
        """
        cross_ref_patterns = [
            r'ধারা (\d+)',
            r'তফসিল (\d+)',
            r'অংশ (\d+)',
            r'অনুচ্ছেদ (\d+)'
        ]
        
        references = []
        for pattern in cross_ref_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                ref_type = pattern.split('(')[0].strip().replace('\\', '')
                ref_number = match.group(1)
                references.append({
                    'type': ref_type,
                    'number': ref_number,
                    'context': content[max(0, match.start()-30):match.end()+30].strip()
                })
        
        return references

    def generate_enhancement_report(self, enhanced_sections: List[Dict]) -> Dict:
        """
        Generate enhancement report
        """
        sections_with_full_content = [s for s in enhanced_sections if s.get('full_content')]
        high_quality_sections = [s for s in enhanced_sections if s.get('quality_metrics', {}).get('quality_score', 0) >= 8.0]
        enhanced_sections_count = [s for s in enhanced_sections if s.get('enhanced', False)]
        
        report = {
            'enhancement_summary': {
                'total_sections': len(enhanced_sections),
                'sections_with_full_content': len(sections_with_full_content),
                'high_quality_sections': len(high_quality_sections),
                'enhanced_sections': len(enhanced_sections_count),
                'content_coverage_percentage': (len(sections_with_full_content) / len(enhanced_sections)) * 100 if enhanced_sections else 0,
                'quality_coverage_percentage': (len(high_quality_sections) / len(enhanced_sections)) * 100 if enhanced_sections else 0
            },
            'quality_distribution': {
                'excellent_quality': len([s for s in enhanced_sections if s.get('quality_metrics', {}).get('quality_score', 0) >= 9.0]),
                'good_quality': len([s for s in enhanced_sections if 7.0 <= s.get('quality_metrics', {}).get('quality_score', 0) < 9.0]),
                'fair_quality': len([s for s in enhanced_sections if 5.0 <= s.get('quality_metrics', {}).get('quality_score', 0) < 7.0]),
                'poor_quality': len([s for s in enhanced_sections if s.get('quality_metrics', {}).get('quality_score', 0) < 5.0])
            },
            'content_statistics': {
                'total_characters_added': self.enhancement_stats['content_added_chars'],
                'average_section_length': sum(len(s.get('full_content', '')) for s in sections_with_full_content) / len(sections_with_full_content) if sections_with_full_content else 0,
                'sections_with_legal_terms': len([s for s in enhanced_sections if s.get('legal_terms')]),
                'sections_with_cross_references': len([s for s in enhanced_sections if s.get('cross_references')])
            }
        }
        
        return report

    def save_enhanced_content(self, enhanced_data: Dict, output_path: str) -> str:
        """
        Save enhanced content
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(enhanced_data, file, ensure_ascii=False, indent=2)
        
        print(f"💾 Enhanced content saved to: {output_path}")
        print(f"📊 Total sections: {enhanced_data['metadata']['sections_found']}")
        print(f"🎯 Enhanced sections: {enhanced_data['metadata']['sections_enhanced']}")
        print(f"📈 Full content sections: {enhanced_data['metadata']['full_content_sections']}")
        
        return output_path

def main():
    """
    Main execution function
    """
    enhancer = SectionContentEnhancer()
    
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/phase0_completion_sprint/expanded_data/fully_enhanced_legal_content.json"
    
    try:
        print("🚀 Starting Section Enhancement...")
        enhanced_data = enhancer.enhance_all_sections()
        
        saved_path = enhancer.save_enhanced_content(enhanced_data, output_file)
        
        print("\n" + "="*60)
        print("✅ SECTION ENHANCEMENT COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"📊 Total sections: {enhanced_data['metadata']['sections_found']}")
        print(f"🎯 Enhanced sections: {enhanced_data['metadata']['sections_enhanced']}")
        print(f"📈 Full content sections: {enhanced_data['metadata']['full_content_sections']}")
        print(f"📋 Coverage: {enhanced_data['metadata']['coverage_percentage']:.1f}%")
        print("="*60)
        
        return enhanced_data
        
    except Exception as e:
        print(f"❌ Error during enhancement: {str(e)}")
        raise

if __name__ == "__main__":
    main()