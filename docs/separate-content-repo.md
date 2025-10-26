# 独立内容仓库模式

mblog 支持将博客内容（Markdown 文件）与博客配置、主题分离到不同的 Git 仓库中。这种模式特别适合团队协作和内容管理分离的场景。

## 架构说明

### 单仓库模式（默认）
```
blog-repo/
├── md/              # Markdown 文章
├── theme/           # 主题文件
├── config.json      # 配置
└── gen.py           # 生成脚本
```

所有内容在一个仓库中，简单直接。

### 双仓库模式
```
blog-repo/           # 主仓库（配置和主题）
├── theme/
├── config.json
└── gen.py

content-repo/        # 内容仓库（只有文章）
└── *.md
```

**工作流程：**
1. 内容仓库更新 Markdown 文章
2. GitHub Actions 自动检测更新（每 30 分钟或手动触发）
3. 自动拉取最新内容
4. 重新生成静态网站
5. 自动部署到 GitHub Pages

## 使用场景

### 适合双仓库模式的场景

- **团队协作博客**：技术人员管理配置，写作者只需关注内容
- **权限分离**：给不同的人分配不同的仓库访问权限
- **内容审核**：通过 PR 流程审核文章
- **多博客共享内容**：一个内容仓库可以被多个博客使用
- **内容备份**：内容独立存储，更容易迁移和备份

### 适合单仓库模式的场景

- **个人博客**：一个人管理所有内容
- **简单场景**：不需要复杂的权限管理
- **快速开始**：最小化配置，立即开始写作

## 创建双仓库模式博客

### 1. 初始化项目

```bash
mblog new my-blog
```

在交互式提示中选择 "2. 双仓库模式"，并输入内容仓库的 SSH URL。

### 2. 准备内容仓库

如果还没有内容仓库，先创建一个：

```bash
# 在 GitHub 上创建一个新仓库（例如：blog-content）
git clone git@github.com:username/blog-content.git
cd blog-content

# 添加一些 Markdown 文章
echo "# 第一篇文章" > first-post.md
git add .
git commit -m "Initial content"
git push
```

### 3. 配置 SSH Deploy Key

生成专用的 SSH 密钥对：

```bash
ssh-keygen -t ed25519 -C "blog-content-access" -f content_deploy_key -N ""
```

这会生成两个文件：
- `content_deploy_key` - 私钥
- `content_deploy_key.pub` - 公钥

### 4. 配置内容仓库

1. 打开内容仓库的 GitHub 页面
2. 进入 **Settings → Deploy keys**
3. 点击 **Add deploy key**
4. 标题：`Blog Access`
5. 将 `content_deploy_key.pub` 的内容粘贴到 Key 框
6. **不要勾选** "Allow write access"（只需要读权限）
7. 点击 **Add key**

### 5. 配置博客仓库 Secrets

1. 打开博客仓库的 GitHub 页面
2. 进入 **Settings → Secrets and variables → Actions**
3. 添加两个 secrets：

**CONTENT_REPO_KEY**：
- Name: `CONTENT_REPO_KEY`
- Value: `content_deploy_key` 文件的完整内容（私钥）

**CONTENT_REPO_URL**：
- Name: `CONTENT_REPO_URL`
- Value: 内容仓库的 SSH URL（例如：`git@github.com:username/blog-content.git`）

### 6. 配置 GitHub Pages

1. 进入博客仓库的 **Settings → Pages**
2. Source 选择 **GitHub Actions**

### 7. 推送博客仓库

```bash
cd my-blog
git remote add origin git@github.com:username/my-blog.git
git push -u origin main
```

### 8. 验证部署

1. 进入博客仓库的 **Actions** 页面
2. 查看 "Deploy Blog" workflow 是否成功运行
3. 访问你的 GitHub Pages 地址查看博客

## 工作流程

### 日常写作流程

1. 在内容仓库中编写或修改 Markdown 文章：
```bash
cd blog-content
echo "# 新文章" > new-post.md
git add .
git commit -m "Add new post"
git push
```

2. 等待自动部署（最多 30 分钟）或手动触发：
   - 进入博客仓库的 Actions 页面
   - 选择 "Deploy Blog" workflow
   - 点击 "Run workflow"

3. 博客自动更新

### 本地预览

本地开发时需要手动克隆内容仓库：

```bash
cd my-blog
git clone git@github.com:username/blog-content.git md
python gen.py
```

生成的静态文件在 `public/` 目录中。

## 自动部署机制

博客仓库的 GitHub Actions workflow 会：

1. **定时检查**：每 30 分钟检查一次内容仓库是否有更新
2. **按需触发**：可以手动触发 workflow
3. **智能部署**：只有内容变化时才重新生成和部署

### Workflow 配置

生成的 `.github/workflows/deploy.yml` 文件包含：

