# 图片处理

mblog 自动处理 Markdown 文章中的图片引用，让你可以使用相对路径引用图片，无需手动管理图片文件。

## 功能特性

- ✅ 自动识别文章中的相对路径图片
- ✅ 自动复制图片到输出目录
- ✅ 自动更新 HTML 中的图片路径
- ✅ 保持原始目录结构，避免命名冲突
- ✅ 支持多级目录
- ✅ 跳过外部链接和绝对路径

## 使用方法

### 基本用法

在 Markdown 文章中使用相对路径引用图片：

```markdown
---
title: "我的文章"
date: 2025-10-26
---

# 文章标题

这是一张图片：

![图片描述](./assets/my-image.png)
```

### 目录结构

推荐的目录结构：

```
md/
├── my-post.md
└── assets/
    ├── image1.png
    └── image2.jpg
```

或者为每篇文章创建独立的 assets 目录：

```
md/
├── tech/
│   ├── python-tips.md
│   └── assets/
│       └── python-logo.png
└── life/
    ├── travel.md
    └── assets/
        └── photo.jpg
```

### 支持的路径格式

#### 1. 相对路径（推荐）

```markdown
![图片](./assets/image.png)
![图片](../images/photo.jpg)
![图片](./subfolder/pic.png)
```

这些图片会被自动处理：
- 复制到 `public/assets/images/` 目录
- 路径更新为绝对路径

#### 2. 外部链接

```markdown
![图片](https://example.com/image.png)
![图片](http://cdn.example.com/photo.jpg)
```

外部链接保持不变，不会被处理。

#### 3. 绝对路径

```markdown
![图片](/static/logo.png)
```

绝对路径保持不变，不会被处理。

## 工作原理

### 1. 图片识别

mblog 在处理 Markdown 文件时，会扫描所有图片引用：

```python
# 识别模式：![alt](path)
img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
```

### 2. 路径解析

对于相对路径图片：
1. 解析图片的绝对路径
2. 检查文件是否存在
3. 计算相对于 `md/` 目录的路径

### 3. 图片复制

将图片复制到输出目录，保持原始目录结构：

```
md/tech/assets/image.png
→ public/assets/images/tech/assets/image.png
```

### 4. 路径更新

更新 HTML 中的图片路径：

```html
<!-- 原始 Markdown -->
![Python Logo](./assets/python.png)

<!-- 生成的 HTML -->
<img alt="Python Logo" src="/assets/images/tech/assets/python.png" />
```

## 示例

### 示例 1：单篇文章

**文件结构：**
```
md/
├── hello-world.md
└── assets/
    └── welcome.png
```

**hello-world.md：**
```markdown
---
title: "Hello World"
date: 2025-10-26
---

# 欢迎

![欢迎图片](./assets/welcome.png)
```

**生成结果：**
- 图片：`public/assets/images/assets/welcome.png`
- HTML：`<img src="/assets/images/assets/welcome.png" />`

### 示例 2：多级目录

**文件结构：**
```
md/
├── tech/
│   ├── python/
│   │   ├── tutorial.md
│   │   └── assets/
│   │       ├── code.png
│   │       └── result.png
│   └── javascript/
│       ├── intro.md
│       └── assets/
│           └── logo.png
```

**tutorial.md：**
```markdown
---
title: "Python 教程"
date: 2025-10-26
---

# Python 基础

代码示例：

![代码](./assets/code.png)

运行结果：

![结果](./assets/result.png)
```

**生成结果：**
- 图片：
  - `public/assets/images/tech/python/assets/code.png`
  - `public/assets/images/tech/python/assets/result.png`
- HTML 路径：
  - `/assets/images/tech/python/assets/code.png`
  - `/assets/images/tech/python/assets/result.png`

### 示例 3：混合路径

```markdown
---
title: "图片示例"
date: 2025-10-26
---

# 各种图片

本地图片（会被处理）：
![本地](./assets/local.png)

外部图片（保持不变）：
![外部](https://example.com/external.png)

绝对路径（保持不变）：
![Logo](/static/logo.png)
```

