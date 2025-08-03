/**
 * Legal-Aware Tax Calculator
 * Built on top of Legal Cross-Reference Engine
 * Provides full citation trails and legal reasoning for every calculation
 */

class LegalAwareTaxCalculator {
    constructor() {
        // Import legal foundation - THIS IS THE KEY
        this.legalEngine = new (require('./legal_cross_reference_engine'))();
        this.calculationRules = new Map();
        this.citationCache = new Map();
        
        this.initializeLegalCalculationRules();
    }

    /**
     * Initialize calculation rules with full legal backing
     */
    initializeLegalCalculationRules() {
        // Each calculation rule must have legal foundation
        this.addLegalCalculationRule('individual_tax_2024', {
            legal_query: 'individual income tax rates for financial year 2024-25',
            primary_authority: 'finance_act_2024_section_6',
            calculation_logic: this.calculateIndividualTaxWithCitations.bind(this),
            required_legal_path: [
                'income_tax_act_2023_section_5', // Basic charge
                'finance_act_2024_section_6',    // Current rates  
                'finance_act_2024_schedule_3',   // Tax slabs
                'income_tax_act_2023_section_163' // Minimum tax
            ]
        });

        this.addLegalCalculationRule('company_tax_2024', {
            legal_query: 'company income tax rates for financial year 2024-25',
            primary_authority: 'finance_act_2024_company_schedule',
            calculation_logic: this.calculateCompanyTaxWithCitations.bind(this),
            required_legal_path: [
                'income_tax_act_2023_section_25', // Company tax provision
                'finance_act_2024_company_schedule' // Current company rates
            ]
        });

        this.addLegalCalculationRule('penalty_calculation_2025', {
            legal_query: 'penalty and interest calculation rules',
            primary_authority: 'finance_ordinance_2025_section_122',
            calculation_logic: this.calculatePenaltyWithCitations.bind(this),
            required_legal_path: [
                'income_tax_act_2023_section_272', // Base penalty provision
                'finance_ordinance_2025_section_122', // Updated penalty rates
                'finance_ordinance_2025_section_99'   // Late filing specifics
            ]
        });
    }

    /**
     * Calculate individual tax with full legal citations
     */
    async calculateIndividualTaxWithCitations(income, category = 'general', location = 'dhaka') {
        const calculation = {
            input: { income, category, location },
            legal_foundation: null,
            calculation_steps: [],
            citations: [],
            result: {},
            audit_trail: []
        };

        try {
            // Step 1: Establish legal foundation FIRST
            console.log('🏛️ Establishing legal foundation...');
            const legalPath = this.legalEngine.findLegalPath(
                `income tax calculation for ${category} taxpayer with income ${income}`,
                { income, category, location }
            );

            calculation.legal_foundation = legalPath;
            calculation.audit_trail.push({
                step: 'establish_legal_foundation',
                legal_chain: legalPath.legal_chain,
                confidence: legalPath.confidence
            });

            if (legalPath.confidence < 0.7) {
                calculation.warnings = ['Low confidence in legal path - manual review recommended'];
            }

            // Step 2: Determine tax-free limit with legal backing
            const taxFreeLimitResult = await this.determineTaxFreeLimitWithCitation(category);
            calculation.calculation_steps.push(taxFreeLimitResult);
            calculation.citations.push(...taxFreeLimitResult.citations);

            const taxFreeLimit = taxFreeLimitResult.amount;
            const taxableIncome = Math.max(0, income - taxFreeLimit);

            // Step 3: Apply tax slabs with legal citations
            const taxSlabResult = await this.applyTaxSlabsWithCitation(taxableIncome);
            calculation.calculation_steps.push(taxSlabResult);
            calculation.citations.push(...taxSlabResult.citations);

            const baseTax = taxSlabResult.total_tax;

            // Step 4: Apply minimum tax with legal backing
            const minimumTaxResult = await this.applyMinimumTaxWithCitation(baseTax, income, location);
            calculation.calculation_steps.push(minimumTaxResult);
            calculation.citations.push(...minimumTaxResult.citations);

            const finalTax = minimumTaxResult.final_tax;

            // Step 5: Compile final result with complete legal trail
            calculation.result = {
                gross_income: income,
                tax_free_limit: taxFreeLimit,
                taxable_income: taxableIncome,
                base_tax: baseTax,
                final_tax: finalTax,
                effective_rate: ((finalTax / income) * 100).toFixed(2) + '%',
                legal_certainty: legalPath.confidence
            };

            // Step 6: Generate comprehensive citation list
            calculation.citations = this.consolidateCitations(calculation.citations);

        } catch (error) {
            calculation.error = error.message;
            calculation.legal_foundation = { error: 'Failed to establish legal foundation' };
        }

        return calculation;
    }

