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
    tables: List[LegalTable]  # Tables associated with this clause

@dataclass
class Subsection:
    identifier: str  # (১), (২), (৩) etc.
    text: str
    clauses: List[Clause]
    tables: List[LegalTable]  # Tables associated with this subsection

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
        
        # Remove excessive whitespace, newlines, and carriage returns
        text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace with single space
        text = re.sub(r'\r\n|\r|\n', ' ', text)  # Replace line breaks with space
        text = text.strip()  # Remove leading/trailing whitespace
        
        return text

    def clean_content_text(self, text: str) -> str:
        """Clean content text while preserving necessary line breaks"""
        if not text:
            return ""
        
        # Split into lines and clean each
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = re.sub(r'\s+', ' ', line.strip())  # Clean excessive spaces
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        # Join with single newlines
        return '\n'.join(cleaned_lines)

    def remove_table_content_from_text(self, text: str, tables: List[LegalTable]) -> str:
        """Remove table content from section text to avoid duplication"""
        if not tables:
            return text
        
        # Split text into paragraphs
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip if this line looks like table content
            should_skip = False
            
            for table in tables:
                # Skip table caption
                if table.caption and table.caption.strip() in line:
                    should_skip = True
                    break
                    
                # Skip table headers
                for header in table.headers:
                    if header and len(header) > 5 and header in line:
                        should_skip = True
                        break
                
                if should_skip:
                    break
                    
                # Skip table row content
                for row in table.rows:
                    for cell in row.cells:
                        cell_content = cell.content.strip()
                        if cell_content and len(cell_content) > 5:
                            # If this line is mostly this cell content, skip it
                            if cell_content in line and len(cell_content) > len(line) * 0.7:
                                should_skip = True
                                break
                    if should_skip:
                        break
                if should_skip:
                    break
            
            # Skip lines that look like table structure
            if not should_skip:
                # Skip lines with table-like patterns
                if re.match(r'^[০-৯0-9\.\s\,\(\)-]+$', line) and len(line) < 30:
                    should_skip = True
                elif any(word in line.lower() for word in ['heading', 'description', 'goods', 'rate', 'h.s.', 'code', 'শিরনামা', 'বিবরণ']):
                    should_skip = True
            
            if not should_skip:
                cleaned_lines.append(line)
        
        # Join cleaned lines
        cleaned_text = '\n'.join(cleaned_lines)
        return self.clean_content_text(cleaned_text)

    def extract_document_header(self, soup: BeautifulSoup) -> DocumentHeader:
        """Extract document header information"""
        
        # Title from h3 in bg-act-section
        title = ""
        title_elem = soup.find('section', class_='bg-act-section')
        if title_elem:
            h3_elem = title_elem.find('h3')
            if h3_elem:
                title = self.clean_text(h3_elem.get_text())
        
        # Ordinance info from h4
        ordinance_info = ""
        if title_elem:
            h4_elem = title_elem.find('h4')
            if h4_elem:
                ordinance_info = self.clean_text(h4_elem.get_text())
        
        # Publish date from .publish-date
        publish_date = ""
        date_elem = soup.find('p', class_='publish-date')
        if date_elem:
            publish_date = self.clean_text(date_elem.get_text())
        
        # Introduction from act-role-style
        introduction = ""
        intro_elem = soup.find('div', class_='act-role-style')
        if intro_elem:
            # Get all p tags in the introduction
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
        
        # Extract caption (if any)
        caption = ""
        # Look for table caption in preceding elements
        prev_elem = table_elem.find_previous_sibling()
        while prev_elem and prev_elem.name in ['p', 'strong']:
            text = prev_elem.get_text().strip()
            if 'টেবিল' in text or 'Table' in text:
                caption = text
                break
            prev_elem = prev_elem.find_previous_sibling()
        
        # Get table rows
        rows = table_elem.find_all('tr')
        if not rows:
            return None
        
        # Extract headers from thead or first row
        headers = []
        thead = table_elem.find('thead')
        if thead:
            header_rows = thead.find_all('tr')
            if len(header_rows) >= 1:
                # Use first row for headers
                for cell in header_rows[0].find_all(['th', 'td']):
                    headers.append(self.clean_content_text(cell.get_text()))
        
        # Parse data rows (skip header rows)
        data_rows = []
        tbody = table_elem.find('tbody')
        if tbody:
            table_rows = tbody.find_all('tr')
        else:
            # Skip header rows manually
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
        direct_clauses = []  # Clauses not under any subsection
        
        # Remove section number from beginning if present
        content = re.sub(r'^[০-৯]+।\s*', '', section_content.strip())
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        current_subsection = None
        current_clause = None
        
        for para in paragraphs:
            # Check if this is a subsection using Bengali numbers (১), (২), (৩) etc.
            subsection_match = re.match(r'^\(([০-৯]+)\)', para)
            if subsection_match:
                # Save previous subsection/clause if exists
                if current_clause and current_subsection:
                    current_subsection.clauses.append(current_clause)
                    current_clause = None
                elif current_clause and not current_subsection:
                    direct_clauses.append(current_clause)
                    current_clause = None
                    
                if current_subsection:
                    subsections.append(current_subsection)
                
                # Start new subsection
                subsection_id = subsection_match.group(1)
                subsection_text = self.clean_text(para[subsection_match.end():])
                
                current_subsection = Subsection(
                    identifier=subsection_id,
                    text=subsection_text,
                    clauses=[]
                )
            
            # Check if this is a main clause using Bengali letters (ক), (খ), (গ), (ঘ), (ঙ), (চ), (ছ), (জ), (ঝ), (ঞ) etc.
            elif re.match(r'^\(([ক-হ])\)', para):
                clause_match = re.match(r'^\(([ক-হ])\)', para)
                
                # Save previous clause
                if current_clause:
                    if current_subsection:
                        current_subsection.clauses.append(current_clause)
                    else:
                        direct_clauses.append(current_clause)
                
                # Start new clause
                clause_id = clause_match.group(1)
                clause_text = self.clean_text(para[clause_match.end():])
                
                current_clause = Clause(
                    identifier=clause_id,
                    text=clause_text,
                    sub_clauses=[]
                )
            
            # Check if this is a sub-clause using Bengali vowels (অ), (আ), (ই), (ঈ), (উ), (ঊ) etc.
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
            
            # Regular content - add to current clause or subsection
            elif not re.match(r'^\([০-৯ক-হঅ-ঔ]+\)', para):
                cleaned_para = self.clean_text(para)
                if cleaned_para:  # Only add non-empty content
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
        
        # Add the last clause and subsection
        if current_clause:
            if current_subsection:
                current_subsection.clauses.append(current_clause)
            else:
                direct_clauses.append(current_clause)
                
        if current_subsection:
            subsections.append(current_subsection)
        
        return subsections, direct_clauses

    def parse_subsections_clauses_subclauses_with_tables(self, section_content: str, section_div, section_title: str) -> tuple:
        """Parse subsections, clauses and subclauses with table association"""
        
        subsections = []
        direct_clauses = []
        
        # Remove section number from beginning if present
        content = re.sub(r'^[০-৯]+।\s*', '', section_content.strip())
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        current_subsection = None
        current_clause = None
        
        # Find tables for potential association
        all_tables = []
        for table_elem in section_div.find_all('table'):
            table = self.parse_table(table_elem, section_title)
            if table:
                all_tables.append(table)
        
        for para in paragraphs:
            # Skip if this paragraph looks like table content
            if self.looks_like_table_content(para):
                continue
                
            # Check if this is a subsection using Bengali numbers (১), (২), (৩) etc.
            subsection_match = re.match(r'^\(([০-৯]+)\)', para)
            if subsection_match:
                # Save previous subsection/clause if exists
                if current_clause and current_subsection:
                    current_subsection.clauses.append(current_clause)
                    current_clause = None
                elif current_clause and not current_subsection:
                    direct_clauses.append(current_clause)
                    current_clause = None
                    
                if current_subsection:
                    subsections.append(current_subsection)
                
                # Start new subsection
                subsection_id = subsection_match.group(1)
                subsection_text = self.clean_text(para[subsection_match.end():])
                
                current_subsection = Subsection(
                    identifier=subsection_id,
                    text=subsection_text,
                    clauses=[],
                    tables=[]
                )
            
            # Check if this is a main clause using Bengali letters (ক), (খ), (গ), (ঘ), (ঙ), (চ), (ছ), (জ), (ঝ), (ঞ) etc.
            elif re.match(r'^\(([ক-হ])\)', para):
                clause_match = re.match(r'^\(([ক-হ])\)', para)
                
                # Save previous clause
                if current_clause:
                    if current_subsection:
                        current_subsection.clauses.append(current_clause)
                    else:
                        direct_clauses.append(current_clause)
                
                # Start new clause
                clause_id = clause_match.group(1)
                clause_text = self.clean_text(para[clause_match.end():])
                
                # Check if this clause mentions a table (like "টেবিল-১")
                associated_tables = []
                if 'টেবিল' in clause_text or 'table' in clause_text.lower():
                    associated_tables = all_tables.copy()  # Associate all tables for now
                
                current_clause = Clause(
                    identifier=clause_id,
                    text=clause_text,
                    sub_clauses=[],
                    tables=associated_tables
                )
            
            # Check if this is a sub-clause using Bengali vowels (অ), (আ), (ই), (ঈ), (উ), (ঊ) etc.
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
            
            # Regular content - add to current clause or subsection
            elif not re.match(r'^\([০-৯ক-হঅ-ঔ]+\)', para):
                cleaned_para = self.clean_text(para)
                if cleaned_para and not self.looks_like_table_content(cleaned_para):
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
        
        # Add the last clause and subsection
        if current_clause:
            if current_subsection:
                current_subsection.clauses.append(current_clause)
            else:
                direct_clauses.append(current_clause)
                
        if current_subsection:
            subsections.append(current_subsection)
        
        return subsections, direct_clauses

    def looks_like_table_content(self, text: str) -> bool:
        """Check if text looks like table content that should be skipped"""
        if not text:
            return False
            
        text = text.strip()
        
        # Skip very short numeric-only content that might be table data
        if re.match(r'^[০-৯০-৯a-zA-Z\s\.,\-\(\)]+$', text) and len(text) < 50:
            return True
            
        # Skip content that looks like table headers
        if any(word in text.lower() for word in ['heading', 'description', 'rate', 'h.s.', 'code']):
            return True
            
        # Skip content with lots of numbers and symbols (likely table data)
        if len(re.findall(r'[০-৯0-9\.\,\%]', text)) > len(text) * 0.3:
            return True
            
        return False

    def extract_structured_content(self, soup: BeautifulSoup) -> List[Chapter]:
        """Extract structured content using the precise HTML patterns"""
        
        chapters = []
        
        # Find all chapter groups and section divs in document order
        chapter_groups = soup.find_all('div', class_='act-chapter-group')
        all_section_divs = soup.find_all('div', class_='row lineremoves')
        
        print(f"🔍 Found {len(chapter_groups)} chapters and {len(all_section_divs)} potential sections")
        
        # Filter to only section divs with txt-head and txt-details
        section_divs_with_content = []
        for div in all_section_divs:
            txt_head = div.find('div', class_='txt-head')
            txt_details = div.find('div', class_='txt-details')
            if txt_head and txt_details:
                section_divs_with_content.append(div)
        
        print(f"✅ Found {len(section_divs_with_content)} sections with content")
        
        # Extract all sections first, with their numbers
        all_sections = []
        processed_section_numbers = set()
        
        for section_div in section_divs_with_content:
            txt_head = section_div.find('div', class_='txt-head')
            txt_details = section_div.find('div', class_='txt-details')
            
            if txt_head and txt_details:
                section_title = self.clean_text(txt_head.get_text())
                
                # Extract section content without table HTML elements
                txt_details_copy = txt_details.__copy__()
                
                # Remove table elements from the copy before extracting text
                for table_elem in txt_details_copy.find_all('table'):
                    table_elem.decompose()  # Remove table HTML
                    
                section_content = self.clean_content_text(txt_details_copy.get_text())
                
                # Extract section number from content (Bengali numbers)
                section_number = ""
                section_match = re.match(r'^([০-৯]+)।', section_content)
                if section_match:
                    section_number = section_match.group(1)
                    
                    # Skip duplicates
                    if section_number in processed_section_numbers:
                        continue
                    processed_section_numbers.add(section_number)
                    
                    # Look for tables in this section
                    tables = []
                    for table_elem in section_div.find_all('table'):
                        table = self.parse_table(table_elem, section_title)
                        if table:
                            tables.append(table)
                    
                    # Parse subsections, clauses and subclauses from content without tables
                    subsections, direct_clauses = self.parse_subsections_clauses_subclauses_with_tables(
                        section_content, section_div, section_title
                    )
                    
                    # Create section object (using full content_text as before)
                    section = Section(
                        number=section_number,
                        title=section_title,
                        content_text=section_content,  # Back to full content
                        subsections=subsections,
                        clauses=direct_clauses,
                        tables=tables
                    )
                    
                    all_sections.append(section)
        
        # Sort sections by number to ensure proper order
        all_sections.sort(key=lambda x: int(x.number))
        
        # Now assign sections to chapters based on expected ranges
        # Chapter 1: sections 1-1 (প্রারম্ভিক)
        # Chapter 2: sections 2-29 (মূল্য সংযোজন কর)  
        # Chapter 3: sections 30-147 (আয়কর আইন)
        # Chapter 4: sections 148-159 (কাস্টমস আইন)
        
        chapter_ranges = [
            (1, 1),      # Chapter 1: section 1
            (2, 29),     # Chapter 2: sections 2-29
            (30, 147),   # Chapter 3: sections 30-147  
            (148, 159)   # Chapter 4: sections 148-159
        ]
        
        for chapter_idx, chapter_group in enumerate(chapter_groups):
            # Extract chapter info
            chapter_no_elem = chapter_group.find('p', class_='act-chapter-no')
            chapter_name_elem = chapter_group.find('p', class_='act-chapter-name')
            
            if not chapter_no_elem or not chapter_name_elem:
                continue
            
            chapter_number = chapter_no_elem.get_text().strip()
            chapter_title = chapter_name_elem.get_text().strip()
            
            # Assign sections based on expected range
            sections = []
            if chapter_idx < len(chapter_ranges):
                start_section, end_section = chapter_ranges[chapter_idx]
                
                for section in all_sections:
                    section_num = int(section.number)
                    if start_section <= section_num <= end_section:
                        sections.append(section)
            
            # Create chapter object
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
            # First establish session with main site
            try:
                self.session.get(self.base_url, timeout=10)
                print("📡 Session established")
            except:
                pass  # Continue even if main site request fails

            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"📄 Content size: {len(response.content)} bytes")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract header information
            header = self.extract_document_header(soup)
            
            # Extract structured content
            chapters = self.extract_structured_content(soup)
            
            # Count elements
            total_sections = sum(len(ch.sections) for ch in chapters)
            total_subsections = sum(len(sec.subsections) for ch in chapters for sec in ch.sections)
            total_tables = sum(len(sec.tables) for ch in chapters for sec in ch.sections)
            total_clauses = sum(len(sec.clauses) + sum(len(sub.clauses) for sub in sec.subsections) 
                              for ch in chapters for sec in ch.sections)
            total_clause_tables = sum(len(clause.tables) for ch in chapters for sec in ch.sections 
                                    for clause in sec.clauses)
            total_subsection_tables = sum(len(sub.tables) for ch in chapters for sec in ch.sections 
                                        for sub in sec.subsections)
            
            # Create document
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
            print(f"   📊 Tables: {total_tables} (section: {total_tables}, clause: {total_clause_tables}, subsection: {total_subsection_tables})")
            
            return document
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def save_document(self, document: StructuredLegalDocument, output_dir: str = 'precise_structured_laws'):
        """Save document with precise structure"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        clean_title = re.sub(r'[^\w\s-]', '', document.header.title).strip()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        filename = f"{clean_title}.json"
        
        # Convert to dict (handling dataclasses recursively)
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
        
        # Add summary statistics
        document_dict['structure_summary'] = {
            'total_chapters': len(document.chapters),
            'total_sections': sum(len(ch.sections) for ch in document.chapters),
            'total_subsections': sum(len(sec.subsections) for ch in document.chapters for sec in ch.sections),
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
    """Main function"""
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