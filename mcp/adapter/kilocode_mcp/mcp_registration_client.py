#!/usr/bin/env python3
"""
KiloCode MCP 注册客户端
负责向MCP Coordinator注册kilocode_mcp并维护注册状态

功能：
1. 自动注册到coordinator
2. 维护心跳和健康检查
3. 处理注册更新
4. 故障恢复机制
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import aiohttp
from kilocode_mcp_redesigned import KiloCodeMCP, KiloCodeConfig

class MCPRegistrationClient:
    """MCP注册客户端"""
    
    def __init__(self, kilocode_mcp: KiloCodeMCP, coordinator_url: str = None):
        self.kilocode_mcp = kilocode_mcp
        self.config = kilocode_mcp.config
        self.coordinator_url = coordinator_url or self.config.get(
            "integration.coordinator_endpoint", 
            "http://localhost:8080/coordinator"
        )
        self.registration_id = None
        self.last_heartbeat = None
        self.is_registered = False
        self.logger = logging.getLogger("mcp_registration")
        
        # 注册信息
        self.registration_info = self._build_registration_info()
    
    def _build_registration_info(self) -> Dict[str, Any]:
        """构建注册信息"""
        return {
            "mcp_id": "kilocode_mcp",
            "mcp_name": "KiloCode兜底创建引擎",
            "mcp_type": "fallback_creator",
            "version": self.kilocode_mcp.version,
            "capabilities": {
                "supported_workflows": self.kilocode_mcp.supported_workflows,
                "supported_creation_types": self.kilocode_mcp.supported_creation_types,
                "supported_languages": self.kilocode_mcp.supported_languages,
                "special_abilities": [
                    "snake_game_generation",
                    "ppt_creation", 
                    "fallback_solution",
                    "cross_workflow_creation",
                    "ai_assisted_creation"
                ]
            },
            "priority_level": "fallback",
            "routing_conditions": {
                "trigger_when": "all_other_mcps_failed",
                "workflow_support": "universal",
                "creation_focus": "code_and_document",
                "fallback_scenarios": [
                    "专用MCP失败",
                    "跨工作流需求",
                    "复杂创建任务",
                    "AI协助失败后兜底"
                ]
            },
            "performance_metrics": {
                "avg_response_time": "2-5秒",
                "success_rate": "95%",
                "complexity_handling": "medium_to_high",
                "concurrent_requests": self.config.get("performance.max_concurrent_requests", 5)
            },
            "endpoint": f"http://localhost:8080/mcp/kilocode",
            "health_check": f"http://localhost:8080/mcp/kilocode/health",
            "status": "active",
            "registration_time": datetime.now().isoformat(),
            "config_version": self.config.get("mcp_info.version", "2.0.0")
        }
    
    async def register(self) -> bool:
        """注册到coordinator"""
        try:
            self.logger.info(f"开始注册到coordinator: {self.coordinator_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coordinator_url}/register",
                    json=self.registration_info,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        self.registration_id = result.get("registration_id")
                        self.is_registered = True
                        self.last_heartbeat = datetime.now()
                        
                        self.logger.info(f"注册成功，ID: {self.registration_id}")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"注册失败: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"注册异常: {str(e)}")
            return False
    
    async def send_heartbeat(self) -> bool:
        """发送心跳"""
        if not self.is_registered:
            return False
            
        try:
            heartbeat_data = {
                "registration_id": self.registration_id,
                "mcp_id": "kilocode_mcp",
                "status": "active",
                "timestamp": datetime.now().isoformat(),
                "performance_stats": await self._get_performance_stats()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coordinator_url}/heartbeat",
                    json=heartbeat_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        self.last_heartbeat = datetime.now()
                        return True
                    else:
                        self.logger.warning(f"心跳失败: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"心跳异常: {str(e)}")
            return False
    
    async def _get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return {
            "requests_processed": getattr(self.kilocode_mcp, 'requests_processed', 0),
            "success_count": getattr(self.kilocode_mcp, 'success_count', 0),
            "error_count": getattr(self.kilocode_mcp, 'error_count', 0),
            "avg_response_time": getattr(self.kilocode_mcp, 'avg_response_time', 0),
            "current_load": getattr(self.kilocode_mcp, 'current_load', 0),
            "memory_usage": self._get_memory_usage(),
            "uptime": self._get_uptime()
        }
    
    def _get_memory_usage(self) -> float:
        """获取内存使用率"""
        try:
            import psutil
            return psutil.Process().memory_percent()
        except:
            return 0.0
    
    def _get_uptime(self) -> float:
        """获取运行时间（秒）"""
        if hasattr(self, 'start_time'):
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    async def update_registration(self, updates: Dict[str, Any]) -> bool:
        """更新注册信息"""
        if not self.is_registered:
            return False
            
        try:
            update_data = {
                "registration_id": self.registration_id,
                "updates": updates,
                "timestamp": datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.coordinator_url}/update",
                    json=update_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        self.logger.info("注册信息更新成功")
                        return True
                    else:
                        self.logger.error(f"更新失败: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"更新异常: {str(e)}")
            return False
    
    async def unregister(self) -> bool:
        """取消注册"""
        if not self.is_registered:
            return True
            
        try:
            unregister_data = {
                "registration_id": self.registration_id,
                "mcp_id": "kilocode_mcp",
                "reason": "正常关闭",
                "timestamp": datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.coordinator_url}/unregister",
                    json=unregister_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        self.is_registered = False
                        self.registration_id = None
                        self.logger.info("取消注册成功")
                        return True
                    else:
                        self.logger.error(f"取消注册失败: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"取消注册异常: {str(e)}")
            return False
    
    async def start_heartbeat_loop(self):
        """启动心跳循环"""
        heartbeat_interval = self.config.get("integration.health_check_interval", 60)
        
        self.logger.info(f"启动心跳循环，间隔: {heartbeat_interval}秒")
        
        while self.is_registered:
            try:
                success = await self.send_heartbeat()
                if not success:
                    self.logger.warning("心跳失败，尝试重新注册")
                    await self.register()
                
                await asyncio.sleep(heartbeat_interval)
                
            except asyncio.CancelledError:
                self.logger.info("心跳循环被取消")
                break
            except Exception as e:
                self.logger.error(f"心跳循环异常: {str(e)}")
                await asyncio.sleep(heartbeat_interval)

class MCPCoordinatorClient:
    """MCP Coordinator客户端"""
    
    def __init__(self, coordinator_url: str = None):
        self.coordinator_url = coordinator_url or "http://localhost:8080/coordinator"
        self.logger = logging.getLogger("coordinator_client")
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """向coordinator发送请求"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.coordinator_url}/request",
                    json=request,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Coordinator请求失败: {response.status} - {error_text}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Coordinator请求异常: {str(e)}"
            }
    
    async def get_mcp_list(self) -> Dict[str, Any]:
        """获取已注册的MCP列表"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.coordinator_url}/mcps",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"success": False, "mcps": []}
                        
        except Exception as e:
            self.logger.error(f"获取MCP列表失败: {str(e)}")
            return {"success": False, "mcps": []}

async def main():
    """主函数 - 演示注册流程"""
    print("🚀 KiloCode MCP 注册演示")
    
    # 1. 创建KiloCode MCP实例
    kilocode_mcp = KiloCodeMCP()
    
    # 2. 创建注册客户端
    registration_client = MCPRegistrationClient(kilocode_mcp)
    
    # 3. 注册到coordinator
    success = await registration_client.register()
    if success:
        print("✅ 注册成功")
        
        # 4. 发送心跳
        heartbeat_success = await registration_client.send_heartbeat()
        print(f"💓 心跳状态: {'成功' if heartbeat_success else '失败'}")
        
        # 5. 演示更新注册信息
        updates = {
            "status": "busy",
            "current_load": 0.8
        }
        update_success = await registration_client.update_registration(updates)
        print(f"🔄 更新状态: {'成功' if update_success else '失败'}")
        
        # 6. 取消注册
        await asyncio.sleep(2)
        unregister_success = await registration_client.unregister()
        print(f"❌ 取消注册: {'成功' if unregister_success else '失败'}")
        
    else:
        print("❌ 注册失败")

if __name__ == "__main__":
    asyncio.run(main())

