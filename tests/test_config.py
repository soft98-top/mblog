"""
测试配置管理模块
"""
import json
import pytest
from pathlib import Path
import tempfile
import os
import sys

# 添加 mblog/templates/runtime 到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent / 'mblog' / 'templates' / 'runtime'))

from config import Config, ConfigError


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def valid_config_data():
    """有效的配置数据"""
    return {
        "site": {
            "title": "测试博客",
            "description": "这是一个测试博客",
            "author": "测试作者",
            "url": "https://example.com",
            "language": "zh-CN"
        },
        "build": {
            "output_dir": "public",
            "theme": "default"
        },
        "theme_config": {
            "posts_per_page": 10,
            "date_format": "%Y-%m-%d",
            "show_toc": True
        }
    }


@pytest.fixture
def valid_config_file(temp_dir, valid_config_data):
    """创建有效的配置文件"""
    config_path = temp_dir / "config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(valid_config_data, f, ensure_ascii=False, indent=2)
    return config_path


class TestConfigInit:
    """测试配置初始化"""
    
    def test_init_with_string_path(self, temp_dir):
        """测试使用字符串路径初始化"""
        config_path = str(temp_dir / "config.json")
        config = Config(config_path)
        assert config.config_path == Path(config_path)
        assert config._loaded is False
    
    def test_init_with_path_object(self, temp_dir):
        """测试使用 Path 对象初始化"""
        config_path = temp_dir / "config.json"
        config = Config(str(config_path))
        assert config.config_path == config_path


