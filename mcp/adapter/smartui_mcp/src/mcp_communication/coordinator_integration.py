"""
SmartUI MCP 协调器集成模块

这个模块实现了SmartUI MCP与上层架构的集成接口，支持三层架构：
- coding_plugin_orchestrator (产品级)
- workflow orchestrator (工作流级)  
- mcp/adapter组件 (组件级)

作者: Manus AI
版本: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from ..common.interfaces import (
    IEventBus,
    IConfigurationManager
)
from ..common.event_bus import EventBus, EventBusEventType
from ..common.communication import ComponentMessage, MessageType, MessagePriority


class OrchestrationLevel(Enum):
    """编排层级枚举"""
    PRODUCT = "product"          # 产品级 - coding_plugin_orchestrator
    WORKFLOW = "workflow"        # 工作流级 - workflow orchestrator
    COMPONENT = "component"      # 组件级 - mcp/adapter


class ComponentCapability(Enum):
    """组件能力枚举"""
    UI_GENERATION = "ui_generation"
    USER_ANALYSIS = "user_analysis"
    INTELLIGENT_ADAPTATION = "intelligent_adaptation"
    THEME_MANAGEMENT = "theme_management"
    LAYOUT_OPTIMIZATION = "layout_optimization"
    COMPONENT_RENDERING = "component_rendering"
    EVENT_HANDLING = "event_handling"
    STATE_MANAGEMENT = "state_management"
    ACCESSIBILITY_SUPPORT = "accessibility_support"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


@dataclass
class ComponentRegistration:
    """组件注册信息"""
    component_id: str
    component_name: str
    component_version: str
    capabilities: List[ComponentCapability]
    endpoints: Dict[str, str]
    health_check_url: str
    metadata: Dict[str, Any]
    registration_time: datetime


@dataclass
class OrchestrationRequest:
    """编排请求数据结构"""
    request_id: str
    source_level: OrchestrationLevel
    source_component: str
    target_capability: ComponentCapability
    request_type: str
    parameters: Dict[str, Any]
    priority: MessagePriority
    timeout: Optional[int] = None
    callback_url: Optional[str] = None


@dataclass
class OrchestrationResponse:
    """编排响应数据结构"""
    request_id: str
    success: bool
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    execution_time: float
    metadata: Dict[str, Any]


class CoordinatorIntegration:
    """
    协调器集成类
    
    负责SmartUI MCP与上层编排系统的集成，提供标准化的组件级接口
    """
    
    def __init__(
        self,
        component_id: str,
        event_bus: IEventBus,
        config_manager: IConfigurationManager,
        logger: Optional[logging.Logger] = None
    ):
        self.component_id = component_id
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # 组件状态
        self.is_registered = False
        self.registration_info: Optional[ComponentRegistration] = None
        self.active_requests: Dict[str, OrchestrationRequest] = {}
        
        # 能力处理器映射
        self.capability_handlers: Dict[ComponentCapability, Callable] = {}
        
        # 上层编排器连接信息
        self.orchestrator_connections: Dict[OrchestrationLevel, Dict[str, Any]] = {}
        
        # 初始化事件监听
        self._setup_event_listeners()
        
        self.logger.info(f"CoordinatorIntegration initialized for component: {component_id}")
    
    def _setup_event_listeners(self):
        """设置事件监听器"""
        # 监听组件状态变化
        self.event_bus.subscribe(
            EventType.COMPONENT_STATUS_CHANGED,
            self._handle_component_status_change
        )
        
        # 监听编排请求
        self.event_bus.subscribe(
            EventType.ORCHESTRATION_REQUEST,
            self._handle_orchestration_request
        )
        
        # 监听健康检查请求
        self.event_bus.subscribe(
            EventType.HEALTH_CHECK_REQUEST,
            self._handle_health_check
        )
    
    async def register_component(
        self,
        component_name: str,
        component_version: str,
        capabilities: List[ComponentCapability],
        endpoints: Dict[str, str],
        health_check_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        注册组件到协调器
        
        Args:
            component_name: 组件名称
            component_version: 组件版本
            capabilities: 组件能力列表
            endpoints: 端点映射
            health_check_url: 健康检查URL
            metadata: 额外元数据
            
        Returns:
            bool: 注册是否成功
        """
        try:
            self.registration_info = ComponentRegistration(
                component_id=self.component_id,
                component_name=component_name,
                component_version=component_version,
                capabilities=capabilities,
                endpoints=endpoints,
                health_check_url=health_check_url,
                metadata=metadata or {},
                registration_time=datetime.now()
            )
            
            # 发送注册请求到各级编排器
            registration_success = await self._send_registration_to_orchestrators()
            
            if registration_success:
                self.is_registered = True
                self.logger.info(f"Component {component_name} registered successfully")
                
                # 发布注册成功事件
                await self.event_bus.publish(
                    EventType.COMPONENT_REGISTERED,
                    {
                        "component_id": self.component_id,
                        "registration_info": asdict(self.registration_info)
                    }
                )
            
            return registration_success
            
        except Exception as e:
            self.logger.error(f"Failed to register component: {e}")
            return False
    
    async def _send_registration_to_orchestrators(self) -> bool:
        """向各级编排器发送注册请求"""
        try:
            # 获取编排器配置
            orchestrator_config = self.config_manager.get_config("orchestrators", {})
            
            registration_tasks = []
            
            # 向产品级编排器注册
            if "product_orchestrator" in orchestrator_config:
                task = self._register_to_orchestrator(
                    OrchestrationLevel.PRODUCT,
                    orchestrator_config["product_orchestrator"]
                )
                registration_tasks.append(task)
            
            # 向工作流级编排器注册
            if "workflow_orchestrator" in orchestrator_config:
                task = self._register_to_orchestrator(
                    OrchestrationLevel.WORKFLOW,
                    orchestrator_config["workflow_orchestrator"]
                )
                registration_tasks.append(task)
            
            # 等待所有注册完成
            results = await asyncio.gather(*registration_tasks, return_exceptions=True)
            
            # 检查注册结果
            success_count = sum(1 for result in results if result is True)
            total_count = len(results)
            
            self.logger.info(f"Registration results: {success_count}/{total_count} successful")
            
            return success_count > 0  # 至少一个编排器注册成功
            
        except Exception as e:
            self.logger.error(f"Failed to send registration to orchestrators: {e}")
            return False
    
    async def _register_to_orchestrator(
        self,
        level: OrchestrationLevel,
        config: Dict[str, Any]
    ) -> bool:
        """向特定编排器注册"""
        try:
            # 构建注册消息
            registration_message = MCPMessage(
                message_type=MessageType.REQUEST,
                source=self.component_id,
                target=config.get("component_id", f"{level.value}_orchestrator"),
                action="register_component",
                data=asdict(self.registration_info),
                priority=MessagePriority.HIGH
            )
            
            # 发送注册消息
            response = await self._send_message_to_orchestrator(level, registration_message)
            
            if response and response.get("success"):
                # 保存连接信息
                self.orchestrator_connections[level] = {
                    "config": config,
                    "last_contact": datetime.now(),
                    "status": "connected"
                }
                
                self.logger.info(f"Successfully registered to {level.value} orchestrator")
                return True
            else:
                self.logger.warning(f"Failed to register to {level.value} orchestrator")
                return False
                
        except Exception as e:
            self.logger.error(f"Error registering to {level.value} orchestrator: {e}")
            return False
    
    async def _send_message_to_orchestrator(
        self,
        level: OrchestrationLevel,
        message: MCPMessage
    ) -> Optional[Dict[str, Any]]:
        """向编排器发送消息"""
        try:
            # 这里应该实现实际的网络通信
            # 目前使用事件总线模拟
            response_event = await self.event_bus.publish_and_wait(
                EventType.ORCHESTRATOR_MESSAGE,
                {
                    "level": level.value,
                    "message": asdict(message)
                },
                timeout=30.0
            )
            
            return response_event.data if response_event else None
            
        except Exception as e:
            self.logger.error(f"Failed to send message to {level.value} orchestrator: {e}")
            return None
    
    def register_capability_handler(
        self,
        capability: ComponentCapability,
        handler: Callable
    ):
        """
        注册能力处理器
        
        Args:
            capability: 组件能力
            handler: 处理函数
        """
        self.capability_handlers[capability] = handler
        self.logger.info(f"Registered handler for capability: {capability.value}")
    
    async def _handle_orchestration_request(self, event_data: Dict[str, Any]):
        """处理编排请求"""
        try:
            request = OrchestrationRequest(**event_data)
            self.active_requests[request.request_id] = request
            
            self.logger.info(f"Received orchestration request: {request.request_id}")
            
            # 检查是否有对应的能力处理器
            if request.target_capability not in self.capability_handlers:
                await self._send_orchestration_response(
                    request.request_id,
                    False,
                    None,
                    f"Capability {request.target_capability.value} not supported"
                )
                return
            
            # 执行能力处理器
            start_time = datetime.now()
            try:
                handler = self.capability_handlers[request.target_capability]
                result = await handler(request.parameters)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                await self._send_orchestration_response(
                    request.request_id,
                    True,
                    result,
                    None,
                    execution_time
                )
                
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                await self._send_orchestration_response(
                    request.request_id,
                    False,
                    None,
                    str(e),
                    execution_time
                )
            
            # 清理请求记录
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]
                
        except Exception as e:
            self.logger.error(f"Error handling orchestration request: {e}")
    
    async def _send_orchestration_response(
        self,
        request_id: str,
        success: bool,
        result: Optional[Dict[str, Any]],
        error_message: Optional[str],
        execution_time: float = 0.0
    ):
        """发送编排响应"""
        try:
            response = OrchestrationResponse(
                request_id=request_id,
                success=success,
                result=result,
                error_message=error_message,
                execution_time=execution_time,
                metadata={
                    "component_id": self.component_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # 发布响应事件
            await self.event_bus.publish(
                EventType.ORCHESTRATION_RESPONSE,
                asdict(response)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send orchestration response: {e}")
    
    async def _handle_component_status_change(self, event_data: Dict[str, Any]):
        """处理组件状态变化"""
        try:
            # 向编排器报告状态变化
            status_message = MCPMessage(
                message_type=MessageType.NOTIFICATION,
                source=self.component_id,
                target="orchestrators",
                action="status_update",
                data=event_data,
                priority=MessagePriority.NORMAL
            )
            
            # 向所有连接的编排器发送状态更新
            for level in self.orchestrator_connections:
                await self._send_message_to_orchestrator(level, status_message)
                
        except Exception as e:
            self.logger.error(f"Error handling component status change: {e}")
    
    async def _handle_health_check(self, event_data: Dict[str, Any]):
        """处理健康检查请求"""
        try:
            health_status = {
                "component_id": self.component_id,
                "status": "healthy" if self.is_registered else "unhealthy",
                "registration_status": self.is_registered,
                "active_requests": len(self.active_requests),
                "orchestrator_connections": len(self.orchestrator_connections),
                "capabilities": [cap.value for cap in self.capability_handlers.keys()],
                "timestamp": datetime.now().isoformat()
            }
            
            # 发布健康状态
            await self.event_bus.publish(
                EventType.HEALTH_CHECK_RESPONSE,
                health_status
            )
            
        except Exception as e:
            self.logger.error(f"Error handling health check: {e}")
    
    async def request_orchestration(
        self,
        target_level: OrchestrationLevel,
        target_component: str,
        capability: ComponentCapability,
        request_type: str,
        parameters: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        timeout: Optional[int] = None
    ) -> Optional[OrchestrationResponse]:
        """
        向上层编排器发送请求
        
        Args:
            target_level: 目标编排层级
            target_component: 目标组件
            capability: 请求的能力
            request_type: 请求类型
            parameters: 请求参数
            priority: 消息优先级
            timeout: 超时时间
            
        Returns:
            OrchestrationResponse: 编排响应
        """
        try:
            request_id = f"{self.component_id}_{datetime.now().timestamp()}"
            
            request = OrchestrationRequest(
                request_id=request_id,
                source_level=OrchestrationLevel.COMPONENT,
                source_component=self.component_id,
                target_capability=capability,
                request_type=request_type,
                parameters=parameters,
                priority=priority,
                timeout=timeout
            )
            
            # 发送请求消息
            request_message = MCPMessage(
                message_type=MessageType.REQUEST,
                source=self.component_id,
                target=target_component,
                action="orchestration_request",
                data=asdict(request),
                priority=priority
            )
            
            response_data = await self._send_message_to_orchestrator(
                target_level,
                request_message
            )
            
            if response_data:
                return OrchestrationResponse(**response_data)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error requesting orchestration: {e}")
            return None
    
    async def unregister_component(self) -> bool:
        """注销组件"""
        try:
            if not self.is_registered:
                return True
            
            # 向所有编排器发送注销请求
            unregister_tasks = []
            for level in self.orchestrator_connections:
                task = self._unregister_from_orchestrator(level)
                unregister_tasks.append(task)
            
            await asyncio.gather(*unregister_tasks, return_exceptions=True)
            
            # 清理状态
            self.is_registered = False
            self.registration_info = None
            self.orchestrator_connections.clear()
            self.active_requests.clear()
            
            self.logger.info("Component unregistered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister component: {e}")
            return False
    
    async def _unregister_from_orchestrator(self, level: OrchestrationLevel):
        """从特定编排器注销"""
        try:
            unregister_message = MCPMessage(
                message_type=MessageType.REQUEST,
                source=self.component_id,
                target=f"{level.value}_orchestrator",
                action="unregister_component",
                data={"component_id": self.component_id},
                priority=MessagePriority.HIGH
            )
            
            await self._send_message_to_orchestrator(level, unregister_message)
            
        except Exception as e:
            self.logger.error(f"Error unregistering from {level.value} orchestrator: {e}")
    
    def get_registration_info(self) -> Optional[ComponentRegistration]:
        """获取注册信息"""
        return self.registration_info
    
    def get_orchestrator_connections(self) -> Dict[OrchestrationLevel, Dict[str, Any]]:
        """获取编排器连接信息"""
        return self.orchestrator_connections.copy()
    
    def get_active_requests(self) -> Dict[str, OrchestrationRequest]:
        """获取活跃请求"""
        return self.active_requests.copy()

