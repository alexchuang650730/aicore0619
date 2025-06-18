#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行执行调度器
Parallel Execution Scheduler

智能调度工作流节点的并行执行，优化资源利用率
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import heapq
from collections import defaultdict, deque

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulingStrategy(Enum):
    """调度策略"""
    FIFO = "fifo"  # 先进先出
    PRIORITY = "priority"  # 优先级调度
    SHORTEST_JOB_FIRST = "sjf"  # 最短作业优先
    ROUND_ROBIN = "round_robin"  # 轮转调度
    ADAPTIVE = "adaptive"  # 自适应调度

class ResourceType(Enum):
    """资源类型"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    GPU = "gpu"
    NETWORK = "network"

@dataclass
class ResourcePool:
    """资源池"""
    cpu_cores: float = 8.0
    memory_mb: int = 16384
    disk_mb: int = 102400
    gpu_count: int = 0
    network_bandwidth: int = 1000
    
    # 当前使用情况
    used_cpu: float = 0.0
    used_memory: int = 0
    used_disk: int = 0
    used_gpu: int = 0
    used_network: int = 0
    
    def can_allocate(self, cpu: float, memory: int, disk: int = 0, gpu: int = 0, network: int = 0) -> bool:
        """检查是否可以分配资源"""
        return (
            self.used_cpu + cpu <= self.cpu_cores and
            self.used_memory + memory <= self.memory_mb and
            self.used_disk + disk <= self.disk_mb and
            self.used_gpu + gpu <= self.gpu_count and
            self.used_network + network <= self.network_bandwidth
        )
    
    def allocate(self, cpu: float, memory: int, disk: int = 0, gpu: int = 0, network: int = 0) -> bool:
        """分配资源"""
        if self.can_allocate(cpu, memory, disk, gpu, network):
            self.used_cpu += cpu
            self.used_memory += memory
            self.used_disk += disk
            self.used_gpu += gpu
            self.used_network += network
            return True
        return False
    
    def release(self, cpu: float, memory: int, disk: int = 0, gpu: int = 0, network: int = 0):
        """释放资源"""
        self.used_cpu = max(0, self.used_cpu - cpu)
        self.used_memory = max(0, self.used_memory - memory)
        self.used_disk = max(0, self.used_disk - disk)
        self.used_gpu = max(0, self.used_gpu - gpu)
        self.used_network = max(0, self.used_network - network)
    
    def get_utilization(self) -> Dict[str, float]:
        """获取资源利用率"""
        return {
            "cpu": self.used_cpu / self.cpu_cores if self.cpu_cores > 0 else 0,
            "memory": self.used_memory / self.memory_mb if self.memory_mb > 0 else 0,
            "disk": self.used_disk / self.disk_mb if self.disk_mb > 0 else 0,
            "gpu": self.used_gpu / self.gpu_count if self.gpu_count > 0 else 0,
            "network": self.used_network / self.network_bandwidth if self.network_bandwidth > 0 else 0
        }

@dataclass
class ExecutionTask:
    """执行任务"""
    task_id: str
    node_id: str
    workflow_id: str
    
    # 资源需求
    cpu_requirement: float
    memory_requirement: int
    disk_requirement: int = 0
    gpu_requirement: int = 0
    network_requirement: int = 0
    
    # 调度信息
    priority: int = 5  # 1-10，数字越小优先级越高
    estimated_duration: int = 300  # 预估执行时间（秒）
    timeout: int = 3600  # 超时时间
    retry_count: int = 3
    
    # 依赖关系
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    
    # 并行配置
    can_parallel: bool = True
    parallel_group: Optional[str] = None
    max_parallel_instances: int = 1
    
    # 状态信息
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 执行结果
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def get_wait_time(self) -> float:
        """获取等待时间"""
        if self.scheduled_at:
            return (self.scheduled_at - self.created_at).total_seconds()
        return (datetime.now() - self.created_at).total_seconds()
    
    def get_execution_time(self) -> float:
        """获取执行时间"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return 0

