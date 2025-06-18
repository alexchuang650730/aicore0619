#!/usr/bin/env python3
"""
Product Orchestrator V3 - 增强主控编排器

基于现有组件的增量增强，实现四大核心能力：
1. 动态工作流生成能力
2. 并行调度支持多个MCP组件
3. 智能依赖管理
4. 主动状态推送到SmartUI

遵循PowerAutomation最新目录规范v2.0
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import websockets
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# 导入现有组件
import sys
sys.path.append('/opt/powerautomation')
from mcp.enhanced_mcp_coordinator import EnhancedMCPCoordinator, MCPRequest, MCPResponse, RequestType
from utils.smart_routing_system import SmartRoutingSystem, RoutingDecision, ProcessingLocation
from mcp.adapter.interaction_log_manager.interaction_log_manager import InteractionLogManager

# ============================================================================
# 1. 增强的数据结构定义
# ============================================================================

class WorkflowType(Enum):
    """六大工作流类型"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    ARCHITECTURE_DESIGN = "architecture_design" 
    CODE_IMPLEMENTATION = "code_implementation"
    TEST_VERIFICATION = "test_verification"
    DEPLOYMENT_RELEASE = "deployment_release"
    MONITORING_OPERATIONS = "monitoring_operations"

class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class DependencyType(Enum):
    """依赖类型"""
    SEQUENTIAL = "sequential"      # 顺序依赖
    PARALLEL = "parallel"          # 并行依赖
    CONDITIONAL = "conditional"    # 条件依赖
    OPTIONAL = "optional"          # 可选依赖

@dataclass
class WorkflowNode:
    """工作流节点"""
    node_id: str
    workflow_type: WorkflowType
    mcp_components: List[str]      # 使用的MCP组件列表
    dependencies: List[str]        # 依赖的节点ID
    dependency_type: DependencyType
    estimated_duration: int        # 预估执行时间(秒)
    priority: int                  # 优先级 1-10
    retry_count: int = 0
    max_retries: int = 3
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@dataclass
class DynamicWorkflow:
    """动态生成的工作流"""
    workflow_id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    user_requirements: Dict[str, Any]
    generated_time: datetime
    estimated_total_duration: int
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_executing_nodes: Set[str] = None
    completed_nodes: Set[str] = None
    failed_nodes: Set[str] = None
    
    def __post_init__(self):
        if self.current_executing_nodes is None:
            self.current_executing_nodes = set()
        if self.completed_nodes is None:
            self.completed_nodes = set()
        if self.failed_nodes is None:
            self.failed_nodes = set()

@dataclass
class MCPComponentMapping:
    """MCP组件映射配置"""
    workflow_type: WorkflowType
    primary_mcp: str               # 主要MCP组件
    secondary_mcps: List[str]      # 辅助MCP组件
    tool_engine_required: bool     # 是否需要unified_smart_tool_engine
    search_fallback: bool          # 是否需要搜索引擎兜底

@dataclass
class StatusUpdate:
    """状态更新消息"""
    update_id: str
    workflow_id: str
    node_id: Optional[str]
    status: WorkflowStatus
    progress: float                # 0.0-1.0
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None

# ============================================================================
# 2. 动态工作流生成器
# ============================================================================

