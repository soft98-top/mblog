# 双仓库模式实战示例

这是一个完整的双仓库模式博客搭建示例，从零开始到部署上线。

## 场景说明

假设你是一个技术团队的负责人，想要搭建一个团队博客：
- 技术人员负责博客的配置、主题和部署
- 内容团队负责撰写文章
- 需要对文章进行审核后再发布

## 步骤 1：创建内容仓库

首先在 GitHub 上创建一个内容仓库，用于存放所有文章。

```bash
# 在 GitHub 上创建仓库：team-blog-content
# 克隆到本地
git clone git@github.com:yourteam/team-blog-content.git
cd team-blog-content

# 创建一些示例文章
mkdir -p tech life

cat > tech/getting-started.md << 'EOF'
---
title: "团队博客开始啦"
date: 2025-10-26
tags: ["公告", "技术"]
author: "技术团队"
---

# 欢迎来到我们的团队博客

这是我们团队的第一篇文章...
EOF

cat > life/team-building.md << 'EOF'
---
title: "团队建设活动回顾"
date: 2025-10-25
tags: ["生活", "团队"]
author: "HR 团队"
---

# 上周的团队建设活动

我们去了...
EOF

# 提交并推送
git add .
git commit -m "Initial blog content"
git push origin main
```

## 步骤 2：创建博客项目

使用 mblog 创建博客项目，选择双仓库模式。

```bash
# 安装 mblog
pip install mblog

# 创建博客项目
mblog new team-blog
```

交互式提示：
```
欢迎使用 mblog！

请选择博客模式：
  1. 单仓库模式（默认）- 所有内容在一个仓库中
  2. 双仓库模式 - 内容与配置分离，支持自动同步

请选择 [1/2] (默认: 1): 2

双仓库模式说明：
  - 博客配置、主题在主仓库
  - Markdown 文章在独立的内容仓库
  - 内容更新自动触发博客重新部署
  - 适合团队协作和内容管理分离

请输入内容仓库的 SSH URL (例如: git@github.com:user/content.git): 
git@github.com:yourteam/team-blog-content.git
```

## 步骤 3：配置博客

```bash
cd team-blog

# 编辑配置文件
cat > config.json << 'EOF'
{
  "site": {
    "title": "我们的团队博客",
    "description": "分享技术与生活",
    "author": "技术团队",
    "url": "https://yourteam.github.io/team-blog",
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
    "date_format": "%Y年%m月%d日",
    "show_toc": true,
    "enable_tags": true,
    "enable_archive": true
  }
}
EOF
```

## 步骤 4：生成 Deploy Key

```bash
# 生成专用的 SSH 密钥对
ssh-keygen -t ed25519 -C "team-blog-content-access" -f content_deploy_key -N ""

# 这会生成两个文件：
# - content_deploy_key (私钥)
# - content_deploy_key.pub (公钥)
```

## 步骤 5：配置内容仓库

1. 打开内容仓库：https://github.com/yourteam/team-blog-content
2. 进入 **Settings → Deploy keys**
3. 点击 **Add deploy key**
4. 配置：
   - Title: `Team Blog Access`
   - Key: 粘贴 `content_deploy_key.pub` 的内容
   - **不要勾选** "Allow write access"
5. 点击 **Add key**

## 步骤 6：创建博客仓库并配置 Secrets

```bash
# 在 GitHub 上创建博客仓库：team-blog
# 推送代码
git remote add origin git@github.com:yourteam/team-blog.git
git push -u origin main
```

配置 Secrets：

1. 打开博客仓库：https://github.com/yourteam/team-blog
2. 进入 **Settings → Secrets and variables → Actions**
3. 添加 `CONTENT_REPO_KEY`：
   - Name: `CONTENT_REPO_KEY`
   - Value: 粘贴 `content_deploy_key` 文件的完整内容
4. 添加 `CONTENT_REPO_URL`：
   - Name: `CONTENT_REPO_URL`
   - Value: `git@github.com:yourteam/team-blog-content.git`

## 步骤 7：配置 GitHub Pages

1. 进入博客仓库的 **Settings → Pages**
2. Source 选择 **GitHub Actions**
3. 保存

## 步骤 8：验证部署

