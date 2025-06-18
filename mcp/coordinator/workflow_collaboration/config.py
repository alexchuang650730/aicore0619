#!/usr/bin/env python3
"""
Product Orchestrator V3 配置文件

定义Product Orchestrator的配置参数和MCP组件映射
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class MCPEndpoint:
    """MCP组件端点配置"""
    name: str
    host: str
    port: int
    protocol: str = "http"
    health_check_path: str = "/health"
    timeout: int = 30
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"

# ============================================================================
# MCP组件端点配置
# ============================================================================

MCP_ENDPOINTS = {
    # Adapter类型MCP组件
    "requirement_analysis_mcp": MCPEndpoint(
        name="requirement_analysis_mcp",
        host="localhost",
        port=8100,
        health_check_path="/api/health"
    ),
    "code_generation_mcp": MCPEndpoint(
        name="code_generation_mcp", 
        host="localhost",
        port=8101,
        health_check_path="/api/health"
    ),
    "test_manage_mcp": MCPEndpoint(
        name="test_manage_mcp",
        host="localhost", 
        port=8102,
        health_check_path="/api/health"
    ),
    "deployment_mcp": MCPEndpoint(
        name="deployment_mcp",
        host="localhost",
        port=8103,
        health_check_path="/api/health"
    ),
    "monitoring_mcp": MCPEndpoint(
        name="monitoring_mcp",
        host="localhost",
        port=8104,
        health_check_path="/api/health"
    ),
    "documentation_mcp": MCPEndpoint(
        name="documentation_mcp",
        host="localhost",
        port=8105,
        health_check_path="/api/health"
    ),
    "enhanced_workflow_mcp": MCPEndpoint(
        name="enhanced_workflow_mcp",
        host="localhost",
        port=8106,
        health_check_path="/api/health"
    ),
    "kilocode_mcp": MCPEndpoint(
        name="kilocode_mcp",
        host="localhost",
        port=8107,
        health_check_path="/api/health"
    ),
    "local_model_mcp": MCPEndpoint(
        name="local_model_mcp",
        host="localhost",
        port=8108,
        health_check_path="/api/health"
    ),
    "github_mcp": MCPEndpoint(
        name="github_mcp",
        host="localhost",
        port=8109,
        health_check_path="/api/health"
    ),
    "smartui_mcp": MCPEndpoint(
        name="smartui_mcp",
        host="localhost",
        port=5001,
        health_check_path="/api/health"
    ),
    "cloud_search_mcp": MCPEndpoint(
        name="cloud_search_mcp",
        host="localhost",
        port=8110,
        health_check_path="/api/health"
    ),
    "directory_structure_mcp": MCPEndpoint(
        name="directory_structure_mcp",
        host="localhost",
        port=8111,
        health_check_path="/api/health"
    ),
    "testing_mcp": MCPEndpoint(
        name="testing_mcp",
        host="localhost",
        port=8112,
        health_check_path="/api/health"
    ),
    
    # 特殊组件
    "unified_smart_tool_engine": MCPEndpoint(
        name="unified_smart_tool_engine",
        host="localhost",
        port=8200,
        health_check_path="/api/health"
    ),
    "mcp_coordinator": MCPEndpoint(
        name="mcp_coordinator",
        host="localhost",
        port=8089,
        health_check_path="/api/health"
    )
}

# ============================================================================
# Product Orchestrator配置
# ============================================================================

PRODUCT_ORCHESTRATOR_CONFIG = {
    # 基本配置
    "name": "ProductOrchestratorV3",
    "version": "3.0.0",
    "description": "Enhanced Product Orchestrator with dynamic workflow generation",
    
    # 执行配置
    "max_parallel_tasks": int(os.getenv("MAX_PARALLEL_TASKS", "4")),
    "default_timeout": int(os.getenv("DEFAULT_TIMEOUT", "300")),
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
    "retry_delay": int(os.getenv("RETRY_DELAY", "5")),
    
    # WebSocket配置
    "smartui_endpoint": os.getenv("SMARTUI_ENDPOINT", "ws://localhost:5001/ws"),
    "status_pusher_port": int(os.getenv("STATUS_PUSHER_PORT", "5002")),
    "websocket_timeout": int(os.getenv("WEBSOCKET_TIMEOUT", "30")),
    
    # 日志配置
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_file": os.getenv("LOG_FILE", "/opt/powerautomation/logs/product_orchestrator.log"),
    "log_max_size": int(os.getenv("LOG_MAX_SIZE", "10485760")),  # 10MB
    "log_backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5")),
    
    # 存储配置
    "workflow_storage_path": os.getenv("WORKFLOW_STORAGE_PATH", "/opt/powerautomation/data/workflows"),
    "interaction_log_path": os.getenv("INTERACTION_LOG_PATH", "/opt/powerautomation/logs/interactions"),
    
    # 性能配置
    "workflow_cache_size": int(os.getenv("WORKFLOW_CACHE_SIZE", "100")),
    "dependency_analysis_timeout": int(os.getenv("DEPENDENCY_ANALYSIS_TIMEOUT", "60")),
    "status_update_interval": int(os.getenv("STATUS_UPDATE_INTERVAL", "5")),
    
    # 安全配置
    "enable_authentication": os.getenv("ENABLE_AUTHENTICATION", "false").lower() == "true",
    "api_key": os.getenv("API_KEY", ""),
    "allowed_origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
    
    # 监控配置
    "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
    "metrics_port": int(os.getenv("METRICS_PORT", "9090")),
    "health_check_interval": int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
}

# ============================================================================
# 工作流模板配置
# ============================================================================

WORKFLOW_TEMPLATES = {
    "software_development": {
        "name": "完整软件开发流程",
        "description": "包含需求分析到监控运维的完整开发流程",
        "estimated_duration": 7200,  # 2小时
        "complexity": "high",
        "workflows": [
            "requirement_analysis",
            "architecture_design", 
            "code_implementation",
            "test_verification",
            "deployment_release",
            "monitoring_operations"
        ]
    },
    "quick_prototype": {
        "name": "快速原型开发",
        "description": "快速创建原型的简化流程",
        "estimated_duration": 1800,  # 30分钟
        "complexity": "low",
        "workflows": [
            "requirement_analysis",
            "code_implementation", 
            "test_verification"
        ]
    },
    "documentation_only": {
        "name": "文档和设计",
        "description": "专注于文档和架构设计",
        "estimated_duration": 1200,  # 20分钟
        "complexity": "medium",
        "workflows": [
            "requirement_analysis",
            "architecture_design"
        ]
    },
    "testing_focus": {
        "name": "测试和质量保证",
        "description": "专注于测试和监控的流程",
        "estimated_duration": 1500,  # 25分钟
        "complexity": "medium",
        "workflows": [
            "test_verification",
            "monitoring_operations"
        ]
    },
    "deployment_focus": {
        "name": "部署和运维",
        "description": "专注于部署和运维的流程",
        "estimated_duration": 1200,  # 20分钟
        "complexity": "medium", 
        "workflows": [
            "deployment_release",
            "monitoring_operations"
        ]
    },
    "ai_model_development": {
        "name": "AI模型开发",
        "description": "AI模型开发的专用流程",
        "estimated_duration": 3600,  # 1小时
        "complexity": "high",
        "workflows": [
            "requirement_analysis",
            "architecture_design",
            "code_implementation",
            "test_verification",
            "deployment_release"
        ]
    }
}

# ============================================================================
# MCP组件能力映射
# ============================================================================

MCP_CAPABILITIES = {
    "requirement_analysis_mcp": {
        "primary_functions": ["需求分析", "用户故事生成", "功能规格定义"],
        "supported_formats": ["text", "json", "markdown"],
        "estimated_processing_time": 300,
        "quality_score": 0.9,
        "reliability_score": 0.95
    },
    "code_generation_mcp": {
        "primary_functions": ["代码生成", "代码重构", "代码优化"],
        "supported_languages": ["python", "javascript", "java", "go", "rust"],
        "estimated_processing_time": 1800,
        "quality_score": 0.85,
        "reliability_score": 0.9
    },
    "test_manage_mcp": {
        "primary_functions": ["测试用例生成", "自动化测试", "测试报告"],
        "supported_frameworks": ["pytest", "jest", "junit", "mocha"],
        "estimated_processing_time": 900,
        "quality_score": 0.88,
        "reliability_score": 0.92
    },
    "deployment_mcp": {
        "primary_functions": ["部署配置", "容器化", "CI/CD管道"],
        "supported_platforms": ["docker", "kubernetes", "aws", "gcp", "azure"],
        "estimated_processing_time": 600,
        "quality_score": 0.9,
        "reliability_score": 0.93
    },
    "monitoring_mcp": {
        "primary_functions": ["性能监控", "日志分析", "告警配置"],
        "supported_tools": ["prometheus", "grafana", "elk", "datadog"],
        "estimated_processing_time": 300,
        "quality_score": 0.87,
        "reliability_score": 0.94
    },
    "documentation_mcp": {
        "primary_functions": ["API文档", "用户手册", "技术文档"],
        "supported_formats": ["markdown", "html", "pdf", "confluence"],
        "estimated_processing_time": 600,
        "quality_score": 0.9,
        "reliability_score": 0.95
    }
}

# ============================================================================
# 依赖规则配置
# ============================================================================

DEPENDENCY_RULES = {
    "requirement_analysis": {
        "dependencies": [],
        "can_run_parallel": False,
        "is_critical": True,
        "failure_impact": "high"
    },
    "architecture_design": {
        "dependencies": ["requirement_analysis"],
        "can_run_parallel": False,
        "is_critical": True,
        "failure_impact": "high"
    },
    "code_implementation": {
        "dependencies": ["architecture_design"],
        "can_run_parallel": True,
        "is_critical": True,
        "failure_impact": "high"
    },
    "test_verification": {
        "dependencies": ["code_implementation"],
        "can_run_parallel": True,
        "is_critical": False,
        "failure_impact": "medium"
    },
    "deployment_release": {
        "dependencies": ["code_implementation"],
        "can_run_parallel": True,
        "is_critical": False,
        "failure_impact": "medium"
    },
    "monitoring_operations": {
        "dependencies": ["deployment_release"],
        "can_run_parallel": False,
        "is_critical": False,
        "failure_impact": "low"
    }
}

# ============================================================================
# 智能路由配置
# ============================================================================

SMART_ROUTING_CONFIG = {
    "enable_smart_routing": True,
    "routing_algorithm": "weighted_round_robin",
    "load_balancing_strategy": "least_connections",
    "health_check_enabled": True,
    "circuit_breaker_enabled": True,
    "circuit_breaker_threshold": 5,
    "circuit_breaker_timeout": 60,
    "retry_policy": {
        "max_retries": 3,
        "retry_delay": 5,
        "exponential_backoff": True
    },
    "timeout_policy": {
        "connection_timeout": 10,
        "read_timeout": 30,
        "total_timeout": 60
    }
}

# ============================================================================
# 状态推送配置
# ============================================================================

STATUS_PUSH_CONFIG = {
    "enable_status_push": True,
    "push_interval": 5,  # 秒
    "batch_size": 10,
    "max_queue_size": 1000,
    "websocket_config": {
        "ping_interval": 20,
        "ping_timeout": 10,
        "close_timeout": 10,
        "max_size": 1048576,  # 1MB
        "max_queue": 32
    },
    "retry_config": {
        "max_retries": 3,
        "retry_delay": 2,
        "exponential_backoff": True
    }
}

# ============================================================================
# 环境特定配置
# ============================================================================

def get_environment_config() -> Dict[str, Any]:
    """获取环境特定配置"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return {
            "log_level": "WARNING",
            "max_parallel_tasks": 8,
            "enable_metrics": True,
            "enable_authentication": True,
            "health_check_interval": 15
        }
    elif env == "staging":
        return {
            "log_level": "INFO", 
            "max_parallel_tasks": 4,
            "enable_metrics": True,
            "enable_authentication": True,
            "health_check_interval": 30
        }
    else:  # development
        return {
            "log_level": "DEBUG",
            "max_parallel_tasks": 2,
            "enable_metrics": False,
            "enable_authentication": False,
            "health_check_interval": 60
        }

