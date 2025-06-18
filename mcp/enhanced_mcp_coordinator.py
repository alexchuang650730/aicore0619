#!/usr/bin/env python3
"""
增强的MCP协调器 - 支持完整工作流通信

基于原有架构，增强MCPCoordinator的通信能力，支持：
1. SmartUI MCP的用户交互请求
2. Enhanced Workflow MCP的工作流处理
3. 所有六大工作流的统一管理
4. 端到端的通信路由和状态管理
"""

import asyncio
import json
import time
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# ============================================================================
# 1. 扩展的数据结构定义
# ============================================================================

class MCPType(Enum):
    """扩展的MCP类型枚举"""
    LOCAL_MODEL = "local_model_mcp"
    CLOUD_SEARCH = "cloud_search_mcp"
    CLOUD_EDGE_DATA = "cloud_edge_data_mcp"
    ENHANCED_WORKFLOW = "enhanced_workflow_mcp"
    SMARTUI = "smartui_mcp"
    REQUIREMENT_ANALYSIS = "requirement_analysis_mcp"
    CODE_GENERATION = "code_generation_mcp"
    TESTING = "testing_mcp"
    DOCUMENTATION = "documentation_mcp"
    DEPLOYMENT = "deployment_mcp"
    MONITORING = "monitoring_mcp"

class InteractionType(Enum):
    """扩展的交互类型枚举"""
    OCR_REQUEST = "ocr_request"
    MODEL_INFERENCE = "model_inference"
    DATA_PROCESSING = "data_processing"
    ROUTING_DECISION = "routing_decision"
    SYSTEM_MONITORING = "system_monitoring"
    USER_INPUT = "user_input"
    WORKFLOW_REQUEST = "workflow_request"
    WORKFLOW_EXECUTION = "workflow_execution"
    STATUS_QUERY = "status_query"
    CONFIGURATION_CHANGE = "configuration_change"

class RequestType(Enum):
    """请求类型枚举"""
    ROUTE_REQUEST = "route_request"
    DIRECT_CALL = "direct_call"
    BROADCAST = "broadcast"
    STATUS_CHECK = "status_check"
    HEALTH_CHECK = "health_check"

class ProcessingLocation(Enum):
    """处理位置"""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    HYBRID = "hybrid"

@dataclass
class MCPRequest:
    """MCP请求数据结构"""
    request_id: str
    request_type: RequestType
    source_mcp: str
    target_mcp: str
    request_data: Dict[str, Any]
    session_id: Optional[str] = None
    priority: int = 5  # 1-10, 10为最高优先级
    timeout: int = 30  # 超时时间（秒）
    retry_count: int = 0
    max_retries: int = 3
    created_time: str = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now().isoformat()

@dataclass
class MCPResponse:
    """MCP响应数据结构"""
    request_id: str
    response_id: str
    source_mcp: str
    target_mcp: str
    status: str  # success, error, timeout, retry
    response_data: Dict[str, Any]
    error_message: Optional[str] = None
    processing_time: float = 0.0
    created_time: str = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now().isoformat()

@dataclass
class WorkflowSession:
    """工作流会话数据结构"""
    session_id: str
    user_id: str
    workflow_type: str
    workflow_id: Optional[str] = None
    status: str = "active"  # active, paused, completed, failed
    created_time: str = None
    last_activity: str = None
    context: Dict[str, Any] = None
    interaction_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now().isoformat()
        if self.last_activity is None:
            self.last_activity = datetime.now().isoformat()
        if self.context is None:
            self.context = {}
        if self.interaction_history is None:
            self.interaction_history = []

# ============================================================================
# 2. MCP注册管理器
# ============================================================================