    /**
     * Determine tax-free limit with proper legal citation
     */
    async determineTaxFreeLimitWithCitation(category) {
        const step = {
            step_name: 'determine_tax_free_limit',
            legal_question: `What is the tax-free limit for ${category} taxpayer?`,
            citations: [],
            reasoning: [],
            amount: 350000
        };

        // Find legal authority for tax-free limits
        const legalPath = this.legalEngine.findLegalPath(`tax free limit for ${category} taxpayer`);
        
        if (legalPath.legal_chain.length > 0) {
            step.legal_authority = legalPath.legal_chain[0];
            step.citations.push({
                provision: 'Finance Act, 2024, Section 6',
                text: 'Tax-free income limits for different categories of taxpayers',
                relevance: 'primary',
                legal_effect: 'establishes_tax_free_limits'
            });
        }

        // Category-specific limits with citations
        const categoryLimits = {
            'general': { amount: 350000, citation: 'Finance Act 2024, Section 6(1)' },
            'female': { amount: 400000, citation: 'Finance Act 2024, Section 6(2)(a)' },
            'senior_citizen': { amount: 400000, citation: 'Finance Act 2024, Section 6(2)(b)' },
            'disabled': { amount: 475000, citation: 'Finance Act 2024, Section 6(2)(c)' },
            'third_gender': { amount: 475000, citation: 'Finance Act 2024, Section 6(2)(d)' },
            'freedom_fighter': { amount: 500000, citation: 'Finance Act 2024, Section 6(2)(e)' }
        };

        const limitInfo = categoryLimits[category] || categoryLimits['general'];
        step.amount = limitInfo.amount;
        step.citations.push({
            provision: limitInfo.citation,
            text: `Tax-free limit for ${category}: BDT ${limitInfo.amount.toLocaleString()}`,
            relevance: 'primary',
            calculation_basis: 'statutory_provision'
        });

        step.reasoning.push(`According to ${limitInfo.citation}, ${category} taxpayers have a tax-free income limit of BDT ${limitInfo.amount.toLocaleString()}`);

        return step;
    }

    /**
     * Apply tax slabs with detailed legal citations
     */
    async applyTaxSlabsWithCitation(taxableIncome) {
        const step = {
            step_name: 'apply_tax_slabs',
            legal_question: 'What are the applicable tax rates for this income level?',
            citations: [],
            slab_calculations: [],
            total_tax: 0
        };

        // Legal authority for tax slabs
        step.citations.push({
            provision: 'Finance Act, 2024, Schedule 3',
            text: 'Tax rates for individual taxpayers for financial year 2024-25',
            relevance: 'primary',
            legal_effect: 'establishes_tax_rates'
        });

        step.citations.push({
            provision: 'Income Tax Act, 2023, Section 5',
            text: 'Basic charge of tax - subject to provisions of this Act',
            relevance: 'foundational',
            legal_effect: 'provides_charging_authority'
        });

        // Tax slabs with legal backing
        const taxSlabs = [
            { min: 0, max: 350000, rate: 0, legal_ref: 'Schedule 3, Slab 1' },
            { min: 350001, max: 450000, rate: 5, legal_ref: 'Schedule 3, Slab 2' },
            { min: 450001, max: 850000, rate: 10, legal_ref: 'Schedule 3, Slab 3' },
            { min: 850001, max: 1350000, rate: 15, legal_ref: 'Schedule 3, Slab 4' },
            { min: 1350001, max: 1850000, rate: 20, legal_ref: 'Schedule 3, Slab 5' },
            { min: 1850001, max: 3850000, rate: 25, legal_ref: 'Schedule 3, Slab 6' },
            { min: 3850001, max: Infinity, rate: 30, legal_ref: 'Schedule 3, Slab 7' }
        ];

        let remainingIncome = taxableIncome;
        let totalTax = 0;

        for (const slab of taxSlabs) {
            if (remainingIncome <= 0) break;

            const slabIncome = Math.min(remainingIncome, slab.max - Math.max(slab.min - 1, 0));
            const slabTax = slabIncome * (slab.rate / 100);
            totalTax += slabTax;
            remainingIncome -= slabIncome;

            if (slabTax > 0) {
                step.slab_calculations.push({
                    slab_range: `${slab.min.toLocaleString()} - ${slab.max === Infinity ? '∞' : slab.max.toLocaleString()}`,
                    rate: `${slab.rate}%`,
                    income_in_slab: slabIncome,
                    tax_from_slab: slabTax,
                    legal_authority: `Finance Act 2024, ${slab.legal_ref}`,
                    calculation: `${slabIncome.toLocaleString()} × ${slab.rate}% = ${slabTax.toLocaleString()}`
                });
            }
        }

        step.total_tax = totalTax;
        step.reasoning = `Tax calculated using progressive slabs as per Finance Act 2024, Schedule 3. Total tax: BDT ${totalTax.toLocaleString()}`;

        return step;
    }