1. 进入博客仓库的 **Actions** 页面
2. 查看 "Deploy Blog" workflow 是否成功运行
3. 等待几分钟后，访问：https://yourteam.github.io/team-blog

## 步骤 9：设置内容审核流程

为内容仓库配置分支保护规则：

1. 进入内容仓库的 **Settings → Branches**
2. 添加分支保护规则：
   - Branch name pattern: `main`
   - 勾选 "Require a pull request before merging"
   - 勾选 "Require approvals" (至少 1 个审核)
3. 保存

## 日常工作流程

### 内容团队写作流程

```bash
# 克隆内容仓库
git clone git@github.com:yourteam/team-blog-content.git
cd team-blog-content

# 创建新分支
git checkout -b add-new-post

# 编写文章
cat > tech/docker-tutorial.md << 'EOF'
---
title: "Docker 入门教程"
date: 2025-10-27
tags: ["Docker", "教程"]
author: "张三"
---

# Docker 基础

Docker 是一个...
EOF

# 提交并推送
git add .
git commit -m "Add Docker tutorial"
git push origin add-new-post
```

### 审核流程

1. 内容作者在 GitHub 上创建 Pull Request
2. 审核者 review 文章内容
3. 提出修改意见或直接批准
4. 合并到 main 分支

### 自动部署

一旦 PR 被合并到 main 分支：
1. 内容仓库更新
2. 博客仓库的 GitHub Actions 在 30 分钟内检测到更新
3. 自动拉取最新内容
4. 重新生成静态网站
5. 自动部署到 GitHub Pages

如果想立即部署，可以手动触发：
1. 进入博客仓库的 **Actions** 页面
2. 选择 "Deploy Blog" workflow
3. 点击 "Run workflow"

## 权限管理

### 博客仓库（team-blog）
- 技术团队：Admin 权限
- 内容团队：无需访问

### 内容仓库（team-blog-content）
- 技术团队：Admin 权限
- 内容团队：Write 权限
- 外部贡献者：通过 PR 贡献

## 本地预览

技术人员本地开发时：

```bash
cd team-blog

# 克隆内容仓库
git clone git@github.com:yourteam/team-blog-content.git md

# 安装依赖
pip install -r requirements.txt

# 生成静态文件
python gen.py

# 预览
cd public
python -m http.server 8000
# 访问 http://localhost:8000
```

## 自定义主题

技术人员可以自定义主题而不影响内容团队：

```bash
cd team-blog

# 修改主题
vim theme/static/css/style.css
vim theme/templates/base.html

# 提交并推送
git add theme/
git commit -m "Update theme styles"
git push

# 自动触发重新部署
```

## 调整同步频率

如果觉得 30 分钟太长，可以修改 `.github/workflows/deploy.yml`：

```yaml
schedule:
  - cron: '*/10 * * * *'  # 改为每 10 分钟
```

或者使用 webhook 实现实时更新（参考[独立内容仓库文档](separate-content-repo.md)的高级配置部分）。

## 故障排查

### 部署失败

查看 Actions 日志：
1. 进入博客仓库的 **Actions** 页面
2. 点击失败的 workflow run
3. 查看详细日志

常见问题：
- **SSH 连接失败**：检查 Deploy Key 是否正确配置
- **权限错误**：确认 `CONTENT_REPO_KEY` secret 包含完整的私钥
- **内容未更新**：手动触发 workflow 或等待下一次定时任务

### 内容未显示

1. 检查文章的 frontmatter 格式是否正确
2. 确认文章已提交到内容仓库的 main 分支
3. 查看生成日志确认文章被正确处理

## 安全提示

1. **删除本地密钥文件**：配置完成后删除 `content_deploy_key` 和 `content_deploy_key.pub`
2. **定期轮换密钥**：建议每年更换一次 Deploy Key
3. **最小权限原则**：Deploy Key 只给予读权限
4. **审核流程**：通过 PR 和分支保护确保内容质量

## 总结

双仓库模式的优势：
- ✅ 职责分离：技术和内容团队各司其职
- ✅ 权限控制：精细的访问权限管理
- ✅ 审核流程：通过 PR 确保内容质量
- ✅ 自动部署：内容更新自动触发部署
- ✅ 独立备份：内容独立存储，易于迁移

现在你的团队博客已经完全搭建好了！内容团队可以专注于写作，技术团队可以专注于优化博客功能和性能。
