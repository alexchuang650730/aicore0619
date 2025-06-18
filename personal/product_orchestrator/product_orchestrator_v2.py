#!/usr/bin/env python3
"""
Product Orchestrator - 基于现有workflow和adapter架构

通过MCPCoordinator协调六个workflow，每个workflow使用相应的mcp组件完成任务：

六大工作流映射：
1. 📋 需求分析 → requirements_analysis_mcp (workflow) + requirement_analysis_mcp (adapter)
2. 🏗️ 架构设计 → architecture_design_mcp (workflow) + enhanced_workflow_mcp (adapter)
3. 💻 编码实现 → coding_workflow_mcp (workflow) + code_generation_mcp + kilocode_mcp (adapter)
4. 🧪 测试验证 → developer_flow_mcp (workflow) + test_manage_mcp (adapter)
5. 🚀 部署发布 → release_manager_mcp (workflow) + deployment_mcp (adapter)
6. 📊 监控运维 → operations_workflow_mcp (workflow) + monitoring_mcp (adapter)
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 1. 数据结构定义
# ============================================================================

class WorkflowType(Enum):
    """六大工作流类型（对应现有workflow目录）"""
    REQUIREMENTS_ANALYSIS = "requirements_analysis_mcp"
    ARCHITECTURE_DESIGN = "architecture_design_mcp"
    CODING_WORKFLOW = "coding_workflow_mcp"
    DEVELOPER_FLOW = "developer_flow_mcp"  # 测试验证
    RELEASE_MANAGER = "release_manager_mcp"
    OPERATIONS_WORKFLOW = "operations_workflow_mcp"

class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProductType(Enum):
    """产品类型"""
    WEB_APPLICATION = "web_application"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    DESKTOP_APPLICATION = "desktop_application"
    GAME = "game"
    AI_MODEL = "ai_model"

@dataclass
class WorkflowMapping:
    """工作流与MCP组件映射"""
    workflow_name: str
    workflow_port: int
    adapter_mcps: List[str]
    description: str
    estimated_duration: str

@dataclass
class ProductRequest:
    """产品开发请求"""
    request_id: str
    user_id: str
    product_name: str
    product_type: ProductType
    description: str
    requirements: Dict[str, Any]
    priority: str = "normal"
    deadline: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class WorkflowTask:
    """工作流任务"""
    task_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration: Optional[float] = None
    workflow_url: Optional[str] = None

@dataclass
class ProductProject:
    """产品项目"""
    project_id: str
    request: ProductRequest
    workflows: List[WorkflowTask]
    current_workflow: Optional[WorkflowType] = None
    overall_status: WorkflowStatus = WorkflowStatus.PENDING
    progress: float = 0.0
    artifacts: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = {}

# ============================================================================
# 2. 工作流映射配置
# ============================================================================

class WorkflowMappingConfig:
    """工作流映射配置"""
    
    @staticmethod
    def get_workflow_mappings() -> Dict[WorkflowType, WorkflowMapping]:
        """获取工作流映射配置"""
        return {
            WorkflowType.REQUIREMENTS_ANALYSIS: WorkflowMapping(
                workflow_name="requirements_analysis_mcp",
                workflow_port=8090,
                adapter_mcps=["requirement_analysis_mcp", "enhanced_workflow_mcp"],
                description="📋 需求分析 - AI理解业务需求，生成技术方案",
                estimated_duration="3-8分钟"
            ),
            WorkflowType.ARCHITECTURE_DESIGN: WorkflowMapping(
                workflow_name="architecture_design_mcp",
                workflow_port=8091,
                adapter_mcps=["enhanced_workflow_mcp", "directory_structure_mcp"],
                description="🏗️ 架构设计 - 智能架构建议，最佳实践推荐",
                estimated_duration="5-12分钟"
            ),
            WorkflowType.CODING_WORKFLOW: WorkflowMapping(
                workflow_name="coding_workflow_mcp",
                workflow_port=8092,
                adapter_mcps=["code_generation_mcp", "kilocode_mcp", "github_mcp"],
                description="💻 编码实现 - AI编程助手，代码自动生成，智能代码补全",
                estimated_duration="10-25分钟"
            ),
            WorkflowType.DEVELOPER_FLOW: WorkflowMapping(
                workflow_name="developer_flow_mcp",
                workflow_port=8093,
                adapter_mcps=["test_manage_mcp", "development_intervention_mcp"],
                description="🧪 测试验证 - 自动化测试，质量保障，智能介入协调",
                estimated_duration="8-18分钟"
            ),
            WorkflowType.RELEASE_MANAGER: WorkflowMapping(
                workflow_name="release_manager_mcp",
                workflow_port=8094,
                adapter_mcps=["deployment_mcp", "github_mcp"],
                description="🚀 部署发布 - 一键部署，环境管理，版本控制",
                estimated_duration="6-15分钟"
            ),
            WorkflowType.OPERATIONS_WORKFLOW: WorkflowMapping(
                workflow_name="operations_workflow_mcp",
                workflow_port=8095,
                adapter_mcps=["monitoring_mcp", "enterprise_smartui_mcp"],
                description="📊 监控运维 - 性能监控，问题预警",
                estimated_duration="4-10分钟"
            )
        }

# ============================================================================
# 3. MCPCoordinator集成客户端
# ============================================================================

class MCPCoordinatorClient:
    """MCPCoordinator集成客户端"""
    
    def __init__(self, coordinator_url: str = "http://localhost:8089"):
        self.coordinator_url = coordinator_url
        self.session = requests.Session()
        
    async def send_workflow_request(self, workflow_type: WorkflowType, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """向指定workflow发送请求"""
        try:
            mapping = WorkflowMappingConfig.get_workflow_mappings()[workflow_type]
            workflow_url = f"http://localhost:{mapping.workflow_port}"
            
            # 首先尝试直接调用workflow
            try:
                response = self.session.post(
                    f"{workflow_url}/api/execute",
                    json=request_data,
                    timeout=300  # 5分钟超时
                )
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                logger.warning(f"直接调用workflow失败，尝试通过MCPCoordinator: {e}")
            
            # 如果直接调用失败，通过MCPCoordinator
            coordinator_payload = {
                "target_workflow": workflow_type.value,
                "action": "execute_workflow",
                "request_data": request_data,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.coordinator_url}/api/workflow/execute",
                json=coordinator_payload,
                timeout=300
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"工作流请求失败 {workflow_type.value}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_workflow_status(self, workflow_type: WorkflowType) -> Dict[str, Any]:
        """获取工作流状态"""
        try:
            mapping = WorkflowMappingConfig.get_workflow_mappings()[workflow_type]
            workflow_url = f"http://localhost:{mapping.workflow_port}"
            
            response = self.session.get(f"{workflow_url}/api/status", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                # 通过MCPCoordinator查询
                response = self.session.get(
                    f"{self.coordinator_url}/api/workflow/status/{workflow_type.value}",
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"获取工作流状态失败 {workflow_type.value}: {e}")
            return {"success": False, "error": str(e)}

# ============================================================================
# 4. 工作流执行器
# ============================================================================

class WorkflowExecutor:
    """工作流执行器"""
    
    def __init__(self, mcp_coordinator: MCPCoordinatorClient):
        self.mcp_coordinator = mcp_coordinator
        self.workflow_mappings = WorkflowMappingConfig.get_workflow_mappings()
    
    async def execute_requirements_analysis(self, task: WorkflowTask) -> WorkflowTask:
        """执行需求分析工作流"""
        logger.info(f"开始需求分析: {task.task_id}")
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        try:
            request_data = {
                "action": "analyze_requirements",
                "product_description": task.input_data.get("description", ""),
                "product_type": task.input_data.get("product_type", ""),
                "user_requirements": task.input_data.get("requirements", {}),
                "priority": task.input_data.get("priority", "normal")
            }
            
            result = await self.mcp_coordinator.send_workflow_request(
                WorkflowType.REQUIREMENTS_ANALYSIS,
                request_data
            )
            
            if result.get("success"):
                task.output_data = {
                    "technical_requirements": result.get("technical_requirements", {}),
                    "functional_requirements": result.get("functional_requirements", []),
                    "non_functional_requirements": result.get("non_functional_requirements", []),
                    "technology_stack_recommendations": result.get("technology_stack_recommendations", []),
                    "complexity_assessment": result.get("complexity_assessment", {}),
                    "risk_analysis": result.get("risk_analysis", []),
                    "timeline_estimate": result.get("timeline_estimate", ""),
                    "resource_requirements": result.get("resource_requirements", {})
                }
                task.status = WorkflowStatus.COMPLETED
                logger.info(f"需求分析完成: {task.task_id}")
            else:
                task.status = WorkflowStatus.FAILED
                task.error_message = result.get("error", "需求分析失败")
                
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
            logger.error(f"需求分析执行异常: {e}")
        
        task.completed_at = datetime.now().isoformat()
        return task
    
    async def execute_architecture_design(self, task: WorkflowTask) -> WorkflowTask:
        """执行架构设计工作流"""
        logger.info(f"开始架构设计: {task.task_id}")
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        try:
            request_data = {
                "action": "design_architecture",
                "technical_requirements": task.input_data.get("technical_requirements", {}),
                "functional_requirements": task.input_data.get("functional_requirements", []),
                "technology_stack_recommendations": task.input_data.get("technology_stack_recommendations", []),
                "complexity_assessment": task.input_data.get("complexity_assessment", {}),
                "constraints": task.input_data.get("constraints", {})
            }
            
            result = await self.mcp_coordinator.send_workflow_request(
                WorkflowType.ARCHITECTURE_DESIGN,
                request_data
            )
            
            if result.get("success"):
                task.output_data = {
                    "system_architecture": result.get("system_architecture", {}),
                    "technology_stack": result.get("technology_stack", {}),
                    "database_design": result.get("database_design", {}),
                    "api_specifications": result.get("api_specifications", {}),
                    "deployment_architecture": result.get("deployment_architecture", {}),
                    "security_architecture": result.get("security_architecture", {}),
                    "scalability_plan": result.get("scalability_plan", {}),
                    "architecture_diagrams": result.get("architecture_diagrams", [])
                }
                task.status = WorkflowStatus.COMPLETED
                logger.info(f"架构设计完成: {task.task_id}")
            else:
                task.status = WorkflowStatus.FAILED
                task.error_message = result.get("error", "架构设计失败")
                
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
            logger.error(f"架构设计执行异常: {e}")
        
        task.completed_at = datetime.now().isoformat()
        return task
    
    async def execute_coding_workflow(self, task: WorkflowTask) -> WorkflowTask:
        """执行编码工作流"""
        logger.info(f"开始编码实现: {task.task_id}")
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        try:
            request_data = {
                "action": "generate_code",
                "system_architecture": task.input_data.get("system_architecture", {}),
                "technology_stack": task.input_data.get("technology_stack", {}),
                "api_specifications": task.input_data.get("api_specifications", {}),
                "database_design": task.input_data.get("database_design", {}),
                "functional_requirements": task.input_data.get("functional_requirements", []),
                "coding_standards": task.input_data.get("coding_standards", {})
            }
            
            result = await self.mcp_coordinator.send_workflow_request(
                WorkflowType.CODING_WORKFLOW,
                request_data
            )
            
            if result.get("success"):
                task.output_data = {
                    "source_code": result.get("source_code", {}),
                    "project_structure": result.get("project_structure", {}),
                    "frontend_code": result.get("frontend_code", {}),
                    "backend_code": result.get("backend_code", {}),
                    "database_scripts": result.get("database_scripts", {}),
                    "configuration_files": result.get("configuration_files", {}),
                    "documentation": result.get("documentation", {}),
                    "build_scripts": result.get("build_scripts", {}),
                    "code_quality_metrics": result.get("code_quality_metrics", {}),
                    "repository_url": result.get("repository_url", "")
                }
                task.status = WorkflowStatus.COMPLETED
                logger.info(f"编码实现完成: {task.task_id}")
            else:
                task.status = WorkflowStatus.FAILED
                task.error_message = result.get("error", "编码实现失败")
                
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
            logger.error(f"编码实现执行异常: {e}")
        
        task.completed_at = datetime.now().isoformat()
        return task
    
    async def execute_developer_flow(self, task: WorkflowTask) -> WorkflowTask:
        """执行测试验证工作流"""
        logger.info(f"开始测试验证: {task.task_id}")
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        try:
            request_data = {
                "action": "run_tests",
                "source_code": task.input_data.get("source_code", {}),
                "functional_requirements": task.input_data.get("functional_requirements", []),
                "api_specifications": task.input_data.get("api_specifications", {}),
                "test_requirements": task.input_data.get("test_requirements", {}),
                "quality_standards": task.input_data.get("quality_standards", {})
            }
            
            result = await self.mcp_coordinator.send_workflow_request(
                WorkflowType.DEVELOPER_FLOW,
                request_data
            )
            
            if result.get("success"):
                task.output_data = {
                    "test_results": result.get("test_results", {}),
                    "test_coverage": result.get("test_coverage", 0),
                    "quality_metrics": result.get("quality_metrics", {}),
                    "performance_metrics": result.get("performance_metrics", {}),
                    "security_scan_results": result.get("security_scan_results", {}),
                    "issues_found": result.get("issues_found", []),
                    "recommendations": result.get("recommendations", []),
                    "test_reports": result.get("test_reports", []),
                    "quality_score": result.get("quality_score", 0),
                    "ready_for_deployment": result.get("ready_for_deployment", False)
                }
                task.status = WorkflowStatus.COMPLETED
                logger.info(f"测试验证完成: {task.task_id}")
            else:
                task.status = WorkflowStatus.FAILED
                task.error_message = result.get("error", "测试验证失败")
                
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
            logger.error(f"测试验证执行异常: {e}")
        
        task.completed_at = datetime.now().isoformat()
        return task
    
    async def execute_release_manager(self, task: WorkflowTask) -> WorkflowTask:
        """执行部署发布工作流"""
        logger.info(f"开始部署发布: {task.task_id}")
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        try:
            request_data = {
                "action": "deploy_release",
                "source_code": task.input_data.get("source_code", {}),
                "deployment_architecture": task.input_data.get("deployment_architecture", {}),
                "configuration_files": task.input_data.get("configuration_files", {}),
                "test_results": task.input_data.get("test_results", {}),
                "ready_for_deployment": task.input_data.get("ready_for_deployment", False),
                "release_notes": task.input_data.get("release_notes", "")
            }
            
            result = await self.mcp_coordinator.send_workflow_request(
                WorkflowType.RELEASE_MANAGER,
                request_data
            )
            
            if result.get("success"):
                task.output_data = {
                    "deployment_url": result.get("deployment_url", ""),
                    "deployment_status": result.get("deployment_status", ""),
                    "environment_details": result.get("environment_details", {}),
                    "service_endpoints": result.get("service_endpoints", []),
                    "monitoring_urls": result.get("monitoring_urls", []),
                    "deployment_logs": result.get("deployment_logs", []),
                    "rollback_plan": result.get("rollback_plan", {}),
                    "performance_baseline": result.get("performance_baseline", {}),
                    "deployment_successful": result.get("deployment_successful", False),
                    "version_info": result.get("version_info", {})
                }
                task.status = WorkflowStatus.COMPLETED
                logger.info(f"部署发布完成: {task.task_id}")
            else:
                task.status = WorkflowStatus.FAILED
                task.error_message = result.get("error", "部署发布失败")
                
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
            logger.error(f"部署发布执行异常: {e}")
        
        task.completed_at = datetime.now().isoformat()
        return task
    
    async def execute_operations_workflow(self, task: WorkflowTask) -> WorkflowTask:
        """执行监控运维工作流"""
        logger.info(f"开始监控运维: {task.task_id}")
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        try:
            request_data = {
                "action": "setup_monitoring",
                "deployment_url": task.input_data.get("deployment_url", ""),
                "service_endpoints": task.input_data.get("service_endpoints", []),
                "environment_details": task.input_data.get("environment_details", {}),
                "performance_baseline": task.input_data.get("performance_baseline", {}),
                "monitoring_requirements": task.input_data.get("monitoring_requirements", {}),
                "alert_thresholds": task.input_data.get("alert_thresholds", {})
            }
            
            result = await self.mcp_coordinator.send_workflow_request(
                WorkflowType.OPERATIONS_WORKFLOW,
                request_data
            )
            
            if result.get("success"):
                task.output_data = {
                    "monitoring_dashboard": result.get("monitoring_dashboard", ""),
                    "alert_system": result.get("alert_system", {}),
                    "log_management": result.get("log_management", {}),
                    "performance_monitoring": result.get("performance_monitoring", {}),
                    "health_checks": result.get("health_checks", []),
                    "backup_strategy": result.get("backup_strategy", {}),
                    "disaster_recovery": result.get("disaster_recovery", {}),
                    "maintenance_procedures": result.get("maintenance_procedures", []),
                    "optimization_recommendations": result.get("optimization_recommendations", []),
                    "monitoring_active": result.get("monitoring_active", False)
                }
                task.status = WorkflowStatus.COMPLETED
                logger.info(f"监控运维完成: {task.task_id}")
            else:
                task.status = WorkflowStatus.FAILED
                task.error_message = result.get("error", "监控运维失败")
                
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
            logger.error(f"监控运维执行异常: {e}")
        
        task.completed_at = datetime.now().isoformat()
        return task

# ============================================================================
# 5. 产品编排器核心
# ============================================================================

class ProductOrchestrator:
    """产品编排器核心"""
    
    def __init__(self, coordinator_url: str = "http://localhost:8089"):
        self.mcp_coordinator = MCPCoordinatorClient(coordinator_url)
        self.workflow_executor = WorkflowExecutor(self.mcp_coordinator)
        self.projects: Dict[str, ProductProject] = {}
        self.workflow_mappings = WorkflowMappingConfig.get_workflow_mappings()
        
        # 工作流执行方法映射
        self.workflow_executors = {
            WorkflowType.REQUIREMENTS_ANALYSIS: self.workflow_executor.execute_requirements_analysis,
            WorkflowType.ARCHITECTURE_DESIGN: self.workflow_executor.execute_architecture_design,
            WorkflowType.CODING_WORKFLOW: self.workflow_executor.execute_coding_workflow,
            WorkflowType.DEVELOPER_FLOW: self.workflow_executor.execute_developer_flow,
            WorkflowType.RELEASE_MANAGER: self.workflow_executor.execute_release_manager,
            WorkflowType.OPERATIONS_WORKFLOW: self.workflow_executor.execute_operations_workflow
        }
    
    async def create_product(self, product_request: ProductRequest) -> str:
        """创建产品开发项目"""
        project_id = str(uuid.uuid4())
        
        # 创建工作流任务序列
        workflows = []
        for workflow_type in WorkflowType:
            task = WorkflowTask(
                task_id=f"{project_id}_{workflow_type.value}",
                workflow_type=workflow_type,
                status=WorkflowStatus.PENDING,
                input_data={},
                workflow_url=f"http://localhost:{self.workflow_mappings[workflow_type].workflow_port}"
            )
            workflows.append(task)
        
        # 创建项目
        project = ProductProject(
            project_id=project_id,
            request=product_request,
            workflows=workflows,
            current_workflow=WorkflowType.REQUIREMENTS_ANALYSIS
        )
        
        self.projects[project_id] = project
        
        logger.info(f"创建产品项目: {project_id} - {product_request.product_name}")
        return project_id
    
    async def execute_product_development(self, project_id: str) -> ProductProject:
        """执行完整的产品开发流程"""
        if project_id not in self.projects:
            raise ValueError(f"项目不存在: {project_id}")
        
        project = self.projects[project_id]
        project.overall_status = WorkflowStatus.RUNNING
        
        logger.info(f"开始执行产品开发流程: {project_id}")
        
        try:
            # 按顺序执行六大工作流
            workflow_sequence = list(WorkflowType)
            
            for i, workflow_type in enumerate(workflow_sequence):
                project.current_workflow = workflow_type
                task = next(w for w in project.workflows if w.workflow_type == workflow_type)
                
                logger.info(f"执行工作流 {i+1}/6: {self.workflow_mappings[workflow_type].description}")
                
                # 准备输入数据
                if i == 0:  # 第一个工作流：需求分析
                    task.input_data = {
                        "description": project.request.description,
                        "product_type": project.request.product_type.value,
                        "requirements": project.request.requirements,
                        "priority": project.request.priority,
                        "deadline": project.request.deadline
                    }
                else:  # 后续工作流使用前一个工作流的输出
                    prev_task = project.workflows[i-1]
                    if prev_task.output_data:
                        task.input_data.update(prev_task.output_data)
                    
                    # 添加项目基本信息
                    task.input_data.update({
                        "project_id": project_id,
                        "product_name": project.request.product_name,
                        "product_type": project.request.product_type.value
                    })
                
                # 执行工作流
                executor = self.workflow_executors[workflow_type]
                task = await executor(task)
                
                # 更新项目进度
                project.progress = (i + 1) / len(workflow_sequence) * 100
                
                # 保存工件
                if task.output_data:
                    project.artifacts[workflow_type.value] = task.output_data
                
                # 如果任务失败，停止执行
                if task.status == WorkflowStatus.FAILED:
                    project.overall_status = WorkflowStatus.FAILED
                    logger.error(f"工作流失败: {workflow_type.value}, 错误: {task.error_message}")
                    break
                
                logger.info(f"工作流完成 {i+1}/6: {workflow_type.value}")
            
            # 检查是否所有工作流都成功完成
            if all(w.status == WorkflowStatus.COMPLETED for w in project.workflows):
                project.overall_status = WorkflowStatus.COMPLETED
                project.progress = 100.0
                logger.info(f"🎉 产品开发完成: {project_id} - {project.request.product_name}")
            
        except Exception as e:
            project.overall_status = WorkflowStatus.FAILED
            logger.error(f"产品开发执行失败: {e}")
        
        return project
    
    def get_project_status(self, project_id: str) -> Optional[ProductProject]:
        """获取项目状态"""
        return self.projects.get(project_id)
    
    def list_projects(self) -> List[ProductProject]:
        """列出所有项目"""
        return list(self.projects.values())
    
    def get_workflow_mappings(self) -> Dict[str, Dict[str, Any]]:
        """获取工作流映射信息"""
        mappings = {}
        for workflow_type, mapping in self.workflow_mappings.items():
            mappings[workflow_type.value] = {
                "name": mapping.workflow_name,
                "port": mapping.workflow_port,
                "adapters": mapping.adapter_mcps,
                "description": mapping.description,
                "estimated_duration": mapping.estimated_duration
            }
        return mappings

# ============================================================================
# 6. Flask API服务器
# ============================================================================

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 创建产品编排器实例
orchestrator = ProductOrchestrator()

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "product_orchestrator",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "workflow_mappings": orchestrator.get_workflow_mappings()
    })

@app.route('/api/workflows')
def get_workflows():
    """获取工作流映射信息"""
    return jsonify({
        "success": True,
        "workflows": orchestrator.get_workflow_mappings()
    })

@app.route('/api/product/create', methods=['POST'])
def create_product():
    """创建产品"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['product_name', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"缺少必需字段: {field}"
                }), 400
        
        # 创建产品请求
        product_request = ProductRequest(
            request_id=str(uuid.uuid4()),
            user_id=data.get('user_id', 'anonymous'),
            product_name=data.get('product_name'),
            product_type=ProductType(data.get('product_type', 'web_application')),
            description=data.get('description'),
            requirements=data.get('requirements', {}),
            priority=data.get('priority', 'normal'),
            deadline=data.get('deadline')
        )
        
        # 创建项目
        project_id = asyncio.run(orchestrator.create_product(product_request))
        
        return jsonify({
            "success": True,
            "project_id": project_id,
            "message": f"产品项目创建成功: {product_request.product_name}",
            "workflows": orchestrator.get_workflow_mappings()
        })
        
    except Exception as e:
        logger.error(f"创建产品失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/product/develop/<project_id>', methods=['POST'])
def develop_product(project_id):
    """开始产品开发"""
    try:
        project = asyncio.run(orchestrator.execute_product_development(project_id))
        
        return jsonify({
            "success": True,
            "project": asdict(project),
            "message": "产品开发流程执行完成"
        })
        
    except Exception as e:
        logger.error(f"产品开发失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/product/status/<project_id>')
def get_product_status(project_id):
    """获取产品状态"""
    try:
        project = orchestrator.get_project_status(project_id)
        
        if project:
            return jsonify({
                "success": True,
                "project": asdict(project)
            })
        else:
            return jsonify({
                "success": False,
                "error": "项目不存在"
            }), 404
            
    except Exception as e:
        logger.error(f"获取产品状态失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/products')
def list_products():
    """列出所有产品"""
    try:
        projects = orchestrator.list_projects()
        
        return jsonify({
            "success": True,
            "projects": [asdict(p) for p in projects],
            "count": len(projects)
        })
        
    except Exception as e:
        logger.error(f"列出产品失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/product/quick-create', methods=['POST'])
def quick_create_product():
    """快速创建并开发产品（用于SmartUI集成）"""
    try:
        data = request.get_json()
        
        # 创建产品请求
        product_request = ProductRequest(
            request_id=str(uuid.uuid4()),
            user_id=data.get('user_id', 'smartui_user'),
            product_name=data.get('product_name', '智能生成产品'),
            product_type=ProductType(data.get('product_type', 'web_application')),
            description=data.get('description', ''),
            requirements=data.get('requirements', {}),
            priority=data.get('priority', 'normal')
        )
        
        # 创建项目
        project_id = await orchestrator.create_product(product_request)
        
        # 立即开始开发
        project = await orchestrator.execute_product_development(project_id)
        
        return jsonify({
            "success": True,
            "project_id": project_id,
            "project": asdict(project),
            "message": "产品快速创建和开发完成"
        })
        
    except Exception as e:
        logger.error(f"快速创建产品失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    logger.info("🚀 启动Product Orchestrator服务器...")
    logger.info("📋 工作流映射:")
    for workflow_type, mapping in WorkflowMappingConfig.get_workflow_mappings().items():
        logger.info(f"  {mapping.description}")
        logger.info(f"    端口: {mapping.workflow_port}, 适配器: {', '.join(mapping.adapter_mcps)}")
    
    app.run(host='0.0.0.0', port=5002, debug=True)

