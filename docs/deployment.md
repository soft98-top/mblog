# 部署文档

本文档介绍如何将 mblog 生成的静态博客部署到各种平台。

## 部署前准备

### 1. 生成静态文件

在部署前，确保已经生成了静态文件：

```bash
cd your-blog
python gen.py
```

生成的文件默认在 `public/` 目录中。

### 2. 测试本地预览

在部署前，建议先在本地预览：

```bash
cd public
python -m http.server 8000
```

在浏览器中访问 `http://localhost:8000` 检查效果。

## GitHub Pages 部署

GitHub Pages 是最简单的免费静态网站托管方案。

### 方式一：使用 GitHub Actions（推荐）

mblog 项目已经包含了 GitHub Actions 配置文件，可以实现自动部署。

#### 步骤 1：创建 GitHub 仓库

在 GitHub 上创建一个新仓库，例如 `my-blog`。

#### 步骤 2：推送代码

```bash
cd your-blog
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/my-blog.git
git push -u origin main
```

#### 步骤 3：配置 GitHub Pages

1. 进入仓库的 Settings
2. 找到 Pages 选项
3. Source 选择 `gh-pages` 分支
4. 点击 Save

#### 步骤 4：等待部署

GitHub Actions 会自动运行，几分钟后你的博客就会发布到：
```
https://yourusername.github.io/my-blog
```

#### 步骤 5：更新博客

以后每次更新博客，只需：

```bash
# 添加或修改 md/ 目录中的文章
git add .
git commit -m "Add new post"
git push
```

GitHub Actions 会自动重新生成和部署。

### 方式二：手动部署

如果不想使用 GitHub Actions，也可以手动部署。

#### 步骤 1：生成静态文件

```bash
python gen.py
```

#### 步骤 2：创建 gh-pages 分支

```bash
git checkout --orphan gh-pages
git rm -rf .
```

#### 步骤 3：复制生成的文件

```bash
cp -r public/* .
git add .
git commit -m "Deploy blog"
git push origin gh-pages
```

#### 步骤 4：配置 GitHub Pages

在仓库设置中，将 Pages 的 Source 设置为 `gh-pages` 分支的根目录。

### 自定义域名

如果你有自己的域名：

#### 步骤 1：添加 CNAME 文件

在项目根目录创建 `CNAME` 文件：

```
yourdomain.com
```

#### 步骤 2：配置 DNS

在域名提供商处添加 DNS 记录：

**使用 A 记录：**
```
A    @    185.199.108.153
A    @    185.199.109.153
A    @    185.199.110.153
A    @    185.199.111.153
```

**使用 CNAME 记录（推荐）：**
```
CNAME    www    yourusername.github.io
```

#### 步骤 3：在 GitHub 设置自定义域名

在仓库的 Settings > Pages 中，输入你的域名并保存。

#### 步骤 4：启用 HTTPS

GitHub Pages 会自动为自定义域名提供免费的 HTTPS 证书。

## Netlify 部署

Netlify 提供了更强大的功能和更好的性能。

### 方式一：通过 Git 连接（推荐）

#### 步骤 1：注册 Netlify

