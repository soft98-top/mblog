#!/usr/bin/env python3
"""
Integration test for search functionality
Tests the actual search index generation and verifies it works correctly
"""

import json
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mblog.templates.runtime.config import Config
from mblog.templates.runtime.theme import Theme
from mblog.templates.runtime.renderer import Renderer
from mblog.templates.runtime.markdown_processor import MarkdownProcessor
from mblog.templates.runtime.generator import StaticGenerator


def test_search_index_generation_integration():
    """
    Integration test: Generate a real blog with search index
    """
    print("\n=== Integration Test: Search Index Generation ===")
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create directory structure
        md_dir = tmpdir / "md"
        md_dir.mkdir()
        output_dir = tmpdir / "public"
        
        # Create test markdown files
        test_posts = [
            {
                "filename": "python-tutorial.md",
                "content": """---
title: Python Tutorial
date: 2024-01-01
author: Test Author
description: Learn Python basics
tags: [Python, Tutorial]
---

# Python Tutorial

This is a Python tutorial.
"""
            },
            {
                "filename": "javascript-guide.md",
                "content": """---
title: JavaScript Guide
date: 2024-01-02
author: Test Author
description: JS fundamentals
tags: [JavaScript, Web]
---

# JavaScript Guide

This is a JavaScript guide.
"""
            },
            {
                "filename": "chinese-post.md",
                "content": """---
title: 中文测试文章
date: 2024-01-03
author: 测试作者
description: 这是一个中文描述
tags: [测试, 中文]
---

# 中文测试文章

这是中文内容。
"""
            }
        ]
        
        # Write test posts
        for post in test_posts:
            post_path = md_dir / post["filename"]
            post_path.write_text(post["content"], encoding='utf-8')
        
        print(f"✓ Created {len(test_posts)} test posts")
        
        # Create minimal config
        config_data = {
            "site": {
                "title": "Test Blog",
                "url": "https://test.com",
                "description": "Test blog",
                "author": "Test Author",
                "language": "zh-CN"
            },
            "build": {
                "md_dir": str(md_dir),
                "output_dir": str(output_dir),
                "theme": "default"
            },
            "theme_config": {
                "posts_per_page": 10,
                "date_format": "%Y-%m-%d"
            }
        }
        
        # Save config
        config_path = tmpdir / "config.json"
        config_path.write_text(json.dumps(config_data, ensure_ascii=False, indent=2))
        
        # Initialize components
        config = Config(str(config_path))
        config.load()
        
        # Get theme path (use the actual theme from the package)
        import mblog
        package_dir = Path(mblog.__file__).parent
        theme_dir = package_dir / "templates" / "themes" / "default"
        
        theme = Theme(str(theme_dir))
        theme.load()
        renderer = Renderer(theme, config)
        
        # Load posts
        processor = MarkdownProcessor(str(md_dir))
        posts = processor.load_posts()
        
        print(f"✓ Loaded {len(posts)} posts")
        
        # Generate site
        generator = StaticGenerator(config, theme, renderer, posts)
        generator.generate()
        
        print("✓ Site generated successfully")
        
        # Verify search index was created
        search_index_path = output_dir / "search-index.json"
        assert search_index_path.exists(), "search-index.json should exist"
        print("✓ search-index.json file created")
        
        # Load and verify search index
        with open(search_index_path, 'r', encoding='utf-8') as f:
            search_index = json.load(f)
        
        # Verify structure
        assert 'posts' in search_index, "Index must have 'posts' field"
        assert 'generated_at' in search_index, "Index must have 'generated_at' field"
        assert 'total_posts' in search_index, "Index must have 'total_posts' field"
        print("✓ Search index has correct structure")
        
        # Verify post count
        assert len(search_index['posts']) == 3, f"Expected 3 posts, got {len(search_index['posts'])}"
        assert search_index['total_posts'] == 3, f"Expected total_posts=3, got {search_index['total_posts']}"
        print("✓ Search index contains all posts")
        
        # Verify each post has required fields
        required_fields = ['title', 'url', 'date', 'tags', 'description', 'relative_path']
        for i, post_data in enumerate(search_index['posts']):
            for field in required_fields:
                assert field in post_data, f"Post {i} missing field: {field}"
        print("✓ All posts have required fields")
        
        # Verify specific post data
        post_titles = [p['title'] for p in search_index['posts']]
        assert "Python Tutorial" in post_titles, "Python Tutorial should be in index"
        assert "JavaScript Guide" in post_titles, "JavaScript Guide should be in index"
        assert "中文测试文章" in post_titles, "Chinese post should be in index"
        print("✓ All post titles present in index")
        
        # Verify Chinese characters are preserved
        chinese_post = next(p for p in search_index['posts'] if p['title'] == "中文测试文章")
        assert "测试" in chinese_post['tags'], "Chinese tags should be preserved"
        assert "中文" in chinese_post['tags'], "Chinese tags should be preserved"
        print("✓ Chinese characters preserved correctly")
        
        # Verify URLs are correct
        for post_data in search_index['posts']:
            assert post_data['url'].startswith('/posts/'), "URL should start with /posts/"
            assert post_data['url'].endswith('.html'), "URL should end with .html"
        print("✓ All URLs are correctly formatted")
        
        print("\n✓✓✓ Integration test PASSED ✓✓✓")
        return True


if __name__ == "__main__":
    try:
        test_search_index_generation_integration()
        print("\n" + "=" * 60)
        print("ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
