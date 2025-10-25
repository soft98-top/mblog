# 设计文档

## 概述

mblog 是一个基于 Python 的静态博客生成器脚手架工具。它采用模块化设计，将命令行界面、项目初始化、Markdown 处理、主题渲染和静态页面生成等功能分离，确保代码的可维护性和可扩展性。

核心设计理念：
- **简单易用**：通过简洁的 CLI 命令快速创建和管理博客
- **完全独立**：生成的博客项目完全独立，不依赖 mblog 工具本身
- **主题可扩展**：统一的主题接口规范，支持社区开发者贡献主题
- **配置驱动**：通过 JSON 配置文件灵活控制博客行为
- **自动化部署**：内置 GitHub Actions 配置，实现 CI/CD

**关键设计决策：**

mblog 工具分为两个部分：
1. **mblog CLI 工具**：用于创建新的博客项目（`mblog new`）
2. **生成运行时**：复制到每个博客项目的 `_mblog/` 目录中，使项目可以独立运行

这种设计确保用户创建博客项目后，可以完全独立于 mblog 工具进行开发和部署。

## 架构

### 整体架构

```
mblog (CLI 工具)
├── 命令行解析层 (CLI Parser)
├── 项目管理层 (Project Manager)
│   ├── 项目初始化 (Initializer)
│   └── 配置管理 (Config Manager)
├── 内容处理层 (Content Processor)
│   ├── Markdown 解析器 (Markdown Parser)
│   └── 元数据提取器 (Metadata Extractor)
├── 渲染层 (Renderer)
│   ├── 主题加载器 (Theme Loader)
│   └── 模板引擎 (Template Engine)
└── 生成层 (Generator)
    ├── 静态文件生成器 (Static Generator)
    └── 资源处理器 (Asset Handler)
```

### 数据流

```
用户命令 → CLI Parser → Project Manager → Content Processor → Renderer → Generator → 静态文件输出
                                ↓
                          Config Manager (配置注入)
                                ↓
                          Theme Loader (主题加载)
```

## 组件和接口

### 1. CLI 模块 (`mblog/cli.py`)

负责命令行参数解析和命令分发。

**主要类：**
- `MblogCLI`: CLI 主类

**接口：**
```python
class MblogCLI:
    def __init__(self):
        """初始化 CLI 解析器"""
        
    def run(self, args: List[str]) -> int:
        """执行命令并返回退出码"""
        
    def handle_new(self, project_name: str) -> int:
        """处理 new 命令"""
        
    def handle_generate(self, project_path: str) -> int:
        """处理 generate 命令"""
        
    def show_help(self) -> None:
        """显示帮助信息"""
        
    def show_version(self) -> None:
        """显示版本信息"""
```

**依赖：**
- Python 标准库 `argparse`

### 2. 项目初始化模块 (`mblog/initializer.py`)

负责创建新的博客项目结构，并将生成运行时复制到项目中。

**主要类：**
- `ProjectInitializer`: 项目初始化器

**接口：**
```python
class ProjectInitializer:
    def __init__(self, project_name: str, target_dir: str):
        """初始化项目创建器"""
        
    def create_project(self) -> bool:
        """创建项目结构"""
        
    def _create_directory_structure(self) -> None:
        """创建目录结构"""
        
    def _copy_runtime(self) -> None:
        """复制生成运行时到 _mblog/ 目录"""
        
    def _create_config_file(self) -> None:
        """创建配置文件"""
        
    def _create_gen_script(self) -> None:
        """创建生成脚本"""
        
    def _create_workflow_file(self) -> None:
        """创建 GitHub Actions 工作流"""
        
    def _create_sample_post(self) -> None:
        """创建示例文章"""
        
    def _create_default_theme(self) -> None:
        """创建默认主题"""
        
    def _create_requirements_file(self) -> None:
        """创建 requirements.txt"""
```

