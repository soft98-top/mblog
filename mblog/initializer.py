"""
项目初始化模块

负责创建新的博客项目结构，包括目录创建、运行时复制、模板文件生成等。
同时提供项目升级功能，用于更新运行时和主题。
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from mblog.exceptions import ProjectExistsError, MblogError


class ProjectInitializer:
    """项目初始化器
    
    负责创建完整的博客项目结构，包括：
    - 目录结构创建
    - 运行时代码复制
    - 模板文件生成
    - 主题复制
    """
    
    def __init__(self, project_name: str, target_dir: Optional[str] = None, 
                 use_separate_content_repo: bool = False, 
                 content_repo_url: Optional[str] = None):
        """初始化项目创建器
        
        Args:
            project_name: 项目名称
            target_dir: 目标目录，如果为 None 则使用当前目录
            use_separate_content_repo: 是否使用独立的内容仓库
            content_repo_url: 内容仓库的 URL（SSH 格式）
        """
        self.project_name = project_name
        self.target_dir = Path(target_dir) if target_dir else Path.cwd()
        self.project_path = self.target_dir / project_name
        self.use_separate_content_repo = use_separate_content_repo
        self.content_repo_url = content_repo_url
        
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
            
            # 根据模式创建内容
            if self.use_separate_content_repo:
                self._create_gitmodules_file()
                self._create_separate_repo_workflow()
                self._create_setup_guide()
            else:
                self._create_sample_post()
                self._create_workflow_file()
            
            # 复制默认主题
            self._create_default_theme()
            
            # 初始化 Git 仓库
            self._init_git_repo()
            
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
    
    def _create_gitmodules_file(self) -> None:
        """创建 .gitmodules 文件用于 submodule 配置"""
        template_path = self.templates_dir / "project" / "gitmodules.template"
        target_path = self.project_path / ".gitmodules"
        
        if not template_path.exists():
            raise MblogError(f"gitmodules 模板文件不存在: {template_path}")
        
        # 读取模板并替换变量
        template_content = template_path.read_text(encoding='utf-8')
        content = template_content.replace('{{CONTENT_REPO_URL}}', self.content_repo_url)
        target_path.write_text(content, encoding='utf-8')
    
    def _create_separate_repo_workflow(self) -> None:
        """创建支持独立内容仓库的 GitHub Actions 工作流"""
        template_path = self.templates_dir / "project" / "deploy-dual-repo.yml.template"
        target_path = self.project_path / ".workflow" / "deploy.yml"
        
        if not template_path.exists():
            raise MblogError(f"deploy-dual-repo.yml 模板文件不存在: {template_path}")
        
        # 直接复制模板文件（不需要变量替换）
        shutil.copy2(template_path, target_path)
    
    def _create_setup_guide(self) -> None:
        """创建独立内容仓库的设置指南"""
        template_path = self.templates_dir / "project" / "SETUP_GUIDE.md.template"
        target_path = self.project_path / "SETUP_GUIDE.md"
        
        if not template_path.exists():
            raise MblogError(f"SETUP_GUIDE.md 模板文件不存在: {template_path}")
        
        # 读取模板并替换变量
        template_content = template_path.read_text(encoding='utf-8')
        content = template_content.replace('{{CONTENT_REPO_URL}}', self.content_repo_url)
        content = content.replace('{{PROJECT_NAME}}', self.project_name)
        target_path.write_text(content, encoding='utf-8')
    
    def _init_git_repo(self) -> None:
        """初始化 Git 仓库"""
        import subprocess
        
        try:
            # 初始化 git 仓库
            subprocess.run(
                ["git", "init"],
                cwd=self.project_path,
                check=True,
                capture_output=True
            )
            
            # 创建 .gitignore
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Generated files
public/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets
content_deploy_key
content_deploy_key.pub
"""
            gitignore_path = self.project_path / ".gitignore"
            gitignore_path.write_text(gitignore_content)
            
            # 如果使用独立内容仓库，添加 md 目录到 .gitignore
            if self.use_separate_content_repo:
                with open(gitignore_path, "a") as f:
                    f.write("\n# Content repository (managed as submodule)\nmd/\n")
            
        except subprocess.CalledProcessError:
            # Git 初始化失败不应该阻止项目创建
            print("警告: Git 初始化失败，请手动运行 'git init'")
        except FileNotFoundError:
            print("警告: 未找到 git 命令，请确保已安装 Git")

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
        
        if self.use_separate_content_repo:
            print("\n模式: 独立内容仓库")
            print(f"内容仓库: {self.content_repo_url}")
            print("\n项目结构:")
            print(f"  {self.project_name}/")
            print("  ├── .workflow/       # GitHub Actions 自动部署配置")
            print("  ├── .gitmodules      # Git submodule 配置")
            print("  ├── md/              # 内容仓库（需要单独配置）")
            print("  ├── theme/           # 主题文件")
            print("  ├── _mblog/          # 生成运行时")
            print("  ├── gen.py           # 静态页面生成脚本")
            print("  ├── config.json      # 博客配置文件")
            print("  ├── SETUP_GUIDE.md   # 详细配置指南")
            print("  └── requirements.txt # Python 依赖")
            print("\n⚠️  重要：下一步操作")
            print(f"  1. cd {self.project_name}")
            print("  2. 阅读 SETUP_GUIDE.md 完成配置")
            print("  3. 生成并配置 SSH Deploy Key")
            print("  4. 在 GitHub 配置 Secrets")
            print("  5. 推送代码到 GitHub")
            print("\n配置完成后，内容仓库的更新会自动触发博客部署！")
        else:
            print("\n模式: 单仓库")
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



