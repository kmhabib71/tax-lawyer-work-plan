#!/usr/bin/env python3
"""
Simple Demo: How to Test the Comprehensive Tax Engine
===================================================

This demonstrates the key testing approaches for the Bangladesh tax engine:
1. Basic individual taxpayer scenarios
2. Company tax calculations  
3. Special status testing
4. Investment rebate testing
5. Precision validation

Run this file to see comprehensive testing in action.
"""

from decimal import Decimal
from comprehensive_tax_engine_2024_25 import (
    ComprehensiveTaxEngine,
    TaxpayerProfile, IncomeDetails, InvestmentRebate, 
    LifestyleExpenses, AssetsLiabilities, TaxPayments,
    TaxpayerCategory, LocationCategory, SpecialStatus
)

def test_basic_scenarios():
    """Test basic tax calculation scenarios"""
    print("🧪 TESTING BASIC SCENARIOS")
    print("=" * 50)
    
    engine = ComprehensiveTaxEngine()
    
    # Test 1: Basic Individual (Below exemption)
    print("\n📋 Test 1: Basic Individual Taxpayer")
    taxpayer = TaxpayerProfile(
        name="আহমেদ হাসান",
        tin="123456789001",
        nid="1234567890123456",
        category=TaxpayerCategory.INDIVIDUAL,
        age=30,
        gender="male",
        marital_status="married",
        location=LocationCategory.DHAKA_CITY
    )
    
    income = IncomeDetails(
        basic_salary=Decimal('300000'),  # 3 lakh - below exemption
        house_rent_allowance=Decimal('90000')
    )
    
    result = engine.calculate_comprehensive_tax(
        taxpayer=taxpayer,
        income=income,
        investments=InvestmentRebate(),
        lifestyle=LifestyleExpenses(),
        assets=AssetsLiabilities(),
        payments=TaxPayments()
    )
    
    print(f"Total Income: ৳{result['income_summary']['total_income']}")
    print(f"Taxable Income: ৳{result['income_summary']['taxable_income']}")
    print(f"Tax Payable: ৳{result['tax_calculation']['tax_payable']}")
    print(f"Status: {'✅ PASSED' if result['tax_calculation']['tax_payable'] == '0' else '❌ FAILED'}")
    
    # Test 2: Taxable Individual
    print("\n📋 Test 2: Taxable Individual")
    income2 = IncomeDetails(
        basic_salary=Decimal('800000'),  # 8 lakh - above exemption
        house_rent_allowance=Decimal('240000'),
        medical_allowance=Decimal('80000')
    )
    
    result2 = engine.calculate_comprehensive_tax(
        taxpayer=taxpayer,
        income=income2,
        investments=InvestmentRebate(),
        lifestyle=LifestyleExpenses(),
        assets=AssetsLiabilities(),
        payments=TaxPayments()
    )
    
    print(f"Total Income: ৳{result2['income_summary']['total_income']}")
    print(f"Taxable Income: ৳{result2['income_summary']['taxable_income']}")
    print(f"Tax Payable: ৳{result2['tax_calculation']['tax_payable']}")
    
    # Expected: (1120000 - 350000) * progressive rates
    # 770000 taxable: 100k@5% + 300k@10% + 370k@15% = 5k + 30k + 55.5k = 90.5k
    expected_range = (85000, 95000)
    actual_tax = float(result2['tax_calculation']['tax_payable'])
    print(f"Status: {'✅ PASSED' if expected_range[0] <= actual_tax <= expected_range[1] else '❌ FAILED'}")

