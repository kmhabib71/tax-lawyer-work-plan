For a COMPREHENSIVE Tax Rules Engine (Days 8-9), here are the specific data files needed for each task:

📋 COMPREHENSIVE TAX RULES ENGINE DATA REQUIREMENTS

🎯 Task 1: Core Tax Calculation Rules

Essential Files:

1. ✅ income_tax_act_2023_cleaned.json - All 345 sections for rule extraction
2. ❓ Income Tax Rate/Slab Tables (2024-25) - Current year tax slabs for all categories
3. ✅ income-tax-schedule-bangla.json - All 8 schedules for calculation rules
4. ✅ income-tax-schedule-english.json - English version for cross-reference
5. ❓ Income Tax Calculation Examples/Worksheets - Practical calculation methods
6. ✅ business_expense_limits.json - Business deduction rules
7. ❓ Income Head Definitions & Rules - Salary, Business, Property, Capital Gains, Other

For Advanced Rules:

8. ❓ Depreciation Tables & Rates - Schedule 3 detailed calculations
9. ❓ Investment Allowance Rules - Schedule 1 detailed provisions
10. ❓ Tax Holiday Provisions - Schedule 6 detailed rules

🎯 Task 2: Tax Slab Calculation Engine

Critical Files:

1. ❓ Tax Slab Tables FY 2024-25 - Individual, Company, Cooperative rates
2. ❓ Surcharge & Additional Tax Rules - High-income surcharge calculations
3. ❓ Special Category Slabs - Women, Senior Citizens, Disabled, Freedom Fighters
4. ✅ minimum-tax-section-163-of-income-tax-act-2023.json - Minimum tax rules
5. ❓ Company Tax Rates by Type - Public, Private, Bank, Insurance, Telecom
6. ❓ Withholding Tax Rates - All TDS/collection rates by payment type

For Progressive Calculation:

7. ❓ Slab Progression Rules - How slabs apply to different income levels
8. ❓ Tax Credit Rules - Credits against calculated tax

🎯 Task 3: Exemption and Rebate Rules

Essential Files:

1. ✅ ereturn_validation_rules.json - Basic exemption validation
2. ❓ Investment Rebate Rules (Detailed) - Section 44 detailed calculations
3. ❓ House Rent Allowance Exemption - Detailed HRA calculation rules
4. ❓ Conveyance Allowance Rules - Transport allowance exemptions
5. ❓ Medical Allowance Rules - Medical exemption calculations
6. ❓ Provident Fund Rules - PF contribution and withdrawal rules
7. ❓ Gratuity Rules - Gratuity exemption calculations

Advanced Exemptions:

8. ❓ Export Income Exemption - Export-related exemptions
9. ❓ Agricultural Income Rules - Agricultural exemption details
10. ❓ Dividend Income Rules - Dividend exemption/taxation

🎯 Task 4: Penalty Calculation Logic

Critical Files:

1. ❓ Penalty Rate Tables - All penalty percentages by violation type
2. ❓ Interest Calculation Rules - Daily/monthly interest rates
3. ❓ Late Filing Penalties - Penalty structure for late returns
4. ❓ Tax Evasion Penalties - Serious violation penalty calculations
5. ❓ Waiver Eligibility Rules - When penalties can be waived
6. ✅ income_tax_circular_2024_25_ultra_enriched.json - Latest penalty guidance

Advanced Penalty Rules:

7. ❓ Prosecution Thresholds - When cases go to prosecution
8. ❓ Settlement Rules - Penalty settlement procedures

📊 DATA AVAILABILITY ANALYSIS:

✅ AVAILABLE (8/24 files):

- income_tax_act_2023_cleaned.json
- income-tax-schedule-bangla/english.json
- business_expense_limits.json
- minimum-tax-section-163.json
- ereturn_validation_rules.json
- income_tax_circular_2024_25_ultra_enriched.json

❓ MISSING/NEEDED (16/24 files):

- Tax Slab Tables FY 2024-25 (CRITICAL)
- Penalty Rate Tables (CRITICAL)
- Investment Rebate Rules (CRITICAL)
- HRA/Conveyance/Medical Rules (IMPORTANT)
- Company Tax Rates by Type (IMPORTANT)
- Depreciation Tables (IMPORTANT)
- Interest Calculation Rules (IMPORTANT)

🎯 RECOMMENDATION:

Option 1: Build with Current Data (70% Comprehensive)

- Can create framework and basic calculations
- Missing specific rates, detailed rules, penalty tables
- Will need significant enhancement when complete data available

Option 2: Wait for Complete Data (100% Comprehensive)

- Delay Week 2 until all critical files available
- Build full system in one go
- Risk: Extends timeline but delivers complete solution

Option 3: Hybrid Approach (RECOMMENDED)

- Build extensible framework now
- Implement placeholders for missing data
- Create data ingestion pipeline for easy updates
- Parallel development while you complete data

required 29 files:
Income Tax Rate/Slab Tables (2024-25)
Income Tax Calculation Examples/Worksheets
Income Head Definitions & Rules
Depreciation Tables & Rates
Investment Allowance Rules
Tax Holiday Provisions
Tax Slab Tables FY 2024-25
Surcharge & Additional Tax Rules
Special Category Slabs
Company Tax Rates by Type
Withholding Tax Rates
Slab Progression Rules
Tax Credit Rules
Investment Rebate Rules (Detailed)
House Rent Allowance Exemption
Conveyance Allowance Rules
Medical Allowance Rules
Provident Fund Rules
Gratuity Rules
Export Income Exemption
Agricultural Income Rules
Dividend Income Rules
Penalty Rate Tables
Interest Calculation Rules
Late Filing Penalties
Tax Evasion Penalties
Waiver Eligibility Rules
Prosecution Thresholds
Settlement Rules
