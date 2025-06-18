#!/usr/bin/env python3
"""
Local Model MCP Adapter 启动脚本
符合PowerAutomation标准的MCP适配器启动入口
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.adapter.local_model_mcp.cli import main

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

