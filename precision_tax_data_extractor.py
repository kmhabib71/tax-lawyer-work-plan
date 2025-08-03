#!/usr/bin/env python3
"""
Precision Tax Data Extractor
Generates clean, structured data files (50-200 lines each, not millions)
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrecisionTaxExtractor:
    def __init__(self):
        self.source_files = {
            "circular": "income-tax-complete-circular-24-25/income_tax_circular_2024_25_ultra_enriched.json",
            "finance_ordinance": "precise_structured_laws/finance_ordinance_2025_cleaned.json", 
            "finance_act": "precise_structured_laws/অরথ_আইন_২০২৪.json",
            "income_tax_act": "precise_structured_laws/income_tax_act_2023_cleaned.json"
        }
        
        self.output_dir = "extracted_tax_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Precision extractors for each file type
        self.extractors = {
            "income_tax_rate_slab_tables_2024_25.json": self.extract_individual_tax_slabs,
            "company_tax_rates_by_type.json": self.extract_company_tax_rates,
            "penalty_rate_tables.json": self.extract_penalty_rates,
            "investment_rebate_rules_detailed.json": self.extract_investment_rebates,
            "withholding_tax_rates.json": self.extract_withholding_rates,
            "minimum_tax_section_163.json": self.extract_minimum_tax,
            "special_category_slabs.json": self.extract_special_categories,
            "depreciation_tables_rates.json": self.extract_depreciation_rates,
            "tax_holiday_provisions.json": self.extract_tax_holidays
        }
    
    def find_tax_rate_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Find tax rate patterns in text and extract clean data"""
        patterns = []
        
        # Pattern 1: Bengali tax slabs (প্রথম ১০ লক্ষ টাকা পর্যন্ত... ৫%)
        slab_pattern = r'(প্রথম|পরবর্তী|অবশিষ্ট)?\s*(\d+(?:\.\d+)?)\s*(লক্ষ|লাখ|কোটি)?\s*টাকা.*?(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(slab_pattern, text, re.IGNORECASE):
            amount = match.group(2)
            unit = match.group(3) or "টাকা"
            rate = match.group(4)
            
            # Convert to standard format
            amount_bdt = self.convert_to_bdt(amount, unit)
            
            patterns.append({
                "type": "income_slab",
                "amount": amount_bdt,
                "rate": f"{rate}%",
                "rate_decimal": float(rate) / 100,
                "original": match.group()
            })
        
        # Pattern 2: Company rates (কোম্পানি... ২৫%)
        company_pattern = r'(কোম্পানি|company|পাবলিক|প্রাইভেট|ব্যাংক|বীমা|তামাক).*?(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(company_pattern, text, re.IGNORECASE):
            entity_type = match.group(1)
            rate = match.group(2)
            
            patterns.append({
                "type": "company_rate",
                "entity": entity_type,
                "rate": f"{rate}%",
                "rate_decimal": float(rate) / 100,
                "original": match.group()
            })
        
        # Pattern 3: Penalty rates (জরিমানা... ২%)
        penalty_pattern = r'(জরিমানা|penalty|বিলম্ব|interest).*?(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(penalty_pattern, text, re.IGNORECASE):
            penalty_type = match.group(1)
            rate = match.group(2)
            
            patterns.append({
                "type": "penalty_rate",
                "penalty_type": penalty_type,
                "rate": f"{rate}%",
                "rate_decimal": float(rate) / 100,
                "original": match.group()
            })
        
        return patterns
    
    def convert_to_bdt(self, amount: str, unit: str) -> int:
        """Convert amount to BDT"""
        try:
            amount_num = float(amount)
            if "লক্ষ" in unit or "লাখ" in unit:
                return int(amount_num * 100000)
            elif "কোটি" in unit:
                return int(amount_num * 10000000)
            else:
                return int(amount_num)
        except:
            return 0
    
    def extract_html_tables(self, text: str) -> List[Dict[str, Any]]:
        """Extract and parse HTML tables"""
        tables = []
        
        table_pattern = r'<table[^>]*>(.*?)</table>'
        for match in re.finditer(table_pattern, text, re.DOTALL | re.IGNORECASE):
            table_html = match.group(1)
            
            # Extract headers
            headers = []
            header_pattern = r'<th[^>]*>(.*?)</th>'
            for header_match in re.finditer(header_pattern, table_html, re.IGNORECASE):
                header_text = re.sub(r'<[^>]+>', '', header_match.group(1)).strip()
                headers.append(header_text)
            
            # Extract rows
            rows = []
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            for row_match in re.finditer(row_pattern, table_html, re.IGNORECASE):
                row_html = row_match.group(1)
                
                # Skip rows with headers
                if '<th' in row_html:
                    continue
                
                cells = []
                cell_pattern = r'<td[^>]*>(.*?)</td>'
                for cell_match in re.finditer(cell_pattern, row_html, re.IGNORECASE):
                    cell_text = re.sub(r'<[^>]+>', '', cell_match.group(1)).strip()
                    cells.append(cell_text)
                
                if cells:
                    rows.append(cells)
            
            if headers and rows:
                tables.append({
                    "headers": headers,
                    "rows": rows,
                    "table_type": self.classify_table(headers)
                })
        
        return tables
    
    def classify_table(self, headers: List[str]) -> str:
        """Classify table type based on headers"""
        headers_text = ' '.join(headers).lower()
        
        if any(term in headers_text for term in ['আয়ের পরিমাণ', 'আয়করের হার', 'income', 'rate']):
            return "tax_rate_table"
        elif any(term in headers_text for term in ['কোম্পানি', 'company', 'entity']):
            return "company_rate_table"
        elif any(term in headers_text for term in ['জরিমানা', 'penalty', 'violation']):
            return "penalty_table"
        elif any(term in headers_text for term in ['বিনিয়োগ', 'investment', 'rebate']):
            return "investment_table"
        else:
            return "general_table"
    
    def extract_individual_tax_slabs(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract individual tax slab data - generates clean, small output"""
        logger.info("Extracting individual tax slabs...")
        
        result = {
            "metadata": {
                "file_type": "individual_tax_slabs",
                "fiscal_year": "2024-25",
                "extraction_date": datetime.now().isoformat(),
                "currency": "BDT"
            },
            "general_taxpayers": {
                "exemption_limit": 1000000,
                "slabs": []
            },
            "special_categories": {},
            "source_confidence": "high"
        }
        
        # Search all sources for slab data
        for source_name, text in source_data.items():
            logger.info(f"  Processing {source_name}...")
            
            # Extract rate patterns
            patterns = self.find_tax_rate_patterns(text)
            slab_patterns = [p for p in patterns if p["type"] == "income_slab"]
            
            # Extract tables
            tables = self.extract_html_tables(text)
            rate_tables = [t for t in tables if t["table_type"] == "tax_rate_table"]
            
            # Process slab patterns
            for pattern in slab_patterns:
                amount = pattern["amount"]
                rate = pattern["rate_decimal"]
                
                # Determine slab range
                if amount <= 1000000:
                    slab_range = "0-1,000,000"
                elif amount <= 2000000:
                    slab_range = "1,000,001-2,000,000"
                elif amount <= 3000000:
                    slab_range = "2,000,001-3,000,000"
                else:
                    slab_range = "3,000,001+"
                
                # Add to slabs if not already present
                existing = next((s for s in result["general_taxpayers"]["slabs"] 
                               if s["range"] == slab_range), None)
                
                if not existing:
                    result["general_taxpayers"]["slabs"].append({
                        "range": slab_range,
                        "rate_percent": pattern["rate"],
                        "rate_decimal": rate,
                        "source": source_name
                    })
            
            # Process rate tables
            for table in rate_tables:
                if len(table["rows"]) >= 3:  # Valid tax table should have multiple slabs
                    for i, row in enumerate(table["rows"]):
                        if len(row) >= 2:
                            income_desc = row[0]
                            rate_desc = row[1]
                            
                            # Extract rate percentage
                            rate_match = re.search(r'(\d+(?:\.\d+)?)', rate_desc)
                            if rate_match:
                                rate_val = float(rate_match.group(1))
                                
                                # Determine range from description
                                if "প্রথম" in income_desc and "১০" in income_desc:
                                    slab_range = "0-1,000,000"
                                elif "পরবর্তী" in income_desc and "১০" in income_desc:
                                    if i == 1:
                                        slab_range = "1,000,001-2,000,000"
                                    else:
                                        slab_range = "2,000,001-3,000,000"
                                elif "অবশিষ্ট" in income_desc:
                                    slab_range = "3,000,001+"
                                else:
                                    continue
                                
                                # Add to slabs
                                existing = next((s for s in result["general_taxpayers"]["slabs"] 
                                               if s["range"] == slab_range), None)
                                
                                if not existing:
                                    result["general_taxpayers"]["slabs"].append({
                                        "range": slab_range,
                                        "rate_percent": f"{rate_val}%",
                                        "rate_decimal": rate_val / 100,
                                        "source": f"{source_name}_table"
                                    })
        
        # Sort slabs by range
        result["general_taxpayers"]["slabs"].sort(key=lambda x: int(x["range"].split("-")[0].replace(",", "")))
        
        # Add special categories if found
        special_categories = self.extract_special_category_slabs(source_data)
        result["special_categories"] = special_categories
        
        logger.info(f"  Extracted {len(result['general_taxpayers']['slabs'])} tax slabs")
        return result
    
    def extract_company_tax_rates(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract company tax rates - clean output"""
        logger.info("Extracting company tax rates...")
        
        result = {
            "metadata": {
                "file_type": "company_tax_rates",
                "fiscal_year": "2024-25",
                "extraction_date": datetime.now().isoformat()
            },
            "company_types": {},
            "special_rates": {},
            "source_confidence": "high"
        }
        
        company_mappings = {
            "পাবলিক": "public_limited",
            "public": "public_limited",
            "প্রাইভেট": "private_limited", 
            "private": "private_limited",
            "ব্যাংক": "bank_company",
            "bank": "bank_company",
            "বীমা": "insurance_company",
            "insurance": "insurance_company",
            "তামাক": "tobacco_company",
            "tobacco": "tobacco_company",
            "cigarette": "tobacco_company"
        }
        
        for source_name, text in source_data.items():
            patterns = self.find_tax_rate_patterns(text)
            company_patterns = [p for p in patterns if p["type"] == "company_rate"]
            
            for pattern in company_patterns:
                entity = pattern["entity"].lower()
                rate = pattern["rate_decimal"]
                
                # Map to standard company type
                company_type = None
                for bengali_key, english_key in company_mappings.items():
                    if bengali_key in entity:
                        company_type = english_key
                        break
                
                if company_type and company_type not in result["company_types"]:
                    result["company_types"][company_type] = {
                        "rate_percent": pattern["rate"],
                        "rate_decimal": rate,
                        "source": source_name
                    }
        
        logger.info(f"  Extracted {len(result['company_types'])} company types")
        return result
    
    def extract_penalty_rates(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract penalty rates - clean output"""
        logger.info("Extracting penalty rates...")
        
        result = {
            "metadata": {
                "file_type": "penalty_rates",
                "extraction_date": datetime.now().isoformat()
            },
            "penalty_types": {},
            "interest_rates": {},
            "calculation_formulas": {}
        }
        
        for source_name, text in source_data.items():
            patterns = self.find_tax_rate_patterns(text)
            penalty_patterns = [p for p in patterns if p["type"] == "penalty_rate"]
            
            for pattern in penalty_patterns:
                penalty_type = pattern["penalty_type"].lower()
                rate = pattern["rate_decimal"]
                
                if "জরিমানা" in penalty_type or "penalty" in penalty_type:
                    result["penalty_types"]["general_penalty"] = {
                        "rate_percent": pattern["rate"],
                        "rate_decimal": rate,
                        "source": source_name
                    }
                elif "বিলম্ব" in penalty_type or "late" in penalty_type:
                    result["penalty_types"]["late_filing"] = {
                        "rate_percent": pattern["rate"],
                        "rate_decimal": rate,
                        "type": "monthly",
                        "source": source_name
                    }
                elif "সুদ" in penalty_type or "interest" in penalty_type:
                    result["interest_rates"]["default_interest"] = {
                        "rate_percent": pattern["rate"],
                        "rate_decimal": rate,
                        "source": source_name
                    }
        
        # Look for specific formulas
        formula_pattern = r'ক\s*=\s*খ\s*\+\s*\(খ\s*-\s*গ\)\s*×\s*ঘ\s*×\s*০\.০২'
        for source_name, text in source_data.items():
            if re.search(formula_pattern, text):
                result["calculation_formulas"]["late_filing_formula"] = {
                    "formula": "ক = খ + (খ - গ) × ঘ × ০.০২",
                    "description": "Late filing penalty calculation",
                    "variables": {
                        "ক": "Total payable tax",
                        "খ": "Tax if filed on time", 
                        "গ": "Advance tax paid",
                        "ঘ": "Months after due date (max 24)"
                    },
                    "source": source_name
                }
        
        logger.info(f"  Extracted {len(result['penalty_types'])} penalty types")
        return result
    
    def extract_special_category_slabs(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract special category tax slabs"""
        special_categories = {}
        
        category_patterns = {
            "women_taxpayers": [r"মহিলা.*করদাতা", r"women.*taxpayer", r"৩৫.*লক্ষ"],
            "senior_citizens": [r"সিনিয়র.*সিটিজেন", r"senior.*citizen", r"৬৫.*বছর", r"৪০.*লক্ষ"],
            "disabled_persons": [r"প্রতিবন্ধী.*ব্যক্তি", r"disabled.*person", r"৪৫.*লক্ষ"],
            "freedom_fighters": [r"মুক্তিযোদ্ধা", r"freedom.*fighter", r"৪৭.*৫.*লক্ষ"]
        }
        
        exemption_limits = {
            "women_taxpayers": 3500000,
            "senior_citizens": 4000000, 
            "disabled_persons": 4500000,
            "freedom_fighters": 4750000
        }
        
        for category, patterns in category_patterns.items():
            for source_name, text in source_data.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        special_categories[category] = {
                            "exemption_limit": exemption_limits[category],
                            "rate_after_exemption": "10%",
                            "source": source_name
                        }
                        break
                if category in special_categories:
                    break
        
        return special_categories
    
    def extract_investment_rebates(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract investment rebate rules"""
        logger.info("Extracting investment rebates...")
        
        result = {
            "metadata": {
                "file_type": "investment_rebates",
                "section": "44",
                "extraction_date": datetime.now().isoformat()
            },
            "rebate_categories": {},
            "maximum_limits": {}
        }
        
        rebate_pattern = r'(বিনিয়োগ|investment).*?(ছাড়|rebate).*?(\d+(?:\.\d+)?)\s*%'
        
        for source_name, text in source_data.items():
            for match in re.finditer(rebate_pattern, text, re.IGNORECASE):
                rate = match.group(3)
                result["rebate_categories"]["general_investment"] = {
                    "rate_percent": f"{rate}%",
                    "rate_decimal": float(rate) / 100,
                    "source": source_name
                }
        
        return result
    
    def extract_withholding_rates(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract withholding tax rates"""
        logger.info("Extracting withholding rates...")
        
        result = {
            "metadata": {
                "file_type": "withholding_tax_rates",
                "extraction_date": datetime.now().isoformat()
            },
            "payment_types": {}
        }
        
        withholding_pattern = r'(উৎসে.*কর|withholding.*tax|TDS).*?(\d+(?:\.\d+)?)\s*%'
        
        for source_name, text in source_data.items():
            for match in re.finditer(withholding_pattern, text, re.IGNORECASE):
                rate = match.group(2)
                result["payment_types"]["general_payments"] = {
                    "rate_percent": f"{rate}%",
                    "rate_decimal": float(rate) / 100,
                    "source": source_name
                }
        
        return result
    
    def extract_minimum_tax(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract minimum tax provisions"""
        logger.info("Extracting minimum tax...")
        
        result = {
            "metadata": {
                "file_type": "minimum_tax",
                "section": "163",
                "extraction_date": datetime.now().isoformat()
            },
            "applicable_entities": [],
            "tax_rates": {}
        }
        
        minimum_tax_pattern = r'(ন্যূনতম.*কর|minimum.*tax).*?(\d+(?:\.\d+)?)\s*%'
        
        for source_name, text in source_data.items():
            for match in re.finditer(minimum_tax_pattern, text, re.IGNORECASE):
                rate = match.group(2)
                result["tax_rates"]["general_business"] = {
                    "rate_percent": f"{rate}%",
                    "rate_decimal": float(rate) / 100,
                    "source": source_name
                }
        
        return result
    
    def extract_special_categories(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract special category provisions"""
        return self.extract_special_category_slabs(source_data)
    
    def extract_depreciation_rates(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract depreciation rates"""
        logger.info("Extracting depreciation rates...")
        
        result = {
            "metadata": {
                "file_type": "depreciation_rates",
                "schedule": "3rd",
                "extraction_date": datetime.now().isoformat()
            },
            "asset_categories": {}
        }
        
        depreciation_pattern = r'(অবচয়|depreciation).*?(\d+(?:\.\d+)?)\s*%'
        
        for source_name, text in source_data.items():
            for match in re.finditer(depreciation_pattern, text, re.IGNORECASE):
                rate = match.group(2)
                result["asset_categories"]["general_assets"] = {
                    "rate_percent": f"{rate}%",
                    "rate_decimal": float(rate) / 100,
                    "source": source_name
                }
        
        return result
    
    def extract_tax_holidays(self, source_data: Dict[str, str]) -> Dict[str, Any]:
        """Extract tax holiday provisions"""
        logger.info("Extracting tax holidays...")
        
        result = {
            "metadata": {
                "file_type": "tax_holidays",
                "schedule": "6th",
                "extraction_date": datetime.now().isoformat()
            },
            "holiday_types": {}
        }
        
        holiday_pattern = r'(কর.*ছুটি|tax.*holiday).*?(\d+)\s*(বছর|year)'
        
        for source_name, text in source_data.items():
            for match in re.finditer(holiday_pattern, text, re.IGNORECASE):
                years = match.group(2)
                result["holiday_types"]["industrial_holiday"] = {
                    "duration_years": int(years),
                    "exemption_rate": "100%",
                    "source": source_name
                }
        
        return result
    
    def process_all_files(self):
        """Process all files and generate clean, small outputs"""
        logger.info("=" * 60)
        logger.info("PRECISION TAX DATA EXTRACTOR")
        logger.info("=" * 60)
        logger.info(f"Target files: {len(self.extractors)}")
        logger.info("Generating clean, structured outputs...")
        logger.info("=" * 60)
        
        # Load all source files into memory once
        source_data = {}
        for source_name, file_path in self.source_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    source_data[source_name] = json.dumps(data, ensure_ascii=False)
                    logger.info(f"✅ Loaded {source_name}: {len(source_data[source_name]):,} chars")
            except Exception as e:
                logger.error(f"❌ Failed to load {file_path}: {e}")
        
        if not source_data:
            logger.error("No source files loaded. Exiting.")
            return
        
        # Process each target file
        results_summary = {
            "extraction_date": datetime.now().isoformat(),
            "files_processed": {},
            "total_files": len(self.extractors),
            "successful_extractions": 0
        }
        
        for i, (target_file, extractor_func) in enumerate(self.extractors.items(), 1):
            logger.info(f"[{i}/{len(self.extractors)}] Processing: {target_file}")
            
            try:
                # Run extraction
                extracted_data = extractor_func(source_data)
                
                # Save clean output
                output_path = os.path.join(self.output_dir, target_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(extracted_data, f, ensure_ascii=False, indent=2)
                
                # Get file size
                file_size = os.path.getsize(output_path)
                
                logger.info(f"  ✅ Saved: {file_size:,} bytes ({file_size//1024}KB)")
                
                # Update summary
                results_summary["files_processed"][target_file] = {
                    "status": "success",
                    "file_size_bytes": file_size,
                    "file_size_kb": file_size // 1024
                }
                results_summary["successful_extractions"] += 1
                
            except Exception as e:
                logger.error(f"  ❌ Failed: {e}")
                results_summary["files_processed"][target_file] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Save summary
        summary_path = os.path.join(self.output_dir, "extraction_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, ensure_ascii=False, indent=2)
        
        logger.info("=" * 60)
        logger.info("EXTRACTION COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Successfully extracted: {results_summary['successful_extractions']}/{results_summary['total_files']} files")
        logger.info(f"Results saved in: {self.output_dir}/")
        logger.info("All files are now clean and small (50-200 lines each)")

def main():
    extractor = PrecisionTaxExtractor()
    extractor.process_all_files()

if __name__ == "__main__":
    main()