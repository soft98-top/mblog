# 部署问题排查指南

## 问题：GitHub Actions 成功但步骤被跳过

### 症状

GitHub Actions 显示 "succeeded"，但关键步骤被跳过（显示灰色圆圈）：
- ⊘ Setup Python
- ⊘ Install dependencies
- ⊘ Generate static site
- ⊘ Deploy to GitHub Pages

### 原因分析

#### 双仓库模式

如果你使用的是双仓库模式，workflow 会检查内容仓库（`md/` 目录）是否有更新：

```yaml
- name: Check for content changes
  id: changes
  run: |
    if [[ -n $(git status -s md) ]]; then
      echo "changed=true" >> $GITHUB_OUTPUT
    else
      echo "changed=false" >> $GITHUB_OUTPUT
    fi
```

**如果没有检测到内容变化，后续步骤会被跳过**，这是为了：
- 节省 GitHub Actions 运行时间
- 避免不必要的构建
- 减少资源消耗

### 解决方案

#### 方案 1：手动触发强制构建（推荐）

1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Deploy Blog" workflow
4. 点击 "Run workflow" 按钮
5. 选择分支（通常是 main）
6. 点击 "Run workflow"

**最新版本的 workflow 会在手动触发或 push 时强制构建**，不再检查内容变化。

#### 方案 2：更新内容仓库

在内容仓库中添加或修改文章：

```bash
cd content-repo
echo "test" >> test.md
git add .
git commit -m "Trigger deployment"
git push
```

内容仓库更新后，博客仓库的定时任务会检测到变化并自动部署。

#### 方案 3：修改主仓库触发部署

在博客仓库中做任何修改：

```bash
cd blog-repo
# 修改配置或主题
echo "# Update" >> README.md
git add .
git commit -m "Trigger deployment"
git push
```

Push 到 main 分支会触发 workflow，并强制构建。

#### 方案 4：升级到最新 workflow（推荐）

如果你的项目是旧版本创建的，升级 workflow 文件：

```bash
# 备份现有 workflow
cp .github/workflows/deploy.yml .github/workflows/deploy.yml.backup

# 使用 mblog 重新生成（需要手动复制）
# 或者手动更新 workflow 文件
```

在 "Check for content changes" 步骤中添加强制构建逻辑：

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

### 验证部署

#### 1. 检查 Actions 日志

在 GitHub Actions 页面查看详细日志：
- 展开 "Check for content changes" 步骤
- 查看输出信息
- 确认 `changed=true` 或 `changed=false`

#### 2. 检查 GitHub Pages 设置

1. 进入仓库 Settings
2. 点击 Pages
3. 确认：
   - Source: GitHub Actions（推荐）或 Deploy from a branch
   - Branch: gh-pages（如果使用分支部署）

#### 3. 访问网站

部署成功后，访问：
- `https://your-username.github.io/your-repo/`
- 或你的自定义域名

### 常见问题

#### Q: 为什么定时任务不触发构建？

A: 定时任务（cron）只在有内容变化时才构建。如果内容仓库没有更新，不会触发构建。

#### Q: 如何禁用内容变化检查？

A: 修改 workflow，移除 `if: steps.changes.outputs.changed == 'true'` 条件：

```yaml
- name: Setup Python
  # 移除这行: if: steps.changes.outputs.changed == 'true'
  uses: actions/setup-python@v5
  with:
    python-version: '3.9'
```

**注意**：这会导致每次定时任务都构建，消耗更多资源。

#### Q: 单仓库模式会有这个问题吗？

A: 不会。单仓库模式的 workflow 没有内容变化检查，每次 push 都会构建。

#### Q: 如何查看是否使用双仓库模式？

A: 检查项目根目录：
- 有 `.gitmodules` 文件 → 双仓库模式
- 有 `md/` 目录且包含文章 → 单仓库模式

#### Q: 部署成功但网站没有更新？

A: 可能的原因：
1. 浏览器缓存 - 强制刷新（Ctrl+F5）
2. GitHub Pages 缓存 - 等待几分钟
3. CDN 缓存 - 如果使用了 CDN，清除缓存

### 调试技巧

#### 1. 查看 workflow 运行历史

```bash
# 在 GitHub 页面
Actions → Deploy Blog → 查看所有运行记录
```

#### 2. 查看详细日志

点击任何一次运行 → 展开每个步骤 → 查看输出

#### 3. 本地测试

```bash
# 克隆内容仓库
git clone <content-repo-url> md

# 生成静态文件
python gen.py

# 检查输出
ls -la public/
```

#### 4. 检查 Secrets 配置

对于双仓库模式，确认已配置：
- `CONTENT_REPO_KEY`: SSH 私钥
- `CONTENT_REPO_URL`: 内容仓库 SSH URL
- `GITHUB_TOKEN`: 自动提供，无需配置

### 最佳实践

#### 1. 开发阶段

使用手动触发进行测试：
```bash
# 修改代码
git add .
git commit -m "Update"
git push

# 然后在 GitHub 手动触发 workflow
```

#### 2. 生产环境

依赖自动触发：
- 单仓库：push 到 main 自动部署
- 双仓库：内容更新自动部署

#### 3. 监控部署

设置 GitHub 通知：
- Settings → Notifications
- 勾选 "Actions" 相关通知

#### 4. 定期检查

每周检查一次：
- Actions 运行状态
- 网站访问情况
- 日志中的警告或错误

### 相关文档

- [独立内容仓库文档](separate-content-repo.md)
- [部署文档](deployment.md)
- [双仓库实战示例](dual-repo-example.md)
- [快速参考](quick-reference.md)

### 获取帮助

如果问题仍未解决：

1. 查看 [GitHub Issues](https://github.com/soft98-top/mblog/issues)
2. 提交新的 Issue，包含：
   - 错误截图
   - Actions 日志
   - 项目配置（隐藏敏感信息）
   - 使用的 mblog 版本
