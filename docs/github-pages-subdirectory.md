# GitHub Pages 子目录部署配置

当你的博客部署到 GitHub Pages 的项目页面（而非用户/组织页面）时，URL 会包含仓库名作为子目录，例如：

```
https://username.github.io/repo-name/
```

这种情况下，所有的静态资源和页面链接都需要包含这个子目录前缀，否则会导致 404 错误。

## 问题示例

假设你的仓库名为 `myblog`，部署后的 URL 是 `https://soft98-top.github.io/myblog/`

如果不配置 `base_path`，生成的链接会是：
- ❌ `/posts/hello.html` → 实际访问 `https://soft98-top.github.io/posts/hello.html` (404)
- ❌ `/static/css/style.css` → 实际访问 `https://soft98-top.github.io/static/css/style.css` (404)

配置 `base_path` 后，链接会变成：
- ✅ `/myblog/posts/hello.html` → 实际访问 `https://soft98-top.github.io/myblog/posts/hello.html`
- ✅ `/myblog/static/css/style.css` → 实际访问 `https://soft98-top.github.io/myblog/static/css/style.css`

## 配置方法

### 1. 修改 config.json

在你的博客项目的 `config.json` 文件中，设置 `site.base_path` 为你的仓库名：

```json
{
  "site": {
    "title": "我的博客",
    "description": "这是我的个人博客",
    "author": "博客作者",
    "url": "https://soft98-top.github.io/myblog",
    "base_path": "/myblog",
    "language": "zh-CN"
  },
  "build": {
    "output_dir": "public",
    "theme": "default",
    "generate_rss": true,
    "generate_sitemap": true
  },
  "theme_config": {
    "posts_per_page": 10,
    "date_format": "%Y-%m-%d",
    "show_toc": true,
    "enable_tags": true,
    "enable_archive": true
  }
}
```

**重要说明：**
- `base_path` 应该以 `/` 开头
- `base_path` 不应该以 `/` 结尾
- `base_path` 应该与你的仓库名一致
- `url` 也应该包含完整的 URL（包括子目录）

### 2. 重新生成静态文件

修改配置后，重新生成静态文件：

```bash
python gen.py
```

### 3. 部署到 GitHub Pages

推送代码到 GitHub，GitHub Actions 会自动部署：

```bash
git add .
git commit -m "Configure base_path for subdirectory deployment"
git push
```

## 不同部署场景的配置

### 场景 1：用户/组织页面（无子目录）

如果你的仓库名是 `username.github.io`，部署后的 URL 是 `https://username.github.io/`，则不需要设置 `base_path`：

```json
{
  "site": {
    "url": "https://username.github.io",
    "base_path": "",
    ...
  }
}
```

### 场景 2：项目页面（有子目录）

如果你的仓库名是 `myblog`，部署后的 URL 是 `https://username.github.io/myblog/`：

```json
{
  "site": {
    "url": "https://username.github.io/myblog",
    "base_path": "/myblog",
    ...
  }
}
```

### 场景 3：自定义域名

如果你使用自定义域名（如 `blog.example.com`），则不需要设置 `base_path`：

```json
{
  "site": {
    "url": "https://blog.example.com",
    "base_path": "",
    ...
  }
}
```

### 场景 4：自定义域名 + 子目录

如果你的自定义域名包含子目录（如 `example.com/blog`）：

```json
{
  "site": {
    "url": "https://example.com/blog",
    "base_path": "/blog",
    ...
  }
}
```

## 验证配置

### 1. 本地测试

生成静态文件后，使用 Python 的 HTTP 服务器测试：

```bash
cd public
python -m http.server 8000
```

访问 `http://localhost:8000`，检查：
- 页面样式是否正常加载
- 链接是否可以正常跳转
- 图片是否正常显示

**注意：** 本地测试时，由于没有子目录，可能会看到一些链接问题。这是正常的，部署到 GitHub Pages 后会正常工作。

### 2. 使用浏览器开发者工具

部署后，打开浏览器的开发者工具（F12），检查：
- Console 标签：查看是否有 404 错误
- Network 标签：查看资源加载情况
- 确保所有 CSS、JS、图片都成功加载

### 3. 检查生成的 HTML

查看生成的 HTML 文件，确认链接格式正确：

