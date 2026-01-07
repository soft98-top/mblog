# Base Path URL 修复文档

## 问题描述

### 问题场景
当博客部署在子路径下（如 `xx.com/myblog/`）时，搜索功能的文章链接会出现 404 错误。

**具体表现：**
- 博客部署在：`xx.com/myblog/`
- 搜索索引中的文章URL：`/posts/1/2.html`
- 点击搜索结果后跳转到：`xx.com/posts/1/2.html` ❌
- 正确的URL应该是：`xx.com/myblog/posts/1/2.html` ✅

### 根本原因
在生成搜索索引、RSS订阅和Sitemap时，文章URL是硬编码的，没有考虑配置文件中的 `base_path` 设置。

---

## 影响范围

### 受影响的功能
1. **搜索功能** ⚠️ 主要问题
   - 搜索结果点击后跳转404
   - 影响用户体验

2. **RSS订阅** ⚠️
   - RSS阅读器中的文章链接错误
   - 影响订阅用户

3. **SEO优化** ⚠️
   - Sitemap中的URL错误
   - 影响搜索引擎收录

### 受影响的文件
- `mblog/templates/runtime/generator.py`
  - `_generate_search_index()` 方法
  - `_generate_rss()` 方法
  - `_generate_sitemap()` 方法

---

## 解决方案

### 修复策略
在生成搜索索引、RSS和Sitemap时，从配置文件中读取 `base_path`，并将其添加到所有URL中。

### 实现细节

#### 1. 搜索索引生成 (`_generate_search_index`)

**修改前：**
```python
post_data = {
    'title': post.title,
    'url': f'/posts/{post.relative_path}.html',  # 硬编码
    ...
}
```

**修改后：**
```python
# 获取 base_path
site_config = self.config.get_site_config()
base_path = site_config.get('base_path', '').strip()
if base_path and not base_path.startswith('/'):
    base_path = '/' + base_path
if base_path.endswith('/'):
    base_path = base_path[:-1]

post_data = {
    'title': post.title,
    'url': f'{base_path}/posts/{post.relative_path}.html',  # 使用 base_path
    ...
}
```

#### 2. RSS订阅生成 (`_generate_rss`)

**修改前：**
```python
site_url = site_config.get('url', 'https://example.com').rstrip('/')
post_url = f'{site_url}/posts/{post.relative_path}.html'
```

**修改后：**
```python
site_url = site_config.get('url', 'https://example.com').rstrip('/')

# 获取 base_path
base_path = site_config.get('base_path', '').strip()
if base_path and not base_path.startswith('/'):
    base_path = '/' + base_path
if base_path.endswith('/'):
    base_path = base_path[:-1]

post_url = f'{site_url}{base_path}/posts/{post.relative_path}.html'
```

**同时修复：**
- RSS 自链接：`{site_url}{base_path}/rss.xml`
- 站点链接：`{site_url}{base_path}/`

#### 3. Sitemap生成 (`_generate_sitemap`)

**修改的URL：**
- 首页：`{site_url}{base_path}/`
- 归档页：`{site_url}{base_path}/archive.html`
- 标签索引：`{site_url}{base_path}/tags/`
- 文章页：`{site_url}{base_path}/posts/{relative_path}.html`
- 标签页：`{site_url}{base_path}/tags/{tag_filename}.html`

---

## 配置说明

### base_path 配置

在 `config.json` 中配置：

```json
{
  "site": {
    "title": "我的博客",
    "url": "https://example.com",
    "base_path": "/myblog",  // 子路径部署
    ...
  }
}
```

### 配置规则

1. **根目录部署**
   ```json
   "base_path": ""  // 或不设置
   ```
   - 生成的URL：`/posts/article.html`

2. **子路径部署**
   ```json
   "base_path": "/myblog"
   ```
   - 生成的URL：`/myblog/posts/article.html`

3. **自动处理**
   - 自动添加前导斜杠：`myblog` → `/myblog`
   - 自动移除尾部斜杠：`/myblog/` → `/myblog`

