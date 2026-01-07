#!/usr/bin/env python3
"""
Test Python-JavaScript encryption compatibility
Verifies that content encrypted in Python can be decrypted in JavaScript
"""
import unittest
import subprocess
import json
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mblog.templates.runtime.renderer import Renderer
from mblog.templates.runtime.theme import Theme
from mblog.templates.runtime.config import Config
import tempfile
import shutil


class TestPythonJavaScriptCompatibility(unittest.TestCase):
    """Test cross-language encryption compatibility"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create minimal theme
        theme_dir = Path(self.test_dir) / 'theme'
        theme_dir.mkdir()
        (theme_dir / 'templates').mkdir()
        (theme_dir / 'theme.json').write_text('{"name": "test", "templates": {}}')
        (theme_dir / 'templates' / 'base.html').write_text('<html></html>')
        (theme_dir / 'templates' / 'index.html').write_text('{% extends "base.html" %}')
        (theme_dir / 'templates' / 'post.html').write_text('{% extends "base.html" %}')
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # Create minimal config
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
        
        config_file = Path(self.test_dir) / 'config.json'
        config_file.write_text(json.dumps(config_data))
        
        config = Config(str(config_file))
        config.load()
        
        self.renderer = Renderer(theme, config)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_round_trip_basic(self):
        """Test basic round-trip encryption with ASCII content"""
        content = "Hello, World!"
        password = "test123"
        
        # Encrypt in Python
        encrypted = self.renderer._encrypt_content(content, password)
        
        # Verify format
        parts = encrypted.split(':')
        self.assertEqual(len(parts), 3, "Encrypted data should have 3 parts")
        
        # Try to decrypt in JavaScript
        self._verify_js_decryption(content, encrypted, password)
    
    def test_round_trip_unicode(self):
        """Test round-trip encryption with Unicode content"""
        content = "你好，世界！🌍"
        password = "密码123"
        
        # Encrypt in Python
        encrypted = self.renderer._encrypt_content(content, password)
        
        # Try to decrypt in JavaScript
        self._verify_js_decryption(content, encrypted, password)
    
    def test_round_trip_html(self):
        """Test round-trip encryption with HTML content"""
        content = "<h1>Title</h1><p>This is a <strong>test</strong> with HTML.</p>"
        password = "html_pass"
        
        # Encrypt in Python
        encrypted = self.renderer._encrypt_content(content, password)
        
        # Try to decrypt in JavaScript
        self._verify_js_decryption(content, encrypted, password)
    
    def test_round_trip_special_chars(self):
        """Test round-trip encryption with special characters"""
        content = "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        password = "special!@#"
        
        # Encrypt in Python
        encrypted = self.renderer._encrypt_content(content, password)
        
        # Try to decrypt in JavaScript
        self._verify_js_decryption(content, encrypted, password)
    
    def test_round_trip_long_content(self):
        """Test round-trip encryption with long content"""
        content = "Lorem ipsum dolor sit amet. " * 100
        password = "long_password_with_many_characters_123"
        
        # Encrypt in Python
        encrypted = self.renderer._encrypt_content(content, password)
        
        # Try to decrypt in JavaScript
        self._verify_js_decryption(content, encrypted, password)
    
    def _verify_js_decryption(self, original_content, encrypted_data, password):
        """
        Verify that JavaScript can decrypt Python-encrypted content
        
        Args:
            original_content: Original plaintext
            encrypted_data: Encrypted data from Python
            password: Password used for encryption
        """
        # Check if Node.js is available
        try:
            subprocess.run(['node', '--version'], 
                         capture_output=True, 
                         check=True,
                         timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            self.skipTest("Node.js not available - skipping JavaScript compatibility test")
        
        # Prepare test data
        test_data = {
            'original': original_content,
            'encrypted': encrypted_data,
            'password': password
        }
        
        # Run JavaScript test
        js_test_path = Path(__file__).parent / 'test_js_compat.js'
        
        try:
            result = subprocess.run(
                ['node', str(js_test_path), json.dumps(test_data)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.fail(f"JavaScript decryption failed:\n{result.stderr}\n{result.stdout}")
            
            # Verify success message
            self.assertIn('SUCCESS', result.stdout)
            
        except subprocess.TimeoutExpired:
            self.fail("JavaScript test timed out")
        except Exception as e:
            self.fail(f"Failed to run JavaScript test: {e}")


if __name__ == '__main__':
    unittest.main()