def test_company_scenarios():
    """Test company tax calculations"""
    print("\n\n🧪 TESTING COMPANY SCENARIOS")
    print("=" * 50)
    
    engine = ComprehensiveTaxEngine()
    
    # Test 3: Publicly Traded Company
    print("\n📋 Test 3: Publicly Traded Company")
    company = TaxpayerProfile(
        name="ABC Industries Ltd",
        tin="123456789007",
        nid="",
        category=TaxpayerCategory.COMPANY,
        age=0,
        gender="",
        marital_status="",
        location=LocationCategory.DHAKA_CITY,
        company_type="publicly_traded"
    )
    
    company_income = IncomeDetails(
        trading_income=Decimal('10000000'),  # 1 crore business income
        export_income=Decimal('5000000'),    # 50 lakh export (50% rate reduction)
    )
    
    result3 = engine.calculate_comprehensive_tax(
        taxpayer=company,
        income=company_income,
        investments=InvestmentRebate(),
        lifestyle=LifestyleExpenses(),
        assets=AssetsLiabilities(),
        payments=TaxPayments()
    )
    
    print(f"Total Income: ৳{result3['income_summary']['total_income']}")
    print(f"Tax Payable: ৳{result3['tax_calculation']['tax_payable']}")
    print(f"Environmental Surcharge: ৳{result3['surcharges']['environmental_surcharge']}")
    
    # Expected: 25% rate + environmental surcharge
    expected_min_tax = 2500000  # At least 25 lakh
    actual_tax = float(result3['tax_calculation']['tax_payable'])
    print(f"Status: {'✅ PASSED' if actual_tax >= expected_min_tax else '❌ FAILED'}")

def test_special_status():
    """Test special status benefits"""
    print("\n\n🧪 TESTING SPECIAL STATUS BENEFITS")
    print("=" * 50)
    
    engine = ComprehensiveTaxEngine()
    
    # Test 4: Female Taxpayer
    print("\n📋 Test 4: Female Taxpayer with Additional Exemption")
    female_taxpayer = TaxpayerProfile(
        name="রেশমা আক্তার",
        tin="123456789004",
        nid="1234567890123459",
        category=TaxpayerCategory.INDIVIDUAL,
        age=28,
        gender="female",
        marital_status="married",
        location=LocationCategory.DHAKA_CITY,
        special_statuses=[SpecialStatus.FEMALE]
    )
    
    female_income = IncomeDetails(
        basic_salary=Decimal('500000'),  # 5 lakh
        trading_income=Decimal('200000')  # 2 lakh business
    )
    
    result4 = engine.calculate_comprehensive_tax(
        taxpayer=female_taxpayer,
        income=female_income,
        investments=InvestmentRebate(),
        lifestyle=LifestyleExpenses(),
        assets=AssetsLiabilities(),
        payments=TaxPayments()
    )
    
    print(f"Total Income: ৳{result4['income_summary']['total_income']}")
    print(f"Taxable Income: ৳{result4['income_summary']['taxable_income']}")
    print(f"Tax Payable: ৳{result4['tax_calculation']['tax_payable']}")
    
    # Female gets 375k exemption, so should have lower tax than male
    taxable = float(result4['income_summary']['taxable_income'])
    print(f"Status: {'✅ PASSED' if taxable <= 325000 else '❌ FAILED'} (Should use 375k female exemption)")

def test_investment_rebate():
    """Test investment rebate calculations"""
    print("\n\n🧪 TESTING INVESTMENT REBATE")
    print("=" * 50)
    
    engine = ComprehensiveTaxEngine()
    
    # Test 5: High earner with investments
    print("\n📋 Test 5: Investment Rebate Calculation")
    investor = TaxpayerProfile(
        name="বিনিয়োগকারী হাসান",
        tin="123456789011",
        nid="1234567890123462",
        category=TaxpayerCategory.INDIVIDUAL,
        age=35,
        gender="male",
        marital_status="married",
        location=LocationCategory.DHAKA_CITY
    )
    
    high_income = IncomeDetails(
        basic_salary=Decimal('2000000'),    # 20 lakh salary
        trading_income=Decimal('1000000')   # 10 lakh business
    )
    
    # Significant investments
    investments = InvestmentRebate(
        life_insurance_premium=Decimal('500000'),  # 5 lakh
        listed_securities=Decimal('1000000'),      # 10 lakh
        dps_contribution=Decimal('200000')         # 2 lakh
    )
    
    result5 = engine.calculate_comprehensive_tax(
        taxpayer=investor,
        income=high_income,
        investments=investments,
        lifestyle=LifestyleExpenses(),
        assets=AssetsLiabilities(),
        payments=TaxPayments()
    )
    
    print(f"Total Income: ৳{result5['income_summary']['total_income']}")
    print(f"Gross Tax: ৳{result5['tax_calculation']['gross_tax']}")
    print(f"Rebate Amount: ৳{result5['tax_calculation']['rebate_amount']}")
    print(f"Net Tax: ৳{result5['tax_calculation']['net_tax']}")
    
    # Should get significant rebate (15% on investments)
    rebate = float(result5['tax_calculation']['rebate_amount'])
    print(f"Status: {'✅ PASSED' if rebate > 100000 else '❌ FAILED'} (Should get significant rebate)")

