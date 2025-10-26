# 配置文档

本文档详细说明 mblog 的所有配置选项。

## 配置文件

mblog 使用 JSON 格式的配置文件 `config.json`，位于项目根目录。

## 文章组织

### 多级目录支持

mblog 支持在 `md/` 目录下使用多级目录组织文章：

```
md/
├── welcome.md              # 根目录文章
├── tech/                   # 技术分类
│   ├── python-tips.md
│   └── javascript.md
├── life/                   # 生活分类
│   ├── travel/            # 旅行子分类
│   │   ├── beijing.md
│   │   └── shanghai.md
│   └── reading.md
└── projects/              # 项目分类
    └── my-app.md
```

生成的 HTML 文件会保持相同的目录结构：

```
public/posts/
├── welcome.html
├── tech/
│   ├── python-tips.html
│   └── javascript.html
├── life/
│   ├── travel/
│   │   ├── beijing.html
│   │   └── shanghai.html
│   └── reading.html
└── projects/
    └── my-app.html
```

### 文章 URL

文章的 URL 路径与文件路径对应：
- `md/welcome.md` → `/posts/welcome.html`
- `md/tech/python-tips.md` → `/posts/tech/python-tips.html`
- `md/life/travel/beijing.md` → `/posts/life/travel/beijing.html`

## 完整配置示例

```json
{
  "site": {
    "title": "我的博客",
    "description": "这是我的个人博客，分享技术和生活",
    "author": "张三",
    "url": "https://zhangsan.github.io",
    "language": "zh-CN",
    "timezone": "Asia/Shanghai"
  },
  "build": {
    "output_dir": "public",
    "theme": "default",
    "posts_dir": "md",
    "clean_output": true,
    "generate_rss": true,
    "generate_sitemap": true
  },
  "theme_config": {
    "posts_per_page": 10,
    "date_format": "%Y-%m-%d",
    "show_toc": true,
    "show_reading_time": true,
    "syntax_highlight": true,
    "excerpt_length": 200,
    "enable_tags": true,
    "enable_archive": true
  },
  "social": {
    "github": "https://github.com/zhangsan",
    "twitter": "https://twitter.com/zhangsan",
    "email": "zhangsan@example.com"
  }
}
```

## 配置项详解

### site - 站点配置

站点的基本信息配置。

#### site.title

- **类型**：`string`
- **必需**：是
- **默认值**：无
- **说明**：博客的标题，显示在页面标题和导航栏中

**示例：**
```json
"title": "我的技术博客"
```

#### site.description

- **类型**：`string`
- **必需**：是
- **默认值**：无
- **说明**：博客的描述，用于 SEO 和页面元信息

**示例：**
```json
"description": "分享 Python、Web 开发和技术心得"
```

#### site.author

- **类型**：`string`
- **必需**：是
- **默认值**：无
- **说明**：博客作者名称，作为默认文章作者

**示例：**
```json
"author": "张三"
```

#### site.url

- **类型**：`string`
- **必需**：是
- **默认值**：无
- **说明**：博客的完整 URL，用于生成绝对链接和 RSS feed

**示例：**
```json
"url": "https://zhangsan.github.io"
```

**注意：** 不要在 URL 末尾添加斜杠。

#### site.language

- **类型**：`string`
- **必需**：否
- **默认值**：`"zh-CN"`
- **说明**：博客的语言代码，用于 HTML lang 属性

**常用值：**
- `zh-CN`：简体中文
- `zh-TW`：繁体中文
- `en-US`：英语（美国）
- `ja-JP`：日语

**示例：**
```json
"language": "zh-CN"
```

#### site.timezone

- **类型**：`string`
- **必需**：否
- **默认值**：`"UTC"`
- **说明**：时区设置，用于日期时间处理

**常用值：**
- `Asia/Shanghai`：中国
- `America/New_York`：美国东部
- `Europe/London`：英国

