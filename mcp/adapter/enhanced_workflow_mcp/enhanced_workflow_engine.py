#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Workflow Engine
增强型工作流引擎

提供增强的工作流编排、执行和优化功能
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import sys
import os

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))

# 导入BaseMCP
try:
    from ..core.base_mcp import BaseMCP
    USE_BASE_MCP = True
except ImportError:
    # 如果导入失败，使用简化的基类
    USE_BASE_MCP = False
    
    class BaseMCP:
        """简化的MCP基类"""
        
        def __init__(self, name: str = "EnhancedWorkflowEngine"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
            self.logger.info(f"初始化MCP适配器: {name}")
            
            # 性能指标
            self.performance_metrics = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0,
                "last_error": None,
                "uptime_start": datetime.now().isoformat(),
                "module_version": "1.0.0"
            }
        
        def get_capabilities(self) -> List[str]:
            """获取能力列表"""
            return [
                "workflow_creation",
                "workflow_execution",
                "workflow_optimization"
            ]
        
        def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
            """处理输入数据"""
            return self._process_implementation(input_data, context)
        
        def _process_implementation(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
            """具体的处理实现 - 子类应该覆盖此方法"""
            return {"message": f"{self.name}基础处理完成"}
        
        def update_metrics(self, success: bool, response_time: float):
            """更新性能指标"""
            self.performance_metrics["total_requests"] += 1
            if success:
                self.performance_metrics["successful_requests"] += 1
            else:
                self.performance_metrics["failed_requests"] += 1
            
            # 更新平均响应时间
            total = self.performance_metrics["total_requests"]
            current_avg = self.performance_metrics["average_response_time"]
            self.performance_metrics["average_response_time"] = (
                (current_avg * (total - 1) + response_time) / total
            )

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """工作流状态枚举"""
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeStatus(Enum):
    """节点状态枚举"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

@dataclass
class WorkflowNode:
    """工作流节点定义"""
    id: str
    type: str
    name: str
    description: str
    
    # 执行配置
    executor: str = "default"
    config: Dict[str, Any] = None
    timeout: int = 3600
    retry_count: int = 3
    
    # 资源需求
    cpu_requirement: float = 1.0
    memory_requirement: int = 512
    disk_requirement: int = 1024
    
    # 并行配置
    can_parallel: bool = True
    parallel_group: Optional[str] = None
    
    # 状态信息
    status: NodeStatus = NodeStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}

@dataclass
class WorkflowEdge:
    """工作流边（依赖关系）"""
    source: str
    target: str
    condition: Optional[str] = None
    data_mapping: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.data_mapping is None:
            self.data_mapping = {}

@dataclass
class EnhancedWorkflow:
    """增强型工作流定义"""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    nodes: List[WorkflowNode] = None
    edges: List[WorkflowEdge] = None
    metadata: Dict[str, Any] = None
    
    # 新增字段
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []
        if self.edges is None:
            self.edges = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "nodes": [asdict(node) for node in self.nodes],
            "edges": [asdict(edge) for edge in self.edges],
            "metadata": self.metadata
        }
    
    def get_node_by_id(self, node_id: str) -> Optional[WorkflowNode]:
        """根据ID获取节点"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """获取节点的依赖关系"""
        dependencies = []
        for edge in self.edges:
            if edge.target == node_id:
                dependencies.append(edge.source)
        return dependencies
    
    def get_dependents(self, node_id: str) -> List[str]:
        """获取依赖于指定节点的节点列表"""
        dependents = []
        for edge in self.edges:
            if edge.source == node_id:
                dependents.append(edge.target)
        return dependents

class EnhancedWorkflowEngine(BaseMCP):
    """增强型工作流引擎 - 主控制器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.name = "EnhancedWorkflowEngine"
        self.config = config or {}
        
        # 工作流存储
        self.workflows: Dict[str, EnhancedWorkflow] = {}
        self.execution_contexts: Dict[str, Dict[str, Any]] = {}
        
        # 初始化核心组件
        self._initialize_components()
        
        # 初始化状态管理
        self._initialize_state_management()
        
        # 注册事件处理器
        self._register_event_handlers()
        
        logger.info(f"EnhancedWorkflowEngine 初始化完成")
    
    def _initialize_components(self):
        """初始化核心组件"""
        try:
            # 延迟导入以避免循环依赖
            from .dynamic_workflow_generator import DynamicWorkflowGenerator
            from .parallel_execution_scheduler import ParallelExecutionScheduler
            from .intelligent_dependency_manager import IntelligentDependencyManager
            from .workflow_optimization_engine import WorkflowOptimizationEngine
            
            self.workflow_generator = DynamicWorkflowGenerator(self.config)
            self.execution_scheduler = ParallelExecutionScheduler(self.config)
            self.dependency_manager = IntelligentDependencyManager(self.config)
            self.optimization_engine = WorkflowOptimizationEngine(self.config)
            
            logger.info("核心组件初始化完成")
        except ImportError as e:
            logger.warning(f"部分组件导入失败，将使用基础实现: {e}")
            # 使用基础实现
            self.workflow_generator = None
            self.execution_scheduler = None
            self.dependency_manager = None
            self.optimization_engine = None
    
    def _initialize_state_management(self):
        """初始化状态管理"""
        self.state_lock = asyncio.Lock()
        self.event_listeners = []
        self.metrics = {
            "workflows_created": 0,
            "workflows_executed": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "total_execution_time": 0
        }
    
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_handlers = {
            "workflow_created": self._on_workflow_created,
            "workflow_started": self._on_workflow_started,
            "workflow_completed": self._on_workflow_completed,
            "workflow_failed": self._on_workflow_failed,
            "node_started": self._on_node_started,
            "node_completed": self._on_node_completed,
            "node_failed": self._on_node_failed
        }
    
    async def create_dynamic_workflow(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """创建动态工作流"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # 如果有工作流生成器，使用它生成工作流
            if self.workflow_generator:
                workflow = await self.workflow_generator.generate_workflow(requirements)
                workflow.id = workflow_id
            else:
                # 使用基础实现创建简单工作流
                workflow = self._create_basic_workflow(workflow_id, requirements)
            
            # 存储工作流
            async with self.state_lock:
                self.workflows[workflow_id] = workflow
                self.metrics["workflows_created"] += 1
            
            # 触发事件
            await self._emit_event("workflow_created", {"workflow_id": workflow_id, "workflow": workflow})
            
            # 如果有优化引擎，优化工作流
            if self.optimization_engine:
                optimized_workflow = await self.optimization_engine.optimize_workflow(workflow)
                self.workflows[workflow_id] = optimized_workflow
                workflow = optimized_workflow
            
            # 生成执行计划
            execution_plan = await self._create_execution_plan(workflow)
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow": workflow.to_dict(),
                "execution_plan": execution_plan,
                "estimated_duration": execution_plan.get("estimated_duration", 0),
                "resource_requirements": execution_plan.get("resource_requirements", {})
            }
            
        except Exception as e:
            logger.error(f"创建动态工作流失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _create_basic_workflow(self, workflow_id: str, requirements: Dict[str, Any]) -> EnhancedWorkflow:
        """创建基础工作流（当没有生成器时使用）"""
        description = requirements.get("description", "基础工作流")
        complexity = requirements.get("complexity", "simple")
        
        # 根据复杂度创建不同的工作流
        if complexity == "simple":
            nodes = [
                WorkflowNode(
                    id="analysis",
                    type="requirement_analysis",
                    name="需求分析",
                    description="分析项目需求"
                ),
                WorkflowNode(
                    id="implementation",
                    type="code_implementation", 
                    name="代码实现",
                    description="实现核心功能"
                ),
                WorkflowNode(
                    id="testing",
                    type="test_verification",
                    name="测试验证",
                    description="验证功能正确性"
                )
            ]
            edges = [
                WorkflowEdge(source="analysis", target="implementation"),
                WorkflowEdge(source="implementation", target="testing")
            ]
        else:
            # 标准工作流
            nodes = [
                WorkflowNode(
                    id="analysis",
                    type="requirement_analysis",
                    name="需求分析",
                    description="分析项目需求"
                ),
                WorkflowNode(
                    id="design",
                    type="architecture_design",
                    name="架构设计", 
                    description="设计系统架构"
                ),
                WorkflowNode(
                    id="implementation",
                    type="code_implementation",
                    name="代码实现",
                    description="实现核心功能"
                ),
                WorkflowNode(
                    id="testing",
                    type="test_verification",
                    name="测试验证",
                    description="验证功能正确性"
                ),
                WorkflowNode(
                    id="deployment",
                    type="deployment_release",
                    name="部署发布",
                    description="部署到生产环境"
                )
            ]
            edges = [
                WorkflowEdge(source="analysis", target="design"),
                WorkflowEdge(source="design", target="implementation"),
                WorkflowEdge(source="implementation", target="testing"),
                WorkflowEdge(source="testing", target="deployment")
            ]
        
        return EnhancedWorkflow(
            id=workflow_id,
            name=requirements.get("name", "动态生成工作流"),
            description=description,
            nodes=nodes,
            edges=edges,
            metadata={"generated_from": requirements, "complexity": complexity}
        )
    
    async def _create_execution_plan(self, workflow: EnhancedWorkflow) -> Dict[str, Any]:
        """创建执行计划"""
        if self.execution_scheduler:
            return await self.execution_scheduler.create_execution_plan(workflow)
        else:
            # 基础执行计划
            return {
                "workflow_id": workflow.id,
                "execution_order": [node.id for node in workflow.nodes],
                "parallel_groups": [[node.id] for node in workflow.nodes],
                "estimated_duration": len(workflow.nodes) * 300,  # 每个节点5分钟
                "resource_requirements": {
                    "cpu": sum(node.cpu_requirement for node in workflow.nodes),
                    "memory": sum(node.memory_requirement for node in workflow.nodes),
                    "disk": sum(node.disk_requirement for node in workflow.nodes)
                }
            }
    
    async def execute_workflow(self, workflow_id: str, execution_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行工作流"""
        try:
            if workflow_id not in self.workflows:
                return {"status": "error", "message": f"工作流 {workflow_id} 不存在"}
            
            workflow = self.workflows[workflow_id]
            execution_options = execution_options or {}
            
            # 更新工作流状态
            workflow.status = WorkflowStatus.RUNNING
            workflow.updated_at = datetime.now()
            
            # 创建执行上下文
            execution_context = {
                "workflow_id": workflow_id,
                "start_time": datetime.now(),
                "options": execution_options,
                "completed_nodes": set(),
                "failed_nodes": set(),
                "node_results": {}
            }
            
            self.execution_contexts[workflow_id] = execution_context
            
            # 触发开始事件
            await self._emit_event("workflow_started", {"workflow_id": workflow_id})
            
            # 执行工作流
            if self.execution_scheduler:
                execution_result = await self.execution_scheduler.execute_workflow(workflow, execution_context)
            else:
                execution_result = await self._execute_workflow_basic(workflow, execution_context)
            
            # 更新工作流状态
            if execution_result["status"] == "completed":
                workflow.status = WorkflowStatus.COMPLETED
                await self._emit_event("workflow_completed", {"workflow_id": workflow_id, "result": execution_result})
                self.metrics["workflows_completed"] += 1
            else:
                workflow.status = WorkflowStatus.FAILED
                await self._emit_event("workflow_failed", {"workflow_id": workflow_id, "result": execution_result})
                self.metrics["workflows_failed"] += 1
            
            workflow.updated_at = datetime.now()
            self.metrics["workflows_executed"] += 1
            
            # 计算执行时间
            execution_time = (datetime.now() - execution_context["start_time"]).total_seconds()
            self.metrics["total_execution_time"] += execution_time
            
            return execution_result
            
        except Exception as e:
            logger.error(f"执行工作流失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _execute_workflow_basic(self, workflow: EnhancedWorkflow, context: Dict[str, Any]) -> Dict[str, Any]:
        """基础工作流执行（当没有调度器时使用）"""
        try:
            # 按依赖顺序执行节点
            execution_order = self._calculate_execution_order(workflow)
            
            for node_id in execution_order:
                node = workflow.get_node_by_id(node_id)
                if not node:
                    continue
                
                # 检查依赖是否完成
                dependencies = workflow.get_dependencies(node_id)
                if not all(dep in context["completed_nodes"] for dep in dependencies):
                    context["failed_nodes"].add(node_id)
                    continue
                
                # 执行节点
                node_result = await self._execute_node_basic(node, context)
                
                if node_result["status"] == "completed":
                    context["completed_nodes"].add(node_id)
                    context["node_results"][node_id] = node_result
                    node.status = NodeStatus.COMPLETED
                else:
                    context["failed_nodes"].add(node_id)
                    node.status = NodeStatus.FAILED
                    # 如果关键节点失败，停止执行
                    break
            
            # 判断整体执行结果
            if len(context["failed_nodes"]) == 0:
                return {
                    "status": "completed",
                    "workflow_id": workflow.id,
                    "completed_nodes": list(context["completed_nodes"]),
                    "node_results": context["node_results"],
                    "execution_time": (datetime.now() - context["start_time"]).total_seconds()
                }
            else:
                return {
                    "status": "failed",
                    "workflow_id": workflow.id,
                    "completed_nodes": list(context["completed_nodes"]),
                    "failed_nodes": list(context["failed_nodes"]),
                    "node_results": context["node_results"],
                    "execution_time": (datetime.now() - context["start_time"]).total_seconds()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "workflow_id": workflow.id,
                "message": str(e),
                "execution_time": (datetime.now() - context["start_time"]).total_seconds()
            }
    
    def _calculate_execution_order(self, workflow: EnhancedWorkflow) -> List[str]:
        """计算执行顺序（拓扑排序）"""
        # 简单的拓扑排序实现
        in_degree = {node.id: 0 for node in workflow.nodes}
        
        # 计算入度
        for edge in workflow.edges:
            in_degree[edge.target] += 1
        
        # 找到入度为0的节点
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # 更新依赖节点的入度
            for edge in workflow.edges:
                if edge.source == current:
                    in_degree[edge.target] -= 1
                    if in_degree[edge.target] == 0:
                        queue.append(edge.target)
        
        return result
    
    async def _execute_node_basic(self, node: WorkflowNode, context: Dict[str, Any]) -> Dict[str, Any]:
        """基础节点执行"""
        try:
            node.status = NodeStatus.RUNNING
            node.start_time = datetime.now()
            
            await self._emit_event("node_started", {"workflow_id": context["workflow_id"], "node_id": node.id})
            
            # 模拟节点执行
            await asyncio.sleep(1)  # 模拟执行时间
            
            # 模拟执行结果
            result = {
                "status": "completed",
                "node_id": node.id,
                "output": f"{node.name} 执行完成",
                "execution_time": 1.0
            }
            
            node.end_time = datetime.now()
            node.execution_result = result
            
            await self._emit_event("node_completed", {"workflow_id": context["workflow_id"], "node_id": node.id, "result": result})
            
            return result
            
        except Exception as e:
            node.status = NodeStatus.FAILED
            node.end_time = datetime.now()
            
            result = {
                "status": "failed",
                "node_id": node.id,
                "error": str(e),
                "execution_time": (node.end_time - node.start_time).total_seconds() if node.start_time else 0
            }
            
            await self._emit_event("node_failed", {"workflow_id": context["workflow_id"], "node_id": node.id, "result": result})
            
            return result
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        if workflow_id not in self.workflows:
            return {"status": "error", "message": f"工作流 {workflow_id} 不存在"}
        
        workflow = self.workflows[workflow_id]
        execution_context = self.execution_contexts.get(workflow_id, {})
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "status": node.status.value,
                    "start_time": node.start_time.isoformat() if node.start_time else None,
                    "end_time": node.end_time.isoformat() if node.end_time else None
                }
                for node in workflow.nodes
            ],
            "execution_context": {
                "completed_nodes": list(execution_context.get("completed_nodes", [])),
                "failed_nodes": list(execution_context.get("failed_nodes", [])),
                "start_time": execution_context.get("start_time").isoformat() if execution_context.get("start_time") else None
            }
        }
    
    async def list_workflows(self) -> Dict[str, Any]:
        """列出所有工作流"""
        workflows = []
        for workflow_id, workflow in self.workflows.items():
            workflows.append({
                "id": workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                "node_count": len(workflow.nodes)
            })
        
        return {
            "workflows": workflows,
            "total_count": len(workflows),
            "metrics": self.metrics
        }
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """触发事件"""
        try:
            if event_type in self.event_handlers:
                await self.event_handlers[event_type](data)
            
            # 通知事件监听器
            for listener in self.event_listeners:
                try:
                    await listener(event_type, data)
                except Exception as e:
                    logger.warning(f"事件监听器处理失败: {e}")
                    
        except Exception as e:
            logger.error(f"事件触发失败: {e}")
    
    # 事件处理器
    async def _on_workflow_created(self, data: Dict[str, Any]):
        """工作流创建事件处理"""
        logger.info(f"工作流已创建: {data['workflow_id']}")
    
    async def _on_workflow_started(self, data: Dict[str, Any]):
        """工作流开始事件处理"""
        logger.info(f"工作流开始执行: {data['workflow_id']}")
    
    async def _on_workflow_completed(self, data: Dict[str, Any]):
        """工作流完成事件处理"""
        logger.info(f"工作流执行完成: {data['workflow_id']}")
    
    async def _on_workflow_failed(self, data: Dict[str, Any]):
        """工作流失败事件处理"""
        logger.error(f"工作流执行失败: {data['workflow_id']}")
    
    async def _on_node_started(self, data: Dict[str, Any]):
        """节点开始事件处理"""
        logger.info(f"节点开始执行: {data['workflow_id']}/{data['node_id']}")
    
    async def _on_node_completed(self, data: Dict[str, Any]):
        """节点完成事件处理"""
        logger.info(f"节点执行完成: {data['workflow_id']}/{data['node_id']}")
    
    async def _on_node_failed(self, data: Dict[str, Any]):
        """节点失败事件处理"""
        logger.error(f"节点执行失败: {data['workflow_id']}/{data['node_id']}")

# 单例模式实现
_instance = None

def get_instance(config: Dict[str, Any] = None):
    """获取EnhancedWorkflowEngine单例实例"""
    global _instance
    if _instance is None:
        _instance = EnhancedWorkflowEngine(config)
    return _instance

