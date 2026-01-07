# Bug 修复：解密后文章显示位置不正确

## 问题描述

解密后的加密文章内容显示宽度受限，与普通文章的显示宽度不一致。

## 问题原因

在 `encrypted_post.html` 模板中，解密后的内容容器 `#decrypted-content` 被包裹在 `encrypted-content-wrapper` 中，该容器设置了 `max-width: 600px` 的样式限制。这导致：

- **密码输入表单**：正确显示，居中且宽度限制为 600px（符合预期）
- **解密后的内容**：也受到 600px 宽度限制（不符合预期）
- **普通文章内容**：使用 `.post` 的 `max-width: 100%`，没有宽度限制

## 修复方案

### 修改前的结构

```html
<div class="encrypted-content-wrapper">
    <div id="password-form">...</div>
    <div id="decrypted-content">...</div>  <!-- 受 wrapper 宽度限制 -->
</div>
```

### 修改后的结构

```html
<div class="encrypted-content-wrapper">
    <div id="password-form">...</div>
</div>
<div id="decrypted-content">...</div>  <!-- 不受 wrapper 宽度限制 -->
```

## 修改内容

### 1. 模板结构调整

**文件**: `mblog/templates/themes/default/templates/encrypted_post.html`

- 将 `#decrypted-content` 移出 `encrypted-content-wrapper`
- 将 `#encrypted-data` 也移出 wrapper（保持在 article 内）

### 2. JavaScript 逻辑调整

解密成功后，隐藏整个 `encrypted-content-wrapper` 而不是只隐藏 `password-form`：

```javascript
// 修改前
passwordForm.style.display = 'none';

// 修改后
document.querySelector('.encrypted-content-wrapper').style.display = 'none';
```

### 3. CSS 样式调整

为 `.password-form` 添加 `margin-bottom: 2rem`，确保在需要时与其他内容有适当间距。

## 效果

修复后：

- ✅ 密码输入表单：居中显示，宽度限制为 600px
- ✅ 解密后的内容：使用 `.post-content` 样式，与普通文章宽度一致
- ✅ 解密成功后：密码表单容器完全隐藏，内容正常显示
- ✅ 视觉体验：解密前后的布局过渡自然流畅

## 测试

运行加密功能测试：

```bash
python -m pytest tests/test_encryption.py -v
```

所有测试通过 ✓

## 相关文件

- `mblog/templates/themes/default/templates/encrypted_post.html` - 加密文章模板
- `mblog/templates/themes/default/templates/post.html` - 普通文章模板（参考）
- `mblog/templates/themes/default/static/css/style.css` - 样式文件

## 版本

- 修复日期：2026-01-07
- 影响版本：所有包含加密功能的版本
