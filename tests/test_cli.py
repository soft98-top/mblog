"""
测试 CLI 模块
"""
import pytest
import sys
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from mblog.cli import MblogCLI, main
from mblog import __version__, __description__
from mblog.exceptions import MblogError, ProjectExistsError


@pytest.fixture
def cli():
    """创建 CLI 实例"""
    return MblogCLI()


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestCLIInitialization:
    """测试 CLI 初始化"""
    
    def test_cli_initialization(self):
        """测试 CLI 正确初始化"""
        cli = MblogCLI()
        assert cli.parser is not None
        assert cli.parser.prog == 'mblog'
    
    def test_parser_has_version_argument(self, cli):
        """测试解析器包含版本参数"""
        # 测试 --version 参数
        with pytest.raises(SystemExit) as exc_info:
            cli.parser.parse_args(['--version'])
        assert exc_info.value.code == 0
    
    def test_parser_has_help_argument(self, cli):
        """测试解析器包含帮助参数"""
        # 测试 --help 参数
        with pytest.raises(SystemExit) as exc_info:
            cli.parser.parse_args(['--help'])
        assert exc_info.value.code == 0


class TestCommandParsing:
    """测试命令解析"""
    
    def test_parse_new_command_with_project_name(self, cli):
        """测试解析 new 命令和项目名称"""
        args = cli.parser.parse_args(['new', 'my-blog'])
        assert args.command == 'new'
        assert args.project_name == 'my-blog'
        assert args.target_dir is None
    
    def test_parse_new_command_with_target_dir(self, cli):
        """测试解析 new 命令和目标目录"""
        args = cli.parser.parse_args(['new', 'my-blog', '-d', '/tmp/blogs'])
        assert args.command == 'new'
        assert args.project_name == 'my-blog'
        assert args.target_dir == '/tmp/blogs'
    
    def test_parse_new_command_with_long_target_dir_option(self, cli):
        """测试解析 new 命令和长格式目标目录选项"""
        args = cli.parser.parse_args(['new', 'my-blog', '--dir', '/tmp/blogs'])
        assert args.command == 'new'
        assert args.project_name == 'my-blog'
        assert args.target_dir == '/tmp/blogs'
    
    def test_parse_no_command(self, cli):
        """测试解析无命令的情况"""
        args = cli.parser.parse_args([])
        assert args.command is None
    
    def test_parse_invalid_command_raises_error(self, cli):
        """测试解析无效命令抛出错误"""
        with pytest.raises(SystemExit) as exc_info:
            cli.parser.parse_args(['invalid-command'])
        # argparse 在遇到无效命令时返回非零退出码
        assert exc_info.value.code != 0


class TestNewCommand:
    """测试 new 命令"""
    
    def test_handle_new_success(self, cli, temp_dir):
        """测试成功处理 new 命令"""
        project_name = "test-blog"
        exit_code = cli.handle_new(project_name, str(temp_dir))
        
        assert exit_code == 0
        assert (temp_dir / project_name).exists()
    
    def test_handle_new_with_existing_project(self, cli, temp_dir):
        """测试处理已存在的项目"""
        project_name = "test-blog"
        
        # 先创建一个项目
        (temp_dir / project_name).mkdir()
        
        # 尝试再次创建应该失败
        exit_code = cli.handle_new(project_name, str(temp_dir))
        
        assert exit_code == 1
    
    def test_handle_new_with_none_target_dir(self, cli, temp_dir, monkeypatch):
        """测试 target_dir 为 None 时使用当前目录"""
        project_name = "test-blog"
        
        # 改变当前工作目录到临时目录
        monkeypatch.chdir(temp_dir)
        
        exit_code = cli.handle_new(project_name, None)
        
        assert exit_code == 0
        assert (temp_dir / project_name).exists()
    
    def test_handle_new_prints_error_on_project_exists(self, cli, temp_dir, capsys):
        """测试项目已存在时打印错误消息"""
        project_name = "test-blog"
        (temp_dir / project_name).mkdir()
        
        cli.handle_new(project_name, str(temp_dir))
        
        captured = capsys.readouterr()
        assert "✗" in captured.err
        assert "已存在" in captured.err or "exist" in captured.err.lower()
    
    def test_handle_new_prints_error_on_generic_error(self, cli, temp_dir, capsys, monkeypatch):
        """测试一般错误时打印错误消息"""
        project_name = "test-blog"
        
        # 模拟 ProjectInitializer 抛出一般错误
        def mock_init(*args, **kwargs):
            raise Exception("模拟的错误")
        
        with patch('mblog.cli.ProjectInitializer', side_effect=mock_init):
            exit_code = cli.handle_new(project_name, str(temp_dir))
        
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "✗" in captured.err
        assert "错误" in captured.err or "error" in captured.err.lower()


