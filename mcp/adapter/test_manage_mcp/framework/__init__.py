"""
Framework模块初始化
包含测试框架的核心组件
"""

from .test_framework_generator import MCPTestFrameworkGenerator
from .test_executor import MCPTestExecutor
from .test_framework_fixer import MCPTestFrameworkFixer

__all__ = [
    "MCPTestFrameworkGenerator",
    "MCPTestExecutor",
    "MCPTestFrameworkFixer"
]