**生成的目录结构：**
```
<project_name>/
├── .workflow/
│   └── deploy.yml
├── md/
│   └── welcome.md (示例文章)
├── theme/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── post.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   └── theme.json (主题元数据)
├── _mblog/                    # 独立的生成运行时
│   ├── __init__.py
│   ├── config.py
│   ├── markdown_processor.py
│   ├── theme.py
│   ├── renderer.py
│   └── generator.py
├── gen.py
├── config.json
└── requirements.txt
```

### 3. 配置管理模块 (`mblog/config.py`)

负责读取、验证和管理配置文件。

**主要类：**
- `Config`: 配置管理器

**接口：**
```python
class Config:
    def __init__(self, config_path: str):
        """初始化配置管理器"""
        
    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        
    def validate(self) -> bool:
        """验证配置文件格式"""
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        
    def get_theme_config(self) -> Dict[str, Any]:
        """获取主题相关配置"""
```

**配置文件结构 (`config.json`)：**
```json
{
  "site": {
    "title": "我的博客",
    "description": "这是我的个人博客",
    "author": "作者名",
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
    "show_toc": true
  }
}
```

### 4. Markdown 处理模块 (`mblog/markdown_processor.py`)

负责解析 Markdown 文件和提取元数据。

**主要类：**
- `MarkdownProcessor`: Markdown 处理器
- `Post`: 文章数据模型

**接口：**
```python
class Post:
    """文章数据模型"""
    def __init__(self, filepath: str, metadata: Dict[str, Any], content: str, html: str):
        self.filepath = filepath
        self.metadata = metadata  # 标题、日期、标签等
        self.content = content    # 原始 Markdown
        self.html = html          # 转换后的 HTML
        self.slug = ""            # URL slug
        
class MarkdownProcessor:
    def __init__(self, md_dir: str):
        """初始化 Markdown 处理器"""
        
    def load_posts(self) -> List[Post]:
        """加载所有文章"""
        
    def parse_post(self, filepath: str) -> Post:
        """解析单个文章文件"""
        
    def _extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """提取 YAML frontmatter"""
        
    def _convert_to_html(self, markdown: str) -> str:
        """转换 Markdown 到 HTML"""
        
    def _generate_slug(self, title: str, date: str) -> str:
        """生成 URL slug"""
```

**Markdown 文件格式（带 frontmatter）：**
```markdown
---
title: "文章标题"
date: 2025-10-23
tags: ["Python", "博客"]
author: "作者名"
description: "文章简介"
---

# 正文内容

这里是文章的正文...
```

**依赖：**
- `markdown` 或 `mistune`: Markdown 转 HTML
- `python-frontmatter` 或 `PyYAML`: 解析 frontmatter

### 5. 主题系统模块 (`mblog/theme.py`)

负责加载和管理主题。

**主要类：**
- `Theme`: 主题管理器

**接口：**
```python
class Theme:
    def __init__(self, theme_dir: str):
        """初始化主题管理器"""
        
    def load(self) -> bool:
        """加载主题"""
        
    def get_template(self, template_name: str) -> str:
        """获取模板文件路径"""
        
    def get_static_dir(self) -> str:
        """获取静态资源目录"""
        
    def validate_structure(self) -> bool:
        """验证主题结构是否符合规范"""
```

**主题结构规范：**
```
theme/
├── theme.json          # 主题元数据
├── templates/          # 模板文件
│   ├── base.html      # 基础模板
│   ├── index.html     # 首页/文章列表
│   ├── post.html      # 文章详情页
│   ├── archive.html   # 归档页（可选）
│   └── tag.html       # 标签页（可选）
└── static/            # 静态资源
    ├── css/
    ├── js/
    └── images/
```

**主题元数据 (`theme.json`)：**
```json
{
  "name": "default",
  "version": "1.0.0",
  "author": "mblog",
  "description": "默认主题",
  "templates": {
    "index": "index.html",
    "post": "post.html",
    "base": "base.html"
  }
}
```

