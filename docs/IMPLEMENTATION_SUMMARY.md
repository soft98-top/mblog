# 文章加密功能实现总结

## 概述

本文档总结了 mblog 文章加密功能的实现细节。

## 实现日期

2025-10-26

## 功能描述

为 mblog 添加了文章加密功能，允许用户创建需要密码才能查看的私密文章。

## 核心特性

1. **Frontmatter 配置**：在 Markdown 文件中通过 `encrypted: true` 和 `password` 字段配置加密
2. **主题可选支持**：主题可以选择是否支持加密模板，不支持的主题会显示提示信息
3. **客户端解密**：使用 JavaScript 在浏览器中解密内容，无需服务器支持
4. **向后兼容**：不影响现有功能，旧主题仍能正常工作

## 技术实现

### 1. 数据模型扩展

**文件**：`mblog/templates/runtime/markdown_processor.py`

在 `Post` 数据类中添加了两个新字段：

```python
@dataclass
class Post:
    # ... 现有字段 ...
    encrypted: bool = False    # 是否加密
    password: str = ""         # 加密密码
```

在 `parse_post()` 方法中从 frontmatter 提取这些字段：

```python
encrypted = metadata.get('encrypted', False)
password = metadata.get('password', '')
```

### 2. 主题系统增强

**文件**：`mblog/templates/runtime/theme.py`

添加了两个新方法：

```python
def has_template(self, template_name: str) -> bool:
    """检查主题是否配置了指定的模板"""
    templates_config = self._metadata.get('templates', {})
    return template_name in templates_config

def get_template(self, template_name: str) -> str:
    """获取模板文件路径（必须在 theme.json 中配置）"""
    # 强制要求模板在 theme.json 中配置
    # 不再使用硬编码的文件名
```

### 3. 渲染器增强

**文件**：`mblog/templates/runtime/renderer.py`

添加了加密相关方法：

```python
def _simple_hash(self, password: str) -> bytes:
    """简单哈希函数（与 JS 端匹配）"""
    # 实现密码哈希

def _encrypt_content(self, content: str, password: str) -> str:
    """使用简化的 XOR 加密内容"""
    # 实现内容加密
    # 返回格式：iv:encrypted_data（Base64 编码）
```

修改了 `render_post()` 方法：

```python
def render_post(self, post: Post) -> str:
    if post.encrypted and post.password:
        if self.theme.has_template('encrypted_post'):
            # 加密内容并使用加密模板
            encrypted_html = self._encrypt_content(post.html, post.password)
            # 临时替换 post.html 为加密内容
            # 使用 encrypted_post.html 模板渲染
        else:
            # 主题不支持，显示提示信息
            # 使用普通 post.html 模板渲染
    else:
        # 普通文章，正常渲染
```

### 4. 默认主题支持

**新增文件**：

1. `mblog/templates/themes/default/templates/encrypted_post.html`
   - 加密文章专用模板
   - 包含密码输入表单
   - 包含解密逻辑

2. `mblog/templates/themes/default/static/js/crypto.js`
   - 客户端解密函数
   - 哈希算法实现
   - 与 Python 端加密算法匹配

**修改文件**：

- `mblog/templates/themes/default/theme.json`
  - 添加 `"encrypted_post": "encrypted_post.html"` 配置

### 5. 加密算法

使用简化的 XOR 加密算法，原因：

1. **兼容性**：不需要额外的加密库
2. **客户端支持**：可以在浏览器中轻松实现
3. **足够安全**：对于防止搜索引擎索引和普通访客查看已足够

**加密流程**：

```
原始内容 → UTF-8 编码 → PKCS7 填充 → XOR 加密 → Base64 编码
```

**数据格式**：

```
iv:encrypted_data
```

其中 `iv` 和 `encrypted_data` 都是 Base64 编码的字节数据。

### 6. 解密流程

**客户端（JavaScript）**：

