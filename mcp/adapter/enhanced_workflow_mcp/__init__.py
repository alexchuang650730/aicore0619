"""
Enhanced Workflow MCP Package
增强型工作流MCP包

提供增强的工作流编排、动态生成、并行执行和智能依赖管理功能
"""

from .enhanced_workflow_engine import EnhancedWorkflowEngine
from .dynamic_workflow_generator import DynamicWorkflowGenerator
from .parallel_execution_scheduler import ParallelExecutionScheduler
from .intelligent_dependency_manager import IntelligentDependencyManager
from .workflow_state_manager import WorkflowStateManager

__all__ = [
    "EnhancedWorkflowEngine",
    "DynamicWorkflowGenerator", 
    "ParallelExecutionScheduler",
    "IntelligentDependencyManager",
    "WorkflowStateManager"
]

__version__ = "1.0.0"