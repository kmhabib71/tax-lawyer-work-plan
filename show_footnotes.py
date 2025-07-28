#!/usr/bin/env python3
"""
Script to demonstrate footnote preservation with a real example
Shows exactly how footnotes are extracted and preserved
"""

from bs4 import BeautifulSoup
from bdlaws_scraper import BDLawsScraper

def demonstrate_footnote_extraction():
    """Demonstrate footnote extraction with the exact HTML structure you provided"""
    
    print("🔍 FOOTNOTE EXTRACTION DEMONSTRATION")
    print("=" * 70)
    
    # Your exact HTML example
    sample_html = '''
    <html>
    <body>
        <p>এই আইনের উদ্দেশ্য পূরণকল্পে সরকার সরকারি গেজেটে প্রজ্ঞাপন দ্বারা বিধি প্রণয়ন করিতে পারিবে।</p>
        
        <p><span class="footnote" title="শর্তাংশ দফা (১৮ক) এর শর্তাংশের পরিবর্তে অর্থ আইন, ২০২২ (২০২২ সনের ১৩ নং আইন) এর ৫৬(ক) ধারাবলে প্রতিস্থাপিত যাহা ১ জুলাই ২০২২ তারিখ হইতে কার্যকর।"><span class="word-formet"><sup class="bn"><a href="8">8</a></sup></span></span>[তবে শর্ত থাকে যে, এই আইনের তৃতীয় তফসিলের অনুচ্ছেদ (৩) এ উল্লিখিত ব্যবসায়ী কর্তৃক ব্যবসা পরিচালনার ক্ষেত্রে বিক্রয়, বিনিময় বা হস্তান্তরের উদ্দেশ্যে আমদানিকৃত, ক্রয়কৃত, অর্জিত বা অন্যকোনভাবে সংগৃহীত পণ্য বা সেবা উপকরণ হিসাবে গণ্য হইবে;]</p>
        
        <p>আরেকটি অনুচ্ছেদ যেখানে <span class="footnote" title="এই বিধান ২০২৩ সালের ১৫ নং আইন দ্বারা সংশোধিত।"><span class="word-formet"><sup class="bn"><a href="15">15</a></sup></span></span> রেফারেন্স রয়েছে।</p>
    </body>
    </html>
    '''
    
    print("📝 ORIGINAL HTML:")
    print("-" * 50)
    print("Your HTML contains footnotes like:")
    print('<span class="footnote" title="শর্তাংশ দফা (১৮ক) এর শর্তাংশের পরিবর্তে...">')
    print('  <span class="word-formet"><sup class="bn"><a href="8">8</a></sup></span>')
    print('</span>')
    print()
    
    # Process with scraper
    scraper = BDLawsScraper()
    soup = BeautifulSoup(sample_html, 'html.parser')
    text_content, footnotes = scraper.extract_text_with_footnotes(soup)
    
    print("📖 EXTRACTED TEXT:")
    print("-" * 50)
    print(text_content)
    print()
    
    print("🔗 EXTRACTED FOOTNOTES:")
    print("-" * 50)
    for i, footnote in enumerate(footnotes, 1):
        print(f"Footnote {i}:")
        print(f"  📌 Reference Number: {footnote.ref_number}")
        print(f"  📍 Position in text: {footnote.position_in_text}")
        print(f"  📚 Tooltip Content: {footnote.tooltip_title}")
        print()
    
    print("🎯 HOW REFERENCES ARE PRESERVED:")
    print("-" * 50)
    print("1. In the text, footnotes become markers like [REF_8]")
    print("2. The full tooltip information is preserved separately")
    print("3. You can use the reference number to look up the full context")
    print()
    
    # Show the mapping
    if footnotes:
        print("🔄 REFERENCE MAPPING:")
        print("-" * 50)
        for footnote in footnotes:
            marker = f"[REF_{footnote.ref_number}]"
            if marker in text_content:
                print(f"{marker} ➜ {footnote.tooltip_title[:100]}...")
        print()
    
    return text_content, footnotes

