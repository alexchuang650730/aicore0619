"""
SmartUI MCP - 响应式组件系统

实现响应式UI组件系统，支持数据绑定、状态同步和动态更新。
提供组件生命周期管理、事件处理和性能优化功能。
"""

import asyncio
import logging
import time
import weakref
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import copy
import json

from ..common import (
    EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    UIConfiguration, UIComponent, ComponentType, LayoutType, ThemeType,
    ComponentProps, ComponentStyle, LayoutConfig, ThemeConfig
)


class ComponentState(str, Enum):
    """组件状态枚举"""
    CREATED = "created"
    MOUNTED = "mounted"
    UPDATED = "updated"
    UNMOUNTED = "unmounted"
    ERROR = "error"


class UpdateTrigger(str, Enum):
    """更新触发器枚举"""
    STATE_CHANGE = "state_change"
    PROPS_CHANGE = "props_change"
    PARENT_UPDATE = "parent_update"
    FORCE_UPDATE = "force_update"
    EXTERNAL_EVENT = "external_event"


@dataclass
class ComponentLifecycleEvent:
    """组件生命周期事件"""
    event_id: str
    component_id: str
    event_type: str
    state: ComponentState
    data: Dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = generate_id("lifecycle_")


@dataclass
class ComponentUpdate:
    """组件更新信息"""
    update_id: str
    component_id: str
    trigger: UpdateTrigger
    changes: Dict[str, Any]
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        if self.update_id is None:
            self.update_id = generate_id("update_")


class IReactiveComponent(ABC):
    """响应式组件接口"""
    
    @abstractmethod
    async def mount(self) -> bool:
        """挂载组件"""
        pass
    
    @abstractmethod
    async def update(self, changes: Dict[str, Any]) -> bool:
        """更新组件"""
        pass
    
    @abstractmethod
    async def unmount(self) -> bool:
        """卸载组件"""
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """获取组件状态"""
        pass
    
    @abstractmethod
    async def set_state(self, state: Dict[str, Any]) -> bool:
        """设置组件状态"""
        pass


