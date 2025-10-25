# 主题开发文档

本文档介绍如何为 mblog 创建和自定义主题。

## 主题结构

一个完整的 mblog 主题包含以下结构：

```
theme/
├── theme.json          # 主题元数据（必需）
├── templates/          # 模板文件目录（必需）
│   ├── base.html      # 基础模板（必需）
│   ├── index.html     # 首页模板（必需）
│   ├── post.html      # 文章详情页模板（必需）
│   ├── archive.html   # 归档页模板（可选）
│   └── tag.html       # 标签页模板（可选）
└── static/            # 静态资源目录（可选）
    ├── css/           # 样式文件
    ├── js/            # JavaScript 文件
    └── images/        # 图片资源
```

## 主题元数据

`theme.json` 文件定义主题的基本信息：

```json
{
  "name": "default",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A beautiful theme for mblog",
  "templates": {
    "base": "base.html",
    "index": "index.html",
    "post": "post.html",
    "archive": "archive.html",
    "tag": "tag.html"
  }
}
```

### 字段说明

- `name`：主题名称（必需）
- `version`：主题版本号（必需）
- `author`：主题作者（可选）
- `description`：主题描述（可选）
- `templates`：模板文件映射（必需）
  - `base`：基础模板文件名
  - `index`：首页模板文件名
  - `post`：文章详情页模板文件名
  - `archive`：归档页模板文件名（可选）
  - `tag`：标签页模板文件名（可选）

## 模板系统

mblog 使用 Jinja2 作为模板引擎。所有模板都可以使用 Jinja2 的完整功能。

### 全局变量

所有模板都可以访问以下全局变量：

#### site

站点配置信息，来自 `config.json` 的 `site` 部分：

```jinja2
{{ site.title }}        <!-- 站点标题 -->
{{ site.description }}  <!-- 站点描述 -->
{{ site.author }}       <!-- 站点作者 -->
{{ site.url }}          <!-- 站点 URL -->
{{ site.language }}     <!-- 站点语言 -->
```

#### config

完整的配置对象，可以访问所有配置项：

```jinja2
{{ config.build.output_dir }}
{{ config.theme_config.posts_per_page }}
```

### 基础模板 (base.html)

基础模板定义页面的整体结构，其他模板通过继承来使用。

**示例：**

```html
<!DOCTYPE html>
<html lang="{{ site.language }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ site.title }}{% endblock %}</title>
    <meta name="description" content="{% block description %}{{ site.description }}{% endblock %}">
    
    <!-- 引入样式 -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    <!-- 导航栏 -->
    <header>
        <nav>
            <h1><a href="/">{{ site.title }}</a></h1>
            <ul>
                <li><a href="/">首页</a></li>
                <li><a href="/archive.html">归档</a></li>
                <li><a href="/about.html">关于</a></li>
            </ul>
        </nav>
    </header>
    
    <!-- 主内容区 -->
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <!-- 页脚 -->
    <footer>
        <p>&copy; {{ site.author }} | Powered by mblog</p>
    </footer>
    
    <!-- 引入脚本 -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

**关键点：**

- 使用 `{% block %}` 定义可被子模板覆盖的区块
- 常见的 block 包括：`title`、`description`、`content`、`extra_head`、`extra_scripts`
- 使用 `url_for()` 函数生成静态资源的 URL

### 首页模板 (index.html)

首页模板用于显示文章列表。

**可用变量：**

- `posts`：文章列表（List[Post]）
- `pagination`：分页信息（如果启用分页）

**Post 对象属性：**

- `post.title`：文章标题
- `post.date`：发布日期（datetime 对象）
- `post.author`：作者
- `post.description`：文章描述/摘要
- `post.tags`：标签列表
- `post.slug`：URL slug
- `post.html`：HTML 内容
- `post.content`：原始 Markdown 内容

**示例：**

```html
{% extends "base.html" %}

{% block title %}{{ site.title }} - 首页{% endblock %}

{% block content %}
<div class="posts-list">
    {% for post in posts %}
    <article class="post-preview">
        <h2><a href="/posts/{{ post.slug }}.html">{{ post.title }}</a></h2>
        <div class="post-meta">
            <span class="date">{{ post.date.strftime('%Y-%m-%d') }}</span>
            <span class="author">{{ post.author }}</span>
        </div>
        <p class="description">{{ post.description }}</p>
        <div class="tags">
            {% for tag in post.tags %}
            <a href="/tags/{{ tag }}.html" class="tag">{{ tag }}</a>
            {% endfor %}
        </div>
        <a href="/posts/{{ post.slug }}.html" class="read-more">阅读更多 →</a>
    </article>
    {% endfor %}
</div>

{% if pagination %}
<div class="pagination">
    {% if pagination.has_prev %}
    <a href="{{ pagination.prev_url }}" class="prev">← 上一页</a>
    {% endif %}
    
    <span class="current">第 {{ pagination.page }} 页 / 共 {{ pagination.pages }} 页</span>
    
    {% if pagination.has_next %}
    <a href="{{ pagination.next_url }}" class="next">下一页 →</a>
    {% endif %}
