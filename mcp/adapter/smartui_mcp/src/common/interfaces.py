"""
SmartUI MCP 核心架构接口

定义了SmartUI MCP系统中各个组件之间的接口规范，
确保组件间的松耦合和高内聚。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
import asyncio
from enum import Enum

from .ui_models import (
    UIConfiguration, UIComponent, UIModificationRequest, UIModificationResponse,
    ComponentEvent, ThemeConfig, LayoutConfig
)


class EventBusEventType(str, Enum):
    """事件总线事件类型"""
    # 用户交互事件
    USER_INTERACTION = "user_interaction"
    USER_BEHAVIOR_CHANGE = "user_behavior_change"
    USER_PREFERENCE_UPDATE = "user_preference_update"
    
    # UI相关事件
    UI_COMPONENT_MOUNTED = "ui_component_mounted"
    UI_COMPONENT_UNMOUNTED = "ui_component_unmounted"
    UI_COMPONENT_UPDATED = "ui_component_updated"
    UI_CONFIGURATION_CHANGED = "ui_configuration_changed"
    UI_RENDER_COMPLETE = "ui_render_complete"
    UI_RENDER_ERROR = "ui_render_error"
    
    # API状态事件
    API_STATE_CHANGED = "api_state_changed"
    API_REQUEST_START = "api_request_start"
    API_REQUEST_COMPLETE = "api_request_complete"
    API_REQUEST_ERROR = "api_request_error"
    
    # MCP通信事件
    MCP_MESSAGE_RECEIVED = "mcp_message_received"
    MCP_MESSAGE_SENT = "mcp_message_sent"
    MCP_CONNECTION_ESTABLISHED = "mcp_connection_established"
    MCP_CONNECTION_LOST = "mcp_connection_lost"
    
    # 决策引擎事件
    DECISION_MADE = "decision_made"
    RULE_TRIGGERED = "rule_triggered"
    ADAPTATION_APPLIED = "adaptation_applied"
    
    # 系统事件
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    SYSTEM_INFO = "system_info"
    PERFORMANCE_METRIC = "performance_metric"


class EventBusEvent(object):
    """事件总线事件对象"""
    
    def __init__(
        self,
        event_type: EventBusEventType,
        data: Dict[str, Any],
        source: str,
        timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = timestamp or datetime.now()
        self.event_id = event_id or f"{source}_{event_type}_{int(self.timestamp.timestamp())}"


class IEventBus(ABC):
    """事件总线接口"""
    
    @abstractmethod
    async def publish(self, event: EventBusEvent) -> None:
        """发布事件"""
        pass
    
    @abstractmethod
    async def subscribe(
        self,
        event_type: EventBusEventType,
        handler: Callable[[EventBusEvent], None],
        filter_func: Optional[Callable[[EventBusEvent], bool]] = None
    ) -> str:
        """订阅事件，返回订阅ID"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        pass
    
    @abstractmethod
    async def get_event_history(
        self,
        event_type: Optional[EventBusEventType] = None,
        source: Optional[str] = None,
        limit: int = 100
    ) -> List[EventBusEvent]:
        """获取事件历史"""
        pass


class IUserAnalyzer(ABC):
    """用户分析器接口"""
    
    @abstractmethod
    async def analyze_user_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户交互数据"""
        pass
    
    @abstractmethod
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        pass
    
    @abstractmethod
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """更新用户画像"""
        pass
    
    @abstractmethod
    async def detect_behavior_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """检测用户行为模式"""
        pass
    
    @abstractmethod
    async def predict_user_intent(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """预测用户意图"""
        pass


class IDecisionEngine(ABC):
    """智能决策引擎接口"""
    
    @abstractmethod
    async def make_decision(
        self,
        context: Dict[str, Any],
        available_actions: List[str]
    ) -> Dict[str, Any]:
        """做出决策"""
        pass
    
    @abstractmethod
    async def evaluate_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """评估规则"""
        pass
    
    @abstractmethod
    async def add_rule(self, rule: Dict[str, Any]) -> str:
        """添加规则，返回规则ID"""
        pass
    
    @abstractmethod
    async def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        pass
    
    @abstractmethod
    async def update_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> bool:
        """更新规则"""
        pass
    
    @abstractmethod
    async def get_decision_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取决策历史"""
        pass


class IApiStateManager(ABC):
    """API状态管理器接口"""
    
    @abstractmethod
    async def get_state(self, path: str) -> Any:
        """获取状态值"""
        pass
    
    @abstractmethod
    async def set_state(self, path: str, value: Any) -> None:
        """设置状态值"""
        pass
    
    @abstractmethod
    async def update_state(self, path: str, updates: Dict[str, Any]) -> None:
        """更新状态"""
        pass
    
    @abstractmethod
    async def delete_state(self, path: str) -> bool:
        """删除状态"""
        pass
    
    @abstractmethod
    async def watch_state(
        self,
        path: str,
        callback: Callable[[str, Any, Any], None]
    ) -> str:
        """监听状态变化，返回监听器ID"""
        pass
    
    @abstractmethod
    async def unwatch_state(self, watcher_id: str) -> bool:
        """取消状态监听"""
        pass
    
    @abstractmethod
    async def get_state_snapshot(self) -> Dict[str, Any]:
        """获取状态快照"""
        pass
    
    @abstractmethod
    async def restore_state_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """恢复状态快照"""
        pass


