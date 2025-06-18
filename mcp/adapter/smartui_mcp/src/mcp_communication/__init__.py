"""
SmartUI MCP 通信模块初始化文件

导出所有MCP通信相关组件，提供统一的导入接口。
"""

from .mcp_protocol import (
    MCPServiceInfo,
    MCPRequest,
    MCPResponse,
    MCPClient,
    HTTPMCPClient,
    WebSocketMCPClient,
    MCPServiceRegistry,
    MCPServiceStatus,
    MCPConnectionType
)

from .event_listener import (
    EventProcessor,
    EventSubscription,
    EventFilter,
    EventPriority,
    EventFilterType,
    SmartUIEventListener,
    EventListenerSystem
)

from .coordinator_integration import (
    MCPCoordinatorClient,
    CoordinatorIntegration
)

from .release_management_integration import (
    ReleaseManagementIntegration,
    ReleaseManagementAPI
)

__all__ = [
    # MCP协议通信
    "MCPServiceInfo",
    "MCPRequest", 
    "MCPResponse",
    "MCPClient",
    "HTTPMCPClient",
    "WebSocketMCPClient",
    "MCPServiceRegistry",
    "MCPServiceStatus",
    "MCPConnectionType",
    
    # 事件监听系统
    "EventProcessor",
    "EventSubscription",
    "EventFilter", 
    "EventPriority",
    "EventFilterType",
    "SmartUIEventListener",
    "EventListenerSystem",
    
    # 协调器集成
    "MCPCoordinatorClient",
    "CoordinatorIntegration",
    
    # 发布管理集成
    "ReleaseManagementIntegration",
    "ReleaseManagementAPI"
]

# 版本信息
__version__ = "1.0.0"
__author__ = "SmartUI MCP Team"
__description__ = "SmartUI MCP通信模块"

