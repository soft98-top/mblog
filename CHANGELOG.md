# 更新日志

## [未发布] - 2025-10-26

### 新增功能

#### 文章图片自动处理 🖼️
- 自动识别和处理 Markdown 文章中的相对路径图片
- 将图片复制到输出目录的 `assets/images/` 下
- 自动更新 HTML 中的图片路径为正确的绝对路径
- 保持原始目录结构，避免图片命名冲突
- 支持 `./assets/image.png` 等相对路径引用
- 跳过外部链接（http/https）和绝对路径图片
- `Post` 数据模型新增 `images` 字段记录引用的图片

#### 双仓库模式 🔀
- 支持将博客内容与配置分离到不同的 Git 仓库
- 交互式初始化，可选择单仓库或双仓库模式
- 使用 SSH Deploy Key 安全访问内容仓库
- 自动生成 GitHub Actions workflow 支持定时同步
- 内容仓库更新后自动触发博客重新部署
- 适合团队协作和内容管理分离的场景
- 自动生成详细的配置指南（SETUP_GUIDE.md）
- 自动初始化 Git 仓库并配置 .gitignore
- 详细文档：[独立内容仓库文档](docs/separate-content-repo.md)

#### 文章加密功能 🔒
- 支持密码保护的私密文章
- 在 frontmatter 中配置 `encrypted: true` 和 `password` 即可加密
- 客户端解密，无需服务器支持
- 主题可选支持，向后兼容
- 默认主题已包含加密模板和解密脚本
- 自动密码记忆（使用 sessionStorage）
- 优雅的密码输入界面
- 详细文档：[加密文章文档](docs/encrypted-posts.md)

#### 多级目录支持
- 支持在 `md/` 目录下使用多级目录组织文章
- 生成的 HTML 文件保持原始目录结构
- 文章 URL 路径与文件路径对应
- 新增 `Post.relative_path` 字段用于生成正确的 URL

#### 归档页面
- 新增专门的 `archive.html` 模板
- 按年份和月份组织文章列表
- 时间线样式的布局设计
- 显示文章发布日期和标签
- 响应式设计，移动端友好

#### 标签索引页面
- 新增专门的 `tags.html` 模板
- 标签云展示所有标签
- 标签大小根据文章数量动态调整
- 每个标签显示最多 5 篇文章预览
- 标签列表按字母顺序排列

#### RSS 订阅
- 自动生成 RSS 2.0 标准的订阅文件 (`rss.xml`)
- 包含最新 20 篇文章
- 支持文章标签作为分类
- 在 HTML `<head>` 中添加 RSS 自动发现链接
- 可通过配置 `build.generate_rss` 开关

#### Sitemap
- 自动生成符合 Sitemap 协议的站点地图 (`sitemap.xml`)
- 包含所有页面：首页、归档页、标签页、文章页
- 每个页面包含最后修改时间、更新频率和优先级
- 有利于搜索引擎优化（SEO）
- 可通过配置 `build.generate_sitemap` 开关

### 改进

#### CLI 交互增强
- 新增交互式项目初始化流程
- 支持选择单仓库或双仓库模式
- 自动验证内容仓库 URL 格式
- 根据选择的模式生成不同的项目结构和配置

#### 项目初始化器增强
- `ProjectInitializer` 支持双仓库模式参数
- 自动生成 .gitmodules 文件
- 自动生成双仓库模式的 GitHub Actions workflow
- 自动生成配置指南文档
- 自动初始化 Git 仓库
- 根据模式自动配置 .gitignore

#### 主题系统增强
- 所有模板获取统一通过 `theme.get_template()` 方法
- 模板配置完全由 `theme.json` 控制，不再使用硬编码的文件名
- 新增 `theme.has_template()` 方法检测主题是否支持特定模板
- 支持可选的 `encrypted_post` 模板

#### 数据模型扩展
- `Post` 类新增 `encrypted` 字段（布尔值）
- `Post` 类新增 `password` 字段（字符串）
- 自动从 frontmatter 提取加密配置

#### 渲染器增强
- 新增 `_encrypt_content()` 方法用于内容加密
- 新增 `_simple_hash()` 方法用于密码哈希
- `render_post()` 方法支持加密文章渲染逻辑
- 根据主题支持情况自动选择合适的渲染方式