```javascript
function decryptContent(encryptedData, password) {
    // 1. 分离 IV 和加密数据
    const [iv, encrypted] = encryptedData.split(':');
    
    // 2. Base64 解码
    const ivBytes = base64ToBytes(iv);
    const encryptedBytes = base64ToBytes(encrypted);
    
    // 3. 生成密钥（与 Python 端相同的哈希算法）
    const key = simpleHash(password);
    
    // 4. XOR 解密
    const decrypted = xorDecrypt(encryptedBytes, key, ivBytes);
    
    // 5. 移除 PKCS7 填充
    const unpadded = removePadding(decrypted);
    
    // 6. UTF-8 解码
    return utf8Decode(unpadded);
}
```

## 文件清单

### 修改的文件

1. `mblog/templates/runtime/markdown_processor.py`
   - 添加 `encrypted` 和 `password` 字段
   - 提取加密配置

2. `mblog/templates/runtime/theme.py`
   - 添加 `has_template()` 方法
   - 修改 `get_template()` 方法

3. `mblog/templates/runtime/renderer.py`
   - 添加加密方法
   - 修改 `render_post()` 方法
   - 统一所有模板获取方式

4. `mblog/templates/themes/default/theme.json`
   - 添加加密模板配置

5. `pyproject.toml`
   - 更新包数据配置

6. `README.md`
   - 添加加密功能说明

7. `CHANGELOG.md`
   - 记录新功能

8. `docs/configuration.md`
   - 添加加密配置说明

9. `docs/theme-development.md`
   - 添加加密模板开发指南

### 新增的文件

1. `mblog/templates/themes/default/templates/encrypted_post.html`
   - 加密文章模板

2. `mblog/templates/themes/default/static/js/crypto.js`
   - 客户端解密脚本

3. `docs/encrypted-posts.md`
   - 完整的加密功能文档

4. `tests/test_encryption.py`
   - 加密功能测试

5. `test-blog/md/encrypted-test.md`
   - 测试用加密文章

6. `docs/IMPLEMENTATION_SUMMARY.md`
   - 本文档

## 使用示例

### 创建加密文章

```markdown
---
title: 我的私密日记
date: 2025-10-26
encrypted: true
password: "my-secret-password"
---

这是只有知道密码的人才能看到的内容...
```

### 主题支持加密

在 `theme.json` 中添加：

```json
{
  "templates": {
    "encrypted_post": "encrypted_post.html"
  }
}
```

创建 `encrypted_post.html` 模板和 `crypto.js` 脚本。

## 测试

运行测试：

```bash
python -m pytest tests/test_encryption.py -v
```

测试覆盖：

1. ✅ Post 对象的加密字段提取
2. ✅ 加密算法正确性
3. ✅ 主题模板检测

## 安全说明

### 适用场景

- ✅ 防止搜索引擎索引
- ✅ 防止普通访客查看
- ✅ 分享给特定人群

### 不适用场景

- ❌ 高安全性需求的机密信息
- ❌ 需要防止技术人员破解
- ❌ 法律或合规要求的数据保护

### 安全限制

1. 加密数据和算法都在客户端，可以被分析
2. 使用简化的加密算法，不是标准的 AES
3. 密码存储在 HTML 中（虽然经过加密）

## 向后兼容性

- ✅ 不影响现有功能
- ✅ 旧主题仍能正常工作
- ✅ 不支持加密的主题会显示提示
- ✅ 普通文章不受影响

## 性能影响

- 加密操作在生成时进行，不影响运行时性能
- 解密在客户端进行，不需要服务器资源
- 加密文章的 HTML 文件略大（包含加密数据）

## 未来改进

1. 支持更强的加密算法（如真正的 AES）
2. 支持多密码（不同用户不同密码）
3. 支持密码过期时间
4. 支持密码提示功能
5. 支持批量加密/解密

## 参考资料

- [加密文章文档](encrypted-posts.md)
- [主题开发文档](theme-development.md)
- [配置文档](configuration.md)

## 贡献者

- 实现：Kiro AI Assistant
- 日期：2025-10-26

---

如有问题或建议，欢迎提交 Issue 或 Pull Request！