def test_precision_validation():
    """Test mathematical precision"""
    print("\n\n🧪 TESTING MATHEMATICAL PRECISION")
    print("=" * 50)
    
    engine = ComprehensiveTaxEngine()
    
    # Test 6: Precision calculation
    print("\n📋 Test 6: Decimal Precision")
    precise_taxpayer = TaxpayerProfile(
        name="নির্ভুল হিসাব",
        tin="123456789013",
        nid="1234567890123464",
        category=TaxpayerCategory.INDIVIDUAL,
        age=30,
        gender="male",
        marital_status="single",
        location=LocationCategory.DHAKA_CITY
    )
    
    precise_income = IncomeDetails(
        basic_salary=Decimal('123456.78'),
        trading_income=Decimal('98765.43'),
        bank_interest=Decimal('12345.67')
    )
    
    result6 = engine.calculate_comprehensive_tax(
        taxpayer=precise_taxpayer,
        income=precise_income,
        investments=InvestmentRebate(),
        lifestyle=LifestyleExpenses(),
        assets=AssetsLiabilities(),
        payments=TaxPayments()
    )
    
    print(f"Total Income: ৳{result6['income_summary']['total_income']}")
    print(f"Expected Total: ৳{Decimal('123456.78') + Decimal('98765.43') + Decimal('12345.67')}")
    
    actual_total = Decimal(result6['income_summary']['total_income'])
    expected_total = Decimal('123456.78') + Decimal('98765.43') + Decimal('12345.67')
    
    print(f"Status: {'✅ PASSED' if actual_total == expected_total else '❌ FAILED'} (Precision maintained)")

def run_comprehensive_demo():
    """Run all test scenarios"""
    print("🚀 COMPREHENSIVE TAX ENGINE TESTING DEMO")
    print("🎯 Bangladesh Income Tax Circular 2024-25")
    print("=" * 60)
    
    test_basic_scenarios()
    test_company_scenarios()
    test_special_status()
    test_investment_rebate()
    test_precision_validation()
    
    print("\n" + "=" * 60)
    print("✅ TESTING DEMO COMPLETED")
    print("🎯 Key Features Demonstrated:")
    print("   • Individual & Company tax calculations")
    print("   • Special status benefits (female, disabled, etc.)")
    print("   • Investment rebate calculations")
    print("   • Mathematical precision (Decimal arithmetic)")
    print("   • Complex conditional logic from eReturn + Circular")
    print("=" * 60)
    
    print("\n📋 HOW TO USE THE TAX ENGINE:")
    print("1. Create TaxpayerProfile with complete details")
    print("2. Define IncomeDetails with all income sources")
    print("3. Add InvestmentRebate for tax savings")
    print("4. Include LifestyleExpenses & AssetsLiabilities for verification")
    print("5. Specify TaxPayments for final reconciliation")
    print("6. Call engine.calculate_comprehensive_tax()")
    print("7. Review detailed result dictionary")
    
    print("\n💡 TESTING BEST PRACTICES:")
    print("• Test edge cases (zero income, maximum income)")
    print("• Verify special status calculations")
    print("• Check investment rebate limits")
    print("• Validate surcharge applications")
    print("• Ensure precision in all calculations")
    print("• Test company vs individual differences")
    print("• Verify lifestyle-income matching")

if __name__ == "__main__":
    run_comprehensive_demo()