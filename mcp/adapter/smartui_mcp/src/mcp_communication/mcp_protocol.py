"""
SmartUI MCP - MCP协议通信模块

实现与MCP Coordinator和其他MCP服务的标准化通信。
支持服务注册、发现、调用和健康检查等核心功能。
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import websockets
from urllib.parse import urljoin

from ..common import (
    EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    MessageType, MessageHeader, MessagePayload, ComponentMessage
)


class MCPServiceStatus(str, Enum):
    """MCP服务状态枚举"""
    UNKNOWN = "unknown"
    REGISTERING = "registering"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class MCPConnectionType(str, Enum):
    """MCP连接类型枚举"""
    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"


@dataclass
class MCPServiceInfo:
    """MCP服务信息"""
    service_id: str
    service_name: str
    service_type: str
    version: str
    description: str
    endpoint: str
    connection_type: MCPConnectionType
    capabilities: List[str]
    status: MCPServiceStatus
    last_heartbeat: datetime
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if isinstance(self.connection_type, str):
            self.connection_type = MCPConnectionType(self.connection_type)
        if isinstance(self.status, str):
            self.status = MCPServiceStatus(self.status)


@dataclass
class MCPRequest:
    """MCP请求"""
    request_id: str
    target_service: str
    method: str
    params: Dict[str, Any]
    timeout: float
    timestamp: datetime
    
    def __post_init__(self):
        if self.request_id is None:
            self.request_id = generate_id("req_")


@dataclass
class MCPResponse:
    """MCP响应"""
    request_id: str
    source_service: str
    success: bool
    result: Any
    error: Optional[str]
    timestamp: datetime
    duration: float


class MCPClient:
    """MCP客户端基类"""
    
    def __init__(
        self,
        service_info: MCPServiceInfo,
        timeout: float = 30.0,
        retry_attempts: int = 3
    ):
        self.service_info = service_info
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.logger = logging.getLogger(f"{__name__}.MCPClient.{service_info.service_id}")
        
        # 连接状态
        self.connected = False
        self.last_error: Optional[str] = None
        
        # 性能统计
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
    
    async def connect(self) -> bool:
        """连接到服务"""
        try:
            success = await self._do_connect()
            self.connected = success
            
            if success:
                self.logger.info(f"Connected to {self.service_info.service_id}")
            else:
                self.logger.error(f"Failed to connect to {self.service_info.service_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error connecting to {self.service_info.service_id}: {e}")
            self.last_error = str(e)
            return False
    
    async def disconnect(self) -> bool:
        """断开连接"""
        try:
            success = await self._do_disconnect()
            self.connected = False
            
            if success:
                self.logger.info(f"Disconnected from {self.service_info.service_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from {self.service_info.service_id}: {e}")
            return False
    
    async def call_method(
        self,
        method: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> MCPResponse:
        """调用方法"""
        request = MCPRequest(
            request_id=generate_id("req_"),
            target_service=self.service_info.service_id,
            method=method,
            params=params,
            timeout=timeout or self.timeout,
            timestamp=datetime.now()
        )
        
        start_time = time.time()
        self.request_count += 1
        
        try:
            if not self.connected:
                await self.connect()
            
            result = await self._do_call_method(request)
            
            duration = time.time() - start_time
            self.total_response_time += duration
            self.success_count += 1
            
            response = MCPResponse(
                request_id=request.request_id,
                source_service=self.service_info.service_id,
                success=True,
                result=result,
                error=None,
                timestamp=datetime.now(),
                duration=duration
            )
            
            self.logger.debug(f"Method {method} completed in {duration:.3f}s")
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self.error_count += 1
            self.last_error = str(e)
            
            response = MCPResponse(
                request_id=request.request_id,
                source_service=self.service_info.service_id,
                success=False,
                result=None,
                error=str(e),
                timestamp=datetime.now(),
                duration=duration
            )
            
            self.logger.error(f"Method {method} failed after {duration:.3f}s: {e}")
            return response
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            response = await self.call_method("health_check", {}, timeout=5.0)
            return response.success
        except Exception:
            return False
    
    async def _do_connect(self) -> bool:
        """执行连接（子类实现）"""
        raise NotImplementedError
    
    async def _do_disconnect(self) -> bool:
        """执行断开连接（子类实现）"""
        raise NotImplementedError
    
    async def _do_call_method(self, request: MCPRequest) -> Any:
        """执行方法调用（子类实现）"""
        raise NotImplementedError
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "service_id": self.service_info.service_id,
            "connected": self.connected,
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / self.request_count if self.request_count > 0 else 0.0,
            "average_response_time": self.total_response_time / self.success_count if self.success_count > 0 else 0.0,
            "last_error": self.last_error
        }


class HTTPMCPClient(MCPClient):
    """HTTP MCP客户端"""
    
    def __init__(self, service_info: MCPServiceInfo, **kwargs):
        super().__init__(service_info, **kwargs)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _do_connect(self) -> bool:
        """建立HTTP连接"""
        try:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "SmartUI-MCP-Client/1.0"
                }
            )
            
            # 测试连接
            health_url = urljoin(self.service_info.endpoint, "/health")
            async with self.session.get(health_url) as response:
                return response.status == 200
                
        except Exception as e:
            if self.session:
                await self.session.close()
                self.session = None
            raise e
    
    async def _do_disconnect(self) -> bool:
        """关闭HTTP连接"""
        if self.session:
            await self.session.close()
            self.session = None
        return True
    
    async def _do_call_method(self, request: MCPRequest) -> Any:
        """执行HTTP方法调用"""
        if not self.session:
            raise RuntimeError("Not connected")
        
        # 构建请求URL
        method_url = urljoin(self.service_info.endpoint, f"/api/{request.method}")
        
        # 构建请求数据
        request_data = {
            "id": request.request_id,
            "method": request.method,
            "params": request.params,
            "timestamp": request.timestamp.isoformat()
        }
        
        # 发送请求
        async with self.session.post(method_url, json=request_data) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("result")
            else:
                error_text = await response.text()
                raise RuntimeError(f"HTTP {response.status}: {error_text}")


class WebSocketMCPClient(MCPClient):
    """WebSocket MCP客户端"""
    
    def __init__(self, service_info: MCPServiceInfo, **kwargs):
        super().__init__(service_info, **kwargs)
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_handler_task: Optional[asyncio.Task] = None
    
    async def _do_connect(self) -> bool:
        """建立WebSocket连接"""
        try:
            # 将HTTP URL转换为WebSocket URL
            ws_url = self.service_info.endpoint.replace("http://", "ws://").replace("https://", "wss://")
            if not ws_url.endswith("/ws"):
                ws_url = urljoin(ws_url, "/ws")
            
            self.websocket = await websockets.connect(
                ws_url,
                timeout=self.timeout,
                ping_interval=20,
                ping_timeout=10
            )
            
            # 启动消息处理器
            self.message_handler_task = asyncio.create_task(self._handle_messages())
            
            return True
            
        except Exception as e:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            raise e
    
    async def _do_disconnect(self) -> bool:
        """关闭WebSocket连接"""
        # 取消消息处理器
        if self.message_handler_task:
            self.message_handler_task.cancel()
            try:
                await self.message_handler_task
            except asyncio.CancelledError:
                pass
            self.message_handler_task = None
        
        # 关闭连接
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        # 清理待处理请求
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        self.pending_requests.clear()
        
        return True
    
    async def _do_call_method(self, request: MCPRequest) -> Any:
        """执行WebSocket方法调用"""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        # 构建请求消息
        message = {
            "id": request.request_id,
            "type": "request",
            "method": request.method,
            "params": request.params,
            "timestamp": request.timestamp.isoformat()
        }
        
        # 创建Future等待响应
        future = asyncio.Future()
        self.pending_requests[request.request_id] = future
        
        try:
            # 发送请求
            await self.websocket.send(json.dumps(message))
            
            # 等待响应
            result = await asyncio.wait_for(future, timeout=request.timeout)
            return result
            
        finally:
            # 清理请求
            self.pending_requests.pop(request.request_id, None)
    
    async def _handle_messages(self) -> None:
        """处理WebSocket消息"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(data)
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("WebSocket connection closed")
        except Exception as e:
            self.logger.error(f"Error in message handler: {e}")
    
    async def _process_message(self, data: Dict[str, Any]) -> None:
        """处理单个消息"""
        message_type = data.get("type")
        message_id = data.get("id")
        
        if message_type == "response" and message_id in self.pending_requests:
            # 响应消息
            future = self.pending_requests[message_id]
            if not future.done():
                if data.get("success", True):
                    future.set_result(data.get("result"))
                else:
                    future.set_exception(RuntimeError(data.get("error", "Unknown error")))
        
        elif message_type == "notification":
            # 通知消息
            await self._handle_notification(data)
    
    async def _handle_notification(self, data: Dict[str, Any]) -> None:
        """处理通知消息"""
        # 发布事件到事件总线
        await publish_event(
            event_type=EventBusEventType.MCP_NOTIFICATION_RECEIVED,
            data={
                "source_service": self.service_info.service_id,
                "notification": data
            },
            source=f"mcp_client_{self.service_info.service_id}"
        )


