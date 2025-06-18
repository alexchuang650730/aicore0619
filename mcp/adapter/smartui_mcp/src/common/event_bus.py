"""
SmartUI MCP 事件总线系统

实现了一个高性能的异步事件总线，支持事件发布、订阅、过滤和历史记录。
这是SmartUI MCP系统中各组件间通信的核心基础设施。
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
import weakref
import uuid
import json

from .interfaces import (
    IEventBus, EventBusEvent, EventBusEventType, EventHandler
)


class EventSubscription:
    """事件订阅对象"""
    
    def __init__(
        self,
        subscription_id: str,
        event_type: EventBusEventType,
        handler: EventHandler,
        filter_func: Optional[Callable[[EventBusEvent], bool]] = None,
        subscriber_name: Optional[str] = None
    ):
        self.subscription_id = subscription_id
        self.event_type = event_type
        self.handler = handler
        self.filter_func = filter_func
        self.subscriber_name = subscriber_name
        self.created_at = datetime.now()
        self.last_triggered = None
        self.trigger_count = 0


class EventBusMetrics:
    """事件总线性能指标"""
    
    def __init__(self):
        self.events_published = 0
        self.events_processed = 0
        self.events_failed = 0
        self.subscriptions_created = 0
        self.subscriptions_removed = 0
        self.average_processing_time = 0.0
        self.peak_processing_time = 0.0
        self.last_reset = datetime.now()
    
    def reset(self):
        """重置指标"""
        self.__init__()


class SmartUIEventBus(IEventBus):
    """SmartUI事件总线实现"""
    
    def __init__(
        self,
        max_history_size: int = 1000,
        cleanup_interval: int = 3600,
        enable_metrics: bool = True
    ):
        self.max_history_size = max_history_size
        self.cleanup_interval = cleanup_interval
        self.enable_metrics = enable_metrics
        
        # 订阅管理
        self._subscriptions: Dict[EventBusEventType, List[EventSubscription]] = defaultdict(list)
        self._subscription_by_id: Dict[str, EventSubscription] = {}
        
        # 事件历史
        self._event_history: deque = deque(maxlen=max_history_size)
        
        # 性能指标
        self._metrics = EventBusMetrics() if enable_metrics else None
        
        # 异步任务管理
        self._processing_tasks: Dict[str, asyncio.Task] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # 日志
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 启动清理任务
        if cleanup_interval > 0:
            self._start_cleanup_task()
    
    async def publish(self, event: EventBusEvent) -> None:
        """发布事件"""
        try:
            # 记录事件到历史
            self._event_history.append(event)
            
            # 更新指标
            if self._metrics:
                self._metrics.events_published += 1
            
            # 获取订阅者
            subscriptions = self._subscriptions.get(event.event_type, [])
            
            if not subscriptions:
                self.logger.debug(f"No subscribers for event type: {event.event_type}")
                return
            
            # 异步处理所有订阅者
            tasks = []
            for subscription in subscriptions:
                task = asyncio.create_task(
                    self._process_subscription(event, subscription)
                )
                tasks.append(task)
            
            # 等待所有任务完成
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            self.logger.debug(
                f"Published event {event.event_type} from {event.source} "
                f"to {len(subscriptions)} subscribers"
            )
            
        except Exception as e:
            self.logger.error(f"Error publishing event: {e}")
            if self._metrics:
                self._metrics.events_failed += 1
            raise
    
    async def _process_subscription(
        self,
        event: EventBusEvent,
        subscription: EventSubscription
    ) -> None:
        """处理单个订阅"""
        start_time = datetime.now()
        
        try:
            # 应用过滤器
            if subscription.filter_func and not subscription.filter_func(event):
                return
            
            # 调用处理函数
            if asyncio.iscoroutinefunction(subscription.handler):
                await subscription.handler(event)
            else:
                subscription.handler(event)
            
            # 更新订阅统计
            subscription.last_triggered = datetime.now()
            subscription.trigger_count += 1
            
            # 更新指标
            if self._metrics:
                processing_time = (datetime.now() - start_time).total_seconds()
                self._metrics.events_processed += 1
                
                # 更新平均处理时间
                total_events = self._metrics.events_processed
                self._metrics.average_processing_time = (
                    (self._metrics.average_processing_time * (total_events - 1) + processing_time) / total_events
                )
                
                # 更新峰值处理时间
                if processing_time > self._metrics.peak_processing_time:
                    self._metrics.peak_processing_time = processing_time
            
        except Exception as e:
            self.logger.error(
                f"Error processing subscription {subscription.subscription_id}: {e}"
            )
            if self._metrics:
                self._metrics.events_failed += 1
    
    async def subscribe(
        self,
        event_type: EventBusEventType,
        handler: EventHandler,
        filter_func: Optional[Callable[[EventBusEvent], bool]] = None,
        subscriber_name: Optional[str] = None
    ) -> str:
        """订阅事件"""
        subscription_id = str(uuid.uuid4())
        
        subscription = EventSubscription(
            subscription_id=subscription_id,
            event_type=event_type,
            handler=handler,
            filter_func=filter_func,
            subscriber_name=subscriber_name
        )
        
        # 添加到订阅列表
        self._subscriptions[event_type].append(subscription)
        self._subscription_by_id[subscription_id] = subscription
        
        # 更新指标
        if self._metrics:
            self._metrics.subscriptions_created += 1
        
        self.logger.debug(
            f"Created subscription {subscription_id} for event type {event_type} "
            f"by {subscriber_name or 'unknown'}"
        )
        
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        subscription = self._subscription_by_id.get(subscription_id)
        if not subscription:
            return False
        
        # 从订阅列表中移除
        event_subscriptions = self._subscriptions[subscription.event_type]
        event_subscriptions[:] = [
            sub for sub in event_subscriptions 
            if sub.subscription_id != subscription_id
        ]
        
        # 从ID映射中移除
        del self._subscription_by_id[subscription_id]
        
        # 更新指标
        if self._metrics:
            self._metrics.subscriptions_removed += 1
        
        self.logger.debug(f"Removed subscription {subscription_id}")
        
        return True
    
    async def get_event_history(
        self,
        event_type: Optional[EventBusEventType] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[EventBusEvent]:
        """获取事件历史"""
        events = list(self._event_history)
        
        # 应用过滤器
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if source:
            events = [e for e in events if e.source == source]
        
        # 按时间倒序排列并限制数量
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
    
    async def get_subscription_info(self) -> Dict[str, Any]:
        """获取订阅信息"""
        subscription_info = {}
        
        for event_type, subscriptions in self._subscriptions.items():
            subscription_info[event_type.value] = [
                {
                    "subscription_id": sub.subscription_id,
                    "subscriber_name": sub.subscriber_name,
                    "created_at": sub.created_at.isoformat(),
                    "last_triggered": sub.last_triggered.isoformat() if sub.last_triggered else None,
                    "trigger_count": sub.trigger_count,
                    "has_filter": sub.filter_func is not None
                }
                for sub in subscriptions
            ]
        
        return subscription_info
    
    async def get_metrics(self) -> Optional[Dict[str, Any]]:
        """获取性能指标"""
        if not self._metrics:
            return None
        
        return {
            "events_published": self._metrics.events_published,
            "events_processed": self._metrics.events_processed,
            "events_failed": self._metrics.events_failed,
            "subscriptions_created": self._metrics.subscriptions_created,
            "subscriptions_removed": self._metrics.subscriptions_removed,
            "average_processing_time": self._metrics.average_processing_time,
            "peak_processing_time": self._metrics.peak_processing_time,
            "last_reset": self._metrics.last_reset.isoformat(),
            "active_subscriptions": len(self._subscription_by_id),
            "event_history_size": len(self._event_history)
        }
    
    async def reset_metrics(self) -> None:
        """重置性能指标"""
        if self._metrics:
            self._metrics.reset()
    
    def _start_cleanup_task(self) -> None:
        """启动清理任务"""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.cleanup_interval)
                    await self._cleanup_old_events()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in cleanup task: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def _cleanup_old_events(self) -> None:
        """清理旧事件"""
        # 事件历史已经通过deque的maxlen自动限制
        # 这里可以添加其他清理逻辑，比如清理失效的订阅等
        
        # 清理已完成的处理任务
        completed_tasks = [
            task_id for task_id, task in self._processing_tasks.items()
            if task.done()
        ]
        
        for task_id in completed_tasks:
            del self._processing_tasks[task_id]
        
        self.logger.debug(f"Cleaned up {len(completed_tasks)} completed tasks")
    
    async def shutdown(self) -> None:
        """关闭事件总线"""
        # 取消清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 取消所有处理任务
        for task in self._processing_tasks.values():
            task.cancel()
        
        if self._processing_tasks:
            await asyncio.gather(
                *self._processing_tasks.values(),
                return_exceptions=True
            )
        
        # 清理数据
        self._subscriptions.clear()
        self._subscription_by_id.clear()
        self._event_history.clear()
        self._processing_tasks.clear()
        
        self.logger.info("Event bus shutdown complete")


class EventBusFactory:
    """事件总线工厂"""
    
    _instance: Optional[SmartUIEventBus] = None
    
    @classmethod
    def get_instance(
        cls,
        max_history_size: int = 1000,
        cleanup_interval: int = 3600,
        enable_metrics: bool = True
    ) -> SmartUIEventBus:
        """获取事件总线单例实例"""
        if cls._instance is None:
            cls._instance = SmartUIEventBus(
                max_history_size=max_history_size,
                cleanup_interval=cleanup_interval,
                enable_metrics=enable_metrics
            )
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例"""
        if cls._instance:
            asyncio.create_task(cls._instance.shutdown())
        cls._instance = None


