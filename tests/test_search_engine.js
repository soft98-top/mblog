#!/usr/bin/env node
/**
 * Comprehensive test suite for SearchEngine JavaScript class
 * Tests all requirements from task 10
 */

// Mock fetch for Node.js environment
global.fetch = async function(url) {
    // Return mock search index data
    const mockData = {
        posts: [
            {
                title: "Python Tutorial",
                url: "/posts/python-tutorial.html",
                date: "2024-01-01",
                tags: ["Python", "Tutorial"],
                description: "Learn Python basics"
            },
            {
                title: "JavaScript Guide",
                url: "/posts/javascript-guide.html",
                date: "2024-01-02",
                tags: ["JavaScript", "Web"],
                description: "JS fundamentals"
            },
            {
                title: "中文测试文章",
                url: "/posts/chinese-post.html",
                date: "2024-01-03",
                tags: ["测试", "中文"],
                description: "这是一个中文描述"
            },
            {
                title: "Python Web Development",
                url: "/posts/python-web.html",
                date: "2024-01-04",
                tags: ["Python", "Web"],
                description: "Build web apps with Python"
            }
        ],
        generated_at: "2024-01-07T12:00:00",
        total_posts: 4
    };
    
    return {
        ok: true,
        json: async () => mockData
    };
};

// Load SearchEngine class by reading and evaluating it
const fs = require('fs');
const path = require('path');
const searchJsPath = path.join(__dirname, '..', 'mblog', 'templates', 'themes', 'default', 'static', 'js', 'search.js');
let searchJsCode = fs.readFileSync(searchJsPath, 'utf8');

// Remove the module.exports check at the end and add our own
searchJsCode = searchJsCode.replace(/if \(typeof module.*\n.*\n\}/g, '');
searchJsCode += '\nif (typeof module !== "undefined") { module.exports = SearchEngine; }';

// Write to temp file and require it
const tempPath = path.join(__dirname, 'temp_search.js');
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

function assertEquals(actual, expected, message) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(`${message}\nExpected: ${JSON.stringify(expected)}\nActual: ${JSON.stringify(actual)}`);
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

// Test 1: Load index
async function testLoadIndex() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    assert(engine.loaded, 'Engine should be loaded');
    assert(engine.posts.length === 4, `Expected 4 posts, got ${engine.posts.length}`);
    console.log('✓ Index loaded successfully');
    console.log(`✓ Loaded ${engine.posts.length} posts`);
}

// Test 2: Query parsing
async function testQueryParsing() {
    const engine = new SearchEngine('/search-index.json');
    
    // Test 1: Keywords only
    let result = engine.parseQuery('python tutorial');
    assertEquals(result.tags, [], 'Should have no tags');
    assertEquals(result.keywords, ['python', 'tutorial'], 'Should have 2 keywords');
    console.log('✓ Keywords-only query parsed correctly');
    
    // Test 2: Tags only
    result = engine.parseQuery('#python #web');
    assertEquals(result.tags, ['python', 'web'], 'Should have 2 tags');
    assertEquals(result.keywords, [], 'Should have no keywords');
    console.log('✓ Tags-only query parsed correctly');
    
    // Test 3: Combined
    result = engine.parseQuery('#python tutorial guide');
    assertEquals(result.tags, ['python'], 'Should have 1 tag');
    assertEquals(result.keywords, ['tutorial', 'guide'], 'Should have 2 keywords');
    console.log('✓ Combined query parsed correctly');
    
    // Test 4: Multiple spaces
    result = engine.parseQuery('  python   tutorial  ');
    assertEquals(result.keywords, ['python', 'tutorial'], 'Should handle multiple spaces');
    console.log('✓ Multiple spaces handled correctly');
    
    // Test 5: Standalone #
    result = engine.parseQuery('# python');
    assertEquals(result.tags, [], 'Standalone # should be ignored');
    assertEquals(result.keywords, ['python'], 'Should have 1 keyword');
    console.log('✓ Standalone # handled correctly');
}

