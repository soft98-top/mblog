# mblog 快速参考

## 创建项目

### 单仓库模式（默认）
```bash
mblog new my-blog
# 选择 1
```

### 双仓库模式
```bash
mblog new my-blog
# 选择 2
# 输入内容仓库 URL: git@github.com:user/content.git
```

## 双仓库配置速查

### 1. 生成密钥
```bash
ssh-keygen -t ed25519 -C "blog-access" -f content_deploy_key -N ""
```

### 2. 配置内容仓库
- Settings → Deploy keys → Add deploy key
- 粘贴 `content_deploy_key.pub`
- 不勾选写权限

### 3. 配置博客仓库 Secrets
- `CONTENT_REPO_KEY`: 私钥内容
- `CONTENT_REPO_URL`: SSH URL

### 4. 启用 GitHub Pages
- Settings → Pages → Source: GitHub Actions

## 日常使用

### 写作（内容仓库）
```bash
cd content-repo
git checkout -b new-post
echo "---
title: 新文章
date: 2025-10-26
---
内容..." > new-post.md
git add .
git commit -m "Add new post"
git push origin new-post
# 创建 PR → 审核 → 合并
```

### 本地预览（博客仓库）
```bash
cd blog-repo
git clone <content-repo-url> md
python gen.py
cd public && python -m http.server 8000
```

### 手动触发部署
- Actions → Deploy Blog → Run workflow

## 文件结构对比

| 文件/目录 | 单仓库 | 双仓库 |
|----------|--------|--------|
| .gitmodules | ❌ | ✅ |
| SETUP_GUIDE.md | ❌ | ✅ |
| md/welcome.md | ✅ | ❌ |
| md/ in .gitignore | ❌ | ✅ |

## Workflow 触发条件

### 单仓库
- Push to main

### 双仓库
- Push to main
- Schedule (每 30 分钟)
- Manual trigger

## 常用命令

```bash
# 查看版本
mblog --version

# 查看帮助
mblog --help

# 创建项目
mblog new <name>

# 升级运行时
mblog upgrade                    # 在博客目录中
mblog upgrade -p my-blog         # 指定路径
mblog upgrade --force            # 强制升级，不询问

# 管理主题
mblog theme update               # 更新主题文件
mblog theme reset                # 重置为默认主题
mblog theme update -p my-blog    # 指定路径
mblog theme reset --force        # 强制重置，不询问

# 生成静态文件
python gen.py

# 本地预览
cd public && python -m http.server 8000
```

## 配置文件位置

- 博客配置: `config.json`
- 主题配置: `theme/theme.json`
- 部署配置: `.workflow/deploy.yml`
- Git 配置: `.gitmodules` (双仓库)

## 故障排查

### 部署失败
1. 检查 Actions 日志
2. 验证 Secrets 配置
3. 确认 Deploy Key 已添加

### 内容未更新
1. 检查内容仓库是否已推送
2. 手动触发 workflow
3. 查看 workflow 日志

### 本地预览问题
```bash
# 确保已克隆内容仓库
git clone <content-url> md

# 安装依赖
pip install -r requirements.txt

# 重新生成
python gen.py
```

## 文档链接

- [完整文档](../README.md)
- [双仓库模式](separate-content-repo.md)
- [实战示例](dual-repo-example.md)
- [配置说明](configuration.md)
- [主题开发](theme-development.md)
- [加密文章](encrypted-posts.md)

## 安全提示

✅ 使用 Deploy Key  
✅ 只给读权限  
✅ 删除本地密钥文件  
✅ 定期轮换密钥  
❌ 不要使用 PAT  
❌ 不要提交密钥到仓库  

## 权限建议

### 博客仓库
- 技术团队: Admin
- 内容团队: 无需访问

### 内容仓库
- 技术团队: Admin
- 内容团队: Write
- 外部贡献者: PR only

## 自定义同步频率

编辑 `.workflow/deploy.yml`:
```yaml
schedule:
  - cron: '*/10 * * * *'  # 每 10 分钟
  - cron: '0 * * * *'     # 每小时
  - cron: '0 0 * * *'     # 每天
```

## 支持的 Markdown 功能

- ✅ 标题、段落、列表
- ✅ 代码块、行内代码
- ✅ 表格
- ✅ 链接、图片
- ✅ 引用
- ✅ 脚注
- ✅ 任务列表
- ✅ Frontmatter (YAML)
- ✅ 文章加密

## 获取帮助

- GitHub Issues: https://github.com/soft98-top/mblog/issues
- 文档: https://github.com/soft98-top/mblog/tree/main/docs
