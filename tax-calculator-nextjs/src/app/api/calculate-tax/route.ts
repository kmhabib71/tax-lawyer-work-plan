import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { TaxCalculationResponse, TaxFormData } from '@/types/tax'

// Validation schema for API request
const apiRequestSchema = z.object({
  taxpayer: z.object({
    name: z.string(),
    nid: z.string(),
    category: z.string(),
    gender: z.string(),
    age: z.number(),
    special_status: z.array(z.string()).optional(),
    residential_status: z.string(),
  }),
  income: z.object({
    employment: z.object({
      basic_salary: z.number(),
      house_rent_allowance: z.number(),
      medical_allowance: z.number(),
      conveyance_allowance: z.number(),
      other_allowances: z.number(),
      bonus: z.number(),
      overtime: z.number(),
    }),
    business: z.object({
      trading_income: z.number(),
      manufacturing_income: z.number(),
      service_income: z.number(),
      professional_income: z.number(),
    }),
    property: z.object({
      house_rent: z.number(),
      commercial_rent: z.number(),
      land_rent: z.number(),
    }),
    agriculture: z.object({
      crops: z.number(),
      livestock: z.number(),
      fisheries: z.number(),
      poultry: z.number(),
    }),
    capital_gains: z.object({
      securities: z.number(),
      property: z.number(),
      other_assets: z.number(),
    }),
    financial: z.object({
      bank_interest: z.number(),
      dividends: z.number(),
      mutual_funds: z.number(),
      debentures: z.number(),
    }),
    other: z.object({
      royalty: z.number(),
      technical_fees: z.number(),
      commission: z.number(),
      lottery_winnings: z.number(),
      gifts: z.number(),
    }),
    export: z.object({
      goods: z.number(),
      services: z.number(),
    }),
    industrial: z.object({
      manufacturing: z.number(),
      processing: z.number(),
    }),
    foreign: z.object({
      employment: z.number(),
      business: z.number(),
      investment: z.number(),
    }),
  }),
  investments: z.object({
    life_insurance: z.number(),
    dps: z.number(),
    government_securities: z.number(),
    stock_market: z.number(),
    mutual_funds: z.number(),
    provident_fund: z.number(),
    superannuation_fund: z.number(),
    benevolent_fund: z.number(),
    zakat_fund: z.number(),
    universal_pension: z.number(),
    other_investments: z.number(),
    donations: z.number(),
  }),
  assets: z.object({
    land_buildings: z.number(),
    agricultural_land: z.number(),
    bank_deposits: z.number(),
    securities: z.number(),
    shares: z.number(),
    bonds: z.number(),
    business_capital: z.number(),
    inventory: z.number(),
    jewelry: z.number(),
    vehicles: z.number(),
    furniture: z.number(),
    other_assets: z.number(),
    loans_payable: z.number(),
    other_liabilities: z.number(),
  }),
  payments: z.object({
    advance_tax: z.number(),
    tds: z.number(),
    ait: z.number(),
    previous_year_tax: z.number(),
    penalties: z.number(),
    interest_paid: z.number(),
  }),
})

