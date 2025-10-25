"""
测试主题管理模块
"""
import json
import pytest
from pathlib import Path
import tempfile
import sys

# 添加 mblog/templates/runtime 到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent / 'mblog' / 'templates' / 'runtime'))

from theme import Theme, ThemeError


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def valid_theme_metadata():
    """有效的主题元数据"""
    return {
        "name": "test-theme",
        "version": "1.0.0",
        "author": "Test Author",
        "description": "测试主题",
        "templates": {
            "base": "base.html",
            "index": "index.html",
            "post": "post.html"
        }
    }


@pytest.fixture
def valid_theme_dir(temp_dir, valid_theme_metadata):
    """创建有效的主题目录结构"""
    theme_dir = temp_dir / "test-theme"
    theme_dir.mkdir()
    
    # 创建 theme.json
    theme_json_path = theme_dir / "theme.json"
    with open(theme_json_path, 'w', encoding='utf-8') as f:
        json.dump(valid_theme_metadata, f, ensure_ascii=False, indent=2)
    
    # 创建 templates 目录和必需的模板文件
    templates_dir = theme_dir / "templates"
    templates_dir.mkdir()
    
    for template_name in ["base.html", "index.html", "post.html"]:
        template_path = templates_dir / template_name
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(f"<html><!-- {template_name} --></html>")
    
    # 创建 static 目录
    static_dir = theme_dir / "static"
    static_dir.mkdir()
    
    css_dir = static_dir / "css"
    css_dir.mkdir()
    (css_dir / "style.css").write_text("body { margin: 0; }")
    
    js_dir = static_dir / "js"
    js_dir.mkdir()
    (js_dir / "main.js").write_text("console.log('test');")
    
    return theme_dir


@pytest.fixture
def minimal_theme_dir(temp_dir):
    """创建最小化的主题目录（没有 theme.json）"""
    theme_dir = temp_dir / "minimal-theme"
    theme_dir.mkdir()
    
    # 创建 templates 目录和必需的模板文件
    templates_dir = theme_dir / "templates"
    templates_dir.mkdir()
    
    for template_name in ["base.html", "index.html", "post.html"]:
        template_path = templates_dir / template_name
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(f"<html><!-- {template_name} --></html>")
    
    return theme_dir


class TestThemeInit:
    """测试主题初始化"""
    
    def test_init_with_string_path(self, temp_dir):
        """测试使用字符串路径初始化"""
        theme_path = str(temp_dir / "theme")
        theme = Theme(theme_path)
        assert theme.theme_dir == Path(theme_path)
        assert theme._loaded is False
        assert theme._metadata == {}
    
    def test_init_with_path_object(self, temp_dir):
        """测试使用 Path 对象初始化"""
        theme_path = temp_dir / "theme"
        theme = Theme(str(theme_path))
        assert theme.theme_dir == theme_path
        assert theme._loaded is False


class TestThemeLoad:
    """测试主题加载功能"""
    
    def test_load_valid_theme(self, valid_theme_dir, valid_theme_metadata):
        """测试加载有效主题"""
        theme = Theme(str(valid_theme_dir))
        result = theme.load()
        
        assert result is True
        assert theme._loaded is True
        assert theme._metadata == valid_theme_metadata
    
    def test_load_nonexistent_directory(self, temp_dir):
        """测试加载不存在的主题目录"""
        theme_path = temp_dir / "nonexistent"
        theme = Theme(str(theme_path))
        
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "主题目录不存在" in str(exc_info.value)
    
    def test_load_file_instead_of_directory(self, temp_dir):
        """测试加载文件而不是目录"""
        file_path = temp_dir / "not_a_dir.txt"
        file_path.write_text("test")
        
        theme = Theme(str(file_path))
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "主题路径不是目录" in str(exc_info.value)
    
    def test_load_theme_without_metadata(self, minimal_theme_dir):
        """测试加载没有 theme.json 的主题"""
        theme = Theme(str(minimal_theme_dir))
        result = theme.load()
        
        assert result is True
        assert theme._loaded is True
        # 应该使用默认元数据
        assert theme._metadata['name'] == minimal_theme_dir.name
        assert theme._metadata['version'] == '1.0.0'
        assert 'templates' in theme._metadata
    
    def test_load_theme_with_invalid_json(self, temp_dir):
        """测试加载包含无效 JSON 的主题"""
        theme_dir = temp_dir / "invalid-theme"
        theme_dir.mkdir()
        
        # 创建无效的 theme.json
        theme_json_path = theme_dir / "theme.json"
        with open(theme_json_path, 'w', encoding='utf-8') as f:
            f.write("{ invalid json }")
        
        # 创建必需的模板
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        for template_name in ["base.html", "index.html", "post.html"]:
            (templates_dir / template_name).write_text("<html></html>")
        
        theme = Theme(str(theme_dir))
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "主题元数据文件格式错误" in str(exc_info.value)
    
    def test_load_theme_with_utf8_metadata(self, temp_dir):
        """测试加载包含 UTF-8 字符的主题元数据"""
        theme_dir = temp_dir / "utf8-theme"
        theme_dir.mkdir()
        
        metadata = {
            "name": "中文主题",
            "version": "1.0.0",
            "author": "作者名",
            "description": "这是一个中文主题",
            "templates": {}
        }
        
        theme_json_path = theme_dir / "theme.json"
        with open(theme_json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False)
        
        # 创建必需的模板
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        for template_name in ["base.html", "index.html", "post.html"]:
            (templates_dir / template_name).write_text("<html></html>")
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        assert theme._metadata['name'] == "中文主题"
        assert theme._metadata['author'] == "作者名"


