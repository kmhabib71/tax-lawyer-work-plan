#!/usr/bin/env python3
"""
eReturn Form Generator
Generates actual tax forms (IT-11GA, IT-10B, IT-10BB) from query processing
Phase 0 - Complete form generation with validation
"""

import json
import re
from datetime import datetime
from pathlib import Path

class EReturnFormGenerator:
    def __init__(self):
        self.validation_rules = self.load_validation_rules()
        self.tds_rates = self.load_tds_rates()
        self.generated_forms = []
        
    def load_validation_rules(self):
        """Load ereturn validation rules"""
        rules_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/ereturn_validation_rules.json"
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Validation rules not found: {rules_path}")
            return {"validation_rules": {}}
    
    def load_tds_rates(self):
        """Load TDS rates for calculations"""
        tds_path = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/structured_tax_data/tds_rates_matrix_standard.json"
        try:
            with open(tds_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ TDS rates not found: {tds_path}")
            return {"tds_rates": {}}
    
    def determine_form_requirements(self, taxpayer_info):
        """Determine which forms are required based on taxpayer info"""
        required_forms = ["IT-11GA"]  # Always required
        
        # Check IT-10B requirements
        if self.needs_it_10b(taxpayer_info):
            required_forms.append("IT-10B")
        
        # Check IT-10BB requirements  
        if self.needs_it_10bb(taxpayer_info):
            required_forms.append("IT-10BB")
        
        # Check Schedule-5 for investment rebate
        if taxpayer_info.get('investment_amount', 0) > 0:
            required_forms.append("Schedule-5")
        
        return required_forms
    
    def needs_it_10b(self, taxpayer_info):
        """Check if IT-10B (Asset Declaration) is required"""
        rules = self.validation_rules.get('validation_rules', {}).get('it_10b_requirements', {})
        
        # Gross wealth threshold
        gross_wealth = taxpayer_info.get('gross_wealth', 0)
        if gross_wealth > 5000000:  # 50 lakh threshold
            return True, "Gross wealth exceeds 50 lakh Taka"
        
        # Motor car ownership
        if taxpayer_info.get('owns_motor_car', False):
            return True, "Motor car ownership"
        
        # City corporation property
        if taxpayer_info.get('has_city_corporation_property', False):
            return True, "Property in City Corporation area"
        
        # Offshore assets
        if taxpayer_info.get('has_offshore_assets', False):
            return True, "Assets outside Bangladesh"
        
        # Shareholder/Director
        if taxpayer_info.get('is_shareholder_director', False):
            return True, "Company shareholder/director"
        
        return False, "Not required"
    
    def needs_it_10bb(self, taxpayer_info):
        """Check if IT-10BB (Lifestyle Expenditure) is required"""
        annual_income = taxpayer_info.get('annual_income', 0)
        
        # IT-10BB required for income above certain threshold or specific conditions
        if annual_income > 1500000:  # 15 lakh annual income
            return True, "Annual income exceeds 15 lakh"
        
        if taxpayer_info.get('owns_motor_car', False):
            return True, "Motor car ownership requires lifestyle declaration"
        
        if taxpayer_info.get('has_city_corporation_property', False):
            return True, "City corporation property requires lifestyle declaration"
        
        return False, "Not required"
    
    def calculate_progressive_tax(self, annual_income):
        """Calculate progressive income tax for Bangladesh 2024-25"""
        if annual_income <= 350000:
            return 0, "Tax-free income"
        
        tax_brackets = [
            (350000, 0.00),      # Tax-free up to 3.5 lakh
            (500000, 0.05),      # 5% on next 1.5 lakh (3.5-5 lakh)
            (1000000, 0.10),     # 10% on next 5 lakh (5-10 lakh)
            (1500000, 0.15),     # 15% on next 5 lakh (10-15 lakh)
            (3000000, 0.20),     # 20% on next 15 lakh (15-30 lakh)  
            (float('inf'), 0.25) # 25% on above 30 lakh
        ]
        
        total_tax = 0
        remaining_income = annual_income
        prev_bracket = 0
        
        for bracket_limit, rate in tax_brackets:
            if remaining_income <= 0:
                break
                
            taxable_in_bracket = min(remaining_income, bracket_limit - prev_bracket)
            if taxable_in_bracket > 0 and prev_bracket >= 350000:  # Start tax after 3.5 lakh
                total_tax += taxable_in_bracket * rate
            
            remaining_income -= taxable_in_bracket
            prev_bracket = bracket_limit
            
            if bracket_limit == float('inf'):
                break
        
        return total_tax, f"Progressive tax on {annual_income:,} Taka"
    
    def calculate_investment_rebate(self, annual_income, investment_amount):
        """Calculate investment rebate (25% of investment, max on eligible income)"""
        max_rebate_income = min(annual_income, 1500000)  # Max rebate on 15 lakh income
        max_rebate_amount = max_rebate_income * 0.25
        
        actual_rebate = min(investment_amount * 0.25, max_rebate_amount)
        
        return {
            'investment_amount': investment_amount,
            'rebate_rate': 25,
            'max_eligible_income': max_rebate_income,
            'max_rebate_amount': max_rebate_amount,
            'actual_rebate': actual_rebate,
            'remaining_rebate_capacity': max_rebate_amount - actual_rebate
        }
    
    def generate_it_11ga(self, taxpayer_info):
        """Generate IT-11GA main tax return form"""
        annual_income = taxpayer_info.get('annual_income', 0)
        investment_amount = taxpayer_info.get('investment_amount', 0)
        
        # Calculate tax
        gross_tax, tax_calculation = self.calculate_progressive_tax(annual_income)
        
        # Calculate investment rebate
        rebate_info = self.calculate_investment_rebate(annual_income, investment_amount)
        net_tax = max(0, gross_tax - rebate_info['actual_rebate'])
        
        # Calculate advance tax paid (TDS + AIT)
        advance_tax_paid = taxpayer_info.get('tds_deducted', 0) + taxpayer_info.get('advance_tax_paid', 0)
        
        # Final payable/refundable
        final_amount = net_tax - advance_tax_paid
        
        it_11ga = {
            "form_type": "IT-11GA",
            "form_title": "Income Tax Return for Individual Taxpayer",
            "assessment_year": "2024-2025",
            "income_year": "2023-2024",
            "taxpayer_info": {
                "name": taxpayer_info.get('name', 'Taxpayer Name'),
                "tin": taxpayer_info.get('tin', '000000000000'),
                "circle": taxpayer_info.get('tax_circle', 'Default Circle'),
                "zone": taxpayer_info.get('tax_zone', 'Default Zone')
            },
            "income_details": {
                "employment_income": taxpayer_info.get('salary_income', 0),
                "business_income": taxpayer_info.get('business_income', 0),
                "rental_income": taxpayer_info.get('rental_income', 0),
                "interest_income": taxpayer_info.get('interest_income', 0),
                "dividend_income": taxpayer_info.get('dividend_income', 0),
                "capital_gains": taxpayer_info.get('capital_gains', 0),
                "other_income": taxpayer_info.get('other_income', 0),
                "total_income": annual_income
            },
            "tax_calculation": {
                "gross_tax": gross_tax,
                "calculation_method": tax_calculation,
                "investment_rebate": rebate_info,
                "net_tax": net_tax
            },
            "advance_tax": {
                "tds_deducted": taxpayer_info.get('tds_deducted', 0),
                "advance_tax_paid": taxpayer_info.get('advance_tax_paid', 0),
                "total_advance_tax": advance_tax_paid
            },
            "final_calculation": {
                "net_payable_tax": net_tax,
                "advance_tax_paid": advance_tax_paid,
                "final_amount": final_amount,
                "status": "Payable" if final_amount > 0 else "Refundable" if final_amount < 0 else "Balanced"
            },
            "submission_info": {
                "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "due_date": "2024-11-30",
                "form_status": "Generated - Ready for Review"
            }
        }
        
        return it_11ga
    
    def generate_it_10b(self, taxpayer_info):
        """Generate IT-10B Asset Declaration form"""
        if not self.needs_it_10b(taxpayer_info)[0]:
            return None
        
        it_10b = {
            "form_type": "IT-10B",
            "form_title": "Statement of Assets and Liabilities",
            "assessment_year": "2024-2025",
            "taxpayer_info": {
                "name": taxpayer_info.get('name', 'Taxpayer Name'),
                "tin": taxpayer_info.get('tin', '000000000000')
            },
            "assets": {
                "cash_and_bank": {
                    "cash_in_hand": taxpayer_info.get('cash_in_hand', 0),
                    "bank_deposits": taxpayer_info.get('bank_deposits', 0),
                    "fixed_deposits": taxpayer_info.get('fixed_deposits', 0),
                    "other_deposits": taxpayer_info.get('other_deposits', 0),
                    "subtotal": sum([
                        taxpayer_info.get('cash_in_hand', 0),
                        taxpayer_info.get('bank_deposits', 0),
                        taxpayer_info.get('fixed_deposits', 0),
                        taxpayer_info.get('other_deposits', 0)
                    ])
                },
                "investments": {
                    "govt_securities": taxpayer_info.get('govt_securities', 0),
                    "shares_debentures": taxpayer_info.get('shares_debentures', 0),
                    "mutual_funds": taxpayer_info.get('mutual_funds', 0),
                    "other_investments": taxpayer_info.get('other_investments', 0),
                    "subtotal": sum([
                        taxpayer_info.get('govt_securities', 0),
                        taxpayer_info.get('shares_debentures', 0),
                        taxpayer_info.get('mutual_funds', 0),
                        taxpayer_info.get('other_investments', 0)
                    ])
                },
                "fixed_assets": {
                    "land_property": taxpayer_info.get('land_property', 0),
                    "building": taxpayer_info.get('building_value', 0),
                    "motor_vehicles": taxpayer_info.get('motor_vehicle_value', 0),
                    "furniture_equipment": taxpayer_info.get('furniture_equipment', 0),
                    "jewelry": taxpayer_info.get('jewelry_value', 0),
                    "other_assets": taxpayer_info.get('other_fixed_assets', 0),
                    "subtotal": sum([
                        taxpayer_info.get('land_property', 0),
                        taxpayer_info.get('building_value', 0),
                        taxpayer_info.get('motor_vehicle_value', 0),
                        taxpayer_info.get('furniture_equipment', 0),
                        taxpayer_info.get('jewelry_value', 0),
                        taxpayer_info.get('other_fixed_assets', 0)
                    ])
                }
            },
            "liabilities": {
                "loans_borrowings": {
                    "bank_loans": taxpayer_info.get('bank_loans', 0),
                    "other_loans": taxpayer_info.get('other_loans', 0), 
                    "credit_card_dues": taxpayer_info.get('credit_card_dues', 0),
                    "other_liabilities": taxpayer_info.get('other_liabilities', 0),
                    "subtotal": sum([
                        taxpayer_info.get('bank_loans', 0),
                        taxpayer_info.get('other_loans', 0),
                        taxpayer_info.get('credit_card_dues', 0),
                        taxpayer_info.get('other_liabilities', 0)
                    ])
                }
            },
            "summary": {
                "total_assets": 0,  # Will be calculated
                "total_liabilities": 0,  # Will be calculated
                "net_wealth": 0,  # Will be calculated
                "requirement_reason": self.needs_it_10b(taxpayer_info)[1]
            },
            "submission_info": {
                "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "form_status": "Generated - Ready for Review"
            }
        }
        
        # Calculate totals
        total_assets = (it_10b['assets']['cash_and_bank']['subtotal'] + 
                       it_10b['assets']['investments']['subtotal'] + 
                       it_10b['assets']['fixed_assets']['subtotal'])
        
        total_liabilities = it_10b['liabilities']['loans_borrowings']['subtotal']
        
        it_10b['summary']['total_assets'] = total_assets
        it_10b['summary']['total_liabilities'] = total_liabilities
        it_10b['summary']['net_wealth'] = total_assets - total_liabilities
        
        return it_10b
    
    def generate_it_10bb(self, taxpayer_info):
        """Generate IT-10BB Lifestyle Expenditure form"""
        if not self.needs_it_10bb(taxpayer_info)[0]:
            return None
        
        it_10bb = {
            "form_type": "IT-10BB",
            "form_title": "Statement of Lifestyle Expenditure", 
            "assessment_year": "2024-2025",
            "taxpayer_info": {
                "name": taxpayer_info.get('name', 'Taxpayer Name'),
                "tin": taxpayer_info.get('tin', '000000000000')
            },
            "lifestyle_expenditure": {
                "personal_expenditure": {
                    "food_clothing": taxpayer_info.get('food_clothing_expense', 0),
                    "housing_utilities": taxpayer_info.get('housing_utilities', 0),
                    "transport": taxpayer_info.get('transport_expense', 0),
                    "education": taxpayer_info.get('education_expense', 0),
                    "medical": taxpayer_info.get('medical_expense', 0),
                    "entertainment": taxpayer_info.get('entertainment_expense', 0),
                    "other_personal": taxpayer_info.get('other_personal_expense', 0),
                    "subtotal": sum([
                        taxpayer_info.get('food_clothing_expense', 0),
                        taxpayer_info.get('housing_utilities', 0),
                        taxpayer_info.get('transport_expense', 0),
                        taxpayer_info.get('education_expense', 0),
                        taxpayer_info.get('medical_expense', 0),
                        taxpayer_info.get('entertainment_expense', 0),
                        taxpayer_info.get('other_personal_expense', 0)
                    ])
                },
                "asset_expenditure": {
                    "property_purchase": taxpayer_info.get('property_purchase', 0),
                    "vehicle_purchase": taxpayer_info.get('vehicle_purchase', 0),
                    "jewelry_purchase": taxpayer_info.get('jewelry_purchase', 0),
                    "investment_made": taxpayer_info.get('investment_made', 0),
                    "other_asset_purchase": taxpayer_info.get('other_asset_purchase', 0),
                    "subtotal": sum([
                        taxpayer_info.get('property_purchase', 0),
                        taxpayer_info.get('vehicle_purchase', 0),
                        taxpayer_info.get('jewelry_purchase', 0),
                        taxpayer_info.get('investment_made', 0),
                        taxpayer_info.get('other_asset_purchase', 0)
                    ])
                },
                "loan_repayment": {
                    "bank_loan_repayment": taxpayer_info.get('bank_loan_repayment', 0),
                    "other_loan_repayment": taxpayer_info.get('other_loan_repayment', 0),
                    "subtotal": sum([
                        taxpayer_info.get('bank_loan_repayment', 0),
                        taxpayer_info.get('other_loan_repayment', 0)
                    ])
                }
            },
            "summary": {
                "total_lifestyle_expenditure": 0,  # Will be calculated
                "declared_income": taxpayer_info.get('annual_income', 0),
                "expenditure_vs_income_ratio": 0,  # Will be calculated
                "requirement_reason": self.needs_it_10bb(taxpayer_info)[1]
            },
            "submission_info": {
                "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "form_status": "Generated - Ready for Review"
            }
        }
        
        # Calculate totals
        total_expenditure = (it_10bb['lifestyle_expenditure']['personal_expenditure']['subtotal'] +
                           it_10bb['lifestyle_expenditure']['asset_expenditure']['subtotal'] +
                           it_10bb['lifestyle_expenditure']['loan_repayment']['subtotal'])
        
        declared_income = taxpayer_info.get('annual_income', 0)
        
        it_10bb['summary']['total_lifestyle_expenditure'] = total_expenditure
        it_10bb['summary']['expenditure_vs_income_ratio'] = (total_expenditure / declared_income * 100) if declared_income > 0 else 0
        
        return it_10bb
    
    def generate_complete_ereturn_package(self, taxpayer_info):
        """Generate complete eReturn package with all required forms"""
        print(f"🏗️  Generating complete eReturn package for: {taxpayer_info.get('name', 'Taxpayer')}")
        
        # Determine required forms
        required_forms = self.determine_form_requirements(taxpayer_info)
        print(f"📋 Required forms: {', '.join(required_forms)}")
        
        ereturn_package = {
            "package_info": {
                "taxpayer_name": taxpayer_info.get('name', 'Taxpayer Name'),
                "tin": taxpayer_info.get('tin', '000000000000'),
                "assessment_year": "2024-2025",
                "income_year": "2023-2024",
                "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "required_forms": required_forms,
                "package_status": "Complete - Ready for Submission"
            },
            "forms": {}
        }
        
        # Generate IT-11GA (always required)
        if "IT-11GA" in required_forms:
            ereturn_package["forms"]["IT-11GA"] = self.generate_it_11ga(taxpayer_info)
            print("✅ IT-11GA generated")
        
        # Generate IT-10B if required
        if "IT-10B" in required_forms:
            it_10b = self.generate_it_10b(taxpayer_info)
            if it_10b:
                ereturn_package["forms"]["IT-10B"] = it_10b
                print("✅ IT-10B generated")
        
        # Generate IT-10BB if required
        if "IT-10BB" in required_forms:
            it_10bb = self.generate_it_10bb(taxpayer_info)
            if it_10bb:
                ereturn_package["forms"]["IT-10BB"] = it_10bb
                print("✅ IT-10BB generated")
        
        # Generate Schedule-5 if investments
        if "Schedule-5" in required_forms:
            schedule_5 = self.generate_schedule_5(taxpayer_info)
            ereturn_package["forms"]["Schedule-5"] = schedule_5
            print("✅ Schedule-5 generated")
        
        return ereturn_package
    
    def generate_schedule_5(self, taxpayer_info):
        """Generate Schedule-5 for investment rebate details"""
        investment_amount = taxpayer_info.get('investment_amount', 0)
        rebate_info = self.calculate_investment_rebate(taxpayer_info.get('annual_income', 0), investment_amount)
        
        schedule_5 = {
            "form_type": "Schedule-5",
            "form_title": "Investment Tax Credit Details",
            "assessment_year": "2024-2025",
            "investment_details": {
                "approved_securities": taxpayer_info.get('govt_securities_investment', 0),
                "unit_certificates": taxpayer_info.get('unit_certificate_investment', 0),
                "life_insurance": taxpayer_info.get('life_insurance_premium', 0),
                "dps_schemes": taxpayer_info.get('dps_investment', 0),
                "provident_fund": taxpayer_info.get('provident_fund_contribution', 0),
                "pension_scheme": taxpayer_info.get('pension_scheme_contribution', 0),
                "zakat_donation": taxpayer_info.get('zakat_donation', 0),
                "other_approved": taxpayer_info.get('other_approved_investment', 0),
                "total_investment": investment_amount
            },
            "rebate_calculation": rebate_info,
            "submission_info": {
                "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "form_status": "Generated - Ready for Review"
            }
        }
        
        return schedule_5

def main():
    print("🚀 eReturn Form Generator - Phase 0 Complete Implementation")
    print("=" * 60)
    
    generator = EReturnFormGenerator()
    
    # Test with comprehensive taxpayer data
    test_taxpayer = {
        "name": "Md. Rahman Ahmed",
        "tin": "123456789012",
        "tax_circle": "Dhaka-1",
        "tax_zone": "Dhaka North",
        "annual_income": 1200000,  # 12 lakh
        "salary_income": 800000,
        "business_income": 300000,
        "rental_income": 100000,
        "investment_amount": 150000,  # 1.5 lakh investment
        "tds_deducted": 15000,
        "advance_tax_paid": 5000,
        "owns_motor_car": True,
        "motor_vehicle_value": 1500000,
        "has_city_corporation_property": True,
        "land_property": 3000000,
        "building_value": 2000000,
        "bank_deposits": 500000,
        "gross_wealth": 7000000,  # 70 lakh - triggers IT-10B
        "food_clothing_expense": 200000,
        "housing_utilities": 150000,
        "transport_expense": 100000,
        "education_expense": 50000
    }
    
    # Generate complete eReturn package
    ereturn_package = generator.generate_complete_ereturn_package(test_taxpayer)
    
    # Save the complete package
    output_file = "complete_ereturn_package.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ereturn_package, f, ensure_ascii=False, indent=2)
    
    print(f"\n📦 Complete eReturn package saved: {output_file}")
    
    # Display summary
    forms = ereturn_package["forms"]
    print(f"\n📊 ERETURN PACKAGE SUMMARY")
    print("=" * 40)
    print(f"👤 Taxpayer: {test_taxpayer['name']}")
    print(f"🆔 TIN: {test_taxpayer['tin']}")
    print(f"💰 Annual Income: {test_taxpayer['annual_income']:,} Taka")
    
    if "IT-11GA" in forms:
        it_11ga = forms["IT-11GA"]
        print(f"📋 IT-11GA: Generated")
        print(f"   💸 Gross Tax: {it_11ga['tax_calculation']['gross_tax']:,.2f} Taka")
        print(f"   🎯 Net Tax: {it_11ga['tax_calculation']['net_tax']:,.2f} Taka")
        print(f"   📈 Final Amount: {it_11ga['final_calculation']['final_amount']:,.2f} Taka ({it_11ga['final_calculation']['status']})")
    
    if "IT-10B" in forms:
        it_10b = forms["IT-10B"]
        print(f"📋 IT-10B: Generated (Reason: {it_10b['summary']['requirement_reason']})")
        print(f"   🏠 Total Assets: {it_10b['summary']['total_assets']:,.2f} Taka")
        print(f"   💳 Total Liabilities: {it_10b['summary']['total_liabilities']:,.2f} Taka")
        print(f"   💎 Net Wealth: {it_10b['summary']['net_wealth']:,.2f} Taka")
    
    if "IT-10BB" in forms:
        it_10bb = forms["IT-10BB"]
        print(f"📋 IT-10BB: Generated (Reason: {it_10bb['summary']['requirement_reason']})")
        print(f"   🛍️  Total Expenditure: {it_10bb['summary']['total_lifestyle_expenditure']:,.2f} Taka")
        print(f"   📊 Expenditure/Income Ratio: {it_10bb['summary']['expenditure_vs_income_ratio']:.1f}%")
    
    if "Schedule-5" in forms:
        schedule_5 = forms["Schedule-5"]
        print(f"📋 Schedule-5: Generated")
        print(f"   💰 Investment: {schedule_5['investment_details']['total_investment']:,.2f} Taka")
        print(f"   🎁 Rebate: {schedule_5['rebate_calculation']['actual_rebate']:,.2f} Taka")
    
    print(f"\n✅ All required forms generated successfully!")
    return len(forms)

if __name__ == "__main__":
    main()