# 便利函数

async def publish_event(
    event_type: EventBusEventType,
    data: Dict[str, Any],
    source: str,
    event_bus: Optional[IEventBus] = None
) -> None:
    """发布事件的便利函数"""
    if event_bus is None:
        event_bus = EventBusFactory.get_instance()
    
    event = EventBusEvent(
        event_type=event_type,
        data=data,
        source=source
    )
    
    await event_bus.publish(event)


async def subscribe_to_event(
    event_type: EventBusEventType,
    handler: EventHandler,
    filter_func: Optional[Callable[[EventBusEvent], bool]] = None,
    subscriber_name: Optional[str] = None,
    event_bus: Optional[IEventBus] = None
) -> str:
    """订阅事件的便利函数"""
    if event_bus is None:
        event_bus = EventBusFactory.get_instance()
    
    return await event_bus.subscribe(
        event_type=event_type,
        handler=handler,
        filter_func=filter_func,
        subscriber_name=subscriber_name
    )


# 装饰器

def event_handler(
    event_type: EventBusEventType,
    filter_func: Optional[Callable[[EventBusEvent], bool]] = None,
    subscriber_name: Optional[str] = None
):
    """事件处理器装饰器"""
    def decorator(func: EventHandler):
        func._event_type = event_type
        func._filter_func = filter_func
        func._subscriber_name = subscriber_name
        return func
    return decorator


