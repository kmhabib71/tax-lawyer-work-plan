#!/usr/bin/env python3
"""
FIXED Structured Legal Document Scraper
Uses the correct content area and improved pattern matching
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class TableCell:
    content: str
    colspan: int
    rowspan: int
    is_header: bool

@dataclass
class TableRow:
    cells: List[TableCell]
    row_number: int

@dataclass
class LegalTable:
    caption: str
    headers: List[str]
    rows: List[TableRow]
    total_columns: int
    total_rows: int
    context: str

@dataclass
class LegalFootnote:
    ref_number: str
    tooltip_text: str
    position_in_text: int

@dataclass
class LegalElement:
    type: str  # chapter, section, subsection, clause, subclause, content
    number: str
    title: str
    text: str
    children: List['LegalElement']
    tables: List[LegalTable]

@dataclass
class StructuredLegalDocument:
    url: str
    title: str
    preamble: str
    structure: List[LegalElement]
    all_tables: List[LegalTable]
    footnotes: List[LegalFootnote]
    scraped_at: str

class FixedStructuredScraper:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def find_best_content_area(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Find the content area with the most legal content"""
        
        candidates = [
            soup.find('div', class_='container'),
            soup.find('section', class_='bg-striped'),
            soup.find('section', class_='padding-bottom-20'),
            soup.find('div', class_='main-content'),
            soup.find('main'),
            soup.find('body')
        ]
        
        best_candidate = None
        best_score = 0
        
        for candidate in candidates:
            if not candidate:
                continue
            
            text_content = candidate.get_text()
            
            # Score based on legal indicators
            bengali_keywords = ['ধারা', 'অধ্যায়', 'দফা', 'উপ-ধারা', 'অনুচ্ছেদ', 'বিধান']
            keyword_count = sum(1 for keyword in bengali_keywords if keyword in text_content)
            
            section_matches = len(re.findall(r'\d+\.', text_content))
            tables = len(candidate.find_all('table'))
            footnotes = len(candidate.find_all('a', class_='tooltip'))
            
            score = keyword_count * 10 + section_matches * 0.1 + tables * 15 + footnotes * 2
            
            if score > best_score:
                best_score = score
                best_candidate = candidate
        
        return best_candidate or soup
    
    def parse_table_structure(self, table_elem: BeautifulSoup, context: str = "") -> LegalTable:
        """Parse table with colspan/rowspan handling"""
        
        caption_elem = table_elem.find('caption')
        caption = caption_elem.get_text().strip() if caption_elem else ""
        
        rows = table_elem.find_all('tr')
        if not rows:
            return None
        
        # Extract headers
        headers = []
        header_row_idx = 0
        
        for i, row in enumerate(rows):
            th_cells = row.find_all('th')
            if th_cells:
                headers = [th.get_text().strip() for th in th_cells]
                header_row_idx = i + 1
                break
        
        if not headers and rows:
            first_row_cells = rows[0].find_all(['td', 'th'])
            headers = [cell.get_text().strip() for cell in first_row_cells]
            header_row_idx = 1
        
        # Parse data rows
        parsed_rows = []
        
        for row_idx, row in enumerate(rows[header_row_idx:], start=header_row_idx):
            cells = row.find_all(['td', 'th'])
            
            parsed_cells = []
            for cell in cells:
                table_cell = TableCell(
                    content=cell.get_text().strip(),
                    colspan=int(cell.get('colspan', 1)),
                    rowspan=int(cell.get('rowspan', 1)),
                    is_header=cell.name == 'th'
                )
                parsed_cells.append(table_cell)
            
            if parsed_cells:  # Only add non-empty rows
                table_row = TableRow(
                    cells=parsed_cells,
                    row_number=row_idx
                )
                parsed_rows.append(table_row)
        
        max_columns = max([len(row.cells) + sum(cell.colspan - 1 for cell in row.cells) 
                          for row in parsed_rows] + [len(headers)]) if parsed_rows else len(headers)
        
        return LegalTable(
            caption=caption,
            headers=headers,
            rows=parsed_rows,
            total_columns=max_columns,
            total_rows=len(parsed_rows),
            context=context
        )
    
    def identify_element_type_and_number(self, text: str) -> tuple:
        """Identify element type and extract number/identifier"""
        
        text_cleaned = text.strip()
        
        # Chapter patterns
        chapter_patterns = [
            (r'(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম|নবম|দশম)\s*অধ্যায়', 'chapter'),
            (r'অধ্যায়\s*[-:]?\s*(\d+)', 'chapter'),
        ]
        
        # Section patterns  
        section_patterns = [
            (r'^(\d+)\.', 'section'),
            (r'ধারা\s*[-:]?\s*(\d+)', 'section'),
        ]
        
        # Subsection patterns
        subsection_patterns = [
            (r'^\((\d+)\)', 'subsection'),
        ]
        
        # Clause patterns
        clause_patterns = [
            (r'^\(([ক-৯]+)\)', 'clause'),  # Bengali letters
            (r'^\(([a-z]+)\)', 'clause'),   # English letters
        ]
        
        # Subclause patterns
        subclause_patterns = [
            (r'^\(([ivxlcdm]+)\)', 'subclause'),
        ]
        
        all_patterns = (chapter_patterns + section_patterns + subsection_patterns + 
                       clause_patterns + subclause_patterns)
        
        for pattern, element_type in all_patterns:
            match = re.search(pattern, text_cleaned, re.IGNORECASE)
            if match:
                number = match.group(1) if match.groups() else ""
                return element_type, number
        
        return 'content', ''
    
    def parse_structured_content(self, content_area: BeautifulSoup) -> tuple:
        """Parse content into structured elements"""
        
        # Extract all tables first
        all_tables = []
        table_elements = content_area.find_all('table')
        
        for table_elem in table_elements:
            # Get context
            context = ""
            prev_elem = table_elem.find_previous_sibling()
            if prev_elem:
                context = prev_elem.get_text().strip()[:200]
            
            legal_table = self.parse_table_structure(table_elem, context)
            if legal_table:
                all_tables.append(legal_table)
        
        # Get all text elements
        elements = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'])
        
        structured_elements = []
        preamble_parts = []
        current_hierarchy = []  # Stack to track current position in hierarchy
        in_preamble = True
        
        for elem in elements:
            text = elem.get_text().strip()
            if not text or len(text) < 3:
                continue
            
            element_type, number = self.identify_element_type_and_number(text)
            
            if element_type != 'content':
                in_preamble = False
                
                # Create new legal element
                legal_element = LegalElement(
                    type=element_type,
                    number=number,
                    title=text if element_type in ['chapter', 'section'] else '',
                    text=text,
                    children=[],
                    tables=[]
                )
                
                # Determine hierarchy level
                hierarchy_levels = ['chapter', 'section', 'subsection', 'clause', 'subclause']
                current_level = hierarchy_levels.index(element_type)
                
                # Adjust current hierarchy
                current_hierarchy = current_hierarchy[:current_level]
                
                # Add to appropriate parent
                if current_hierarchy:
                    current_hierarchy[-1].children.append(legal_element)
                else:
                    structured_elements.append(legal_element)
                
                current_hierarchy.append(legal_element)
                
            else:
                if in_preamble:
                    preamble_parts.append(text)
                elif current_hierarchy:
                    # Add content to the current element
                    if current_hierarchy[-1].text:
                        current_hierarchy[-1].text += '\n' + text
                    else:
                        current_hierarchy[-1].text = text
        
        preamble = '\n'.join(preamble_parts)
        return preamble, structured_elements, all_tables
    
    def extract_footnotes(self, soup: BeautifulSoup) -> List[LegalFootnote]:
        """Extract footnotes (if any exist)"""
        footnotes = []
        
        for i, footnote_elem in enumerate(soup.find_all('a', class_='tooltip')):
            footnote = LegalFootnote(
                ref_number=footnote_elem.get_text().strip(),
                tooltip_text=footnote_elem.get('title', footnote_elem.get('data-original-title', '')),
                position_in_text=i
            )
            footnotes.append(footnote)
        
        return footnotes
    
    def scrape_document(self, url: str) -> Optional[StructuredLegalDocument]:
        """Scrape document with improved content detection"""
        
        print(f"🔄 Scraping: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = "Unknown Document"
            title_elem = soup.find('h3')
            if title_elem:
                title = title_elem.get_text().strip()
            
            # Find best content area
            content_area = self.find_best_content_area(soup)
            
            # Extract footnotes
            footnotes = self.extract_footnotes(soup)
            
            # Parse structured content
            preamble, structure, all_tables = self.parse_structured_content(content_area)
            
            # Count elements
            def count_elements(elements, element_type):
                count = sum(1 for elem in elements if elem.type == element_type)
                for elem in elements:
                    count += count_elements(elem.children, element_type)
                return count
            
            chapters = count_elements(structure, 'chapter')
            sections = count_elements(structure, 'section')
            
            # Create document
            document = StructuredLegalDocument(
                url=url,
                title=title,
                preamble=preamble,
                structure=structure,
                all_tables=all_tables,
                footnotes=footnotes,
                scraped_at=datetime.now().isoformat()
            )
            
            print(f"✅ {title}")
            print(f"   📚 Chapters: {chapters}")
            print(f"   📋 Sections: {sections}")
            print(f"   📊 Tables: {len(all_tables)}")
            print(f"   📝 Footnotes: {len(footnotes)}")
            
            return document
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def save_document(self, document: StructuredLegalDocument, output_dir: str = 'fixed_structured_laws'):
        """Save document with proper structure"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        clean_title = re.sub(r'[^\w\s-]', '', document.title).strip()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        filename = f"{clean_title}.json"
        
        # Convert to dict (handling dataclasses)
        def convert_to_dict(obj):
            if hasattr(obj, '__dict__'):
                return {key: convert_to_dict(value) for key, value in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [convert_to_dict(item) for item in obj]
            else:
                return obj
        
        document_dict = convert_to_dict(document)
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {filepath}")
        return filepath

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python fixed_structured_scraper.py <url1> <url2> ... or --file <urls.txt>")
        return
    
    scraper = FixedStructuredScraper()
    
    if sys.argv[1] == '--file':
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = sys.argv[1:]
    
    print(f"🚀 FIXED STRUCTURED SCRAPER")
    print(f"📋 URLs: {len(urls)}")
    print("=" * 50)
    
    for url in urls:
        document = scraper.scrape_document(url)
        if document:
            scraper.save_document(document)

if __name__ == "__main__":
    main()