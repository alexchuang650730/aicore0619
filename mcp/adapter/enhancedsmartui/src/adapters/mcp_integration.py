#!/usr/bin/env python3
"""
SmartUI Enhanced - MCP协作管理器和Workflow驱动器
实现与其他MCP的深度集成，协调多MCP协作任务，以及基于workflow需求的界面驱动
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import requests
import websockets
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class MCPStatus(Enum):
    """MCP状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class CollaborationType(Enum):
    """协作类型"""
    DATA_EXCHANGE = "data_exchange"
    WORKFLOW_CHAIN = "workflow_chain"
    PARALLEL_PROCESSING = "parallel_processing"
    EVENT_DRIVEN = "event_driven"
    REAL_TIME_SYNC = "real_time_sync"

class WorkflowStage(Enum):
    """工作流阶段"""
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    COMPLETION = "completion"
    ERROR_HANDLING = "error_handling"

@dataclass
class MCPInfo:
    """MCP信息"""
    mcp_id: str
    name: str
    endpoint: str
    capabilities: List[str]
    status: MCPStatus
    last_heartbeat: datetime
    response_time: float
    error_count: int
    metadata: Dict[str, Any]

@dataclass
class CollaborationSession:
    """协作会话"""
    session_id: str
    collaboration_type: CollaborationType
    participating_mcps: List[str]
    initiator_mcp: str
    created_at: datetime
    status: str
    shared_context: Dict[str, Any]
    communication_log: List[Dict[str, Any]]
    expected_duration: Optional[int] = None
    actual_duration: Optional[int] = None

@dataclass
class WorkflowDefinition:
    """工作流定义"""
    workflow_id: str
    name: str
    description: str
    stages: List[Dict[str, Any]]
    required_mcps: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    ui_requirements: Dict[str, Any]
    triggers: List[Dict[str, Any]]

@dataclass
class WorkflowExecution:
    """工作流执行"""
    execution_id: str
    workflow_id: str
    stage: WorkflowStage
    current_step: int
    total_steps: int
    started_at: datetime
    context: Dict[str, Any]
    results: Dict[str, Any]
    errors: List[Dict[str, Any]]
    ui_state: Dict[str, Any]

