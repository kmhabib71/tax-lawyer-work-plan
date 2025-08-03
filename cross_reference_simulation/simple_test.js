/**
 * Simple Pattern Test for Bengali Text
 * Focus on the most basic patterns first
 */

const testText = "আয়কর আইন, ২০২৩ এর ২য় ধারার উপ-ধারা (১) অনুযায়ী";

console.log('🔍 SIMPLE PATTERN TEST');
console.log(`Test text: "${testText}"`);
console.log(`Length: ${testText.length} characters\n`);

// Break down the text character by character
console.log('Character breakdown:');
for (let i = 0; i < testText.length; i++) {
    const char = testText[i];
    const code = char.charCodeAt(0);
    console.log(`${i}: "${char}" (U+${code.toString(16).toUpperCase().padStart(4, '0')})`);
}

console.log('\n📝 Pattern Tests:');

// Test very simple patterns first
const patterns = [
    { name: 'Find "আয়কর আইন"', pattern: /আয়কর আইন/g },
    { name: 'Find Bengali digits', pattern: /[০-৯]+/g },
    { name: 'Find "২০২৩"', pattern: /২০২৩/g },
    { name: 'Find "এর"', pattern: /এর/g },
    { name: 'Find "ধারা"', pattern: /ধারা/g },
    { name: 'Find "২য়"', pattern: /২য়/g },
    { name: 'Basic pattern', pattern: /আয়কর আইন.*২০২৩/g },
    { name: 'With comma', pattern: /আয়কর আইন,\s*২০২৩/g },
    { name: 'Full basic', pattern: /আয়কর আইন,\s*২০২৩\s*এর\s*২য়\s*ধারা/g }
];

patterns.forEach(({ name, pattern }) => {
    const matches = testText.match(pattern);
    if (matches) {
        console.log(`✅ ${name}: Found "${matches[0]}"`);
    } else {
        console.log(`❌ ${name}: No match`);
    }
});

console.log('\n🔧 Character Range Test:');

// Test character ranges
const bengaliDigits = "০১২৩৪৫৬৭৮৯";
const englishDigits = "0123456789";

console.log(`Bengali digits: ${bengaliDigits}`);
console.log(`English digits: ${englishDigits}`);

// Check what digits are actually in our text
const foundDigits = testText.match(/[০-৯]/g);
console.log(`Found Bengali digits in text: ${foundDigits ? foundDigits.join('') : 'None'}`);

const foundEnglishDigits = testText.match(/[0-9]/g);
console.log(`Found English digits in text: ${foundEnglishDigits ? foundEnglishDigits.join('') : 'None'}`);

// Test specific text fragments
console.log('\n🧪 Fragment Tests:');
const fragments = [
    "আয়কর আইন",
    "২০২৩",
    "২য়",
    "ধারা", 
    "উপ-ধারা",
    "(১)"
];

fragments.forEach(fragment => {
    const found = testText.includes(fragment);
    console.log(`${found ? '✅' : '❌'} "${fragment}": ${found ? 'Found' : 'Not found'}`);
});

console.log('\n✅ Test completed');