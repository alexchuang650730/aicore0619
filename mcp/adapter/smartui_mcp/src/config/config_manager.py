"""
SmartUI MCP - 配置管理系统

实现完整的配置管理，支持YAML/JSON配置文件、环境变量、
动态配置更新和配置验证等功能。
"""

import os
import yaml
import json
import logging
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ..common import (
    EventBusEvent, EventBusEventType,
    publish_event, AsyncCache, generate_id
)


class ConfigFormat(str, Enum):
    """配置文件格式枚举"""
    YAML = "yaml"
    JSON = "json"
    ENV = "env"


class ConfigSource(str, Enum):
    """配置源枚举"""
    FILE = "file"
    ENVIRONMENT = "environment"
    RUNTIME = "runtime"
    DEFAULT = "default"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "smartui_mcp.db"
    username: str = ""
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: str = ""
    max_connections: int = 10
    decode_responses: bool = True


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/smartui_mcp.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 4
    max_request_size: int = 16777216  # 16MB
    request_timeout: int = 30
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class CoordinatorConfig:
    """MCP Coordinator配置"""
    endpoint: str = "http://localhost:8080"
    service_id: str = "smartui_mcp"
    service_name: str = "SmartUI MCP"
    service_type: str = "ui_service"
    version: str = "1.0.0"
    description: str = "智慧感知UI服务"
    capabilities: List[str] = field(default_factory=lambda: [
        "ui_generation", "user_behavior_analysis", "intelligent_adaptation",
        "theme_management", "layout_optimization", "component_rendering",
        "event_handling", "state_management"
    ])
    heartbeat_interval: int = 30
    reconnect_interval: int = 10
    max_reconnect_attempts: int = 5


@dataclass
class IntelligenceConfig:
    """智能组件配置"""
    user_analyzer_enabled: bool = True
    decision_engine_enabled: bool = True
    ui_generator_enabled: bool = True
    mcp_integration_enabled: bool = True
    
    # 用户分析器配置
    behavior_cache_ttl: int = 3600
    session_timeout: int = 1800
    max_behavior_history: int = 1000
    
    # 决策引擎配置
    default_strategy: str = "hybrid"
    confidence_threshold: float = 0.7
    max_decision_time: float = 5.0
    
    # UI生成器配置
    template_cache_size: int = 100
    component_cache_ttl: int = 1800
    max_generation_time: float = 10.0


@dataclass
class UIConfig:
    """UI配置"""
    default_theme: str = "dark"
    default_layout: str = "vscode"
    responsive_enabled: bool = True
    accessibility_enabled: bool = True
    
    # 主题配置
    available_themes: List[str] = field(default_factory=lambda: [
        "light", "dark", "high_contrast"
    ])
    
    # 布局配置
    sidebar_width: int = 300
    panel_height: int = 200
    header_height: int = 35
    status_bar_height: int = 22
    
    # 组件配置
    animation_enabled: bool = True
    animation_duration: int = 200
    lazy_loading_enabled: bool = True


@dataclass
class EventConfig:
    """事件系统配置"""
    max_workers: int = 10
    queue_size: int = 1000
    batch_size: int = 50
    batch_timeout: float = 1.0
    
    # 事件过滤配置
    enable_filtering: bool = True
    max_filters_per_subscription: int = 10
    
    # 性能配置
    enable_metrics: bool = True
    metrics_retention_days: int = 7
    max_event_history: int = 10000


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str = ""
    jwt_secret: str = ""
    jwt_expiration: int = 3600
    
    # API安全
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # CORS配置
    cors_max_age: int = 86400
    cors_allow_credentials: bool = False