class TestThemeValidateStructure:
    """测试主题结构验证"""
    
    def test_validate_valid_structure(self, valid_theme_dir):
        """测试验证有效的主题结构"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        assert theme.validate_structure() is True
    
    def test_validate_missing_templates_directory(self, temp_dir):
        """测试缺少 templates 目录"""
        theme_dir = temp_dir / "no-templates"
        theme_dir.mkdir()
        
        theme = Theme(str(theme_dir))
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "主题缺少 templates 目录" in str(exc_info.value)
    
    def test_validate_templates_is_file_not_directory(self, temp_dir):
        """测试 templates 是文件而不是目录"""
        theme_dir = temp_dir / "bad-templates"
        theme_dir.mkdir()
        
        # 创建 templates 作为文件
        (theme_dir / "templates").write_text("not a directory")
        
        theme = Theme(str(theme_dir))
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "主题缺少 templates 目录" in str(exc_info.value)
    
    def test_validate_missing_base_template(self, temp_dir):
        """测试缺少 base.html 模板"""
        theme_dir = temp_dir / "no-base"
        theme_dir.mkdir()
        
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        # 只创建部分模板
        (templates_dir / "index.html").write_text("<html></html>")
        (templates_dir / "post.html").write_text("<html></html>")
        
        theme = Theme(str(theme_dir))
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "主题缺少必需的模板文件: base.html" in str(exc_info.value)
    
    def test_validate_missing_index_template(self, temp_dir):
        """测试缺少 index.html 模板"""
        theme_dir = temp_dir / "no-index"
        theme_dir.mkdir()
        
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        (templates_dir / "base.html").write_text("<html></html>")
        (templates_dir / "post.html").write_text("<html></html>")
        
        theme = Theme(str(theme_dir))
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "主题缺少必需的模板文件: index.html" in str(exc_info.value)
    
    def test_validate_missing_post_template(self, temp_dir):
        """测试缺少 post.html 模板"""
        theme_dir = temp_dir / "no-post"
        theme_dir.mkdir()
        
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        (templates_dir / "base.html").write_text("<html></html>")
        (templates_dir / "index.html").write_text("<html></html>")
        
        theme = Theme(str(theme_dir))
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "主题缺少必需的模板文件: post.html" in str(exc_info.value)
    
    def test_validate_static_is_file_not_directory(self, temp_dir):
        """测试 static 是文件而不是目录"""
        theme_dir = temp_dir / "bad-static"
        theme_dir.mkdir()
        
        # 创建必需的模板
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        for template_name in ["base.html", "index.html", "post.html"]:
            (templates_dir / template_name).write_text("<html></html>")
        
        # 创建 static 作为文件
        (theme_dir / "static").write_text("not a directory")
        
        theme = Theme(str(theme_dir))
        with pytest.raises(ThemeError) as exc_info:
            theme.load()
        assert "static 路径存在但不是目录" in str(exc_info.value)
    
    def test_validate_theme_without_static_directory(self, minimal_theme_dir):
        """测试没有 static 目录的主题（应该是有效的）"""
        theme = Theme(str(minimal_theme_dir))
        result = theme.load()
        
        assert result is True
        assert theme.validate_structure() is True


class TestThemeGetTemplate:
    """测试获取模板文件路径"""
    
    def test_get_template_before_load_raises_error(self, valid_theme_dir):
        """测试在加载前获取模板抛出错误"""
        theme = Theme(str(valid_theme_dir))
        
        with pytest.raises(ThemeError) as exc_info:
            theme.get_template("index.html")
        assert "主题尚未加载" in str(exc_info.value)
    
    def test_get_template_with_full_name(self, valid_theme_dir):
        """测试使用完整文件名获取模板"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        template_path = theme.get_template("index.html")
        assert Path(template_path).exists()
        assert Path(template_path).name == "index.html"
        assert "index.html" in template_path
    
    def test_get_template_without_extension(self, valid_theme_dir):
        """测试使用不带扩展名的名称获取模板"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        template_path = theme.get_template("index")
        assert Path(template_path).exists()
        assert Path(template_path).name == "index.html"
    
    def test_get_template_with_metadata_mapping(self, valid_theme_dir):
        """测试使用元数据映射获取模板"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        # 元数据中定义了 "index": "index.html"
        template_path = theme.get_template("index")
        assert Path(template_path).exists()
        assert Path(template_path).name == "index.html"
    
    def test_get_all_required_templates(self, valid_theme_dir):
        """测试获取所有必需的模板"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        for template_name in ["base.html", "index.html", "post.html"]:
            template_path = theme.get_template(template_name)
            assert Path(template_path).exists()
            assert Path(template_path).name == template_name
    
    def test_get_nonexistent_template(self, valid_theme_dir):
        """测试获取不存在的模板"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        with pytest.raises(ThemeError) as exc_info:
            theme.get_template("nonexistent.html")
        assert "模板文件不存在" in str(exc_info.value)
    
    def test_get_template_returns_absolute_path(self, valid_theme_dir):
        """测试获取模板返回绝对路径"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        template_path = theme.get_template("index.html")
        assert Path(template_path).is_absolute()


class TestThemeGetStaticDir:
    """测试获取静态资源目录"""
    
    def test_get_static_dir_before_load_raises_error(self, valid_theme_dir):
        """测试在加载前获取静态目录抛出错误"""
        theme = Theme(str(valid_theme_dir))
        
        with pytest.raises(ThemeError) as exc_info:
            theme.get_static_dir()
        assert "主题尚未加载" in str(exc_info.value)
    
    def test_get_static_dir_when_exists(self, valid_theme_dir):
        """测试获取存在的静态目录"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        static_dir = theme.get_static_dir()
        assert static_dir != ""
        assert Path(static_dir).exists()
        assert Path(static_dir).is_dir()
        assert Path(static_dir).name == "static"
    
    def test_get_static_dir_when_not_exists(self, minimal_theme_dir):
        """测试获取不存在的静态目录"""
        theme = Theme(str(minimal_theme_dir))
        theme.load()
        
        static_dir = theme.get_static_dir()
        assert static_dir == ""
    
    def test_get_static_dir_returns_absolute_path(self, valid_theme_dir):
        """测试获取静态目录返回绝对路径"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        static_dir = theme.get_static_dir()
        assert Path(static_dir).is_absolute()


class TestThemeGetTemplatesDir:
    """测试获取模板目录"""
    
    def test_get_templates_dir_before_load_raises_error(self, valid_theme_dir):
        """测试在加载前获取模板目录抛出错误"""
        theme = Theme(str(valid_theme_dir))
        
        with pytest.raises(ThemeError) as exc_info:
            theme.get_templates_dir()
        assert "主题尚未加载" in str(exc_info.value)
    
    def test_get_templates_dir(self, valid_theme_dir):
        """测试获取模板目录"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        templates_dir = theme.get_templates_dir()
        assert Path(templates_dir).exists()
        assert Path(templates_dir).is_dir()
        assert Path(templates_dir).name == "templates"
    
    def test_get_templates_dir_returns_absolute_path(self, valid_theme_dir):
        """测试获取模板目录返回绝对路径"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        templates_dir = theme.get_templates_dir()
        assert Path(templates_dir).is_absolute()


class TestThemeProperties:
    """测试主题属性"""
    
    def test_name_property_after_load(self, valid_theme_dir):
        """测试加载后的 name 属性"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        assert theme.name == "test-theme"
    
    def test_name_property_before_load(self, valid_theme_dir):
        """测试加载前的 name 属性"""
        theme = Theme(str(valid_theme_dir))
        
        assert theme.name == ""
    
    def test_name_property_without_metadata(self, minimal_theme_dir):
        """测试没有元数据时的 name 属性"""
        theme = Theme(str(minimal_theme_dir))
        theme.load()
        
        # 应该使用目录名
        assert theme.name == minimal_theme_dir.name
    
    def test_version_property_after_load(self, valid_theme_dir):
        """测试加载后的 version 属性"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        assert theme.version == "1.0.0"
    
    def test_version_property_before_load(self, valid_theme_dir):
        """测试加载前的 version 属性"""
        theme = Theme(str(valid_theme_dir))
        
        assert theme.version == ""
    
    def test_version_property_without_metadata(self, minimal_theme_dir):
        """测试没有元数据时的 version 属性"""
        theme = Theme(str(minimal_theme_dir))
        theme.load()
        
        # 应该使用默认版本
        assert theme.version == "1.0.0"
    
    def test_metadata_property_after_load(self, valid_theme_dir, valid_theme_metadata):
        """测试加载后的 metadata 属性"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        metadata = theme.metadata
        assert metadata == valid_theme_metadata
        # 确保返回的是副本
        metadata['name'] = "modified"
        assert theme.metadata['name'] == "test-theme"
    
    def test_metadata_property_before_load_raises_error(self, valid_theme_dir):
        """测试加载前访问 metadata 属性抛出错误"""
        theme = Theme(str(valid_theme_dir))
        
        with pytest.raises(ThemeError) as exc_info:
            _ = theme.metadata
        assert "主题尚未加载" in str(exc_info.value)