## 最佳实践

### 1. 使用 assets 目录

为每篇文章或每个分类创建 `assets` 目录：

```
md/
├── post1.md
├── assets/          # post1 的图片
│   └── image1.png
├── post2.md
└── assets/          # post2 的图片（会冲突！）
    └── image2.png
```

**注意**：同级目录下的 `assets` 会共享，建议使用子目录：

```
md/
├── post1/
│   ├── index.md
│   └── assets/
│       └── image1.png
└── post2/
    ├── index.md
    └── assets/
        └── image2.png
```

### 2. 图片命名

使用描述性的文件名：

```
✅ python-logo.png
✅ tutorial-step1.png
✅ result-screenshot.png

❌ image1.png
❌ 屏幕截图.png
❌ IMG_0001.png
```

### 3. 图片格式

推荐使用 Web 友好的格式：

- **PNG**：适合截图、图标、透明背景
- **JPG**：适合照片、大图
- **SVG**：适合矢量图、图标
- **WebP**：现代格式，体积小（需要浏览器支持）

### 4. 图片优化

在添加图片前进行优化：

- 压缩图片大小
- 调整合适的分辨率
- 使用工具如 TinyPNG、ImageOptim 等

### 5. Alt 文本

始终为图片添加有意义的 alt 文本：

```markdown
✅ ![Python 官方 Logo](./assets/python-logo.png)
✅ ![代码运行结果截图](./assets/result.png)

❌ ![](./assets/image.png)
❌ ![图片](./assets/photo.jpg)
```

## 故障排除

### 图片不显示

**可能原因：**

1. **图片文件不存在**
   - 检查文件路径是否正确
   - 检查文件名大小写（Linux 区分大小写）

2. **路径格式错误**
   - 使用 `./` 开头的相对路径
   - 避免使用 Windows 风格的反斜杠 `\`

3. **图片未被复制**
   - 查看生成日志中的警告信息
   - 确认图片在 `md/` 目录下

### 查看处理日志

生成博客时会显示图片处理信息：

```bash
$ python gen.py
开始生成静态博客文件...
→ 加载配置文件...
→ 加载主题: default
→ 处理 Markdown 文章...
  找到 10 篇文章
→ 初始化渲染器...
→ 生成静态文件...
✓ 静态资源已复制: theme/static -> public/static
✓ 文章图片已复制: 25 个文件  # 这里显示复制的图片数量
```

### 检查生成的文件

查看输出目录中的图片：

```bash
# 查看所有复制的图片
ls -R public/assets/images/

# 查看特定文章的图片
ls public/assets/images/tech/python/assets/
```

### 检查 HTML 路径

查看生成的 HTML 文件中的图片路径：

```bash
grep -n "img src" public/posts/my-post.html
```

## 技术细节

### Post 数据模型

`Post` 类新增了 `images` 字段：

```python
@dataclass
class Post:
    # ... 其他字段
    images: List[str] = field(default_factory=list)  # 图片文件路径列表
```

### 处理流程

1. **解析阶段**（`MarkdownProcessor._process_markdown_with_images`）
   - 使用正则表达式查找图片引用
   - 解析相对路径为绝对路径
   - 检查文件是否存在
   - 更新 Markdown 中的图片路径
   - 记录图片路径到 `Post.images`

2. **生成阶段**（`StaticGenerator._copy_post_images`）
   - 遍历所有文章的 `images` 列表
   - 计算目标路径
   - 复制图片文件
   - 保持目录结构

### 路径转换示例

```
原始路径：./assets/image.png
文章路径：/path/to/md/tech/python/tutorial.md
图片绝对路径：/path/to/md/tech/python/assets/image.png
相对于 md：tech/python/assets/image.png
输出路径：public/assets/images/tech/python/assets/image.png
HTML 路径：/assets/images/tech/python/assets/image.png
```

## 相关文档

- [配置文档](configuration.md)
- [主题开发](theme-development.md)
- [快速参考](quick-reference.md)
