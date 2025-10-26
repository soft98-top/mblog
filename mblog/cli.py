"""
mblog CLI 模块

命令行界面的主要实现
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from mblog import __version__, __description__
from mblog.initializer import ProjectInitializer
from mblog.exceptions import MblogError, ProjectExistsError


class MblogCLI:
    """mblog 命令行界面
    
    负责解析命令行参数并执行相应的命令。
    """
    
    def __init__(self):
        """初始化 CLI 解析器"""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器
        
        Returns:
            argparse.ArgumentParser: 配置好的参数解析器
        """
        parser = argparse.ArgumentParser(
            prog='mblog',
            description=__description__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  mblog new my-blog          创建名为 my-blog 的新博客项目
  mblog upgrade              升级当前博客的运行时到最新版本
  mblog theme update         更新当前博客的主题文件
  mblog theme reset          重置主题为默认主题
  mblog --version            显示版本信息

更多信息请访问: https://github.com/username/mblog
            """
        )
        
        # 添加版本选项
        parser.add_argument(
            '-v', '--version',
            action='version',
            version=f'%(prog)s {__version__}'
        )
        
        # 创建子命令
        subparsers = parser.add_subparsers(
            dest='command',
            help='可用命令'
        )
        
        # new 命令
        new_parser = subparsers.add_parser(
            'new',
            help='创建新的博客项目',
            description='创建一个新的博客项目，包含完整的目录结构、配置文件和默认主题'
        )
        new_parser.add_argument(
            'project_name',
            help='项目名称（将作为目录名）'
        )
        new_parser.add_argument(
            '-d', '--dir',
            dest='target_dir',
            help='目标目录（默认为当前目录）',
            default=None
        )
        
        # upgrade 命令
        upgrade_parser = subparsers.add_parser(
            'upgrade',
            help='升级博客运行时到最新版本',
            description='更新 _mblog/ 目录中的运行时文件到最新版本'
        )
        upgrade_parser.add_argument(
            '-p', '--path',
            dest='project_path',
            help='博客项目路径（默认为当前目录）',
            default='.'
        )
        upgrade_parser.add_argument(
            '-f', '--force',
            action='store_true',
            help='强制覆盖，不进行备份确认'
        )
        
        # theme 命令
        theme_parser = subparsers.add_parser(
            'theme',
            help='管理博客主题',
            description='更换或更新博客主题'
        )
        theme_parser.add_argument(
            'action',
            choices=['update', 'reset'],
            help='操作类型：update=更新当前主题，reset=重置为默认主题'
        )
        theme_parser.add_argument(
            '-p', '--path',
            dest='project_path',
            help='博客项目路径（默认为当前目录）',
            default='.'
        )
        theme_parser.add_argument(
            '-f', '--force',
            action='store_true',
            help='强制覆盖，不进行备份确认'
        )
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """执行命令并返回退出码
        
        Args:
            args: 命令行参数列表，如果为 None 则使用 sys.argv[1:]
            
        Returns:
            int: 退出码，0 表示成功，非 0 表示失败
        """
        try:
            # 解析参数
            parsed_args = self.parser.parse_args(args)
            
            # 如果没有提供命令，显示帮助信息
            if not parsed_args.command:
                self.show_help()
                return 0
            
            # 根据命令执行相应的处理器
            if parsed_args.command == 'new':
                return self.handle_new(
                    parsed_args.project_name,
                    parsed_args.target_dir
                )
            elif parsed_args.command == 'upgrade':
                return self.handle_upgrade(
                    parsed_args.project_path,
                    parsed_args.force
                )
            elif parsed_args.command == 'theme':
                return self.handle_theme(
                    parsed_args.action,
                    parsed_args.project_path,
                    parsed_args.force
                )
            else:
                print(f"✗ 未知命令: {parsed_args.command}", file=sys.stderr)
                self.show_help()
                return 1
                
        except SystemExit as e:
            # argparse 在遇到 --help 或 --version 时会抛出 SystemExit
            # 或者在参数错误时也会抛出
            return e.code if e.code is not None else 0
        except KeyboardInterrupt:
            print("\n\n✗ 操作已取消", file=sys.stderr)
            return 130  # 标准的 Ctrl+C 退出码
        except Exception as e:
            print(f"✗ 发生未预期的错误: {e}", file=sys.stderr)
            return 1
    
    def handle_new(self, project_name: str, target_dir: Optional[str] = None) -> int:
        """处理 new 命令
        
        Args:
            project_name: 项目名称
            target_dir: 目标目录
            
        Returns:
            int: 退出码，0 表示成功，非 0 表示失败
        """
        try:
            # 询问是否使用独立内容仓库
            print("\n欢迎使用 mblog！")
            print("\n请选择博客模式：")
            print("  1. 单仓库模式（默认）- 所有内容在一个仓库中")
            print("  2. 双仓库模式 - 内容与配置分离，支持自动同步")
            
            while True:
                choice = input("\n请选择 [1/2] (默认: 1): ").strip() or "1"
                if choice in ["1", "2"]:
                    break
                print("无效选择，请输入 1 或 2")
            
            use_separate_content_repo = (choice == "2")
            content_repo_url = None
            
            if use_separate_content_repo:
                print("\n双仓库模式说明：")
                print("  - 博客配置、主题在主仓库")
                print("  - Markdown 文章在独立的内容仓库")
                print("  - 内容更新自动触发博客重新部署")
                print("  - 适合团队协作和内容管理分离")
                
                while True:
                    content_repo_url = input("\n请输入内容仓库的 SSH URL (例如: git@github.com:user/content.git): ").strip()
                    if content_repo_url:
                        # 简单验证 SSH URL 格式
                        if content_repo_url.startswith("git@") and content_repo_url.endswith(".git"):
                            break
                        else:
                            print("⚠️  URL 格式可能不正确，请使用 SSH 格式 (git@github.com:user/repo.git)")
                            confirm = input("是否继续使用此 URL？[y/N]: ").strip().lower()
                            if confirm == 'y':
                                break
                    else:
                        print("内容仓库 URL 不能为空")
            
            # 创建项目初始化器
            initializer = ProjectInitializer(
                project_name, 
                target_dir,
                use_separate_content_repo=use_separate_content_repo,
                content_repo_url=content_repo_url
            )
            
            # 执行项目创建
            initializer.create_project()
            
            # 显示成功消息
            initializer.print_success_message()
            
            return 0
            
        except ProjectExistsError as e:
            print(f"✗ {e}", file=sys.stderr)
            return 1
        except MblogError as e:
            print(f"✗ {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ 创建项目时发生错误: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def handle_upgrade(self, project_path: str, force: bool = False) -> int:
        """处理 upgrade 命令
        
        Args:
            project_path: 博客项目路径
            force: 是否强制覆盖
            
        Returns:
            int: 退出码，0 表示成功，非 0 表示失败
        """
        try:
            from mblog.initializer import ProjectUpgrader
            
            upgrader = ProjectUpgrader(project_path)
            
            # 验证项目
            if not upgrader.validate_project():
                print("✗ 当前目录不是有效的 mblog 项目", file=sys.stderr)
                print("  提示：请确保目录中包含 _mblog/ 和 config.json", file=sys.stderr)
                return 1
            
            # 显示当前版本信息
            print(f"\n正在升级博客运行时...")
            print(f"项目路径: {Path(project_path).absolute()}")
            
            # 如果不是强制模式，询问确认
            if not force:
                print("\n⚠️  此操作将更新 _mblog/ 目录中的所有运行时文件")
                print("   建议先备份或提交当前更改到 Git")
                confirm = input("\n是否继续？[y/N]: ").strip().lower()
                if confirm != 'y':
                    print("✗ 操作已取消")
                    return 0
            
            # 执行升级
            upgrader.upgrade_runtime()
            
            print("\n✓ 运行时升级成功！")
            print("\n下一步操作:")
            print("  1. 测试生成功能: python gen.py")
            print("  2. 如有问题，可从备份恢复")
            
            return 0
            
        except MblogError as e:
            print(f"✗ {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ 升级时发生错误: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def handle_theme(self, action: str, project_path: str, force: bool = False) -> int:
        """处理 theme 命令
        
        Args:
            action: 操作类型（update 或 reset）
            project_path: 博客项目路径
            force: 是否强制覆盖
            
        Returns:
            int: 退出码，0 表示成功，非 0 表示失败
        """
        try:
            from mblog.initializer import ProjectUpgrader
            
            upgrader = ProjectUpgrader(project_path)
            
            # 验证项目
            if not upgrader.validate_project():
                print("✗ 当前目录不是有效的 mblog 项目", file=sys.stderr)
                print("  提示：请确保目录中包含 theme/ 和 config.json", file=sys.stderr)
                return 1
            
            print(f"\n正在{('更新' if action == 'update' else '重置')}主题...")
            print(f"项目路径: {Path(project_path).absolute()}")
            
            # 如果不是强制模式，询问确认
            if not force:
                if action == 'update':
                    print("\n⚠️  此操作将更新 theme/ 目录中的默认主题文件")
                    print("   自定义的修改可能会被覆盖")
                else:
                    print("\n⚠️  此操作将重置 theme/ 目录为默认主题")
                    print("   所有自定义修改将丢失")
                print("   建议先备份或提交当前更改到 Git")
                confirm = input("\n是否继续？[y/N]: ").strip().lower()
                if confirm != 'y':
                    print("✗ 操作已取消")
                    return 0
            
            # 执行主题操作
            if action == 'update':
                upgrader.update_theme()
                print("\n✓ 主题更新成功！")
            else:  # reset
                upgrader.reset_theme()
                print("\n✓ 主题重置成功！")
            
            print("\n下一步操作:")
            print("  1. 检查 theme/ 目录中的文件")
            print("  2. 重新生成博客: python gen.py")
            
            return 0
            
        except MblogError as e:
            print(f"✗ {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ 主题操作时发生错误: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def show_help(self) -> None:
        """显示帮助信息"""
        self.parser.print_help()
    
    def show_version(self) -> None:
        """显示版本信息"""
        print(f"mblog {__version__}")


def main(args: Optional[List[str]] = None) -> int:
    """CLI 主入口点
    
    Args:
        args: 命令行参数列表，如果为 None 则使用 sys.argv[1:]
        
    Returns:
        int: 退出码，0 表示成功，非 0 表示失败
    """
    cli = MblogCLI()
    return cli.run(args)
