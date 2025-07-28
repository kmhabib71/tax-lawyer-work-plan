#!/usr/bin/env python3
"""
Resume-capable scraper that can restart from where it left off
"""

import os
import json
import pickle
import argparse
from datetime import datetime
from bdlaws_scraper import BDLawsScraper
from config import SCRAPER_CONFIG

class ResumableScraper:
    def __init__(self, session_name="default"):
        self.session_name = session_name
        self.state_file = f"scraper_state_{session_name}.pkl"
        self.progress_file = f"scraper_progress_{session_name}.json"
        self.scraper = None
        
    def save_state(self, remaining_urls, completed_urls, total_urls):
        """Save current scraping state"""
        state = {
            'remaining_urls': list(remaining_urls),
            'completed_urls': list(completed_urls),
            'total_urls': total_urls,
            'timestamp': datetime.now().isoformat(),
            'session_name': self.session_name
        }
        
        # Save state
        with open(self.state_file, 'wb') as f:
            pickle.dump(state, f)
        
        # Save human-readable progress
        progress = {
            'session': self.session_name,
            'total_urls': total_urls,
            'completed': len(completed_urls),
            'remaining': len(remaining_urls),
            'progress_percent': (len(completed_urls) / total_urls * 100) if total_urls > 0 else 0,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
        
        print(f"💾 State saved: {len(completed_urls)}/{total_urls} completed ({progress['progress_percent']:.1f}%)")
    
    def load_state(self):
        """Load previous scraping state"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'rb') as f:
                    state = pickle.load(f)
                
                print(f"🔄 Resuming session: {state['session_name']}")
                print(f"📊 Progress: {len(state['completed_urls'])}/{state['total_urls']} completed")
                print(f"⏰ Last update: {state['timestamp']}")
                
                return state['remaining_urls'], state['completed_urls'], state['total_urls']
            except Exception as e:
                print(f"❌ Error loading state: {e}")
                return None, None, None
        else:
            print(f"📋 No previous session found, starting fresh")
            return None, None, None
    
    def get_completed_urls_from_files(self, output_dir):
        """Scan output directory to find already scraped URLs"""
        completed_urls = set()
        
        if not os.path.exists(output_dir):
            return completed_urls
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.json'):
                    try:
                        json_path = os.path.join(root, file)
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'url' in data:
                                completed_urls.add(data['url'])
                    except:
                        pass  # Skip corrupted files
        
        return completed_urls
    
    def scrape_with_resume(self, urls, output_dir, delay=1.5, auto_save_interval=50):
        """Main scraping method with resume capability"""
        
        # Load previous state or start fresh
        remaining_urls, completed_urls, total_urls = self.load_state()
        
        if remaining_urls is None:
            # Starting fresh
            remaining_urls = set(urls)
            completed_urls = set()
            total_urls = len(urls)
            
            # Check what's already been scraped
            existing_completed = self.get_completed_urls_from_files(output_dir)
            if existing_completed:
                print(f"📋 Found {len(existing_completed)} already scraped files")
                completed_urls.update(existing_completed)
                remaining_urls -= existing_completed
                print(f"📊 Adjusted: {len(remaining_urls)} remaining")
        else:
            # Resuming
            remaining_urls = set(remaining_urls)
            completed_urls = set(completed_urls)
        
        # Initialize scraper
        self.scraper = BDLawsScraper(
            base_url=SCRAPER_CONFIG['base_url'],
            output_dir=output_dir,
            delay=delay
        )
        
        print(f"\n🚀 Starting scraper:")
        print(f"   📋 Total URLs: {total_urls}")
        print(f"   ✅ Completed: {len(completed_urls)}")
        print(f"   🔄 Remaining: {len(remaining_urls)}")
        print(f"   💾 Auto-save every {auto_save_interval} URLs")
        print(f"=" * 50)
        
        processed_count = 0
        
        try:
            for url in list(remaining_urls):
                try:
                    # Process single URL
                    soup = self.scraper.get_page(url)
                    if soup and self.scraper.is_details_page(url):
                        
                        # Extract and save
                        text_content, footnotes = self.scraper.extract_text_with_footnotes(soup)
                        
                        if len(text_content.strip()) >= 100:
                            title = self.scraper.extract_document_title(soup)
                            category = self.scraper.categorize_document(title, url, text_content)
                            
                            from bdlaws_scraper import LegalDocument
                            document = LegalDocument(
                                url=url,
                                title=title,
                                text_content=text_content,
                                footnotes=footnotes,
                                file_path="",
                                category=category
                            )
                            
                            file_path = self.scraper.save_document(document)
                            print(f"✅ [{len(completed_urls)+1}/{total_urls}] {title}")
                    
                    # Update progress
                    remaining_urls.remove(url)
                    completed_urls.add(url)
                    processed_count += 1
                    
                    # Auto-save state
                    if processed_count % auto_save_interval == 0:
                        self.save_state(remaining_urls, completed_urls, total_urls)
                    
                except Exception as e:
                    print(f"❌ Error processing {url}: {e}")
                    # Still mark as completed to avoid infinite retry
                    remaining_urls.discard(url)
                    completed_urls.add(url)
                
                # Delay between requests
                import time
                time.sleep(delay)
        
        except KeyboardInterrupt:
            print(f"\n⏹️  Scraping interrupted by user")
            self.save_state(remaining_urls, completed_urls, total_urls)
            print(f"💾 Progress saved. Resume with same command.")
            return False
        
        # Final save
        self.save_state(remaining_urls, completed_urls, total_urls)
        
        print(f"\n🎉 Scraping Complete!")
        print(f"📊 Final stats: {len(completed_urls)}/{total_urls} URLs processed")
        
        # Clean up state files
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Resumable Bangladesh Laws Scraper')
    parser.add_argument('--urls-file', required=True, help='File containing URLs to scrape')
    parser.add_argument('--session-name', default='default', help='Session name for resume capability')
    parser.add_argument('--output-dir', default='scraped_texts', help='Output directory')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests')
    parser.add_argument('--auto-save', type=int, default=50, help='Auto-save interval')
    
    args = parser.parse_args()
    
    # Load URLs
    try:
        with open(args.urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"📋 Loaded {len(urls)} URLs from {args.urls_file}")
    except FileNotFoundError:
        print(f"❌ URLs file not found: {args.urls_file}")
        return
    
    # Create resumable scraper
    scraper = ResumableScraper(session_name=args.session_name)
    
    # Start scraping
    success = scraper.scrape_with_resume(
        urls=urls,
        output_dir=args.output_dir,
        delay=args.delay,
        auto_save_interval=args.auto_save
    )
    
    if success:
        print(f"🚀 All done! Check {args.output_dir} for results.")

if __name__ == "__main__":
    main()