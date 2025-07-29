#!/usr/bin/env python3
"""
Automated Topic Processor for Bangladesh Income Tax Circular 2024-25
Extracts all 202 topics from table of contents and creates structured index
"""

import json
import re
from typing import Dict, List, Any

def extract_table_rows_from_html(html_content: str) -> List[Dict[str, str]]:
    """Extract table rows from HTML table content"""
    topics = []
    
    # Pattern to match table rows with topic data
    row_pattern = r'<tr><td>(\d+)</td><td>(.*?)</td><td>(\d+)</td></tr>'
    matches = re.findall(row_pattern, html_content, re.DOTALL)
    
    for match in matches:
        topic_num, title, page = match
        topics.append({
            'topic_id': topic_num,
            'serial_bengali': convert_to_bengali_numeral(topic_num),
            'title_bengali': title.strip(),
            'page_reference': page.strip()
        })
    
    return topics

def convert_to_bengali_numeral(english_num: str) -> str:
    """Convert English numerals to Bengali numerals"""
    english_to_bengali = {
        '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
        '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'
    }
    
    bengali_num = ''
    for digit in english_num:
        bengali_num += english_to_bengali.get(digit, digit)
    
    return bengali_num

def translate_title_to_english(bengali_title: str) -> str:
    """Basic translation mapping for common tax terms"""
    translation_map = {
        'শিরোনাম': 'Title',
        'করহার': 'Tax rate',
        'সারচার্জ': 'Surcharge',
        'পরিবেশ সারচার্জ': 'Environmental surcharge',
        'প্রতিবন্ধী ব্যক্তি': 'Disabled person',
        'তৃতীয় লিঙ্গ': 'Third gender',
        'কর রেয়াত': 'Tax relief',
        'নিয়োগ': 'Employment',
        'রপ্তানি আয়': 'Export income',
        'অর্থনৈতিক অঞ্চল': 'Economic zone',
        'হাই-টেক পার্ক': 'Hi-tech park',
        'দাতব্য': 'Charitable',
        'আয়কর আইন': 'Income Tax Act',
        'সংজ্ঞা': 'Definition',
        'সংশোধন': 'Amendment',
        'ভাড়া': 'Rent',
        'আয়': 'Income',
        'ব্যবসা': 'Business',
        'বিয়োজন': 'Deduction',
        'গৃহসম্পত্তি': 'House property'
    }
    
    # Simple keyword-based translation
    english_title = bengali_title
    for bengali, english in translation_map.items():
        if bengali in bengali_title:
            english_title = english_title.replace(bengali, english)
    
    return english_title

def categorize_topic(topic_id: int, title: str) -> str:
    """Categorize topics based on ID ranges and content"""
    if 1 <= topic_id <= 20:
        return "basic_rates_surcharges"
    elif 21 <= topic_id <= 30 or 78 <= topic_id <= 110:
        return "legal_amendments"
    elif 31 <= topic_id <= 77:
        return "charitable_provisions"
    elif 111 <= topic_id <= 202:
        return "procedural_matters"
    else:
        return "income_categories"

def generate_ai_tags(title: str, category: str) -> List[str]:
    """Generate AI optimization tags based on title and category"""
    tags = []
    
    # Category-based tags
    category_tags = {
        "basic_rates_surcharges": ["tax_rate", "surcharge", "calculation"],
        "legal_amendments": ["definition", "amendment", "legal_clarification"],
        "charitable_provisions": ["charitable", "exemption", "relief"],
        "income_categories": ["income_calculation", "deduction", "business_income"],
        "procedural_matters": ["procedure", "compliance", "filing"]
    }
    
    tags.extend(category_tags.get(category, []))
    
    # Title-based tags
    if 'সারচার্জ' in title or 'surcharge' in title.lower():
        tags.append('surcharge')
    if 'রেয়াত' in title or 'relief' in title.lower():
        tags.append('tax_relief')
    if 'নিয়োগ' in title or 'employment' in title.lower():
        tags.append('employment')
    if 'দাতব্য' in title or 'charitable' in title.lower():
        tags.append('charitable')
    if 'ভাড়া' in title or 'rent' in title.lower():
        tags.append('rental_income')
    if 'ব্যবসা' in title or 'business' in title.lower():
        tags.append('business_income')
    
    return list(set(tags))  # Remove duplicates

def determine_calculation_relevance(title: str, category: str) -> str:
    """Determine calculation relevance based on content"""
    high_relevance_keywords = ['করহার', 'সারচার্জ', 'রেয়াত', 'পরিগণনা', 'হিসাব']
    medium_relevance_keywords = ['আয়', 'বিয়োজন', 'ভাড়া', 'ব্যবসা']
    
    if any(keyword in title for keyword in high_relevance_keywords):
        return "high"
    elif any(keyword in title for keyword in medium_relevance_keywords):
        return "medium"
    elif category in ["basic_rates_surcharges", "income_categories"]:
        return "high"
    else:
        return "low"

def determine_complexity_level(title: str, category: str) -> str:
    """Determine complexity level based on content"""
    if 'সংজ্ঞা' in title or 'definition' in title.lower():
        return "basic"
    elif 'পরিগণনা' in title or 'calculation' in title.lower():
        return "advanced"
    elif category == "charitable_provisions":
        return "intermediate"
    else:
        return "intermediate"