# ============================================================================
# 配置验证
# ============================================================================

def validate_config() -> bool:
    """验证配置的有效性"""
    try:
        # 验证必需的环境变量
        required_paths = [
            PRODUCT_ORCHESTRATOR_CONFIG["workflow_storage_path"],
            PRODUCT_ORCHESTRATOR_CONFIG["interaction_log_path"]
        ]
        
        for path in required_paths:
            os.makedirs(path, exist_ok=True)
        
        # 验证端口配置
        ports = [endpoint.port for endpoint in MCP_ENDPOINTS.values()]
        if len(ports) != len(set(ports)):
            raise ValueError("Duplicate port configurations found")
        
        # 验证工作流模板
        for template_name, template_config in WORKFLOW_TEMPLATES.items():
            if not template_config.get("workflows"):
                raise ValueError(f"Template {template_name} has no workflows defined")
        
        return True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

# ============================================================================
# 配置加载函数
# ============================================================================

def load_config() -> Dict[str, Any]:
    """加载完整配置"""
    # 验证配置
    if not validate_config():
        raise RuntimeError("Configuration validation failed")
    
    # 合并环境特定配置
    env_config = get_environment_config()
    config = {**PRODUCT_ORCHESTRATOR_CONFIG, **env_config}
    
    return {
        "orchestrator": config,
        "mcp_endpoints": MCP_ENDPOINTS,
        "workflow_templates": WORKFLOW_TEMPLATES,
        "mcp_capabilities": MCP_CAPABILITIES,
        "dependency_rules": DEPENDENCY_RULES,
        "smart_routing": SMART_ROUTING_CONFIG,
        "status_push": STATUS_PUSH_CONFIG
    }

if __name__ == "__main__":
    # 测试配置加载
    try:
        config = load_config()
        print("✅ Configuration loaded successfully")
        print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        print(f"Max parallel tasks: {config['orchestrator']['max_parallel_tasks']}")
        print(f"MCP endpoints: {len(config['mcp_endpoints'])}")
        print(f"Workflow templates: {len(config['workflow_templates'])}")
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        exit(1)