// Mock comprehensive tax calculation function
// In production, this would call our actual comprehensive_tax_engine_2024_25.py
async function calculateTaxComprehensive(data: any) {
  const startTime = Date.now()
  
  // Calculate total income
  const totalIncome = 
    data.income.employment.basic_salary +
    data.income.employment.house_rent_allowance +
    data.income.employment.medical_allowance +
    data.income.employment.conveyance_allowance +
    data.income.employment.other_allowances +
    data.income.employment.bonus +
    data.income.employment.overtime +
    data.income.business.trading_income +
    data.income.business.manufacturing_income +
    data.income.business.service_income +
    data.income.business.professional_income +
    data.income.property.house_rent +
    data.income.property.commercial_rent +
    data.income.property.land_rent +
    data.income.agriculture.crops +
    data.income.agriculture.livestock +
    data.income.agriculture.fisheries +
    data.income.agriculture.poultry +
    data.income.capital_gains.securities +
    data.income.capital_gains.property +
    data.income.capital_gains.other_assets +
    data.income.financial.bank_interest +
    data.income.financial.dividends +
    data.income.financial.mutual_funds +
    data.income.financial.debentures +
    data.income.other.royalty +
    data.income.other.technical_fees +
    data.income.other.commission +
    data.income.other.lottery_winnings +
    data.income.other.gifts +
    data.income.export.goods +
    data.income.export.services +
    data.income.industrial.manufacturing +
    data.income.industrial.processing +
    data.income.foreign.employment +
    data.income.foreign.business +
    data.income.foreign.investment

  // Calculate exemption based on taxpayer profile
  let exemption = 350000 // Basic exemption for individual
  
  // Special status exemptions
  if (data.taxpayer.special_status?.includes('senior_citizen')) {
    exemption = 400000
  }
  if (data.taxpayer.gender === 'female') {
    exemption = Math.max(exemption, 375000)
  }
  if (data.taxpayer.special_status?.includes('disabled_person')) {
    exemption = Math.max(exemption, 450000)
  }
  if (data.taxpayer.special_status?.includes('freedom_fighter')) {
    exemption = Math.max(exemption, 425000)
  }

  // Calculate taxable income
  const taxableIncome = Math.max(0, totalIncome - exemption)

  // Progressive tax calculation (2024-25 slabs) - Show actual income ranges including exemption
  const displaySlabs = [
    { min: 0, max: exemption, rate: 0.00 }, // Exempt portion: 0%
    { min: exemption, max: exemption + 100000, rate: 0.05 }, // Next 1 lakh: 5%
    { min: exemption + 100000, max: exemption + 400000, rate: 0.10 }, // Next 3 lakh: 10%
    { min: exemption + 400000, max: exemption + 800000, rate: 0.15 }, // Next 4 lakh: 15%
    { min: exemption + 800000, max: exemption + 1300000, rate: 0.20 }, // Next 5 lakh: 20%
    { min: exemption + 1300000, max: Infinity, rate: 0.25 }, // Above: 25%
  ]

  let grossTax = 0
  const slabCalculation = []
  
  // Apply progressive tax slabs to total income (for display and calculation)
  for (const slab of displaySlabs) {
    if (totalIncome > slab.min) {
      const incomeAtThisSlab = Math.min(totalIncome, slab.max) - slab.min
      const taxAtThisSlab = incomeAtThisSlab * slab.rate
      grossTax += taxAtThisSlab
      
      if (incomeAtThisSlab > 0) {
        slabCalculation.push({
          slab_min: slab.min,
          slab_max: slab.max === Infinity ? null : slab.max,
          rate: slab.rate,
          taxable_amount: incomeAtThisSlab,
          tax_amount: taxAtThisSlab,
        })
      }
    }
  }

  // Calculate investment rebate
  const totalInvestments = 
    data.investments.life_insurance +
    data.investments.dps +
    data.investments.government_securities +
    data.investments.stock_market +
    data.investments.mutual_funds +
    data.investments.provident_fund +
    data.investments.superannuation_fund +
    data.investments.benevolent_fund +
    data.investments.zakat_fund +
    data.investments.universal_pension +
    data.investments.other_investments +
    data.investments.donations

  // Investment rebate: 15% of investments, max 15 lakh, cannot exceed 15% of gross tax
  const maxInvestmentRebate = Math.min(
    totalInvestments * 0.15,
    1500000, // 15 lakh max
    grossTax * 0.15 // Cannot exceed 15% of gross tax
  )

  const investmentRebate = maxInvestmentRebate
  const netTaxBeforeSurcharge = Math.max(0, grossTax - investmentRebate)

  // Surcharge calculation (simplified)
  let surcharge = 0
  if (data.taxpayer.category === 'company') {
    surcharge = netTaxBeforeSurcharge * 0.01 // 1% environmental surcharge for companies
  }

  const finalTaxPayable = netTaxBeforeSurcharge + surcharge

  // Income breakdown
  const incomeBreakdown = {
    employment_income: data.income.employment.basic_salary + 
                      data.income.employment.house_rent_allowance +
                      data.income.employment.medical_allowance +
                      data.income.employment.conveyance_allowance +
                      data.income.employment.other_allowances +
                      data.income.employment.bonus +
                      data.income.employment.overtime,
    business_income: data.income.business.trading_income +
                    data.income.business.manufacturing_income +
                    data.income.business.service_income +
                    data.income.business.professional_income,
    property_income: data.income.property.house_rent +
                    data.income.property.commercial_rent +
                    data.income.property.land_rent,
    agriculture_income: data.income.agriculture.crops +
                       data.income.agriculture.livestock +
                       data.income.agriculture.fisheries +
                       data.income.agriculture.poultry,
    capital_gains: data.income.capital_gains.securities +
                  data.income.capital_gains.property +
                  data.income.capital_gains.other_assets,
    financial_income: data.income.financial.bank_interest +
                     data.income.financial.dividends +
                     data.income.financial.mutual_funds +
                     data.income.financial.debentures,
    other_income: data.income.other.royalty +
                 data.income.other.technical_fees +
                 data.income.other.commission +
                 data.income.other.lottery_winnings +
                 data.income.other.gifts,
    export_income: data.income.export.goods + data.income.export.services,
    industrial_income: data.income.industrial.manufacturing + data.income.industrial.processing,
    foreign_income: data.income.foreign.employment + 
                   data.income.foreign.business + 
                   data.income.foreign.investment,
  }

  // Calculation steps for audit trail
  const calculationSteps = [
    {
      step: 1,
      description: 'Calculate total income from all sources',
      formula: 'Sum of all income types',
      inputs: { total_sources: Object.keys(incomeBreakdown).length },
      result: totalIncome,
      notes: 'Includes employment, business, property, and other income'
    },
    {
      step: 2,
      description: 'Apply applicable exemption',
      formula: `Max exemption based on taxpayer profile`,
      inputs: { basic_exemption: 350000, applied_exemption: exemption },
      result: exemption,
      notes: `Applied ${data.taxpayer.gender === 'female' ? 'female' : data.taxpayer.special_status?.join(', ') || 'basic'} exemption`
    },
    {
      step: 3,
      description: 'Calculate taxable income',
      formula: 'Total Income - Exemption',
      inputs: { total_income: totalIncome, exemption: exemption },
      result: taxableIncome,
      notes: 'Taxable income cannot be negative'
    },
    {
      step: 4,
      description: 'Apply progressive tax slabs',
      formula: 'Progressive tax calculation',
      inputs: { slabs_applied: slabCalculation.length },
      result: grossTax,
      notes: `Applied ${slabCalculation.length} tax slabs`
    },
    {
      step: 5,
      description: 'Calculate investment rebate',
      formula: 'Min(15% of investments, 15 lakh, 15% of gross tax)',
      inputs: { total_investments: totalInvestments, gross_tax: grossTax },
      result: investmentRebate,
      notes: 'Investment rebate reduces tax liability'
    },
    {
      step: 6,
      description: 'Calculate final tax payable',
      formula: 'Gross Tax - Investment Rebate + Surcharge',
      inputs: { gross_tax: grossTax, rebate: investmentRebate, surcharge: surcharge },
      result: finalTaxPayable,
      notes: 'Final amount payable to government'
    }
  ]

  const processingTime = Date.now() - startTime

  return {
    total_income: totalIncome,
    taxable_income: taxableIncome,
    exemption: exemption,
    gross_tax: grossTax,
    investment_rebate: investmentRebate,
    net_tax_before_surcharge: netTaxBeforeSurcharge,
    surcharge: surcharge,
    environmental_surcharge: data.taxpayer.category === 'company' ? surcharge : 0,
    total_surcharge: surcharge,
    tax_payable: finalTaxPayable,
    
    income_breakdown: incomeBreakdown,
    exemption_details: {
      basic_exemption: 350000,
      age_based_exemption: data.taxpayer.special_status?.includes('senior_citizen') ? 50000 : 0,
      gender_based_exemption: data.taxpayer.gender === 'female' ? 25000 : 0,
      disability_exemption: data.taxpayer.special_status?.includes('disabled_person') ? 100000 : 0,
      freedom_fighter_exemption: data.taxpayer.special_status?.includes('freedom_fighter') ? 75000 : 0,
      total_exemption: exemption,
    },
    slab_calculation: slabCalculation,
    investment_rebate_details: {
      eligible_investments: totalInvestments,
      rebate_percentage: 0.15,
      gross_tax_limit: grossTax * 0.15,
      investment_limit: 1500000,
      applicable_rebate: investmentRebate,
    },
    surcharge_details: {
      wealth_surcharge: 0,
      environmental_surcharge: data.taxpayer.category === 'company' ? surcharge : 0,
      tobacco_surcharge: 0,
      location_surcharge: 0,
      total_surcharge: surcharge,
    },
    
    total_payments: 0,
    refund_or_payable: finalTaxPayable,
    
    calculation_steps: calculationSteps,
    applied_rules: [
      {
        rule_id: 'ITA_2023_EXEMPTION',
        rule_description: 'Basic exemption for individuals',
        source: 'act' as const,
        section_reference: 'Section 44',
        conditions_met: ['Individual taxpayer', 'Resident status'],
      },
      {
        rule_id: 'CIRCULAR_2024_25_INVESTMENT',
        rule_description: '15% investment rebate on eligible investments',
        source: 'circular' as const,
        section_reference: 'Circular 2024-25, Topic 156',
        conditions_met: ['Has eligible investments', 'Within rebate limits'],
      }
    ],
    
    tax_year: '2024-25',
    calculation_date: new Date().toISOString(),
    engine_version: 'comprehensive_v2024.25',
    
    suggested_forms: ['IT-11GA', 'Schedule-5'],
    form_data: {
      it_11ga: {
        total_income: totalIncome,
        taxable_income: taxableIncome,
        tax_payable: finalTaxPayable,
      }
    },
    
    processing_time_ms: processingTime,
  }
}

