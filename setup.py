"""
mblog 包安装配置文件
"""
from setuptools import setup, find_packages
from pathlib import Path

# 读取 README 文件
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# 读取版本信息
about = {}
version_file = Path(__file__).parent / "mblog" / "__init__.py"
with open(version_file, encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, about)
            break

setup(
    name="mblog",
    version=about.get("__version__", "0.1.0"),
    author="mblog",
    author_email="",
    description="静态博客生成器脚手架工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mblog",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={
        "mblog": [
            "templates/project/*",
            "templates/runtime/*",
            "templates/themes/default/templates/*",
            "templates/themes/default/static/css/*",
            "templates/themes/default/static/js/*",
            "templates/themes/default/*.json",
        ],
    },
    install_requires=[
        # mblog 工具本身不需要运行时依赖
        # 运行时依赖会在生成的项目的 requirements.txt 中定义
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mblog=mblog.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    keywords="blog static-site-generator markdown",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mblog/issues",
        "Source": "https://github.com/yourusername/mblog",
    },
)
