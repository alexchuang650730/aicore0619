#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流状态管理系统
Workflow State Management System

管理工作流的状态、历史记录、持久化和恢复
"""

import json
import logging
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import pickle
import gzip
from collections import defaultdict, deque

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """工作流状态"""
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class NodeStatus(Enum):
    """节点状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

@dataclass
class StateSnapshot:
    """状态快照"""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 工作流状态
    workflow_status: WorkflowStatus = WorkflowStatus.CREATED
    workflow_data: Dict[str, Any] = field(default_factory=dict)
    
    # 节点状态
    node_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # 执行上下文
    execution_context: Dict[str, Any] = field(default_factory=dict)
    
    # 资源状态
    resource_allocation: Dict[str, Any] = field(default_factory=dict)
    
    # 错误信息
    errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # 性能指标
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["workflow_status"] = self.workflow_status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateSnapshot':
        """从字典创建"""
        snapshot = cls()
        snapshot.snapshot_id = data.get("snapshot_id", str(uuid.uuid4()))
        snapshot.workflow_id = data.get("workflow_id", "")
        snapshot.timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        snapshot.workflow_status = WorkflowStatus(data.get("workflow_status", "created"))
        snapshot.workflow_data = data.get("workflow_data", {})
        snapshot.node_states = data.get("node_states", {})
        snapshot.execution_context = data.get("execution_context", {})
        snapshot.resource_allocation = data.get("resource_allocation", {})
        snapshot.errors = data.get("errors", [])
        snapshot.metrics = data.get("metrics", {})
        return snapshot

@dataclass
class StateTransition:
    """状态转换记录"""
    transition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 转换信息
    from_status: WorkflowStatus = WorkflowStatus.CREATED
    to_status: WorkflowStatus = WorkflowStatus.CREATED
    trigger: str = ""  # 触发原因
    
    # 节点级别的转换
    node_transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    # 上下文变化
    context_changes: Dict[str, Any] = field(default_factory=dict)
    
    # 操作者信息
    operator: str = "system"
    operation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["from_status"] = self.from_status.value
        data["to_status"] = self.to_status.value
        return data