class MCPCoordinatorClient:
    """MCP协调器客户端"""
    
    def __init__(self, coordinator_url: str = "http://localhost:8089"):
        self.coordinator_url = coordinator_url
        self.session = requests.Session()
        self.timeout = 30
        self.retry_count = 3
    
    async def register_mcp(self, mcp_info: MCPInfo) -> bool:
        """注册MCP到协调器"""
        try:
            registration_data = {
                "mcp_id": mcp_info.mcp_id,
                "name": mcp_info.name,
                "endpoint": mcp_info.endpoint,
                "capabilities": mcp_info.capabilities,
                "metadata": mcp_info.metadata
            }
            
            response = self.session.post(
                f"{self.coordinator_url}/api/mcps/register",
                json=registration_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"MCP注册成功: {mcp_info.mcp_id}")
                return True
            else:
                logger.error(f"MCP注册失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"MCP注册异常: {e}")
            return False
    
    async def discover_mcps(self, capabilities: List[str] = None) -> List[MCPInfo]:
        """发现可用的MCP"""
        try:
            params = {}
            if capabilities:
                params["capabilities"] = ",".join(capabilities)
            
            response = self.session.get(
                f"{self.coordinator_url}/api/mcps",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                mcps_data = response.json()
                mcps = []
                
                for mcp_data in mcps_data.get("mcps", []):
                    mcp_info = MCPInfo(
                        mcp_id=mcp_data["mcp_id"],
                        name=mcp_data["name"],
                        endpoint=mcp_data["endpoint"],
                        capabilities=mcp_data["capabilities"],
                        status=MCPStatus(mcp_data.get("status", "offline")),
                        last_heartbeat=datetime.fromisoformat(mcp_data.get("last_heartbeat", datetime.now().isoformat())),
                        response_time=mcp_data.get("response_time", 0.0),
                        error_count=mcp_data.get("error_count", 0),
                        metadata=mcp_data.get("metadata", {})
                    )
                    mcps.append(mcp_info)
                
                return mcps
            else:
                logger.error(f"MCP发现失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"MCP发现异常: {e}")
            return []
    
    async def call_mcp(self, mcp_id: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP方法"""
        try:
            call_data = {
                "method": method,
                "params": params,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.coordinator_url}/api/mcps/{mcp_id}/call",
                json=call_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"MCP调用失败: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"MCP调用异常: {e}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    async def get_mcp_status(self, mcp_id: str) -> Optional[MCPInfo]:
        """获取MCP状态"""
        try:
            response = self.session.get(
                f"{self.coordinator_url}/api/mcps/{mcp_id}/status",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                mcp_data = response.json()
                return MCPInfo(
                    mcp_id=mcp_data["mcp_id"],
                    name=mcp_data["name"],
                    endpoint=mcp_data["endpoint"],
                    capabilities=mcp_data["capabilities"],
                    status=MCPStatus(mcp_data["status"]),
                    last_heartbeat=datetime.fromisoformat(mcp_data["last_heartbeat"]),
                    response_time=mcp_data["response_time"],
                    error_count=mcp_data["error_count"],
                    metadata=mcp_data["metadata"]
                )
            else:
                return None
                
        except Exception as e:
            logger.error(f"获取MCP状态异常: {e}")
            return None

class MCPCollaborator:
    """MCP协作管理器"""
    
    def __init__(self, coordinator_client: MCPCoordinatorClient):
        self.coordinator = coordinator_client
        self.active_collaborations: Dict[str, CollaborationSession] = {}
        self.mcp_capabilities: Dict[str, List[str]] = {}
        self.collaboration_patterns: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._setup_collaboration_patterns()
    
    def _setup_collaboration_patterns(self):
        """设置协作模式"""
        
        # 数据交换模式
        self.collaboration_patterns["data_exchange"] = {
            "description": "MCP之间的数据交换",
            "steps": [
                {"action": "request_data", "timeout": 30},
                {"action": "process_data", "timeout": 60},
                {"action": "return_result", "timeout": 30}
            ],
            "error_handling": "retry_with_fallback",
            "max_participants": 5
        }
        
        # 工作流链模式
        self.collaboration_patterns["workflow_chain"] = {
            "description": "顺序执行的工作流链",
            "steps": [
                {"action": "validate_input", "timeout": 10},
                {"action": "execute_stage", "timeout": 120},
                {"action": "validate_output", "timeout": 10},
                {"action": "pass_to_next", "timeout": 5}
            ],
            "error_handling": "rollback_and_retry",
            "max_participants": 10
        }
        
        # 并行处理模式
        self.collaboration_patterns["parallel_processing"] = {
            "description": "并行处理任务",
            "steps": [
                {"action": "distribute_tasks", "timeout": 15},
                {"action": "parallel_execute", "timeout": 180},
                {"action": "collect_results", "timeout": 30},
                {"action": "merge_outputs", "timeout": 60}
            ],
            "error_handling": "partial_failure_tolerance",
            "max_participants": 20
        }
    
    async def initiate_collaboration(self, collaboration_type: CollaborationType,
                                   required_capabilities: List[str],
                                   context: Dict[str, Any]) -> str:
        """发起MCP协作"""
        try:
            # 1. 发现符合条件的MCP
            available_mcps = await self.coordinator.discover_mcps(required_capabilities)
            
            if not available_mcps:
                raise ValueError(f"未找到具备所需能力的MCP: {required_capabilities}")
            
            # 2. 选择最优MCP组合
            selected_mcps = await self._select_optimal_mcps(
                available_mcps, collaboration_type, required_capabilities
            )
            
            # 3. 创建协作会话
            session_id = f"collab_{int(time.time())}_{len(self.active_collaborations)}"
            
            collaboration_session = CollaborationSession(
                session_id=session_id,
                collaboration_type=collaboration_type,
                participating_mcps=[mcp.mcp_id for mcp in selected_mcps],
                initiator_mcp="smartui_enhanced",
                created_at=datetime.now(),
                status="initializing",
                shared_context=context,
                communication_log=[]
            )
            
            self.active_collaborations[session_id] = collaboration_session
            
            # 4. 通知参与的MCP
            await self._notify_collaboration_start(collaboration_session, selected_mcps)
            
            logger.info(f"协作会话已创建: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"发起协作失败: {e}")
            raise
    
    async def _select_optimal_mcps(self, available_mcps: List[MCPInfo],
                                 collaboration_type: CollaborationType,
                                 required_capabilities: List[str]) -> List[MCPInfo]:
        """选择最优MCP组合"""
        # 按响应时间和错误率排序
        scored_mcps = []
        
        for mcp in available_mcps:
            # 计算MCP评分
            score = 100.0  # 基础分数
            
            # 响应时间评分 (越低越好)
            if mcp.response_time > 0:
                score -= min(mcp.response_time / 100, 50)  # 最多扣50分
            
            # 错误率评分 (越低越好)
            score -= min(mcp.error_count * 5, 30)  # 最多扣30分
            
            # 状态评分
            if mcp.status == MCPStatus.ONLINE:
                score += 10
            elif mcp.status == MCPStatus.BUSY:
                score -= 20
            elif mcp.status == MCPStatus.ERROR:
                score -= 50
            
            # 能力匹配评分
            matched_capabilities = set(mcp.capabilities) & set(required_capabilities)
            capability_score = (len(matched_capabilities) / len(required_capabilities)) * 20
            score += capability_score
            
            scored_mcps.append((mcp, score))
        
        # 按分数排序并选择最优的
        scored_mcps.sort(key=lambda x: x[1], reverse=True)
        
        # 根据协作类型选择MCP数量
        pattern = self.collaboration_patterns.get(collaboration_type.value, {})
        max_participants = pattern.get("max_participants", 5)
        
        selected_count = min(len(scored_mcps), max_participants)
        return [mcp for mcp, score in scored_mcps[:selected_count]]
    
    async def _notify_collaboration_start(self, session: CollaborationSession,
                                        mcps: List[MCPInfo]):
        """通知MCP协作开始"""
        notification_data = {
            "session_id": session.session_id,
            "collaboration_type": session.collaboration_type.value,
            "participants": session.participating_mcps,
            "shared_context": session.shared_context,
            "expected_duration": session.expected_duration
        }
        
        for mcp in mcps:
            try:
                await self.coordinator.call_mcp(
                    mcp.mcp_id,
                    "collaboration_start",
                    notification_data
                )
            except Exception as e:
                logger.warning(f"通知MCP {mcp.mcp_id} 协作开始失败: {e}")
    
    async def execute_collaboration_step(self, session_id: str, step_name: str,
                                       step_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行协作步骤"""
        if session_id not in self.active_collaborations:
            raise ValueError(f"协作会话不存在: {session_id}")
        
        session = self.active_collaborations[session_id]
        
        try:
            # 记录通信日志
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "step": step_name,
                "data": step_data,
                "participants": session.participating_mcps
            }
            session.communication_log.append(log_entry)
            
            # 并行调用所有参与的MCP
            tasks = []
            for mcp_id in session.participating_mcps:
                task = self._call_mcp_async(mcp_id, step_name, step_data)
                tasks.append(task)
            
            # 等待所有MCP响应
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            successful_results = []
            errors = []
            
            for i, result in enumerate(results):
                mcp_id = session.participating_mcps[i]
                if isinstance(result, Exception):
                    errors.append({"mcp_id": mcp_id, "error": str(result)})
                else:
                    successful_results.append({"mcp_id": mcp_id, "result": result})
            
            return {
                "session_id": session_id,
                "step": step_name,
                "successful_results": successful_results,
                "errors": errors,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"执行协作步骤失败: {e}")
            raise
    
    async def _call_mcp_async(self, mcp_id: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """异步调用MCP"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: asyncio.run(self.coordinator.call_mcp(mcp_id, method, params))
        )
    
    async def end_collaboration(self, session_id: str) -> Dict[str, Any]:
        """结束协作会话"""
        if session_id not in self.active_collaborations:
            raise ValueError(f"协作会话不存在: {session_id}")
        
        session = self.active_collaborations[session_id]
        session.status = "completed"
        session.actual_duration = int((datetime.now() - session.created_at).total_seconds())
        
        # 通知所有参与的MCP
        for mcp_id in session.participating_mcps:
            try:
                await self.coordinator.call_mcp(
                    mcp_id,
                    "collaboration_end",
                    {"session_id": session_id}
                )
            except Exception as e:
                logger.warning(f"通知MCP {mcp_id} 协作结束失败: {e}")
        
        # 生成协作报告
        report = {
            "session_id": session_id,
            "collaboration_type": session.collaboration_type.value,
            "participants": session.participating_mcps,
            "duration": session.actual_duration,
            "communication_count": len(session.communication_log),
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "completed_at": datetime.now().isoformat()
        }
        
        # 从活跃会话中移除
        del self.active_collaborations[session_id]
        
        logger.info(f"协作会话已结束: {session_id}")
        return report
    
    def get_collaboration_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取协作状态"""
        if session_id not in self.active_collaborations:
            return None
        
        session = self.active_collaborations[session_id]
        return {
            "session_id": session_id,
            "collaboration_type": session.collaboration_type.value,
            "participants": session.participating_mcps,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "communication_count": len(session.communication_log),
            "shared_context": session.shared_context
        }
    
    def list_active_collaborations(self) -> List[Dict[str, Any]]:
        """列出活跃的协作会话"""
        return [
            self.get_collaboration_status(session_id)
            for session_id in self.active_collaborations.keys()
        ]

class WorkflowDriver:
    """Workflow驱动器"""
    
    def __init__(self, mcp_collaborator: MCPCollaborator):
        self.collaborator = mcp_collaborator
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}
        self._setup_default_workflows()
    
    def _setup_default_workflows(self):
        """设置默认工作流"""
        
        # 数据分析工作流
        self.register_workflow(WorkflowDefinition(
            workflow_id="data_analysis",
            name="数据分析工作流",
            description="从数据收集到可视化的完整数据分析流程",
            stages=[
                {
                    "stage_id": "data_collection",
                    "name": "数据收集",
                    "required_capabilities": ["data_source", "data_extraction"],
                    "ui_components": ["progress_bar", "data_preview"],
                    "timeout": 300
                },
                {
                    "stage_id": "data_processing",
                    "name": "数据处理",
                    "required_capabilities": ["data_processing", "data_cleaning"],
                    "ui_components": ["processing_status", "error_log"],
                    "timeout": 600
                },
                {
                    "stage_id": "data_analysis",
                    "name": "数据分析",
                    "required_capabilities": ["statistical_analysis", "machine_learning"],
                    "ui_components": ["analysis_config", "results_preview"],
                    "timeout": 900
                },
                {
                    "stage_id": "visualization",
                    "name": "数据可视化",
                    "required_capabilities": ["chart_generation", "dashboard_creation"],
                    "ui_components": ["chart_selector", "dashboard_builder"],
                    "timeout": 300
                }
            ],
            required_mcps=["data_mcp", "analytics_mcp", "visualization_mcp"],
            input_schema={
                "type": "object",
                "properties": {
                    "data_source": {"type": "string"},
                    "analysis_type": {"type": "string"},
                    "output_format": {"type": "string"}
                },
                "required": ["data_source", "analysis_type"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "results": {"type": "object"},
                    "visualizations": {"type": "array"},
                    "summary": {"type": "string"}
                }
            },
            ui_requirements={
                "layout": "dashboard",
                "theme": "light",
                "responsive": True,
                "accessibility": ["screen_reader", "keyboard_navigation"]
            },
            triggers=[
                {"type": "user_request", "condition": "analysis_needed"},
                {"type": "scheduled", "cron": "0 9 * * 1"},  # 每周一上午9点
                {"type": "data_change", "threshold": 0.1}
            ]
        ))
        
        # 内容生成工作流
        self.register_workflow(WorkflowDefinition(
            workflow_id="content_generation",
            name="内容生成工作流",
            description="从需求分析到内容发布的完整内容生成流程",
            stages=[
                {
                    "stage_id": "requirement_analysis",
                    "name": "需求分析",
                    "required_capabilities": ["nlp", "requirement_extraction"],
                    "ui_components": ["requirement_form", "analysis_results"],
                    "timeout": 180
                },
                {
                    "stage_id": "content_planning",
                    "name": "内容规划",
                    "required_capabilities": ["content_strategy", "outline_generation"],
                    "ui_components": ["outline_editor", "strategy_display"],
                    "timeout": 300
                },
                {
                    "stage_id": "content_creation",
                    "name": "内容创建",
                    "required_capabilities": ["text_generation", "image_generation"],
                    "ui_components": ["content_editor", "media_gallery"],
                    "timeout": 1200
                },
                {
                    "stage_id": "review_approval",
                    "name": "审核批准",
                    "required_capabilities": ["content_review", "quality_check"],
                    "ui_components": ["review_interface", "approval_workflow"],
                    "timeout": 600
                }
            ],
            required_mcps=["nlp_mcp", "content_mcp", "review_mcp"],
            input_schema={
                "type": "object",
                "properties": {
                    "content_type": {"type": "string"},
                    "target_audience": {"type": "string"},
                    "requirements": {"type": "string"},
                    "deadline": {"type": "string"}
                },
                "required": ["content_type", "requirements"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "media": {"type": "array"},
                    "metadata": {"type": "object"}
                }
            },
            ui_requirements={
                "layout": "sidebar",
                "theme": "auto",
                "responsive": True,
                "accessibility": ["high_contrast", "large_fonts"]
            },
            triggers=[
                {"type": "user_request", "condition": "content_needed"},
                {"type": "calendar_event", "event_type": "content_deadline"}
            ]
        ))
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """注册工作流定义"""
        self.workflow_definitions[workflow.workflow_id] = workflow
        logger.info(f"注册工作流: {workflow.workflow_id}")
    
    async def start_workflow(self, workflow_id: str, input_data: Dict[str, Any],
                           ui_preferences: Dict[str, Any] = None) -> str:
        """启动工作流执行"""
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        workflow_def = self.workflow_definitions[workflow_id]
        
        # 验证输入数据
        if not self._validate_input(input_data, workflow_def.input_schema):
            raise ValueError("输入数据不符合工作流要求")
        
        # 创建执行实例
        execution_id = f"exec_{workflow_id}_{int(time.time())}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            stage=WorkflowStage.PLANNING,
            current_step=0,
            total_steps=len(workflow_def.stages),
            started_at=datetime.now(),
            context=input_data.copy(),
            results={},
            errors=[],
            ui_state={}
        )
        
        self.active_executions[execution_id] = execution
        
        # 生成工作流专用UI
        ui_config = await self._generate_workflow_ui(workflow_def, ui_preferences or {})
        execution.ui_state = ui_config
        
        # 发起MCP协作
        collaboration_id = await self.collaborator.initiate_collaboration(
            CollaborationType.WORKFLOW_CHAIN,
            workflow_def.required_mcps,
            {
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "input_data": input_data
            }
        )
        
        execution.context["collaboration_id"] = collaboration_id
        execution.stage = WorkflowStage.EXECUTION
        
        logger.info(f"工作流执行已启动: {execution_id}")
        return execution_id
    
    def _validate_input(self, input_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """验证输入数据"""
        # 简化的JSON Schema验证
        required_fields = schema.get("required", [])
        
        for field in required_fields:
            if field not in input_data:
                logger.error(f"缺少必需字段: {field}")
                return False
        
        return True
    
    async def _generate_workflow_ui(self, workflow_def: WorkflowDefinition,
                                  ui_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """生成工作流专用UI"""
        ui_config = {
            "workflow_id": workflow_def.workflow_id,
            "layout": workflow_def.ui_requirements.get("layout", "dashboard"),
            "theme": workflow_def.ui_requirements.get("theme", "light"),
            "components": [],
            "navigation": {
                "type": "stepper",
                "steps": [stage["name"] for stage in workflow_def.stages]
            }
        }
        
        # 为每个阶段生成UI组件
        for i, stage in enumerate(workflow_def.stages):
            stage_components = {
                "stage_id": stage["stage_id"],
                "stage_name": stage["name"],
                "components": []
            }
            
            # 根据阶段要求的UI组件生成配置
            for component_type in stage.get("ui_components", []):
                component_config = self._generate_stage_component(component_type, stage)
                stage_components["components"].append(component_config)
            
            ui_config["components"].append(stage_components)
        
        # 应用用户偏好
        if ui_preferences.get("theme"):
            ui_config["theme"] = ui_preferences["theme"]
        
        if ui_preferences.get("layout"):
            ui_config["layout"] = ui_preferences["layout"]
        
        return ui_config
    
    def _generate_stage_component(self, component_type: str, stage: Dict[str, Any]) -> Dict[str, Any]:
        """生成阶段组件配置"""
        component_configs = {
            "progress_bar": {
                "type": "progress",
                "props": {
                    "label": f"{stage['name']}进度",
                    "show_percentage": True,
                    "animated": True
                }
            },
            "data_preview": {
                "type": "table",
                "props": {
                    "title": "数据预览",
                    "paginated": True,
                    "searchable": True
                }
            },
            "processing_status": {
                "type": "card",
                "props": {
                    "title": "处理状态",
                    "real_time_updates": True,
                    "status_indicators": True
                }
            },
            "error_log": {
                "type": "list",
                "props": {
                    "title": "错误日志",
                    "filterable": True,
                    "expandable_items": True
                }
            },
            "analysis_config": {
                "type": "form",
                "props": {
                    "title": "分析配置",
                    "validation": True,
                    "auto_save": True
                }
            },
            "results_preview": {
                "type": "card",
                "props": {
                    "title": "结果预览",
                    "collapsible": True,
                    "export_options": True
                }
            },
            "chart_selector": {
                "type": "grid",
                "props": {
                    "title": "图表选择",
                    "selectable": True,
                    "preview_mode": True
                }
            },
            "dashboard_builder": {
                "type": "canvas",
                "props": {
                    "title": "仪表板构建器",
                    "drag_drop": True,
                    "real_time_preview": True
                }
            }
        }
        
        return component_configs.get(component_type, {
            "type": "card",
            "props": {"title": component_type}
        })
    
    async def execute_workflow_stage(self, execution_id: str) -> Dict[str, Any]:
        """执行工作流阶段"""
        if execution_id not in self.active_executions:
            raise ValueError(f"工作流执行不存在: {execution_id}")
        
        execution = self.active_executions[execution_id]
        workflow_def = self.workflow_definitions[execution.workflow_id]
        
        if execution.current_step >= len(workflow_def.stages):
            execution.stage = WorkflowStage.COMPLETION
            return {"status": "completed", "execution_id": execution_id}
        
        current_stage = workflow_def.stages[execution.current_step]
        
        try:
            # 执行当前阶段
            stage_result = await self.collaborator.execute_collaboration_step(
                execution.context["collaboration_id"],
                f"execute_stage_{current_stage['stage_id']}",
                {
                    "stage_config": current_stage,
                    "execution_context": execution.context,
                    "previous_results": execution.results
                }
            )
            
            # 更新执行状态
            execution.results[current_stage["stage_id"]] = stage_result
            execution.current_step += 1
            
            # 更新UI状态
            await self._update_workflow_ui(execution, current_stage, stage_result)
            
            return {
                "status": "stage_completed",
                "execution_id": execution_id,
                "stage": current_stage["stage_id"],
                "result": stage_result,
                "progress": execution.current_step / execution.total_steps
            }
            
        except Exception as e:
            execution.stage = WorkflowStage.ERROR_HANDLING
            execution.errors.append({
                "stage": current_stage["stage_id"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.error(f"工作流阶段执行失败: {e}")
            return {
                "status": "stage_failed",
                "execution_id": execution_id,
                "stage": current_stage["stage_id"],
                "error": str(e)
            }
    
    async def _update_workflow_ui(self, execution: WorkflowExecution,
                                stage: Dict[str, Any], result: Dict[str, Any]):
        """更新工作流UI状态"""
        # 更新进度
        execution.ui_state["progress"] = execution.current_step / execution.total_steps
        
        # 更新当前阶段状态
        execution.ui_state["current_stage"] = stage["stage_id"]
        
        # 更新组件数据
        if "ui_updates" in result:
            execution.ui_state.setdefault("component_data", {})
            execution.ui_state["component_data"].update(result["ui_updates"])
    
    async def complete_workflow(self, execution_id: str) -> Dict[str, Any]:
        """完成工作流执行"""
        if execution_id not in self.active_executions:
            raise ValueError(f"工作流执行不存在: {execution_id}")
        
        execution = self.active_executions[execution_id]
        execution.stage = WorkflowStage.COMPLETION
        
        # 结束协作会话
        collaboration_report = await self.collaborator.end_collaboration(
            execution.context["collaboration_id"]
        )
        
        # 生成工作流报告
        workflow_report = {
            "execution_id": execution_id,
            "workflow_id": execution.workflow_id,
            "started_at": execution.started_at.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "duration": int((datetime.now() - execution.started_at).total_seconds()),
            "stages_completed": execution.current_step,
            "total_stages": execution.total_steps,
            "results": execution.results,
            "errors": execution.errors,
            "collaboration_report": collaboration_report,
            "ui_state": execution.ui_state
        }
        
        # 从活跃执行中移除
        del self.active_executions[execution_id]
        
        logger.info(f"工作流执行已完成: {execution_id}")
        return workflow_report
    
    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流执行状态"""
        if execution_id not in self.active_executions:
            return None
        
        execution = self.active_executions[execution_id]
        return {
            "execution_id": execution_id,
            "workflow_id": execution.workflow_id,
            "stage": execution.stage.value,
            "current_step": execution.current_step,
            "total_steps": execution.total_steps,
            "progress": execution.current_step / execution.total_steps,
            "started_at": execution.started_at.isoformat(),
            "errors": execution.errors,
            "ui_state": execution.ui_state
        }
    
    def list_available_workflows(self) -> List[Dict[str, Any]]:
        """列出可用的工作流"""
        return [
            {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "required_mcps": workflow.required_mcps,
                "stages_count": len(workflow.stages),
                "triggers": workflow.triggers
            }
            for workflow in self.workflow_definitions.values()
        ]
    
    def list_active_executions(self) -> List[Dict[str, Any]]:
        """列出活跃的工作流执行"""
        return [
            self.get_workflow_status(execution_id)
            for execution_id in self.active_executions.keys()
        ]

if __name__ == "__main__":
    # 测试代码
    async def test_mcp_integration():
        # 创建协调器客户端
        coordinator_client = MCPCoordinatorClient()
        
        # 创建协作管理器
        collaborator = MCPCollaborator(coordinator_client)
        
        # 创建工作流驱动器
        workflow_driver = WorkflowDriver(collaborator)
        
        # 列出可用工作流
        workflows = workflow_driver.list_available_workflows()
        print(f"可用工作流: {json.dumps(workflows, indent=2, ensure_ascii=False)}")
        
        # 模拟启动数据分析工作流
        try:
            execution_id = await workflow_driver.start_workflow(
                "data_analysis",
                {
                    "data_source": "user_behavior_data.csv",
                    "analysis_type": "trend_analysis",
                    "output_format": "dashboard"
                },
                {"theme": "dark", "layout": "dashboard"}
            )
            
            print(f"工作流执行已启动: {execution_id}")
            
            # 获取执行状态
            status = workflow_driver.get_workflow_status(execution_id)
            print(f"执行状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"工作流启动失败: {e}")
    
    # 运行测试
    asyncio.run(test_mcp_integration())