class TestThemeEdgeCases:
    """测试主题边界情况"""
    
    def test_theme_with_extra_templates(self, temp_dir):
        """测试包含额外模板的主题"""
        theme_dir = temp_dir / "extra-templates"
        theme_dir.mkdir()
        
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        # 创建必需的模板
        for template_name in ["base.html", "index.html", "post.html"]:
            (templates_dir / template_name).write_text("<html></html>")
        
        # 创建额外的模板
        (templates_dir / "archive.html").write_text("<html></html>")
        (templates_dir / "tag.html").write_text("<html></html>")
        
        theme = Theme(str(theme_dir))
        result = theme.load()
        
        assert result is True
        # 应该能获取额外的模板
        archive_path = theme.get_template("archive.html")
        assert Path(archive_path).exists()
    
    def test_theme_with_nested_static_structure(self, temp_dir):
        """测试包含嵌套静态资源结构的主题"""
        theme_dir = temp_dir / "nested-static"
        theme_dir.mkdir()
        
        # 创建必需的模板
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        for template_name in ["base.html", "index.html", "post.html"]:
            (templates_dir / template_name).write_text("<html></html>")
        
        # 创建嵌套的静态资源结构
        static_dir = theme_dir / "static"
        static_dir.mkdir()
        
        css_dir = static_dir / "css" / "vendor"
        css_dir.mkdir(parents=True)
        (css_dir / "bootstrap.css").write_text("/* css */")
        
        js_dir = static_dir / "js" / "lib"
        js_dir.mkdir(parents=True)
        (js_dir / "jquery.js").write_text("/* js */")
        
        images_dir = static_dir / "images" / "icons"
        images_dir.mkdir(parents=True)
        (images_dir / "logo.png").write_text("fake image")
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        static_path = Path(theme.get_static_dir())
        assert static_path.exists()
        assert (static_path / "css" / "vendor" / "bootstrap.css").exists()
        assert (static_path / "js" / "lib" / "jquery.js").exists()
        assert (static_path / "images" / "icons" / "logo.png").exists()
    
    def test_reload_theme(self, valid_theme_dir):
        """测试重新加载主题"""
        theme = Theme(str(valid_theme_dir))
        theme.load()
        
        original_name = theme.name
        assert original_name == "test-theme"
        
        # 修改元数据
        theme_json_path = valid_theme_dir / "theme.json"
        with open(theme_json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        metadata['name'] = "modified-theme"
        
        with open(theme_json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False)
        
        # 重新加载
        theme.load()
        assert theme.name == "modified-theme"
    
    def test_theme_with_custom_template_mapping(self, temp_dir):
        """测试使用自定义模板映射的主题"""
        theme_dir = temp_dir / "custom-mapping"
        theme_dir.mkdir()
        
        # 创建自定义的元数据
        metadata = {
            "name": "custom",
            "version": "1.0.0",
            "templates": {
                "base": "layout.html",
                "index": "home.html",
                "post": "article.html"
            }
        }
        
        theme_json_path = theme_dir / "theme.json"
        with open(theme_json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f)
        
        # 创建对应的模板文件
        templates_dir = theme_dir / "templates"
        templates_dir.mkdir()
        
        # 使用映射中的文件名
        (templates_dir / "layout.html").write_text("<html></html>")
        (templates_dir / "home.html").write_text("<html></html>")
        (templates_dir / "article.html").write_text("<html></html>")
        
        # 但验证仍然需要标准名称
        (templates_dir / "base.html").write_text("<html></html>")
        (templates_dir / "index.html").write_text("<html></html>")
        (templates_dir / "post.html").write_text("<html></html>")
        
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 使用映射键获取模板
        base_path = theme.get_template("base")
        assert "layout.html" in base_path
        
        index_path = theme.get_template("index")
        assert "home.html" in index_path
        
        post_path = theme.get_template("post")
        assert "article.html" in post_path