class MCPRegistry:
    """MCP注册管理器"""
    
    def __init__(self):
        self.registered_mcps: Dict[str, Dict[str, Any]] = {}
        self.mcp_instances: Dict[str, Any] = {}
        self.mcp_status: Dict[str, str] = {}
        self.logger = logging.getLogger("MCPRegistry")
    
    async def register_mcp(self, mcp_name: str, mcp_instance: Any, 
                          capabilities: List[str] = None) -> bool:
        """注册MCP实例"""
        try:
            # 获取MCP信息
            mcp_info = mcp_instance.get_info() if hasattr(mcp_instance, 'get_info') else {}
            
            self.registered_mcps[mcp_name] = {
                "name": mcp_name,
                "instance": mcp_instance,
                "capabilities": capabilities or mcp_info.get("capabilities", []),
                "version": mcp_info.get("version", "unknown"),
                "description": mcp_info.get("description", ""),
                "registered_time": datetime.now().isoformat()
            }
            
            self.mcp_instances[mcp_name] = mcp_instance
            self.mcp_status[mcp_name] = "registered"
            
            # 初始化MCP
            if hasattr(mcp_instance, 'initialize'):
                await mcp_instance.initialize()
                self.mcp_status[mcp_name] = "active"
            
            self.logger.info(f"MCP注册成功: {mcp_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"MCP注册失败 {mcp_name}: {e}")
            self.mcp_status[mcp_name] = "error"
            return False
    
    def get_mcp_instance(self, mcp_name: str) -> Optional[Any]:
        """获取MCP实例"""
        return self.mcp_instances.get(mcp_name)
    
    def get_mcp_status(self, mcp_name: str) -> str:
        """获取MCP状态"""
        return self.mcp_status.get(mcp_name, "unknown")
    
    def list_mcps(self) -> Dict[str, Dict[str, Any]]:
        """列出所有注册的MCP"""
        return self.registered_mcps.copy()
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """对所有MCP进行健康检查"""
        health_status = {}
        
        for mcp_name, mcp_instance in self.mcp_instances.items():
            try:
                if hasattr(mcp_instance, 'get_status'):
                    status = await mcp_instance.get_status()
                    health_status[mcp_name] = {
                        "status": "healthy",
                        "details": status
                    }
                else:
                    health_status[mcp_name] = {
                        "status": "unknown",
                        "details": {"message": "No status method available"}
                    }
            except Exception as e:
                health_status[mcp_name] = {
                    "status": "unhealthy",
                    "details": {"error": str(e)}
                }
                self.mcp_status[mcp_name] = "error"
        
        return health_status

# ============================================================================
# 3. 增强的MCP协调器
# ============================================================================

class EnhancedMCPCoordinator:
    """
    增强的MCP协调器
    
    支持完整的工作流通信和管理功能
    """
    
    def __init__(self, base_dir: str = "/opt/powerautomation/coordinator_data"):
        self.base_dir = Path(base_dir)
        self.setup_directory_structure()
        
        # 核心组件
        self.mcp_registry = MCPRegistry()
        self.request_queue = asyncio.Queue()
        self.response_cache: Dict[str, MCPResponse] = {}
        self.workflow_sessions: Dict[str, WorkflowSession] = {}
        
        # 统计和监控
        self.request_count = 0
        self.response_count = 0
        self.error_count = 0
        self.performance_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "active_sessions": 0,
            "active_workflows": 0
        }
        
        # 配置
        self.config = {
            "max_concurrent_requests": 10,
            "default_timeout": 30,
            "cache_ttl": 300,  # 5分钟
            "session_timeout": 3600,  # 1小时
            "enable_logging": True,
            "enable_metrics": True
        }
        
        self.logger = logging.getLogger("EnhancedMCPCoordinator")
        self.running = False
        
    def setup_directory_structure(self):
        """设置目录结构"""
        directories = [
            "requests",
            "responses", 
            "sessions",
            "workflows",
            "logs",
            "metrics",
            "cache"
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
    
    async def start(self):
        """启动协调器"""
        self.running = True
        self.logger.info("Enhanced MCP Coordinator 启动")
        
        # 启动请求处理任务
        asyncio.create_task(self._process_requests())
        asyncio.create_task(self._cleanup_expired_sessions())
        asyncio.create_task(self._performance_monitoring())
    
    async def stop(self):
        """停止协调器"""
        self.running = False
        self.logger.info("Enhanced MCP Coordinator 停止")
    
    async def register_mcp(self, mcp_name: str, mcp_instance: Any, 
                          capabilities: List[str] = None) -> bool:
        """注册MCP"""
        return await self.mcp_registry.register_mcp(mcp_name, mcp_instance, capabilities)
    
    async def route_request(self, request: MCPRequest) -> MCPResponse:
        """路由请求到目标MCP"""
        start_time = time.time()
        
        try:
            self.request_count += 1
            self.performance_stats["total_requests"] += 1
            
            # 验证目标MCP
            target_mcp = self.mcp_registry.get_mcp_instance(request.target_mcp)
            if not target_mcp:
                return MCPResponse(
                    request_id=request.request_id,
                    response_id=str(uuid.uuid4()),
                    source_mcp=request.target_mcp,
                    target_mcp=request.source_mcp,
                    status="error",
                    response_data={},
                    error_message=f"Target MCP not found: {request.target_mcp}"
                )
            
            # 处理请求
            if hasattr(target_mcp, 'process'):
                response_data = await target_mcp.process(request.request_data)
            else:
                response_data = {"error": "MCP does not support process method"}
            
            # 创建响应
            response = MCPResponse(
                request_id=request.request_id,
                response_id=str(uuid.uuid4()),
                source_mcp=request.target_mcp,
                target_mcp=request.source_mcp,
                status="success",
                response_data=response_data,
                processing_time=time.time() - start_time
            )
            
            self.response_count += 1
            self.performance_stats["successful_requests"] += 1
            
            # 更新性能统计
            self._update_performance_stats(response.processing_time)
            
            # 缓存响应
            self.response_cache[response.response_id] = response
            
            # 记录会话信息
            if request.session_id:
                await self._update_session(request.session_id, request, response)
            
            return response
            
        except Exception as e:
            self.error_count += 1
            self.performance_stats["failed_requests"] += 1
            
            error_response = MCPResponse(
                request_id=request.request_id,
                response_id=str(uuid.uuid4()),
                source_mcp=request.target_mcp,
                target_mcp=request.source_mcp,
                status="error",
                response_data={},
                error_message=str(e),
                processing_time=time.time() - start_time
            )
            
            self.logger.error(f"请求处理失败: {e}")
            return error_response
    
    async def handle_smartui_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理来自SmartUI MCP的请求"""
        try:
            request_type = request_data.get("type", "route_request")
            
            if request_type == "route_request":
                # 创建路由请求
                mcp_request = MCPRequest(
                    request_id=str(uuid.uuid4()),
                    request_type=RequestType.ROUTE_REQUEST,
                    source_mcp=request_data.get("source_mcp", "smartui_mcp"),
                    target_mcp=request_data.get("target_mcp", "enhanced_workflow_mcp"),
                    request_data=request_data.get("request_data", {}),
                    session_id=request_data.get("session_id")
                )
                
                # 路由请求
                response = await self.route_request(mcp_request)
                
                return {
                    "status": response.status,
                    "request_id": response.request_id,
                    "response_id": response.response_id,
                    "data": response.response_data,
                    "error": response.error_message,
                    "processing_time": response.processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            
            elif request_type == "create_workflow_session":
                # 创建工作流会话
                session_id = request_data.get("session_id", str(uuid.uuid4()))
                user_id = request_data.get("user_id", "anonymous")
                workflow_type = request_data.get("workflow_type", "general")
                
                session = WorkflowSession(
                    session_id=session_id,
                    user_id=user_id,
                    workflow_type=workflow_type
                )
                
                self.workflow_sessions[session_id] = session
                self.performance_stats["active_sessions"] = len(self.workflow_sessions)
                
                return {
                    "status": "success",
                    "session_id": session_id,
                    "workflow_type": workflow_type,
                    "timestamp": datetime.now().isoformat()
                }
            
            elif request_type == "get_session_status":
                # 获取会话状态
                session_id = request_data.get("session_id")
                if session_id and session_id in self.workflow_sessions:
                    session = self.workflow_sessions[session_id]
                    return {
                        "status": "success",
                        "session_data": asdict(session),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "error",
                        "error": "Session not found",
                        "timestamp": datetime.now().isoformat()
                    }
            
            elif request_type == "health_check":
                # 健康检查
                health_status = await self.mcp_registry.health_check_all()
                return {
                    "status": "success",
                    "health_status": health_status,
                    "coordinator_stats": self.performance_stats,
                    "timestamp": datetime.now().isoformat()
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown request type: {request_type}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"SmartUI请求处理失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_requests(self):
        """处理请求队列"""
        while self.running:
            try:
                # 这里可以实现更复杂的请求队列处理逻辑
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"请求处理循环错误: {e}")
    
    async def _cleanup_expired_sessions(self):
        """清理过期会话"""
        while self.running:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.workflow_sessions.items():
                    session_time = datetime.fromisoformat(session.last_activity)
                    if (current_time - session_time).total_seconds() > self.config["session_timeout"]:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.workflow_sessions[session_id]
                    self.logger.info(f"清理过期会话: {session_id}")
                
                self.performance_stats["active_sessions"] = len(self.workflow_sessions)
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                self.logger.error(f"会话清理错误: {e}")
    
    async def _performance_monitoring(self):
        """性能监控"""
        while self.running:
            try:
                # 记录性能指标
                if self.config["enable_metrics"]:
                    metrics_file = self.base_dir / "metrics" / f"metrics_{datetime.now().strftime('%Y%m%d_%H')}.json"
                    with open(metrics_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "timestamp": datetime.now().isoformat(),
                            "performance_stats": self.performance_stats,
                            "mcp_status": self.mcp_registry.mcp_status,
                            "active_sessions": len(self.workflow_sessions)
                        }, f, indent=2, ensure_ascii=False)
                
                await asyncio.sleep(300)  # 每5分钟记录一次
                
            except Exception as e:
                self.logger.error(f"性能监控错误: {e}")
    
    async def _update_session(self, session_id: str, request: MCPRequest, response: MCPResponse):
        """更新会话信息"""
        if session_id in self.workflow_sessions:
            session = self.workflow_sessions[session_id]
            session.last_activity = datetime.now().isoformat()
            session.interaction_history.append({
                "request_id": request.request_id,
                "response_id": response.response_id,
                "target_mcp": request.target_mcp,
                "status": response.status,
                "timestamp": response.created_time
            })
    
    def _update_performance_stats(self, processing_time: float):
        """更新性能统计"""
        total_requests = self.performance_stats["successful_requests"]
        current_avg = self.performance_stats["average_response_time"]
        new_avg = (current_avg * (total_requests - 1) + processing_time) / total_requests
        self.performance_stats["average_response_time"] = new_avg
    
    async def get_status(self) -> Dict[str, Any]:
        """获取协调器状态"""
        return {
            "coordinator_status": "running" if self.running else "stopped",
            "registered_mcps": len(self.mcp_registry.registered_mcps),
            "active_sessions": len(self.workflow_sessions),
            "performance_stats": self.performance_stats,
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_info(self) -> Dict[str, Any]:
        """获取协调器信息"""
        return {
            "name": "EnhancedMCPCoordinator",
            "version": "2.0.0",
            "description": "Enhanced MCP Coordinator with workflow communication support",
            "capabilities": [
                "mcp_registration", "request_routing", "session_management",
                "workflow_coordination", "performance_monitoring", "health_checking"
            ],
            "supported_request_types": [rt.value for rt in RequestType],
            "supported_mcp_types": [mt.value for mt in MCPType]
        }

# ============================================================================
# 4. 全局协调器实例
# ============================================================================

# 创建全局协调器实例
coordinator = EnhancedMCPCoordinator()

async def get_coordinator() -> EnhancedMCPCoordinator:
    """获取协调器实例"""
    return coordinator

async def start_coordinator():
    """启动协调器"""
    await coordinator.start()

async def stop_coordinator():
    """停止协调器"""
    await coordinator.stop()

if __name__ == "__main__":
    # 测试代码
    async def test_coordinator():
        await start_coordinator()
        
        # 模拟注册MCP
        class MockMCP:
            def get_info(self):
                return {"capabilities": ["test"], "version": "1.0.0"}
            
            async def initialize(self):
                return True
            
            async def process(self, data):
                return {"result": "mock_processed", "data": data}
        
        await coordinator.register_mcp("test_mcp", MockMCP())
        
        # 测试请求路由
        request = MCPRequest(
            request_id="test_001",
            request_type=RequestType.ROUTE_REQUEST,
            source_mcp="smartui_mcp",
            target_mcp="test_mcp",
            request_data={"test": "data"}
        )
        
        response = await coordinator.route_request(request)
        print(f"Response: {response}")
        
        await stop_coordinator()
    
    asyncio.run(test_coordinator())

