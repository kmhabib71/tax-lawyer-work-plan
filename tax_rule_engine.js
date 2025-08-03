/**
 * Simple Tax Rule Hierarchy System for Bangladesh
 * Handles complex cross-references through priority-based rules
 */

class TaxRuleEngine {
    constructor() {
        this.ruleHierarchy = {
            CURRENT_YEAR: 1,      // Finance Act 2024/2025 (overrides everything)
            IMPLEMENTATION: 2,     // NBR Circulars (how to apply)
            BASE_LAW: 3,          // Income Tax Act 2023 (foundation)
            HISTORICAL: 4         // Previous years (reference only)
        };
        
        this.rules = new Map();
        this.calculations = new Map();
        this.sources = new Map();
        
        this.initializeRules();
    }

    /**
     * Initialize core tax rules with priority-based hierarchy
     */
    initializeRules() {
        // Individual Tax Slabs (Finance Act 2024)
        this.addRule('individual_tax_slabs_2024', {
            priority: this.ruleHierarchy.CURRENT_YEAR,
            source: 'Finance Act 2024, Schedule 3',
            effective_date: '2024-07-01',
            slabs: [
                { min: 0, max: 350000, rate: 0, description: 'Tax-free' },
                { min: 350001, max: 450000, rate: 5, description: 'First slab' },
                { min: 450001, max: 850000, rate: 10, description: 'Second slab' },
                { min: 850001, max: 1350000, rate: 15, description: 'Third slab' },
                { min: 1350001, max: 1850000, rate: 20, description: 'Fourth slab' },
                { min: 1850001, max: 3850000, rate: 25, description: 'Fifth slab' },
                { min: 3850001, max: Infinity, rate: 30, description: 'Highest slab' }
            ]
        });

        // Special Categories (Finance Act 2024)
        this.addRule('special_tax_free_limits_2024', {
            priority: this.ruleHierarchy.CURRENT_YEAR,
            source: 'Finance Act 2024, Section 6',
            effective_date: '2024-07-01',
            categories: {
                'female': 400000,
                'senior_citizen': 400000, // 65+ years
                'disabled': 475000,
                'third_gender': 475000,
                'freedom_fighter': 500000
            }
        });

        // Company Tax Rates (Finance Act 2024)
        this.addRule('company_tax_rates_2024', {
            priority: this.ruleHierarchy.CURRENT_YEAR,
            source: 'Finance Act 2024, Company Tax Schedule',
            effective_date: '2024-07-01',
            rates: {
                'public_listed_10_percent_ipo': { standard: 22.5, condition_met: 20 },
                'public_listed_less_10_percent': { standard: 25, condition_met: 22.5 },
                'private_limited': { standard: 27.5, condition_met: 25 },
                'one_person_company': { standard: 22.5, condition_met: 20 },
                'bank_insurance_public': 37.5,
                'bank_insurance_private': 40,
                'merchant_bank': 37.5,
                'tobacco_company': 45,
                'mobile_operator_public': 40,
                'mobile_operator_private': 45
            }
        });

        // Surcharge Rules (Finance Act 2024)
        this.addRule('surcharge_rates_2024', {
            priority: this.ruleHierarchy.CURRENT_YEAR,
            source: 'Finance Act 2024, Surcharge Schedule',
            effective_date: '2024-07-01',
            net_wealth_slabs: [
                { min: 0, max: 40000000, rate: 0, description: 'No surcharge' },
                { min: 40000001, max: 100000000, rate: 10, description: 'Low wealth' },
                { min: 100000001, max: 200000000, rate: 20, description: 'Medium wealth' },
                { min: 200000001, max: 500000000, rate: 30, description: 'High wealth' },
                { min: 500000001, max: Infinity, rate: 35, description: 'Ultra high wealth' }
            ],
            special_conditions: {
                'multiple_cars': { rate: 10, condition: 'more than one car' },
                'large_property': { rate: 10, condition: 'more than 8000 sq ft property' }
            }
        });

        // Penalty Rates (Finance Ordinance 2025)
        this.addRule('penalty_rates_2025', {
            priority: this.ruleHierarchy.CURRENT_YEAR,
            source: 'Finance Ordinance 2025, Section 122',
            effective_date: '2025-01-01',
            penalties: {
                'tax_evasion': {
                    formula: '(evaded_amount * 0.10) * years_concealed',
                    description: '10% of evaded amount × years from evasion to detection'
                },
                'late_filing': {
                    formula: 'payable_tax * 0.02 * months_delay',
                    max_months: 24,
                    description: '2% per month on payable tax, max 24 months'
                },
                'interest_on_default': {
                    formula: 'outstanding_amount * 0.02 * months',
                    max_months: 24,
                    description: '2% per month simple interest, max 24 months'
                }
            }
        });

        // Minimum Tax Rules (Income Tax Act 2023)
        this.addRule('minimum_tax_2024', {
            priority: this.ruleHierarchy.BASE_LAW,
            source: 'Income Tax Act 2023, Section 163',
            effective_date: '2023-07-01',
            by_location: {
                'dhaka_north_south_chittagong': 5000,
                'other_city_corporations': 4000,
                'other_areas': 3000
            }
        });
    }