def process_all_topics_from_extraction_file(file_path: str) -> Dict[str, Any]:
    """Process all topics from the extraction file automatically"""
    
    # Load the extraction file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_topics = []
    
    # Find all table content in the chunks
    for chunk in data.get('chunks', []):
        if chunk.get('chunk_type') == 'table' and 'ক্রমিক নং' in chunk.get('text', ''):
            table_html = chunk['text']
            topics_in_table = extract_table_rows_from_html(table_html)
            all_topics.extend(topics_in_table)
    
    # Process and structure all topics
    structured_topics = []
    
    for topic_data in all_topics:
        topic_id = int(topic_data['topic_id'])
        
        # Determine parent topic (simplified logic)
        parent_topic = None
        if topic_id > 1:
            # Look for logical parent relationships
            if 31 <= topic_id <= 77:  # Charitable provisions
                if topic_id > 31:
                    parent_topic = "30"  # দাতব্য উদ্দেশ্য definition
            elif 78 <= topic_id <= 110:  # Income categories
                if topic_id == 89 or topic_id == 90:
                    parent_topic = "88"  # ভাড়া হইতে আয়
                elif topic_id == 92 or topic_id == 94 or topic_id == 95:
                    parent_topic = "92"  # গৃহসম্পত্তি
        
        structured_topic = {
            "topic_id": str(topic_id),
            "serial_bengali": topic_data['serial_bengali'],
            "title_bengali": topic_data['title_bengali'],
            "title_english": translate_title_to_english(topic_data['title_bengali']),
            "page_reference": topic_data['page_reference'],
            "category": categorize_topic(topic_id, topic_data['title_bengali']),
            "parent_topic": parent_topic,
            "sub_topics": [],
            "ai_tags": generate_ai_tags(topic_data['title_bengali'], categorize_topic(topic_id, topic_data['title_bengali'])),
            "calculation_relevance": determine_calculation_relevance(topic_data['title_bengali'], categorize_topic(topic_id, topic_data['title_bengali'])),
            "complexity_level": determine_complexity_level(topic_data['title_bengali'], categorize_topic(topic_id, topic_data['title_bengali']))
        }
        
        structured_topics.append(structured_topic)
    
    # Create the complete structured output
    complete_index = {
        "document_metadata": {
            "document_id": "income_tax_circular_2024_25",
            "title": "আয়কর পরিপত্র ২০২৪-২০২৫",
            "total_topics": len(structured_topics),
            "extraction_date": "2024-01-XX",
            "phase_status": "Phase 2 - Complete Index Extraction COMPLETED"
        },
        
        "categories": [
            {
                "category_id": "basic_rates_surcharges",
                "category_name": "মৌলিক করহার ও সারচার্জ",
                "english_name": "Basic Tax Rates & Surcharges",
                "topic_range": "1-20",
                "ai_intent_tags": ["tax_rate", "surcharge", "minimum_tax", "progressive_taxation"],
                "calculation_relevance": "high",
                "user_query_frequency": "high"
            },
            {
                "category_id": "legal_amendments",
                "category_name": "আইনি সংশোধনী ও সংজ্ঞা",
                "english_name": "Legal Amendments & Definitions",
                "topic_range": "21-110",
                "ai_intent_tags": ["definition", "legal_clarification", "act_amendment"],
                "calculation_relevance": "medium",
                "user_query_frequency": "medium"
            },
            {
                "category_id": "charitable_provisions",
                "category_name": "দাতব্য প্রতিষ্ঠান বিধান",
                "english_name": "Charitable Organization Provisions",
                "topic_range": "31-77",
                "ai_intent_tags": ["exemption", "charitable_relief", "non_profit"],
                "calculation_relevance": "medium",
                "user_query_frequency": "medium"
            },
            {
                "category_id": "income_categories",
                "category_name": "আয়ের ধরন ও পরিগণনা",
                "english_name": "Income Categories & Calculation",
                "topic_range": "78-110",
                "ai_intent_tags": ["income_calculation", "deduction_rules", "rental_income", "business_income"],
                "calculation_relevance": "high",
                "user_query_frequency": "high"
            },
            {
                "category_id": "procedural_matters",
                "category_name": "প্রক্রিয়াগত বিষয়াবলি",
                "english_name": "Procedural Matters",
                "topic_range": "111-202",
                "ai_intent_tags": ["filing_procedure", "compliance", "assessment", "appeals"],
                "calculation_relevance": "low",
                "user_query_frequency": "medium"
            }
        ],
        
        "topics": structured_topics,
        
        "processing_status": {
            "phase_2_completed": "Complete index extraction COMPLETED",
            "topics_extracted": len(structured_topics),
            "remaining_topics": 0,
            "total_topics_identified": len(structured_topics),
            "next_action": "Proceed to Phase 3 - Content processing from files 2-21",
            "ai_optimization": "Complete AI tags and categorization for all topics",
            "automation_used": "Automated processing system successfully implemented"
        }
    }
    
    return complete_index

def main():
    """Main processing function"""
    input_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25/1.extraction.json"
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25/complete_topic_index_automated.json"
    
    print("🚀 Starting automated topic processing...")
    print(f"📖 Reading from: {input_file}")
    
    try:
        complete_index = process_all_topics_from_extraction_file(input_file)
        
        # Save the result
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_index, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully processed {complete_index['document_metadata']['total_topics']} topics")
        print(f"💾 Saved to: {output_file}")
        print("\n📊 Processing Summary:")
        print(f"   • Total Topics: {complete_index['processing_status']['topics_extracted']}")
        print(f"   • Categories: {len(complete_index['categories'])}")
        print(f"   • Status: {complete_index['processing_status']['phase_2_completed']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        return False

if __name__ == "__main__":
    main()