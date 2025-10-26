# mblog 示例

本目录包含 mblog 的使用示例和演示脚本。

## 升级功能演示

### upgrade_demo.sh

演示 mblog 的升级和主题管理功能。

**运行演示：**

```bash
cd examples
./upgrade_demo.sh
```

**演示内容：**

1. 显示 mblog 版本
2. 显示升级命令帮助
3. 显示主题管理命令帮助
4. 创建测试博客
5. 升级博客运行时
6. 更新博客主题
7. 查看创建的备份
8. 测试博客生成
9. 清理演示环境（可选）

**预期输出：**

```
==========================================
mblog 升级功能演示
==========================================

1. 查看 mblog 版本
mblog 0.1.0

2. 查看升级命令帮助
usage: mblog upgrade [-h] [-p PROJECT_PATH] [-f]
...

3. 查看主题管理命令帮助
usage: mblog theme [-h] [-p PROJECT_PATH] [-f] {update,reset}
...

4. 创建测试博客
✓ 项目 'demo-blog' 创建成功！
...

5. 升级博客运行时
✓ 已创建备份: _mblog.backup_20251026_124244
✓ 已更新 6 个运行时文件
...

6. 更新博客主题
✓ 已创建备份: theme.backup_20251026_124250
✓ 已更新 10 个主题文件
...

7. 查看创建的备份
drwxr-xr-x  9 user  staff  288 Oct 26 12:42 _mblog.backup_20251026_124244
drwxr-xr-x  5 user  staff  160 Oct 26 12:42 theme.backup_20251026_124250

8. 测试博客生成
开始生成静态博客文件...
✓ 成功生成 1 篇文章
...

9. 清理演示环境
是否删除演示博客？[y/N]
```

## 手动测试

### 测试升级功能

```bash
# 创建测试博客
mblog new test-blog

# 进入博客目录
cd test-blog

# 修改一个运行时文件（模拟旧版本）
echo "# Modified" >> _mblog/generator.py

# 升级运行时
mblog upgrade

# 验证文件已恢复
cat _mblog/generator.py | grep "Modified"  # 应该找不到

# 检查备份
ls -la | grep backup
```

### 测试主题管理

```bash
# 在博客目录中
cd test-blog

# 添加自定义文件
echo "Custom content" > theme/custom.txt

# 更新主题（应该保留自定义文件）
mblog theme update

# 验证自定义文件仍然存在
cat theme/custom.txt

# 重置主题（会删除自定义文件）
mblog theme reset

# 验证自定义文件已被删除
ls theme/custom.txt  # 应该报错
```

### 测试备份恢复

```bash
# 升级后出现问题，从备份恢复
cd test-blog

# 查看备份
ls -la | grep backup

# 恢复运行时
rm -rf _mblog
mv _mblog.backup_20251026_124244 _mblog

# 恢复主题
rm -rf theme
mv theme.backup_20251026_124250 theme

# 测试生成
python gen.py
```

## 自动化测试

运行完整的测试套件：

```bash
# 运行所有测试
pytest tests/test_upgrader.py -v

# 运行特定测试
pytest tests/test_upgrader.py::test_upgrade_runtime -v

# 查看覆盖率
pytest tests/test_upgrader.py --cov=mblog.initializer --cov-report=html
```

## 常见问题

### Q: 演示脚本失败了怎么办？

A: 确保：
1. 已安装 mblog：`pip install -e .`
2. 在项目根目录运行：`cd /path/to/mblog`
3. 有执行权限：`chmod +x examples/upgrade_demo.sh`

### Q: 如何清理测试环境？

A: 删除测试博客：
```bash
rm -rf demo-blog test-blog
```

### Q: 如何查看详细日志？

A: 在命令中添加 `-v` 或 `--verbose` 参数（如果支持）。

## 相关文档

- [升级指南](../docs/upgrade-guide.md)
- [快速参考](../docs/quick-reference.md)
- [功能总结](../docs/UPGRADE_FEATURE_SUMMARY.md)
- [主 README](../README.md)
