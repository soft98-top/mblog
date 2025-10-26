#!/usr/bin/env python3
"""
测试图片处理功能
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from mblog.templates.runtime.markdown_processor import MarkdownProcessor
from mblog.templates.runtime.generator import StaticGenerator
from mblog.templates.runtime.config import Config
from mblog.templates.runtime.theme import Theme
from mblog.templates.runtime.renderer import Renderer


def test_image_path_extraction():
    """测试图片路径提取"""
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        md_dir = Path(tmpdir) / 'md'
        md_dir.mkdir()
        
        # 创建测试文章和图片
        post_dir = md_dir / 'test-post'
        post_dir.mkdir()
        
        assets_dir = post_dir / 'assets'
        assets_dir.mkdir()
        
        # 创建测试图片
        test_img = assets_dir / 'test.png'
        test_img.write_text('fake image')
        
        # 创建测试文章
        post_file = post_dir / 'test.md'
        post_content = """---
title: Test Post
date: 2024-01-01
---

# Test Post

This is a test post with an image:

![Test Image](./assets/test.png)

And another external image:

![External](https://example.com/image.png)
"""
        post_file.write_text(post_content)
        
        # 处理文章
        processor = MarkdownProcessor(str(md_dir))
        post = processor.parse_post(str(post_file))
        
        # 验证图片被提取
        assert len(post.images) == 1
        # 使用 resolve() 来处理符号链接
        assert test_img.resolve() == Path(post.images[0]).resolve()
        
        # 验证 HTML 中的路径被更新
        assert '/assets/images/test-post/assets/test.png' in post.html
        assert 'https://example.com/image.png' in post.html


def test_image_copying():
    """测试图片复制功能"""
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        md_dir = tmpdir / 'md'
        md_dir.mkdir()
        
        # 创建测试文章和图片
        post_dir = md_dir / 'test-post'
        post_dir.mkdir()
        
        assets_dir = post_dir / 'assets'
        assets_dir.mkdir()
        
        # 创建测试图片
        test_img = assets_dir / 'test.png'
        test_img.write_bytes(b'fake image data')
        
        # 创建测试文章
        post_file = post_dir / 'test.md'
        post_content = """---
title: Test Post
date: 2024-01-01
---

![Test Image](./assets/test.png)
"""
        post_file.write_text(post_content)
        
        # 创建配置
        config_file = tmpdir / 'config.json'
        config_data = {
            "site": {
                "title": "Test Blog",
                "description": "Test Description",
                "author": "Test Author",
                "url": "https://example.com"
            },
            "build": {
                "md_dir": str(md_dir),
                "output_dir": str(tmpdir / 'public'),
                "theme": "default"
            }
        }
        import json
        config_file.write_text(json.dumps(config_data))
        
        # 创建简单主题
        theme_dir = tmpdir / 'theme'
        theme_dir.mkdir()
        theme_json = theme_dir / 'theme.json'
        theme_json.write_text(json.dumps({
            "name": "test",
            "version": "1.0.0",
            "templates": {
                "index": "index.html",
                "post": "post.html",
                "base": "base.html"
            }
        }))
        
        templates_dir = theme_dir / 'templates'
        templates_dir.mkdir()
        
        # 创建模板
        (templates_dir / 'base.html').write_text('<html>{% block content %}{% endblock %}</html>')
        (templates_dir / 'index.html').write_text('{% extends "base.html" %}{% block content %}Index{% endblock %}')
        (templates_dir / 'post.html').write_text('{% extends "base.html" %}{% block content %}{{ post.html|safe }}{% endblock %}')
        
        # 加载配置和主题
        config = Config(str(config_file))
        config.load()
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 处理文章
        processor = MarkdownProcessor(str(md_dir))
        posts = processor.load_posts()
        
        # 初始化渲染器和生成器
        renderer = Renderer(theme, config)
        generator = StaticGenerator(config, theme, renderer, posts)
        
        # 生成静态文件
        generator.generate()
        
        # 验证图片被复制
        output_img = tmpdir / 'public' / 'assets' / 'images' / 'test-post' / 'assets' / 'test.png'
        assert output_img.exists()
        assert output_img.read_bytes() == b'fake image data'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
