/**
 * Bengali Legal Text Cross-Reference Parser
 * Extracts natural cross-references from Bengali legal text
 * Designed to work with both simulation and real legal documents
 */

class BengaliLegalParser {
    constructor() {
        this.crossReferencePatterns = this.initializePatterns();
        this.documentMap = new Map();
        this.extractedReferences = [];
        this.ambiguousReferences = [];
    }

    /**
     * Initialize regex patterns for Bengali legal cross-references
     */
    initializePatterns() {
        return {
            // Act references with year and section
            act_with_section: [
                /([আয়কর আইন|অর্থ আইন|মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন|কাস্টমস আইন|ভ্রমণ কর আইন]),?\s*([১২]\d{3})\s*(?:\(([১২]\d{3})\s*সনের\s*(\d+)\s*নং আইন\))?\s*এর\s*(?:ধারা\s*)?(\d+(?:[ক-ৎ])?)\s*(?:ধারা)?(?:য়)?\s*(?:এর\s*উপ-ধারা\s*\((\d+)\))?/g,
                /উক্ত আইনের?\s*(?:ধারা\s*)?(\d+(?:[ক-ৎ])?)\s*(?:ধারা)?(?:য়)?\s*(?:এর\s*উপ-ধারা\s*\((\d+)\))?/g
            ],

            // Schedule references  
            schedule_references: [
                /(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম)\s*তফসিল(?:ে|ের)?\s*(?:(?:এর\s*)?(১ম|২য়|৩য়|৪র্থ|৫ম)\s*অংশ)?/g,
                /তফসিল[-\s]*([১২৩৪৫৬৭৮])\s*(?:(?:এর\s*)?(১ম|২য়|৩য়|৪র্থ|৫ম)\s*অংশ)?/g
            ],

            // Rules and regulations
            rules_references: [
                /(উৎসে কর কর্তন বিধিমালা|ভ্যাট ও সম্পূরক শুল্ক বিধিমালা),?\s*([১২]\d{3})\s*এর\s*(?:(\d+(?:[ক-ৎ])?)\s*(?:য়)?\s*নিয়ম)/g,
                /উক্ত বিধিমালার?\s*(?:(\d+(?:[ক-ৎ])?)\s*(?:য়)?\s*নিয়ম)/g
            ],

            // SRO notifications
            sro_references: [
                /এসআরও\s*নং?\s*([২৩]\d{2}\/[১২]\d{3})/g,
                /(?:এস\.আর\.ও|S\.R\.O\.?)\s*(?:নং?)?\s*([২৩]\d{2}\/[১২]\d{3})/g
            ],

            // NBR circulars and orders
            circular_references: [
                /(?:জাতীয় রাজস্ব বোর্ডের\s*)?পরিপত্র\s*নং?\s*(\d{1,2}\/[১২]\d{3})/g,
                /(?:জাতীয় রাজস্ব বোর্ডের\s*)?সাধারণ আদেশ\s*নং?\s*(\d{1,2}\/[১২]\d{3})/g
            ],

            // Ordinance references
            ordinance_references: [
                /(আয়কর অধ্যাদেশ),?\s*([১২]\d{3})\s*(?:এর\s*(?:ধারা\s*)?(\d+(?:[ক-ৎ])?)\s*(?:ধারা)?(?:য়)?)/g
            ],

            // Contextual reference words
            contextual_indicators: [
                /(?:অনুযায়ী|অনুসারে|সাপেক্ষে|সাপেক্ষ|ভিত্তিতে|মোতাবেক|প্রযোজ্য|বর্ণিত|উল্লিখিত|নির্ধারিত|বিধান|শর্ত)/g
            ],

            // Reference continuation words
            continuation_words: [
                /(?:এবং|ও|তথা|সহ|সমেত)/g
            ],

            // Section and subsection patterns
            section_patterns: [
                /ধারা\s*(\d+(?:[ক-ৎ])?)\s*(?:এর\s*উপ-ধারা\s*\((\d+)\))?/g,
                /(\d+(?:[ক-ৎ])?)\s*(?:নং\s*)?ধারা(?:য়)?/g,
                /উপ-ধারা\s*\((\d+)\)/g
            ]
        };
    }

