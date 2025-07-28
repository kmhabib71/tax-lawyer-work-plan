#!/usr/bin/env python3
"""
Precise Structured Legal Document Scraper
Based on actual HTML structure from Bangladesh Laws website
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
class DocumentHeader:
    title: str  # From h3 tag
    ordinance_info: str  # From h4 tag 
    publish_date: str  # From .publish-date
    introduction: str  # From act-role-style section

@dataclass
class TableCell:
    content: str
    colspan: int
    rowspan: int
    is_header: bool

@dataclass
class TableRow:
    cells: List[TableCell]

@dataclass
class LegalTable:
    caption: str
    headers: List[str]
    rows: List[TableRow]
    context: str

@dataclass
class SubClause:
    identifier: str  # (অ), (আ), (ই) etc.
    text: str

@dataclass
class Clause:
    identifier: str  # (ক), (খ), (গ) etc.
    text: str
    sub_clauses: List[SubClause]
    tables: List[LegalTable]

@dataclass
class Subsection:
    identifier: str  # (১), (২), (৩) etc.
    text: str
    clauses: List[Clause]
    tables: List[LegalTable]

@dataclass
class Section:
    number: str  # ১, ২, ৩ etc.
    title: str  # From txt-head div
    content_text: str  # Main section text
    subsections: List[Subsection]
    clauses: List[Clause]  # Direct clauses (when no subsections)
    tables: List[LegalTable]

@dataclass
class Chapter:
    number: str  # প্রথম, দ্বিতীয় etc.
    title: str  # From act-chapter-name
    sections: List[Section]

@dataclass
class StructuredLegalDocument:
    header: DocumentHeader
    chapters: List[Chapter]
    scraped_at: str
    url: str

class PreciseStructuredScraper:
    def __init__(self, base_url="http://bdlaws.minlaw.gov.bd"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing excessive whitespace and formatting"""
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\r\n|\r|\n', ' ', text)
        text = text.strip()
        return text

    def clean_content_text(self, text: str) -> str:
        """Clean content text while preserving necessary line breaks"""
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)

    def extract_document_header(self, soup: BeautifulSoup) -> DocumentHeader:
        """Extract document header information"""
        
        title = ""
        title_elem = soup.find('section', class_='bg-act-section')
        if title_elem:
            h3_elem = title_elem.find('h3')
            if h3_elem:
                title = self.clean_text(h3_elem.get_text())
        
        ordinance_info = ""
        if title_elem:
            h4_elem = title_elem.find('h4')
            if h4_elem:
                ordinance_info = self.clean_text(h4_elem.get_text())
        
        publish_date = ""
        date_elem = soup.find('p', class_='publish-date')
        if date_elem:
            publish_date = self.clean_text(date_elem.get_text())
        
        introduction = ""
        intro_elem = soup.find('div', class_='act-role-style')
        if intro_elem:
            intro_parts = []
            for p in intro_elem.find_all('p'):
                text = self.clean_text(p.get_text())
                if text:
                    intro_parts.append(text)
            introduction = '\n'.join(intro_parts)
        
        return DocumentHeader(
            title=title,
            ordinance_info=ordinance_info,
            publish_date=publish_date,
            introduction=introduction
        )
    
    def parse_table(self, table_elem: BeautifulSoup, context: str = "") -> LegalTable:
        """Parse table structure with precise handling"""
        
        caption = ""
        prev_elem = table_elem.find_previous_sibling()
        while prev_elem and prev_elem.name in ['p', 'strong']:
            text = prev_elem.get_text().strip()
            if 'টেবিল' in text or 'Table' in text:
                caption = text
                break
            prev_elem = prev_elem.find_previous_sibling()
        
        rows = table_elem.find_all('tr')
        if not rows:
            return None
        
        headers = []
        thead = table_elem.find('thead')
        if thead:
            header_rows = thead.find_all('tr')
            if len(header_rows) >= 1:
                for cell in header_rows[0].find_all(['th', 'td']):
                    headers.append(self.clean_content_text(cell.get_text()))
        
        data_rows = []
        tbody = table_elem.find('tbody')
        if tbody:
            table_rows = tbody.find_all('tr')
        else:
            table_rows = rows[2:] if thead and len(rows) > 2 else rows[1:] if len(rows) > 1 else rows
        
        for row in table_rows:
            cells = []
            for cell in row.find_all(['td', 'th']):
                table_cell = TableCell(
                    content=self.clean_content_text(cell.get_text()),
                    colspan=int(cell.get('colspan', 1)),
                    rowspan=int(cell.get('rowspan', 1)),
                    is_header=cell.name == 'th'
                )
                cells.append(table_cell)
            
            if cells:
                data_rows.append(TableRow(cells=cells))
        
        return LegalTable(
            caption=caption,
            headers=headers,
            rows=data_rows,
            context=context
        )
    
    def parse_subsections_clauses_subclauses(self, section_content: str) -> tuple:
        """Parse subsections, clauses and subclauses from section content"""
        
        subsections = []
        direct_clauses = []
        
        content = re.sub(r'^[০-৯]+।\s*', '', section_content.strip())
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        current_subsection = None
        current_clause = None
        
        for para in paragraphs:
            subsection_match = re.match(r'^\(([০-৯]+)\)', para)
            if subsection_match:
                if current_clause and current_subsection:
                    current_subsection.clauses.append(current_clause)
                    current_clause = None
                elif current_clause and not current_subsection:
                    direct_clauses.append(current_clause)
                    current_clause = None
                    
                if current_subsection:
                    subsections.append(current_subsection)
                
                subsection_id = subsection_match.group(1)
                subsection_text = self.clean_text(para[subsection_match.end():])
                
                current_subsection = Subsection(
                    identifier=subsection_id,
                    text=subsection_text,
                    clauses=[]
                )
            
            elif re.match(r'^\(([ক-হ])\)', para):
                clause_match = re.match(r'^\(([ক-হ])\)', para)
                
                if current_clause:
                    if current_subsection:
                        current_subsection.clauses.append(current_clause)
                    else:
                        direct_clauses.append(current_clause)
                
                clause_id = clause_match.group(1)
                clause_text = self.clean_text(para[clause_match.end():])
                
                current_clause = Clause(
                    identifier=clause_id,
                    text=clause_text,
                    sub_clauses=[]
                )
            
            elif re.match(r'^\(([অ-ঔ])\)', para):
                subclause_match = re.match(r'^\(([অ-ঔ])\)', para)
                if subclause_match and current_clause:
                    subclause_id = subclause_match.group(1)
                    subclause_text = self.clean_text(para[subclause_match.end():])
                    
                    sub_clause = SubClause(
                        identifier=subclause_id,
                        text=subclause_text
                    )
                    current_clause.sub_clauses.append(sub_clause)
            
            elif not re.match(r'^\([০-৯ক-হঅ-ঔ]+\)', para):
                cleaned_para = self.clean_text(para)
                if cleaned_para:
                    if current_clause:
                        if current_clause.text:
                            current_clause.text += ' ' + cleaned_para
                        else:
                            current_clause.text = cleaned_para
                    elif current_subsection:
                        if current_subsection.text:
                            current_subsection.text += ' ' + cleaned_para
                        else:
                            current_subsection.text = cleaned_para
        
        if current_clause:
            if current_subsection:
                current_subsection.clauses.append(current_clause)
            else:
                direct_clauses.append(current_clause)
                
        if current_subsection:
            subsections.append(current_subsection)
        
        return subsections, direct_clauses

    def extract_structured_content(self, soup: BeautifulSoup) -> List[Chapter]:
        """Extract structured content using the precise HTML patterns"""
        
        chapters = []
        
        chapter_groups = soup.find_all('div', class_='act-chapter-group')
        all_section_divs = soup.find_all('div', class_='row lineremoves')
        
        section_divs_with_content = []
        for div in all_section_divs:
            txt_head = div.find('div', class_='txt-head')
            txt_details = div.find('div', class_='txt-details')
            if txt_head and txt_details:
                section_divs_with_content.append(div)
        
        all_sections = []
        processed_section_numbers = set()
        
        for section_div in section_divs_with_content:
            txt_head = section_div.find('div', class_='txt-head')
            txt_details = section_div.find('div', class_='txt-details')
            
            if txt_head and txt_details:
                section_title = self.clean_text(txt_head.get_text())
                
                txt_details_copy = txt_details.__copy__()
                for table_elem in txt_details_copy.find_all('table'):
                    table_elem.decompose()
                    
                section_content = self.clean_content_text(txt_details_copy.get_text())
                
                section_number = ""
                section_match = re.match(r'^([০-৯]+)।', section_content)
                if section_match:
                    section_number = section_match.group(1)
                    
                    if section_number in processed_section_numbers:
                        continue
                    processed_section_numbers.add(section_number)
                    
                    tables = []
                    for table_elem in section_div.find_all('table'):
                        table = self.parse_table(table_elem, section_title)
                        if table:
                            tables.append(table)
                    
                    subsections, direct_clauses = self.parse_subsections_clauses_subclauses(section_content)
                    
                    section = Section(
                        number=section_number,
                        title=section_title,
                        content_text=section_content,
                        subsections=subsections,
                        clauses=direct_clauses,
                        tables=tables
                    )
                    
                    all_sections.append(section)
        
        all_sections.sort(key=lambda x: int(x.number))
        
        chapter_ranges = [
            (1, 1),
            (2, 29),
            (30, 147),
            (148, 159)
        ]
        
        for chapter_idx, chapter_group in enumerate(chapter_groups):
            chapter_no_elem = chapter_group.find('p', class_='act-chapter-no')
            chapter_name_elem = chapter_group.find('p', class_='act-chapter-name')
            
            if not chapter_no_elem or not chapter_name_elem:
                continue
            
            chapter_number = chapter_no_elem.get_text().strip()
            chapter_title = chapter_name_elem.get_text().strip()
            
            sections = []
            if chapter_idx < len(chapter_ranges):
                start_section, end_section = chapter_ranges[chapter_idx]
                
                for section in all_sections:
                    section_num = int(section.number)
                    if start_section <= section_num <= end_section:
                        sections.append(section)
            
            chapter = Chapter(
                number=chapter_number,
                title=chapter_title,
                sections=sections
            )
            
            chapters.append(chapter)
        
        return chapters
    
    def scrape_document(self, url: str) -> Optional[StructuredLegalDocument]:
        """Scrape document with precise structure extraction"""
        
        print(f"🔄 Scraping: {url}")
        
        try:
            try:
                self.session.get(self.base_url, timeout=10)
            except:
                pass

            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            header = self.extract_document_header(soup)
            chapters = self.extract_structured_content(soup)
            
            total_sections = sum(len(ch.sections) for ch in chapters)
            total_subsections = sum(len(sec.subsections) for ch in chapters for sec in ch.sections)
            total_tables = sum(len(sec.tables) for ch in chapters for sec in ch.sections)
            total_clauses = sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) 
                              for ch in chapters for sec in ch.sections)
            
            document = StructuredLegalDocument(
                header=header,
                chapters=chapters,
                scraped_at=datetime.now().isoformat(),
                url=url
            )
            
            print(f"✅ {header.title}")
            print(f"   📚 Chapters: {len(chapters)}")
            print(f"   📋 Sections: {total_sections}")
            print(f"   📄 Subsections: {total_subsections}")
            print(f"   🔹 Clauses: {total_clauses}")
            print(f"   📊 Tables: {total_tables}")
            
            return document
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def save_document(self, document: StructuredLegalDocument, output_dir: str = 'precise_structured_laws'):
        """Save document with precise structure"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        clean_title = re.sub(r'[^\w\s-]', '', document.header.title).strip()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        filename = f"{clean_title}.json"
        
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: convert_dataclass(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [convert_dataclass(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_dataclass(v) for k, v in obj.items()}
            else:
                return obj
        
        document_dict = convert_dataclass(document)
        
        document_dict['structure_summary'] = {
            'total_chapters': len(document.chapters),
            'total_sections': sum(len(ch.sections) for ch in document.chapters),
            'total_subsections': sum(len(sec.subsections) for ch in chapters for sec in ch.sections),
            'total_clauses': sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) 
                               for ch in document.chapters for sec in ch.sections),
            'total_tables': sum(len(sec.tables) for ch in document.chapters for sec in ch.sections),
            'chapters_breakdown': [
                {
                    'chapter_number': ch.number,
                    'chapter_title': ch.title,
                    'sections_count': len(ch.sections)
                }
                for ch in document.chapters
            ]
        }
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to: {filepath}")
        return filepath

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python precise_structured_scraper.py <url1> <url2> ... or --file <urls.txt>")
        return
    
    scraper = PreciseStructuredScraper()
    
    if sys.argv[1] == '--file':
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = sys.argv[1:]
    
    print(f"🎯 PRECISE STRUCTURED SCRAPER")
    print(f"📋 URLs: {len(urls)}")
    print("=" * 50)
    
    for url in urls:
        document = scraper.scrape_document(url)
        if document:
            scraper.save_document(document)

if __name__ == "__main__":
    main()