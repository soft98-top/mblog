# 项目模板说明

这个目录包含用于生成新博客项目的模板文件。

## 模板文件列表

### 通用模板（单仓库和双仓库都使用）

- **config.json.template** - 博客配置文件模板
- **gen.py.template** - 静态网站生成脚本模板
- **requirements.txt.template** - Python 依赖列表模板
- **welcome.md.template** - 示例文章模板（仅单仓库模式）

### 单仓库模式模板

- **deploy.yml.template** - 标准 GitHub Actions 部署配置

### 双仓库模式模板

- **deploy-dual-repo.yml.template** - 支持内容仓库同步的 GitHub Actions 配置
- **gitmodules.template** - Git submodule 配置文件
- **SETUP_GUIDE.md.template** - 双仓库模式配置指南

## 模板变量

模板文件中可以使用以下变量（使用 `{{VARIABLE}}` 格式）：

- `{{CONTENT_REPO_URL}}` - 内容仓库的 SSH URL
- `{{PROJECT_NAME}}` - 项目名称

## 添加新模板

1. 在此目录创建新的 `.template` 文件
2. 在 `mblog/initializer.py` 中添加相应的创建方法
3. 如果需要变量替换，使用 `{{VARIABLE}}` 格式
4. 在创建方法中使用 `str.replace()` 替换变量

## 示例

```python
def _create_my_template(self) -> None:
    """创建自定义模板文件"""
    template_path = self.templates_dir / "project" / "my-template.template"
    target_path = self.project_path / "my-file.txt"
    
    if not template_path.exists():
        raise MblogError(f"模板文件不存在: {template_path}")
    
    # 读取模板并替换变量
    template_content = template_path.read_text(encoding='utf-8')
    content = template_content.replace('{{MY_VAR}}', self.my_value)
    target_path.write_text(content, encoding='utf-8')
```

## 注意事项

- 模板文件使用 UTF-8 编码
- 变量名使用大写字母和下划线
- 不需要变量替换的模板可以直接使用 `shutil.copy2()` 复制
- 模板文件应该保持简洁，避免过多的硬编码内容
