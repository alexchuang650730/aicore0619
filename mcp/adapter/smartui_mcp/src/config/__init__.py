"""
SmartUI MCP 配置模块初始化文件

导出所有配置相关组件，提供统一的配置管理接口。
"""

from .config_manager import (
    SmartUIConfig,
    ServerConfig,
    DatabaseConfig,
    RedisConfig,
    LoggingConfig,
    CoordinatorConfig,
    IntelligenceConfig,
    UIConfig,
    EventConfig,
    SecurityConfig,
    ConfigManager,
    ConfigValidator,
    ConfigFormat,
    ConfigSource
)

__all__ = [
    # 配置数据类
    "SmartUIConfig",
    "ServerConfig",
    "DatabaseConfig", 
    "RedisConfig",
    "LoggingConfig",
    "CoordinatorConfig",
    "IntelligenceConfig",
    "UIConfig",
    "EventConfig",
    "SecurityConfig",
    
    # 配置管理
    "ConfigManager",
    "ConfigValidator",
    
    # 枚举类型
    "ConfigFormat",
    "ConfigSource"
]

# 版本信息
__version__ = "1.0.0"
__author__ = "SmartUI MCP Team"
__description__ = "SmartUI MCP配置管理模块"

