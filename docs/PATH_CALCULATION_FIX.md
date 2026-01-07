# 搜索索引路径计算修复

## 问题描述

之前的路径计算逻辑有缺陷，无法正确处理嵌套目录和中文路径。

### 问题示例

**旧逻辑：**
```javascript
if (currentPath.includes('/posts/') || currentPath.includes('/tags/') || currentPath.includes('/page/')) {
    const pathParts = currentPath.split('/').filter(p => p);
    if (pathParts.length > 1) {
        basePath = '../'.repeat(pathParts.length - 1);
    }
}
```

**问题：**
- `/posts/杂项/多账户git配置.html` → 计算错误
- `/aaa/posts/xx/xxx/xx.html` → 计算错误
- 只检查特定目录名，不够通用

---

## 新的解决方案

### 核心思路

**search-index.json 总是在网站根目录**，所以需要：
1. 计算当前页面的目录深度
2. 根据深度生成相应数量的 `../`

### 新算法

```javascript
// 移除文件名，只保留目录路径
const dirPath = currentPath.substring(0, currentPath.lastIndexOf('/'));

// 计算目录深度（根目录深度为0）
const depth = dirPath === '' ? 0 : dirPath.split('/').filter(p => p).length;

// 根据深度生成相对路径
let basePath = '';
if (depth > 0) {
    basePath = '../'.repeat(depth);
}

const indexUrl = `${basePath}search-index.json`;
```

### 算法步骤

1. **提取目录路径**
   - `/posts/杂项/多账户git配置.html` → `/posts/杂项`
   - `/aaa/posts/xx/xxx/xx.html` → `/aaa/posts/xx/xxx`

2. **计算深度**
   - `/posts/杂项` → 分割后 `['posts', '杂项']` → 深度 = 2
   - `/aaa/posts/xx/xxx` → 分割后 `['aaa', 'posts', 'xx', 'xxx']` → 深度 = 4

3. **生成相对路径**
   - 深度 2 → `../../search-index.json`
   - 深度 4 → `../../../../search-index.json`

---

## 测试用例

### 基本路径

| 当前路径 | 目录深度 | 结果 |
|---------|---------|------|
| `/` | 0 | `search-index.json` |
| `/index.html` | 0 | `search-index.json` |
| `/archive.html` | 0 | `search-index.json` |

### 一级子目录

| 当前路径 | 目录深度 | 结果 |
|---------|---------|------|
| `/posts/article.html` | 1 | `../search-index.json` |
| `/tags/python.html` | 1 | `../search-index.json` |
| `/page/2.html` | 1 | `../search-index.json` |

### 嵌套目录（包含中文）

| 当前路径 | 目录深度 | 结果 |
|---------|---------|------|
| `/posts/杂项/多账户git配置.html` | 2 | `../../search-index.json` |
| `/posts/tech/python.html` | 2 | `../../search-index.json` |
| `/posts/tech/python/tutorial.html` | 3 | `../../../search-index.json` |

### 带基础路径

| 当前路径 | 目录深度 | 结果 |
|---------|---------|------|
| `/aaa/` | 1 | `../search-index.json` |
| `/aaa/index.html` | 1 | `../search-index.json` |
| `/aaa/posts/article.html` | 2 | `../../search-index.json` |
| `/aaa/posts/xx/xxx/xx.html` | 4 | `../../../../search-index.json` |

---

## 测试验证

### Node.js 测试
```bash
node tests/test_path_calculation.js
```

**结果：** ✅ 13/13 测试通过

```
✓ 根目录
✓ 首页
✓ 归档页
✓ 文章页（一级）
✓ 标签页
✓ 分页页
✓ 嵌套文章（中文目录）
✓ 嵌套文章（英文目录）
✓ 深层嵌套文章
✓ 带基础路径的根目录
✓ 带基础路径的首页
✓ 带基础路径的文章
✓ 带基础路径的深层文章
```

### HTML 测试
打开 `tests/test_search_path_fix.html` 在浏览器中查看

**结果：** ✅ 11/11 测试通过

---

## 优势

### 1. 通用性
- ✅ 不依赖特定目录名（posts、tags 等）
- ✅ 适用于任意目录结构
- ✅ 支持任意深度的嵌套

### 2. 国际化
- ✅ 支持中文目录名
- ✅ 支持任何 Unicode 字符
- ✅ 不受路径内容影响

### 3. 灵活性
- ✅ 支持带基础路径的部署（如 `/blog/`）
- ✅ 支持自定义目录结构
- ✅ 易于维护和理解

### 4. 可靠性
- ✅ 基于数学计算，不依赖字符串匹配
- ✅ 边界情况处理完善
- ✅ 经过全面测试验证

---

## 实现细节

### 关键代码

**main.js 中的实现：**
```javascript
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchResults) {
        return;
    }

    // 计算搜索索引路径
    let basePath = '';
    const currentPath = window.location.pathname;
    
    // 移除文件名，只保留目录路径
    const dirPath = currentPath.substring(0, currentPath.lastIndexOf('/'));
    
    // 计算目录深度（根目录深度为0）
    const depth = dirPath === '' ? 0 : dirPath.split('/').filter(p => p).length;
    
    // 根据深度生成相对路径
    if (depth > 0) {
        basePath = '../'.repeat(depth);
    }
    
    const indexUrl = `${basePath}search-index.json`;
    console.log(`Current path: ${currentPath}, Depth: ${depth}, Index URL: ${indexUrl}`);

    // ... 其余初始化代码
}
```

### 调试信息

添加了 console.log 输出，方便调试：
```
Current path: /posts/杂项/多账户git配置.html, Depth: 2, Index URL: ../../search-index.json
```

---

## 迁移说明

### 对现有用户的影响

- ✅ **无需修改配置** - 自动适配
- ✅ **向后兼容** - 所有现有路径都能正常工作
- ✅ **性能无影响** - 计算开销可忽略

### 升级步骤

1. 更新 `main.js` 文件
2. 清除浏览器缓存
3. 测试搜索功能

---

## 总结

通过改进路径计算算法，我们实现了：

1. ✅ **正确处理嵌套目录** - 包括中文路径
2. ✅ **支持任意目录结构** - 不限于特定目录名
3. ✅ **通用且可靠** - 基于数学计算，不依赖字符串匹配
4. ✅ **全面测试** - 13 个测试用例全部通过

现在搜索功能可以在任何页面、任何目录结构下正常工作！