**示例：**
```json
"timezone": "Asia/Shanghai"
```

### build - 构建配置

控制博客生成过程的配置。

#### build.output_dir

- **类型**：`string`
- **必需**：否
- **默认值**：`"public"`
- **说明**：生成的静态文件输出目录

**示例：**
```json
"output_dir": "dist"
```

#### build.theme

- **类型**：`string`
- **必需**：否
- **默认值**：`"default"`
- **说明**：使用的主题名称或主题目录路径

**示例：**
```json
"theme": "default"
```

或使用自定义主题：
```json
"theme": "my-custom-theme"
```

#### build.posts_dir

- **类型**：`string`
- **必需**：否
- **默认值**：`"md"`
- **说明**：Markdown 文章所在目录

**示例：**
```json
"posts_dir": "content"
```

#### build.clean_output

- **类型**：`boolean`
- **必需**：否
- **默认值**：`true`
- **说明**：生成前是否清空输出目录

**示例：**
```json
"clean_output": false
```

#### build.generate_rss

- **类型**：`boolean`
- **必需**：否
- **默认值**：`true`
- **说明**：是否生成 RSS 订阅文件 (rss.xml)

**示例：**
```json
"generate_rss": true
```

生成的 RSS 文件包含：
- 博客基本信息（标题、描述、语言）
- 最新 20 篇文章
- 文章标题、链接、描述、发布日期
- 文章标签（作为分类）
- 符合 RSS 2.0 标准

#### build.generate_sitemap

- **类型**：`boolean`
- **必需**：否
- **默认值**：`true`
- **说明**：是否生成 Sitemap 文件 (sitemap.xml)

**示例：**
```json
"generate_sitemap": true
```

生成的 Sitemap 包含：
- 首页、归档页、标签索引页
- 所有文章页面（保持目录结构）
- 所有标签页面
- 每个页面的最后修改时间、更新频率和优先级
- 符合 Sitemap 协议标准

### theme_config - 主题配置

主题相关的配置选项，不同主题可能有不同的配置项。

#### theme_config.posts_per_page

- **类型**：`integer`
- **必需**：否
- **默认值**：`10`
- **说明**：首页每页显示的文章数量（如果主题支持分页）

**示例：**
```json
"posts_per_page": 15
```

#### theme_config.date_format

- **类型**：`string`
- **必需**：否
- **默认值**：`"%Y-%m-%d"`
- **说明**：日期显示格式，使用 Python strftime 格式

**常用格式：**
- `%Y-%m-%d`：2025-10-23
- `%Y年%m月%d日`：2025年10月23日
- `%B %d, %Y`：October 23, 2025
- `%Y/%m/%d`：2025/10/23

**示例：**
```json
"date_format": "%Y年%m月%d日"
```

#### theme_config.show_toc

- **类型**：`boolean`
- **必需**：否
- **默认值**：`false`
- **说明**：是否在文章页显示目录（Table of Contents）

**示例：**
```json
"show_toc": true
```

#### theme_config.show_reading_time

- **类型**：`boolean`
- **必需**：否
- **默认值**：`false`
- **说明**：是否显示文章预计阅读时间

**示例：**
```json
"show_reading_time": true
```

#### theme_config.syntax_highlight

- **类型**：`boolean` 或 `string`
- **必需**：否
- **默认值**：`true`
- **说明**：是否启用代码语法高亮，或指定高亮主题

**示例：**
```json
"syntax_highlight": true
```

或指定主题：
```json
"syntax_highlight": "monokai"
```

#### theme_config.excerpt_length

- **类型**：`integer`
- **必需**：否
- **默认值**：`200`
- **说明**：文章摘要的最大字符数

**示例：**
```json
"excerpt_length": 150
```

### features - 功能开关

控制博客的各种功能是否启用。

#### features.rss

- **类型**：`boolean`
- **必需**：否
- **默认值**：`true`
- **说明**：是否生成 RSS feed

**示例：**
```json
"rss": true
```

