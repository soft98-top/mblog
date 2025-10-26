# 双仓库模式功能总结

## 实现概述

mblog 现在支持双仓库模式，允许将博客内容与配置分离到不同的 Git 仓库中。

## 核心功能

### 1. 交互式初始化
- 运行 `mblog new <project>` 时提供模式选择
- 用户可选择单仓库或双仓库模式
- 自动验证内容仓库 URL 格式

### 2. 自动配置生成
- 生成 `.gitmodules` 文件配置 submodule
- 生成专用的 GitHub Actions workflow
- 生成详细的 `SETUP_GUIDE.md` 配置指南
- 自动初始化 Git 仓库和 `.gitignore`

### 3. 安全的访问机制
- 使用 SSH Deploy Key 而非 PAT
- 最小权限原则（只读访问）
- 密钥通过 GitHub Secrets 安全存储

### 4. 自动同步部署
- 定时检查内容仓库更新（默认 30 分钟）
- 支持手动触发部署
- 只在内容变化时重新生成和部署

## 技术实现

### 修改的文件

1. **mblog/initializer.py**
   - 添加 `use_separate_content_repo` 和 `content_repo_url` 参数
   - 新增 `_create_gitmodules_file()` 方法
   - 新增 `_create_separate_repo_workflow()` 方法
   - 新增 `_create_setup_guide()` 方法
   - 新增 `_init_git_repo()` 方法
   - 修改 `create_project()` 根据模式创建不同内容
   - 修改 `print_success_message()` 显示不同的提示信息

2. **mblog/cli.py**
   - 修改 `handle_new()` 添加交互式模式选择
   - 添加内容仓库 URL 输入和验证
   - 传递参数给 `ProjectInitializer`

3. **tests/test_initializer.py**
   - 新增 `TestSeparateContentRepo` 测试类
   - 11 个新测试用例覆盖双仓库功能

### 新增的文档

1. **docs/separate-content-repo.md** - 完整的功能文档
2. **docs/dual-repo-example.md** - 实战示例
3. **SETUP_GUIDE.md** - 自动生成的配置指南（在项目中）

### 生成的文件结构

**双仓库模式：**
```
project/
├── .git/
├── .gitignore          # 包含 md/ 目录
├── .gitmodules         # submodule 配置
├── .workflow/
│   └── deploy.yml      # 支持内容仓库同步
├── SETUP_GUIDE.md      # 配置指南
├── md/                 # 空目录（由 submodule 管理）
├── theme/
├── _mblog/
├── gen.py
├── config.json
└── requirements.txt
```

**单仓库模式：**
```
project/
├── .git/
├── .gitignore
├── .workflow/
│   └── deploy.yml      # 标准部署配置
├── md/
│   └── welcome.md      # 示例文章
├── theme/
├── _mblog/
├── gen.py
├── config.json
└── requirements.txt
```

## GitHub Actions Workflow

双仓库模式的 workflow 特性：

```yaml
on:
  push:
    branches: [ main ]
  schedule:
    - cron: '*/30 * * * *'  # 定时检查
  workflow_dispatch:         # 手动触发

steps:
  - Setup SSH for content repo
  - Clone/Update content repository
  - Check for content changes
  - Generate static site (only if changed)
  - Deploy to GitHub Pages
```

## 配置步骤

用户需要完成的配置：

1. 生成 SSH Deploy Key
2. 在内容仓库添加公钥（Deploy Key）
3. 在博客仓库添加两个 Secrets：
   - `CONTENT_REPO_KEY` - 私钥
   - `CONTENT_REPO_URL` - 内容仓库 URL
4. 配置 GitHub Pages
5. 推送代码

## 使用场景

### 适合双仓库模式
- 团队协作博客
- 需要内容审核流程
- 权限分离需求
- 多博客共享内容
- 内容独立备份

### 适合单仓库模式
- 个人博客
- 简单场景
- 快速开始

## 测试覆盖

- ✅ 双仓库项目创建
- ✅ .gitmodules 文件生成
- ✅ SETUP_GUIDE.md 生成
- ✅ 专用 workflow 生成
- ✅ 不创建示例文章
- ✅ .gitignore 包含 md/
- ✅ 单仓库模式不受影响
- ✅ Git 仓库自动初始化
- ✅ .gitignore 自动创建

所有 40 个测试用例通过。

## 向后兼容性

- ✅ 默认行为不变（单仓库模式）
- ✅ 现有项目不受影响
- ✅ API 向后兼容（新参数为可选）

## 安全性

- ✅ 使用 Deploy Key 而非 PAT
- ✅ 最小权限（只读访问）
- ✅ 密钥通过 GitHub Secrets 存储
- ✅ 自动生成的 .gitignore 排除密钥文件

## 文档完整性

- ✅ README.md 更新
- ✅ CHANGELOG.md 更新
- ✅ 完整的功能文档
- ✅ 实战示例
- ✅ 自动生成的配置指南

## 未来改进方向

1. **Webhook 支持**：实时触发而非定时检查
2. **多内容仓库**：支持从多个仓库拉取内容
3. **GUI 配置工具**：简化 Deploy Key 配置流程
4. **内容预览**：PR 中预览文章效果
5. **增量构建**：只重新生成变化的文章

## 总结

双仓库模式为 mblog 带来了：
- 更灵活的团队协作能力
- 更好的权限管理
- 自动化的部署流程
- 内容与配置的清晰分离

同时保持了：
- 简单的使用体验
- 向后兼容性
- 安全性
- 完整的文档支持
