#!/bin/bash
# mblog 升级功能演示脚本

set -e

echo "=========================================="
echo "mblog 升级功能演示"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 显示版本
echo -e "${BLUE}1. 查看 mblog 版本${NC}"
mblog --version
echo ""

# 2. 显示帮助
echo -e "${BLUE}2. 查看升级命令帮助${NC}"
mblog upgrade --help
echo ""

# 3. 显示主题命令帮助
echo -e "${BLUE}3. 查看主题管理命令帮助${NC}"
mblog theme --help
echo ""

# 4. 创建测试博客（如果不存在）
if [ ! -d "demo-blog" ]; then
    echo -e "${BLUE}4. 创建测试博客${NC}"
    echo "1" | mblog new demo-blog
    echo ""
fi

# 5. 升级运行时
echo -e "${BLUE}5. 升级博客运行时${NC}"
echo -e "${YELLOW}提示：在实际使用中，系统会询问确认${NC}"
mblog upgrade -p demo-blog --force
echo ""

# 6. 更新主题
echo -e "${BLUE}6. 更新博客主题${NC}"
mblog theme update -p demo-blog --force
echo ""

# 7. 查看备份
echo -e "${BLUE}7. 查看创建的备份${NC}"
ls -lh demo-blog/ | grep backup
echo ""

# 8. 测试生成
echo -e "${BLUE}8. 测试博客生成${NC}"
cd demo-blog
python gen.py
cd ..
echo ""

# 9. 清理
echo -e "${BLUE}9. 清理演示环境${NC}"
echo -e "${YELLOW}是否删除演示博客？[y/N]${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    rm -rf demo-blog
    echo -e "${GREEN}✓ 演示环境已清理${NC}"
else
    echo -e "${GREEN}✓ 演示博客保留在 demo-blog/ 目录${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}演示完成！${NC}"
echo "=========================================="
echo ""
echo "更多信息请查看："
echo "  - 升级指南: docs/upgrade-guide.md"
echo "  - 快速参考: docs/quick-reference.md"
echo "  - 功能总结: docs/UPGRADE_FEATURE_SUMMARY.md"