```bash
# 查看首页
cat public/index.html | grep href

# 查看文章页
cat public/posts/hello.html | grep href
```

应该看到类似这样的链接：
```html
<a href="/myblog/">首页</a>
<a href="/myblog/posts/hello.html">文章标题</a>
<link rel="stylesheet" href="/myblog/static/css/style.css">
```

## 常见问题

### Q1: 修改了 base_path 但样式还是不正常？

**A:** 确保：
1. 重新运行了 `python gen.py` 生成新的静态文件
2. 清除了浏览器缓存（Ctrl+Shift+R 强制刷新）
3. GitHub Pages 已经完成了新的部署（查看 Actions 标签）

### Q2: 本地测试时链接不工作？

**A:** 这是正常的。本地测试时，由于没有子目录结构，带有 `base_path` 的链接会失败。你可以：
1. 忽略本地测试的链接问题，直接部署到 GitHub Pages 测试
2. 或者临时将 `base_path` 设置为空字符串进行本地测试

### Q3: 如何在本地模拟子目录环境？

**A:** 使用 Nginx 或 Apache 配置子目录：

**使用 Python 的 http.server（简单方法）：**
```bash
# 创建临时目录结构
mkdir -p temp/myblog
cp -r public/* temp/myblog/
cd temp
python -m http.server 8000
```

然后访问 `http://localhost:8000/myblog/`

**使用 Nginx：**
```nginx
server {
    listen 8000;
    server_name localhost;
    
    location /myblog/ {
        alias /path/to/your/blog/public/;
        index index.html;
    }
}
```

### Q4: 部署后首页正常，但其他页面 404？

**A:** 检查：
1. `base_path` 配置是否正确
2. GitHub Pages 的设置是否正确（应该使用 `gh-pages` 分支）
3. 查看 GitHub Actions 的构建日志，确认没有错误

### Q5: RSS 和 Sitemap 的 URL 是否也需要配置？

**A:** 是的，RSS 和 Sitemap 中的 URL 也会自动使用 `base_path`。生成器会自动处理这些文件中的 URL。

## 自动化配置

如果你经常在不同环境部署，可以使用环境变量：

### 1. 创建多个配置文件

```bash
# 本地开发配置
config.local.json

# GitHub Pages 配置
config.github.json

# 生产环境配置
config.prod.json
```

### 2. 使用脚本切换配置

```bash
#!/bin/bash
# deploy.sh

ENV=${1:-github}

case $ENV in
  local)
    cp config.local.json config.json
    ;;
  github)
    cp config.github.json config.json
    ;;
  prod)
    cp config.prod.json config.json
    ;;
esac

python gen.py
```

使用：
```bash
./deploy.sh github  # 使用 GitHub Pages 配置
./deploy.sh local   # 使用本地配置
```

## 迁移现有博客

如果你已经有一个部署在根目录的博客，现在需要迁移到子目录：

### 步骤 1：更新配置

在 `config.json` 中添加 `base_path`。

### 步骤 2：重新生成

```bash
python gen.py
```

### 步骤 3：更新 GitHub Pages 设置

如果需要，在 GitHub 仓库设置中更新 Pages 配置。

### 步骤 4：设置重定向（可选）

如果你想保留旧的 URL，可以在旧位置添加重定向：

在根目录创建 `index.html`：
```html
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=/myblog/">
    <link rel="canonical" href="/myblog/" />
</head>
<body>
    <p>Redirecting to <a href="/myblog/">new location</a>...</p>
</body>
</html>
```

## 相关文档

- [部署文档](deployment.md) - 完整的部署指南
- [配置文档](configuration.md) - 所有配置选项说明
- [故障排除](troubleshooting-deployment.md) - 部署问题解决方案

## 总结

配置 `base_path` 的关键点：
1. ✅ 在 `config.json` 中设置 `site.base_path`
2. ✅ `base_path` 应该与仓库名一致
3. ✅ `base_path` 以 `/` 开头，不以 `/` 结尾
4. ✅ 修改后重新运行 `python gen.py`
5. ✅ 部署后检查所有链接和资源是否正常

如果遇到问题，请查看 [故障排除文档](troubleshooting-deployment.md) 或提交 Issue。
