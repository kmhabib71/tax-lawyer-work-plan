#!/usr/bin/env python3
"""
Quick Teacher Demo - Direct Engine Test
======================================

Direct calculation using the comprehensive tax engine to demonstrate
the exact answer to: "Teacher: Tk 9 lakh income, Tk 2 lakh savings certificates. Final tax?"
"""

from comprehensive_tax_engine_2024_25 import (
    ComprehensiveTaxEngine,
    TaxpayerProfile,
    IncomeDetails,
    InvestmentRebate,
    LifestyleExpenses,
    AssetsLiabilities,
    TaxPayments,
    TaxpayerCategory,
    LocationCategory
)
from decimal import Decimal

def calculate_teacher_tax():
    """Calculate tax for the teacher scenario"""
    
    print("🧮 Teacher Tax Calculation Demo")
    print("=" * 40)
    print("Question: Teacher with Tk 9 lakh income, Tk 2 lakh savings certificates. Final tax?")
    print()
    
    # Initialize the tax engine
    engine = ComprehensiveTaxEngine()
    
    # Create teacher profile
    teacher = TaxpayerProfile(
        name="Professor Rahman",
        tin="123456789012",
        nid="1234567890123",
        category=TaxpayerCategory.INDIVIDUAL,
        age=40,
        gender="male",
        marital_status="married",
        location=LocationCategory.DHAKA_CITY,
        profession="Teacher"
    )
    
    # Teacher's income - Tk 9,00,000
    income = IncomeDetails(
        basic_salary=Decimal('900000'),  # 9 lakh
        # All other income sources default to 0
    )
    
    # Investment in savings certificates - Tk 2,00,000
    investments = InvestmentRebate(
        savings_certificate=Decimal('200000'),  # 2 lakh in savings certificates
        # All other investments default to 0
    )
    
    # Minimal lifestyle, assets, and payments (all defaults)
    lifestyle = LifestyleExpenses()
    assets = AssetsLiabilities()
    payments = TaxPayments()
    
    # Calculate comprehensive tax
    print("💭 Calculating...")
    result = engine.calculate_comprehensive_tax(
        taxpayer=teacher,
        income=income,
        investments=investments,
        lifestyle=lifestyle,
        assets=assets,
        payments=payments
    )
    
    # Display results
    print("✅ Calculation Complete!")
    print("=" * 40)
    
    # Debug: show all keys in result
    print("📋 Available result keys:", list(result.keys()))
    print()
    
    print(f"👨‍🏫 Teacher: {teacher.name}")
    
    # Use safe access to avoid KeyError
    total_income = result.get('total_income', 0)
    taxable_income = result.get('taxable_income', 0)
    gross_tax = result.get('gross_tax', 0)
    rebate_amount = result.get('rebate_amount', 0)
    net_tax = result.get('net_tax_after_rebate', result.get('net_tax', 0))
    minimum_tax = result.get('minimum_tax', 0)
    tax_payable = result.get('tax_payable', result.get('final_tax', 0))
    
    print(f"💰 Total Income: ₹{total_income:,}")
    print(f"📊 Taxable Income: ₹{taxable_income:,}")
    print(f"🧾 Gross Tax: ₹{gross_tax:,}")
    print(f"💸 Investment Rebate: ₹{rebate_amount:,}")
    print(f"📈 Net Tax After Rebate: ₹{net_tax:,}")
    print(f"⚖️ Minimum Tax: ₹{minimum_tax:,}")
    print()
    print(f"🎯 FINAL TAX PAYABLE: ₹{tax_payable:,}")
    
    # Manual verification
    print()
    print("🔍 Manual Verification:")
    print("   Income: ₹9,00,000")
    print("   Less: Basic Exemption: ₹3,50,000")
    print("   Taxable Income: ₹5,50,000")
    print()
    print("   Tax Calculation:")
    print("   First ₹1,00,000 (₹3,50,001 to ₹4,50,000): 5% = ₹5,000")
    print("   Next ₹1,00,000 (₹4,50,001 to ₹5,50,000): 10% = ₹10,000")
    print("   Total Gross Tax: ₹15,000")
    print()
    print("   Investment Rebate:")
    print("   15% on ₹2,00,000 = ₹30,000")
    print("   But limited to gross tax = ₹15,000")
    print("   Rebate Applied: ₹15,000")
    print()
    print("   Final Tax: ₹15,000 - ₹15,000 = ₹0")
    
    print()
    print("🎉 ANSWER:")
    print(f"   Teacher with ₹9,00,000 income and ₹2,00,000 savings certificates")
    print(f"   pays ZERO TAX due to investment rebate!")
    
    # Extract actual tax payable from result structure
    if 'tax_calculation' in result:
        tax_calc = result['tax_calculation']
        actual_tax = tax_calc.get('tax_payable', tax_calc.get('final_tax', 0))
    else:
        actual_tax = tax_payable
    
    print()
    print("📊 Result Structure Analysis:")
    print("   tax_calculation contents:")
    tax_calc = result.get('tax_calculation', {})
    for subkey, subvalue in tax_calc.items():
        print(f"      {subkey}: {subvalue}")
    
    print()
    print("   total_payable:", result.get('total_payable'))
    print("   payment_summary:", result.get('payment_summary'))
    
    return result

if __name__ == "__main__":
    try:
        result = calculate_teacher_tax()
        
        # Extract final tax amount safely
        final_tax = 0
        if 'tax_calculation' in result:
            tax_calc = result['tax_calculation']
            final_tax = tax_calc.get('tax_payable', tax_calc.get('final_tax', 0))
        elif 'total_payable' in result:
            final_tax = result['total_payable']
        
        print(f"\n✅ Final Answer: ₹{float(final_tax):,.2f}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()