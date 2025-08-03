#!/usr/bin/env python3
"""
Comprehensive Tax Data Extractor
Extracts all 29 required tax data files from 4 primary source files
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTaxExtractor:
    def __init__(self):
        self.source_files = {
            "circular": "income-tax-complete-circular-24-25/income_tax_circular_2024_25_ultra_enriched.json",
            "finance_ordinance": "precise_structured_laws/finance_ordinance_2025_cleaned.json", 
            "finance_act": "precise_structured_laws/অরথ_আইন_২০২৪.json",
            "income_tax_act": "precise_structured_laws/income_tax_act_2023_cleaned.json"
        }
        
        self.output_dir = "extracted_tax_data"
        self.ensure_output_directory()
        
        # Comprehensive extraction patterns for all 29 required files
        self.extraction_patterns = {
            "income_tax_rate_slab_tables_2024_25.json": {
                "patterns": [
                    r"আয়করের হার",
                    r"tax.*rate.*table",
                    r"করের হার.*তালিকা",
                    r"প্রথম.*লক্ষ.*টাকা",
                    r"পরবর্তী.*লক্ষ",
                    r"অবশিষ্ট.*আয়ের.*উপর",
                    r"slab.*structure",
                    r"তফসিল.*১.*অংশ.*১"
                ],
                "context_keywords": ["২০২৪.*২৫", "২০২৫.*২৬", "individual", "ব্যক্তি", "করদাতা"],
                "table_indicators": ["<table", "thead", "tbody", "আয়ের পরিমাণ"],
                "description": "Individual and entity tax rate slabs for FY 2024-25"
            },
            
            "company_tax_rates_by_type.json": {
                "patterns": [
                    r"কোম্পানি.*কর.*হার",
                    r"company.*tax.*rate",
                    r"পাবলিক.*লিমিটেড",
                    r"প্রাইভেট.*লিমিটেড",
                    r"ব্যাংক.*কোম্পানি",
                    r"বীমা.*কোম্পানি",
                    r"তামাক.*কোম্পানি",
                    r"মোবাইল.*অপারেটর"
                ],
                "context_keywords": ["করহার", "tax rate", "২৫%", "২৭.৫%", "৪০%", "৪৫%"],
                "table_indicators": ["company", "কোম্পানি", "corporate"],
                "description": "Tax rates for different types of companies and entities"
            },
            
            "penalty_rate_tables.json": {
                "patterns": [
                    r"জরিমানা.*হার",
                    r"penalty.*rate",
                    r"বিলম্ব.*জরিমানা",
                    r"late.*filing.*penalty",
                    r"ধারা.*২৭০",
                    r"section.*271",
                    r"সুদের.*হার",
                    r"interest.*rate",
                    r"০\.০২.*মাস",
                    r"2%.*month"
                ],
                "context_keywords": ["penalty", "জরিমানা", "বিলম্ব", "interest", "সুদ"],
                "table_indicators": ["penalty", "জরিমানা", "violation", "default"],
                "description": "Penalty rates for various tax violations and late payments"
            },
            
            "investment_rebate_rules_detailed.json": {
                "patterns": [
                    r"বিনিয়োগ.*ছাড়",
                    r"investment.*rebate",
                    r"ধারা.*৪৪",
                    r"section.*44",
                    r"rebate.*rate",
                    r"ছাড়ের.*হার",
                    r"সরকারি.*সিকিউরিটি",
                    r"স্টক.*এক্সচেঞ্জ",
                    r"জীবন.*বীমা",
                    r"provident.*fund"
                ],
                "context_keywords": ["rebate", "ছাড়", "investment", "বিনিয়োগ", "৪৪"],
                "table_indicators": ["investment", "বিনিয়োগ", "rebate", "ছাড়"],
                "description": "Investment rebate rules and rates under Section 44"
            },
            
            "depreciation_tables_rates.json": {
                "patterns": [
                    r"অবচয়.*হার",
                    r"depreciation.*rate",
                    r"তৃতীয়.*তফসিল",
                    r"3rd.*schedule",
                    r"straight.*line",
                    r"declining.*balance",
                    r"plant.*machinery",
                    r"building.*structure",
                    r"furniture.*fixture"
                ],
                "context_keywords": ["depreciation", "অবচয়", "schedule", "তফসিল", "rate"],
                "table_indicators": ["depreciation", "অবচয়", "asset", "সম্পদ"],
                "description": "Depreciation rates for various asset categories"
            },
            
            "tax_holiday_provisions.json": {
                "patterns": [
                    r"কর.*ছুটি",
                    r"tax.*holiday",
                    r"ষষ্ঠ.*তফসিল",
                    r"6th.*schedule",
                    r"exemption.*period",
                    r"শিল্প.*ছাড়",
                    r"export.*oriented",
                    r"ইপিজেড",
                    r"EPZ"
                ],
                "context_keywords": ["holiday", "ছুটি", "exemption", "ছাড়", "industrial"],
                "table_indicators": ["holiday", "ছুটি", "exemption", "শিল্প"],
                "description": "Tax holiday provisions for industries and special zones"
            },
            
            "withholding_tax_rates.json": {
                "patterns": [
                    r"উৎসে.*কর.*কর্তন",
                    r"withholding.*tax",
                    r"TDS.*rate",
                    r"advance.*tax",
                    r"অগ্রিম.*কর",
                    r"ধারা.*৫২",
                    r"section.*52",
                    r"কর্তন.*হার",
                    r"deduction.*rate"
                ],
                "context_keywords": ["withholding", "TDS", "উৎসে", "কর্তন", "advance"],
                "table_indicators": ["withholding", "TDS", "উৎসে", "কর্তন"],
                "description": "Withholding tax rates for various payment types"
            },
            
            "surcharge_additional_tax_rules.json": {
                "patterns": [
                    r"সারচার্জ",
                    r"surcharge",
                    r"অতিরিক্ত.*কর",
                    r"additional.*tax",
                    r"১০.*কোটি",
                    r"10.*crore",
                    r"৩%.*হার",
                    r"3%.*rate"
                ],
                "context_keywords": ["surcharge", "সারচার্জ", "additional", "অতিরিক্ত"],
                "table_indicators": ["surcharge", "সারচার্জ", "high income", "উচ্চ আয়"],
                "description": "Surcharge rules for high-income taxpayers"
            },
            
            "special_category_slabs.json": {
                "patterns": [
                    r"মহিলা.*করদাতা",
                    r"women.*taxpayer",
                    r"সিনিয়র.*সিটিজেন",
                    r"senior.*citizen",
                    r"প্রতিবন্ধী.*ব্যক্তি",
                    r"disabled.*person",
                    r"মুক্তিযোদ্ধা",
                    r"freedom.*fighter",
                    r"৩৫.*লক্ষ",
                    r"৪০.*লক্ষ",
                    r"৪৫.*লক্ষ"
                ],
                "context_keywords": ["special", "বিশেষ", "category", "শ্রেণী", "exemption"],
                "table_indicators": ["women", "মহিলা", "senior", "সিনিয়র", "disabled"],
                "description": "Special tax slabs for women, senior citizens, disabled persons"
            },
            
            "slab_progression_rules.json": {
                "patterns": [
                    r"ক্রমান্বয়ে.*প্রয়োগ",
                    r"progressive.*taxation",
                    r"slab.*calculation",
                    r"marginal.*rate",
                    r"effective.*rate",
                    r"graduated.*tax"
                ],
                "context_keywords": ["progressive", "ক্রমান্বয়ে", "slab", "calculation"],
                "table_indicators": ["progression", "calculation", "formula"],
                "description": "Rules for progressive slab application"
            },
            
            "tax_credit_rules.json": {
                "patterns": [
                    r"কর.*ক্রেডিট",
                    r"tax.*credit",
                    r"credit.*against.*tax",
                    r"অগ্রিম.*কর.*সমন্বয়",
                    r"advance.*tax.*adjustment"
                ],
                "context_keywords": ["credit", "ক্রেডিট", "adjustment", "সমন্বয়"],
                "table_indicators": ["credit", "ক্রেডিট", "adjustment"],
                "description": "Tax credit rules and adjustment mechanisms"
            },
            
            "house_rent_allowance_exemption.json": {
                "patterns": [
                    r"বাড়ি.*ভাড়া.*ভাতা",
                    r"house.*rent.*allowance",
                    r"HRA.*exemption",
                    r"বাসস্থান.*ভাতা",
                    r"accommodation.*allowance"
                ],
                "context_keywords": ["HRA", "house rent", "বাড়ি ভাড়া", "accommodation"],
                "table_indicators": ["HRA", "house", "বাড়ি", "rent"],
                "description": "House rent allowance exemption calculation rules"
            },
            
            "conveyance_allowance_rules.json": {
                "patterns": [
                    r"যাতায়াত.*ভাতা",
                    r"conveyance.*allowance",
                    r"transport.*allowance",
                    r"যাতায়াত.*খরচ"
                ],
                "context_keywords": ["conveyance", "যাতায়াত", "transport", "ভাতা"],
                "table_indicators": ["conveyance", "যাতায়াত", "transport"],
                "description": "Conveyance allowance exemption rules"
            },
            
            "medical_allowance_rules.json": {
                "patterns": [
                    r"চিকিৎসা.*ভাতা",
                    r"medical.*allowance",
                    r"চিকিৎসা.*খরচ",
                    r"medical.*expenses"
                ],
                "context_keywords": ["medical", "চিকিৎসা", "health", "স্বাস্থ্য"],
                "table_indicators": ["medical", "চিকিৎসা", "health"],
                "description": "Medical allowance and expenses exemption rules"
            },
            
            "provident_fund_rules.json": {
                "patterns": [
                    r"ভবিষ্য.*তহবিল",
                    r"provident.*fund",
                    r"PF.*contribution",
                    r"employees.*fund",
                    r"কর্মচারী.*তহবিল"
                ],
                "context_keywords": ["provident", "ভবিষ্য", "fund", "তহবিল", "PF"],
                "table_indicators": ["provident", "ভবিষ্য", "fund", "PF"],
                "description": "Provident fund contribution and withdrawal rules"
            },
            
            "gratuity_rules.json": {
                "patterns": [
                    r"গ্রাচুইটি",
                    r"gratuity",
                    r"অবসর.*ভাতা",
                    r"retirement.*benefit"
                ],
                "context_keywords": ["gratuity", "গ্রাচুইটি", "retirement", "অবসর"],
                "table_indicators": ["gratuity", "গ্রাচুইটি", "retirement"],
                "description": "Gratuity calculation and exemption rules"
            },
            
            "export_income_exemption.json": {
                "patterns": [
                    r"রপ্তানি.*আয়.*ছাড়",
                    r"export.*income.*exemption",
                    r"রপ্তানি.*শিল্প",
                    r"export.*oriented.*industry"
                ],
                "context_keywords": ["export", "রপ্তানি", "exemption", "ছাড়"],
                "table_indicators": ["export", "রপ্তানি", "industry", "শিল্প"],
                "description": "Export income exemption provisions"
            },
            
            "agricultural_income_rules.json": {
                "patterns": [
                    r"কৃষি.*আয়",
                    r"agricultural.*income",
                    r"farming.*income",
                    r"চাষাবাদ.*আয়"
                ],
                "context_keywords": ["agricultural", "কৃষি", "farming", "চাষাবাদ"],
                "table_indicators": ["agricultural", "কৃষি", "farming"],
                "description": "Agricultural income taxation rules"
            },
            
            "dividend_income_rules.json": {
                "patterns": [
                    r"লভ্যাংশ.*আয়",
                    r"dividend.*income",
                    r"শেয়ার.*লভ্যাংশ",
                    r"share.*dividend"
                ],
                "context_keywords": ["dividend", "লভ্যাংশ", "share", "শেয়ার"],
                "table_indicators": ["dividend", "লভ্যাংশ", "share"],
                "description": "Dividend income taxation and exemption rules"
            },
            
            "interest_calculation_rules.json": {
                "patterns": [
                    r"সুদ.*গণনা",
                    r"interest.*calculation",
                    r"দৈনিক.*সুদ",
                    r"daily.*interest",
                    r"মাসিক.*সুদ",
                    r"monthly.*interest"
                ],
                "context_keywords": ["interest", "সুদ", "calculation", "গণনা"],
                "table_indicators": ["interest", "সুদ", "daily", "monthly"],
                "description": "Interest calculation methods and rates"
            },
            
            "late_filing_penalties.json": {
                "patterns": [
                    r"বিলম্বে.*রিটার্ন",
                    r"late.*filing.*penalty",
                    r"দেরিতে.*দাখিল",
                    r"delayed.*submission"
                ],
                "context_keywords": ["late filing", "বিলম্বে", "delayed", "penalty"],
                "table_indicators": ["late", "বিলম্বে", "filing", "দাখিল"],
                "description": "Late filing penalty structure and calculation"
            },
            
            "tax_evasion_penalties.json": {
                "patterns": [
                    r"কর.*ফাঁকি.*জরিমানা",
                    r"tax.*evasion.*penalty",
                    r"আয়.*গোপন",
                    r"income.*concealment"
                ],
                "context_keywords": ["evasion", "ফাঁকি", "concealment", "গোপন"],
                "table_indicators": ["evasion", "ফাঁকি", "serious", "গুরুতর"],
                "description": "Tax evasion penalties and serious violations"
            },
            
            "waiver_eligibility_rules.json": {
                "patterns": [
                    r"জরিমানা.*মওকুফ",
                    r"penalty.*waiver",
                    r"ছাড়.*নীতি",
                    r"waiver.*policy"
                ],
                "context_keywords": ["waiver", "মওকুফ", "relief", "ত্রাণ"],
                "table_indicators": ["waiver", "মওকুফ", "relief"],
                "description": "Penalty waiver eligibility criteria and process"
            },
            
            "prosecution_thresholds.json": {
                "patterns": [
                    r"মামলা.*সীমা",
                    r"prosecution.*threshold",
                    r"আইনি.*ব্যবস্থা",
                    r"legal.*action"
                ],
                "context_keywords": ["prosecution", "মামলা", "legal", "আইনি"],
                "table_indicators": ["prosecution", "মামলা", "threshold", "সীমা"],
                "description": "Prosecution thresholds for tax violations"
            },
            
            "settlement_rules.json": {
                "patterns": [
                    r"নিষ্পত্তি.*নীতি",
                    r"settlement.*policy",
                    r"আপস.*নিষ্পত্তি",
                    r"compromise.*settlement"
                ],
                "context_keywords": ["settlement", "নিষ্পত্তি", "compromise", "আপস"],
                "table_indicators": ["settlement", "নিষ্পত্তি", "compromise"],
                "description": "Tax settlement and compromise procedures"
            },
            
            "income_head_definitions_rules.json": {
                "patterns": [
                    r"আয়ের.*খাত",
                    r"income.*head",
                    r"বেতন.*আয়",
                    r"salary.*income",
                    r"ব্যবসায়.*আয়",
                    r"business.*income",
                    r"পুঁজিগত.*আয়",
                    r"capital.*gain"
                ],
                "context_keywords": ["income head", "আয়ের খাত", "salary", "business"],
                "table_indicators": ["income", "আয়", "head", "খাত"],
                "description": "Income head definitions and calculation rules"
            },
            
            "minimum_tax_section_163.json": {
                "patterns": [
                    r"ন্যূনতম.*কর",
                    r"minimum.*tax",
                    r"ধারা.*১৬৩",
                    r"section.*163",
                    r"গ্রস.*প্রাপ্তি",
                    r"gross.*receipt"
                ],
                "context_keywords": ["minimum tax", "ন্যূনতম কর", "section 163", "gross"],
                "table_indicators": ["minimum", "ন্যূনতম", "gross", "receipt"],
                "description": "Minimum tax provisions under Section 163"
            },
            
            "advance_tax_calculation.json": {
                "patterns": [
                    r"অগ্রিম.*কর.*গণনা",
                    r"advance.*tax.*calculation",
                    r"quarterly.*payment",
                    r"ত্রৈমাসিক.*পরিশোধ"
                ],
                "context_keywords": ["advance tax", "অগ্রিম কর", "quarterly", "calculation"],
                "table_indicators": ["advance", "অগ্রিম", "quarterly", "payment"],
                "description": "Advance tax calculation and payment rules"
            },
            
            "income_computation_examples.json": {
                "patterns": [
                    r"আয়.*গণনা.*উদাহরণ",
                    r"income.*computation.*example",
                    r"calculation.*worksheet",
                    r"গণনার.*নমুনা"
                ],
                "context_keywords": ["computation", "গণনা", "example", "উদাহরণ"],
                "table_indicators": ["example", "উদাহরণ", "worksheet", "calculation"],
                "description": "Income computation examples and worksheets"
            }
        }
    
    def ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def load_source_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse JSON source file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded source file: {file_path}")
                return data
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return {}
    
    def search_patterns_in_content(self, content: str, patterns: List[str]) -> List[Dict[str, Any]]:
        """Search for patterns in content and return matches with context"""
        matches = []
        
        for pattern in patterns:
            try:
                regex_matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in regex_matches:
                    start = max(0, match.start() - 200)
                    end = min(len(content), match.end() + 200)
                    context = content[start:end]
                    
                    matches.append({
                        "pattern": pattern,
                        "match": match.group(),
                        "position": match.start(),
                        "context": context.strip(),
                        "confidence": self.calculate_match_confidence(pattern, context)
                    })
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {str(e)}")
                continue
        
        return matches
    
    def calculate_match_confidence(self, pattern: str, context: str) -> float:
        """Calculate confidence score for a match based on context"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for table-like structures
        if any(indicator in context.lower() for indicator in ['<table', 'thead', 'tbody', '|', 'rate', 'হার']):
            confidence += 0.3
        
        # Boost for numerical values (likely rates)
        if re.search(r'\d+\.?\d*\s*%', context):
            confidence += 0.2
        
        # Boost for Bengali tax terminology
        bengali_terms = ['আয়কর', 'করহার', 'জরিমানা', 'তফসিল', 'ধারা']
        if any(term in context for term in bengali_terms):
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    def extract_tables_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract table structures from content"""
        tables = []
        
        # HTML table extraction
        html_table_pattern = r'<table[^>]*>(.*?)</table>'
        html_matches = re.finditer(html_table_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in html_matches:
            table_html = match.group(1)
            table_data = self.parse_html_table(table_html)
            if table_data:
                tables.append({
                    "type": "html",
                    "position": match.start(),
                    "content": table_data,
                    "raw_html": match.group()
                })
        
        # JSON table-like structures
        json_table_pattern = r'"html_content":\s*"([^"]*<table[^"]*)"'
        json_matches = re.finditer(json_table_pattern, content, re.IGNORECASE)
        
        for match in json_matches:
            table_html = match.group(1)
            table_data = self.parse_html_table(table_html)
            if table_data:
                tables.append({
                    "type": "json_embedded",
                    "position": match.start(),
                    "content": table_data,
                    "raw_html": table_html
                })
        
        return tables
    
    def parse_html_table(self, html_content: str) -> Dict[str, Any]:
        """Parse HTML table content into structured data"""
        try:
            # Simple table parsing - extract headers and rows
            headers = []
            rows = []
            
            # Extract headers
            header_pattern = r'<th[^>]*>(.*?)</th>'
            header_matches = re.findall(header_pattern, html_content, re.IGNORECASE | re.DOTALL)
            headers = [re.sub(r'<[^>]+>', '', h).strip() for h in header_matches]
            
            # Extract rows
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            row_matches = re.findall(row_pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            for row_html in row_matches:
                if '<th' in row_html:  # Skip header rows
                    continue
                
                cell_pattern = r'<td[^>]*>(.*?)</td>'
                cell_matches = re.findall(cell_pattern, row_html, re.IGNORECASE | re.DOTALL)
                cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cell_matches]
                
                if cells:
                    rows.append(cells)
            
            return {
                "headers": headers,
                "rows": rows,
                "total_rows": len(rows),
                "total_columns": len(headers) if headers else (len(rows[0]) if rows else 0)
            }
        
        except Exception as e:
            logger.warning(f"Error parsing HTML table: {str(e)}")
            return {}
    
    def extract_from_source(self, source_data: Dict[str, Any], target_file: str, 
                          patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data for a specific target file from source data"""
        
        extraction_result = {
            "target_file": target_file,
            "description": patterns.get("description", ""),
            "extraction_timestamp": datetime.now().isoformat(),
            "matches": [],
            "tables": [],
            "confidence_score": 0.0,
            "data_quality": "low"
        }
        
        # Convert source data to searchable text
        source_text = json.dumps(source_data, ensure_ascii=False)
        
        # Search for patterns
        matches = self.search_patterns_in_content(source_text, patterns["patterns"])
        extraction_result["matches"] = matches
        
        # Extract tables
        tables = self.extract_tables_from_content(source_text)
        extraction_result["tables"] = tables
        
        # Calculate overall confidence
        if matches:
            avg_confidence = sum(m["confidence"] for m in matches) / len(matches)
            extraction_result["confidence_score"] = avg_confidence
            
            if avg_confidence > 0.8:
                extraction_result["data_quality"] = "high"
            elif avg_confidence > 0.6:
                extraction_result["data_quality"] = "medium"
        
        # Extract structured data based on file type
        structured_data = self.extract_structured_data(target_file, matches, tables)
        extraction_result["structured_data"] = structured_data
        
        return extraction_result
    
    def extract_structured_data(self, target_file: str, matches: List[Dict], 
                               tables: List[Dict]) -> Dict[str, Any]:
        """Extract and structure data based on target file type"""
        
        structured_data = {
            "metadata": {
                "file_type": target_file,
                "extraction_method": "pattern_matching_with_tables",
                "total_matches": len(matches),
                "total_tables": len(tables)
            }
        }
        
        # File-specific structured extraction
        if "income_tax_rate_slab" in target_file:
            structured_data.update(self.extract_tax_rate_slabs(matches, tables))
        
        elif "company_tax_rates" in target_file:
            structured_data.update(self.extract_company_rates(matches, tables))
        
        elif "penalty_rate" in target_file:
            structured_data.update(self.extract_penalty_rates(matches, tables))
        
        elif "investment_rebate" in target_file:
            structured_data.update(self.extract_investment_rebates(matches, tables))
        
        elif "withholding_tax" in target_file:
            structured_data.update(self.extract_withholding_rates(matches, tables))
        
        else:
            # Generic extraction for other files
            structured_data.update(self.extract_generic_data(matches, tables))
        
        return structured_data
    
    def extract_tax_rate_slabs(self, matches: List[Dict], tables: List[Dict]) -> Dict[str, Any]:
        """Extract tax rate slab data"""
        slab_data = {
            "individual_slabs": [],
            "company_rates": {},
            "special_categories": {}
        }
        
        # Look for slab patterns in matches
        for match in matches:
            context = match["context"]
            
            # Extract numerical rates
            rate_pattern = r'(\d+\.?\d*)\s*%'
            rates = re.findall(rate_pattern, context)
            
            # Extract amount ranges
            amount_pattern = r'(\d+(?:,\d+)*)\s*(?:লক্ষ|লাখ|crore|কোটি)?'
            amounts = re.findall(amount_pattern, context)
            
            if rates and amounts:
                slab_data["individual_slabs"].append({
                    "amounts": amounts,
                    "rates": rates,
                    "context": context[:100]
                })
        
        # Extract from tables
        for table in tables:
            if table["content"] and table["content"].get("headers"):
                headers = table["content"]["headers"]
                rows = table["content"]["rows"]
                
                # Check if this looks like a tax rate table
                if any("হার" in str(h) or "rate" in str(h).lower() for h in headers):
                    slab_data["table_data"] = {
                        "headers": headers,
                        "rows": rows
                    }
        
        return slab_data
    
    def extract_company_rates(self, matches: List[Dict], tables: List[Dict]) -> Dict[str, Any]:
        """Extract company tax rate data"""
        company_data = {
            "company_types": {},
            "special_rates": {}
        }
        
        company_keywords = {
            "public_limited": ["পাবলিক", "public"],
            "private_limited": ["প্রাইভেট", "private"],
            "bank": ["ব্যাংক", "bank"],
            "insurance": ["বীমা", "insurance"],
            "tobacco": ["তামাক", "tobacco", "cigarette"]
        }
        
        for match in matches:
            context = match["context"]
            rates = re.findall(r'(\d+\.?\d*)\s*%', context)
            
            for company_type, keywords in company_keywords.items():
                if any(keyword in context.lower() for keyword in keywords):
                    if rates:
                        company_data["company_types"][company_type] = {
                            "rate": rates[0] + "%",
                            "context": context[:150]
                        }
        
        return company_data
    
    def extract_penalty_rates(self, matches: List[Dict], tables: List[Dict]) -> Dict[str, Any]:
        """Extract penalty rate data"""
        penalty_data = {
            "penalty_types": {},
            "interest_rates": {}
        }
        
        for match in matches:
            context = match["context"]
            
            # Extract penalty percentages
            penalty_rates = re.findall(r'(\d+\.?\d*)\s*%', context)
            
            if "জরিমানা" in context or "penalty" in context.lower():
                if penalty_rates:
                    penalty_data["penalty_types"]["general"] = {
                        "rate": penalty_rates[0] + "%",
                        "context": context[:150]
                    }
            
            if "সুদ" in context or "interest" in context.lower():
                if penalty_rates:
                    penalty_data["interest_rates"]["general"] = {
                        "rate": penalty_rates[0] + "%",
                        "context": context[:150]
                    }
        
        return penalty_data
    
    def extract_investment_rebates(self, matches: List[Dict], tables: List[Dict]) -> Dict[str, Any]:
        """Extract investment rebate data"""
        rebate_data = {
            "rebate_categories": {},
            "maximum_limits": {}
        }
        
        for match in matches:
            context = match["context"]
            
            if "ছাড়" in context or "rebate" in context.lower():
                rates = re.findall(r'(\d+\.?\d*)\s*%', context)
                amounts = re.findall(r'(\d+(?:,\d+)*)', context)
                
                rebate_data["rebate_categories"]["investment"] = {
                    "rates": rates,
                    "amounts": amounts,
                    "context": context[:150]
                }
        
        return rebate_data
    
    def extract_withholding_rates(self, matches: List[Dict], tables: List[Dict]) -> Dict[str, Any]:
        """Extract withholding tax rate data"""
        withholding_data = {
            "payment_types": {},
            "deduction_rates": {}
        }
        
        for match in matches:
            context = match["context"]
            
            if "উৎসে" in context or "withholding" in context.lower():
                rates = re.findall(r'(\d+\.?\d*)\s*%', context)
                
                if rates:
                    withholding_data["deduction_rates"]["general"] = {
                        "rate": rates[0] + "%",
                        "context": context[:150]
                    }
        
        return withholding_data
    
    def extract_generic_data(self, matches: List[Dict], tables: List[Dict]) -> Dict[str, Any]:
        """Generic data extraction for other file types"""
        generic_data = {
            "key_findings": [],
            "numerical_data": [],
            "regulatory_references": []
        }
        
        for match in matches:
            context = match["context"]
            
            # Extract numerical values
            numbers = re.findall(r'\d+(?:\.\d+)?', context)
            if numbers:
                generic_data["numerical_data"].extend(numbers)
            
            # Extract section references
            sections = re.findall(r'(?:ধারা|section)\s*(\d+)', context, re.IGNORECASE)
            if sections:
                generic_data["regulatory_references"].extend(sections)
            
            generic_data["key_findings"].append({
                "pattern": match["pattern"],
                "context": context[:200],
                "confidence": match["confidence"]
            })
        
        return generic_data
    
    def run_comprehensive_extraction(self) -> Dict[str, Any]:
        """Run extraction for all 29 target files across all source files"""
        
        logger.info("Starting comprehensive tax data extraction...")
        
        # Load all source files
        source_data = {}
        for source_name, file_path in self.source_files.items():
            data = self.load_source_file(file_path)
            if data:
                source_data[source_name] = data
        
        if not source_data:
            logger.error("No source files loaded successfully")
            return {}
        
        # Process each target file
        extraction_results = {}
        total_files = len(self.extraction_patterns)
        
        for i, (target_file, patterns) in enumerate(self.extraction_patterns.items(), 1):
            logger.info(f"Processing {i}/{total_files}: {target_file}")
            
            file_results = {}
            
            # Extract from each source file
            for source_name, source_content in source_data.items():
                logger.info(f"  Extracting from {source_name}")
                
                extraction = self.extract_from_source(source_content, target_file, patterns)
                file_results[source_name] = extraction
            
            # Combine results from all sources
            combined_result = self.combine_source_results(target_file, file_results)
            extraction_results[target_file] = combined_result
            
            # Save individual file
            self.save_extraction_result(target_file, combined_result)
        
        # Save master summary
        summary = self.generate_extraction_summary(extraction_results)
        self.save_extraction_result("extraction_summary.json", summary)
        
        logger.info("Comprehensive extraction completed!")
        return extraction_results
    
    def combine_source_results(self, target_file: str, file_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine extraction results from multiple source files"""
        
        combined = {
            "target_file": target_file,
            "extraction_timestamp": datetime.now().isoformat(),
            "source_files_processed": list(file_results.keys()),
            "total_matches": 0,
            "total_tables": 0,
            "combined_confidence": 0.0,
            "source_results": file_results,
            "consolidated_data": {}
        }
        
        # Aggregate statistics
        confidences = []
        all_matches = []
        all_tables = []
        
        for source_name, result in file_results.items():
            combined["total_matches"] += len(result.get("matches", []))
            combined["total_tables"] += len(result.get("tables", []))
            
            if result.get("confidence_score", 0) > 0:
                confidences.append(result["confidence_score"])
            
            all_matches.extend(result.get("matches", []))
            all_tables.extend(result.get("tables", []))
        
        # Calculate combined confidence
        if confidences:
            combined["combined_confidence"] = sum(confidences) / len(confidences)
        
        # Determine data quality
        if combined["combined_confidence"] > 0.8:
            combined["data_quality"] = "high"
        elif combined["combined_confidence"] > 0.6:
            combined["data_quality"] = "medium"
        else:
            combined["data_quality"] = "low"
        
        # Create consolidated structured data
        combined["consolidated_data"] = self.consolidate_structured_data(
            target_file, file_results
        )
        
        return combined
    
    def consolidate_structured_data(self, target_file: str, 
                                  file_results: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate structured data from multiple sources"""
        
        consolidated = {
            "metadata": {
                "target_file": target_file,
                "consolidation_method": "priority_based_merge",
                "source_priority": ["circular", "finance_ordinance", "finance_act", "income_tax_act"]
            }
        }
        
        # Priority-based consolidation
        source_priority = consolidated["metadata"]["source_priority"]
        
        for source in source_priority:
            if source in file_results:
                source_structured = file_results[source].get("structured_data", {})
                
                # Merge with priority to higher-ranking sources
                for key, value in source_structured.items():
                    if key not in consolidated or key == "metadata":
                        consolidated[key] = value
                    else:
                        # Merge nested dictionaries
                        if isinstance(consolidated[key], dict) and isinstance(value, dict):
                            consolidated[key].update(value)
        
        return consolidated
    
    def generate_extraction_summary(self, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive extraction summary"""
        
        summary = {
            "extraction_metadata": {
                "extraction_date": datetime.now().isoformat(),
                "total_target_files": len(extraction_results),
                "source_files": list(self.source_files.keys()),
                "extraction_version": "1.0"
            },
            "extraction_statistics": {
                "files_processed": len(extraction_results),
                "high_quality_extractions": 0,
                "medium_quality_extractions": 0,
                "low_quality_extractions": 0,
                "total_matches_found": 0,
                "total_tables_extracted": 0
            },
            "file_status": {},
            "recommendations": []
        }
        
        # Calculate statistics
        for file_name, result in extraction_results.items():
            quality = result.get("data_quality", "low")
            
            if quality == "high":
                summary["extraction_statistics"]["high_quality_extractions"] += 1
            elif quality == "medium":
                summary["extraction_statistics"]["medium_quality_extractions"] += 1
            else:
                summary["extraction_statistics"]["low_quality_extractions"] += 1
            
            summary["extraction_statistics"]["total_matches_found"] += result.get("total_matches", 0)
            summary["extraction_statistics"]["total_tables_extracted"] += result.get("total_tables", 0)
            
            summary["file_status"][file_name] = {
                "status": "extracted" if result.get("total_matches", 0) > 0 else "no_data_found",
                "quality": quality,
                "confidence": result.get("combined_confidence", 0.0),
                "matches": result.get("total_matches", 0),
                "tables": result.get("total_tables", 0)
            }
        
        # Generate recommendations
        if summary["extraction_statistics"]["low_quality_extractions"] > 10:
            summary["recommendations"].append(
                "High number of low-quality extractions. Consider refining search patterns."
            )
        
        if summary["extraction_statistics"]["total_tables_extracted"] < 20:
            summary["recommendations"].append(
                "Low table extraction count. May need enhanced table detection algorithms."
            )
        
        # Calculate completion percentage
        high_medium = (summary["extraction_statistics"]["high_quality_extractions"] + 
                      summary["extraction_statistics"]["medium_quality_extractions"])
        completion_rate = (high_medium / len(extraction_results)) * 100
        
        summary["extraction_statistics"]["completion_rate"] = f"{completion_rate:.1f}%"
        
        return summary
    
    def save_extraction_result(self, filename: str, data: Dict[str, Any]):
        """Save extraction result to JSON file"""
        
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved extraction result: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving {output_path}: {str(e)}")

def main():
    """Main execution function"""
    extractor = ComprehensiveTaxExtractor()
    
    logger.info("=" * 60)
    logger.info("COMPREHENSIVE TAX DATA EXTRACTOR")
    logger.info("=" * 60)
    logger.info(f"Target files to extract: {len(extractor.extraction_patterns)}")
    logger.info(f"Source files to process: {len(extractor.source_files)}")
    logger.info("=" * 60)
    
    # Run comprehensive extraction
    results = extractor.run_comprehensive_extraction()
    
    if results:
        logger.info("=" * 60)
        logger.info("EXTRACTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Results saved in: {extractor.output_dir}/")
        logger.info("Check 'extraction_summary.json' for detailed results")
    else:
        logger.error("Extraction failed. Check logs for details.")

if __name__ == "__main__":
    main()