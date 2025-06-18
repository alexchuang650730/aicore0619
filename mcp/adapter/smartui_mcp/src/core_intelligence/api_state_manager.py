"""
SmartUI MCP - API状态管理器

实现智能的应用状态管理、数据绑定和状态同步系统。
提供响应式状态管理、自动数据同步和智能缓存机制。
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import weakref
from pathlib import Path
import copy

from ..common import (
    IApiStateManager, EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    deep_merge, flatten_dict, unflatten_dict, AsyncLock
)


class StateChangeType(str, Enum):
    """状态变化类型枚举"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    REPLACE = "replace"
    MERGE = "merge"
    RESET = "reset"


class StatePersistenceType(str, Enum):
    """状态持久化类型枚举"""
    MEMORY = "memory"
    LOCAL_STORAGE = "local_storage"
    SESSION_STORAGE = "session_storage"
    DATABASE = "database"
    FILE = "file"
    REMOTE = "remote"


class StateAccessLevel(str, Enum):
    """状态访问级别枚举"""
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"
    READONLY = "readonly"


@dataclass
class StateMetadata:
    """状态元数据"""
    created_at: datetime
    updated_at: datetime
    version: int
    access_level: StateAccessLevel
    persistence_type: StatePersistenceType
    tags: List[str]
    description: str
    schema: Optional[Dict[str, Any]] = None
    validators: List[str] = None
    
    def __post_init__(self):
        if self.validators is None:
            self.validators = []


@dataclass
class StateChange:
    """状态变化记录"""
    change_id: str
    path: str
    change_type: StateChangeType
    old_value: Any
    new_value: Any
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.change_id is None:
            self.change_id = generate_id("change_")


@dataclass
class StateWatcher:
    """状态监听器"""
    watcher_id: str
    path: str
    callback: Callable
    filter_func: Optional[Callable] = None
    debounce_ms: int = 0
    immediate: bool = True
    deep: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.watcher_id is None:
            self.watcher_id = generate_id("watcher_")
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class StateBinding:
    """状态绑定"""
    binding_id: str
    source_path: str
    target_path: str
    transform_func: Optional[Callable] = None
    bidirectional: bool = False
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.binding_id is None:
            self.binding_id = generate_id("binding_")
        if self.created_at is None:
            self.created_at = datetime.now()


class StateValidator:
    """状态验证器"""
    
    def __init__(self):
        self.validators: Dict[str, Callable] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}
    
    def register_validator(self, name: str, validator_func: Callable[[Any], bool]) -> None:
        """注册验证器"""
        self.validators[name] = validator_func
    
    def register_schema(self, name: str, schema: Dict[str, Any]) -> None:
        """注册JSON Schema"""
        self.schemas[name] = schema
    
    def validate(self, value: Any, validators: List[str]) -> Tuple[bool, List[str]]:
        """验证值"""
        errors = []
        
        for validator_name in validators:
            if validator_name in self.validators:
                try:
                    if not self.validators[validator_name](value):
                        errors.append(f"Validation failed: {validator_name}")
                except Exception as e:
                    errors.append(f"Validator error ({validator_name}): {str(e)}")
            
            elif validator_name in self.schemas:
                # JSON Schema验证
                try:
                    import jsonschema
                    jsonschema.validate(value, self.schemas[validator_name])
                except ImportError:
                    errors.append("jsonschema library not available")
                except Exception as e:
                    errors.append(f"Schema validation failed: {str(e)}")
            
            else:
                errors.append(f"Unknown validator: {validator_name}")
        
        return len(errors) == 0, errors


