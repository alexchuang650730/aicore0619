"""
SmartUI MCP - 事件监听系统

实现完整的事件监听、处理和分发机制。
支持事件过滤、优先级处理、批量处理和性能监控。
"""

import asyncio
import logging
import time
import weakref
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import json
import re

from ..common import (
    EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time
)


class EventPriority(int, Enum):
    """事件优先级枚举"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class EventFilterType(str, Enum):
    """事件过滤器类型枚举"""
    SOURCE = "source"
    EVENT_TYPE = "event_type"
    DATA_FIELD = "data_field"
    REGEX = "regex"
    CUSTOM = "custom"


@dataclass
class EventFilter:
    """事件过滤器"""
    filter_id: str
    filter_type: EventFilterType
    pattern: str
    value: Any
    enabled: bool = True
    
    def __post_init__(self):
        if self.filter_id is None:
            self.filter_id = generate_id("filter_")


@dataclass
class EventSubscription:
    """事件订阅"""
    subscription_id: str
    event_types: List[EventBusEventType]
    handler: Callable
    filters: List[EventFilter]
    priority: EventPriority
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.subscription_id is None:
            self.subscription_id = generate_id("sub_")
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class EventProcessingResult:
    """事件处理结果"""
    event_id: str
    subscription_id: str
    success: bool
    duration: float
    error: Optional[str]
    timestamp: datetime


class EventProcessor:
    """事件处理器"""
    
    def __init__(self, max_workers: int = 10, queue_size: int = 1000):
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.logger = logging.getLogger(f"{__name__}.EventProcessor")
        
        # 事件队列（按优先级分组）
        self.event_queues: Dict[EventPriority, asyncio.Queue] = {
            priority: asyncio.Queue(maxsize=queue_size)
            for priority in EventPriority
        }
        
        # 工作者任务
        self.worker_tasks: List[asyncio.Task] = []
        self.running = False
        
        # 订阅管理
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.event_type_subscriptions: Dict[EventBusEventType, List[str]] = defaultdict(list)
        
        # 性能统计
        self.processed_events = 0
        self.failed_events = 0
        self.total_processing_time = 0.0
        self.processing_results: deque = deque(maxlen=1000)  # 保留最近1000个处理结果
        
        # 缓存
        self.filter_cache = AsyncCache(default_ttl=300)
        
        self.logger.info("Event Processor initialized")
    
    async def start(self) -> None:
        """启动事件处理器"""
        if self.running:
            return
        
        self.running = True
        
        # 启动工作者任务
        for i in range(self.max_workers):
            task = asyncio.create_task(self._worker_loop(f"worker_{i}"))
            self.worker_tasks.append(task)
        
        self.logger.info(f"Event Processor started with {self.max_workers} workers")
    
    async def stop(self) -> None:
        """停止事件处理器"""
        if not self.running:
            return
        
        self.running = False
        
        # 取消所有工作者任务
        for task in self.worker_tasks:
            task.cancel()
        
        # 等待任务完成
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        self.worker_tasks.clear()
        self.logger.info("Event Processor stopped")
    
    async def subscribe(
        self,
        event_types: Union[EventBusEventType, List[EventBusEventType]],
        handler: Callable,
        filters: Optional[List[EventFilter]] = None,
        priority: EventPriority = EventPriority.NORMAL
    ) -> str:
        """订阅事件"""
        if isinstance(event_types, EventBusEventType):
            event_types = [event_types]
        
        subscription = EventSubscription(
            subscription_id=generate_id("sub_"),
            event_types=event_types,
            handler=handler,
            filters=filters or [],
            priority=priority
        )
        
        # 存储订阅
        self.subscriptions[subscription.subscription_id] = subscription
        
        # 更新事件类型索引
        for event_type in event_types:
            self.event_type_subscriptions[event_type].append(subscription.subscription_id)
        
        self.logger.debug(f"Created subscription {subscription.subscription_id} for {len(event_types)} event types")
        return subscription.subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        # 从事件类型索引中移除
        for event_type in subscription.event_types:
            if subscription_id in self.event_type_subscriptions[event_type]:
                self.event_type_subscriptions[event_type].remove(subscription_id)
        
        # 删除订阅
        del self.subscriptions[subscription_id]
        
        self.logger.debug(f"Removed subscription {subscription_id}")
        return True
    
    async def process_event(self, event: EventBusEvent, priority: EventPriority = EventPriority.NORMAL) -> None:
        """处理事件"""
        try:
            # 将事件加入对应优先级的队列
            queue = self.event_queues[priority]
            
            # 如果队列满了，丢弃低优先级事件
            if queue.full():
                if priority in [EventPriority.LOW, EventPriority.BACKGROUND]:
                    self.logger.warning(f"Dropping {priority.name} priority event due to full queue")
                    return
                else:
                    # 对于高优先级事件，等待队列有空间
                    await queue.put((event, priority))
            else:
                await queue.put((event, priority))
                
        except Exception as e:
            self.logger.error(f"Error queuing event {event.event_id}: {e}")
    
    async def _worker_loop(self, worker_name: str) -> None:
        """工作者循环"""
        self.logger.debug(f"Worker {worker_name} started")
        
        while self.running:
            try:
                # 按优先级处理事件
                event_data = await self._get_next_event()
                if event_data is None:
                    continue
                
                event, priority = event_data
                await self._handle_event(event, priority)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in worker {worker_name}: {e}")
        
        self.logger.debug(f"Worker {worker_name} stopped")
    
    async def _get_next_event(self) -> Optional[Tuple[EventBusEvent, EventPriority]]:
        """获取下一个事件（按优先级）"""
        # 按优先级顺序检查队列
        for priority in EventPriority:
            queue = self.event_queues[priority]
            try:
                # 非阻塞检查
                return queue.get_nowait()
            except asyncio.QueueEmpty:
                continue
        
        # 如果所有队列都为空，等待任意队列有事件
        tasks = [
            asyncio.create_task(queue.get())
            for queue in self.event_queues.values()
        ]
        
        try:
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
                timeout=1.0  # 1秒超时
            )
            
            # 取消未完成的任务
            for task in pending:
                task.cancel()
            
            # 返回第一个完成的结果
            if done:
                return await done.pop()
            
        except asyncio.TimeoutError:
            # 超时，取消所有任务
            for task in tasks:
                task.cancel()
        
        return None
    
    async def _handle_event(self, event: EventBusEvent, priority: EventPriority) -> None:
        """处理单个事件"""
        start_time = time.time()
        
        try:
            # 查找匹配的订阅
            matching_subscriptions = await self._find_matching_subscriptions(event)
            
            # 处理每个匹配的订阅
            for subscription_id in matching_subscriptions:
                subscription = self.subscriptions.get(subscription_id)
                if not subscription or not subscription.enabled:
                    continue
                
                await self._execute_handler(event, subscription)
            
            # 更新统计
            self.processed_events += 1
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            self.logger.debug(f"Processed event {event.event_id} in {processing_time:.3f}s")
            
        except Exception as e:
            self.failed_events += 1
            self.logger.error(f"Error handling event {event.event_id}: {e}")
    
    async def _find_matching_subscriptions(self, event: EventBusEvent) -> List[str]:
        """查找匹配的订阅"""
        matching_subscriptions = []
        
        # 根据事件类型查找订阅
        subscription_ids = self.event_type_subscriptions.get(event.event_type, [])
        
        for subscription_id in subscription_ids:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription or not subscription.enabled:
                continue
            
            # 检查过滤器
            if await self._check_filters(event, subscription.filters):
                matching_subscriptions.append(subscription_id)
        
        return matching_subscriptions
    
    async def _check_filters(self, event: EventBusEvent, filters: List[EventFilter]) -> bool:
        """检查事件是否通过过滤器"""
        if not filters:
            return True
        
        for event_filter in filters:
            if not event_filter.enabled:
                continue
            
            if not await self._apply_filter(event, event_filter):
                return False
        
        return True
    
    async def _apply_filter(self, event: EventBusEvent, event_filter: EventFilter) -> bool:
        """应用单个过滤器"""
        try:
            if event_filter.filter_type == EventFilterType.SOURCE:
                return event.source == event_filter.value
            
            elif event_filter.filter_type == EventFilterType.EVENT_TYPE:
                return event.event_type == EventBusEventType(event_filter.value)
            
            elif event_filter.filter_type == EventFilterType.DATA_FIELD:
                # 检查数据字段
                field_path = event_filter.pattern
                field_value = self._get_nested_value(event.data, field_path)
                return field_value == event_filter.value
            
            elif event_filter.filter_type == EventFilterType.REGEX:
                # 正则表达式匹配
                pattern = re.compile(event_filter.pattern)
                text = str(event_filter.value)
                return bool(pattern.search(text))
            
            elif event_filter.filter_type == EventFilterType.CUSTOM:
                # 自定义过滤器（通过缓存的函数）
                filter_func = await self.filter_cache.get(event_filter.filter_id)
                if filter_func and callable(filter_func):
                    return await filter_func(event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying filter {event_filter.filter_id}: {e}")
            return False
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """获取嵌套字典值"""
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    async def _execute_handler(self, event: EventBusEvent, subscription: EventSubscription) -> None:
        """执行事件处理器"""
        start_time = time.time()
        
        try:
            # 执行处理器
            if asyncio.iscoroutinefunction(subscription.handler):
                await subscription.handler(event)
            else:
                subscription.handler(event)
            
            # 记录成功结果
            duration = time.time() - start_time
            result = EventProcessingResult(
                event_id=event.event_id,
                subscription_id=subscription.subscription_id,
                success=True,
                duration=duration,
                error=None,
                timestamp=datetime.now()
            )
            
            self.processing_results.append(result)
            
        except Exception as e:
            # 记录失败结果
            duration = time.time() - start_time
            result = EventProcessingResult(
                event_id=event.event_id,
                subscription_id=subscription.subscription_id,
                success=False,
                duration=duration,
                error=str(e),
                timestamp=datetime.now()
            )
            
            self.processing_results.append(result)
            self.logger.error(f"Error executing handler for subscription {subscription.subscription_id}: {e}")
    
    async def add_custom_filter(self, filter_id: str, filter_func: Callable) -> None:
        """添加自定义过滤器函数"""
        await self.filter_cache.set(filter_id, filter_func)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取处理器统计信息"""
        return {
            "running": self.running,
            "workers": len(self.worker_tasks),
            "subscriptions": len(self.subscriptions),
            "processed_events": self.processed_events,
            "failed_events": self.failed_events,
            "success_rate": self.processed_events / (self.processed_events + self.failed_events) if (self.processed_events + self.failed_events) > 0 else 0.0,
            "average_processing_time": self.total_processing_time / self.processed_events if self.processed_events > 0 else 0.0,
            "queue_sizes": {
                priority.name: queue.qsize()
                for priority, queue in self.event_queues.items()
            },
            "recent_results": [
                asdict(result) for result in list(self.processing_results)[-10:]
            ]
        }


