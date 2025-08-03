/**
 * Test Script for Bengali Legal Cross-Reference Parser
 * Demonstrates parsing natural Bengali legal cross-references
 */

const fs = require('fs');
const path = require('path');
const BengaliLegalParser = require('./engine/bengali_legal_parser');

async function testCrossReferenceParser() {
    console.log('🚀 Testing Bengali Legal Cross-Reference Parser\n');
    
    const parser = new BengaliLegalParser();
    const documentsDir = './documents';
    const documentFiles = [
        '01_income_tax_act_simulation.json',
        '02_finance_act_simulation.json', 
        '03_nbr_circular_simulation.json',
        '04_sro_notification_simulation.json',
        '05_tax_schedules_simulation.json',
        '06_tds_rules_simulation.json'
    ];

    // Load all documents
    console.log('📂 Loading simulation documents...');
    const documentContents = {};
    const allReferences = [];

    for (const filename of documentFiles) {
        const filePath = path.join(documentsDir, filename);
        try {
            const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
            documentContents[filename] = content;
            
            // Parse each document for cross-references
            const references = parser.parseDocument(content, filename);
            allReferences.push(...references);
            
            console.log(`✅ Loaded: ${filename} (${references.length} references found)`);
        } catch (error) {
            console.error(`❌ Error loading ${filename}:`, error.message);
        }
    }

    console.log(`\n📊 Total references extracted: ${allReferences.length}\n`);

    // Build cross-reference graph
    const graph = parser.buildCrossReferenceGraph(documentFiles);
    
    // Validate references
    const validationResults = parser.validateReferences(graph, documentContents);
    
    // Generate analysis report
    const report = parser.generateAnalysisReport(graph, validationResults);
    
    // Display results
    displayResults(allReferences, graph, validationResults, report);
    
    // Save detailed results
    saveResults(allReferences, graph, validationResults, report);
    
    return { references: allReferences, graph, validation: validationResults, report };
}

function displayResults(references, graph, validation, report) {
    console.log('📈 ANALYSIS RESULTS\n');
    console.log('=' * 50);
    
    // Summary
    console.log('📋 SUMMARY:');
    console.log(`Documents Analyzed: ${report.summary.documentsAnalyzed}`);
    console.log(`Total References: ${report.summary.totalReferences}`);
    console.log(`Valid References: ${report.summary.validReferences}`);
    console.log(`Invalid References: ${report.summary.invalidReferences}`);
    console.log(`Ambiguous References: ${report.summary.ambiguousReferences}`);
    console.log(`Accuracy Rate: ${report.summary.accuracyRate}\n`);
    
    // Reference types breakdown
    console.log('🔍 REFERENCE TYPES:');
    Object.entries(report.referenceTypes).forEach(([type, count]) => {
        console.log(`${type}: ${count}`);
    });
    console.log('');
    
    // Sample high-confidence references
    console.log('✨ SAMPLE HIGH-CONFIDENCE REFERENCES:');
    const highConfidenceRefs = references
        .filter(ref => ref.confidence > 0.8)
        .slice(0, 5);
    
    highConfidenceRefs.forEach((ref, index) => {
        console.log(`${index + 1}. [${ref.type}] ${ref.source_text}`);
        console.log(`   Source: ${ref.source_document}`);
        console.log(`   Target: ${ref.target_document} → ${ref.target_section}`);
        console.log(`   Confidence: ${(ref.confidence * 100).toFixed(1)}%`);
        console.log(`   Context: ...${ref.context_after.substring(0, 100)}...\n`);
    });
    
    // Document connectivity
    console.log('🔗 DOCUMENT CONNECTIVITY:');
    Object.entries(report.documentConnectivity).forEach(([doc, connectivity]) => {
        console.log(`${doc}: ${connectivity.outgoing} outgoing, ${connectivity.incoming} incoming`);
    });
    console.log('');
    
    // Recommendations
    console.log('💡 RECOMMENDATIONS:');
    report.recommendations.forEach((rec, index) => {
        console.log(`${index + 1}. ${rec}`);
    });
}