### 6. 模板渲染模块 (`mblog/renderer.py`)

负责使用模板引擎渲染页面。

**主要类：**
- `Renderer`: 模板渲染器

**接口：**
```python
class Renderer:
    def __init__(self, theme: Theme, config: Config):
        """初始化渲染器"""
        
    def render_index(self, posts: List[Post]) -> str:
        """渲染首页"""
        
    def render_post(self, post: Post) -> str:
        """渲染文章页"""
        
    def render_archive(self, posts: List[Post]) -> str:
        """渲染归档页"""
        
    def render_tag_page(self, tag: str, posts: List[Post]) -> str:
        """渲染标签页"""
```

**模板变量规范：**

所有模板都可以访问以下全局变量：
- `site`: 站点配置信息
- `config`: 完整配置对象

**index.html 模板变量：**
- `posts`: 文章列表
- `pagination`: 分页信息（如果启用）

**post.html 模板变量：**
- `post`: 当前文章对象
  - `post.title`: 标题
  - `post.date`: 日期
  - `post.author`: 作者
  - `post.tags`: 标签列表
  - `post.html`: HTML 内容
  - `post.description`: 描述

**依赖：**
- `Jinja2`: 模板引擎

### 7. 静态文件生成模块 (`_mblog/generator.py`)

负责生成最终的静态文件。这个模块会被复制到生成的项目中。

**主要类：**
- `StaticGenerator`: 静态文件生成器

**接口：**
```python
class StaticGenerator:
    def __init__(self, config: Config, theme: Theme, renderer: Renderer, posts: List[Post]):
        """初始化生成器"""
        
    def generate(self) -> bool:
        """执行生成流程"""
        
    def _prepare_output_dir(self) -> None:
        """准备输出目录"""
        
    def _generate_pages(self) -> None:
        """生成所有页面"""
        
    def _copy_static_assets(self) -> None:
        """复制静态资源"""
        
    def _generate_index_pages(self) -> None:
        """生成首页和分页"""
        
    def _generate_post_pages(self) -> None:
        """生成文章详情页"""
        
    def _generate_feed(self) -> None:
        """生成 RSS/Atom feed（可选）"""
```

**输出目录结构：**
```
public/
├── index.html
├── posts/
│   ├── 2025-10-23-welcome.html
│   └── ...
├── tags/
│   ├── python.html
│   └── ...
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── feed.xml (可选)
```

### 8. 生成脚本和独立运行时 (`gen.py` 和 `_mblog/`)

**重要设计决策：生成的博客项目完全独立**

生成的博客项目不依赖 mblog 工具，所有生成逻辑都会被复制到项目中。

**项目结构调整：**
```
<project_name>/
├── .workflow/
│   └── deploy.yml
├── md/
│   └── welcome.md
├── theme/
│   └── ...
├── _mblog/                    # 独立的生成运行时（核心变化）
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   ├── markdown_processor.py # Markdown 处理
│   ├── theme.py              # 主题加载
│   ├── renderer.py           # 模板渲染
│   └── generator.py          # 静态文件生成
├── gen.py                     # 生成脚本（调用 _mblog）
├── config.json
└── requirements.txt           # 项目自己的依赖
```

