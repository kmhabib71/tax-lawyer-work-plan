#!/usr/bin/env python3
"""
Test script for footnote extraction functionality
Tests the footnote parsing with sample HTML content
"""

from bs4 import BeautifulSoup
from bdlaws_scraper import BDLawsScraper, FootnoteReference

def test_footnote_extraction():
    """Test footnote extraction with sample HTML"""
    
    # Sample HTML content similar to the one provided
    sample_html = '''
    <html>
    <body>
        <p>এই আইনের উদ্দেশ্য পূরণকল্পে সরকার সরকারি গেজেটে প্রজ্ঞাপন দ্বারা বিধি প্রণয়ন করিতে পারিবে।</p>
        
        <p><span class="footnote" title="শর্তাংশ দফা (১৮ক) এর শর্তাংশের পরিবর্তে অর্থ আইন, ২০২২ (২০২২ সনের ১৩ নং আইন) এর ৫৬(ক) ধারাবলে প্রতিস্থাপিত যাহা ১ জুলাই ২০২২ তারিখ হইতে কার্যকর।"><span class="word-formet"><sup class="bn"><a href="8">8</a></sup></span></span>[তবে শর্ত থাকে যে, এই আইনের তৃতীয় তফসিলের অনুচ্ছেদ (৩) এ উল্লিখিত ব্যবসায়ী কর্তৃক ব্যবসা পরিচালনার ক্ষেত্রে বিক্রয়, বিনিময় বা হস্তান্তরের উদ্দেশ্যে আমদানিকৃত, ক্রয়কৃত, অর্জিত বা অন্যকোনভাবে সংগৃহীত পণ্য বা সেবা উপকরণ হিসাবে গণ্য হইবে;]</p>
        
        <p>আরেকটি অনুচ্ছেদ <span class="footnote" title="এই বিধান ২০২৩ সালের ১৫ নং আইন দ্বারা সংশোধিত।"><span class="word-formet"><sup class="bn"><a href="15">15</a></sup></span></span> যেখানে আরেকটি রেফারেন্স রয়েছে।</p>
    </body>
    </html>
    '''
    
    print("Testing Footnote Extraction")
    print("=" * 50)
    
    # Create scraper instance
    scraper = BDLawsScraper()
    
    # Parse HTML
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # Extract text and footnotes
    text_content, footnotes = scraper.extract_text_with_footnotes(soup)
    
    print("Extracted Text:")
    print("-" * 30)
    print(text_content)
    print()
    
    print("Extracted Footnotes:")
    print("-" * 30)
    for i, footnote in enumerate(footnotes, 1):
        print(f"{i}. Reference Number: {footnote.ref_number}")
        print(f"   Tooltip: {footnote.tooltip_title}")
        print(f"   Position: {footnote.position_in_text}")
        print()
    
    # Test that references are preserved in text
    ref_count = text_content.count('[REF_')
    print(f"Total references found in text: {ref_count}")
    print(f"Total footnotes extracted: {len(footnotes)}")
    
    if ref_count == len(footnotes):
        print("✓ All footnotes correctly preserved in text!")
    else:
        print("✗ Mismatch between text references and footnotes")
    
    return text_content, footnotes

def test_file_output():
    """Test complete file output with footnotes"""
    
    print("\nTesting File Output")
    print("=" * 50)
    
    # Create a test document
    from bdlaws_scraper import LegalDocument
    
    # Sample data
    footnotes = [
        FootnoteReference(
            ref_number="8",
            tooltip_title="শর্তাংশ দফা (১৮ক) এর শর্তাংশের পরিবর্তে অর্থ আইন, ২০২২ (২০২২ সনের ১৩ নং আইন) এর ৫৬(ক) ধারাবলে প্রতিস্থাপিত যাহা ১ জুলাই ২০২২ তারিখ হইতে কার্যকর।",
            position_in_text=150
        )
    ]
    
    document = LegalDocument(
        url="http://bdlaws.minlaw.gov.bd/act-details-1106.html",
        title="Test Income Tax Act",
        text_content="এই আইনের উদ্দেশ্য পূরণকল্পে সরকার [REF_8] বিধি প্রণয়ন করিতে পারিবে।",
        footnotes=footnotes,
        file_path="",
        category="tax_law"
    )
    
    # Create scraper and save document
    scraper = BDLawsScraper(output_dir="test_output")
    file_path = scraper.save_document(document)
    
    print(f"Test document saved to: {file_path}")
    
    # Read and display the saved file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\nSaved File Content:")
        print("-" * 30)
        print(content)
        
        # Check JSON file
        json_file = file_path.replace('.txt', '.json')
        with open(json_file, 'r', encoding='utf-8') as f:
            import json
            json_content = json.load(f)
        
        print(f"\nJSON file also created with {len(json_content['footnotes'])} footnotes")
        
        return True
        
    except Exception as e:
        print(f"Error reading saved file: {e}")
        return False

if __name__ == "__main__":
    print("Bangladesh Laws Footnote Extraction Test")
    print("=" * 60)
    
    # Test footnote extraction
    text, footnotes = test_footnote_extraction()
    
    # Test file output
    success = test_file_output()
    
    if success and footnotes:
        print("\n✓ All tests passed! Footnote extraction is working correctly.")
    else:
        print("\n✗ Some tests failed. Check the implementation.")
    
    print("\nTest completed!")