    /**
     * Apply minimum tax with legal citation
     */
    async applyMinimumTaxWithCitation(calculatedTax, income, location) {
        const step = {
            step_name: 'apply_minimum_tax',
            legal_question: 'What is the minimum tax requirement?',
            citations: [],
            calculated_tax: calculatedTax,
            minimum_tax: 0,
            final_tax: calculatedTax
        };

        // Legal authority for minimum tax
        step.citations.push({
            provision: 'Income Tax Act, 2023, Section 163',
            text: 'Minimum tax provisions for different locations',
            relevance: 'primary',
            legal_effect: 'establishes_minimum_tax_requirement'
        });

        // Location-based minimum tax with citations
        const minimumTaxRates = {
            'dhaka': { amount: 5000, citation: 'Section 163(1)(a)' },
            'other_city': { amount: 4000, citation: 'Section 163(1)(b)' },
            'other_areas': { amount: 3000, citation: 'Section 163(1)(c)' }
        };

        const locationKey = location.includes('dhaka') || location.includes('chittagong') ? 'dhaka' : 
                          location.includes('city') ? 'other_city' : 'other_areas';

        const minTaxInfo = minimumTaxRates[locationKey];
        step.minimum_tax = minTaxInfo.amount;

        step.citations.push({
            provision: `Income Tax Act, 2023, ${minTaxInfo.citation}`,
            text: `Minimum tax for ${location}: BDT ${minTaxInfo.amount.toLocaleString()}`,
            relevance: 'primary',
            calculation_basis: 'location_based_minimum'
        });

        // Apply minimum tax rule
        const applicableMinimum = income > 350000 ? step.minimum_tax : 0; // Only if above tax-free limit
        step.final_tax = Math.max(calculatedTax, applicableMinimum);

        step.reasoning = `Per Section 163, minimum tax of BDT ${applicableMinimum.toLocaleString()} applies. Final tax: max(${calculatedTax.toLocaleString()}, ${applicableMinimum.toLocaleString()}) = BDT ${step.final_tax.toLocaleString()}`;

        return step;
    }

    /**
     * Consolidate and organize citations
     */
    consolidateCitations(citations) {
        const consolidated = {
            primary_authorities: [],
            supporting_provisions: [],
            implementation_guidance: [],
            total_citations: citations.length
        };

        citations.forEach(citation => {
            if (citation.relevance === 'primary') {
                consolidated.primary_authorities.push(citation);
            } else if (citation.relevance === 'foundational') {
                consolidated.supporting_provisions.push(citation);
            } else {
                consolidated.implementation_guidance.push(citation);
            }
        });

        return consolidated;
    }

    /**
     * Calculate with full legal transparency
     */
    async calculateWithLegalFoundation(calculationType, ...args) {
        const rule = this.calculationRules.get(calculationType);
        if (!rule) {
            throw new Error(`Unknown calculation type: ${calculationType}`);
        }

        // Verify legal foundation exists
        const legalPath = this.legalEngine.findLegalPath(rule.legal_query);
        if (legalPath.confidence < 0.5) {
            throw new Error(`Insufficient legal foundation for ${calculationType}`);
        }

        // Execute calculation with legal backing
        const result = await rule.calculation_logic(...args);
        
        // Add legal foundation to result
        result.legal_validation = this.legalEngine.validateLegalPath(legalPath);
        result.calculation_authority = rule.primary_authority;
        result.legal_confidence = legalPath.confidence;

        return result;
    }

    /**
     * Generate legal report for calculation
     */
    generateLegalReport(calculationResult) {
        return {
            executive_summary: {
                calculation_type: calculationResult.step_name || 'tax_calculation',
                legal_confidence: calculationResult.legal_confidence || 'unknown',
                primary_authorities: calculationResult.citations?.primary_authorities?.length || 0,
                total_citations: calculationResult.citations?.total_citations || 0
            },
            legal_foundation: calculationResult.legal_foundation,
            citation_analysis: calculationResult.citations,
            compliance_status: this.assessCompliance(calculationResult),
            recommendations: this.generateRecommendations(calculationResult)
        };
    }

    /**
     * Helper methods
     */
    addLegalCalculationRule(ruleId, ruleData) {
        this.calculationRules.set(ruleId, ruleData);
    }

    assessCompliance(result) {
        return {
            status: result.legal_confidence > 0.8 ? 'compliant' : 'review_required',
            confidence: result.legal_confidence,
            issues: result.warnings || []
        };
    }

    generateRecommendations(result) {
        const recommendations = [];
        
        if (result.legal_confidence < 0.8) {
            recommendations.push('Seek legal review due to low confidence in legal foundation');
        }
        
        if (result.warnings && result.warnings.length > 0) {
            recommendations.push('Address calculation warnings before finalizing');
        }

        return recommendations;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LegalAwareTaxCalculator;
}

// Example usage
if (typeof window !== 'undefined' || require.main === module) {
    console.log('⚖️ Legal-Aware Tax Calculator - Citation-Based System');
    console.log('=====================================================\n');
    
    const calculator = new LegalAwareTaxCalculator();
    
    // Test with full legal backing
    calculator.calculateWithLegalFoundation('individual_tax_2024', 1000000, 'female', 'dhaka')
        .then(result => {
            console.log('📊 Individual Tax Calculation with Legal Citations:');
            console.log(JSON.stringify(result, null, 2));
            
            console.log('\n📋 Legal Report:');
            const report = calculator.generateLegalReport(result);
            console.log(JSON.stringify(report, null, 2));
        })
        .catch(error => {
            console.error('Calculation error:', error.message);
        });
}