```yaml
on:
  push:
    branches: [ main ]
  schedule:
    - cron: '*/30 * * * *'  # 每 30 分钟
  workflow_dispatch:         # 手动触发
```

你可以根据需要调整定时频率。

## 安全性

### Deploy Key 的优势

- **最小权限**：只有读取内容仓库的权限
- **仓库级别**：只能访问指定的内容仓库
- **独立管理**：可以随时撤销而不影响其他访问

### 与 Personal Access Token (PAT) 的对比

| 特性 | Deploy Key | PAT |
|------|-----------|-----|
| 权限范围 | 单个仓库 | 所有仓库 |
| 访问类型 | 只读/读写 | 完整权限 |
| 安全性 | 高 | 中 |
| 推荐使用 | ✅ | ❌ |

### 安全最佳实践

1. **使用 Deploy Key 而不是 PAT**
2. **只给予读权限**：内容仓库的 Deploy Key 不需要写权限
3. **定期轮换密钥**：建议每年更换一次 Deploy Key
4. **删除本地密钥文件**：配置完成后删除 `content_deploy_key` 和 `content_deploy_key.pub`
5. **使用 GitHub Secrets**：永远不要在代码中硬编码密钥

## 团队协作

### 权限分配示例

**场景**：技术团队维护博客，内容团队负责写作

1. **博客仓库**（私有）
   - 技术团队：Admin 权限
   - 内容团队：无需访问

2. **内容仓库**（私有或公开）
   - 技术团队：Admin 权限
   - 内容团队：Write 权限
   - 外部贡献者：通过 PR 贡献

### 内容审核流程

1. 内容作者在内容仓库创建分支
2. 编写文章并提交 PR
3. 审核者 review 内容
4. 合并到 main 分支
5. 自动触发博客部署

## 故障排查

### 部署失败

检查以下几点：

1. **Secrets 配置**
   - `CONTENT_REPO_KEY` 是否包含完整的私钥（包括开头和结尾的标记）
   - `CONTENT_REPO_URL` 是否是正确的 SSH URL

2. **Deploy Key 配置**
   - 公钥是否正确添加到内容仓库
   - Deploy Key 是否启用

3. **仓库访问**
   - 内容仓库是否存在
   - SSH URL 是否正确

4. **查看日志**
   - 进入 Actions 页面查看详细的错误信息

### 内容未更新

1. **检查定时任务**：GitHub Actions 的 cron 可能有延迟
2. **手动触发**：在 Actions 页面手动运行 workflow
3. **查看 workflow 日志**：确认是否检测到内容变化

### 本地开发问题

如果本地 `md/` 目录为空：

```bash
# 手动克隆内容仓库
git clone git@github.com:username/blog-content.git md
```

## 迁移指南

### 从单仓库迁移到双仓库

1. 创建新的内容仓库
2. 将 `md/` 目录的内容移动到内容仓库
3. 按照上述步骤配置 Deploy Key 和 Secrets
4. 更新 `.github/workflows/deploy.yml` 使用双仓库模式的配置
5. 在博客仓库的 `.gitignore` 中添加 `md/`

### 从双仓库迁移到单仓库

1. 克隆内容仓库到 `md/` 目录
2. 删除 `.gitmodules` 文件
3. 更新 `.github/workflows/deploy.yml` 使用单仓库模式的配置
4. 从 `.gitignore` 中移除 `md/`
5. 提交所有更改

## 高级配置

### 自定义同步频率

编辑 `.github/workflows/deploy.yml`：

```yaml
schedule:
  - cron: '*/15 * * * *'  # 改为每 15 分钟
```

### 使用多个内容仓库

如果需要从多个仓库拉取内容：

```yaml
- name: Clone content repositories
  run: |
    git clone ${{ secrets.CONTENT_REPO_URL_1 }} md/blog
    git clone ${{ secrets.CONTENT_REPO_URL_2 }} md/notes
```

### Webhook 触发（实时更新）

如果需要内容更新后立即部署，可以使用 Repository Dispatch：

在内容仓库添加 `.github/workflows/trigger.yml`：

```yaml
name: Trigger Blog Deploy

on:
  push:
    branches: [ main ]

jobs:
  trigger:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger blog repository
        run: |
          curl -X POST \
            -H "Authorization: token ${{ secrets.BLOG_REPO_TOKEN }}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/username/blog-repo/dispatches \
            -d '{"event_type":"content-updated"}'
```

这需要在内容仓库配置 `BLOG_REPO_TOKEN` secret。

## 总结

双仓库模式提供了：

✅ 内容与配置分离  
✅ 灵活的权限管理  
✅ 自动化的部署流程  
✅ 更好的团队协作体验  
✅ 内容独立备份和迁移  

选择适合你的模式，开始写作吧！
