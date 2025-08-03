/**
 * Legal Cross-Reference Engine for Bangladesh Tax Law
 * Builds the legal foundation BEFORE tax calculations
 * Handles citations, cross-references, and legal reasoning paths
 */

class LegalCrossReferenceEngine {
    constructor() {
        this.legalDatabase = new Map();
        this.crossReferences = new Map();
        this.citationPaths = new Map();
        this.amendments = new Map();
        this.schedules = new Map();
        
        this.initializeLegalStructure();
    }

    /**
     * Initialize the legal document structure with proper cross-references
     */
    initializeLegalStructure() {
        // Core legal documents hierarchy
        this.addLegalDocument('income_tax_act_2023', {
            title: 'Income Tax Act, 2023',
            authority: 'Parliament of Bangladesh',
            gazette_date: '2023-06-30',
            effective_date: '2023-07-01',
            sections: 345,
            schedules: 8,
            status: 'active',
            amendment_history: ['finance_act_2024']
        });

        this.addLegalDocument('finance_act_2024', {
            title: 'Finance Act, 2024',
            authority: 'Parliament of Bangladesh',
            gazette_date: '2024-06-30', 
            effective_date: '2024-07-01',
            amends: ['income_tax_act_2023'],
            status: 'active'
        });

        // Initialize cross-reference patterns
        this.initializeCrossReferencePatterns();
    }

    /**
     * Add a legal document to the database
     */
    addLegalDocument(documentId, documentData) {
        this.legalDatabase.set(documentId, {
            ...documentData,
            id: documentId,
            last_updated: new Date().toISOString()
        });
    }

    /**
     * Parse and store cross-references from legal text
     */
    addCrossReference(sourceSection, referenceType, targetSection, condition = null) {
        const referenceId = `${sourceSection}_to_${targetSection}`;
        
        this.crossReferences.set(referenceId, {
            source: sourceSection,
            target: targetSection,
            type: referenceType, // 'refers_to', 'amended_by', 'subject_to', 'unless', 'provided_that'
            condition: condition,
            legal_effect: this.determineLegalEffect(referenceType),
            created: new Date().toISOString()
        });

        // Build reverse index for efficient lookup
        this.buildReverseReference(targetSection, sourceSection, referenceType);
    }

    /**
     * Initialize common cross-reference patterns from Bangladesh tax law
     */
    initializeCrossReferencePatterns() {
        // Section 5 - Basic charge of tax
        this.addSection('income_tax_act_2023_section_5', {
            title: 'Basic charge of tax',
            text: 'Subject to the other provisions of this Act, there shall be charged for each year of income...',
            cross_references: [
                { type: 'subject_to', target: 'entire_act', condition: 'other provisions' },
                { type: 'refers_to', target: 'section_2_definitions' },
                { type: 'modified_by', target: 'finance_act_2024_section_6' }
            ]
        });

        // Schedule references
        this.addSection('income_tax_act_2023_section_44', {
            title: 'Investment rebate',
            text: 'An assessee shall be allowed rebate as specified in the First Schedule...',
            cross_references: [
                { type: 'refers_to', target: 'first_schedule_part_1', condition: 'investment_type' },
                { type: 'subject_to', target: 'section_44_conditions' },
                { type: 'maximum_limit', target: 'first_schedule_limits' }
            ]
        });

        // Amendment references
        this.addAmendment('finance_act_2024_section_6', {
            amends: 'income_tax_act_2023_section_5',
            amendment_type: 'rate_modification',
            effective_date: '2024-07-01',
            text: 'In section 5 of the Income Tax Act 2023, the tax rates shall be as per Schedule 3...',
            cross_references: [
                { type: 'replaces', target: 'original_tax_rates' },
                { type: 'refers_to', target: 'finance_act_2024_schedule_3' }
            ]
        });

        // Schedule cross-references
        this.addSchedule('first_schedule_part_1', {
            title: 'Investment allowances and rebates',
            parent_act: 'income_tax_act_2023',
            cross_references: [
                { type: 'implemented_by', target: 'nbr_circular_investment_rules' },
                { type: 'limits_defined_in', target: 'first_schedule_part_3' },
                { type: 'conditions_in', target: 'section_44_subsection_4' }
            ]
        });

        // Complex conditional references
        this.addConditionalReference('section_52_tds_salary', {
            base_rule: 'TDS on salary payments',
            conditions: [
                {
                    if: 'monthly_salary > 25000',
                    then: { type: 'refers_to', target: 'tds_rate_schedule' },
                    unless: { type: 'exempt_under', target: 'section_52_exemptions' }
                },
                {
                    if: 'employer_type = government',
                    then: { type: 'follows', target: 'government_pay_rules' },
                    and: { type: 'subject_to', target: 'section_52_subsection_3' }
                }
            ]
        });
    }