class ReactiveComponent(IReactiveComponent):
    """响应式组件基类"""
    
    def __init__(
        self,
        component_id: str,
        component_type: ComponentType,
        props: Optional[Dict[str, Any]] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ):
        self.component_id = component_id
        self.component_type = component_type
        self.props = props or {}
        self.state = initial_state or {}
        
        # 组件状态
        self.lifecycle_state = ComponentState.CREATED
        self.is_mounted = False
        self.is_updating = False
        
        # 子组件
        self.children: List['ReactiveComponent'] = []
        self.parent: Optional['ReactiveComponent'] = None
        
        # 事件处理
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.state_watchers: Dict[str, List[Callable]] = {}
        
        # 更新队列
        self.pending_updates: List[ComponentUpdate] = []
        self.update_lock = asyncio.Lock()
        
        # 性能监控
        self.render_count = 0
        self.last_render_time = 0.0
        self.total_render_time = 0.0
        
        # 日志
        self.logger = logging.getLogger(f"{__name__}.ReactiveComponent.{component_id}")
        
        self.logger.debug(f"Created reactive component: {component_type.value}")
    
    async def mount(self) -> bool:
        """挂载组件"""
        try:
            if self.is_mounted:
                return True
            
            # 执行挂载前钩子
            await self._before_mount()
            
            # 设置状态
            self.lifecycle_state = ComponentState.MOUNTED
            self.is_mounted = True
            
            # 挂载子组件
            for child in self.children:
                await child.mount()
            
            # 执行挂载后钩子
            await self._after_mount()
            
            # 发布生命周期事件
            await self._emit_lifecycle_event("mounted")
            
            self.logger.debug("Component mounted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error mounting component: {e}")
            self.lifecycle_state = ComponentState.ERROR
            return False
    
    async def update(self, changes: Dict[str, Any]) -> bool:
        """更新组件"""
        try:
            async with self.update_lock:
                if not self.is_mounted:
                    return False
                
                self.is_updating = True
                start_time = time.time()
                
                # 记录更新信息
                update_info = ComponentUpdate(
                    update_id=generate_id("update_"),
                    component_id=self.component_id,
                    trigger=UpdateTrigger.EXTERNAL_EVENT,
                    changes=changes,
                    previous_state=copy.deepcopy(self.state),
                    new_state={},  # 将在更新后设置
                    timestamp=datetime.now()
                )
                
                # 执行更新前钩子
                should_update = await self._should_update(changes)
                if not should_update:
                    self.is_updating = False
                    return False
                
                await self._before_update(changes)
                
                # 应用更改
                await self._apply_changes(changes)
                
                # 更新状态
                self.lifecycle_state = ComponentState.UPDATED
                update_info.new_state = copy.deepcopy(self.state)
                
                # 触发重新渲染
                await self._render()
                
                # 更新子组件
                await self._update_children(changes)
                
                # 执行更新后钩子
                await self._after_update(changes)
                
                # 记录性能指标
                render_time = time.time() - start_time
                self.last_render_time = render_time
                self.total_render_time += render_time
                self.render_count += 1
                
                # 发布更新事件
                await self._emit_update_event(update_info)
                
                self.is_updating = False
                self.logger.debug(f"Component updated in {render_time:.3f}s")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating component: {e}")
            self.lifecycle_state = ComponentState.ERROR
            self.is_updating = False
            return False
    
    async def unmount(self) -> bool:
        """卸载组件"""
        try:
            if not self.is_mounted:
                return True
            
            # 执行卸载前钩子
            await self._before_unmount()
            
            # 卸载子组件
            for child in self.children:
                await child.unmount()
            
            # 清理事件处理器
            self.event_handlers.clear()
            self.state_watchers.clear()
            
            # 设置状态
            self.lifecycle_state = ComponentState.UNMOUNTED
            self.is_mounted = False
            
            # 执行卸载后钩子
            await self._after_unmount()
            
            # 发布生命周期事件
            await self._emit_lifecycle_event("unmounted")
            
            self.logger.debug("Component unmounted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unmounting component: {e}")
            return False
    
    def get_state(self) -> Dict[str, Any]:
        """获取组件状态"""
        return copy.deepcopy(self.state)
    
    async def set_state(self, state: Dict[str, Any]) -> bool:
        """设置组件状态"""
        try:
            changes = {}
            
            # 计算状态变化
            for key, value in state.items():
                if key not in self.state or self.state[key] != value:
                    changes[key] = value
            
            if not changes:
                return True
            
            # 触发状态观察者
            await self._notify_state_watchers(changes)
            
            # 更新状态
            self.state.update(changes)
            
            # 如果组件已挂载，触发更新
            if self.is_mounted:
                await self.update({"state_changes": changes})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting state: {e}")
            return False
    
    def add_child(self, child: 'ReactiveComponent') -> None:
        """添加子组件"""
        if child not in self.children:
            self.children.append(child)
            child.parent = self
    
    def remove_child(self, child: 'ReactiveComponent') -> None:
        """移除子组件"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """添加事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: str, handler: Callable) -> None:
        """移除事件处理器"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def watch_state(self, state_key: str, watcher: Callable) -> None:
        """监听状态变化"""
        if state_key not in self.state_watchers:
            self.state_watchers[state_key] = []
        self.state_watchers[state_key].append(watcher)
    
    def unwatch_state(self, state_key: str, watcher: Callable) -> None:
        """取消监听状态变化"""
        if state_key in self.state_watchers:
            try:
                self.state_watchers[state_key].remove(watcher)
            except ValueError:
                pass
    
    async def emit_event(self, event_type: str, data: Any = None) -> None:
        """发射事件"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event_type}: {e}")
    
    # 生命周期钩子方法
    async def _before_mount(self) -> None:
        """挂载前钩子"""
        pass
    
    async def _after_mount(self) -> None:
        """挂载后钩子"""
        pass
    
    async def _should_update(self, changes: Dict[str, Any]) -> bool:
        """是否应该更新"""
        return True
    
    async def _before_update(self, changes: Dict[str, Any]) -> None:
        """更新前钩子"""
        pass
    
    async def _after_update(self, changes: Dict[str, Any]) -> None:
        """更新后钩子"""
        pass
    
    async def _before_unmount(self) -> None:
        """卸载前钩子"""
        pass
    
    async def _after_unmount(self) -> None:
        """卸载后钩子"""
        pass
    
    async def _apply_changes(self, changes: Dict[str, Any]) -> None:
        """应用变更"""
        # 更新props
        if "props" in changes:
            self.props.update(changes["props"])
        
        # 更新状态
        if "state_changes" in changes:
            self.state.update(changes["state_changes"])
    
    async def _render(self) -> None:
        """渲染组件"""
        # 基类的渲染方法，子类可以重写
        pass
    
    async def _update_children(self, changes: Dict[str, Any]) -> None:
        """更新子组件"""
        for child in self.children:
            # 传播相关的变更到子组件
            child_changes = self._filter_changes_for_child(child, changes)
            if child_changes:
                await child.update(child_changes)
    
    def _filter_changes_for_child(
        self,
        child: 'ReactiveComponent',
        changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """过滤传递给子组件的变更"""
        # 基类实现，子类可以重写
        return {}
    
    async def _notify_state_watchers(self, changes: Dict[str, Any]) -> None:
        """通知状态观察者"""
        for state_key, new_value in changes.items():
            watchers = self.state_watchers.get(state_key, [])
            for watcher in watchers:
                try:
                    if asyncio.iscoroutinefunction(watcher):
                        await watcher(new_value, self.state.get(state_key))
                    else:
                        watcher(new_value, self.state.get(state_key))
                except Exception as e:
                    self.logger.error(f"Error in state watcher for {state_key}: {e}")
    
    async def _emit_lifecycle_event(self, event_type: str) -> None:
        """发射生命周期事件"""
        lifecycle_event = ComponentLifecycleEvent(
            event_id=generate_id("lifecycle_"),
            component_id=self.component_id,
            event_type=event_type,
            state=self.lifecycle_state,
            data={
                "component_type": self.component_type.value,
                "props": self.props,
                "state": self.state
            },
            timestamp=datetime.now()
        )
        
        await publish_event(
            event_type=EventBusEventType.UI_COMPONENT_LIFECYCLE,
            data=asdict(lifecycle_event),
            source=f"component_{self.component_id}"
        )
    
    async def _emit_update_event(self, update_info: ComponentUpdate) -> None:
        """发射更新事件"""
        await publish_event(
            event_type=EventBusEventType.UI_COMPONENT_UPDATED,
            data=asdict(update_info),
            source=f"component_{self.component_id}"
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            "render_count": self.render_count,
            "last_render_time": self.last_render_time,
            "total_render_time": self.total_render_time,
            "average_render_time": self.total_render_time / self.render_count if self.render_count > 0 else 0.0,
            "is_updating": self.is_updating,
            "lifecycle_state": self.lifecycle_state.value
        }


class ComponentRegistry:
    """组件注册表"""
    
    def __init__(self):
        self.components: Dict[str, ReactiveComponent] = {}
        self.component_types: Dict[ComponentType, type] = {}
        self.component_tree: Dict[str, List[str]] = {}  # parent_id -> [child_ids]
        self.logger = logging.getLogger(f"{__name__}.ComponentRegistry")
    
    def register_component_type(
        self,
        component_type: ComponentType,
        component_class: type
    ) -> None:
        """注册组件类型"""
        self.component_types[component_type] = component_class
        self.logger.debug(f"Registered component type: {component_type.value}")
    
    def create_component(
        self,
        component_id: str,
        component_type: ComponentType,
        props: Optional[Dict[str, Any]] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> Optional[ReactiveComponent]:
        """创建组件"""
        try:
            component_class = self.component_types.get(component_type, ReactiveComponent)
            component = component_class(component_id, component_type, props, initial_state)
            
            self.components[component_id] = component
            self.component_tree[component_id] = []
            
            self.logger.debug(f"Created component: {component_id}")
            return component
            
        except Exception as e:
            self.logger.error(f"Error creating component {component_id}: {e}")
            return None
    
    def get_component(self, component_id: str) -> Optional[ReactiveComponent]:
        """获取组件"""
        return self.components.get(component_id)
    
    def remove_component(self, component_id: str) -> bool:
        """移除组件"""
        try:
            if component_id in self.components:
                component = self.components[component_id]
                
                # 卸载组件
                asyncio.create_task(component.unmount())
                
                # 从注册表移除
                del self.components[component_id]
                
                # 从组件树移除
                if component_id in self.component_tree:
                    del self.component_tree[component_id]
                
                # 从父组件的子组件列表中移除
                for parent_id, children in self.component_tree.items():
                    if component_id in children:
                        children.remove(component_id)
                
                self.logger.debug(f"Removed component: {component_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing component {component_id}: {e}")
            return False
    
    def add_child_component(self, parent_id: str, child_id: str) -> bool:
        """添加子组件关系"""
        try:
            parent = self.components.get(parent_id)
            child = self.components.get(child_id)
            
            if parent and child:
                parent.add_child(child)
                
                if parent_id not in self.component_tree:
                    self.component_tree[parent_id] = []
                
                if child_id not in self.component_tree[parent_id]:
                    self.component_tree[parent_id].append(child_id)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error adding child component {child_id} to {parent_id}: {e}")
            return False
    
    def get_component_tree(self) -> Dict[str, List[str]]:
        """获取组件树"""
        return copy.deepcopy(self.component_tree)
    
    def get_all_components(self) -> Dict[str, ReactiveComponent]:
        """获取所有组件"""
        return dict(self.components)
    
    def get_components_by_type(self, component_type: ComponentType) -> List[ReactiveComponent]:
        """根据类型获取组件"""
        return [
            comp for comp in self.components.values()
            if comp.component_type == component_type
        ]


class ReactiveComponentSystem:
    """响应式组件系统"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 组件注册表
        self.registry = ComponentRegistry()
        
        # 更新队列
        self.update_queue: asyncio.Queue = asyncio.Queue()
        self.update_processor_task: Optional[asyncio.Task] = None
        
        # 性能监控
        self.performance_metrics: Dict[str, Any] = {
            "total_components": 0,
            "active_components": 0,
            "total_updates": 0,
            "average_update_time": 0.0
        }
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        # 启动更新处理器
        self._start_update_processor()
        
        self.logger.info("Reactive Component System initialized")
    
    def _start_update_processor(self) -> None:
        """启动更新处理器"""
        if self.update_processor_task is None or self.update_processor_task.done():
            self.update_processor_task = asyncio.create_task(self._process_updates())
    
    async def _process_updates(self) -> None:
        """处理更新队列"""
        while True:
            try:
                # 从队列获取更新任务
                update_task = await self.update_queue.get()
                
                # 执行更新
                await update_task
                
                # 标记任务完成
                self.update_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing update: {e}")
    
    async def create_component(
        self,
        component_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建组件"""
        try:
            component_id = component_config.get("id") or generate_id("comp_")
            component_type = ComponentType(component_config.get("type", "div"))
            props = component_config.get("props", {})
            initial_state = component_config.get("state", {})
            
            # 创建组件
            component = self.registry.create_component(
                component_id, component_type, props, initial_state
            )
            
            if component:
                # 更新性能指标
                self.performance_metrics["total_components"] += 1
                self.performance_metrics["active_components"] += 1
                
                # 挂载组件
                await component.mount()
                
                return {
                    "success": True,
                    "component_id": component_id,
                    "component_type": component_type.value,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create component",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error creating component: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def update_component(
        self,
        component_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新组件"""
        try:
            component = self.registry.get_component(component_id)
            if not component:
                return {
                    "success": False,
                    "error": f"Component {component_id} not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 将更新任务加入队列
            update_task = component.update(updates)
            await self.update_queue.put(update_task)
            
            # 更新性能指标
            self.performance_metrics["total_updates"] += 1
            
            return {
                "success": True,
                "component_id": component_id,
                "updates": updates,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error updating component {component_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def remove_component(self, component_id: str) -> Dict[str, Any]:
        """移除组件"""
        try:
            success = self.registry.remove_component(component_id)
            
            if success:
                # 更新性能指标
                self.performance_metrics["active_components"] -= 1
                
                return {
                    "success": True,
                    "component_id": component_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Component {component_id} not found",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error removing component {component_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_component_state(self, component_id: str) -> Dict[str, Any]:
        """获取组件状态"""
        try:
            component = self.registry.get_component(component_id)
            if not component:
                return {
                    "success": False,
                    "error": f"Component {component_id} not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": True,
                "component_id": component_id,
                "state": component.get_state(),
                "props": component.props,
                "lifecycle_state": component.lifecycle_state.value,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting component state {component_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def set_component_state(
        self,
        component_id: str,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """设置组件状态"""
        try:
            component = self.registry.get_component(component_id)
            if not component:
                return {
                    "success": False,
                    "error": f"Component {component_id} not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            success = await component.set_state(state)
            
            return {
                "success": success,
                "component_id": component_id,
                "state": state,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error setting component state {component_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def build_component_tree(
        self,
        tree_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建组件树"""
        try:
            created_components = []
            
            # 递归创建组件树
            async def create_tree_node(node_config: Dict[str, Any], parent_id: Optional[str] = None):
                # 创建当前节点
                result = await self.create_component(node_config)
                if not result["success"]:
                    return False
                
                component_id = result["component_id"]
                created_components.append(component_id)
                
                # 如果有父组件，建立父子关系
                if parent_id:
                    self.registry.add_child_component(parent_id, component_id)
                
                # 递归创建子组件
                children = node_config.get("children", [])
                for child_config in children:
                    success = await create_tree_node(child_config, component_id)
                    if not success:
                        return False
                
                return True
            
            # 开始构建
            success = await create_tree_node(tree_config)
            
            return {
                "success": success,
                "created_components": created_components,
                "component_tree": self.registry.get_component_tree(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error building component tree: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @event_handler(EventBusEventType.API_STATE_CHANGED)
    async def handle_state_changed(self, event: EventBusEvent) -> None:
        """处理状态变化事件"""
        state_data = event.data
        path = state_data.get("path")
        value = state_data.get("value")
        
        # 如果是组件相关的状态变化，更新对应组件
        if path and path.startswith("components."):
            path_parts = path.split(".")
            if len(path_parts) >= 2:
                component_id = path_parts[1]
                component = self.registry.get_component(component_id)
                
                if component:
                    # 提取状态路径
                    state_path = ".".join(path_parts[2:]) if len(path_parts) > 2 else ""
                    
                    if state_path:
                        # 更新特定状态
                        current_state = component.get_state()
                        self._set_nested_value(current_state, state_path, value)
                        await component.set_state(current_state)
                    else:
                        # 更新整个状态
                        if isinstance(value, dict):
                            await component.set_state(value)
    
    def _set_nested_value(self, obj: Dict[str, Any], path: str, value: Any) -> None:
        """设置嵌套值"""
        keys = path.split(".")
        current = obj
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        # 计算组件性能指标
        all_components = self.registry.get_all_components()
        total_render_time = sum(comp.total_render_time for comp in all_components.values())
        total_renders = sum(comp.render_count for comp in all_components.values())
        
        self.performance_metrics.update({
            "active_components": len(all_components),
            "average_update_time": total_render_time / total_renders if total_renders > 0 else 0.0,
            "queue_size": self.update_queue.qsize(),
            "component_types": len(self.registry.component_types)
        })
        
        return dict(self.performance_metrics)
    
    async def cleanup(self) -> Dict[str, int]:
        """清理资源"""
        cleanup_stats = {
            "removed_components": 0,
            "cancelled_tasks": 0
        }
        
        try:
            # 移除所有组件
            all_components = list(self.registry.get_all_components().keys())
            for component_id in all_components:
                self.registry.remove_component(component_id)
                cleanup_stats["removed_components"] += 1
            
            # 取消更新处理器任务
            if self.update_processor_task and not self.update_processor_task.done():
                self.update_processor_task.cancel()
                cleanup_stats["cancelled_tasks"] += 1
            
            # 清空更新队列
            while not self.update_queue.empty():
                try:
                    self.update_queue.get_nowait()
                    self.update_queue.task_done()
                except asyncio.QueueEmpty:
                    break
            
            self.logger.info(f"Reactive Component System cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return cleanup_stats