class SmartUIEventListener:
    """SmartUI事件监听器"""
    
    def __init__(self, event_processor: EventProcessor):
        self.event_processor = event_processor
        self.logger = logging.getLogger(f"{__name__}.SmartUIEventListener")
        
        # 订阅ID存储
        self.subscription_ids: List[str] = []
        
        self.logger.info("SmartUI Event Listener initialized")
    
    async def start(self) -> None:
        """启动事件监听"""
        # 订阅用户行为事件
        user_behavior_sub = await self.event_processor.subscribe(
            event_types=[
                EventBusEventType.USER_INTERACTION,
                EventBusEventType.USER_BEHAVIOR_ANALYZED
            ],
            handler=self.handle_user_behavior_event,
            priority=EventPriority.HIGH
        )
        self.subscription_ids.append(user_behavior_sub)
        
        # 订阅API状态变化事件
        api_state_sub = await self.event_processor.subscribe(
            event_types=[EventBusEventType.API_STATE_CHANGED],
            handler=self.handle_api_state_changed,
            priority=EventPriority.NORMAL
        )
        self.subscription_ids.append(api_state_sub)
        
        # 订阅UI相关事件
        ui_events_sub = await self.event_processor.subscribe(
            event_types=[
                EventBusEventType.UI_GENERATED,
                EventBusEventType.UI_RENDERED,
                EventBusEventType.UI_COMPONENT_UPDATED,
                EventBusEventType.UI_THEME_CHANGED,
                EventBusEventType.UI_LAYOUT_CHANGED
            ],
            handler=self.handle_ui_event,
            priority=EventPriority.NORMAL
        )
        self.subscription_ids.append(ui_events_sub)
        
        # 订阅MCP通信事件
        mcp_events_sub = await self.event_processor.subscribe(
            event_types=[
                EventBusEventType.MCP_SERVICE_REGISTERED,
                EventBusEventType.MCP_SERVICE_UNREGISTERED,
                EventBusEventType.MCP_REQUEST_SENT,
                EventBusEventType.MCP_RESPONSE_RECEIVED,
                EventBusEventType.MCP_NOTIFICATION_RECEIVED
            ],
            handler=self.handle_mcp_event,
            priority=EventPriority.NORMAL
        )
        self.subscription_ids.append(mcp_events_sub)
        
        # 订阅决策事件
        decision_sub = await self.event_processor.subscribe(
            event_types=[EventBusEventType.DECISION_MADE],
            handler=self.handle_decision_event,
            priority=EventPriority.HIGH
        )
        self.subscription_ids.append(decision_sub)
        
        self.logger.info(f"Started {len(self.subscription_ids)} event subscriptions")
    
    async def stop(self) -> None:
        """停止事件监听"""
        for subscription_id in self.subscription_ids:
            await self.event_processor.unsubscribe(subscription_id)
        
        self.subscription_ids.clear()
        self.logger.info("Stopped all event subscriptions")
    
    async def handle_user_behavior_event(self, event: EventBusEvent) -> None:
        """处理用户行为事件"""
        try:
            if event.event_type == EventBusEventType.USER_INTERACTION:
                # 用户交互事件
                interaction_data = event.data
                self.logger.debug(f"User interaction: {interaction_data.get('interaction_type')}")
                
                # 可以在这里触发UI适配逻辑
                await publish_event(
                    event_type=EventBusEventType.UI_ADAPTATION_REQUESTED,
                    data={
                        "trigger": "user_interaction",
                        "interaction_data": interaction_data
                    },
                    source="smartui_event_listener"
                )
            
            elif event.event_type == EventBusEventType.USER_BEHAVIOR_ANALYZED:
                # 用户行为分析结果
                analysis_data = event.data
                self.logger.debug(f"User behavior analyzed: {analysis_data.get('behavior_type')}")
                
                # 触发智能决策
                await publish_event(
                    event_type=EventBusEventType.DECISION_REQUESTED,
                    data={
                        "trigger": "behavior_analysis",
                        "analysis_data": analysis_data
                    },
                    source="smartui_event_listener"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling user behavior event: {e}")
    
    async def handle_api_state_changed(self, event: EventBusEvent) -> None:
        """处理API状态变化事件"""
        try:
            state_data = event.data
            path = state_data.get("path")
            value = state_data.get("value")
            
            self.logger.debug(f"API state changed: {path} = {value}")
            
            # 如果是UI相关状态变化，触发UI更新
            if path and path.startswith("ui."):
                await publish_event(
                    event_type=EventBusEventType.UI_UPDATE_REQUESTED,
                    data={
                        "trigger": "state_change",
                        "path": path,
                        "value": value
                    },
                    source="smartui_event_listener"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling API state changed event: {e}")
    
    async def handle_ui_event(self, event: EventBusEvent) -> None:
        """处理UI事件"""
        try:
            self.logger.debug(f"UI event: {event.event_type.value}")
            
            if event.event_type == EventBusEventType.UI_GENERATED:
                # UI生成完成，触发渲染
                ui_data = event.data
                await publish_event(
                    event_type=EventBusEventType.UI_RENDER_REQUESTED,
                    data=ui_data,
                    source="smartui_event_listener"
                )
            
            elif event.event_type == EventBusEventType.UI_COMPONENT_UPDATED:
                # 组件更新，可能需要重新分析用户行为
                component_data = event.data
                await publish_event(
                    event_type=EventBusEventType.USER_ANALYSIS_REQUESTED,
                    data={
                        "trigger": "component_update",
                        "component_data": component_data
                    },
                    source="smartui_event_listener"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling UI event: {e}")
    
    async def handle_mcp_event(self, event: EventBusEvent) -> None:
        """处理MCP事件"""
        try:
            self.logger.debug(f"MCP event: {event.event_type.value}")
            
            if event.event_type == EventBusEventType.MCP_SERVICE_REGISTERED:
                # 新服务注册，可能需要更新UI
                service_data = event.data
                await publish_event(
                    event_type=EventBusEventType.UI_UPDATE_REQUESTED,
                    data={
                        "trigger": "service_registered",
                        "service_data": service_data
                    },
                    source="smartui_event_listener"
                )
            
            elif event.event_type == EventBusEventType.MCP_NOTIFICATION_RECEIVED:
                # 收到MCP通知，可能需要更新UI状态
                notification_data = event.data
                await publish_event(
                    event_type=EventBusEventType.API_STATE_UPDATE_REQUESTED,
                    data={
                        "trigger": "mcp_notification",
                        "notification_data": notification_data
                    },
                    source="smartui_event_listener"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling MCP event: {e}")
    
    async def handle_decision_event(self, event: EventBusEvent) -> None:
        """处理决策事件"""
        try:
            decision_data = event.data
            decision_type = decision_data.get("decision_type")
            
            self.logger.debug(f"Decision made: {decision_type}")
            
            # 根据决策类型执行相应操作
            if decision_type == "ui_adaptation":
                # UI适配决策
                await publish_event(
                    event_type=EventBusEventType.UI_ADAPTATION_EXECUTED,
                    data=decision_data,
                    source="smartui_event_listener"
                )
            
            elif decision_type == "layout_optimization":
                # 布局优化决策
                await publish_event(
                    event_type=EventBusEventType.UI_LAYOUT_CHANGED,
                    data=decision_data,
                    source="smartui_event_listener"
                )
            
            elif decision_type == "theme_adjustment":
                # 主题调整决策
                await publish_event(
                    event_type=EventBusEventType.UI_THEME_CHANGED,
                    data=decision_data,
                    source="smartui_event_listener"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling decision event: {e}")


class EventListenerSystem:
    """事件监听系统"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.EventListenerSystem")
        
        # 事件处理器
        self.event_processor = EventProcessor(
            max_workers=self.config.get("max_workers", 10),
            queue_size=self.config.get("queue_size", 1000)
        )
        
        # SmartUI事件监听器
        self.smartui_listener = SmartUIEventListener(self.event_processor)
        
        # 系统状态
        self.running = False
        
        self.logger.info("Event Listener System initialized")
    
    async def start(self) -> Dict[str, Any]:
        """启动事件监听系统"""
        try:
            if self.running:
                return {"success": True, "message": "Already running"}
            
            # 启动事件处理器
            await self.event_processor.start()
            
            # 启动SmartUI监听器
            await self.smartui_listener.start()
            
            self.running = True
            
            self.logger.info("Event Listener System started")
            return {
                "success": True,
                "message": "Event Listener System started successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error starting Event Listener System: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def stop(self) -> Dict[str, Any]:
        """停止事件监听系统"""
        try:
            if not self.running:
                return {"success": True, "message": "Already stopped"}
            
            # 停止SmartUI监听器
            await self.smartui_listener.stop()
            
            # 停止事件处理器
            await self.event_processor.stop()
            
            self.running = False
            
            self.logger.info("Event Listener System stopped")
            return {
                "success": True,
                "message": "Event Listener System stopped successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping Event Listener System: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        processor_stats = await self.event_processor.get_statistics()
        
        return {
            "running": self.running,
            "event_processor": processor_stats,
            "smartui_listener": {
                "subscriptions": len(self.smartui_listener.subscription_ids)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def process_external_event(
        self,
        event_type: EventBusEventType,
        data: Dict[str, Any],
        source: str,
        priority: EventPriority = EventPriority.NORMAL
    ) -> Dict[str, Any]:
        """处理外部事件"""
        try:
            event = EventBusEvent(
                event_id=generate_id("ext_event_"),
                event_type=event_type,
                data=data,
                source=source,
                timestamp=datetime.now()
            )
            
            await self.event_processor.process_event(event, priority)
            
            return {
                "success": True,
                "event_id": event.event_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing external event: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

