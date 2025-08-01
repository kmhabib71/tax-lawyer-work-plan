#!/usr/bin/env python3
"""
Simple Bengali Query Processor
Processes basic Bengali tax queries and maps to tax calculations
Phase 0 - Basic implementation with real functionality
"""

import json
import re
from pathlib import Path

class SimpleBengaliQueryProcessor:
    def __init__(self):
        self.dictionary = self.load_bengali_dictionary()
        self.tds_rates = self.load_tds_rates()
        self.processed_queries = []
        
    def load_bengali_dictionary(self):
        """Load Bengali legal term dictionary"""
        dict_path = "bengali_legal_dictionary.json"
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Dictionary not found: {dict_path}")
            return {"terms": {}, "query_patterns": {}}
    
    def load_tds_rates(self):
        """Load current TDS rates"""
        tds_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/structured_tax_data/tds_rates_matrix_standard.json"
        try:
            with open(tds_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ TDS rates not found: {tds_path}")
            return {"tds_rates": {}}
    
    def extract_amount_from_query(self, query):
        """Extract monetary amounts from Bengali query"""
        # Bengali number patterns
        bengali_numbers = {
            'এক': 1, 'দুই': 2, 'তিন': 3, 'চার': 4, 'পাঁচ': 5,
            'ছয়': 6, 'সাত': 7, 'আট': 8, 'নয়': 9, 'দশ': 10,
            'বিশ': 20, 'ত্রিশ': 30, 'চল্লিশ': 40, 'পঞ্চাশ': 50,
            'ষাট': 60, 'সত্তর': 70, 'আশি': 80, 'নব্বই': 90,
            'একশ': 100, 'দুইশ': 200, 'তিনশ': 300, 'চারশ': 400,
            'পাঁচশ': 500, 'ছয়শ': 600, 'সাতশ': 700, 'আটশ': 800, 'নয়শ': 900
        }
        
        # Look for digit amounts
        digit_match = re.search(r'(\d+(?:,\d+)*)\s*(টাকা|লাখ|হাজার|কোটি)?', query)
        if digit_match:
            amount_str = digit_match.group(1).replace(',', '')
            amount = int(amount_str)
            unit = digit_match.group(2) if digit_match.group(2) else 'টাকা'
            
            # Convert to actual amount
            if unit == 'লাখ':
                amount *= 100000
            elif unit == 'হাজার':
                amount *= 1000
            elif unit == 'কোটি':
                amount *= 10000000
                
            return amount
        
        # Look for Bengali number words
        for bengali_num, value in bengali_numbers.items():
            if bengali_num in query:
                if 'লাখ' in query:
                    return value * 100000
                elif 'হাজার' in query:
                    return value * 1000
                elif 'কোটি' in query:
                    return value * 10000000
                else:
                    return value
        
        return 0
    
    def identify_income_type(self, query):
        """Identify type of income from query"""
        income_types = {
            'বেতন': 'salary',
            'ব্যবসায়িক আয়': 'business_income', 
            'ভাড়া': 'rent',
            'সুদ': 'interest',
            'লভ্যাংশ': 'dividend',
            'কমিশন': 'commission',
            'পেশাজীবী': 'professional_fees'
        }
        
        for bengali_term, english_type in income_types.items():
            if bengali_term in query:
                return english_type
        
        return 'unknown'
    
    def calculate_tds(self, income_type, amount):
        """Calculate TDS based on income type and amount"""
        if income_type not in self.tds_rates.get('tds_rates', {}):
            return {
                'tds_amount': 0,
                'applicable_rate': 0,
                'threshold': 0,
                'message': f'TDS rates not available for {income_type}'
            }
        
        rate_info = self.tds_rates['tds_rates'][income_type]
        
        # Handle salary income (progressive)
        if income_type == 'salary' and rate_info.get('rate_percent') == 'progressive':
            if amount <= rate_info.get('tax_free_income', 350000):
                return {
                    'tds_amount': 0,
                    'applicable_rate': 0,
                    'threshold': rate_info.get('tax_free_income', 350000),
                    'message': 'No tax on income below tax-free threshold'
                }
            else:
                # Simplified progressive calculation
                taxable_income = amount - rate_info.get('tax_free_income', 350000)
                if taxable_income <= 150000:  # Up to 5 lakh total
                    annual_tax = taxable_income * 0.05
                elif taxable_income <= 650000:  # Up to 10 lakh total
                    annual_tax = 150000 * 0.05 + (taxable_income - 150000) * 0.10
                else:
                    annual_tax = 150000 * 0.05 + 500000 * 0.10 + (taxable_income - 650000) * 0.15
                
                monthly_tds = annual_tax / 12
                return {
                    'tds_amount': round(monthly_tds, 2),
                    'annual_tax': round(annual_tax, 2),
                    'applicable_rate': 'progressive',
                    'threshold': rate_info.get('tax_free_income', 350000),
                    'message': f'Monthly TDS: {monthly_tds:.2f}, Annual Tax: {annual_tax:.2f}'
                }
        
        # Handle other income types with fixed rates
        rate_percent = rate_info.get('rate_percent', 0)
        threshold = rate_info.get('threshold_annual', 25000)
        
        if amount <= threshold:
            return {
                'tds_amount': 0,
                'applicable_rate': rate_percent,
                'threshold': threshold,
                'message': f'No TDS - below threshold of {threshold:,} Taka'
            }
        
        taxable_amount = amount - threshold
        tds_amount = taxable_amount * (rate_percent / 100)
        
        return {
            'tds_amount': round(tds_amount, 2),
            'applicable_rate': rate_percent,
            'threshold': threshold,
            'taxable_amount': taxable_amount,
            'message': f'TDS: {tds_amount:.2f} Taka ({rate_percent}% on {taxable_amount:,} Taka)'
        }
    
    def process_query(self, bengali_query):
        """Process a Bengali tax query and provide response"""
        print(f"\n🔍 Processing query: '{bengali_query}'")
        
        # Extract information from query
        amount = self.extract_amount_from_query(bengali_query)
        income_type = self.identify_income_type(bengali_query)
        
        print(f"📊 Extracted: Amount = {amount:,} Taka, Income Type = {income_type}")
        
        if amount == 0:
            response = {
                'query': bengali_query,
                'status': 'error',
                'message': 'Could not extract amount from query',
                'suggestion': 'Please specify amount in digits (e.g., ৮০০০০ টাকা বেতন)'
            }
        elif income_type == 'unknown':
            response = {
                'query': bengali_query,
                'status': 'error', 
                'message': 'Could not identify income type',
                'suggestion': 'Please specify income type (e.g., বেতন, ভাড়া, কমিশন)'
            }
        else:
            # Calculate TDS
            tds_calculation = self.calculate_tds(income_type, amount)
            
            response = {
                'query': bengali_query,
                'status': 'success',
                'extracted_info': {
                    'amount': amount,
                    'income_type': income_type
                },
                'tds_calculation': tds_calculation,
                'bengali_response': self.generate_bengali_response(income_type, amount, tds_calculation)
            }
        
        self.processed_queries.append(response)
        return response
    
    def generate_bengali_response(self, income_type, amount, tds_calc):
        """Generate response in Bengali"""
        income_type_bengali = {
            'salary': 'বেতন',
            'professional_fees': 'পেশাজীবী ফি',
            'business_income': 'ব্যবসায়িক আয়',
            'rent': 'ভাড়া',
            'interest': 'সুদ',
            'commission': 'কমিশন'
        }
        
        income_name = income_type_bengali.get(income_type, income_type)
        
        if tds_calc['tds_amount'] == 0:
            return f"আপনার {amount:,} টাকা {income_name} থেকে কোন TDS কাটা হবে না কারণ এটি {tds_calc['threshold']:,} টাকার সীমার নিচে।"
        else:
            if income_type == 'salary':
                return f"আপনার {amount:,} টাকা বার্ষিক {income_name} থেকে মাসিক {tds_calc['tds_amount']:,.2f} টাকা TDS কাটা হবে। বার্ষিক কর {tds_calc['annual_tax']:,.2f} টাকা।"
            else:
                return f"আপনার {amount:,} টাকা {income_name} থেকে {tds_calc['tds_amount']:,.2f} টাকা TDS কাটা হবে ({tds_calc['applicable_rate']}% হারে)।"

def main():
    print("🚀 Simple Bengali Query Processor - Phase 0")
    print("=" * 50)
    
    processor = SimpleBengaliQueryProcessor()
    
    # Test queries
    test_queries = [
        "আমার ৮০০০০ টাকা বেতন",
        "৫ লাখ টাকা বার্ষিক বেতন", 
        "৫০০০০ টাকা পেশাজীবী ফি",
        "৩০০০০ টাকা ভাড়া",
        "১০০০০ টাকা কমিশন",
        "২ লাখ টাকা সুদ"
    ]
    
    print("📝 Processing test queries:")
    results = []
    
    for query in test_queries:
        result = processor.process_query(query)
        results.append(result)
        
        if result['status'] == 'success':
            print(f"✅ {result['bengali_response']}")
        else:
            print(f"❌ {result['message']}")
    
    # Save results
    output_file = "bengali_query_processing_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'processor': 'SimpleBengaliQueryProcessor',
                'test_date': '2025-08-01',
                'queries_processed': len(results),
                'success_rate': len([r for r in results if r['status'] == 'success']) / len(results) * 100
            },
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Results saved to: {output_file}")
    print(f"✅ Successfully processed {len([r for r in results if r['status'] == 'success'])}/{len(results)} queries")
    
    return len([r for r in results if r['status'] == 'success'])

if __name__ == "__main__":
    main()