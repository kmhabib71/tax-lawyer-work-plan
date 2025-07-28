#!/usr/bin/env python3
"""
Enhanced Structured Legal Document Scraper with Table Support
Handles chapters, sections, subsections, clauses, subclauses, articles, footnotes, AND tables
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
class TableCell:
    content: str
    colspan: int
    rowspan: int
    is_header: bool
    html: str

@dataclass
class TableRow:
    cells: List[TableCell]
    row_number: int
    html: str

@dataclass
class LegalTable:
    caption: str
    headers: List[str]
    rows: List[TableRow]
    total_columns: int
    total_rows: int
    html: str
    context: str  # Surrounding text context

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
    tables: List[LegalTable]
    html: str

@dataclass
class LegalSubclause:
    identifier: str
    text: str
    tables: List[LegalTable]
    html: str

@dataclass
class LegalSubsection:
    number: str
    text: str
    clauses: List[LegalClause]
    tables: List[LegalTable]
    html: str

@dataclass
class LegalSection:
    number: str
    title: str
    text: str
    subsections: List[LegalSubsection]
    clauses: List[LegalClause]
    tables: List[LegalTable]
    html: str

@dataclass
class LegalChapter:
    number: str
    title: str
    sections: List[LegalSection]
    tables: List[LegalTable]
    html: str

@dataclass
class StructuredLegalDocument:
    url: str
    title: str
    preamble: str
    chapters: List[LegalChapter]
    sections: List[LegalSection]
    tables: List[LegalTable]  # Standalone tables
    footnotes: List[LegalFootnote]
    raw_html: str
    scraped_at: str

class EnhancedStructuredScraper:
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
                r'^\d+\.',
                r'ধারা\s*[-:]?\s*\d+',
                r'Section\s+\d+',
            ],
            'subsection': [
                r'^\(\d+\)',
                r'উপ-ধারা\s*[-:]?\s*\(\d+\)',
            ],
            'clause': [
                r'^\([^\d\)][^\)]*\)',
                r'দফা\s*[-:]?\s*\([^\)]+\)',
            ],
            'subclause': [
                r'^\([ivxlcdm]+\)',
                r'উপ-দফা\s*[-:]?\s*\([ivxlcdm]+\)',
            ]
        }
    
    def parse_table_structure(self, table_elem: BeautifulSoup, context: str = "") -> LegalTable:
        """Parse table with intelligent colspan/rowspan handling"""
        
        # Extract caption
        caption_elem = table_elem.find('caption')
        caption = caption_elem.get_text().strip() if caption_elem else ""
        
        # Get all rows
        rows = table_elem.find_all('tr')
        
        if not rows:
            return None
        
        # Parse header row (usually first row or rows with th elements)
        headers = []
        header_row_idx = 0
        
        # Look for header rows
        for i, row in enumerate(rows):
            th_cells = row.find_all('th')
            if th_cells:
                for th in th_cells:
                    headers.append(th.get_text().strip())
                header_row_idx = i + 1
                break
        
        # If no th elements, use first row as headers
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
                cell_content = cell.get_text().strip()
                colspan = int(cell.get('colspan', 1))
                rowspan = int(cell.get('rowspan', 1))
                is_header = cell.name == 'th'
                
                table_cell = TableCell(
                    content=cell_content,
                    colspan=colspan,
                    rowspan=rowspan,
                    is_header=is_header,
                    html=str(cell)
                )
                parsed_cells.append(table_cell)
            
            table_row = TableRow(
                cells=parsed_cells,
                row_number=row_idx,
                html=str(row)
            )
            parsed_rows.append(table_row)
        
        # Calculate table dimensions
        max_columns = max([len(row.cells) + sum(cell.colspan - 1 for cell in row.cells) 
                          for row in parsed_rows] + [len(headers)]) if parsed_rows else len(headers)
        
        legal_table = LegalTable(
            caption=caption,
            headers=headers,
            rows=parsed_rows,
            total_columns=max_columns,
            total_rows=len(parsed_rows),
            html=str(table_elem),
            context=context
        )
        
        return legal_table
    
    def extract_tables_with_context(self, content_area: BeautifulSoup) -> List[LegalTable]:
        """Extract tables along with their contextual information"""
        
        tables = []
        
        # Find all tables
        table_elements = content_area.find_all('table')
        
        for table_elem in table_elements:
            # Get context - look at preceding elements
            context_parts = []
            
            # Look for preceding heading or paragraph
            prev_elem = table_elem.find_previous_sibling()
            context_distance = 0
            
            while prev_elem and context_distance < 3:  # Look at max 3 preceding elements
                if prev_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
                    text = prev_elem.get_text().strip()
                    if text:
                        context_parts.insert(0, text)
                        if len(' '.join(context_parts)) > 200:  # Limit context length
                            break
                prev_elem = prev_elem.find_previous_sibling()
                context_distance += 1
            
            context = ' '.join(context_parts)
            
            # Parse the table
            legal_table = self.parse_table_structure(table_elem, context)
            if legal_table:
                tables.append(legal_table)
        
        return tables
    
    def identify_element_type(self, text: str) -> str:
        """Identify the type of legal element based on text patterns"""
        text_cleaned = text.strip()
        
        for element_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_cleaned, re.IGNORECASE):
                    return element_type
        
        return 'content'
    
    def extract_footnotes(self, soup: BeautifulSoup) -> List[LegalFootnote]:
        """Extract footnotes with their references"""
        footnotes = []
        
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
    
    def parse_structured_content_with_tables(self, content_area: BeautifulSoup) -> tuple:
        """Parse content into structured legal elements including tables"""
        
        # First extract all tables with context
        all_tables = self.extract_tables_with_context(content_area)
        
        chapters = []
        sections = []
        standalone_tables = []
        current_chapter = None
        current_section = None
        current_subsection = None
        current_clause = None
        
        # Get all relevant elements including tables
        elements = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'table'])
        
        preamble_parts = []
        in_preamble = True
        table_index = 0
        
        for elem in elements:
            if elem.name == 'table':
                # Handle table
                if table_index < len(all_tables):
                    current_table = all_tables[table_index]
                    table_index += 1
                    
                    # Assign table to current context
                    if current_clause:
                        current_clause.tables.append(current_table)
                    elif current_subsection:
                        current_subsection.tables.append(current_table)
                    elif current_section:
                        current_section.tables.append(current_table)
                    elif current_chapter:
                        current_chapter.tables.append(current_table)
                    else:
                        standalone_tables.append(current_table)
                continue
            
            text = elem.get_text().strip()
            if not text:
                continue
            
            element_type = self.identify_element_type(text)
            
            if element_type == 'chapter':
                in_preamble = False
                chapter_match = re.search(r'(\d+|প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম)', text)
                chapter_number = chapter_match.group(1) if chapter_match else 'Unknown'
                
                current_chapter = LegalChapter(
                    number=chapter_number,
                    title=text,
                    sections=[],
                    tables=[],
                    html=str(elem)
                )
                chapters.append(current_chapter)
                current_section = None
                current_subsection = None
                current_clause = None
                
            elif element_type == 'section':
                in_preamble = False
                section_match = re.search(r'(\d+)', text)
                section_number = section_match.group(1) if section_match else 'Unknown'
                
                current_section = LegalSection(
                    number=section_number,
                    title=text,
                    text='',
                    subsections=[],
                    clauses=[],
                    tables=[],
                    html=str(elem)
                )
                
                if current_chapter:
                    current_chapter.sections.append(current_section)
                else:
                    sections.append(current_section)
                
                current_subsection = None
                current_clause = None
                
            elif element_type == 'subsection':
                subsection_match = re.search(r'\((\d+)\)', text)
                subsection_number = subsection_match.group(1) if subsection_match else 'Unknown'
                
                current_subsection = LegalSubsection(
                    number=subsection_number,
                    text=text,
                    clauses=[],
                    tables=[],
                    html=str(elem)
                )
                
                if current_section:
                    current_section.subsections.append(current_subsection)
                
                current_clause = None
                
            elif element_type == 'clause':
                clause_match = re.search(r'\(([^\)]+)\)', text)
                clause_id = clause_match.group(1) if clause_match else 'Unknown'
                
                current_clause = LegalClause(
                    number=clause_id,
                    text=text,
                    subclauses=[],
                    tables=[],
                    html=str(elem)
                )
                
                if current_subsection:
                    current_subsection.clauses.append(current_clause)
                elif current_section:
                    current_section.clauses.append(current_clause)
                
            elif element_type == 'subclause':
                subclause_match = re.search(r'\(([ivxlcdm]+)\)', text)
                subclause_id = subclause_match.group(1) if subclause_match else 'Unknown'
                
                subclause = LegalSubclause(
                    identifier=subclause_id,
                    text=text,
                    tables=[],
                    html=str(elem)
                )
                
                if current_clause:
                    current_clause.subclauses.append(subclause)
                
            else:  # Regular content
                if in_preamble:
                    preamble_parts.append(text)
                elif current_section:
                    if current_section.text:
                        current_section.text += '\n' + text
                    else:
                        current_section.text = text
        
        preamble = '\n'.join(preamble_parts)
        return preamble, chapters, sections, standalone_tables
    
    def scrape_document(self, url: str) -> Optional[StructuredLegalDocument]:
        """Scrape a single document with full structure preservation including tables"""
        
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
            
            # Parse structured content with tables
            preamble, chapters, sections, standalone_tables = self.parse_structured_content_with_tables(content_area)
            
            # Count total tables
            total_tables = (len(standalone_tables) + 
                          sum(len(ch.tables) for ch in chapters) +
                          sum(len(sec.tables) for sec in sections) +
                          sum(len(subsec.tables) for ch in chapters for sec in ch.sections for subsec in sec.subsections) +
                          sum(len(clause.tables) for ch in chapters for sec in ch.sections for clause in sec.clauses))
            
            # Create structured document
            document = StructuredLegalDocument(
                url=url,
                title=title,
                preamble=preamble,
                chapters=chapters,
                sections=sections,
                tables=standalone_tables,
                footnotes=footnotes,
                raw_html=str(soup),
                scraped_at=datetime.now().isoformat()
            )
            
            print(f"✅ {title}")
            print(f"   📚 Chapters: {len(chapters)}")
            print(f"   📋 Sections: {len(sections)}")
            print(f"   📊 Tables: {total_tables}")
            print(f"   📝 Footnotes: {len(footnotes)}")
            
            return document
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def save_structured_document(self, document: StructuredLegalDocument, output_dir: str = 'structured_laws_with_tables'):
        """Save document in structured JSON format with tables"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create clean filename
        clean_title = re.sub(r'[^\w\s-]', '', document.title).strip()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        filename = f"{clean_title}.json"
        
        # Convert to dictionary
        document_dict = {
            'url': document.url,
            'title': document.title,
            'preamble': document.preamble,
            'chapters': [self._chapter_to_dict(ch) for ch in document.chapters],
            'sections': [self._section_to_dict(sec) for sec in document.sections],
            'standalone_tables': [self._table_to_dict(table) for table in document.tables],
            'footnotes': [self._footnote_to_dict(fn) for fn in document.footnotes],
            'scraped_at': document.scraped_at,
            'structure_summary': {
                'total_chapters': len(document.chapters),
                'total_sections': len(document.sections) + sum(len(ch.sections) for ch in document.chapters),
                'total_tables': len(document.tables) + sum(len(ch.tables) for ch in document.chapters),
                'total_footnotes': len(document.footnotes)
            }
        }
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {filepath}")
        return filepath
    
    def _table_to_dict(self, table: LegalTable) -> Dict:
        return {
            'caption': table.caption,
            'headers': table.headers,
            'rows': [
                {
                    'row_number': row.row_number,
                    'cells': [
                        {
                            'content': cell.content,
                            'colspan': cell.colspan,
                            'rowspan': cell.rowspan,
                            'is_header': cell.is_header
                        }
                        for cell in row.cells
                    ]
                }
                for row in table.rows
            ],
            'total_columns': table.total_columns,
            'total_rows': table.total_rows,
            'context': table.context,
            'html': table.html
        }
    
    def _chapter_to_dict(self, chapter: LegalChapter) -> Dict:
        return {
            'number': chapter.number,
            'title': chapter.title,
            'sections': [self._section_to_dict(sec) for sec in chapter.sections],
            'tables': [self._table_to_dict(table) for table in chapter.tables],
            'html': chapter.html
        }
    
    def _section_to_dict(self, section: LegalSection) -> Dict:
        return {
            'number': section.number,
            'title': section.title,
            'text': section.text,
            'subsections': [self._subsection_to_dict(sub) for sub in section.subsections],
            'clauses': [self._clause_to_dict(clause) for clause in section.clauses],
            'tables': [self._table_to_dict(table) for table in section.tables],
            'html': section.html
        }
    
    def _subsection_to_dict(self, subsection: LegalSubsection) -> Dict:
        return {
            'number': subsection.number,
            'text': subsection.text,
            'clauses': [self._clause_to_dict(clause) for clause in subsection.clauses],
            'tables': [self._table_to_dict(table) for table in subsection.tables],
            'html': subsection.html
        }
    
    def _clause_to_dict(self, clause: LegalClause) -> Dict:
        return {
            'number': clause.number,
            'text': clause.text,
            'subclauses': [self._subclause_to_dict(sub) for sub in clause.subclauses],
            'tables': [self._table_to_dict(table) for table in clause.tables],
            'html': clause.html
        }
    
    def _subclause_to_dict(self, subclause: LegalSubclause) -> Dict:
        return {
            'identifier': subclause.identifier,
            'text': subclause.text,
            'tables': [self._table_to_dict(table) for table in subclause.tables],
            'html': subclause.html
        }
    
    def _footnote_to_dict(self, footnote: LegalFootnote) -> Dict:
        return {
            'ref_number': footnote.ref_number,
            'tooltip_text': footnote.tooltip_text,
            'position_in_text': footnote.position_in_text,
            'html': footnote.html
        }