def show_file_output_example():
    """Show what the actual saved file would look like"""
    
    print("💾 EXAMPLE OF SAVED FILE OUTPUT:")
    print("=" * 70)
    
    # Create sample document
    from bdlaws_scraper import LegalDocument, FootnoteReference
    
    footnotes = [
        FootnoteReference(
            ref_number="8",
            tooltip_title="শর্তাংশ দফা (১৮ক) এর শর্তাংশের পরিবর্তে অর্থ আইন, ২০২২ (২০২২ সনের ১৩ নং আইন) এর ৫৬(ক) ধারাবলে প্রতিস্থাপিত যাহা ১ জুলাই ২০২২ তারিখ হইতে কার্যকর।",
            position_in_text=150
        ),
        FootnoteReference(
            ref_number="15",
            tooltip_title="এই বিধান ২০২৩ সালের ১৫ নং আইন দ্বারা সংশোধিত।",
            position_in_text=300
        )
    ]
    
    sample_text = '''এই আইনের উদ্দেশ্য পূরণকল্পে সরকার সরকারি গেজেটে প্রজ্ঞাপন দ্বারা বিধি প্রণয়ন করিতে পারিবে।

[REF_8][তবে শর্ত থাকে যে, এই আইনের তৃতীয় তফসিলের অনুচ্ছেদ (৩) এ উল্লিখিত ব্যবসায়ী কর্তৃক ব্যবসা পরিচালনার ক্ষেত্রে বিক্রয়, বিনিময় বা হস্তান্তরের উদ্দেশ্যে আমদানিকৃত, ক্রয়কৃত, অর্জিত বা অন্যকোনভাবে সংগৃহীত পণ্য বা সেবা উপকরণ হিসাবে গণ্য হইবে;]

আরেকটি অনুচ্ছেদ যেখানে [REF_15] রেফারেন্স রয়েছে।'''
    
    document = LegalDocument(
        url="http://bdlaws.minlaw.gov.bd/act-details-1106.html",
        title="আয়কর আইন, ২০২৩",
        text_content=sample_text,
        footnotes=footnotes,
        file_path="",
        category="tax_law"
    )
    
    # Show what gets saved to .txt file
    print("📄 CONTENT OF .TXT FILE:")
    print("-" * 50)
    print(f"Title: {document.title}")
    print(f"URL: {document.url}")
    print(f"Category: {document.category}")
    print("=" * 80)
    print()
    print("CONTENT:")
    print(document.text_content)
    print()
    print("FOOTNOTES:")
    print("-" * 40)
    for footnote in document.footnotes:
        print(f"[REF_{footnote.ref_number}]: {footnote.tooltip_title}")
        print(f"Position: {footnote.position_in_text}")
        print()
    
    print("📊 JSON FILE STRUCTURE:")
    print("-" * 50)
    import json
    json_data = {
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
    }
    
    print(json.dumps(json_data, ensure_ascii=False, indent=2)[:500] + "...")

def test_with_actual_page():
    """Test with a real page if possible"""
    print("\n🌐 TESTING WITH ACTUAL PAGE:")
    print("=" * 70)
    
    try:
        scraper = BDLawsScraper(output_dir="demo_output")
        
        # Try to fetch a real page
        test_url = "http://bdlaws.minlaw.gov.bd/act-details-950.html"
        print(f"Attempting to fetch: {test_url}")
        
        soup = scraper.get_page(test_url)
        if soup:
            text_content, footnotes = scraper.extract_text_with_footnotes(soup)
            title = scraper.extract_document_title(soup)
            
            print(f"✅ Successfully fetched page!")
            print(f"📝 Title: {title}")
            print(f"📄 Text length: {len(text_content)} characters")
            print(f"🔗 Footnotes found: {len(footnotes)}")
            
            if footnotes:
                print("\n📋 Sample footnotes:")
                for i, footnote in enumerate(footnotes[:3], 1):  # Show first 3
                    print(f"  {i}. [REF_{footnote.ref_number}]: {footnote.tooltip_title[:100]}...")
            else:
                print("ℹ️  No footnotes found on this page")
                
        else:
            print("❌ Could not fetch the page (network issue or server down)")
            
    except Exception as e:
        print(f"❌ Error testing with actual page: {e}")

if __name__ == "__main__":
    print("🧪 FOOTNOTE PRESERVATION DEMONSTRATION")
    print("=" * 70)
    print("This script shows exactly how footnotes are extracted and preserved")
    print()
    
    # Demonstrate extraction
    text, footnotes = demonstrate_footnote_extraction()
    
    # Show file output format
    show_file_output_example()
    
    # Test with actual page
    test_with_actual_page()
    
    print("\n✨ SUMMARY:")
    print("=" * 70)
    print("• Footnotes are converted to [REF_X] markers in text")
    print("• Complete tooltip information is preserved separately")
    print("• Both .txt and .json files contain the references")
    print("• You can cross-reference using the reference numbers")
    print("• Perfect for AI systems that need to follow legal citations!")