class EventHandlerRegistry:
    """事件处理器注册表"""
    
    def __init__(self, event_bus: Optional[IEventBus] = None):
        self.event_bus = event_bus or EventBusFactory.get_instance()
        self.registered_handlers: List[str] = []
    
    async def register_handlers(self, handler_object: Any) -> None:
        """注册对象中的所有事件处理器"""
        for attr_name in dir(handler_object):
            attr = getattr(handler_object, attr_name)
            
            if hasattr(attr, '_event_type'):
                subscription_id = await self.event_bus.subscribe(
                    event_type=attr._event_type,
                    handler=attr,
                    filter_func=getattr(attr, '_filter_func', None),
                    subscriber_name=getattr(attr, '_subscriber_name', None) or f"{handler_object.__class__.__name__}.{attr_name}"
                )
                self.registered_handlers.append(subscription_id)
    
    async def unregister_all(self) -> None:
        """取消注册所有处理器"""
        for subscription_id in self.registered_handlers:
            await self.event_bus.unsubscribe(subscription_id)
        self.registered_handlers.clear()



# 导出主要类和函数
EventBus = SmartUIEventBus  # 为了向后兼容
__all__ = [
    'EventBus',
    'SmartUIEventBus', 
    'EventBusFactory',
    'EventSubscription',
    'EventBusMetrics',
    'publish_event',
    'subscribe_to_event',
    'event_handler',
    'EventHandlerRegistry'
]