class MCPServiceRegistry:
    """MCP服务注册表"""
    
    def __init__(self, coordinator_endpoint: Optional[str] = None):
        self.coordinator_endpoint = coordinator_endpoint
        self.services: Dict[str, MCPServiceInfo] = {}
        self.clients: Dict[str, MCPClient] = {}
        self.logger = logging.getLogger(f"{__name__}.MCPServiceRegistry")
        
        # 缓存
        self.cache = AsyncCache(default_ttl=300)  # 5分钟缓存
        
        # 健康检查
        self.health_check_interval = 60  # 60秒
        self.health_check_task: Optional[asyncio.Task] = None
        
        self.logger.info("MCP Service Registry initialized")
    
    async def start(self) -> None:
        """启动服务注册表"""
        # 启动健康检查任务
        if self.health_check_task is None or self.health_check_task.done():
            self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        self.logger.info("MCP Service Registry started")
    
    async def stop(self) -> None:
        """停止服务注册表"""
        # 停止健康检查任务
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # 断开所有客户端连接
        for client in self.clients.values():
            await client.disconnect()
        
        self.clients.clear()
        self.logger.info("MCP Service Registry stopped")
    
    async def register_service(self, service_info: MCPServiceInfo) -> bool:
        """注册服务"""
        try:
            # 更新服务信息
            service_info.status = MCPServiceStatus.REGISTERING
            service_info.last_heartbeat = datetime.now()
            
            self.services[service_info.service_id] = service_info
            
            # 创建客户端
            client = await self._create_client(service_info)
            if client:
                self.clients[service_info.service_id] = client
                
                # 尝试连接
                if await client.connect():
                    service_info.status = MCPServiceStatus.ACTIVE
                    self.logger.info(f"Service registered and connected: {service_info.service_id}")
                else:
                    service_info.status = MCPServiceStatus.INACTIVE
                    self.logger.warning(f"Service registered but connection failed: {service_info.service_id}")
                
                return True
            else:
                service_info.status = MCPServiceStatus.ERROR
                self.logger.error(f"Failed to create client for service: {service_info.service_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error registering service {service_info.service_id}: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """注销服务"""
        try:
            # 断开客户端连接
            if service_id in self.clients:
                await self.clients[service_id].disconnect()
                del self.clients[service_id]
            
            # 移除服务信息
            if service_id in self.services:
                del self.services[service_id]
            
            # 清理缓存
            await self.cache.delete(f"service_{service_id}")
            
            self.logger.info(f"Service unregistered: {service_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unregistering service {service_id}: {e}")
            return False
    
    async def get_service(self, service_id: str) -> Optional[MCPServiceInfo]:
        """获取服务信息"""
        return self.services.get(service_id)
    
    async def list_services(
        self,
        service_type: Optional[str] = None,
        status: Optional[MCPServiceStatus] = None
    ) -> List[MCPServiceInfo]:
        """列出服务"""
        services = list(self.services.values())
        
        if service_type:
            services = [s for s in services if s.service_type == service_type]
        
        if status:
            services = [s for s in services if s.status == status]
        
        return services
    
    async def call_service(
        self,
        service_id: str,
        method: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> MCPResponse:
        """调用服务方法"""
        client = self.clients.get(service_id)
        if not client:
            return MCPResponse(
                request_id=generate_id("req_"),
                source_service=service_id,
                success=False,
                result=None,
                error=f"Service {service_id} not found",
                timestamp=datetime.now(),
                duration=0.0
            )
        
        return await client.call_method(method, params, timeout)
    
    async def _create_client(self, service_info: MCPServiceInfo) -> Optional[MCPClient]:
        """创建客户端"""
        try:
            if service_info.connection_type == MCPConnectionType.HTTP:
                return HTTPMCPClient(service_info)
            elif service_info.connection_type == MCPConnectionType.WEBSOCKET:
                return WebSocketMCPClient(service_info)
            else:
                self.logger.error(f"Unsupported connection type: {service_info.connection_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating client for {service_info.service_id}: {e}")
            return None
    
    async def _health_check_loop(self) -> None:
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
    
    async def _perform_health_checks(self) -> None:
        """执行健康检查"""
        for service_id, client in self.clients.items():
            try:
                is_healthy = await client.health_check()
                service_info = self.services.get(service_id)
                
                if service_info:
                    if is_healthy:
                        service_info.status = MCPServiceStatus.ACTIVE
                        service_info.last_heartbeat = datetime.now()
                    else:
                        service_info.status = MCPServiceStatus.INACTIVE
                        self.logger.warning(f"Health check failed for service: {service_id}")
                
            except Exception as e:
                self.logger.error(f"Error in health check for {service_id}: {e}")
                service_info = self.services.get(service_id)
                if service_info:
                    service_info.status = MCPServiceStatus.ERROR
    
    async def get_registry_statistics(self) -> Dict[str, Any]:
        """获取注册表统计信息"""
        total_services = len(self.services)
        active_services = len([s for s in self.services.values() if s.status == MCPServiceStatus.ACTIVE])
        
        client_stats = {}
        for service_id, client in self.clients.items():
            client_stats[service_id] = client.get_statistics()
        
        return {
            "total_services": total_services,
            "active_services": active_services,
            "inactive_services": total_services - active_services,
            "client_statistics": client_stats,
            "cache_stats": await self.cache.get_stats()
        }