    /**
     * Add a legal section with full cross-reference tracking
     */
    addSection(sectionId, sectionData) {
        const section = {
            id: sectionId,
            ...sectionData,
            parsed_references: this.parseReferences(sectionData.text),
            citation_strength: this.calculateCitationStrength(sectionData.cross_references),
            last_updated: new Date().toISOString()
        };

        this.legalDatabase.set(sectionId, section);

        // Process cross-references
        if (sectionData.cross_references) {
            sectionData.cross_references.forEach(ref => {
                this.addCrossReference(sectionId, ref.type, ref.target, ref.condition);
            });
        }
    }

    /**
     * Parse natural language references from legal text
     */
    parseReferences(legalText) {
        const referencePatterns = [
            // Section references
            /section\s+(\d+)/gi,
            /ধারা\s+([০-৯\d]+)/g,
            
            // Schedule references  
            /schedule\s+(\d+)/gi,
            /তফসিল[－\-\s]*([০-৯\d]+)/g,
            
            // Conditional references
            /subject to\s+([^,\.]+)/gi,
            /সাপেক্ষে\s+([^,।]+)/g,
            
            // Cross-act references
            /as per\s+([^,\.]+)/gi,
            /অনুযায়ী\s+([^,।]+)/g,
            
            // Amendment references
            /as amended by\s+([^,\.]+)/gi,
            /সংশোধিত\s+([^,।]+)/g
        ];

        const references = [];
        
        referencePatterns.forEach(pattern => {
            const matches = legalText.matchAll(pattern);
            for (const match of matches) {
                references.push({
                    type: this.classifyReferenceType(match[0]),
                    text: match[0],
                    target: match[1],
                    position: match.index
                });
            }
        });

        return references;
    }

    /**
     * Find the complete legal path for a query
     */
    findLegalPath(query, context = {}) {
        const path = {
            query: query,
            context: context,
            legal_chain: [],
            citations: [],
            conditions: [],
            final_authority: null,
            confidence: 0
        };

        try {
            // Step 1: Identify primary legal provision
            const primaryProvision = this.identifyPrimaryProvision(query);
            if (!primaryProvision) {
                throw new Error('No primary legal provision found');
            }

            path.legal_chain.push({
                step: 1,
                type: 'primary_provision',
                section: primaryProvision.id,
                title: primaryProvision.title,
                authority: this.getLegalAuthority(primaryProvision.id)
            });

            // Step 2: Check for amendments
            const amendments = this.findAmendments(primaryProvision.id);
            amendments.forEach((amendment, index) => {
                path.legal_chain.push({
                    step: path.legal_chain.length + 1,
                    type: 'amendment',
                    section: amendment.id,
                    amends: amendment.amends,
                    effective_date: amendment.effective_date,
                    legal_effect: 'modifies_primary_provision'
                });
            });

            // Step 3: Follow cross-references
            const crossRefs = this.followCrossReferences(primaryProvision.id, context);
            crossRefs.forEach(ref => {
                path.legal_chain.push({
                    step: path.legal_chain.length + 1,
                    type: 'cross_reference',
                    from: ref.source,
                    to: ref.target,
                    relationship: ref.type,
                    condition: ref.condition
                });
            });

            // Step 4: Apply conditions and exceptions
            const conditions = this.evaluateConditions(primaryProvision.id, context);
            path.conditions = conditions;

            // Step 5: Determine final authority
            path.final_authority = this.determineFinalAuthority(path.legal_chain);
            
            // Step 6: Generate citations
            path.citations = this.generateCitations(path.legal_chain);
            
            // Step 7: Calculate confidence
            path.confidence = this.calculatePathConfidence(path);

        } catch (error) {
            path.error = error.message;
            path.confidence = 0;
        }

        return path;
    }

