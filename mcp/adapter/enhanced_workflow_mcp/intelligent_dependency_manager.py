#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能依赖管理器
Intelligent Dependency Manager

智能分析和管理工作流节点之间的依赖关系，解决循环依赖和资源冲突
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import networkx as nx
import heapq

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """依赖类型"""
    DATA = "data"  # 数据依赖
    CONTROL = "control"  # 控制依赖
    RESOURCE = "resource"  # 资源依赖
    TEMPORAL = "temporal"  # 时间依赖
    CONDITIONAL = "conditional"  # 条件依赖

class ConflictType(Enum):
    """冲突类型"""
    CIRCULAR_DEPENDENCY = "circular_dependency"
    RESOURCE_CONFLICT = "resource_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"
    DATA_INCONSISTENCY = "data_inconsistency"
    DEADLOCK = "deadlock"

@dataclass
class DependencyEdge:
    """依赖边"""
    source_node: str
    target_node: str
    dependency_type: DependencyType
    
    # 依赖条件
    condition: Optional[str] = None
    weight: float = 1.0
    
    # 数据传递
    data_mapping: Dict[str, str] = field(default_factory=dict)
    
    # 时间约束
    min_delay: int = 0  # 最小延迟（秒）
    max_delay: int = 0  # 最大延迟（秒）
    
    # 资源约束
    shared_resources: List[str] = field(default_factory=list)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DependencyConflict:
    """依赖冲突"""
    conflict_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conflict_type: ConflictType = ConflictType.CIRCULAR_DEPENDENCY
    
    # 冲突涉及的节点
    involved_nodes: List[str] = field(default_factory=list)
    involved_edges: List[DependencyEdge] = field(default_factory=list)
    
    # 冲突描述
    description: str = ""
    severity: str = "medium"  # low, medium, high, critical
    
    # 解决方案
    suggested_solutions: List[Dict[str, Any]] = field(default_factory=list)
    
    # 检测信息
    detected_at: datetime = field(default_factory=datetime.now)
    detection_method: str = ""

@dataclass
class DependencyResolution:
    """依赖解决方案"""
    resolution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conflict_id: str = ""
    
    # 解决方案类型
    resolution_type: str = ""  # remove_edge, add_condition, reorder_nodes, etc.
    
    # 具体操作
    operations: List[Dict[str, Any]] = field(default_factory=list)
    
    # 影响评估
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # 应用状态
    applied: bool = False
    applied_at: Optional[datetime] = None

