# Base Path 功能实现总结

## 概述

实现了 `base_path` 配置选项，用于支持 GitHub Pages 子目录部署（如 `https://username.github.io/repo-name/`）。

## 问题背景

当博客部署到 GitHub Pages 的项目页面时，URL 会包含仓库名作为子目录。如果不配置 `base_path`，所有的静态资源和页面链接都会失效，导致：
- CSS/JS 文件 404
- 页面链接无法跳转
- 图片无法显示

## 解决方案

### 1. 配置文件更新

在 `config.json.template` 中添加 `base_path` 选项：

```json
{
  "site": {
    "title": "我的博客",
    "url": "https://example.com/myblog",
    "base_path": "/myblog",
    ...
  }
}
```

### 2. 渲染器更新

在 `renderer.py` 中实现了两个新的全局函数：

#### `url_for(path)`
生成页面 URL，自动添加 `base_path` 前缀：
```python
url_for('/posts/hello.html')  # → /myblog/posts/hello.html
```

#### `url_for_static(path)`
生成静态资源 URL，自动添加 `base_path` 前缀：
```python
url_for_static('css/style.css')  # → /myblog/static/css/style.css
```

### 3. 模板更新

更新所有默认主题模板，使用新的 URL 生成函数：

**base.html:**
```html
<link rel="stylesheet" href="{{ url_for_static('css/style.css') }}">
<a href="{{ url_for('/') }}">首页</a>
<a href="{{ url_for('/archive.html') }}">归档</a>
<a href="{{ url_for('/tags/') }}">标签</a>
```

**index.html:**
```html
<a href="{{ url_for('/posts/' ~ post.relative_path ~ '.html') }}">{{ post.title }}</a>
<a href="{{ url_for('/tags/' ~ tag ~ '.html') }}" class="tag">{{ tag }}</a>
```

**post.html:**
```html
<a href="{{ url_for('/posts/' ~ prev_post.relative_path ~ '.html') }}">上一篇</a>
<a href="{{ url_for('/posts/' ~ next_post.relative_path ~ '.html') }}">下一篇</a>
<a href="{{ url_for('/tags/' ~ tag ~ '.html') }}" class="tag">{{ tag }}</a>
```

**archive.html:**
```html
<a href="{{ url_for('/posts/' ~ post.relative_path ~ '.html') }}" class="post-link">{{ post.title }}</a>
<a href="{{ url_for('/tags/' ~ tag ~ '.html') }}" class="tag-small">{{ tag }}</a>
```

**tags.html:**
```html
<a href="{{ url_for('/tags/' ~ tag_info.name ~ '.html') }}" class="tag-cloud-item">...</a>
<a href="{{ url_for('/posts/' ~ post.relative_path ~ '.html') }}" class="post-link">{{ post.title }}</a>
```

**encrypted_post.html:**
```html
<a href="{{ url_for('/tags/' ~ tag ~ '.html') }}" class="tag">{{ tag }}</a>
```

### 4. 路径规范化

`base_path` 会自动规范化：
- 自动添加前导 `/`
- 自动移除尾部 `/`
- 空字符串或 `/` 表示无子目录

示例：
```python
"myblog"    → "/myblog"
"/myblog/"  → "/myblog"
""          → ""
"/"         → ""
```

## 使用方法

### 场景 1：项目页面（有子目录）

仓库名：`myblog`  
URL：`https://username.github.io/myblog/`

```json
{
  "site": {
    "url": "https://username.github.io/myblog",
    "base_path": "/myblog"
  }
}
```

### 场景 2：用户/组织页面（无子目录）

仓库名：`username.github.io`  
URL：`https://username.github.io/`

```json
{
  "site": {
    "url": "https://username.github.io",
    "base_path": ""
  }
}
```

### 场景 3：自定义域名

域名：`blog.example.com`

```json
{
  "site": {
    "url": "https://blog.example.com",
    "base_path": ""
  }
}
```

## 测试验证

### 手动测试

1. 配置 `base_path`：
```bash
# 编辑 config.json
{
  "site": {
    "base_path": "/myblog"
  }
}
```