    /**
     * Add a rule to the system with automatic conflict resolution
     */
    addRule(ruleId, ruleData) {
        // Check for conflicts with existing rules
        const existingRule = this.rules.get(ruleId);
        if (existingRule && existingRule.priority < ruleData.priority) {
            console.warn(`Rule conflict: ${ruleId} - keeping higher priority rule`);
            return false;
        }

        this.rules.set(ruleId, ruleData);
        this.sources.set(ruleId, {
            primary_source: ruleData.source,
            effective_date: ruleData.effective_date,
            last_updated: new Date().toISOString()
        });

        return true;
    }

    /**
     * Get the most current rule, handling conflicts automatically
     */
    getRule(ruleId) {
        const rule = this.rules.get(ruleId);
        if (!rule) {
            throw new Error(`Rule not found: ${ruleId}`);
        }
        return rule;
    }

    /**
     * Calculate individual income tax
     */
    calculateIndividualTax(income, category = 'general', location = 'dhaka_north_south_chittagong') {
        const calculation = {
            input: { income, category, location },
            steps: [],
            sources: [],
            result: {}
        };

        try {
            // Step 1: Determine tax-free limit
            const specialLimits = this.getRule('special_tax_free_limits_2024');
            const taxFreeLimit = specialLimits.categories[category] || 350000;
            
            calculation.steps.push({
                step: 'determine_tax_free_limit',
                value: taxFreeLimit,
                description: `Tax-free limit for ${category}: ${taxFreeLimit.toLocaleString()}`
            });
            calculation.sources.push(specialLimits.source);

            // Step 2: Calculate taxable income
            const taxableIncome = Math.max(0, income - taxFreeLimit);
            calculation.steps.push({
                step: 'calculate_taxable_income',
                value: taxableIncome,
                description: `Taxable income: ${income.toLocaleString()} - ${taxFreeLimit.toLocaleString()} = ${taxableIncome.toLocaleString()}`
            });

            // Step 3: Apply tax slabs
            const slabs = this.getRule('individual_tax_slabs_2024');
            let totalTax = 0;
            let remainingIncome = taxableIncome;

            for (const slab of slabs.slabs) {
                if (remainingIncome <= 0) break;

                const slabIncome = Math.min(remainingIncome, slab.max - Math.max(slab.min - 1, 0));
                const slabTax = slabIncome * (slab.rate / 100);
                totalTax += slabTax;
                remainingIncome -= slabIncome;

                if (slabTax > 0) {
                    calculation.steps.push({
                        step: 'apply_tax_slab',
                        slab_range: `${slab.min.toLocaleString()} - ${slab.max === Infinity ? '∞' : slab.max.toLocaleString()}`,
                        rate: `${slab.rate}%`,
                        slab_income: slabIncome,
                        slab_tax: slabTax,
                        description: `${slab.description}: ${slabIncome.toLocaleString()} × ${slab.rate}% = ${slabTax.toLocaleString()}`
                    });
                }
            }
            calculation.sources.push(slabs.source);

            // Step 4: Apply minimum tax
            const minimumTaxRules = this.getRule('minimum_tax_2024');
            const minimumTax = minimumTaxRules.by_location[location] || 3000;
            const finalTax = Math.max(totalTax, income > taxFreeLimit ? minimumTax : 0);

            calculation.steps.push({
                step: 'apply_minimum_tax',
                calculated_tax: totalTax,
                minimum_tax: minimumTax,
                final_tax: finalTax,
                description: `Final tax: max(${totalTax.toLocaleString()}, ${minimumTax.toLocaleString()}) = ${finalTax.toLocaleString()}`
            });
            calculation.sources.push(minimumTaxRules.source);

            // Step 5: Calculate surcharge (if applicable)
            // Note: This would require net wealth information
            const surcharge = 0; // Placeholder - requires wealth calculation

            calculation.result = {
                gross_income: income,
                tax_free_limit: taxFreeLimit,
                taxable_income: taxableIncome,
                base_tax: totalTax,
                minimum_tax: minimumTax,
                surcharge: surcharge,
                total_tax: finalTax + surcharge,
                effective_rate: ((finalTax + surcharge) / income * 100).toFixed(2) + '%'
            };

        } catch (error) {
            calculation.error = error.message;
        }

        return calculation;
    }

