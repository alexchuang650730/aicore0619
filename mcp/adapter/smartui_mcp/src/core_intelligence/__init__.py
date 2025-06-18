"""
SmartUI MCP 智能感知与决策层初始化文件

导出所有核心智能组件，提供统一的导入接口。
"""

from .user_analyzer import SmartUIUserAnalyzer
from .decision_engine import SmartUIDecisionEngine
from .api_state_manager import SmartUIApiStateManager
from .ui_generator import SmartUIGenerator
from .mcp_integration import SmartUIMCPIntegration

__all__ = [
    "SmartUIUserAnalyzer",
    "SmartUIDecisionEngine", 
    "SmartUIApiStateManager",
    "SmartUIGenerator",
    "SmartUIMCPIntegration"
]

# 版本信息
__version__ = "1.0.0"
__author__ = "SmartUI MCP Team"
__description__ = "SmartUI MCP 智能感知与决策层组件"