@dataclass
class ExecutionPlan:
    """执行计划"""
    workflow_id: str
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 任务分组
    sequential_groups: List[List[str]] = field(default_factory=list)
    parallel_groups: List[List[str]] = field(default_factory=list)
    
    # 资源分配
    resource_allocation: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # 时间估算
    estimated_total_time: int = 0
    estimated_parallel_time: int = 0
    
    # 优化信息
    optimization_applied: List[str] = field(default_factory=list)
    bottlenecks: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)

class ParallelExecutionScheduler:
    """并行执行调度器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 初始化资源池
        self.resource_pool = ResourcePool(
            cpu_cores=self.config.get("cpu_cores", 8.0),
            memory_mb=self.config.get("memory_mb", 16384),
            disk_mb=self.config.get("disk_mb", 102400),
            gpu_count=self.config.get("gpu_count", 0),
            network_bandwidth=self.config.get("network_bandwidth", 1000)
        )
        
        # 调度配置
        self.scheduling_strategy = SchedulingStrategy(self.config.get("scheduling_strategy", "adaptive"))
        self.max_concurrent_tasks = self.config.get("max_concurrent_tasks", 10)
        self.resource_utilization_threshold = self.config.get("resource_utilization_threshold", 0.8)
        
        # 任务队列和状态
        self.task_queue = []  # 优先级队列
        self.running_tasks: Dict[str, ExecutionTask] = {}
        self.completed_tasks: Dict[str, ExecutionTask] = {}
        self.failed_tasks: Dict[str, ExecutionTask] = {}
        
        # 调度状态
        self.scheduler_running = False
        self.scheduler_task = None
        
        # 统计信息
        self.metrics = {
            "tasks_scheduled": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_wait_time": 0,
            "total_execution_time": 0,
            "resource_utilization_history": []
        }
        
        logger.info("ParallelExecutionScheduler 初始化完成")
    
    async def create_execution_plan(self, workflow: 'EnhancedWorkflow') -> Dict[str, Any]:
        """创建执行计划"""
        try:
            # 分析工作流结构
            dependency_graph = self._build_dependency_graph(workflow)
            
            # 计算拓扑排序
            topological_order = self._topological_sort(dependency_graph)
            
            # 识别并行组
            parallel_groups = self._identify_parallel_groups(workflow, dependency_graph)
            
            # 计算资源需求
            resource_requirements = self._calculate_resource_requirements(workflow)
            
            # 估算执行时间
            time_estimates = self._estimate_execution_times(workflow, parallel_groups)
            
            # 识别瓶颈
            bottlenecks = self._identify_bottlenecks(workflow, dependency_graph, resource_requirements)
            
            # 应用优化策略
            optimizations = self._apply_optimization_strategies(workflow, parallel_groups, resource_requirements)
            
            # 创建执行计划
            execution_plan = ExecutionPlan(
                workflow_id=workflow.id,
                sequential_groups=topological_order,
                parallel_groups=parallel_groups,
                resource_allocation=resource_requirements,
                estimated_total_time=time_estimates["total_time"],
                estimated_parallel_time=time_estimates["parallel_time"],
                optimization_applied=optimizations,
                bottlenecks=bottlenecks
            )
            
            return {
                "status": "success",
                "execution_plan": {
                    "plan_id": execution_plan.plan_id,
                    "workflow_id": execution_plan.workflow_id,
                    "sequential_groups": execution_plan.sequential_groups,
                    "parallel_groups": execution_plan.parallel_groups,
                    "resource_allocation": execution_plan.resource_allocation,
                    "estimated_total_time": execution_plan.estimated_total_time,
                    "estimated_parallel_time": execution_plan.estimated_parallel_time,
                    "optimization_applied": execution_plan.optimization_applied,
                    "bottlenecks": execution_plan.bottlenecks,
                    "created_at": execution_plan.created_at.isoformat()
                },
                "resource_requirements": resource_requirements,
                "time_estimates": time_estimates,
                "optimization_recommendations": self._generate_optimization_recommendations(workflow, bottlenecks)
            }
            
        except Exception as e:
            logger.error(f"创建执行计划失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _build_dependency_graph(self, workflow: 'EnhancedWorkflow') -> Dict[str, Set[str]]:
        """构建依赖图"""
        graph = defaultdict(set)
        
        # 初始化所有节点
        for node in workflow.nodes:
            graph[node.id] = set()
        
        # 添加依赖关系
        for edge in workflow.edges:
            graph[edge.target].add(edge.source)
        
        return dict(graph)
    
    def _topological_sort(self, dependency_graph: Dict[str, Set[str]]) -> List[List[str]]:
        """拓扑排序，返回分层结果"""
        in_degree = {node: len(deps) for node, deps in dependency_graph.items()}
        layers = []
        
        while in_degree:
            # 找到入度为0的节点
            current_layer = [node for node, degree in in_degree.items() if degree == 0]
            
            if not current_layer:
                # 检测到循环依赖
                remaining_nodes = list(in_degree.keys())
                logger.warning(f"检测到循环依赖: {remaining_nodes}")
                layers.append(remaining_nodes)
                break
            
            layers.append(current_layer)
            
            # 移除当前层的节点并更新入度
            for node in current_layer:
                del in_degree[node]
                
                # 更新依赖于当前节点的其他节点的入度
                for other_node, deps in dependency_graph.items():
                    if node in deps and other_node in in_degree:
                        in_degree[other_node] -= 1
        
        return layers
    
    def _identify_parallel_groups(self, workflow: 'EnhancedWorkflow', dependency_graph: Dict[str, Set[str]]) -> List[List[str]]:
        """识别可并行执行的节点组"""
        parallel_groups = []
        
        # 按并行组分类
        parallel_group_map = defaultdict(list)
        independent_nodes = []
        
        for node in workflow.nodes:
            if node.can_parallel and node.parallel_group:
                parallel_group_map[node.parallel_group].append(node.id)
            elif node.can_parallel:
                independent_nodes.append(node.id)
        
        # 添加显式并行组
        for group_name, node_ids in parallel_group_map.items():
            if len(node_ids) > 1:
                parallel_groups.append(node_ids)
        
        # 分析独立节点的并行可能性
        if independent_nodes:
            # 按层级分组独立节点
            layers = self._topological_sort({node_id: dependency_graph[node_id] for node_id in independent_nodes})
            for layer in layers:
                if len(layer) > 1:
                    parallel_groups.append(layer)
        
        return parallel_groups
    
    def _calculate_resource_requirements(self, workflow: 'EnhancedWorkflow') -> Dict[str, Dict[str, Any]]:
        """计算资源需求"""
        resource_requirements = {}
        
        for node in workflow.nodes:
            resource_requirements[node.id] = {
                "cpu": node.cpu_requirement,
                "memory": node.memory_requirement,
                "disk": node.disk_requirement,
                "gpu": node.config.get("gpu_requirement", 0),
                "network": node.config.get("network_requirement", 0),
                "estimated_duration": self._estimate_node_duration(node)
            }
        
        return resource_requirements
    
    def _estimate_node_duration(self, node: 'WorkflowNode') -> int:
        """估算节点执行时间"""
        # 基于节点类型的基础时间
        base_times = {
            "requirement_analysis": 300,
            "architecture_design": 600,
            "code_implementation": 1800,
            "unit_testing": 300,
            "integration_testing": 600,
            "deployment_execution": 900,
            "data_processing": 1200,
            "model_training": 3600,
            "validation": 300
        }
        
        # 查找匹配的基础时间
        estimated_time = 300  # 默认5分钟
        for node_type, base_time in base_times.items():
            if node_type in node.type:
                estimated_time = base_time
                break
        
        # 根据资源需求调整
        if node.cpu_requirement > 2.0:
            estimated_time = int(estimated_time * 0.8)  # 更多CPU，更快执行
        if node.memory_requirement > 4096:
            estimated_time = int(estimated_time * 0.9)  # 更多内存，稍快执行
        
        return min(estimated_time, node.timeout)
    
    def _estimate_execution_times(self, workflow: 'EnhancedWorkflow', parallel_groups: List[List[str]]) -> Dict[str, int]:
        """估算执行时间"""
        node_durations = {}
        for node in workflow.nodes:
            node_durations[node.id] = self._estimate_node_duration(node)
        
        # 计算顺序执行总时间
        total_time = sum(node_durations.values())
        
        # 计算并行执行时间
        parallel_time = total_time
        
        # 考虑并行组的时间节省
        for group in parallel_groups:
            if len(group) > 1:
                group_times = [node_durations[node_id] for node_id in group]
                sequential_time = sum(group_times)
                parallel_time_for_group = max(group_times)
                time_saved = sequential_time - parallel_time_for_group
                parallel_time -= time_saved
        
        return {
            "total_time": total_time,
            "parallel_time": parallel_time,
            "time_saved": total_time - parallel_time,
            "parallelization_efficiency": (total_time - parallel_time) / total_time if total_time > 0 else 0
        }
    
    def _identify_bottlenecks(self, workflow: 'EnhancedWorkflow', dependency_graph: Dict[str, Set[str]], resource_requirements: Dict[str, Dict[str, Any]]) -> List[str]:
        """识别瓶颈"""
        bottlenecks = []
        
        # 1. 资源瓶颈：资源需求超过可用资源的节点
        for node in workflow.nodes:
            req = resource_requirements[node.id]
            if (req["cpu"] > self.resource_pool.cpu_cores or
                req["memory"] > self.resource_pool.memory_mb or
                req["gpu"] > self.resource_pool.gpu_count):
                bottlenecks.append(f"resource_bottleneck:{node.id}")
        
        # 2. 依赖瓶颈：被很多节点依赖的关键路径节点
        dependency_count = defaultdict(int)
        for node_id, deps in dependency_graph.items():
            for dep in deps:
                dependency_count[dep] += 1
        
        # 找出依赖度最高的节点
        if dependency_count:
            max_deps = max(dependency_count.values())
            for node_id, count in dependency_count.items():
                if count >= max_deps * 0.8:  # 依赖度超过80%最大值的节点
                    bottlenecks.append(f"dependency_bottleneck:{node_id}")
        
        # 3. 时间瓶颈：执行时间最长的节点
        max_duration = 0
        longest_node = None
        for node in workflow.nodes:
            duration = self._estimate_node_duration(node)
            if duration > max_duration:
                max_duration = duration
                longest_node = node.id
        
        if longest_node and max_duration > 1800:  # 超过30分钟
            bottlenecks.append(f"time_bottleneck:{longest_node}")
        
        return bottlenecks
    
    def _apply_optimization_strategies(self, workflow: 'EnhancedWorkflow', parallel_groups: List[List[str]], resource_requirements: Dict[str, Dict[str, Any]]) -> List[str]:
        """应用优化策略"""
        optimizations = []
        
        # 1. 并行化优化
        if parallel_groups:
            optimizations.append("parallel_execution_enabled")
        
        # 2. 资源优化
        total_cpu = sum(req["cpu"] for req in resource_requirements.values())
        if total_cpu > self.resource_pool.cpu_cores:
            optimizations.append("resource_scheduling_applied")
        
        # 3. 缓存优化
        similar_nodes = self._find_similar_nodes(workflow)
        if similar_nodes:
            optimizations.append("result_caching_enabled")
        
        # 4. 预取优化
        data_nodes = [node for node in workflow.nodes if "data" in node.type]
        if data_nodes:
            optimizations.append("data_prefetching_enabled")
        
        return optimizations
    
    def _find_similar_nodes(self, workflow: 'EnhancedWorkflow') -> List[List[str]]:
        """查找相似节点（可以共享缓存）"""
        similar_groups = []
        node_types = defaultdict(list)
        
        for node in workflow.nodes:
            node_types[node.type].append(node.id)
        
        for node_type, node_ids in node_types.items():
            if len(node_ids) > 1:
                similar_groups.append(node_ids)
        
        return similar_groups
    
    def _generate_optimization_recommendations(self, workflow: 'EnhancedWorkflow', bottlenecks: List[str]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck.startswith("resource_bottleneck"):
                recommendations.append("考虑增加计算资源或优化资源使用")
            elif bottleneck.startswith("dependency_bottleneck"):
                recommendations.append("考虑重构工作流以减少关键路径依赖")
            elif bottleneck.startswith("time_bottleneck"):
                recommendations.append("考虑拆分长时间运行的任务或增加并行度")
        
        # 通用建议
        if len(workflow.nodes) > 10:
            recommendations.append("考虑将大型工作流拆分为多个子工作流")
        
        parallel_nodes = [node for node in workflow.nodes if node.can_parallel]
        if len(parallel_nodes) < len(workflow.nodes) * 0.5:
            recommendations.append("考虑增加更多节点的并行执行能力")
        
        return recommendations
    
    async def execute_workflow(self, workflow: 'EnhancedWorkflow', execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流"""
        try:
            # 创建执行任务
            tasks = self._create_execution_tasks(workflow)
            
            # 启动调度器
            await self._start_scheduler()
            
            # 提交任务到队列
            for task in tasks:
                await self._submit_task(task)
            
            # 等待所有任务完成
            result = await self._wait_for_completion(workflow.id, execution_context)
            
            # 停止调度器
            await self._stop_scheduler()
            
            return result
            
        except Exception as e:
            logger.error(f"执行工作流失败: {e}")
            await self._stop_scheduler()
            return {"status": "error", "message": str(e)}
    
    def _create_execution_tasks(self, workflow: 'EnhancedWorkflow') -> List[ExecutionTask]:
        """创建执行任务"""
        tasks = []
        
        for node in workflow.nodes:
            # 获取依赖关系
            dependencies = set(workflow.get_dependencies(node.id))
            dependents = set(workflow.get_dependents(node.id))
            
            task = ExecutionTask(
                task_id=f"task_{node.id}",
                node_id=node.id,
                workflow_id=workflow.id,
                cpu_requirement=node.cpu_requirement,
                memory_requirement=node.memory_requirement,
                disk_requirement=node.disk_requirement,
                gpu_requirement=node.config.get("gpu_requirement", 0),
                network_requirement=node.config.get("network_requirement", 0),
                priority=self._calculate_task_priority(node, dependencies, dependents),
                estimated_duration=self._estimate_node_duration(node),
                timeout=node.timeout,
                retry_count=node.retry_count,
                dependencies=dependencies,
                dependents=dependents,
                can_parallel=node.can_parallel,
                parallel_group=node.parallel_group
            )
            
            tasks.append(task)
        
        return tasks
    
    def _calculate_task_priority(self, node: 'WorkflowNode', dependencies: Set[str], dependents: Set[str]) -> int:
        """计算任务优先级"""
        # 基础优先级
        priority = 5
        
        # 根据依赖数量调整（被依赖越多，优先级越高）
        priority -= len(dependents)
        
        # 根据节点类型调整
        if "critical" in node.type or "important" in node.type:
            priority -= 2
        elif "optional" in node.type:
            priority += 2
        
        # 确保优先级在合理范围内
        return max(1, min(10, priority))
    
    async def _start_scheduler(self):
        """启动调度器"""
        if not self.scheduler_running:
            self.scheduler_running = True
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            logger.info("调度器已启动")
    
    async def _stop_scheduler(self):
        """停止调度器"""
        if self.scheduler_running:
            self.scheduler_running = False
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            logger.info("调度器已停止")
    
    async def _scheduler_loop(self):
        """调度器主循环"""
        try:
            while self.scheduler_running:
                # 检查是否有可执行的任务
                await self._schedule_ready_tasks()
                
                # 检查运行中任务的状态
                await self._check_running_tasks()
                
                # 更新资源利用率统计
                self._update_resource_metrics()
                
                # 短暂休眠
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("调度器循环被取消")
        except Exception as e:
            logger.error(f"调度器循环异常: {e}")
    
    async def _submit_task(self, task: ExecutionTask):
        """提交任务到队列"""
        # 根据调度策略插入任务
        if self.scheduling_strategy == SchedulingStrategy.PRIORITY:
            heapq.heappush(self.task_queue, (task.priority, task.created_at, task))
        else:
            self.task_queue.append(task)
        
        self.metrics["tasks_scheduled"] += 1
        logger.info(f"任务已提交: {task.task_id}")
    
    async def _schedule_ready_tasks(self):
        """调度就绪的任务"""
        if not self.task_queue:
            return
        
        # 检查资源可用性
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            return
        
        # 获取下一个任务
        if self.scheduling_strategy == SchedulingStrategy.PRIORITY:
            if self.task_queue:
                _, _, task = heapq.heappop(self.task_queue)
            else:
                return
        else:
            task = self.task_queue.pop(0)
        
        # 检查依赖是否满足
        if not self._are_dependencies_satisfied(task):
            # 重新放回队列
            await self._submit_task(task)
            return
        
        # 检查资源是否可用
        if not self.resource_pool.can_allocate(
            task.cpu_requirement,
            task.memory_requirement,
            task.disk_requirement,
            task.gpu_requirement,
            task.network_requirement
        ):
            # 重新放回队列
            await self._submit_task(task)
            return
        
        # 分配资源并启动任务
        if self.resource_pool.allocate(
            task.cpu_requirement,
            task.memory_requirement,
            task.disk_requirement,
            task.gpu_requirement,
            task.network_requirement
        ):
            await self._start_task(task)
    
    def _are_dependencies_satisfied(self, task: ExecutionTask) -> bool:
        """检查任务依赖是否满足"""
        for dep_node_id in task.dependencies:
            dep_task_id = f"task_{dep_node_id}"
            if dep_task_id not in self.completed_tasks:
                return False
        return True
    
    async def _start_task(self, task: ExecutionTask):
        """启动任务"""
        task.status = "running"
        task.scheduled_at = datetime.now()
        task.started_at = datetime.now()
        
        self.running_tasks[task.task_id] = task
        
        # 创建任务执行协程
        asyncio.create_task(self._execute_task(task))
        
        logger.info(f"任务开始执行: {task.task_id}")
    
    async def _execute_task(self, task: ExecutionTask):
        """执行任务"""
        try:
            # 模拟任务执行
            execution_time = min(task.estimated_duration, task.timeout)
            await asyncio.sleep(execution_time)
            
            # 模拟执行结果
            task.result = {
                "status": "completed",
                "output": f"任务 {task.task_id} 执行完成",
                "execution_time": execution_time
            }
            task.status = "completed"
            task.completed_at = datetime.now()
            
            # 移动到完成队列
            del self.running_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task
            
            # 释放资源
            self.resource_pool.release(
                task.cpu_requirement,
                task.memory_requirement,
                task.disk_requirement,
                task.gpu_requirement,
                task.network_requirement
            )
            
            # 更新统计
            self.metrics["tasks_completed"] += 1
            self.metrics["total_execution_time"] += task.get_execution_time()
            
            logger.info(f"任务执行完成: {task.task_id}")
            
        except Exception as e:
            # 任务执行失败
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
            
            # 移动到失败队列
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            self.failed_tasks[task.task_id] = task
            
            # 释放资源
            self.resource_pool.release(
                task.cpu_requirement,
                task.memory_requirement,
                task.disk_requirement,
                task.gpu_requirement,
                task.network_requirement
            )
            
            # 更新统计
            self.metrics["tasks_failed"] += 1
            
            logger.error(f"任务执行失败: {task.task_id}, 错误: {e}")
    
    async def _check_running_tasks(self):
        """检查运行中任务的状态"""
        current_time = datetime.now()
        timeout_tasks = []
        
        for task_id, task in self.running_tasks.items():
            if task.started_at:
                running_time = (current_time - task.started_at).total_seconds()
                if running_time > task.timeout:
                    timeout_tasks.append(task)
        
        # 处理超时任务
        for task in timeout_tasks:
            logger.warning(f"任务超时: {task.task_id}")
            task.status = "timeout"
            task.error = "任务执行超时"
            task.completed_at = current_time
            
            # 移动到失败队列
            del self.running_tasks[task.task_id]
            self.failed_tasks[task.task_id] = task
            
            # 释放资源
            self.resource_pool.release(
                task.cpu_requirement,
                task.memory_requirement,
                task.disk_requirement,
                task.gpu_requirement,
                task.network_requirement
            )
            
            self.metrics["tasks_failed"] += 1
    
    def _update_resource_metrics(self):
        """更新资源利用率统计"""
        utilization = self.resource_pool.get_utilization()
        utilization["timestamp"] = datetime.now().isoformat()
        
        self.metrics["resource_utilization_history"].append(utilization)
        
        # 保持历史记录在合理范围内
        if len(self.metrics["resource_utilization_history"]) > 1000:
            self.metrics["resource_utilization_history"] = self.metrics["resource_utilization_history"][-500:]
    
    async def _wait_for_completion(self, workflow_id: str, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """等待工作流完成"""
        start_time = datetime.now()
        timeout = execution_context.get("timeout", 3600)  # 默认1小时超时
        
        while True:
            # 检查是否所有任务都完成
            workflow_tasks = [task for task in list(self.completed_tasks.values()) + list(self.failed_tasks.values()) 
                           if task.workflow_id == workflow_id]
            
            total_tasks = len([task for task in list(self.running_tasks.values()) + list(self.completed_tasks.values()) + list(self.failed_tasks.values())
                             if task.workflow_id == workflow_id])
            
            if len(workflow_tasks) == total_tasks and not any(task.workflow_id == workflow_id for task in self.running_tasks.values()):
                # 所有任务完成
                completed_tasks = [task for task in workflow_tasks if task.status == "completed"]
                failed_tasks = [task for task in workflow_tasks if task.status in ["failed", "timeout"]]
                
                if failed_tasks:
                    return {
                        "status": "failed",
                        "workflow_id": workflow_id,
                        "completed_tasks": [task.task_id for task in completed_tasks],
                        "failed_tasks": [{"task_id": task.task_id, "error": task.error} for task in failed_tasks],
                        "execution_time": (datetime.now() - start_time).total_seconds(),
                        "metrics": self._get_workflow_metrics(workflow_id)
                    }
                else:
                    return {
                        "status": "completed",
                        "workflow_id": workflow_id,
                        "completed_tasks": [task.task_id for task in completed_tasks],
                        "execution_time": (datetime.now() - start_time).total_seconds(),
                        "metrics": self._get_workflow_metrics(workflow_id)
                    }
            
            # 检查超时
            if (datetime.now() - start_time).total_seconds() > timeout:
                return {
                    "status": "timeout",
                    "workflow_id": workflow_id,
                    "message": "工作流执行超时",
                    "execution_time": timeout,
                    "metrics": self._get_workflow_metrics(workflow_id)
                }
            
            # 短暂等待
            await asyncio.sleep(2)
    
    def _get_workflow_metrics(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流执行指标"""
        workflow_tasks = [task for task in list(self.completed_tasks.values()) + list(self.failed_tasks.values()) + list(self.running_tasks.values())
                         if task.workflow_id == workflow_id]
        
        if not workflow_tasks:
            return {}
        
        total_wait_time = sum(task.get_wait_time() for task in workflow_tasks)
        total_execution_time = sum(task.get_execution_time() for task in workflow_tasks if task.status == "completed")
        
        return {
            "total_tasks": len(workflow_tasks),
            "completed_tasks": len([task for task in workflow_tasks if task.status == "completed"]),
            "failed_tasks": len([task for task in workflow_tasks if task.status in ["failed", "timeout"]]),
            "running_tasks": len([task for task in workflow_tasks if task.status == "running"]),
            "average_wait_time": total_wait_time / len(workflow_tasks) if workflow_tasks else 0,
            "total_execution_time": total_execution_time,
            "resource_utilization": self.resource_pool.get_utilization()
        }
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            "scheduler_running": self.scheduler_running,
            "scheduling_strategy": self.scheduling_strategy.value,
            "resource_pool": {
                "total": {
                    "cpu_cores": self.resource_pool.cpu_cores,
                    "memory_mb": self.resource_pool.memory_mb,
                    "disk_mb": self.resource_pool.disk_mb,
                    "gpu_count": self.resource_pool.gpu_count
                },
                "used": {
                    "cpu": self.resource_pool.used_cpu,
                    "memory": self.resource_pool.used_memory,
                    "disk": self.resource_pool.used_disk,
                    "gpu": self.resource_pool.used_gpu
                },
                "utilization": self.resource_pool.get_utilization()
            },
            "task_queues": {
                "pending": len(self.task_queue),
                "running": len(self.running_tasks),
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks)
            },
            "metrics": self.metrics
        }

