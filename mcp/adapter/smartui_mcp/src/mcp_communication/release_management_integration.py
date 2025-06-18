"""
SmartUI MCP - 发布管理集成接口

为SmartUI MCP提供与发布管理MCP的集成接口，
支持构建、测试、部署等CI/CD流程的协调。
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from ..common.interfaces import MCPServiceInterface
from ..common.event_bus import EventBus
from ..mcp_communication.mcp_protocol import MCPClient

logger = logging.getLogger(__name__)


class ReleaseManagementIntegration:
    """发布管理MCP集成接口"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.release_mcp_client: Optional[MCPClient] = None
        self.module_info = {
            "name": "smartui_mcp",
            "version": "1.0.0",
            "type": "adapter",
            "capabilities": [
                "ui_generation",
                "user_behavior_analysis", 
                "intelligent_adaptation",
                "theme_management",
                "layout_optimization",
                "component_rendering",
                "event_handling",
                "state_management"
            ]
        }
        
        # 注册事件监听器
        self._register_event_listeners()
        
    def _register_event_listeners(self):
        """注册事件监听器"""
        self.event_bus.subscribe("MODULE_READY", self._on_module_ready)
        self.event_bus.subscribe("DEPLOYMENT_REQUEST", self._on_deployment_request)
        self.event_bus.subscribe("QUALITY_CHECK_REQUEST", self._on_quality_check_request)
        
    async def connect_to_release_management(self, release_mcp_url: str) -> bool:
        """连接到发布管理MCP"""
        try:
            self.release_mcp_client = MCPClient(release_mcp_url)
            await self.release_mcp_client.connect()
            
            # 注册模块信息
            await self._register_module()
            
            logger.info(f"已连接到发布管理MCP: {release_mcp_url}")
            return True
            
        except Exception as e:
            logger.error(f"连接发布管理MCP失败: {e}")
            return False
            
    async def _register_module(self):
        """向发布管理MCP注册模块信息"""
        try:
            registration_data = {
                "module_info": self.module_info,
                "health_check_endpoint": "/health",
                "metrics_endpoint": "/api/status",
                "build_requirements": {
                    "python_version": "3.11+",
                    "dependencies_file": "requirements.txt",
                    "test_command": "pytest tests/",
                    "build_command": "python -m build"
                },
                "deployment_config": {
                    "port": 8000,
                    "health_check_path": "/health",
                    "startup_timeout": 30,
                    "shutdown_timeout": 10
                }
            }
            
            if self.release_mcp_client:
                response = await self.release_mcp_client.call_method(
                    "register_module",
                    registration_data
                )
                
                if response.get("success"):
                    logger.info("模块注册成功")
                    await self.event_bus.publish("MODULE_REGISTERED", {
                        "module": self.module_info["name"],
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.error(f"模块注册失败: {response.get('error')}")
                    
        except Exception as e:
            logger.error(f"模块注册异常: {e}")
            
    async def request_build(self, build_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """请求构建"""
        try:
            build_request = {
                "module_name": self.module_info["name"],
                "build_type": "standard",
                "config": build_config or {},
                "timestamp": datetime.now().isoformat()
            }
            
            if self.release_mcp_client:
                response = await self.release_mcp_client.call_method(
                    "trigger_build",
                    build_request
                )
                
                await self.event_bus.publish("BUILD_REQUESTED", {
                    "module": self.module_info["name"],
                    "build_id": response.get("build_id"),
                    "status": response.get("status")
                })
                
                return response
            else:
                return {"success": False, "error": "未连接到发布管理MCP"}
                
        except Exception as e:
            logger.error(f"请求构建失败: {e}")
            return {"success": False, "error": str(e)}
            
    async def request_test(self, test_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """请求测试"""
        try:
            test_request = {
                "module_name": self.module_info["name"],
                "test_types": ["unit", "integration", "performance"],
                "config": test_config or {},
                "coverage_threshold": 90,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.release_mcp_client:
                response = await self.release_mcp_client.call_method(
                    "trigger_test",
                    test_request
                )
                
                await self.event_bus.publish("TEST_REQUESTED", {
                    "module": self.module_info["name"],
                    "test_id": response.get("test_id"),
                    "status": response.get("status")
                })
                
                return response
            else:
                return {"success": False, "error": "未连接到发布管理MCP"}
                
        except Exception as e:
            logger.error(f"请求测试失败: {e}")
            return {"success": False, "error": str(e)}
            
    async def request_deployment(self, environment: str, deployment_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """请求部署"""
        try:
            deployment_request = {
                "module_name": self.module_info["name"],
                "environment": environment,
                "version": self.module_info["version"],
                "config": deployment_config or {},
                "timestamp": datetime.now().isoformat()
            }
            
            if self.release_mcp_client:
                response = await self.release_mcp_client.call_method(
                    "trigger_deployment",
                    deployment_request
                )
                
                await self.event_bus.publish("DEPLOYMENT_REQUESTED", {
                    "module": self.module_info["name"],
                    "environment": environment,
                    "deployment_id": response.get("deployment_id"),
                    "status": response.get("status")
                })
                
                return response
            else:
                return {"success": False, "error": "未连接到发布管理MCP"}
                
        except Exception as e:
            logger.error(f"请求部署失败: {e}")
            return {"success": False, "error": str(e)}
            
    async def get_build_status(self, build_id: str) -> Dict[str, Any]:
        """获取构建状态"""
        try:
            if self.release_mcp_client:
                response = await self.release_mcp_client.call_method(
                    "get_build_status",
                    {"build_id": build_id}
                )
                return response
            else:
                return {"success": False, "error": "未连接到发布管理MCP"}
                
        except Exception as e:
            logger.error(f"获取构建状态失败: {e}")
            return {"success": False, "error": str(e)}
            
    async def get_test_results(self, test_id: str) -> Dict[str, Any]:
        """获取测试结果"""
        try:
            if self.release_mcp_client:
                response = await self.release_mcp_client.call_method(
                    "get_test_results",
                    {"test_id": test_id}
                )
                return response
            else:
                return {"success": False, "error": "未连接到发布管理MCP"}
                
        except Exception as e:
            logger.error(f"获取测试结果失败: {e}")
            return {"success": False, "error": str(e)}
            
    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """获取部署状态"""
        try:
            if self.release_mcp_client:
                response = await self.release_mcp_client.call_method(
                    "get_deployment_status",
                    {"deployment_id": deployment_id}
                )
                return response
            else:
                return {"success": False, "error": "未连接到发布管理MCP"}
                
        except Exception as e:
            logger.error(f"获取部署状态失败: {e}")
            return {"success": False, "error": str(e)}
            
    async def report_health_status(self) -> Dict[str, Any]:
        """报告健康状态"""
        try:
            health_data = {
                "module_name": self.module_info["name"],
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "uptime": "获取运行时间",
                    "memory_usage": "获取内存使用",
                    "cpu_usage": "获取CPU使用",
                    "active_connections": "获取活跃连接数"
                }
            }
            
            if self.release_mcp_client:
                response = await self.release_mcp_client.call_method(
                    "report_health",
                    health_data
                )
                return response
            else:
                return {"success": False, "error": "未连接到发布管理MCP"}
                
        except Exception as e:
            logger.error(f"报告健康状态失败: {e}")
            return {"success": False, "error": str(e)}
            
    async def _on_module_ready(self, event_data: Dict[str, Any]):
        """模块就绪事件处理"""
        logger.info("SmartUI MCP模块就绪，准备注册到发布管理MCP")
        
    async def _on_deployment_request(self, event_data: Dict[str, Any]):
        """部署请求事件处理"""
        environment = event_data.get("environment", "development")
        config = event_data.get("config", {})
        
        result = await self.request_deployment(environment, config)
        logger.info(f"部署请求结果: {result}")
        
    async def _on_quality_check_request(self, event_data: Dict[str, Any]):
        """质量检查请求事件处理"""
        test_config = event_data.get("config", {})
        
        result = await self.request_test(test_config)
        logger.info(f"质量检查请求结果: {result}")
        
    async def disconnect(self):
        """断开连接"""
        if self.release_mcp_client:
            await self.release_mcp_client.disconnect()
            self.release_mcp_client = None
            logger.info("已断开与发布管理MCP的连接")


class ReleaseManagementAPI:
    """发布管理API接口"""
    
    def __init__(self, integration: ReleaseManagementIntegration):
        self.integration = integration
        
    async def trigger_build(self, build_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """触发构建"""
        return await self.integration.request_build(build_config)
        
    async def trigger_test(self, test_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """触发测试"""
        return await self.integration.request_test(test_config)
        
    async def deploy_to_environment(self, environment: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """部署到环境"""
        return await self.integration.request_deployment(environment, config)
        
    async def get_pipeline_status(self, pipeline_id: str, pipeline_type: str) -> Dict[str, Any]:
        """获取流水线状态"""
        if pipeline_type == "build":
            return await self.integration.get_build_status(pipeline_id)
        elif pipeline_type == "test":
            return await self.integration.get_test_results(pipeline_id)
        elif pipeline_type == "deployment":
            return await self.integration.get_deployment_status(pipeline_id)
        else:
            return {"success": False, "error": f"未知的流水线类型: {pipeline_type}"}
            
    async def report_module_health(self) -> Dict[str, Any]:
        """报告模块健康状态"""
        return await self.integration.report_health_status()