// Test 3: Chinese character search
async function testChineseSearch() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Search for Chinese characters
    let results = engine.search('中文');
    assert(results.length === 1, `Expected 1 result for '中文', got ${results.length}`);
    assert(results[0].title === '中文测试文章', 'Should find Chinese post');
    console.log('✓ Chinese character search works');
    
    // Search for Chinese + English mixed
    results = engine.search('Python');
    assert(results.length === 2, `Expected 2 results for 'Python', got ${results.length}`);
    console.log('✓ Mixed language search works');
}

// Test 4: Multiple keyword search
async function testMultipleKeywords() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Two keywords
    let results = engine.search('Python Tutorial');
    assert(results.length === 1, `Expected 1 result, got ${results.length}`);
    assert(results[0].title === 'Python Tutorial', 'Should match Python Tutorial');
    console.log('✓ Two-keyword search works');
    
    // Three keywords
    results = engine.search('Python Web Development');
    assert(results.length === 1, `Expected 1 result, got ${results.length}`);
    assert(results[0].title === 'Python Web Development', 'Should match Python Web Development');
    console.log('✓ Three-keyword search works');
    
    // No matches
    results = engine.search('Python JavaScript');
    assert(results.length === 0, `Expected 0 results, got ${results.length}`);
    console.log('✓ No-match scenario works');
}

// Test 5: Tag filtering
async function testTagFiltering() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Single tag
    let results = engine.search('#Python');
    assert(results.length === 2, `Expected 2 results for #Python, got ${results.length}`);
    console.log('✓ Single tag filter works (2 matches)');
    
    // Different tag
    results = engine.search('#Web');
    assert(results.length === 2, `Expected 2 results for #Web, got ${results.length}`);
    console.log('✓ Single tag filter works (2 matches)');
    
    // Case-insensitive
    results = engine.search('#python');
    assert(results.length === 2, `Expected 2 results for #python (lowercase), got ${results.length}`);
    console.log('✓ Case-insensitive tag matching works');
}

// Test 6: Combined tag and keyword search
async function testCombinedSearch() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Tag + keyword
    let results = engine.search('#Python Tutorial');
    assert(results.length === 1, `Expected 1 result, got ${results.length}`);
    assert(results[0].title === 'Python Tutorial', 'Should match Python Tutorial');
    console.log('✓ Tag + keyword combination works');
    
    // Tag + keyword (different combination)
    results = engine.search('#Python Web');
    assert(results.length === 1, `Expected 1 result, got ${results.length}`);
    assert(results[0].title === 'Python Web Development', 'Should match Python Web Development');
    console.log('✓ Tag + keyword combination works (different combo)');
    
    // Multiple tags + keyword
    results = engine.search('#Python #Web Development');
    assert(results.length === 1, `Expected 1 result, got ${results.length}`);
    console.log('✓ Multiple tags + keyword works');
}

// Test 7: Empty query
async function testEmptyQuery() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Empty string
    let results = engine.search('');
    assert(results.length === 4, `Expected 4 results for empty query, got ${results.length}`);
    console.log('✓ Empty query returns all posts');
    
    // Whitespace only
    results = engine.search('   ');
    assert(results.length === 4, `Expected 4 results for whitespace query, got ${results.length}`);
    console.log('✓ Whitespace-only query returns all posts');
}

// Test 8: Date ordering preservation
async function testDateOrdering() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Get all posts
    const results = engine.search('');
    
    // Verify order is preserved (should be in the same order as loaded)
    assert(results[0].title === 'Python Tutorial', 'First post should be Python Tutorial');
    assert(results[1].title === 'JavaScript Guide', 'Second post should be JavaScript Guide');
    assert(results[2].title === '中文测试文章', 'Third post should be Chinese post');
    assert(results[3].title === 'Python Web Development', 'Fourth post should be Python Web Development');
    console.log('✓ Date ordering preserved in results');
}