    /**
     * Generate proper legal citations for the path
     */
    generateCitations(legalChain) {
        const citations = [];
        
        legalChain.forEach(step => {
            if (step.type === 'primary_provision') {
                citations.push({
                    type: 'primary',
                    citation: this.formatCitation(step.section),
                    authority: step.authority,
                    weight: 'high'
                });
            } else if (step.type === 'amendment') {
                citations.push({
                    type: 'amendment',
                    citation: this.formatCitation(step.section),
                    amends: this.formatCitation(step.amends),
                    weight: 'high'
                });
            } else if (step.type === 'cross_reference') {
                citations.push({
                    type: 'supporting',
                    citation: this.formatCitation(step.to),
                    relationship: step.relationship,
                    weight: 'medium'
                });
            }
        });

        return this.sortCitationsByWeight(citations);
    }

    /**
     * Format proper legal citation
     */
    formatCitation(sectionId) {
        const section = this.legalDatabase.get(sectionId);
        if (!section) return sectionId;

        // Extract document and section info
        const parts = sectionId.split('_');
        const actName = parts.slice(0, -2).join(' ').replace(/_/g, ' ');
        const sectionNumber = parts[parts.length - 1];

        // Format according to legal citation standards
        if (sectionId.includes('income_tax_act_2023')) {
            return `Income Tax Act, 2023, Section ${sectionNumber}`;
        } else if (sectionId.includes('finance_act_2024')) {
            return `Finance Act, 2024, Section ${sectionNumber}`;
        } else if (sectionId.includes('schedule')) {
            return `${actName}, Schedule ${sectionNumber}`;
        }

        return sectionId;
    }

    /**
     * Validate legal reasoning path
     */
    validateLegalPath(path) {
        const validation = {
            is_valid: true,
            issues: [],
            recommendations: [],
            confidence_score: path.confidence
        };

        // Check for circular references
        const sections = path.legal_chain.map(step => step.section);
        const uniqueSections = new Set(sections);
        if (sections.length !== uniqueSections.size) {
            validation.issues.push('Circular reference detected in legal chain');
            validation.is_valid = false;
        }

        // Check for conflicting authorities
        const authorities = path.legal_chain.map(step => step.authority).filter(Boolean);
        const conflictingAuthorities = authorities.filter(auth => 
            authorities.some(other => auth !== other && this.checkAuthorityConflict(auth, other))
        );
        
        if (conflictingAuthorities.length > 0) {
            validation.issues.push(`Conflicting authorities: ${conflictingAuthorities.join(', ')}`);
            validation.recommendations.push('Review hierarchy of legal authorities');
        }

        // Check for outdated references
        const outdatedRefs = path.legal_chain.filter(step => 
            step.effective_date && new Date(step.effective_date) < new Date('2023-07-01')
        );
        
        if (outdatedRefs.length > 0) {
            validation.issues.push('Path contains potentially outdated legal references');
            validation.recommendations.push('Verify current status of all referenced provisions');
        }

        return validation;
    }

