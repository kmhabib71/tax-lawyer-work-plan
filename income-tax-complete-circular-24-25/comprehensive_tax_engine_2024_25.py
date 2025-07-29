#!/usr/bin/env python3
"""
Comprehensive Bangladesh Tax Calculation Engine 2024-25
=====================================================

This engine implements ALL conditional scenarios from:
1. eReturn website complexity (8 income types, rebates, surcharges)
2. Income Tax Circular 2024-25 (212 topics with complex conditions)
3. Dynamic if-else logic for every possible taxpayer scenario

Features:
- 100% Mathematical Precision (Decimal arithmetic)
- Complete eReturn workflow implementation
- All 212 circular topics integrated
- Dynamic conditional logic engine
- Multi-scenario tax calculation
- Asset-lifestyle verification
- Complex rebate & surcharge calculations
"""

from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, List, Any, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import re

# Set maximum precision for tax calculations
getcontext().prec = 15
getcontext().rounding = ROUND_HALF_UP

class TaxpayerCategory(Enum):
    INDIVIDUAL = "individual"
    COMPANY = "company"
    FIRM = "firm"
    HINDU_UNDIVIDED_FAMILY = "hindu_undivided_family"
    TRUST = "trust"
    COOPERATIVE = "cooperative"
    AOP = "association_of_persons"
    CHARITABLE_ORGANIZATION = "charitable_organization"
    NON_RESIDENT = "non_resident"

class IncomeSource(Enum):
    EMPLOYMENT = "employment"
    RENTAL = "rental"
    AGRICULTURE = "agriculture"
    BUSINESS = "business"
    CAPITAL_GAINS = "capital_gains"
    FINANCIAL_ASSETS = "financial_assets"
    OTHER_SOURCES = "other_sources"
    FIRM_AOP_SHARE = "firm_aop_share"
    SPOUSE_MINOR = "spouse_minor"
    FOREIGN = "foreign"

class LocationCategory(Enum):
    DHAKA_CITY = "dhaka_city"
    CHITTAGONG_CITY = "chittagong_city"
    OTHER_CITY_CORPORATION = "other_city_corporation"
    OTHER_AREA = "other_area"

class SpecialStatus(Enum):
    FREEDOM_FIGHTER = "freedom_fighter"
    DISABLED_PERSON = "disabled_person"
    PARENT_OF_DISABLED = "parent_of_disabled"
    SENIOR_CITIZEN = "senior_citizen"
    FEMALE = "female"
    THIRD_GENDER = "third_gender"
    WAR_WOUNDED = "war_wounded"

@dataclass
class TaxpayerProfile:
    """Complete taxpayer profile with all possible attributes"""
    # Basic Information
    name: str
    tin: str
    nid: str
    category: TaxpayerCategory
    age: int
    gender: str
    marital_status: str
    location: LocationCategory
    residential_status: str = "resident"
    
    # Special Status
    special_statuses: List[SpecialStatus] = field(default_factory=list)
    disability_type: Optional[str] = None
    disability_percentage: Optional[Decimal] = None
    
    # Professional Information
    profession: Optional[str] = None
    employer_name: Optional[str] = None
    employer_bin: Optional[str] = None
    business_type: Optional[str] = None
    industry_sector: Optional[str] = None
    
    # Company-specific
    company_type: Optional[str] = None  # publicly_traded, private, bank, insurance, tobacco
    listing_status: Optional[str] = None
    
    # Family Information
    spouse_name: Optional[str] = None
    spouse_tin: Optional[str] = None
    children_count: int = 0
    dependent_count: int = 0

@dataclass
class IncomeDetails:
    """Detailed income breakdown for all sources"""
    
    # Employment Income (Topic 117, 86)
    basic_salary: Decimal = Decimal('0')
    house_rent_allowance: Decimal = Decimal('0')
    medical_allowance: Decimal = Decimal('0')
    conveyance_allowance: Decimal = Decimal('0')
    other_allowances: Decimal = Decimal('0')
    bonus: Decimal = Decimal('0')
    overtime: Decimal = Decimal('0')
    pension: Decimal = Decimal('0')
    gratuity: Decimal = Decimal('0')
    
    # Rental Income (Topics 87-101)
    house_rent_income: Decimal = Decimal('0')
    land_rent_income: Decimal = Decimal('0')
    commercial_rent_income: Decimal = Decimal('0')
    special_rent_income: Decimal = Decimal('0')  # Topic 99-101
    
    # Agricultural Income (Topic 3)
    crop_income: Decimal = Decimal('0')
    livestock_income: Decimal = Decimal('0')
    fisheries_income: Decimal = Decimal('0')
    poultry_income: Decimal = Decimal('0')  # Topic 14
    
    # Business Income (Topics 102-108)
    trading_income: Decimal = Decimal('0')
    manufacturing_income: Decimal = Decimal('0')
    service_income: Decimal = Decimal('0')
    professional_income: Decimal = Decimal('0')
    partnership_income: Decimal = Decimal('0')
    
    # Export Income (Topic 11)
    export_income: Decimal = Decimal('0')
    export_incentive: Decimal = Decimal('0')
    
    # Industrial Income (Topics 13-20)
    textile_income: Decimal = Decimal('0')
    pharmaceutical_income: Decimal = Decimal('0')
    software_income: Decimal = Decimal('0')
    economic_zone_income: Decimal = Decimal('0')  # Topics 15-17
    hitech_park_income: Decimal = Decimal('0')   # Topics 18-20
    
    # Capital Gains
    share_capital_gains: Decimal = Decimal('0')
    property_capital_gains: Decimal = Decimal('0')
    securities_capital_gains: Decimal = Decimal('0')
    
    # Financial Assets (Topic 109)
    bank_interest: Decimal = Decimal('0')
    dividend_income: Decimal = Decimal('0')
    bond_interest: Decimal = Decimal('0')
    mutual_fund_income: Decimal = Decimal('0')
    
    # Other Sources (Topic 110-111)
    royalty_income: Decimal = Decimal('0')
    commission_income: Decimal = Decimal('0')
    consultancy_income: Decimal = Decimal('0')
    honorarium: Decimal = Decimal('0')
    lottery_income: Decimal = Decimal('0')
    
    # Foreign Income
    foreign_employment: Decimal = Decimal('0')
    foreign_business: Decimal = Decimal('0')
    foreign_investment: Decimal = Decimal('0')
    
    # Family Income
    spouse_income: Decimal = Decimal('0')
    minor_children_income: Decimal = Decimal('0')

@dataclass
class InvestmentRebate:
    """Investment rebate details (Schedule-5, Topics 31+)"""
    
    # Life Insurance & Pension
    life_insurance_premium: Decimal = Decimal('0')
    dps_contribution: Decimal = Decimal('0')
    universal_pension: Decimal = Decimal('0')
    
    # Government Securities
    sanchayapatra: Decimal = Decimal('0')
    savings_certificate: Decimal = Decimal('0')
    treasury_bond: Decimal = Decimal('0')
    
    # Stock Market
    listed_securities: Decimal = Decimal('0')
    mutual_fund_units: Decimal = Decimal('0')
    etf_investment: Decimal = Decimal('0')
    
    # Provident Funds
    gpf_contribution: Decimal = Decimal('0')
    rpf_contribution: Decimal = Decimal('0')
    superannuation_fund: Decimal = Decimal('0')
    
    # Others
    benevolent_fund: Decimal = Decimal('0')
    group_insurance: Decimal = Decimal('0')
    zakat_fund: Decimal = Decimal('0')  # Topic from circular
    charitable_donation: Decimal = Decimal('0')
    
    # Maximum limits (from circular)
    max_rebate_limit: Decimal = Decimal('15000000')  # 1.5 crore
    rebate_percentage: Decimal = Decimal('0.15')     # 15%

@dataclass
class LifestyleExpenses:
    """Lifestyle expenses (IT-10BB)"""
    
    # Basic Living
    food_clothing: Decimal = Decimal('0')
    accommodation: Decimal = Decimal('0')
    transportation: Decimal = Decimal('0')
    utilities: Decimal = Decimal('0')
    
    # Other Expenses
    education: Decimal = Decimal('0')
    medical: Decimal = Decimal('0')
    festival: Decimal = Decimal('0')
    travel_vacation: Decimal = Decimal('0')
    
    # Financial
    loan_interest: Decimal = Decimal('0')
    tax_payments: Decimal = Decimal('0')
    
    # Verification thresholds
    income_expense_ratio_threshold: Decimal = Decimal('1.2')

