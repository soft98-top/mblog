"""
项目初始化模块

负责创建新的博客项目结构，包括目录创建、运行时复制、模板文件生成等。
"""
import os
import shutil
from pathlib import Path
from typing import Optional

from mblog.exceptions import ProjectExistsError, MblogError


class ProjectInitializer:
    """项目初始化器
    
    负责创建完整的博客项目结构，包括：
    - 目录结构创建
    - 运行时代码复制
    - 模板文件生成
    - 主题复制
    """
    
    def __init__(self, project_name: str, target_dir: Optional[str] = None):
        """初始化项目创建器
        
        Args:
            project_name: 项目名称
            target_dir: 目标目录，如果为 None 则使用当前目录
        """
        self.project_name = project_name
        self.target_dir = Path(target_dir) if target_dir else Path.cwd()
        self.project_path = self.target_dir / project_name
        
        # 获取 mblog 包的根目录
        self.mblog_root = Path(__file__).parent
        self.templates_dir = self.mblog_root / "templates"
        
    def create_project(self) -> bool:
        """创建项目结构
        
        Returns:
            bool: 创建成功返回 True
            
        Raises:
            ProjectExistsError: 项目目录已存在
            MblogError: 创建过程中发生错误
        """
        try:
            # 检查目标目录是否已存在
            if self.project_path.exists():
                raise ProjectExistsError(
                    f"目录 '{self.project_name}' 已存在，请选择其他名称或删除现有目录"
                )
            
            # 创建目录结构
            self._create_directory_structure()
            
            # 复制运行时代码
            self._copy_runtime()
            
            # 生成模板文件
            self._create_gen_script()
            self._create_config_file()
            self._create_requirements_file()
            self._create_sample_post()
            self._create_workflow_file()
            
            # 复制默认主题
            self._create_default_theme()
            
            return True
            
        except ProjectExistsError:
            raise
        except Exception as e:
            # 如果创建失败，清理已创建的目录
            if self.project_path.exists():
                shutil.rmtree(self.project_path)
            raise MblogError(f"项目创建失败: {e}") from e
    
    def _create_directory_structure(self) -> None:
        """创建目录结构
        
        创建以下目录：
        - <project_name>/
        - <project_name>/.workflow/
        - <project_name>/md/
        - <project_name>/theme/
        - <project_name>/_mblog/
        """
        # 创建主项目目录
        self.project_path.mkdir(parents=True, exist_ok=False)
        
        # 创建子目录
        (self.project_path / ".workflow").mkdir(exist_ok=True)
        (self.project_path / "md").mkdir(exist_ok=True)
        (self.project_path / "theme").mkdir(exist_ok=True)
        (self.project_path / "_mblog").mkdir(exist_ok=True)

    def _copy_runtime(self) -> None:
        """复制生成运行时到 _mblog/ 目录
        
        将 templates/runtime/ 目录下的所有 Python 文件复制到项目的 _mblog/ 目录，
        使生成的项目可以独立运行，不依赖 mblog 工具。
        """
        runtime_src = self.templates_dir / "runtime"
        runtime_dst = self.project_path / "_mblog"
        
        if not runtime_src.exists():
            raise MblogError(f"运行时模板目录不存在: {runtime_src}")
        
        # 复制所有 Python 文件
        for py_file in runtime_src.glob("*.py"):
            shutil.copy2(py_file, runtime_dst / py_file.name)

    def _create_gen_script(self) -> None:
        """创建生成脚本 gen.py
        
        从模板生成 gen.py 文件，这是博客项目的主要生成脚本。
        """
        template_path = self.templates_dir / "project" / "gen.py.template"
        target_path = self.project_path / "gen.py"
        
        if not template_path.exists():
            raise MblogError(f"gen.py 模板文件不存在: {template_path}")
        
        # 直接复制模板文件（模板不需要变量替换）
        shutil.copy2(template_path, target_path)
        
        # 设置可执行权限（Unix/Linux/macOS）
        if os.name != 'nt':  # 非 Windows 系统
            os.chmod(target_path, 0o755)
    
    def _create_config_file(self) -> None:
        """创建配置文件 config.json
        
        从模板生成 config.json 文件，包含博客的默认配置。
        """
        template_path = self.templates_dir / "project" / "config.json.template"
        target_path = self.project_path / "config.json"
        
        if not template_path.exists():
            raise MblogError(f"config.json 模板文件不存在: {template_path}")
        
        # 直接复制模板文件
        shutil.copy2(template_path, target_path)
    
    def _create_requirements_file(self) -> None:
        """创建 requirements.txt
        
        从模板生成 requirements.txt 文件，列出项目的 Python 依赖。
        """
        template_path = self.templates_dir / "project" / "requirements.txt.template"
        target_path = self.project_path / "requirements.txt"
        
        if not template_path.exists():
            raise MblogError(f"requirements.txt 模板文件不存在: {template_path}")
        
        # 直接复制模板文件
        shutil.copy2(template_path, target_path)
    
    def _create_sample_post(self) -> None:
        """创建示例文章
        
        从模板生成示例 Markdown 文章，帮助用户快速开始。
        """
        template_path = self.templates_dir / "project" / "welcome.md.template"
        target_path = self.project_path / "md" / "welcome.md"
        
        if not template_path.exists():
            raise MblogError(f"welcome.md 模板文件不存在: {template_path}")
        
        # 直接复制模板文件
        shutil.copy2(template_path, target_path)
    
    def _create_workflow_file(self) -> None:
        """创建 GitHub Actions 工作流文件
        
        从模板生成 deploy.yml 文件，用于自动部署到 GitHub Pages。
        """
        template_path = self.templates_dir / "project" / "deploy.yml.template"
        target_path = self.project_path / ".workflow" / "deploy.yml"
        
        if not template_path.exists():
            raise MblogError(f"deploy.yml 模板文件不存在: {template_path}")
        
        # 直接复制模板文件
        shutil.copy2(template_path, target_path)

    def _create_default_theme(self) -> None:
        """创建默认主题
        
        从 templates/themes/default 复制默认主题到项目的 theme/ 目录。
        确保主题结构完整，包括模板文件、静态资源和主题元数据。
        """
        theme_src = self.templates_dir / "themes" / "default"
        theme_dst = self.project_path / "theme"
        
        if not theme_src.exists():
            raise MblogError(f"默认主题目录不存在: {theme_src}")
        
        # 复制整个主题目录
        # 由于 theme_dst 已经在 _create_directory_structure 中创建，
        # 我们需要复制目录内容而不是目录本身
        for item in theme_src.iterdir():
            if item.is_file():
                shutil.copy2(item, theme_dst / item.name)
            elif item.is_dir():
                shutil.copytree(item, theme_dst / item.name)

    def print_success_message(self) -> None:
        """输出成功消息并提示用户下一步操作
        
        在项目创建成功后调用，提供友好的反馈和使用指南。
        """
        print(f"\n✓ 项目 '{self.project_name}' 创建成功！")
        print(f"\n项目位置: {self.project_path.absolute()}")
        print("\n项目结构:")
        print(f"  {self.project_name}/")
        print("  ├── .workflow/       # GitHub Actions 自动部署配置")
        print("  ├── md/              # Markdown 文章目录")
        print("  ├── theme/           # 主题文件")
        print("  ├── _mblog/          # 生成运行时（独立运行）")
        print("  ├── gen.py           # 静态页面生成脚本")
        print("  ├── config.json      # 博客配置文件")
        print("  └── requirements.txt # Python 依赖")
        print("\n下一步操作:")
        print(f"  1. cd {self.project_name}")
        print("  2. pip install -r requirements.txt  # 安装依赖")
        print("  3. 在 md/ 目录中编写 Markdown 文章")
        print("  4. python gen.py                    # 生成静态文件")
        print("  5. 查看 public/ 目录中的生成结果")
        print("\n提示:")
        print("  - 编辑 config.json 自定义博客配置")
        print("  - 修改 theme/ 目录自定义主题样式")
        print("  - 推送到 GitHub 自动触发部署（需配置 GitHub Pages）")
        print("\n开始写作吧！✨\n")
