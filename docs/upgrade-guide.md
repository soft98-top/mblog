# mblog 升级指南

本指南介绍如何升级现有的 mblog 博客项目。

## 为什么需要升级？

mblog 会不断改进和修复 bug。升级可以让你的博客项目获得：

- 最新的功能特性
- 性能优化
- Bug 修复
- 安全更新

## 升级运行时

运行时文件位于博客项目的 `_mblog/` 目录中，包含博客生成的核心逻辑。

### 基本用法

在博客目录中运行：

```bash
cd my-blog
mblog upgrade
```

系统会提示确认：

```
正在升级博客运行时...
项目路径: /path/to/my-blog

⚠️  此操作将更新 _mblog/ 目录中的所有运行时文件
   建议先备份或提交当前更改到 Git

是否继续？[y/N]:
```

输入 `y` 确认后，升级将开始。

### 指定项目路径

如果不在博客目录中，可以指定路径：

```bash
mblog upgrade -p ~/projects/my-blog
```

### 强制升级

跳过确认提示，直接升级：

```bash
mblog upgrade --force
```

### 升级过程

1. 自动创建备份：`_mblog.backup_YYYYMMDD_HHMMSS`
2. 更新所有运行时文件
3. 显示更新的文件列表

示例输出：

```
✓ 已创建备份: _mblog.backup_20251026_124244
✓ 已更新 6 个运行时文件
  - config.py
  - theme.py
  - renderer.py
  - __init__.py
  - generator.py
  - markdown_processor.py

✓ 运行时升级成功！

下一步操作:
  1. 测试生成功能: python gen.py
  2. 如有问题，可从备份恢复
```

## 管理主题

主题文件位于博客项目的 `theme/` 目录中，包含模板和样式文件。

### 更新主题

更新主题文件到最新版本（保留自定义文件）：

```bash
cd my-blog
mblog theme update
```

这会：
- 更新默认主题文件
- 保留你添加的自定义文件
- 创建备份

### 重置主题

完全重置为默认主题（删除所有自定义修改）：

```bash
mblog theme reset
```

⚠️ **警告**：此操作会删除所有自定义修改！

系统会提示确认：

```
正在重置主题...
项目路径: /path/to/my-blog

⚠️  此操作将重置 theme/ 目录为默认主题
   所有自定义修改将丢失
   建议先备份或提交当前更改到 Git

是否继续？[y/N]:
```

### 强制操作

跳过确认提示：

```bash
mblog theme update --force
mblog theme reset --force
```

### 主题操作过程

示例输出：

```
✓ 已创建备份: theme.backup_20251026_124250
✓ 已更新 10 个主题文件

✓ 主题更新成功！

下一步操作:
  1. 检查 theme/ 目录中的文件
  2. 重新生成博客: python gen.py
```

## 备份管理

### 自动备份

所有升级操作都会自动创建带时间戳的备份：

- 运行时备份：`_mblog.backup_YYYYMMDD_HHMMSS/`
- 主题备份：`theme.backup_YYYYMMDD_HHMMSS/`

### 恢复备份

如果升级后出现问题，可以手动恢复：

```bash
# 恢复运行时
rm -rf _mblog
mv _mblog.backup_20251026_124244 _mblog

# 恢复主题
rm -rf theme
mv theme.backup_20251026_124250 theme
```

### 清理旧备份

定期清理不需要的备份：

```bash
# 删除所有备份
rm -rf _mblog.backup_* theme.backup_*

# 只保留最新的备份
ls -t _mblog.backup_* | tail -n +2 | xargs rm -rf
ls -t theme.backup_* | tail -n +2 | xargs rm -rf
```

## 升级最佳实践

### 1. 升级前

- ✅ 提交所有更改到 Git
- ✅ 确保博客可以正常生成
- ✅ 记录当前的自定义修改

```bash
git add .
git commit -m "Before upgrade"
git push
```

### 2. 升级时

