#!/usr/bin/env python3
"""
Structured Legal Document Scraper
Preserves chapters, sections, subsections, clauses, subclauses, articles, and footnotes
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class LegalFootnote:
    ref_number: str
    tooltip_text: str
    position_in_text: int
    html: str

@dataclass
class LegalClause:
    number: str
    text: str
    subclauses: List['LegalSubclause']
    html: str

@dataclass
class LegalSubclause:
    identifier: str
    text: str
    html: str

@dataclass
class LegalSubsection:
    number: str
    text: str
    clauses: List[LegalClause]
    html: str

@dataclass
class LegalSection:
    number: str
    title: str
    text: str
    subsections: List[LegalSubsection]
    clauses: List[LegalClause]
    html: str

@dataclass
class LegalChapter:
    number: str
    title: str
    sections: List[LegalSection]
    html: str

@dataclass
class StructuredLegalDocument:
    url: str
    title: str
    preamble: str
    chapters: List[LegalChapter]
    sections: List[LegalSection]  # Sections not in chapters
    footnotes: List[LegalFootnote]
    raw_html: str
    scraped_at: str

class StructuredLegalScraper:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Pattern definitions for structure recognition
        self.patterns = {
            'chapter': [
                r'(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম|নবম|দশম)\s*অধ্যায়',
                r'অধ্যায়\s*[-:]?\s*\d+',
                r'CHAPTER\s+[IVXLCDM]+',
                r'Chapter\s+\d+',
            ],
            'section': [
                r'^\d+\.',  # Numbers followed by period
                r'ধারা\s*[-:]?\s*\d+',
                r'Section\s+\d+',
            ],
            'subsection': [
                r'^\(\d+\)',  # (1), (2), etc.
                r'উপ-ধারা\s*[-:]?\s*\(\d+\)',
            ],
            'clause': [
                r'^\([^\d\)][^\)]*\)',  # (ক), (খ), (গ), etc.
                r'দফা\s*[-:]?\s*\([^\)]+\)',
            ],
            'subclause': [
                r'^\([ivxlcdm]+\)',  # (i), (ii), (iii), etc.
                r'উপ-দফা\s*[-:]?\s*\([ivxlcdm]+\)',
            ]
        }
    
    def identify_element_type(self, text: str) -> str:
        """Identify the type of legal element based on text patterns"""
        text_cleaned = text.strip()
        
        # Check each pattern type
        for element_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_cleaned, re.IGNORECASE):
                    return element_type
        
        return 'content'
    
    def extract_footnotes(self, soup: BeautifulSoup) -> List[LegalFootnote]:
        """Extract footnotes with their references"""
        footnotes = []
        
        # Find all tooltip footnotes
        for i, footnote_elem in enumerate(soup.find_all('a', class_='tooltip')):
            ref_text = footnote_elem.get_text().strip()
            tooltip = footnote_elem.get('title', footnote_elem.get('data-original-title', ''))
            
            footnote = LegalFootnote(
                ref_number=ref_text,
                tooltip_text=tooltip,
                position_in_text=i,
                html=str(footnote_elem)
            )
            footnotes.append(footnote)
        
        return footnotes
    
    def parse_structured_content(self, content_area: BeautifulSoup) -> tuple:
        """Parse content into structured legal elements"""
        
        chapters = []
        sections = []
        current_chapter = None
        current_section = None
        current_subsection = None
        
        # Get all relevant elements
        elements = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'])
        
        preamble_parts = []
        in_preamble = True
        
        for elem in elements:
            text = elem.get_text().strip()
            if not text:
                continue
            
            element_type = self.identify_element_type(text)
            
            if element_type == 'chapter':
                in_preamble = False
                # Extract chapter number and title
                chapter_match = re.search(r'(\d+|প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম)', text)
                chapter_number = chapter_match.group(1) if chapter_match else 'Unknown'
                
                current_chapter = LegalChapter(
                    number=chapter_number,
                    title=text,
                    sections=[],
                    html=str(elem)
                )
                chapters.append(current_chapter)
                current_section = None
                current_subsection = None
                
            elif element_type == 'section':
                in_preamble = False
                # Extract section number
                section_match = re.search(r'(\d+)', text)
                section_number = section_match.group(1) if section_match else 'Unknown'
                
                current_section = LegalSection(
                    number=section_number,
                    title=text,
                    text='',
                    subsections=[],
                    clauses=[],
                    html=str(elem)
                )
                
                if current_chapter:
                    current_chapter.sections.append(current_section)
                else:
                    sections.append(current_section)
                
                current_subsection = None
                
            elif element_type == 'subsection':
                # Extract subsection number
                subsection_match = re.search(r'\((\d+)\)', text)
                subsection_number = subsection_match.group(1) if subsection_match else 'Unknown'
                
                current_subsection = LegalSubsection(
                    number=subsection_number,
                    text=text,
                    clauses=[],
                    html=str(elem)
                )
                
                if current_section:
                    current_section.subsections.append(current_subsection)
                
            elif element_type == 'clause':
                # Extract clause identifier
                clause_match = re.search(r'\(([^\)]+)\)', text)
                clause_id = clause_match.group(1) if clause_match else 'Unknown'
                
                clause = LegalClause(
                    number=clause_id,
                    text=text,
                    subclauses=[],
                    html=str(elem)
                )
                
                if current_subsection:
                    current_subsection.clauses.append(clause)
                elif current_section:
                    current_section.clauses.append(clause)
                
            elif element_type == 'subclause':
                # Extract subclause identifier
                subclause_match = re.search(r'\(([ivxlcdm]+)\)', text)
                subclause_id = subclause_match.group(1) if subclause_match else 'Unknown'
                
                subclause = LegalSubclause(
                    identifier=subclause_id,
                    text=text,
                    html=str(elem)
                )
                
                # Add to the most recent clause
                if (current_subsection and current_subsection.clauses and 
                    current_subsection.clauses[-1].subclauses is not None):
                    current_subsection.clauses[-1].subclauses.append(subclause)
                elif (current_section and current_section.clauses and 
                      current_section.clauses[-1].subclauses is not None):
                    current_section.clauses[-1].subclauses.append(subclause)
                
            else:  # Regular content
                if in_preamble:
                    preamble_parts.append(text)
                elif current_section:
                    if current_section.text:
                        current_section.text += '\n' + text
                    else:
                        current_section.text = text
        
        preamble = '\n'.join(preamble_parts)
        return preamble, chapters, sections
    
    def scrape_document(self, url: str) -> Optional[StructuredLegalDocument]:
        """Scrape a single document with full structure preservation"""
        
        print(f"🔄 Scraping: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = "Unknown Document"
            title_elem = soup.find('section', class_='bg-act-section')
            if title_elem:
                h3_elem = title_elem.find('h3')
                if h3_elem:
                    title = h3_elem.get_text().strip()
            
            # Find main content area
            content_area = soup.find('section', class_='bg-act-section')
            if not content_area:
                content_area = soup.find('div', class_='main-content') or soup.find('main') or soup
            
            # Extract footnotes
            footnotes = self.extract_footnotes(soup)
            
            # Parse structured content
            preamble, chapters, sections = self.parse_structured_content(content_area)
            
            # Create structured document
            document = StructuredLegalDocument(
                url=url,
                title=title,
                preamble=preamble,
                chapters=chapters,
                sections=sections,
                footnotes=footnotes,
                raw_html=str(soup),
                scraped_at=datetime.now().isoformat()
            )
            
            print(f"✅ {title}")
            print(f"   📚 Chapters: {len(chapters)}")
            print(f"   📋 Sections: {len(sections)}")
            print(f"   📝 Footnotes: {len(footnotes)}")
            
            return document
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def save_structured_document(self, document: StructuredLegalDocument, output_dir: str = 'structured_laws'):
        """Save document in structured JSON format"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create clean filename
        clean_title = re.sub(r'[^\w\s-]', '', document.title).strip()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        filename = f"{clean_title}.json"
        
        # Convert dataclasses to dictionaries for JSON serialization
        document_dict = {
            'url': document.url,
            'title': document.title,
            'preamble': document.preamble,
            'chapters': [self._chapter_to_dict(ch) for ch in document.chapters],
            'sections': [self._section_to_dict(sec) for sec in document.sections],
            'footnotes': [self._footnote_to_dict(fn) for fn in document.footnotes],
            'scraped_at': document.scraped_at,
            'structure_summary': {
                'total_chapters': len(document.chapters),
                'total_sections': len(document.sections) + sum(len(ch.sections) for ch in document.chapters),
                'total_footnotes': len(document.footnotes)
            }
        }
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {filepath}")
        
        return filepath
    
    def _chapter_to_dict(self, chapter: LegalChapter) -> Dict:
        return {
            'number': chapter.number,
            'title': chapter.title,
            'sections': [self._section_to_dict(sec) for sec in chapter.sections],
            'html': chapter.html
        }
    
    def _section_to_dict(self, section: LegalSection) -> Dict:
        return {
            'number': section.number,
            'title': section.title,
            'text': section.text,
            'subsections': [self._subsection_to_dict(sub) for sub in section.subsections],
            'clauses': [self._clause_to_dict(clause) for clause in section.clauses],
            'html': section.html
        }
    
    def _subsection_to_dict(self, subsection: LegalSubsection) -> Dict:
        return {
            'number': subsection.number,
            'text': subsection.text,
            'clauses': [self._clause_to_dict(clause) for clause in subsection.clauses],
            'html': subsection.html
        }
    
    def _clause_to_dict(self, clause: LegalClause) -> Dict:
        return {
            'number': clause.number,
            'text': clause.text,
            'subclauses': [self._subclause_to_dict(sub) for sub in clause.subclauses],
            'html': clause.html
        }
    
    def _subclause_to_dict(self, subclause: LegalSubclause) -> Dict:
        return {
            'identifier': subclause.identifier,
            'text': subclause.text,
            'html': subclause.html
        }
    
    def _footnote_to_dict(self, footnote: LegalFootnote) -> Dict:
        return {
            'ref_number': footnote.ref_number,
            'tooltip_text': footnote.tooltip_text,
            'position_in_text': footnote.position_in_text,
            'html': footnote.html
        }

