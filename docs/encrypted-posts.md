# 加密文章功能

mblog 支持文章加密功能，允许你创建需要密码才能查看的私密文章。

## 功能特性

- ✅ 基于密码的文章加密
- ✅ 客户端解密（无需服务器支持）
- ✅ 主题可选支持（向后兼容）
- ✅ 自动密码记忆（使用 sessionStorage）
- ✅ 优雅的用户界面

## 使用方法

### 1. 创建加密文章

在 Markdown 文件的 frontmatter 中添加 `encrypted` 和 `password` 字段：

```markdown
---
title: 我的私密文章
date: 2025-10-26
author: 作者名
description: 这是一篇加密文章
tags: [private, encrypted]
encrypted: true
password: "your-secret-password"
---

# 文章内容

这里是只有知道密码的人才能看到的内容...
```

### 2. 生成博客

正常运行生成命令：

```bash
python gen.py
```

系统会自动：
- 检测文章是否配置了加密
- 使用密码加密文章内容
- 根据主题支持情况选择合适的模板渲染

### 3. 查看加密文章

访问加密文章页面时：
1. 页面显示密码输入框
2. 输入正确的密码
3. 点击"解锁"按钮或按回车键
4. 内容在浏览器中解密并显示

## 主题支持

### 支持加密的主题

如果主题配置了 `encrypted_post` 模板，文章将使用专门的加密模板渲染，提供更好的用户体验。

**theme.json 配置：**

```json
{
  "templates": {
    "base": "base.html",
    "index": "index.html",
    "post": "post.html",
    "encrypted_post": "encrypted_post.html"
  }
}
```

### 不支持加密的主题

如果主题没有配置 `encrypted_post` 模板，系统会：
- 使用普通的 `post.html` 模板
- 将文章内容替换为提示信息："当前主题不支持加密文章功能"
- 文章的其他信息（标题、日期、标签等）正常显示

## 安全说明

### 加密强度

- 使用自定义的 XOR 加密算法
- 密码通过哈希函数处理
- 加密数据以 Base64 编码存储

### 安全限制

⚠️ **重要提示：** 这种加密方式适合以下场景：

- ✅ 防止搜索引擎索引敏感内容
- ✅ 防止普通访客随意查看
- ✅ 分享给特定人群的内容保护

**不适合以下场景：**

- ❌ 高安全性需求的机密信息
- ❌ 需要防止技术人员破解的内容
- ❌ 法律或合规要求的数据保护

### 为什么不够安全？

1. **密码暴露风险**：加密后的内容和加密参数都在客户端，技术人员可以分析加密算法
2. **静态加密**：所有访客看到的是相同的加密数据，容易被离线分析
3. **简化算法**：为了兼容性使用了简化的加密算法，而非标准的 AES

### 最佳实践

1. **使用强密码**：至少 12 个字符，包含字母、数字和特殊字符
2. **定期更换密码**：对于重要内容，定期更新密码
3. **谨慎分享**：只将密码分享给需要查看的人
4. **避免敏感信息**：不要在加密文章中存储真正的机密信息

## 开发者指南

### 创建加密模板

如果你是主题开发者，可以为主题添加加密文章支持：

**1. 创建 encrypted_post.html 模板：**