// Test 9: Highlight matching
async function testHighlighting() {
    const engine = new SearchEngine('/search-index.json');
    
    // Test highlighting
    let highlighted = engine.highlightMatch('Python Tutorial', ['Python']);
    assert(highlighted.includes('<mark>Python</mark>'), 'Should highlight Python');
    console.log('✓ Keyword highlighting works');
    
    // Multiple keywords
    highlighted = engine.highlightMatch('Python Web Development', ['Python', 'Web']);
    assert(highlighted.includes('<mark>Python</mark>'), 'Should highlight Python');
    assert(highlighted.includes('<mark>Web</mark>'), 'Should highlight Web');
    console.log('✓ Multiple keyword highlighting works');
    
    // Chinese characters
    highlighted = engine.highlightMatch('中文测试文章', ['中文']);
    assert(highlighted.includes('<mark>中文</mark>'), 'Should highlight Chinese characters');
    console.log('✓ Chinese character highlighting works');
}

// Test 10: Performance with large collection
async function testPerformance() {
    // Create large dataset
    const largePosts = [];
    for (let i = 0; i < 1000; i++) {
        largePosts.push({
            title: `Test Post ${i} with Python and Tutorial keywords`,
            url: `/posts/post-${i}.html`,
            date: `2024-01-${String(i % 28 + 1).padStart(2, '0')}`,
            tags: ['Python', 'Tutorial', `Tag${i % 10}`],
            description: `Description for post ${i}`
        });
    }
    
    // Mock fetch with large dataset
    const originalFetch = global.fetch;
    global.fetch = async function() {
        return {
            ok: true,
            json: async () => ({ posts: largePosts, generated_at: '2024-01-07', total_posts: 1000 })
        };
    };
    
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    console.log(`✓ Loaded ${engine.posts.length} posts`);
    
    // Measure search time
    const start = Date.now();
    const results = engine.search('Python Tutorial');
    const elapsed = Date.now() - start;
    
    console.log(`✓ Search completed in ${elapsed}ms`);
    console.log(`✓ Found ${results.length} matching posts`);
    
    assert(elapsed < 100, `Search took ${elapsed}ms, expected < 100ms`);
    console.log('✓ Performance requirement met (< 100ms)');
    
    // Restore original fetch
    global.fetch = originalFetch;
}

// Test 11: Case-insensitive matching
async function testCaseInsensitive() {
    const engine = new SearchEngine('/search-index.json');
    await engine.loadIndex();
    
    // Lowercase search
    let results = engine.search('python');
    assert(results.length === 2, `Expected 2 results for 'python', got ${results.length}`);
    console.log('✓ Lowercase search works');
    
    // Uppercase search
    results = engine.search('PYTHON');
    assert(results.length === 2, `Expected 2 results for 'PYTHON', got ${results.length}`);
    console.log('✓ Uppercase search works');
    
    // Mixed case
    results = engine.search('PyThOn');
    assert(results.length === 2, `Expected 2 results for 'PyThOn', got ${results.length}`);
    console.log('✓ Mixed case search works');
}

// Run all tests
async function runAllTests() {
    console.log('='.repeat(60));
    console.log('JAVASCRIPT SEARCH ENGINE - COMPREHENSIVE TEST SUITE');
    console.log('='.repeat(60));
    
    await runTest('Test 1: Load Index', testLoadIndex);
    await runTest('Test 2: Query Parsing', testQueryParsing);
    await runTest('Test 3: Chinese Character Search', testChineseSearch);
    await runTest('Test 4: Multiple Keyword Search', testMultipleKeywords);
    await runTest('Test 5: Tag Filtering', testTagFiltering);
    await runTest('Test 6: Combined Tag + Keyword Search', testCombinedSearch);
    await runTest('Test 7: Empty Query Handling', testEmptyQuery);
    await runTest('Test 8: Date Ordering Preservation', testDateOrdering);
    await runTest('Test 9: Keyword Highlighting', testHighlighting);
    await runTest('Test 10: Performance (1000 posts)', testPerformance);
    await runTest('Test 11: Case-Insensitive Matching', testCaseInsensitive);
    
    console.log('\n' + '='.repeat(60));
    console.log(`TEST RESULTS: ${testsPassed} passed, ${testsFailed} failed`);
    console.log('='.repeat(60));
    
    process.exit(testsFailed === 0 ? 0 : 1);
}

runAllTests();
