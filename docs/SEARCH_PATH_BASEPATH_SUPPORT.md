# 搜索路径 - 支持基础路径部署

## 问题场景

当博客部署在子路径下时（如 `xx.com/mblog/`），需要正确找到 `search-index.json` 的位置。

### 部署示例

**场景 1：根目录部署**
- 首页：`xx.com/`
- 搜索索引：`xx.com/search-index.json`
- 文章：`xx.com/posts/article.html`

**场景 2：子路径部署**
- 首页：`xx.com/mblog/`
- 搜索索引：`xx.com/mblog/search-index.json`
- 文章：`xx.com/mblog/posts/article.html`

---

## 解决方案

### 核心思路

`search-index.json` 总是在 `posts`、`tags`、`page` 这些目录的**上一级**。

### 算法逻辑

```javascript
// 1. 检查路径中是否包含特殊目录
const specialDirs = ['posts', 'tags', 'page'];

// 2. 如果找到特殊目录，提取其上一级路径
if (currentPath.includes('/posts/')) {
    const dirIndex = currentPath.indexOf('/posts/');
    const basePath = currentPath.substring(0, dirIndex);
    indexUrl = `${basePath}/search-index.json`;
}

// 3. 如果没有找到，使用当前目录
else {
    indexUrl = 'search-index.json';
}
```

---

## 路径计算示例

### 根目录部署

| 当前路径 | 找到目录 | 上一级路径 | 结果 |
|---------|---------|-----------|------|
| `/` | - | - | `search-index.json` |
| `/index.html` | - | - | `search-index.json` |
| `/posts/article.html` | `/posts/` | `` (空) | `/search-index.json` |
| `/posts/杂项/多账户git配置.html` | `/posts/` | `` (空) | `/search-index.json` |
| `/tags/python.html` | `/tags/` | `` (空) | `/search-index.json` |
| `/page/2.html` | `/page/` | `` (空) | `/search-index.json` |

### 子路径部署 (/mblog)

| 当前路径 | 找到目录 | 上一级路径 | 结果 |
|---------|---------|-----------|------|
| `/mblog/` | - | - | `search-index.json` |
| `/mblog/index.html` | - | - | `search-index.json` |
| `/mblog/posts/article.html` | `/posts/` | `/mblog` | `/mblog/search-index.json` |
| `/mblog/posts/杂项/多账户git配置.html` | `/posts/` | `/mblog` | `/mblog/search-index.json` |
| `/mblog/tags/python.html` | `/tags/` | `/mblog` | `/mblog/search-index.json` |

### 子路径部署 (/aaa)

| 当前路径 | 找到目录 | 上一级路径 | 结果 |
|---------|---------|-----------|------|
| `/aaa/posts/xx/xxx/xx.html` | `/posts/` | `/aaa` | `/aaa/search-index.json` |

---

## 实现代码

### main.js

```javascript
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchResults) {
        return;
    }

    // 获取基础路径
    // search-index.json 在 posts/tags/page 的上一级目录
    let indexUrl = 'search-index.json';  // 默认在当前目录
    const currentPath = window.location.pathname;
    
    // 检查是否在 posts、tags 或 page 目录下
    const specialDirs = ['posts', 'tags', 'page'];
    let foundSpecialDir = false;
    
    for (const dir of specialDirs) {
        const dirPattern = `/${dir}/`;
        if (currentPath.includes(dirPattern)) {
            // 找到特殊目录，提取其上一级路径
            const dirIndex = currentPath.indexOf(dirPattern);
            const basePath = currentPath.substring(0, dirIndex);
            indexUrl = `${basePath}/search-index.json`;
            foundSpecialDir = true;
            break;
        }
    }
    
    // 如果没有找到特殊目录，使用当前目录
    if (!foundSpecialDir) {
        indexUrl = 'search-index.json';
    }
    
    console.log(`Current path: ${currentPath}, Index URL: ${indexUrl}`);

    // 初始化搜索引擎
    const searchEngine = new SearchEngine(indexUrl);
    
    // ... 其余代码
}
```

---

## 测试验证

### 测试命令
```bash
node tests/test_path_calculation.js
```

### 测试结果
```
✅ 14/14 测试通过

✓ 根目录
✓ 首页
✓ 归档页
✓ 文章页（一级）
✓ 嵌套文章（中文目录）
✓ 深层嵌套文章
✓ 标签页
✓ 分页页
✓ 带基础路径的根目录
✓ 带基础路径的首页
✓ 带基础路径的文章
✓ 带基础路径的嵌套文章
✓ 带基础路径的标签页
✓ 带基础路径 /aaa 的深层文章
```

---

## 优势

### 1. 支持基础路径部署
- ✅ 根目录部署：`xx.com/`
- ✅ 子路径部署：`xx.com/mblog/`
- ✅ 任意子路径：`xx.com/blog/`, `xx.com/site/` 等

### 2. 支持嵌套目录
- ✅ 一级：`/posts/article.html`
- ✅ 二级：`/posts/杂项/多账户git配置.html`
- ✅ 多级：`/posts/tech/python/tutorial.html`

### 3. 支持中文路径
- ✅ 中文目录名：`/posts/杂项/`
- ✅ 中文文件名：`多账户git配置.html`
- ✅ Unicode 字符

### 4. 简单可靠
- ✅ 逻辑清晰，易于理解
- ✅ 不依赖复杂计算
- ✅ 经过全面测试

---

## 部署配置

### 无需额外配置

这个方案**不需要任何配置**，自动适配：

1. **根目录部署** - 直接部署到 `xx.com/`
2. **子路径部署** - 部署到 `xx.com/mblog/`
3. **任意路径** - 部署到任何子路径

只要保持目录结构：
```
/
├── search-index.json
├── posts/
│   └── article.html
├── tags/
│   └── python.html
└── page/
    └── 2.html
```

或者：
```
/mblog/
├── search-index.json
├── posts/
│   └── article.html
├── tags/
│   └── python.html
└── page/
    └── 2.html
```

搜索功能都能自动工作！

---

## 调试信息

在浏览器控制台可以看到：

```javascript
// 根目录部署
Current path: /posts/article.html, Index URL: /search-index.json

// 子路径部署
Current path: /mblog/posts/article.html, Index URL: /mblog/search-index.json
```

---

## 总结

通过检测 `posts`、`tags`、`page` 目录并提取其上一级路径，我们实现了：

1. ✅ **自动适配基础路径** - 无需配置
2. ✅ **支持嵌套目录** - 任意深度
3. ✅ **支持中文路径** - Unicode 友好
4. ✅ **简单可靠** - 逻辑清晰，易于维护

这个方案完美支持各种部署场景！