def scrape_urls_from_list(urls: List[str], output_dir: str = 'structured_laws'):
    """Scrape multiple URLs with structure preservation"""
    
    scraper = StructuredLegalScraper()
    
    print(f"🚀 STRUCTURED LEGAL SCRAPER")
    print(f"=" * 50)
    print(f"📋 URLs to scrape: {len(urls)}")
    print(f"📁 Output directory: {output_dir}")
    print(f"=" * 50)
    
    scraped_documents = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]", end=" ")
        
        document = scraper.scrape_document(url)
        if document:
            filepath = scraper.save_structured_document(document, output_dir)
            scraped_documents.append(document)
    
    # Save summary
    summary = {
        'total_urls': len(urls),
        'successful_scrapes': len(scraped_documents),
        'failed_scrapes': len(urls) - len(scraped_documents),
        'documents': [
            {
                'title': doc.title,
                'url': doc.url,
                'chapters': len(doc.chapters),
                'sections': len(doc.sections),
                'footnotes': len(doc.footnotes)
            }
            for doc in scraped_documents
        ],
        'scraped_at': datetime.now().isoformat()
    }
    
    summary_path = os.path.join(output_dir, 'scraping_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 SCRAPING COMPLETE!")
    print(f"📊 Results:")
    print(f"   ✅ Successful: {len(scraped_documents)}/{len(urls)}")
    print(f"   📁 Saved to: {output_dir}/")
    print(f"   📄 Summary: {summary_path}")
    
    return scraped_documents

def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python structured_legal_scraper.py <url1> <url2> ... or --file <urls.txt>")
        print("Example: python structured_legal_scraper.py http://bdlaws.minlaw.gov.bd/act-details-1541.html")
        return
    
    if sys.argv[1] == '--file':
        # Load URLs from file
        if len(sys.argv) < 3:
            print("Please provide a file with URLs")
            return
        
        try:
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"File not found: {sys.argv[2]}")
            return
    else:
        # URLs provided as arguments
        urls = sys.argv[1:]
    
    # Scrape the URLs
    scrape_urls_from_list(urls)

if __name__ == "__main__":
    main()