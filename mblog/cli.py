"""
mblog CLI 模块

命令行界面的主要实现
"""
import argparse
import sys
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
  mblog --version            显示版本信息
  mblog --help               显示帮助信息

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
            # 创建项目初始化器
            initializer = ProjectInitializer(project_name, target_dir)
            
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