class IntelligentDependencyManager:
    """智能依赖管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 依赖图
        self.dependency_graph = nx.DiGraph()
        self.dependency_edges: Dict[str, DependencyEdge] = {}
        
        # 冲突管理
        self.detected_conflicts: Dict[str, DependencyConflict] = {}
        self.resolutions: Dict[str, DependencyResolution] = {}
        
        # 分析配置
        self.max_cycle_length = self.config.get("max_cycle_length", 10)
        self.enable_auto_resolution = self.config.get("enable_auto_resolution", True)
        self.conflict_detection_interval = self.config.get("conflict_detection_interval", 60)
        
        # 资源管理
        self.resource_registry: Dict[str, Set[str]] = defaultdict(set)  # resource -> nodes
        self.node_resources: Dict[str, Set[str]] = defaultdict(set)  # node -> resources
        
        logger.info("IntelligentDependencyManager 初始化完成")
    
    async def add_dependency(self, source_node: str, target_node: str, dependency_type: DependencyType, **kwargs) -> Dict[str, Any]:
        """添加依赖关系"""
        try:
            # 创建依赖边
            edge = DependencyEdge(
                source_node=source_node,
                target_node=target_node,
                dependency_type=dependency_type,
                condition=kwargs.get("condition"),
                weight=kwargs.get("weight", 1.0),
                data_mapping=kwargs.get("data_mapping", {}),
                min_delay=kwargs.get("min_delay", 0),
                max_delay=kwargs.get("max_delay", 0),
                shared_resources=kwargs.get("shared_resources", []),
                metadata=kwargs.get("metadata", {})
            )
            
            edge_id = f"{source_node}->{target_node}"
            
            # 检查是否会产生循环依赖
            temp_graph = self.dependency_graph.copy()
            temp_graph.add_edge(source_node, target_node, edge_data=edge)
            
            if not nx.is_directed_acyclic_graph(temp_graph):
                cycles = list(nx.simple_cycles(temp_graph))
                return {
                    "status": "error",
                    "message": "添加此依赖会产生循环依赖",
                    "cycles": cycles
                }
            
            # 添加到图中
            self.dependency_graph.add_edge(source_node, target_node, edge_data=edge)
            self.dependency_edges[edge_id] = edge
            
            # 更新资源注册
            for resource in edge.shared_resources:
                self.resource_registry[resource].add(source_node)
                self.resource_registry[resource].add(target_node)
                self.node_resources[source_node].add(resource)
                self.node_resources[target_node].add(resource)
            
            # 检测新的冲突
            await self._detect_conflicts()
            
            logger.info(f"依赖关系已添加: {source_node} -> {target_node} ({dependency_type.value})")
            
            return {
                "status": "success",
                "edge_id": edge_id,
                "dependency_type": dependency_type.value,
                "conflicts_detected": len(self.detected_conflicts)
            }
            
        except Exception as e:
            logger.error(f"添加依赖关系失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def remove_dependency(self, source_node: str, target_node: str) -> Dict[str, Any]:
        """移除依赖关系"""
        try:
            edge_id = f"{source_node}->{target_node}"
            
            if not self.dependency_graph.has_edge(source_node, target_node):
                return {"status": "error", "message": "依赖关系不存在"}
            
            # 获取边数据
            edge_data = self.dependency_graph[source_node][target_node].get("edge_data")
            
            # 从图中移除
            self.dependency_graph.remove_edge(source_node, target_node)
            
            # 从边字典中移除
            if edge_id in self.dependency_edges:
                del self.dependency_edges[edge_id]
            
            # 更新资源注册
            if edge_data:
                for resource in edge_data.shared_resources:
                    self.resource_registry[resource].discard(source_node)
                    self.resource_registry[resource].discard(target_node)
                    self.node_resources[source_node].discard(resource)
                    self.node_resources[target_node].discard(resource)
            
            # 重新检测冲突
            await self._detect_conflicts()
            
            logger.info(f"依赖关系已移除: {source_node} -> {target_node}")
            
            return {
                "status": "success",
                "edge_id": edge_id,
                "conflicts_detected": len(self.detected_conflicts)
            }
            
        except Exception as e:
            logger.error(f"移除依赖关系失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_dependencies(self, workflow: 'EnhancedWorkflow') -> Dict[str, Any]:
        """分析工作流的依赖关系"""
        try:
            # 构建依赖图
            await self._build_dependency_graph(workflow)
            
            # 检测冲突
            conflicts = await self._detect_conflicts()
            
            # 计算拓扑排序
            topological_order = self._calculate_topological_order()
            
            # 识别关键路径
            critical_paths = self._identify_critical_paths()
            
            # 分析并行机会
            parallel_opportunities = self._analyze_parallel_opportunities()
            
            # 资源冲突分析
            resource_conflicts = self._analyze_resource_conflicts()
            
            # 生成优化建议
            optimization_suggestions = self._generate_optimization_suggestions(conflicts, critical_paths, parallel_opportunities)
            
            return {
                "status": "success",
                "workflow_id": workflow.id,
                "analysis": {
                    "total_nodes": len(workflow.nodes),
                    "total_dependencies": len(self.dependency_edges),
                    "conflicts_detected": len(conflicts),
                    "topological_order": topological_order,
                    "critical_paths": critical_paths,
                    "parallel_opportunities": parallel_opportunities,
                    "resource_conflicts": resource_conflicts,
                    "optimization_suggestions": optimization_suggestions
                },
                "conflicts": [conflict.__dict__ for conflict in conflicts.values()],
                "dependency_matrix": self._generate_dependency_matrix(workflow)
            }
            
        except Exception as e:
            logger.error(f"分析依赖关系失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _build_dependency_graph(self, workflow: 'EnhancedWorkflow'):
        """构建依赖图"""
        # 清空现有图
        self.dependency_graph.clear()
        self.dependency_edges.clear()
        
        # 添加所有节点
        for node in workflow.nodes:
            self.dependency_graph.add_node(node.id, node_data=node)
        
        # 添加显式依赖关系
        for edge in workflow.edges:
            await self.add_dependency(
                edge.source,
                edge.target,
                DependencyType.CONTROL,  # 默认为控制依赖
                condition=edge.condition,
                data_mapping=edge.data_mapping,
                metadata={"edge_type": edge.type}
            )
        
        # 分析隐式依赖关系
        await self._detect_implicit_dependencies(workflow)
    
    async def _detect_implicit_dependencies(self, workflow: 'EnhancedWorkflow'):
        """检测隐式依赖关系"""
        # 数据依赖分析
        await self._detect_data_dependencies(workflow)
        
        # 资源依赖分析
        await self._detect_resource_dependencies(workflow)
        
        # 时间依赖分析
        await self._detect_temporal_dependencies(workflow)
    
    async def _detect_data_dependencies(self, workflow: 'EnhancedWorkflow'):
        """检测数据依赖"""
        # 分析节点的输入输出
        node_outputs = {}
        node_inputs = {}
        
        for node in workflow.nodes:
            # 从节点配置中提取输入输出信息
            outputs = node.config.get("outputs", [])
            inputs = node.config.get("inputs", [])
            
            node_outputs[node.id] = set(outputs)
            node_inputs[node.id] = set(inputs)
        
        # 查找数据依赖
        for consumer_id, inputs in node_inputs.items():
            for producer_id, outputs in node_outputs.items():
                if producer_id != consumer_id:
                    # 检查是否有数据交集
                    shared_data = inputs.intersection(outputs)
                    if shared_data:
                        # 添加数据依赖
                        if not self.dependency_graph.has_edge(producer_id, consumer_id):
                            await self.add_dependency(
                                producer_id,
                                consumer_id,
                                DependencyType.DATA,
                                data_mapping={data: data for data in shared_data},
                                metadata={"implicit": True, "shared_data": list(shared_data)}
                            )
    
    async def _detect_resource_dependencies(self, workflow: 'EnhancedWorkflow'):
        """检测资源依赖"""
        # 分析节点的资源需求
        for node in workflow.nodes:
            resources = node.config.get("required_resources", [])
            
            # 注册节点的资源需求
            for resource in resources:
                self.resource_registry[resource].add(node.id)
                self.node_resources[node.id].add(resource)
        
        # 查找资源冲突并添加依赖
        for resource, nodes in self.resource_registry.items():
            if len(nodes) > 1:
                # 多个节点使用同一资源，需要串行化
                node_list = list(nodes)
                for i in range(len(node_list) - 1):
                    for j in range(i + 1, len(node_list)):
                        node1, node2 = node_list[i], node_list[j]
                        
                        # 添加资源依赖（选择一个方向）
                        if not self.dependency_graph.has_edge(node1, node2) and not self.dependency_graph.has_edge(node2, node1):
                            await self.add_dependency(
                                node1,
                                node2,
                                DependencyType.RESOURCE,
                                shared_resources=[resource],
                                metadata={"implicit": True, "resource_conflict": resource}
                            )
    
    async def _detect_temporal_dependencies(self, workflow: 'EnhancedWorkflow'):
        """检测时间依赖"""
        # 分析节点的时间约束
        for node in workflow.nodes:
            # 检查节点是否有时间窗口约束
            time_window = node.config.get("time_window")
            if time_window:
                # 查找其他有时间约束的节点
                for other_node in workflow.nodes:
                    if other_node.id != node.id:
                        other_time_window = other_node.config.get("time_window")
                        if other_time_window:
                            # 分析时间窗口是否冲突
                            if self._time_windows_conflict(time_window, other_time_window):
                                # 添加时间依赖
                                if not self.dependency_graph.has_edge(node.id, other_node.id) and not self.dependency_graph.has_edge(other_node.id, node.id):
                                    await self.add_dependency(
                                        node.id,
                                        other_node.id,
                                        DependencyType.TEMPORAL,
                                        metadata={"implicit": True, "time_conflict": True}
                                    )
    
    def _time_windows_conflict(self, window1: Dict[str, Any], window2: Dict[str, Any]) -> bool:
        """检查时间窗口是否冲突"""
        # 简化的时间窗口冲突检测
        start1 = window1.get("start", 0)
        end1 = window1.get("end", float('inf'))
        start2 = window2.get("start", 0)
        end2 = window2.get("end", float('inf'))
        
        # 检查是否有重叠
        return not (end1 <= start2 or end2 <= start1)
    
    async def _detect_conflicts(self) -> Dict[str, DependencyConflict]:
        """检测依赖冲突"""
        conflicts = {}
        
        # 检测循环依赖
        circular_conflicts = self._detect_circular_dependencies()
        conflicts.update(circular_conflicts)
        
        # 检测资源冲突
        resource_conflicts = self._detect_resource_conflicts()
        conflicts.update(resource_conflicts)
        
        # 检测时间冲突
        temporal_conflicts = self._detect_temporal_conflicts()
        conflicts.update(temporal_conflicts)
        
        # 检测死锁
        deadlock_conflicts = self._detect_deadlocks()
        conflicts.update(deadlock_conflicts)
        
        # 更新冲突记录
        self.detected_conflicts = conflicts
        
        return conflicts
    
    def _detect_circular_dependencies(self) -> Dict[str, DependencyConflict]:
        """检测循环依赖"""
        conflicts = {}
        
        try:
            # 查找所有简单循环
            cycles = list(nx.simple_cycles(self.dependency_graph))
            
            for i, cycle in enumerate(cycles):
                if len(cycle) <= self.max_cycle_length:
                    conflict = DependencyConflict(
                        conflict_type=ConflictType.CIRCULAR_DEPENDENCY,
                        involved_nodes=cycle,
                        description=f"检测到循环依赖: {' -> '.join(cycle + [cycle[0]])}",
                        severity="high" if len(cycle) <= 3 else "medium",
                        detection_method="simple_cycles_algorithm"
                    )
                    
                    # 添加涉及的边
                    for j in range(len(cycle)):
                        source = cycle[j]
                        target = cycle[(j + 1) % len(cycle)]
                        edge_id = f"{source}->{target}"
                        if edge_id in self.dependency_edges:
                            conflict.involved_edges.append(self.dependency_edges[edge_id])
                    
                    # 生成解决方案
                    conflict.suggested_solutions = self._generate_cycle_solutions(cycle)
                    
                    conflicts[conflict.conflict_id] = conflict
        
        except Exception as e:
            logger.error(f"检测循环依赖失败: {e}")
        
        return conflicts
    
    def _detect_resource_conflicts(self) -> Dict[str, DependencyConflict]:
        """检测资源冲突"""
        conflicts = {}
        
        for resource, nodes in self.resource_registry.items():
            if len(nodes) > 1:
                # 检查是否有并行执行的可能性
                parallel_nodes = []
                for node1 in nodes:
                    for node2 in nodes:
                        if node1 != node2:
                            # 检查两个节点是否可能并行执行
                            if not nx.has_path(self.dependency_graph, node1, node2) and not nx.has_path(self.dependency_graph, node2, node1):
                                if node1 not in parallel_nodes:
                                    parallel_nodes.append(node1)
                                if node2 not in parallel_nodes:
                                    parallel_nodes.append(node2)
                
                if len(parallel_nodes) > 1:
                    conflict = DependencyConflict(
                        conflict_type=ConflictType.RESOURCE_CONFLICT,
                        involved_nodes=parallel_nodes,
                        description=f"资源 '{resource}' 被多个可能并行的节点使用: {parallel_nodes}",
                        severity="medium",
                        detection_method="resource_analysis"
                    )
                    
                    # 生成解决方案
                    conflict.suggested_solutions = self._generate_resource_conflict_solutions(resource, parallel_nodes)
                    
                    conflicts[conflict.conflict_id] = conflict
        
        return conflicts
    
    def _detect_temporal_conflicts(self) -> Dict[str, DependencyConflict]:
        """检测时间冲突"""
        conflicts = {}
        
        # 查找有时间约束的边
        temporal_edges = [edge for edge in self.dependency_edges.values() 
                         if edge.dependency_type == DependencyType.TEMPORAL]
        
        for edge in temporal_edges:
            if edge.min_delay > 0 or edge.max_delay > 0:
                # 检查时间约束是否可能导致冲突
                if edge.max_delay > 0 and edge.max_delay < edge.min_delay:
                    conflict = DependencyConflict(
                        conflict_type=ConflictType.TEMPORAL_CONFLICT,
                        involved_nodes=[edge.source_node, edge.target_node],
                        involved_edges=[edge],
                        description=f"时间约束冲突: 最大延迟 ({edge.max_delay}) 小于最小延迟 ({edge.min_delay})",
                        severity="high",
                        detection_method="temporal_constraint_analysis"
                    )
                    
                    conflict.suggested_solutions = [
                        {
                            "type": "adjust_time_constraints",
                            "description": "调整时间约束参数",
                            "operations": [
                                {"action": "set_max_delay", "value": max(edge.min_delay, edge.max_delay)}
                            ]
                        }
                    ]
                    
                    conflicts[conflict.conflict_id] = conflict
        
        return conflicts
    
    def _detect_deadlocks(self) -> Dict[str, DependencyConflict]:
        """检测死锁"""
        conflicts = {}
        
        # 简化的死锁检测：查找强连通分量
        try:
            strongly_connected = list(nx.strongly_connected_components(self.dependency_graph))
            
            for component in strongly_connected:
                if len(component) > 1:
                    # 可能的死锁情况
                    conflict = DependencyConflict(
                        conflict_type=ConflictType.DEADLOCK,
                        involved_nodes=list(component),
                        description=f"检测到可能的死锁: 强连通分量 {list(component)}",
                        severity="critical",
                        detection_method="strongly_connected_components"
                    )
                    
                    # 生成解决方案
                    conflict.suggested_solutions = self._generate_deadlock_solutions(component)
                    
                    conflicts[conflict.conflict_id] = conflict
        
        except Exception as e:
            logger.error(f"检测死锁失败: {e}")
        
        return conflicts
    
    def _generate_cycle_solutions(self, cycle: List[str]) -> List[Dict[str, Any]]:
        """生成循环依赖解决方案"""
        solutions = []
        
        # 方案1：移除最弱的边
        weakest_edge = None
        min_weight = float('inf')
        
        for i in range(len(cycle)):
            source = cycle[i]
            target = cycle[(i + 1) % len(cycle)]
            edge_id = f"{source}->{target}"
            
            if edge_id in self.dependency_edges:
                edge = self.dependency_edges[edge_id]
                if edge.weight < min_weight:
                    min_weight = edge.weight
                    weakest_edge = edge
        
        if weakest_edge:
            solutions.append({
                "type": "remove_weakest_edge",
                "description": f"移除权重最小的边: {weakest_edge.source_node} -> {weakest_edge.target_node}",
                "operations": [
                    {"action": "remove_edge", "source": weakest_edge.source_node, "target": weakest_edge.target_node}
                ],
                "impact": "low"
            })
        
        # 方案2：添加条件依赖
        solutions.append({
            "type": "add_conditional_dependency",
            "description": "将部分依赖转换为条件依赖",
            "operations": [
                {"action": "add_condition", "edge": f"{cycle[0]}->{cycle[1]}", "condition": "runtime_check"}
            ],
            "impact": "medium"
        })
        
        # 方案3：重新设计工作流
        solutions.append({
            "type": "redesign_workflow",
            "description": "重新设计工作流结构以消除循环",
            "operations": [
                {"action": "manual_intervention", "description": "需要人工重新设计工作流"}
            ],
            "impact": "high"
        })
        
        return solutions
    
    def _generate_resource_conflict_solutions(self, resource: str, nodes: List[str]) -> List[Dict[str, Any]]:
        """生成资源冲突解决方案"""
        solutions = []
        
        # 方案1：资源池化
        solutions.append({
            "type": "resource_pooling",
            "description": f"为资源 '{resource}' 创建资源池",
            "operations": [
                {"action": "create_resource_pool", "resource": resource, "pool_size": len(nodes)}
            ],
            "impact": "low"
        })
        
        # 方案2：串行化执行
        solutions.append({
            "type": "serialize_execution",
            "description": "强制串行执行使用相同资源的节点",
            "operations": [
                {"action": "add_dependencies", "nodes": nodes, "type": "serial"}
            ],
            "impact": "medium"
        })
        
        # 方案3：资源复制
        solutions.append({
            "type": "resource_replication",
            "description": f"复制资源 '{resource}' 以支持并行访问",
            "operations": [
                {"action": "replicate_resource", "resource": resource, "copies": len(nodes)}
            ],
            "impact": "high"
        })
        
        return solutions
    
    def _generate_deadlock_solutions(self, component: Set[str]) -> List[Dict[str, Any]]:
        """生成死锁解决方案"""
        solutions = []
        
        # 方案1：打破循环
        solutions.append({
            "type": "break_cycle",
            "description": "打破强连通分量中的循环依赖",
            "operations": [
                {"action": "analyze_and_remove_edges", "component": list(component)}
            ],
            "impact": "medium"
        })
        
        # 方案2：超时机制
        solutions.append({
            "type": "timeout_mechanism",
            "description": "添加超时机制防止死锁",
            "operations": [
                {"action": "add_timeout", "nodes": list(component), "timeout": 300}
            ],
            "impact": "low"
        })
        
        return solutions
    
    def _calculate_topological_order(self) -> List[List[str]]:
        """计算拓扑排序"""
        try:
            if nx.is_directed_acyclic_graph(self.dependency_graph):
                # 分层拓扑排序
                layers = []
                remaining_graph = self.dependency_graph.copy()
                
                while remaining_graph.nodes():
                    # 找到入度为0的节点
                    zero_in_degree = [node for node in remaining_graph.nodes() 
                                    if remaining_graph.in_degree(node) == 0]
                    
                    if not zero_in_degree:
                        # 剩余的都是循环依赖
                        layers.append(list(remaining_graph.nodes()))
                        break
                    
                    layers.append(zero_in_degree)
                    remaining_graph.remove_nodes_from(zero_in_degree)
                
                return layers
            else:
                # 有循环依赖，返回所有节点
                return [list(self.dependency_graph.nodes())]
        
        except Exception as e:
            logger.error(f"计算拓扑排序失败: {e}")
            return []
    
    def _identify_critical_paths(self) -> List[Dict[str, Any]]:
        """识别关键路径"""
        critical_paths = []
        
        try:
            # 查找所有简单路径
            source_nodes = [node for node in self.dependency_graph.nodes() 
                          if self.dependency_graph.in_degree(node) == 0]
            sink_nodes = [node for node in self.dependency_graph.nodes() 
                         if self.dependency_graph.out_degree(node) == 0]
            
            for source in source_nodes:
                for sink in sink_nodes:
                    if nx.has_path(self.dependency_graph, source, sink):
                        # 找到最长路径（关键路径）
                        try:
                            path = nx.shortest_path(self.dependency_graph, source, sink)
                            path_length = len(path) - 1
                            
                            # 计算路径权重
                            path_weight = 0
                            for i in range(len(path) - 1):
                                edge_id = f"{path[i]}->{path[i+1]}"
                                if edge_id in self.dependency_edges:
                                    path_weight += self.dependency_edges[edge_id].weight
                            
                            critical_paths.append({
                                "path": path,
                                "length": path_length,
                                "weight": path_weight,
                                "source": source,
                                "sink": sink
                            })
                        except nx.NetworkXNoPath:
                            continue
            
            # 按权重排序，返回最关键的路径
            critical_paths.sort(key=lambda x: x["weight"], reverse=True)
            
        except Exception as e:
            logger.error(f"识别关键路径失败: {e}")
        
        return critical_paths[:5]  # 返回前5条关键路径
    
    def _analyze_parallel_opportunities(self) -> List[Dict[str, Any]]:
        """分析并行机会"""
        opportunities = []
        
        try:
            # 查找可以并行执行的节点组
            topological_layers = self._calculate_topological_order()
            
            for i, layer in enumerate(topological_layers):
                if len(layer) > 1:
                    # 这一层的节点可以并行执行
                    opportunities.append({
                        "layer": i,
                        "nodes": layer,
                        "parallel_count": len(layer),
                        "opportunity_type": "topological_parallelism"
                    })
            
            # 查找独立的子图
            if not nx.is_connected(self.dependency_graph.to_undirected()):
                components = list(nx.weakly_connected_components(self.dependency_graph))
                if len(components) > 1:
                    opportunities.append({
                        "components": [list(comp) for comp in components],
                        "parallel_count": len(components),
                        "opportunity_type": "independent_components"
                    })
        
        except Exception as e:
            logger.error(f"分析并行机会失败: {e}")
        
        return opportunities
    
    def _analyze_resource_conflicts(self) -> List[Dict[str, Any]]:
        """分析资源冲突"""
        resource_conflicts = []
        
        for resource, nodes in self.resource_registry.items():
            if len(nodes) > 1:
                # 分析冲突的严重程度
                conflict_pairs = []
                for node1 in nodes:
                    for node2 in nodes:
                        if node1 != node2:
                            # 检查是否可能并行执行
                            if not nx.has_path(self.dependency_graph, node1, node2) and not nx.has_path(self.dependency_graph, node2, node1):
                                conflict_pairs.append((node1, node2))
                
                if conflict_pairs:
                    resource_conflicts.append({
                        "resource": resource,
                        "conflicting_nodes": list(nodes),
                        "conflict_pairs": conflict_pairs,
                        "severity": "high" if len(conflict_pairs) > 3 else "medium"
                    })
        
        return resource_conflicts
    
    def _generate_optimization_suggestions(self, conflicts: Dict[str, DependencyConflict], critical_paths: List[Dict[str, Any]], parallel_opportunities: List[Dict[str, Any]]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 基于冲突的建议
        if conflicts:
            suggestions.append(f"检测到 {len(conflicts)} 个依赖冲突，建议优先解决高严重级别的冲突")
            
            high_severity_conflicts = [c for c in conflicts.values() if c.severity == "high"]
            if high_severity_conflicts:
                suggestions.append(f"有 {len(high_severity_conflicts)} 个高严重级别冲突需要立即处理")
        
        # 基于关键路径的建议
        if critical_paths:
            longest_path = critical_paths[0]
            suggestions.append(f"关键路径长度为 {longest_path['length']}，考虑优化路径上的节点以减少总执行时间")
        
        # 基于并行机会的建议
        total_parallel_nodes = sum(opp.get("parallel_count", 0) for opp in parallel_opportunities)
        if total_parallel_nodes > 0:
            suggestions.append(f"发现 {total_parallel_nodes} 个节点可以并行执行，建议启用并行执行以提高效率")
        
        # 资源优化建议
        if len(self.resource_registry) > 0:
            avg_nodes_per_resource = sum(len(nodes) for nodes in self.resource_registry.values()) / len(self.resource_registry)
            if avg_nodes_per_resource > 2:
                suggestions.append("资源使用较为集中，考虑资源池化或增加资源副本")
        
        return suggestions
    
    def _generate_dependency_matrix(self, workflow: 'EnhancedWorkflow') -> List[List[int]]:
        """生成依赖矩阵"""
        nodes = [node.id for node in workflow.nodes]
        node_index = {node_id: i for i, node_id in enumerate(nodes)}
        
        matrix = [[0 for _ in range(len(nodes))] for _ in range(len(nodes))]
        
        for edge_id, edge in self.dependency_edges.items():
            if edge.source_node in node_index and edge.target_node in node_index:
                source_idx = node_index[edge.source_node]
                target_idx = node_index[edge.target_node]
                matrix[source_idx][target_idx] = 1
        
        return matrix
    
    async def resolve_conflict(self, conflict_id: str, resolution_type: str, **kwargs) -> Dict[str, Any]:
        """解决冲突"""
        try:
            if conflict_id not in self.detected_conflicts:
                return {"status": "error", "message": "冲突不存在"}
            
            conflict = self.detected_conflicts[conflict_id]
            
            # 创建解决方案
            resolution = DependencyResolution(
                conflict_id=conflict_id,
                resolution_type=resolution_type
            )
            
            # 根据解决方案类型执行操作
            if resolution_type == "remove_edge":
                source = kwargs.get("source")
                target = kwargs.get("target")
                if source and target:
                    result = await self.remove_dependency(source, target)
                    resolution.operations.append({"action": "remove_edge", "source": source, "target": target, "result": result})
            
            elif resolution_type == "add_condition":
                # 添加条件依赖
                edge_id = kwargs.get("edge_id")
                condition = kwargs.get("condition")
                if edge_id in self.dependency_edges:
                    self.dependency_edges[edge_id].condition = condition
                    resolution.operations.append({"action": "add_condition", "edge_id": edge_id, "condition": condition})
            
            elif resolution_type == "serialize_nodes":
                # 串行化节点
                nodes = kwargs.get("nodes", [])
                for i in range(len(nodes) - 1):
                    result = await self.add_dependency(nodes[i], nodes[i+1], DependencyType.CONTROL)
                    resolution.operations.append({"action": "add_dependency", "source": nodes[i], "target": nodes[i+1], "result": result})
            
            # 标记解决方案已应用
            resolution.applied = True
            resolution.applied_at = datetime.now()
            
            # 保存解决方案
            self.resolutions[resolution.resolution_id] = resolution
            
            # 重新检测冲突
            await self._detect_conflicts()
            
            logger.info(f"冲突已解决: {conflict_id} 使用方案 {resolution_type}")
            
            return {
                "status": "success",
                "conflict_id": conflict_id,
                "resolution_id": resolution.resolution_id,
                "resolution_type": resolution_type,
                "operations_count": len(resolution.operations),
                "remaining_conflicts": len(self.detected_conflicts)
            }
            
        except Exception as e:
            logger.error(f"解决冲突失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_dependency_status(self) -> Dict[str, Any]:
        """获取依赖管理状态"""
        return {
            "total_nodes": self.dependency_graph.number_of_nodes(),
            "total_edges": self.dependency_graph.number_of_edges(),
            "dependency_types": {
                dep_type.value: len([edge for edge in self.dependency_edges.values() 
                                  if edge.dependency_type == dep_type])
                for dep_type in DependencyType
            },
            "conflicts": {
                "total": len(self.detected_conflicts),
                "by_type": {
                    conflict_type.value: len([c for c in self.detected_conflicts.values() 
                                            if c.conflict_type == conflict_type])
                    for conflict_type in ConflictType
                },
                "by_severity": {
                    severity: len([c for c in self.detected_conflicts.values() 
                                 if c.severity == severity])
                    for severity in ["low", "medium", "high", "critical"]
                }
            },
            "resolutions": {
                "total": len(self.resolutions),
                "applied": len([r for r in self.resolutions.values() if r.applied])
            },
            "resources": {
                "total_resources": len(self.resource_registry),
                "total_resource_usage": sum(len(nodes) for nodes in self.resource_registry.values()),
                "resource_conflicts": len([resource for resource, nodes in self.resource_registry.items() if len(nodes) > 1])
            },
            "graph_properties": {
                "is_dag": nx.is_directed_acyclic_graph(self.dependency_graph),
                "is_connected": nx.is_weakly_connected(self.dependency_graph) if self.dependency_graph.nodes() else False,
                "strongly_connected_components": len(list(nx.strongly_connected_components(self.dependency_graph)))
            }
        }