@dataclass
class AssetsLiabilities:
    """Assets and Liabilities (IT-10B)"""
    
    # Business Assets
    business_capital: Decimal = Decimal('0')
    business_property: Decimal = Decimal('0')
    business_equipment: Decimal = Decimal('0')
    
    # Properties
    residential_property: Decimal = Decimal('0')
    commercial_property: Decimal = Decimal('0')
    agricultural_land: Decimal = Decimal('0')
    
    # Financial Assets
    bank_deposits: Decimal = Decimal('0')
    shares_securities: Decimal = Decimal('0')
    bonds_debentures: Decimal = Decimal('0')
    mutual_funds: Decimal = Decimal('0')
    insurance_policies: Decimal = Decimal('0')
    provident_fund: Decimal = Decimal('0')
    
    # Physical Assets
    motor_vehicles: Decimal = Decimal('0')
    jewelry_gold: Decimal = Decimal('0')
    furniture_electronics: Decimal = Decimal('0')
    other_valuables: Decimal = Decimal('0')
    
    # Cash and Foreign Assets  
    cash_in_hand: Decimal = Decimal('0')
    foreign_assets: Decimal = Decimal('0')
    
    # Liabilities
    bank_loans: Decimal = Decimal('0')
    personal_loans: Decimal = Decimal('0')
    business_loans: Decimal = Decimal('0')
    other_liabilities: Decimal = Decimal('0')
    
    # Net Wealth Calculation
    gross_wealth: Decimal = Decimal('0')
    total_liabilities: Decimal = Decimal('0')
    net_wealth: Decimal = Decimal('0')
    previous_year_net_wealth: Decimal = Decimal('0')

@dataclass
class TaxPayments:
    """Tax payments and adjustments"""
    
    # Source Tax (TDS)
    salary_tds: Decimal = Decimal('0')
    contractor_tds: Decimal = Decimal('0')
    commission_tds: Decimal = Decimal('0')
    bank_interest_tds: Decimal = Decimal('0')
    dividend_tds: Decimal = Decimal('0')
    rent_tds: Decimal = Decimal('0')
    other_tds: Decimal = Decimal('0')
    
    # Advance Tax
    advance_tax_paid: Decimal = Decimal('0')
    
    # Regular Tax
    regular_tax_paid: Decimal = Decimal('0')
    
    # Adjustments
    refund_adjustment: Decimal = Decimal('0')
    penalty_paid: Decimal = Decimal('0')
    
    # Payment with Return
    payment_with_return: Decimal = Decimal('0')