**gen.py 内容（独立版本）：**
```python
#!/usr/bin/env python3
"""
博客静态文件生成脚本
此脚本完全独立，不依赖 mblog 工具
"""
import sys
from pathlib import Path

# 将 _mblog 添加到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from _mblog.config import Config
from _mblog.markdown_processor import MarkdownProcessor
from _mblog.theme import Theme
from _mblog.renderer import Renderer
from _mblog.generator import StaticGenerator

def main():
    """主函数"""
    try:
        # 加载配置
        config = Config("config.json")
        config.load()
        
        # 加载主题
        theme_dir = Path("theme")
        theme = Theme(str(theme_dir))
        theme.load()
        
        # 处理 Markdown 文件
        processor = MarkdownProcessor("md")
        posts = processor.load_posts()
        
        # 初始化渲染器
        renderer = Renderer(theme, config)
        
        # 生成静态文件
        generator = StaticGenerator(config, theme, renderer, posts)
        generator.generate()
        
        print(f"✓ 成功生成 {len(posts)} 篇文章")
        print(f"✓ 输出目录: {config.get('build', {}).get('output_dir', 'public')}")
        
    except Exception as e:
        print(f"✗ 生成失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**requirements.txt（生成项目的依赖）：**
```
markdown>=3.4.0
Jinja2>=3.1.0
python-frontmatter>=1.0.0
PyYAML>=6.0
```

**mblog 工具的职责调整：**

mblog 工具本身包含两部分：
1. **CLI 和项目初始化**：`mblog new` 命令
2. **生成运行时模板**：将 `_mblog/` 目录的代码作为模板复制到新项目中

**mblog 工具的新结构：**
```
mblog/
├── mblog/
│   ├── __init__.py
│   ├── cli.py                # CLI 命令
│   ├── initializer.py        # 项目初始化
│   └── templates/            # 项目模板
│       ├── project/          # 项目文件模板
│       │   ├── gen.py.template
│       │   ├── config.json.template
│       │   ├── requirements.txt.template
│       │   └── welcome.md.template
│       ├── runtime/          # 生成运行时代码（会复制到 _mblog/）
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── markdown_processor.py
│       │   ├── theme.py
│       │   ├── renderer.py
│       │   └── generator.py
│       └── themes/           # 默认主题
│           └── default/
│               ├── theme.json
│               ├── templates/
│               └── static/
├── tests/
├── setup.py
└── README.md
```

## 数据模型

### Post（文章）

```python
@dataclass
class Post:
    """文章数据模型"""
    filepath: str              # 源文件路径
    slug: str                  # URL slug
    title: str                 # 标题
    date: datetime             # 发布日期
    author: str                # 作者
    description: str           # 描述/摘要
    tags: List[str]            # 标签
    content: str               # 原始 Markdown
    html: str                  # 转换后的 HTML
    metadata: Dict[str, Any]   # 其他元数据
```

### Config（配置）

```python
@dataclass
class SiteConfig:
    """站点配置"""
    title: str
    description: str
    author: str
    url: str
    language: str

@dataclass
class BuildConfig:
    """构建配置"""
    output_dir: str
    theme: str

class Config:
    """配置管理器"""
    site: SiteConfig
    build: BuildConfig
    theme_config: Dict[str, Any]
```

## 错误处理

### 错误类型

定义自定义异常类 (`mblog/exceptions.py`)：

```python
class MblogError(Exception):
    """基础异常类"""
    pass

class ProjectExistsError(MblogError):
    """项目已存在"""
    pass

class ConfigError(MblogError):
    """配置文件错误"""
    pass

class ThemeError(MblogError):
    """主题错误"""
    pass

class MarkdownError(MblogError):
    """Markdown 处理错误"""
    pass

class GenerationError(MblogError):
    """生成错误"""
    pass
```

### 错误处理策略

1. **CLI 层**：捕获所有异常，显示友好的错误消息，返回适当的退出码
2. **业务逻辑层**：抛出具体的自定义异常，包含详细的错误信息
3. **日志记录**：使用 Python `logging` 模块记录详细的错误堆栈
4. **用户反馈**：错误消息应该清晰、可操作，指出问题所在和解决方法

### 错误消息示例

```python
# 好的错误消息
"✗ 配置文件 'config.json' 格式错误: 第 5 行缺少逗号"
"✗ 主题 'custom' 缺少必需的模板文件: post.html"
"✗ Markdown 文件 'md/post1.md' 缺少必需的 frontmatter 字段: title"