---

## 测试验证

### 测试文件
`tests/test_basepath_urls.py`

### 测试用例

#### 1. 搜索索引测试
```python
def test_search_index_with_basepath():
    # 配置 base_path = "/myblog"
    # 验证搜索索引中的 URL 格式
    assert url.startswith('/myblog/')
```

#### 2. RSS测试
```python
def test_rss_with_basepath():
    # 配置 base_path = "/blog"
    # 验证 RSS 中的所有链接
    assert 'https://example.com/blog/posts/' in rss_content
    assert 'https://example.com/blog/rss.xml' in rss_content
```

#### 3. Sitemap测试
```python
def test_sitemap_with_basepath():
    # 配置 base_path = "/site"
    # 验证 Sitemap 中的所有 URL
    assert 'https://example.com/site/' in sitemap_content
```

#### 4. 向后兼容测试
```python
def test_without_basepath():
    # 配置 base_path = ""
    # 验证不影响现有功能
    assert url.startswith('/posts/')
```

### 运行测试
```bash
python tests/test_basepath_urls.py
```

---

## 部署示例

### 场景1：根目录部署

**配置：**
```json
{
  "site": {
    "url": "https://myblog.com",
    "base_path": ""
  }
}
```

**生成的URL：**
- 搜索索引：`/posts/article.html`
- RSS：`https://myblog.com/posts/article.html`
- Sitemap：`https://myblog.com/posts/article.html`

**访问：**
- 首页：`https://myblog.com/`
- 文章：`https://myblog.com/posts/article.html`

### 场景2：GitHub Pages 子路径部署

**配置：**
```json
{
  "site": {
    "url": "https://username.github.io",
    "base_path": "/myblog"
  }
}
```

**生成的URL：**
- 搜索索引：`/myblog/posts/article.html`
- RSS：`https://username.github.io/myblog/posts/article.html`
- Sitemap：`https://username.github.io/myblog/posts/article.html`

**访问：**
- 首页：`https://username.github.io/myblog/`
- 文章：`https://username.github.io/myblog/posts/article.html`

### 场景3：自定义子路径

**配置：**
```json
{
  "site": {
    "url": "https://example.com",
    "base_path": "/blog/tech"
  }
}
```

**生成的URL：**
- 搜索索引：`/blog/tech/posts/article.html`
- RSS：`https://example.com/blog/tech/posts/article.html`
- Sitemap：`https://example.com/blog/tech/posts/article.html`

---

## 修复效果

### 修复前
```json
// search-index.json
{
  "posts": [
    {
      "url": "/posts/article.html"  // ❌ 缺少 base_path
    }
  ]
}
```

**问题：**
- 部署在 `xx.com/myblog/` 时
- 点击搜索结果跳转到 `xx.com/posts/article.html`
- 返回 404 错误

### 修复后
```json
// search-index.json
{
  "posts": [
    {
      "url": "/myblog/posts/article.html"  // ✅ 包含 base_path
    }
  ]
}
```

**效果：**
- 部署在 `xx.com/myblog/` 时
- 点击搜索结果跳转到 `xx.com/myblog/posts/article.html`
- 正确访问文章 ✅

---

## 相关文档

- [搜索路径支持](./SEARCH_PATH_BASEPATH_SUPPORT.md) - 前端搜索索引路径计算
- [配置文档](./configuration.md) - base_path 配置说明
- [部署文档](./deployment.md) - 子路径部署指南

---

## 总结

### 修改内容
- **文件数量：** 1个文件
- **修改方法：** 3个方法
- **代码行数：** 约30行

### 修复效果
✅ 搜索功能在子路径部署时正常工作
✅ RSS订阅链接正确
✅ Sitemap URL正确
✅ 向后兼容（不影响根目录部署）

### 适用场景
- GitHub Pages 子路径部署
- 服务器子目录部署
- CDN 子路径部署
- 任何需要 base_path 的部署场景

---

**修复日期：** 2026-01-07
**版本：** v1.0.0+
