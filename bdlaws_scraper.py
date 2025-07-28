#!/usr/bin/env python3
"""
Bangladesh Laws Text Scraper with Reference Preservation
Scrapes text content from bdlaws.minlaw.gov.bd while preserving footnote references
Extracts tooltip titles for cross-referencing
"""

import requests
import time
import json
import os
import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup, NavigableString
from typing import Set, List, Dict, Optional, Tuple
from dataclasses import dataclass
from tqdm import tqdm
import logging

@dataclass
class FootnoteReference:
    """Data structure for footnote references"""
    ref_number: str
    tooltip_title: str
    position_in_text: int

@dataclass
class LegalDocument:
    """Data structure for legal documents with references"""
    url: str
    title: str
    text_content: str
    footnotes: List[FootnoteReference]
    file_path: str
    category: str

class BDLawsScraper:
    """
    Text scraper for Bangladesh Laws website that extracts content with footnote references
    """
    
    def __init__(self, base_url: str = "http://bdlaws.minlaw.gov.bd", 
                 output_dir: str = "scraped_texts", 
                 delay: float = 1.0):
        self.base_url = base_url
        self.output_dir = output_dir
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.session = requests.Session()
        self.documents: List[LegalDocument] = []
        
        # Setup session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # PDF extensions to filter out
        self.pdf_extensions = {'.pdf', '.PDF'}
        
    def check_robots_txt(self) -> bool:
        """Check robots.txt compliance"""
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch('*', self.base_url)
        except Exception as e:
            self.logger.warning(f"Could not check robots.txt: {e}")
            return True
    
    def is_pdf_url(self, url: str) -> bool:
        """Check if URL points to a PDF file"""
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        return any(path.endswith(ext) for ext in self.pdf_extensions)
    
    def get_page(self, url: str, timeout: int = 30, retries: int = 3) -> Optional[BeautifulSoup]:
        """Safely fetch and parse a web page"""
        if url in self.visited_urls or self.is_pdf_url(url):
            return None
            
        for attempt in range(retries):
            try:
                self.logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'application/pdf' in content_type:
                    self.logger.info(f"Skipping PDF: {url}")
                    return None
                
                self.visited_urls.add(url)
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Rate limiting
                time.sleep(self.delay)
                
                return soup
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {retries} attempts")
                    
        return None
    
    def create_folder_structure(self, url: str) -> str:
        """Create folder structure based on URL path and return file path"""
        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        # Create base directory structure
        current_dir = self.output_dir
        
        # If it's an act-details page, organize by type
        if any('act-details' in part for part in path_parts):
            current_dir = os.path.join(current_dir, 'acts')
        elif any('rules-details' in part for part in path_parts):
            current_dir = os.path.join(current_dir, 'rules') 
        elif any('ordinance-details' in part for part in path_parts):
            current_dir = os.path.join(current_dir, 'ordinances')
        elif any('list' in part for part in path_parts):
            current_dir = os.path.join(current_dir, 'lists')
        else:
            current_dir = os.path.join(current_dir, 'others')
        
        # Create directory if it doesn't exist
        os.makedirs(current_dir, exist_ok=True)
        
        # Generate filename from URL
        if path_parts:
            filename = path_parts[-1]
            if not filename.endswith('.html'):
                filename += '.html'
        else:
            filename = 'index.html'
        
        # Handle special characters in filename
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        return os.path.join(current_dir, filename)
    
    def extract_text_with_footnotes(self, soup: BeautifulSoup) -> Tuple[str, List[FootnoteReference]]:
        """Extract text content while preserving footnote references"""
        footnotes = []
        text_parts = []
        
        # Find the main content area - typically in body or specific content divs
        content_area = soup.find('body')
        if not content_area:
            content_area = soup
        
        # Remove unwanted elements
        for element in content_area(['script', 'style', 'nav', 'header', 'footer', 'menu']):
            element.decompose()
        
        def process_element(element, text_position=0):
            """Recursively process elements to extract text and footnotes"""
            current_text = ""
            current_footnotes = []
            
            if isinstance(element, NavigableString):
                return str(element), []
            
            # Check if this is a footnote element
            if element.name == 'span' and element.get('class') and 'footnote' in element.get('class'):
                tooltip = element.get('title', '')
                
                # Find the reference number
                ref_link = element.find('a')
                ref_number = ""
                if ref_link:
                    ref_number = ref_link.get_text().strip()
                
                if tooltip and ref_number:
                    footnote = FootnoteReference(
                        ref_number=ref_number,
                        tooltip_title=tooltip,
                        position_in_text=text_position + len(current_text)
                    )
                    current_footnotes.append(footnote)
                    
                    # Include the reference in text with a marker
                    current_text += f"[REF_{ref_number}]"
                    return current_text, current_footnotes
            
            # Process child elements
            for child in element.children:
                child_text, child_footnotes = process_element(child, text_position + len(current_text))
                current_text += child_text
                current_footnotes.extend(child_footnotes)
            
            # Add spacing for block elements
            if element.name in ['p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                current_text += '\n'
            
            return current_text, current_footnotes
        
        # Process the content
        full_text, footnotes = process_element(content_area)
        
        # Clean up the text
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)
        
        return clean_text, footnotes
    
    def categorize_document(self, title: str, url: str, content: str) -> str:
        """Categorize the document based on title, URL, and content"""
        title_lower = title.lower() if title else ""
        url_lower = url.lower()
        content_lower = content.lower()
        
        # Tax-related categories
        if any(term in title_lower or term in url_lower or term in content_lower 
               for term in ['tax', 'vat', 'income tax', 'customs', 'duty', 'tariff', 'revenue', 'কর']):
            return 'tax_law'
        
        # Corporate and business law
        if any(term in title_lower or term in url_lower 
               for term in ['company', 'corporate', 'business', 'commercial', 'trade', 'কোম্পানি']):
            return 'corporate_law'
        
        # Constitutional and administrative
        if any(term in title_lower or term in url_lower 
               for term in ['constitution', 'administrative', 'government', 'public', 'সংবিধান']):
            return 'constitutional_law'
        
        # Civil and criminal
        if any(term in title_lower or term in url_lower 
               for term in ['civil', 'criminal', 'penal', 'procedure', 'দণ্ড', 'ফৌজদারি']):
            return 'civil_criminal_law'
        
        # Labor and employment
        if any(term in title_lower or term in url_lower 
               for term in ['labor', 'labour', 'employment', 'worker', 'industrial', 'শ্রমিক']):
            return 'labor_law'
        
        return 'general_law'
    
    def save_document(self, document: LegalDocument):
        """Save document with text content and footnotes"""
        # Create category directory
        category_dir = os.path.join(self.output_dir, document.category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Generate filename from document title
        safe_title = self.sanitize_filename(document.title)
        filename = f"{safe_title}.txt"
        
        # Handle potential filename conflicts
        file_path = os.path.join(category_dir, filename)
        counter = 1
        original_path = file_path
        while os.path.exists(file_path):
            name_without_ext = safe_title
            file_path = os.path.join(category_dir, f"{name_without_ext}_{counter}.txt")
            counter += 1
        
        # Save as structured text file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {document.title}\n")
            f.write(f"URL: {document.url}\n")
            f.write(f"Category: {document.category}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write main content
            f.write("CONTENT:\n")
            f.write(document.text_content)
            f.write("\n\n")
            
            # Write footnotes section
            if document.footnotes:
                f.write("FOOTNOTES:\n")
                f.write("-" * 40 + "\n")
                for footnote in document.footnotes:
                    f.write(f"[REF_{footnote.ref_number}]: {footnote.tooltip_title}\n")
                    f.write(f"Position: {footnote.position_in_text}\n\n")
        
        # Also save as JSON for structured access
        json_file = file_path.replace('.txt', '.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'title': document.title,
                'url': document.url,
                'category': document.category,
                'text_content': document.text_content,
                'footnotes': [
                    {
                        'ref_number': fn.ref_number,
                        'tooltip_title': fn.tooltip_title,
                        'position_in_text': fn.position_in_text
                    } for fn in document.footnotes
                ]
            }, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved document: {document.title} -> {file_path}")
        
        return file_path
    
    def is_details_page(self, url: str) -> bool:
        """Check if URL is a details page we want to scrape"""
        details_patterns = ['-details-', 'act-details', 'rules-details', 'ordinance-details']
        return any(pattern in url for pattern in details_patterns)
    
    def discover_urls(self, soup: BeautifulSoup, current_url: str) -> Set[str]:
        """Discover new URLs to crawl, focusing only on details pages"""
        urls = set()
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            # Filter URLs - only include details pages from the same domain
            if (full_url.startswith(self.base_url) and 
                not self.is_pdf_url(full_url) and 
                full_url not in self.visited_urls):
                
                # Only include details pages and list pages (to discover more details pages)
                if self.is_details_page(full_url):
                    urls.add(full_url)
                elif any(pattern in full_url for pattern in ['act-list', 'rules-list', 'ordinance-list']):
                    # Include list pages to discover details pages
                    urls.add(full_url)
        
        return urls
    
    def extract_document_title(self, soup: BeautifulSoup) -> str:
        """Extract the actual document title from the specific HTML structure"""
        # Look for the specific structure you mentioned
        bg_act_section = soup.find('section', class_='bg-act-section')
        if bg_act_section:
            h3_elem = bg_act_section.find('h3')
            if h3_elem:
                title = h3_elem.get_text().strip()
                if title:
                    return title
        
        # Fallback to other title elements
        title_selectors = [
            'section.bg-act-section h3',
            '.act-title h3',
            '.document-title',
            'h1', 'h2', 'h3'
        ]
        
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text().strip()
                if title and len(title) > 5:  # Ensure it's a meaningful title
                    return title
        
        # Final fallback to page title
        title_elem = soup.find('title')
        if title_elem:
            return title_elem.get_text().strip()
        
        return 'Untitled Document'
    
    def sanitize_filename(self, title: str) -> str:
        """Convert title to a safe filename"""
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', title)
        filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
        filename = re.sub(r'[,।]', '', filename)  # Remove commas and Bengali periods
        filename = filename.strip('_')[:100]  # Limit length and trim underscores
        
        if not filename:
            filename = 'untitled'
        
        return filename
    
    def crawl_page(self, url: str) -> Set[str]:
        """Crawl a single page and extract text content with footnotes"""
        soup = self.get_page(url)
        if not soup:
            return set()
        
        # Always discover URLs from this page first
        discovered_urls = self.discover_urls(soup, url)
        
        # Only process details pages for content extraction
        if not self.is_details_page(url):
            self.logger.info(f"Skipping non-details page: {url}")
            return discovered_urls
        
        # Extract text content and footnotes
        text_content, footnotes = self.extract_text_with_footnotes(soup)
        
        # Skip pages with minimal content
        if len(text_content.strip()) < 100:
            self.logger.info(f"Skipping page with minimal content: {url}")
            return discovered_urls
        
        # Extract actual document title from the specific structure
        title = self.extract_document_title(soup)
        
        # Categorize document
        category = self.categorize_document(title, url, text_content)
        
        # Create document
        document = LegalDocument(
            url=url,
            title=title,
            text_content=text_content,
            footnotes=footnotes,
            file_path="",  # Will be set in save_document
            category=category
        )
        
        # Save document
        file_path = self.save_document(document)
        document.file_path = file_path
        
        self.documents.append(document)
        
        self.logger.info(f"Processed: {title} ({len(footnotes)} footnotes) -> {category}")
        
        return discovered_urls
    
    
    def crawl_site(self, max_pages: int = 1000, start_urls: List[str] = None):
        """Main crawling function"""
        if not self.check_robots_txt():
            self.logger.warning("Robots.txt disallows crawling. Proceeding with caution.")
        
        # Initialize URL queue
        if start_urls:
            urls_to_visit = set(start_urls)
        else:
            urls_to_visit = {self.base_url}
        
        pages_crawled = 0
        
        with tqdm(total=max_pages, desc="Crawling pages") as pbar:
            while urls_to_visit and pages_crawled < max_pages:
                current_url = urls_to_visit.pop()
                
                try:
                    new_urls = self.crawl_page(current_url)
                    urls_to_visit.update(new_urls)
                    pages_crawled += 1
                    
                    pbar.update(1)
                    pbar.set_postfix({
                        'Current': current_url[-50:],
                        'Queue': len(urls_to_visit),
                        'Docs': len(self.documents)
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error crawling {current_url}: {e}")
                    continue
        
        self.logger.info(f"Crawling completed. {len(self.documents)} documents collected.")
        self.generate_summary()
    
    def generate_summary(self):
        """Generate summary statistics"""
        if not self.documents:
            return
        
        # Category breakdown
        categories = {}
        total_footnotes = 0
        
        for doc in self.documents:
            categories[doc.category] = categories.get(doc.category, 0) + 1
            total_footnotes += len(doc.footnotes)
        
        # Generate summary report
        summary = {
            'total_documents': len(self.documents),
            'total_footnotes': total_footnotes,
            'categories': categories,
            'total_pages_visited': len(self.visited_urls),
            'crawl_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'documents': [
                {
                    'url': doc.url,
                    'title': doc.title,
                    'category': doc.category,
                    'footnote_count': len(doc.footnotes),
                    'file_path': doc.file_path
                } for doc in self.documents
            ]
        }
        
        # Save summary
        summary_path = os.path.join(self.output_dir, 'crawl_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("TEXT EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total documents collected: {summary['total_documents']}")
        print(f"Total footnotes extracted: {summary['total_footnotes']}")
        print(f"Pages visited: {summary['total_pages_visited']}")
        print("\nDocuments by category:")
        for category, count in categories.items():
            print(f"  {category}: {count}")
        print("="*60)

def main():
    """Main execution function"""
    scraper = BDLawsScraper(
        base_url="http://bdlaws.minlaw.gov.bd",
        output_dir="scraped_texts",
        delay=1.5  # Respectful crawling delay
    )
    
    # Start crawling
    scraper.crawl_site(max_pages=500)

if __name__ == "__main__":
    main()