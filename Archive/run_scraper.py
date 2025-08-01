#!/usr/bin/env python3
"""
Runner script for Bangladesh Laws Text Scraper with Footnote References
"""

import sys
import argparse
from bdlaws_scraper import BDLawsScraper
from config import SCRAPER_CONFIG, START_URLS, SAMPLE_DETAILS_URLS

def main():
    parser = argparse.ArgumentParser(description='Bangladesh Laws Text Scraper with Footnote References')
    parser.add_argument('--max-pages', type=int, default=SCRAPER_CONFIG['max_pages'],
                        help='Maximum number of pages to scrape')
    parser.add_argument('--delay', type=float, default=SCRAPER_CONFIG['delay_between_requests'],
                        help='Delay between requests in seconds')
    parser.add_argument('--output-dir', default=SCRAPER_CONFIG['output_directory'],
                        help='Output directory for scraped text files')
    parser.add_argument('--start-url', default=SCRAPER_CONFIG['base_url'],
                        help='Starting URL for scraping')
    parser.add_argument('--use-predefined-urls', action='store_true',
                        help='Use predefined starting URLs for comprehensive scraping')
    parser.add_argument('--use-discovered-urls', action='store_true',
                        help='Use URLs discovered by website crawler')
    parser.add_argument('--use-fast-urls', action='store_true',
                        help='Use URLs discovered by fast crawler')
    parser.add_argument('--use-smart-urls', action='store_true',
                        help='Use URLs discovered by smart crawler')
    parser.add_argument('--use-ultra-fast-urls', action='store_true',
                        help='Use URLs discovered by ultra fast crawler')
    parser.add_argument('--test-mode', action='store_true',
                        help='Test mode: only scrape a few sample details pages')
    
    args = parser.parse_args()
    
    print("Bangladesh Laws Details Page Scraper")
    print("=" * 60)
    print(f"Target: {args.start_url}")
    print(f"Max pages: {args.max_pages}")
    print(f"Delay: {args.delay}s")
    print(f"Output: {args.output_dir}")
    print()
    print("FOCUSED SCRAPING:")
    print("- Only processes *-details-* pages (act-details, rules-details, etc.)")
    print("- Uses actual document titles for filenames")
    print("- Extracts text content with footnote references preserved")
    print("- Skips unnecessary pages (lists, about, contact, etc.)")
    print("=" * 60)
    
    # Initialize scraper
    scraper = BDLawsScraper(
        base_url=args.start_url,
        output_dir=args.output_dir,
        delay=args.delay
    )
    
    # Determine starting URLs
    if args.test_mode:
        start_urls = SAMPLE_DETAILS_URLS
        print(f"TEST MODE: Using {len(start_urls)} sample details pages")
        for url in start_urls:
            print(f"  - {url}")
    elif args.use_ultra_fast_urls:
        # Load URLs discovered by ultra fast crawler
        try:
            with open('ultra_fast_urls.txt', 'r', encoding='utf-8') as f:
                start_urls = [line.strip() for line in f if line.strip()]
            print(f"ULTRA FAST URLs: Using {len(start_urls)} details pages found by ultra fast crawler")
        except FileNotFoundError:
            print("❌ No ultra fast URLs file found. Run 'python ultra_fast_crawler.py' first!")
            sys.exit(1)
    elif args.use_smart_urls:
        # Load URLs discovered by smart crawler
        try:
            with open('smart_discovered_urls.txt', 'r', encoding='utf-8') as f:
                start_urls = [line.strip() for line in f if line.strip()]
            print(f"SMART DISCOVERED URLs: Using {len(start_urls)} details pages found by smart crawler")
        except FileNotFoundError:
            print("❌ No smart URLs file found. Run 'python smart_crawler.py' first!")
            sys.exit(1)
    elif args.use_fast_urls:
        # Load URLs discovered by fast crawler
        try:
            with open('fast_discovered_urls.txt', 'r', encoding='utf-8') as f:
                start_urls = [line.strip() for line in f if line.strip()]
            print(f"FAST DISCOVERED URLs: Using {len(start_urls)} details pages found by fast crawler")
        except FileNotFoundError:
            print("❌ No fast URLs file found. Run 'python fast_crawler.py' first!")
            sys.exit(1)
    elif args.use_discovered_urls:
        # Load URLs discovered by website crawler
        try:
            with open('discovered_details_urls.txt', 'r', encoding='utf-8') as f:
                start_urls = [line.strip() for line in f if line.strip()]
            print(f"DISCOVERED URLs: Using {len(start_urls)} details pages found by crawler")
        except FileNotFoundError:
            print("❌ No discovered URLs file found. Run 'python website_crawler.py' first!")
            sys.exit(1)
    elif args.use_predefined_urls:
        start_urls = START_URLS
        print(f"Using predefined URLs: {len(start_urls)} starting points")
    else:
        start_urls = [args.start_url]
    
    try:
        # Start crawling
        scraper.crawl_site(max_pages=args.max_pages, start_urls=start_urls)
        print("\nScraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
        scraper.generate_summary()
        
    except Exception as e:
        print(f"\nError during scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()