</div>
{% endif %}
{% endblock %}
```

### 文章详情页模板 (post.html)

文章详情页模板用于显示单篇文章的完整内容。

**可用变量：**

- `post`：当前文章对象（Post）

**示例：**

```html
{% extends "base.html" %}

{% block title %}{{ post.title }} - {{ site.title }}{% endblock %}
{% block description %}{{ post.description }}{% endblock %}

{% block content %}
<article class="post">
    <header class="post-header">
        <h1>{{ post.title }}</h1>
        <div class="post-meta">
            <time datetime="{{ post.date.isoformat() }}">
                {{ post.date.strftime('%Y年%m月%d日') }}
            </time>
            <span class="author">作者：{{ post.author }}</span>
        </div>
        <div class="tags">
            {% for tag in post.tags %}
            <a href="/tags/{{ tag }}.html" class="tag">#{{ tag }}</a>
            {% endfor %}
        </div>
    </header>
    
    <div class="post-content">
        {{ post.html | safe }}
    </div>
    
    <footer class="post-footer">
        <p>本文由 {{ post.author }} 发表</p>
    </footer>
</article>

<!-- 相关文章（如果实现） -->
{% if related_posts %}
<section class="related-posts">
    <h2>相关文章</h2>
    <ul>
        {% for related in related_posts %}
        <li><a href="/posts/{{ related.slug }}.html">{{ related.title }}</a></li>
        {% endfor %}
    </ul>
</section>
{% endif %}
{% endblock %}
```

**重要：** 使用 `| safe` 过滤器来渲染 HTML 内容，因为 `post.html` 已经是安全的 HTML。

### 归档页模板 (archive.html)

归档页模板用于按时间顺序显示所有文章。

**可用变量：**

- `posts`：所有文章列表，按日期排序
- `posts_by_year`：按年份分组的文章字典（可选）

**示例：**

```html
{% extends "base.html" %}

{% block title %}归档 - {{ site.title }}{% endblock %}

{% block content %}
<div class="archive">
    <h1>文章归档</h1>
    
    {% for year, year_posts in posts_by_year.items() %}
    <section class="year-section">
        <h2>{{ year }}</h2>
        <ul class="archive-list">
            {% for post in year_posts %}
            <li>
                <time>{{ post.date.strftime('%m-%d') }}</time>
                <a href="/posts/{{ post.slug }}.html">{{ post.title }}</a>
            </li>
            {% endfor %}
        </ul>
    </section>
    {% endfor %}
</div>
{% endblock %}
```

### 标签页模板 (tag.html)

标签页模板用于显示特定标签下的所有文章。

**可用变量：**

- `tag`：当前标签名称
- `posts`：该标签下的文章列表

**示例：**

```html
{% extends "base.html" %}

{% block title %}标签: {{ tag }} - {{ site.title }}{% endblock %}

{% block content %}
<div class="tag-page">
    <h1>标签: {{ tag }}</h1>
    <p>共 {{ posts|length }} 篇文章</p>
    
    <div class="posts-list">
        {% for post in posts %}
        <article class="post-preview">
            <h2><a href="/posts/{{ post.slug }}.html">{{ post.title }}</a></h2>
            <div class="post-meta">
                <span class="date">{{ post.date.strftime('%Y-%m-%d') }}</span>
            </div>
            <p class="description">{{ post.description }}</p>
        </article>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

## 静态资源

### CSS 样式

将 CSS 文件放在 `static/css/` 目录中。

**推荐的 CSS 结构：**

```css
/* style.css */

/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
}

/* 导航栏 */
header nav {
    /* ... */
}

/* 文章列表 */
.posts-list {
    /* ... */
}

/* 文章内容 */
.post-content {
    /* ... */
}

/* 代码高亮 */
.post-content pre {
    background: #f5f5f5;
    padding: 1rem;
    overflow-x: auto;
}

.post-content code {
    font-family: "Courier New", monospace;
}

/* 响应式设计 */
@media (max-width: 768px) {
    /* 移动端样式 */
}
```

### JavaScript

将 JavaScript 文件放在 `static/js/` 目录中。

**示例功能：**

```javascript
// main.js

// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// 代码复制按钮
document.querySelectorAll('pre code').forEach(block => {
    const button = document.createElement('button');
    button.textContent = '复制';
    button.className = 'copy-button';
    button.addEventListener('click', () => {
        navigator.clipboard.writeText(block.textContent);
        button.textContent = '已复制！';
        setTimeout(() => button.textContent = '复制', 2000);
    });
    block.parentElement.appendChild(button);
});
```

## Jinja2 过滤器和函数

### 常用过滤器

```jinja2
{{ post.title | upper }}              <!-- 转大写 -->
{{ post.title | lower }}              <!-- 转小写 -->
{{ post.title | capitalize }}         <!-- 首字母大写 -->
{{ post.description | truncate(100) }} <!-- 截断文本 -->
{{ post.html | safe }}                <!-- 不转义 HTML -->
{{ post.date | string }}              <!-- 转字符串 -->
```

