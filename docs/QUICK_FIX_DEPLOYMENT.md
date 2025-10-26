# 快速修复：GitHub Actions 步骤被跳过

## 问题

GitHub Actions 显示成功，但关键步骤被跳过（灰色圆圈）：
- ⊘ Setup Python
- ⊘ Install dependencies  
- ⊘ Generate static site
- ⊘ Deploy to GitHub Pages

## 快速解决方案

### 方法 1：手动触发（最快）⚡

1. 打开你的 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Deploy Blog** workflow
4. 点击右上角 **Run workflow** 按钮
5. 选择 **main** 分支
6. 点击绿色的 **Run workflow** 按钮

✅ 这次运行应该会执行所有步骤并成功部署！

### 方法 2：使用更新脚本（推荐）🔧

如果你想永久修复这个问题：

```bash
# 在 mblog 项目目录中
cd /path/to/mblog

# 运行更新脚本
./scripts/update_workflow.sh /path/to/your-blog

# 提交更改
cd /path/to/your-blog
git add .github/workflows/deploy.yml  # 或 .workflow/deploy.yml
git commit -m "Fix: Update workflow to force build on push/manual trigger"
git push
```

### 方法 3：手动更新 workflow 文件 📝

编辑你的博客项目中的 `.github/workflows/deploy.yml`（或 `.workflow/deploy.yml`）：

找到 "Check for content changes" 步骤，替换为：

```yaml
- name: Check for content changes
  id: changes
  run: |
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"
    # 如果是手动触发或 push 事件，强制构建
    if [[ "${{ github.event_name }}" == "workflow_dispatch" ]] || [[ "${{ github.event_name }}" == "push" ]]; then
      echo "changed=true" >> $GITHUB_OUTPUT
      echo "Force build triggered by ${{ github.event_name }}"
    elif [[ -n $(git status -s md) ]]; then
      echo "changed=true" >> $GITHUB_OUTPUT
      echo "Content repository has updates"
    else
      echo "changed=false" >> $GITHUB_OUTPUT
      echo "No content changes detected"
    fi
```

然后提交并推送：

```bash
git add .github/workflows/deploy.yml
git commit -m "Fix workflow"
git push
```

## 验证修复

1. Push 后，GitHub Actions 应该自动运行
2. 所有步骤应该显示绿色勾号 ✓
3. 访问你的网站确认部署成功

## 为什么会发生这个问题？

双仓库模式的 workflow 会检查内容仓库是否有更新。如果没有检测到变化，就跳过构建步骤以节省资源。

但这导致：
- 首次部署时没有内容变化，步骤被跳过
- 修改配置或主题时，步骤也被跳过
- 手动触发时，仍然检查内容变化

## 修复后的行为

✅ **Push 到 main 分支** → 强制构建和部署  
✅ **手动触发** → 强制构建和部署  
✅ **定时任务** → 只在有内容变化时构建（节省资源）

## 需要帮助？

查看详细文档：
- [部署问题排查指南](troubleshooting-deployment.md)
- [双仓库模式文档](separate-content-repo.md)

或提交 Issue：
- [GitHub Issues](https://github.com/soft98-top/mblog/issues)