class DynamicWorkflowGenerator:
    """动态工作流生成器 - 基于用户需求智能生成工作流"""
    
    def __init__(self):
        self.workflow_templates = self._load_workflow_templates()
        self.mcp_mappings = self._initialize_mcp_mappings()
        self.logger = logging.getLogger(__name__)
    
    def _load_workflow_templates(self) -> Dict[str, List[WorkflowType]]:
        """加载工作流模板"""
        return {
            "software_development": [
                WorkflowType.REQUIREMENT_ANALYSIS,
                WorkflowType.ARCHITECTURE_DESIGN,
                WorkflowType.CODE_IMPLEMENTATION,
                WorkflowType.TEST_VERIFICATION,
                WorkflowType.DEPLOYMENT_RELEASE,
                WorkflowType.MONITORING_OPERATIONS
            ],
            "quick_prototype": [
                WorkflowType.REQUIREMENT_ANALYSIS,
                WorkflowType.CODE_IMPLEMENTATION,
                WorkflowType.TEST_VERIFICATION
            ],
            "documentation_only": [
                WorkflowType.REQUIREMENT_ANALYSIS,
                WorkflowType.ARCHITECTURE_DESIGN
            ],
            "testing_focus": [
                WorkflowType.TEST_VERIFICATION,
                WorkflowType.MONITORING_OPERATIONS
            ],
            "deployment_focus": [
                WorkflowType.DEPLOYMENT_RELEASE,
                WorkflowType.MONITORING_OPERATIONS
            ]
        }
    
    def _initialize_mcp_mappings(self) -> Dict[WorkflowType, MCPComponentMapping]:
        """初始化MCP组件映射"""
        return {
            WorkflowType.REQUIREMENT_ANALYSIS: MCPComponentMapping(
                workflow_type=WorkflowType.REQUIREMENT_ANALYSIS,
                primary_mcp="requirement_analysis_mcp",
                secondary_mcps=["documentation_mcp", "smartui_mcp"],
                tool_engine_required=True,
                search_fallback=True
            ),
            WorkflowType.ARCHITECTURE_DESIGN: MCPComponentMapping(
                workflow_type=WorkflowType.ARCHITECTURE_DESIGN,
                primary_mcp="enhanced_workflow_mcp",
                secondary_mcps=["documentation_mcp", "directory_structure_mcp"],
                tool_engine_required=True,
                search_fallback=True
            ),
            WorkflowType.CODE_IMPLEMENTATION: MCPComponentMapping(
                workflow_type=WorkflowType.CODE_IMPLEMENTATION,
                primary_mcp="code_generation_mcp",
                secondary_mcps=["kilocode_mcp", "local_model_mcp", "github_mcp"],
                tool_engine_required=True,
                search_fallback=True
            ),
            WorkflowType.TEST_VERIFICATION: MCPComponentMapping(
                workflow_type=WorkflowType.TEST_VERIFICATION,
                primary_mcp="test_manage_mcp",
                secondary_mcps=["testing_mcp", "github_mcp"],
                tool_engine_required=True,
                search_fallback=False
            ),
            WorkflowType.DEPLOYMENT_RELEASE: MCPComponentMapping(
                workflow_type=WorkflowType.DEPLOYMENT_RELEASE,
                primary_mcp="deployment_mcp",
                secondary_mcps=["github_mcp", "monitoring_mcp"],
                tool_engine_required=True,
                search_fallback=False
            ),
            WorkflowType.MONITORING_OPERATIONS: MCPComponentMapping(
                workflow_type=WorkflowType.MONITORING_OPERATIONS,
                primary_mcp="monitoring_mcp",
                secondary_mcps=["deployment_mcp"],
                tool_engine_required=False,
                search_fallback=False
            )
        }
    
    async def generate_workflow(self, user_requirements: Dict[str, Any]) -> DynamicWorkflow:
        """基于用户需求生成动态工作流"""
        try:
            # 1. 分析用户需求
            workflow_template = self._analyze_requirements(user_requirements)
            
            # 2. 生成工作流节点
            nodes = self._generate_workflow_nodes(workflow_template, user_requirements)
            
            # 3. 计算依赖关系
            self._calculate_dependencies(nodes)
            
            # 4. 估算执行时间
            total_duration = self._estimate_total_duration(nodes)
            
            # 5. 创建工作流对象
            workflow = DynamicWorkflow(
                workflow_id=str(uuid.uuid4()),
                name=user_requirements.get('name', 'Generated Workflow'),
                description=user_requirements.get('description', 'Dynamically generated workflow'),
                nodes=nodes,
                user_requirements=user_requirements,
                generated_time=datetime.now(),
                estimated_total_duration=total_duration
            )
            
            self.logger.info(f"Generated dynamic workflow: {workflow.workflow_id}")
            return workflow
            
        except Exception as e:
            self.logger.error(f"Failed to generate workflow: {str(e)}")
            raise
    
    def _analyze_requirements(self, requirements: Dict[str, Any]) -> str:
        """分析用户需求，选择合适的工作流模板"""
        keywords = requirements.get('description', '').lower()
        
        if any(word in keywords for word in ['prototype', 'quick', 'demo']):
            return "quick_prototype"
        elif any(word in keywords for word in ['document', 'design', 'architecture']):
            return "documentation_only"
        elif any(word in keywords for word in ['test', 'verify', 'quality']):
            return "testing_focus"
        elif any(word in keywords for word in ['deploy', 'release', 'production']):
            return "deployment_focus"
        else:
            return "software_development"
    
    def _generate_workflow_nodes(self, template: str, requirements: Dict[str, Any]) -> List[WorkflowNode]:
        """生成工作流节点"""
        workflow_types = self.workflow_templates[template]
        nodes = []
        
        for i, workflow_type in enumerate(workflow_types):
            mapping = self.mcp_mappings[workflow_type]
            
            # 构建MCP组件列表
            mcp_components = [mapping.primary_mcp] + mapping.secondary_mcps
            if mapping.tool_engine_required:
                mcp_components.append("unified_smart_tool_engine")
            if mapping.search_fallback:
                mcp_components.append("cloud_search_mcp")
            
            node = WorkflowNode(
                node_id=f"node_{i+1}_{workflow_type.value}",
                workflow_type=workflow_type,
                mcp_components=mcp_components,
                dependencies=[],  # 将在_calculate_dependencies中设置
                dependency_type=DependencyType.SEQUENTIAL,
                estimated_duration=self._estimate_node_duration(workflow_type, requirements),
                priority=10 - i  # 前面的节点优先级更高
            )
            nodes.append(node)
        
        return nodes
    
    def _calculate_dependencies(self, nodes: List[WorkflowNode]):
        """计算节点间的依赖关系"""
        for i, node in enumerate(nodes):
            if i > 0:
                # 默认顺序依赖前一个节点
                node.dependencies = [nodes[i-1].node_id]
                node.dependency_type = DependencyType.SEQUENTIAL
            
            # 特殊依赖规则
            if node.workflow_type == WorkflowType.TEST_VERIFICATION:
                # 测试验证可以与部署并行
                if i < len(nodes) - 1 and nodes[i+1].workflow_type == WorkflowType.DEPLOYMENT_RELEASE:
                    nodes[i+1].dependency_type = DependencyType.PARALLEL
    
    def _estimate_node_duration(self, workflow_type: WorkflowType, requirements: Dict[str, Any]) -> int:
        """估算节点执行时间"""
        base_durations = {
            WorkflowType.REQUIREMENT_ANALYSIS: 300,      # 5分钟
            WorkflowType.ARCHITECTURE_DESIGN: 600,       # 10分钟
            WorkflowType.CODE_IMPLEMENTATION: 1800,      # 30分钟
            WorkflowType.TEST_VERIFICATION: 900,         # 15分钟
            WorkflowType.DEPLOYMENT_RELEASE: 600,        # 10分钟
            WorkflowType.MONITORING_OPERATIONS: 300      # 5分钟
        }
        
        base_duration = base_durations.get(workflow_type, 600)
        
        # 根据复杂度调整
        complexity = requirements.get('complexity', 'medium')
        if complexity == 'simple':
            return int(base_duration * 0.5)
        elif complexity == 'complex':
            return int(base_duration * 2.0)
        else:
            return base_duration
    
    def _estimate_total_duration(self, nodes: List[WorkflowNode]) -> int:
        """估算总执行时间"""
        # 简化计算：假设大部分是顺序执行
        return sum(node.estimated_duration for node in nodes)