class TestRunMethod:
    """测试 run 方法"""
    
    def test_run_with_new_command(self, cli, temp_dir):
        """测试运行 new 命令"""
        exit_code = cli.run(['new', 'test-blog', '-d', str(temp_dir)])
        assert exit_code == 0
    
    def test_run_with_no_command_shows_help(self, cli, capsys):
        """测试无命令时显示帮助"""
        exit_code = cli.run([])
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert 'mblog' in captured.out
        assert 'new' in captured.out
    
    def test_run_with_version_flag(self, cli, capsys):
        """测试 --version 标志"""
        exit_code = cli.run(['--version'])
        assert exit_code == 0
    
    def test_run_with_help_flag(self, cli, capsys):
        """测试 --help 标志"""
        exit_code = cli.run(['--help'])
        assert exit_code == 0
    
    def test_run_with_invalid_command(self, cli, capsys):
        """测试无效命令"""
        exit_code = cli.run(['invalid-command'])
        assert exit_code != 0
    
    def test_run_handles_keyboard_interrupt(self, cli, monkeypatch, capsys):
        """测试处理键盘中断"""
        def mock_parse_args(*args, **kwargs):
            raise KeyboardInterrupt()
        
        monkeypatch.setattr(cli.parser, 'parse_args', mock_parse_args)
        
        exit_code = cli.run(['new', 'test-blog'])
        
        assert exit_code == 130  # 标准的 Ctrl+C 退出码
        captured = capsys.readouterr()
        assert "取消" in captured.err or "cancel" in captured.err.lower()
    
    def test_run_handles_unexpected_exception(self, cli, monkeypatch, capsys):
        """测试处理未预期的异常"""
        def mock_parse_args(*args, **kwargs):
            raise RuntimeError("未预期的错误")
        
        monkeypatch.setattr(cli.parser, 'parse_args', mock_parse_args)
        
        exit_code = cli.run(['new', 'test-blog'])
        
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "✗" in captured.err
        assert "错误" in captured.err or "error" in captured.err.lower()
    
    def test_run_with_none_args_uses_sys_argv(self, cli, temp_dir, monkeypatch):
        """测试 args 为 None 时使用 sys.argv"""
        # 模拟 sys.argv
        monkeypatch.setattr(sys, 'argv', ['mblog', 'new', 'test-blog', '-d', str(temp_dir)])
        
        exit_code = cli.run(None)
        assert exit_code == 0


class TestHelpAndVersion:
    """测试帮助和版本信息"""
    
    def test_show_help(self, cli, capsys):
        """测试显示帮助信息"""
        cli.show_help()
        
        captured = capsys.readouterr()
        assert 'mblog' in captured.out
        assert 'new' in captured.out
        assert __description__ in captured.out or '博客' in captured.out
    
    def test_show_version(self, cli, capsys):
        """测试显示版本信息"""
        cli.show_version()
        
        captured = capsys.readouterr()
        assert 'mblog' in captured.out
        assert __version__ in captured.out
    
    def test_help_contains_usage_examples(self, cli, capsys):
        """测试帮助信息包含使用示例"""
        cli.show_help()
        
        captured = capsys.readouterr()
        assert '示例' in captured.out or 'example' in captured.out.lower()
        assert 'new' in captured.out
    
    def test_help_contains_command_descriptions(self, cli, capsys):
        """测试帮助信息包含命令描述"""
        cli.show_help()
        
        captured = capsys.readouterr()
        assert 'new' in captured.out
        assert '创建' in captured.out or 'create' in captured.out.lower()