- ✅ 先在测试环境升级
- ✅ 查看升级日志
- ✅ 检查备份是否创建

### 3. 升级后

- ✅ 测试生成功能
- ✅ 检查生成的页面
- ✅ 验证自定义功能

```bash
# 测试生成
python gen.py

# 本地预览
cd public
python -m http.server 8000
```

### 4. 验证升级

检查关键功能：

- [ ] 首页正常显示
- [ ] 文章页面正常
- [ ] 标签页面正常
- [ ] 归档页面正常
- [ ] RSS 订阅正常
- [ ] 图片显示正常
- [ ] 加密文章功能正常（如果使用）

### 5. 提交更改

确认无误后提交：

```bash
git add .
git commit -m "Upgrade mblog runtime and theme"
git push
```

## 常见问题

### Q: 升级会影响我的文章吗？

A: 不会。升级只更新 `_mblog/` 和 `theme/` 目录，不会修改 `md/` 目录中的文章。

### Q: 升级会影响我的配置吗？

A: 不会。`config.json` 不会被修改。

### Q: 我修改了运行时代码，升级会覆盖吗？

A: 是的。如果你修改了 `_mblog/` 中的文件，升级会覆盖这些修改。建议：
- 将自定义逻辑放在单独的文件中
- 或者在升级前备份你的修改
- 升级后重新应用修改

### Q: 我自定义了主题，如何安全升级？

A: 使用 `mblog theme update` 而不是 `reset`。`update` 只更新默认文件，不会删除你添加的自定义文件。

### Q: 升级失败了怎么办？

A: 从自动创建的备份恢复：

```bash
rm -rf _mblog
mv _mblog.backup_YYYYMMDD_HHMMSS _mblog
```

### Q: 如何查看 mblog 版本？

A: 运行：

```bash
mblog --version
```

### Q: 如何知道是否需要升级？

A: 检查 [CHANGELOG](../CHANGELOG.md) 查看最新版本的更新内容。

### Q: 可以降级吗？

A: 可以从备份恢复到之前的版本，但不建议降级。如果遇到问题，请报告 bug。

## 版本兼容性

### 配置文件

mblog 保持配置文件的向后兼容性。旧版本的 `config.json` 可以在新版本中使用。

### 主题文件

主题结构保持稳定。如果有重大变更，会在 CHANGELOG 中说明。

### 运行时 API

运行时的公共 API 保持稳定。内部实现可能会改变，但不影响正常使用。

## 自动化升级

### 使用脚本

创建升级脚本 `upgrade.sh`：

```bash
#!/bin/bash
set -e

echo "开始升级 mblog..."

# 提交当前更改
git add .
git commit -m "Before upgrade" || true

# 升级运行时
mblog upgrade --force

# 测试生成
python gen.py

# 提交升级
git add .
git commit -m "Upgrade mblog"

echo "升级完成！"
```

使用：

```bash
chmod +x upgrade.sh
./upgrade.sh
```

### CI/CD 集成

在 GitHub Actions 中自动检查更新：

```yaml
name: Check mblog updates

on:
  schedule:
    - cron: '0 0 * * 0'  # 每周检查
  workflow_dispatch:

jobs:
  check-update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install mblog
        run: pip install mblog
      
      - name: Check version
        run: mblog --version
      
      - name: Upgrade
        run: mblog upgrade --force
      
      - name: Test generation
        run: python gen.py
      
      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: Upgrade mblog
          title: 'chore: Upgrade mblog runtime'
          body: 'Automated mblog upgrade'
```

## 获取帮助

如果升级过程中遇到问题：

1. 查看 [文档](../README.md)
2. 检查 [CHANGELOG](../CHANGELOG.md)
3. 提交 [Issue](https://github.com/soft98-top/mblog/issues)

## 相关文档

- [配置文档](configuration.md)
- [主题开发](theme-development.md)
- [快速参考](quick-reference.md)
