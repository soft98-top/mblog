"""
测试项目升级功能
"""
import pytest
import shutil
from pathlib import Path
from mblog.initializer import ProjectInitializer, ProjectUpgrader
from mblog.exceptions import MblogError


@pytest.fixture
def test_project(tmp_path):
    """创建一个测试项目"""
    project_name = "test-blog"
    initializer = ProjectInitializer(project_name, str(tmp_path))
    initializer.create_project()
    project_path = tmp_path / project_name
    return project_path


def test_validate_project(test_project):
    """测试项目验证"""
    upgrader = ProjectUpgrader(str(test_project))
    assert upgrader.validate_project() is True


def test_validate_invalid_project(tmp_path):
    """测试无效项目验证"""
    upgrader = ProjectUpgrader(str(tmp_path))
    assert upgrader.validate_project() is False


def test_upgrade_runtime(test_project):
    """测试运行时升级"""
    upgrader = ProjectUpgrader(str(test_project))
    
    # 修改一个运行时文件以测试升级
    generator_file = test_project / "_mblog" / "generator.py"
    original_content = generator_file.read_text()
    generator_file.write_text("# Modified content")
    
    # 执行升级
    upgrader.upgrade_runtime()
    
    # 验证文件已恢复
    new_content = generator_file.read_text()
    assert new_content != "# Modified content"
    assert "# Modified content" not in new_content
    
    # 验证备份已创建
    backup_dirs = list(test_project.glob("_mblog.backup_*"))
    assert len(backup_dirs) > 0


def test_update_theme(test_project):
    """测试主题更新"""
    upgrader = ProjectUpgrader(str(test_project))
    
    # 修改一个主题文件
    theme_json = test_project / "theme" / "theme.json"
    original_content = theme_json.read_text()
    theme_json.write_text('{"modified": true}')
    
    # 执行更新
    upgrader.update_theme()
    
    # 验证文件已恢复
    new_content = theme_json.read_text()
    assert new_content != '{"modified": true}'
    
    # 验证备份已创建
    backup_dirs = list(test_project.glob("theme.backup_*"))
    assert len(backup_dirs) > 0


def test_reset_theme(test_project):
    """测试主题重置"""
    upgrader = ProjectUpgrader(str(test_project))
    
    # 添加一个自定义文件
    custom_file = test_project / "theme" / "custom.txt"
    custom_file.write_text("Custom content")
    
    # 执行重置
    upgrader.reset_theme()
    
    # 验证自定义文件已被删除
    assert not custom_file.exists()
    
    # 验证默认文件仍然存在
    assert (test_project / "theme" / "theme.json").exists()
    
    # 验证备份已创建
    backup_dirs = list(test_project.glob("theme.backup_*"))
    assert len(backup_dirs) > 0


def test_backup_creation(test_project):
    """测试备份创建"""
    upgrader = ProjectUpgrader(str(test_project))
    
    # 创建备份
    backup_dir = upgrader._create_backup(test_project / "_mblog")
    
    # 验证备份目录存在
    assert backup_dir.exists()
    assert backup_dir.name.startswith("_mblog.backup_")
    
    # 验证备份内容完整
    original_files = set(f.name for f in (test_project / "_mblog").glob("*.py"))
    backup_files = set(f.name for f in backup_dir.glob("*.py"))
    assert original_files == backup_files


def test_upgrade_nonexistent_project(tmp_path):
    """测试升级不存在的项目"""
    upgrader = ProjectUpgrader(str(tmp_path / "nonexistent"))
    
    with pytest.raises(MblogError):
        upgrader.upgrade_runtime()
