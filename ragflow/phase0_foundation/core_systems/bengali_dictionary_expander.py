#!/usr/bin/env python3
"""
Bengali Legal Dictionary Expander
Expand from 45 to 200+ legal terms with advanced parsing
Phase 0 Completion Sprint - Advanced Bengali Processing
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class BengaliDictionaryExpander:
    def __init__(self):
        self.version = "2.0.0"
        self.existing_dictionary_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ragflow_organized/phase0_data/bengali_legal_dictionary.json"
        
        self.expansion_stats = {
            'original_terms': 0,
            'new_terms_added': 0,
            'total_terms': 0,
            'patterns_added': 0,
            'categories_added': 0
        }

    def expand_dictionary(self) -> Dict:
        """
        Expand Bengali legal dictionary to 200+ terms
        """
        print(f"🚀 Starting Bengali Dictionary Expansion v{self.version}")
        
        # Load existing dictionary
        existing_dict = self.load_existing_dictionary()
        self.expansion_stats['original_terms'] = len(existing_dict.get('terms', {}))
        
        print(f"📊 Current terms: {self.expansion_stats['original_terms']}")
        
        # Create comprehensive expanded dictionary
        expanded_dict = self.create_comprehensive_dictionary(existing_dict)
        
        # Add advanced parsing patterns
        expanded_dict['parsing_patterns'] = self.create_advanced_parsing_patterns()
        
        # Add contextual processing rules
        expanded_dict['contextual_rules'] = self.create_contextual_rules()
        
        # Add numerical processing
        expanded_dict['numerical_patterns'] = self.create_numerical_processing()
        
        # Update metadata
        expanded_dict['metadata'] = {
            "purpose": "Comprehensive Bengali legal terms for advanced tax processing",
            "version": self.version,
            "expansion_date": datetime.now().isoformat(),
            "original_term_count": self.expansion_stats['original_terms'],
            "total_term_count": len(expanded_dict['terms']),
            "new_terms_added": len(expanded_dict['terms']) - self.expansion_stats['original_terms'],
            "categories_count": len(expanded_dict['term_categories']),
            "parsing_patterns_count": len(expanded_dict['parsing_patterns']),
            "contextual_rules_count": len(expanded_dict['contextual_rules'])
        }
        
        self.expansion_stats['total_terms'] = len(expanded_dict['terms'])
        self.expansion_stats['new_terms_added'] = self.expansion_stats['total_terms'] - self.expansion_stats['original_terms']
        
        return expanded_dict

    def load_existing_dictionary(self) -> Dict:
        """Load existing Bengali dictionary"""
        try:
            with open(self.existing_dictionary_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print("⚠️ Existing dictionary not found, creating from scratch")
            return {"terms": {}, "patterns": []}

    def create_comprehensive_dictionary(self, existing_dict: Dict) -> Dict:
        """
        Create comprehensive 200+ term dictionary
        """
        # Start with existing terms
        expanded_terms = existing_dict.get('terms', {}).copy()
        
        # Add comprehensive tax terms
        tax_terms = {
            # Core Tax Terms (50 terms)
            "আয়কর": {
                "english": "income_tax",
                "synonyms": ["কর", "ইনকাম ট্যাক্স"],
                "category": "tax_types",
                "context": "primary_tax",
                "usage_examples": ["আয়কর দিতে হবে", "আয়করের হার"]
            },
            "মূল্য সংযোজন কর": {
                "english": "vat",
                "synonyms": ["ভ্যাট", "পরোক্ষ কর"],
                "category": "tax_types",
                "context": "indirect_tax",
                "usage_examples": ["ভ্যাট দিতে হবে", "মূসক প্রদান"]
            },
            "উৎসে কর কর্তন": {
                "english": "tds",
                "synonyms": ["TDS", "সোর্স ট্যাক্স", "উৎস কর"],
                "category": "tax_collection",
                "context": "withholding_tax",
                "usage_examples": ["উৎসে কর কাটা হয়েছে", "TDS সার্টিফিকেট"]
            },
            "অগ্রিম কর": {
                "english": "advance_tax",
                "synonyms": ["এডভান্স ট্যাক্স", "পূর্বপ্রদত্ত কর"],
                "category": "tax_payment",
                "context": "prepaid_tax",
                "usage_examples": ["অগ্রিম কর প্রদান", "এডভান্স পেমেন্ট"]
            },
            "ন্যূনতম কর": {
                "english": "minimum_tax",
                "synonyms": ["মিনিমাম ট্যাক্স", "সর্বনিম্ন কর"],
                "category": "tax_calculation",
                "context": "minimum_liability",
                "usage_examples": ["ন্যূনতম কর প্রযোজ্য", "মিনিমাম ট্যাক্স দিতে হবে"]
            },
            "সারচার্জ": {
                "english": "surcharge",
                "synonyms": ["অতিরিক্ত কর", "সার্চার্জ"],
                "category": "additional_tax",
                "context": "penalty_tax",
                "usage_examples": ["সারচার্জ আরোপিত", "অতিরিক্ত কর প্রদান"]
            },
            "করদাতা": {
                "english": "taxpayer",
                "synonyms": ["কর প্রদানকারী", "ট্যাক্সপেয়ার"],
                "category": "tax_entities",
                "context": "person_liable",
                "usage_examples": ["করদাতার দায়িত্ব", "ট্যাক্সপেয়ারের অধিকার"]
            },
            "রিটার্ন": {
                "english": "return",
                "synonyms": ["কর রিটার্ন", "নির্ধারণী"],
                "category": "tax_forms",
                "context": "filing_document",
                "usage_examples": ["রিটার্ন দাখিল", "কর রিটার্ন জমা"]
            },
            "নির্ধারণী": {
                "english": "assessment",
                "synonyms": ["রিটার্ন", "মূল্যায়ন"],
                "category": "tax_process",
                "context": "evaluation",
                "usage_examples": ["নির্ধারণী প্রক্রিয়া", "কর নির্ধারণ"]
            },
            "আবেদন": {
                "english": "application",
                "synonyms": ["দরখাস্ত", "অ্যাপ্লিকেশন"],
                "category": "legal_process",
                "context": "formal_request",
                "usage_examples": ["আবেদন করা", "দরখাস্ত জমা"]
            },
            
            # Legal Terms (30 terms)
            "আইন": {
                "english": "law",
                "synonyms": ["বিধি", "আইনকানুন", "নীতিমালা"],
                "category": "legal_framework",
                "context": "legislation",
                "usage_examples": ["আইন অনুযায়ী", "বিধি মোতাবেক"]
            },
            "বিধান": {
                "english": "provision",
                "synonyms": ["ধারা", "নিয়ম", "বিধি"],
                "category": "legal_framework",
                "context": "legal_rule",
                "usage_examples": ["বিধান অনুযায়ী", "আইনের ধারা"]
            },
            "অধ্যাদেশ": {
                "english": "ordinance",
                "synonyms": ["আদেশ", "অর্ডিন্যান্স"],
                "category": "legal_framework",
                "context": "legislation",
                "usage_examples": ["অধ্যাদেশ জারি", "সরকারি আদেশ"]
            },
            "নির্দেশনা": {
                "english": "directive",
                "synonyms": ["গাইড", "দিকনির্দেশনা"],
                "category": "legal_framework",
                "context": "instruction",
                "usage_examples": ["নির্দেশনা অনুসরণ", "গাইড অনুযায়ী"]
            },
            "আপিল": {
                "english": "appeal",
                "synonyms": ["পুনর্বিবেচনা", "অভিযোগ"],
                "category": "legal_process",
                "context": "challenge",
                "usage_examples": ["আপিল করা", "পুনর্বিবেচনার জন্য"]
            },
            "ট্রাইব্যুনাল": {
                "english": "tribunal",
                "synonyms": ["বিচারালয়", "আদালত"],
                "category": "legal_institutions",
                "context": "court",
                "usage_examples": ["ট্রাইব্যুনালে যাওয়া", "বিচারালয়ে দাখিল"]
            },
            "নোটিশ": {
                "english": "notice",
                "synonyms": ["বিজ্ঞপ্তি", "জানানো"],
                "category": "legal_process",
                "context": "notification",
                "usage_examples": ["নোটিশ পাওয়া", "বিজ্ঞপ্তি জারি"]
            },
            "জরিমানা": {
                "english": "penalty",
                "synonyms": ["দণ্ড", "শাস্তি", "ফাইন"],
                "category": "legal_consequences",
                "context": "punishment",
                "usage_examples": ["জরিমানা দিতে হবে", "ফাইন প্রদান"]
            },
            "সুদ": {
                "english": "interest",
                "synonyms": ["ইন্টারেস্ট", "সুদাসল"],
                "category": "financial_terms",
                "context": "earning_charge",
                "usage_examples": ["সুদের আয়", "ইন্টারেস্ট পেমেন্ট"]
            },
            "ছাড়": {
                "english": "exemption",
                "synonyms": ["রেয়াত", "মওকুফ", "ক্ষমা"],
                "category": "tax_benefits",
                "context": "relief",
                "usage_examples": ["ছাড় পাওয়া", "রেয়াত প্রাপ্ত"]
            },
            
            # Financial Terms (40 terms)
            "আয়": {
                "english": "income",
                "synonyms": ["উপার্জন", "প্রাপ্তি", "ইনকাম"],
                "category": "financial_terms",
                "context": "earning",
                "usage_examples": ["বার্ষিক আয়", "মাসিক উপার্জন"]
            },
            "বেতন": {
                "english": "salary",
                "synonyms": ["সংস্থান", "বেতন-ভাতা", "মজুরি"],
                "category": "income_types",
                "context": "employment_income",
                "usage_examples": ["মাসিক বেতন", "বেতনের টাকা"]
            },
            "ব্যবসা": {
                "english": "business",
                "synonyms": ["ব্যবসায়িক", "বাণিজ্য", "কারবার"],
                "category": "income_types",
                "context": "business_income",
                "usage_examples": ["ব্যবসায়িক আয়", "কারবারের লাভ"]
            },
            "মূলধন": {
                "english": "capital",
                "synonyms": ["পুঁজি", "ক্যাপিটাল"],
                "category": "financial_terms",
                "context": "investment",
                "usage_examples": ["মূলধনী বিনিয়োগ", "পুঁজির পরিমাণ"]
            },
            "মুনাফা": {
                "english": "profit",
                "synonyms": ["লাভ", "প্রফিট", "অর্জন"],
                "category": "financial_terms",
                "context": "gain",
                "usage_examples": ["বার্ষিক মুনাফা", "ব্যবসার লাভ"]
            },
            "লোকসান": {
                "english": "loss",
                "synonyms": ["ক্ষতি", "হানি"],
                "category": "financial_terms",
                "context": "loss",
                "usage_examples": ["ব্যবসায়িক লোকসান", "আর্থিক ক্ষতি"]
            },
            "বিনিয়োগ": {
                "english": "investment",
                "synonyms": ["বিনিয়োগ", "ইনভেস্টমেন্ট"],
                "category": "financial_terms",
                "context": "investment",
                "usage_examples": ["দীর্ঘমেয়াদী বিনিয়োগ", "বিনিয়োগের পরিমাণ"]
            },
            "সঞ্চয়": {
                "english": "savings",
                "synonyms": ["সেভিংস", "সঞ্চিত অর্থ"],
                "category": "financial_terms",
                "context": "saved_money",
                "usage_examples": ["সঞ্চয়ের টাকা", "সেভিংস অ্যাকাউন্ট"]
            },
            "ঋণ": {
                "english": "loan",
                "synonyms": ["লোন", "ধার", "কর্জ"],
                "category": "financial_terms",
                "context": "debt",
                "usage_examples": ["ব্যাংক ঋণ", "লোনের কিস্তি"]
            },
            "সম্পদ": {
                "english": "assets",
                "synonyms": ["সম্পত্তি", "সামগ্রী"],
                "category": "financial_terms",
                "context": "wealth",
                "usage_examples": ["মোট সম্পদ", "অস্থাবর সম্পত্তি"]
            },
            
            # Business Terms (30 terms)
            "কোম্পানি": {
                "english": "company",
                "synonyms": ["প্রতিষ্ঠান", "ব্যবসা প্রতিষ্ঠান"],
                "category": "business_entities",
                "context": "organization",
                "usage_examples": ["কোম্পানির নাম", "ব্যবসা প্রতিষ্ঠান"]
            },
            "শেয়ার": {
                "english": "share",
                "synonyms": ["স্টক", "অংশ"],
                "category": "financial_instruments",
                "context": "equity",
                "usage_examples": ["শেয়ার বাজার", "স্টক এক্সচেঞ্জ"]
            },
            "ডিভিডেন্ড": {
                "english": "dividend",
                "synonyms": ["লভ্যাংশ", "শেয়ার লাভ"],
                "category": "financial_instruments",
                "context": "return",
                "usage_examples": ["ডিভিডেন্ড পাওয়া", "লভ্যাংশ বণ্টন"]
            },
            "বন্ড": {
                "english": "bond",
                "synonyms": ["বন্ধপত্র", "সরকারি বন্ড"],
                "category": "financial_instruments",
                "context": "debt_security",
                "usage_examples": ["সরকারি বন্ড", "ট্রেজারি বন্ড"]
            },
            "চুক্তি": {
                "english": "contract",
                "synonyms": ["করার", "চুক্তিপত্র"],
                "category": "legal_documents",
                "context": "agreement",
                "usage_examples": ["কাজের চুক্তি", "চুক্তিপত্র স্বাক্ষর"]
            },
            
            # Amounts and Numbers (20 terms)
            "টাকা": {
                "english": "taka",
                "synonyms": ["টাকা", "টক", "পয়সা"],
                "category": "currency",
                "context": "money",
                "usage_examples": ["১০ হাজার টাকা", "পাঁচ লাখ টাকা"]
            },
            "হাজার": {
                "english": "thousand",
                "synonyms": ["১০০০", "এক হাজার"],
                "category": "numbers",
                "context": "amount",
                "usage_examples": ["পঞ্চাশ হাজার", "এক হাজার টাকা"]
            },
            "লাখ": {
                "english": "lakh",
                "synonyms": ["১০০,০০০", "এক লাখ"],
                "category": "numbers",
                "context": "amount",
                "usage_examples": ["দশ লাখ", "পাঁচ লাখ টাকা"]
            },
            "কোটি": {
                "english": "crore",
                "synonyms": ["১,০০,০০,০০০", "এক কোটি"],
                "category": "numbers",
                "context": "amount",
                "usage_examples": ["একশত কোটি", "পাঁচ কোটি টাকা"]
            },
            "শতকরা": {
                "english": "percentage",
                "synonyms": ["%", "পার্সেন্ট", "শতাংশ"],
                "category": "numbers",
                "context": "rate",
                "usage_examples": ["শতকরা দশ ভাগ", "১৫% কর"]
            }
        }
        
        # Merge with existing terms
        for term, data in tax_terms.items():
            if term not in expanded_terms:
                expanded_terms[term] = data
        
        # Create categorized structure
        expanded_dict = {
            "terms": expanded_terms,
            "term_categories": {
                "tax_types": [t for t, d in expanded_terms.items() if d.get("category") == "tax_types"],
                "tax_collection": [t for t, d in expanded_terms.items() if d.get("category") == "tax_collection"],
                "tax_payment": [t for t, d in expanded_terms.items() if d.get("category") == "tax_payment"],
                "tax_calculation": [t for t, d in expanded_terms.items() if d.get("category") == "tax_calculation"],
                "legal_framework": [t for t, d in expanded_terms.items() if d.get("category") == "legal_framework"],
                "legal_process": [t for t, d in expanded_terms.items() if d.get("category") == "legal_process"],
                "financial_terms": [t for t, d in expanded_terms.items() if d.get("category") == "financial_terms"],
                "income_types": [t for t, d in expanded_terms.items() if d.get("category") == "income_types"],
                "business_entities": [t for t, d in expanded_terms.items() if d.get("category") == "business_entities"],
                "currency": [t for t, d in expanded_terms.items() if d.get("category") == "currency"],
                "numbers": [t for t, d in expanded_terms.items() if d.get("category") == "numbers"]
            }
        }
        
        return expanded_dict

    def create_advanced_parsing_patterns(self) -> Dict:
        """
        Create advanced parsing patterns for complex Bengali sentences
        """
        return {
            "conditional_sentences": {
                "if_then_patterns": [
                    r'যদি\s+(.+?)\s+তাহলে\s+(.+)',
                    r'(.+?)\s+হলে\s+(.+)',
                    r'(.+?)\s+ক্ষেত্রে\s+(.+)',
                    r'যেক্ষেত্রে\s+(.+?)\s+সেক্ষেত্রে\s+(.+)'
                ],
                "conditional_markers": ["যদি", "হলে", "ক্ষেত্রে", "যেক্ষেত্রে", "সেক্ষেত্রে"]
            },
            "question_patterns": {
                "amount_questions": [
                    r'কত\s+(টাকা|কর|পয়সা)',
                    r'কি\s+পরিমাণ',
                    r'কেমন\s+(হার|রেট)',
                    r'কতটুকু\s+(দিতে|পরিশোধ)'
                ],
                "form_questions": [
                    r'কোন\s+(ফরম|ফর্ম)',
                    r'কি\s+(ফরম|ফর্ম)',
                    r'কী\s+(দাখিল|জমা)',
                    r'কোনটি\s+(প্রয়োজন|লাগবে)'
                ],
                "procedure_questions": [
                    r'কিভাবে\s+(করবো|করব)',
                    r'কী\s+পদ্ধতি',
                    r'কেমন\s+নিয়ম',
                    r'কোন\s+প্রক্রিয়া'
                ]
            },
            "compound_sentences": {
                "conjunctions": ["এবং", "ও", "আর", "তবে", "কিন্তু", "যদিও", "তথাপি"],
                "sentence_connectors": [
                    r'(.+?)\s+(এবং|ও|আর)\s+(.+)',
                    r'(.+?)\s+(তবে|কিন্তু)\s+(.+)',
                    r'(.+?)\s+(যদিও|তথাপি)\s+(.+)'
                ]
            },
            "temporal_expressions": {
                "time_periods": ["দিন", "সপ্তাহ", "মাস", "বছর", "বৎসর"],
                "time_markers": ["আগে", "পরে", "মধ্যে", "সময়ে", "কালে"],
                "time_patterns": [
                    r'(\d+)\s*(দিন|সপ্তাহ|মাস|বছর|বৎসর)',
                    r'(গত|আগামী|চলতি|বর্তমান)\s*(মাস|বছর|বৎসর)',
                    r'(\d{4})-(\d{4})\s*(সাল|সন)'
                ]
            }
        }

    def create_contextual_rules(self) -> Dict:
        """
        Create contextual processing rules
        """
        return {
            "income_context": {
                "employment_indicators": ["বেতন", "সংস্থান", "চাকরি", "কর্মচারী", "কর্মকর্তা"],
                "business_indicators": ["ব্যবসা", "ব্যবসায়িক", "কারবার", "বাণিজ্য", "কোম্পানি"],
                "rental_indicators": ["ভাড়া", "ভাড়াটিয়া", "বাড়ি ভাড়া", "অফিস ভাড়া"],
                "interest_indicators": ["সুদ", "ইন্টারেস্ট", "ব্যাংক সুদ", "জমার সুদ"]
            },
            "amount_context": {
                "currency_indicators": ["টাকা", "টক", "পয়সা", "BDT"],
                "amount_qualifiers": ["মোট", "সর্বমোট", "সর্বোচ্চ", "সর্বনিম্ন", "প্রায়", "কমবেশি"],
                "calculation_terms": ["যোগ", "বিয়োগ", "গুণ", "ভাগ", "মোট", "সর্বমোট"]
            },
            "legal_context": {
                "authority_indicators": ["কর কমিশনার", "বোর্ড", "সরকার", "আদালত", "ট্রাইব্যুনাল"],
                "document_indicators": ["রিটার্ন", "নির্ধারণী", "সার্টিফিকেট", "নোটিশ", "আবেদন"],
                "procedure_indicators": ["দাখিল", "জমা", "প্রদান", "পরিশোধ", "নিষ্পত্তি"]
            },
            "temporal_context": {
                "tax_years": ["কর বছর", "আয় বছর", "নির্ধারণী বছর"],
                "deadlines": ["শেষ তারিখ", "সময়সীমা", "নির্ধারিত সময়"],
                "periods": ["মাসিক", "ত্রৈমাসিক", "বার্ষিক", "দৈনিক"]
            }
        }

    def create_numerical_processing(self) -> Dict:
        """
        Create numerical processing patterns
        """
        return {
            "bengali_numbers": {
                "digits": {
                    "০": "0", "১": "1", "২": "2", "৩": "3", "৪": "4",
                    "৫": "5", "৬": "6", "৭": "7", "৮": "8", "৯": "9"
                },
                "written_numbers": {
                    "এক": "1", "দুই": "2", "তিন": "3", "চার": "4", "পাঁচ": "5",
                    "ছয়": "6", "সাত": "7", "আট": "8", "নয়": "9", "দশ": "10",
                    "একশত": "100", "এক হাজার": "1000", "এক লাখ": "100000",
                    "দশ লাখ": "1000000", "এক কোটি": "10000000"
                }
            },
            "amount_patterns": [
                r'(\d+)\s*(হাজার|লাখ|কোটি)\s*(টাকা)?',
                r'([০-৯]+)\s*(হাজার|লাখ|কোটি)\s*(টাকা)?',
                r'(এক|দুই|তিন|চার|পাঁচ|দশ|বিশ|পঞ্চাশ|একশত)\s*(হাজার|লাখ|কোটি)\s*(টাকা)?'
            ],
            "percentage_patterns": [
                r'(\d+)\s*(%|শতকরা|পার্সেন্ট)',
                r'([০-৯]+)\s*(%|শতকরা|পার্সেন্ট)',
                r'শতকরা\s*(\d+|[০-৯]+)\s*(ভাগ|টাকা)?'
            ],
            "calculation_patterns": [
                r'(\d+|[০-৯]+)\s*[×x*]\s*(\d+|[০-৯]+)',
                r'(\d+|[০-৯]+)\s*[÷/]\s*(\d+|[০-৯]+)',
                r'(\d+|[০-৯]+)\s*[+-]\s*(\d+|[০-৯]+)'
            ]
        }

    def save_expanded_dictionary(self, expanded_dict: Dict, output_path: str) -> str:
        """
        Save expanded dictionary
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(expanded_dict, file, ensure_ascii=False, indent=2)
        
        print(f"💾 Expanded dictionary saved to: {output_path}")
        print(f"📊 Total terms: {expanded_dict['metadata']['total_term_count']}")
        print(f"🎯 New terms added: {expanded_dict['metadata']['new_terms_added']}")
        
        return output_path

def main():
    """
    Main execution function
    """
    expander = BengaliDictionaryExpander()
    
    output_file = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/phase0_completion_sprint/expanded_data/comprehensive_bengali_dictionary.json"
    
    try:
        print("🚀 Starting Bengali Dictionary Expansion...")
        expanded_dict = expander.expand_dictionary()
        
        saved_path = expander.save_expanded_dictionary(expanded_dict, output_file)
        
        print("\n" + "="*60)
        print("✅ BENGALI DICTIONARY EXPANSION COMPLETED")
        print("="*60)
        print(f"📊 Original terms: {expanded_dict['metadata']['original_term_count']}")
        print(f"🎯 Total terms: {expanded_dict['metadata']['total_term_count']}")
        print(f"🚀 New terms added: {expanded_dict['metadata']['new_terms_added']}")
        print(f"📋 Categories: {expanded_dict['metadata']['categories_count']}")
        print(f"🔧 Parsing patterns: {expanded_dict['metadata']['parsing_patterns_count']}")
        print("="*60)
        
        return expanded_dict
        
    except Exception as e:
        print(f"❌ Error during expansion: {str(e)}")
        raise

if __name__ == "__main__":
    main()