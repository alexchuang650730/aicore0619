"""
PowerAutomation 测试管理工作流包初始化

导出工作流的主要组件和接口
符合PowerAutomation目录规范v2.0

作者: PowerAutomation Team
版本: 2.0.0
日期: 2025-06-18
"""

from .test_manager import (
    TestWorkflowManager, 
    AIStrategyGenerator,
    WorkflowEngine,
    AnalyticsEngine,
    create_workflow_manager
)
from .workflow_engine import WorkflowEngine as CoreWorkflowEngine

# 版本信息
__version__ = "2.0.0"
__author__ = "PowerAutomation Team"
__description__ = "PowerAutomation测试管理工作流 - 智能测试编排和策略管理"

# 导出的主要组件
__all__ = [
    # 核心组件
    "TestWorkflowManager",
    "AIStrategyGenerator", 
    "WorkflowEngine",
    "CoreWorkflowEngine",
    "AnalyticsEngine",
    
    # 工厂函数
    "create_workflow_manager",
    
    # 版本信息
    "__version__",
    "__author__",
    "__description__"
]

# 工作流元数据
WORKFLOW_METADATA = {
    "name": "test_management_workflow_mcp",
    "version": __version__,
    "type": "workflow",
    "layer": "workflow",
    "category": "test_management",
    "capabilities": [
        "ai_strategy_generation",
        "workflow_orchestration",
        "multi_adapter_coordination",
        "intelligent_optimization",
        "predictive_analytics",
        "complex_flow_control",
        "real_time_monitoring"
    ],
    "dependencies": [
        "asyncio",
        "yaml",
        "logging",
        "uuid"
    ],
    "supported_adapters": [
        "test_management_mcp",
        "smartui_mcp",
        "performance_test_mcp"
    ],
    "ai_features": [
        "strategy_generation",
        "adaptive_optimization",
        "predictive_analysis",
        "intelligent_scheduling"
    ]
}

def get_workflow_metadata():
    """获取工作流元数据"""
    return WORKFLOW_METADATA.copy()

def get_version():
    """获取工作流版本"""
    return __version__

def get_capabilities():
    """获取工作流能力列表"""
    return WORKFLOW_METADATA["capabilities"].copy()

def get_supported_adapters():
    """获取支持的适配器列表"""
    return WORKFLOW_METADATA["supported_adapters"].copy()