@dataclass
class WorkflowCheckpoint:
    """工作流检查点"""
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 检查点类型
    checkpoint_type: str = "manual"  # manual, auto, milestone
    description: str = ""
    
    # 状态快照
    state_snapshot: StateSnapshot = field(default_factory=StateSnapshot)
    
    # 恢复信息
    recovery_data: Dict[str, Any] = field(default_factory=dict)
    
    # 标签和元数据
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowStateManager:
    """工作流状态管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 数据库配置
        self.db_path = Path(self.config.get("db_path", "/tmp/workflow_state.db"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 内存状态缓存
        self.workflow_states: Dict[str, StateSnapshot] = {}
        self.state_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.transitions: Dict[str, List[StateTransition]] = defaultdict(list)
        self.checkpoints: Dict[str, List[WorkflowCheckpoint]] = defaultdict(list)
        
        # 配置参数
        self.max_history_size = self.config.get("max_history_size", 100)
        self.auto_checkpoint_interval = self.config.get("auto_checkpoint_interval", 300)  # 5分钟
        self.state_persistence_enabled = self.config.get("state_persistence_enabled", True)
        self.compression_enabled = self.config.get("compression_enabled", True)
        
        # 线程锁
        self.state_lock = threading.RLock()
        
        # 初始化数据库
        self._init_database()
        
        # 启动自动检查点线程
        if self.auto_checkpoint_interval > 0:
            self._start_auto_checkpoint_thread()
        
        logger.info("WorkflowStateManager 初始化完成")
    
    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建状态快照表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS state_snapshots (
                        snapshot_id TEXT PRIMARY KEY,
                        workflow_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        workflow_status TEXT NOT NULL,
                        snapshot_data BLOB,
                        compressed INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建状态转换表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS state_transitions (
                        transition_id TEXT PRIMARY KEY,
                        workflow_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        from_status TEXT NOT NULL,
                        to_status TEXT NOT NULL,
                        trigger TEXT,
                        transition_data BLOB,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建检查点表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                        checkpoint_id TEXT PRIMARY KEY,
                        workflow_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        checkpoint_type TEXT NOT NULL,
                        description TEXT,
                        checkpoint_data BLOB,
                        compressed INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_workflow_id ON state_snapshots(workflow_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON state_snapshots(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transitions_workflow_id ON state_transitions(workflow_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_workflow_id ON workflow_checkpoints(workflow_id)")
                
                conn.commit()
                logger.info("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def _start_auto_checkpoint_thread(self):
        """启动自动检查点线程"""
        def auto_checkpoint_worker():
            while True:
                try:
                    time.sleep(self.auto_checkpoint_interval)
                    self._create_auto_checkpoints()
                except Exception as e:
                    logger.error(f"自动检查点线程异常: {e}")
        
        thread = threading.Thread(target=auto_checkpoint_worker, daemon=True)
        thread.start()
        logger.info("自动检查点线程已启动")
    
    def _create_auto_checkpoints(self):
        """创建自动检查点"""
        with self.state_lock:
            for workflow_id, current_state in self.workflow_states.items():
                if current_state.workflow_status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
                    try:
                        self.create_checkpoint(
                            workflow_id,
                            checkpoint_type="auto",
                            description=f"自动检查点 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                    except Exception as e:
                        logger.error(f"创建自动检查点失败 {workflow_id}: {e}")
    
    async def create_workflow_state(self, workflow_id: str, initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建工作流状态"""
        try:
            with self.state_lock:
                # 检查是否已存在
                if workflow_id in self.workflow_states:
                    return {"status": "error", "message": "工作流状态已存在"}
                
                # 创建初始状态快照
                snapshot = StateSnapshot(
                    workflow_id=workflow_id,
                    workflow_status=WorkflowStatus.CREATED,
                    workflow_data=initial_data or {},
                    execution_context={"created_at": datetime.now().isoformat()}
                )
                
                # 保存到内存
                self.workflow_states[workflow_id] = snapshot
                self.state_history[workflow_id].append(snapshot)
                
                # 持久化
                if self.state_persistence_enabled:
                    await self._persist_snapshot(snapshot)
                
                # 记录状态转换
                transition = StateTransition(
                    workflow_id=workflow_id,
                    from_status=WorkflowStatus.CREATED,
                    to_status=WorkflowStatus.CREATED,
                    trigger="workflow_creation",
                    operation="create_workflow"
                )
                self.transitions[workflow_id].append(transition)
                
                if self.state_persistence_enabled:
                    await self._persist_transition(transition)
                
                logger.info(f"工作流状态已创建: {workflow_id}")
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "snapshot_id": snapshot.snapshot_id,
                    "current_status": snapshot.workflow_status.value
                }
                
        except Exception as e:
            logger.error(f"创建工作流状态失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def update_workflow_status(self, workflow_id: str, new_status: WorkflowStatus, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """更新工作流状态"""
        try:
            with self.state_lock:
                # 检查工作流是否存在
                if workflow_id not in self.workflow_states:
                    return {"status": "error", "message": "工作流状态不存在"}
                
                current_snapshot = self.workflow_states[workflow_id]
                old_status = current_snapshot.workflow_status
                
                # 验证状态转换的合法性
                if not self._is_valid_status_transition(old_status, new_status):
                    return {"status": "error", "message": f"无效的状态转换: {old_status.value} -> {new_status.value}"}
                
                # 创建新的状态快照
                new_snapshot = StateSnapshot(
                    workflow_id=workflow_id,
                    workflow_status=new_status,
                    workflow_data=current_snapshot.workflow_data.copy(),
                    node_states=current_snapshot.node_states.copy(),
                    execution_context={**current_snapshot.execution_context, **(context or {})},
                    resource_allocation=current_snapshot.resource_allocation.copy(),
                    errors=current_snapshot.errors.copy(),
                    metrics=current_snapshot.metrics.copy()
                )
                
                # 更新执行上下文
                new_snapshot.execution_context[f"status_changed_to_{new_status.value}_at"] = datetime.now().isoformat()
                
                # 保存到内存
                self.workflow_states[workflow_id] = new_snapshot
                self.state_history[workflow_id].append(new_snapshot)
                
                # 持久化
                if self.state_persistence_enabled:
                    await self._persist_snapshot(new_snapshot)
                
                # 记录状态转换
                transition = StateTransition(
                    workflow_id=workflow_id,
                    from_status=old_status,
                    to_status=new_status,
                    trigger=context.get("trigger", "manual") if context else "manual",
                    context_changes=context or {},
                    operation="update_status"
                )
                self.transitions[workflow_id].append(transition)
                
                if self.state_persistence_enabled:
                    await self._persist_transition(transition)
                
                logger.info(f"工作流状态已更新: {workflow_id} {old_status.value} -> {new_status.value}")
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "snapshot_id": new_snapshot.snapshot_id
                }
                
        except Exception as e:
            logger.error(f"更新工作流状态失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _is_valid_status_transition(self, from_status: WorkflowStatus, to_status: WorkflowStatus) -> bool:
        """验证状态转换的合法性"""
        # 定义合法的状态转换
        valid_transitions = {
            WorkflowStatus.CREATED: [WorkflowStatus.PLANNING, WorkflowStatus.CANCELLED],
            WorkflowStatus.PLANNING: [WorkflowStatus.READY, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED],
            WorkflowStatus.READY: [WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED],
            WorkflowStatus.RUNNING: [WorkflowStatus.PAUSED, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.TIMEOUT, WorkflowStatus.CANCELLED],
            WorkflowStatus.PAUSED: [WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED],
            WorkflowStatus.COMPLETED: [],  # 终态
            WorkflowStatus.FAILED: [WorkflowStatus.READY],  # 可以重试
            WorkflowStatus.CANCELLED: [],  # 终态
            WorkflowStatus.TIMEOUT: [WorkflowStatus.READY]  # 可以重试
        }
        
        return to_status in valid_transitions.get(from_status, [])
    
    async def update_node_state(self, workflow_id: str, node_id: str, node_state: Dict[str, Any]) -> Dict[str, Any]:
        """更新节点状态"""
        try:
            with self.state_lock:
                # 检查工作流是否存在
                if workflow_id not in self.workflow_states:
                    return {"status": "error", "message": "工作流状态不存在"}
                
                current_snapshot = self.workflow_states[workflow_id]
                
                # 创建新的状态快照
                new_snapshot = StateSnapshot(
                    workflow_id=workflow_id,
                    workflow_status=current_snapshot.workflow_status,
                    workflow_data=current_snapshot.workflow_data.copy(),
                    node_states=current_snapshot.node_states.copy(),
                    execution_context=current_snapshot.execution_context.copy(),
                    resource_allocation=current_snapshot.resource_allocation.copy(),
                    errors=current_snapshot.errors.copy(),
                    metrics=current_snapshot.metrics.copy()
                )
                
                # 更新节点状态
                new_snapshot.node_states[node_id] = {
                    **new_snapshot.node_states.get(node_id, {}),
                    **node_state,
                    "updated_at": datetime.now().isoformat()
                }
                
                # 保存到内存
                self.workflow_states[workflow_id] = new_snapshot
                self.state_history[workflow_id].append(new_snapshot)
                
                # 持久化
                if self.state_persistence_enabled:
                    await self._persist_snapshot(new_snapshot)
                
                logger.info(f"节点状态已更新: {workflow_id}/{node_id}")
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "node_id": node_id,
                    "snapshot_id": new_snapshot.snapshot_id
                }
                
        except Exception as e:
            logger.error(f"更新节点状态失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def add_error(self, workflow_id: str, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """添加错误信息"""
        try:
            with self.state_lock:
                # 检查工作流是否存在
                if workflow_id not in self.workflow_states:
                    return {"status": "error", "message": "工作流状态不存在"}
                
                current_snapshot = self.workflow_states[workflow_id]
                
                # 创建新的状态快照
                new_snapshot = StateSnapshot(
                    workflow_id=workflow_id,
                    workflow_status=current_snapshot.workflow_status,
                    workflow_data=current_snapshot.workflow_data.copy(),
                    node_states=current_snapshot.node_states.copy(),
                    execution_context=current_snapshot.execution_context.copy(),
                    resource_allocation=current_snapshot.resource_allocation.copy(),
                    errors=current_snapshot.errors.copy(),
                    metrics=current_snapshot.metrics.copy()
                )
                
                # 添加错误信息
                error_record = {
                    "error_id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    **error_info
                }
                new_snapshot.errors.append(error_record)
                
                # 保存到内存
                self.workflow_states[workflow_id] = new_snapshot
                self.state_history[workflow_id].append(new_snapshot)
                
                # 持久化
                if self.state_persistence_enabled:
                    await self._persist_snapshot(new_snapshot)
                
                logger.warning(f"错误信息已添加: {workflow_id} - {error_info.get('message', 'Unknown error')}")
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "error_id": error_record["error_id"],
                    "snapshot_id": new_snapshot.snapshot_id
                }
                
        except Exception as e:
            logger.error(f"添加错误信息失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def update_metrics(self, workflow_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """更新性能指标"""
        try:
            with self.state_lock:
                # 检查工作流是否存在
                if workflow_id not in self.workflow_states:
                    return {"status": "error", "message": "工作流状态不存在"}
                
                current_snapshot = self.workflow_states[workflow_id]
                
                # 创建新的状态快照
                new_snapshot = StateSnapshot(
                    workflow_id=workflow_id,
                    workflow_status=current_snapshot.workflow_status,
                    workflow_data=current_snapshot.workflow_data.copy(),
                    node_states=current_snapshot.node_states.copy(),
                    execution_context=current_snapshot.execution_context.copy(),
                    resource_allocation=current_snapshot.resource_allocation.copy(),
                    errors=current_snapshot.errors.copy(),
                    metrics=current_snapshot.metrics.copy()
                )
                
                # 更新指标
                new_snapshot.metrics.update(metrics)
                new_snapshot.metrics["last_updated"] = datetime.now().isoformat()
                
                # 保存到内存
                self.workflow_states[workflow_id] = new_snapshot
                self.state_history[workflow_id].append(new_snapshot)
                
                # 持久化
                if self.state_persistence_enabled:
                    await self._persist_snapshot(new_snapshot)
                
                logger.info(f"性能指标已更新: {workflow_id}")
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "snapshot_id": new_snapshot.snapshot_id
                }
                
        except Exception as e:
            logger.error(f"更新性能指标失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def create_checkpoint(self, workflow_id: str, checkpoint_type: str = "manual", description: str = "", tags: List[str] = None) -> Dict[str, Any]:
        """创建检查点"""
        try:
            with self.state_lock:
                # 检查工作流是否存在
                if workflow_id not in self.workflow_states:
                    return {"status": "error", "message": "工作流状态不存在"}
                
                current_snapshot = self.workflow_states[workflow_id]
                
                # 创建检查点
                checkpoint = WorkflowCheckpoint(
                    workflow_id=workflow_id,
                    checkpoint_type=checkpoint_type,
                    description=description or f"{checkpoint_type}检查点",
                    state_snapshot=current_snapshot,
                    tags=tags or [],
                    metadata={
                        "workflow_status": current_snapshot.workflow_status.value,
                        "node_count": len(current_snapshot.node_states),
                        "error_count": len(current_snapshot.errors)
                    }
                )
                
                # 保存到内存
                self.checkpoints[workflow_id].append(checkpoint)
                
                # 持久化
                if self.state_persistence_enabled:
                    self._persist_checkpoint(checkpoint)
                
                logger.info(f"检查点已创建: {workflow_id} - {checkpoint.checkpoint_id}")
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "checkpoint_type": checkpoint_type,
                    "description": description
                }
                
        except Exception as e:
            logger.error(f"创建检查点失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def restore_from_checkpoint(self, workflow_id: str, checkpoint_id: str) -> Dict[str, Any]:
        """从检查点恢复"""
        try:
            with self.state_lock:
                # 查找检查点
                checkpoint = None
                for cp in self.checkpoints.get(workflow_id, []):
                    if cp.checkpoint_id == checkpoint_id:
                        checkpoint = cp
                        break
                
                if not checkpoint:
                    # 尝试从数据库加载
                    checkpoint = await self._load_checkpoint(checkpoint_id)
                
                if not checkpoint:
                    return {"status": "error", "message": "检查点不存在"}
                
                # 恢复状态
                restored_snapshot = checkpoint.state_snapshot
                restored_snapshot.snapshot_id = str(uuid.uuid4())  # 生成新的快照ID
                restored_snapshot.timestamp = datetime.now()
                
                # 保存到内存
                self.workflow_states[workflow_id] = restored_snapshot
                self.state_history[workflow_id].append(restored_snapshot)
                
                # 持久化
                if self.state_persistence_enabled:
                    await self._persist_snapshot(restored_snapshot)
                
                # 记录状态转换
                transition = StateTransition(
                    workflow_id=workflow_id,
                    from_status=self.workflow_states.get(workflow_id, restored_snapshot).workflow_status,
                    to_status=restored_snapshot.workflow_status,
                    trigger="checkpoint_restore",
                    operation="restore_from_checkpoint",
                    context_changes={"checkpoint_id": checkpoint_id}
                )
                self.transitions[workflow_id].append(transition)
                
                if self.state_persistence_enabled:
                    await self._persist_transition(transition)
                
                logger.info(f"已从检查点恢复: {workflow_id} - {checkpoint_id}")
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "checkpoint_id": checkpoint_id,
                    "restored_snapshot_id": restored_snapshot.snapshot_id,
                    "restored_status": restored_snapshot.workflow_status.value
                }
                
        except Exception as e:
            logger.error(f"从检查点恢复失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_current_state(self, workflow_id: str) -> Dict[str, Any]:
        """获取当前状态"""
        try:
            with self.state_lock:
                if workflow_id not in self.workflow_states:
                    return {"status": "error", "message": "工作流状态不存在"}
                
                current_snapshot = self.workflow_states[workflow_id]
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "current_state": current_snapshot.to_dict()
                }
                
        except Exception as e:
            logger.error(f"获取当前状态失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_state_history(self, workflow_id: str, limit: int = 10) -> Dict[str, Any]:
        """获取状态历史"""
        try:
            with self.state_lock:
                if workflow_id not in self.state_history:
                    return {"status": "error", "message": "工作流状态历史不存在"}
                
                history = list(self.state_history[workflow_id])
                history.reverse()  # 最新的在前
                
                limited_history = history[:limit]
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "history": [snapshot.to_dict() for snapshot in limited_history],
                    "total_count": len(history)
                }
                
        except Exception as e:
            logger.error(f"获取状态历史失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_transitions(self, workflow_id: str, limit: int = 10) -> Dict[str, Any]:
        """获取状态转换历史"""
        try:
            with self.state_lock:
                if workflow_id not in self.transitions:
                    return {"status": "error", "message": "工作流转换历史不存在"}
                
                transitions = self.transitions[workflow_id]
                transitions.reverse()  # 最新的在前
                
                limited_transitions = transitions[:limit]
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "transitions": [transition.to_dict() for transition in limited_transitions],
                    "total_count": len(transitions)
                }
                
        except Exception as e:
            logger.error(f"获取状态转换历史失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_checkpoints(self, workflow_id: str) -> Dict[str, Any]:
        """获取检查点列表"""
        try:
            with self.state_lock:
                checkpoints = self.checkpoints.get(workflow_id, [])
                
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "checkpoints": [
                        {
                            "checkpoint_id": cp.checkpoint_id,
                            "timestamp": cp.timestamp.isoformat(),
                            "checkpoint_type": cp.checkpoint_type,
                            "description": cp.description,
                            "tags": cp.tags,
                            "metadata": cp.metadata
                        }
                        for cp in checkpoints
                    ],
                    "total_count": len(checkpoints)
                }
                
        except Exception as e:
            logger.error(f"获取检查点列表失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _persist_snapshot(self, snapshot: StateSnapshot):
        """持久化状态快照"""
        try:
            # 序列化数据
            snapshot_data = snapshot.to_dict()
            
            if self.compression_enabled:
                # 压缩数据
                serialized_data = gzip.compress(pickle.dumps(snapshot_data))
                compressed = 1
            else:
                serialized_data = pickle.dumps(snapshot_data)
                compressed = 0
            
            # 保存到数据库
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO state_snapshots 
                    (snapshot_id, workflow_id, timestamp, workflow_status, snapshot_data, compressed)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    snapshot.snapshot_id,
                    snapshot.workflow_id,
                    snapshot.timestamp.isoformat(),
                    snapshot.workflow_status.value,
                    serialized_data,
                    compressed
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"持久化状态快照失败: {e}")
    
    async def _persist_transition(self, transition: StateTransition):
        """持久化状态转换"""
        try:
            # 序列化数据
            transition_data = transition.to_dict()
            serialized_data = pickle.dumps(transition_data)
            
            # 保存到数据库
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO state_transitions 
                    (transition_id, workflow_id, timestamp, from_status, to_status, trigger, transition_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    transition.transition_id,
                    transition.workflow_id,
                    transition.timestamp.isoformat(),
                    transition.from_status.value,
                    transition.to_status.value,
                    transition.trigger,
                    serialized_data
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"持久化状态转换失败: {e}")
    
    def _persist_checkpoint(self, checkpoint: WorkflowCheckpoint):
        """持久化检查点"""
        try:
            # 序列化数据
            checkpoint_data = {
                "checkpoint_id": checkpoint.checkpoint_id,
                "workflow_id": checkpoint.workflow_id,
                "timestamp": checkpoint.timestamp.isoformat(),
                "checkpoint_type": checkpoint.checkpoint_type,
                "description": checkpoint.description,
                "state_snapshot": checkpoint.state_snapshot.to_dict(),
                "recovery_data": checkpoint.recovery_data,
                "tags": checkpoint.tags,
                "metadata": checkpoint.metadata
            }
            
            if self.compression_enabled:
                # 压缩数据
                serialized_data = gzip.compress(pickle.dumps(checkpoint_data))
                compressed = 1
            else:
                serialized_data = pickle.dumps(checkpoint_data)
                compressed = 0
            
            # 保存到数据库
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO workflow_checkpoints 
                    (checkpoint_id, workflow_id, timestamp, checkpoint_type, description, checkpoint_data, compressed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    checkpoint.checkpoint_id,
                    checkpoint.workflow_id,
                    checkpoint.timestamp.isoformat(),
                    checkpoint.checkpoint_type,
                    checkpoint.description,
                    serialized_data,
                    compressed
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"持久化检查点失败: {e}")
    
    async def _load_checkpoint(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """从数据库加载检查点"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT checkpoint_data, compressed FROM workflow_checkpoints 
                    WHERE checkpoint_id = ?
                """, (checkpoint_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                checkpoint_data, compressed = row
                
                # 反序列化数据
                if compressed:
                    data = pickle.loads(gzip.decompress(checkpoint_data))
                else:
                    data = pickle.loads(checkpoint_data)
                
                # 重建检查点对象
                checkpoint = WorkflowCheckpoint()
                checkpoint.checkpoint_id = data["checkpoint_id"]
                checkpoint.workflow_id = data["workflow_id"]
                checkpoint.timestamp = datetime.fromisoformat(data["timestamp"])
                checkpoint.checkpoint_type = data["checkpoint_type"]
                checkpoint.description = data["description"]
                checkpoint.state_snapshot = StateSnapshot.from_dict(data["state_snapshot"])
                checkpoint.recovery_data = data["recovery_data"]
                checkpoint.tags = data["tags"]
                checkpoint.metadata = data["metadata"]
                
                return checkpoint
                
        except Exception as e:
            logger.error(f"加载检查点失败: {e}")
            return None
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """清理旧数据"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.isoformat()
            
            deleted_counts = {"snapshots": 0, "transitions": 0, "checkpoints": 0}
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 清理旧的状态快照
                cursor.execute("DELETE FROM state_snapshots WHERE timestamp < ?", (cutoff_str,))
                deleted_counts["snapshots"] = cursor.rowcount
                
                # 清理旧的状态转换
                cursor.execute("DELETE FROM state_transitions WHERE timestamp < ?", (cutoff_str,))
                deleted_counts["transitions"] = cursor.rowcount
                
                # 清理旧的检查点
                cursor.execute("DELETE FROM workflow_checkpoints WHERE timestamp < ?", (cutoff_str,))
                deleted_counts["checkpoints"] = cursor.rowcount
                
                conn.commit()
            
            logger.info(f"数据清理完成: {deleted_counts}")
            
            return {
                "status": "success",
                "deleted_counts": deleted_counts,
                "cutoff_date": cutoff_str
            }
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            with self.state_lock:
                stats = {
                    "active_workflows": len(self.workflow_states),
                    "total_snapshots": sum(len(history) for history in self.state_history.values()),
                    "total_transitions": sum(len(transitions) for transitions in self.transitions.values()),
                    "total_checkpoints": sum(len(checkpoints) for checkpoints in self.checkpoints.values()),
                    "workflow_status_distribution": defaultdict(int),
                    "memory_usage": {
                        "workflow_states": len(self.workflow_states),
                        "state_history_size": sum(len(history) for history in self.state_history.values()),
                        "transitions_size": sum(len(transitions) for transitions in self.transitions.values()),
                        "checkpoints_size": sum(len(checkpoints) for checkpoints in self.checkpoints.values())
                    }
                }
                
                # 统计工作流状态分布
                for snapshot in self.workflow_states.values():
                    stats["workflow_status_distribution"][snapshot.workflow_status.value] += 1
                
                return {
                    "status": "success",
                    "statistics": dict(stats)
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"status": "error", "message": str(e)}

