#!/usr/bin/env python3
"""
测试分页功能
"""
import pytest
import tempfile
from pathlib import Path
from mblog.templates.runtime.markdown_processor import MarkdownProcessor, Post
from mblog.templates.runtime.renderer import Renderer
from mblog.templates.runtime.config import Config
from mblog.templates.runtime.theme import Theme
from datetime import datetime


def create_test_posts(count=20):
    """创建测试文章列表"""
    posts = []
    for i in range(count):
        post = Post(
            filepath=f'/tmp/post{i}.md',
            slug=f'2024-01-{i+1:02d}-post-{i}',
            relative_path=f'post-{i}',
            title=f'Test Post {i}',
            date=datetime(2024, 1, i+1),
            author='Test Author',
            description=f'Description {i}',
            tags=['test'],
            content=f'Content {i}',
            html=f'<p>Content {i}</p>',
            images=[]
        )
        posts.append(post)
    return posts


def test_pagination_urls():
    """测试分页 URL 生成"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建配置
        config_file = tmpdir / 'config.json'
        config_data = {
            "site": {
                "title": "Test Blog",
                "description": "Test",
                "author": "Test",
                "url": "https://example.com"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            },
            "theme_config": {
                "date_format": "%Y-%m-%d",
                "posts_per_page": 10
            }
        }
        import json
        config_file.write_text(json.dumps(config_data))
        
        # 创建主题
        theme_dir = tmpdir / 'theme'
        theme_dir.mkdir()
        theme_json = theme_dir / 'theme.json'
        theme_json.write_text(json.dumps({
            "name": "test",
            "version": "1.0.0",
            "templates": {
                "index": "index.html",
                "base": "base.html"
            }
        }))
        
        templates_dir = theme_dir / 'templates'
        templates_dir.mkdir()
        
        # 创建模板
        (templates_dir / 'base.html').write_text('<html>{% block content %}{% endblock %}</html>')
        (templates_dir / 'post.html').write_text('{% extends "base.html" %}{% block content %}Post{% endblock %}')
        (templates_dir / 'index.html').write_text('''
{% extends "base.html" %}
{% block content %}
<div class="posts">
{% for post in posts %}
<article>{{ post.title }}</article>
{% endfor %}
</div>
{% if pagination %}
<nav class="pagination">
{% if pagination.has_prev %}
<a href="{{ pagination.prev_url }}" class="prev">Prev</a>
{% endif %}
<span>Page {{ pagination.page }} / {{ pagination.total_pages }}</span>
{% if pagination.has_next %}
<a href="{{ pagination.next_url }}" class="next">Next</a>
{% endif %}
</nav>
{% endif %}
{% endblock %}
''')
        
        # 加载配置和主题
        config = Config(str(config_file))
        config.load()
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 创建渲染器
        renderer = Renderer(theme, config)
        
        # 创建测试文章（20篇，每页10篇，共2页）
        posts = create_test_posts(20)
        
        # 测试第1页
        html_page1 = renderer.render_index(posts, page=1, posts_per_page=10)
        assert 'Page 1 / 2' in html_page1
        assert 'href="/page/2.html"' in html_page1
        assert 'class="next"' in html_page1
        assert 'class="prev"' not in html_page1  # 第1页没有上一页
        
        # 测试第2页
        html_page2 = renderer.render_index(posts, page=2, posts_per_page=10)
        assert 'Page 2 / 2' in html_page2
        assert 'href="/"' in html_page2  # 上一页链接到首页
        assert 'class="prev"' in html_page2
        assert 'class="next"' not in html_page2  # 最后一页没有下一页


def test_pagination_with_three_pages():
    """测试三页分页的 URL"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建配置
        config_file = tmpdir / 'config.json'
        config_data = {
            "site": {
                "title": "Test Blog",
                "description": "Test",
                "author": "Test",
                "url": "https://example.com"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            },
            "theme_config": {
                "date_format": "%Y-%m-%d",
                "posts_per_page": 10
            }
        }
        import json
        config_file.write_text(json.dumps(config_data))
        
        # 创建主题
        theme_dir = tmpdir / 'theme'
        theme_dir.mkdir()
        theme_json = theme_dir / 'theme.json'
        theme_json.write_text(json.dumps({
            "name": "test",
            "version": "1.0.0",
            "templates": {
                "index": "index.html",
                "base": "base.html"
            }
        }))
        
        templates_dir = theme_dir / 'templates'
        templates_dir.mkdir()
        
        # 创建模板
        (templates_dir / 'base.html').write_text('<html>{% block content %}{% endblock %}</html>')
        (templates_dir / 'post.html').write_text('{% extends "base.html" %}{% block content %}Post{% endblock %}')
        (templates_dir / 'index.html').write_text('''
{% extends "base.html" %}
{% block content %}
{% if pagination %}
<nav>
{% if pagination.prev_url %}<a href="{{ pagination.prev_url }}">Prev</a>{% endif %}
<span>{{ pagination.page }}/{{ pagination.total_pages }}</span>
{% if pagination.next_url %}<a href="{{ pagination.next_url }}">Next</a>{% endif %}
</nav>
{% endif %}
{% endblock %}
''')
        
        # 加载配置和主题
        config = Config(str(config_file))
        config.load()
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 创建渲染器
        renderer = Renderer(theme, config)
        
        # 创建测试文章（25篇，每页10篇，共3页）
        posts = create_test_posts(25)
        
        # 测试第1页
        html_page1 = renderer.render_index(posts, page=1, posts_per_page=10)
        assert '1/3' in html_page1
        assert 'href="/page/2.html"' in html_page1
        
        # 测试第2页
        html_page2 = renderer.render_index(posts, page=2, posts_per_page=10)
        assert '2/3' in html_page2
        assert 'href="/"' in html_page2  # 上一页链接到首页
        assert 'href="/page/3.html"' in html_page2
        
        # 测试第3页
        html_page3 = renderer.render_index(posts, page=3, posts_per_page=10)
        assert '3/3' in html_page3
        assert 'href="/page/2.html"' in html_page3
        # 第3页没有下一页链接


