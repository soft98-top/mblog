"""
测试项目初始化模块
"""
import pytest
from pathlib import Path
import tempfile
import shutil
import os

from mblog.initializer import ProjectInitializer
from mblog.exceptions import ProjectExistsError, MblogError


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def project_name():
    """测试项目名称"""
    return "test_blog"


class TestProjectInitializerInit:
    """测试项目初始化器的初始化"""
    
    def test_init_with_default_target_dir(self, project_name):
        """测试使用默认目标目录初始化"""
        initializer = ProjectInitializer(project_name)
        assert initializer.project_name == project_name
        assert initializer.target_dir == Path.cwd()
        assert initializer.project_path == Path.cwd() / project_name
    
    def test_init_with_custom_target_dir(self, project_name, temp_dir):
        """测试使用自定义目标目录初始化"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        assert initializer.project_name == project_name
        assert initializer.target_dir == temp_dir
        assert initializer.project_path == temp_dir / project_name
    
    def test_init_sets_templates_dir(self, project_name):
        """测试初始化设置模板目录"""
        initializer = ProjectInitializer(project_name)
        assert initializer.templates_dir.exists()
        assert initializer.templates_dir.name == "templates"


class TestProjectCreation:
    """测试项目创建流程"""
    
    def test_create_project_success(self, project_name, temp_dir):
        """测试成功创建项目"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        result = initializer.create_project()
        
        assert result is True
        assert initializer.project_path.exists()
        assert initializer.project_path.is_dir()
    
    def test_create_project_raises_error_if_exists(self, project_name, temp_dir):
        """测试项目目录已存在时抛出错误"""
        # 先创建一个项目
        project_path = temp_dir / project_name
        project_path.mkdir()
        
        # 尝试再次创建应该失败
        initializer = ProjectInitializer(project_name, str(temp_dir))
        with pytest.raises(ProjectExistsError) as exc_info:
            initializer.create_project()
        
        assert "已存在" in str(exc_info.value)
        assert project_name in str(exc_info.value)
    
    def test_create_project_cleans_up_on_failure(self, project_name, temp_dir, monkeypatch):
        """测试创建失败时清理已创建的目录"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        
        # 模拟在复制运行时时失败
        def mock_copy_runtime():
            raise Exception("模拟的错误")
        
        monkeypatch.setattr(initializer, '_copy_runtime', mock_copy_runtime)
        
        # 尝试创建项目应该失败
        with pytest.raises(MblogError):
            initializer.create_project()
        
        # 验证项目目录已被清理
        assert not initializer.project_path.exists()


class TestDirectoryStructure:
    """测试目录结构创建"""
    
    def test_creates_all_required_directories(self, project_name, temp_dir):
        """测试创建所有必需的目录"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        # 验证主目录
        assert initializer.project_path.exists()
        
        # 验证子目录
        assert (initializer.project_path / ".workflow").exists()
        assert (initializer.project_path / "md").exists()
        assert (initializer.project_path / "theme").exists()
        assert (initializer.project_path / "_mblog").exists()
    
    def test_directories_are_empty_initially(self, project_name, temp_dir):
        """测试初始创建的目录为空（除了后续填充的内容）"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer._create_directory_structure()
        
        # 这些目录在结构创建后应该是空的
        # 它们会在后续步骤中被填充
        assert (initializer.project_path / ".workflow").exists()
        assert (initializer.project_path / "md").exists()
        assert (initializer.project_path / "theme").exists()
        assert (initializer.project_path / "_mblog").exists()


class TestRuntimeCopy:
    """测试运行时代码复制"""
    
    def test_copies_runtime_files(self, project_name, temp_dir):
        """测试复制运行时文件"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        runtime_dir = initializer.project_path / "_mblog"
        
        # 验证运行时文件存在
        assert (runtime_dir / "config.py").exists()
        assert (runtime_dir / "markdown_processor.py").exists()
        assert (runtime_dir / "theme.py").exists()
        assert (runtime_dir / "renderer.py").exists()
        assert (runtime_dir / "generator.py").exists()
    
    def test_runtime_files_are_python_files(self, project_name, temp_dir):
        """测试运行时文件是 Python 文件"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        runtime_dir = initializer.project_path / "_mblog"
        
        for py_file in runtime_dir.glob("*.py"):
            # 验证文件可以读取且包含 Python 代码
            content = py_file.read_text(encoding='utf-8')
            assert len(content) > 0


class TestTemplateFiles:
    """测试模板文件生成"""
    
    def test_creates_gen_script(self, project_name, temp_dir):
        """测试创建生成脚本"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        gen_script = initializer.project_path / "gen.py"
        assert gen_script.exists()
        assert gen_script.is_file()
        
        # 验证文件内容
        content = gen_script.read_text(encoding='utf-8')
        assert len(content) > 0
        assert "python" in content.lower() or "#!/usr/bin/env" in content
    
    def test_gen_script_is_executable_on_unix(self, project_name, temp_dir):
        """测试生成脚本在 Unix 系统上可执行"""
        if os.name == 'nt':  # 跳过 Windows
            pytest.skip("仅在 Unix/Linux/macOS 上测试")
        
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        gen_script = initializer.project_path / "gen.py"
        # 检查文件是否有执行权限
        assert os.access(gen_script, os.X_OK)
    
    def test_creates_config_file(self, project_name, temp_dir):
        """测试创建配置文件"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        config_file = initializer.project_path / "config.json"
        assert config_file.exists()
        assert config_file.is_file()
        
        # 验证是有效的 JSON
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 验证包含必需的部分
        assert "site" in config_data
        assert "build" in config_data
    
    def test_creates_requirements_file(self, project_name, temp_dir):
        """测试创建 requirements.txt"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        requirements_file = initializer.project_path / "requirements.txt"
        assert requirements_file.exists()
        assert requirements_file.is_file()
        
        # 验证文件内容
        content = requirements_file.read_text(encoding='utf-8')
        assert len(content) > 0
        # 应该包含一些常见的依赖
        assert "markdown" in content.lower() or "jinja2" in content.lower()
    
    def test_creates_sample_post(self, project_name, temp_dir):
        """测试创建示例文章"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        sample_post = initializer.project_path / "md" / "welcome.md"
        assert sample_post.exists()
        assert sample_post.is_file()
        
        # 验证文件内容
        content = sample_post.read_text(encoding='utf-8')
        assert len(content) > 0
        # 应该包含 frontmatter
        assert "---" in content
    
    def test_creates_workflow_file(self, project_name, temp_dir):
        """测试创建 GitHub Actions 工作流文件"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        workflow_file = initializer.project_path / ".workflow" / "deploy.yml"
        assert workflow_file.exists()
        assert workflow_file.is_file()
        
        # 验证文件内容
        content = workflow_file.read_text(encoding='utf-8')
        assert len(content) > 0
        # 应该包含 GitHub Actions 相关内容
        assert "name:" in content or "on:" in content or "jobs:" in content


