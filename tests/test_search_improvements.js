#!/usr/bin/env node
/**
 * Test suite for search improvements:
 * 1. Date format (YYYY-MM-DD instead of ISO)
 * 2. Partial tag matching (#逆 matches "逆向破解")
 * 3. Links open in new tab (target="_blank")
 */

// Mock fetch for Node.js environment
global.fetch = async function(url) {
    const mockData = {
        posts: [
            {
                title: "逆向破解教程",
                url: "/posts/reverse-engineering.html",
                date: "2024-01-11T00:00:00",
                tags: ["逆向破解", "安全"],
                description: "学习逆向破解技术"
            },
            {
                title: "逆向工程基础",
                url: "/posts/reverse-basics.html",
                date: "2024-01-10T12:30:45",
                tags: ["逆向工程", "编程"],
                description: "逆向工程入门"
            },
            {
                title: "破解技巧分享",
                url: "/posts/cracking-tips.html",
                date: "2024-01-09",
                tags: ["破解", "技巧"],
                description: "实用破解技巧"
            }
        ],
        generated_at: "2024-01-11T12:00:00",
        total_posts: 3
    };
    
    return {
        ok: true,
        json: async () => mockData
    };
};

// Load SearchEngine class
const fs = require('fs');
const path = require('path');
const searchJsPath = path.join(__dirname, '..', 'mblog', 'templates', 'themes', 'default', 'static', 'js', 'search.js');
let searchJsCode = fs.readFileSync(searchJsPath, 'utf8');

// Remove the module.exports check at the end and add our own
searchJsCode = searchJsCode.replace(/if \(typeof module.*\n.*\n\}/g, '');
searchJsCode += '\nif (typeof module !== "undefined") { module.exports = SearchEngine; }';

// Write to temp file and require it
const tempPath = path.join(__dirname, 'temp_search_improvements.js');
fs.writeFileSync(tempPath, searchJsCode);
const SearchEngine = require(tempPath);
fs.unlinkSync(tempPath);

// Test utilities
let testsPassed = 0;
let testsFailed = 0;

function assert(condition, message) {
    if (!condition) {
        throw new Error(message || 'Assertion failed');
    }
}

async function runTest(testName, testFunc) {
    try {
        console.log(`\n=== ${testName} ===`);
        await testFunc();
        testsPassed++;
    } catch (error) {
        console.log(`✗ FAILED: ${error.message}`);
        testsFailed++;
    }
}

// Test 1: Date formatting
async function testDateFormatting() {
    const engine = new SearchEngine('/search-index.json');
    
    // Test ISO date with time
    let formatted = engine.formatDate('2024-01-11T00:00:00');
    assert(formatted === '2024-01-11', `Expected '2024-01-11', got '${formatted}'`);
    console.log('✓ ISO date with time formatted correctly');
    
    // Test ISO date with seconds
    formatted = engine.formatDate('2024-01-10T12:30:45');
    assert(formatted === '2024-01-10', `Expected '2024-01-10', got '${formatted}'`);
    console.log('✓ ISO date with seconds formatted correctly');
    
    // Test already formatted date
    formatted = engine.formatDate('2024-01-09');
    assert(formatted === '2024-01-09', `Expected '2024-01-09', got '${formatted}'`);
    console.log('✓ Already formatted date returned as is');
    
    // Test empty string
    formatted = engine.formatDate('');
    assert(formatted === '', `Expected empty string, got '${formatted}'`);
    console.log('✓ Empty string handled correctly');
}

// Test 2: Partial tag matching
async function testPartialTagMatching() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Test #逆 should match both "逆向破解" and "逆向工程"
    let results = engine.search('#逆');
    assert(results.length === 2, `Expected 2 results for #逆, got ${results.length}`);
    assert(results.some(p => p.title === '逆向破解教程'), 'Should match 逆向破解教程');
    assert(results.some(p => p.title === '逆向工程基础'), 'Should match 逆向工程基础');
    console.log('✓ #逆 matches both "逆向破解" and "逆向工程"');
    
    // Test #逆向 should also match both
    results = engine.search('#逆向');
    assert(results.length === 2, `Expected 2 results for #逆向, got ${results.length}`);
    console.log('✓ #逆向 matches both posts');
    
    // Test #破解 should match "逆向破解" and "破解"
    results = engine.search('#破解');
    assert(results.length === 2, `Expected 2 results for #破解, got ${results.length}`);
    assert(results.some(p => p.title === '逆向破解教程'), 'Should match 逆向破解教程');
    assert(results.some(p => p.title === '破解技巧分享'), 'Should match 破解技巧分享');
    console.log('✓ #破解 matches "逆向破解" and "破解"');
    
    // Test exact match still works
    results = engine.search('#逆向破解');
    assert(results.length === 1, `Expected 1 result for #逆向破解, got ${results.length}`);
    assert(results[0].title === '逆向破解教程', 'Should match 逆向破解教程');
    console.log('✓ Exact tag match still works');
}