生成的 RSS feed 位于 `<output_dir>/feed.xml`

#### features.sitemap

- **类型**：`boolean`
- **必需**：否
- **默认值**：`true`
- **说明**：是否生成 sitemap.xml

**示例：**
```json
"sitemap": true
```

#### features.archive

- **类型**：`boolean`
- **必需**：否
- **默认值**：`true`
- **说明**：是否生成归档页面

**示例：**
```json
"archive": true
```

#### features.tags

- **类型**：`boolean`
- **必需**：否
- **默认值**：`true`
- **说明**：是否生成标签页面

**示例：**
```json
"tags": true
```

### social - 社交链接

社交媒体和联系方式配置。

#### social.github

- **类型**：`string`
- **必需**：否
- **说明**：GitHub 个人主页 URL

**示例：**
```json
"github": "https://github.com/zhangsan"
```

#### social.twitter

- **类型**：`string`
- **必需**：否
- **说明**：Twitter 个人主页 URL

**示例：**
```json
"twitter": "https://twitter.com/zhangsan"
```

#### social.email

- **类型**：`string`
- **必需**：否
- **说明**：联系邮箱

**示例：**
```json
"email": "zhangsan@example.com"
```

你可以添加任意其他社交平台：

```json
"social": {
  "github": "https://github.com/zhangsan",
  "weibo": "https://weibo.com/zhangsan",
  "zhihu": "https://zhihu.com/people/zhangsan",
  "linkedin": "https://linkedin.com/in/zhangsan"
}
```

## 配置验证

mblog 会在生成时验证配置文件：

### 必需字段检查

以下字段必须存在：
- `site.title`
- `site.description`
- `site.author`
- `site.url`

### 类型检查

配置项的值必须符合指定的类型，例如：
- `posts_per_page` 必须是整数
- `show_toc` 必须是布尔值

### 格式验证

某些配置项有格式要求：
- `site.url` 必须是有效的 URL
- `date_format` 必须是有效的 strftime 格式

## 配置示例

### 最小配置

```json
{
  "site": {
    "title": "我的博客",
    "description": "个人博客",
    "author": "作者",
    "url": "https://example.com"
  }
}
```

### 中文博客配置

```json
{
  "site": {
    "title": "技术笔记",
    "description": "记录学习和工作中的技术心得",
    "author": "李明",
    "url": "https://liming.github.io",
    "language": "zh-CN",
    "timezone": "Asia/Shanghai"
  },
  "build": {
    "output_dir": "public",
    "theme": "default"
  },
  "theme_config": {
    "posts_per_page": 10,
    "date_format": "%Y年%m月%d日",
    "show_toc": true,
    "show_reading_time": true
  },
  "social": {
    "github": "https://github.com/liming",
    "email": "liming@example.com"
  }
}
```

### 英文博客配置

```json
{
  "site": {
    "title": "Tech Blog",
    "description": "Sharing thoughts on software development",
    "author": "John Doe",
    "url": "https://johndoe.com",
    "language": "en-US",
    "timezone": "America/New_York"
  },
  "build": {
    "output_dir": "dist",
    "theme": "minimal"
  },
  "theme_config": {
    "posts_per_page": 5,
    "date_format": "%B %d, %Y",
    "show_toc": false,
    "syntax_highlight": "github"
  },
  "features": {
    "rss": true,
    "sitemap": true,
    "archive": true,
    "tags": true
  },
  "social": {
    "github": "https://github.com/johndoe",
    "twitter": "https://twitter.com/johndoe",
    "linkedin": "https://linkedin.com/in/johndoe"
  }
}
```

### 极简配置

```json
{
  "site": {
    "title": "Simple Blog",
    "description": "A minimalist blog",
    "author": "Minimalist",
    "url": "https://simple.blog"
  },
  "theme_config": {
    "posts_per_page": 20,
    "show_toc": false,
    "show_reading_time": false
  },
  "features": {
    "rss": false,
    "sitemap": false,
    "archive": false,
    "tags": false
  }
}
```

