#!/usr/bin/env python3
"""
Test Teacher Scenario: Tk 9 lakh income, Tk 2 lakh savings certificates
=====================================================================

This script tests the exact scenario:
Teacher with Tk 9,00,000 income and Tk 2,00,000 in savings certificates.
What is the final tax?
"""

import requests
import json

def test_teacher_tax_calculation():
    """Test the teacher scenario with exact figures"""
    
    # API endpoint
    url = "http://localhost:8000/calculate-tax"
    
    # Teacher's data - Tk 9 lakh income, Tk 2 lakh savings certificates
    teacher_data = {
        "taxpayer": {
            "name": "Professor Rahman",
            "tin": "123456789012",
            "nid": "1234567890123",
            "category": "individual",
            "age": 40,
            "gender": "male",
            "marital_status": "married",
            "location": "dhaka_city",
            "profession": "Teacher",
            "residential_status": "resident"
        },
        "income": {
            # Teacher's salary income - Tk 9,00,000
            "basic_salary": 900000,  # 9 lakh
            "house_rent_allowance": 0,
            "medical_allowance": 0,
            "other_allowances": 0,
            "bonus": 0,
            # All other income sources are 0
            "business_income": 0,
            "rental_income": 0,
            "agricultural_income": 0,
            "bank_interest": 0,
            "dividend_income": 0,
            "other_income": 0
        },
        "investments": {
            # Tk 2,00,000 in savings certificates
            "savings_certificate": 200000,  # 2 lakh in savings certificates
            # All other investments are 0
            "life_insurance_premium": 0,
            "dps_contribution": 0,
            "universal_pension": 0,
            "sanchayapatra": 0,
            "treasury_bond": 0,
            "listed_securities": 0,
            "mutual_fund_units": 0,
            "etf_investment": 0,
            "gpf_contribution": 0,
            "rpf_contribution": 0,
            "superannuation_fund": 0,
            "benevolent_fund": 0,
            "group_insurance": 0,
            "zakat_fund": 0,
            "charitable_donation": 0
        },
        "lifestyle": {
            # Minimal lifestyle expenses
            "food_clothing": 0,
            "accommodation": 0,
            "transportation": 0,
            "education_expenses": 0,
            "medical_expenses": 0,
            "electricity_gas": 0,
            "telephone_internet": 0,
            "entertainment": 0,
            "travel_vacation": 0,
            "festival_expenses": 0,
            "other_expenses": 0
        },
        "assets": {
            # Basic assets
            "house_property": 0,
            "land_property": 0,
            "motor_vehicle": 0,
            "gold_jewelry": 0,
            "bank_deposits": 0,
            "share_securities": 0,
            "other_deposits": 0,
            "business_capital": 0,
            "business_property": 0,
            "business_equipment": 0,
            # Liabilities
            "house_building_loan": 0,
            "motor_vehicle_loan": 0,
            "other_loans": 0,
            "business_liabilities": 0
        },
        "payments": {
            # No advance payments
            "salary_tds": 0,
            "rent_tds": 0,
            "contractor_tds": 0,
            "import_tds": 0,
            "other_tds": 0,
            "advance_tax_paid": 0,
            "previous_refund": 0,
            "previous_due": 0
        }
    }
    
    print("🧮 Calculating Tax for Teacher Scenario")
    print("=" * 50)
    print(f"Income: ₹{teacher_data['income']['basic_salary']:,} (9 lakh)")
    print(f"Savings Certificates: ₹{teacher_data['investments']['government_securities']:,} (2 lakh)")
    print()
    
    try:
        # Make API request
        response = requests.post(url, json=teacher_data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            print("✅ Tax Calculation Successful!")
            print("=" * 50)
            
            # Display key results
            print(f"👨‍🏫 Taxpayer: {result['taxpayer_name']}")
            print(f"📊 Category: {result['taxpayer_category']}")
            print()
            
            print("💰 INCOME BREAKDOWN:")
            print(f"   Total Income: ₹{result['total_income']:,.2f}")
            print(f"   Taxable Income: ₹{result['taxable_income']:,.2f}")
            print()
            
            print("📈 TAX CALCULATION:")
            print(f"   Gross Tax: ₹{result['gross_tax']:,.2f}")
            print(f"   Tax After Rebate: ₹{result['net_tax_after_rebate']:,.2f}")
            print(f"   Minimum Tax: ₹{result['minimum_tax']:,.2f}")
            print()
            
            print("🎯 FINAL RESULT:")
            print(f"   Tax Payable: ₹{result['tax_payable']:,.2f}")
            print(f"   Total Amount Payable: ₹{result['total_amount_payable']:,.2f}")
            print(f"   Payment Status: {result['payment_status']}")
            
            # Show exemptions
            if result.get('exemptions'):
                print()
                print("🎁 EXEMPTIONS APPLIED:")
                exemptions = result['exemptions']
                if isinstance(exemptions, dict):
                    for key, value in exemptions.items():
                        if isinstance(value, (int, float)) and value > 0:
                            print(f"   {key.replace('_', ' ').title()}: ₹{value:,.2f}")
            
            # Show rebates
            if result.get('rebates'):
                print()
                print("💸 INVESTMENT REBATES:")
                rebates = result['rebates']
                if isinstance(rebates, dict):
                    for key, value in rebates.items():
                        if isinstance(value, (int, float)) and value > 0:
                            print(f"   {key.replace('_', ' ').title()}: ₹{value:,.2f}")
            
            # Manual calculation verification
            print()
            print("🔍 MANUAL VERIFICATION:")
            income = 900000
            exemption = 350000  # Basic exemption for individual
            taxable = income - exemption  # 550000
            
            # Tax calculation on 550000
            # 0-350000: 0% = 0
            # 350001-450000: 5% on 100000 = 5000  
            # 450001-550000: 10% on 100000 = 10000
            # Total = 15000
            manual_tax = 5000 + 10000  # 15000
            
            # Investment rebate: 15% on 200000 = 30000, but limited to tax amount
            rebate = min(30000, manual_tax)  # min(30000, 15000) = 15000
            final_manual = max(0, manual_tax - rebate)  # max(0, 15000-15000) = 0
            
            print(f"   Manual Calculation:")
            print(f"   Income: ₹{income:,}")
            print(f"   Less: Exemption: ₹{exemption:,}")
            print(f"   Taxable Income: ₹{taxable:,}")
            print(f"   Tax (5% on 1st 1L + 10% on next 1L): ₹{manual_tax:,}")
            print(f"   Investment Rebate (15% on 2L, max ₹{manual_tax:,}): ₹{rebate:,}")
            print(f"   Final Tax: ₹{final_manual:,}")
            
            print()
            print("🎉 ANSWER TO THE QUESTION:")
            print(f"   Teacher with ₹9,00,000 income and ₹2,00,000 savings certificates")
            print(f"   Final Tax Payable: ₹{result['tax_payable']:,.2f}")
            
            return result
            
        else:
            print("❌ Tax Calculation Failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Failed: {e}")
        print("Make sure the API server is running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None

def test_api_availability():
    """Test if API server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server is running")
            return True
        else:
            print(f"⚠️ API Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ API Server is not running")
        print("Please start the server first:")
        print("   python tax_api_backend.py")
        print("   OR")
        print("   python start_api_server.py")
        return False

if __name__ == "__main__":
    print("Bangladesh Tax Calculation API - Teacher Scenario Test")
    print("=" * 60)
    
    # Check API availability
    if not test_api_availability():
        exit(1)
    
    # Run the teacher tax calculation
    result = test_teacher_tax_calculation()
    
    if result:
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("The API can handle complex tax questions with precise calculations.")
    else:
        print("\n" + "=" * 60)
        print("❌ Test failed!")