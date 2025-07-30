// Tax calculation types based on our comprehensive tax engine

export interface TaxpayerProfile {
  // Basic Information
  name: string
  nid: string
  tin?: string
  
  // Category and Classification
  category: TaxpayerCategory
  gender: Gender
  age: number
  
  // Special Status
  special_status: SpecialStatus[]
  
  // Contact Information
  phone?: string
  email?: string
  address?: string
  
  // Residential Status
  residential_status: ResidentialStatus
}

export interface IncomeData {
  // Employment Income
  employment: {
    basic_salary: number
    house_rent_allowance: number
    medical_allowance: number
    conveyance_allowance: number
    other_allowances: number
    bonus: number
    overtime: number
  }
  
  // Business Income
  business: {
    trading_income: number
    manufacturing_income: number
    service_income: number
    professional_income: number
  }
  
  // Property Income
  property: {
    house_rent: number
    commercial_rent: number
    land_rent: number
  }
  
  // Agriculture Income
  agriculture: {
    crops: number
    livestock: number
    fisheries: number
    poultry: number
  }
  
  // Capital Gains
  capital_gains: {
    securities: number
    property: number
    other_assets: number
  }
  
  // Financial Assets
  financial: {
    bank_interest: number
    dividends: number
    mutual_funds: number
    debentures: number
  }
  
  // Other Income
  other: {
    royalty: number
    technical_fees: number
    commission: number
    lottery_winnings: number
    gifts: number
  }
  
  // Export Income (special rates)
  export: {
    goods: number
    services: number
  }
  
  // Industrial Income
  industrial: {
    manufacturing: number
    processing: number
  }
  
  // Foreign Income
  foreign: {
    employment: number
    business: number
    investment: number
  }
}

export interface InvestmentData {
  // Life Insurance
  life_insurance: number
  
  // DPS (Deposit Pension Scheme)
  dps: number
  
  // Government Securities
  government_securities: number
  
  // Stock Market Investments
  stock_market: number
  
  // Mutual Funds
  mutual_funds: number
  
  // Provident Fund
  provident_fund: number
  
  // Superannuation Fund
  superannuation_fund: number
  
  // Benevolent Fund
  benevolent_fund: number
  
  // Zakat Fund
  zakat_fund: number
  
  // Universal Pension
  universal_pension: number
  
  // Other Approved Investments
  other_investments: number
  
  // Donation to Charitable Organizations
  donations: number
}

export interface AssetData {
  // Immovable Assets
  land_buildings: number
  agricultural_land: number
  
  // Financial Assets
  bank_deposits: number
  securities: number
  shares: number
  bonds: number
  
  // Business Assets
  business_capital: number
  inventory: number
  
  // Personal Assets
  jewelry: number
  vehicles: number
  furniture: number
  
  // Other Assets
  other_assets: number
  
  // Liabilities
  loans_payable: number
  other_liabilities: number
}

export interface PaymentData {
  // Advance Tax
  advance_tax: number
  
  // Tax Deducted at Source
  tds: number
  
  // Advance Income Tax
  ait: number
  
  // Previous Year Tax
  previous_year_tax: number
  
  // Penalties Paid
  penalties: number
  
  // Interest Paid
  interest_paid: number
}

export interface TaxCalculationResult {
  // Basic Results
  total_income: number
  taxable_income: number
  exemption: number
  gross_tax: number
  investment_rebate: number
  net_tax_before_surcharge: number
  surcharge: number
  environmental_surcharge: number
  total_surcharge: number
  tax_payable: number
  
  // Detailed Breakdown
  income_breakdown: IncomeBreakdown
  exemption_details: ExemptionDetails
  slab_calculation: SlabCalculation[]
  investment_rebate_details: InvestmentRebateDetails
  surcharge_details: SurchargeDetails
  
  // Payment Information
  total_payments: number
  refund_or_payable: number
  
  // Audit Trail
  calculation_steps: CalculationStep[]
  applied_rules: AppliedRule[]
  
  // Metadata
  tax_year: string
  calculation_date: string
  engine_version: string
  
  // Forms Data
  suggested_forms: string[]
  form_data: Record<string, any>
}

export interface IncomeBreakdown {
  employment_income: number
  business_income: number
  property_income: number
  agriculture_income: number
  capital_gains: number
  financial_income: number
  other_income: number
  export_income: number
  industrial_income: number
  foreign_income: number
}

export interface ExemptionDetails {
  basic_exemption: number
  age_based_exemption: number
  gender_based_exemption: number
  disability_exemption: number
  freedom_fighter_exemption: number
  total_exemption: number
}

export interface SlabCalculation {
  slab_min: number
  slab_max: number | null
  rate: number
  taxable_amount: number
  tax_amount: number
}

export interface InvestmentRebateDetails {
  eligible_investments: number
  rebate_percentage: number
  gross_tax_limit: number
  investment_limit: number
  applicable_rebate: number
}

export interface SurchargeDetails {
  wealth_surcharge: number
  environmental_surcharge: number
  tobacco_surcharge: number
  location_surcharge: number
  total_surcharge: number
}

export interface CalculationStep {
  step: number
  description: string
  formula: string
  inputs: Record<string, number>
  result: number
  notes?: string
}

export interface AppliedRule {
  rule_id: string
  rule_description: string
  source: 'act' | 'circular' | 'rule'
  section_reference: string
  conditions_met: string[]
}

// Enums and Constants
export enum TaxpayerCategory {
  INDIVIDUAL = 'individual',
  COMPANY = 'company',
  FIRM = 'firm',
  HINDU_UNDIVIDED_FAMILY = 'hindu_undivided_family',
  TRUST = 'trust',
  COOPERATIVE = 'cooperative',
  ASSOCIATION_OF_PERSONS = 'association_of_persons',
  CHARITABLE_ORGANIZATION = 'charitable_organization'
}

export enum Gender {
  MALE = 'male',
  FEMALE = 'female',
  OTHER = 'other'
}

export enum SpecialStatus {
  SENIOR_CITIZEN = 'senior_citizen',
  DISABLED_PERSON = 'disabled_person',
  FREEDOM_FIGHTER = 'freedom_fighter',
  WAR_WOUNDED = 'war_wounded',
  THIRD_GENDER = 'third_gender'
}

export enum ResidentialStatus {
  RESIDENT = 'resident',
  NON_RESIDENT = 'non_resident'
}

// Form validation schemas
export interface TaxFormData {
  taxpayer: TaxpayerProfile
  income: IncomeData
  investments: InvestmentData
  assets: AssetData
  payments: PaymentData
}

// API Response types
export interface TaxCalculationResponse {
  success: boolean
  data?: TaxCalculationResult
  error?: {
    code: string
    message: string
    details?: Record<string, any>
  }
  metadata: {
    processing_time_ms: number
    engine_version: string
    api_version: string
  }
}

// Form step types for multi-step wizard
export enum FormStep {
  TAXPAYER_INFO = 'taxpayer_info',
  INCOME_DETAILS = 'income_details',
  INVESTMENTS = 'investments',
  ASSETS = 'assets',
  PAYMENTS = 'payments',
  REVIEW = 'review'
}

export interface FormStepData {
  step: FormStep
  title: string
  description: string
  isCompleted: boolean
  isValid: boolean
  data: Partial<TaxFormData>
}