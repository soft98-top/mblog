# Base Path 功能完整实现

## 概述

成功实现了 `base_path` 配置选项，完全解决了 GitHub Pages 子目录部署的路径问题。

## 实现细节

### 1. 配置层面

在 `config.json.template` 中添加 `base_path` 字段：

```json
{
  "site": {
    "base_path": ""
  }
}
```

### 2. 渲染器层面

在 `renderer.py` 中实现了两个全局函数：

```python
def url_for(path: str) -> str:
    """生成页面 URL（支持 base_path）"""
    if not path.startswith('/'):
        path = '/' + path
    return f'{base_path}{path}'

def url_for_static(path: str) -> str:
    """生成静态资源 URL"""
    if not path.startswith('static/'):
        path = f'static/{path}'
    return url_for(path)
```

### 3. 模板层面

更新了所有 6 个默认主题模板：

#### base.html
- 导航链接：首页、归档、标签
- 静态资源：CSS、JS
- RSS 链接

#### index.html
- 文章列表链接
- 标签链接
- 分页链接

#### post.html
- 文章详情链接
- 上一篇/下一篇导航
- 标签链接

#### encrypted_post.html
- 加密文章的标签链接
- 静态资源（crypto.js）

#### archive.html
- 归档文章列表链接
- 文章标签链接

#### tags.html
- 标签云链接
- 标签详情链接
- 标签下的文章列表链接

## 测试验证

### 自动化测试

创建了 `scripts/verify_base_path.sh` 脚本，测试：

1. ✅ 带 base_path 的配置
   - 首页链接
   - 归档页链接
   - 标签页链接
   - 文章页链接
   - 静态资源链接

2. ✅ 不带 base_path 的配置
   - 所有链接恢复正常（无前缀）

### 手动测试

在 test-blog 中验证：

```bash
# 设置 base_path
python -c "import json; c=json.load(open('config.json')); c['site']['base_path']='/myblog'; json.dump(c, open('config.json', 'w'), ensure_ascii=False, indent=2)"

# 生成
python gen.py

# 验证各个页面
grep "href=" public/index.html | head -10
grep "href=" public/archive.html | head -10
grep "href=" public/tags/index.html | head -10
```

所有测试均通过 ✅

## 覆盖范围

### 页面类型

- ✅ 首页（index.html）
- ✅ 文章详情页（posts/*.html）
- ✅ 归档页（archive.html）
- ✅ 标签索引页（tags/index.html）
- ✅ 单个标签页（tags/*.html）
- ✅ 加密文章页（encrypted posts）
- ✅ 分页（page/*.html）

### 链接类型

- ✅ 页面链接（href="/posts/..."）
- ✅ 静态资源（href="/static/..."）
- ✅ 导航链接（href="/"）
- ✅ 标签链接（href="/tags/..."）
- ✅ RSS 链接（href="/rss.xml"）
- ✅ 分页链接（href="/page/2.html"）

### 特殊处理

- ✅ RSS 订阅文件中的 URL
- ✅ Sitemap 文件中的 URL
- ✅ 分页导航中的 URL

## 使用场景

### 场景 1: GitHub Pages 项目页面

```json
{
  "site": {
    "url": "https://username.github.io/myblog",
    "base_path": "/myblog"
  }
}
```

部署后访问：`https://username.github.io/myblog/`

### 场景 2: GitHub Pages 用户页面

```json
{
  "site": {
    "url": "https://username.github.io",
    "base_path": ""
  }
}
```

部署后访问：`https://username.github.io/`

### 场景 3: 自定义域名

```json
{
  "site": {
    "url": "https://blog.example.com",
    "base_path": ""
  }
}
```

部署后访问：`https://blog.example.com/`

### 场景 4: 自定义域名 + 子目录

```json
{
  "site": {
    "url": "https://example.com/blog",
    "base_path": "/blog"
  }
}
```

部署后访问：`https://example.com/blog/`

## 向后兼容性

✅ **完全向后兼容**

- 如果不设置 `base_path` 或设置为空字符串，行为与之前完全一致
- 现有项目无需任何修改
- 新项目可以选择性地配置 `base_path`

## 文档

### 新增文档

1. **[github-pages-subdirectory.md](github-pages-subdirectory.md)**
   - 详细的配置说明
   - 多种部署场景示例
   - 常见问题解答
   - 故障排除指南

2. **[BASE_PATH_FEATURE_SUMMARY.md](BASE_PATH_FEATURE_SUMMARY.md)**
   - 功能实现总结
   - 技术细节
   - 测试验证

3. **[examples/github-pages-subdirectory-example.md](../examples/github-pages-subdirectory-example.md)**
   - 完整的实战示例
   - 步骤详解
   - 验证方法

### 更新文档

1. **[README.md](../README.md)**
   - 添加 base_path 配置说明
   - 更新部署步骤

2. **[troubleshooting-deployment.md](troubleshooting-deployment.md)**
   - 添加子目录部署问题排查

3. **[CHANGELOG.md](../CHANGELOG.md)**
   - 记录新功能和所有更新

## 验证清单

在发布前，确保：

- [x] 所有模板文件都已更新
- [x] 配置模板包含 base_path 字段
- [x] 渲染器正确实现 URL 生成函数
- [x] RSS 和 Sitemap 正确处理 base_path
- [x] 分页链接正确生成
- [x] 自动化测试通过
- [x] 手动测试验证
- [x] 文档完整且准确
- [x] 示例清晰易懂
- [x] 向后兼容性确认

## 性能影响

✅ **无性能影响**

- URL 生成在模板渲染时进行，不影响运行时性能
- 配置加载只在初始化时进行一次
- 生成的静态文件大小无变化

## 安全性

✅ **无安全问题**

- base_path 只用于 URL 生成，不涉及文件系统操作
- 所有 URL 都经过 Jinja2 的自动转义
- 不存在路径遍历风险

## 未来改进

可能的增强功能：

1. **环境变量支持**
   ```bash
   BASE_PATH=/myblog python gen.py
   ```

2. **自动检测**
   从 Git 远程仓库 URL 自动推断 base_path

3. **配置验证**
   在生成时验证 base_path 格式

4. **开发服务器**
   提供支持 base_path 的本地开发服务器

## 总结

base_path 功能的实现：

✅ **完整** - 覆盖所有页面和链接类型  
✅ **正确** - 所有测试通过  
✅ **简单** - 只需配置一个选项  
✅ **兼容** - 不影响现有项目  
✅ **文档** - 提供详细的使用指南  

这个功能让 mblog 可以无缝部署到任何 GitHub Pages 项目页面，大大提升了工具的实用性和灵活性。

---

**实现日期**: 2025-10-26  
**测试状态**: ✅ 全部通过  
**文档状态**: ✅ 完整  
**发布状态**: ✅ 准备就绪