2. 生成静态文件：
```bash
python gen.py
```

3. 检查生成的 HTML：
```bash
grep "href=" public/index.html | head -10
```

应该看到所有链接都包含 `/myblog/` 前缀。

### 自动化测试

在 test-blog 中验证：
```bash
cd test-blog

# 设置 base_path
python -c "import json; c=json.load(open('config.json')); c['site']['base_path']='/myblog'; json.dump(c, open('config.json', 'w'), ensure_ascii=False, indent=2)"

# 生成
python gen.py

# 验证
grep "href=" public/index.html | head -5
```

## 影响范围

### 修改的文件

1. **配置模板**
   - `mblog/templates/project/config.json.template`

2. **运行时文件**
   - `mblog/templates/runtime/renderer.py`

3. **主题模板**
   - `mblog/templates/themes/default/templates/base.html`
   - `mblog/templates/themes/default/templates/index.html`
   - `mblog/templates/themes/default/templates/post.html`
   - `mblog/templates/themes/default/templates/encrypted_post.html`
   - `mblog/templates/themes/default/templates/archive.html`
   - `mblog/templates/themes/default/templates/tags.html`

4. **文档**
   - `docs/github-pages-subdirectory.md` (新增)
   - `docs/troubleshooting-deployment.md` (更新)
   - `README.md` (更新)
   - `CHANGELOG.md` (更新)

### 向后兼容性

✅ **完全向后兼容**

- 如果不设置 `base_path` 或设置为空字符串，行为与之前完全一致
- 现有项目不需要任何修改即可继续使用
- 新项目可以选择性地配置 `base_path`

## 相关功能

### RSS 和 Sitemap

RSS 和 Sitemap 中的 URL 也会自动使用 `base_path`：

```xml
<!-- RSS -->
<link>https://example.com/myblog/posts/hello.html</link>

<!-- Sitemap -->
<loc>https://example.com/myblog/posts/hello.html</loc>
```

### 分页

分页链接也会正确处理 `base_path`：

```html
<a href="/myblog/">首页</a>
<a href="/myblog/page/2.html">第 2 页</a>
<a href="/myblog/page/3.html">第 3 页</a>
```

## 文档

### 新增文档

- **[GitHub Pages 子目录部署配置](github-pages-subdirectory.md)**
  - 详细的配置说明
  - 多种部署场景示例
  - 常见问题解答
  - 故障排除指南

### 更新文档

- **[README.md](../README.md)**
  - 添加 base_path 配置说明
  - 更新部署步骤

- **[troubleshooting-deployment.md](troubleshooting-deployment.md)**
  - 添加子目录部署问题排查

- **[CHANGELOG.md](../CHANGELOG.md)**
  - 记录新功能

## 最佳实践

### 1. 配置建议

- 始终保持 `base_path` 与仓库名一致
- 使用 `/` 开头，不使用 `/` 结尾
- `url` 也要包含完整路径

### 2. 本地测试

本地测试时可以临时设置 `base_path` 为空：
```json
{
  "site": {
    "base_path": ""
  }
}
```

### 3. 多环境配置

可以创建多个配置文件：
- `config.local.json` - 本地开发
- `config.github.json` - GitHub Pages
- `config.prod.json` - 生产环境

## 未来改进

### 可能的增强

1. **环境变量支持**
   ```bash
   BASE_PATH=/myblog python gen.py
   ```

2. **自动检测**
   从 Git 远程仓库 URL 自动推断 `base_path`

3. **配置验证**
   在生成时验证 `base_path` 格式是否正确

4. **开发服务器**
   提供支持 `base_path` 的本地开发服务器

## 总结

`base_path` 功能成功解决了 GitHub Pages 子目录部署的路径问题，具有以下特点：

✅ **简单易用** - 只需配置一个选项  
✅ **自动处理** - 所有 URL 自动添加前缀  
✅ **向后兼容** - 不影响现有项目  
✅ **文档完善** - 提供详细的使用指南  
✅ **测试验证** - 在 test-blog 中验证通过

这个功能让 mblog 可以无缝部署到任何 GitHub Pages 项目页面，大大提升了工具的实用性。