def test_no_pagination_when_disabled():
    """测试禁用分页时不显示分页导航"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 创建配置
        config_file = tmpdir / 'config.json'
        config_data = {
            "site": {
                "title": "Test Blog",
                "description": "Test",
                "author": "Test",
                "url": "https://example.com"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            },
            "theme_config": {
                "date_format": "%Y-%m-%d"
            }
        }
        import json
        config_file.write_text(json.dumps(config_data))
        
        # 创建主题
        theme_dir = tmpdir / 'theme'
        theme_dir.mkdir()
        theme_json = theme_dir / 'theme.json'
        theme_json.write_text(json.dumps({
            "name": "test",
            "version": "1.0.0",
            "templates": {
                "index": "index.html",
                "base": "base.html"
            }
        }))
        
        templates_dir = theme_dir / 'templates'
        templates_dir.mkdir()
        
        # 创建模板
        (templates_dir / 'base.html').write_text('<html>{% block content %}{% endblock %}</html>')
        (templates_dir / 'post.html').write_text('{% extends "base.html" %}{% block content %}Post{% endblock %}')
        (templates_dir / 'index.html').write_text('''
{% extends "base.html" %}
{% block content %}
<div class="posts">
{% for post in posts %}
<article>{{ post.title }}</article>
{% endfor %}
</div>
{% if pagination %}
<nav class="pagination">Pagination</nav>
{% endif %}
{% endblock %}
''')
        
        # 加载配置和主题
        config = Config(str(config_file))
        config.load()
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 创建渲染器
        renderer = Renderer(theme, config)
        
        # 创建测试文章
        posts = create_test_posts(20)
        
        # 不分页
        html = renderer.render_index(posts, page=1, posts_per_page=None)
        assert 'Pagination' not in html
        assert len([p for p in posts]) == 20  # 所有文章都显示


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