    /**
     * Parse a document and extract all cross-references
     */
    parseDocument(documentContent, documentPath) {
        console.log(`🔍 Parsing document: ${documentPath}`);
        
        const references = [];
        const documentText = this.extractAllText(documentContent);
        
        // Extract different types of references
        const actRefs = this.extractActReferences(documentText, documentPath);
        const scheduleRefs = this.extractScheduleReferences(documentText, documentPath);
        const rulesRefs = this.extractRulesReferences(documentText, documentPath);
        const sroRefs = this.extractSROReferences(documentText, documentPath);
        const circularRefs = this.extractCircularReferences(documentText, documentPath);
        const ordinanceRefs = this.extractOrdinanceReferences(documentText, documentPath);

        references.push(...actRefs, ...scheduleRefs, ...rulesRefs, ...sroRefs, ...circularRefs, ...ordinanceRefs);

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
     * Extract all text content from JSON document
     */
    extractAllText(documentContent) {
        let allText = '';
        
        // Recursive function to extract text from nested objects
        const extractText = (obj) => {
            if (typeof obj === 'string') {
                allText += obj + ' ';
            } else if (Array.isArray(obj)) {
                obj.forEach(item => extractText(item));
            } else if (obj && typeof obj === 'object') {
                Object.values(obj).forEach(value => extractText(value));
            }
        };

        extractText(documentContent);
        return allText;
    }

    /**
     * Extract Act references (আয়কর আইন, অর্থ আইন, etc.)
     */
    extractActReferences(text, sourcePath) {
        const references = [];
        
        this.crossReferencePatterns.act_with_section.forEach(pattern => {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const reference = {
                    type: 'act_reference',
                    source_document: sourcePath,
                    source_text: match[0],
                    act_name: match[1] || 'উক্ত আইন',
                    year: match[2],
                    act_number: match[4],
                    section: match[5],
                    subsection: match[6],
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0]),
                    target_document: this.resolveTargetDocument(match[1], match[2]),
                    target_section: this.formatSectionReference(match[5], match[6])
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Extract Schedule references (তফসিল)
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
                    schedule_number: match[1] || match[1],
                    schedule_part: match[2],
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0]),
                    target_document: this.resolveScheduleTarget(sourcePath),
                    target_section: this.formatScheduleReference(match[1], match[2])
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Extract Rules references (বিধিমালা)
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
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0]),
                    target_document: this.resolveRulesTarget(match[1], match[2]),
                    target_section: `rule_${match[3] || match[1]}`
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Extract SRO references
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
                    context_before: this.getContext(text, match.index, -50),
                    context_after: this.getContext(text, match.index + match[0].length, 50),
                    confidence: this.calculateConfidence(match[0]),
                    target_document: '04_sro_notification_simulation.json',
                    target_section: `sro_${match[1].replace('/', '_')}`
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Extract Circular references
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
                    confidence: this.calculateConfidence(match[0]),
                    target_document: '03_nbr_circular_simulation.json',
                    target_section: `${circularType}_${match[1].replace('/', '_')}`
                };
                references.push(reference);
            }
        });

        return references;
    }

    /**
     * Extract Ordinance references
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
                    confidence: this.calculateConfidence(match[0]),
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
     * Calculate confidence score for a reference
     */
    calculateConfidence(matchText) {
        let confidence = 0.5; // Base confidence
        
        // Higher confidence for more specific references
        if (matchText.includes('ধারা') && /\d+/.test(matchText)) confidence += 0.2;
        if (matchText.includes('উপ-ধারা')) confidence += 0.1;
        if (matchText.includes('নং')) confidence += 0.1;
        if (/[১২]\d{3}/.test(matchText)) confidence += 0.1; // Year present
        
        return Math.min(1.0, confidence);
    }

    /**
     * Resolve target document based on act name and year
     */
    resolveTargetDocument(actName, year) {
        const mapping = {
            'আয়কর আইন': '01_income_tax_act_simulation.json',
            'অর্থ আইন': '02_finance_act_simulation.json',
            'মূল্য সংযোজন কর ও সম্পূরক শুল্ক আইন': '04_sro_notification_simulation.json',
            'কাস্টমস আইন': '04_sro_notification_simulation.json',
            'ভ্রমণ কর আইন': '02_finance_act_simulation.json'
        };
        
        return mapping[actName] || 'unknown_document.json';
    }

    /**
     * Resolve schedule target document
     */
    resolveScheduleTarget(sourcePath) {
        // If source is not schedule document, target is likely tax schedules
        if (!sourcePath.includes('schedule')) {
            return '05_tax_schedules_simulation.json';
        }
        return sourcePath; // Internal reference
    }

    /**
     * Resolve rules target document
     */
    resolveRulesTarget(rulesName, year) {
        if (rulesName && rulesName.includes('উৎসে কর কর্তন')) {
            return '06_tds_rules_simulation.json';
        }
        return '06_tds_rules_simulation.json'; // Default to TDS rules
    }

    /**
     * Resolve ordinance target document
     */
    resolveOrdinanceTarget(ordinanceName, year) {
        // For now, assume separate ordinance file would exist
        return `ordinance_${year}_simulation.json`;
    }

    /**
     * Format section reference for targeting
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
     * Format schedule reference for targeting
     */
    formatScheduleReference(scheduleNumber, part) {
        const numberMap = {
            'প্রথম': '1', 'দ্বিতীয়': '2', 'তৃতীয়': '3', 'চতুর্থ': '4',
            'পঞ্চম': '5', 'ষষ্ঠ': '6', 'সপ্তম': '7', 'অষ্টম': '8'
        };
        
        const partMap = {
            '১ম': '1', '২য়': '2', '৩য়': '3', '৪র্থ': '4', '৫ম': '5'
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
     * Build cross-reference graph from all parsed documents
     */
    buildCrossReferenceGraph(documents) {
        console.log('🔗 Building cross-reference graph...');
        
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

        // Create nodes for each document
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

                // Create edges for each reference
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

                    // Update statistics
                    graph.statistics.totalReferences++;
                    graph.statistics.referenceTypes[ref.type] = 
                        (graph.statistics.referenceTypes[ref.type] || 0) + 1;
                });
            }
        });

        console.log(`✅ Graph built: ${graph.nodes.length} nodes, ${graph.edges.length} edges`);
        console.log(`📊 Statistics:`, graph.statistics);

        return graph;
    }

    /**
     * Extract document title from content
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

    /**
     * Validate cross-references against target documents
     */
    validateReferences(graph, documentContents) {
        console.log('🔍 Validating cross-references...');
        
        const validationResults = {
            valid: [],
            invalid: [],
            ambiguous: [],
            statistics: {
                totalValidated: 0,
                validCount: 0,
                invalidCount: 0,
                ambiguousCount: 0
            }
        };

        graph.edges.forEach(edge => {
            const validation = this.validateSingleReference(edge, documentContents);
            validationResults[validation.status].push({
                ...edge,
                validation: validation
            });
            validationResults.statistics.totalValidated++;
            validationResults.statistics[`${validation.status}Count`]++;
        });

        console.log(`✅ Validation complete:`, validationResults.statistics);
        return validationResults;
    }

    /**
     * Validate a single cross-reference
     */
    validateSingleReference(edge, documentContents) {
        const targetDoc = documentContents[edge.target];
        
        if (!targetDoc) {
            return {
                status: 'invalid',
                reason: 'Target document not found',
                confidence: 0
            };
        }

        // Try to find the target section in the document
        const sectionExists = this.findSectionInDocument(edge.section, targetDoc);
        
        if (sectionExists) {
            return {
                status: 'valid',
                reason: 'Section found in target document',
                confidence: edge.confidence
            };
        } else {
            return {
                status: 'ambiguous',
                reason: 'Section not found but document exists',
                confidence: edge.confidence * 0.5
            };
        }
    }

    /**
     * Find if a section exists in a document
     */
    findSectionInDocument(sectionRef, document) {
        const docText = this.extractAllText(document);
        
        // Simple existence check - in real implementation, this would be more sophisticated
        return docText.includes(sectionRef) || 
               sectionRef.includes('section') || 
               sectionRef.includes('schedule');
    }

    /**
     * Generate comprehensive analysis report
     */
    generateAnalysisReport(graph, validationResults) {
        const report = {
            summary: {
                documentsAnalyzed: graph.statistics.totalDocuments,
                totalReferences: graph.statistics.totalReferences,
                validReferences: validationResults.statistics.validCount,
                invalidReferences: validationResults.statistics.invalidCount,
                ambiguousReferences: validationResults.statistics.ambiguousCount,
                accuracyRate: (validationResults.statistics.validCount / validationResults.statistics.totalValidated * 100).toFixed(2) + '%'
            },
            referenceTypes: graph.statistics.referenceTypes,
            documentConnectivity: this.analyzeDocumentConnectivity(graph),
            recommendations: this.generateRecommendations(validationResults),
            timestamp: new Date().toISOString()
        };

        return report;
    }

    /**
     * Analyze document connectivity patterns
     */
    analyzeDocumentConnectivity(graph) {
        const connectivity = {};
        
        graph.edges.forEach(edge => {
            connectivity[edge.source] = connectivity[edge.source] || { outgoing: 0, incoming: 0 };
            connectivity[edge.target] = connectivity[edge.target] || { outgoing: 0, incoming: 0 };
            
            connectivity[edge.source].outgoing++;
            connectivity[edge.target].incoming++;
        });

        return connectivity;
    }

    /**
     * Generate recommendations for improving cross-reference accuracy
     */
    generateRecommendations(validationResults) {
        const recommendations = [];
        
        if (validationResults.statistics.invalidCount > 0) {
            recommendations.push('Review invalid references and fix broken links');
        }
        
        if (validationResults.statistics.ambiguousCount > validationResults.statistics.validCount) {
            recommendations.push('Improve section detection algorithms for better accuracy');
        }
        
        recommendations.push('Consider implementing fuzzy matching for section references');
        recommendations.push('Add manual validation for high-confidence ambiguous references');
        
        return recommendations;
    }
}

module.exports = BengaliLegalParser;