#### 配置系统
- 在 `build` 部分新增 `generate_rss` 配置项（默认 true）
- 在 `build` 部分新增 `generate_sitemap` 配置项（默认 true）
- 更新配置模板文件

#### 主题系统
- 主题配置文件 `theme.json` 新增 `archive` 和 `tags` 模板映射
- 所有模板使用 `post.relative_path` 替代 `post.slug` 生成链接
- 静态资源 URL 使用绝对路径，修复子目录页面的资源加载问题

#### 样式优化
- 新增归档页面样式（时间线布局）
- 新增标签页面样式（标签云和列表）
- 改进响应式设计
- 统一配色方案

### 修复

- 修复文章页面静态资源路径错误（从相对路径改为绝对路径）
- 修复标签索引页导航链接（从 `/tags.html` 改为 `/tags/`）
- 修复多级目录文章无法被扫描的问题

### 文档更新

- 更新 README.md，添加双仓库模式和加密功能说明
- 新增 docs/separate-content-repo.md，完整的双仓库模式文档
- 新增 docs/encrypted-posts.md，完整的加密功能使用文档
- 更新 docs/theme-development.md，添加加密模板开发指南
- 更新 docs/configuration.md，添加新配置项说明和多级目录使用指南
- 更新 CHANGELOG.md 记录版本变更
- 自动生成的项目包含 SETUP_GUIDE.md（双仓库模式）

### 技术改进

- `MarkdownProcessor.load_posts()` 使用 `rglob()` 递归扫描所有子目录
- `Post` 数据模型新增 `relative_path`、`encrypted`、`password`、`images` 字段
- `MarkdownProcessor._process_markdown_with_images()` 方法处理图片路径转换
- `StaticGenerator._copy_post_images()` 方法复制文章图片到输出目录
- `MarkdownProcessor.__init__()` 使用 `resolve()` 确保路径为绝对路径
- `StaticGenerator` 新增 `_generate_rss()` 和 `_generate_sitemap()` 方法
- 生成器在输出文章时保持目录结构
- `Theme` 类新增 `has_template()` 方法
- `Renderer` 类新增加密相关方法
- 默认主题新增 `encrypted_post.html` 模板和 `crypto.js` 脚本
- 双仓库模式相关内容抽离到模板文件，避免硬编码
  - `deploy-dual-repo.yml.template` - 双仓库 workflow 模板
  - `gitmodules.template` - Git submodule 配置模板
  - `SETUP_GUIDE.md.template` - 配置指南模板

## 升级指南

### 从旧版本升级

1. **更新配置文件**
   
   在 `config.json` 的 `build` 部分添加：
   ```json
   {
     "build": {
       "generate_rss": true,
       "generate_sitemap": true
     }
   }
   ```

2. **更新主题模板**
   
   将所有模板中的 `post.slug` 替换为 `post.relative_path`：
   ```html
   <!-- 旧的 -->
   <a href="/posts/{{ post.slug }}.html">
   
   <!-- 新的 -->
   <a href="/posts/{{ post.relative_path }}.html">
   ```

3. **更新主题配置**
   
   在 `theme/theme.json` 中添加新模板：
   ```json
   {
     "templates": {
       "archive": "archive.html",
       "tags": "tags.html"
     }
   }
   ```

4. **添加新模板文件**
   
   从默认主题复制 `archive.html`、`tags.html` 和 `encrypted_post.html`（可选）到你的主题目录。

5. **支持加密功能（可选）**
   
   如果想支持加密文章，需要：
   - 在 `theme.json` 中添加 `"encrypted_post": "encrypted_post.html"`
   - 创建 `encrypted_post.html` 模板
   - 创建 `static/js/crypto.js` 解密脚本
   
   详见 [加密文章文档](docs/encrypted-posts.md)。

6. **重新生成博客**
   
   ```bash
   python gen.py
   ```

### 新项目

使用 `mblog new` 创建的新项目会自动包含所有新功能。

## 兼容性

- Python 3.7+
- 所有依赖包版本保持不变
- 向后兼容旧的配置文件（新配置项有默认值）
- 旧的 `post.slug` 字段仍然可用，但推荐使用 `post.relative_path`

## 已知问题

无

## 贡献者

感谢所有贡献者的付出！

---

更多信息请查看 [README.md](README.md) 和 [文档](docs/)。