class IUIGenerator(ABC):
    """UI生成器接口"""
    
    @abstractmethod
    async def generate_ui(self, requirements: Dict[str, Any]) -> UIConfiguration:
        """生成UI配置"""
        pass
    
    @abstractmethod
    async def update_ui(
        self,
        current_config: UIConfiguration,
        updates: Dict[str, Any]
    ) -> UIConfiguration:
        """更新UI配置"""
        pass
    
    @abstractmethod
    async def validate_ui_config(self, config: UIConfiguration) -> Dict[str, Any]:
        """验证UI配置"""
        pass
    
    @abstractmethod
    async def optimize_ui_config(self, config: UIConfiguration) -> UIConfiguration:
        """优化UI配置"""
        pass
    
    @abstractmethod
    async def generate_component(
        self,
        component_type: str,
        props: Dict[str, Any]
    ) -> UIComponent:
        """生成单个组件"""
        pass


class IUIRenderer(ABC):
    """UI渲染器接口"""
    
    @abstractmethod
    async def render_ui(self, config: UIConfiguration) -> str:
        """渲染UI，返回HTML字符串"""
        pass
    
    @abstractmethod
    async def render_component(self, component: UIComponent) -> str:
        """渲染单个组件"""
        pass
    
    @abstractmethod
    async def update_component(
        self,
        component_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """更新组件"""
        pass
    
    @abstractmethod
    async def remove_component(self, component_id: str) -> bool:
        """移除组件"""
        pass
    
    @abstractmethod
    async def add_component(
        self,
        parent_id: str,
        component: UIComponent,
        position: Optional[int] = None
    ) -> bool:
        """添加组件"""
        pass
    
    @abstractmethod
    async def get_rendered_html(self) -> str:
        """获取当前渲染的HTML"""
        pass
    
    @abstractmethod
    async def get_component_events(self) -> List[ComponentEvent]:
        """获取组件事件列表"""
        pass


class IMCPIntegration(ABC):
    """MCP集成接口"""
    
    @abstractmethod
    async def register_mcp(self, mcp_config: Dict[str, Any]) -> bool:
        """注册MCP"""
        pass
    
    @abstractmethod
    async def send_message(
        self,
        target_mcp_id: str,
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """发送消息到其他MCP"""
        pass
    
    @abstractmethod
    async def handle_incoming_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理接收到的消息"""
        pass
    
    @abstractmethod
    async def get_registered_mcps(self) -> List[Dict[str, Any]]:
        """获取已注册的MCP列表"""
        pass
    
    @abstractmethod
    async def check_mcp_health(self, mcp_id: str) -> Dict[str, Any]:
        """检查MCP健康状态"""
        pass
    
    @abstractmethod
    async def subscribe_to_mcp_events(
        self,
        mcp_id: str,
        event_types: List[str],
        callback: Callable[[Dict[str, Any]], None]
    ) -> str:
        """订阅MCP事件"""
        pass


class IConfigurationManager(ABC):
    """配置管理器接口"""
    
    @abstractmethod
    async def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置"""
        pass
    
    @abstractmethod
    async def save_config(self, config_path: str, config: Dict[str, Any]) -> None:
        """保存配置"""
        pass
    
    @abstractmethod
    async def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    @abstractmethod
    async def set_config_value(self, key: str, value: Any) -> None:
        """设置配置值"""
        pass
    
    @abstractmethod
    async def watch_config_changes(
        self,
        key: str,
        callback: Callable[[str, Any, Any], None]
    ) -> str:
        """监听配置变化"""
        pass
    
    @abstractmethod
    async def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证配置"""
        pass


class IPerformanceMonitor(ABC):
    """性能监控器接口"""
    
    @abstractmethod
    async def start_timing(self, operation_name: str) -> str:
        """开始计时，返回计时器ID"""
        pass
    
    @abstractmethod
    async def end_timing(self, timer_id: str) -> float:
        """结束计时，返回耗时（秒）"""
        pass
    
    @abstractmethod
    async def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """记录性能指标"""
        pass
    
    @abstractmethod
    async def get_metrics(
        self,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """获取性能指标"""
        pass
    
    @abstractmethod
    async def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        pass


class ISmartUICore(ABC):
    """SmartUI核心接口"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """初始化系统"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """关闭系统"""
        pass
    
    @abstractmethod
    async def process_ui_modification_request(
        self,
        request: UIModificationRequest
    ) -> UIModificationResponse:
        """处理UI修改请求"""
        pass
    
    @abstractmethod
    async def get_current_ui_config(self) -> Optional[UIConfiguration]:
        """获取当前UI配置"""
        pass
    
    @abstractmethod
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        pass
    
    @abstractmethod
    async def handle_user_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """处理用户交互"""
        pass
    
    @abstractmethod
    async def trigger_adaptation(self, context: Dict[str, Any]) -> None:
        """触发自适应调整"""
        pass


# 工厂接口

class IComponentFactory(ABC):
    """组件工厂接口"""
    
    @abstractmethod
    def create_component(
        self,
        component_type: str,
        props: Dict[str, Any]
    ) -> UIComponent:
        """创建组件"""
        pass
    
    @abstractmethod
    def register_component_type(
        self,
        component_type: str,
        factory_func: Callable[[Dict[str, Any]], UIComponent]
    ) -> None:
        """注册组件类型"""
        pass
    
    @abstractmethod
    def get_available_component_types(self) -> List[str]:
        """获取可用的组件类型"""
        pass


class IThemeFactory(ABC):
    """主题工厂接口"""
    
    @abstractmethod
    def create_theme(self, theme_type: str, customizations: Optional[Dict[str, Any]] = None) -> ThemeConfig:
        """创建主题"""
        pass
    
    @abstractmethod
    def register_theme_type(
        self,
        theme_type: str,
        factory_func: Callable[[Optional[Dict[str, Any]]], ThemeConfig]
    ) -> None:
        """注册主题类型"""
        pass
    
    @abstractmethod
    def get_available_theme_types(self) -> List[str]:
        """获取可用的主题类型"""
        pass


class ILayoutFactory(ABC):
    """布局工厂接口"""
    
    @abstractmethod
    def create_layout(self, layout_type: str, config: Optional[Dict[str, Any]] = None) -> LayoutConfig:
        """创建布局"""
        pass
    
    @abstractmethod
    def register_layout_type(
        self,
        layout_type: str,
        factory_func: Callable[[Optional[Dict[str, Any]]], LayoutConfig]
    ) -> None:
        """注册布局类型"""
        pass
    
    @abstractmethod
    def get_available_layout_types(self) -> List[str]:
        """获取可用的布局类型"""
        pass


# 插件接口

class ISmartUIPlugin(ABC):
    """SmartUI插件接口"""
    
    @abstractmethod
    async def initialize(self, core: ISmartUICore, config: Dict[str, Any]) -> None:
        """初始化插件"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """关闭插件"""
        pass
    
    @abstractmethod
    def get_plugin_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        pass
    
    @abstractmethod
    async def handle_event(self, event: EventBusEvent) -> None:
        """处理事件"""
        pass


class IPluginManager(ABC):
    """插件管理器接口"""
    
    @abstractmethod
    async def load_plugin(self, plugin_path: str, config: Optional[Dict[str, Any]] = None) -> str:
        """加载插件，返回插件ID"""
        pass
    
    @abstractmethod
    async def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        pass
    
    @abstractmethod
    async def get_loaded_plugins(self) -> List[Dict[str, Any]]:
        """获取已加载的插件"""
        pass
    
    @abstractmethod
    async def enable_plugin(self, plugin_id: str) -> bool:
        """启用插件"""
        pass
    
    @abstractmethod
    async def disable_plugin(self, plugin_id: str) -> bool:
        """禁用插件"""
        pass


# 辅助类型定义

EventHandler = Callable[[EventBusEvent], None]
StateChangeHandler = Callable[[str, Any, Any], None]
ConfigChangeHandler = Callable[[str, Any, Any], None]
MCPEventHandler = Callable[[Dict[str, Any]], None]

# 常量定义

class SmartUIConstants:
    """SmartUI常量定义"""
    
    # 默认配置
    DEFAULT_PORT = 5002
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_DEBUG = False
    
    # 事件总线配置
    EVENT_HISTORY_LIMIT = 1000
    EVENT_CLEANUP_INTERVAL = 3600  # 1小时
    
    # 性能监控配置
    PERFORMANCE_METRIC_RETENTION = 86400  # 24小时
    PERFORMANCE_ALERT_THRESHOLD = 5.0  # 5秒
    
    # API状态管理配置
    STATE_SYNC_INTERVAL = 1.0  # 1秒
    STATE_CACHE_SIZE = 1000
    
    # UI生成配置
    UI_GENERATION_TIMEOUT = 30.0  # 30秒
    UI_COMPONENT_CACHE_SIZE = 500
    
    # MCP通信配置
    MCP_REQUEST_TIMEOUT = 10.0  # 10秒
    MCP_RETRY_ATTEMPTS = 3
    MCP_HEARTBEAT_INTERVAL = 30.0  # 30秒
    
    # 用户分析配置
    USER_SESSION_TIMEOUT = 1800  # 30分钟
    BEHAVIOR_PATTERN_WINDOW = 3600  # 1小时
    
    # 决策引擎配置
    DECISION_CACHE_SIZE = 100
    RULE_EVALUATION_TIMEOUT = 5.0  # 5秒