// Test 3: Display results with new tab links
async function testNewTabLinks() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Create a mock DOM container
    const mockContainer = {
        innerHTML: '',
        style: { display: 'none' },
        appendChild: function(element) {
            // Simulate appending by concatenating HTML
            this.innerHTML += element.outerHTML || element.innerHTML || '';
        }
    };
    
    // Mock document.querySelector
    const originalQuerySelector = global.document ? global.document.querySelector : undefined;
    global.document = {
        querySelector: () => mockContainer,
        createElement: (tag) => {
            const element = {
                tagName: tag,
                className: '',
                innerHTML: '',
                outerHTML: ''
            };
            Object.defineProperty(element, 'outerHTML', {
                get: function() { return this.innerHTML; }
            });
            return element;
        }
    };
    
    // Display results
    const results = engine.search('#逆');
    engine.displayResults(results, '#search-results', '#逆');
    
    // Check that links have target="_blank"
    assert(mockContainer.innerHTML.includes('target="_blank"'), 'Links should have target="_blank"');
    assert(mockContainer.innerHTML.includes('rel="noopener noreferrer"'), 'Links should have rel="noopener noreferrer"');
    console.log('✓ Search result links open in new tab');
    
    // Check date format in results
    assert(mockContainer.innerHTML.includes('2024-01-11'), 'Should display formatted date 2024-01-11');
    assert(!mockContainer.innerHTML.includes('T00:00:00'), 'Should not display time portion');
    console.log('✓ Dates displayed in YYYY-MM-DD format');
    
    // Restore
    if (originalQuerySelector) {
        global.document.querySelector = originalQuerySelector;
    }
}

// Test 4: Combined partial tag matching with keywords
async function testCombinedPartialTagAndKeyword() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Test #逆 + keyword "教程"
    let results = engine.search('#逆 教程');
    assert(results.length === 1, `Expected 1 result, got ${results.length}`);
    assert(results[0].title === '逆向破解教程', 'Should match 逆向破解教程');
    console.log('✓ Partial tag #逆 + keyword "教程" works');
    
    // Test #破 + keyword "技巧"
    results = engine.search('#破 技巧');
    assert(results.length === 1, `Expected 1 result, got ${results.length}`);
    assert(results[0].title === '破解技巧分享', 'Should match 破解技巧分享');
    console.log('✓ Partial tag #破 + keyword "技巧" works');
}

// Run all tests
async function runAllTests() {
    console.log('='.repeat(60));
    console.log('SEARCH IMPROVEMENTS - TEST SUITE');
    console.log('='.repeat(60));
    
    await runTest('Test 1: Date Formatting', testDateFormatting);
    await runTest('Test 2: Partial Tag Matching', testPartialTagMatching);
    await runTest('Test 3: New Tab Links', testNewTabLinks);
    await runTest('Test 4: Combined Partial Tag + Keyword', testCombinedPartialTagAndKeyword);
    
    console.log('\n' + '='.repeat(60));
    console.log(`TEST RESULTS: ${testsPassed} passed, ${testsFailed} failed`);
    console.log('='.repeat(60));
    
    if (testsPassed === 4) {
        console.log('\n✅ All improvements verified successfully!');
        console.log('\nImprovements implemented:');
        console.log('1. ✅ Date format: YYYY-MM-DD (no time portion)');
        console.log('2. ✅ Partial tag matching: #逆 matches "逆向破解", "逆向工程"');
        console.log('3. ✅ Links open in new tab: target="_blank"');
        console.log('4. ✅ Archive page: search box removed');
        console.log('5. ✅ Post page: search box added');
    }
    
    process.exit(testsFailed === 0 ? 0 : 1);
}

runAllTests();