    /**
     * Calculate company tax
     */
    calculateCompanyTax(income, companyType, meetsConditions = false) {
        const calculation = {
            input: { income, companyType, meetsConditions },
            steps: [],
            sources: [],
            result: {}
        };

        try {
            const companyRates = this.getRule('company_tax_rates_2024');
            const rateInfo = companyRates.rates[companyType];

            if (!rateInfo) {
                throw new Error(`Unknown company type: ${companyType}`);
            }

            let applicableRate;
            if (typeof rateInfo === 'object' && rateInfo.condition_met) {
                applicableRate = meetsConditions ? rateInfo.condition_met : rateInfo.standard;
                calculation.steps.push({
                    step: 'determine_rate',
                    condition_met: meetsConditions,
                    rate: applicableRate,
                    description: `Rate for ${companyType}: ${applicableRate}% (${meetsConditions ? 'conditions met' : 'standard rate'})`
                });
            } else {
                applicableRate = rateInfo;
                calculation.steps.push({
                    step: 'determine_rate',
                    rate: applicableRate,
                    description: `Fixed rate for ${companyType}: ${applicableRate}%`
                });
            }

            const tax = income * (applicableRate / 100);
            calculation.sources.push(companyRates.source);

            calculation.result = {
                gross_income: income,
                applicable_rate: applicableRate + '%',
                calculated_tax: tax,
                total_tax: tax,
                effective_rate: applicableRate + '%'
            };

        } catch (error) {
            calculation.error = error.message;
        }

        return calculation;
    }