class StatePersistence:
    """状态持久化管理器"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd() / "state_data"
        self.base_path.mkdir(exist_ok=True)
        
        self.persistence_handlers: Dict[StatePersistenceType, Callable] = {
            StatePersistenceType.MEMORY: self._handle_memory_persistence,
            StatePersistenceType.FILE: self._handle_file_persistence,
            StatePersistenceType.LOCAL_STORAGE: self._handle_local_storage_persistence,
            StatePersistenceType.SESSION_STORAGE: self._handle_session_storage_persistence,
        }
    
    async def save_state(
        self,
        path: str,
        value: Any,
        persistence_type: StatePersistenceType,
        metadata: StateMetadata
    ) -> bool:
        """保存状态"""
        try:
            handler = self.persistence_handlers.get(persistence_type)
            if handler:
                return await handler("save", path, value, metadata)
            return False
        except Exception as e:
            logging.error(f"Error saving state {path}: {e}")
            return False
    
    async def load_state(
        self,
        path: str,
        persistence_type: StatePersistenceType,
        metadata: StateMetadata
    ) -> Tuple[bool, Any]:
        """加载状态"""
        try:
            handler = self.persistence_handlers.get(persistence_type)
            if handler:
                return await handler("load", path, None, metadata)
            return False, None
        except Exception as e:
            logging.error(f"Error loading state {path}: {e}")
            return False, None
    
    async def delete_state(
        self,
        path: str,
        persistence_type: StatePersistenceType,
        metadata: StateMetadata
    ) -> bool:
        """删除状态"""
        try:
            handler = self.persistence_handlers.get(persistence_type)
            if handler:
                return await handler("delete", path, None, metadata)
            return False
        except Exception as e:
            logging.error(f"Error deleting state {path}: {e}")
            return False
    
    async def _handle_memory_persistence(
        self,
        operation: str,
        path: str,
        value: Any,
        metadata: StateMetadata
    ) -> Union[bool, Tuple[bool, Any]]:
        """处理内存持久化"""
        # 内存持久化不需要实际操作
        if operation == "save":
            return True
        elif operation == "load":
            return False, None  # 内存中没有持久化数据
        elif operation == "delete":
            return True
        return False
    
    async def _handle_file_persistence(
        self,
        operation: str,
        path: str,
        value: Any,
        metadata: StateMetadata
    ) -> Union[bool, Tuple[bool, Any]]:
        """处理文件持久化"""
        file_path = self.base_path / f"{path.replace('/', '_')}.json"
        
        if operation == "save":
            try:
                data = {
                    "value": value,
                    "metadata": asdict(metadata),
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                return True
            except Exception as e:
                logging.error(f"Error saving to file {file_path}: {e}")
                return False
        
        elif operation == "load":
            try:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return True, data["value"]
                return False, None
            except Exception as e:
                logging.error(f"Error loading from file {file_path}: {e}")
                return False, None
        
        elif operation == "delete":
            try:
                if file_path.exists():
                    file_path.unlink()
                return True
            except Exception as e:
                logging.error(f"Error deleting file {file_path}: {e}")
                return False
        
        return False
    
    async def _handle_local_storage_persistence(
        self,
        operation: str,
        path: str,
        value: Any,
        metadata: StateMetadata
    ) -> Union[bool, Tuple[bool, Any]]:
        """处理本地存储持久化"""
        # 这里应该与前端的localStorage交互
        # 在服务器端，我们可以模拟或使用文件系统
        return await self._handle_file_persistence(operation, f"localStorage_{path}", value, metadata)
    
    async def _handle_session_storage_persistence(
        self,
        operation: str,
        path: str,
        value: Any,
        metadata: StateMetadata
    ) -> Union[bool, Tuple[bool, Any]]:
        """处理会话存储持久化"""
        # 这里应该与前端的sessionStorage交互
        # 在服务器端，我们可以模拟或使用内存
        return await self._handle_memory_persistence(operation, path, value, metadata)


class StateComputer:
    """状态计算器"""
    
    def __init__(self):
        self.computed_states: Dict[str, Dict[str, Any]] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependency_graph: Dict[str, Set[str]] = defaultdict(set)
    
    def register_computed_state(
        self,
        path: str,
        dependencies: List[str],
        compute_func: Callable,
        cache: bool = True
    ) -> None:
        """注册计算状态"""
        self.computed_states[path] = {
            "dependencies": dependencies,
            "compute_func": compute_func,
            "cache": cache,
            "cached_value": None,
            "last_computed": None,
            "dirty": True
        }
        
        # 更新依赖图
        for dep in dependencies:
            self.dependency_graph[dep].add(path)
            self.reverse_dependency_graph[path].add(dep)
    
    def unregister_computed_state(self, path: str) -> None:
        """取消注册计算状态"""
        if path in self.computed_states:
            # 清理依赖图
            dependencies = self.computed_states[path]["dependencies"]
            for dep in dependencies:
                self.dependency_graph[dep].discard(path)
                self.reverse_dependency_graph[path].discard(dep)
            
            del self.computed_states[path]
    
    def mark_dirty(self, path: str) -> Set[str]:
        """标记状态为脏数据"""
        dirty_paths = set()
        
        # 标记所有依赖此状态的计算状态为脏
        for computed_path in self.dependency_graph[path]:
            if computed_path in self.computed_states:
                self.computed_states[computed_path]["dirty"] = True
                dirty_paths.add(computed_path)
                
                # 递归标记
                dirty_paths.update(self.mark_dirty(computed_path))
        
        return dirty_paths
    
    async def compute_state(self, path: str, state_manager) -> Any:
        """计算状态值"""
        if path not in self.computed_states:
            raise ValueError(f"Computed state not registered: {path}")
        
        computed_info = self.computed_states[path]
        
        # 检查缓存
        if computed_info["cache"] and not computed_info["dirty"] and computed_info["cached_value"] is not None:
            return computed_info["cached_value"]
        
        # 获取依赖值
        dependency_values = {}
        for dep_path in computed_info["dependencies"]:
            dependency_values[dep_path] = await state_manager.get_state(dep_path)
        
        # 计算新值
        try:
            if asyncio.iscoroutinefunction(computed_info["compute_func"]):
                new_value = await computed_info["compute_func"](dependency_values)
            else:
                new_value = computed_info["compute_func"](dependency_values)
            
            # 更新缓存
            if computed_info["cache"]:
                computed_info["cached_value"] = new_value
                computed_info["dirty"] = False
            
            computed_info["last_computed"] = datetime.now()
            
            return new_value
            
        except Exception as e:
            logging.error(f"Error computing state {path}: {e}")
            raise


class SmartUIApiStateManager(IApiStateManager):
    """SmartUI API状态管理器实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 状态存储
        self.state_data: Dict[str, Any] = {}
        self.state_metadata: Dict[str, StateMetadata] = {}
        
        # 变化历史
        self.change_history: deque = deque(maxlen=self.config.get("max_history", 10000))
        
        # 监听器管理
        self.watchers: Dict[str, StateWatcher] = {}
        self.path_watchers: Dict[str, Set[str]] = defaultdict(set)
        
        # 绑定管理
        self.bindings: Dict[str, StateBinding] = {}
        self.source_bindings: Dict[str, Set[str]] = defaultdict(set)
        
        # 子组件
        self.validator = StateValidator()
        self.persistence = StatePersistence(self.config.get("persistence_path"))
        self.computer = StateComputer()
        
        # 缓存和锁
        self.state_cache = AsyncCache(max_size=1000, ttl=300)
        self.state_locks = AsyncLock()
        
        # 性能监控
        self.performance_metrics: Dict[str, float] = defaultdict(float)
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        # 初始化默认验证器
        self._initialize_default_validators()
        
        self.logger.info("SmartUI API State Manager initialized")
    
    @log_execution_time()
    async def get_state(self, path: str, default: Any = None) -> Any:
        """获取状态值"""
        try:
            async with self.state_locks.acquire(f"get_{path}"):
                # 检查缓存
                cached_value = await self.state_cache.get(path)
                if cached_value is not None:
                    return cached_value
                
                # 检查是否为计算状态
                if path in self.computer.computed_states:
                    value = await self.computer.compute_state(path, self)
                    await self.state_cache.set(path, value)
                    return value
                
                # 获取普通状态
                value = self._get_nested_value(self.state_data, path, default)
                
                # 缓存结果
                if value is not None:
                    await self.state_cache.set(path, value)
                
                return value
                
        except Exception as e:
            self.logger.error(f"Error getting state {path}: {e}")
            return default
    
    @log_execution_time()
    async def set_state(
        self,
        path: str,
        value: Any,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """设置状态值"""
        try:
            async with self.state_locks.acquire(f"set_{path}"):
                # 获取旧值
                old_value = await self.get_state(path)
                
                # 验证新值
                if path in self.state_metadata:
                    state_meta = self.state_metadata[path]
                    if state_meta.validators:
                        is_valid, errors = self.validator.validate(value, state_meta.validators)
                        if not is_valid:
                            self.logger.warning(f"Validation failed for {path}: {errors}")
                            return False
                
                # 设置值
                self._set_nested_value(self.state_data, path, value)
                
                # 更新缓存
                await self.state_cache.set(path, value)
                
                # 记录变化
                change = StateChange(
                    change_id=generate_id("change_"),
                    path=path,
                    change_type=StateChangeType.UPDATE,
                    old_value=old_value,
                    new_value=value,
                    timestamp=datetime.now(),
                    source=source,
                    metadata=metadata or {}
                )
                self.change_history.append(change)
                
                # 标记计算状态为脏
                dirty_paths = self.computer.mark_dirty(path)
                
                # 清理相关缓存
                for dirty_path in dirty_paths:
                    await self.state_cache.delete(dirty_path)
                
                # 触发监听器
                await self._trigger_watchers(path, change)
                
                # 处理绑定
                await self._process_bindings(path, value, source)
                
                # 持久化
                if path in self.state_metadata:
                    state_meta = self.state_metadata[path]
                    if state_meta.persistence_type != StatePersistenceType.MEMORY:
                        await self.persistence.save_state(path, value, state_meta.persistence_type, state_meta)
                
                # 发布状态变化事件
                await publish_event(
                    event_type=EventBusEventType.API_STATE_CHANGED,
                    data={
                        "path": path,
                        "old_value": old_value,
                        "new_value": value,
                        "source": source,
                        "change_id": change.change_id
                    },
                    source="api_state_manager"
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error setting state {path}: {e}")
            return False
    
    async def update_state(
        self,
        path: str,
        updates: Dict[str, Any],
        source: str = "unknown"
    ) -> bool:
        """更新状态（合并更新）"""
        try:
            current_value = await self.get_state(path, {})
            
            if isinstance(current_value, dict) and isinstance(updates, dict):
                # 深度合并
                new_value = deep_merge(current_value, updates)
            else:
                # 直接替换
                new_value = updates
            
            return await self.set_state(path, new_value, source, {"update_type": "merge"})
            
        except Exception as e:
            self.logger.error(f"Error updating state {path}: {e}")
            return False
    
    async def delete_state(self, path: str, source: str = "unknown") -> bool:
        """删除状态"""
        try:
            async with self.state_locks.acquire(f"delete_{path}"):
                # 获取旧值
                old_value = await self.get_state(path)
                
                if old_value is None:
                    return True  # 已经不存在
                
                # 删除值
                self._delete_nested_value(self.state_data, path)
                
                # 清理缓存
                await self.state_cache.delete(path)
                
                # 记录变化
                change = StateChange(
                    change_id=generate_id("change_"),
                    path=path,
                    change_type=StateChangeType.DELETE,
                    old_value=old_value,
                    new_value=None,
                    timestamp=datetime.now(),
                    source=source,
                    metadata={}
                )
                self.change_history.append(change)
                
                # 标记计算状态为脏
                dirty_paths = self.computer.mark_dirty(path)
                for dirty_path in dirty_paths:
                    await self.state_cache.delete(dirty_path)
                
                # 触发监听器
                await self._trigger_watchers(path, change)
                
                # 持久化删除
                if path in self.state_metadata:
                    state_meta = self.state_metadata[path]
                    if state_meta.persistence_type != StatePersistenceType.MEMORY:
                        await self.persistence.delete_state(path, state_meta.persistence_type, state_meta)
                
                # 发布状态变化事件
                await publish_event(
                    event_type=EventBusEventType.API_STATE_CHANGED,
                    data={
                        "path": path,
                        "old_value": old_value,
                        "new_value": None,
                        "source": source,
                        "change_id": change.change_id,
                        "change_type": "delete"
                    },
                    source="api_state_manager"
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting state {path}: {e}")
            return False
    
    async def watch_state(
        self,
        path: str,
        callback: Callable,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """监听状态变化"""
        try:
            options = options or {}
            
            watcher = StateWatcher(
                watcher_id=generate_id("watcher_"),
                path=path,
                callback=callback,
                filter_func=options.get("filter"),
                debounce_ms=options.get("debounce", 0),
                immediate=options.get("immediate", True),
                deep=options.get("deep", True)
            )
            
            self.watchers[watcher.watcher_id] = watcher
            self.path_watchers[path].add(watcher.watcher_id)
            
            # 如果设置了immediate，立即触发一次
            if watcher.immediate:
                current_value = await self.get_state(path)
                if current_value is not None:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(current_value, None, path)
                        else:
                            callback(current_value, None, path)
                    except Exception as e:
                        self.logger.error(f"Error in immediate watcher callback: {e}")
            
            self.logger.debug(f"Added watcher {watcher.watcher_id} for path {path}")
            return watcher.watcher_id
            
        except Exception as e:
            self.logger.error(f"Error adding watcher for {path}: {e}")
            return ""
    
    async def unwatch_state(self, watcher_id: str) -> bool:
        """取消监听状态变化"""
        try:
            if watcher_id not in self.watchers:
                return False
            
            watcher = self.watchers[watcher_id]
            path = watcher.path
            
            # 从映射中移除
            del self.watchers[watcher_id]
            self.path_watchers[path].discard(watcher_id)
            
            # 如果路径没有其他监听器，清理映射
            if not self.path_watchers[path]:
                del self.path_watchers[path]
            
            self.logger.debug(f"Removed watcher {watcher_id} for path {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing watcher {watcher_id}: {e}")
            return False
    
    async def bind_states(
        self,
        source_path: str,
        target_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """绑定状态"""
        try:
            options = options or {}
            
            binding = StateBinding(
                binding_id=generate_id("binding_"),
                source_path=source_path,
                target_path=target_path,
                transform_func=options.get("transform"),
                bidirectional=options.get("bidirectional", False),
                enabled=options.get("enabled", True)
            )
            
            self.bindings[binding.binding_id] = binding
            self.source_bindings[source_path].add(binding.binding_id)
            
            # 如果是双向绑定，也要监听目标路径
            if binding.bidirectional:
                self.source_bindings[target_path].add(binding.binding_id)
            
            # 立即同步一次
            if binding.enabled:
                source_value = await self.get_state(source_path)
                if source_value is not None:
                    await self._apply_binding(binding, source_value, "initial_sync")
            
            self.logger.debug(f"Created binding {binding.binding_id}: {source_path} -> {target_path}")
            return binding.binding_id
            
        except Exception as e:
            self.logger.error(f"Error creating binding {source_path} -> {target_path}: {e}")
            return ""
    
    async def unbind_states(self, binding_id: str) -> bool:
        """解除状态绑定"""
        try:
            if binding_id not in self.bindings:
                return False
            
            binding = self.bindings[binding_id]
            
            # 从映射中移除
            del self.bindings[binding_id]
            self.source_bindings[binding.source_path].discard(binding_id)
            
            if binding.bidirectional:
                self.source_bindings[binding.target_path].discard(binding_id)
            
            self.logger.debug(f"Removed binding {binding_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing binding {binding_id}: {e}")
            return False
    
    async def register_computed_state(
        self,
        path: str,
        dependencies: List[str],
        compute_func: Callable,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """注册计算状态"""
        try:
            options = options or {}
            
            self.computer.register_computed_state(
                path=path,
                dependencies=dependencies,
                compute_func=compute_func,
                cache=options.get("cache", True)
            )
            
            # 注册状态元数据
            self.state_metadata[path] = StateMetadata(
                created_at=datetime.now(),
                updated_at=datetime.now(),
                version=1,
                access_level=StateAccessLevel.READONLY,
                persistence_type=StatePersistenceType.MEMORY,
                tags=["computed"],
                description=f"Computed state depending on: {', '.join(dependencies)}"
            )
            
            self.logger.debug(f"Registered computed state {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering computed state {path}: {e}")
            return False
    
    async def get_state_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """获取状态元数据"""
        if path in self.state_metadata:
            return asdict(self.state_metadata[path])
        return None
    
    async def set_state_metadata(
        self,
        path: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """设置状态元数据"""
        try:
            if path in self.state_metadata:
                # 更新现有元数据
                current_meta = self.state_metadata[path]
                for key, value in metadata.items():
                    if hasattr(current_meta, key):
                        setattr(current_meta, key, value)
                current_meta.updated_at = datetime.now()
                current_meta.version += 1
            else:
                # 创建新元数据
                self.state_metadata[path] = StateMetadata(
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    version=1,
                    access_level=StateAccessLevel(metadata.get("access_level", "public")),
                    persistence_type=StatePersistenceType(metadata.get("persistence_type", "memory")),
                    tags=metadata.get("tags", []),
                    description=metadata.get("description", ""),
                    schema=metadata.get("schema"),
                    validators=metadata.get("validators", [])
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting metadata for {path}: {e}")
            return False
    
    async def get_state_history(
        self,
        path: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取状态变化历史"""
        try:
            changes = list(self.change_history)
            
            # 过滤路径
            if path:
                changes = [c for c in changes if c.path == path or c.path.startswith(f"{path}.")]
            
            # 按时间倒序排列
            changes.sort(key=lambda c: c.timestamp, reverse=True)
            
            # 限制数量
            changes = changes[:limit]
            
            # 转换为字典
            return [asdict(change) for change in changes]
            
        except Exception as e:
            self.logger.error(f"Error getting state history: {e}")
            return []
    
    async def export_state(
        self,
        paths: Optional[List[str]] = None,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """导出状态"""
        try:
            export_data = {}
            
            if paths is None:
                # 导出所有状态
                export_data["state"] = copy.deepcopy(self.state_data)
            else:
                # 导出指定路径的状态
                export_data["state"] = {}
                for path in paths:
                    value = await self.get_state(path)
                    if value is not None:
                        self._set_nested_value(export_data["state"], path, value)
            
            if include_metadata:
                export_data["metadata"] = {
                    path: asdict(meta) for path, meta in self.state_metadata.items()
                    if paths is None or path in paths
                }
            
            export_data["exported_at"] = datetime.now().isoformat()
            export_data["version"] = "1.0"
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting state: {e}")
            return {}
    
    async def import_state(
        self,
        import_data: Dict[str, Any],
        merge: bool = True,
        source: str = "import"
    ) -> bool:
        """导入状态"""
        try:
            if "state" not in import_data:
                return False
            
            imported_state = import_data["state"]
            
            if merge:
                # 合并导入
                for path, value in flatten_dict(imported_state).items():
                    await self.set_state(path, value, source)
            else:
                # 替换导入
                self.state_data.clear()
                await self.state_cache.clear()
                
                for path, value in flatten_dict(imported_state).items():
                    await self.set_state(path, value, source)
            
            # 导入元数据
            if "metadata" in import_data:
                for path, meta_data in import_data["metadata"].items():
                    await self.set_state_metadata(path, meta_data)
            
            self.logger.info(f"Imported state from {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing state: {e}")
            return False
    
    def _get_nested_value(self, data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """获取嵌套值"""
        try:
            keys = path.split('.')
            current = data
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            
            return current
            
        except Exception:
            return default
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """设置嵌套值"""
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _delete_nested_value(self, data: Dict[str, Any], path: str) -> None:
        """删除嵌套值"""
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return  # 路径不存在
        
        if isinstance(current, dict) and keys[-1] in current:
            del current[keys[-1]]
    
    async def _trigger_watchers(self, path: str, change: StateChange) -> None:
        """触发监听器"""
        # 获取所有相关的监听器
        relevant_watchers = set()
        
        # 精确匹配
        if path in self.path_watchers:
            relevant_watchers.update(self.path_watchers[path])
        
        # 父路径匹配（深度监听）
        for watcher_path in self.path_watchers:
            if path.startswith(f"{watcher_path}."):
                relevant_watchers.update(self.path_watchers[watcher_path])
        
        # 子路径匹配
        for watcher_path in self.path_watchers:
            if watcher_path.startswith(f"{path}."):
                relevant_watchers.update(self.path_watchers[watcher_path])
        
        # 触发监听器
        for watcher_id in relevant_watchers:
            if watcher_id in self.watchers:
                watcher = self.watchers[watcher_id]
                
                try:
                    # 应用过滤器
                    if watcher.filter_func and not watcher.filter_func(change):
                        continue
                    
                    # 防抖处理
                    if watcher.debounce_ms > 0:
                        # 这里应该实现防抖逻辑
                        # 简化实现，直接调用
                        pass
                    
                    # 调用回调
                    if asyncio.iscoroutinefunction(watcher.callback):
                        await watcher.callback(change.new_value, change.old_value, change.path)
                    else:
                        watcher.callback(change.new_value, change.old_value, change.path)
                        
                except Exception as e:
                    self.logger.error(f"Error in watcher {watcher_id}: {e}")
    
    async def _process_bindings(self, path: str, value: Any, source: str) -> None:
        """处理状态绑定"""
        if path not in self.source_bindings:
            return
        
        for binding_id in self.source_bindings[path]:
            if binding_id in self.bindings:
                binding = self.bindings[binding_id]
                
                if not binding.enabled:
                    continue
                
                # 避免循环绑定
                if source == f"binding_{binding_id}":
                    continue
                
                try:
                    await self._apply_binding(binding, value, f"binding_{binding_id}")
                except Exception as e:
                    self.logger.error(f"Error applying binding {binding_id}: {e}")
    
    async def _apply_binding(self, binding: StateBinding, value: Any, source: str) -> None:
        """应用状态绑定"""
        target_value = value
        
        # 应用转换函数
        if binding.transform_func:
            try:
                if asyncio.iscoroutinefunction(binding.transform_func):
                    target_value = await binding.transform_func(value)
                else:
                    target_value = binding.transform_func(value)
            except Exception as e:
                self.logger.error(f"Error in binding transform function: {e}")
                return
        
        # 设置目标值
        await self.set_state(binding.target_path, target_value, source)
    
    def _initialize_default_validators(self) -> None:
        """初始化默认验证器"""
        # 基本类型验证器
        self.validator.register_validator("string", lambda x: isinstance(x, str))
        self.validator.register_validator("number", lambda x: isinstance(x, (int, float)))
        self.validator.register_validator("boolean", lambda x: isinstance(x, bool))
        self.validator.register_validator("array", lambda x: isinstance(x, list))
        self.validator.register_validator("object", lambda x: isinstance(x, dict))
        
        # 范围验证器
        self.validator.register_validator("positive", lambda x: isinstance(x, (int, float)) and x > 0)
        self.validator.register_validator("non_negative", lambda x: isinstance(x, (int, float)) and x >= 0)
        
        # 字符串验证器
        self.validator.register_validator("non_empty_string", lambda x: isinstance(x, str) and len(x.strip()) > 0)
        self.validator.register_validator("email", lambda x: isinstance(x, str) and "@" in x and "." in x)
        
        # 数组验证器
        self.validator.register_validator("non_empty_array", lambda x: isinstance(x, list) and len(x) > 0)
    
    @event_handler(EventBusEventType.UI_COMPONENT_MOUNTED)
    async def handle_component_mounted(self, event: EventBusEvent) -> None:
        """处理UI组件挂载事件"""
        component_data = event.data
        component_id = component_data.get("component_id")
        
        # 可以在这里初始化组件相关的状态
        if component_id:
            await self.set_state(f"ui.components.{component_id}.mounted", True, "system")
    
    @event_handler(EventBusEventType.UI_COMPONENT_UNMOUNTED)
    async def handle_component_unmounted(self, event: EventBusEvent) -> None:
        """处理UI组件卸载事件"""
        component_data = event.data
        component_id = component_data.get("component_id")
        
        # 清理组件相关的状态
        if component_id:
            await self.delete_state(f"ui.components.{component_id}", "system")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "total_states": len(flatten_dict(self.state_data)),
            "watchers_count": len(self.watchers),
            "bindings_count": len(self.bindings),
            "computed_states_count": len(self.computer.computed_states),
            "change_history_size": len(self.change_history),
            "cache_hit_rate": getattr(self.state_cache, "hit_rate", 0.0),
            "performance_metrics": dict(self.performance_metrics)
        }
    
    async def cleanup(self) -> Dict[str, int]:
        """清理过期数据"""
        cleanup_stats = {
            "cleared_cache_entries": 0,
            "removed_watchers": 0,
            "removed_bindings": 0
        }
        
        # 清理缓存
        await self.state_cache.clear()
        cleanup_stats["cleared_cache_entries"] = 1
        
        # 清理过期的监听器（这里可以添加更复杂的逻辑）
        # 清理过期的绑定
        
        self.logger.info(f"Cleanup completed: {cleanup_stats}")
        return cleanup_stats


# 导出主要类
ApiStateManager = SmartUIApiStateManager  # 为了向后兼容
__all__ = ['SmartUIApiStateManager', 'ApiStateManager']