### 日期格式化

```jinja2
{{ post.date.strftime('%Y-%m-%d') }}           <!-- 2025-10-23 -->
{{ post.date.strftime('%Y年%m月%d日') }}        <!-- 2025年10月23日 -->
{{ post.date.strftime('%B %d, %Y') }}          <!-- October 23, 2025 -->
```

### 条件判断

```jinja2
{% if post.tags %}
    <div class="tags">
        {% for tag in post.tags %}
        <span>{{ tag }}</span>
        {% endfor %}
    </div>
{% endif %}
```

### 循环

```jinja2
{% for post in posts %}
    <article>{{ post.title }}</article>
{% else %}
    <p>暂无文章</p>
{% endfor %}
```

## 主题配置

你可以在 `config.json` 的 `theme_config` 部分添加主题特定的配置：

```json
{
  "theme_config": {
    "posts_per_page": 10,
    "date_format": "%Y-%m-%d",
    "show_toc": true,
    "syntax_highlight": "monokai",
    "custom_color": "#3498db"
  }
}
```

在模板中访问：

```jinja2
{% if config.theme_config.show_toc %}
    <!-- 显示目录 -->
{% endif %}

<style>
    :root {
        --primary-color: {{ config.theme_config.custom_color }};
    }
</style>
```

## 最佳实践

### 1. 响应式设计

确保主题在各种设备上都能良好显示：

```css
/* 移动优先 */
.container {
    width: 100%;
    padding: 1rem;
}

/* 平板 */
@media (min-width: 768px) {
    .container {
        max-width: 720px;
        margin: 0 auto;
    }
}

/* 桌面 */
@media (min-width: 1024px) {
    .container {
        max-width: 960px;
    }
}
```

### 2. 语义化 HTML

使用语义化标签提高可访问性和 SEO：

```html
<article>
    <header>
        <h1>文章标题</h1>
        <time datetime="2025-10-23">2025年10月23日</time>
    </header>
    <main>
        <!-- 文章内容 -->
    </main>
    <footer>
        <!-- 文章元信息 -->
    </footer>
</article>
```

### 3. 性能优化

- 压缩 CSS 和 JavaScript
- 优化图片大小
- 使用 CDN 加载常用库
- 延迟加载非关键资源

### 4. 可访问性

- 提供足够的颜色对比度
- 为图片添加 alt 属性
- 支持键盘导航
- 使用 ARIA 标签

## 主题示例

### 极简主题

专注于内容，去除多余装饰：

```css
body {
    max-width: 650px;
    margin: 0 auto;
    padding: 2rem;
    font-family: Georgia, serif;
    font-size: 18px;
    line-height: 1.8;
}

h1, h2, h3 {
    font-weight: 600;
    margin-top: 2rem;
}

a {
    color: #000;
    text-decoration: underline;
}
```

### 暗色主题

```css
:root {
    --bg-color: #1a1a1a;
    --text-color: #e0e0e0;
    --link-color: #64b5f6;
}

body {
    background: var(--bg-color);
    color: var(--text-color);
}

a {
    color: var(--link-color);
}

code {
    background: #2d2d2d;
    color: #f8f8f2;
}
```

## 调试技巧

### 1. 查看可用变量

在模板中添加：

```jinja2
<pre>{{ posts | pprint }}</pre>
<pre>{{ config | pprint }}</pre>
```

### 2. 条件调试

```jinja2
{% if config.debug %}
    <div class="debug-info">
        <p>Posts count: {{ posts | length }}</p>
        <p>Current page: {{ pagination.page }}</p>
    </div>
{% endif %}
```

### 3. 使用浏览器开发工具

- 检查生成的 HTML 结构
- 调试 CSS 样式
- 测试响应式布局

## 发布主题

如果你创建了一个优秀的主题，可以分享给社区：

1. 在 GitHub 上创建主题仓库
2. 提供清晰的 README 和截图
3. 包含安装和使用说明
4. 遵循 mblog 主题规范

## 常见问题

### 如何添加自定义页面？

1. 在 `templates/` 中创建新模板
2. 在 `_mblog/generator.py` 中添加生成逻辑

### 如何使用 Web 字体？

在 `base.html` 的 `<head>` 中添加：

```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap" rel="stylesheet">
```

### 如何添加评论系统？

集成第三方评论系统（如 Disqus、Gitalk）：

```html
<div id="comments"></div>
<script>
    // 评论系统初始化代码
</script>
```

### 如何添加统计分析？

在 `base.html` 中添加统计代码：

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 参考资源

- [Jinja2 文档](https://jinja.palletsprojects.com/)
- [Markdown 语法](https://www.markdownguide.org/)
- [CSS 响应式设计](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [Web 可访问性](https://www.w3.org/WAI/fundamentals/accessibility-intro/)

---

祝你创建出美丽的主题！