export async function POST(request: NextRequest) {
  try {
    const startTime = Date.now()
    
    // Parse and validate request body
    const body = await request.json()
    const validatedData = apiRequestSchema.parse(body)
    
    // Calculate tax using our comprehensive engine
    const result = await calculateTaxComprehensive(validatedData)
    
    const processingTime = Date.now() - startTime
    
    // Return successful response
    const response: TaxCalculationResponse = {
      success: true,
      data: result,
      metadata: {
        processing_time_ms: processingTime,
        engine_version: 'comprehensive_v2024.25',
        api_version: '1.0.0',
      }
    }
    
    return NextResponse.json(response)
    
  } catch (error) {
    console.error('Tax calculation error:', error)
    
    // Handle validation errors
    if (error instanceof z.ZodError) {
      const response: TaxCalculationResponse = {
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid input data',
          details: error.errors.reduce((acc, err) => {
            acc[err.path.join('.')] = err.message
            return acc
          }, {} as Record<string, any>)
        },
        metadata: {
          processing_time_ms: Date.now() - Date.now(),
          engine_version: 'comprehensive_v2024.25',
          api_version: '1.0.0',
        }
      }
      
      return NextResponse.json(response, { status: 400 })
    }
    
    // Handle other errors
    const response: TaxCalculationResponse = {
      success: false,
      error: {
        code: 'CALCULATION_ERROR',
        message: 'Failed to calculate tax',
        details: { 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }
      },
      metadata: {
        processing_time_ms: Date.now() - Date.now(),
        engine_version: 'comprehensive_v2024.25',
        api_version: '1.0.0',
      }
    }
    
    return NextResponse.json(response, { status: 500 })
  }
}

// Handle OPTIONS for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}