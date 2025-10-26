#!/usr/bin/env python3
"""
加密功能测试
"""
import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mblog.templates.runtime.markdown_processor import MarkdownProcessor, Post
from mblog.templates.runtime.theme import Theme
from mblog.templates.runtime.config import Config
from mblog.templates.runtime.renderer import Renderer


class TestEncryption(unittest.TestCase):
    """测试加密功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp()
        self.md_dir = Path(self.test_dir) / 'md'
        self.md_dir.mkdir()
        
        # 创建测试文章
        self.create_test_post()
        
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.test_dir)
    
    def create_test_post(self):
        """创建测试文章"""
        # 普通文章
        normal_post = self.md_dir / 'normal.md'
        normal_post.write_text("""---
title: Normal Post
date: 2025-10-26
---

This is a normal post.
""", encoding='utf-8')
        
        # 加密文章
        encrypted_post = self.md_dir / 'encrypted.md'
        encrypted_post.write_text("""---
title: Encrypted Post
date: 2025-10-26
encrypted: true
password: "test123"
---

This is an encrypted post.
""", encoding='utf-8')
    
    def test_post_encryption_fields(self):
        """测试 Post 对象的加密字段"""
        processor = MarkdownProcessor(str(self.md_dir))
        posts = processor.load_posts()
        
        # 应该有两篇文章
        self.assertEqual(len(posts), 2)
        
        # 找到加密文章
        encrypted_post = None
        normal_post = None
        
        for post in posts:
            if post.encrypted:
                encrypted_post = post
            else:
                normal_post = post
        
        # 验证加密文章
        self.assertIsNotNone(encrypted_post)
        self.assertTrue(encrypted_post.encrypted)
        self.assertEqual(encrypted_post.password, "test123")
        self.assertEqual(encrypted_post.title, "Encrypted Post")
        
        # 验证普通文章
        self.assertIsNotNone(normal_post)
        self.assertFalse(normal_post.encrypted)
        self.assertEqual(normal_post.password, "")
        self.assertEqual(normal_post.title, "Normal Post")
    
    def test_encryption_algorithm(self):
        """测试加密算法"""
        # 创建一个简单的渲染器来测试加密
        config_data = {
            'site': {
                'title': 'Test',
                'description': 'Test Blog',
                'author': 'Test Author',
                'url': 'http://test.com'
            },
            'build': {'output_dir': 'public', 'theme': 'default'},
            'theme_config': {}
        }
        
        # 创建临时主题目录
        theme_dir = Path(self.test_dir) / 'theme'
        theme_dir.mkdir()
        (theme_dir / 'templates').mkdir()
        (theme_dir / 'theme.json').write_text('{"name": "test", "templates": {}}')
        (theme_dir / 'templates' / 'base.html').write_text('<html></html>')
        (theme_dir / 'templates' / 'index.html').write_text('{% extends "base.html" %}')
        (theme_dir / 'templates' / 'post.html').write_text('{% extends "base.html" %}')
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 创建配置文件
        import json
        config_file = Path(self.test_dir) / 'config.json'
        config_file.write_text(json.dumps(config_data))
        
        config = Config(str(config_file))
        config.load()
        renderer = Renderer(theme, config)
        
        # 测试加密
        content = "Hello, World!"
        password = "test123"
        
        encrypted = renderer._encrypt_content(content, password)
        
        # 验证加密结果格式
        self.assertIn(':', encrypted)
        parts = encrypted.split(':')
        self.assertEqual(len(parts), 2)
        
        # IV 和加密数据都应该是 base64 编码
        import base64
        try:
            base64.b64decode(parts[0])
            base64.b64decode(parts[1])
        except Exception as e:
            self.fail(f"加密结果不是有效的 base64: {e}")
    
    def test_theme_has_template(self):
        """测试主题模板检测"""
        # 创建临时主题目录
        theme_dir = Path(self.test_dir) / 'theme'
        theme_dir.mkdir()
        (theme_dir / 'templates').mkdir()
        
        # 创建 theme.json
        theme_json = {
            "name": "test",
            "templates": {
                "base": "base.html",
                "index": "index.html",
                "post": "post.html",
                "encrypted_post": "encrypted_post.html"
            }
        }
        
        import json
        (theme_dir / 'theme.json').write_text(json.dumps(theme_json))
        
        # 创建必需的模板文件
        (theme_dir / 'templates' / 'base.html').write_text('<html></html>')
        (theme_dir / 'templates' / 'index.html').write_text('index')
        (theme_dir / 'templates' / 'post.html').write_text('post')
        (theme_dir / 'templates' / 'encrypted_post.html').write_text('encrypted')
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 测试模板检测
        self.assertTrue(theme.has_template('base'))
        self.assertTrue(theme.has_template('index'))
        self.assertTrue(theme.has_template('post'))
        self.assertTrue(theme.has_template('encrypted_post'))
        self.assertFalse(theme.has_template('nonexistent'))


if __name__ == '__main__':
    unittest.main()
