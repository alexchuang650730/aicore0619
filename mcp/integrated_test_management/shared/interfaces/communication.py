"""
PowerAutomation 测试管理 - 组件间通信协议

定义工作流层和适配器层之间的标准通信协议，
支持异步消息传递、事件驱动架构和错误处理。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-18
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid
import weakref


class MessageType(Enum):
    """消息类型枚举"""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    NOTIFICATION = "notification"
    ERROR = "error"


class EventType(Enum):
    """事件类型枚举"""
    TEST_STARTED = "test_started"
    TEST_COMPLETED = "test_completed"
    TEST_FAILED = "test_failed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    STRATEGY_GENERATED = "strategy_generated"
    REPORT_GENERATED = "report_generated"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Message:
    """消息数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.REQUEST
    source: str = ""
    target: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: int = 3600  # Time to live in seconds


@dataclass
class Event:
    """事件数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.TEST_STARTED
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


class MessageBus:
    """消息总线 - 实现组件间通信"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._subscribers: Dict[str, List[Callable]] = {}
        self._message_handlers: Dict[str, Callable] = {}
        self._pending_messages: Dict[str, Message] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        
    async def send_message(self, message: Message) -> Optional[Message]:
        """发送消息并等待响应"""
        try:
            self.logger.info(f"发送消息: {message.id} from {message.source} to {message.target}")
            
            # 存储待处理消息
            if message.type == MessageType.REQUEST:
                self._pending_messages[message.id] = message
            
            # 查找目标处理器
            handler = self._message_handlers.get(message.target)
            if handler:
                response = await handler(message)
                if response and message.type == MessageType.REQUEST:
                    response.correlation_id = message.id
                return response
            else:
                self.logger.warning(f"未找到目标处理器: {message.target}")
                return self._create_error_response(message, "Target handler not found")
                
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            return self._create_error_response(message, str(e))
    
    async def publish_event(self, event: Event) -> bool:
        """发布事件"""
        try:
            self.logger.info(f"发布事件: {event.type.value} from {event.source}")
            
            # 添加到事件历史
            self._event_history.append(event)
            if len(self._event_history) > self._max_history_size:
                self._event_history.pop(0)
            
            # 通知订阅者
            subscribers = self._subscribers.get(event.type.value, [])
            for subscriber in subscribers:
                try:
                    await subscriber(event)
                except Exception as e:
                    self.logger.error(f"事件订阅者处理失败: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"发布事件失败: {e}")
            return False
    
    def register_handler(self, component_name: str, handler: Callable) -> bool:
        """注册消息处理器"""
        try:
            self._message_handlers[component_name] = handler
            self.logger.info(f"注册消息处理器: {component_name}")
            return True
        except Exception as e:
            self.logger.error(f"注册处理器失败: {e}")
            return False
    
    def subscribe_to_event(self, event_type: EventType, callback: Callable) -> bool:
        """订阅事件"""
        try:
            if event_type.value not in self._subscribers:
                self._subscribers[event_type.value] = []
            
            self._subscribers[event_type.value].append(callback)
            self.logger.info(f"订阅事件: {event_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"订阅事件失败: {e}")
            return False
    
    def unsubscribe_from_event(self, event_type: EventType, callback: Callable) -> bool:
        """取消订阅事件"""
        try:
            if event_type.value in self._subscribers:
                self._subscribers[event_type.value].remove(callback)
                self.logger.info(f"取消订阅事件: {event_type.value}")
            return True
        except Exception as e:
            self.logger.error(f"取消订阅失败: {e}")
            return False
    
    def get_event_history(self, event_type: Optional[EventType] = None, 
                         limit: int = 100) -> List[Event]:
        """获取事件历史"""
        if event_type:
            filtered_events = [e for e in self._event_history if e.type == event_type]
            return filtered_events[-limit:]
        return self._event_history[-limit:]
    
    def _create_error_response(self, original_message: Message, error_msg: str) -> Message:
        """创建错误响应消息"""
        return Message(
            type=MessageType.ERROR,
            source="message_bus",
            target=original_message.source,
            payload={"error": error_msg, "original_message_id": original_message.id},
            correlation_id=original_message.id
        )


class CommunicationProtocol:
    """通信协议实现"""
    
    def __init__(self, component_name: str, message_bus: MessageBus):
        self.component_name = component_name
        self.message_bus = message_bus
        self.logger = logging.getLogger(f"{__name__}.{component_name}")
        
        # 注册自己为消息处理器
        self.message_bus.register_handler(component_name, self._handle_message)
    
    async def send_request(self, target: str, payload: Dict[str, Any], 
                          timeout: int = 30) -> Optional[Message]:
        """发送请求消息"""
        message = Message(
            type=MessageType.REQUEST,
            source=self.component_name,
            target=target,
            payload=payload
        )
        
        try:
            response = await asyncio.wait_for(
                self.message_bus.send_message(message),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            self.logger.error(f"请求超时: {message.id}")
            return None
    
    async def send_notification(self, target: str, payload: Dict[str, Any]) -> bool:
        """发送通知消息"""
        message = Message(
            type=MessageType.NOTIFICATION,
            source=self.component_name,
            target=target,
            payload=payload
        )
        
        response = await self.message_bus.send_message(message)
        return response is not None
    
    async def publish_event(self, event_type: EventType, data: Dict[str, Any], 
                           tags: List[str] = None) -> bool:
        """发布事件"""
        event = Event(
            type=event_type,
            source=self.component_name,
            data=data,
            tags=tags or []
        )
        
        return await self.message_bus.publish_event(event)
    
    def subscribe_to_event(self, event_type: EventType, callback: Callable) -> bool:
        """订阅事件"""
        return self.message_bus.subscribe_to_event(event_type, callback)
    
    async def _handle_message(self, message: Message) -> Optional[Message]:
        """处理接收到的消息 - 子类应重写此方法"""
        self.logger.info(f"收到消息: {message.type.value} from {message.source}")
        
        # 默认响应
        if message.type == MessageType.REQUEST:
            return Message(
                type=MessageType.RESPONSE,
                source=self.component_name,
                target=message.source,
                payload={"status": "received", "message": "Default handler"},
                correlation_id=message.id
            )
        
        return None


class WorkflowCommunicationAdapter(CommunicationProtocol):
    """工作流层通信适配器"""
    
    def __init__(self, message_bus: MessageBus):
        super().__init__("test_manager_workflow", message_bus)
        self._execution_callbacks: Dict[str, Callable] = {}
    
    async def request_test_execution(self, execution_plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """请求测试执行"""
        response = await self.send_request(
            target="test_execution_engine",
            payload={
                "action": "execute_tests",
                "plan": execution_plan
            }
        )
        
        if response and response.type != MessageType.ERROR:
            return response.payload
        return None
    
    async def request_framework_generation(self, modules: List[str]) -> Optional[Dict[str, Any]]:
        """请求测试框架生成"""
        response = await self.send_request(
            target="test_execution_engine",
            payload={
                "action": "generate_frameworks",
                "modules": modules
            }
        )
        
        if response and response.type != MessageType.ERROR:
            return response.payload
        return None
    
    async def _handle_message(self, message: Message) -> Optional[Message]:
        """处理工作流层消息"""
        if message.type == MessageType.REQUEST:
            action = message.payload.get("action")
            
            if action == "create_strategy":
                # 处理策略创建请求
                return await self._handle_strategy_creation(message)
            elif action == "get_status":
                # 处理状态查询请求
                return await self._handle_status_query(message)
        
        return await super()._handle_message(message)
    
    async def _handle_strategy_creation(self, message: Message) -> Message:
        """处理策略创建"""
        # 实际的策略创建逻辑
        return Message(
            type=MessageType.RESPONSE,
            source=self.component_name,
            target=message.source,
            payload={"status": "strategy_created", "strategy_id": str(uuid.uuid4())},
            correlation_id=message.id
        )
    
    async def _handle_status_query(self, message: Message) -> Message:
        """处理状态查询"""
        return Message(
            type=MessageType.RESPONSE,
            source=self.component_name,
            target=message.source,
            payload={"status": "active", "workflows": []},
            correlation_id=message.id
        )


class AdapterCommunicationAdapter(CommunicationProtocol):
    """适配器层通信适配器"""
    
    def __init__(self, message_bus: MessageBus):
        super().__init__("test_execution_engine", message_bus)
    
    async def report_execution_progress(self, workflow_id: str, progress: Dict[str, Any]) -> bool:
        """报告执行进度"""
        return await self.publish_event(
            event_type=EventType.TEST_STARTED,
            data={
                "workflow_id": workflow_id,
                "progress": progress
            }
        )
    
    async def report_execution_completion(self, workflow_id: str, result: Dict[str, Any]) -> bool:
        """报告执行完成"""
        return await self.publish_event(
            event_type=EventType.TEST_COMPLETED,
            data={
                "workflow_id": workflow_id,
                "result": result
            }
        )
    
    async def _handle_message(self, message: Message) -> Optional[Message]:
        """处理适配器层消息"""
        if message.type == MessageType.REQUEST:
            action = message.payload.get("action")
            
            if action == "execute_tests":
                return await self._handle_test_execution(message)
            elif action == "generate_frameworks":
                return await self._handle_framework_generation(message)
            elif action == "fix_issues":
                return await self._handle_issue_fixing(message)
        
        return await super()._handle_message(message)
    
    async def _handle_test_execution(self, message: Message) -> Message:
        """处理测试执行请求"""
        plan = message.payload.get("plan", {})
        
        # 模拟测试执行
        execution_id = str(uuid.uuid4())
        
        return Message(
            type=MessageType.RESPONSE,
            source=self.component_name,
            target=message.source,
            payload={
                "status": "execution_started",
                "execution_id": execution_id,
                "estimated_duration": 300
            },
            correlation_id=message.id
        )
    
    async def _handle_framework_generation(self, message: Message) -> Message:
        """处理框架生成请求"""
        modules = message.payload.get("modules", [])
        
        return Message(
            type=MessageType.RESPONSE,
            source=self.component_name,
            target=message.source,
            payload={
                "status": "generation_completed",
                "generated_files": len(modules) * 2,
                "modules": modules
            },
            correlation_id=message.id
        )
    
    async def _handle_issue_fixing(self, message: Message) -> Message:
        """处理问题修复请求"""
        issues = message.payload.get("issues", [])
        
        return Message(
            type=MessageType.RESPONSE,
            source=self.component_name,
            target=message.source,
            payload={
                "status": "fixing_completed",
                "fixed_issues": len(issues),
                "remaining_issues": 0
            },
            correlation_id=message.id
        )


# 全局消息总线实例
_global_message_bus = None

def get_message_bus() -> MessageBus:
    """获取全局消息总线实例"""
    global _global_message_bus
    if _global_message_bus is None:
        _global_message_bus = MessageBus()
    return _global_message_bus


def create_workflow_adapter() -> WorkflowCommunicationAdapter:
    """创建工作流通信适配器"""
    return WorkflowCommunicationAdapter(get_message_bus())


def create_adapter_communication() -> AdapterCommunicationAdapter:
    """创建适配器通信适配器"""
    return AdapterCommunicationAdapter(get_message_bus())

