# mblog

一个简单易用的静态博客生成器脚手架工具，帮助你快速创建和管理个人博客。

## 特性

- 🚀 **快速启动**：一条命令创建完整的博客项目
- 📝 **Markdown 写作**：使用熟悉的 Markdown 格式撰写文章
- 🎨 **主题系统**：支持自定义主题，轻松更换博客外观
- ⚙️ **配置驱动**：通过 JSON 配置文件灵活控制博客行为
- 🔄 **完全独立**：生成的项目完全独立，不依赖 mblog 工具
- 🤖 **自动部署**：内置 GitHub Actions 配置，自动构建和部署

## 安装

### 通过 pip 安装

```bash
pip install mblog
```

### 从源码安装

```bash
git clone https://github.com/username/mblog.git
cd mblog
pip install -e .
```

## 快速开始

### 1. 创建新博客项目

```bash
mblog new my-blog
```

这将创建一个名为 `my-blog` 的目录，包含以下结构：

```
my-blog/
├── .workflow/          # GitHub Actions 配置
│   └── deploy.yml
├── md/                 # Markdown 文章目录
│   └── welcome.md
├── theme/              # 主题文件
│   ├── templates/
│   ├── static/
│   └── theme.json
├── _mblog/             # 生成运行时（独立）
├── gen.py              # 生成脚本
├── config.json         # 配置文件
└── requirements.txt    # Python 依赖
```

### 2. 进入项目目录

```bash
cd my-blog
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 撰写文章

在 `md/` 目录中创建 Markdown 文件，例如 `md/my-first-post.md`：

```markdown
---
title: "我的第一篇文章"
date: 2025-10-23
tags: ["博客", "开始"]
author: "你的名字"
description: "这是我的第一篇博客文章"
---

# 欢迎

这是我的第一篇博客文章！

## 关于我

我是一名开发者...
```

### 5. 生成静态文件

```bash
python gen.py
```

生成的静态文件将保存在 `public/` 目录中。

### 6. 本地预览

你可以使用 Python 的内置 HTTP 服务器预览：

```bash
cd public
python -m http.server 8000
```

然后在浏览器中访问 `http://localhost:8000`

### 7. 部署到 GitHub Pages

1. 在 GitHub 上创建一个新仓库
2. 将项目推送到 GitHub：

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/my-blog.git
git push -u origin main
```

3. 在仓库设置中启用 GitHub Pages，选择 `gh-pages` 分支
4. 每次推送代码时，GitHub Actions 会自动构建和部署你的博客

## 命令参考

### mblog new

创建新的博客项目。

```bash
mblog new <project_name>
```

**参数：**
- `<project_name>`：项目名称（必需）

**示例：**
```bash
mblog new my-awesome-blog
```

### mblog --help

显示帮助信息。

```bash
mblog --help
# 或
mblog -h
```

### mblog --version

显示版本信息。

```bash
mblog --version
# 或
mblog -v
```

## 配置

编辑 `config.json` 文件来自定义你的博客：

```json
{
  "site": {
    "title": "我的博客",
    "description": "这是我的个人博客",
    "author": "你的名字",
    "url": "https://yourusername.github.io",
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

详细的配置说明请参考 [配置文档](docs/configuration.md)。

## 主题开发

mblog 支持自定义主题。你可以修改 `theme/` 目录中的文件来自定义博客外观。

主题结构：

```
theme/
├── theme.json          # 主题元数据
├── templates/          # 模板文件
│   ├── base.html
│   ├── index.html
│   └── post.html
└── static/            # 静态资源
    ├── css/
    ├── js/
    └── images/
```

详细的主题开发指南请参考 [主题开发文档](docs/theme-development.md)。

## 文档

- [配置文档](docs/configuration.md) - 详细的配置选项说明
- [主题开发文档](docs/theme-development.md) - 如何创建自定义主题
- [部署文档](docs/deployment.md) - 部署到各种平台的指南

## 项目结构

生成的博客项目是完全独立的，不依赖 mblog 工具本身。这意味着：

- 你可以自由修改生成的代码
- 不需要安装 mblog 工具就能生成静态文件
- 所有生成逻辑都在 `_mblog/` 目录中

## 依赖

mblog 使用以下 Python 库：

- `markdown` - Markdown 转 HTML
- `Jinja2` - 模板引擎
- `python-frontmatter` - Frontmatter 解析
- `PyYAML` - YAML 解析

## 开发

### 运行测试

```bash
pip install -r requirements-dev.txt
pytest
```

### 代码格式化

```bash
black mblog tests
```

### 类型检查

```bash
mypy mblog
```

## 贡献

欢迎贡献！请随时提交 Issue 或 Pull Request。

## 许可证

MIT License

## 常见问题

### 如何添加新文章？

在 `md/` 目录中创建新的 Markdown 文件，然后运行 `python gen.py` 重新生成。

### 如何更改主题？

修改 `theme/` 目录中的文件，或者创建新的主题目录并在 `config.json` 中指定。

### 生成的文件在哪里？

默认在 `public/` 目录中，可以通过 `config.json` 中的 `build.output_dir` 配置修改。

### 如何添加自定义页面？

在 `theme/templates/` 中创建新的模板文件，并在 `_mblog/generator.py` 中添加生成逻辑。

### 支持哪些 Markdown 扩展？

mblog 使用 Python-Markdown 库，支持大多数标准 Markdown 语法和常用扩展。

## 联系方式

- GitHub: https://github.com/username/mblog
- Issues: https://github.com/username/mblog/issues

---

用 ❤️ 和 Python 构建