class ProjectUpgrader:
    """项目升级器
    
    负责升级现有博客项目的运行时和主题文件。
    """
    
    def __init__(self, project_path: str = '.'):
        """初始化项目升级器
        
        Args:
            project_path: 博客项目路径，默认为当前目录
        """
        self.project_path = Path(project_path).resolve()
        self.mblog_dir = self.project_path / "_mblog"
        self.theme_dir = self.project_path / "theme"
        self.config_file = self.project_path / "config.json"
        
        # 获取 mblog 包的根目录
        self.mblog_root = Path(__file__).parent
        self.templates_dir = self.mblog_root / "templates"
    
    def validate_project(self) -> bool:
        """验证是否为有效的 mblog 项目
        
        Returns:
            bool: 如果是有效项目返回 True
        """
        return (
            self.project_path.exists() and
            self.mblog_dir.exists() and
            self.config_file.exists()
        )
    
    def upgrade_runtime(self) -> None:
        """升级运行时文件
        
        将 _mblog/ 目录中的运行时文件更新到最新版本。
        会自动创建备份。
        
        Raises:
            MblogError: 升级过程中发生错误
        """
        try:
            # 创建备份
            backup_dir = self._create_backup(self.mblog_dir)
            print(f"✓ 已创建备份: {backup_dir.name}")
            
            # 获取运行时源目录
            runtime_src = self.templates_dir / "runtime"
            if not runtime_src.exists():
                raise MblogError(f"运行时模板目录不存在: {runtime_src}")
            
            # 复制所有 Python 文件
            updated_files = []
            for py_file in runtime_src.glob("*.py"):
                target_file = self.mblog_dir / py_file.name
                shutil.copy2(py_file, target_file)
                updated_files.append(py_file.name)
            
            print(f"✓ 已更新 {len(updated_files)} 个运行时文件")
            for filename in updated_files:
                print(f"  - {filename}")
            
        except Exception as e:
            raise MblogError(f"运行时升级失败: {e}") from e
    
    def update_theme(self) -> None:
        """更新主题文件
        
        更新 theme/ 目录中的默认主题文件到最新版本。
        只更新默认主题文件，不会删除用户添加的自定义文件。
        
        Raises:
            MblogError: 更新过程中发生错误
        """
        try:
            # 创建备份
            backup_dir = self._create_backup(self.theme_dir)
            print(f"✓ 已创建备份: {backup_dir.name}")
            
            # 获取主题源目录
            theme_src = self.templates_dir / "themes" / "default"
            if not theme_src.exists():
                raise MblogError(f"默认主题目录不存在: {theme_src}")
            
            # 递归复制主题文件
            updated_files = []
            self._copy_theme_files(theme_src, self.theme_dir, updated_files)
            
            print(f"✓ 已更新 {len(updated_files)} 个主题文件")
            
        except Exception as e:
            raise MblogError(f"主题更新失败: {e}") from e
    
    def reset_theme(self) -> None:
        """重置主题为默认主题
        
        完全删除 theme/ 目录并重新创建默认主题。
        会删除所有自定义修改。
        
        Raises:
            MblogError: 重置过程中发生错误
        """
        try:
            # 创建备份
            backup_dir = self._create_backup(self.theme_dir)
            print(f"✓ 已创建备份: {backup_dir.name}")
            
            # 删除现有主题目录
            shutil.rmtree(self.theme_dir)
            self.theme_dir.mkdir()
            
            # 获取主题源目录
            theme_src = self.templates_dir / "themes" / "default"
            if not theme_src.exists():
                raise MblogError(f"默认主题目录不存在: {theme_src}")
            
            # 复制整个主题目录
            file_count = 0
            for item in theme_src.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.theme_dir / item.name)
                    file_count += 1
                elif item.is_dir():
                    shutil.copytree(item, self.theme_dir / item.name)
                    file_count += sum(1 for _ in (self.theme_dir / item.name).rglob('*') if _.is_file())
            
            print(f"✓ 已重置主题，共 {file_count} 个文件")
            
        except Exception as e:
            raise MblogError(f"主题重置失败: {e}") from e
    
    def _create_backup(self, target_dir: Path) -> Path:
        """创建目录备份
        
        Args:
            target_dir: 要备份的目录
            
        Returns:
            Path: 备份目录路径
            
        Raises:
            MblogError: 备份失败
        """
        if not target_dir.exists():
            raise MblogError(f"目标目录不存在: {target_dir}")
        
        # 生成备份目录名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{target_dir.name}.backup_{timestamp}"
        backup_dir = target_dir.parent / backup_name
        
        # 创建备份
        shutil.copytree(target_dir, backup_dir)
        
        return backup_dir
    
    def _copy_theme_files(self, src_dir: Path, dst_dir: Path, updated_files: list) -> None:
        """递归复制主题文件
        
        Args:
            src_dir: 源目录
            dst_dir: 目标目录
            updated_files: 用于记录更新的文件列表
        """
        for item in src_dir.iterdir():
            src_item = src_dir / item.name
            dst_item = dst_dir / item.name
            
            if item.is_file():
                # 复制文件
                dst_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_item, dst_item)
                updated_files.append(str(dst_item.relative_to(self.theme_dir)))
            elif item.is_dir():
                # 递归处理子目录
                dst_item.mkdir(parents=True, exist_ok=True)
                self._copy_theme_files(src_item, dst_item, updated_files)
