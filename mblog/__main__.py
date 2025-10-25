"""
mblog 命令行入口点

允许通过 `python -m mblog` 运行工具
"""

import sys
from mblog.cli import main

if __name__ == "__main__":
    sys.exit(main())
