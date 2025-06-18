"""
SmartUI MCP 组件通信协议

定义了SmartUI MCP系统中各组件间的通信协议和消息格式，
确保组件间的标准化通信和数据交换。
"""

from typing import Dict, List, Optional, Any, Union, Literal, Callable
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid

from .ui_models import UIConfiguration, UIComponent


class MessageType(str, Enum):
    """消息类型枚举"""
    # 请求消息
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    
    # 系统消息
    HEARTBEAT = "heartbeat"
    HEALTH_CHECK = "health_check"
    STATUS_UPDATE = "status_update"
    
    # 错误消息
    ERROR = "error"
    WARNING = "warning"


class MessagePriority(str, Enum):
    """消息优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ComponentMessageType(str, Enum):
    """组件消息类型枚举"""
    # UI相关消息
    UI_RENDER_REQUEST = "ui_render_request"
    UI_RENDER_RESPONSE = "ui_render_response"
    UI_UPDATE_REQUEST = "ui_update_request"
    UI_UPDATE_RESPONSE = "ui_update_response"
    UI_COMPONENT_EVENT = "ui_component_event"
    
    # 用户分析消息
    USER_INTERACTION_DATA = "user_interaction_data"
    USER_BEHAVIOR_ANALYSIS = "user_behavior_analysis"
    USER_PROFILE_UPDATE = "user_profile_update"
    USER_INTENT_PREDICTION = "user_intent_prediction"
    
    # 决策引擎消息
    DECISION_REQUEST = "decision_request"
    DECISION_RESPONSE = "decision_response"
    RULE_EVALUATION = "rule_evaluation"
    ADAPTATION_TRIGGER = "adaptation_trigger"
    
    # API状态管理消息
    STATE_GET_REQUEST = "state_get_request"
    STATE_SET_REQUEST = "state_set_request"
    STATE_UPDATE_REQUEST = "state_update_request"
    STATE_CHANGE_NOTIFICATION = "state_change_notification"
    STATE_SYNC_REQUEST = "state_sync_request"
    
    # MCP集成消息
    MCP_REGISTER_REQUEST = "mcp_register_request"
    MCP_MESSAGE_FORWARD = "mcp_message_forward"
    MCP_HEALTH_CHECK = "mcp_health_check"
    MCP_EVENT_SUBSCRIPTION = "mcp_event_subscription"
    
    # 性能监控消息
    PERFORMANCE_METRIC = "performance_metric"
    PERFORMANCE_ALERT = "performance_alert"
    PERFORMANCE_REPORT = "performance_report"


class MessageHeader(BaseModel):
    """消息头部"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType
    component_message_type: ComponentMessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    source_component: str
    target_component: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None  # 用于关联请求和响应
    reply_to: Optional[str] = None  # 回复地址
    ttl: Optional[int] = None  # 消息生存时间（秒）
    version: str = "1.0"


class MessagePayload(BaseModel):
    """消息载荷基类"""
    pass


class UIRenderRequestPayload(MessagePayload):
    """UI渲染请求载荷"""
    ui_configuration: UIConfiguration
    render_options: Optional[Dict[str, Any]] = None
    target_format: Literal["html", "json", "react"] = "html"
    include_assets: bool = True
    optimize: bool = True


class UIRenderResponsePayload(MessagePayload):
    """UI渲染响应载荷"""
    success: bool
    rendered_content: Optional[str] = None
    assets: Optional[Dict[str, str]] = None  # CSS, JS等资源
    render_time: float
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class UIUpdateRequestPayload(MessagePayload):
    """UI更新请求载荷"""
    component_id: str
    updates: Dict[str, Any]
    update_type: Literal["props", "style", "content", "replace"] = "props"
    animate: bool = False
    animation_config: Optional[Dict[str, Any]] = None


class UIUpdateResponsePayload(MessagePayload):
    """UI更新响应载荷"""
    success: bool
    component_id: str
    applied_updates: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class UIComponentEventPayload(MessagePayload):
    """UI组件事件载荷"""
    component_id: str
    event_type: str
    event_data: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class UserInteractionDataPayload(MessagePayload):
    """用户交互数据载荷"""
    user_id: str
    session_id: str
    interaction_type: str
    interaction_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class UserBehaviorAnalysisPayload(MessagePayload):
    """用户行为分析载荷"""
    user_id: str
    analysis_results: Dict[str, Any]
    behavior_patterns: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    confidence_score: float
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


class DecisionRequestPayload(MessagePayload):
    """决策请求载荷"""
    decision_context: Dict[str, Any]
    available_actions: List[str]
    constraints: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None


class DecisionResponsePayload(MessagePayload):
    """决策响应载荷"""
    success: bool
    selected_action: Optional[str] = None
    action_parameters: Optional[Dict[str, Any]] = None
    confidence_score: float
    reasoning: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    decision_time: float