class TestErrorHandling:
    """测试错误处理"""
    
    def test_handles_project_exists_error(self, cli, temp_dir, capsys):
        """测试处理项目已存在错误"""
        project_name = "test-blog"
        (temp_dir / project_name).mkdir()
        
        exit_code = cli.handle_new(project_name, str(temp_dir))
        
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "✗" in captured.err
    
    def test_handles_mblog_error(self, cli, temp_dir, capsys):
        """测试处理 MblogError"""
        project_name = "test-blog"
        
        with patch('mblog.cli.ProjectInitializer') as mock_init:
            mock_instance = Mock()
            mock_instance.create_project.side_effect = MblogError("测试错误")
            mock_init.return_value = mock_instance
            
            exit_code = cli.handle_new(project_name, str(temp_dir))
        
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "✗" in captured.err
        assert "测试错误" in captured.err
    
    def test_handles_generic_exception_with_traceback(self, cli, temp_dir, capsys):
        """测试处理一般异常并打印堆栈跟踪"""
        project_name = "test-blog"
        
        with patch('mblog.cli.ProjectInitializer') as mock_init:
            mock_instance = Mock()
            mock_instance.create_project.side_effect = Exception("一般错误")
            mock_init.return_value = mock_instance
            
            exit_code = cli.handle_new(project_name, str(temp_dir))
        
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "✗" in captured.err
        assert "错误" in captured.err or "error" in captured.err.lower()
    
    def test_returns_correct_exit_codes(self, cli, temp_dir):
        """测试返回正确的退出码"""
        # 成功情况
        exit_code = cli.handle_new("test-blog-1", str(temp_dir))
        assert exit_code == 0
        
        # 失败情况（项目已存在）
        exit_code = cli.handle_new("test-blog-1", str(temp_dir))
        assert exit_code == 1


class TestMainFunction:
    """测试 main 函数"""
    
    def test_main_function_returns_exit_code(self, temp_dir):
        """测试 main 函数返回退出码"""
        exit_code = main(['new', 'test-blog', '-d', str(temp_dir)])
        assert exit_code == 0
    
    def test_main_function_with_no_args(self, capsys):
        """测试 main 函数无参数"""
        exit_code = main([])
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert 'mblog' in captured.out
    
    def test_main_function_with_version(self, capsys):
        """测试 main 函数显示版本"""
        exit_code = main(['--version'])
        assert exit_code == 0
    
    def test_main_function_with_help(self, capsys):
        """测试 main 函数显示帮助"""
        exit_code = main(['--help'])
        assert exit_code == 0
    
    def test_main_function_with_invalid_args(self):
        """测试 main 函数处理无效参数"""
        exit_code = main(['invalid-command'])
        assert exit_code != 0
    
    def test_main_function_creates_cli_instance(self, temp_dir):
        """测试 main 函数创建 CLI 实例"""
        with patch('mblog.cli.MblogCLI') as mock_cli_class:
            mock_cli = Mock()
            mock_cli.run.return_value = 0
            mock_cli_class.return_value = mock_cli
            
            exit_code = main(['new', 'test-blog'])
            
            mock_cli_class.assert_called_once()
            mock_cli.run.assert_called_once()
            assert exit_code == 0


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow_new_command(self, temp_dir):
        """测试完整的 new 命令工作流"""
        cli = MblogCLI()
        project_name = "integration-test-blog"
        
        # 运行命令
        exit_code = cli.run(['new', project_name, '-d', str(temp_dir)])
        
        # 验证结果
        assert exit_code == 0
        project_path = temp_dir / project_name
        assert project_path.exists()
        assert (project_path / "config.json").exists()
        assert (project_path / "gen.py").exists()
        assert (project_path / "_mblog").exists()
    
    def test_cli_with_various_project_names(self, temp_dir):
        """测试 CLI 处理各种项目名称"""
        cli = MblogCLI()
        
        test_names = [
            "simple",
            "with-dashes",
            "with_underscores",
            "MixedCase",
            "with123numbers",
        ]
        
        for name in test_names:
            exit_code = cli.run(['new', name, '-d', str(temp_dir)])
            assert exit_code == 0
            assert (temp_dir / name).exists()
    
    def test_cli_error_recovery(self, temp_dir):
        """测试 CLI 错误恢复"""
        cli = MblogCLI()
        project_name = "error-test"
        
        # 第一次创建应该成功
        exit_code = cli.run(['new', project_name, '-d', str(temp_dir)])
        assert exit_code == 0
        
        # 第二次创建应该失败但不崩溃
        exit_code = cli.run(['new', project_name, '-d', str(temp_dir)])
        assert exit_code == 1
        
        # 创建另一个项目应该仍然可以工作
        exit_code = cli.run(['new', 'another-project', '-d', str(temp_dir)])
        assert exit_code == 0


