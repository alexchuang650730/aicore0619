"""
SmartUI MCP 通用模块初始化文件

导出通用模块中的核心类和函数，提供统一的导入接口。
"""

# 数据模型
from .ui_models import (
    # 枚举类型
    ComponentType, LayoutType, ThemeType, ComponentVariant,
    ResponsiveBreakpoint, EventType, AccessibilityFeature,
    
    # 数据模型
    UIConfiguration, UIComponent, ComponentProps, ComponentStyle,
    ComponentEvent, ComponentValidation, LayoutConfig, ThemeConfig,
    APIStateBinding, InteractionRule, AdaptationRule,
    UIModificationRequest, UIModificationResponse,
    
    # 工厂函数
    create_button_component, create_input_component, create_card_component,
    create_default_theme, create_default_layout, create_basic_ui_configuration
)

# 接口定义
from .interfaces import (
    # 事件总线
    IEventBus, EventBusEvent, EventBusEventType,
    
    # 核心组件接口
    IUserAnalyzer, IDecisionEngine, IApiStateManager,
    IUIGenerator, IUIRenderer, IMCPIntegration,
    IConfigurationManager, IPerformanceMonitor, ISmartUICore,
    
    # 工厂接口
    IComponentFactory, IThemeFactory, ILayoutFactory,
    
    # 插件接口
    ISmartUIPlugin, IPluginManager,
    
    # 类型定义
    EventHandler, StateChangeHandler, ConfigChangeHandler, MCPEventHandler,
    
    # 常量
    SmartUIConstants
)

# 事件总线
from .event_bus import (
    SmartUIEventBus, EventSubscription, EventBusMetrics,
    EventBusFactory, publish_event, subscribe_to_event,
    event_handler, EventHandlerRegistry
)

# 通信协议
from .communication import (
    # 消息类型
    MessageType, MessagePriority, ComponentMessageType,
    
    # 消息结构
    MessageHeader, MessagePayload, ComponentMessage,
    
    # 载荷类型
    UIRenderRequestPayload, UIRenderResponsePayload,
    UIUpdateRequestPayload, UIUpdateResponsePayload,
    UIComponentEventPayload, UserInteractionDataPayload,
    UserBehaviorAnalysisPayload, DecisionRequestPayload,
    DecisionResponsePayload, StateRequestPayload, StateResponsePayload,
    StateChangeNotificationPayload, MCPMessageForwardPayload,
    PerformanceMetricPayload,
    
    # 消息总线和工厂
    MessageBus, MessageFactory, MessageHandlerRegistry,
    
    # 中间件
    LoggingMiddleware, MetricsMiddleware, ValidationMiddleware,
    
    # 装饰器
    message_handler
)

# 工具函数
from .utils import (
    # 缓存和性能
    AsyncCache, Timer, RateLimiter, CircuitBreaker, RetryPolicy,
    PerformanceProfiler,
    
    # 配置和数据
    ConfigLoader, DataValidator, WeakRefDict,
    
    # 事件和锁
    EventEmitter, AsyncLock,
    
    # 装饰器
    async_timeout, log_execution_time, memoize,
    
    # 工具函数
    generate_id, deep_merge, flatten_dict, unflatten_dict,
    safe_execute, format_bytes, format_duration,
    
    # 元类
    SingletonMeta
)

__all__ = [
    # 数据模型
    "ComponentType", "LayoutType", "ThemeType", "ComponentVariant",
    "ResponsiveBreakpoint", "EventType", "AccessibilityFeature",
    "UIConfiguration", "UIComponent", "ComponentProps", "ComponentStyle",
    "ComponentEvent", "ComponentValidation", "LayoutConfig", "ThemeConfig",
    "APIStateBinding", "InteractionRule", "AdaptationRule",
    "UIModificationRequest", "UIModificationResponse",
    "create_button_component", "create_input_component", "create_card_component",
    "create_default_theme", "create_default_layout", "create_basic_ui_configuration",
    
    # 接口定义
    "IEventBus", "EventBusEvent", "EventBusEventType",
    "IUserAnalyzer", "IDecisionEngine", "IApiStateManager",
    "IUIGenerator", "IUIRenderer", "IMCPIntegration",
    "IConfigurationManager", "IPerformanceMonitor", "ISmartUICore",
    "IComponentFactory", "IThemeFactory", "ILayoutFactory",
    "ISmartUIPlugin", "IPluginManager",
    "EventHandler", "StateChangeHandler", "ConfigChangeHandler", "MCPEventHandler",
    "SmartUIConstants",
    
    # 事件总线
    "SmartUIEventBus", "EventSubscription", "EventBusMetrics",
    "EventBusFactory", "publish_event", "subscribe_to_event",
    "event_handler", "EventHandlerRegistry",
    
    # 通信协议
    "MessageType", "MessagePriority", "ComponentMessageType",
    "MessageHeader", "MessagePayload", "ComponentMessage",
    "UIRenderRequestPayload", "UIRenderResponsePayload",
    "UIUpdateRequestPayload", "UIUpdateResponsePayload",
    "UIComponentEventPayload", "UserInteractionDataPayload",
    "UserBehaviorAnalysisPayload", "DecisionRequestPayload",
    "DecisionResponsePayload", "StateRequestPayload", "StateResponsePayload",
    "StateChangeNotificationPayload", "MCPMessageForwardPayload",
    "PerformanceMetricPayload",
    "MessageBus", "MessageFactory", "MessageHandlerRegistry",
    "LoggingMiddleware", "MetricsMiddleware", "ValidationMiddleware",
    "message_handler",
    
    # 工具函数
    "AsyncCache", "Timer", "RateLimiter", "CircuitBreaker", "RetryPolicy",
    "PerformanceProfiler", "ConfigLoader", "DataValidator", "WeakRefDict",
    "EventEmitter", "AsyncLock",
    "async_timeout", "log_execution_time", "memoize",
    "generate_id", "deep_merge", "flatten_dict", "unflatten_dict",
    "safe_execute", "format_bytes", "format_duration",
    "SingletonMeta"
]

