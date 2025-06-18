"""
Test Management MCP 模块初始化
PowerAutomation测试框架管理器，提供统一的测试生成、执行和管理功能
"""

__version__ = "1.0.0"
__author__ = "PowerAutomation Team"
__description__ = "PowerAutomation测试框架管理器"

from .test_manage_mcp import TestManageMCP
from .framework.test_framework_generator import MCPTestFrameworkGenerator
from .framework.test_executor import MCPTestExecutor
from .framework.test_framework_fixer import MCPTestFrameworkFixer

__all__ = [
    "TestManageMCP",
    "MCPTestFrameworkGenerator",
    "MCPTestExecutor", 
    "MCPTestFrameworkFixer"
]