def scrape_urls_with_tables(urls: List[str], output_dir: str = 'structured_laws_with_tables'):
    """Scrape multiple URLs with full structure and table preservation"""
    
    scraper = EnhancedStructuredScraper()
    
    print(f"🚀 ENHANCED STRUCTURED LEGAL SCRAPER WITH TABLES")
    print(f"=" * 60)
    print(f"📋 URLs to scrape: {len(urls)}")
    print(f"📁 Output directory: {output_dir}")
    print(f"🏗️  Features: Chapters, Sections, Clauses, Tables, Footnotes")
    print(f"=" * 60)
    
    scraped_documents = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]", end=" ")
        
        document = scraper.scrape_document(url)
        if document:
            filepath = scraper.save_structured_document(document, output_dir)
            scraped_documents.append(document)
    
    print(f"\n🎉 ENHANCED SCRAPING COMPLETE!")
    print(f"📊 Results: {len(scraped_documents)}/{len(urls)} successful")
    
    return scraped_documents

def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_structured_scraper.py <url1> <url2> ... or --file <urls.txt>")
        print("Example: python enhanced_structured_scraper.py http://bdlaws.minlaw.gov.bd/act-details-1541.html")
        return
    
    if sys.argv[1] == '--file':
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
        urls = sys.argv[1:]
    
    scrape_urls_with_tables(urls)

if __name__ == "__main__":
    main()