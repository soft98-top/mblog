#!/bin/bash
# 验证 base_path 功能的脚本

set -e

echo "=========================================="
echo "验证 base_path 功能"
echo "=========================================="

cd test-blog

# 备份原始配置
echo "备份配置..."
cp config.json config.json.backup

# 测试 1: 带 base_path
echo ""
echo "测试 1: 带 base_path='/myblog'"
echo "----------------------------------------"
python -c "import json; c=json.load(open('config.json')); c['site']['base_path']='/myblog'; c['site']['url']='https://example.com/myblog'; json.dump(c, open('config.json', 'w'), ensure_ascii=False, indent=2)"

echo "生成静态文件..."
python gen.py > /dev/null 2>&1

echo "检查首页..."
if grep -q 'href="/myblog/' public/index.html; then
    echo "✓ 首页链接正确"
else
    echo "✗ 首页链接错误"
    exit 1
fi

echo "检查归档页..."
if grep -q 'href="/myblog/posts/' public/archive.html; then
    echo "✓ 归档页链接正确"
else
    echo "✗ 归档页链接错误"
    exit 1
fi

echo "检查标签页..."
if grep -q 'href="/myblog/tags/' public/tags/index.html; then
    echo "✓ 标签页链接正确"
else
    echo "✗ 标签页链接错误"
    exit 1
fi

echo "检查文章页..."
FIRST_POST=$(find public/posts -name "*.html" | head -1)
if [ -n "$FIRST_POST" ] && grep -q 'href="/myblog/' "$FIRST_POST"; then
    echo "✓ 文章页链接正确"
else
    echo "✗ 文章页链接错误"
    exit 1
fi

echo "检查静态资源..."
if grep -q 'href="/myblog/static/' public/index.html; then
    echo "✓ 静态资源链接正确"
else
    echo "✗ 静态资源链接错误"
    exit 1
fi

# 测试 2: 不带 base_path
echo ""
echo "测试 2: 不带 base_path (空字符串)"
echo "----------------------------------------"
python -c "import json; c=json.load(open('config.json')); c['site']['base_path']=''; c['site']['url']='https://example.com'; json.dump(c, open('config.json', 'w'), ensure_ascii=False, indent=2)"

echo "生成静态文件..."
python gen.py > /dev/null 2>&1

echo "检查首页..."
if grep -q 'href="/posts/' public/index.html && ! grep -q 'href="/myblog/' public/index.html; then
    echo "✓ 首页链接正确（无前缀）"
else
    echo "✗ 首页链接错误"
    exit 1
fi

echo "检查归档页..."
if grep -q 'href="/posts/' public/archive.html && ! grep -q 'href="/myblog/' public/archive.html; then
    echo "✓ 归档页链接正确（无前缀）"
else
    echo "✗ 归档页链接错误"
    exit 1
fi

echo "检查标签页..."
if grep -q 'href="/tags/' public/tags/index.html && ! grep -q 'href="/myblog/' public/tags/index.html; then
    echo "✓ 标签页链接正确（无前缀）"
else
    echo "✗ 标签页链接错误"
    exit 1
fi

# 恢复配置
echo ""
echo "恢复配置..."
mv config.json.backup config.json

echo ""
echo "=========================================="
echo "✅ 所有测试通过！"
echo "=========================================="
