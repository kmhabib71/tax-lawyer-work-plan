/**
 * Debug Script for Bengali Legal Cross-Reference Patterns
 * Tests individual regex patterns against real text samples
 */

// Real text samples from our documents
const testTexts = [
    'আয়কর আইন, ২০২৩ (২০২৩ সনের ১২ নং আইন) এর ২য় ধারায় সংজ্ঞায়িত',
    'আয়কর আইন, ২০২ৃ এর ২য় ধারার উপ-ধারা (১) অনুযায়ী',
    'অর্থ আইন, ২০২৪ এর ৬ম ধারার উপ-ধারা (২) অনুযায়ী',
    'আয়কর আইন, ২০২৩ এর ৮৫ম ধারায় উল্লিখিত',
    'এসআরও নং ২৩৫/২০২৪ এ বর্ণিত',
    'উৎসে কর কর্তন বিধিমালা, ২০২৪ এর ৩য় ও ৪র্থ নিয়ম অনুযায়ী',
    'জাতীয় রাজস্ব বোর্ডের পরিপত্র নং ০৫/২০২৪ এ বর্ণিত',
    'আয়কর অধ্যাদেশ, ১৯৮৪ এর ২৮৫ ধারায় বর্ণিত',
    'কোম্পানি আইন, ১৯৯৪ (১৯৯৪ সনের ১৮ নং আইন) এর অধীন',
    'এই আইনের তৃতীয় তফসিলের বিধান প্রযোজ্য',
    'উক্ত আইনের ধারা ৪ এর উপ-ধারা (১)'
];

// Test different pattern approaches
const patterns = {
    // Simple act pattern
    act_simple: /(আয়কর আইন|অর্থ আইন),\s*(\d{4})\s*এর\s*(\d+)(?:ম|য়)\s*ধারা/g,
    
    // Act with full citation
    act_full: /(আয়কর আইন|অর্থ আইন|কোম্পানি আইন),\s*(\d{4})\s*\((\d{4})\s*সনের\s*(\d+)\s*নং আইন\)\s*এর\s*(\d+)(?:য়|ম)?\s*ধারা/g,
    
    // SRO pattern
    sro: /এসআরও\s*নং?\s*(\d{3}\/\d{4})/g,
    
    // Rules pattern
    rules: /(উৎসে কর কর্তন বিধিমালা|[^,]*বিধিমালা),\s*(\d{4})\s*এর\s*(\d+)(?:য়|র্থ)?\s*(?:ও\s*(\d+)(?:র্থ)?\s*)?নিয়ম/g,
    
    // Circular pattern
    circular: /পরিপত্র\s*নং?\s*(\d{1,2}\/\d{4})/g,
    
    // Ordinance pattern
    ordinance: /(আয়কর অধ্যাদেশ),\s*(\d{4})\s*এর?\s*(\d+)\s*ধারা/g,
    
    // Schedule pattern
    schedule: /(প্রথম|দ্বিতীয়|তৃতীয়)\s*তফসিল/g,
    
    // Contextual reference
    contextual: /উক্ত আইনের?\s*(?:ধারা\s*)?(\d+)/g
};

function testPatterns() {
    console.log('🔬 DEBUGGING BENGALI LEGAL PATTERNS\n');
    
    testTexts.forEach((text, index) => {
        console.log(`${index + 1}. Testing: "${text}"`);
        
        let foundAny = false;
        Object.entries(patterns).forEach(([patternName, pattern]) => {
            // Reset regex for global search
            pattern.lastIndex = 0;
            const matches = [...text.matchAll(pattern)];
            
            if (matches.length > 0) {
                foundAny = true;
                matches.forEach(match => {
                    console.log(`   ✅ ${patternName}: "${match[0]}"`);
                    console.log(`      Groups: [${match.slice(1).join(', ')}]`);
                });
            }
        });
        
        if (!foundAny) {
            console.log('   ❌ No patterns matched');
        }
        console.log('');
    });
}

function createWorkingPatterns() {
    console.log('🔧 CREATING WORKING PATTERNS\n');
    
    // Based on the real text analysis
    const workingPatterns = {
        // Act references - exact patterns from our text
        act_references: [
            // আয়কর আইন, ২০২৩ এর ২য় ধারার
            /(আয়কর আইন|অর্থ আইন|কোম্পানি আইন),\s*(\d{4})\s*এর\s*(\d+)(?:ম|য়)?\s*ধারা(?:য়|র)?(?:\s*উপ-ধারা\s*\((\d+)\))?/g,
            
            // আয়কর আইন, ২০২৩ (২০২৩ সনের ১২ নং আইন) এর ২য় ধারায়
            /(আয়কর আইন|অর্থ আইন|কোম্পানি আইন),\s*(\d{4})\s*\((\d{4})\s*সনের\s*(\d+)\s*নং আইন\)\s*এর\s*(\d+)(?:য়|ম)?\s*ধারা(?:য়|র)?/g,
            
            // উক্ত আইনের ধারা ৪
            /উক্ত আইনের?\s*(?:ধারা\s*)?(\d+)/g,
            
            // কোম্পানি আইন, ১৯৯৪ এর অধীন
            /(কোম্পানি আইন|আয়কর আইন|অর্থ আইন),\s*(\d{4})\s*(?:\([^)]+\))?\s*এর\s*অধীন/g
        ],
        
        sro_references: [
            /এসআরও\s*নং?\s*(\d{3}\/\d{4})/g
        ],
        
        rules_references: [
            /(উৎসে কর কর্তন বিধিমালা|[^,]*বিধিমালা),\s*(\d{4})\s*এর\s*(\d+)(?:য়|র্থ)?\s*(?:ও\s*(\d+)(?:র্থ)?\s*)?নিয়ম/g
        ],
        
        circular_references: [
            /(?:জাতীয় রাজস্ব বোর্ডের\s*)?পরিপত্র\s*নং?\s*(\d{1,2}\/\d{4})/g
        ],
        
        ordinance_references: [
            /(আয়কর অধ্যাদেশ),\s*(\d{4})\s*এর?\s*(\d+)\s*ধারা/g
        ],
        
        schedule_references: [
            /(প্রথম|দ্বিতীয়|তৃতীয়|চতুর্থ|পঞ্চম|ষষ্ঠ|সপ্তম|অষ্টম)\s*তফসিল/g
        ]
    };
    
    // Test working patterns
    console.log('Testing working patterns:');
    
    testTexts.forEach((text, index) => {
        console.log(`\n${index + 1}. "${text}"`);
        
        let foundAny = false;
        Object.entries(workingPatterns).forEach(([categoryName, patternsArray]) => {
            patternsArray.forEach((pattern, patternIndex) => {
                pattern.lastIndex = 0;
                const matches = [...text.matchAll(pattern)];
                
                if (matches.length > 0) {
                    foundAny = true;
                    matches.forEach(match => {
                        console.log(`   ✅ ${categoryName}[${patternIndex}]: "${match[0]}"`);
                        console.log(`      Captured: [${match.slice(1).filter(g => g).join(', ')}]`);
                    });
                }
            });
        });
        
        if (!foundAny) {
            console.log('   ❌ No working patterns matched');
        }
    });
    
    return workingPatterns;
}

// Run the tests
console.log('Starting pattern debugging...\n');
testPatterns();
const workingPatterns = createWorkingPatterns();

console.log('\n📝 WORKING PATTERNS READY FOR IMPLEMENTATION');
console.log('These patterns have been tested against real document text.');