## 环境变量

某些配置可以通过环境变量覆盖（如果实现）：

```bash
export MBLOG_OUTPUT_DIR="build"
export MBLOG_THEME="custom"
python gen.py
```

## 配置文件位置

默认情况下，mblog 在项目根目录查找 `config.json`。你也可以指定配置文件路径：

```bash
python gen.py --config custom-config.json
```

## 配置继承

你可以创建多个配置文件用于不同环境：

**config.json**（基础配置）：
```json
{
  "site": {
    "title": "我的博客",
    "description": "个人博客",
    "author": "作者"
  }
}
```

**config.prod.json**（生产环境）：
```json
{
  "site": {
    "url": "https://myblog.com"
  },
  "build": {
    "clean_output": true
  }
}
```

**config.dev.json**（开发环境）：
```json
{
  "site": {
    "url": "http://localhost:8000"
  },
  "build": {
    "clean_output": false
  }
}
```

## 配置最佳实践

### 1. 使用有意义的标题和描述

```json
{
  "site": {
    "title": "Python 学习笔记",
    "description": "记录 Python 学习过程中的知识点、实践经验和踩坑记录"
  }
}
```

### 2. 设置正确的 URL

确保 URL 与实际部署地址一致：

```json
{
  "site": {
    "url": "https://yourusername.github.io/blog"
  }
}
```

### 3. 选择合适的分页数量

根据文章长度和读者习惯选择：

```json
{
  "theme_config": {
    "posts_per_page": 10  // 文章较短时可以增加
  }
}
```

### 4. 启用有用的功能

```json
{
  "features": {
    "rss": true,      // 方便读者订阅
    "sitemap": true,  // 有利于 SEO
    "archive": true,  // 方便查找历史文章
    "tags": true      // 方便文章分类
  }
}
```

### 5. 添加社交链接

```json
{
  "social": {
    "github": "https://github.com/yourusername",
    "email": "your@email.com"
  }
}
```

## 故障排除

### 配置文件格式错误

**错误信息：**
```
✗ 配置文件 'config.json' 格式错误: Expecting ',' delimiter: line 5 column 3
```

**解决方法：**
- 检查 JSON 语法，确保所有字符串用双引号
- 检查逗号和括号是否匹配
- 使用 JSON 验证工具检查格式

### 缺少必需字段

**错误信息：**
```
✗ 配置文件缺少必需字段: site.title
```

**解决方法：**
- 添加缺少的字段
- 参考完整配置示例

### 无效的配置值

**错误信息：**
```
✗ 配置项 'posts_per_page' 必须是正整数
```

**解决方法：**
- 检查配置值的类型和范围
- 参考配置项详解中的说明

### 主题不存在

**错误信息：**
```
✗ 主题 'custom' 不存在
```

**解决方法：**
- 检查主题目录是否存在
- 确认 `build.theme` 配置正确

## 高级配置

### 自定义主题配置

不同主题可能需要特定的配置：

```json
{
  "theme_config": {
    "custom_theme_option": "value",
    "color_scheme": "dark",
    "font_family": "Noto Sans SC"
  }
}
```

查看主题文档了解支持的配置项。

### 多语言配置

如果主题支持多语言：

```json
{
  "site": {
    "language": "zh-CN",
    "languages": ["zh-CN", "en-US"]
  },
  "i18n": {
    "zh-CN": {
      "home": "首页",
      "archive": "归档"
    },
    "en-US": {
      "home": "Home",
      "archive": "Archive"
    }
  }
}
```

## 参考

- [JSON 格式规范](https://www.json.org/)
- [Python strftime 格式](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
- [语言代码列表](https://www.w3.org/International/O-charset-lang.html)
- [时区列表](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

---

如有问题，请查看 [常见问题](../README.md#常见问题) 或提交 Issue。
