# GitHub Actions 目录结构修复

## 问题描述

之前的实现使用了 `.workflow/` 目录来存放 GitHub Actions 配置文件，但这是不正确的。GitHub Actions 要求配置文件必须放在 `.github/workflows/` 目录中才能被识别和执行。

## 修复内容

### 1. 目录结构变更

**之前（错误）：**
```
my-blog/
├── .workflow/
│   └── deploy.yml
├── md/
├── theme/
└── ...
```

**现在（正确）：**
```
my-blog/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── md/
├── theme/
└── ...
```

### 2. 代码修改

#### mblog/initializer.py

1. **目录创建**
   ```python
   # 之前
   (self.project_path / ".workflow").mkdir(exist_ok=True)
   
   # 现在
   (self.project_path / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
   ```

2. **Workflow 文件路径**
   ```python
   # 之前
   target_path = self.project_path / ".workflow" / "deploy.yml"
   
   # 现在
   target_path = self.project_path / ".github" / "workflows" / "deploy.yml"
   ```

3. **成功消息输出**
   - 更新了项目结构显示，正确显示 `.github/workflows/` 目录

#### 测试文件更新

- `tests/test_initializer.py`: 更新了所有目录路径断言
- `tests/test_integration.py`: 更新了 workflow 文件路径检查

#### 文档更新

更新了以下文档中的所有引用：
- `README.md`
- `docs/quick-reference.md`
- `docs/dual-repo-example.md`
- `docs/deployment.md`
- `docs/DUAL_REPO_SUMMARY.md`
- `docs/separate-content-repo.md`

### 3. 验证

创建新项目后验证：

```bash
# 创建测试项目
echo "1" | mblog new test-blog

# 验证目录结构
ls -la test-blog/.github/workflows/
# 输出：deploy.yml

# 验证文件内容
cat test-blog/.github/workflows/deploy.yml
# 输出：正确的 GitHub Actions workflow 配置
```

## GitHub Actions 工作原理

### 目录要求

GitHub Actions 会自动扫描仓库中的 `.github/workflows/` 目录，查找 YAML 格式的 workflow 文件。

**必须满足：**
1. 目录路径必须是 `.github/workflows/`（大小写敏感）
2. 文件必须是 `.yml` 或 `.yaml` 扩展名
3. 文件必须包含有效的 workflow 配置

### Workflow 触发

当满足以下条件时，workflow 会被触发：

1. **Push 事件**
   ```yaml
   on:
     push:
       branches: [ main ]
   ```

2. **手动触发**
   ```yaml
   on:
     workflow_dispatch:
   ```

3. **定时触发**（双仓库模式）
   ```yaml
   on:
     schedule:
       - cron: '*/30 * * * *'
   ```

### 验证 Workflow 是否生效

推送代码到 GitHub 后：

1. 进入仓库页面
2. 点击 "Actions" 标签
3. 应该能看到 "Deploy Blog" workflow
4. 如果看不到，检查：
   - 目录路径是否正确（`.github/workflows/`）
   - 文件名是否正确（`deploy.yml`）
   - YAML 语法是否正确

## 常见问题

### Q: 为什么之前使用 `.workflow/`？

A: 这可能是一个误解或早期的设计错误。GitHub Actions 从一开始就要求使用 `.github/workflows/` 目录。

### Q: 旧项目如何迁移？

A: 如果你有使用旧版本 mblog 创建的项目，需要手动迁移：

```bash
cd your-blog
mkdir -p .github/workflows
mv .workflow/deploy.yml .github/workflows/
rm -rf .workflow
git add .github
git commit -m "Fix: Move workflow to correct directory"
git push
```

### Q: 如何验证 workflow 配置正确？

A: 使用 GitHub 的 workflow 语法检查：

1. 在本地安装 `act`（GitHub Actions 本地运行工具）
   ```bash
   brew install act  # macOS
   ```

2. 验证 workflow
   ```bash
   cd your-blog
   act -l  # 列出所有 workflow
   ```

3. 或者直接推送到 GitHub，在 Actions 页面查看

### Q: Workflow 文件可以有其他名字吗？

A: 可以。`.github/workflows/` 目录下的所有 `.yml` 和 `.yaml` 文件都会被识别。例如：
- `deploy.yml`
- `test.yml`
- `build-and-deploy.yaml`

### Q: 可以有多个 workflow 文件吗？

A: 可以。你可以创建多个 workflow 文件来处理不同的任务：

```
.github/
└── workflows/
    ├── deploy.yml      # 部署
    ├── test.yml        # 测试
    └── lint.yml        # 代码检查
```

## 影响范围

### 新项目

使用修复后的版本创建的项目会自动使用正确的目录结构，GitHub Actions 会正常工作。

### 现有项目

如果你已经使用旧版本创建了项目：

1. **不影响本地生成**：`python gen.py` 仍然正常工作
2. **影响自动部署**：GitHub Actions 不会触发，需要手动迁移

### 迁移步骤

```bash
# 1. 进入项目目录
cd your-blog

# 2. 创建正确的目录
mkdir -p .github/workflows

# 3. 移动 workflow 文件
mv .workflow/deploy.yml .github/workflows/

# 4. 删除旧目录
rm -rf .workflow

# 5. 提交更改
git add .github
git rm -r .workflow
git commit -m "Fix: Move workflow to .github/workflows/"
git push

# 6. 验证
# 访问 GitHub 仓库的 Actions 页面，应该能看到 workflow
```

## 测试结果

所有相关测试已通过：

```bash
pytest tests/test_initializer.py -v
# 40 passed

pytest tests/test_integration.py -v -k "not test_cli"
# 8 passed, 2 skipped
```

## 相关资源

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [Workflow 语法参考](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Pages 部署](https://docs.github.com/en/pages/getting-started-with-github-pages)

## 总结

这次修复确保了：

✅ 新创建的项目使用正确的 `.github/workflows/` 目录  
✅ GitHub Actions 能够正确识别和执行 workflow  
✅ 自动部署功能正常工作  
✅ 所有文档和测试已更新  
✅ 向后兼容（旧项目可以手动迁移）

如果你在使用过程中遇到 GitHub Actions 不工作的问题，请首先检查目录结构是否正确。