@dataclass
class SmartUIConfig:
    """SmartUI MCP完整配置"""
    # 基础配置
    environment: str = "development"
    debug: bool = False
    config_version: str = "1.0.0"
    
    # 各模块配置
    server: ServerConfig = field(default_factory=ServerConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    coordinator: CoordinatorConfig = field(default_factory=CoordinatorConfig)
    intelligence: IntelligenceConfig = field(default_factory=IntelligenceConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    events: EventConfig = field(default_factory=EventConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # 自定义配置
    custom: Dict[str, Any] = field(default_factory=dict)


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ConfigValidator")
    
    def validate_config(self, config: SmartUIConfig) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证服务器配置
        errors.extend(self._validate_server_config(config.server))
        
        # 验证数据库配置
        errors.extend(self._validate_database_config(config.database))
        
        # 验证Coordinator配置
        errors.extend(self._validate_coordinator_config(config.coordinator))
        
        # 验证智能组件配置
        errors.extend(self._validate_intelligence_config(config.intelligence))
        
        # 验证UI配置
        errors.extend(self._validate_ui_config(config.ui))
        
        # 验证事件配置
        errors.extend(self._validate_event_config(config.events))
        
        # 验证安全配置
        errors.extend(self._validate_security_config(config.security))
        
        return errors
    
    def _validate_server_config(self, config: ServerConfig) -> List[str]:
        """验证服务器配置"""
        errors = []
        
        if not (1 <= config.port <= 65535):
            errors.append(f"Invalid server port: {config.port}")
        
        if config.workers < 1:
            errors.append(f"Invalid worker count: {config.workers}")
        
        if config.request_timeout < 1:
            errors.append(f"Invalid request timeout: {config.request_timeout}")
        
        return errors
    
    def _validate_database_config(self, config: DatabaseConfig) -> List[str]:
        """验证数据库配置"""
        errors = []
        
        if config.type not in ["sqlite", "postgresql", "mysql"]:
            errors.append(f"Unsupported database type: {config.type}")
        
        if not (1 <= config.port <= 65535):
            errors.append(f"Invalid database port: {config.port}")
        
        if config.pool_size < 1:
            errors.append(f"Invalid pool size: {config.pool_size}")
        
        return errors
    
    def _validate_coordinator_config(self, config: CoordinatorConfig) -> List[str]:
        """验证Coordinator配置"""
        errors = []
        
        if not config.endpoint.startswith(("http://", "https://")):
            errors.append(f"Invalid coordinator endpoint: {config.endpoint}")
        
        if not config.service_id:
            errors.append("Service ID cannot be empty")
        
        if config.heartbeat_interval < 5:
            errors.append(f"Heartbeat interval too short: {config.heartbeat_interval}")
        
        return errors
    
    def _validate_intelligence_config(self, config: IntelligenceConfig) -> List[str]:
        """验证智能组件配置"""
        errors = []
        
        if config.confidence_threshold < 0 or config.confidence_threshold > 1:
            errors.append(f"Invalid confidence threshold: {config.confidence_threshold}")
        
        if config.max_decision_time < 0.1:
            errors.append(f"Decision time too short: {config.max_decision_time}")
        
        if config.session_timeout < 60:
            errors.append(f"Session timeout too short: {config.session_timeout}")
        
        return errors
    
    def _validate_ui_config(self, config: UIConfig) -> List[str]:
        """验证UI配置"""
        errors = []
        
        if config.default_theme not in config.available_themes:
            errors.append(f"Default theme not in available themes: {config.default_theme}")
        
        if config.sidebar_width < 100:
            errors.append(f"Sidebar width too small: {config.sidebar_width}")
        
        if config.animation_duration < 50:
            errors.append(f"Animation duration too short: {config.animation_duration}")
        
        return errors
    
    def _validate_event_config(self, config: EventConfig) -> List[str]:
        """验证事件配置"""
        errors = []
        
        if config.max_workers < 1:
            errors.append(f"Invalid worker count: {config.max_workers}")
        
        if config.queue_size < 10:
            errors.append(f"Queue size too small: {config.queue_size}")
        
        if config.batch_timeout < 0.1:
            errors.append(f"Batch timeout too short: {config.batch_timeout}")
        
        return errors
    
    def _validate_security_config(self, config: SecurityConfig) -> List[str]:
        """验证安全配置"""
        errors = []
        
        if not config.secret_key:
            errors.append("Secret key cannot be empty")
        
        if len(config.secret_key) < 32:
            errors.append("Secret key too short (minimum 32 characters)")
        
        if config.jwt_expiration < 300:
            errors.append(f"JWT expiration too short: {config.jwt_expiration}")
        
        return errors


class ConfigFileWatcher(FileSystemEventHandler):
    """配置文件监控器"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        self.logger = logging.getLogger(f"{__name__}.ConfigFileWatcher")
    
    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory and event.src_path == str(self.config_manager.config_file):
            self.logger.info(f"Config file modified: {event.src_path}")
            asyncio.create_task(self.config_manager.reload_config())


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(f"{__name__}.ConfigManager")
        
        # 配置文件路径
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = Path("config/smartui_config.yaml")
        
        # 配置对象
        self.config: Optional[SmartUIConfig] = None
        self.config_cache = AsyncCache(default_ttl=300)
        
        # 配置验证器
        self.validator = ConfigValidator()
        
        # 文件监控
        self.observer: Optional[Observer] = None
        self.file_watcher: Optional[ConfigFileWatcher] = None
        
        # 配置更新回调
        self.update_callbacks: List[Callable[[SmartUIConfig], None]] = []
        
        self.logger.info(f"Config Manager initialized with file: {self.config_file}")
    
    async def load_config(self) -> SmartUIConfig:
        """加载配置"""
        try:
            # 检查缓存
            cached_config = await self.config_cache.get("main_config")
            if cached_config:
                self.config = cached_config
                return self.config
            
            # 创建默认配置
            config = SmartUIConfig()
            
            # 从文件加载配置
            if self.config_file.exists():
                file_config = await self._load_from_file()
                if file_config:
                    config = self._merge_configs(config, file_config)
            else:
                self.logger.warning(f"Config file not found: {self.config_file}")
                # 创建默认配置文件
                await self._save_default_config()
            
            # 从环境变量加载配置
            env_config = self._load_from_environment()
            if env_config:
                config = self._merge_configs(config, env_config)
            
            # 验证配置
            validation_errors = self.validator.validate_config(config)
            if validation_errors:
                self.logger.error(f"Config validation errors: {validation_errors}")
                raise ValueError(f"Configuration validation failed: {validation_errors}")
            
            # 缓存配置
            await self.config_cache.set("main_config", config)
            self.config = config
            
            self.logger.info("Configuration loaded successfully")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            # 返回默认配置
            self.config = SmartUIConfig()
            return self.config
    
    async def reload_config(self) -> SmartUIConfig:
        """重新加载配置"""
        self.logger.info("Reloading configuration...")
        
        # 清除缓存
        await self.config_cache.clear()
        
        # 重新加载
        old_config = self.config
        new_config = await self.load_config()
        
        # 检查配置是否有变化
        if old_config and asdict(old_config) != asdict(new_config):
            self.logger.info("Configuration changed, notifying callbacks")
            
            # 发布配置更新事件
            await publish_event(
                event_type=EventBusEventType.CONFIG_UPDATED,
                data={
                    "old_config": asdict(old_config) if old_config else None,
                    "new_config": asdict(new_config),
                    "timestamp": datetime.now().isoformat()
                },
                source="config_manager"
            )
            
            # 调用更新回调
            for callback in self.update_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(new_config)
                    else:
                        callback(new_config)
                except Exception as e:
                    self.logger.error(f"Error in config update callback: {e}")
        
        return new_config
    
    async def save_config(self, config: Optional[SmartUIConfig] = None) -> bool:
        """保存配置"""
        try:
            if config is None:
                config = self.config
            
            if config is None:
                raise ValueError("No configuration to save")
            
            # 验证配置
            validation_errors = self.validator.validate_config(config)
            if validation_errors:
                raise ValueError(f"Configuration validation failed: {validation_errors}")
            
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到文件
            config_dict = asdict(config)
            
            if self.config_file.suffix.lower() in ['.yaml', '.yml']:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            elif self.config_file.suffix.lower() == '.json':
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported config file format: {self.config_file.suffix}")
            
            # 更新缓存
            await self.config_cache.set("main_config", config)
            self.config = config
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    async def _load_from_file(self) -> Optional[Dict[str, Any]]:
        """从文件加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                if self.config_file.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif self.config_file.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    self.logger.error(f"Unsupported config file format: {self.config_file.suffix}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error loading config from file: {e}")
            return None
    
    def _load_from_environment(self) -> Optional[Dict[str, Any]]:
        """从环境变量加载配置"""
        try:
            env_config = {}
            
            # 服务器配置
            if os.getenv("SMARTUI_HOST"):
                env_config.setdefault("server", {})["host"] = os.getenv("SMARTUI_HOST")
            if os.getenv("SMARTUI_PORT"):
                env_config.setdefault("server", {})["port"] = int(os.getenv("SMARTUI_PORT"))
            if os.getenv("SMARTUI_DEBUG"):
                env_config.setdefault("server", {})["debug"] = os.getenv("SMARTUI_DEBUG").lower() == "true"
            
            # 数据库配置
            if os.getenv("DATABASE_URL"):
                env_config.setdefault("database", {})["url"] = os.getenv("DATABASE_URL")
            if os.getenv("DATABASE_TYPE"):
                env_config.setdefault("database", {})["type"] = os.getenv("DATABASE_TYPE")
            
            # Coordinator配置
            if os.getenv("COORDINATOR_ENDPOINT"):
                env_config.setdefault("coordinator", {})["endpoint"] = os.getenv("COORDINATOR_ENDPOINT")
            if os.getenv("SERVICE_ID"):
                env_config.setdefault("coordinator", {})["service_id"] = os.getenv("SERVICE_ID")
            
            # 安全配置
            if os.getenv("SECRET_KEY"):
                env_config.setdefault("security", {})["secret_key"] = os.getenv("SECRET_KEY")
            if os.getenv("JWT_SECRET"):
                env_config.setdefault("security", {})["jwt_secret"] = os.getenv("JWT_SECRET")
            
            return env_config if env_config else None
            
        except Exception as e:
            self.logger.error(f"Error loading config from environment: {e}")
            return None
    
    def _merge_configs(self, base_config: SmartUIConfig, override_config: Dict[str, Any]) -> SmartUIConfig:
        """合并配置"""
        try:
            # 将基础配置转换为字典
            base_dict = asdict(base_config)
            
            # 深度合并配置
            merged_dict = self._deep_merge(base_dict, override_config)
            
            # 转换回配置对象
            return self._dict_to_config(merged_dict)
            
        except Exception as e:
            self.logger.error(f"Error merging configs: {e}")
            return base_config
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> SmartUIConfig:
        """将字典转换为配置对象"""
        # 这里简化处理，实际应该递归转换所有嵌套对象
        return SmartUIConfig(
            environment=config_dict.get("environment", "development"),
            debug=config_dict.get("debug", False),
            config_version=config_dict.get("config_version", "1.0.0"),
            server=ServerConfig(**config_dict.get("server", {})),
            database=DatabaseConfig(**config_dict.get("database", {})),
            redis=RedisConfig(**config_dict.get("redis", {})),
            logging=LoggingConfig(**config_dict.get("logging", {})),
            coordinator=CoordinatorConfig(**config_dict.get("coordinator", {})),
            intelligence=IntelligenceConfig(**config_dict.get("intelligence", {})),
            ui=UIConfig(**config_dict.get("ui", {})),
            events=EventConfig(**config_dict.get("events", {})),
            security=SecurityConfig(**config_dict.get("security", {})),
            custom=config_dict.get("custom", {})
        )
    
    async def _save_default_config(self) -> None:
        """保存默认配置"""
        default_config = SmartUIConfig()
        await self.save_config(default_config)
    
    def start_file_watching(self) -> None:
        """启动文件监控"""
        try:
            if self.observer is not None:
                return
            
            self.file_watcher = ConfigFileWatcher(self)
            self.observer = Observer()
            self.observer.schedule(
                self.file_watcher,
                str(self.config_file.parent),
                recursive=False
            )
            self.observer.start()
            
            self.logger.info("Config file watching started")
            
        except Exception as e:
            self.logger.error(f"Error starting file watching: {e}")
    
    def stop_file_watching(self) -> None:
        """停止文件监控"""
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
                self.file_watcher = None
            
            self.logger.info("Config file watching stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping file watching: {e}")
    
    def add_update_callback(self, callback: Callable[[SmartUIConfig], None]) -> None:
        """添加配置更新回调"""
        self.update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable[[SmartUIConfig], None]) -> None:
        """移除配置更新回调"""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
    
    async def get_config_section(self, section: str) -> Optional[Any]:
        """获取配置节"""
        if self.config is None:
            await self.load_config()
        
        return getattr(self.config, section, None)
    
    async def update_config_section(self, section: str, data: Dict[str, Any]) -> bool:
        """更新配置节"""
        try:
            if self.config is None:
                await self.load_config()
            
            # 获取当前节配置
            current_section = getattr(self.config, section, None)
            if current_section is None:
                return False
            
            # 更新配置
            section_dict = asdict(current_section)
            section_dict.update(data)
            
            # 重新创建配置对象
            section_class = type(current_section)
            new_section = section_class(**section_dict)
            
            # 更新主配置
            setattr(self.config, section, new_section)
            
            # 保存配置
            return await self.save_config()
            
        except Exception as e:
            self.logger.error(f"Error updating config section {section}: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """获取配置管理器状态"""
        return {
            "config_file": str(self.config_file),
            "config_loaded": self.config is not None,
            "file_watching": self.observer is not None and self.observer.is_alive(),
            "update_callbacks": len(self.update_callbacks),
            "cache_size": await self.config_cache.size(),
            "last_modified": self.config_file.stat().st_mtime if self.config_file.exists() else None
        }

