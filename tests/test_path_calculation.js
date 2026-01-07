#!/usr/bin/env node
/**
 * Test path calculation logic for search-index.json
 * 新逻辑：找到 posts/tags/page 的上一级目录
 */

// 路径计算函数（与 main.js 中的逻辑一致）
function calculateSearchIndexPath(currentPath) {
    let indexUrl = 'search-index.json';  // 默认在当前目录
    
    // 检查是否在 posts、tags 或 page 目录下
    const specialDirs = ['posts', 'tags', 'page'];
    let foundSpecialDir = false;
    
    for (const dir of specialDirs) {
        const dirPattern = `/${dir}/`;
        if (currentPath.includes(dirPattern)) {
            // 找到特殊目录，提取其上一级路径
            const dirIndex = currentPath.indexOf(dirPattern);
            const basePath = currentPath.substring(0, dirIndex);
            indexUrl = `${basePath}/search-index.json`;
            foundSpecialDir = true;
            break;
        }
    }
    
    return indexUrl;
}

// 测试用例
const testCases = [
    // 根目录（无基础路径）
    { path: '/', expected: 'search-index.json', desc: '根目录' },
    { path: '/index.html', expected: 'search-index.json', desc: '首页' },
    { path: '/archive.html', expected: 'search-index.json', desc: '归档页' },
    
    // posts 目录
    { path: '/posts/article.html', expected: '/search-index.json', desc: '文章页（一级）' },
    { path: '/posts/杂项/多账户git配置.html', expected: '/search-index.json', desc: '嵌套文章（中文目录）' },
    { path: '/posts/tech/python/tutorial.html', expected: '/search-index.json', desc: '深层嵌套文章' },
    
    // tags 目录
    { path: '/tags/python.html', expected: '/search-index.json', desc: '标签页' },
    
    // page 目录
    { path: '/page/2.html', expected: '/search-index.json', desc: '分页页' },
    
    // 带基础路径 /mblog
    { path: '/mblog/', expected: 'search-index.json', desc: '带基础路径的根目录' },
    { path: '/mblog/index.html', expected: 'search-index.json', desc: '带基础路径的首页' },
    { path: '/mblog/posts/article.html', expected: '/mblog/search-index.json', desc: '带基础路径的文章' },
    { path: '/mblog/posts/杂项/多账户git配置.html', expected: '/mblog/search-index.json', desc: '带基础路径的嵌套文章' },
    { path: '/mblog/tags/python.html', expected: '/mblog/search-index.json', desc: '带基础路径的标签页' },
    
    // 带基础路径 /aaa
    { path: '/aaa/posts/xx/xxx/xx.html', expected: '/aaa/search-index.json', desc: '带基础路径 /aaa 的深层文章' },
];

// 运行测试
console.log('='.repeat(60));
console.log('搜索索引路径计算测试（新逻辑）');
console.log('='.repeat(60));

let passed = 0;
let failed = 0;

testCases.forEach((testCase, index) => {
    const result = calculateSearchIndexPath(testCase.path);
    const isPass = result === testCase.expected;
    
    if (isPass) {
        passed++;
        console.log(`\n✓ 测试 ${index + 1}: ${testCase.desc}`);
    } else {
        failed++;
        console.log(`\n✗ 测试 ${index + 1}: ${testCase.desc}`);
        console.log(`  路径: ${testCase.path}`);
        console.log(`  期望: ${testCase.expected}`);
        console.log(`  实际: ${result}`);
    }
});

console.log('\n' + '='.repeat(60));
console.log(`测试结果: ${passed} 通过, ${failed} 失败`);
console.log(`成功率: ${Math.round(passed / testCases.length * 100)}%`);
console.log('='.repeat(60));

// 显示算法说明
if (passed === testCases.length) {
    console.log('\n✅ 所有测试通过！');
    console.log('\n算法说明:');
    console.log('1. 检查路径中是否包含 /posts/、/tags/ 或 /page/');
    console.log('2. 如果找到，提取该目录的上一级路径');
    console.log('3. 在上一级路径拼接 /search-index.json');
    console.log('\n示例:');
    console.log('  /mblog/posts/杂项/多账户git配置.html');
    console.log('  → 找到 /posts/');
    console.log('  → 上一级路径: /mblog');
    console.log('  → 结果: /mblog/search-index.json');
    console.log('\n  /posts/article.html');
    console.log('  → 找到 /posts/');
    console.log('  → 上一级路径: (空)');
    console.log('  → 结果: /search-index.json');
}

process.exit(failed === 0 ? 0 : 1);