    /**
     * Calculate penalties
     */
    calculatePenalty(penaltyType, baseAmount, additionalParams = {}) {
        const calculation = {
            input: { penaltyType, baseAmount, additionalParams },
            steps: [],
            sources: [],
            result: {}
        };

        try {
            const penaltyRules = this.getRule('penalty_rates_2025');
            const penalty = penaltyRules.penalties[penaltyType];

            if (!penalty) {
                throw new Error(`Unknown penalty type: ${penaltyType}`);
            }

            let calculatedPenalty = 0;

            switch (penaltyType) {
                case 'tax_evasion':
                    const yearsConcealed = additionalParams.years || 1;
                    calculatedPenalty = baseAmount * 0.10 * yearsConcealed;
                    calculation.steps.push({
                        step: 'calculate_evasion_penalty',
                        formula: penalty.formula,
                        evaded_amount: baseAmount,
                        years: yearsConcealed,
                        penalty: calculatedPenalty,
                        description: `${baseAmount.toLocaleString()} × 10% × ${yearsConcealed} years = ${calculatedPenalty.toLocaleString()}`
                    });
                    break;

                case 'late_filing':
                    const months = Math.min(additionalParams.months || 1, 24);
                    calculatedPenalty = baseAmount * 0.02 * months;
                    calculation.steps.push({
                        step: 'calculate_late_filing_penalty',
                        formula: penalty.formula,
                        payable_tax: baseAmount,
                        months: months,
                        penalty: calculatedPenalty,
                        description: `${baseAmount.toLocaleString()} × 2% × ${months} months = ${calculatedPenalty.toLocaleString()}`
                    });
                    break;

                case 'interest_on_default':
                    const interestMonths = Math.min(additionalParams.months || 1, 24);
                    calculatedPenalty = baseAmount * 0.02 * interestMonths;
                    calculation.steps.push({
                        step: 'calculate_interest',
                        formula: penalty.formula,
                        outstanding_amount: baseAmount,
                        months: interestMonths,
                        interest: calculatedPenalty,
                        description: `${baseAmount.toLocaleString()} × 2% × ${interestMonths} months = ${calculatedPenalty.toLocaleString()}`
                    });
                    break;
            }

            calculation.sources.push(penaltyRules.source);
            calculation.result = {
                penalty_type: penaltyType,
                base_amount: baseAmount,
                calculated_penalty: calculatedPenalty,
                total_amount: baseAmount + calculatedPenalty
            };

        } catch (error) {
            calculation.error = error.message;
        }

        return calculation;
    }

    /**
     * Get all sources used in a calculation
     */
    getCalculationSources(calculationResult) {
        return {
            primary_sources: [...new Set(calculationResult.sources)],
            calculation_date: new Date().toISOString(),
            confidence: 'high', // Based on using current year rules
            notes: 'Calculation based on latest available tax laws and circulars'
        };
    }

    /**
     * Validate calculation against multiple rule sources
     */
    validateCalculation(calculationResult) {
        const validation = {
            status: 'valid',
            warnings: [],
            recommendations: []
        };

        // Check if using current year rules
        const hasCurrentYearRules = calculationResult.sources.some(source => 
            source.includes('2024') || source.includes('2025')
        );

        if (!hasCurrentYearRules) {
            validation.warnings.push('Calculation may be using outdated rules');
            validation.recommendations.push('Verify with latest Finance Act provisions');
        }

        // Check for edge cases
        if (calculationResult.result.effective_rate) {
            const rate = parseFloat(calculationResult.result.effective_rate);
            if (rate > 45) {
                validation.warnings.push('Unusually high effective tax rate detected');
                validation.recommendations.push('Review calculation for surcharge applicability');
            }
        }

        return validation;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TaxRuleEngine;
}

// Example usage and testing
if (typeof window !== 'undefined' || require.main === module) {
    console.log('🏗️ Tax Rule Engine - Simple Hierarchy System');
    console.log('=============================================\n');
    
    const engine = new TaxRuleEngine();
    
    // Test individual tax calculation
    console.log('📊 Individual Tax Calculation Test:');
    const individualResult = engine.calculateIndividualTax(1000000, 'general', 'dhaka_north_south_chittagong');
    console.log(JSON.stringify(individualResult, null, 2));
    
    console.log('\n📊 Company Tax Calculation Test:');
    const companyResult = engine.calculateCompanyTax(5000000, 'private_limited', true);
    console.log(JSON.stringify(companyResult, null, 2));
    
    console.log('\n📊 Penalty Calculation Test:');
    const penaltyResult = engine.calculatePenalty('late_filing', 50000, { months: 6 });
    console.log(JSON.stringify(penaltyResult, null, 2));
}