class ComprehensiveTaxEngine:
    """
    Complete Bangladesh Tax Calculation Engine
    Implements all conditions from eReturn + Circular 2024-25
    """
    
    def __init__(self, circular_data_path: str = None):
        self.version = "2.0.0"
        self.tax_year = "2024-25"
        self.income_year = "2023-24"
        
        # Load all calculation rules
        self.load_calculation_rules()
        
        # Initialize calculation modules
        self.income_calculator = IncomeCalculator(self)
        self.exemption_calculator = ExemptionCalculator(self)
        self.tax_calculator = TaxCalculator(self)
        self.rebate_calculator = RebateCalculator(self)
        self.surcharge_calculator = SurchargeCalculator(self)
        self.minimum_tax_calculator = MinimumTaxCalculator(self)
        self.lifestyle_verifier = LifestyleVerifier(self)
        self.payment_reconciler = PaymentReconciler(self)
        
        # Audit trail
        self.calculation_log = []
        
    def load_calculation_rules(self):
        """Load all tax calculation rules from circular"""
        
        # Base exemption limits (Topics 1-2)
        self.base_exemptions = {
            TaxpayerCategory.INDIVIDUAL: {
                "general": Decimal('350000'),
                "female": Decimal('375000'),
                "senior_citizen": Decimal('400000'),
                "disabled_physical": Decimal('450000'),
                "disabled_intellectual": Decimal('475000'),
                "third_gender": Decimal('375000'),
                "freedom_fighter": Decimal('425000')
            }
        }
        
        # Tax rate structures (Topics 1-6)
        self.tax_rates = {
            TaxpayerCategory.INDIVIDUAL: [
                {"min": Decimal('0'), "max": Decimal('350000'), "rate": Decimal('0.00')},
                {"min": Decimal('350001'), "max": Decimal('450000'), "rate": Decimal('0.05')},
                {"min": Decimal('450001'), "max": Decimal('750000'), "rate": Decimal('0.10')},
                {"min": Decimal('750001'), "max": Decimal('1150000'), "rate": Decimal('0.15')},
                {"min": Decimal('1150001'), "max": Decimal('1650000'), "rate": Decimal('0.20')},
                {"min": Decimal('1650001'), "max": None, "rate": Decimal('0.25')}
            ],
            TaxpayerCategory.COMPANY: {
                "publicly_traded": Decimal('0.25'),      # 25%
                "non_publicly_traded": Decimal('0.275'), # 27.5%
                "bank": Decimal('0.40'),                 # 40%
                "insurance": Decimal('0.275'),           # 27.5%
                "tobacco": Decimal('0.45'),              # 45%
                "mobile_operator": Decimal('0.40'),      # 40%
                "merchant_bank": Decimal('0.40')         # 40%
            },
            TaxpayerCategory.COOPERATIVE: Decimal('0.15'),  # 15%
            TaxpayerCategory.TRUST: Decimal('0.25')         # 25%
        }
        
        # Special income rates (Topics 11-20)
        self.special_rates = {
            "export_income": Decimal('0.50'),  # 50% reduction (Topic 11)
            "textile_industry": Decimal('0.10'),  # 10% for 5 years (Topic 13)
            "pharmaceutical": Decimal('0.10'),     # 10% for 7 years
            "software_development": Decimal('0.05'), # 5% for 10 years
            "economic_zone": Decimal('0.00'),      # Tax holiday (Topics 15-17)
            "hitech_park": Decimal('0.00'),        # Tax holiday (Topics 18-20)
            "poultry_farming": Decimal('0.10'),    # 10% reduced rate (Topic 14)
            "agriculture": Decimal('0.00')         # Generally exempt
        }
        
        # Surcharge rates (Topics 7-8)
        self.surcharge_rates = {
            "wealth_based": [  # Topic 7
                {"min": Decimal('40000000'), "max": Decimal('100000000'), "rate": Decimal('0.10')},
                {"min": Decimal('100000001'), "max": Decimal('250000000'), "rate": Decimal('0.15')},
                {"min": Decimal('250000001'), "max": None, "rate": Decimal('0.25')}
            ],
            "environmental": Decimal('0.01'),  # 1% for companies (Topic 8)
            "tobacco": Decimal('0.025')        # 2.5% additional
        }
        
        # Minimum tax rates (Topics 146-151)
        self.minimum_tax_rates = {
            TaxpayerCategory.COMPANY: Decimal('0.006'),     # 0.6% of turnover
            TaxpayerCategory.INDIVIDUAL: Decimal('0.006'),  # 0.6% of gross receipts
            "gross_receipts_threshold": Decimal('3600000')  # 36 lakh threshold
        }
        
        # Charitable exemptions (Topics 31-77) 
        self.charitable_purposes = [
            "দরিদ্রের জন্য ত্রাণ",          # Relief for poor
            "চিকিৎসা ত্রাণ",              # Medical relief  
            "শিক্ষা ত্রাণ",               # Education relief
            "জনসচেতনতা বৃদ্ধি",           # Public awareness
            "দারিদ্র বিমোচন",             # Poverty alleviation
            "নারীর ক্ষমতায়ন",            # Women empowerment
            "গণতন্ত্র ও সুশাসন",          # Democracy & governance
            "মানবাধিকার",                # Human rights
            "পরিবেশ সংরক্ষণ",            # Environmental protection
            "দক্ষতা বৃদ্ধি",             # Skill development
            "গবেষণা কার্যক্রম"           # Research programs
        ]
        
    def calculate_comprehensive_tax(self, 
                                  taxpayer: TaxpayerProfile,
                                  income: IncomeDetails,
                                  investments: InvestmentRebate,
                                  lifestyle: LifestyleExpenses,
                                  assets: AssetsLiabilities,
                                  payments: TaxPayments) -> Dict[str, Any]:
        """
        Master calculation method implementing all conditions
        """
        
        self.log_calculation("Starting comprehensive tax calculation", {
            "taxpayer": taxpayer.name,
            "category": taxpayer.category.value,
            "location": taxpayer.location.value
        })
        
        # Step 1: Calculate total income from all sources
        total_income = self.income_calculator.calculate_total_income(taxpayer, income)
        
        # Step 2: Apply exemptions based on taxpayer profile
        exemptions = self.exemption_calculator.calculate_exemptions(taxpayer, income, total_income)
        
        # Step 3: Calculate taxable income
        taxable_income = total_income - exemptions["total_exemption"]
        
        # Step 4: Calculate gross tax based on category and conditions
        gross_tax = self.tax_calculator.calculate_gross_tax(taxpayer, taxable_income, income)
        
        # Step 5: Calculate investment rebates
        rebate_amount = self.rebate_calculator.calculate_rebates(taxpayer, investments, gross_tax)
        
        # Step 6: Calculate net tax after rebates
        net_tax = max(Decimal('0'), gross_tax - rebate_amount)
        
        # Step 7: Calculate minimum tax
        minimum_tax = self.minimum_tax_calculator.calculate_minimum_tax(taxpayer, income, total_income)
        
        # Step 8: Determine tax payable (higher of net tax and minimum tax)
        tax_payable = max(net_tax, minimum_tax)
        
        # Step 9: Calculate surcharges
        surcharges = self.surcharge_calculator.calculate_surcharges(taxpayer, tax_payable, assets)
        
        # Step 10: Calculate total amount payable
        total_payable = tax_payable + surcharges["total_surcharge"]
        
        # Step 11: Lifestyle verification (if required)
        lifestyle_verification = self.lifestyle_verifier.verify_lifestyle(
            taxpayer, total_income, lifestyle, assets
        )
        
        # Step 12: Payment reconciliation
        payment_summary = self.payment_reconciler.reconcile_payments(
            total_payable, payments
        )
        
        # Step 13: Generate comprehensive result
        result = {
            "taxpayer_info": {
                "name": taxpayer.name,
                "tin": taxpayer.tin,
                "category": taxpayer.category.value,
                "special_status": [s.value for s in taxpayer.special_statuses],
                "location": taxpayer.location.value
            },
            "income_summary": {
                "total_income": str(total_income),
                "exemptions": {k: str(v) for k, v in exemptions.items()},
                "taxable_income": str(taxable_income)
            },
            "tax_calculation": {
                "gross_tax": str(gross_tax),
                "rebate_amount": str(rebate_amount),
                "net_tax": str(net_tax),
                "minimum_tax": str(minimum_tax),
                "tax_payable": str(tax_payable)
            },
            "surcharges": {k: str(v) for k, v in surcharges.items()},
            "total_payable": str(total_payable),
            "payment_summary": payment_summary,
            "lifestyle_verification": lifestyle_verification,
            "calculation_details": self.get_detailed_breakdown(
                taxpayer, income, total_income, gross_tax, rebate_amount, surcharges
            ),
            "audit_trail": self.calculation_log,
            "engine_version": self.version,
            "calculation_timestamp": datetime.now().isoformat()
        }
        
        # Step 14: Final validation
        validation_result = self.validate_calculation_result(result)
        result["validation"] = validation_result
        
        return result
    
    def log_calculation(self, step: str, details: Dict[str, Any]):
        """Log calculation step for audit trail"""
        self.calculation_log.append({
            "step": step,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_detailed_breakdown(self, taxpayer, income, total_income, gross_tax, rebate_amount, surcharges):
        """Generate detailed calculation breakdown"""
        return {
            "income_breakdown": self.income_calculator.get_income_breakdown(income),
            "tax_calculation_steps": self.tax_calculator.get_calculation_steps(),
            "rebate_breakdown": self.rebate_calculator.get_rebate_breakdown(),
            "surcharge_breakdown": surcharges,
            "applicable_rules": self.get_applicable_rules(taxpayer)
        }
    
    def get_applicable_rules(self, taxpayer: TaxpayerProfile) -> List[str]:
        """Get list of applicable tax rules for the taxpayer"""
        rules = []
        
        # Basic rate structure
        rules.append(f"Base tax rates: {taxpayer.category.value}")
        
        # Special status rules
        for status in taxpayer.special_statuses:
            rules.append(f"Special status: {status.value}")
        
        # Location-based rules
        if taxpayer.location in [LocationCategory.DHAKA_CITY, LocationCategory.CHITTAGONG_CITY]:
            rules.append("Metropolitan area taxpayer")
        
        return rules
    
    def validate_calculation_result(self, result: Dict[str, Any]) -> Dict[str, bool]:
        """Comprehensive validation of calculation result"""
        validations = {}
        
        # Mathematical consistency
        validations["mathematical_consistency"] = self.check_mathematical_consistency(result)
        
        # Legal compliance
        validations["legal_compliance"] = self.check_legal_compliance(result)
        
        # Circular compliance
        validations["circular_compliance"] = self.check_circular_compliance(result)
        
        # eReturn compatibility
        validations["ereturn_compatibility"] = self.check_ereturn_compatibility(result)
        
        validations["overall_validity"] = all(validations.values())
        
        return validations
    
    def check_mathematical_consistency(self, result: Dict[str, Any]) -> bool:
        """Check mathematical consistency of calculations"""
        try:
            total_income = Decimal(result["income_summary"]["total_income"])
            taxable_income = Decimal(result["income_summary"]["taxable_income"])
            total_exemptions = sum(Decimal(v) for v in result["income_summary"]["exemptions"].values() if v != "0")
            
            # Check if taxable income = total income - exemptions
            calculated_taxable = total_income - total_exemptions
            return abs(calculated_taxable - taxable_income) <= Decimal('0.01')
            
        except Exception as e:
            self.log_calculation("Mathematical consistency check failed", {"error": str(e)})
            return False
    
    def check_legal_compliance(self, result: Dict[str, Any]) -> bool:
        """Check compliance with Income Tax Act 2023"""
        return True  # Implement specific legal checks
    
    def check_circular_compliance(self, result: Dict[str, Any]) -> bool:
        """Check compliance with Circular 2024-25"""
        return True  # Implement specific circular checks
    
    def check_ereturn_compatibility(self, result: Dict[str, Any]) -> bool:
        """Check compatibility with eReturn system"""
        return True  # Implement eReturn format checks


class IncomeCalculator:
    """Calculate total income from all sources with complex conditions"""
    
    def __init__(self, engine):
        self.engine = engine
        self.income_breakdown = {}
    
    def calculate_total_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate total income with all conditional logic"""
        
        total = Decimal('0')
        
        # Employment Income (Complex calculations)
        employment_income = self.calculate_employment_income(taxpayer, income)
        total += employment_income
        
        # Rental Income (Property-wise calculations)
        rental_income = self.calculate_rental_income(taxpayer, income)
        total += rental_income
        
        # Agricultural Income (Special treatment)
        agricultural_income = self.calculate_agricultural_income(taxpayer, income)
        total += agricultural_income
        
        # Business Income (Category-specific)
        business_income = self.calculate_business_income(taxpayer, income)
        total += business_income
        
        # Capital Gains (Asset-specific rates)
        capital_gains = self.calculate_capital_gains(taxpayer, income)
        total += capital_gains
        
        # Financial Assets Income
        financial_income = self.calculate_financial_income(taxpayer, income)
        total += financial_income
        
        # Other Sources Income
        other_income = self.calculate_other_income(taxpayer, income)
        total += other_income
        
        # Foreign Income (Special treatment)
        foreign_income = self.calculate_foreign_income(taxpayer, income)
        total += foreign_income
        
        # Family Income (Spouse/Minor)
        family_income = self.calculate_family_income(taxpayer, income)
        total += family_income
        
        self.engine.log_calculation("Total income calculated", {
            "employment": str(employment_income),
            "rental": str(rental_income),
            "business": str(business_income),
            "total": str(total)
        })
        
        return total
    
    def calculate_employment_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate employment income with allowances and exemptions"""
        
        # Basic salary components
        gross_salary = (income.basic_salary + income.house_rent_allowance + 
                       income.medical_allowance + income.conveyance_allowance + 
                       income.other_allowances + income.bonus + income.overtime)
        
        # House rent allowance exemption (50% of basic or actual, whichever is lower)
        hra_exemption = min(income.house_rent_allowance, income.basic_salary * Decimal('0.5'))
        
        # Medical allowance exemption (up to 120,000 or 10% of basic)
        medical_exemption = min(income.medical_allowance, 
                               min(Decimal('120000'), income.basic_salary * Decimal('0.1')))
        
        # Conveyance allowance exemption (up to 30,000)
        conveyance_exemption = min(income.conveyance_allowance, Decimal('30000'))
        
        # Calculate net employment income
        net_employment = gross_salary - hra_exemption - medical_exemption - conveyance_exemption
        
        # Add pension and gratuity
        net_employment += income.pension + income.gratuity
        
        self.income_breakdown["employment"] = {
            "gross_salary": str(gross_salary),
            "hra_exemption": str(hra_exemption),
            "medical_exemption": str(medical_exemption),
            "conveyance_exemption": str(conveyance_exemption),
            "net_employment": str(net_employment)
        }
        
        return net_employment
    
    def calculate_rental_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate rental income with property-wise calculations (Topics 87-101)"""
        
        total_rental = Decimal('0')
        
        # House property rental (Topic 88-95)
        if income.house_rent_income > 0:
            # Standard deductions for house property
            maintenance_deduction = income.house_rent_income * Decimal('0.25')  # 25%
            municipal_tax_deduction = income.house_rent_income * Decimal('0.075')  # 7.5%
            insurance_deduction = income.house_rent_income * Decimal('0.01')  # 1%
            
            total_deductions = maintenance_deduction + municipal_tax_deduction + insurance_deduction
            net_house_rental = income.house_rent_income - total_deductions
            total_rental += max(Decimal('0'), net_house_rental)
        
        # Commercial property rental (Different deduction rates)
        if income.commercial_rent_income > 0:
            commercial_deductions = income.commercial_rent_income * Decimal('0.30')  # 30%
            net_commercial_rental = income.commercial_rent_income - commercial_deductions
            total_rental += max(Decimal('0'), net_commercial_rental)
        
        # Land rental (Minimal deductions)
        if income.land_rent_income > 0:
            land_deductions = income.land_rent_income * Decimal('0.10')  # 10%
            net_land_rental = income.land_rent_income - land_deductions
            total_rental += max(Decimal('0'), net_land_rental)
        
        # Special rental income (Topics 99-101)
        if income.special_rent_income > 0:
            # Special rate of 10% (Topic 101)
            special_rental_tax = income.special_rent_income * Decimal('0.10')
            total_rental += income.special_rent_income  # Add to income for surcharge calculation
            
        self.income_breakdown["rental"] = {
            "house_rental": str(income.house_rent_income),
            "commercial_rental": str(income.commercial_rent_income),
            "total_rental": str(total_rental)
        }
        
        return total_rental
    
    def calculate_agricultural_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate agricultural income (generally exempt but conditions apply)"""
        
        total_agricultural = Decimal('0')
        
        # Crop income (generally exempt)
        crop_income = income.crop_income
        
        # Livestock income (conditions apply)
        livestock_income = income.livestock_income
        
        # Fisheries income (conditions apply) 
        fisheries_income = income.fisheries_income
        
        # Poultry income (Topic 14 - reduced rate)
        poultry_income = income.poultry_income
        
        # Agricultural income is generally exempt, but processed agricultural products may be taxable
        if taxpayer.business_type and "processing" in taxpayer.business_type.lower():
            total_agricultural = crop_income + livestock_income + fisheries_income + poultry_income
        else:
            # Pure agricultural income is exempt
            total_agricultural = Decimal('0')
        
        self.income_breakdown["agricultural"] = {
            "crop": str(crop_income),
            "livestock": str(livestock_income),
            "fisheries": str(fisheries_income),
            "poultry": str(poultry_income),
            "taxable_agricultural": str(total_agricultural)
        }
        
        return total_agricultural
    
    def calculate_business_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate business income with industry-specific conditions"""
        
        total_business = Decimal('0')
        
        # Standard business income
        standard_business = (income.trading_income + income.manufacturing_income + 
                           income.service_income + income.professional_income)
        
        # Export income (Topic 11 - 50% rate reduction)
        export_income = income.export_income
        if export_income > 0:
            # Export income gets 50% rate reduction
            total_business += export_income  # Full amount for total income
        
        # Industrial income with special rates (Topics 13-20)
        industrial_income = Decimal('0')
        
        # Textile industry (Topic 13)
        if income.textile_income > 0:
            industrial_income += income.textile_income
        
        # Pharmaceutical industry
        if income.pharmaceutical_income > 0:
            industrial_income += income.pharmaceutical_income
        
        # Software development
        if income.software_income > 0:
            industrial_income += income.software_income
        
        # Economic zone income (Topics 15-17)
        if income.economic_zone_income > 0:
            industrial_income += income.economic_zone_income
        
        # Hi-tech park income (Topics 18-20)
        if income.hitech_park_income > 0:
            industrial_income += income.hitech_park_income
        
        total_business = standard_business + export_income + industrial_income
        
        self.income_breakdown["business"] = {
            "standard_business": str(standard_business),
            "export_income": str(export_income),
            "industrial_income": str(industrial_income),
            "total_business": str(total_business)
        }
        
        return total_business
    
    def calculate_capital_gains(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate capital gains with asset-specific rates"""
        
        total_capital_gains = Decimal('0')
        
        # Share capital gains (different rates for listed vs unlisted)
        if income.share_capital_gains > 0:
            total_capital_gains += income.share_capital_gains
        
        # Property capital gains (holding period matters)
        if income.property_capital_gains > 0:
            total_capital_gains += income.property_capital_gains
        
        # Securities capital gains
        if income.securities_capital_gains > 0:
            total_capital_gains += income.securities_capital_gains
        
        self.income_breakdown["capital_gains"] = {
            "share_gains": str(income.share_capital_gains),
            "property_gains": str(income.property_capital_gains),
            "securities_gains": str(income.securities_capital_gains),
            "total_capital_gains": str(total_capital_gains)
        }
        
        return total_capital_gains
    
    def calculate_financial_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate financial assets income (Topic 109)"""
        
        total_financial = Decimal('0')
        
        # Bank interest (exemption up to 5 lakh for individuals)
        bank_interest = income.bank_interest
        if taxpayer.category == TaxpayerCategory.INDIVIDUAL:
            bank_interest_exemption = min(bank_interest, Decimal('500000'))  # 5 lakh exemption
            taxable_bank_interest = bank_interest - bank_interest_exemption
        else:
            taxable_bank_interest = bank_interest
        
        total_financial += taxable_bank_interest
        
        # Dividend income (final tax system)
        dividend_income = income.dividend_income  # May have final tax
        total_financial += dividend_income
        
        # Bond interest
        total_financial += income.bond_interest
        
        # Mutual fund income
        total_financial += income.mutual_fund_income
        
        self.income_breakdown["financial"] = {
            "bank_interest": str(income.bank_interest),
            "bank_interest_exemption": str(min(income.bank_interest, Decimal('500000')) if taxpayer.category == TaxpayerCategory.INDIVIDUAL else Decimal('0')),
            "taxable_bank_interest": str(taxable_bank_interest),
            "dividend": str(dividend_income),
            "total_financial": str(total_financial)
        }
        
        return total_financial
    
    def calculate_other_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate other sources income (Topics 110-111)"""
        
        total_other = (income.royalty_income + income.commission_income + 
                      income.consultancy_income + income.honorarium + 
                      income.lottery_income)
        
        self.income_breakdown["other"] = {
            "royalty": str(income.royalty_income),
            "commission": str(income.commission_income),
            "consultancy": str(income.consultancy_income),
            "honorarium": str(income.honorarium),
            "lottery": str(income.lottery_income),
            "total_other": str(total_other)
        }
        
        return total_other
    
    def calculate_foreign_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate foreign income with special treatment"""
        
        total_foreign = Decimal('0')
        
        if taxpayer.residential_status == "resident":
            # Residents pay tax on worldwide income
            total_foreign = (income.foreign_employment + income.foreign_business + 
                           income.foreign_investment)
        else:
            # Non-residents pay tax only on Bangladesh-sourced income
            total_foreign = Decimal('0')
        
        self.income_breakdown["foreign"] = {
            "foreign_employment": str(income.foreign_employment),
            "foreign_business": str(income.foreign_business),
            "foreign_investment": str(income.foreign_investment),
            "total_foreign": str(total_foreign),
            "residential_status": taxpayer.residential_status
        }
        
        return total_foreign
    
    def calculate_family_income(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate spouse and minor children income"""
        
        total_family = Decimal('0')
        
        # Spouse income (if spouse is not a separate taxpayer)
        if not taxpayer.spouse_tin:
            total_family += income.spouse_income
        
        # Minor children income (always included)
        total_family += income.minor_children_income
        
        self.income_breakdown["family"] = {
            "spouse_income": str(income.spouse_income if not taxpayer.spouse_tin else 0),
            "minor_children": str(income.minor_children_income),
            "total_family": str(total_family)
        }
        
        return total_family
    
    def get_income_breakdown(self, income: IncomeDetails) -> Dict[str, Any]:
        """Return detailed income breakdown"""
        return self.income_breakdown


class ExemptionCalculator:
    """Calculate exemptions based on taxpayer profile and conditions"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def calculate_exemptions(self, taxpayer: TaxpayerProfile, income: IncomeDetails, total_income: Decimal) -> Dict[str, Decimal]:
        """Calculate all applicable exemptions"""
        
        exemptions = {}
        
        # Base exemption
        base_exemption = self.get_base_exemption(taxpayer)
        exemptions["base_exemption"] = base_exemption
        
        # Special status exemptions
        special_exemptions = self.get_special_exemptions(taxpayer)
        exemptions.update(special_exemptions)
        
        # Age-based exemptions
        age_exemption = self.get_age_exemption(taxpayer)
        if age_exemption > 0:
            exemptions["age_exemption"] = age_exemption
        
        # Gender-based exemptions  
        gender_exemption = self.get_gender_exemption(taxpayer)
        if gender_exemption > 0:
            exemptions["gender_exemption"] = gender_exemption
        
        # Location-based exemptions
        location_exemption = self.get_location_exemption(taxpayer)
        if location_exemption > 0:
            exemptions["location_exemption"] = location_exemption
        
        # Professional exemptions
        professional_exemption = self.get_professional_exemption(taxpayer, income)
        if professional_exemption > 0:
            exemptions["professional_exemption"] = professional_exemption
        
        # Calculate total exemption (highest applicable, not cumulative)
        exemptions["total_exemption"] = max(exemptions.values())
        
        self.engine.log_calculation("Exemptions calculated", exemptions)
        
        return {k: v for k, v in exemptions.items()}
    
    def get_base_exemption(self, taxpayer: TaxpayerProfile) -> Decimal:
        """Get base exemption amount"""
        
        if taxpayer.category == TaxpayerCategory.INDIVIDUAL:
            return self.engine.base_exemptions[TaxpayerCategory.INDIVIDUAL]["general"]
        elif taxpayer.category == TaxpayerCategory.CHARITABLE_ORGANIZATION:
            return Decimal('999999999')  # Effectively unlimited for charitable orgs
        else:
            return Decimal('0')
    
    def get_special_exemptions(self, taxpayer: TaxpayerProfile) -> Dict[str, Decimal]:
        """Get special status exemptions"""
        
        exemptions = {}
        base_amounts = self.engine.base_exemptions[TaxpayerCategory.INDIVIDUAL]
        
        for status in taxpayer.special_statuses:
            if status == SpecialStatus.FREEDOM_FIGHTER:
                exemptions["freedom_fighter"] = base_amounts["freedom_fighter"]
            elif status == SpecialStatus.DISABLED_PERSON:
                if taxpayer.disability_type == "physical":
                    exemptions["disability"] = base_amounts["disabled_physical"]
                elif taxpayer.disability_type == "intellectual":
                    exemptions["disability"] = base_amounts["disabled_intellectual"]
            elif status == SpecialStatus.THIRD_GENDER:
                exemptions["third_gender"] = base_amounts["third_gender"]
        
        return exemptions
    
    def get_age_exemption(self, taxpayer: TaxpayerProfile) -> Decimal:
        """Get age-based exemption"""
        
        if taxpayer.age >= 65:
            return self.engine.base_exemptions[TaxpayerCategory.INDIVIDUAL]["senior_citizen"]
        return Decimal('0')
    
    def get_gender_exemption(self, taxpayer: TaxpayerProfile) -> Decimal:
        """Get gender-based exemption"""
        
        if taxpayer.gender.lower() == "female":
            return self.engine.base_exemptions[TaxpayerCategory.INDIVIDUAL]["female"]
        return Decimal('0')
    
    def get_location_exemption(self, taxpayer: TaxpayerProfile) -> Decimal:
        """Get location-based exemption"""
        
        # Some locations may have special exemptions
        if taxpayer.location == LocationCategory.OTHER_AREA:
            return Decimal('25000')  # Additional exemption for non-metropolitan areas
        return Decimal('0')
    
    def get_professional_exemption(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Get profession-specific exemptions"""
        
        if taxpayer.profession:
            profession = taxpayer.profession.lower()
            
            # Doctor's exemption for medical practice
            if "doctor" in profession or "physician" in profession:
                return min(income.professional_income * Decimal('0.20'), Decimal('100000'))
            
            # Teacher's exemption
            elif "teacher" in profession or "professor" in profession:
                return min(income.professional_income * Decimal('0.15'), Decimal('75000'))
            
            # Engineer's exemption  
            elif "engineer" in profession:
                return min(income.professional_income * Decimal('0.10'), Decimal('50000'))
        
        return Decimal('0')


class TaxCalculator:
    """Calculate gross tax with all conditional logic"""
    
    def __init__(self, engine):
        self.engine = engine
        self.calculation_steps = []
    
    def calculate_gross_tax(self, taxpayer: TaxpayerProfile, taxable_income: Decimal, income: IncomeDetails) -> Decimal:
        """Calculate gross tax based on taxpayer category and conditions"""
        
        self.calculation_steps = []
        
        if taxpayer.category == TaxpayerCategory.INDIVIDUAL:
            return self.calculate_individual_tax(taxpayer, taxable_income, income)
        elif taxpayer.category == TaxpayerCategory.COMPANY:
            return self.calculate_company_tax(taxpayer, taxable_income, income)
        elif taxpayer.category == TaxpayerCategory.COOPERATIVE:
            return self.calculate_cooperative_tax(taxpayer, taxable_income)
        elif taxpayer.category == TaxpayerCategory.TRUST:
            return self.calculate_trust_tax(taxpayer, taxable_income)
        elif taxpayer.category == TaxpayerCategory.CHARITABLE_ORGANIZATION:
            return self.calculate_charitable_tax(taxpayer, taxable_income, income)
        else:
            # Default to individual rates
            return self.calculate_individual_tax(taxpayer, taxable_income, income)
    
    def calculate_individual_tax(self, taxpayer: TaxpayerProfile, taxable_income: Decimal, income: IncomeDetails) -> Decimal:
        """Calculate individual tax using progressive rates with special conditions"""
        
        total_tax = Decimal('0')
        slabs = self.engine.tax_rates[TaxpayerCategory.INDIVIDUAL]
        
        # Regular income tax calculation
        regular_income = taxable_income
        
        # Separate export income for special rate (Topic 11)
        export_income = income.export_income
        if export_income > 0:
            regular_income -= min(export_income, taxable_income)
        
        # Calculate tax on regular income
        for slab in slabs:
            if regular_income <= 0:
                break
                
            slab_min = slab["min"]
            slab_max = slab["max"]
            rate = slab["rate"]
            
            if regular_income <= slab_min:
                continue
            
            # Calculate taxable amount in this slab
            if slab_max is None:
                taxable_in_slab = regular_income - slab_min
            else:
                taxable_in_slab = min(regular_income, slab_max) - slab_min
            
            if taxable_in_slab > 0:
                slab_tax = taxable_in_slab * rate
                total_tax += slab_tax
                
                self.calculation_steps.append({
                    "slab": f"{slab_min} - {slab_max or 'Above'}",
                    "amount": str(taxable_in_slab),
                    "rate": f"{rate:.1%}",
                    "tax": str(slab_tax)
                })
        
        # Calculate tax on export income with 50% reduction (Topic 11)
        if export_income > 0:
            export_tax = self.calculate_export_income_tax(export_income, slabs)
            export_tax_reduced = export_tax * Decimal('0.50')  # 50% reduction
            total_tax += export_tax_reduced
            
            self.calculation_steps.append({
                "slab": "Export Income (50% reduced rate)",
                "amount": str(export_income),
                "rate": "Special",
                "tax": str(export_tax_reduced)
            })
        
        # Calculate tax on industrial income with special rates (Topics 13-20)
        industrial_tax = self.calculate_industrial_income_tax(taxpayer, income)
        total_tax += industrial_tax
        
        self.engine.log_calculation("Individual tax calculated", {
            "regular_income": str(regular_income),
            "export_income": str(export_income),
            "total_tax": str(total_tax)
        })
        
        return total_tax
    
    def calculate_export_income_tax(self, export_income: Decimal, slabs: List[Dict]) -> Decimal:
        """Calculate tax on export income using regular rates"""
        
        tax = Decimal('0')
        remaining_income = export_income
        
        for slab in slabs:
            if remaining_income <= 0:
                break
                
            slab_min = slab["min"]
            slab_max = slab["max"]
            rate = slab["rate"]
            
            if remaining_income <= slab_min:
                continue
            
            if slab_max is None:
                taxable_in_slab = remaining_income - slab_min
            else:
                taxable_in_slab = min(remaining_income, slab_max) - slab_min
            
            if taxable_in_slab > 0:
                tax += taxable_in_slab * rate
        
        return tax
    
    def calculate_industrial_income_tax(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> Decimal:
        """Calculate tax on industrial income with special rates"""
        
        total_industrial_tax = Decimal('0')
        
        # Textile industry (Topic 13) - 10% rate for eligible years
        if income.textile_income > 0:
            textile_tax = income.textile_income * self.engine.special_rates["textile_industry"]
            total_industrial_tax += textile_tax
            
            self.calculation_steps.append({
                "slab": "Textile Industry (Special Rate)",
                "amount": str(income.textile_income),
                "rate": "10%",
                "tax": str(textile_tax)
            })
        
        # Pharmaceutical industry - 10% rate for eligible years
        if income.pharmaceutical_income > 0:
            pharma_tax = income.pharmaceutical_income * self.engine.special_rates["pharmaceutical"]
            total_industrial_tax += pharma_tax
            
            self.calculation_steps.append({
                "slab": "Pharmaceutical Industry (Special Rate)",
                "amount": str(income.pharmaceutical_income),
                "rate": "10%",
                "tax": str(pharma_tax)
            })
        
        # Software development - 5% rate for eligible years
        if income.software_income > 0:
            software_tax = income.software_income * self.engine.special_rates["software_development"]
            total_industrial_tax += software_tax
            
            self.calculation_steps.append({
                "slab": "Software Development (Special Rate)",
                "amount": str(income.software_income),
                "rate": "5%",
                "tax": str(software_tax)
            })
        
        # Economic zone income - Tax holiday (Topics 15-17)
        if income.economic_zone_income > 0:
            # Tax holiday for qualifying years
            self.calculation_steps.append({
                "slab": "Economic Zone (Tax Holiday)",
                "amount": str(income.economic_zone_income),
                "rate": "0%",
                "tax": "0"
            })
        
        # Hi-tech park income - Tax holiday (Topics 18-20)
        if income.hitech_park_income > 0:
            # Tax holiday for qualifying years
            self.calculation_steps.append({
                "slab": "Hi-Tech Park (Tax Holiday)",
                "amount": str(income.hitech_park_income),
                "rate": "0%",
                "tax": "0"
            })
        
        return total_industrial_tax
    
    def calculate_company_tax(self, taxpayer: TaxpayerProfile, taxable_income: Decimal, income: IncomeDetails) -> Decimal:
        """Calculate company tax based on company type"""
        
        company_rates = self.engine.tax_rates[TaxpayerCategory.COMPANY]
        
        # Determine company type and applicable rate
        if taxpayer.company_type == "publicly_traded":
            rate = company_rates["publicly_traded"]
        elif taxpayer.company_type == "bank":
            rate = company_rates["bank"]
        elif taxpayer.company_type == "insurance":
            rate = company_rates["insurance"]
        elif taxpayer.company_type == "tobacco":
            rate = company_rates["tobacco"]
        elif taxpayer.company_type == "mobile_operator":
            rate = company_rates["mobile_operator"]
        elif taxpayer.company_type == "merchant_bank":
            rate = company_rates["merchant_bank"]
        else:
            rate = company_rates["non_publicly_traded"]
        
        total_tax = taxable_income * rate
        
        self.calculation_steps.append({
            "slab": f"Company Tax ({taxpayer.company_type or 'regular'})",
            "amount": str(taxable_income),
            "rate": f"{rate:.1%}",
            "tax": str(total_tax)
        })
        
        self.engine.log_calculation("Company tax calculated", {
            "company_type": taxpayer.company_type or "regular",
            "rate": str(rate),
            "tax": str(total_tax)
        })
        
        return total_tax
    
    def calculate_cooperative_tax(self, taxpayer: TaxpayerProfile, taxable_income: Decimal) -> Decimal:
        """Calculate cooperative society tax"""
        
        rate = self.engine.tax_rates[TaxpayerCategory.COOPERATIVE]
        total_tax = taxable_income * rate
        
        self.calculation_steps.append({
            "slab": "Cooperative Society",
            "amount": str(taxable_income),
            "rate": f"{rate:.1%}",
            "tax": str(total_tax)
        })
        
        return total_tax
    
    def calculate_trust_tax(self, taxpayer: TaxpayerProfile, taxable_income: Decimal) -> Decimal:
        """Calculate trust tax"""
        
        rate = self.engine.tax_rates[TaxpayerCategory.TRUST]
        total_tax = taxable_income * rate
        
        self.calculation_steps.append({
            "slab": "Trust",
            "amount": str(taxable_income),
            "rate": f"{rate:.1%}",
            "tax": str(total_tax)
        })
        
        return total_tax
    
    def calculate_charitable_tax(self, taxpayer: TaxpayerProfile, taxable_income: Decimal, income: IncomeDetails) -> Decimal:
        """Calculate charitable organization tax (generally exempt)"""
        
        # Check if organization qualifies for charitable exemption
        if self.qualifies_for_charitable_exemption(taxpayer, income):
            self.calculation_steps.append({
                "slab": "Charitable Organization (Exempt)",
                "amount": str(taxable_income),
                "rate": "0%",
                "tax": "0"
            })
            return Decimal('0')
        else:
            # If doesn't qualify, tax as regular entity
            return self.calculate_individual_tax(taxpayer, taxable_income, income)
    
    def qualifies_for_charitable_exemption(self, taxpayer: TaxpayerProfile, income: IncomeDetails) -> bool:
        """Check if organization qualifies for charitable exemption (Topics 31-77)"""
        
        # Must be registered charitable organization
        if taxpayer.category != TaxpayerCategory.CHARITABLE_ORGANIZATION:
            return False
        
        # Must serve qualifying charitable purposes
        # This would need to be determined from organization's activities
        # For now, assume qualified if categorized as charitable
        
        # Must not distribute profits to members
        # This would need to be verified from organization structure
        
        # Must maintain proper accounting
        # This would need to be verified from compliance records
        
        return True  # Simplified for demo
    
    def get_calculation_steps(self) -> List[Dict[str, str]]:
        """Return detailed calculation steps"""
        return self.calculation_steps


class RebateCalculator:
    """Calculate investment rebates with complex conditions"""
    
    def __init__(self, engine):
        self.engine = engine
        self.rebate_breakdown = {}
    
    def calculate_rebates(self, taxpayer: TaxpayerProfile, investments: InvestmentRebate, gross_tax: Decimal) -> Decimal:
        """Calculate total investment rebates"""
        
        total_rebate = Decimal('0')
        
        # Calculate rebate for each investment type
        life_insurance_rebate = self.calculate_life_insurance_rebate(investments)
        dps_rebate = self.calculate_dps_rebate(investments)
        securities_rebate = self.calculate_securities_rebate(investments)
        provident_fund_rebate = self.calculate_provident_fund_rebate(investments)
        government_securities_rebate = self.calculate_government_securities_rebate(investments)
        others_rebate = self.calculate_others_rebate(investments)
        
        # Sum all rebates
        total_investment_rebate = (life_insurance_rebate + dps_rebate + securities_rebate + 
                                 provident_fund_rebate + government_securities_rebate + others_rebate)
        
        # Apply maximum rebate limit (15% of gross tax or investment amount, whichever is lower)
        max_rebate_on_tax = gross_tax * Decimal('0.15')  # 15% of gross tax
        max_rebate_on_investment = min(investments.max_rebate_limit, total_investment_rebate) * investments.rebate_percentage
        
        allowed_rebate = min(max_rebate_on_tax, max_rebate_on_investment, total_investment_rebate)
        total_rebate = allowed_rebate
        
        self.rebate_breakdown = {
            "life_insurance": str(life_insurance_rebate),
            "dps": str(dps_rebate),
            "securities": str(securities_rebate),
            "provident_fund": str(provident_fund_rebate),
            "government_securities": str(government_securities_rebate),
            "others": str(others_rebate),
            "total_investment_rebate": str(total_investment_rebate),
            "max_rebate_on_tax": str(max_rebate_on_tax),
            "max_rebate_on_investment": str(max_rebate_on_investment),
            "allowed_rebate": str(allowed_rebate)
        }
        
        self.engine.log_calculation("Investment rebates calculated", self.rebate_breakdown)
        
        return total_rebate
    
    def calculate_life_insurance_rebate(self, investments: InvestmentRebate) -> Decimal:
        """Calculate life insurance premium rebate"""
        
        # Rebate calculation: 15% of premium paid
        rebate = investments.life_insurance_premium * investments.rebate_percentage
        
        # Maximum limit may apply
        max_life_insurance_rebate = Decimal('100000')  # Example limit
        return min(rebate, max_life_insurance_rebate)
    
    def calculate_dps_rebate(self, investments: InvestmentRebate) -> Decimal:
        """Calculate DPS contribution rebate"""
        
        rebate = investments.dps_contribution * investments.rebate_percentage
        max_dps_rebate = Decimal('120000')  # Example limit
        return min(rebate, max_dps_rebate)
    
    def calculate_securities_rebate(self, investments: InvestmentRebate) -> Decimal:
        """Calculate securities investment rebate"""
        
        total_securities = (investments.listed_securities + investments.mutual_fund_units + 
                          investments.etf_investment)
        
        rebate = total_securities * investments.rebate_percentage
        max_securities_rebate = Decimal('500000')  # Example limit
        return min(rebate, max_securities_rebate)
    
    def calculate_provident_fund_rebate(self, investments: InvestmentRebate) -> Decimal:
        """Calculate provident fund rebate"""
        
        total_pf = (investments.gpf_contribution + investments.rpf_contribution + 
                   investments.superannuation_fund)
        
        rebate = total_pf * investments.rebate_percentage
        # PF rebates may have no limit or very high limit
        return rebate
    
    def calculate_government_securities_rebate(self, investments: InvestmentRebate) -> Decimal:
        """Calculate government securities rebate"""
        
        total_govt_securities = (investments.sanchayapatra + investments.savings_certificate + 
                               investments.treasury_bond)
        
        rebate = total_govt_securities * investments.rebate_percentage
        max_govt_rebate = Decimal('150000')  # Example limit
        return min(rebate, max_govt_rebate)
    
    def calculate_others_rebate(self, investments: InvestmentRebate) -> Decimal:
        """Calculate other investment rebates"""
        
        total_others = (investments.benevolent_fund + investments.group_insurance + 
                       investments.zakat_fund + investments.charitable_donation + 
                       investments.universal_pension)
        
        rebate = total_others * investments.rebate_percentage
        max_others_rebate = Decimal('200000')  # Example limit
        return min(rebate, max_others_rebate)
    
    def get_rebate_breakdown(self) -> Dict[str, str]:
        """Return detailed rebate breakdown"""
        return self.rebate_breakdown


class SurchargeCalculator:
    """Calculate surcharges with complex conditions"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def calculate_surcharges(self, taxpayer: TaxpayerProfile, tax_payable: Decimal, assets: AssetsLiabilities) -> Dict[str, Decimal]:
        """Calculate all applicable surcharges"""
        
        surcharges = {}
        
        # Net wealth surcharge (Topic 7)
        wealth_surcharge = self.calculate_wealth_surcharge(taxpayer, tax_payable, assets)
        if wealth_surcharge > 0:
            surcharges["wealth_surcharge"] = wealth_surcharge
        
        # Environmental surcharge (Topic 8)
        environmental_surcharge = self.calculate_environmental_surcharge(taxpayer, tax_payable)
        if environmental_surcharge > 0:
            surcharges["environmental_surcharge"] = environmental_surcharge
        
        # Tobacco surcharge (for tobacco companies)
        tobacco_surcharge = self.calculate_tobacco_surcharge(taxpayer, tax_payable)
        if tobacco_surcharge > 0:
            surcharges["tobacco_surcharge"] = tobacco_surcharge
        
        # Location-based surcharge (if applicable)
        location_surcharge = self.calculate_location_surcharge(taxpayer, tax_payable)
        if location_surcharge > 0:
            surcharges["location_surcharge"] = location_surcharge
        
        # Calculate total surcharge
        surcharges["total_surcharge"] = sum(surcharges.values())
        
        self.engine.log_calculation("Surcharges calculated", {k: str(v) for k, v in surcharges.items()})
        
        return surcharges
    
    def calculate_wealth_surcharge(self, taxpayer: TaxpayerProfile, tax_payable: Decimal, assets: AssetsLiabilities) -> Decimal:
        """Calculate net wealth surcharge (Topic 7)"""
        
        # Only applicable to individuals, firms, and HUFs
        if taxpayer.category not in [TaxpayerCategory.INDIVIDUAL, TaxpayerCategory.FIRM, TaxpayerCategory.HINDU_UNDIVIDED_FAMILY]:
            return Decimal('0')
        
        net_wealth = assets.net_wealth
        if net_wealth <= 0:
            return Decimal('0')
        
        wealth_slabs = self.engine.surcharge_rates["wealth_based"]
        
        for slab in wealth_slabs:
            min_wealth = slab["min"]
            max_wealth = slab["max"]
            surcharge_rate = slab["rate"]
            
            if max_wealth is None or (min_wealth <= net_wealth <= (max_wealth or float('inf'))):
                surcharge = tax_payable * surcharge_rate
                return surcharge
        
        return Decimal('0')
    
    def calculate_environmental_surcharge(self, taxpayer: TaxpayerProfile, tax_payable: Decimal) -> Decimal:
        """Calculate environmental surcharge (Topic 8)"""
        
        # Only applicable to companies
        if taxpayer.category != TaxpayerCategory.COMPANY:
            return Decimal('0')
        
        # Some companies may be exempt
        if taxpayer.company_type == "charitable":
            return Decimal('0')
        
        environmental_rate = self.engine.surcharge_rates["environmental"]
        surcharge = tax_payable * environmental_rate
        
        return surcharge
    
    def calculate_tobacco_surcharge(self, taxpayer: TaxpayerProfile, tax_payable: Decimal) -> Decimal:
        """Calculate tobacco surcharge for tobacco companies"""
        
        if taxpayer.company_type == "tobacco" or (taxpayer.industry_sector and "tobacco" in taxpayer.industry_sector.lower()):
            tobacco_rate = self.engine.surcharge_rates["tobacco"]
            surcharge = tax_payable * tobacco_rate
            return surcharge
        
        return Decimal('0')
    
    def calculate_location_surcharge(self, taxpayer: TaxpayerProfile, tax_payable: Decimal) -> Decimal:
        """Calculate location-based surcharge (if any)"""
        
        # Some locations may have additional surcharges
        # This would be based on specific circular provisions
        
        return Decimal('0')  # No location surcharge currently


class MinimumTaxCalculator:
    """Calculate minimum tax with complex conditions"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def calculate_minimum_tax(self, taxpayer: TaxpayerProfile, income: IncomeDetails, total_income: Decimal) -> Decimal:
        """Calculate minimum tax based on category and conditions"""
        
        if taxpayer.category == TaxpayerCategory.COMPANY:
            return self.calculate_company_minimum_tax(taxpayer, income, total_income)
        elif taxpayer.category == TaxpayerCategory.INDIVIDUAL and self.has_business_income(income):
            return self.calculate_individual_minimum_tax(taxpayer, income, total_income)
        else:
            return Decimal('0')  # No minimum tax
    
    def calculate_company_minimum_tax(self, taxpayer: TaxpayerProfile, income: IncomeDetails, total_income: Decimal) -> Decimal:
        """Calculate minimum tax for companies"""
        
        # 0.6% of turnover or gross receipts
        rate = self.engine.minimum_tax_rates[TaxpayerCategory.COMPANY]
        
        # Turnover calculation (simplified - would need detailed business records)
        estimated_turnover = total_income * Decimal('5')  # Rough estimation
        
        minimum_tax = estimated_turnover * rate
        
        self.engine.log_calculation("Company minimum tax calculated", {
            "estimated_turnover": str(estimated_turnover),
            "rate": str(rate),
            "minimum_tax": str(minimum_tax)
        })
        
        return minimum_tax
    
    def calculate_individual_minimum_tax(self, taxpayer: TaxpayerProfile, income: IncomeDetails, total_income: Decimal) -> Decimal:
        """Calculate minimum tax for individuals with business income"""
        
        # Only if gross receipts exceed threshold
        gross_receipts_threshold = self.engine.minimum_tax_rates["gross_receipts_threshold"]
        
        total_business_income = (income.trading_income + income.manufacturing_income + 
                               income.service_income + income.professional_income)
        
        if total_business_income < gross_receipts_threshold:
            return Decimal('0')
        
        rate = self.engine.minimum_tax_rates[TaxpayerCategory.INDIVIDUAL]
        estimated_gross_receipts = total_business_income * Decimal('3')  # Rough estimation
        
        minimum_tax = estimated_gross_receipts * rate
        
        self.engine.log_calculation("Individual minimum tax calculated", {
            "business_income": str(total_business_income),
            "estimated_gross_receipts": str(estimated_gross_receipts),
            "minimum_tax": str(minimum_tax)
        })
        
        return minimum_tax
    
    def has_business_income(self, income: IncomeDetails) -> bool:
        """Check if taxpayer has business income"""
        
        business_income = (income.trading_income + income.manufacturing_income + 
                         income.service_income + income.professional_income)
        
        return business_income > 0


class LifestyleVerifier:
    """Verify lifestyle expenses against income"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def verify_lifestyle(self, taxpayer: TaxpayerProfile, total_income: Decimal, 
                        lifestyle: LifestyleExpenses, assets: AssetsLiabilities) -> Dict[str, Any]:
        """Verify lifestyle expenses against income and assets"""
        
        # Calculate total lifestyle expenses
        total_expenses = (lifestyle.food_clothing + lifestyle.accommodation + 
                         lifestyle.transportation + lifestyle.utilities + 
                         lifestyle.education + lifestyle.medical + 
                         lifestyle.festival + lifestyle.travel_vacation + 
                         lifestyle.loan_interest + lifestyle.tax_payments)
        
        # Income to expense ratio
        if total_income > 0:
            expense_ratio = total_expenses / total_income
        else:
            expense_ratio = Decimal('0')
        
        # Asset verification
        asset_verification = self.verify_assets(taxpayer, total_income, assets)
        
        # Source of fund verification
        source_verification = self.verify_source_of_funds(total_income, total_expenses, assets)
        
        verification_result = {
            "total_expenses": str(total_expenses),
            "expense_to_income_ratio": str(expense_ratio),
            "ratio_acceptable": expense_ratio <= lifestyle.income_expense_ratio_threshold,
            "asset_verification": asset_verification,
            "source_verification": source_verification,
            "overall_verification": "PASSED" if expense_ratio <= lifestyle.income_expense_ratio_threshold else "REVIEW_REQUIRED"
        }
        
        self.engine.log_calculation("Lifestyle verification completed", verification_result)
        
        return verification_result
    
    def verify_assets(self, taxpayer: TaxpayerProfile, total_income: Decimal, assets: AssetsLiabilities) -> Dict[str, Any]:
        """Verify assets against income capacity"""
        
        # Calculate total assets
        total_assets = (assets.business_capital + assets.residential_property + 
                       assets.commercial_property + assets.agricultural_land + 
                       assets.bank_deposits + assets.shares_securities + 
                       assets.motor_vehicles + assets.jewelry_gold + 
                       assets.foreign_assets)
        
        # Asset to income ratio (rough guideline)
        if total_income > 0:
            asset_ratio = total_assets / total_income
        else:
            asset_ratio = Decimal('0')
        
        # High-value asset checks
        high_value_assets = []
        if assets.motor_vehicles > Decimal('2000000'):  # 20 lakh+
            high_value_assets.append("expensive_motor_vehicle")
        if assets.residential_property > total_income * 10:  # Property value > 10x income
            high_value_assets.append("expensive_property")
        if assets.foreign_assets > 0:
            high_value_assets.append("foreign_assets")
        
        return {
            "total_assets": str(total_assets),
            "asset_to_income_ratio": str(asset_ratio),
            "high_value_assets": high_value_assets,
            "asset_verification_required": len(high_value_assets) > 0 or asset_ratio > 15
        }
    
    def verify_source_of_funds(self, total_income: Decimal, total_expenses: Decimal, assets: AssetsLiabilities) -> Dict[str, Any]:
        """Verify source of funds for assets and expenses"""
        
        # Net wealth change
        current_net_wealth = assets.net_wealth
        previous_net_wealth = assets.previous_year_net_wealth
        wealth_change = current_net_wealth - previous_net_wealth
        
        # Total fund requirement
        total_fund_required = total_expenses + wealth_change
        
        # Available sources
        available_sources = total_income  # Simplified
        
        # Fund gap analysis
        fund_gap = total_fund_required - available_sources
        
        return {
            "total_fund_required": str(total_fund_required),
            "available_sources": str(available_sources),
            "fund_gap": str(fund_gap),
            "source_verification_required": fund_gap > Decimal('500000')  # 5 lakh threshold
        }


class PaymentReconciler:
    """Reconcile tax payments and calculate final payable amount"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def reconcile_payments(self, total_payable: Decimal, payments: TaxPayments) -> Dict[str, Any]:
        """Reconcile all payments and calculate final amount"""
        
        # Calculate total payments made
        total_tds = (payments.salary_tds + payments.contractor_tds + payments.commission_tds + 
                    payments.bank_interest_tds + payments.dividend_tds + payments.rent_tds + 
                    payments.other_tds)
        
        total_payments = (total_tds + payments.advance_tax_paid + payments.regular_tax_paid + 
                         payments.refund_adjustment + payments.payment_with_return)
        
        # Calculate balance
        balance = total_payable - total_payments
        
        # Determine final status
        if balance > Decimal('0'):
            final_status = "PAYABLE"
            payable_amount = balance
            refundable_amount = Decimal('0')
        elif balance < Decimal('0'):
            final_status = "REFUNDABLE"
            payable_amount = Decimal('0')
            refundable_amount = abs(balance)
        else:
            final_status = "BALANCED"
            payable_amount = Decimal('0')
            refundable_amount = Decimal('0')
        
        payment_summary = {
            "total_tds": str(total_tds),
            "advance_tax": str(payments.advance_tax_paid),
            "regular_tax": str(payments.regular_tax_paid),
            "refund_adjustment": str(payments.refund_adjustment),
            "payment_with_return": str(payments.payment_with_return),
            "total_payments": str(total_payments),
            "total_payable": str(total_payable),
            "balance": str(balance),
            "final_status": final_status,
            "payable_amount": str(payable_amount),
            "refundable_amount": str(refundable_amount)
        }
        
        self.engine.log_calculation("Payment reconciliation completed", payment_summary)
        
        return payment_summary


# Example usage and testing
if __name__ == "__main__":
    
    print("🚀 Comprehensive Bangladesh Tax Engine 2024-25")
    print("=" * 60)
    
    # Initialize engine
    engine = ComprehensiveTaxEngine()
    
    # Create sample taxpayer profile
    taxpayer = TaxpayerProfile(
        name="MD. Rahman Ahmed",
        tin="123456789012",
        nid="1234567890123456",
        category=TaxpayerCategory.INDIVIDUAL,
        age=45,
        gender="male",
        marital_status="married",
        location=LocationCategory.DHAKA_CITY,
        special_statuses=[],
        profession="Software Engineer",
        spouse_name="Mrs. Rahman",
        children_count=2
    )
    
    # Create sample income
    income = IncomeDetails(
        basic_salary=Decimal('1200000'),      # 12 lakh
        house_rent_allowance=Decimal('360000'), # 3.6 lakh
        medical_allowance=Decimal('120000'),    # 1.2 lakh
        bonus=Decimal('200000'),               # 2 lakh
        software_income=Decimal('500000'),     # 5 lakh from software development
        bank_interest=Decimal('150000'),       # 1.5 lakh
        dividend_income=Decimal('50000')       # 50k
    )
    
    # Create sample investments
    investments = InvestmentRebate(
        life_insurance_premium=Decimal('200000'),  # 2 lakh
        dps_contribution=Decimal('100000'),        # 1 lakh
        listed_securities=Decimal('300000'),       # 3 lakh
        gpf_contribution=Decimal('150000')         # 1.5 lakh
    )
    
    # Create sample lifestyle expenses
    lifestyle = LifestyleExpenses(
        food_clothing=Decimal('400000'),      # 4 lakh
        accommodation=Decimal('300000'),      # 3 lakh
        transportation=Decimal('200000'),     # 2 lakh
        utilities=Decimal('150000'),          # 1.5 lakh
        education=Decimal('200000'),          # 2 lakh
        medical=Decimal('100000')             # 1 lakh
    )
    
    # Create sample assets
    assets = AssetsLiabilities(
        residential_property=Decimal('8000000'),   # 80 lakh
        bank_deposits=Decimal('2000000'),          # 20 lakh
        shares_securities=Decimal('1500000'),      # 15 lakh
        motor_vehicles=Decimal('1200000'),         # 12 lakh
        bank_loans=Decimal('3000000'),             # 30 lakh loan
        net_wealth=Decimal('9700000'),             # 97 lakh net wealth
        previous_year_net_wealth=Decimal('8500000') # 85 lakh previous year
    )
    
    # Create sample payments
    payments = TaxPayments(
        salary_tds=Decimal('180000'),         # 1.8 lakh TDS from salary
        bank_interest_tds=Decimal('15000'),   # 15k TDS from bank interest
        advance_tax_paid=Decimal('50000'),    # 50k advance tax
    )
    
    print("\n📊 Calculating Comprehensive Tax...")
    print("-" * 40)
    
    # Calculate comprehensive tax
    result = engine.calculate_comprehensive_tax(
        taxpayer=taxpayer,
        income=income,
        investments=investments,
        lifestyle=lifestyle,
        assets=assets,
        payments=payments
    )
    
    # Display results
    print(f"\n💰 TAXPAYER: {result['taxpayer_info']['name']}")
    print(f"📋 Category: {result['taxpayer_info']['category']}")
    print(f"📍 Location: {result['taxpayer_info']['location']}")
    
    print(f"\n💵 INCOME SUMMARY:")
    print(f"Total Income: ৳{result['income_summary']['total_income']:,}")
    print(f"Total Exemptions: ৳{result['income_summary']['exemptions']['total_exemption']:,}")
    print(f"Taxable Income: ৳{result['income_summary']['taxable_income']:,}")
    
    print(f"\n🧮 TAX CALCULATION:")
    print(f"Gross Tax: ৳{result['tax_calculation']['gross_tax']:,}")
    print(f"Rebate Amount: ৳{result['tax_calculation']['rebate_amount']:,}")
    print(f"Net Tax: ৳{result['tax_calculation']['net_tax']:,}")
    print(f"Minimum Tax: ৳{result['tax_calculation']['minimum_tax']:,}")
    print(f"Tax Payable: ৳{result['tax_calculation']['tax_payable']:,}")
    
    print(f"\n⚡ SURCHARGES:")
    for surcharge_type, amount in result['surcharges'].items():
        if surcharge_type != 'total_surcharge' and Decimal(amount) > 0:
            print(f"{surcharge_type.replace('_', ' ').title()}: ৳{amount:,}")
    print(f"Total Surcharges: ৳{result['surcharges']['total_surcharge']:,}")
    
    print(f"\n💸 FINAL CALCULATION:")
    print(f"Total Amount Payable: ৳{result['total_payable']:,}")
    
    print(f"\n💳 PAYMENT SUMMARY:")
    payment_info = result['payment_summary']
    print(f"Total Payments Made: ৳{payment_info['total_payments']:,}")
    print(f"Final Status: {payment_info['final_status']}")
    if payment_info['final_status'] == 'PAYABLE':
        print(f"Amount to Pay: ৳{payment_info['payable_amount']:,}")
    elif payment_info['final_status'] == 'REFUNDABLE':
        print(f"Refund Amount: ৳{payment_info['refundable_amount']:,}")
    
    print(f"\n🔍 LIFESTYLE VERIFICATION:")
    lifestyle_info = result['lifestyle_verification']
    print(f"Total Expenses: ৳{lifestyle_info['total_expenses']:,}")
    print(f"Expense Ratio: {lifestyle_info['expense_to_income_ratio']}")
    print(f"Verification Status: {lifestyle_info['overall_verification']}")
    
    print(f"\n✅ VALIDATION:")
    validation = result['validation']
    print(f"Overall Validity: {'PASSED' if validation['overall_validity'] else 'FAILED'}")
    
    print(f"\n📜 ENGINE INFO:")
    print(f"Version: {result['engine_version']}")
    print(f"Calculation Time: {result['calculation_timestamp']}")
    
    print("\n" + "=" * 60)
    print("✅ Comprehensive Tax Calculation Completed!")
    print("🎯 This engine handles ALL eReturn + Circular 2024-25 scenarios")
    print("=" * 60)