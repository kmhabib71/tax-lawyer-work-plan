/**
 * Fixed Bengali Legal Text Cross-Reference Parser
 * Correctly extracts natural cross-references from Bengali legal text
 * Fixed regex patterns based on actual document content analysis
 */

class FixedBengaliParser {
    constructor() {
        this.crossReferencePatterns = this.initializeFixedPatterns();
        this.documentMap = new Map();
        this.extractedReferences = [];
    }

    /**
     * Fixed regex patterns based on actual Bengali legal text patterns
     */
    initializeFixedPatterns() {
        return {
            // Act references - Fixed patterns based on actual text
            act_references: [
                // Pattern 1: আয়কর আইন, ২০২৩ (২০২৩ সনের ১২ নং আইন) এর ৮৫তম ধারা
                /(আয়কর আইন|অর্থ আইন|কোম্পানি আইন|প্রতিবন্ধী ব্যক্তির অধিকার ও সুরক্ষা আইন),\s*([১২০-৯]\d{3})\s*\(([১২০-৯]\d{3})\s*সনের\s*(\d+)\s*নং আইন\)\s*এর\s*(\d+)(?:তম|ম)?\s*ধারা(?:য়|র|তে)?(?:\s*(?:এর\s*)?উপ-ধারা\s*\((\d+)\))?/g,
                
                // Pattern 2: আয়কর আইন, ২০২৩ এর ৮৫তম ধারা
                /(আয়কর আইন|অর্থ আইন|কোম্পানি আইন|প্রতিবন্ধী ব্যক্তির অধিকার ও সুরক্ষা আইন),\s*([১২০-৯]\d{3})\s*এর\s*(\d+)(?:তম|ম)?\s*ধারা(?:য়|র|তে)?(?:\s*(?:এর\s*)?উপ-ধারা\s*\((\d+)\))?/g,
                
                // Pattern 3: উক্ত আইনের ৮৫তম ধারা
                /উক্ত আইনে?র?\s*(\d+)\s*(?:তম|ম)?\s*ধারা(?:য়|র|তে)?(?:\s*(?:এর\s*)?উপ-ধারা\s*\((\d+)\))?/g,
                
                // Pattern 4: এই আইনের ৮৫তম ধারা
                /এই আইনে?র?\s*(\d+)\s*(?:তম|ম)?\s*ধারা(?:য়|র|তে)?(?:\s*(?:এর\s*)?উপ-ধারা\s*\((\d+)\))?/g,

                // Pattern 5: আয়কর আইন, ২০২৩ এর অধীন
                /(আয়কর আইন|অর্থ আইন|কোম্পানি আইন),\s*([১২০-৯]\d{3})\s*(?:\([^)]*\))?\s*এর\s*অধীন/g
            ],

            // Rules and regulations - Fixed
            rules_references: [
                // Pattern 1: উৎসে কর কর্তন বিধিমালা, ২০২৪ এর ৩য় নিয়ম
                /(উৎসে কর কর্তন বিধিমালা|ভ্যাট ও সম্পূরক শুল্ক বিধিমালা|[^,]*বিধিমালা),\s*([১২০-৯]\d{3})\s*এর\s*(\d+)(?:য়|র্থ|তম)?\s*(?:ও\s*(\d+)(?:র্থ|তম)?\s*)?নিয়ম/g,
                
                // Pattern 2: উক্ত বিধিমালার ৩য় নিয়ম
                /উক্ত বিধিমালার?\s*(\d+)(?:য়|র্থ|তম)?\s*(?:ও\s*(\d+)(?:র্থ|তম)?\s*)?নিয়ম/g
            ],

            // SRO notifications - Fixed  
            sro_references: [
                // Pattern 1: এসআরও নং ২৪১/২০২৪
                /এসআরও\s*নং?\s*([২৩]\d{2}\/[১২০-৯]\d{3})/g,
                
                // Pattern 2: এসআরও নং ২৪১/২০২৪ এর ২য় ধারা
                /এসআরও\s*নং?\s*([২৩]\d{2}\/[১২০-৯]\d{3})\s*এর?\s*(\d+)(?:তম|য়|ম)?\s*ধারা/g
            ],

            // NBR circulars and orders - Fixed
            circular_references: [
                // Pattern 1: জাতীয় রাজস্ব বোর্ডের পরিপত্র নং ০৯/২০২৪
                /(?:জাতীয় রাজস্ব বোর্ডের\s*)?পরিপত্র\s*নং?\s*(\d{1,2}\/[১২০-৯]\d{3})/g,
                
                // Pattern 2: জাতীয় রাজস্ব বোর্ডের সাধারণ আদেশ নং ১৫/২০২৪
                /(?:জাতীয় রাজস্ব বোর্ডের\s*)?সাধারণ আদেশ\s*নং?\s*(\d{1,2}\/[১২০-৯]\d{3})/g
            ],

            // Schedule references - Fixed
            schedule_references: [
                // Pattern 1: প্রথম তফসিলের ৩য় অংশ
                /(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম)\s*তফসিল(?:ে|ের|এর)?\s*(?:(\d+)(?:য়|ম|র্থ)\s*অংশ)?/g,
                
                // Pattern 2: এই আইনের প্রথম তফসিল
                /এই আইনের\s*(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম)\s*তফসিল(?:ে|ের|এর)?/g,
                
                // Pattern 3: তৃতীয় তফসিলের বিধান
                /(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম)\s*তফসিলের\s*বিধান/g
            ],

            // Ordinance references - Fixed
            ordinance_references: [
                // Pattern 1: আয়কর অধ্যাদেশ, ১৯৮৪ এর ২৮৫ ধারা
                /(আয়কর অধ্যাদেশ|[^,]*অধ্যাদেশ),\s*([১২০-৯]\d{3})\s*এর?\s*(\d+)\s*ধারা(?:য়|র)?/g
            ]
        };
    }

    /**
     * Main parsing function with improved detection
     */
    parseDocument(documentContent, documentPath) {
        console.log(`🔍 Parsing document: ${documentPath}`);
        
        const references = [];
        const documentText = this.extractAllText(documentContent);
        
        // Extract different types of references with fixed patterns
        references.push(...this.extractActReferences(documentText, documentPath));
        references.push(...this.extractRulesReferences(documentText, documentPath));
        references.push(...this.extractSROReferences(documentText, documentPath));
        references.push(...this.extractCircularReferences(documentText, documentPath));
        references.push(...this.extractScheduleReferences(documentText, documentPath));
        references.push(...this.extractOrdinanceReferences(documentText, documentPath));

        // Store document references
        this.documentMap.set(documentPath, {
            content: documentContent,
            text: documentText,
            references: references,
            totalReferences: references.length
        });

        console.log(`✅ Found ${references.length} references in ${documentPath}`);
        return references;
    }

    /**
     * Extract all text content from JSON document recursively
     */
    extractAllText(documentContent) {
        let allText = '';
        
        const extractText = (obj, depth = 0) => {
            if (depth > 10) return; // Prevent infinite recursion
            
            if (typeof obj === 'string') {
                allText += obj + ' ';
            } else if (Array.isArray(obj)) {
                obj.forEach(item => extractText(item, depth + 1));
            } else if (obj && typeof obj === 'object') {
                Object.values(obj).forEach(value => extractText(value, depth + 1));
            }
        };

        extractText(documentContent);
        return allText;
    }

    /**
     * Enhanced Act references extraction with fixed patterns
     */
    extractActReferences(text, sourcePath) {
        const references = [];
        
        this.crossReferencePatterns.act_references.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                let reference;
                
                if (match[1] && match[2]) {
                    // Full act reference with name and year
                    reference = {
                        type: 'act_reference',
                        source_document: sourcePath,
                        source_text: match[0],
                        act_name: match[1],
                        year: match[2] || match[3],
                        act_number: match[4],
                        section: match[5] || match[3] || match[1],
                        subsection: match[6] || match[4] || match[2],
                        context_before: this.getContext(text, match.index, -50),
                        context_after: this.getContext(text, match.index + match[0].length, 50),
                        confidence: this.calculateConfidence(match[0], 'act'),
                        target_document: this.resolveTargetDocument(match[1], match[2] || match[3]),
                        target_section: this.formatSectionReference(match[5] || match[3] || match[1], match[6] || match[4] || match[2])
                    };
                } else {
                    // Context reference (উক্ত আইন, এই আইন)
                    reference = {
                        type: 'contextual_act_reference',
                        source_document: sourcePath,
                        source_text: match[0],
                        act_name: match[0].includes('উক্ত') ? 'উক্ত আইন' : 'এই আইন',
                        section: match[1],
                        subsection: match[2],
                        context_before: this.getContext(text, match.index, -50),
                        context_after: this.getContext(text, match.index + match[0].length, 50),
                        confidence: this.calculateConfidence(match[0], 'contextual_act'),
                        target_document: this.resolveContextualTarget(sourcePath),
                        target_section: this.formatSectionReference(match[1], match[2])
                    };
                }
                
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Enhanced Rules references extraction
     */
    extractRulesReferences(text, sourcePath) {
        const references = [];
        
        this.crossReferencePatterns.rules_references.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const reference = {
                    type: 'rules_reference',
                    source_document: sourcePath,
                    source_text: match[0],
                    rules_name: match[1] || 'উক্ত বিধিমালা',
                    year: match[2],
                    rule_number: match[3] || match[1],
                    rule_number_2: match[4],
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0], 'rules'),
                    target_document: this.resolveRulesTarget(match[1], match[2]),
                    target_section: `rule_${match[3] || match[1]}${match[4] ? '_and_' + match[4] : ''}`
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Enhanced SRO references extraction
     */
    extractSROReferences(text, sourcePath) {
        const references = [];
        
        this.crossReferencePatterns.sro_references.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const reference = {
                    type: 'sro_reference',
                    source_document: sourcePath,
                    source_text: match[0],
                    sro_number: match[1],
                    section: match[2],
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0], 'sro'),
                    target_document: '04_sro_notification_simulation.json',
                    target_section: `sro_${match[1].replace('/', '_')}${match[2] ? '_section_' + match[2] : ''}`
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Enhanced Circular references extraction
     */
    extractCircularReferences(text, sourcePath) {
        const references = [];
        
        this.crossReferencePatterns.circular_references.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const circularType = match[0].includes('সাধারণ আদেশ') ? 'general_order' : 'circular';
                const reference = {
                    type: 'circular_reference',
                    circular_type: circularType,
                    source_document: sourcePath,
                    source_text: match[0],
                    circular_number: match[1],
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0], 'circular'),
                    target_document: '03_nbr_circular_simulation.json',
                    target_section: `${circularType}_${match[1].replace('/', '_')}`
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Enhanced Schedule references extraction
     */
    extractScheduleReferences(text, sourcePath) {
        const references = [];
        
        this.crossReferencePatterns.schedule_references.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const reference = {
                    type: 'schedule_reference',
                    source_document: sourcePath,
                    source_text: match[0],
                    schedule_number: match[1],
                    schedule_part: match[2],
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0], 'schedule'),
                    target_document: this.resolveScheduleTarget(sourcePath),
                    target_section: this.formatScheduleReference(match[1], match[2])
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Enhanced Ordinance references extraction
     */
    extractOrdinanceReferences(text, sourcePath) {
        const references = [];
        
        this.crossReferencePatterns.ordinance_references.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const reference = {
                    type: 'ordinance_reference',
                    source_document: sourcePath,
                    source_text: match[0],
                    ordinance_name: match[1],
                    year: match[2],
                    section: match[3],
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0], 'ordinance'),
                    target_document: this.resolveOrdinanceTarget(match[1], match[2]),
                    target_section: `section_${match[3]}`
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Get context around a match
     */
    getContext(text, index, length) {
        const start = Math.max(0, index + (length < 0 ? length : 0));
        const end = Math.min(text.length, index + (length > 0 ? length : 0));
        return text.substring(start, end).trim();
    }

    /**
     * Enhanced confidence calculation
     */
    calculateConfidence(matchText, type) {
        let confidence = 0.5; // Base confidence
        
        // Type-specific confidence boosts
        const typeBoosts = {
            'act': 0.3,
            'rules': 0.2, 
            'sro': 0.3,
            'circular': 0.2,
            'schedule': 0.1,
            'ordinance': 0.2,
            'contextual_act': 0.1
        };
        
        confidence += typeBoosts[type] || 0;
        
        // Content-based confidence adjustments
        if (matchText.includes('ধারা') && /\d+/.test(matchText)) confidence += 0.2;
        if (matchText.includes('উপ-ধারা')) confidence += 0.1;
        if (matchText.includes('নং')) confidence += 0.1;
        if (/[১২০-৯]\d{3}/.test(matchText)) confidence += 0.1; // Year present
        if (matchText.includes('তম')) confidence += 0.05; // Ordinal indicator
        if (matchText.includes('সনের') && matchText.includes('আইন')) confidence += 0.1; // Full act citation
        
        return Math.min(1.0, confidence);
    }

    /**
     * Resolve target document based on act name and year
     */
    resolveTargetDocument(actName, year) {
        const mapping = {
            'আয়কর আইন': '01_income_tax_act_simulation.json',
            'অর্থ আইন': '02_finance_act_simulation.json',
            'মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন': 'vat_act_simulation.json',
            'কাস্টমস আইন': 'customs_act_simulation.json',
            'ভ্রমণ কর আইন': 'travel_tax_act_simulation.json',
            'কোম্পানি আইন': 'company_act_simulation.json',
            'প্রতিবন্ধী ব্যক্তির অধিকার ও সুরক্ষা আইন': 'disability_rights_act_simulation.json'
        };
        
        return mapping[actName] || 'unknown_document.json';
    }

    /**
     * Resolve contextual target (উক্ত আইন, এই আইন)
     */
    resolveContextualTarget(sourcePath) {
        // Context references usually refer to the main act being discussed
        if (sourcePath.includes('finance_act')) {
            return '01_income_tax_act_simulation.json'; // Finance act usually amends income tax act
        }
        return sourcePath; // Self-reference
    }

    /**
     * Resolve schedule target document
     */
    resolveScheduleTarget(sourcePath) {
        if (!sourcePath.includes('schedule')) {
            return '05_tax_schedules_simulation.json';
        }
        return sourcePath;
    }

    /**
     * Resolve rules target document
     */
    resolveRulesTarget(rulesName, year) {
        if (rulesName && rulesName.includes('উৎসে কর কর্তন')) {
            return '06_tds_rules_simulation.json';
        }
        return '06_tds_rules_simulation.json';
    }

    /**
     * Resolve ordinance target document
     */
    resolveOrdinanceTarget(ordinanceName, year) {
        return `ordinance_${year}_simulation.json`;
    }

    /**
     * Format section reference
     */
    formatSectionReference(section, subsection) {
        if (section && subsection) {
            return `section_${section}_subsection_${subsection}`;
        } else if (section) {
            return `section_${section}`;
        }
        return 'unknown_section';
    }

    /**
     * Format schedule reference
     */
    formatScheduleReference(scheduleNumber, part) {
        const numberMap = {
            'প্রথম': '1', 'দ্বিতীয়': '2', 'তৃতীয়': '3', 'চতুর্থ': '4',
            'পঞ্চম': '5', 'ষষ্ঠ': '6', 'সপ্তম': '7', 'অষ্টম': '8'
        };
        
        const partMap = {
            '১': '1', '২': '2', '৩': '3', '৪': '4', '৫': '5'
        };
        
        const scheduleNum = numberMap[scheduleNumber] || scheduleNumber;
        const partNum = partMap[part] || part;
        
        if (scheduleNum && partNum) {
            return `schedule_${scheduleNum}_part_${partNum}`;
        } else if (scheduleNum) {
            return `schedule_${scheduleNum}`;
        }
        return 'unknown_schedule';
    }

    /**
     * Build comprehensive analysis
     */
    buildAnalysis(documents) {
        console.log('🔗 Building comprehensive cross-reference analysis...');
        
        const graph = this.buildCrossReferenceGraph(documents);
        const patterns = this.analyzePatterns();
        const coverage = this.analyzeCoverage();
        
        return {
            graph,
            patterns,
            coverage,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Build cross-reference graph
     */
    buildCrossReferenceGraph(documents) {
        const graph = {
            nodes: [],
            edges: [],
            statistics: {
                totalDocuments: documents.length,
                totalReferences: 0,
                referenceTypes: {},
                documentsWithReferences: 0
            }
        };

        documents.forEach(docPath => {
            const docData = this.documentMap.get(docPath);
            if (docData) {
                graph.nodes.push({
                    id: docPath,
                    type: 'document',
                    references: docData.references.length,
                    title: this.extractDocumentTitle(docData.content)
                });

                if (docData.references.length > 0) {
                    graph.statistics.documentsWithReferences++;
                }

                docData.references.forEach(ref => {
                    graph.edges.push({
                        source: docPath,
                        target: ref.target_document,
                        type: ref.type,
                        section: ref.target_section,
                        confidence: ref.confidence,
                        sourceText: ref.source_text,
                        context: ref.context_after
                    });

                    graph.statistics.totalReferences++;
                    graph.statistics.referenceTypes[ref.type] = 
                        (graph.statistics.referenceTypes[ref.type] || 0) + 1;
                });
            }
        });

        return graph;
    }

    /**
     * Analyze reference patterns
     */
    analyzePatterns() {
        const patterns = {
            mostCommonTypes: {},
            averageConfidence: {},
            documentsWithMostReferences: [],
            mostReferencedDocuments: {}
        };

        this.documentMap.forEach((docData, docPath) => {
            docData.references.forEach(ref => {
                // Track reference types
                patterns.mostCommonTypes[ref.type] = 
                    (patterns.mostCommonTypes[ref.type] || 0) + 1;
                
                // Track confidence by type
                if (!patterns.averageConfidence[ref.type]) {
                    patterns.averageConfidence[ref.type] = [];
                }
                patterns.averageConfidence[ref.type].push(ref.confidence);
                
                // Track most referenced documents
                patterns.mostReferencedDocuments[ref.target_document] = 
                    (patterns.mostReferencedDocuments[ref.target_document] || 0) + 1;
            });
        });

        // Calculate average confidence
        Object.keys(patterns.averageConfidence).forEach(type => {
            const confidences = patterns.averageConfidence[type];
            patterns.averageConfidence[type] = 
                confidences.reduce((a, b) => a + b, 0) / confidences.length;
        });

        return patterns;
    }

    /**
     * Analyze coverage
     */
    analyzeCoverage() {
        const coverage = {
            documentsWithReferences: 0,
            totalDocuments: this.documentMap.size,
            coveragePercentage: 0,
            referenceDensity: {}
        };

        this.documentMap.forEach((docData, docPath) => {
            if (docData.references.length > 0) {
                coverage.documentsWithReferences++;
            }
            
            coverage.referenceDensity[docPath] = {
                references: docData.references.length,
                textLength: docData.text.length,
                density: docData.references.length / (docData.text.length / 1000) // refs per 1000 chars
            };
        });

        coverage.coveragePercentage = 
            (coverage.documentsWithReferences / coverage.totalDocuments) * 100;

        return coverage;
    }

    /**
     * Extract document title
     */
    extractDocumentTitle(content) {
        if (content.header && content.header.title) {
            return content.header.title;
        }
        if (content.metadata && content.metadata.source) {
            return content.metadata.source;
        }
        return 'Unknown Document';
    }
}

module.exports = FixedBengaliParser;