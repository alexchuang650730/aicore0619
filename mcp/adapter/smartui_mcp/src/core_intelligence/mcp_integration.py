"""
SmartUI MCP - MCP集成组件

实现与其他MCP服务的通信和集成，包括服务发现、调用管理、
数据同步和错误处理等功能。
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import weakref

from ..common import (
    IMCPIntegration, EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    MessageType, MessageHeader, MessagePayload, ComponentMessage
)


class MCPServiceStatus(str, Enum):
    """MCP服务状态枚举"""
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class MCPCallType(str, Enum):
    """MCP调用类型枚举"""
    SYNC = "sync"
    ASYNC = "async"
    STREAMING = "streaming"
    BATCH = "batch"


@dataclass
class MCPService:
    """MCP服务信息"""
    service_id: str
    name: str
    description: str
    version: str
    endpoint: str
    capabilities: List[str]
    status: MCPServiceStatus
    last_health_check: Optional[datetime] = None
    response_time: float = 0.0
    error_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MCPCall:
    """MCP调用记录"""
    call_id: str
    service_id: str
    method: str
    call_type: MCPCallType
    parameters: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: float = 0.0
    
    def __post_init__(self):
        if self.call_id is None:
            self.call_id = generate_id("mcp_call_")


@dataclass
class MCPSubscription:
    """MCP订阅"""
    subscription_id: str
    service_id: str
    event_type: str
    callback: Callable
    filter_conditions: Dict[str, Any]
    created_at: datetime
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def __post_init__(self):
        if self.subscription_id is None:
            self.subscription_id = generate_id("mcp_sub_")


class MCPServiceRegistry:
    """MCP服务注册表"""
    
    def __init__(self):
        self.services: Dict[str, MCPService] = {}
        self.service_groups: Dict[str, List[str]] = {}
        self.capability_index: Dict[str, List[str]] = {}
        
    def register_service(self, service: MCPService) -> None:
        """注册服务"""
        self.services[service.service_id] = service
        
        # 更新能力索引
        for capability in service.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = []
            self.capability_index[capability].append(service.service_id)
    
    def unregister_service(self, service_id: str) -> bool:
        """取消注册服务"""
        if service_id not in self.services:
            return False
        
        service = self.services[service_id]
        
        # 从能力索引中移除
        for capability in service.capabilities:
            if capability in self.capability_index:
                self.capability_index[capability].remove(service_id)
                if not self.capability_index[capability]:
                    del self.capability_index[capability]
        
        # 从服务组中移除
        for group_services in self.service_groups.values():
            if service_id in group_services:
                group_services.remove(service_id)
        
        del self.services[service_id]
        return True
    
    def find_services_by_capability(self, capability: str) -> List[MCPService]:
        """根据能力查找服务"""
        service_ids = self.capability_index.get(capability, [])
        return [self.services[sid] for sid in service_ids if sid in self.services]
    
    def find_services_by_status(self, status: MCPServiceStatus) -> List[MCPService]:
        """根据状态查找服务"""
        return [service for service in self.services.values() if service.status == status]
    
    def get_service(self, service_id: str) -> Optional[MCPService]:
        """获取服务信息"""
        return self.services.get(service_id)
    
    def list_services(self) -> List[MCPService]:
        """列出所有服务"""
        return list(self.services.values())
    
    def update_service_status(self, service_id: str, status: MCPServiceStatus) -> bool:
        """更新服务状态"""
        if service_id in self.services:
            self.services[service_id].status = status
            self.services[service_id].last_health_check = datetime.now()
            return True
        return False


class MCPCallManager:
    """MCP调用管理器"""
    
    def __init__(self, max_concurrent_calls: int = 50):
        self.max_concurrent_calls = max_concurrent_calls
        self.active_calls: Dict[str, MCPCall] = {}
        self.call_history: List[MCPCall] = []
        self.call_semaphore = asyncio.Semaphore(max_concurrent_calls)
        self.call_cache = AsyncCache(max_size=500, ttl=300)  # 5分钟缓存
        
    async def make_call(
        self,
        service: MCPService,
        method: str,
        parameters: Dict[str, Any],
        call_type: MCPCallType = MCPCallType.SYNC,
        timeout: float = 30.0,
        cache_key: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """执行MCP调用"""
        
        # 检查缓存
        if cache_key:
            cached_result = await self.call_cache.get(cache_key)
            if cached_result:
                return True, cached_result, None
        
        # 创建调用记录
        call = MCPCall(
            call_id=generate_id("mcp_call_"),
            service_id=service.service_id,
            method=method,
            call_type=call_type,
            parameters=parameters,
            started_at=datetime.now()
        )
        
        try:
            async with self.call_semaphore:
                self.active_calls[call.call_id] = call
                
                if call_type == MCPCallType.SYNC:
                    success, response, error = await self._make_sync_call(service, method, parameters, timeout)
                elif call_type == MCPCallType.ASYNC:
                    success, response, error = await self._make_async_call(service, method, parameters, timeout)
                elif call_type == MCPCallType.STREAMING:
                    success, response, error = await self._make_streaming_call(service, method, parameters, timeout)
                elif call_type == MCPCallType.BATCH:
                    success, response, error = await self._make_batch_call(service, method, parameters, timeout)
                else:
                    success, response, error = False, None, f"Unsupported call type: {call_type}"
                
                # 更新调用记录
                call.completed_at = datetime.now()
                call.duration = (call.completed_at - call.started_at).total_seconds()
                call.response = response
                call.error = error
                
                # 移除活跃调用
                if call.call_id in self.active_calls:
                    del self.active_calls[call.call_id]
                
                # 添加到历史
                self.call_history.append(call)
                
                # 限制历史大小
                if len(self.call_history) > 10000:
                    self.call_history = self.call_history[-5000:]
                
                # 缓存成功的结果
                if success and cache_key and response:
                    await self.call_cache.set(cache_key, response)
                
                return success, response, error
                
        except Exception as e:
            # 确保清理
            if call.call_id in self.active_calls:
                del self.active_calls[call.call_id]
            
            call.completed_at = datetime.now()
            call.duration = (call.completed_at - call.started_at).total_seconds()
            call.error = str(e)
            self.call_history.append(call)
            
            return False, None, str(e)
    
    async def _make_sync_call(
        self,
        service: MCPService,
        method: str,
        parameters: Dict[str, Any],
        timeout: float
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """执行同步调用"""
        try:
            # 构建请求消息
            message = create_request_message(
                method=method,
                params=parameters,
                target_service=service.service_id
            )
            
            # 发送HTTP请求
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(
                    service.endpoint,
                    json=asdict(message),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return True, result, None
                    else:
                        error_text = await response.text()
                        return False, None, f"HTTP {response.status}: {error_text}"
                        
        except asyncio.TimeoutError:
            return False, None, "Request timeout"
        except Exception as e:
            return False, None, str(e)
    
    async def _make_async_call(
        self,
        service: MCPService,
        method: str,
        parameters: Dict[str, Any],
        timeout: float
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """执行异步调用"""
        # 异步调用通常返回一个任务ID，然后需要轮询结果
        try:
            # 首先发起异步任务
            message = create_request_message(
                method=f"{method}_async",
                params=parameters,
                target_service=service.service_id
            )
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(
                    service.endpoint,
                    json=asdict(message),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        task_result = await response.json()
                        task_id = task_result.get("task_id")
                        
                        if task_id:
                            # 轮询任务状态
                            return await self._poll_async_task(service, task_id, timeout)
                        else:
                            return False, None, "No task ID returned"
                    else:
                        error_text = await response.text()
                        return False, None, f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            return False, None, str(e)
    
    async def _poll_async_task(
        self,
        service: MCPService,
        task_id: str,
        timeout: float
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """轮询异步任务结果"""
        start_time = time.time()
        poll_interval = 1.0  # 1秒轮询间隔
        
        while time.time() - start_time < timeout:
            try:
                message = create_request_message(
                    method="get_task_status",
                    params={"task_id": task_id},
                    target_service=service.service_id
                )
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        service.endpoint,
                        json=asdict(message),
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            status = result.get("status")
                            
                            if status == "completed":
                                return True, result.get("result"), None
                            elif status == "failed":
                                return False, None, result.get("error", "Task failed")
                            elif status in ["pending", "running"]:
                                # 继续轮询
                                await asyncio.sleep(poll_interval)
                                continue
                            else:
                                return False, None, f"Unknown task status: {status}"
                        else:
                            return False, None, f"HTTP {response.status}"
                            
            except Exception as e:
                return False, None, str(e)
        
        return False, None, "Async task timeout"
    
    async def _make_streaming_call(
        self,
        service: MCPService,
        method: str,
        parameters: Dict[str, Any],
        timeout: float
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """执行流式调用"""
        try:
            message = create_request_message(
                method=f"{method}_stream",
                params=parameters,
                target_service=service.service_id
            )
            
            results = []
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(
                    service.endpoint,
                    json=asdict(message),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                try:
                                    chunk = json.loads(line.decode('utf-8'))
                                    results.append(chunk)
                                except json.JSONDecodeError:
                                    continue
                        
                        return True, {"stream_results": results}, None
                    else:
                        error_text = await response.text()
                        return False, None, f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            return False, None, str(e)
    
    async def _make_batch_call(
        self,
        service: MCPService,
        method: str,
        parameters: Dict[str, Any],
        timeout: float
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """执行批量调用"""
        try:
            message = create_request_message(
                method=f"{method}_batch",
                params=parameters,
                target_service=service.service_id
            )
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(
                    service.endpoint,
                    json=asdict(message),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return True, result, None
                    else:
                        error_text = await response.text()
                        return False, None, f"HTTP {response.status}: {error_text}"
                        
        except Exception as e:
            return False, None, str(e)
    
    def get_call_statistics(self) -> Dict[str, Any]:
        """获取调用统计信息"""
        if not self.call_history:
            return {
                "total_calls": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "active_calls": len(self.active_calls)
            }
        
        total_calls = len(self.call_history)
        successful_calls = sum(1 for call in self.call_history if call.error is None)
        success_rate = successful_calls / total_calls if total_calls > 0 else 0.0
        
        total_duration = sum(call.duration for call in self.call_history)
        average_duration = total_duration / total_calls if total_calls > 0 else 0.0
        
        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": total_calls - successful_calls,
            "success_rate": success_rate,
            "average_duration": average_duration,
            "active_calls": len(self.active_calls)
        }


class MCPEventManager:
    """MCP事件管理器"""
    
    def __init__(self):
        self.subscriptions: Dict[str, MCPSubscription] = {}
        self.service_subscriptions: Dict[str, List[str]] = {}
        
    def subscribe(
        self,
        service_id: str,
        event_type: str,
        callback: Callable,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """订阅MCP事件"""
        subscription = MCPSubscription(
            subscription_id=generate_id("mcp_sub_"),
            service_id=service_id,
            event_type=event_type,
            callback=callback,
            filter_conditions=filter_conditions or {},
            created_at=datetime.now()
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        
        if service_id not in self.service_subscriptions:
            self.service_subscriptions[service_id] = []
        self.service_subscriptions[service_id].append(subscription.subscription_id)
        
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        if subscription_id not in self.subscriptions:
            return False
        
        subscription = self.subscriptions[subscription_id]
        service_id = subscription.service_id
        
        # 从服务订阅列表中移除
        if service_id in self.service_subscriptions:
            self.service_subscriptions[service_id].remove(subscription_id)
            if not self.service_subscriptions[service_id]:
                del self.service_subscriptions[service_id]
        
        del self.subscriptions[subscription_id]
        return True
    
    async def handle_event(self, service_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """处理MCP事件"""
        if service_id not in self.service_subscriptions:
            return
        
        for subscription_id in self.service_subscriptions[service_id]:
            if subscription_id in self.subscriptions:
                subscription = self.subscriptions[subscription_id]
                
                # 检查事件类型匹配
                if subscription.event_type != event_type and subscription.event_type != "*":
                    continue
                
                # 应用过滤条件
                if not self._match_filter_conditions(event_data, subscription.filter_conditions):
                    continue
                
                # 调用回调
                try:
                    if asyncio.iscoroutinefunction(subscription.callback):
                        await subscription.callback(service_id, event_type, event_data)
                    else:
                        subscription.callback(service_id, event_type, event_data)
                    
                    # 更新统计
                    subscription.last_triggered = datetime.now()
                    subscription.trigger_count += 1
                    
                except Exception as e:
                    logging.error(f"Error in MCP event callback: {e}")
    
    def _match_filter_conditions(
        self,
        event_data: Dict[str, Any],
        filter_conditions: Dict[str, Any]
    ) -> bool:
        """匹配过滤条件"""
        if not filter_conditions:
            return True
        
        for key, expected_value in filter_conditions.items():
            if key not in event_data:
                return False
            
            actual_value = event_data[key]
            
            if isinstance(expected_value, dict) and "operator" in expected_value:
                # 支持操作符
                operator = expected_value["operator"]
                value = expected_value["value"]
                
                if operator == "eq" and actual_value != value:
                    return False
                elif operator == "ne" and actual_value == value:
                    return False
                elif operator == "gt" and actual_value <= value:
                    return False
                elif operator == "lt" and actual_value >= value:
                    return False
                elif operator == "in" and actual_value not in value:
                    return False
                elif operator == "contains" and value not in actual_value:
                    return False
            else:
                # 简单相等比较
                if actual_value != expected_value:
                    return False
        
        return True


class SmartUIMCPIntegration(IMCPIntegration):
    """SmartUI MCP集成实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 子组件
        self.service_registry = MCPServiceRegistry()
        self.call_manager = MCPCallManager(
            max_concurrent_calls=self.config.get("max_concurrent_calls", 50)
        )
        self.event_manager = MCPEventManager()
        
        # 健康检查
        self.health_check_interval = self.config.get("health_check_interval", 60)  # 60秒
        self.health_check_task: Optional[asyncio.Task] = None
        
        # 缓存
        self.service_cache = AsyncCache(max_size=100, ttl=300)
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        # 性能监控
        self.performance_metrics: Dict[str, Any] = {}
        
        self.logger.info("SmartUI MCP Integration initialized")
    
    async def start(self) -> None:
        """启动MCP集成"""
        try:
            # 启动健康检查任务
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            # 发现并注册已知的MCP服务
            await self._discover_services()
            
            self.logger.info("MCP Integration started")
            
        except Exception as e:
            self.logger.error(f"Error starting MCP Integration: {e}")
            raise
    
    async def stop(self) -> None:
        """停止MCP集成"""
        try:
            # 停止健康检查任务
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("MCP Integration stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping MCP Integration: {e}")
    
    @log_execution_time()
    async def call_mcp_service(
        self,
        service_id: str,
        method: str,
        parameters: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """调用MCP服务"""
        try:
            options = options or {}
            
            # 获取服务信息
            service = self.service_registry.get_service(service_id)
            if not service:
                return {
                    "success": False,
                    "error": f"Service not found: {service_id}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 检查服务状态
            if service.status != MCPServiceStatus.AVAILABLE:
                return {
                    "success": False,
                    "error": f"Service unavailable: {service.status.value}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 执行调用
            call_type = MCPCallType(options.get("call_type", "sync"))
            timeout = options.get("timeout", 30.0)
            cache_key = options.get("cache_key")
            
            success, response, error = await self.call_manager.make_call(
                service=service,
                method=method,
                parameters=parameters,
                call_type=call_type,
                timeout=timeout,
                cache_key=cache_key
            )
            
            # 更新服务统计
            if error:
                service.error_count += 1
            
            # 发布调用事件
            await publish_event(
                event_type=EventBusEventType.MCP_SERVICE_CALLED,
                data={
                    "service_id": service_id,
                    "method": method,
                    "success": success,
                    "duration": response.get("duration", 0) if response else 0
                },
                source="mcp_integration"
            )
            
            return {
                "success": success,
                "response": response,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calling MCP service {service_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def register_mcp_service(self, service_info: Dict[str, Any]) -> bool:
        """注册MCP服务"""
        try:
            service = MCPService(
                service_id=service_info["service_id"],
                name=service_info["name"],
                description=service_info.get("description", ""),
                version=service_info.get("version", "1.0.0"),
                endpoint=service_info["endpoint"],
                capabilities=service_info.get("capabilities", []),
                status=MCPServiceStatus(service_info.get("status", "unknown")),
                metadata=service_info.get("metadata", {})
            )
            
            self.service_registry.register_service(service)
            
            # 清理缓存
            await self.service_cache.clear()
            
            # 发布注册事件
            await publish_event(
                event_type=EventBusEventType.MCP_SERVICE_REGISTERED,
                data={
                    "service_id": service.service_id,
                    "name": service.name,
                    "capabilities": service.capabilities
                },
                source="mcp_integration"
            )
            
            self.logger.info(f"Registered MCP service: {service.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering MCP service: {e}")
            return False
    
    async def unregister_mcp_service(self, service_id: str) -> bool:
        """取消注册MCP服务"""
        try:
            success = self.service_registry.unregister_service(service_id)
            
            if success:
                # 清理缓存
                await self.service_cache.clear()
                
                # 发布取消注册事件
                await publish_event(
                    event_type=EventBusEventType.MCP_SERVICE_UNREGISTERED,
                    data={"service_id": service_id},
                    source="mcp_integration"
                )
                
                self.logger.info(f"Unregistered MCP service: {service_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error unregistering MCP service {service_id}: {e}")
            return False
    
    async def list_mcp_services(
        self,
        capability: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """列出MCP服务"""
        try:
            cache_key = f"list_services_{capability}_{status}"
            
            # 尝试从缓存获取
            cached_result = await self.service_cache.get(cache_key)
            if cached_result:
                return cached_result
            
            services = self.service_registry.list_services()
            
            # 应用过滤器
            if capability:
                services = self.service_registry.find_services_by_capability(capability)
            
            if status:
                service_status = MCPServiceStatus(status)
                services = [s for s in services if s.status == service_status]
            
            # 转换为字典
            result = [asdict(service) for service in services]
            
            # 缓存结果
            await self.service_cache.set(cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error listing MCP services: {e}")
            return []
    
    async def get_mcp_service_info(self, service_id: str) -> Optional[Dict[str, Any]]:
        """获取MCP服务信息"""
        try:
            service = self.service_registry.get_service(service_id)
            if service:
                return asdict(service)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting MCP service info {service_id}: {e}")
            return None
    
    async def subscribe_to_mcp_events(
        self,
        service_id: str,
        event_type: str,
        callback: Callable,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """订阅MCP事件"""
        try:
            subscription_id = self.event_manager.subscribe(
                service_id=service_id,
                event_type=event_type,
                callback=callback,
                filter_conditions=filter_conditions
            )
            
            self.logger.debug(f"Subscribed to MCP events: {service_id}/{event_type}")
            return subscription_id
            
        except Exception as e:
            self.logger.error(f"Error subscribing to MCP events: {e}")
            return ""
    
    async def unsubscribe_from_mcp_events(self, subscription_id: str) -> bool:
        """取消订阅MCP事件"""
        try:
            success = self.event_manager.unsubscribe(subscription_id)
            
            if success:
                self.logger.debug(f"Unsubscribed from MCP events: {subscription_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error unsubscribing from MCP events: {e}")
            return False
    
    async def _discover_services(self) -> None:
        """发现MCP服务"""
        try:
            # 从配置中加载已知服务
            known_services = self.config.get("known_services", [])
            
            for service_info in known_services:
                await self.register_mcp_service(service_info)
            
            # 这里可以添加自动发现逻辑
            # 例如通过服务注册中心、DNS-SD等方式
            
        except Exception as e:
            self.logger.error(f"Error discovering MCP services: {e}")
    
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
        services = self.service_registry.list_services()
        
        for service in services:
            try:
                start_time = time.time()
                
                # 调用健康检查端点
                success, response, error = await self.call_manager.make_call(
                    service=service,
                    method="health_check",
                    parameters={},
                    call_type=MCPCallType.SYNC,
                    timeout=10.0
                )
                
                response_time = time.time() - start_time
                
                # 更新服务状态
                if success:
                    service.status = MCPServiceStatus.AVAILABLE
                    service.response_time = response_time
                    service.error_count = max(0, service.error_count - 1)  # 逐渐减少错误计数
                else:
                    service.error_count += 1
                    if service.error_count >= 3:
                        service.status = MCPServiceStatus.UNAVAILABLE
                    else:
                        service.status = MCPServiceStatus.ERROR
                
                service.last_health_check = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Error checking health of service {service.service_id}: {e}")
                service.status = MCPServiceStatus.ERROR
                service.error_count += 1
    
    @event_handler(EventBusEventType.USER_INTERACTION)
    async def handle_user_intent_detected(self, event: EventBusEvent) -> None:
        """处理用户意图检测事件"""
        intent_data = event.data
        intent_type = intent_data.get("intent_type")
        
        # 根据意图类型调用相关的MCP服务
        if intent_type == "search":
            # 调用搜索服务
            search_services = self.service_registry.find_services_by_capability("search")
            for service in search_services:
                if service.status == MCPServiceStatus.AVAILABLE:
                    await self.call_mcp_service(
                        service_id=service.service_id,
                        method="search",
                        parameters={"query": intent_data.get("query", "")}
                    )
                    break
    
    @event_handler(EventBusEventType.DECISION_MADE)
    async def handle_decision_made(self, event: EventBusEvent) -> None:
        """处理决策事件"""
        decision_data = event.data
        decision_type = decision_data.get("decision_type")
        
        # 根据决策类型调用相关的MCP服务
        if decision_type == "data_fetch":
            # 调用数据获取服务
            data_services = self.service_registry.find_services_by_capability("data_provider")
            for service in data_services:
                if service.status == MCPServiceStatus.AVAILABLE:
                    await self.call_mcp_service(
                        service_id=service.service_id,
                        method="fetch_data",
                        parameters=decision_data.get("parameters", {})
                    )
                    break
    
    async def get_integration_statistics(self) -> Dict[str, Any]:
        """获取集成统计信息"""
        try:
            # 服务统计
            services = self.service_registry.list_services()
            service_stats = {
                "total_services": len(services),
                "available_services": len([s for s in services if s.status == MCPServiceStatus.AVAILABLE]),
                "unavailable_services": len([s for s in services if s.status == MCPServiceStatus.UNAVAILABLE]),
                "error_services": len([s for s in services if s.status == MCPServiceStatus.ERROR])
            }
            
            # 调用统计
            call_stats = self.call_manager.get_call_statistics()
            
            # 订阅统计
            subscription_stats = {
                "total_subscriptions": len(self.event_manager.subscriptions),
                "active_subscriptions": len([s for s in self.event_manager.subscriptions.values() if s.trigger_count > 0])
            }
            
            return {
                "service_statistics": service_stats,
                "call_statistics": call_stats,
                "subscription_statistics": subscription_stats,
                "cache_hit_rate": getattr(self.service_cache, "hit_rate", 0.0)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting integration statistics: {e}")
            return {}
    
    async def cleanup(self) -> Dict[str, int]:
        """清理资源"""
        cleanup_stats = {
            "cleared_cache_entries": 0,
            "cancelled_calls": 0,
            "removed_subscriptions": 0
        }
        
        try:
            # 清理缓存
            await self.service_cache.clear()
            await self.call_manager.call_cache.clear()
            cleanup_stats["cleared_cache_entries"] = 2
            
            # 取消活跃调用
            active_calls = len(self.call_manager.active_calls)
            self.call_manager.active_calls.clear()
            cleanup_stats["cancelled_calls"] = active_calls
            
            # 清理订阅
            subscription_count = len(self.event_manager.subscriptions)
            self.event_manager.subscriptions.clear()
            self.event_manager.service_subscriptions.clear()
            cleanup_stats["removed_subscriptions"] = subscription_count
            
            self.logger.info(f"MCP Integration cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error during MCP Integration cleanup: {e}")
            return cleanup_stats


# 导出主要类
MCPIntegration = SmartUIMCPIntegration  # 为了向后兼容
__all__ = ['SmartUIMCPIntegration', 'MCPIntegration']