访问 [netlify.com](https://www.netlify.com/) 并注册账号。

#### 步骤 2：连接 GitHub 仓库

1. 点击 "New site from Git"
2. 选择 GitHub 并授权
3. 选择你的博客仓库

#### 步骤 3：配置构建设置

- **Build command**: `python gen.py`
- **Publish directory**: `public`
- **Python version**: 在项目根目录创建 `runtime.txt`：
  ```
  3.10
  ```

#### 步骤 4：部署

点击 "Deploy site"，Netlify 会自动构建和部署。

#### 步骤 5：自定义域名

在 Netlify 的 Domain settings 中可以添加自定义域名。

### 方式二：手动上传

#### 步骤 1：生成静态文件

```bash
python gen.py
```

#### 步骤 2：上传到 Netlify

1. 登录 Netlify
2. 将 `public/` 目录拖拽到 Netlify 的部署区域
3. 等待部署完成

### Netlify 配置文件

创建 `netlify.toml` 文件以自定义构建：

```toml
[build]
  command = "python gen.py"
  publish = "public"

[build.environment]
  PYTHON_VERSION = "3.10"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

## Vercel 部署

Vercel 是另一个优秀的静态网站托管平台。

### 步骤 1：安装 Vercel CLI

```bash
npm install -g vercel
```

### 步骤 2：登录

```bash
vercel login
```

### 步骤 3：部署

```bash
cd your-blog
python gen.py
vercel --prod
```

### 步骤 4：配置

创建 `vercel.json` 文件：

```json
{
  "buildCommand": "python gen.py",
  "outputDirectory": "public",
  "installCommand": "pip install -r requirements.txt"
}
```

## Cloudflare Pages 部署

Cloudflare Pages 提供全球 CDN 加速。

### 步骤 1：注册 Cloudflare

访问 [pages.cloudflare.com](https://pages.cloudflare.com/) 并注册。

### 步骤 2：连接 Git 仓库

1. 点击 "Create a project"
2. 连接你的 GitHub 账号
3. 选择博客仓库

### 步骤 3：配置构建

- **Build command**: `python gen.py`
- **Build output directory**: `public`
- **Environment variables**:
  - `PYTHON_VERSION`: `3.10`

### 步骤 4：部署

点击 "Save and Deploy"。

## 自托管部署

如果你有自己的服务器，可以自行托管。

### 使用 Nginx

#### 步骤 1：生成静态文件

```bash
python gen.py
```

#### 步骤 2：上传到服务器

```bash
scp -r public/* user@yourserver:/var/www/blog/
```

#### 步骤 3：配置 Nginx

创建 Nginx 配置文件 `/etc/nginx/sites-available/blog`：

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/blog;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # 启用 gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # 缓存静态资源
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 步骤 4：启用配置

```bash
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 步骤 5：配置 HTTPS

使用 Let's Encrypt 获取免费 SSL 证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 使用 Apache

#### 步骤 1：上传文件

```bash
scp -r public/* user@yourserver:/var/www/html/blog/
```

#### 步骤 2：配置 Apache

创建配置文件 `/etc/apache2/sites-available/blog.conf`：

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    DocumentRoot /var/www/html/blog

    <Directory /var/www/html/blog>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/blog_error.log
    CustomLog ${APACHE_LOG_DIR}/blog_access.log combined
</VirtualHost>
```

#### 步骤 3：启用配置

```bash
sudo a2ensite blog
sudo systemctl reload apache2
```

## Docker 部署

使用 Docker 容器化部署。

### Dockerfile

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 生成静态文件
RUN python gen.py

# 使用 nginx 提供静态文件
FROM nginx:alpine
COPY --from=0 /app/public /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 构建和运行

```bash
docker build -t my-blog .
docker run -d -p 80:80 my-blog
```

### Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3'
services:
  blog:
    build: .
    ports:
      - "80:80"
    restart: unless-stopped
```

运行：

```bash
docker-compose up -d
```

## 持续集成/持续部署 (CI/CD)

### GitHub Actions 工作流详解

mblog 项目包含的 `.workflow/deploy.yml` 文件：

```yaml
name: Deploy Blog

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Generate static files
      run: |
        python gen.py
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./public
```

### 自定义工作流

你可以根据需要修改工作流：

#### 添加测试步骤

```yaml
- name: Run tests
  run: |
    pytest tests/
```

#### 部署到多个平台

```yaml
- name: Deploy to Netlify
  uses: netlify/actions/cli@master
  with:
    args: deploy --dir=public --prod
  env:
    NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
    NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

#### 发送通知

```yaml
- name: Send notification
  if: success()
  run: |
    curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Blog deployed successfully!"}' \
    ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 性能优化

### 1. 启用 CDN

使用 CDN 加速静态资源加载：

- Cloudflare
- jsDelivr
- Fastly

### 2. 图片优化

压缩图片以减小文件大小：

```bash
# 使用 ImageMagick
convert input.jpg -quality 85 output.jpg

# 使用 TinyPNG API
# 或在线工具 tinypng.com
```

### 3. 启用缓存

在 Nginx 配置中添加缓存头：

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 4. 压缩资源

启用 gzip 压缩：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### 5. 使用 HTTP/2

在 Nginx 中启用 HTTP/2：

```nginx
listen 443 ssl http2;
```

## 监控和分析

### Google Analytics

在主题的 `base.html` 中添加：

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

### Cloudflare Analytics

如果使用 Cloudflare，可以在控制面板中查看分析数据。

### 自托管分析

使用开源分析工具：

- [Plausible](https://plausible.io/)
- [Umami](https://umami.is/)
- [Matomo](https://matomo.org/)

## 备份策略

### 1. Git 版本控制

所有源文件都应该在 Git 中管理：

```bash
git add .
git commit -m "Update blog"
git push
```

### 2. 定期备份

设置定期备份脚本：

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/blog"

# 备份源文件
tar -czf "$BACKUP_DIR/blog-source-$DATE.tar.gz" /path/to/blog

# 备份生成的文件
tar -czf "$BACKUP_DIR/blog-public-$DATE.tar.gz" /path/to/blog/public

# 删除 30 天前的备份
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### 3. 云端备份

将备份上传到云存储：

- AWS S3
- Google Cloud Storage
- 阿里云 OSS

## 故障排除

### 部署失败

**问题：** GitHub Actions 构建失败

**解决方法：**
1. 检查 Actions 日志查看错误信息
2. 确认 `requirements.txt` 包含所有依赖
3. 检查 Python 版本是否正确

### 页面 404

**问题：** 部署后访问页面显示 404

**解决方法：**
1. 确认 GitHub Pages 设置正确
2. 检查 `config.json` 中的 `site.url` 是否正确
3. 等待几分钟让 DNS 生效

### 样式丢失

**问题：** 页面显示但样式不正确

**解决方法：**
1. 检查静态资源路径是否正确
2. 确认 `public/static/` 目录包含所有资源
3. 检查浏览器控制台的错误信息

### 自定义域名不工作

**问题：** 自定义域名无法访问

**解决方法：**
1. 检查 DNS 记录是否正确配置
2. 等待 DNS 传播（可能需要 24-48 小时）
3. 使用 `dig` 或 `nslookup` 检查 DNS 解析

```bash
dig yourdomain.com
```

## 最佳实践

### 1. 使用版本控制

始终使用 Git 管理你的博客源文件。

### 2. 自动化部署

使用 CI/CD 工具自动化部署流程。

### 3. 测试后部署

在本地测试无误后再推送到生产环境。

### 4. 监控网站状态

使用监控工具（如 UptimeRobot）监控网站可用性。

### 5. 定期更新

定期更新依赖和主题以获得最新功能和安全修复。

### 6. 备份重要数据

定期备份源文件和配置。

### 7. 使用 HTTPS

始终为网站启用 HTTPS。

### 8. 优化性能

压缩图片、启用缓存、使用 CDN。

## 平台对比

| 平台 | 优点 | 缺点 | 适合场景 |
|------|------|------|----------|
| GitHub Pages | 免费、简单、与 Git 集成 | 功能有限、构建时间限制 | 个人博客、开源项目 |
| Netlify | 功能强大、免费额度高、自动 HTTPS | 国内访问可能较慢 | 专业博客、商业项目 |
| Vercel | 性能优秀、部署快速 | 免费额度有限 | 现代化项目 |
| Cloudflare Pages | 全球 CDN、免费额度高 | 配置相对复杂 | 需要全球访问的博客 |
| 自托管 | 完全控制、无限制 | 需要维护服务器、成本较高 | 企业博客、高流量网站 |

## 参考资源

- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [Netlify 文档](https://docs.netlify.com/)
- [Vercel 文档](https://vercel.com/docs)
- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [Nginx 文档](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

祝你部署顺利！如有问题，请查看 [常见问题](../README.md#常见问题) 或提交 Issue。
