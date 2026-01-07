"""
mblog - 静态博客生成器脚手架工具

一个简单易用的 Python 静态博客生成器，支持 Markdown 文章管理、
主题系统和 GitHub Actions 自动部署。
"""

__version__ = "0.2.0"
__author__ = "mblog"
__description__ = "静态博客生成器脚手架工具"

from mblog.exceptions import (
    MblogError,
    ProjectExistsError,
    ConfigError,
    ThemeError,
    MarkdownError,
    GenerationError,
)

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "MblogError",
    "ProjectExistsError",
    "ConfigError",
    "ThemeError",
    "MarkdownError",
    "GenerationError",
]