    /**
     * Search for legal provisions using natural language
     */
    searchLegalProvisions(query, filters = {}) {
        const results = [];
        
        for (const [id, section] of this.legalDatabase) {
            const relevanceScore = this.calculateRelevance(query, section);
            
            if (relevanceScore > 0.3) { // Threshold for relevance
                results.push({
                    id: id,
                    title: section.title,
                    relevance: relevanceScore,
                    summary: this.generateSummary(section),
                    cross_references: section.cross_references || [],
                    citation: this.formatCitation(id)
                });
            }
        }

        return results.sort((a, b) => b.relevance - a.relevance);
    }

    /**
     * Helper methods
     */
    identifyPrimaryProvision(query) {
        // Simplified - in real implementation, use NLP/ML
        const provisions = this.searchLegalProvisions(query);
        return provisions.length > 0 ? this.legalDatabase.get(provisions[0].id) : null;
    }

    findAmendments(sectionId) {
        const amendments = [];
        for (const [id, amendment] of this.amendments) {
            if (amendment.amends === sectionId) {
                amendments.push(amendment);
            }
        }
        return amendments.sort((a, b) => new Date(b.effective_date) - new Date(a.effective_date));
    }

    followCrossReferences(sectionId, context, maxDepth = 3, currentDepth = 0) {
        if (currentDepth >= maxDepth) return [];
        
        const references = [];
        for (const [id, ref] of this.crossReferences) {
            if (ref.source === sectionId) {
                references.push(ref);
                // Recursively follow references
                const nestedRefs = this.followCrossReferences(ref.target, context, maxDepth, currentDepth + 1);
                references.push(...nestedRefs);
            }
        }
        return references;
    }

    calculateRelevance(query, section) {
        // Simplified relevance calculation
        const queryWords = query.toLowerCase().split(' ');
        const sectionText = (section.title + ' ' + (section.text || '')).toLowerCase();
        
        let matches = 0;
        queryWords.forEach(word => {
            if (sectionText.includes(word)) matches++;
        });
        
        return matches / queryWords.length;
    }

    determineLegalEffect(referenceType) {
        const effects = {
            'refers_to': 'provides_additional_detail',
            'amended_by': 'modifies_original_provision',
            'subject_to': 'creates_conditional_dependency',
            'unless': 'creates_exception',
            'provided_that': 'adds_qualification'
        };
        return effects[referenceType] || 'unknown_effect';
    }

    // Additional helper methods would be implemented here...
    addAmendment(id, data) { this.amendments.set(id, data); }
    addSchedule(id, data) { this.schedules.set(id, data); }
    addConditionalReference(id, data) { /* Implementation */ }
    buildReverseReference(target, source, type) { /* Implementation */ }
    calculateCitationStrength(refs) { return refs ? refs.length * 0.1 : 0; }
    classifyReferenceType(text) { return 'general_reference'; }
    getLegalAuthority(id) { return 'Parliament of Bangladesh'; }
    evaluateConditions(id, context) { return []; }
    determineFinalAuthority(chain) { return chain[0]?.authority || 'Unknown'; }
    calculatePathConfidence(path) { return Math.min(0.9, path.legal_chain.length * 0.1); }
    sortCitationsByWeight(citations) { return citations.sort((a, b) => b.weight === 'high' ? 1 : -1); }
    checkAuthorityConflict(auth1, auth2) { return false; }
    generateSummary(section) { return section.title; }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LegalCrossReferenceEngine;
}

// Example usage
if (typeof window !== 'undefined' || require.main === module) {
    console.log('🏛️ Legal Cross-Reference Engine - Foundation System');
    console.log('==================================================\n');
    
    const legalEngine = new LegalCrossReferenceEngine();
    
    // Test legal path finding
    console.log('📖 Finding Legal Path for Tax Rate Calculation:');
    const path = legalEngine.findLegalPath('individual income tax rates', { 
        income: 1000000, 
        taxpayer_type: 'individual' 
    });
    console.log(JSON.stringify(path, null, 2));
    
    console.log('\n🔍 Searching Legal Provisions:');
    const searchResults = legalEngine.searchLegalProvisions('investment rebate');
    console.log(JSON.stringify(searchResults, null, 2));
}