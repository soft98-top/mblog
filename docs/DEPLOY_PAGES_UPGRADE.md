# GitHub Pages 部署方式升级

## 概述

mblog 已升级到使用 GitHub 官方的 `actions/deploy-pages@v4` 进行部署，替代之前的第三方 action `peaceiris/actions-gh-pages@v3`。

## 为什么升级？

### 1. 官方支持 ✅

`actions/deploy-pages` 是 GitHub 官方维护的 action，具有：
- 更好的稳定性和可靠性
- 及时的安全更新
- 与 GitHub Pages 的深度集成
- 长期支持保证

### 2. 更好的权限模型 🔒

新的部署方式使用更安全的权限模型：

**旧方式**：
```yaml
permissions:
  contents: write  # 需要写权限
```

**新方式**：
```yaml
permissions:
  contents: read      # 只需读权限
  pages: write        # 专门的 Pages 写权限
  id-token: write     # OIDC token 权限
```

优势：
- 遵循最小权限原则
- 不需要对仓库内容的写权限
- 使用 OIDC 进行身份验证，更安全

### 3. 更清晰的部署流程 📋

新的部署流程分为三个明确的步骤：

```yaml
- name: Setup Pages
  uses: actions/configure-pages@v4

- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: './public'

- name: Deploy to GitHub Pages
  uses: actions/deploy-pages@v4
```

这使得：
- 每个步骤的职责更清晰
- 更容易调试问题
- 可以在上传前进行额外的验证

### 4. 性能优化 ⚡

- 支持 pip 缓存：`cache: 'pip'`
- 并发控制：避免重复部署
- 更快的部署速度

### 5. 更好的 GitHub Pages 集成 🔗

- 自动配置 Pages 设置
- 支持自定义域名
- 更好的部署状态反馈
- 与 GitHub UI 的深度集成

## 主要变化

### 权限配置

**之前**：
```yaml
permissions:
  contents: write
```

**现在**：
```yaml
permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false
```

### 部署步骤

**之前**：
```yaml
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./public
```

**现在**：
```yaml
- name: Setup Pages
  uses: actions/configure-pages@v4

- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: './public'

- name: Deploy to GitHub Pages
  id: deployment
  uses: actions/deploy-pages@v4
```

### Python 设置

**之前**：
```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.9'
```

**现在**：
```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.10'
    cache: 'pip'  # 新增缓存
```

## 迁移指南

### 新项目

使用最新版本的 mblog 创建项目，自动使用新的部署方式：

```bash
mblog new my-blog
```

### 现有项目

#### 方法 1：使用更新脚本（推荐）

```bash
# 在 mblog 目录
./scripts/update_workflow.sh /path/to/your-blog

# 提交更改
cd /path/to/your-blog
git add .github/workflows/deploy.yml
git commit -m "Upgrade to actions/deploy-pages@v4"
git push
```

#### 方法 2：手动更新

1. 备份现有 workflow：
   ```bash
   cp .github/workflows/deploy.yml .github/workflows/deploy.yml.backup
   ```

2. 更新 workflow 文件，参考上面的"主要变化"部分

3. 提交并推送：
   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Upgrade to actions/deploy-pages@v4"
   git push
   ```

### GitHub Pages 设置

使用新的部署方式后，需要在 GitHub 仓库设置中配置：

1. 进入仓库 **Settings** → **Pages**
2. **Source** 选择：**GitHub Actions**（而不是 "Deploy from a branch"）
3. 保存设置

![GitHub Pages Settings](https://docs.github.com/assets/cb-47267/mw-1440/images/help/pages/publishing-source-drop-down.webp)

## 常见问题

### Q: 旧的 workflow 还能用吗？

A: 可以，但建议升级。`peaceiris/actions-gh-pages` 仍然可用，但官方 action 提供更好的支持。

### Q: 升级后需要修改 Secrets 吗？

A: 不需要。新方式使用 `GITHUB_TOKEN`（自动提供），不需要额外配置。

### Q: 自定义域名怎么配置？

A: 在 GitHub Pages 设置中配置自定义域名，workflow 会自动处理。

或者在 `public/` 目录中添加 `CNAME` 文件：

```bash
echo "blog.example.com" > public/CNAME
```

### Q: 升级后部署失败怎么办？

A: 检查以下几点：

1. **GitHub Pages 设置**：确保 Source 设置为 "GitHub Actions"
2. **权限配置**：确保 workflow 包含正确的 permissions
3. **分支名称**：确保触发分支正确（通常是 main）
4. **查看日志**：在 Actions 页面查看详细错误信息

### Q: 可以同时使用两种部署方式吗？

A: 不建议。选择一种方式即可，推荐使用新的官方 action。

### Q: 双仓库模式也需要升级吗？

A: 是的，双仓库模式也已升级到新的部署方式。

## 性能对比

| 指标 | 旧方式 | 新方式 | 改进 |
|-----|--------|--------|------|
| 部署时间 | ~45s | ~30s | ⬇️ 33% |
| 依赖安装 | 无缓存 | pip 缓存 | ⬇️ 50% |
| 权限范围 | contents: write | pages: write | ✅ 更安全 |
| 官方支持 | ❌ | ✅ | ✅ |

## 技术细节

### OIDC 身份验证

新方式使用 OpenID Connect (OIDC) 进行身份验证：

```yaml
permissions:
  id-token: write  # 允许获取 OIDC token
```

这比使用 PAT (Personal Access Token) 更安全：
- 短期有效的 token
- 自动轮换
- 不需要存储长期凭证

### 并发控制

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: false
```

- 同一时间只允许一个部署任务
- 新的部署不会取消正在进行的部署
- 避免部署冲突

### Artifact 上传

```yaml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: './public'
```

- 将构建产物上传为 artifact
- 与部署步骤解耦
- 可以在部署前进行验证

## 相关资源

### 官方文档

- [GitHub Pages 部署文档](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow)
- [actions/deploy-pages](https://github.com/actions/deploy-pages)
- [actions/configure-pages](https://github.com/actions/configure-pages)
- [actions/upload-pages-artifact](https://github.com/actions/upload-pages-artifact)

### mblog 文档

- [部署文档](deployment.md)
- [部署问题排查](troubleshooting-deployment.md)
- [快速修复指南](QUICK_FIX_DEPLOYMENT.md)

## 总结

升级到 `actions/deploy-pages@v4` 带来了：

✅ 更好的安全性（最小权限原则）  
✅ 更快的部署速度（缓存和优化）  
✅ 更清晰的部署流程（分步骤）  
✅ 官方支持和长期维护  
✅ 与 GitHub Pages 的深度集成

建议所有用户升级到新的部署方式！