# ============================================================================
# 3. 并行执行调度器
# ============================================================================

class ParallelExecutionScheduler:
    """并行执行调度器 - 支持多个MCP组件的并行执行"""
    
    def __init__(self, max_parallel_tasks: int = 4):
        self.max_parallel_tasks = max_parallel_tasks
        self.executor = ThreadPoolExecutor(max_workers=max_parallel_tasks)
        self.running_tasks = {}
        self.task_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
    
    async def schedule_workflow_execution(self, workflow: DynamicWorkflow, 
                                        mcp_coordinator: EnhancedMCPCoordinator) -> Dict[str, Any]:
        """调度工作流执行"""
        try:
            self.logger.info(f"Starting workflow execution: {workflow.workflow_id}")
            workflow.status = WorkflowStatus.RUNNING
            
            # 创建执行计划
            execution_plan = self._create_execution_plan(workflow)
            
            # 并行执行节点
            results = await self._execute_parallel_nodes(workflow, execution_plan, mcp_coordinator)
            
            # 更新工作流状态
            if all(result.get('status') == 'success' for result in results.values()):
                workflow.status = WorkflowStatus.COMPLETED
            else:
                workflow.status = WorkflowStatus.FAILED
            
            return {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status.value,
                "results": results,
                "execution_time": self._calculate_execution_time(workflow)
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            workflow.status = WorkflowStatus.FAILED
            raise
    
    def _create_execution_plan(self, workflow: DynamicWorkflow) -> Dict[str, List[str]]:
        """创建执行计划 - 确定哪些节点可以并行执行"""
        execution_plan = {}
        processed_nodes = set()
        
        # 按依赖层级分组
        level = 0
        while len(processed_nodes) < len(workflow.nodes):
            current_level_nodes = []
            
            for node in workflow.nodes:
                if node.node_id in processed_nodes:
                    continue
                
                # 检查依赖是否已满足
                if all(dep in processed_nodes for dep in node.dependencies):
                    current_level_nodes.append(node.node_id)
            
            if current_level_nodes:
                execution_plan[f"level_{level}"] = current_level_nodes
                processed_nodes.update(current_level_nodes)
                level += 1
            else:
                # 避免无限循环
                break
        
        return execution_plan
    
    async def _execute_parallel_nodes(self, workflow: DynamicWorkflow, 
                                    execution_plan: Dict[str, List[str]],
                                    mcp_coordinator: EnhancedMCPCoordinator) -> Dict[str, Any]:
        """并行执行节点"""
        results = {}
        
        for level, node_ids in execution_plan.items():
            self.logger.info(f"Executing level {level} with nodes: {node_ids}")
            
            # 并行执行当前层级的所有节点
            level_tasks = []
            for node_id in node_ids:
                node = next(n for n in workflow.nodes if n.node_id == node_id)
                task = asyncio.create_task(
                    self._execute_single_node(node, mcp_coordinator)
                )
                level_tasks.append((node_id, task))
            
            # 等待当前层级所有任务完成
            for node_id, task in level_tasks:
                try:
                    result = await task
                    results[node_id] = result
                    
                    # 更新节点状态
                    node = next(n for n in workflow.nodes if n.node_id == node_id)
                    if result.get('status') == 'success':
                        node.status = WorkflowStatus.COMPLETED
                        workflow.completed_nodes.add(node_id)
                    else:
                        node.status = WorkflowStatus.FAILED
                        workflow.failed_nodes.add(node_id)
                    
                except Exception as e:
                    self.logger.error(f"Node {node_id} execution failed: {str(e)}")
                    results[node_id] = {"status": "error", "message": str(e)}
                    workflow.failed_nodes.add(node_id)
        
        return results
    
    async def _execute_single_node(self, node: WorkflowNode, 
                                 mcp_coordinator: EnhancedMCPCoordinator) -> Dict[str, Any]:
        """执行单个节点"""
        try:
            node.status = WorkflowStatus.RUNNING
            node.start_time = datetime.now()
            
            # 调用主要MCP组件
            primary_mcp = node.mcp_components[0]
            request = MCPRequest(
                request_id=str(uuid.uuid4()),
                request_type=RequestType.DIRECT_CALL,
                source_mcp="product_orchestrator",
                target_mcp=primary_mcp,
                request_data={
                    "workflow_type": node.workflow_type.value,
                    "node_id": node.node_id,
                    "mcp_components": node.mcp_components
                }
            )
            
            response = await mcp_coordinator.route_request(request)
            
            node.end_time = datetime.now()
            node.result_data = response.response_data if response else {}
            
            return {
                "status": "success" if response and response.status == "success" else "failed",
                "data": node.result_data,
                "execution_time": (node.end_time - node.start_time).total_seconds()
            }
            
        except Exception as e:
            node.status = WorkflowStatus.FAILED
            node.end_time = datetime.now()
            node.error_message = str(e)
            return {"status": "error", "message": str(e)}
    
    def _calculate_execution_time(self, workflow: DynamicWorkflow) -> float:
        """计算工作流执行时间"""
        start_times = [node.start_time for node in workflow.nodes if node.start_time]
        end_times = [node.end_time for node in workflow.nodes if node.end_time]
        
        if start_times and end_times:
            return (max(end_times) - min(start_times)).total_seconds()
        return 0.0

# ============================================================================
# 4. 智能依赖管理器
# ============================================================================

class IntelligentDependencyManager:
    """智能依赖管理器 - 自动处理workflow间的复杂依赖"""
    
    def __init__(self):
        self.dependency_graph = {}
        self.execution_history = {}
        self.logger = logging.getLogger(__name__)
    
    async def analyze_dependencies(self, workflow: DynamicWorkflow) -> Dict[str, Any]:
        """分析工作流依赖关系"""
        try:
            # 构建依赖图
            dependency_graph = self._build_dependency_graph(workflow)
            
            # 检测循环依赖
            cycles = self._detect_cycles(dependency_graph)
            
            # 优化依赖关系
            optimized_dependencies = self._optimize_dependencies(workflow, dependency_graph)
            
            # 计算关键路径
            critical_path = self._calculate_critical_path(workflow, dependency_graph)
            
            return {
                "dependency_graph": dependency_graph,
                "cycles": cycles,
                "optimized_dependencies": optimized_dependencies,
                "critical_path": critical_path,
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Dependency analysis failed: {str(e)}")
            raise
    
    def _build_dependency_graph(self, workflow: DynamicWorkflow) -> Dict[str, List[str]]:
        """构建依赖图"""
        graph = {}
        
        for node in workflow.nodes:
            graph[node.node_id] = node.dependencies.copy()
        
        return graph
    
    def _detect_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """检测循环依赖"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                # 找到循环
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _optimize_dependencies(self, workflow: DynamicWorkflow, 
                             graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """优化依赖关系 - 识别可以并行执行的节点"""
        optimized = {}
        
        for node in workflow.nodes:
            node_id = node.node_id
            dependencies = graph.get(node_id, [])
            
            # 检查是否可以并行执行
            if node.dependency_type == DependencyType.PARALLEL:
                # 移除不必要的顺序依赖
                optimized[node_id] = self._filter_parallel_dependencies(dependencies, workflow)
            else:
                optimized[node_id] = dependencies
        
        return optimized
    
    def _filter_parallel_dependencies(self, dependencies: List[str], 
                                    workflow: DynamicWorkflow) -> List[str]:
        """过滤并行依赖 - 只保留真正必要的依赖"""
        filtered = []
        
        for dep in dependencies:
            dep_node = next((n for n in workflow.nodes if n.node_id == dep), None)
            if dep_node and self._is_critical_dependency(dep_node):
                filtered.append(dep)
        
        return filtered
    
    def _is_critical_dependency(self, node: WorkflowNode) -> bool:
        """判断是否为关键依赖"""
        # 某些工作流类型是关键依赖
        critical_types = {
            WorkflowType.REQUIREMENT_ANALYSIS,
            WorkflowType.ARCHITECTURE_DESIGN
        }
        return node.workflow_type in critical_types
    
    def _calculate_critical_path(self, workflow: DynamicWorkflow, 
                               graph: Dict[str, List[str]]) -> List[str]:
        """计算关键路径"""
        # 使用拓扑排序和最长路径算法
        in_degree = {node.node_id: 0 for node in workflow.nodes}
        
        # 计算入度
        for node_id, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[node_id] += 1
        
        # 拓扑排序
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        topo_order = []
        
        while queue:
            current = queue.pop(0)
            topo_order.append(current)
            
            # 更新后续节点的入度
            for node_id, deps in graph.items():
                if current in deps:
                    in_degree[node_id] -= 1
                    if in_degree[node_id] == 0:
                        queue.append(node_id)
        
        # 计算最长路径（关键路径）
        distances = {node.node_id: 0 for node in workflow.nodes}
        
        for node_id in topo_order:
            node = next(n for n in workflow.nodes if n.node_id == node_id)
            for dep in graph.get(node_id, []):
                distances[node_id] = max(
                    distances[node_id], 
                    distances[dep] + node.estimated_duration
                )
        
        # 找到关键路径
        max_distance = max(distances.values())
        critical_path = []
        
        # 反向追踪关键路径
        current_distance = max_distance
        for node_id in reversed(topo_order):
            if distances[node_id] == current_distance:
                critical_path.insert(0, node_id)
                node = next(n for n in workflow.nodes if n.node_id == node_id)
                current_distance -= node.estimated_duration
        
        return critical_path

# ============================================================================
# 5. 主动状态推送器
# ============================================================================

class ActiveStatusPusher:
    """主动状态推送器 - 实时推送状态到SmartUI"""
    
    def __init__(self, smartui_endpoint: str = "ws://localhost:5001/ws"):
        self.smartui_endpoint = smartui_endpoint
        self.websocket_connections = set()
        self.status_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
        self.running = False
    
    async def start(self):
        """启动状态推送服务"""
        self.running = True
        await asyncio.gather(
            self._status_pusher_worker(),
            self._websocket_server()
        )
    
    async def stop(self):
        """停止状态推送服务"""
        self.running = False
        for ws in self.websocket_connections.copy():
            await ws.close()
    
    async def push_status_update(self, update: StatusUpdate):
        """推送状态更新"""
        await self.status_queue.put(update)
    
    async def _status_pusher_worker(self):
        """状态推送工作线程"""
        while self.running:
            try:
                # 等待状态更新
                update = await asyncio.wait_for(self.status_queue.get(), timeout=1.0)
                
                # 推送到所有连接的客户端
                await self._broadcast_update(update)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Status pusher error: {str(e)}")
    
    async def _broadcast_update(self, update: StatusUpdate):
        """广播状态更新到所有客户端"""
        if not self.websocket_connections:
            return
        
        message = {
            "type": "status_update",
            "data": {
                "update_id": update.update_id,
                "workflow_id": update.workflow_id,
                "node_id": update.node_id,
                "status": update.status.value,
                "progress": update.progress,
                "message": update.message,
                "timestamp": update.timestamp.isoformat(),
                "data": update.data
            }
        }
        
        # 发送到所有连接的客户端
        disconnected = set()
        for ws in self.websocket_connections:
            try:
                await ws.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(ws)
            except Exception as e:
                self.logger.error(f"Failed to send update to client: {str(e)}")
                disconnected.add(ws)
        
        # 清理断开的连接
        self.websocket_connections -= disconnected
    
    async def _websocket_server(self):
        """WebSocket服务器"""
        async def handle_client(websocket, path):
            self.websocket_connections.add(websocket)
            self.logger.info(f"New WebSocket connection: {websocket.remote_address}")
            
            try:
                await websocket.wait_closed()
            finally:
                self.websocket_connections.discard(websocket)
                self.logger.info(f"WebSocket connection closed: {websocket.remote_address}")
        
        try:
            server = await websockets.serve(handle_client, "localhost", 5002)
            self.logger.info("WebSocket server started on ws://localhost:5002")
            await server.wait_closed()
        except Exception as e:
            self.logger.error(f"WebSocket server error: {str(e)}")

# ============================================================================
# 6. Product Orchestrator V3 主控制器
# ============================================================================

class ProductOrchestratorV3:
    """Product Orchestrator V3 - 增强主控编排器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 初始化核心组件
        self.workflow_generator = DynamicWorkflowGenerator()
        self.execution_scheduler = ParallelExecutionScheduler(
            max_parallel_tasks=self.config.get('max_parallel_tasks', 4)
        )
        self.dependency_manager = IntelligentDependencyManager()
        self.status_pusher = ActiveStatusPusher(
            smartui_endpoint=self.config.get('smartui_endpoint', 'ws://localhost:5001/ws')
        )
        
        # 集成现有组件
        self.mcp_coordinator = EnhancedMCPCoordinator()
        self.smart_routing = SmartRoutingSystem()
        self.interaction_log = InteractionLogManager()
        
        # 状态管理
        self.active_workflows = {}
        self.workflow_history = []
        
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """启动Product Orchestrator"""
        self.logger.info("Starting Product Orchestrator V3...")
        
        # 启动状态推送服务
        await self.status_pusher.start()
        
        self.logger.info("Product Orchestrator V3 started successfully")
    
    async def stop(self):
        """停止Product Orchestrator"""
        self.logger.info("Stopping Product Orchestrator V3...")
        
        # 停止状态推送服务
        await self.status_pusher.stop()
        
        self.logger.info("Product Orchestrator V3 stopped")
    
    async def create_and_execute_workflow(self, user_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """创建并执行工作流 - 主要入口方法"""
        try:
            # 1. 动态生成工作流
            workflow = await self.workflow_generator.generate_workflow(user_requirements)
            self.active_workflows[workflow.workflow_id] = workflow
            
            # 推送工作流创建状态
            await self.status_pusher.push_status_update(StatusUpdate(
                update_id=str(uuid.uuid4()),
                workflow_id=workflow.workflow_id,
                node_id=None,
                status=WorkflowStatus.PENDING,
                progress=0.0,
                message=f"Workflow created: {workflow.name}",
                timestamp=datetime.now(),
                data={"total_nodes": len(workflow.nodes)}
            ))
            
            # 2. 智能依赖分析
            dependency_analysis = await self.dependency_manager.analyze_dependencies(workflow)
            
            # 推送依赖分析完成状态
            await self.status_pusher.push_status_update(StatusUpdate(
                update_id=str(uuid.uuid4()),
                workflow_id=workflow.workflow_id,
                node_id=None,
                status=WorkflowStatus.RUNNING,
                progress=0.1,
                message="Dependency analysis completed",
                timestamp=datetime.now(),
                data=dependency_analysis
            ))
            
            # 3. 并行执行调度
            execution_result = await self.execution_scheduler.schedule_workflow_execution(
                workflow, self.mcp_coordinator
            )
            
            # 推送执行完成状态
            await self.status_pusher.push_status_update(StatusUpdate(
                update_id=str(uuid.uuid4()),
                workflow_id=workflow.workflow_id,
                node_id=None,
                status=workflow.status,
                progress=1.0,
                message=f"Workflow execution completed: {workflow.status.value}",
                timestamp=datetime.now(),
                data=execution_result
            ))
            
            # 4. 记录到历史
            self.workflow_history.append(workflow)
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
            
            # 5. 记录交互日志
            await self._log_workflow_execution(workflow, execution_result)
            
            return {
                "workflow_id": workflow.workflow_id,
                "status": workflow.status.value,
                "execution_result": execution_result,
                "dependency_analysis": dependency_analysis,
                "total_execution_time": execution_result.get("execution_time", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Workflow creation and execution failed: {str(e)}")
            
            # 推送错误状态
            if 'workflow' in locals():
                await self.status_pusher.push_status_update(StatusUpdate(
                    update_id=str(uuid.uuid4()),
                    workflow_id=workflow.workflow_id,
                    node_id=None,
                    status=WorkflowStatus.FAILED,
                    progress=0.0,
                    message=f"Workflow failed: {str(e)}",
                    timestamp=datetime.now()
                ))
            
            raise
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            # 检查历史记录
            workflow = next((w for w in self.workflow_history if w.workflow_id == workflow_id), None)
        
        if not workflow:
            return {"error": "Workflow not found"}
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "progress": len(workflow.completed_nodes) / len(workflow.nodes) if workflow.nodes else 0,
            "completed_nodes": list(workflow.completed_nodes),
            "failed_nodes": list(workflow.failed_nodes),
            "current_executing_nodes": list(workflow.current_executing_nodes),
            "estimated_total_duration": workflow.estimated_total_duration,
            "generated_time": workflow.generated_time.isoformat()
        }
    
    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """列出活跃的工作流"""
        return [
            {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "progress": len(workflow.completed_nodes) / len(workflow.nodes) if workflow.nodes else 0,
                "generated_time": workflow.generated_time.isoformat()
            }
            for workflow in self.active_workflows.values()
        ]
    
    async def _log_workflow_execution(self, workflow: DynamicWorkflow, execution_result: Dict[str, Any]):
        """记录工作流执行到交互日志"""
        try:
            log_data = {
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.name,
                "user_requirements": workflow.user_requirements,
                "execution_result": execution_result,
                "nodes_executed": len(workflow.nodes),
                "nodes_completed": len(workflow.completed_nodes),
                "nodes_failed": len(workflow.failed_nodes),
                "total_execution_time": execution_result.get("execution_time", 0)
            }
            
            await self.interaction_log.log_interaction(
                interaction_type="workflow_execution",
                user_request=workflow.user_requirements,
                agent_response=execution_result,
                deliverable_type="workflow_result",
                deliverable_content=log_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log workflow execution: {str(e)}")

if __name__ == "__main__":
    # 示例使用
    async def main():
        orchestrator = ProductOrchestratorV3()
        
        try:
            await orchestrator.start()
            
            # 示例用户需求
            user_requirements = {
                "name": "Web Application Development",
                "description": "Create a full-stack web application with user authentication",
                "complexity": "medium",
                "priority": "high"
            }
            
            # 创建并执行工作流
            result = await orchestrator.create_and_execute_workflow(user_requirements)
            print(f"Workflow execution result: {result}")
            
        finally:
            await orchestrator.stop()
    
    # 运行示例
    # asyncio.run(main())