```html
{% extends "base.html" %}

{% block content %}
<article class="post encrypted-post">
    <header class="post-header">
        <h1>🔒 {{ post.title }}</h1>
        <div class="post-meta">
            <time>{{ post.date.strftime('%Y-%m-%d') }}</time>
        </div>
    </header>

    <div class="encrypted-wrapper">
        <!-- 密码输入表单 -->
        <div id="password-form">
            <p>此文章已加密，请输入密码查看</p>
            <input type="password" id="password-input" placeholder="请输入密码" />
            <button id="decrypt-btn">解锁</button>
            <p id="error-msg" style="display:none;"></p>
        </div>

        <!-- 解密后的内容容器 -->
        <div id="decrypted-content" style="display:none;"></div>

        <!-- 隐藏的加密数据 -->
        <div id="encrypted-data" data-encrypted="{{ post.html }}" style="display:none;"></div>
    </div>
</article>

<script src="{{ url_for_static('js/crypto.js') }}"></script>
<script>
// 解密逻辑
document.getElementById('decrypt-btn').addEventListener('click', function() {
    const password = document.getElementById('password-input').value;
    const encryptedData = document.getElementById('encrypted-data').dataset.encrypted;
    
    try {
        const decrypted = decryptContent(encryptedData, password);
        document.getElementById('password-form').style.display = 'none';
        document.getElementById('decrypted-content').innerHTML = decrypted;
        document.getElementById('decrypted-content').style.display = 'block';
    } catch (e) {
        document.getElementById('error-msg').textContent = '密码错误';
        document.getElementById('error-msg').style.display = 'block';
    }
});
</script>
{% endblock %}
```

**2. 创建 crypto.js 解密脚本：**

参考默认主题的 `static/js/crypto.js` 实现 `decryptContent()` 函数。

**3. 更新 theme.json：**

```json
{
  "templates": {
    "encrypted_post": "encrypted_post.html"
  }
}
```

### 可用变量

在 `encrypted_post.html` 模板中，`post` 对象包含：

- `post.title`：文章标题
- `post.date`：发布日期
- `post.author`：作者
- `post.description`：描述
- `post.tags`：标签列表
- `post.html`：**加密后的内容**（Base64 编码，格式：`iv:encrypted_data`）
- `post.encrypted`：始终为 `true`
- `post.password`：加密密码（不应在模板中显示）

## 常见问题

### Q: 忘记密码怎么办？

A: 密码存储在 Markdown 文件的 frontmatter 中，查看源文件即可找回。

### Q: 可以修改密码吗？

A: 可以，修改 frontmatter 中的 `password` 字段，然后重新生成博客。

### Q: 加密文章会被搜索引擎索引吗？

A: 不会。加密后的内容是乱码，搜索引擎无法理解。但标题和元信息仍然可见。

### Q: 可以在首页隐藏加密文章吗？

A: 目前加密文章仍会在首页显示（标题和描述可见）。如需完全隐藏，可以在 frontmatter 中添加 `draft: true`。

### Q: 密码输入错误有次数限制吗？

A: 没有。这是客户端解密，用户可以无限次尝试。

### Q: 可以为不同文章设置不同密码吗？

A: 可以。每篇文章的 `password` 字段独立配置。

### Q: 如何取消文章加密？

A: 将 frontmatter 中的 `encrypted` 设置为 `false` 或删除该字段，然后重新生成。

## 示例

### 示例 1：简单加密文章

```markdown
---
title: 我的日记
date: 2025-10-26
encrypted: true
password: "diary2025"
---

今天天气不错...
```

### 示例 2：带完整元信息的加密文章

```markdown
---
title: 项目技术方案
date: 2025-10-26
author: 技术团队
description: 内部技术方案文档
tags: [tech, internal, confidential]
encrypted: true
password: "team-secret-2025"
---

# 技术方案

## 架构设计

...
```

### 示例 3：多语言加密文章

```markdown
---
title: Secret Document
date: 2025-10-26
language: en
encrypted: true
password: "secret123"
---

# Confidential Information

This document contains sensitive information...
```

## 更新日志

### v1.0.0 (2025-10-26)

- ✨ 新增文章加密功能
- ✨ 支持主题可选加密模板
- ✨ 默认主题添加加密支持
- ✨ 客户端解密实现
- 📝 添加加密功能文档

## 参考资料

- [主题开发文档](theme-development.md)
- [配置文档](configuration.md)
- [默认主题源码](../mblog/templates/themes/default/)

---

如有问题或建议，欢迎提交 Issue 或 Pull Request！