class StateRequestPayload(MessagePayload):
    """状态请求载荷"""
    operation: Literal["get", "set", "update", "delete", "watch", "unwatch"]
    path: str
    value: Optional[Any] = None
    updates: Optional[Dict[str, Any]] = None
    watch_config: Optional[Dict[str, Any]] = None


class StateResponsePayload(MessagePayload):
    """状态响应载荷"""
    success: bool
    operation: str
    path: str
    value: Optional[Any] = None
    previous_value: Optional[Any] = None
    watcher_id: Optional[str] = None
    error_message: Optional[str] = None


class StateChangeNotificationPayload(MessagePayload):
    """状态变化通知载荷"""
    path: str
    new_value: Any
    old_value: Any
    change_type: Literal["create", "update", "delete"]
    change_source: str
    timestamp: datetime = Field(default_factory=datetime.now)


class MCPMessageForwardPayload(MessagePayload):
    """MCP消息转发载荷"""
    target_mcp_id: str
    original_message: Dict[str, Any]
    forward_options: Optional[Dict[str, Any]] = None


class PerformanceMetricPayload(MessagePayload):
    """性能指标载荷"""
    metric_name: str
    metric_value: float
    metric_unit: str
    tags: Optional[Dict[str, str]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    component_source: str


class ComponentMessage(BaseModel):
    """组件消息"""
    header: MessageHeader
    payload: MessagePayload
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "header": self.header.dict(),
            "payload": self.payload.dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentMessage":
        """从字典创建消息"""
        header = MessageHeader(**data["header"])
        
        # 根据消息类型创建相应的载荷
        payload_class = _get_payload_class(header.component_message_type)
        payload = payload_class(**data["payload"])
        
        return cls(header=header, payload=payload)


class MessageBus:
    """消息总线"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []
    
    def register_handler(
        self,
        component_name: str,
        message_type: ComponentMessageType,
        handler: Callable[[ComponentMessage], Any]
    ) -> None:
        """注册消息处理器"""
        key = f"{component_name}:{message_type.value}"
        if key not in self._handlers:
            self._handlers[key] = []
        self._handlers[key].append(handler)
    
    def add_middleware(self, middleware: Callable[[ComponentMessage], ComponentMessage]) -> None:
        """添加中间件"""
        self._middleware.append(middleware)
    
    async def send_message(self, message: ComponentMessage) -> Optional[Any]:
        """发送消息"""
        # 应用中间件
        for middleware in self._middleware:
            message = middleware(message)
        
        # 查找处理器
        target = message.header.target_component
        message_type = message.header.component_message_type
        key = f"{target}:{message_type.value}"
        
        handlers = self._handlers.get(key, [])
        if not handlers:
            return None
        
        # 执行处理器
        results = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(message)
            else:
                result = handler(message)
            results.append(result)
        
        return results[0] if len(results) == 1 else results


class MessageFactory:
    """消息工厂"""
    
    @staticmethod
    def create_ui_render_request(
        source_component: str,
        target_component: str,
        ui_configuration: UIConfiguration,
        render_options: Optional[Dict[str, Any]] = None
    ) -> ComponentMessage:
        """创建UI渲染请求"""
        header = MessageHeader(
            message_type=MessageType.REQUEST,
            component_message_type=ComponentMessageType.UI_RENDER_REQUEST,
            source_component=source_component,
            target_component=target_component
        )
        
        payload = UIRenderRequestPayload(
            ui_configuration=ui_configuration,
            render_options=render_options
        )
        
        return ComponentMessage(header=header, payload=payload)
    
    @staticmethod
    def create_ui_render_response(
        source_component: str,
        correlation_id: str,
        success: bool,
        rendered_content: Optional[str] = None,
        render_time: float = 0.0,
        error_message: Optional[str] = None
    ) -> ComponentMessage:
        """创建UI渲染响应"""
        header = MessageHeader(
            message_type=MessageType.RESPONSE,
            component_message_type=ComponentMessageType.UI_RENDER_RESPONSE,
            source_component=source_component,
            correlation_id=correlation_id
        )
        
        payload = UIRenderResponsePayload(
            success=success,
            rendered_content=rendered_content,
            render_time=render_time,
            error_message=error_message
        )
        
        return ComponentMessage(header=header, payload=payload)
    
    @staticmethod
    def create_user_interaction_data(
        source_component: str,
        user_id: str,
        session_id: str,
        interaction_type: str,
        interaction_data: Dict[str, Any]
    ) -> ComponentMessage:
        """创建用户交互数据消息"""
        header = MessageHeader(
            message_type=MessageType.NOTIFICATION,
            component_message_type=ComponentMessageType.USER_INTERACTION_DATA,
            source_component=source_component
        )
        
        payload = UserInteractionDataPayload(
            user_id=user_id,
            session_id=session_id,
            interaction_type=interaction_type,
            interaction_data=interaction_data
        )
        
        return ComponentMessage(header=header, payload=payload)
    
    @staticmethod
    def create_decision_request(
        source_component: str,
        target_component: str,
        decision_context: Dict[str, Any],
        available_actions: List[str]
    ) -> ComponentMessage:
        """创建决策请求"""
        header = MessageHeader(
            message_type=MessageType.REQUEST,
            component_message_type=ComponentMessageType.DECISION_REQUEST,
            source_component=source_component,
            target_component=target_component
        )
        
        payload = DecisionRequestPayload(
            decision_context=decision_context,
            available_actions=available_actions
        )
        
        return ComponentMessage(header=header, payload=payload)
    
    @staticmethod
    def create_state_request(
        source_component: str,
        target_component: str,
        operation: str,
        path: str,
        value: Optional[Any] = None
    ) -> ComponentMessage:
        """创建状态请求"""
        header = MessageHeader(
            message_type=MessageType.REQUEST,
            component_message_type=ComponentMessageType.STATE_GET_REQUEST if operation == "get" else ComponentMessageType.STATE_SET_REQUEST,
            source_component=source_component,
            target_component=target_component
        )
        
        payload = StateRequestPayload(
            operation=operation,
            path=path,
            value=value
        )
        
        return ComponentMessage(header=header, payload=payload)


def _get_payload_class(message_type: ComponentMessageType) -> type:
    """根据消息类型获取载荷类"""
    payload_mapping = {
        ComponentMessageType.UI_RENDER_REQUEST: UIRenderRequestPayload,
        ComponentMessageType.UI_RENDER_RESPONSE: UIRenderResponsePayload,
        ComponentMessageType.UI_UPDATE_REQUEST: UIUpdateRequestPayload,
        ComponentMessageType.UI_UPDATE_RESPONSE: UIUpdateResponsePayload,
        ComponentMessageType.UI_COMPONENT_EVENT: UIComponentEventPayload,
        ComponentMessageType.USER_INTERACTION_DATA: UserInteractionDataPayload,
        ComponentMessageType.USER_BEHAVIOR_ANALYSIS: UserBehaviorAnalysisPayload,
        ComponentMessageType.DECISION_REQUEST: DecisionRequestPayload,
        ComponentMessageType.DECISION_RESPONSE: DecisionResponsePayload,
        ComponentMessageType.STATE_GET_REQUEST: StateRequestPayload,
        ComponentMessageType.STATE_SET_REQUEST: StateRequestPayload,
        ComponentMessageType.STATE_UPDATE_REQUEST: StateRequestPayload,
        ComponentMessageType.STATE_CHANGE_NOTIFICATION: StateChangeNotificationPayload,
        ComponentMessageType.MCP_MESSAGE_FORWARD: MCPMessageForwardPayload,
        ComponentMessageType.PERFORMANCE_METRIC: PerformanceMetricPayload,
    }
    
    return payload_mapping.get(message_type, MessagePayload)


# 装饰器

def message_handler(message_type: ComponentMessageType):
    """消息处理器装饰器"""
    def decorator(func):
        func._message_type = message_type
        return func
    return decorator


class MessageHandlerRegistry:
    """消息处理器注册表"""
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
    
    def register_component_handlers(self, component_name: str, handler_object: Any) -> None:
        """注册组件的所有消息处理器"""
        for attr_name in dir(handler_object):
            attr = getattr(handler_object, attr_name)
            
            if hasattr(attr, '_message_type'):
                self.message_bus.register_handler(
                    component_name=component_name,
                    message_type=attr._message_type,
                    handler=attr
                )


# 中间件

class LoggingMiddleware:
    """日志中间件"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def __call__(self, message: ComponentMessage) -> ComponentMessage:
        self.logger.debug(
            f"Message: {message.header.component_message_type} "
            f"from {message.header.source_component} "
            f"to {message.header.target_component}"
        )
        return message


class MetricsMiddleware:
    """性能指标中间件"""
    
    def __init__(self, metrics_collector):
        self.metrics_collector = metrics_collector
    
    def __call__(self, message: ComponentMessage) -> ComponentMessage:
        self.metrics_collector.increment_counter(
            "messages_processed",
            tags={
                "message_type": message.header.component_message_type.value,
                "source": message.header.source_component
            }
        )
        return message


class ValidationMiddleware:
    """验证中间件"""
    
    def __call__(self, message: ComponentMessage) -> ComponentMessage:
        # 验证消息格式
        if not message.header.source_component:
            raise ValueError("Source component is required")
        
        if message.header.message_type == MessageType.REQUEST and not message.header.target_component:
            raise ValueError("Target component is required for request messages")
        
        return message