class TestEdgeCases:
    """测试边界情况"""
    
    def test_empty_project_name(self, cli):
        """测试空项目名称"""
        # argparse 应该捕获这个错误
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['new'])
    
    def test_project_name_with_spaces(self, cli, temp_dir):
        """测试包含空格的项目名称"""
        # 这应该被当作多个参数，argparse 会报错
        with pytest.raises(SystemExit):
            cli.parser.parse_args(['new', 'my', 'blog'])
    
    def test_unicode_project_name(self, cli, temp_dir):
        """测试 Unicode 项目名称"""
        project_name = "我的博客"
        exit_code = cli.handle_new(project_name, str(temp_dir))
        
        assert exit_code == 0
        assert (temp_dir / project_name).exists()
    
    def test_very_long_project_name(self, cli, temp_dir):
        """测试非常长的项目名称"""
        project_name = "a" * 200
        exit_code = cli.handle_new(project_name, str(temp_dir))
        
        # 应该成功或失败，但不应该崩溃
        assert exit_code in [0, 1]
    
    def test_special_characters_in_project_name(self, cli, temp_dir):
        """测试项目名称中的特殊字符"""
        # 某些特殊字符在文件系统中可能无效
        project_name = "test-blog_2024"
        exit_code = cli.handle_new(project_name, str(temp_dir))
        
        assert exit_code == 0
        assert (temp_dir / project_name).exists()


class TestCLIOutput:
    """测试 CLI 输出"""
    
    def test_success_output_format(self, cli, temp_dir, capsys):
        """测试成功输出格式"""
        project_name = "test-blog"
        cli.handle_new(project_name, str(temp_dir))
        
        captured = capsys.readouterr()
        # 成功消息应该在标准输出
        assert len(captured.out) > 0
    
    def test_error_output_to_stderr(self, cli, temp_dir, capsys):
        """测试错误输出到标准错误"""
        project_name = "test-blog"
        (temp_dir / project_name).mkdir()
        
        cli.handle_new(project_name, str(temp_dir))
        
        captured = capsys.readouterr()
        # 错误消息应该在标准错误
        assert len(captured.err) > 0
        assert "✗" in captured.err
    
    def test_help_output_format(self, cli, capsys):
        """测试帮助输出格式"""
        cli.show_help()
        
        captured = capsys.readouterr()
        # 帮助应该包含程序名称和描述
        assert 'mblog' in captured.out
        assert len(captured.out) > 100  # 帮助信息应该相当详细
    
    def test_version_output_format(self, cli, capsys):
        """测试版本输出格式"""
        cli.show_version()
        
        captured = capsys.readouterr()
        assert 'mblog' in captured.out
        assert __version__ in captured.out
        # 版本输出应该简洁
        assert len(captured.out) < 100