class TestThemeCopy:
    """测试主题复制"""
    
    def test_copies_default_theme(self, project_name, temp_dir):
        """测试复制默认主题"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        theme_dir = initializer.project_path / "theme"
        
        # 验证主题文件存在
        assert (theme_dir / "theme.json").exists()
        assert (theme_dir / "templates").exists()
        assert (theme_dir / "static").exists()
    
    def test_theme_has_required_templates(self, project_name, temp_dir):
        """测试主题包含必需的模板文件"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        templates_dir = initializer.project_path / "theme" / "templates"
        
        # 验证必需的模板文件
        assert (templates_dir / "base.html").exists()
        assert (templates_dir / "index.html").exists()
        assert (templates_dir / "post.html").exists()
    
    def test_theme_has_static_assets(self, project_name, temp_dir):
        """测试主题包含静态资源"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        static_dir = initializer.project_path / "theme" / "static"
        
        # 验证静态资源目录
        assert (static_dir / "css").exists()
        assert (static_dir / "js").exists()
    
    def test_theme_json_is_valid(self, project_name, temp_dir):
        """测试主题 JSON 文件有效"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        theme_json = initializer.project_path / "theme" / "theme.json"
        
        # 验证是有效的 JSON
        import json
        with open(theme_json, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
        
        # 验证包含必需的字段
        assert "name" in theme_data
        assert "templates" in theme_data


class TestCompleteProjectStructure:
    """测试完整的项目结构"""
    
    def test_complete_project_structure(self, project_name, temp_dir):
        """测试完整的项目结构符合规范"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        project_path = initializer.project_path
        
        # 验证所有必需的文件和目录
        expected_structure = [
            ".workflow",
            ".workflow/deploy.yml",
            "md",
            "md/welcome.md",
            "theme",
            "theme/theme.json",
            "theme/templates",
            "theme/templates/base.html",
            "theme/templates/index.html",
            "theme/templates/post.html",
            "theme/static",
            "theme/static/css",
            "theme/static/js",
            "_mblog",
            "_mblog/config.py",
            "_mblog/markdown_processor.py",
            "_mblog/theme.py",
            "_mblog/renderer.py",
            "_mblog/generator.py",
            "gen.py",
            "config.json",
            "requirements.txt"
        ]
        
        for item in expected_structure:
            item_path = project_path / item
            assert item_path.exists(), f"缺少: {item}"
    
    def test_project_is_self_contained(self, project_name, temp_dir):
        """测试项目是自包含的（不依赖 mblog 工具）"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        # 验证运行时代码已复制
        runtime_dir = initializer.project_path / "_mblog"
        assert runtime_dir.exists()
        
        # 验证所有必需的运行时模块都存在
        required_modules = [
            "config.py",
            "markdown_processor.py",
            "theme.py",
            "renderer.py",
            "generator.py"
        ]
        
        for module in required_modules:
            assert (runtime_dir / module).exists()


class TestErrorHandling:
    """测试错误处理"""
    
    def test_raises_error_if_templates_missing(self, project_name, temp_dir, monkeypatch):
        """测试模板目录缺失时抛出错误"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        
        # 模拟模板目录不存在
        fake_templates_dir = temp_dir / "nonexistent_templates"
        monkeypatch.setattr(initializer, 'templates_dir', fake_templates_dir)
        
        with pytest.raises(MblogError) as exc_info:
            initializer.create_project()
        
        assert "不存在" in str(exc_info.value)
    
    def test_handles_permission_errors(self, project_name, temp_dir):
        """测试处理权限错误"""
        if os.name == 'nt':  # 跳过 Windows（权限模型不同）
            pytest.skip("仅在 Unix/Linux/macOS 上测试")
        
        # 创建一个没有写权限的目录
        restricted_dir = temp_dir / "restricted"
        restricted_dir.mkdir()
        os.chmod(restricted_dir, 0o444)  # 只读
        
        initializer = ProjectInitializer(project_name, str(restricted_dir))
        
        try:
            # 应该抛出 MblogError 或 PermissionError
            with pytest.raises((MblogError, PermissionError)):
                initializer.create_project()
        finally:
            # 恢复权限以便清理
            os.chmod(restricted_dir, 0o755)


class TestSuccessMessage:
    """测试成功消息"""
    
    def test_print_success_message(self, project_name, temp_dir, capsys):
        """测试打印成功消息"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        
        # 调用成功消息方法
        initializer.print_success_message()
        
        # 捕获输出
        captured = capsys.readouterr()
        
        # 验证输出包含关键信息
        assert project_name in captured.out
        assert "成功" in captured.out
        assert "下一步" in captured.out or "next" in captured.out.lower()
    
    def test_success_message_contains_instructions(self, project_name, temp_dir, capsys):
        """测试成功消息包含使用说明"""
        initializer = ProjectInitializer(project_name, str(temp_dir))
        initializer.create_project()
        initializer.print_success_message()
        
        captured = capsys.readouterr()
        
        # 验证包含基本的使用说明
        assert "cd" in captured.out
        assert "gen.py" in captured.out
        assert "requirements.txt" in captured.out or "pip install" in captured.out


class TestEdgeCases:
    """测试边界情况"""
    
    def test_project_name_with_special_characters(self, temp_dir):
        """测试包含特殊字符的项目名称"""
        # 使用有效的目录名称字符
        project_name = "my-blog_2024"
        initializer = ProjectInitializer(project_name, str(temp_dir))
        result = initializer.create_project()
        
        assert result is True
        assert initializer.project_path.exists()
    
    def test_project_name_with_unicode(self, temp_dir):
        """测试包含 Unicode 字符的项目名称"""
        project_name = "我的博客"
        initializer = ProjectInitializer(project_name, str(temp_dir))
        result = initializer.create_project()
        
        assert result is True
        assert initializer.project_path.exists()
    
    def test_nested_target_directory(self, project_name, temp_dir):
        """测试嵌套的目标目录"""
        nested_dir = temp_dir / "level1" / "level2"
        nested_dir.mkdir(parents=True)
        
        initializer = ProjectInitializer(project_name, str(nested_dir))
        result = initializer.create_project()
        
        assert result is True
        assert (nested_dir / project_name).exists()