function saveResults(references, graph, validation, report) {
    const outputDir = './analysis_results';
    
    // Create output directory if it doesn't exist
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Save detailed results
    fs.writeFileSync(
        path.join(outputDir, 'extracted_references.json'),
        JSON.stringify(references, null, 2)
    );
    
    fs.writeFileSync(
        path.join(outputDir, 'cross_reference_graph.json'),
        JSON.stringify(graph, null, 2)
    );
    
    fs.writeFileSync(
        path.join(outputDir, 'validation_results.json'),
        JSON.stringify(validation, null, 2)
    );
    
    fs.writeFileSync(
        path.join(outputDir, 'analysis_report.json'),
        JSON.stringify(report, null, 2)
    );
    
    // Generate CSV for easy analysis
    generateCSVReport(references, path.join(outputDir, 'references_summary.csv'));
    
    console.log(`\n💾 Results saved to: ${outputDir}/`);
}

function generateCSVReport(references, outputPath) {
    const csvHeaders = [
        'Source Document',
        'Target Document', 
        'Reference Type',
        'Source Text',
        'Target Section',
        'Confidence',
        'Context'
    ];
    
    const csvRows = references.map(ref => [
        ref.source_document,
        ref.target_document,
        ref.type,
        `"${ref.source_text}"`,
        ref.target_section,
        ref.confidence.toFixed(3),
        `"${ref.context_after ? ref.context_after.substring(0, 100).replace(/"/g, '""') : ''}"`
    ]);
    
    const csvContent = [
        csvHeaders.join(','),
        ...csvRows.map(row => row.join(','))
    ].join('\n');
    
    fs.writeFileSync(outputPath, csvContent);
}

// Demonstrate specific parsing capabilities
function demonstrateParsingCapabilities() {
    console.log('\n🔬 PARSING CAPABILITIES DEMONSTRATION\n');
    
    const parser = new BengaliLegalParser();
    
    // Test cases with natural Bengali legal text
    const testCases = [
        {
            name: 'Act Reference with Section',
            text: 'আয়কর আইন, ২০২৩ (২০২৩ সনের ১২ নং আইন) এর ৮৫তম ধারায় বর্ণিত উৎসে কর কর্তন'
        },
        {
            name: 'Finance Act Amendment',
            text: 'অর্থ আইন, ২০২৪ এর ৬ম ধারার উপ-ধারা (২) অনুযায়ী নির্ধারিত করমুক্ত সীমা'
        },
        {
            name: 'Rules Reference',
            text: 'উৎসে কর কর্তন বিধিমালা, ২০২৪ এর ৩য় নিয়ম অনুযায়ী কর কর্তন করিতে হইবে'
        },
        {
            name: 'SRO Notification',
            text: 'এসআরও নং ২৪১/২০২৪ এ বর্ণিত বিশেষ ক্ষেত্রে অতিরিক্ত শর্ত প্রযোজ্য'
        },
        {
            name: 'NBR Circular',
            text: 'জাতীয় রাজস্ব বোর্ডের পরিপত্র নং ০৯/২০২৪ এা বর্ণিত নির্দেশনা অনুসরণ'
        },
        {
            name: 'Schedule Reference',
            text: 'এই আইনের প্রথম তফসিলের ৩য় অংশে বিস্তারিতভাবে বর্ণিত'
        },
        {
            name: 'Previous Act Reference',
            text: 'উক্ত আইনের ধারা ৪ এর উপ-ধারা (১) এর দফা (ঝ) এর পরিবর্তে'
        }
    ];
    
    testCases.forEach((testCase, index) => {
        console.log(`${index + 1}. ${testCase.name}:`);
        console.log(`   Text: "${testCase.text}"`);
        
        // Parse the text
        const mockDocument = { test_content: testCase.text };
        const references = parser.parseDocument(mockDocument, 'test_document.json');
        
        if (references.length > 0) {
            references.forEach(ref => {
                console.log(`   ✅ Detected: ${ref.type}`);
                console.log(`      Target: ${ref.target_document} → ${ref.target_section}`);
                console.log(`      Confidence: ${(ref.confidence * 100).toFixed(1)}%`);
            });
        } else {
            console.log(`   ❌ No references detected`);
        }
        console.log('');
    });
}

// Run the test
if (require.main === module) {
    testCrossReferenceParser()
        .then(results => {
            console.log('\n🎉 Cross-reference parsing test completed successfully!');
            
            // Demonstrate parsing capabilities
            demonstrateParsingCapabilities();
            
            console.log('\n🔄 Ready to test with real documents!');
            console.log('Replace simulation files with real legal documents to test production parsing.');
        })
        .catch(error => {
            console.error('❌ Test failed:', error);
        });
}

module.exports = {
    testCrossReferenceParser,
    demonstrateParsingCapabilities
};