class TestConfigLoad:
    """测试配置加载功能"""
    
    def test_load_valid_config(self, valid_config_file, valid_config_data):
        """测试加载有效配置"""
        config = Config(str(valid_config_file))
        loaded_data = config.load()
        
        assert config._loaded is True
        assert loaded_data == valid_config_data
        assert config._config_data == valid_config_data
    
    def test_load_nonexistent_file(self, temp_dir):
        """测试加载不存在的配置文件"""
        config_path = temp_dir / "nonexistent.json"
        config = Config(str(config_path))
        
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "配置文件不存在" in str(exc_info.value)
    
    def test_load_invalid_json(self, temp_dir):
        """测试加载无效的 JSON 文件"""
        config_path = temp_dir / "invalid.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("{ invalid json }")
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "配置文件格式错误" in str(exc_info.value)
    
    def test_load_empty_json(self, temp_dir):
        """测试加载空 JSON 文件"""
        config_path = temp_dir / "empty.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("{}")
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "配置缺少必需的部分" in str(exc_info.value)
    
    def test_load_with_utf8_content(self, temp_dir):
        """测试加载包含 UTF-8 字符的配置"""
        config_data = {
            "site": {
                "title": "中文博客",
                "description": "包含中文的描述",
                "author": "作者"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False)
        
        config = Config(str(config_path))
        loaded_data = config.load()
        assert loaded_data["site"]["title"] == "中文博客"
    
    def test_load_file_permission_error(self, temp_dir):
        """测试加载无权限读取的文件"""
        config_data = {
            "site": {
                "title": "标题",
                "description": "描述",
                "author": "作者"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        # 移除读取权限
        os.chmod(config_path, 0o000)
        
        config = Config(str(config_path))
        try:
            with pytest.raises(ConfigError) as exc_info:
                config.load()
            assert "无法读取配置文件" in str(exc_info.value)
        finally:
            # 恢复权限以便清理
            os.chmod(config_path, 0o644)


class TestConfigValidate:
    """测试配置验证功能"""
    
    def test_validate_valid_config(self, valid_config_file):
        """测试验证有效配置"""
        config = Config(str(valid_config_file))
        config.load()
        assert config.validate() is True
    
    def test_validate_missing_site_section(self, temp_dir):
        """测试缺少 site 部分"""
        config_data = {
            "build": {
                "output_dir": "public",
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "配置缺少必需的部分: site" in str(exc_info.value)
    
    def test_validate_missing_build_section(self, temp_dir):
        """测试缺少 build 部分"""
        config_data = {
            "site": {
                "title": "测试",
                "description": "描述",
                "author": "作者"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "配置缺少必需的部分: build" in str(exc_info.value)
    
    def test_validate_missing_site_title(self, temp_dir):
        """测试缺少 site.title 字段"""
        config_data = {
            "site": {
                "description": "描述",
                "author": "作者"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "site 配置缺少必需字段: title" in str(exc_info.value)
    
    def test_validate_missing_site_description(self, temp_dir):
        """测试缺少 site.description 字段"""
        config_data = {
            "site": {
                "title": "标题",
                "author": "作者"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "site 配置缺少必需字段: description" in str(exc_info.value)
    
    def test_validate_missing_site_author(self, temp_dir):
        """测试缺少 site.author 字段"""
        config_data = {
            "site": {
                "title": "标题",
                "description": "描述"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "site 配置缺少必需字段: author" in str(exc_info.value)
    
    def test_validate_missing_build_output_dir(self, temp_dir):
        """测试缺少 build.output_dir 字段"""
        config_data = {
            "site": {
                "title": "标题",
                "description": "描述",
                "author": "作者"
            },
            "build": {
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "build 配置缺少必需字段: output_dir" in str(exc_info.value)
    
    def test_validate_missing_build_theme(self, temp_dir):
        """测试缺少 build.theme 字段"""
        config_data = {
            "site": {
                "title": "标题",
                "description": "描述",
                "author": "作者"
            },
            "build": {
                "output_dir": "public"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        with pytest.raises(ConfigError) as exc_info:
            config.load()
        assert "build 配置缺少必需字段: theme" in str(exc_info.value)


class TestConfigGet:
    """测试配置获取方法"""
    
    def test_get_top_level_key(self, valid_config_file):
        """测试获取顶级键"""
        config = Config(str(valid_config_file))
        config.load()
        
        site = config.get('site')
        assert site is not None
        assert site['title'] == "测试博客"
    
    def test_get_nested_key_with_dot_notation(self, valid_config_file):
        """测试使用点号获取嵌套键"""
        config = Config(str(valid_config_file))
        config.load()
        
        title = config.get('site.title')
        assert title == "测试博客"
        
        output_dir = config.get('build.output_dir')
        assert output_dir == "public"
    
    def test_get_deep_nested_key(self, valid_config_file):
        """测试获取深层嵌套键"""
        config = Config(str(valid_config_file))
        config.load()
        
        posts_per_page = config.get('theme_config.posts_per_page')
        assert posts_per_page == 10
    
    def test_get_nonexistent_key_returns_default(self, valid_config_file):
        """测试获取不存在的键返回默认值"""
        config = Config(str(valid_config_file))
        config.load()
        
        value = config.get('nonexistent', 'default_value')
        assert value == 'default_value'
    
    def test_get_nonexistent_key_returns_none(self, valid_config_file):
        """测试获取不存在的键返回 None"""
        config = Config(str(valid_config_file))
        config.load()
        
        value = config.get('nonexistent')
        assert value is None
    
    def test_get_nonexistent_nested_key(self, valid_config_file):
        """测试获取不存在的嵌套键"""
        config = Config(str(valid_config_file))
        config.load()
        
        value = config.get('site.nonexistent.key', 'default')
        assert value == 'default'
    
    def test_get_before_load_raises_error(self, valid_config_file):
        """测试在加载前获取配置抛出错误"""
        config = Config(str(valid_config_file))
        
        with pytest.raises(ConfigError) as exc_info:
            config.get('site.title')
        assert "配置尚未加载" in str(exc_info.value)
    
    def test_get_with_various_types(self, temp_dir):
        """测试获取不同类型的值"""
        config_data = {
            "site": {
                "title": "标题",
                "description": "描述",
                "author": "作者"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            },
            "settings": {
                "count": 42,
                "enabled": True,
                "ratio": 3.14,
                "items": ["a", "b", "c"],
                "nested": {
                    "key": "value"
                }
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        config.load()
        
        assert config.get('settings.count') == 42
        assert config.get('settings.enabled') is True
        assert config.get('settings.ratio') == 3.14
        assert config.get('settings.items') == ["a", "b", "c"]
        assert config.get('settings.nested.key') == "value"


class TestConfigHelperMethods:
    """测试配置辅助方法"""
    
    def test_get_theme_config(self, valid_config_file):
        """测试获取主题配置"""
        config = Config(str(valid_config_file))
        config.load()
        
        theme_config = config.get_theme_config()
        assert theme_config is not None
        assert theme_config['posts_per_page'] == 10
        assert theme_config['date_format'] == "%Y-%m-%d"
        assert theme_config['show_toc'] is True
    
    def test_get_theme_config_when_missing(self, temp_dir):
        """测试获取不存在的主题配置"""
        config_data = {
            "site": {
                "title": "标题",
                "description": "描述",
                "author": "作者"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        config.load()
        
        theme_config = config.get_theme_config()
        assert theme_config == {}
    
    def test_get_site_config(self, valid_config_file):
        """测试获取站点配置"""
        config = Config(str(valid_config_file))
        config.load()
        
        site_config = config.get_site_config()
        assert site_config is not None
        assert site_config['title'] == "测试博客"
        assert site_config['author'] == "测试作者"
    
    def test_get_build_config(self, valid_config_file):
        """测试获取构建配置"""
        config = Config(str(valid_config_file))
        config.load()
        
        build_config = config.get_build_config()
        assert build_config is not None
        assert build_config['output_dir'] == "public"
        assert build_config['theme'] == "default"
    
    def test_data_property(self, valid_config_file, valid_config_data):
        """测试 data 属性"""
        config = Config(str(valid_config_file))
        config.load()
        
        data = config.data
        assert data == valid_config_data
    
    def test_data_property_before_load_raises_error(self, valid_config_file):
        """测试在加载前访问 data 属性抛出错误"""
        config = Config(str(valid_config_file))
        
        with pytest.raises(ConfigError) as exc_info:
            _ = config.data
        assert "配置尚未加载" in str(exc_info.value)


class TestConfigEdgeCases:
    """测试配置边界情况"""
    
    def test_config_with_extra_fields(self, temp_dir):
        """测试包含额外字段的配置"""
        config_data = {
            "site": {
                "title": "标题",
                "description": "描述",
                "author": "作者",
                "extra_field": "额外值"
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            },
            "custom_section": {
                "key": "value"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        loaded_data = config.load()
        
        assert loaded_data == config_data
        assert config.get('site.extra_field') == "额外值"
        assert config.get('custom_section.key') == "value"
    
    def test_reload_config(self, temp_dir, valid_config_data):
        """测试重新加载配置"""
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(valid_config_data, f)
        
        config = Config(str(config_path))
        config.load()
        
        original_title = config.get('site.title')
        assert original_title == "测试博客"
        
        # 修改配置文件
        valid_config_data['site']['title'] = "新标题"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(valid_config_data, f)
        
        # 重新加载
        config.load()
        new_title = config.get('site.title')
        assert new_title == "新标题"
    
    def test_config_with_empty_strings(self, temp_dir):
        """测试包含空字符串的配置"""
        config_data = {
            "site": {
                "title": "",
                "description": "",
                "author": ""
            },
            "build": {
                "output_dir": "public",
                "theme": "default"
            }
        }
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        config = Config(str(config_path))
        # 应该能加载，即使字段为空字符串
        config.load()
        assert config.get('site.title') == ""
