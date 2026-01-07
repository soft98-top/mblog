"""
测试 base_path 在各种生成文件中的正确应用

验证搜索索引、RSS、Sitemap 中的 URL 都正确包含 base_path
"""
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
runtime_path = project_root / "mblog" / "templates" / "runtime"
sys.path.insert(0, str(runtime_path))

# 导入运行时模块
import config as config_module
import theme as theme_module
import renderer as renderer_module
import markdown_processor as md_module
import generator as generator_module

Config = config_module.Config
Theme = theme_module.Theme
Renderer = renderer_module.Renderer
MarkdownProcessor = md_module.MarkdownProcessor
Post = md_module.Post
StaticGenerator = generator_module.StaticGenerator


def test_search_index_with_basepath():
    """测试搜索索引中的 URL 包含 base_path"""
    print("\n=== Test 1: Search Index with base_path ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建配置文件（带 base_path）
        config_data = {
            "site": {
                "title": "测试博客",
                "description": "测试描述",
                "author": "测试作者",
                "url": "https://example.com",
                "base_path": "/myblog",  # 设置 base_path
                "language": "zh-CN"
            },
            "build": {
                "output_dir": str(tmpdir / "public"),
                "theme": "default",
                "md_dir": str(tmpdir / "md")
            },
            "theme_config": {
                "posts_per_page": 10
            }
        }
        
        config_path = tmpdir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # 创建主题目录
        theme_dir = tmpdir / "theme"
        theme_dir.mkdir()
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        # 创建基础模板
        (templates_dir / "base.html").write_text("""
<!DOCTYPE html>
<html>
<head><title>{{ site.title }}</title></head>
<body>{% block content %}{% endblock %}</body>
</html>
        """)
        
        (templates_dir / "index.html").write_text("""
{% extends "base.html" %}
{% block content %}
<h1>首页</h1>
{% endblock %}
        """)
        
        (templates_dir / "post.html").write_text("""
{% extends "base.html" %}
{% block content %}
<article>{{ post.html|safe }}</article>
{% endblock %}
        """)
        
        # 创建 theme.json
        theme_config = {
            "name": "test-theme",
            "version": "1.0.0",
            "templates": {
                "index": "index.html",
                "post": "post.html"
            }
        }
        with open(theme_dir / "theme.json", 'w', encoding='utf-8') as f:
            json.dump(theme_config, f)
        
        # 创建测试文章
        md_dir = tmpdir / "md"
        md_dir.mkdir()
        
        post1 = md_dir / "test-post.md"
        post1.write_text("""---
title: 测试文章
date: 2024-01-01
tags: [测试, Python]
description: 这是一篇测试文章
---

# 测试内容

这是测试文章的内容。
""", encoding='utf-8')
        
        # 加载配置和主题
        config = Config(str(config_path))
        config.load()
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 处理 Markdown
        processor = MarkdownProcessor(str(md_dir), base_path="/myblog")
        posts = processor.process_all()
        
        # 创建渲染器和生成器
        renderer = Renderer(theme, config)
        generator = StaticGenerator(config, theme, renderer, posts)
        
        # 生成静态文件
        generator.generate()
        
        # 验证搜索索引
        search_index_path = tmpdir / "public" / "search-index.json"
        assert search_index_path.exists(), "search-index.json 应该存在"
        
        with open(search_index_path, 'r', encoding='utf-8') as f:
            search_index = json.load(f)
        
        assert 'posts' in search_index, "搜索索引应该包含 posts 字段"
        assert len(search_index['posts']) > 0, "搜索索引应该包含文章"
        
        # 验证 URL 包含 base_path
        for post_data in search_index['posts']:
            url = post_data['url']
            assert url.startswith('/myblog/'), f"URL 应该以 /myblog/ 开头，实际: {url}"
            print(f"✓ 搜索索引 URL 正确: {url}")
        
        print("✓ 搜索索引测试通过")


def test_rss_with_basepath():
    """测试 RSS 中的 URL 包含 base_path"""
    print("\n=== Test 2: RSS with base_path ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建配置文件（带 base_path）
        config_data = {
            "site": {
                "title": "测试博客",
                "description": "测试描述",
                "author": "测试作者",
                "url": "https://example.com",
                "base_path": "/blog",  # 不同的 base_path
                "language": "zh-CN"
            },
            "build": {
                "output_dir": str(tmpdir / "public"),
                "theme": "default",
                "md_dir": str(tmpdir / "md"),
                "generate_rss": True
            },
            "theme_config": {
                "posts_per_page": 10
            }
        }
        
        config_path = tmpdir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # 创建主题目录（复用上面的逻辑）
        theme_dir = tmpdir / "theme"
        theme_dir.mkdir()
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        (templates_dir / "base.html").write_text("""
<!DOCTYPE html>
<html>
<head><title>{{ site.title }}</title></head>
<body>{% block content %}{% endblock %}</body>
</html>
        """)
        
        (templates_dir / "index.html").write_text("""
{% extends "base.html" %}
{% block content %}<h1>首页</h1>{% endblock %}
        """)
        
        (templates_dir / "post.html").write_text("""
{% extends "base.html" %}
{% block content %}<article>{{ post.html|safe }}</article>{% endblock %}
        """)
        
        theme_config = {
            "name": "test-theme",
            "version": "1.0.0",
            "templates": {"index": "index.html", "post": "post.html"}
        }
        with open(theme_dir / "theme.json", 'w', encoding='utf-8') as f:
            json.dump(theme_config, f)
        
        # 创建测试文章
        md_dir = tmpdir / "md"
        md_dir.mkdir()
        
        post1 = md_dir / "rss-test.md"
        post1.write_text("""---
title: RSS测试文章
date: 2024-01-15
tags: [RSS]
description: RSS测试
---

# RSS 内容
""", encoding='utf-8')
        
        # 加载并生成
        config = Config(str(config_path))
        config.load()
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        processor = MarkdownProcessor(str(md_dir), base_path="/blog")
        posts = processor.process_all()
        
        renderer = Renderer(theme, config)
        generator = StaticGenerator(config, theme, renderer, posts)
        generator.generate()
        
        # 验证 RSS
        rss_path = tmpdir / "public" / "rss.xml"
        assert rss_path.exists(), "rss.xml 应该存在"
        
        rss_content = rss_path.read_text(encoding='utf-8')
        
        # 验证 RSS 中的 URL 包含 base_path
        assert 'https://example.com/blog/posts/' in rss_content, "RSS 文章链接应该包含 base_path"
        assert 'https://example.com/blog/rss.xml' in rss_content, "RSS 自链接应该包含 base_path"
        assert '<link>https://example.com/blog/</link>' in rss_content, "RSS 站点链接应该包含 base_path"
        
        print("✓ RSS URL 包含 base_path")
        print("✓ RSS 测试通过")


def test_sitemap_with_basepath():
    """测试 Sitemap 中的 URL 包含 base_path"""
    print("\n=== Test 3: Sitemap with base_path ===")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建配置文件（带 base_path）
        config_data = {
            "site": {
                "title": "测试博客",
                "description": "测试描述",
                "author": "测试作者",
                "url": "https://example.com",
                "base_path": "/site",
                "language": "zh-CN"
            },
            "build": {
                "output_dir": str(tmpdir / "public"),
                "theme": "default",
                "md_dir": str(tmpdir / "md"),
                "generate_sitemap": True
            },
            "theme_config": {
                "posts_per_page": 10
            }
        }
        
        config_path = tmpdir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # 创建主题
        theme_dir = tmpdir / "theme"
        theme_dir.mkdir()
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        (templates_dir / "base.html").write_text("""
<!DOCTYPE html>
<html><body>{% block content %}{% endblock %}</body></html>
        """)
        
        (templates_dir / "index.html").write_text("""
{% extends "base.html" %}
{% block content %}<h1>首页</h1>{% endblock %}
        """)
        
        (templates_dir / "post.html").write_text("""
{% extends "base.html" %}
{% block content %}<article>{{ post.html|safe }}</article>{% endblock %}
        """)
        
        theme_config = {
            "name": "test-theme",
            "version": "1.0.0",
            "templates": {"index": "index.html", "post": "post.html"}
        }
        with open(theme_dir / "theme.json", 'w', encoding='utf-8') as f:
            json.dump(theme_config, f)
        
        # 创建测试文章
        md_dir = tmpdir / "md"
        md_dir.mkdir()
        
        post1 = md_dir / "sitemap-test.md"
        post1.write_text("""---
title: Sitemap测试
date: 2024-01-20
tags: [SEO]
---

# Sitemap 测试
""", encoding='utf-8')
        
        # 加载并生成
        config = Config(str(config_path))
        config.load()
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        processor = MarkdownProcessor(str(md_dir), base_path="/site")
        posts = processor.process_all()
        
        renderer = Renderer(theme, config)
        generator = StaticGenerator(config, theme, renderer, posts)
        generator.generate()
        
        # 验证 Sitemap
        sitemap_path = tmpdir / "public" / "sitemap.xml"
        assert sitemap_path.exists(), "sitemap.xml 应该存在"
        
        sitemap_content = sitemap_path.read_text(encoding='utf-8')
        
        # 验证各种 URL 都包含 base_path
        assert 'https://example.com/site/</loc>' in sitemap_content, "首页 URL 应该包含 base_path"
        assert 'https://example.com/site/archive.html</loc>' in sitemap_content, "归档页 URL 应该包含 base_path"
        assert 'https://example.com/site/tags/</loc>' in sitemap_content, "标签索引 URL 应该包含 base_path"
        assert 'https://example.com/site/posts/' in sitemap_content, "文章 URL 应该包含 base_path"
        
        print("✓ Sitemap 所有 URL 都包含 base_path")
        print("✓ Sitemap 测试通过")


def test_without_basepath():
    """测试没有 base_path 时的正常工作（向后兼容）"""
    print("\n=== Test 4: Without base_path (backward compatibility) ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建配置文件（不设置 base_path）
        config_data = {
            "site": {
                "title": "测试博客",
                "description": "测试描述",
                "author": "测试作者",
                "url": "https://example.com",
                "base_path": "",  # 空 base_path
                "language": "zh-CN"
            },
            "build": {
                "output_dir": str(tmpdir / "public"),
                "theme": "default",
                "md_dir": str(tmpdir / "md")
            },
            "theme_config": {
                "posts_per_page": 10
            }
        }
        
        config_path = tmpdir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # 创建主题
        theme_dir = tmpdir / "theme"
        theme_dir.mkdir()
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        (templates_dir / "base.html").write_text("""
<!DOCTYPE html>
<html><body>{% block content %}{% endblock %}</body></html>
        """)
        
        (templates_dir / "index.html").write_text("""
{% extends "base.html" %}
{% block content %}<h1>首页</h1>{% endblock %}
        """)
        
        (templates_dir / "post.html").write_text("""
{% extends "base.html" %}
{% block content %}<article>{{ post.html|safe }}</article>{% endblock %}
        """)
        
        theme_config = {
            "name": "test-theme",
            "version": "1.0.0",
            "templates": {"index": "index.html", "post": "post.html"}
        }
        with open(theme_dir / "theme.json", 'w', encoding='utf-8') as f:
            json.dump(theme_config, f)
        
        # 创建测试文章
        md_dir = tmpdir / "md"
        md_dir.mkdir()
        
        post1 = md_dir / "normal-test.md"
        post1.write_text("""---
title: 普通测试
date: 2024-01-25
---

# 内容
""", encoding='utf-8')
        
        # 加载并生成
        config = Config(str(config_path))
        config.load()
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        processor = MarkdownProcessor(str(md_dir), base_path="")
        posts = processor.process_all()
        
        renderer = Renderer(theme, config)
        generator = StaticGenerator(config, theme, renderer, posts)
        generator.generate()
        
        # 验证搜索索引（不应该有额外的前缀）
        search_index_path = tmpdir / "public" / "search-index.json"
        with open(search_index_path, 'r', encoding='utf-8') as f:
            search_index = json.load(f)
        
        for post_data in search_index['posts']:
            url = post_data['url']
            assert url.startswith('/posts/'), f"没有 base_path 时，URL 应该以 /posts/ 开头: {url}"
            assert not url.startswith('//'), f"URL 不应该有双斜杠: {url}"
            print(f"✓ 无 base_path 时 URL 正确: {url}")
        
        print("✓ 向后兼容测试通过")


if __name__ == "__main__":
    try:
        test_search_index_with_basepath()
        test_rss_with_basepath()
        test_sitemap_with_basepath()
        test_without_basepath()
        
        print("\n" + "=" * 60)
        print("✅ 所有 base_path URL 测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