# 避免的错误消息
"Error"
"Invalid config"
"Something went wrong"
```

## 测试策略

### 单元测试

使用 `pytest` 框架进行单元测试。

**测试覆盖：**
- `test_cli.py`: CLI 命令解析和执行
- `test_initializer.py`: 项目初始化逻辑
- `test_config.py`: 配置加载和验证
- `test_markdown_processor.py`: Markdown 解析和转换
- `test_theme.py`: 主题加载和验证
- `test_renderer.py`: 模板渲染
- `test_generator.py`: 静态文件生成

**测试数据：**
- 在 `tests/fixtures/` 目录中准备测试用的配置文件、Markdown 文件、主题文件等

### 集成测试

**测试场景：**
1. 完整的项目创建流程
2. 从 Markdown 到静态 HTML 的完整生成流程
3. 不同主题的切换和渲染
4. 错误场景的处理

### 端到端测试

**测试场景：**
1. 创建新项目 → 添加文章 → 生成静态文件 → 验证输出
2. 修改配置 → 重新生成 → 验证配置生效
3. 自定义主题 → 生成 → 验证主题应用

## 依赖管理

### 核心依赖

```
# requirements.txt
markdown>=3.4.0          # Markdown 转 HTML
Jinja2>=3.1.0           # 模板引擎
python-frontmatter>=1.0.0  # Frontmatter 解析
PyYAML>=6.0             # YAML 解析
click>=8.1.0            # CLI 框架（可选，也可用 argparse）
```

### 开发依赖

```
# requirements-dev.txt
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0           # 代码格式化
flake8>=6.0.0          # 代码检查
mypy>=1.5.0            # 类型检查
```

## 部署和分发

### 包结构

```
mblog/
├── mblog/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── initializer.py
│   ├── config.py
│   ├── markdown_processor.py
│   ├── theme.py
│   ├── renderer.py
│   ├── generator.py
│   ├── exceptions.py
│   └── templates/          # 内置模板
│       ├── project/        # 项目模板
│       └── themes/         # 默认主题
├── tests/
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
└── requirements.txt
```

### 安装方式

1. **通过 pip 安装**：
   ```bash
   pip install mblog
   ```

2. **从源码安装**：
   ```bash
   git clone https://github.com/username/mblog.git
   cd mblog
   pip install -e .
   ```

### 命令行入口

在 `setup.py` 或 `pyproject.toml` 中配置：

```python
entry_points={
    'console_scripts': [
        'mblog=mblog.cli:main',
    ],
}
```

## GitHub Actions 工作流

### 工作流文件 (`.workflow/deploy.yml`)

```yaml
name: Deploy Blog

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Generate static files
      run: |
        python gen.py
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./public
```

## 扩展性设计

### 插件系统（未来扩展）

为了支持更多功能，可以设计插件系统：

```python
class Plugin:
    """插件基类"""
    def on_init(self, config: Config) -> None:
        """初始化时调用"""
        pass
        
    def on_pre_generate(self, posts: List[Post]) -> List[Post]:
        """生成前调用，可以修改文章列表"""
        return posts
        
    def on_post_generate(self, output_dir: str) -> None:
        """生成后调用"""
        pass
```

**插件示例：**
- 搜索插件：生成搜索索引
- 评论插件：集成第三方评论系统
- 统计插件：集成 Google Analytics
- SEO 插件：生成 sitemap.xml、robots.txt

### 主题市场（未来扩展）

可以建立主题仓库，用户可以通过命令安装主题：

```bash
mblog theme install <theme-name>
mblog theme list
```

## 性能考虑

1. **增量构建**：只重新生成修改过的文章
2. **并行处理**：使用多进程处理大量文章
3. **缓存机制**：缓存 Markdown 转 HTML 的结果
4. **资源优化**：压缩 CSS/JS，优化图片

## 安全考虑

1. **路径遍历防护**：验证文件路径，防止访问项目外的文件
2. **XSS 防护**：模板引擎自动转义 HTML
3. **配置验证**：严格验证配置文件内容
4. **依赖安全**：定期更新依赖，修复安全漏洞
